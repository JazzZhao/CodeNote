import time
import numpy as np
import tqdm
from config import (
    question_max_len,
    embedding_name
)

def milvus_data_search(query_embedding, collection_name, company_id, vecToMilvus, ):
    
    recall_result = []
    batch_query_embedding = query_embedding.tolist()
    result = vecToMilvus.search(batch_query_embedding,
                        embedding_name,
                        collection_name,
                        partition_tags=[company_id],
                        output_fields=["pk", "answer", "question"])
    for hits in result:
        for hit in hits:
            print(f"question field: {hit.entity.get('question')}, answer field: {hit.entity.get('answer')}, score: {hit.distance}")
            recall_result.append({"question":hit.entity.get('question'), "answer":hit.entity.get('answer'), "score":hit.distance})
    return recall_result

    #插入
def milvus_data_insert(data, embeddings, batch_size, collection_name, company_id, vecToMilvus):
    if vecToMilvus.has_collection(collection_name=collection_name):
        vecToMilvus.drop_collection(collection_name)
    data_size = data.shape[0]
    entities = [
            [j for j in range(0, data_size, 1)],
            data["question"].tolist(),
            data["answer"].tolist(),
            embeddings.tolist(),  # field embeddings, supports numpy.ndarray and list
        ]
    vecToMilvus.insert(
        collection_name=collection_name, entities=entities, index_name=embedding_name, partition_tag=company_id
    )
        
