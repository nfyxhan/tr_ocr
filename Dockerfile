FROM  ubuntu:18.04 as builder
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    libsm6 libxext6 libxrender-dev libgomp1 libglib2.0-dev && \ 
  apt-get autoclean && rm -rf /var/lib/apt/lists/* && \
  python3 -m venv /opt/venv && \
  pip3 install wheel --no-cache-dir && \
  pip3 install pyinstaller --no-cache-dir
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /workdir
ADD requirements.txt .
ADD setup.py .
ADD tr  tr
ADD main.py .
RUN pip3 install -r requirements.txt --no-cache-dir  && \
    python3 setup.py install && \
    pyinstaller -F ./main.py

FROM  ubuntu:18.04
ENV  LANGUAGE zh_CN.UTF-8
ENV  LANG zh_CN.UTF-8
ENV  LC_ALL zh_CN.UTF-8
RUN apt-get update && apt-get install -y \
    git curl vim \
    locales && \ 
  apt-get autoclean && rm -rf /var/lib/apt/lists/* && \
  locale-gen zh_CN && \
  locale-gen zh_CN.UTF-8
  
WORKDIR /workdir
COPY --from=builder /workdir/dist/main /workdir/tr_ocr
ADD tr  tr
ADD imgs imgs
CMD ./tr_ocr
