FROM python:3.14.0rc1-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]