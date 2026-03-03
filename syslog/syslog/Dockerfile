FROM ubuntu:focal-20231128

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    syslog-ng \
    mysql-client \
    net-tools \
    ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd /var/log/firewall /etc/syslog-ng/patterndb.d

COPY sshd_config /etc/ssh/sshd_config
COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
COPY pattern_ulog.xml /etc/syslog-ng/patterndb.d/pattern_ulog.xml
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && echo "root:toto" | chpasswd

EXPOSE 22 514

ENTRYPOINT ["/entrypoint.sh"]
CMD ["syslog-ng", "-F"]
