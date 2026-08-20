FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py binance_fund.py notifications.py solar_validation.py ./

CMD ["python", "main.py"]
