# Human++ Dockerfile sample
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN python -m compileall .
CMD ["python", "samples/app.py"]
