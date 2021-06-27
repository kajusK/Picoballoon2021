FROM python:3

WORKDIR /project
ADD --chown=1000:1000 web /project
RUN pip install -r requirements.txt
CMD gunicorn app:app -w 2 --threads 2 -b 0.0.0.0:80
