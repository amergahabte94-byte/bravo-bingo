FROM python:3.11-slim

WORKDIR /app

# ቴሌግራም ላይብራሪዎችን በቀጥታ እዚህ እንጭናለን
RUN pip install --no-cache-dir python-telegram-bot

COPY . .

CMD ["python", "main.py"]

