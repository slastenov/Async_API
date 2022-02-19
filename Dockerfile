FROM python:3.8.10

WORKDIR /srv/www/movies
COPY requirements/prod.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r prod.txt

COPY . .

EXPOSE 8000

CMD  ["gunicorn", "--chdir", "src/", "src.main:app", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]
