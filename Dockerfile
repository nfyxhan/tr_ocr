FROM  ubuntu:18.04 as builder
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    libsm6 libxext6 libxrender-dev && \ 
  apt-get autoclean && rm -rf /var/lib/apt/lists/* 
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /workdir
ADD requirements.txt .
ADD setup.py .
ADD tr  tr
RUN python3 -m venv /opt/venv
RUN pip3 install -r requirements.txt --no-cache-dir
RUN python3 setup.py install

FROM  ubuntu:18.04
ENV  LANGUAGE zh_CN.UTF-8
ENV  LANG zh_CN.UTF-8
ENV  LC_ALL zh_CN.UTF-8
RUN apt-get update && apt-get install -y \
    git curl vim \
    locales \
    python3 \
    libsm6 libxext6  libgomp1  libglib2.0-dev && \ 
  apt-get autoclean && rm -rf /var/lib/apt/lists/* && \
  locale-gen zh_CN && \
  locale-gen zh_CN.UTF-8

COPY --from=builder /opt/venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /workdir
ADD tr  tr
ADD imgs imgs
ADD main.py .
CMD python3 ./main.py
