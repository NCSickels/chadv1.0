# syntax=docker/dockerfile:1

# Work in progress - not yet fully functional
FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive
# FROM kalilinux/kali-rolling

WORKDIR /chadv1.0

# Install dependencies
RUN apt update -y && apt install -y \
    clang \
    graphviz-dev \
    libcap-dev \
    git \
    make \
    gcc \
    automake \
    autoconf \
    libssl-dev \
    wget \
    curl \
    dos2unix \
    php-cli \
    vim \
    tmux

RUN git clone https://github.com/robertdavidgraham/masscan.git --depth 1 && \
    cd masscan && \
    make -j && \
    make install

RUN git clone https://salsa.debian.org/pkg-security-team/medusa.git --depth 1 && \
    cd medusa && \
    ./configure

RUN git clone https://github.com/aflnet/aflnet.git --depth 1 && \
    export LLVM_CONFIG=/usr/bin/llvm-config-6.0 && \
    cd aflnet && \
    make clean all && \
    cd llvm_mode && \
    make && \
    cd .. && \
    mkdir in out && \
    cd in && \
    echo "masscan -p21-8180 192.168.1.100 --banners --packet-trace" > scan1.txt && \
    echo "masscan -p80,443 192.168.1.100 --banners" > scan2.txt && \
    echo "masscan -p1-65535 192.168.1.100 --reate=1000" > scan3.txt && \
    cd .. && \
    export AFLNET=$(pwd)/aflnet && \
    export WORKDIR=$(pwd) && \
    export PATH=$PATH:$AFLNET && \
    export AFL_PATH=$AFLNET
    
RUN git clone https://gitlab.com/akihe/radamsa.git --depth 1 && \
    cd radamsa && \
    make && \
    make install

RUN mkdir /chadv1.0/www && \
    cd /chadv1.0/www && \
    touch index.html && \
    echo "<h1>Radamsa - Chadv1.0</h1>" > index.html

COPY fuzzing/radamsa/www/http-request.txt /chadv1.0/www/http-request.txt

COPY fuzzing/repeat_medusa.sh /chadv1.0/repeat_medusa.sh

COPY fuzzing/password_list.txt /chadv1.0/password_list.txt

# Convert files to unix format
RUN dos2unix /chadv1.0/www/http-request.txt && \
    dos2unix /chadv1.0/repeat_medusa.sh && \
    dos2unix /chadv1.0/password_list.txt

RUN chmod +x /chadv1.0/repeat_medusa.sh

