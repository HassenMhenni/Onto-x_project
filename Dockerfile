FROM python:3.12.3

WORKDIR /app

COPY data/onto_x.csv ./data/
COPY app/ app/
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

