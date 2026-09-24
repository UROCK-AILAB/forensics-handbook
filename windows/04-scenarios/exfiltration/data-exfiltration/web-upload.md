---
title: "웹메일·웹하드로 올렸나"
parent: "자료를 밖으로 빼돌렸나"
grand_parent: "시나리오 · 정보 유출"
nav_order: 3640
---

# 웹메일·웹하드로 올렸나 (Web Upload)

> 상위 허브: [자료를 밖으로 빼돌렸나 (Data Exfiltration)](index.md)

이 페이지는 브라우저로 웹메일에 파일을 첨부하거나 웹하드에 파일을 올렸는지 확인하는 순서를 다룹니다. 웹하드는 브라우저로 파일을 올리고 내려받는 인터넷 저장 공간 서비스입니다. PC 에 설치한 동기화 앱으로 올린 경우는 [클라우드로 밖에 보냈나 (Cloud)](cloud.md) 에서 다룹니다. 메일 프로그램으로 보낸 경우는 [메일로 밖에 보냈나 (Email)](email.md) 에서 다룹니다.

앱별 송신량을 읽는 법은 이 페이지의 "SRUM 네트워크 사용량 읽기" 에서 다룹니다. 다른 하위 페이지도 이 절을 가리킵니다.

"(현장 관찰)" 을 붙인 내용은 실제 사건 검체를 다루며 적어 둔 관찰입니다.

## 조사 질문

- 조사 기간에 어느 사용자가 어느 브라우저로 웹메일·웹하드 페이지를 열었습니까?
- 그 시간대에 브라우저가 밖으로 보낸 양은 얼마입니까?
- 올린 파일이 무엇인지 PC 기록으로 좁힐 수 있습니까?

## ATT&CK 에서 보는 이 경로

MITRE ATT&CK 은 이 경로를 웹 서비스로 빼내기 (T1567 Exfiltration Over Web Service) 로 나눕니다[1]. 하위 기법은 네 가지입니다[1].

| 하위 기법 | 이름 |
|---|---|
| T1567.001 | Code Repository |
| T1567.002 | Cloud Storage |
| T1567.003 | Text Storage Sites |
| T1567.004 | Webhook |

(표는 [1])

## 먼저 확인할 것

| 확인할 것 | 까닭 |
|---|---|
| 사용한 브라우저 | 브라우저마다 방문 기록을 두는 곳과 형식이 다릅니다. [설치 프로그램](../../../02-artifacts/system-account/uninstall.md) 과 사용자 프로필 안의 브라우저 폴더를 봅니다. |
| 사용자 SID | SRUM 은 사용자를 SID 로 적습니다[2]. SID 와 사용자 이름의 짝은 [사용자 프로필 목록](../../../02-artifacts/system-account/profilelist.md) 에서 찾습니다. |
| 시각 형식 | SRUM 의 시각은 OLE Automation 날짜 값입니다[2]. 브라우저 방문 기록과 형식이 다르므로 하나의 기준으로 바꿔 맞춥니다([시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)). |
| 수집 범위 | `C:\Windows\System32\sru\` 폴더를 통째로 확보합니다. 사용자 프로필의 브라우저 폴더와 사용자 하이브(NTUSER.DAT) 도 확보합니다. |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 브라우저 방문 기록 | 웹메일·웹하드 페이지를 연 시각 | [크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md), [파이어폭스](../../../02-artifacts/browsers/firefox/index.md), [인터넷 익스플로러·옛 엣지](../../../02-artifacts/browsers/ie-edgehtml/index.md) |
| 2 | SRUM 네트워크 사용량 | 브라우저가 그 시간대에 보낸 바이트 수 | [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) |
| 3 | 열기·저장 대화상자 기록 | 올릴 파일을 고른 흔적 (남는지는 아래 참고) | [열기·저장 대화상자 기록](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) |
| 4 | 바로가기 파일·점프리스트·최근 문서 | 올리기 전에 원본 파일을 연 흔적 | [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md), [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md), [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md) |
| 5 | Sysmon 로그 | Sysmon 을 설치해 둔 PC 에서만, 네트워크 쪽 기록 | [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) |

## 브라우저 방문 기록

방문 기록에서 웹메일·웹하드 주소를 찾아 페이지를 연 시각을 적습니다. 방문 기록은 페이지를 연 기록이지, 그 페이지에서 파일을 올렸다는 뜻이 아닙니다. 방문 기록 DB 에 업로드 자체를 적는 표가 있는지는 이 페이지를 쓰면서 확인하지 않았는데, 브라우저별 페이지에서 확인합니다.

방문 기록이 없다고 브라우저를 안 썼다고 단정하지 않습니다. 시크릿 모드로 썼을 수 있습니다([시크릿 모드로 무엇을 했나](../../activity/private-browsing.md)). SRUM 은 브라우저 안의 기록이 아니라 윈도 폴더에 있는 DB 라서, 방문 기록이 없어도 SRUM 은 따로 봅니다.

- 웹 사용 전체를 되짚는 순서는 [웹 사용 행위 재구성](../../activity/web-activity.md) 에서 다룹니다.

## SRUM 네트워크 사용량 읽기

시스템 자원 사용 모니터 (System Resource Usage Monitor, SRUM) 의 DB 에는 앱별·사용자별 네트워크 사용 기록이 있습니다[2]. DB 전체 구조는 [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) 에서 다룹니다. 여기서는 송신량을 뽑는 데 쓰는 부분만 봅니다.

### 위치와 표

DB 파일은 `C:\Windows\System32\sru\SRUDB.dat` 이고[2], 형식은 ESE 입니다. 여는 법은 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. 네트워크 데이터 사용량 표의 이름은 `{973F5D5C-1D90-4944-BE8E-24B94231A174}` 이며 앱별·사용자별 네트워크 사용을 적습니다[2].

- 같은 DB 의 앱 자원 사용량 표는 `{D10CA2FE-6FCF-4F6D-848E-B2E99266FA89}` 입니다[2]. 같은 시간대의 브라우저 행을 이 표에서도 찾아 함께 봅니다.

### 네트워크 데이터 사용량 표의 칸

표의 칸은 AutoIncId, TimeStamp, AppId, UserId, InterfaceLuid, L2ProfileId, L2ProfileFlags, BytesSent, BytesRecvd 입니다[2]. 송신량을 뽑을 때 쓰는 칸은 아래와 같습니다.

| 칸 | 읽는 법 |
|---|---|
| TimeStamp | OLE Automation 날짜(부동소수점) 값입니다[2]. |
| AppId | SruDbIdMapTable 의 IdIndex 를 가리킵니다[2]. |
| UserId | SruDbIdMapTable 의 IdIndex 를 가리킵니다[2]. |
| BytesSent | 앱이 보낸 바이트 수입니다. |
| BytesRecvd | 앱이 받은 바이트 수입니다. |

### 앱과 사용자 찾기 (SruDbIdMapTable)

AppId·UserId 값과 IdIndex 가 같은 행을 SruDbIdMapTable 에서 찾으면 그 행의 IdBlob 칸에 실제 값이 있고[2], IdBlob 을 읽는 법은 IdType 칸에 따라 다릅니다[2].

| IdType | IdBlob 에 든 값 |
|---|---|
| 0~2 | UTF-16 문자열 |
| 3 | 사용자 SID |

(표는 [2])

- 문자열은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 을, SID 는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 을 따라 읽습니다.
- AppId 로 찾은 문자열에서 브라우저를 가리키는 항목을 고릅니다. 그 AppId 의 행만 네트워크 데이터 사용량 표에서 뽑습니다.

### 이 표가 말해 주는 것과 못 하는 것

**말해 주는 것.**

- 어느 앱이 어느 사용자로 기록 시각 무렵에 몇 바이트를 보내고 받았는지 알려 줍니다.

**말해 주지 못하는 것.**

- 어느 사이트로 보냈는지는 알 수 없습니다. 표에 주소 칸이 없습니다[2].
- 어떤 파일을 보냈는지는 알 수 없습니다. 표에 파일 칸이 없습니다[2].
- 송신량은 앱 단위 합계이며, 그 가운데 파일 하나를 보낸 양을 가려낼 칸이 없습니다.
- SRUM 이 얼마 간격으로 모아 적는지, 언제 DB 에 쓰는지는 이 페이지를 쓰면서 확인하지 않았는데, [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) 에서 확인합니다. 그 전까지 TimeStamp 를 송신이 일어난 정확한 순간으로 읽지 않습니다.

### 손상된 SRUDB.dat 다루기

압수한 이미지에서 꺼낸 ESE DB 는 대부분 비정상 종료 상태였고, 이런 DB 는 로그로 복구해야 하지만 로그 사슬이 끊겨 있으면 복구가 안 될 수 있습니다(현장 관찰). 복구는 늘 사본에서 하고 원본 SRUDB.dat 는 열지 않습니다.

손상된 SRUDB.dat 는 읽는 방식에 따라 행 수가 달랐습니다(현장 관찰). 같은 앱 사용량 표가 한 방식에서는 1,612 행, 다른 방식에서는 1,742 행이었습니다(현장 관찰). 그래서 두 가지 이상 방식으로 열어 행 수를 비교합니다. 보고서에는 어떤 방식으로 읽었는지 적습니다([도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)).

## 올린 파일 좁히기

브라우저에 파일을 올릴 때는 파일을 고르는 창을 쓰거나 파일을 끌어 놓습니다. 파일을 고르는 창에서 고른 파일이 열기·저장 대화상자 기록에 남는지는 이 페이지를 쓰면서 확인하지 않았는데, [열기·저장 대화상자 기록](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) 에서 확인합니다. 올리기 전에 원본 파일을 연 흔적은 바로가기 파일·점프리스트·최근 문서에서 찾습니다.

- 파일 하나를 중심으로 연 기록을 모으는 순서는 [이 파일을 누가 언제 열었나](../../activity/file-access.md) 에서 다룹니다.
- 올리기 전에 여러 파일을 모으거나 압축했는지는 [퇴사 전 자료를 모으고 압축했나 (Staging)](staging.md) 를 따릅니다.

## 분석 흐름

1. 사용자마다 쓴 브라우저를 정리하고, SID 와 사용자 이름을 짝짓습니다.
2. 방문 기록에서 조사 기간의 웹메일·웹하드 주소를 뽑아 페이지를 연 시각을 적습니다.
3. sru 폴더 사본에서 SRUDB.dat 를 엽니다. 비정상 종료 상태면 복구하고, 두 가지 이상 방식으로 읽어 행 수를 비교합니다.
4. SruDbIdMapTable 로 AppId 는 앱 문자열로, UserId 는 SID 로 바꿉니다.
5. 네트워크 데이터 사용량 표에서 그 사용자·브라우저의 행을 뽑아 BytesSent 를 시각순으로 정리합니다.
6. 같은 사용자의 다른 날과 견줘 송신량이 유난히 큰 시간대를 찾습니다. 그 시간대를 2 의 방문 시각과 맞춰 봅니다.
7. 그 시간대 앞뒤로 원본 파일을 연 흔적과 열기·저장 대화상자 기록을 찾습니다.
8. 의심하는 파일의 크기와 그 시간대 송신량을 나란히 적습니다. 송신량은 앱 단위 합계이므로, 크기가 비슷하다는 것만으로 그 파일을 보냈다고 쓰지 않습니다.
9. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **방문 기록을 업로드 증거로 씁니다.** 방문 기록은 페이지를 연 기록입니다. 올렸는지는 다른 기록과 맞춰서만 말합니다.
2. **SRUM 송신량을 특정 사이트나 파일로 보낸 양으로 씁니다.** 표에 주소 칸과 파일 칸이 없습니다[2]. 송신량은 그 앱이 그 시간대에 보낸 양일 뿐입니다.
3. **TimeStamp 를 송신한 순간으로 읽습니다.** 기록 간격을 확인하기 전에는 "기록 시각 무렵" 으로만 씁니다.
4. **도구 한 가지의 결과만 믿습니다.** 손상된 SRUDB.dat 는 읽는 방식에 따라 행 수가 달랐습니다(현장 관찰).
5. **방문 기록이 없으니 올리지 않았다고 봅니다.** 시크릿 모드, 다른 브라우저, 기록 지우기를 생각합니다. 지운 흔적은 [증거를 없애려 했나](../../activity/anti-forensics/index.md) 에서 봅니다.
6. **원본 SRUDB.dat 를 바로 엽니다.** 복구 과정에서 파일이 바뀔 수 있습니다. 사본에서 작업합니다.

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 웹하드에 설계 도면을 올렸습니다."
- 쓸 문장: "사용자 ○○ 의 크롬 방문 기록에 ○○(UTC) 에 웹하드 ○○ 의 페이지를 연 기록이 있습니다. SRUDB.dat 네트워크 데이터 사용량 표에는 TimeStamp 가 ○○ 인 행에 이 사용자의 크롬이 ○○ 바이트를 보냈다고 적혀 있습니다. 이 표에는 목적지 주소 칸과 파일 이름 칸이 없습니다. 이 기록은 그 시간대 무렵 크롬이 이만큼 송신했음을 보여 줍니다. 어느 사이트로 어떤 파일을 보냈는지는 이 기록만으로 정할 수 없습니다."

## 함께 볼 페이지

- [SRUM](../../../02-artifacts/execution/system-resource-usage-monitor/index.md) — 표 구조, 기록 간격, 해석할 때의 함정입니다.
- [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md) — SRUDB.dat 를 열고 복구하는 법입니다.
- [크롬 계열 브라우저](../../../02-artifacts/browsers/chrome-edge-whale/index.md) · [파이어폭스](../../../02-artifacts/browsers/firefox/index.md) · [인터넷 익스플로러·옛 엣지](../../../02-artifacts/browsers/ie-edgehtml/index.md) — 브라우저별 방문 기록입니다.
- [웹 사용 행위 재구성](../../activity/web-activity.md) · [시크릿 모드로 무엇을 했나](../../activity/private-browsing.md) — 웹 사용 전체를 되짚는 순서입니다.
- [열기·저장 대화상자 기록](../../../02-artifacts/file-folder-usage/comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) · [바로가기 파일](../../../02-artifacts/file-folder-usage/lnk.md) · [점프리스트](../../../02-artifacts/file-folder-usage/jump-lists.md) · [최근 문서](../../../02-artifacts/file-folder-usage/recentdocs.md) — 올린 파일을 좁히는 기록입니다.
- [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) · [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) · [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) — SRUM 값을 바꾸는 법입니다.
- [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) — 손상된 DB 를 여러 방식으로 읽어 비교합니다.
- [클라우드로 밖에 보냈나 (Cloud)](cloud.md) · [메일로 밖에 보냈나 (Email)](email.md) · [메신저로 파일을 보냈나 (Messenger)](messenger.md) — 앱으로 보낸 경우입니다.

## 참고 문헌

1. MITRE ATT&CK, "Exfiltration" (TA0010) — https://attack.mitre.org/tactics/TA0010/
2. libyal esedb-kb, "System Resource Usage Monitor (SRUM)" — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
