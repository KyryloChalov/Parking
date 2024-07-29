FROM python:3.11.9-slim

LABEL authors="Imagine Pythons Team"

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY poetry.lock $APP_HOME/poetry.lock
COPY pyproject.toml $APP_HOME/pyproject.toml


RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --only main


COPY . .


EXPOSE 8000

# CMD ["poetry", "update", "package"]
ENTRYPOINT ["uvicorn","main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 