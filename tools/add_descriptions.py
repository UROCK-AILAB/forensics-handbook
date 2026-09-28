# -*- coding: utf-8 -*-
"""빌드 전에 쪽마다 머리말에 description 을 넣는다(저장소 파일이 아니라 빌드용 작업 사본에만).
설명은 H1 바로 밑 요약 문단에서 뽑는다. 검색 결과와 AI 가 쪽을 구분할 수 있게 한다.
이미 description 이 있는 쪽은 건드리지 않는다."""
import io, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else '.'
KS = ['home', 'windows', 'mac', 'linux', 'android', 'ios', 'cloud', 'network', 'crypto', 'ai']
LIMIT = 160


def summary(body):
    lines = body.splitlines()
    i = 0
    while i < len(lines) and not lines[i].startswith('# '):  # H1 까지 건너뛴다
        i += 1
    i += 1
    para = []
    for line in lines[i:]:
        t = line.strip()
        if not t:
            if para:
                break
            continue
        if t.startswith(('#', '|', '>', '```', '<', '- ', '* ', '{')) or re.match(r'\d+\.\s', t):
            if para:
                break
            continue
        para.append(t)
    s = ' '.join(para)
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', s)          # 그림
    s = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', s)       # 링크는 글자만
    s = re.sub(r'\[\d+(?:\]\[\d+)*\]', '', s)            # 참고 문헌 번호 [1][2]
    s = re.sub(r'\{:[^}]*\}', '', s)                     # kramdown 속성
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace('`', '').replace('**', '').replace('__', '')
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > LIMIT:
        cut = s[:LIMIT]
        end = max(cut.rfind('다. '), cut.rfind('다.'))
        s = cut[:end + 2] if end > 60 else cut.rsplit(' ', 1)[0] + '…'
    return s


def title_of(p):
    try:
        head = io.open(p, encoding='utf-8').read(600)
    except OSError:
        return None
    return name_of(head)


def name_of(head):
    t = re.search(r'^nav_title:\s*"?(.*?)"?\s*$', head, re.M) or re.search(r'^title:\s*"?(.*?)"?\s*$', head, re.M)
    return t.group(1).split(' · ')[-1] if t else None


def children(dp, f):
    """목차 쪽(index.md) 옆의 쪽과 하위 폴더 목차의 제목. 제목 줄만 읽으므로 그 쪽에 description 을 먼저 넣었어도 상관없다."""
    if f != 'index.md':
        return []
    out = []
    for name in sorted(os.listdir(dp)):
        q = os.path.join(dp, name)
        if name.endswith('.md') and name != 'index.md':
            out.append(title_of(q))
        elif os.path.isdir(q) and not name.startswith('_') and os.path.exists(os.path.join(q, 'index.md')):
            out.append(title_of(os.path.join(q, 'index.md')))
    return [x for x in out if x]


def yq(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


done = 0
for k in KS:
    for dp, dn, fn in os.walk(os.path.join(ROOT, k)):
        dn[:] = [d for d in dn if not d.startswith('_')]
        for f in fn:
            if not f.endswith('.md'):
                continue
            p = os.path.join(dp, f)
            s = io.open(p, encoding='utf-8').read()
            m = re.match(r'---\n(.*?)\n---\n', s, re.S)
            if not m or re.search(r'^description:', m.group(1), re.M):
                continue
            d = summary(s[m.end():])
            if len(d) < 40 or '아래 목록에서 고릅니다' in d:  # 목차뿐인 쪽은 아래 쪽 제목으로 설명한다
                t = name_of(m.group(1))
                kids = children(dp, f)
                if kids:
                    d = (t + ' 분류에는 ' if t else '') + ', '.join(kids[:12]) + (' 등' if len(kids) > 12 else '') + ' 페이지가 있습니다.'
                else:
                    d = (t + ' — ' if t else '') + d
            if not d.strip(' —'):
                continue
            s = s[:m.end() - 4] + '\ndescription: ' + yq(d) + '\n---\n' + s[m.end():]
            io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
            done += 1
print('description 넣은 쪽', done)
