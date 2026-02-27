FROM ubuntu:22.04

# Install SSH and common tools (Removed rsyslog)
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    iproute2 \
    iptables \
    net-tools \
    vim \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Setup SSH server
RUN mkdir /var/run/sshd
RUN echo 'root:password' | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22

# Touch the log file so it exists for tailing, then run SSHD forcing logs to that file
CMD touch /var/log/auth.log && /usr/sbin/sshd -D -E /var/log/auth.log   