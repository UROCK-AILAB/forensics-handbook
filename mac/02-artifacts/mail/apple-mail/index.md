---
title: "애플 메일"
parent: "아티팩트 · 메일"
nav_order: 1280
has_children: true
has_toc: false
---

# 애플 메일 (Apple Mail)

macOS 기본 메일 앱인 애플 메일은 사용자 홈의 `~/Library/Mail/V<n>/` 아래에 메시지 본문을 `.emlx` 파일로, 메타데이터를 SQLite 파일 `Envelope Index` 로 나눠 저장하고, 두 쪽은 메시지 번호(ROWID)로 이어집니다 [1][2][3].

## 왜 중요한가

메일에는 누가 누구와 무엇을 주고받았는지와 어떤 파일이 첨부로 오갔는지가 남고, 애플 메일은 메시지 원본 사본을 디스크에 파일로 두는 경우가 많습니다 [2][4]. 그래서 서버에 접근하지 못해도 맥 한 대에서 메일함 구성, 메시지 헤더와 본문, 읽음·답장·전달 같은 상태 값을 함께 볼 수 있습니다. 색인 DB 만 먼저 읽으면 계정·메일함·발신자별 규모를 빠르게 잡을 수 있고, 필요한 메시지만 골라 본문 파일로 내려가는 순서가 편합니다.

다만 이 구조는 공개 도구가 역분석한 결과이고 Apple 이 문서로 밝힌 API 가 아닙니다 [1]. 그래서 보고서에는 어느 도구로 읽었는지와 실제 데이터에서 몇 건을 직접 맞춰 봤는지를 함께 적습니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 저장소 위치 | `~/Library/Mail/V<n>/`, 공개 도구는 번호가 가장 큰 폴더를 현재 저장소로 고름 [2] |
| 본문 | 메시지마다 `.emlx` 파일 하나, 내려받기가 끝나지 않은 메시지는 `.partial.emlx`, Exchange 계정은 본문 파일이 없을 수 있음 [2] |
| 메타데이터 | `MailData/Envelope Index` (확장자 없는 SQLite 파일), 본문 텍스트는 없음 [1][3] |
| 첨부 | 색인 DB 의 `attachments` 표, `.emlx` 상태 값의 첨부 개수, 본문 안 MIME 파트 [3][4] |
| macOS 버전 | 구조가 알려진 폴더는 `V10`, 버전별 번호 대응은 공개 자료 없음 [1] |
| 수집 조건 | 라이브 시스템에서는 전체 디스크 접근 권한 (Full Disk Access)이 필요 [1] |
| 알려 주는 것 | 메시지 헤더·본문, 계정과 메일함, 발신자·받는 사람, 읽음·깃발·답장·전달 상태, 첨부 이름과 개수 |
| 알려 주지 않는 것 | 상태가 바뀐 시각과 바꾼 사람, 사용자가 첨부를 열거나 저장했는지 |
| 공개 도구 예 | emlx (파이썬 `.emlx` 파서) [4], apple-mail-parser (분류 표 읽기) [5], `sqlite3` |

메일 앱의 샌드박스 컨테이너 쪽 경로와 메일 활동이 남는 통합 로그 항목은 공개된 분석 자료가 없어 실제 데이터로 확인해야 합니다.

> 그림 자리: `V<n>` 폴더 아래에서 `MailData/Envelope Index` 의 `messages` 행과 `.mbox` 폴더 속 `.emlx` 파일이 ROWID 와 메일함 URL 로 이어지는 모습

## 읽는 순서

1. [저장 구조 (emlx·V10)](storage.md) — 계정·메일함 폴더를 거쳐 `.emlx` 파일까지 내려가는 경로와 나눔 폴더 규칙, `.emlx` 한 파일의 세 부분과 `flags` 비트를 다룹니다.
2. [메일 색인 DB (Envelope Index)](envelope-index.md) — 메시지·제목·주소·메일함 표를 잇는 법과 분류 표, 시각 열의 기준을 정하는 법, WAL 을 챙겨 수집하는 법을 다룹니다.
3. [첨부 파일 (Attachments)](attachments.md) — 색인 DB·상태 값·MIME 파트 세 곳에서 첨부를 찾아 맞춰 보는 법과 공개 자료가 없는 저장 위치를 다룹니다.

## 함께 볼 페이지

- [아웃룩 (Outlook for Mac)](../outlook.md), [썬더버드 (Thunderbird)](../thunderbird.md) — 같은 맥에 다른 메일 앱이 있을 때
- [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) — 색인 DB 의 저장 형식과 WAL
- [속성 목록 파일 (Property List)](../../../01-foundations/data-formats/plist/index.md) — `.emlx` 끝부분의 형식
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 색인 DB 의 날짜 열을 풀 때
- [개인 정보 보호 권한 (TCC)](../../credentials/tcc/index.md) — 전체 디스크 접근 권한 기록
- [격리 속성과 다운로드 기록 (Quarantine)](../../filesystem/quarantine/index.md) — 메일에서 저장한 첨부의 출처를 볼 때
- [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md)
- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)

## 참고 문헌

1. Inkvi/apple-mail-mcp (Envelope Index + .emlx 읽기 도구 README) — https://github.com/Inkvi/apple-mail-mcp
2. Inkvi/apple-mail-mcp — src/store/paths.ts (저장소 루트·.emlx 경로 계산 코드) — https://raw.githubusercontent.com/Inkvi/apple-mail-mcp/main/src/store/paths.ts
3. Inkvi/apple-mail-mcp — src/store/probe.ts (필수 표·칸 목록) — https://raw.githubusercontent.com/Inkvi/apple-mail-mcp/main/src/store/probe.ts
4. mikez/emlx — emlx.py (Python .emlx 파서 소스) — https://raw.githubusercontent.com/mikez/emlx/master/emlx/emlx.py
5. maxgribov/apple-mail-parser (Envelope Index 분류 파서 README) — https://github.com/maxgribov/apple-mail-parser
