FROM registry.baidubce.com/paddlepaddle/paddle:2.4.2-jupyter

COPY requirements.txt requirements.txt

RUN pip install -i https://pypi.douban.com/simple -r requirements.txt

WORKDIR /home/jovyan

ENV PYTHONPATH="${PYTHONPATH}:/home/jovyan/work"