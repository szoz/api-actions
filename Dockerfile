FROM python:3.10

WORKDIR /app

RUN pip install pipenv
COPY Pipfile.lock .
RUN pipenv sync

COPY main.py .

EXPOSE 5000

CMD ["pipenv", "run", "python", "main.py"]
