---
title: "앱별 네트워크 사용량"
parent: "아티팩트 · 네트워크"
nav_order: 1620
---

# 앱별 네트워크 사용량 (netusage)

`netusage.sqlite` 에는 프로세스마다 Wi-Fi·유선·셀룰러로 받은 양과 보낸 양, 처음 본 시각과 마지막으로 본 시각이 남고, 망 연결마다 주고받은 양도 따로 남아서, 어떤 프로세스가 어느 무렵 어느 경로로 네트워크를 썼는지 가늠할 수 있습니다.

이 페이지는 공개 도구 mac_apt 의 NETUSAGE 플러그인 소스 [1]와 ForensicArtifacts 정의 [2]로 확인한 경로와 표를 다룹니다. mac_apt 소스는 도구가 이 표와 칸을 읽는다는 근거이고 Apple 이 밝힌 형식 명세가 아니라서, 칸의 뜻은 칸 이름과 도구의 처리 방식에서 읽어 낼 수 있는 만큼만 적습니다.

## 무엇을 기록하나 · 왜 생기나

macOS 는 프로세스별 네트워크 사용량을 SQLite 데이터베이스에 모아 두고, mac_apt 는 이 DB 에서 두 가지를 뽑습니다 [1]. 하나는 프로세스별 사용량이고, 칸 이름으로 보면 Wi-Fi, 유선, 셀룰러(WWAN) 각각의 받은 양과 보낸 양이 나뉘어 있습니다. 다른 하나는 망 연결(network attachment)별로 주고받은 양입니다 [1].

이 DB 를 어느 데몬이 쓰는지, 값을 얼마나 자주 쌓고 언제 지우는지는 이번 자료로 확인하지 못했습니다. 그래서 이 기록은 "이 프로세스가 네트워크를 이만큼 썼다는 기록이 이 시각 기준으로 있다" 는 데까지 쓰고, 쌓인 기간은 시각 칸으로 따로 따집니다.

## 위치와 버전별 차이

| macOS 버전 | 경로 |
|---|---|
| 10.15 Catalina 까지 | `/private/var/networkd/netusage.sqlite` |
| 11 Big Sur 부터 | `/private/var/networkd/db/netusage.sqlite` |

경로는 mac_apt 가 읽는 위치이고 [1], iOS 에서는 `/private/var/networkd/netusage.sqlite` 입니다 [1]. ForensicArtifacts 의 `MacOSNetworkUsageSQLiteDatabaseFile` 정의에는 옛 경로(`/private/var/networkd/netusage.sqlite`, `/var/networkd/netusage.sqlite`)만 있고 `db/` 아래 경로는 없어서 [2], macOS 11 이후 검체를 이 정의로 수집했다면 DB 가 빠지지 않았는지 확인합니다.

## 구조

DB 는 SQLite 이고, 표 이름에 `Z` 접두어가 붙는 Core Data 방식입니다 [1]. 파일 형식과 레코드 읽는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)를 따릅니다. 아래는 mac_apt 가 쓰는 표와 칸이고 [1], 표마다 다른 칸이 더 있는지는 확인하지 못했습니다.

| 표 | 칸 | 이어지는 곳 |
|---|---|---|
| `ZPROCESS` | `Z_PK`, `Z_ENT`, `ZPROCNAME`, `ZFIRSTTIMESTAMP`, `ZTIMESTAMP` | |
| `ZLIVEUSAGE` | `ZHASPROCESS`, `ZTIMESTAMP`, `ZWIFIIN`, `ZWIFIOUT`, `ZWIREDIN`, `ZWIREDOUT`, `ZWWANIN`, `ZWWANOUT` | `ZHASPROCESS` → `ZPROCESS.Z_PK` |
| `ZNETWORKATTACHMENT` | `Z_PK`, `Z_ENT`, `ZIDENTIFIER`, `ZFIRSTTIMESTAMP`, `ZTIMESTAMP` | |
| `ZLIVEROUTEPERF` | `ZHASNETWORKATTACHMENT`, `ZTIMESTAMP`, `ZBYTESIN`, `ZBYTESOUT` | `ZHASNETWORKATTACHMENT` → `ZNETWORKATTACHMENT.Z_PK` |
| `Z_PRIMARYKEY` | `Z_ENT`, `Z_NAME` | 각 표의 `Z_ENT` 가 어떤 종류의 항목인지 이름으로 풀어 줍니다 |

프로세스 사용량은 `ZLIVEUSAGE` 한 줄을 `ZHASPROCESS` 로 `ZPROCESS` 에 이어 읽고, 망 연결 사용량은 `ZLIVEROUTEPERF` 한 줄을 `ZHASNETWORKATTACHMENT` 로 `ZNETWORKATTACHMENT` 에 이어 읽습니다 [1]. `ZPROCNAME` 이 프로세스 이름만 담는지 번들 ID 와 섞인 모양인지, `ZNETWORKATTACHMENT.ZIDENTIFIER` 가 어떤 모양의 값인지는 확인하지 못해서, 검체에서 나온 값을 그대로 옮겨 적습니다.

## 증거로서 의미

**증명하는 것.** `ZPROCESS` 에 프로세스가 있으면 그 이름으로 네트워크 사용량 기록이 남았다는 뜻이고, `ZFIRSTTIMESTAMP` 와 `ZTIMESTAMP` 는 칸 이름으로 보아 이 DB 가 그 프로세스를 처음 본 때와 마지막으로 본 때입니다 [1]. `ZLIVEUSAGE` 의 여섯 칸은 경로(Wi-Fi·유선·셀룰러)마다 받은 양과 보낸 양을 나눠 적어서, 한 프로세스가 주로 어느 경로로 얼마나 보냈는지 비교할 수 있습니다. 보낸 양이 받은 양보다 크게 많은 프로세스는 자료 유출을 따질 때 먼저 볼 후보가 되지만, 이 판단은 칸 이름에서 끌어낸 해석이라 다른 기록으로 받칩니다.

**증명하지 못하는 것.** 이 DB 는 어느 주소와 통신했는지, 무엇을 보냈는지 알려 주지 않습니다. mac_apt 가 쓰는 칸에는 사용자 계정 칸이 없어서, 같은 이름의 프로세스를 여러 사용자가 돌렸다면 누구의 사용량인지 이 DB 로는 알 수 없습니다. 값의 단위가 바이트인지는 이번 자료로 확인하지 못했고, 망 연결 쪽 칸만 mac_apt 가 "Bytes in/out" 으로 설명합니다 [1]. 프로세스가 목록에 없다고 네트워크를 쓰지 않았다는 뜻도 아닌데, 기록을 언제 지우거나 초기화하는지 확인하지 못했기 때문입니다.

보고서에는 "`ZLIVEUSAGE` 에 이 프로세스가 이 시각 이후 Wi-Fi 로 보낸 양이 이만큼 적혀 있다" 처럼 기록이 말하는 만큼만 쓰고, 단위를 확인하지 못했다면 그 점도 함께 적습니다.

## 시각 해석

이 페이지의 `*TIMESTAMP` 칸은 모두 맥 절대 시각(2001-01-01 기준 초)이고, mac_apt 는 이 값을 `ReadMacAbsoluteTime` 으로 바꿉니다 [1]. 기준 시각과 시간대 처리는 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따르고, 도구가 보여 주는 값이 UTC 인지 현지 시각으로 바꾼 값인지 함께 적습니다.

사용량 칸을 읽을 때는 시각 칸과 짝을 맞춰야 합니다. mac_apt 출력 주석은 프로세스 사용량에 "Data usage is counted from ArtifactDate onwards" 라고 적는데 [1], 곧 `ZLIVEUSAGE` 의 여섯 칸은 같은 줄의 `ZTIMESTAMP` 이후에 쌓인 양입니다. 망 연결 쪽은 "Bytes in/out are based off ArtifactDate" 라고 적습니다 [1]. 그래서 사용량 수치를 `ZPROCESS.ZFIRSTTIMESTAMP` 부터 쌓인 전체 양으로 읽으면 틀릴 수 있습니다.

## 함정과 한계

- **두 경로.** macOS 11 부터 DB 가 `db/` 아래로 옮겨 가서 [1], 옛 경로만 찾으면 없는 것으로 잘못 봅니다. 업그레이드한 맥이라면 두 경로를 모두 찾아봅니다.
- **수집 정의의 빈틈.** ForensicArtifacts 정의에 새 경로가 없어서 [2], 이 정의에 기대는 수집 도구가 새 DB 를 빠뜨릴 수 있습니다.
- **사용량 칸의 기준 시각.** 사용량은 그 줄의 `ZTIMESTAMP` 이후에 쌓인 양이라서 [1], 시각 칸 없이 수치만 옮기면 기간을 잃습니다.
- **확인하지 못한 단위와 주기.** 값의 단위, 쌓는 주기, 초기화 조건은 이번 자료로 확인하지 못했습니다.
- **SQLite 부속 파일.** DB 옆에 `-wal`, `-shm` 파일이 있으면 함께 수집해야 최근 기록을 잃지 않고, 지운 레코드를 찾는 법은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)와 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)를 따릅니다.

## 직접 분석해 보기

원본을 바로 열지 말고 DB 와 부속 파일을 함께 작업 폴더에 복사한 뒤 사본으로 봅니다.

### 헥스로 한 번

맥 절대 시각은 2001-01-01 00:00:00 부터 흐른 초라서, Unix 시각으로 바꾸려면 1970-01-01 과 2001-01-01 사이의 초 978307200 을 더합니다. 아래는 이 규칙으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다.

```
ZTIMESTAMP 값             700000000
+ 978307200               1678307200  (Unix 시각)
날짜로 바꾸면             2023-03-08 20:26:40 UTC
```

헥스 편집기로 DB 를 열었을 때 파일 머리말과 표 레코드 안의 값이 어떤 바이트로 저장되는지는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 레코드 형식을 따라 읽습니다.

### 공개 도구로 한 번

`sqlite3` 로 사본을 열어 위 표 관계대로 이어 읽습니다. 아래 쿼리는 mac_apt 가 쓰는 칸 [1]만으로 만든 것입니다.

```sql
SELECT p.ZPROCNAME,
       datetime(p.ZFIRSTTIMESTAMP + 978307200, 'unixepoch') AS first_seen_utc,
       datetime(p.ZTIMESTAMP      + 978307200, 'unixepoch') AS last_seen_utc,
       datetime(u.ZTIMESTAMP      + 978307200, 'unixepoch') AS counted_from_utc,
       u.ZWIFIIN, u.ZWIFIOUT, u.ZWIREDIN, u.ZWIREDOUT, u.ZWWANIN, u.ZWWANOUT
FROM ZLIVEUSAGE u
JOIN ZPROCESS p ON u.ZHASPROCESS = p.Z_PK
ORDER BY u.ZWIFIOUT + u.ZWIREDOUT + u.ZWWANOUT DESC;

SELECT n.ZIDENTIFIER,
       datetime(r.ZTIMESTAMP + 978307200, 'unixepoch') AS based_on_utc,
       r.ZBYTESIN, r.ZBYTESOUT
FROM ZLIVEROUTEPERF r
JOIN ZNETWORKATTACHMENT n ON r.ZHASNETWORKATTACHMENT = n.Z_PK;
```

mac_apt NETUSAGE 플러그인 [1]을 돌려 같은 프로세스의 수치와 시각이 같게 나오는지 맞춰 보면, 쿼리와 도구 결과를 서로 검증할 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [와이파이 기록 (Wi-Fi)](wifi.md) | Wi-Fi 송수신이 쌓인 무렵 어느 망에 붙어 있었는지 |
| [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md) | 그 무렵 받은 IP 와 공유기 |
| [KnowledgeC (knowledgeC.db)](../execution/knowledgec/index.md) | 같은 앱이 그 무렵 앞에 나와 쓰였는지 |
| [통합 로그의 프로세스 실행 기록 (Process Events)](../execution/unified-log-process.md) | 프로세스가 실제로 실행된 시각 |
| [원격 접속 (Remote Access)](remote-access/index.md) | 원격 접속 도구의 송수신 양 |
| [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) | 보낸 양이 많은 프로세스를 유출 경로로 따지는 흐름 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 검체의 macOS 버전을 먼저 확인하고, 두 경로 가운데 어디에 `netusage.sqlite` 가 있는지 찾아보세요.
2. `Z_PRIMARYKEY` 의 `Z_NAME` 목록을 뽑아 표마다 어떤 항목 종류인지 적어 보세요.
3. 보낸 양(`ZWIFIOUT`, `ZWIREDOUT`, `ZWWANOUT`의 합)이 가장 큰 프로세스 다섯 개를 뽑고, 각 줄의 `ZTIMESTAMP` 를 함께 적어 보세요.
4. `ZNETWORKATTACHMENT.ZIDENTIFIER` 값은 어떤 모양인가요? 와이파이 기록의 SSID 와 이어지는 값이 있는지 보세요.
5. 3번의 프로세스가 KnowledgeC 나 통합 로그에도 같은 무렵 나오는지 확인해 보세요.

## 참고 문헌

1. mac_apt `netusage.py` NETUSAGE 플러그인 소스 (Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/netusage.py
2. ForensicArtifacts `macos.yaml` (MacOSNetworkUsageSQLiteDatabaseFile) — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
