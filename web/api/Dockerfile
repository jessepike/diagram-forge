FROM python:3.11-slim
WORKDIR /app
COPY . /app/repo
WORKDIR /app/repo
RUN pip install --no-cache-dir -r web/api/requirements.txt
CMD ["uvicorn", "web.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
