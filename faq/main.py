import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from predict import Predictor
from milvus_utils import VecToMilvus
from logs import LOGGER
import time
import pandas as pd
from service import (
    milvus_data_search,
    milvus_data_insert
)
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
batch_size = 1

# 在全局定义 PREDICTOR 对象
PREDICTOR = None
MILVUS_CLI = None

@app.on_event("startup")
def load_predictor():
    global PREDICTOR
    global MILVUS_CLI
    # 加载模型
    PREDICTOR = Predictor("checkpoints/epoch002_valacc0.525_ckpt.tar", batch_size=batch_size)
    # 加载milvus
    MILVUS_CLI = VecToMilvus()

@app.get('/qa/update_data')
def do_load_api(file_name: str,company_id:str):
    try:
        #暂时从文件导入，后期做成从mongo数据库中导入
        data = pd.read_excel(file_name, names=['question', 'answer'], index_col=False)
        data = data.dropna()
        embeddings = PREDICTOR.predict(data['question'].tolist())
        milvus_data_insert(data,embeddings,batch_size=batch_size,collection_name=collection_name, company_id=company_id, vecToMilvus=MILVUS_CLI)
        LOGGER.info(f"Successfully loaded data, total count: {len(data)}")
        return {'status': True, 'msg': f"Successfully loaded data: {len(data)}"}, 200
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}, 400


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
        questions = [question]
        embeddings = PREDICTOR.predict(questions,False)
        results = milvus_data_search(query_embedding=embeddings, collection_name=collection_name, company_id=company_id, vecToMilvus=MILVUS_CLI)
        time_end = time.time()  
        sum_t = time_end - time_start
        print("search time cost", sum_t, "s") 
        return {'status': True, 'msg': results},200
    except Exception as e:
        LOGGER.error(e)
        return {'status': False, 'msg': e}


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8000)