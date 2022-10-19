FROM python:3.9.7-slim-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

WORKDIR /
#COPY .env /src
#COPY requirements.txt /src
COPY ./ /
RUN pip install -r requirements.txt

#CMD ["python", "app.py"]
