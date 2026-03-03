param(
  [Parameter(Mandatory = $true)]
  [string]$Ip
)

$conf = Join-Path $PSScriptRoot 'rsyslog_ip.conf'
(Get-Content -Raw $conf).Replace('__SYSLOG_NG_IP__', $Ip) | Set-Content -Encoding UTF8 $conf
Write-Host "rsyslog_ip.conf updated with SYSLOG IP: $Ip"

