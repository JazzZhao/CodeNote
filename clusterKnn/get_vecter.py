import argparse

import numpy as np
from feature_extract import Predictor
from paddlenlp.transformers import AutoTokenizer
import data
from sklearn.cluster import  KMeans
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--batch_size", default=32, type=int, help="Batch size per GPU/CPU for training.")
parser.add_argument("--precision", default="fp32", type=str, choices=["fp32", "fp16", "int8"], help='The tensorrt precision.')
parser.add_argument('--device', choices=['cpu', 'gpu', 'xpu'], default="cpu", help="Select which device to train model, defaults to cpu.")
parser.add_argument("--model_dir", default="./model", type=str, required=True, help="The directory to static model.")
parser.add_argument('--model_name_or_path', default="rocketqa-zh-base-query-encoder", help="The pretrained model used for training")
parser.add_argument("--corpus_file", type=str, required=True, help="The corpus_file path.")
parser.add_argument('--cpu_threads', default=10, type=int, help='Number of threads to predict when using cpu.')
parser.add_argument('--enable_mkldnn', default=False, type=eval, choices=[True, False], help='Enable to use mkldnn to speed up when using cpu.')
parser.add_argument('--use_tensorrt', default=False, type=eval, choices=[True, False], help='Enable to use tensorrt to speed up.')
parser.add_argument("--max_seq_length", default=64, type=int, help="The maximum total input sequence length after tokenization. Sequences longer than this will be truncated, sequences shorter will be padded.")
parser.add_argument("--n_clusters", default=10, type=int, help="k-means class number")

args = parser.parse_args()


if __name__ == "__main__":
    predictor = Predictor(
        args.model_dir,
        args.device,
        args.max_seq_length,
        args.batch_size,
        args.use_tensorrt,
        args.precision,
        args.cpu_threads,
        args.enable_mkldnn,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
    #读取corpus
    id2corpus = data.gen_id2corpus(args.corpus_file)
    corpus_list = [{idx: text} for idx, text in id2corpus.items()]
    def gen_corpus(corpus_file):
        corpus = []
        with open(corpus_file, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                corpus.append( line.rstrip())
        return corpus
    data_corpus = gen_corpus(args.corpus_file)
    #获取词向量
    embeddings = predictor.predict(corpus_list, tokenizer)
    #聚类
    cluster = KMeans(n_clusters=args.n_clusters,random_state=0).fit(embeddings)
    #结果导出
    result = pd.DataFrame(data_corpus)
    result['label'] = cluster.labels_
    result.to_excel("result.xlsx")
