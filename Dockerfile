# === setup python ===
FROM python:3.7.0 as setup
WORKDIR /app

COPY ./mipsplusplus ./mipsplusplus
COPY ./tests ./tests
COPY ./examples ./examples
COPY setup.py README.md LICENSE.txt ./

RUN python -m pip install -e .
