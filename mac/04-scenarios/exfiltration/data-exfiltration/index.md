---
title: "자료를 밖으로 빼돌렸나"
parent: "시나리오 · 정보 유출"
nav_order: 2440
has_children: true
has_toc: false
---

# 자료를 밖으로 빼돌렸나 (Data Exfiltration)

맥에 있던 자료가 USB·에어드롭·클라우드·메일·메신저·웹·아이폰·인쇄 가운데 어느 길로 나갔는지, 길마다 남는 흔적을 모아 판단하는 조사 시나리오 모음입니다.

## 왜 중요한가

정보 유출 사건에서는 "자료가 나갔는가"와 "어느 길로 나갔는가"를 함께 묻고, 길마다 흔적이 남는 곳이 달라서 한 길만 보면 다른 길을 놓칩니다. 그래서 아래 표로 길마다 먼저 볼 곳을 잡고, 하위 페이지에서 길 하나씩 조사 순서를 따라갑니다.

길을 가리지 않고 쓰는 판단 원칙이 하나 있습니다. "파일이 나갔다"는 사실은 흔적 하나로 증명하기 어려워서, 파일을 다룬 흔적(최근 항목·FSEvents), 경로 흔적(장치·앱·서버 기록), 두 흔적의 시각 세 가지가 서로 맞는지로 판단합니다. 하위 페이지의 분석 흐름도 이 원칙을 따릅니다. 흔적이 없을 때 지웠다고 곧바로 보지 않고, 지운 흔적은 [증거를 없애려 했나](../../activity/anti-forensics/index.md)의 방법으로 따로 찾습니다. 기록이 말하는 만큼만 보고서에 쓰는 방법은 [포렌식 보고서](../../../03-techniques/reporting/forensic-report.md)에 있습니다.

수집할 때도 주의할 점이 있습니다. ForensicArtifacts 정의(macos.yaml)에는 CUPS 인쇄, 에어드롭, 드롭박스·구글 드라이브·원드라이브·박스, 사파리 다운로드 항목이 없습니다 [1]. 수집 도구가 이 정의만 쓴다면 이 흔적들이 자동 수집에서 빠질 수 있으므로, 수집 목록에 들어 있는지 직접 확인합니다([맥 증거 확보](../../../03-techniques/process-acquisition/evidence-acquisition/index.md)).

## 한눈에 보기

| 길 | 먼저 볼 위치 | macOS 버전 | 알려 주는 것 |
|---|---|---|---|
| USB | 통합 로그의 DiskArbitration 메시지, `/private/var/db/volinfo.database`, `~/Library/Preferences/com.apple.sidebarlists.plist` [1] | 검체에서 확인 | 외부 볼륨이 연결된 시각과 볼륨 |
| 에어드롭 | 받는 쪽은 받은 파일(기본은 다운로드 폴더) [2]. 보내는 쪽 전용 기록은 공개 자료 없음 | OS X 10.11 이상 맥 [3] | 받은 파일 |
| 클라우드 | `~/Library/Application Support/CloudDocs/session/db/client.db`·`server.db` [4], `~/Library/CloudStorage/` 아래 드롭박스 폴더 [5] | 파일 공급자판 드롭박스는 macOS 12.5 이상 [5] | 동기화 항목과 올린 기기 |
| 메일 | `~/Library/Mail/V[0-9]/...`, `~/Library/Containers/com.apple.mail/Data/Library/Mail Downloads/*` [1] | 검체에서 확인 | 보낸 메일과 첨부 |
| 메신저 | `~/Library/Messages/chat.db`, `~/Library/Messages/Attachments/` [1][6] | 검체에서 확인 | 보낸 메시지와 첨부 |
| 웹 업로드 | 업로드 전용 기록은 공개 자료 없음. 브라우저 방문 기록과 파일 접근 흔적으로 정황을 모음 | 검체에서 확인 | 업로드 사이트 방문과 같은 시간대의 파일 접근 |
| 아이폰 | `~/Library/Preferences/com.apple.iPod.plist`, `~/Library/Application Support/MobileSync/Backup/*` [1][7] | 검체에서 확인 | 연결된 기기와 마지막 연결 시각 |
| 인쇄 | 스풀 폴더 `/var/spool/cups`(제어 파일 c·데이터 파일 d), 로그 폴더 `/var/log/cups/` [8][9] | 검체에서 확인 | 인쇄 작업·요청 계정·인쇄한 앱·시각 |

버전 경계가 알려진 항목은 에어드롭과 드롭박스 두 가지이고, 나머지는 검체의 OS 버전에서 실제 위치를 확인합니다([OS 버전과 설치 기록](../../../02-artifacts/system-account/os-version-install-history.md)).

## 읽는 순서

1. [USB 저장 장치로 (USB)](usb.md) — 외부 볼륨 연결 시각을 확인하고 그 시간대의 파일 흔적을 맞춰 봅니다.
2. [에어드롭으로 (AirDrop)](airdrop.md) — 기기끼리 직접 보낸 경우를 받는 쪽과 보내는 쪽 흔적으로 따집니다.
3. [클라우드로 (Cloud)](cloud.md) — 아이클라우드 드라이브와 드롭박스 같은 동기화 폴더에 넣어 올린 경우를 봅니다.
4. [메일로 (Email)](email.md) — 메일 앱 기록에서 보낸 메일과 첨부를 골라냅니다.
5. [메신저로 (Messenger)](messenger.md) — 메시지 앱에서 내가 보낸 첨부를 찾습니다.
6. [웹 업로드로 (Web Upload)](web-upload.md) — 전용 기록이 없는 브라우저 업로드를 정황으로 모읍니다.
7. [아이폰으로 (iPhone)](iphone.md) — 연결된 아이폰을 확보한 기기와 맞추고 연결 시간대를 봅니다.
8. [인쇄로 (Print)](print.md) — CUPS 스풀 파일과 로그로 인쇄 작업을 재구성합니다.

## 함께 볼 페이지

- [개인정보 파일이 어디 있고 밖으로 나갔나 (PII Exposure)](../pii-exposure.md) — 나간 자료가 개인정보인 경우
- [이 파일을 누가 언제 열었나 (File Access)](../../activity/file-access.md) — 모든 길에서 쓰는 파일 접근 흔적
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../activity/user-attribution.md) — 계정과 실제 사람을 잇는 방법
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 여러 흔적의 시각을 한 줄로 맞추는 방법

## 참고 문헌

1. ForensicArtifacts, "artifacts/data/macos.yaml" — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
2. Apple Support, Mac 사용 설명서 "Use AirDrop to send items to nearby Apple devices" — https://support.apple.com/guide/mac-help/use-airdrop-on-your-mac-mh35868/mac
3. Apple Platform Security, "AirDrop security" — https://support.apple.com/guide/security/airdrop-security-sec2261183f4/web
4. mac_apt, plugins/iCloud.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/iCloud.py
5. Dropbox Help Center, "Expected changes with Dropbox for macOS on File Provider" — https://help.dropbox.com/installs/macos-support-for-expected-changes
6. mac_apt, plugins/imessage.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/imessage.py
7. mac_apt, plugins/iDeviceInfo.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/iDeviceInfo.py
8. mac_apt, plugins/printjobs.py (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/printjobs.py
9. CUPS, "cups-files.conf(5)" — https://www.cups.org/doc/man-cups-files.conf.html
