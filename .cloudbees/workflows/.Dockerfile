# Use Ubuntu 18.04 as the base image
FROM ubuntu:18.04

# Update and upgrade the system
RUN apt update && apt upgrade -yuf

# Install dependencies
RUN apt-get install -y sudo \
    libsqlite3-dev \
    git \
    curl \
    vim \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    wget \
    libbz2-dev \
    pkg-config

# Set up Node.js (version 16.x)
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | sudo bash - && \
    sudo apt install -y nodejs

# Set up Yarn
RUN curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | sudo tee /usr/share/keyrings/yarnkey.gpg >/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list && \
    sudo apt update && sudo apt install yarn -y

# Download and build Python 3.11.5
RUN wget https://www.python.org/ftp/python/3.11.5/Python-3.11.5.tgz && \
    tar -xf Python-3.11.5.tgz && \
    cd Python-3.11.5 && \
    ./configure --enable-optimizations && \
    make -j 6 && \
    sudo make altinstall && \
    cd .. && \
    rm -rf Python-3.11.5 Python-3.11.5.tgz

# Upgrade pip for Python 3.11
RUN python3.11 -m pip install --upgrade pip

# Clone the SPMA repository
WORKDIR /root/SP
RUN git clone https://github.com/freshremix/SPMA.git

# Install Python dependencies
WORKDIR /root/SP/SPMA
RUN pip3.11 install -r requirements.txt

# Expose port 80
EXPOSE 80

# Run the application in the background
CMD python3.11 main.py & \
    python3.11 -m http.server 80
