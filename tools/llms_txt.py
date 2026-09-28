# -*- coding: utf-8 -*-
"""빌드가 끝난 뒤 llms.txt 를 만든다. AI 서비스가 사이트 구성을 한 번에 읽을 수 있게,
첫 화면에는 권 목록을, 권마다 모든 쪽의 제목·주소·설명을 적는다(llmstxt.org 형식)."""
import html, io, os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
BASE = 'https://urock-ailab.github.io/forensics-handbook/'
KS = ['windows', 'mac', 'linux', 'android', 'ios', 'cloud', 'network', 'crypto', 'ai']


def meta(path):
    s = io.open(path, encoding='utf-8').read()
    t = re.search(r'<title>(.*?)</title>', s, re.S)
    d = re.search(r'<meta name="description" content="(.*?)"', s)
    title = html.unescape(t.group(1)).split(' | ')[0].strip() if t else ''
    return title, html.unescape(d.group(1)) if d else ''


def local(url):
    rel = url[len(BASE):]
    p = os.path.join(SITE, *rel.split('/'))
    return os.path.join(p, 'index.html') if url.endswith('/') else p


home_title, home_desc = meta(os.path.join(SITE, 'index.html'))
top = [f'# {home_title}', '', f'> {home_desc}', '',
       '주식회사 유락이 만든 한국어 디지털 포렌식 핸드북입니다. 글은 CC BY 4.0 으로 공개합니다. '
       '권마다 모든 페이지의 제목·주소·설명을 적은 llms.txt 가 따로 있습니다.', '', '## 핸드북', '']
total = 0
for k in KS:
    sm = os.path.join(SITE, k, 'sitemap.xml')
    if not os.path.exists(sm):
        continue
    urls = re.findall(r'<loc>(.*?)</loc>', io.open(sm, encoding='utf-8').read())
    hb_title, hb_desc = meta(os.path.join(SITE, k, 'index.html'))
    site_name = re.search(r'<title>.*? \| (.*?)</title>', io.open(os.path.join(SITE, k, 'index.html'), encoding='utf-8').read())
    name = html.unescape(site_name.group(1)) if site_name else hb_title
    lines = [f'# {name}', '', f'> {hb_desc}', '', '## 페이지', '']
    for u in urls:
        p = local(u)
        if not os.path.exists(p):
            continue
        t, d = meta(p)
        lines.append(f'- [{t}]({u}): {d}' if d else f'- [{t}]({u})')
    io.open(os.path.join(SITE, k, 'llms.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
    total += len(lines) - 6
    top.append(f'- [{name}]({BASE}{k}/): {hb_desc.rstrip(".")}. 전체 페이지 목록은 {BASE}{k}/llms.txt')
io.open(os.path.join(SITE, 'llms.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(top) + '\n')
print('llms.txt 페이지 줄', total)
