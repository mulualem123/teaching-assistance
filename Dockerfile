# Dockerfile
FROM python:3.11.0
#FROM python:3.8-slim-buster

#WORKDIR /app
WORKDIR /python-docker

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

#EXPOSE 8000
#EXPOSE 8000/tcp
#EXPOSE 8000/udp
#EXPOSE 5000
#EXPOSE 5000/tcp
#EXPOSE 5000/udp

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]



