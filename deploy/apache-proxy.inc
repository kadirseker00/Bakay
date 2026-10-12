# BAKAY_PROXY_BEGIN
# /etc/apache2/sites-available/bakai.conf içindeki HTTPS VirtualHost'a eklenir.
# Önce aynı VirtualHost'taki eski ProxyPass/ProxyPassReverse satırlarını kaldırın.
# ServerName ve çalışan TLS sertifikası yolları mevcut yapılandırmadan korunur.
ProxyRequests Off
ProxyPreserveHost On
ProxyAddHeaders On
# İstemcinin sahte IP zinciri kaldırılır; mod_proxy gerçek bağlantı IP'sini ekler.
RequestHeader unset X-Forwarded-For
RequestHeader unset Forwarded
RequestHeader set X-Forwarded-Proto "https"

# Küçük JSON istekleri: yavaş bağlantı ve büyük gövdeyi uygulamadan önce durdur.
RequestReadTimeout header=20-40,MinRate=500 body=10-20,MinRate=500
<Location /api/>
    LimitRequestBody 131072
</Location>

# Daha özel /api/ kuralı, genel / kuralından önce gelmelidir.
ProxyPass        /api/ http://127.0.0.1:8000/ connectiontimeout=5 timeout=300
ProxyPassReverse /api/ http://127.0.0.1:8000/
ProxyPass        /     http://127.0.0.1:3000/ connectiontimeout=5 timeout=60
ProxyPassReverse /     http://127.0.0.1:3000/
# BAKAY_PROXY_END
