FROM snakepacker/python:all AS builder

RUN python3.7 -m venv /usr/share/python3/app

ADD requirements.txt /tmp/
RUN /usr/share/python3/app/bin/pip install -U pip

# bump this number for invalidating installing dependencies
# cache for following layers
ENV DOCKERFILE_VERSION 1

RUN /usr/share/python3/app/bin/pip install -Ur /tmp/requirements.txt

ADD dist/ /tmp/app/
RUN /usr/share/python3/app/bin/pip install /tmp/app/*

########################################################################
FROM snakepacker/python:3.7

RUN locale-gen en_US.UTF-8

COPY --from=builder /usr/share/python3/app /usr/share/python3/app
RUN ln -snf /usr/share/python3/app/bin/storyteller /usr/bin/

#CMD ["socket_web_server"]