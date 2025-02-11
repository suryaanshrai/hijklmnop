FROM python:3.12
WORKDIR /app

COPY pyproject.toml .
COPY poetry.lock .
RUN pip install poetry 
RUN poetry config virtualenvs.create false && poetry lock && poetry install --no-root

COPY app .
CMD ["uvicorn", "app.main:app", "--reload", "--host=0.0.0.0"]