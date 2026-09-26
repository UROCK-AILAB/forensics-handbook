---
title: "저장 구조"
parent: "애플 메일"
grand_parent: "아티팩트 · 메일"
nav_order: 1290
---

# 저장 구조 (emlx·V10)

애플 메일은 메시지 하나를 `.emlx` 파일 하나로 저장하고, 파일 이름의 숫자가 메일 색인 DB 의 메시지 번호(ROWID)라서 색인 DB 한 행과 본문 파일 하나가 짝을 이룹니다 [3]. 파일 안에는 원본 MIME 메시지와 상태 플래그를 담은 속성 목록 (Property List)이 차례로 들어 있습니다 [1].

## 무엇을 기록하나

`.emlx` 파일에는 원본 MIME 메시지가 RFC 822 헤더와 본문 그대로 들어 있고, 그 뒤에 읽음·깃발·첨부 개수 같은 상태를 담은 속성 목록이 붙습니다 [1]. [메일 색인 DB (Envelope Index)](envelope-index.md)에는 본문 텍스트가 없어서, 메일 내용을 확인하려면 이 파일을 읽어야 합니다 [2].

내려받기가 끝나지 않은 메시지는 `<ROWID>.emlx` 대신 `<ROWID>.partial.emlx` 로 남습니다 [3]. 그래서 같은 폴더 안에서도 파일 이름 끝이 `.emlx` 와 `.partial.emlx` 로 갈리고, 뒤쪽 파일에는 본문 일부만 있을 수 있습니다. Exchange 계정은 본문 파일이 디스크에 아예 없는 경우가 흔합니다 [3].

## 위치와 버전별 차이

메일 데이터는 사용자 홈의 `~/Library/Mail/V<n>/` 아래에 있고, 공개 도구는 `V` 뒤 숫자가 가장 큰 폴더를 현재 저장소로 고릅니다 [3]. 구조가 알려진 폴더 이름은 `V10` 이고, 다른 번호도 스키마가 같으면 같은 방식으로 읽을 수 있습니다 [2]. macOS 버전별로 어느 번호를 쓰는지는 공개 자료가 없어서, 실제 데이터에서 폴더 이름을 직접 보고 [OS 버전과 설치 기록](../../system-account/os-version-install-history.md)과 함께 적어 둡니다.

`~/Library/Mail` 은 보호 영역이라서 라이브 시스템에서 직접 읽으려면 전체 디스크 접근 권한 (Full Disk Access)이 필요합니다 [2]. 권한 기록은 [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md)에서, 켜진 맥에서 수집하는 순서는 [라이브 대응 (Live Response)](../../../03-techniques/process-acquisition/live-response/index.md)에서 다룹니다.

## 구조

### 폴더 구조

메시지 파일까지 내려가는 경로는 아래와 같습니다 [3].

```
~/Library/Mail/V<n>/<계정 UUID>/<메일함>.mbox/<저장소 UUID>/Data/[<나눔 폴더>/]Messages/<ROWID>.emlx
```

메일함 폴더는 메일함 URL 에서 찾아 들어갑니다. `imap://<계정 UUID>/<경로>` 같은 URL 에서 계정 UUID 폴더를 잡고, 경로를 이루는 이름마다 뒤에 `.mbox` 를 붙인 폴더로 한 단계씩 내려갑니다 [3]. 규칙대로라면 `imap://<계정 UUID>/Archive/2024` 는 `<계정 UUID>/Archive.mbox/2024.mbox/` 가 되고(규칙에서 만든 예), `.mbox` 폴더 안에는 UUID 이름의 하위 폴더가 하나 더 있고 그 아래에 `Data` 가 옵니다 [3]. 메일함 URL 은 [메일 색인 DB](envelope-index.md)의 `mailboxes.url` 열에 있고, UUID 를 읽는 법은 [식별자 읽기 (UUID·UID·GUID)](../../../01-foundations/value-decoding/uuid-uid.md)에 있습니다.

### 나눔 폴더 (Shard)

`Data` 아래는 ROWID 에 따라 숫자 폴더로 나뉩니다. ROWID 를 1000 으로 나눈 몫을 구하고, 그 숫자를 뒤에서부터 한 자리씩 폴더로 만들며, ROWID 가 1000 보다 작으면 나눔 폴더 없이 `Data/Messages/` 에 바로 둡니다 [3].

| ROWID | 1000 으로 나눈 몫 | `Data/` 아래 위치 |
|---|---|---|
| 842 | 0 (1000 미만) | `Messages/842.emlx` |
| 12345 | 12 | `2/1/Messages/12345.emlx` |
| 159566 | 159 | `9/5/1/Messages/159566.emlx` |

마지막 줄은 공개 도구 코드에 실린 예이고 [3], 위의 두 줄은 같은 규칙으로 계산한 예입니다. 거꾸로 경로를 보고 ROWID 를 짐작할 수도 있지만, 파일 이름에 ROWID 가 그대로 있으니 이름을 읽는 쪽이 정확합니다.

### `.emlx` 파일 안

한 파일은 세 부분으로 나뉩니다 [1].

| 순서 | 내용 | 읽는 법 |
|---|---|---|
| 1 | 첫 줄: 뒤따르는 메시지의 바이트 수 | 10진 정수 문자열이고 줄바꿈으로 끝남, 앞뒤 공백은 떼고 읽음 |
| 2 | 원본 MIME 메시지 (RFC 822 헤더 + 본문) | 첫 줄에 적힌 바이트 수만큼 읽음 |
| 3 | 나머지: Apple 속성 목록 | 속성 목록으로 읽음 |

끝부분은 XML 과 바이너리 속성 목록 가운데 어느 쪽인지 정해져 있지 않고, 파이썬 참고 구현도 두 형식을 모두 읽는 `plistlib.loads` 로 읽습니다 [1]. 끝부분의 형식은 첫 바이트를 보고 판별하고, 형식별 구조는 [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md)을 봅니다.

속성 목록 키 가운데 뜻이 알려진 것은 정수 비트마스크인 `flags` 하나입니다 [1]. 다른 키의 이름과 시각 기준은 공개 자료가 없어 실제 데이터로 확인해야 합니다.

### `flags` 비트

`flags` 의 비트는 낮은 비트부터 아래와 같습니다 [1]. 비트 번호는 파서 소스의 이름 순서에서 계산한 값이라서, 실제 데이터에서 몇 건을 메일 앱 화면과 맞춰 본 뒤에 씁니다.

| 비트 | 이름 | 뜻 (이름으로 본 뜻) |
|---|---|---|
| 0 | read | 읽음 |
| 1 | deleted | 삭제 표시 |
| 2 | answered | 답장함 |
| 3 | encrypted | 암호화된 메일 |
| 4 | flagged | 깃발 표시 |
| 5 | recent | 최근 메일 |
| 6 | draft | 임시 저장 |
| 7 | initial | (공개 자료 없음) |
| 8 | forwarded | 전달함 |
| 9 | redirected | 재전송함 |
| 10–15 | attachment_count | 첨부 개수 (6비트) |
| 16–22 | priority_level | 중요도 (7비트) |
| 23 | signed | 서명된 메일 |
| 24 | is_junk | 정크로 표시 |
| 25 | is_not_junk | 정크 아님으로 표시 |
| 26–28 | font_size_delta | 글자 크기 조정 (3비트) |
| 29 | junk_mail_level_recorded | (공개 자료 없음) |
| 30 | highlight_text_in_toc | (공개 자료 없음) |

MIME 헤더의 `Message-ID` 로 만든 `message:<Message-ID>` 형태의 URL 이 메시지를 가리키는 값으로 쓰입니다 [1].

## 증거로서 의미

**증명하는 것.** 수집 시점에 이 사용자 계정의 메일 저장소에 해당 메시지의 사본이 있었다는 점과 그 헤더·본문 내용을 보여 줍니다. 파일이 들어 있는 `.mbox` 폴더에서 어느 계정의 어느 메일함에 있었는지 알 수 있고, `flags` 에서는 수집 시점의 읽음·답장·전달·깃발·정크 상태를 읽을 수 있습니다 [1][3].

**증명하지 못하는 것.** `flags` 에는 상태만 있고 그 상태가 바뀐 시각이나 바꾼 사람은 없어서, 읽음 비트만으로 "이 사람이 언제 읽었다" 고 쓸 수는 없습니다. 헤더의 발신자·날짜는 보낸 쪽이 적은 값이라서 그대로 사실로 옮기지 않고 기록된 값으로만 인용합니다. `.partial.emlx` 에 본문이 없다고 해서 원래 메일에 본문이 없었다고 볼 수도 없습니다.

보고서에는 "이 계정의 받은 편지함 폴더에 이 Message-ID 의 메시지가 있고, 수집 시점 상태 값에는 읽음과 전달 비트가 켜져 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`.emlx` 안에서 뜻이 알려진 시각은 MIME 헤더의 날짜뿐이고, 이 값은 보낸 쪽 기기가 적은 시각입니다. 속성 목록 쪽 시각 키는 공개 자료가 없어서, 받은 시각과 보낸 시각은 [메일 색인 DB](envelope-index.md)의 열과 함께 봅니다. 여러 시각을 하나로 모아 보는 방법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에 있습니다.

## 함정과 한계

이 구조는 공개 도구가 역분석한 결과이고 Apple 이 문서로 밝힌 API 가 아니라서 [2], 버전이 바뀌면 폴더 규칙이나 속성 목록 내용이 달라질 수 있습니다. 나눔 규칙과 폴더 구조는 공개 도구 하나의 코드에만 나와 있어서, 실제 데이터에서 몇 건을 직접 따라가 맞는지 먼저 봅니다.

`.partial.emlx` 말고 다른 부분 파일 확장자가 있는지, 로컬 메일함(`local://`)이나 Exchange 계정(`ews://`) URL 이 같은 규칙으로 폴더가 되는지는 공개 자료가 없습니다. IMAP 이 아닌 계정은 폴더를 직접 둘러보고 규칙을 확인하고, Exchange 계정은 본문 파일이 없는 것이 흔하다는 점도 함께 적어 둡니다 [3].

`deleted` 비트가 켜진 파일이 남아 있을 수 있지만, 삭제한 메일이 언제 파일에서 사라지는지는 공개 자료가 없습니다. 파일이 사라진 뒤의 흔적을 찾는 방법은 [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 따라가기

아래는 명세대로 만든 예시이고, 실제 데이터에서 나온 값이 아닙니다. 첫 줄이 `1520` 이라면 파일 앞부분은 이렇게 보입니다.

```
00000000  31 35 32 30 0A 46 72 6F 6D 3A 20 ...   1520.From: ...
```

`31 35 32 30` 은 ASCII 숫자 `1520` 이고 `0A` 가 첫 줄을 끝냅니다. 그 바로 뒤 오프셋 5(0x05)부터 1520 바이트가 MIME 메시지이고, 속성 목록은 오프셋 5 + 1520 = 1525(0x5F5)에서 시작합니다. 0x5F5 로 가서 첫 바이트를 보면 속성 목록이 XML 인지 바이너리인지 가릴 수 있습니다.

`flags` 값이 2065 (0x811)라고 하면(계산용 예시), 비트 0 과 비트 4 가 켜져 있어 읽음과 깃발이고, 비트 10–15 를 떼어 내면 `(2065 >> 10) & 0x3F = 2` 라서 첨부 개수는 2 입니다.

### 공개 도구로 읽기

증거 사본에서 파일을 꺼낸 뒤, 파이썬 표준 라이브러리만으로 세 부분을 나눌 수 있습니다.

```python
import plistlib, email

data = open("159566.emlx", "rb").read()
nl = data.index(b"\n")
size = int(data[:nl])
mime = data[nl + 1 : nl + 1 + size]
meta = plistlib.loads(data[nl + 1 + size :])

msg = email.message_from_bytes(mime)
flags = meta.get("flags", 0)
print(msg["Message-ID"], msg["Date"], msg["From"])
print("read", flags & 1, "flagged", (flags >> 4) & 1, "attachments", (flags >> 10) & 0x3F)
```

공개 파서로는 파이썬 패키지 emlx 가 있고, 위와 같은 방식으로 세 부분을 나눠 `flags` 를 풀어 줍니다 [1]. 도구마다 비트 해석이 다를 수 있어서 한 건은 손으로 계산해 도구 출력과 맞춰 봅니다.

## 교차 검증

파일 이름의 ROWID 로 [메일 색인 DB](envelope-index.md)의 `messages` 행을 찾아 제목·발신자·메일함이 본문 헤더와 맞는지 봅니다. `Message-ID` 헤더는 색인 DB 의 `message_global_data.message_id_header` 와 맞춰 볼 수 있고, 다른 기록에서 `message:` 로 시작하는 문자열이 나오면 같은 값으로 메시지를 짚어 볼 수 있습니다. 첨부 개수 비트는 [첨부 파일 (Attachments)](attachments.md)에서 다른 두 곳과 함께 맞춰 봅니다. 여러 메일에서 낱말을 찾을 때는 [콘텐츠 검색 (Content Search)](../../../03-techniques/analysis/content-search.md)을 참고합니다.

## 실습

애플 메일 데이터가 들어 있는 공개 시험 데이터나 직접 만든 시험 계정으로 아래 질문을 풀어 봅니다.

1. `~/Library/Mail/` 아래에 `V` 로 시작하는 폴더가 몇 개 있고, 가장 큰 번호는 무엇인가?
2. ROWID 가 1000 이상인 메시지 하나를 골라 나눔 규칙으로 경로를 계산하고 실제 위치와 맞는지 확인한다.
3. 한 `.emlx` 의 첫 줄 숫자로 속성 목록 시작 위치를 구하고, 그 속성 목록이 XML 인지 바이너리인지 확인한다.
4. 메일 앱에서 깃발을 달고 읽음 표시를 바꾼 메일의 `flags` 를 전후로 비교해 비트 표가 맞는지 확인한다.

## 참고 문헌

1. mikez/emlx — emlx.py (Python .emlx 파서 소스) — https://raw.githubusercontent.com/mikez/emlx/master/emlx/emlx.py
2. Inkvi/apple-mail-mcp (Envelope Index + .emlx 읽기 도구 README) — https://github.com/Inkvi/apple-mail-mcp
3. Inkvi/apple-mail-mcp — src/store/paths.ts (저장소 루트·.emlx 경로 계산 코드) — https://raw.githubusercontent.com/Inkvi/apple-mail-mcp/main/src/store/paths.ts
