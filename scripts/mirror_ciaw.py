#!/usr/bin/env python3
"""Copia la web pública ciaw.es y sus recursos. No configura CNAME."""
import hashlib
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

BASE = 'https://ciaw.es/'
DOMAINS = {'ciaw.es', 'www.ciaw.es'}
ROOT = Path(__file__).resolve().parent.parent
session = requests.Session()
session.headers.update({'User-Agent':'Mozilla/5.0 (compatible; CIAW-Website-Backup/1.0)'})
cache = {}
bytes_total = 0
MAX_BYTES = 160_000_000
URL_RE = re.compile(r'url\(\s*([\'\"]?)([^)\'\"]+)\1\s*\)', re.I)
IMPORT_RE = re.compile(r'(@import\s+[\'\"])([^\'\"]+)([\'\"])', re.I)

def fetch(url):
    global bytes_total
    r = session.get(url, timeout=45)
    r.raise_for_status()
    content = r.content
    if len(content) > 45_000_000 or bytes_total + len(content) > MAX_BYTES:
        raise ValueError('Límite de tamaño para recursos estáticos superado')
    bytes_total += len(content)
    return content, r.headers.get('Content-Type', '')

def path_for(url, content_type):
    parsed = urlsplit(url)
    name = unquote(parsed.path).lstrip('/')
    parts = [x for x in name.split('/') if x and x not in {'.', '..'}]
    if not parts:
        parts = ['assets', 'unnamed']
    dest = Path(*parts)
    if not dest.suffix:
        ext = mimetypes.guess_extension(content_type.split(';')[0]) or '.bin'
        dest = dest.with_suffix(ext)
    if parsed.query:
        digest = hashlib.sha256(url.encode()).hexdigest()[:10]
        dest = dest.with_name(dest.stem + '-' + digest + dest.suffix)
    return dest

def asset(raw, parent=BASE):
    if not raw or raw.startswith(('#','data:','blob:','javascript:','mailto:','tel:')):
        return None
    absolute = urljoin(parent, raw)
    parsed = urlsplit(absolute)
    if parsed.scheme not in ('http','https') or parsed.hostname not in DOMAINS:
        return None
    if absolute in cache:
        return cache[absolute]
    if len(cache) >= 160:
        print('Límite de recursos alcanzado:', raw)
        return None
    try:
        content, content_type = fetch(absolute)
        if 'text/html' in content_type:
            return None
        dest = path_for(absolute, content_type)
        cache[absolute] = dest
        if dest.suffix.lower() == '.css':
            content = patch_css(content.decode('utf-8-sig', errors='replace'), absolute, dest).encode('utf-8')
        target = ROOT / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        print('Guardado:', absolute, '→', dest, len(content), 'bytes')
        return dest
    except Exception as e:
        print('AVISO: No se pudo recuperar', absolute, e)
        return None

def patch_css(css, css_url, css_path):
    def replace_url(match):
        raw = match.group(2).strip()
        target = asset(raw, css_url)
        if target:
            relative = os.path.relpath(target, css_path.parent).replace(os.sep, '/')
            return 'url("' + relative + '")'
        return match.group(0)
    css = URL_RE.sub(replace_url, css)
    def replace_import(match):
        target = asset(match.group(2), css_url)
        if target:
            relative = os.path.relpath(target, css_path.parent).replace(os.sep, '/')
            return match.group(1) + relative + match.group(3)
        return match.group(0)
    return IMPORT_RE.sub(replace_import, css)

def change(tag, attribute, base=BASE):
    raw = tag.get(attribute)
    if not raw:
        return
    target = asset(raw, base)
    if target:
        tag[attribute] = target.as_posix()

def srcset(tag):
    old = tag.get('srcset')
    if not old:
        return
    elements = []
    for part in old.split(','):
        fields = part.strip().split()
        if fields:
            target = asset(fields[0])
            elements.append(' '.join([target.as_posix() if target else fields[0], *fields[1:]]))
    tag['srcset'] = ', '.join(elements)

def main():
    response = session.get(BASE, timeout=45)
    response.raise_for_status()
    html = response.text
    if len(html) < 3000 or '<html' not in html.lower():
        raise RuntimeError('El sitio no devolvió un HTML completo; se conserva la copia.')
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup.find_all(['img','script','source','video','audio','iframe']):
        for key in ('src', 'poster'):
            change(tag, key)
        srcset(tag)
    for tag in soup.find_all('link'):
        rel = ' '.join(tag.get('rel') or []).lower()
        if any(x in rel for x in ('stylesheet','icon','preload','manifest','modulepreload')):
            change(tag, 'href')
    for tag in soup.find_all('a', href=True):
        parsed = urlsplit(urljoin(BASE, tag['href']))
        if parsed.hostname in DOMAINS and parsed.path.lower().endswith(('.pdf','.webp','.png','.jpg','.jpeg','.svg','.zip','.docx','.xlsx')):
            change(tag,'href')
    for tag in soup.find_all(attrs={'style':True}):
        tag['style'] = patch_css(tag['style'], BASE, Path('index.html'))
    for style in soup.find_all('style'):
        if style.string:
            style.string.replace_with(patch_css(str(style.string), BASE, Path('index.html')))
    for meta in soup.find_all('meta'):
        if meta.get('property') in ('og:image','twitter:image') and meta.get('content'):
            change(meta,'content')
    document = str(soup)
    if not document.lstrip().lower().startswith('<!doctype'):
        document = '<!doctype html>\n' + document
    (ROOT / 'index.html').write_text(document, encoding='utf-8')
    (ROOT / '.nojekyll').touch()
    # No se crea CNAME: transferir el dominio será un paso independiente.
    print(f'Copia creada: {len(cache)} recursos; {bytes_total/1_000_000:.1f} MB; index {len(document)} caracteres')

if __name__ == '__main__':
    main()
