FROM ubuntu:22.04

# Install SSH and common tools
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

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
