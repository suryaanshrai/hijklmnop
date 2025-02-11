FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry 

COPY . .

RUN poetry config virtualenvs.create false && poetry lock && poetry install --no-root

CMD ["uvicorn", "app.main:app", "--reload", "--host=0.0.0.0"]