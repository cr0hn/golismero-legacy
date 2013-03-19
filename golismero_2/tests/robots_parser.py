texto="""User-agent: *    # aplicable a todos
Disallow: /map     # impide la indexacion de estas paginas
Disallow: /static/js
Disallow: /static/img
Disallow: /static/fichero
Disallow:
Allow:
Allow: /hola
Disallow: /tmp
Disallow: /*uuid
Disallow: /*token
Disallow: /ayuda/chelp/
Disallow: /ayuda/appmanager/chelp
Disallow: /static/microsites


"""

import codecs

m_robots = texto

try:
    if m_robots.startswith(codecs.BOM_UTF8):
        m_robots = m_robots.decode('utf-8').lstrip(unicode(codecs.BOM_UTF8, 'utf-8'))
    elif m_robots.startswith(codecs.BOM_UTF16):
        m_robots = m_robots.decode('utf-16')
except UnicodeDecodeError:
    pass


m_return = []

for rawline in m_robots.splitlines():
    m_line = rawline

    # Remove comments
    m_octothorpe = m_line.find('#')
    if m_octothorpe >= 0:
        m_line = m_line[:m_octothorpe]

    # Throw away any trailing whitespace
    m_line = m_line.rstrip()

    # Silently ignore blank and comment lines
    if m_line == '' and ':' not in m_line:
        continue

    # Looks valid. Split and interpret it
    m_key, m_val = [x.strip() for x in m_line.split(':', 1)]
    m_key = m_key.lower()
    try:
        # If a wildcard found, is not a valid URL
        if '*' in m_val:
            continue

        if m_key in ('disallow', 'allow', 'sitemap') and m_val:
            m_return.append(val)
    except:
        pass



# Send info
print  m_return
