# -*- coding: utf-8 -*-
"""빌드된 각 권의 sitemap.xml 에서 페이지 수를 세어 첫 화면(_site/index.html) 핸드북 표의 페이지 칸과 합계를 채운다."""
import os, re, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
counts = {}
for k in ['windows', 'mac', 'linux', 'android', 'ios', 'cloud', 'network', 'crypto', 'ai']:
    p = os.path.join(SITE, k, 'sitemap.xml')
    if os.path.exists(p):
        counts[k] = open(p, encoding='utf-8').read().count('<loc>')
counts['all'] = sum(counts.values())
print(counts)

home = os.path.join(SITE, 'index.html')
html = open(home, encoding='utf-8').read()
html, n = re.subn(r'(<span class="pages" data-hb="(\w+)">)[^<]*(</span>)',
                  lambda m: m.group(1) + (f'{counts[m.group(2)]:,}' if m.group(2) in counts else '-') + m.group(3), html)
assert n == len(counts), f'표의 칸 {n}개, 센 권 {len(counts)}개'
open(home, 'w', encoding='utf-8').write(html)
