FROM python

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY reqs.txt .

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -r reqs.txt

COPY . .

CMD ["python", "run.py"]