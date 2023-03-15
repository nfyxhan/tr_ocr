FROM  ubuntu:18.04
ENV  LANGUAGE zh_CN.UTF-8
ENV  LANG zh_CN.UTF-8
ENV  LC_ALL zh_CN.UTF-8
RUN apt-get update && apt-get install -y \
    git curl vim \
    locales \
    python3 python3-pip \
    libsm6 libxext6 libxrender-dev && \
  locale-gen zh_CN && \
  locale-gen zh_CN.UTF-8

WORKDIR /workdir

# git clone https://github.com/myhub/tr.git 
# git clonehttps://github.com/alisen39/TrWebOCR.git

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD setup.py .
ADD tr  tr
RUN python3 setup.py install
ADD imgs imgs

ADD main.py
CMD python3 ./main.py
