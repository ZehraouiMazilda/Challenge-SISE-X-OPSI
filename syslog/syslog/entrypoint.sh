#!/bin/bash
set -euo pipefail

mkdir -p /var/log/firewall
touch /var/log/brut.log /var/log/firewall/firewall.log

service ssh start

exec "$@"

