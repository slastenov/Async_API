FROM python:3.8.10

WORKDIR /srv/www/movies
COPY requirements/prod.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r prod.txt

COPY . .

EXPOSE 8000

CMD  python src/main.py