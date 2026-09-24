---
title: "네트워크 사용량"
parent: "SRUM"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1000
---

# 네트워크 사용량 (Network Data Usage)

> 상위 허브: [SRUM (System Resource Usage Monitor)](index.md)

## 한 줄 요약

SRUDB.dat 의 네트워크 사용량 표는 앱·계정·네트워크 인터페이스별로 보낸 바이트와 받은 바이트를 적습니다. 한 행은 DB 에 쓰기 전 한 시간 안팎 동안 쌓인 양이고, 이 표에는 목적지 주소와 파일 이름이 없어서 이 표로는 "어느 시간대에 어떤 앱이 얼마나 주고받았나" 까지만 말할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

SRUM 은 확장 (Extension) 마다 DLL 을 불러 값을 모읍니다. 이 표는 `nduprov.dll` 확장이 채웁니다. 확장과 표의 짝은 [구조와 ID 매핑](srudbidmaptable.md)에 정리돼 있습니다.

WithSecure 조사팀은 2023년 SANS DFIR Summit Europe 에서 이 확장을 분석해 발표했습니다. 이 페이지와 관련 있는 내용은 `Ndu.sys` 드라이버가 Windows 필터링 플랫폼 (Windows Filtering Platform, WFP) 위에서 프로세스마다 오간 양을 세고, 조사팀이 시험한 범위에서는 세지 않고 빠지는 프로세스가 없었다는 점입니다. 바이트 수에는 2계층 (데이터 링크 계층) 프레임 크기가 들어가며, VPN 을 거친 통신은 VPN 프로세스나 서비스의 몫으로 잡혔습니다.

SRUM 은 모은 값을 메모리에 쌓아 두었다가 기본 1시간마다 SRUDB.dat 로 옮깁니다. 이 흐름과 거기서 생기는 함정은 [SRUM 해석 함정](1.md)에서 다룹니다. 이 페이지는 네트워크 사용량 표에만 해당하는 내용을 다룹니다.

## 위치와 버전별 차이

| 항목 | 값 |
|---|---|
| 파일 | `%SystemRoot%\System32\sru\SRUDB.dat` |
| 표 이름 | `{973F5D5C-1D90-4944-BE8E-24B94231A174}` |
| 확장 등록 키 | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SRUM\Extensions\{973F5D5C-1D90-4944-BE8E-24B94231A174}` |
| 확장 DLL | 등록 키의 `DllName` 값. `C:\WINDOWS\System32\nduprov.dll` 이었습니다 (확인 범위: Windows 11 25H2 한 대) |

| Windows | 이 표 | 근거 |
|---|---|---|
| 8 · 8.1 | SRUM DB 가 있습니다. 이 표의 열 구성은 이 글에서 확인하지 못했습니다 | WithSecure |
| 10 · 11 | 있습니다. 두 버전의 열 9개가 같았습니다 | libyal 명세, 공개 표본 |
| Server 2019 · 2022 | 없습니다. SRUM DB 가 있는 빌드에서도 이 표는 없었습니다 | WithSecure 시험 |

- 이 글의 "공개 표본" 은 Andrew Rathbun 의 GIAC 골드 페이퍼 연구 저장소에 올라 있는 SRUDB.dat 두 개입니다. 2022년에 만든 Windows 10·11 가상 머신에서 나왔습니다.
- 보관 기간은 기본 60일입니다 (WithSecure). 확장 키에 `Tier2MaxEntries` 값을 따로 두면 기간이 달라집니다. 위 Windows 11 PC 의 이 확장 키에는 이 값이 없었습니다 (관찰). 계산식은 [앱별 자원 사용](application-resource-usage.md)에 있습니다.

## 구조

ESE 표 하나입니다. 레코드를 찾아가는 법은 [파일 구조 (Page·B+Tree·Catalog)](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)에서 다룹니다. 열은 libyal 명세와 공개 표본의 카탈로그가 같았습니다. 모두 고정 길이 열입니다.

| 열 ID | 이름 | 형식 (카탈로그 번호) | 크기 | 뜻 |
|---|---|---|---|---|
| 1 | AutoIncId | 32비트 정수 (4) | 4 | 행 번호 |
| 2 | TimeStamp | DateTime (8) | 8 | 이 행을 DB 에 쓴 시각 |
| 3 | AppId | 32비트 정수 (4) | 4 | 앱 번호. SruDbIdMapTable 에서 풉니다 |
| 4 | UserId | 32비트 정수 (4) | 4 | 계정 번호. SruDbIdMapTable 에서 SID 로 풉니다 |
| 5 | InterfaceLuid | 64비트 정수 (15) | 8 | 네트워크 인터페이스 식별자 |
| 6 | L2ProfileId | 32비트 정수 (4) | 4 | 2계층 프로필 번호. 무선이면 Wi-Fi 프로필 번호 |
| 7 | L2ProfileFlags | 32비트 정수 (4) | 4 | 명세에 뜻이 없습니다 |
| 8 | BytesSent | 64비트 정수 (15) | 8 | 보낸 바이트 |
| 9 | BytesRecvd | 64비트 정수 (15) | 8 | 받은 바이트 |

AppId·UserId 를 푸는 법은 [구조와 ID 매핑](srudbidmaptable.md)을 봅니다.

### 인터페이스 풀기 (InterfaceLuid)

InterfaceLuid 는 Windows 의 NET_LUID 값입니다. 위 16비트가 인터페이스 유형 (IfType) 입니다. 비트 배치와 흔한 유형 번호는 [네트워크 연결 기록](network-connectivity.md)에 표로 있습니다. 그 표에 없는 모바일 광대역은 243 (GSM 계열) 과 244 (CDMA 계열) 입니다 (Microsoft Learn).

유형만으로는 어느 어댑터인지 모릅니다. 가운데 24비트인 NetLuidIndex 로 어댑터를 좁힐 수 있습니다.

- SYSTEM 하이브의 `ControlSet00X\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\NNNN` 키에 `NetLuidIndex` 값과 `*IfType` 값이 있었습니다 (확인 범위: Windows 11 25H2 한 대).
- 같은 NetLuidIndex 가 유형이 다른 어댑터에도 쓰였습니다. 그래서 NetLuidIndex 와 IfType 을 함께 맞춥니다.
- 같은 키의 `NetCfgInstanceId` 가 인터페이스 GUID 입니다. 이 GUID 로 [네트워크 인터페이스 설정](../../network/tcp-ip-interfaces.md)의 IP 설정과 이어 봅니다.
- ControlSet 번호는 [컨트롤셋 고르기](../../../01-foundations/database-log-formats/registry-hive/controlset-select.md)로 정합니다.

공개 표본의 이더넷 행은 InterfaceLuid 가 `0x0006008001000000` 이었습니다. 위 16비트 6 은 이더넷입니다. 가운데 24비트 `0x008001` 은 NetLuidIndex 32769 입니다.

### Wi-Fi 프로필 풀기 (L2ProfileId)

무선 행의 L2ProfileId 는 SOFTWARE 하이브 `Microsoft\WlanSvc\Interfaces\{인터페이스 GUID}\Profiles\{프로필 GUID}` 키의 `ProfileIndex` 와 맞춥니다. 공개 도구 srum-dump 가 이 방법을 씁니다. 순서와 이름 읽는 법은 [네트워크 연결 기록](network-connectivity.md)에 있습니다.

- 프로필 GUID 는 `C:\ProgramData\Microsoft\Wlansvc\Profiles\Interfaces\{인터페이스 GUID}\` 아래 Wi-Fi 프로필 XML 의 파일 이름과 같았습니다 (확인 범위: Windows 11 25H2 한 대). SSID 와 보안 설정은 [Wi-Fi 프로필](../../network/wlan-profiles.md)에서 읽습니다.
- 공개 표본의 이더넷 행은 L2ProfileId 와 L2ProfileFlags 가 모두 0 이었습니다. 유선 행은 이 방법으로 네트워크 이름을 풀 수 없습니다. 유선 네트워크는 [네트워크 목록](../../network/networklist.md)과 시각을 맞춰 좁힙니다.

### 한 번 기록할 때 생기는 행

공개 표본에서 본 모양입니다. 두 파일 모두 이 표에 기록이 한 번씩만 있었습니다. 그래서 여러 번 기록한 DB 에서도 같은지는 검체에서 확인합니다.

- 한 번에 들어간 행(22행, 23행)은 TimeStamp 가 모두 같았습니다. 같은 파일의 앱별 자원 사용 표와 네트워크 연결 표의 TimeStamp 도 같은 값이었습니다.
- 같은 AppId 가 UserId 만 다른 여러 행으로 나왔습니다. 앱 하나가 그 구간에 주고받은 양은 같은 TimeStamp 의 행을 앱별로 더해서 구합니다.
- 서비스는 `BITS`, `DoSvc`, `wuauserv` 처럼 서비스 이름으로 나왔습니다. 일반 프로그램은 `\device\harddiskvolume3\…` 꼴의 경로로 나왔습니다.
- AppId 와 UserId 가 모두 이름 칸이 빈 매핑을 가리키는 행이 한 묶음에 하나 있었습니다. 이 행의 받은 바이트가 묶음에서 가장 컸습니다. 이 행이 무엇을 뜻하는지는 명세에 없습니다. 앱별 순위를 낼 때 이 행은 따로 표시합니다.
- InterfaceLuid 가 0 이고 보낸·받은 바이트가 모두 0 인 행도 있었습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 기록 시각 앞 구간에 이 앱(또는 서비스)이 이만큼 보내고 받은 기록이 있습니다 | 어디로 보냈는지. 이 표에는 IP·도메인·포트 칸이 없습니다 |
| 그 양이 어느 계정으로 돈 프로세스의 몫으로 잡혔는지 | 키보드 앞에 누가 있었는지. 서비스는 서비스 계정으로 나옵니다 |
| 이 앱이 그 구간에 이 PC 에서 돌며 통신했습니다 | 어떤 파일을 보냈는지. 파일 이름과 내용은 없습니다 |
| 어떤 유형의 인터페이스를 거쳤는지. 무선이면 어느 프로필인지 (풀 수 있을 때) | 구간 안에서 통신을 시작하고 끝낸 시각 |
| 평소보다 송신이 많은 시간대가 있었는지 | 인터넷으로 나갔는지, 같은 망 안의 장치로 갔는지 |
| | 보낸 파일의 정확한 크기 |

WithSecure 조사팀은 77,989,497바이트 파일을 보내 보았습니다. SRUM 에는 79,414,089바이트가 남았습니다. 파일보다 약 1.8% 컸습니다. 이 비율은 한 번 시험한 결과입니다. 다른 사건에 그대로 옮겨 쓰지 않습니다. "보낸 양이 파일 크기와 비슷하거나 조금 크다" 까지만 씁니다.

### 보고서 문장

아래 경로와 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "SRUDB.dat 네트워크 사용량 표에 TimeStamp 2025-03-14 02:00:00 UTC 인 행이 있습니다. 이 행에는 `\device\harddiskvolume3\…\uploader.exe` 가 SID `S-1-5-21-…-1001` 의 몫으로 무선 인터페이스(IfType 71)를 거쳐 734,003,200바이트를 보낸 것으로 적혀 있습니다. 이 양은 이 기록 시각 앞 구간의 합계입니다."
- 쓰면 안 되는 문장: "사용자가 02:00 에 기밀 파일 700MB 를 외부 서버로 유출했습니다."

## 시각 해석

이 표의 시각 열은 TimeStamp 하나입니다.

- 형식은 OLE 자동화 날짜 (OLE Automation Date) 입니다. 1899-12-30 00:00 부터 센 날 수를 8바이트 실수로 적습니다. 변환은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다.
- 기준은 UTC 입니다. 근거와 검증 사례는 [네트워크 연결 기록](network-connectivity.md)에 있습니다. 현지 시각으로 바꿀 때는 [시간대 설정](../../system-account/time-zone.md)을 씁니다.
- TimeStamp 는 통신한 시각이 아니라 DB 에 쓴 시각입니다. 한 행이 덮는 구간을 어떻게 추정하는지는 [SRUM 해석 함정](1.md)에서 다룹니다.

이 표에만 해당하는 점은 다음과 같습니다.

- 한 행의 바이트 수는 그 구간의 양입니다. 켠 뒤로 쌓인 누적값이 아닙니다. 여러 시간의 총량은 여러 행을 더해서 구합니다.
- 긴 전송이 기록 시각을 넘기면 둘 이상의 묶음에 나뉘어 적힙니다. 그래서 전송 하나를 찾을 때는 이어지는 TimeStamp 의 행을 함께 봅니다.
- 한 구간의 송신량을 구간 길이로 나누면 평균 속도가 나옵니다. 실제 전송은 구간 일부에서만 일어났을 수 있어서 실제 속도는 이 값보다 빨랐을 수 있습니다. 회선 속도로 불가능한 양인지 가늠할 때만 씁니다.

## 함정과 한계

1. **한 행을 앱의 총량으로 봅니다.** 같은 TimeStamp 안에 계정이나 인터페이스가 다른 행이 더 있을 수 있습니다. 앱별로 더한 뒤 비교합니다.
2. **보낸 양과 받은 양을 합쳐서 봅니다.** 반출을 볼 때는 BytesSent 를 따로 봅니다. 공개 도구 가운데에는 두 값을 더한 열을 따로 만들어 주는 것도 있습니다.
3. **큰 송신량을 곧바로 반출로 봅니다.** 공개 표본에서도 `BITS`·`DoSvc`·`wuauserv` 같은 업데이트 관련 서비스가 행을 남겼습니다. 먼저 어떤 앱·서비스의 몫인지 가립니다.
4. **브라우저·동기화 앱의 행에서 사이트를 찾습니다.** 한 앱이 여러 사이트와 주고받은 양이 한 행에 합쳐집니다. 어느 사이트였는지는 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md)에서 찾습니다.
5. **VPN 을 켠 PC 에서 앱별 송신량을 그대로 믿습니다.** VPN 을 거친 양은 VPN 프로세스나 서비스 몫으로 잡힙니다 (WithSecure). 조사팀도 이 부분은 더 연구할 거리로 남겼습니다. [VPN 연결 기록](../../network/vpn-connections.md)과 함께 봅니다.
6. **L2ProfileId 이름이 비었다고 연결이 없었다고 봅니다.** 프로필을 지웠거나, SOFTWARE 하이브와 SRUDB.dat 의 시점이 다를 수 있습니다. 옛 하이브는 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 찾습니다.
7. **DB 를 한 가지 방식으로만 엽니다.** 압수 이미지의 SRUDB.dat 는 대부분 비정상 종료 상태였고, 손상된 DB 는 읽는 방식에 따라 행 수가 달랐습니다 (현장 관찰). 읽는 순서는 [SRUM 해석 함정](1.md)을 따릅니다.
8. **수집 직전 구간을 놓칩니다.** 마지막 TimeStamp 뒤의 사용량은 아직 DB 에 없을 수 있습니다. 켜져 있는 PC 라면 [네트워크 상태 수집](../../../03-techniques/process-acquisition/live-response/connections-dns-arp-routes.md)으로 지금 연결을 따로 남깁니다.
9. **보관 기간이 지난 행을 "없었다" 로 봅니다.** 기본 60일이 지난 행은 지워집니다. 지운 행이 파일 안에 남는지는 [파일 안에 남은 지운 레코드](../../../01-foundations/database-log-formats/extensible-storage-engine/deleted-records.md)에서 봅니다. 옛 SRUDB.dat 는 섀도 복사본에서 꺼냅니다.

### 지우기와 조작

- 서비스를 끄거나 SRUDB.dat 를 바꿔치기한 흔적을 찾는 법은 [SRUM 해석 함정](1.md)의 "끄기·지우기가 남기는 흔적" 에서 다룹니다.
- 행 값을 고쳤는지는 파일 하나만 봐서는 가리기 어렵습니다. 아래를 맞춰 봅니다.
  - AutoIncId 가 중간에 비는지 봅니다. 빈 번호가 있으면 까닭을 따로 확인합니다.
  - 같은 TimeStamp 의 [네트워크 연결 기록](network-connectivity.md)에 같은 인터페이스·프로필의 연결이 있는지 봅니다. 연결 기록이 없는 인터페이스로 큰 양이 오갔다면 이상합니다.
  - 그 시간대에 앱이 실행된 다른 흔적이 있는지 봅니다 (아래 교차 검증).

## 직접 분석해 보기

### 헥스로 한 번

아래는 libyal 명세와 Microsoft 문서로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. 오프셋은 레코드 머리의 첫 바이트를 0 으로 센 값입니다. 페이지에서 레코드를 찾는 법은 [파일 구조](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)를 봅니다. `??` 는 설명에 쓰지 않는 바이트입니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    09 7F 3A 00 2C 01 00 00 AB AA AA AA 42 54 E6 40
0x10    45 02 00 00 0D 00 00 00 00 00 00 00 80 00 47 00
0x20    03 00 00 10 00 00 00 00 00 00 C0 2B 00 00 00 00
0x30    00 00 50 00 00 00 00 00 ?? ??
```

1. 앞 4바이트가 레코드 머리입니다. 마지막 고정 열 ID 는 `09` 입니다. 이 표의 열 9개가 모두 고정 열이므로 맞습니다.
2. 마지막 가변 열 ID 는 `7F` (127) 입니다. 가변 열 ID 는 128 부터이므로 가변 열이 없다는 뜻입니다.
3. `3A 00` 은 가변 열 영역이 0x3A (58) 에서 시작한다는 뜻입니다. 고정 열은 4 + 52 = 56 (0x38) 에서 끝납니다. 사이의 2바이트는 명세가 뜻을 밝히지 않은 칸입니다.
4. 공개 표본의 이 표 레코드도 머리가 `09 7F 3A 00` 이었습니다.
5. 고정 열을 ID 순서대로 읽습니다. 모두 리틀 엔디언입니다.

| 오프셋 | 열 | 바이트 | 값 |
|---|---|---|---|
| 0x04 | AutoIncId | `2C 01 00 00` | 300 |
| 0x08 | TimeStamp | `AB AA AA AA 42 54 E6 40` | 실수 45730.08333… |
| 0x10 | AppId | `45 02 00 00` | 581 |
| 0x14 | UserId | `0D 00 00 00` | 13 |
| 0x18 | InterfaceLuid | `00 00 00 00 80 00 47 00` | 0x0047008000000000 |
| 0x20 | L2ProfileId | `03 00 00 10` | 0x10000003 (268435459) |
| 0x24 | L2ProfileFlags | `00 00 00 00` | 0 |
| 0x28 | BytesSent | `00 00 C0 2B 00 00 00 00` | 0x2BC00000 = 734,003,200 |
| 0x30 | BytesRecvd | `00 00 50 00 00 00 00 00` | 0x500000 = 5,242,880 |

6. TimeStamp 의 정수 부분 45730 은 1899-12-30 부터 45,730일 뒤인 2025-03-14 입니다. 소수 부분 0.08333… 에 24 를 곱하면 2시간입니다. 그래서 2025-03-14 02:00:00 UTC 이고, 한국 시각으로는 같은 날 11:00:00 입니다.
7. InterfaceLuid 의 위 16비트는 0x0047 (71) 입니다. 무선(IEEE 802.11) 인터페이스입니다. 가운데 24비트 0x008000 은 NetLuidIndex 32768 입니다.
8. L2ProfileId 268435459 는 SOFTWARE 하이브에서 `ProfileIndex` 가 같은 Wi-Fi 프로필을 찾아 이름을 읽습니다.
9. BytesSent 는 700 MiB, BytesRecvd 는 5 MiB 입니다. 이 구간에는 보낸 양이 받은 양보다 훨씬 많았습니다.
10. AppId 581 과 UserId 13 은 SruDbIdMapTable 에서 앱 경로와 SID 로 풉니다.

> 그림 자리: 위 레코드의 바이트를 머리(4바이트)·고정 열 9개(52바이트)·뜻 모를 2바이트로 색을 나누고, InterfaceLuid 8바이트를 IfType·NetLuidIndex·예약 칸으로 쪼개 보여 주는 그림

### 공개 도구로 한 번

srum-dump, SrumECmd, dissect.target 의 SRUM 플러그인, libesedb 의 `esedbexport` 가 이 표를 읽습니다. 도구는 예로만 듭니다. 결과를 볼 때 다음을 확인합니다.

- TimeStamp 를 UTC 로 보여 주는지, 분석 PC 의 현지 시각으로 바꿔 보여 주는지 확인합니다. srum-dump 는 이 열에 "SRUM Entry Creation (UTC)" 라는 이름을 붙입니다.
- InterfaceLuid 를 유형 이름으로 바꿀 때 위 16비트를 쓰는지 확인합니다. srum-dump 는 위 16비트를 씁니다.
- L2ProfileId 가 이름으로 바뀌지 않고 숫자로 남은 행이 있는지 셉니다. srum-dump 는 SOFTWARE 하이브를 함께 줄 때만 이름을 풉니다.
- 두 도구로 같은 사본을 열어 이 표의 행 수와 TimeStamp 범위를 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.
- 한두 행은 위 헥스 절차로 직접 풀어 도구 값과 비교합니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [네트워크 연결 기록](network-connectivity.md) | 같은 인터페이스·프로필이 그 시간대에 연결돼 있었는지 |
| [앱별 자원 사용](application-resource-usage.md) | 같은 구간에 그 앱이 디스크에서 읽은 양. 보낸 양과 크기가 비슷한지 |
| [Wi-Fi 프로필](../../network/wlan-profiles.md) · [네트워크 목록](../../network/networklist.md) | 프로필의 SSID, 네트워크별 처음·마지막 연결 |
| [네트워크 연결 이벤트](../../event-logs/wlan-autoconfig-networkprofile.md) | 연결·해제 시각을 초 단위로 |
| [윈도 방화벽](../../network/windows-firewall-pfirewall-log.md) · [Sysmon 이벤트 3·22](../../event-logs/sysmon/3-22.md) | 목적지 IP·포트·도메인. 로그를 켜 두었을 때만 남습니다 |
| [VPN 연결 기록](../../network/vpn-connections.md) | 송신량이 VPN 프로세스로 몰린 시간대 |
| [프리페치](../prefetch/index.md) · [AmCache](../amcache-hve/index.md) | 앱의 실행 시각과 실행 파일 정보 |
| [켜짐·꺼짐](../../event-logs/power-on-off-events.md) | 한 행이 덮는 구간에 PC 가 켜져 있던 시간 |

무엇을 어디로 보냈는지는 이 표 밖에서 찾습니다. 흐름은 [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md), [클라우드로 밖에 보냈나](../../../04-scenarios/exfiltration/data-exfiltration/cloud.md), [웹메일·웹하드로 올렸나](../../../04-scenarios/exfiltration/data-exfiltration/web-upload.md)를 봅니다.

## 실습

**공개 표본** 은 GitHub 의 `AndrewRathbun/SANSGoldPaperResearch_FOR500_Rathbun` 저장소 `SRUM` 폴더에 있습니다. Windows 10 과 Windows 11 의 SRUDB.dat 를 사본으로 받아 풀어 봅니다.

1. 두 파일에서 네트워크 사용량 표의 행 수와 서로 다른 TimeStamp 개수를 세어 봅니다. 같은 파일의 앱별 자원 사용 표와 TimeStamp 를 비교합니다.
2. 행 하나를 헥스 편집기로 찾아 레코드 머리와 BytesSent 를 직접 읽어 봅니다.
3. InterfaceLuid 를 IfType 과 NetLuidIndex 로 나눠 봅니다. 어떤 유형의 인터페이스입니까?
4. 받은 바이트가 가장 큰 행의 AppId 를 SruDbIdMapTable 에서 찾아봅니다. 이름이 나옵니까?
5. 한 묶음에서 두 번 이상 나오는 AppId 를 찾고, 행마다 UserId 를 SID 로 풀어 봅니다.

**직접 만든 Windows 10·11 가상 머신** 에서도 해 봅니다.

1. 크기를 아는 파일을 웹 저장소에 올리고 시각을 적어 둡니다.
2. 한 시간 넘게 기다리거나 정상 종료한 뒤 SRUDB.dat 를 꺼냅니다.
3. 브라우저 행의 BytesSent 가 파일 크기보다 몇 퍼센트 큰지 재 봅니다.
4. 올리는 도중에 기록 시각이 지나도록 큰 파일로 다시 해 봅니다. 송신량이 몇 개 묶음으로 나뉘는지 봅니다.
5. VPN 을 켜고 1번을 되풀이합니다. 송신량이 어느 앱 몫으로 잡히는지 봅니다.

## 참고 문헌

- libyal, "System Resource Usage Monitor (SRUM)", esedb-kb — https://github.com/libyal/esedb-kb/blob/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
- Microsoft Learn, "NET_LUID_LH union (ifdef.h)" — https://learn.microsoft.com/en-us/windows/win32/api/ifdef/ns-ifdef-net_luid_lh
- Microsoft Learn, "MIB_IF_ROW2 structure (netioapi.h)" — https://learn.microsoft.com/en-us/windows/win32/api/netioapi/ns-netioapi-mib_if_row2
- Catarina de Faria Cristas·Lucas Echard·Diego Fuschini (WithSecure), "Exploring the depths of SRUM for incident response", SANS DFIR Summit Europe 2023 발표 자료 — https://github.com/ReversecLabs/slide-decks/blob/main/2023-SANS_DFIR_Summit_Europe/Exploring_the_depths_of_SRUM_for_incident_response.pdf
- Mark Baggett, srum-dump 소스 코드 (`srum-dump/helpers.py`, `srum-dump/srum_dump.py`) — https://github.com/MarkBaggett/srum-dump
- Andrew Rathbun, SANSGoldPaperResearch_FOR500_Rathbun (Windows 10·11 SRUM 표본) — https://github.com/AndrewRathbun/SANSGoldPaperResearch_FOR500_Rathbun
