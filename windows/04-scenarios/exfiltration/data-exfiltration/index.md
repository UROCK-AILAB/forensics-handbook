# 자료를 밖으로 빼돌렸나 (Data Exfiltration)

## 한 줄 요약

PC 의 자료가 USB·휴대폰·메일·메신저·클라우드·웹·인쇄로 밖에 나갔는지를, 여러 흔적을 시각으로 이어 붙여 확인하는 조사 시나리오 묶음입니다.

## 왜 중요한가

- MITRE ATT&CK 은 유출 (Exfiltration, TA0010) 을 "적이 데이터를 훔치려 한다" 로 정의합니다[1].
- 파일을 밖으로 옮겼다는 사실 하나만 적는 기록에 기대기는 어렵습니다. 파일에 접근한 기록(4663)도 파일 접근 감사를 켜 둔 PC 에서만 남습니다([파일 접근 감사](/02-artifacts/event-logs/4656-4663-4660.md)).
- 그래서 장치 연결, 파일 열람, 앱 송신 같은 흔적을 시각으로 이어 붙여 판단합니다.
- 각 흔적은 제 몫만 말합니다. 연결 기록은 장치가 붙었다는 것만, 송신량은 앱이 보낸 양만 보여 줍니다.
- 보고서에는 "파일을 보냈다" 가 아니라 "이 시간대에 이 앱이 이만큼 송신한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 한눈에 보기

| 경로 | 먼저 볼 기록 | 알려 주는 것 | 주의할 점 |
|---|---|---|---|
| USB | USB 장치 기록, 외부 장치 연결 이벤트, 바로가기 파일 | 어느 장치가 언제 붙었고, 그 안의 어떤 파일을 열었나 | 연결 기록은 복사 증거가 아닙니다. |
| 휴대폰 | USB 장치 키, 휴대용 장치(WPD) 키, MTP 드라이버 로그, 휴대폰과 연결 앱 DB | 휴대폰이 언제 붙었나, 휴대폰과 연동한 기록 | MTP 로 붙은 휴대폰은 USBSTOR 에 남지 않습니다. |
| 메일 | .pst·.ost, 새 Outlook 폴더 | 보낸 메일, 받는 사람, 첨부 | 새 Outlook 은 PC 에 캐시만 남을 수 있습니다. |
| 메신저 | 메신저별 대화 DB, SRUM | 파일 전송 메시지, 앱 송신량 | 대화 DB 가 암호화돼 있으면 바로 읽지 못합니다. |
| 클라우드 | 동기화 루트 등록 키, 동기화 폴더 안 파일 상태, 서비스별 동기화 DB | 누가 어느 폴더를 동기화했나, 올린 기록 | 동기화 폴더에 있다는 것은 올렸다는 뜻이 아닙니다. |
| 웹 | 브라우저 방문 기록, SRUM 네트워크 사용량 | 웹메일·웹하드 페이지를 연 시각, 브라우저 송신량 | SRUM 에는 주소 칸과 파일 칸이 없습니다. |
| 인쇄 | 인쇄 이벤트 307, 프린터 목록 | 문서 이름, 프린터, 쪽수 | 인쇄 로그가 켜져 있을 때만 남습니다. |
| 모으기·압축 | $MFT·$UsnJrnl, 압축 프로그램 기록, 프로세스 생성 기록 | 한 폴더로 모은 흔적, 만든 압축 파일 | 압축 프로그램이 없어도 명령줄로 압축할 수 있습니다. |

Windows 판에 따라 달라지는 점과 한 PC 에서 관찰한 범위는 각 하위 페이지에 적었습니다.

### ATT&CK 대응

| 하위 페이지 | ATT&CK |
|---|---|
| USB | T1052.001 Exfiltration over USB[1] |
| 클라우드 | T1567.002 Cloud Storage[1] |
| 웹메일·웹하드 | T1567 Exfiltration Over Web Service[1] |
| 모으고 압축 | T1074 Data Staged[2] |
| 휴대폰 (MTP) | T1052 Exfiltration Over Physical Medium[3]. 이 기법 설명이 드는 매체 예에 휴대폰 (cellular phone) 이 있습니다[3]. |
| 메일·메신저·인쇄 | TA0010 목록에는 딱 맞는 항목이 없습니다[1]. |

TA0010 에는 이 밖에도 C2 채널, 다른 프로토콜, 블루투스, 예약 전송 같은 방법으로 빼내는 기법이 들어 있습니다[1].

## 읽는 순서

1. [USB 로 무엇을 가져갔나 (USB)](/04-scenarios/exfiltration/data-exfiltration/usb.md) — 장치 연결 기록에 이벤트 로그와 장치 안 파일을 연 흔적을 이어 붙입니다.
2. [스마트폰으로 옮겼나 (MTP·Phone Link)](/04-scenarios/exfiltration/data-exfiltration/mtp-phone-link.md) — USB 저장장치로 남지 않는 휴대폰 연결과 휴대폰 연동 앱 기록을 봅니다.
3. [메일로 밖에 보냈나 (Email)](/04-scenarios/exfiltration/data-exfiltration/email.md) — 메일 프로그램의 보낸 메일과 첨부를 봅니다.
4. [메신저로 파일을 보냈나 (Messenger)](/04-scenarios/exfiltration/data-exfiltration/messenger.md) — 메신저 대화 DB 와, 읽지 못할 때 볼 앱 송신량을 다룹니다.
5. [클라우드로 밖에 보냈나 (Cloud)](/04-scenarios/exfiltration/data-exfiltration/cloud.md) — 동기화 앱의 동기화 루트와 파일 상태를 봅니다.
6. [웹메일·웹하드로 올렸나 (Web Upload)](/04-scenarios/exfiltration/data-exfiltration/web-upload.md) — 방문 기록과 SRUM 으로 브라우저 업로드를 봅니다. 앱별 송신량을 읽는 법도 여기 있습니다.
7. [인쇄해서 가져갔나 (Print)](/04-scenarios/exfiltration/data-exfiltration/print.md) — 인쇄 이벤트와 프린터 목록으로 종이 인쇄와 PDF 인쇄를 가립니다.
8. [퇴사 전 자료를 모으고 압축했나 (Staging)](/04-scenarios/exfiltration/data-exfiltration/staging.md) — 내보내기 전에 한 폴더에 모으고 압축한 흔적을 봅니다.

**경로를 모를 때.**

1. 먼저 Staging 페이지를 따라 조사 기간에 모은 폴더와 압축 파일을 찾습니다.
2. 찾은 파일의 이름과 시각을 기준으로 경로별 페이지를 차례로 봅니다.
3. 앱별 송신량(SRUM)은 경로와 상관없이 함께 봅니다.
4. 모든 시각을 UTC 하나로 맞춰 [타임라인](/03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 함께 볼 페이지

- [개인정보 파일이 어디 있고 밖으로 나갔나](/04-scenarios/exfiltration/pii-exposure.md) — 나간 자료가 개인정보 파일일 때 봅니다.
- [이 파일을 누가 언제 열었나](/04-scenarios/activity/file-access.md) · [이 파일은 어디서 왔나](/04-scenarios/activity/file-origin.md) — 파일 하나를 중심으로 흔적을 모읍니다.
- [그 시각에 PC 를 쓴 사람이 누구인가](/04-scenarios/activity/user-attribution.md) — 계정과 사람을 잇습니다.
- [증거를 없애려 했나](/04-scenarios/activity/anti-forensics/index.md) — 내보낸 뒤 흔적을 지웠는지 봅니다.
- [USB 저장장치 흔적](/02-artifacts/external-devices/usb-storage-artifacts/index.md) · [SRUM](/02-artifacts/execution/system-resource-usage-monitor/index.md) · [바로가기 파일](/02-artifacts/file-folder-usage/lnk.md) · [셸백](/02-artifacts/file-folder-usage/shellbags/index.md) — 여러 하위 페이지가 함께 쓰는 아티팩트입니다.
- [파일 접근 감사](/02-artifacts/event-logs/4656-4663-4660.md) · [감사 정책과 로그 설정](/02-artifacts/event-logs/audit-policy-log-settings.md) — 파일 접근 기록이 남는 조건입니다.
- [타임라인 작성](/03-techniques/analysis/timeline/index.md) · [분석 보고서 작성](/03-techniques/reporting/forensic-report.md) — 흔적을 이어 붙이고 보고서에 옮깁니다.

## 참고 문헌

1. MITRE ATT&CK, "Exfiltration" (TA0010) — https://attack.mitre.org/tactics/TA0010/
2. MITRE ATT&CK, "Data Staged" (T1074) — https://attack.mitre.org/techniques/T1074/
3. MITRE ATT&CK, "Exfiltration Over Physical Medium" (T1052) — https://attack.mitre.org/techniques/T1052/
