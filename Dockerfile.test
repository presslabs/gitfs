FROM ubuntu:18.04

ARG PYTHON=3.7

RUN apt-get update && \
    apt-get install -qy build-essential software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    add-apt-repository ppa:presslabs/gitfs && \
    apt-get update && \
    apt-get install -qy python-pip python-virtualenv python-dev libfuse-dev fuse git libffi-dev python${PYTHON}-dev libgit2-dev python3-pip

RUN if [ "$PYTHON" = "3.8" ] ; then apt-get install -qy python3.8-distutils; fi

COPY test_requirements.txt requirements.txt /
RUN if [ "$PYTHON" = "2.7" ] ; then pip install -r /test_requirements.txt; else pip3 install -r /test_requirements.txt; fi
