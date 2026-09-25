---
title: "도구 검증"
parent: "기법 · 보고"
nav_order: 1410
---

# 도구 검증 (Tool Validation)

포렌식 도구가 아이폰 데이터에서 뽑아낸 결과를 원본 파일과 다른 도구로 다시 확인해, 보고서에 싣는 값이 도구 탓에 틀리거나 빠지지 않았는지 보는 방법을 다룹니다.

## 언제 쓰나

결론을 떠받치는 결과를 보고서에 싣기 전에 이 페이지를 봅니다. 도구가 새 버전이거나 검체가 새 iOS 버전일 때, 두 도구의 결과가 서로 다를 때, 도구가 "없음" 이라고 낸 결과를 결론에 쓰려 할 때도 여기서 확인합니다. 도구를 검증하려면 여러 도구의 결과를 비교하고, 도구가 만든 보고서와 도구 화면에 보이는 데이터가 서로 맞는지도 반드시 확인합니다.

여기서 다루는 검증은 도구 하나를 통째로 인증하는 일이 아니라, 이번 사건 보고서에 쓸 항목 하나하나를 원본과 맞춰 보는 일입니다.

## 도구 결과가 어긋나는 곳

도구끼리 결과가 다른 까닭은 대개 어느 항목을 뽑을지, 값을 어떤 기준으로 바꿀지, 찾지 못한 파일을 어떻게 다룰지가 도구마다 달라서입니다. 아래는 검증할 때 먼저 의심해 볼 곳의 예입니다.

| 어긋나는 곳 | 예 | 자세히 |
|---|---|---|
| 뽑는 항목의 범위 | iOS 15 이미지로 도구 세 개를 견준 시험에서, MobileInstallation 로그를 한 상용 도구는 설치 성공 항목만, 다른 상용 도구는 설치·제거 항목 모두, iLEAPP 는 재부팅 관련 항목까지 뽑았습니다. | [설치된 앱](../../02-artifacts/app-usage/installed-apps.md) |
| 지운 레코드 복원 | 지운 레코드 278개가 든 SQLite DB 27개로 시험한 연구에서 bring2lite 는 52.9% 를 되살렸고, FQLite 는 이 시험에서 전부 되살렸습니다. 이 연구는 FQLite 를 만든 사람들이 쓴 것이라, 결과도 검증 대상으로 봅니다. | [삭제 데이터 복구](../analysis/data-recovery/index.md) |
| 시각 형식의 이름 | iLEAPP 가 "webkit 시각" 이라 부르는 변환은 값에 978307200 을 더하는 Mac 절대 시각 기준이고, 1601년 기준 형식이 아닙니다. 같은 이름이 도구마다 다른 기준을 가리킬 수 있습니다. | [시각 값](../../01-foundations/value-decoding/time-values.md) |
| 시각 단위 추정 | iLEAPP 의 Unix 시각 변환 함수는 값의 크기로 초·밀리초·마이크로초·나노초를 가립니다. | [시각 값](../../01-foundations/value-decoding/time-values.md) |
| 시간대 가정 | iLEAPP 는 plist 날짜를 시간대 정보 없이 UTC 로 보고 변환합니다. | [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md) |
| 한 칸에 섞인 단위 | iOS 11 부터 `sms.db` 의 시각 칸에 9자리(초)와 18자리(나노초) Mac 절대 값이 같은 칸 안에서도 섞여 들어갑니다. | [메시지](../../02-artifacts/communications/messages/index.md) |
| 말없이 빠지는 파일 | 백업에서 메시지 첨부는 `MediaDomain` 에 있고, 도메인을 잘못 넣어 파일 이름(fileID)을 계산하면 오류 없이 첨부를 모두 못 찾습니다. iLEAPP 의 메시지 모듈은 폴더로 된 묶음 첨부를 결과에 넣지 않고 처리 로그에 한 줄만 남기므로, 결과 화면만 보면 빠진 줄 모릅니다. | [메시지](../../02-artifacts/communications/messages/index.md) |
| 풀지 않은 값 | 통합 로그를 읽는 `macos-UnifiedLogs` 는 printf `%m` 같은 오류 코드를 글로 바꾸지 않고, 지원하지 않는 객체는 base64 로 남깁니다. | [통합 로그 형식](../../01-foundations/data-formats/unified-log.md) |
| 문서와 다른 위치 | MVT 문서는 전체 파일 시스템에서 앱의 WebKit LocalStorage 를 앱 컨테이너의 `Library/WebKit/WebsiteData/LocalStorage/` 아래로 적지만, 백업에서는 `Library/WebKit/WebsiteData/Default/` 아래 해시 폴더 두 단계 밑에 `LocalStorage/localstorage.sqlite` 가 있습니다. | [앱 데이터 분석](../analysis/app-data-analysis/index.md) |

iLEAPP 에 관한 내용은 main 브랜치 코드 기준이라, 검증할 때는 실제로 쓴 버전의 코드를 다시 봅니다. 공개 연구의 해석도 검증 대상입니다. 복원·이전 흔적을 다룬 한 연구는 시험을 두 번만 한 결과라서, 중요한 사건이면 직접 재현 시험을 합니다.

## 절차

1. **도구와 입력을 적습니다.** 도구 이름·버전·설정과, 도구에 넣은 결과물의 해시를 적습니다.
2. **검증할 항목을 고릅니다.** 결론을 떠받치는 값, 시각, 도구가 "없음" 이라고 낸 결과를 먼저 고릅니다.
3. **도구 안에서 먼저 맞춰 봅니다.** 도구 화면과 도구가 만든 보고서, 내보낸 파일이 같은 값을 보여 주는지 확인합니다.
4. **원본 파일로 되돌아갑니다.** 로컬 백업이면 `Manifest.db` 의 `Files` 표에서 도메인과 상대 경로로 파일 이름(fileID)을 찾아 그 파일의 사본을 엽니다. 백업 구조는 [로컬 백업](../../01-foundations/backups/local-backup/index.md)에서 다룹니다.
5. **원본 값을 직접 읽습니다.** SQLite 는 `sqlite3` 로 쿼리하고, plist 는 [속성 목록 파일](../../01-foundations/data-formats/plist.md)에 나온 방법으로 읽고, 시각은 원본 값과 기준으로 직접 계산합니다.
6. **두 번째 도구로 같은 항목을 뽑습니다.** 가능하면 해석 방식이 다른 도구를 고릅니다.
7. **차이가 나면 까닭을 찾습니다.** 위 표의 어긋나는 곳부터 차례로 맞춰 보고, 까닭을 찾지 못하면 찾지 못했다고 적습니다.
8. **검증 기록을 남깁니다.** 아래 "검증 기록 남기기" 의 표를 채워 보고서 부록에 붙입니다.

## 직접 확인해 보기

아래는 로컬 백업 사본에서 메시지 DB 하나를 찾아 도구가 낸 행 수와 맞춰 보는 예입니다. 메시지 DB 는 `HomeDomain` 의 `Library/SMS/sms.db` 에 있고, `Manifest.db` 의 `Files` 표 칸은 `fileID, domain, relativePath, flags, file` 입니다.

```
# 1) Manifest.db 를 -wal·-shm 까지 함께 복사한 사본에서 fileID 를 찾는다
sqlite3 Manifest-copy.db "SELECT fileID, domain, relativePath FROM Files WHERE domain='HomeDomain' AND relativePath='Library/SMS/sms.db';"

# 2) fileID 는 '도메인-상대경로' 의 SHA-1 이라 직접 계산해 1)과 맞춰 볼 수 있다
printf 'HomeDomain-Library/SMS/sms.db' | sha1sum

# 3) fileID 앞 두 글자 폴더 안의 파일을 사본으로 복사해 연다
cp <백업 폴더>/<fileID 앞 두 글자>/<fileID> sms-copy.db
sqlite3 sms-copy.db "SELECT COUNT(*) FROM message;"

# 4) Mac 절대 초를 UTC 로 바꿔 도구가 보여 준 시각과 맞춘다
#    (700000000 은 명세로 만든 예시 값이고 검체 값이 아니다)
sqlite3 :memory: "SELECT datetime(700000000 + 978307200, 'unixepoch');"
# 2023-03-08 20:26:40
```

1)과 2)의 값이 같으면 도구가 찾은 파일과 직접 찾은 파일이 같은지 확인할 수 있고, 3)의 행 수가 도구 결과보다 많으면 도구가 어떤 행을 걸렀는지 찾아봅니다. 원본을 바로 열면 WAL 내용이 본 파일에 옮겨 적힐 수 있어서 늘 사본으로 작업하고, 이 동작은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다. 4)에서 원본 값이 18자리라면 나노초 값일 수 있으니 10^9 로 나눈 뒤 더합니다.

## 검증 기록 남기기

항목마다 한 줄씩 남기면 보고서를 읽는 사람이 같은 확인을 다시 해 볼 수 있습니다.

| 칸 | 적을 것 |
|---|---|
| 항목 | 보고서의 어느 발견 사항인지 |
| 도구·버전 | 처음 결과를 낸 도구와 버전, 설정 |
| 도구 값 | 도구가 보여 준 값 그대로 |
| 원본 위치 | 도메인·경로·표·칸, 행을 찾은 쿼리 |
| 직접 확인 값 | 원본에서 읽은 값과 변환 식 |
| 두 번째 도구 값 | 도구 이름·버전과 값 |
| 판단 | 일치, 불일치(까닭), 확인 못 함 |

## 도구

원본을 직접 읽는 데는 SQLite 공식 명령 줄 도구 `sqlite3` 와 해시 도구(`sha1sum`, `sha256sum`)면 충분합니다. 결과를 견줄 공개 도구로는 백업·파일 시스템 결과물을 읽는 iLEAPP, 백업에서 흔적과 지표를 대조하는 MVT, 통합 로그를 읽는 `macos-UnifiedLogs`, 지운 SQLite 레코드를 되살리는 FQLite·bring2lite 가 있습니다. 어느 도구도 기준으로 삼지 않고, 원본에서 직접 읽은 값을 기준으로 둡니다.

## 함정과 한계

**두 도구가 같은 답을 내도 둘 다 틀릴 수 있습니다.** 두 도구가 같은 변환 기준이나 같은 공개 코드를 쓰면 같은 실수를 함께 합니다. 두 번째 도구는 해석 방식이 다른 것으로 고르고, 원본 값을 직접 읽는 단계를 건너뛰지 않습니다.

**도구가 낸 "없음" 은 검증하기 가장 어렵습니다.** 위 표처럼 도구는 도메인을 잘못 잡거나 지원하지 않는 형식을 만나도 오류 없이 빈 결과를 낼 수 있어서, 없다는 결과는 원본 DB 를 직접 열어 행이 정말 없는지까지 봐야 결론에 쓸 수 있습니다.

**검증은 항목 단위입니다.** 한 항목이 원본과 맞았다고 그 도구의 다른 결과까지 믿을 근거가 생기지는 않습니다. 검증한 항목과 하지 않은 항목을 보고서에서 나눠 적습니다.

**도구끼리 해시를 대조하기는 어렵습니다.** 도구마다 보고 형식이 달라 도구 간 해시 대조가 어렵고, 해시가 어긋나면 항목 단위로 비교합니다. 해시 기록 방법은 [모바일 증거 확보](../acquisition/mobile-acquisition/index.md) 아래 페이지에서 다룹니다.

**새 iOS 버전에서는 위치부터 맞춰 봅니다.** 위 표의 LocalStorage 예처럼 문서나 도구가 기대하는 경로가 실제 백업과 다를 수 있어서, 도구가 읽는 경로·표·칸 이름이 검체에 실제로 있는지 먼저 확인합니다.

## 결과를 어떻게 해석하나

원본에서 직접 읽은 값과 도구 값이 맞으면 그 항목에 한해 도구 값을 보고서에 쓸 근거가 생기고, 보고서에는 "원본에서 직접 확인" 이라고 표시합니다. 둘이 다르면 원본 값을 기준으로 쓰고 도구 값과 차이, 그리고 찾은 까닭을 함께 적습니다. 까닭을 찾지 못한 차이는 결론의 근거로 쓰지 않고 한계로 적습니다. 검증하지 못한 도구 결과를 써야 하면 "도구 결과, 원본 확인 안 함" 이라고 밝혀, 읽는 사람이 근거의 무게를 가늠할 수 있게 합니다. 보고서에 싣는 형식은 [포렌식 보고서](forensic-report.md)에서 다룹니다.

## 참고 문헌

- NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
- iOS 15 Image Forensics Analysis and Tools Comparison - Processing details and general device information — blog.digital-forensics.it (2023-09) — https://blog.digital-forensics.it/2023/09/ios-15-image-forensics-analysis-and.html
- Dirk Pawlaszczyk, Christian Hummert, "Making the Invisible Visible – Techniques for Recovering Deleted SQLite Data Records", International Journal of Cyber Forensics and Advanced Threat Investigations 1(1-3), 27-41, 2021 — https://conceptechint.net/index.php/CFATI/article/download/17/6
- iLEAPP (Alexis Brignoni) — scripts/ilapfuncs.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/ilapfuncs.py
- iLEAPP (Alexis Brignoni) — scripts/artifacts/sms.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/sms.py
- Time is NOT on our side when it comes to messages in iOS 11 — Smarter Forensics (2017-09) — https://smarterforensics.com/2017/09/time-is-not-on-our-side-when-it-comes-to-messages-in-ios-11/
- ChatExport/ChatExportKnowledge attachments.md — https://raw.githubusercontent.com/ChatExport/ChatExportKnowledge/main/attachments.md
- Mandiant, macos-UnifiedLogs (GitHub README) — https://github.com/mandiant/macos-UnifiedLogs
- MVT 문서, iOS Records — https://docs.mvt.re/en/latest/ios/records/
- Device Set-up – Transferring data to new iPhone & Effects to Photos.sqlite — The Forensic Scooter (2024-02) — https://theforensicscooter.com/2024/02/04/device-setup-transferring-data-to-new-iphone-effects-to-photos-sqlite/
- Reverse Engineering the iOS Backup — Rich Infante (2017) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
