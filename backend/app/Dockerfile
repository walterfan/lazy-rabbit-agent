FROM python:3.12-slim-bookworm

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && \
  apt-get install -y build-essential cmake libssl-dev

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip

WORKDIR /app
COPY . /app

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload"]
