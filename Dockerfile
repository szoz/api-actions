FROM python:3.10-slim

WORKDIR /app

RUN pip install pipenv
COPY Pipfile.lock .
RUN pipenv sync

COPY . .

CMD ["pipenv", "run", "python", "main.py"]
