# 构建kmeans镜像
docker build -t kmeans:0.1 .

# 导出镜像
docker save 0906db66bd00 > kmeans.tar

# 导入镜像
docker load --input kmeans.tar

# 启动kmeans镜像
docker run -p 8081:80 -d --env USER_PASSWD="123456" -v C:/Users/zjt78/Documents/CodeNote/clusterKnn:/home/jovyan/work kmeans:0.1

# 进入镜像
docker exec -it /bin/bash