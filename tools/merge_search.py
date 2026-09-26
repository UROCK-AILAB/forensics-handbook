# -*- coding: utf-8 -*-
"""빌드된 각 권의 search-data.json 을 합쳐 첫 화면(_site/assets/js/search-data.json)의 검색 목록으로 쓴다.
결과 제목 앞에 권 이름을 붙이고, 보이는 경로(relUrl) 앞에 권 폴더를 붙인다."""
import json, os, sys

SITE = sys.argv[1] if len(sys.argv) > 1 else '_site'
NAMES = [('windows', 'Windows'), ('mac', 'macOS'), ('linux', 'Linux'), ('android', 'Android'),
         ('ios', 'iOS'), ('cloud', 'Cloud'), ('ai', 'AI')]
merged = {}
home = os.path.join(SITE, 'assets', 'js', 'search-data.json')
if os.path.exists(home):
    for v in json.load(open(home, encoding='utf-8')).values():
        merged[str(len(merged))] = v
for k, name in NAMES:
    p = os.path.join(SITE, k, 'assets', 'js', 'search-data.json')
    if not os.path.exists(p):
        continue
    n = 0
    for v in json.load(open(p, encoding='utf-8')).values():
        v['doc'] = f'[{name}] {v["doc"]}'
        if v.get('title') == v['doc'][len(name) + 3:]:
            v['title'] = v['doc']
        v['relUrl'] = f'/{k}{v.get("relUrl", "")}'
        merged[str(len(merged))] = v
        n += 1
    print(k, n)
os.makedirs(os.path.dirname(home), exist_ok=True)
json.dump(merged, open(home, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('합계', len(merged), '크기', os.path.getsize(home))
