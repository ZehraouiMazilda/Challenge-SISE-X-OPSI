#!/bin/bash
set -u

if [ -n "${SYSLOG_SERVER_IP:-}" ]; then
  sed -i "s/__SYSLOG_NG_IP__/${SYSLOG_SERVER_IP}/g" /etc/rsyslog.d/rsyslog_ip.conf
fi

mkdir -p /var/log/ulog
touch /var/log/ulog/iptables_ulogd2.log /var/log/ulog/syslogemu.log /var/log/opsie.log /var/log/ulog/ulogd-start.log /var/log/ulog/rsyslog-start.log

# Bloc services de notre stack OPSIE
# 20:21 FTP, 22 SSH, 23 Telnet, 80 HTTP, 3306 uniquement en local
mkdir -p /var/www/html/Backup /var/www/html/Restore
if [ ! -f /var/www/html/index.html ]; then
  cat > /var/www/html/index.html <<'EOF'
<html><body><h1>OPSIE Challenge Firewall Service</h1></body></html>
EOF
fi

# Service HTTP
service apache2 start >/dev/null 2>&1 || apachectl start >/dev/null 2>&1 || true

# Service FTP (port 21)
if [ ! -f /etc/vsftpd.conf ] || ! grep -q "opsie-managed" /etc/vsftpd.conf 2>/dev/null; then
  cat > /etc/vsftpd.conf <<'EOF'
# opsie-managed
listen=YES
listen_ipv6=NO
anonymous_enable=NO
local_enable=YES
write_enable=YES
local_umask=022
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
chroot_local_user=YES
allow_writeable_chroot=YES
pam_service_name=vsftpd
secure_chroot_dir=/var/run/vsftpd/empty
EOF
fi

id ftpuser >/dev/null 2>&1 || useradd -m -s /bin/bash ftpuser
echo "ftpuser:ftp123" | chpasswd
pkill -f "vsftpd" 2>/dev/null || true
nohup /usr/sbin/vsftpd /etc/vsftpd.conf >/var/log/ulog/vsftpd-start.log 2>&1 &

# Listeners simples pour la joignabilite des ports 20 et 23
pkill -f "nc -l -k -p 20" 2>/dev/null || true
pkill -f "nc -l -k -p 23" 2>/dev/null || true
nohup nc -l -k -p 20 >/var/log/ulog/port20.log 2>&1 &
nohup nc -l -k -p 23 >/var/log/ulog/port23.log 2>&1 &

# MySQL local only (127.0.0.1)
if [ -f /etc/mysql/mariadb.conf.d/50-server.cnf ]; then
  sed -i 's/^[#[:space:]]*bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mariadb.conf.d/50-server.cnf
fi
service mysql start >/dev/null 2>&1 || service mariadb start >/dev/null 2>&1 || true

# Demarrage SSH
/usr/sbin/sshd || true

# Demarrage ulogd en arriere-plan
ULOGD_BIN=""
if command -v ulogd >/dev/null 2>&1; then
  ULOGD_BIN="$(command -v ulogd)"
elif command -v ulogd2 >/dev/null 2>&1; then
  ULOGD_BIN="$(command -v ulogd2)"
fi

if [ -n "${ULOGD_BIN}" ]; then
  pkill -f "${ULOGD_BIN}" 2>/dev/null || true
  nohup "${ULOGD_BIN}" -c /etc/ulogd.conf >/var/log/ulog/ulogd-start.log 2>&1 &
else
  echo "[entrypoint] warning: ulogd binary not found" | tee -a /var/log/ulog/ulogd-start.log
fi

# Demarrage rsyslog en arriere-plan
pkill -f rsyslogd 2>/dev/null || true
nohup rsyslogd -n >/var/log/ulog/rsyslog-start.log 2>&1 &

sleep 1

if ! iptables-restore < /root/newip2.rules; then
  echo "[entrypoint] warning: iptables-restore failed, applying fallback NFLOG rules"
  iptables -F INPUT || true
  iptables -P INPUT ACCEPT || true
  iptables -A INPUT -i eth0 -p tcp --dport 22 -m limit --limit 3/sec -j NFLOG --nflog-prefix "action=PERMIT RULE=1 " --nflog-group 1 || true
  iptables -A INPUT -i eth0 -p tcp -m multiport ! --dports 22,514 -j NFLOG --nflog-prefix "action=DENY RULE=999 " --nflog-group 1 || true
fi

if ! iptables -S | grep -q NFLOG; then
  echo "[entrypoint] warning: no NFLOG rules found, forcing minimal NFLOG rules"
  iptables -A INPUT -i eth0 -p tcp --dport 22 -m limit --limit 3/sec -j NFLOG --nflog-prefix "action=PERMIT RULE=1 " --nflog-group 1 || true
  iptables -A INPUT -i eth0 -p tcp -m multiport ! --dports 22,514 -j NFLOG --nflog-prefix "action=DENY RULE=999 " --nflog-group 1 || true
fi

echo "[entrypoint] iptables rules loaded:"
iptables -S
echo "[entrypoint] nflog rules:"
iptables -S | grep NFLOG || true

echo "[entrypoint] forwarding to syslog target configured in /etc/rsyslog.d/rsyslog_ip.conf"
echo "[entrypoint] rsyslog target line:"
grep -n "target=" /etc/rsyslog.d/rsyslog_ip.conf || true
echo "[entrypoint] ulogd startup log (tail):"
tail -n 20 /var/log/ulog/ulogd-start.log || true
echo "[entrypoint] rsyslog startup log (tail):"
tail -n 20 /var/log/ulog/rsyslog-start.log || true
echo "[entrypoint] service ports:"
ss -ltnup || true

exec "$@"
