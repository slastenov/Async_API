FROM python:3.8.10

WORKDIR /srv/www/postgres_elastic
COPY etl.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r etl.txt

COPY . .

CMD  python main.py