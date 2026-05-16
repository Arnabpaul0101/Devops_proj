FROM python:3.13-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
COPY tests/ tests/

EXPOSE 5000

ENV FLASK_APP=run.py

CMD ["python", "run.py"]
