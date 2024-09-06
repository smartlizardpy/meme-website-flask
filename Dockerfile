FROM python:3.9

WORKDIR /app

COPY reqs.txt . 

RUN pip install --no cach-dir -r reqs.txt

COPY . .

EXPOSE 5000

CMD ["python", "mainpy"]

