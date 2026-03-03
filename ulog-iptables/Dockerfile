FROM ubuntu:focal-20231128

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    rsyslog \
    ulogd2 \
    iptables \
    apache2 \
    vsftpd \
    mariadb-server \
    netcat-openbsd \
    iproute2 \
    iputils-ping \
    net-tools \
    tcpdump \
    nmap \
    vim \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd /var/log/ulog

COPY rsyslog_ip.conf /etc/rsyslog.d/rsyslog_ip.conf
COPY ulogd.conf.in /tmp/ulogd.conf.in
COPY newip2.rules /root/newip2.rules
COPY entrypoint.sh /entrypoint.sh

RUN arch="$(dpkg --print-architecture)" && \
    case "$arch" in \
      amd64) multiarch="x86_64-linux-gnu" ;; \
      arm64) multiarch="aarch64-linux-gnu" ;; \
      *) multiarch="$arch-linux-gnu" ;; \
    esac && \
    sed "s#__ULOGD_PLUGIN_DIR__#/usr/lib/${multiarch}/ulogd#g" /tmp/ulogd.conf.in > /etc/ulogd.conf && \
    rm -f /tmp/ulogd.conf.in && \
    chmod +x /entrypoint.sh && \
    echo "root:toto" | chpasswd

EXPOSE 20 21 22 23 80 3306

ENTRYPOINT ["/entrypoint.sh"]
CMD ["tail", "-f", "/dev/null"]
