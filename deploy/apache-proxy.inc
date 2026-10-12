# BAKAY_PROXY_BEGIN
# /etc/apache2/sites-available/bakai.conf içindeki HTTPS VirtualHost'a eklenir.
# Önce aynı VirtualHost'taki eski ProxyPass/ProxyPassReverse satırlarını kaldırın.
# ServerName ve çalışan TLS sertifikası yolları mevcut yapılandırmadan korunur.
ProxyRequests Off
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "https"

# Daha özel /api/ kuralı, genel / kuralından önce gelmelidir.
ProxyPass        /api/ http://127.0.0.1:8000/ connectiontimeout=5 timeout=300
ProxyPassReverse /api/ http://127.0.0.1:8000/
ProxyPass        /     http://127.0.0.1:3000/ connectiontimeout=5 timeout=60
ProxyPassReverse /     http://127.0.0.1:3000/
# BAKAY_PROXY_END
