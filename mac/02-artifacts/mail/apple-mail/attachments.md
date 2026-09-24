---
title: "메일 첨부 파일"
parent: "애플 메일"
grand_parent: "아티팩트 · 메일"
nav_order: 1310
---

# 첨부 파일 (Attachments)

애플 메일의 첨부 흔적은 메일 색인 DB 의 `attachments` 표, `.emlx` 상태 값 안의 첨부 개수, `.emlx` 본문 안의 MIME 파트 세 곳에서 볼 수 있고, 세 곳을 서로 맞춰 보면 어느 메시지에 어떤 이름의 첨부가 몇 개 있었는지를 정리할 수 있습니다 [1][2].

## 무엇을 기록하나

[메일 색인 DB (Envelope Index)](envelope-index.md)의 `attachments` 표에는 메시지 번호와 첨부 이름이 한 줄씩 들어 있습니다 [2]. [저장 구조 (emlx·V10)](storage.md)에서 다룬 `.emlx` 끝부분의 `flags` 값에는 첨부 개수가 들어 있고, `.emlx` 본문은 원본 MIME 메시지라서 첨부가 MIME 파트로 본문 파일 안에 들어 있을 수 있습니다 [1].

메일 앱이 첨부를 본문에서 떼어 따로 저장하는지, 따로 저장한다면 어느 폴더에 두는지는 확인한 자료가 없습니다. 사용자가 첨부를 열거나 미리 볼 때 복사본을 어디에 만드는지도 확인하지 못했습니다.

## 위치

| 위치 | 담긴 것 | 확인 여부 |
|---|---|---|
| `Envelope Index` 의 `attachments` 표 | `message`(메시지 ROWID), `name`(첨부 이름) [2] | 공개 도구 코드로 확인 |
| `.emlx` 속성 목록의 `flags` 비트 10–15 | 첨부 개수 (6비트) [1] | 공개 도구 코드로 확인 |
| `.emlx` 본문의 MIME 파트 | 첨부 내용 자체일 수 있음 [1] | 첨부가 늘 본문에 남는지는 확인 못 함 |
| 첨부를 따로 저장하는 폴더 | — | 확인 못 함 |
| 첨부를 열 때 복사되는 폴더 | — | 확인 못 함 |

macOS 버전에 따라 위 위치가 달라지는지도 확인한 자료가 없습니다.

## 구조

`attachments` 표에서 공개 도구가 필수로 보는 칸은 `message` 와 `name` 두 개이고, `message` 는 `messages.ROWID` 를 가리킵니다 [2]. 크기·MIME 형식·첨부 번호 같은 다른 칸이 있는지는 확인하지 못해서, 검체에서 표 정의를 직접 뽑아 봅니다.

`flags` 의 첨부 개수는 비트 10–15 의 6비트 값이고 [1], 6비트로 담을 수 있는 가장 큰 수는 63 입니다. 비트 전체 표는 [저장 구조](storage.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 수집 시점에 색인에 이 메시지와 이 이름의 첨부가 짝지어 있었고, `.emlx` 에 해당 첨부 개수가 적혀 있었다는 점을 보여 줍니다 [1][2]. 본문 파일 안에서 MIME 파트를 꺼낼 수 있으면 첨부 내용도 확인할 수 있습니다.

**증명하지 못하는 것.** 이 세 곳에는 사용자가 첨부를 열었는지, 디스크의 다른 곳에 저장했는지, 다른 메일로 다시 보냈는지가 나타나지 않습니다. 첨부 이름은 보낸 쪽이 붙인 이름이라서 내용이 이름과 맞는다는 뜻도 아닙니다. 본문을 다 받지 않은 `.partial.emlx` 도 있어서([저장 구조](storage.md)), 본문 파일에 첨부 파트가 없다고 원래 메일에 첨부가 없었다고 볼 수는 없습니다.

보고서에는 "이 메시지 번호의 색인 행에 이 이름의 첨부가 기록되어 있고, 본문 파일에서 같은 이름의 파트를 꺼냈다" 처럼 어느 자료에서 무엇을 보았는지를 나눠 씁니다.

## 함정과 한계

세 곳이 각각 무엇을 첨부로 세는지는 확인한 자료가 없어서, 개수가 서로 어긋나면 MIME 파트를 직접 열어 무엇이 들어 있는지 봅니다.

메일에서 디스크로 저장한 첨부 파일에 격리 속성 `com.apple.quarantine` 이 붙는지와 그 값은 확인하지 못했습니다. 저장한 파일이 있다면 [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md)의 방법으로 속성을 직접 읽어 보고, 메일 앱과 이어지는 값이 있는지 확인합니다.

## 직접 분석해 보기

### 헥스로 따라가기

`.emlx` 파일에서 MIME 메시지가 시작하는 위치를 찾는 법은 [저장 구조](storage.md)의 헥스 예시를 따릅니다. MIME 부분 안에서 파트를 나누는 경계 문자열은 메일마다 `Content-Type` 헤더에 적혀 있어서, 그 문자열로 검색하면 파트가 몇 개인지 눈으로 셀 수 있습니다.

### 공개 도구로 읽기

색인 DB 에서는 `sqlite3` 로 메시지별 첨부 이름을 모읍니다.

```sql
SELECT a.message, a.name
FROM attachments a
ORDER BY a.message;
```

본문 파일에서는 파이썬 표준 라이브러리 `email` 로 파트를 돌며 파일 이름이 있는 파트를 꺼냅니다. 꺼낸 파일은 증거 사본 밖의 작업 폴더에 저장하고 해시를 남깁니다.

```python
import email, hashlib

data = open("159566.emlx", "rb").read()
nl = data.index(b"\n")
size = int(data[:nl])
msg = email.message_from_bytes(data[nl + 1 : nl + 1 + size])

for part in msg.walk():
    name = part.get_filename()
    if name:
        body = part.get_payload(decode=True) or b""
        print(name, len(body), hashlib.sha256(body).hexdigest())
```

같은 메시지에서 `attachments` 표의 이름 목록, `flags` 의 첨부 개수, 위 코드가 꺼낸 파트 목록을 나란히 놓고 비교합니다.

## 교차 검증

첨부 이름으로 디스크를 찾으면 사용자가 첨부를 저장했는지 짐작할 단서가 되고, 그 파일의 출처는 [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md)과 [다운로드 출처 속성 (kMDItemWhereFroms)](../../filesystem/where-froms.md)에서 확인합니다. 파일이 어디서 왔는지 따지는 흐름은 [이 파일은 어디서 왔나 (File Origin)](../../../04-scenarios/activity/file-origin.md)에, 메일로 자료를 내보냈는지 따지는 흐름은 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)에 있습니다. 첨부로 악성 파일이 들어왔는지 볼 때는 [악성 코드는 어디서 들어왔나 (Initial Access)](../../../04-scenarios/incident/initial-access.md)를 함께 봅니다.

## 실습

애플 메일 데이터가 들어 있는 공개 검체나 직접 만든 시험 계정으로 아래 질문을 풀어 봅니다.

1. 첨부가 두 개 달린 메일을 받아 `attachments` 표의 행 수, `flags` 의 첨부 개수, MIME 파트 수를 비교한다.
2. `attachments` 표의 정의를 뽑아 이 페이지에 적힌 두 칸 말고 어떤 칸이 있는지 확인한다.
3. 받은 첨부를 메일 앱에서 한 번 열고, 파일 시스템에서 새로 생긴 파일이 있는지 찾아 본다.
4. 메일에서 저장한 첨부 파일에 격리 속성이 붙었는지, 붙었다면 어떤 앱 이름이 적혔는지 확인한다.

## 참고 문헌

1. mikez/emlx — emlx.py (Python .emlx 파서 소스) — https://raw.githubusercontent.com/mikez/emlx/master/emlx/emlx.py
2. Inkvi/apple-mail-mcp — src/store/probe.ts (필수 표·칸 목록) — https://raw.githubusercontent.com/Inkvi/apple-mail-mcp/main/src/store/probe.ts
