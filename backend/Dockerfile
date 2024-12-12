FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OBGYM_CORE_HOST=localhost
ENV OBGYM_CORE_PORT=16999

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 16998

CMD ["python", "main.py"]
