FROM python:3-alpine
WORKDIR /app
COPY requirements.txt ./
RUN apk add git && pip install --no-cache-dir -r requirements.txt
COPY git-release-notifier.py ./
CMD ["python", "git-release-notifier.py"]