#milvus参数
collection_name = "faq_finance"
collection_name_test = "faq_test_recall"
embedding_name = "embeddings"
MILVUS_HOST = "103.116.120.27"
MILVUS_PORT = 19530
#mysql参数
MYSQL_HOST = "103.116.120.29"
MYSQL_PORT = 3309
MYSQL_USER = "root"
MYSQL_PASSWORD = "Thinkit@2019"
MYSQL_DATABASE = "incs_db"

#向量最长度
data_dim = 256
#文本最长度
question_max_len = 200
answer_max_len = 4024
#top
top_k = 1
#索引参数
index_config = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 1000},
}
#搜索参数
search_params = {
    "metric_type": "L2",
    "params": {"nprobe": top_k},
}