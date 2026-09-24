---
title: "악성코드는 어디서 들어왔나"
parent: "시나리오 · 침해 사고"
nav_order: 3680
---

# 악성코드는 어디서 들어왔나 (Initial Access)

이 페이지는 악성코드가 PC 에 처음 들어온 길을 거슬러 찾는 순서를 다룹니다. 메일 첨부, 메일·메신저 링크, 웹 방문, 원격 접속, USB 가운데 어느 길인지 가립니다. 파일 하나의 출처를 가리는 기본 순서는 [이 파일은 어디서 왔나](../activity/file-origin.md) 에 있습니다. 이 페이지는 그 순서를 침해 사고에 맞춰 쓰는 법과 오피스 매크로 차단을 다룹니다. 원격 데스크톱과 원격 제어 프로그램으로 들어온 경우는 [원격 데스크톱 침입 확인](rdp-intrusion.md) 과 [원격 제어 프로그램으로 누가 조작했나](remote-access-tool-abuse.md) 에서 다룹니다.

## 조사 질문

- 악성코드는 어떤 길로 이 PC 에 처음 들어왔습니까?
- 처음 들어온 파일은 무엇이고, 어느 계정에서 언제 실행됐습니까?
- 그 파일이 다음 단계 파일을 내려받거나 다른 프로그램을 설치했습니까?
- 문서 매크로가 실행됐다면, 매크로 차단은 왜 막지 못했습니까?

## 들어오는 길 나누기

MITRE ATT&CK 은 처음 들어오는 단계를 초기 접근 (Initial Access) 전술(TA0001)로 묶습니다[1]. 사용자 PC 한 대를 분석할 때는 보통 아래 다섯 갈래를 먼저 가립니다. 갈래와 기법을 짝지은 것은 이 위키의 정리입니다.

| 갈래 | 가까운 ATT&CK 기법 | 이 PC 에서 먼저 볼 흔적 |
|---|---|---|
| 메일 첨부 | T1566.001 첨부 파일 피싱 (Spearphishing Attachment) | 메일 데이터, 첨부 임시 폴더, 출처 표시 |
| 메일·메신저 링크로 받은 파일 | T1566.002 링크 피싱 (Spearphishing Link), T1566.003 제3자 서비스 피싱 (Spearphishing via Service) | 브라우저 다운로드 기록, 출처 표시 |
| 웹 방문 중 받은 파일 | T1189 Drive-by Compromise | 브라우저 방문·다운로드 기록 |
| 원격 접속 | T1133 외부 원격 서비스 (External Remote Services), T1078 유효 계정 (Valid Accounts) | 로그온 이벤트, 원격 데스크톱 이벤트, 원격 제어 프로그램 흔적 |
| USB | T1091 이동식 매체를 통한 복제 (Replication Through Removable Media) | USB 저장장치 흔적, 바로가기 파일 |

- T1566.003 은 회사 메일이 아닌 제3자 서비스로 보내는 피싱입니다[1]. 피싱 아래에는 전화로 속이는 T1566.004 도 있습니다[1].
- T1133 은 VPN·Citrix 같은 원격 접속 서비스로 처음 들어오거나 계속 머무는 기법입니다[1].
- T1078 은 이미 있는 계정의 자격 증명을 얻어 쓰는 기법입니다[1]. 하위 기법은 기본 계정, 도메인 계정, 로컬 계정, 클라우드 계정입니다[1].
- MITRE 는 T1091 을 이동식 매체에 악성코드를 복사해 자동 실행 기능을 노리는 기법으로 설명합니다[1].
- 이 전술에는 공개 서버 취약점 이용(T1190), 공급망 침해(T1195), 신뢰 관계(T1199), 하드웨어 추가(T1200), 콘텐츠 주입(T1659), Wi-Fi 네트워크(T1669)도 들어 있습니다[1]. 이 페이지는 이 기법들을 따로 다루지 않습니다.

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| Windows 버전 | 버전과 빌드를 [시스템 기본 정보](../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 에서 먼저 적습니다. |
| 시간대 | 메일·브라우저·이벤트 로그·파일 시스템의 시각 기준이 서로 다릅니다. [시간대 설정](../../02-artifacts/system-account/time-zone.md) 을 읽습니다. Bias 값을 부호 있는 수로 읽는 법은 [이 파일을 누가 언제 열었나](../activity/file-access.md) 의 "먼저 확인할 것" 에 있습니다. |
| 사용자와 권한 | 대상 계정과 그 계정이 로컬 관리자였는지 적습니다. 한 공개 사례에서는 사용자가 로컬 관리자여서 첫 파일의 설치가 성공했습니다[2]. 보고서는 권한이 낮은 사용자였다면 설치가 실패했을 것이라고 적었습니다[2]. 계정은 [사용자 계정](../../02-artifacts/system-account/sam.md) 에서 봅니다. |
| Office 버전과 업데이트 채널 | 인터넷에서 온 문서의 매크로를 기본으로 막는 변경은 채널과 버전마다 적용 시기가 다릅니다[3]. 아래 "오피스 매크로 차단" 절의 표와 맞춰 봅니다. |
| 파일 시스템 | 웹 표시 (Mark of the Web, MOTW) 는 NTFS 에 저장한 파일에만 붙습니다[3]. FAT32 로 포맷한 장치에 저장한 파일에는 붙지 않습니다[3]. |
| 감사 정책·Sysmon | 이벤트 기록은 감사 정책과 Sysmon 설정에 따라 남기도 하고 안 남기도 합니다. 기록이 없다고 해서 일이 없었다고 읽지 않습니다. [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 확인합니다. |
| 수집 범위 | 의심 파일과 그 스트림, 사용자 프로필의 메일·브라우저 데이터, $MFT, $UsnJrnl:$J, 이벤트 로그, 레지스트리 하이브를 함께 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 실행 흔적 | 악성 파일의 경로, 실행 시각의 단서 | [프리페치](../../02-artifacts/execution/prefetch/index.md) · [AmCache](../../02-artifacts/execution/amcache-hve/index.md) |
| 2 | 출처 표시 (Zone.Identifier) | 인터넷 영역에서 온 파일인지 | [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) |
| 3 | 브라우저 방문·다운로드 기록 | 받은 주소, 받은 시각, 저장 경로 | [방문·다운로드 기록 (크롬 계열)](../../02-artifacts/browsers/chrome-edge-whale/history.md) · [places.sqlite (파이어폭스)](../../02-artifacts/browsers/firefox/places-sqlite.md) |
| 4 | 메일 데이터·첨부 임시 폴더 | 첨부 파일, 보낸 곳, 받은 시각 | [아웃룩](../../02-artifacts/mail/outlook/index.md) · [첨부 임시 폴더](../../02-artifacts/mail/outlook/olk-content-outlook.md) · [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) |
| 5 | 오피스 흔적 | 신뢰 문서 기록, 매크로 내용, 오피스가 띄운 경고 | [신뢰 문서 기록](../../02-artifacts/file-folder-usage/microsoft-office/trust-records.md) · [오피스 매크로](../../02-artifacts/embedded-metadata/vba-macro.md) · [오피스 경고](../../02-artifacts/event-logs/oalerts.md) |
| 6 | 바로가기 파일 | 파일을 열었을 때의 볼륨 정보 | [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) |
| 7 | USB 저장장치 흔적 | 장치를 연결한 시각 | [USB 저장장치 흔적](../../02-artifacts/external-devices/usb-storage-artifacts/index.md) |
| 8 | 원격 접속 흔적 | 원격 데스크톱·원격 제어 프로그램 접속 | [원격 데스크톱 침입 확인](rdp-intrusion.md) · [원격 제어 프로그램으로 누가 조작했나](remote-access-tool-abuse.md) |

악성으로 확인된 파일(1)에서 시작해 거꾸로 올라갑니다. 2~3 은 인터넷 갈래, 4~5 는 메일 갈래, 6~7 은 USB 갈래입니다. 셋 다 막히면 8 을 봅니다.

## 오피스 매크로 차단

Office 는 인터넷에서 온 파일의 VBA 매크로를 기본으로 막도록 바뀌었고, 메일 첨부도 인터넷에서 온 파일에 듭니다[3]. 막힌 파일을 열면 사용자는 [보안 위험] (SECURITY RISK) 배너를 봅니다[3].

**적용 범위.**

- 이 변경은 Windows 의 Office 에만 적용됩니다[3]. Mac·Android·iOS·웹 Office 는 해당하지 않습니다[3].
- 대상 앱은 Access·Excel·PowerPoint·Project·Publisher·Visio·Word 입니다[3].

| 앱 | 업데이트 채널 | 버전 | 적용 시작 |
|---|---|---|---|
| Access·Excel·PowerPoint·Visio·Word | Current Channel | 2206 | 2022-07-27 (배포 시작) |
| Access·Excel·PowerPoint·Visio·Word | Monthly Enterprise Channel | 2208 | 2022-10-11 |
| Access·Excel·PowerPoint·Visio·Word | Semi-Annual Enterprise Channel | 2208 | 2023-01-10 |
| Publisher | 모든 채널 | Current Channel 2301 등 | 2023-02-14 |
| Project | 모든 채널 | Current Channel 2407 등 | 2024-08-13 |

(표는 [3] 에서 옮겼습니다.)

**변경 전과 뒤.**

변경 전에는 MOTW 가 붙은 파일을 열면 [보안 경고] (SECURITY WARNING) 배너와 [콘텐츠 사용] (Enable content) 단추가 나왔고, 이 단추를 누르면 그 파일은 신뢰 문서 (Trusted Document) 가 되어 매크로가 실행됐습니다[3]. 변경 전에 [콘텐츠 사용] 을 눌러 둔 파일은 신뢰 문서로 남아 있어서 변경 뒤에도 그 파일의 매크로는 실행됩니다[3]. 새 [보안 위험] 배너에는 [콘텐츠 사용] 단추가 없습니다[3].

**차단을 건너뛰는 경우.**

- 사용자가 파일 속성에서 [차단 해제] (Unblock) 를 누르면 MOTW 가 지워집니다[3]. 정책이나 보안 센터 설정이 막지 않으면 매크로가 실행됩니다[3].
- 파일 속성 [일반] 탭의 [차단 해제] 확인란과 PowerShell 의 Unblock-File 은 같은 일을 합니다[3]. 둘 다 파일에서 ZoneId 값을 지웁니다[3].
- 신뢰할 수 있는 위치 (Trusted Location) 에 저장한 파일은 MOTW 검사를 건너뜁니다[3]. 이 파일은 매크로가 켜진 채 열립니다[3].
- IP 주소로 연 네트워크 공유의 파일은 신뢰할 수 있는 사이트나 로컬 인트라넷 영역에 들어 있지 않으면 매크로가 막힙니다[3].

**MOTW 가 처음부터 없는 경우.** 기본 설정에서 MOTW 는 인터넷 영역이나 제한된 사이트 (Restricted sites) 영역에서 온 파일에만 붙습니다[3]. Microsoft 문서는 아래 경우에 MOTW 가 없다고 적습니다[3].

- OneDrive·SharePoint 웹에서 [데스크톱 앱에서 열기] 로 연 파일
- OneDrive 동기화 클라이언트가 내려받은 파일
- OneDrive 로 동기화하는 알려진 폴더(바탕 화면·문서·사진·스크린샷·카메라 앨범)의 파일
- FAT32 로 포맷한 장치에 저장한 파일

브라우저로 OneDrive·SharePoint 파일을 내려받을 때는 인터넷 보안 영역 설정에 따라 MOTW 가 붙습니다[3]. 예를 들어 Microsoft Edge 는 인터넷 영역 파일에 MOTW 를 붙입니다[3]. ZoneId 값의 뜻과 스트림 구조는 [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) 에 있습니다.

**매크로 가설을 세울 때 함께 볼 것.** "인터넷에서 받은 문서의 매크로가 실행됐다" 는 가설을 세우면 아래를 함께 봅니다.

1. Office 버전과 업데이트 채널 — 기본 차단이 적용된 버전인지 위 표와 맞춥니다.
2. 문서의 ZoneId — [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) 에서 읽습니다.
3. 차단 해제 흔적 — 파일에서 ZoneId 값이 지워졌는지 봅니다. 같은 페이지의 "시각 해석" 절을 따릅니다.
4. 신뢰 문서 기록 — [신뢰 문서 기록](../../02-artifacts/file-folder-usage/microsoft-office/trust-records.md) 에서 그 문서 경로를 찾습니다.
5. 신뢰할 수 있는 위치 — 설정된 위치와 문서가 저장된 폴더를 맞춥니다.
6. 매크로 내용 — [오피스 매크로](../../02-artifacts/embedded-metadata/vba-macro.md) 에서 무엇을 하려 했는지 봅니다.

## 공개 사례에서 본 첫 파일

아래 두 공개 사례에서 처음 들어온 파일은 악성코드 본체가 아니라 다음 단계를 내려받거나 설치하는 파일이었습니다.

- CISA 권고 AA23-025A 에서는 헬프데스크를 사칭한 피싱 메일이 받는 사람을 악성 도메인으로 보냈습니다[4]. 그 사이트를 방문하면 실행 파일을 내려받게 됐습니다[4]. 이 실행 파일은 두 번째 악성 도메인에 접속해 원격 관리 (Remote Monitoring and Management, RMM) 프로그램을 더 내려받았습니다[4].
- The DFIR Report 사례(2023-09-25 공개)에서는 사용자가 메일 링크로 문서처럼 꾸민 실행 파일(document8765.exe)을 내려받았습니다[2]. 이 파일은 %TEMP% 에 MSI 를 풀었습니다[2]. 그리고 msiexec.exe 로 그 MSI 를 실행해 정상 원격 관리 프로그램(ScreenConnect)을 설치했습니다[2].

그래서 첫 파일을 찾아도 거기서 멈추지 않습니다. 그 파일이 뒤이어 내려받거나 설치한 것으로 사슬을 이어 갑니다. 거꾸로, 가장 먼저 눈에 띈 파일이 사슬의 첫 고리라고 단정하지도 않습니다.

## 분석 흐름

1. Windows 버전·시간대·대상 계정과 그 계정의 권한을 정리합니다. Office 버전과 업데이트 채널도 적습니다.
2. 악성으로 확인된 파일에서 시작합니다. [프리페치](../../02-artifacts/execution/prefetch/index.md) 와 [AmCache](../../02-artifacts/execution/amcache-hve/index.md) 로 경로와 실행 시각의 단서를 모읍니다. 실행 흔적을 읽는 순서는 [어떤 프로그램을 언제 실행했나](../activity/program-execution.md) 에 있습니다.
3. 그 파일을 만든 프로세스를 거슬러 올라갑니다. 프로세스 생성 기록이 있으면 부모 프로세스를 봅니다. 기록의 칸은 [프로세스 생성](../../02-artifacts/event-logs/4688.md) 과 [프로세스 생성 (Sysmon 1)](../../02-artifacts/event-logs/sysmon/1.md) 에 있습니다. 가장 먼저 생긴 관련 파일이 나올 때까지 되풀이합니다.
4. 가장 먼저 생긴 파일의 출처 표시와 브라우저 다운로드 기록을 봅니다. 순서는 [이 파일은 어디서 왔나](../activity/file-origin.md) 를 따릅니다.
5. 출처가 메일로 보이면 메일 데이터와 첨부 임시 폴더에서 같은 이름·크기·해시의 첨부를 찾습니다. 보낸 곳은 [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) 으로 확인합니다.
6. 첫 파일이 매크로 문서면 위 "매크로 가설을 세울 때 함께 볼 것" 을 차례로 확인합니다.
7. 출처 표시도, 다운로드 기록도, 메일도 없으면 USB 와 원격 접속 갈래를 봅니다. 그 전에 아래 흔한 오판 1 의 경우인지 먼저 가립니다.
8. 첫 파일 뒤에 설치된 프로그램·서비스·자동실행 항목을 찾습니다. [악성코드 지속성(자동실행) 찾기](persistence.md) 와 [원격 제어 프로그램으로 누가 조작했나](remote-access-tool-abuse.md) 로 이어 갑니다.
9. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올립니다. "처음 들어온 시각" 과 "처음 눈에 띈 파일의 실행 시각" 을 나눠 적습니다.

## 흔한 오판

1. **Zone.Identifier 가 없으니 인터넷에서 온 파일이 아니라고 봅니다.** FAT32 에 저장한 파일, OneDrive 로 동기화한 파일, [데스크톱 앱에서 열기] 로 연 파일에는 처음부터 MOTW 가 없습니다[3]. 차단 해제를 하면 ZoneId 가 지워집니다[3].
2. **ZoneId 3 이면 사용자가 브라우저로 직접 내려받았다고 봅니다.** ZoneId 3 은 인터넷 영역이라는 뜻입니다[3]. 영역만 알려 줄 뿐, 받은 방법은 알려 주지 않습니다. 메일 첨부에도 MOTW 가 붙습니다[3]. 받은 방법은 브라우저 기록과 메일 데이터로 따로 가립니다.
3. **매크로 차단 뒤 버전이니 매크로가 실행될 수 없었다고 봅니다.** 변경 전에 [콘텐츠 사용] 을 누른 신뢰 문서, 신뢰할 수 있는 위치에 둔 파일, 차단 해제한 파일은 차단을 건너뜁니다[3].
4. **악성코드 실행 시각을 침입 시각으로 씁니다.** 한 공개 사례에서는 첫 파일 실행 뒤에 원격 관리 프로그램 설치, 발견, 측면 이동이 이어졌습니다[2]. 가장 먼저 눈에 띈 파일이 첫 파일이 아닐 수 있습니다.

## 보고서 문장 예

- 쓰지 않을 문장: "사용자 ○○ 가 ○○ 에 피싱 메일을 열어 악성코드에 감염됐습니다."
- 쓸 문장: "`○○\Downloads\○○.exe` 에 Zone.Identifier 스트림이 있고, ZoneId 는 3 입니다. 사용자 ○○ 프로필의 ○○ 브라우저 다운로드 기록에 같은 저장 경로의 항목이 있습니다. 이 항목의 끝 시각은 ○○(UTC) 입니다. 이 파일의 실행 흔적 가운데 가장 이른 시각은 ○○(UTC) 입니다. 이 기록은 이 계정의 세션에서 이 브라우저가 인터넷 영역에서 이 파일을 받았음을 보여 줍니다. 어떤 메일이나 메시지를 보고 받았는지는 이 기록만으로 정할 수 없습니다."
- 매크로 문서일 때: "`○○.docm` 의 ZoneId 는 3 입니다. 이 PC 의 Office 는 ○○ 채널 ○○ 버전입니다. 사용자 ○○ 의 신뢰 문서 기록에 이 문서 경로가 있습니다. 이 기록은 이 계정에서 이 문서를 신뢰 문서로 정한 기록이 있음을 보여 줍니다. 매크로가 실행된 시각과 한 일은 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [이 파일은 어디서 왔나](../activity/file-origin.md) — 파일 하나의 출처를 가리는 기본 순서입니다.
- [다운로드 출처 표시](../../02-artifacts/filesystem/zone-identifier.md) — Zone.Identifier 스트림의 구조와 ZoneId 값입니다.
- [방문·다운로드 기록 (크롬 계열)](../../02-artifacts/browsers/chrome-edge-whale/history.md) · [places.sqlite (파이어폭스)](../../02-artifacts/browsers/firefox/places-sqlite.md) — 받은 주소와 시각입니다.
- [아웃룩](../../02-artifacts/mail/outlook/index.md) · [첨부 임시 폴더](../../02-artifacts/mail/outlook/olk-content-outlook.md) · [메일 헤더 분석](../../03-techniques/analysis/email-header-analysis.md) — 메일 첨부 갈래입니다.
- [신뢰 문서 기록](../../02-artifacts/file-folder-usage/microsoft-office/trust-records.md) · [오피스 매크로](../../02-artifacts/embedded-metadata/vba-macro.md) · [오피스 경고](../../02-artifacts/event-logs/oalerts.md) — 매크로 문서 갈래입니다.
- [프리페치](../../02-artifacts/execution/prefetch/index.md) · [AmCache](../../02-artifacts/execution/amcache-hve/index.md) · [바로가기 파일](../../02-artifacts/file-folder-usage/lnk.md) — 실행과 열람 흔적입니다.
- [USB 저장장치 흔적](../../02-artifacts/external-devices/usb-storage-artifacts/index.md) — USB 갈래입니다.
- [원격 데스크톱 침입 확인](rdp-intrusion.md) · [원격 제어 프로그램으로 누가 조작했나](remote-access-tool-abuse.md) — 원격 접속 갈래입니다.
- [악성코드 지속성(자동실행) 찾기](persistence.md) — 첫 파일 뒤에 남긴 자동실행을 찾습니다.

## 참고 문헌

1. MITRE ATT&CK, "Initial Access, Tactic TA0001" (v19, 2025-04-25 수정) — https://attack.mitre.org/tactics/TA0001/
2. The DFIR Report, "From ScreenConnect to Hive Ransomware in 61 hours" (2023-09-25) — https://thedfirreport.com/2023/09/25/from-screenconnect-to-hive-ransomware-in-61-hours/
3. Microsoft Learn, "Macros from the internet are blocked by default in Office" (ms.date 2026-07-17) — https://learn.microsoft.com/en-us/microsoft-365-apps/security/internet-macros-blocked
4. CISA, "Protecting Against Malicious Use of Remote Monitoring and Management Software" (AA23-025A, 2023-01-26 마지막 수정) — https://www.cisa.gov/news-events/cybersecurity-advisories/aa23-025a
