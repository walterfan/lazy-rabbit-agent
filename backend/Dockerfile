FROM python:3.12-slim-bookworm

#RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && \
  apt-get install -y build-essential cmake libssl-dev

RUN pip install --upgrade pip

WORKDIR /app
COPY ./app /app
COPY ./requirements.txt /app/
#COPY ../pyproject.toml ../poetry.lock /app/
#RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple poetry && \
#    poetry config virtualenvs.create false && \
#    poetry install --no-interaction --no-ansi
RUN pip install -r requirements.txt
EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload"]
