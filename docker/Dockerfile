FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=US/Eastern

RUN apt update && apt update
RUN apt install -y curl software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt update
RUN apt install -y git \
    python3.7 \
    python3-pip \
    python3.7-dev \
    libbz2-dev \
    libffi-dev \
    libreadline-dev \
    libssl-dev \
    libsqlite3-dev \
    libblas-dev \
    liblapack-dev

# Set a virtual environment to isolate usage of pip 3.7
RUN python3.7 -m pip install virtualenv && python3.7 -m virtualenv rootenv && \
  . rootenv/bin/activate && pip install --upgrade pip setuptools wheel

# Install packages in environment
RUN . rootenv/bin/activate && pip install \
    ipython \
    keras==2.6.0 \
    kymatio==0.2.1 \
    matplotlib==3.4.3 \
    nltk==3.6.5 \
    numpy==1.19.5 \
    pandas==1.3.3 \
    Pillow==8.4.0 \
    progressbar33==2.4 \
    scikit_learn==1.0.1 \
    scipy==1.7.1 \
    seaborn==0.11.2 \
    torch==1.10.0 \
    transformers==4.12.2 \
    umap==0.1.1 \
    wordcloud==1.8.1 \
    # Split up literally only because it exhausts my docker runtime's memory to do this all at once
    # (torch & tensor chonky)
    wordninja==2.0.0 && pip install \
    spams==2.6.2.5 \
    tensorflow==1.15 \
    'tensorflow_hub>=0.6.0' \
    tensorflow_text==1.15 && pip install h5py==2.10.0

RUN mkdir -p /content/module_useT
RUN git clone https://github.com/ayaanzhaque/SDCNL.git
RUN echo ". /rootenv/bin/activate" >> /root/.bashrc && chmod 755 /root/.bashrc
RUN echo 'alias ll="ls -l"' >> /root/.bashrc && chmod 755 /root/.bashrc
COPY sdcnl/*.py SDCNL
