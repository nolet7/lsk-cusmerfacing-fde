FROM python:3.12-slim
WORKDIR /opt/lsk
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY frontend ./frontend
RUN useradd --uid 10001 --create-home appuser
USER appuser
EXPOSE 18641
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","18641"]
