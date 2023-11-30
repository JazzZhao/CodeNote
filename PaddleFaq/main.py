import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from predict import Predictor
from milvus_utils import VecToMilvus
from paddlenlp.transformers import AutoTokenizer
from mysql_utils import Mysql
from logs import LOGGER
import time
import pandas as pd
from service import (
    milvus_data_search,
    milvus_data_insert
)
from data import read_text
from config import (
    collection_name
)


app = FastAPI()

#跨域使用（留用）
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
batch_size = 32

# 在全局定义 PREDICTOR 对象
PREDICTOR = None
MILVUS_CLI = None

@app.on_event("startup")
def load_predictor():
    global PREDICTOR
    global MILVUS_CLI
    global CONN
    # 加载模型
    PREDICTOR = Predictor(
        "output",
        "cpu",
        64,
        32,
        False,
        "fp32",
        10,
        False,
    )
    # 加载milvus
    MILVUS_CLI = VecToMilvus()


@app.get('/qa/update_data')
def do_load_api(company_id:str):
    try:
         # 加载mysql
        CONN = Mysql()
        LOGGER.info(f"请求的公司ID: {company_id}")
        #暂时从文件导入，后期做成从mongo数据库中导入
        data = CONN.get_question(company_id=company_id)
        LOGGER.info(f"读取数据成功,数据长度{len(data)}")
        # data = pd.read_csv("corpus.csv", encoding='utf-8',  names=['question'])
        data = data.dropna()
        LOGGER.info(f"处理后数据长度{len(data)}")
        tokenizer = AutoTokenizer.from_pretrained("rocketqa-zh-base-query-encoder")
        LOGGER.info(f"导入模型成功")
        # id2corpus = read_text("corpus.csv")
        corpus_list = [{idx: text} for idx, text in enumerate(data['question'])]
        embeddings = PREDICTOR.predict(corpus_list, tokenizer)
        LOGGER.info(f"推理成功")
        milvus_data_insert(data,embeddings,batch_size=batch_size,collection_name=collection_name, company_id=company_id, vecToMilvus=MILVUS_CLI)
        LOGGER.info(f"插入成功")
        LOGGER.info(f"Successfully loaded data, total count: {len(data)}")
        return {'status': True, 'msg': f"Successfully loaded data: {len(data)}"}
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}


# @app.get('/qa/search')
# async def do_get_question_api(question: str, table_name: str = None):
#     try:
#         questions, _= do_search(table_name, question, MODEL, MILVUS_CLI, MYSQL_CLI)
#         LOGGER.info("Successfully searched similar images!")
#         return {'status': True, 'msg': questions}, 200
#     except Exception as e:
#         LOGGER.error(e)
#         return {'status': False, 'msg': e}, 400
 

@app.get('/qa/answer')
async def do_get_answer_api(question: str, company_id:str):
    try:
        time_start = time.time()
        questions = [{1:question}]
        # questions = [question]
        tokenizer = AutoTokenizer.from_pretrained("rocketqa-zh-base-query-encoder")
        embeddings = PREDICTOR.predict(questions,tokenizer)
        time_end = time.time()
        sum_t = time_end - time_start
        print("predict time cost", sum_t, "s")
        results = milvus_data_search(query_embedding=embeddings, collection_name=collection_name, company_id=company_id, vecToMilvus=MILVUS_CLI)
        time_end = time.time()
        sum_t = time_end - time_start
        print("search time cost", sum_t, "s")
        return {'status': True, 'msg': results}
    except Exception as e:
        LOGGER.error(e)
        e = [e]
        return {'status': False, 'msg': e}


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8000)
