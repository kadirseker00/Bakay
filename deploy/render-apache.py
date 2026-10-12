"""Mevcut HTTPS VirtualHost'un proxy hedeflerini günceller; TLS yollarını korur."""
from pathlib import Path
import re
import sys


def render(configuration: str, proxy: str) -> str:
    pattern = re.compile(r"(<VirtualHost\s+[^>]*:443[^>]*>)(.*?)(</VirtualHost>)", re.I | re.S)
    matches = list(pattern.finditer(configuration))
    if len(matches) != 1:
        raise ValueError("Tam bir HTTPS VirtualHost bekleniyor; yapılandırma elle incelenmeli.")
    match = matches[0]
    body = re.sub(r"\n?# BAKAY_PROXY_BEGIN\n.*?# BAKAY_PROXY_END\n?", "\n", match.group(2), flags=re.S)
    body = re.sub(
        r"^[ \t]*(?:ProxyPassReverse|ProxyPass|ProxyRequests|ProxyPreserveHost)\b[^\n]*\n?",
        "", body, flags=re.M,
    )
    body = re.sub(
        r"^[ \t]*RequestHeader\s+set\s+X-Forwarded-Proto\b[^\n]*\n?",
        "", body, flags=re.M | re.I,
    )
    block = match.group(1) + body.rstrip() + "\n\n" + proxy.rstrip() + "\n" + match.group(3)
    return configuration[:match.start()] + block + configuration[match.end():]


if __name__ == "__main__":
    site_path, proxy_path = map(Path, sys.argv[1:])
    result = render(site_path.read_text(), proxy_path.read_text())
    site_path.write_text(result)
