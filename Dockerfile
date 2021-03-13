################################################################################
FROM snakepacker/python:all AS builder

RUN python3.9 -m venv /usr/share/python3/urlcut
RUN /usr/share/python3/urlcut/bin/pip install -U pip

ADD requirements.txt /tmp/

RUN /usr/share/python3/urlcut/bin/pip install -Ur /tmp/requirements.txt --no-cache-dir

COPY dist/ /tmp/

RUN /usr/share/python3/urlcut/bin/pip install /tmp/urlcut* && /usr/share/python3/urlcut/bin/pip check

################################################################################
FROM snakepacker/python:3.9 AS release

COPY --from=builder /usr/share/python3/urlcut /usr/share/python3/urlcut
RUN ln -snf /usr/share/python3/urlcut/bin/urlcut* /usr/bin/

CMD ["urlcut"]
