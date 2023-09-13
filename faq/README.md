<!-- # 构建milvus镜像 -->
<!-- docker build -t milvus:0.1 . -->

# 导出镜像
docker save 0906db66bd00 > milvus.tar

# 导入镜像
docker load --input milvus.tar

# 修改tag和库
docker tag 1234567890ab milvusdb/milvus:v2.2.5

# 启动milvus的指令
docker compose up -d

# 关闭milvus的指令
docke compose down

# 启动Milvus Insight的指令
docker run -p 8800:3000 -e HOST_URL=http://103.116.120.27:8800 -e MILVUS_URL=103.116.120.27:19530 milvusdb/milvus-insight:latest

# 启动Http应用
uvicorn web_server:app --host '0.0.0.0' --port 8082 --reload