import ipaddress
from urllib.parse import urlsplit, parse_qs

def initiation_url(value):
    url = urlsplit(value)
    host = (url.hostname or '').lower()
    if url.scheme != 'https' or not host or url.username or url.password or url.fragment or url.port not in (None,443):
        raise ValueError('Asiointilinkin on oltava pysyvä HTTPS-osoite ilman tunnuksia tai fragmenttia')
    if (host == 'localhost' or host.endswith(('.localhost','.invalid','.test','.example'))
            or any(host == domain or host.endswith('.'+domain) for domain in ('example.com','example.org','example.net'))):
        raise ValueError('Esimerkkiverkkotunnus ei ole käytettävä myöntämispalvelu')
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError('Sisäverkon osoite ei ole julkinen asiointilinkki')
    except ValueError as error:
        if 'Sisäverkon' in str(error):raise
    query = parse_qs(url.query, keep_blank_values=True)
    if set(query) - {'product','profile','configuration'} or len(value)>2048:
        raise ValueError('Asiointilinkkiin sallitaan vain julkiset product/profile/configuration-tunnisteet, ei tarjouksia tai tokeneita')
    if any(len(v)>256 for values in query.values() for v in values):
        raise ValueError('Liian pitkä julkinen tunniste')
    return value


