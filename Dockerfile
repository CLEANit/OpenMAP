FROM python:3.8
RUN mkdir /app
WORKDIR /app

RUN pip install poetry
RUN poetry config settings.virtualenvs.create false
COPY poetry.lock pyproject.toml README.md /app/

# to prevent poetry from installing my actual app,
# and keep docker able to cache layers
RUN mkdir -p /app/src/app
RUN touch /app/src/app/__init__.py

RUN poetry install -n

# now actually copy the real contents of my app
COPY app /app/src/app

EXPOSE 8000
CMD ["gunicorn", "-c", "docker/services/gunicorn/conf.py", "--bind", ":8000", "--chdir", "src/app", "core.wsgi:application"]