FROM python:3.10

ARG PYTHONUNBUFFERED=1

ARG WORKDIR=/workdir
ARG USER=user

WORKDIR ${WORKDIR}

RUN useradd --system ${USER} && \
    chown --recursive ${USER} ${WORKDIR}

RUN apt update && apt upgrade -y

COPY --chown=${USER} requirements.txt requirements.txt

RUN python3 -m venv venv

RUN pip install --upgrade pip && \
    pip install --requirement requirements.txt

COPY --chown=${USER} ./main_scraping.py main.py

USER ${USER}

CMD ["python", "main.py"]