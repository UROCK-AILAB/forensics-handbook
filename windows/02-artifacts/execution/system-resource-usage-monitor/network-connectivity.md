---
title: "네트워크 연결 기록"
parent: "SRUM"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1010
---

# 네트워크 연결 기록 (Network Connectivity)

SRUM 의 네트워크 연결 표는 이 PC 의 네트워크 인터페이스가 어떤 네트워크에 언제 연결되어 얼마나 붙어 있었는지를 적습니다. 행마다 연결 시작 시각과 연결된 시간(초)이 있습니다. 무선이면 프로필 번호를 SOFTWARE 하이브와 맞춰 네트워크 이름(SSID)까지 알아낼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

SRUM 은 확장 모듈 여러 개가 각자 표를 채우는 구조입니다. 네트워크 연결 표는 "Windows Network Connectivity Usage Monitor" 모듈이 채웁니다. 표 이름은 GUID `{DD6636C4-8929-4683-974E-22C046A43763}` 입니다.

이 표는 연결 하나를 행 하나로 적지 않고, 연결이 이어지는 동안 SRUM 이 기록할 때마다 같은 연결의 행을 하나씩 더 만듭니다. 행마다 시작 시각은 같고 연결된 시간만 늘어납니다.

예를 들어 한 PC 의 이 표에는 1,472행이 있었고, 인터페이스·프로필 번호·시작 시각이 같은 행끼리 묶으면 연결은 108개였습니다. 가장 긴 연결 하나에는 행이 300개 넘게 쌓여 있었습니다.

> 그림 자리: 한 연결의 행 여러 개가 같은 ConnectStartTime 을 두고, 기록 시각(TimeStamp)마다 ConnectedTime 만 늘어나는 모습을 시간 축에 그린 그림

데이터를 얼마나 주고받았는지는 이 표에 없습니다. 그 내용은 [네트워크 사용량](network-data-usage.md) 표에 있습니다.

## 위치와 버전별 차이

| 항목 | 값 |
|---|---|
| 데이터베이스 | `C:\Windows\System32\sru\SRUDB.dat` (ESE 형식) |
| 표 이름 | `{DD6636C4-8929-4683-974E-22C046A43763}` |
| 모듈 등록 위치 | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SRUM\Extensions\{DD6636C4-8929-4683-974E-22C046A43763}` |
| 모듈 DLL | 등록 키의 `DllName` 값. 보통 `C:\WINDOWS\System32\ncuprov.dll` 입니다 |
| 무선 프로필 이름을 풀 곳 | SOFTWARE 하이브 `Microsoft\WlanSvc\Interfaces\{인터페이스 GUID}\Profiles\{프로필 GUID}` |

| Windows | 이 표 |
|---|---|
| 8·8.1 | 실제 파일에서 이 표와 열 구성을 확인합니다 |
| 10 | 아래 열 목록의 기준 버전입니다 |
| 11 | 10 과 같은 열 아홉 개가 있습니다 |

SRUM 전체의 보관 기간과 버전별 차이는 [SRUM 허브](index.md)를 봅니다. ESE 파일 구조는 [ESE 데이터베이스](../../../01-foundations/database-log-formats/extensible-storage-engine/index.md)를 봅니다.

## 구조

열은 다음과 같습니다.

| 열 | 형식 | 뜻 |
|---|---|---|
| AutoIncId | 32비트 정수 | 행 일련번호 |
| TimeStamp | 날짜 (OLE 자동화 날짜) | SRUM 이 이 행을 적은 시각 |
| AppId | 32비트 정수 | `SruDbIdMapTable` 의 번호 |
| UserId | 32비트 정수 | `SruDbIdMapTable` 의 번호 |
| InterfaceLuid | 64비트 정수 | 네트워크 인터페이스 식별자 |
| L2ProfileId | 32비트 정수 | 2계층 프로필 번호. 무선이면 Wi-Fi 프로필 번호 |
| ConnectedTime | 32비트 정수 | 연결된 시간 (초) |
| ConnectStartTime | 64비트 정수 (FILETIME) | 연결을 시작한 시각 |
| L2ProfileFlags | 32비트 정수 | 프로필 플래그 |

AppId·UserId 를 푸는 방법은 [구조와 ID 매핑](srudbidmaptable.md)을 봅니다. 이 표에서는 두 열이 쓸모없는 경우가 많습니다. 위 PC 에서는 1,472행 모두 AppId 가 1, UserId 가 2 였고, 매핑 표의 1번과 2번은 이름 열(`IdBlob`)이 비어 있었습니다.

L2ProfileFlags 의 뜻은 정해져 있지 않아 값만 옮깁니다. 위 PC 에서는 모든 행이 0 이었습니다.

### InterfaceLuid 풀기

InterfaceLuid 는 `NET_LUID` 구조입니다. 64비트 값을 세 필드로 나눕니다.

| 비트 | 필드 | 뜻 |
|---|---|---|
| 0~23 | Reserved | 예약 |
| 24~47 | NetLuidIndex | 인터페이스 LUID 번호 |
| 48~63 | IfType | 인터페이스 유형 (IANA 번호) |

그래서 값을 오른쪽으로 48비트 밀면 인터페이스 유형이 나옵니다. 흔한 유형은 다음과 같습니다.

| IfType | 이름 | 뜻 |
|---|---|---|
| 1 | IF_TYPE_OTHER | 그 밖의 인터페이스 |
| 6 | IF_TYPE_ETHERNET_CSMACD | 이더넷 (유선) |
| 23 | IF_TYPE_PPP | PPP |
| 24 | IF_TYPE_SOFTWARE_LOOPBACK | 소프트웨어 루프백 |
| 71 | IF_TYPE_IEEE80211 | IEEE 802.11 무선 |
| 131 | IF_TYPE_TUNNEL | 터널 |
| 144 | IF_TYPE_IEEE1394 | IEEE 1394 (파이어와이어) |

InterfaceLuid 에는 어댑터 이름이나 MAC 주소가 없습니다. 유형과 PC 안의 번호만 있습니다.

### L2ProfileId 를 네트워크 이름으로 바꾸기

표에는 네트워크 이름이 없습니다. 무선 연결이면 L2ProfileId 를 SOFTWARE 하이브의 Wi-Fi 프로필과 맞춥니다.

1. SOFTWARE 하이브의 `Microsoft\WlanSvc\Interfaces` 아래 인터페이스 GUID 키를 엽니다.
2. 그 아래 `Profiles\{프로필 GUID}` 키마다 `ProfileIndex` 값을 봅니다.
3. `ProfileIndex` 가 L2ProfileId 와 같은 프로필을 고릅니다.
4. 그 프로필의 `MetaData` 하위 키에서 네트워크 이름을 읽습니다.

이름은 `MetaData` 의 `Channel Hints` 나 `Band Channel Hints` 값에 있습니다. 앞 4바이트가 길이이고, 그 뒤 길이만큼이 이름입니다. srum-dump 도 이 순서로 이름을 찾습니다.

위 PC 에서는 표에 나온 L2ProfileId 네 개가 모두 `ProfileIndex` 와 맞았습니다. 프로필 열 개의 `ProfileIndex` 는 0x10000001(268435457)부터 1씩 늘어난 값이었습니다. `Band Channel Hints` 는 100바이트였고, 앞 4바이트 길이 뒤에 네트워크 이름이 있었습니다.

SSID 는 문자열이 아니라 바이트열입니다. 한글 이름이면 인코딩을 따져 봅니다. [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)을 봅니다. Wi-Fi 프로필 자체의 구조는 [Wi-Fi 프로필](../../network/wlan-profiles.md)을 봅니다.

## 증거로서 의미

**증명하는 것**

- 이 PC 의 어떤 유형 인터페이스가 어떤 L2 프로필로 연결을 시작한 시각(ConnectStartTime)
- 그 연결이 기록 시각까지, 또는 끊길 때까지 이어진 시간(ConnectedTime)
- 기록 시각(TimeStamp)에 이 PC 가 켜져 있었고 SRUM 이 동작했다는 것
- 무선이면, 프로필 번호로 찾은 SSID 의 네트워크에 연결했다는 것

**증명하지 못하는 것**

- 어느 프로그램이나 사용자가 네트워크를 썼는지. 이 표의 AppId·UserId 는 흔히 이 정보를 담지 않습니다.
- 데이터를 주고받았는지, 얼마나 주고받았는지. [네트워크 사용량](network-data-usage.md) 표를 함께 봅니다.
- 접속한 무선 AP 의 MAC 주소(BSSID), 받은 IP 주소, 물리적 위치
- 사람이 직접 연결했는지, 저장된 프로필로 자동 연결되었는지
- 같은 이름(SSID)의 다른 장소 네트워크인지. 이름이 같으면 한 프로필로 묶일 수 있습니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "SRUM 기록상 이 PC 의 무선(802.11) 인터페이스가 `<시각 UTC>` 에 프로필 번호 `<번호>` 로 연결을 시작했다. 이 번호는 SOFTWARE 하이브에서 SSID `<이름>` 의 프로필과 맞는다. 기록 시각 `<시각 UTC>` 에 이 연결은 `<초>` 초째 이어지고 있었다." 처럼 씁니다.

## 시각 해석

| 열 | 형식 | 뜻 | 기준 |
|---|---|---|---|
| TimeStamp | OLE 자동화 날짜 (8바이트 실수) | SRUM 이 이 행을 적은 시각 | UTC (아래 설명) |
| ConnectStartTime | FILETIME | 이 연결이 시작된 시각 | UTC |
| ConnectedTime | 초 | 시작부터 잰 연결 시간 | 시간 길이 |

두 날짜 형식을 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)을 봅니다.

**TimeStamp 도 UTC 입니다.** 위 PC 는 한국 표준시(UTC+9)를 썼고, 1,472행 중 1,355행에서 "TimeStamp − ConnectStartTime" 이 ConnectedTime 과 1초 안으로 같았습니다. TimeStamp 가 현지 시각이었다면 9시간이 어긋났을 것입니다.

**TimeStamp 는 분 단위로 적힐 수 있습니다.** 위 PC 에서는 모든 행의 초 자리가 0 이었습니다. ConnectStartTime 은 1초보다 작은 단위까지 적혀 있었습니다.

**연결이 끝난 시각은 계산으로 구합니다.** 끝난 시각은 "ConnectStartTime + ConnectedTime" 으로 추정합니다. srum-dump 도 이 식으로 "Calculated Stop Time" 열을 만듭니다. 한 연결의 마지막 행은 TimeStamp 가 이 계산값보다 늦을 수 있습니다. 위 PC 의 108개 연결 가운데 23개는 마지막 행이 계산한 끝 시각보다 1시간 넘게 뒤에 적혀 있었습니다. 그러니 마지막 행의 TimeStamp 를 연결이 끊긴 시각으로 쓰지 않습니다.

**행이 적히는 때는 따로 따집니다.** 기록 간격은 대부분 1시간 안팎입니다. 위 PC 에서는 기록 간격 1,375개 중 1,353개가 50~70분이었습니다. 기록 주기와 레지스트리 임시 저장은 [SRUM 해석 함정](1.md)을 봅니다.

**절전 시간이 ConnectedTime 에 들어가는지는 따로 확인합니다.** 연결이 여러 날 이어진 것처럼 보이면 [켜짐·꺼짐](../../event-logs/power-on-off-events.md) 기록과 맞춰 봅니다.

## 함정과 한계

- **행 수는 연결 횟수가 아닙니다.** 같은 연결이 기록 때마다 행을 하나씩 더 남깁니다. 인터페이스·L2ProfileId·ConnectStartTime 이 같은 행을 한 연결로 묶습니다. 연결 시간은 그 묶음에서 가장 큰 ConnectedTime 을 씁니다.
- **L2ProfileId 가 0 인 짧은 행이 섞입니다.** 위 PC 의 무선 행 중 53행이 L2ProfileId 0 이었습니다. 그중 52행은 ConnectedTime 이 0 이었습니다. 이 52행은 모두 같은 인터페이스의 프로필 번호가 있는 행과 시작 시각이 1초 안으로 붙어 있었습니다. 이런 행을 별도 연결로 세지 않습니다.
- **유선 연결은 이름을 풀기 어렵습니다.** 위 PC 의 유선(IfType 6) 행은 L2ProfileId 가 0 이었습니다. 유선 연결은 [네트워크 목록](../../network/networklist.md)과 시각을 맞춰 어느 네트워크였는지 좁힙니다.
- **이름을 못 풀 때가 있습니다.** SOFTWARE 하이브에 맞는 `ProfileIndex` 가 없으면 네트워크 이름을 알 수 없습니다. 프로필을 지웠거나, 하이브와 SRUDB.dat 의 시점이 다를 수 있습니다. SRUM 행은 별도 파일에 있으므로 프로필이 없다고 연결이 없었던 것은 아닙니다. 예전 하이브는 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 찾아봅니다.
- **시작 시각이 보관 기간보다 앞설 수 있습니다.** 위 PC 에서는 가장 오래된 행의 TimeStamp 보다 4일 넘게 앞선 ConnectStartTime 이 있었습니다. 연결이 오래 이어지면 시작 시각이 보관 기간보다 앞선 날짜로 남습니다.
- **도구마다 InterfaceLuid 를 다르게 보여 줍니다.** 원래 숫자를 그대로 보여 주는 도구도 있고, 유형 이름으로 바꿔 주는 도구도 있습니다. 결과를 비교할 때 한 행을 직접 풀어 봅니다.
- **압수 이미지의 SRUDB.dat 는 대개 비정상 종료 상태입니다.** 로그로 복구해야 여는 방식은 실패할 수 있습니다. 같은 손상 DB 도 읽는 방식에 따라 행 수가 다르게 나올 수 있습니다. 두 가지 이상 방식으로 열어 행 수를 비교하고, 항상 사본에서 작업합니다. 자세한 내용은 [트랜잭션 로그와 비정상 종료 상태](../../../01-foundations/database-log-formats/extensible-storage-engine/edb-log-dirty-shutdown.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 값은 형식 명세와 Microsoft 문서로 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. ESE 레코드 안에서 열을 찾는 방법은 [파일 구조](../../../01-foundations/database-log-formats/extensible-storage-engine/page-b-tree-catalog.md)를 봅니다. 여기서는 열 값만 풉니다. 모든 값은 리틀 엔디언 (Little-endian)입니다.

| 열 | 바이트 | 푼 값 |
|---|---|---|
| InterfaceLuid | `00 00 00 01 00 00 47 00` | 0x0047000001000000 |
| L2ProfileId | `01 00 00 10` | 0x10000001 = 268435457 |
| ConnectedTime | `18 15 00 00` | 0x1518 = 5400초 (1시간 30분) |
| ConnectStartTime | `00 74 4F C2 1E AA DC 01` | FILETIME 0x01DCAA1EC24F7400 = 2026-03-02 08:30:00 UTC |
| TimeStamp | `55 55 55 55 6D 80 E6 40` | 실수 46083.41666… = 2026-03-02 10:00:00 UTC |

InterfaceLuid 를 나누면 다음과 같습니다.

- 위 16비트 0x0047 → IfType 71 → 무선(IEEE 802.11)
- 가운데 24비트 0x000001 → NetLuidIndex 1
- 아래 24비트 0 → 예약

ConnectStartTime 에 5400초를 더하면 10:00:00 입니다. TimeStamp 와 같습니다. 즉 이 행을 적을 때 연결이 아직 이어지고 있었습니다. 더한 값이 TimeStamp 보다 이르면 그 시각에 연결이 끝났다고 봅니다.

L2ProfileId 0x10000001 은 SOFTWARE 하이브에서 `ProfileIndex` 가 268435457 인 프로필을 찾아 이름을 읽습니다.

### 공개 도구로 한 번

공개 도구의 결과를 위 계산과 맞춰 봅니다. 도구는 예로만 듭니다.

- **srum-dump** 는 InterfaceLuid 의 위 16비트를 유형 이름으로 바꿉니다. SOFTWARE 하이브를 함께 주면 L2ProfileId 를 네트워크 이름으로 바꿉니다. 끝난 시각을 계산한 열도 넣습니다.
- **plaso(log2timeline)** 의 SRUM 해석기는 TimeStamp 를 OLE 자동화 날짜로, ConnectStartTime 을 FILETIME 으로 읽습니다. 타임라인에는 두 시각이 따로 들어갑니다.
- **libesedb·dissect.esedb** 같은 ESE 라이브러리는 열 값을 원래 숫자로 내줍니다. 도구의 변환이 맞는지 한 행을 골라 직접 풀어 봅니다.

확인할 점은 세 가지입니다.

1. 연결 하나의 행들이 같은 ConnectStartTime 으로 묶이는지 봅니다.
2. "TimeStamp − ConnectStartTime" 과 ConnectedTime 을 비교해 연결이 이어지던 행과 끝난 행을 가릅니다.
3. 이름이 붙지 않은 L2ProfileId 가 있으면 프로필이 지워졌는지 확인합니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [Wi-Fi 프로필](../../network/wlan-profiles.md) | L2ProfileId 에 해당하는 SSID 와 보안 설정 |
| [네트워크 목록](../../network/networklist.md) | 네트워크별 처음·마지막 연결 날짜와 게이트웨이 MAC 주소 |
| [네트워크 연결 이벤트](../../event-logs/wlan-autoconfig-networkprofile.md) | 연결·해제 시각을 분·초 단위로 확인 |
| [네트워크 사용량](network-data-usage.md) | 같은 시간대, 같은 인터페이스·프로필에서 앱별 송수신량 |
| [네트워크 인터페이스 설정](../../network/tcp-ip-interfaces.md) | 인터페이스가 받은 IP 주소와 DHCP 기록 |
| [VPN 연결 기록](../../network/vpn-connections.md) | PPP·터널 유형 인터페이스가 보일 때 |
| [켜짐·꺼짐](../../event-logs/power-on-off-events.md) | 긴 연결 시간이 PC 가 켜져 있던 시간과 맞는지 |

사용 시간 전체를 재구성하는 흐름은 [PC 사용 시간 재구성](../../../04-scenarios/activity/system-usage-time.md)을 봅니다.

## 실습

Windows 10 이상 공개 데이터 세트(NIST CFReDS 등)에서 `SRUDB.dat` 와 SOFTWARE 하이브를 꺼내 아래 질문을 풀어 봅니다.

1. 네트워크 연결 표의 행은 몇 개이고, 인터페이스·L2ProfileId·ConnectStartTime 으로 묶으면 연결은 몇 개입니까?
2. 인터페이스 유형(IfType)은 몇 가지가 나옵니까? 무선과 유선의 비율은 어떻습니까?
3. 가장 오래 이어진 연결의 시작 시각과 계산한 끝 시각은 언제입니까? 이 시간대에 켜짐·꺼짐 이벤트는 맞습니까?
4. 모든 L2ProfileId 가 SOFTWARE 하이브의 `ProfileIndex` 와 맞습니까? 맞지 않는 번호가 있다면 이유를 찾아봅니다.
5. TimeStamp 와 ConnectStartTime 을 비교해 TimeStamp 가 UTC 인지 스스로 확인해 봅니다.

## 참고 문헌

- libyal, "System Resource Usage Monitor (SRUM)", esedb-kb — https://github.com/libyal/esedb-kb/blob/main/documentation/System%20Resource%20Usage%20Monitor%20(SRUM).asciidoc
- Microsoft Learn, "NET_LUID_LH union (ifdef.h)" — https://learn.microsoft.com/en-us/windows/win32/api/ifdef/ns-ifdef-net_luid_lh
- Mark Baggett, srum-dump 소스 코드 (`srum-dump/helpers.py`, `srum-dump/srum_dump.py`) — https://github.com/MarkBaggett/srum-dump
- plaso, `plaso.parsers.esedb_plugins.srum` 소스 — https://plaso.readthedocs.io/en/latest/_modules/plaso/parsers/esedb_plugins/srum.html
