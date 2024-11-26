# syntax=docker/dockerfile:1

FROM kalilinux/kali-rolling

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
    medusa \
    masscan 

RUN git clone https://github.com/robertdavidgraham/masscan.git --depth 1 && \
    cd masscan && \
    make -j && \
    make install

RUN git clone https://salsa.debian.org/pkg-security-team/medusa.git --depth 1 && \
    cd medusa && \
    ./configure

RUN git clone https://github.com/aflnet/aflnet.git --depth 1

RUN git clone https://gitlab.com/akihe/radamsa.git --depth 1 && \
    cd radamsa && \
    make && \
    make install




