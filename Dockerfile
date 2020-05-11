FROM python:3.6.1-alpine
WORKDIR /api
ADD . /api
RUN pip install -r requirements.txt
CMD ["python","singo"]
