FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
# Install packages and the spaCy language model
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_sm

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]