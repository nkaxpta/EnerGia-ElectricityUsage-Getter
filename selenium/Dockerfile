FROM python:3

RUN apt-get update && \
    apt-get install -y locales && \
    locale-gen ja_JP.UTF-8 && \
    localedef -f UTF-8 -i ja_JP ja_JP && \
    echo "export LANG=ja_JP.UTF-8" >> ~/.bash_profile && \
    echo "export LANGUAGE=ja_JP:jp" >> ~/.bash_profile && \
    echo "export LC_ALL=ja_JP.UTF-8" >> ~/.bash_profile

ENV PYTHONIOENCODING utf-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

WORKDIR /workspace

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt && \
    echo "export PS1='\[\033[32m\]\u@\h \[\033[33m\]\w \[\033[0m\]$ '" >> ~/.bashrc
