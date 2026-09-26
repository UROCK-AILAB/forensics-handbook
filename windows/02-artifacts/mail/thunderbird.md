---
title: "썬더버드"
parent: "아티팩트 · 메일"
nav_order: 1950
---

# 썬더버드 (Thunderbird)

> 위치: 아티팩트 사전 > 메일

## 한 줄 요약

썬더버드 (Thunderbird) 는 Mozilla 의 메일 프로그램입니다. 메시지마다 읽음·답장·전달·삭제 대기 같은 상태를 비트 값으로 적고, 이 값을 메시지 헤더 `X-Mozilla-Status`·`X-Mozilla-Status2` 에 둡니다. 지운 메시지는 폴더 압축 전까지 파일에 남습니다. 비트 값의 뜻은 Mozilla 소스 코드에 정의돼 있습니다[1]. 프로필 위치와 파일 구성은 흔한 설명이라 따로 나눠 적습니다.

## 내용별 근거

| 내용 | 근거 |
|---|---|
| 메시지 플래그 값과 뜻, 헤더에 적지 않는 값, 라벨을 적는 헤더 | Mozilla 소스 코드(`nsMsgMessageFlags.idl`)[1] |
| 지운 메시지가 폴더 압축 전까지 남는다는 점 | 같은 소스의 `Expunged` 설명[1] |
| 압축하면 파일에서 실제로 빠진다는 점, 자동 압축 기준 | 공개 자료 없음. 실제 데이터로 확인 |
| 두 헤더에 값을 나눠 적는 방법과 자릿수 | 공개 자료 없음. 실제 데이터로 확인 |
| 프로필 위치, 폴더 파일 구성(mbox·`.msf`·`.sbd`) | 흔한 설명. 실제 데이터로 확인 |
| 검색 색인·주소록·비밀번호·설정 파일 | 흔한 설명. 실제 데이터로 확인 |
| Maildir 저장 방식 | 고를 수 있다는 흔한 설명. 실제 데이터로 확인 |

파일 위치와 구성은 흔한 설명입니다. 보고서에 쓰기 전에 분석 대상과 같은 판의 썬더버드로 재현해 확인합니다(아래 실습).

## 무엇을 기록하나 · 왜 생기나

썬더버드는 POP 메일, IMAP 메일, 뉴스 글, RSS 피드를 같은 플래그 체계로 다룹니다[1]. 메시지를 읽고, 답장하고, 전달하고, 별표를 붙이면 그 상태가 메시지의 플래그 비트로 남고, 대부분의 플래그는 `X-Mozilla-Status` 헤더에, 라벨은 `X-Mozilla-Status2` 헤더에 들어갑니다[1]. 지운 메시지는 폴더 압축 (compaction) 을 기다리는 동안 `Expunged` 비트가 선 채 남습니다[1].

메일 폴더는 사용자 프로필 안에 파일로 쌓인다는 설명이 흔합니다. 프로그램을 지운 뒤에도 프로필 폴더가 남았는지 봅니다.

## 위치와 버전별 차이

### 흔히 알려진 위치 (실제 데이터로 확인)

| 무엇 | 흔히 알려진 위치 |
|---|---|
| 프로필 목록 | `%APPDATA%\Thunderbird\profiles.ini`, `%APPDATA%\Thunderbird\installs.ini` |
| 프로필 폴더 | `%APPDATA%\Thunderbird\Profiles\<무작위 8글자>.default` 또는 `.default-release` |
| 로컬 폴더 | 프로필 폴더 아래 `Mail\Local Folders\` |
| POP 계정 메일 | 프로필 폴더 아래 `Mail\<POP 서버 이름>\` |
| IMAP 계정 메일 | 프로필 폴더 아래 `ImapMail\<IMAP 서버 이름>\` |

- 프로필 폴더 이름에는 무작위 글자가 붙는다는 설명이 흔합니다. 이름을 짐작하지 말고 `profiles.ini` 가 가리키는 폴더를 따라갑니다.
- 프로필 폴더가 여럿일 수 있습니다. 모든 프로필 폴더를 봅니다.
- 파이어폭스에도 `profiles.ini`·`prefs.js` 가 있습니다. 두 프로그램의 파일 형식이 같은지는 실제 데이터로 확인합니다. 파이어폭스 쪽 설명은 [파이어폭스](../browsers/firefox/index.md) 에서 다룹니다.

### 판에 따른 차이 (흔한 설명)

- 주소록은 예전 판에서 Mork 형식의 `abook.mab`·`history.mab` 였고, 새 판에서 SQLite 형식의 `abook.sqlite`·`history.sqlite` 로 바뀌었다는 설명이 흔합니다. 바뀐 판은 실제 데이터로 확인해야 합니다.
- 폴더마다 파일 하나에 메시지를 모으는 mbox 방식 대신, 메시지 하나를 파일 하나로 두는 Maildir 방식도 고를 수 있다는 설명이 흔합니다. 이 방식이 들어온 판과 설정 이름은 실제 데이터로 확인합니다.

## 구조

### 메일 폴더 파일 (흔한 설명)

| 파일 | 흔한 설명 |
|---|---|
| 확장자 없는 파일 (`Inbox`, `Sent`, `Trash` 등) | 메일 폴더 하나입니다. 메시지를 mbox 형식으로 이어 붙입니다 |
| `<폴더 이름>.msf` | 폴더의 요약(색인) 파일입니다. Mork 형식입니다. 지워도 mbox 에서 다시 만듭니다 |
| `<폴더 이름>.sbd\` | 하위 폴더를 담는 디렉터리입니다 |

mbox 형식과 메시지를 나누는 법은 [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) 에서 다룹니다.

### 메시지 플래그

Mozilla 소스 `mailnews/base/public/nsMsgMessageFlags.idl` 에 정의된 값입니다[1].

| 이름 | 값 | 뜻 | 비고 |
|---|---|---|---|
| Read | `0x00000001` | 읽음 | |
| Replied | `0x00000002` | 답장을 보냄 | |
| Marked | `0x00000004` | 별표(플래그) 표시 | |
| Expunged | `0x00000008` | 지워졌고 폴더 압축을 기다림 | |
| HasRe | `0x00000010` | 제목에 원래 "Re:" 가 있었음 | |
| Elided | `0x00000020` | 스레드 접힘(화면 표시용) | 헤더에 적지 않음 |
| FeedMsg | `0x00000040` | RSS 계정에서 받은 피드 | |
| Offline | `0x00000080` | 뉴스 글이나 IMAP 메시지가 디스크 캐시에 있음 | 헤더에 적지 않음 |
| Watched | `0x00000100` | 스레드 지켜보기 | |
| SenderAuthed | `0x00000200` | 보낸 사람이 인증됨 | |
| Partial | `0x00000400` | 본문이 잘려 있음. 나머지를 POP 서버에서 받아야 함 | |
| Queued | `0x00000800` | 보낼 대기 중 | |
| Forwarded | `0x00001000` | 전달함 | |
| Redirected | `0x00002000` | 리디렉트함 | |
| Priorities | `0x0000E000` | 옛 중요도 자리(3비트) | |
| New | `0x00010000` | 폴더를 마지막으로 닫은 뒤 새로 온 메시지 | 헤더에 적지 않음 |
| Ignored | `0x00040000` | 스레드 무시 | |
| IMAPDeleted | `0x00200000` | IMAP 서버에서 지움 표시됨 | |
| MDNReportNeeded | `0x00400000` | 수신 확인 요청이 있음 | |
| MDNReportSent | `0x00800000` | 수신 확인을 보냄 | |
| Template | `0x01000000` | 서식 | |
| Labels | `0x0E000000` | 라벨 | `X-Mozilla-Status2` 에 적음 |
| Attachment | `0x10000000` | 첨부가 있음 | |

- `Elided`·`New`·`Offline` 은 실행 중에만 쓰는 값이라서 `X-Mozilla-Status`·`X-Mozilla-Status2` 헤더에 적지 않습니다[1].
- `Redirected`(`0x00002000`) 는 옛 `Priorities` 자리(`0x0000E000`) 안에 있습니다. 옛 판이 쓴 파일에서 이 비트를 어느 뜻으로 읽을지는 분석 대상과 같은 판으로 재현해 정합니다.
- `X-Mozilla-Status` 에는 아래 16비트를, `X-Mozilla-Status2` 에는 위 16비트를 적는다는 설명이 흔합니다. 분석 대상과 같은 판으로 재현해 확인합니다.

### 그 밖의 프로필 파일 (흔한 설명)

| 파일 | 흔한 설명 |
|---|---|
| `global-messages-db.sqlite` | 전체 검색 (Gloda) 색인입니다. 표·열 이름과 시각 단위는 실제 데이터로 확인합니다 |
| `abook.sqlite`, `history.sqlite` (예전 판은 `abook.mab`, `history.mab`) | 주소록입니다 |
| `logins.json`, `key4.db` | 저장된 비밀번호와 그 키입니다. 파이어폭스와 같은 NSS 방식이라는 설명이 흔합니다 |
| `prefs.js` | 계정·서버·사용자 이름·메일 주소·폴더 경로 설정입니다. 설정 이름은 `mail.account.`·`mail.identity.`·`mail.server.` 로 시작합니다 |
| `msgFilterRules.dat` | 메시지 필터 규칙입니다 |
| `training.dat` | 스팸 학습 자료입니다 |
| `virtualFolders.dat` | 저장된 검색입니다 |
| `folderTree.json`, `panacea.dat` | 폴더 캐시입니다 |

- `global-messages-db.sqlite` 와 `abook.sqlite` 를 여는 법은 [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.
- `logins.json`·`key4.db` 의 복호는 [파이어폭스](../browsers/firefox/index.md) 에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| mbox 안에 메시지가 있으면, 그 메시지가 이 프로필의 그 폴더에 들어온 적이 있습니다 | 이 PC 에서 받거나 보냈다는 것. 프로필 폴더는 다른 PC 에서 복사해 올 수 있습니다 |
| `Replied`·`Forwarded` 비트가 서 있으면 썬더버드가 그 메시지에 답장·전달 상태를 적었습니다 | 누구에게 답장·전달했는지. 보낸 메시지는 따로 찾습니다 |
| `Read` 비트는 메시지가 읽음 상태였다는 뜻입니다 | 사람이 내용을 실제로 읽었다는 것 |
| `Expunged` 비트가 선 메시지는 지워졌고 압축을 기다리던 메시지입니다[1] | 누가 언제 지웠는지. 비트에는 시각이 없습니다 |
| `Queued` 비트는 보낼 대기 중이었다는 뜻입니다[1] | 그 뒤에 실제로 보냈다는 것 |
| `Attachment` 비트는 첨부가 있다고 표시됐다는 뜻입니다[1] | 첨부의 내용. 첨부는 메시지의 MIME 부분에서 꺼냅니다 |

### 보고서 문장

아래 폴더 이름과 주소는 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "프로필의 `Inbox` mbox 파일에 보낸 사람이 `partner@example.com` 인 메시지가 있습니다. 이 메시지의 `X-Mozilla-Status` 값을 비트로 풀면 `Read` 와 `Forwarded` 가 서 있습니다."
- 쓰면 안 되는 문장: "사용자는 이 메일을 읽고 외부로 전달했습니다."

전달 비트는 전달 상태만 알려 줍니다. 누구에게 보냈는지는 보낸 편지함의 메시지로 따로 확인합니다.

## 시각 해석

- 플래그 비트에는 시각이 없습니다. 상태가 언제 바뀌었는지는 비트만으로 알 수 없습니다.
- 메시지를 보낸 시각은 mbox 안 메시지의 헤더에 있습니다. 읽는 법은 [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) 과 [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) 에서 다룹니다.
- 흔한 설명대로 폴더 하나가 mbox 파일 하나라면, 파일의 NTFS 시각은 폴더 전체가 마지막으로 바뀐 때입니다. 메시지 한 통의 시각이 아닙니다.
- `global-messages-db.sqlite` 의 시각 단위는 공개 자료가 없습니다. 값을 읽을 때는 같은 메시지의 헤더 시각과 맞춰 단위부터 정합니다([시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)).

## 함정과 한계

1. **지운 메일이 파일에서 사라졌다고 봅니다.** 지운 메시지는 폴더 압축 전까지 `Expunged` 비트가 선 채 남습니다[1]. 휴지통 폴더만 보지 말고 모든 mbox 에서 이 비트를 찾습니다.
2. **압축 뒤에도 파일에 남는다고 봅니다.** 압축하면 지운 메시지가 파일에서 빠진다는 설명이 흔합니다. 자동 압축 기준과 함께 실제 데이터로 확인합니다. 압축 뒤라면 미할당 영역과 섀도 복사본에서 옛 모습을 찾습니다([삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md), [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md)).
3. **헤더에서 `New`·`Offline` 비트를 찾습니다.** 이 두 값과 `Elided` 는 헤더에 적지 않습니다[1]. 헤더에 이 비트가 없다고 새 메시지가 아니었다거나 본문이 PC 에 없었다고 보지 않습니다.
4. **본문이 짧으니 누가 지웠다고 봅니다.** `Partial` 비트는 본문이 잘려 있고 나머지를 POP 서버에서 받아야 한다는 뜻입니다[1]. 이 비트가 서 있으면 본문 일부만 받은 메시지입니다.
5. **IMAP 계정 폴더에 모든 메일이 있다고 봅니다.** IMAP 계정은 "오프라인 사용" 설정일 때만 본문 전체를 받아 둔다는 설명이 흔합니다. `Offline` 비트의 뜻("디스크 캐시에 있음")이 이 설명과 맞습니다[1]. 기본값은 분석 대상의 설정에서 확인합니다. PC 에서 찾지 못한 메일은 서버에 있을 수 있습니다.
6. **`IMAPDeleted` 를 PC 에서 지운 메시지로 봅니다.** 이 비트는 IMAP 서버에서 지움 표시된 메시지입니다[1]. `Expunged` 와 나눠 적습니다.
7. **`.msf` 만 읽습니다.** `.msf` 는 요약 파일이라 지워도 mbox 에서 다시 만든다는 설명이 흔하므로 메시지 원문은 mbox 에서 봅니다. 두 파일의 메시지 수가 다르면 그 차이를 적습니다.
8. **라벨 비트를 `X-Mozilla-Status` 에서 찾습니다.** 라벨은 `X-Mozilla-Status2` 에 적습니다[1].
9. **Maildir 프로필을 mbox 로 읽습니다.** 폴더 자리에 파일 대신 디렉터리가 있고 그 안에 메시지마다 파일이 있으면 Maildir 방식일 수 있습니다. 이 방식의 세부는 실제 데이터로 확인해야 합니다.
10. **원본 프로필을 썬더버드로 엽니다.** 프로그램은 열린 파일을 고칠 수 있습니다. 사본만 엽니다.

## 직접 분석해 보기

### 원시 바이트로 한 번

mbox 는 글자로 된 메시지를 이어 붙인 파일이라 헥스 편집기로 헤더를 바로 찾을 수 있습니다. 아래 바이트는 헤더 이름을 ASCII 로 바꿔 계산한 값입니다. 실제 데이터에서 뽑은 값이 아닙니다.

| 찾을 글자 | 바이트 |
|---|---|
| `X-Mozilla-Status` | `58 2D 4D 6F 7A 69 6C 6C 61 2D 53 74 61 74 75 73` |
| `X-Mozilla-Status2` | 위 바이트 뒤에 `32` |

1. mbox 파일의 사본에서 `X-Mozilla-Status` 바이트를 찾습니다.
2. 콜론 뒤의 16진수 글자를 읽습니다.
3. 읽은 값을 위 플래그 표의 값과 비트 단위로 맞춥니다.

아래는 플래그 표로 만든 풀이 예입니다. 실제 데이터에서 나온 값이 아닙니다.

| 값 | 나눈 비트 | 뜻 |
|---|---|---|
| `0x00001003` | `0x00001000` + `0x00000002` + `0x00000001` | Forwarded + Replied + Read. 읽었고, 답장했고, 전달한 메시지 |
| `0x00000009` | `0x00000008` + `0x00000001` | Expunged + Read. 읽은 뒤 지웠고 압축을 기다리는 메시지 |
| `0x00000401` | `0x00000400` + `0x00000001` | Partial + Read. 본문 일부만 받았고 읽은 메시지 |

두 헤더에 값을 나눠 적는 방법은 공개 자료가 없습니다. 실제 값을 풀기 전에 같은 판으로 재현해 비트 자리를 먼저 맞춥니다.

4. 압축 뒤 지워진 mbox 조각은 미할당 영역에서 같은 바이트로 찾아볼 수 있습니다. 찾은 조각은 앞뒤 헤더로 메시지 경계를 정합니다.

### 공개 도구로 한 번

- mbox 를 읽는 공개 도구나 메일 뷰어로 폴더 파일을 엽니다. 도구가 `Expunged` 메시지를 보여 주는지, 숨기는지 먼저 확인합니다.
- 격리한 가상 머신의 썬더버드에 프로필 사본을 넣고 화면과 파일 내용을 비교합니다.
- `global-messages-db.sqlite`·`abook.sqlite` 는 SQLite 뷰어로 엽니다. 표 이름부터 목록으로 뽑습니다.
- 도구 두 가지로 같은 mbox 의 메시지 수를 세어 비교합니다([도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)).

> 그림 자리: 프로필 폴더 → 계정별 폴더 → mbox·`.msf`·`.sbd` 의 관계(흔한 설명 기준), 그리고 메시지 한 통의 `X-Mozilla-Status` 값을 비트로 푸는 흐름

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) | mbox 안 메시지의 헤더·본문·첨부 |
| [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) | 보낸 시각, 거친 서버 |
| [파이어폭스](../browsers/firefox/index.md) | 저장된 비밀번호 파일의 복호 |
| [설치 프로그램](../system-account/uninstall.md) | 썬더버드가 깔렸던 때와 판 |
| [마스터 파일 테이블](../filesystem/mft.md) · [USN 변경 저널](../filesystem/usnjrnl.md) | mbox 파일이 바뀌고 다시 써진 때 |
| [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) | 압축 전의 mbox |
| [SQLite 데이터베이스](../../01-foundations/database-log-formats/sqlite/index.md) | 검색 색인과 주소록 |

메일로 누구와 연락했는지 정리하는 순서는 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.

## 실습

**직접 만든 가상 머신에 썬더버드를 깔고** 해 봅니다. 이 페이지의 흔한 설명을 확인하는 실습입니다.

1. 프로필 폴더는 어디에 생깁니까? `profiles.ini` 에는 무엇이 적힙니까?
2. 메일을 받고, 읽고, 답장하고, 전달합니다. 그때마다 `X-Mozilla-Status`·`X-Mozilla-Status2` 값이 어떻게 바뀝니까? 값은 몇 자리 16진수로 적힙니까?
3. 메일 하나를 지웁니다. 폴더를 압축하기 전과 뒤의 mbox 를 비교해 보십시오. 지운 메시지는 언제 파일에서 빠집니까?
4. `.msf` 를 지우고 썬더버드를 다시 엽니다. `.msf` 가 다시 생깁니까?
5. IMAP 계정을 더하고 "오프라인 사용" 설정을 켠 경우와 끈 경우를 비교합니다. `ImapMail` 폴더에 본문이 남습니까?

**공개 시험 이미지(NIST CFReDS 등)** 가운데 썬더버드를 쓴 이미지에서도 해 봅니다.

1. 프로필 폴더는 몇 개입니까?
2. `Expunged` 비트가 선 메시지가 있습니까? 있다면 어느 폴더입니까?
3. `global-messages-db.sqlite` 의 메시지 수와 mbox 의 메시지 수가 맞습니까?

## 참고 문헌

1. Mozilla comm-central 소스, `mailnews/base/public/nsMsgMessageFlags.idl` (Searchfox) — https://searchfox.org/comm-central/source/mailnews/base/public/nsMsgMessageFlags.idl
