---
title: "앱별 데이터 사용량"
parent: "아티팩트 · 네트워크·연결"
nav_order: 680
---

# 앱별 데이터 사용량 (DataUsage.sqlite)

## 한 줄 요약

`DataUsage.sqlite` 는 아이폰이 앱·프로세스마다 셀룰러 데이터를 얼마나 주고받았는지 적는 Core Data 형식 SQLite DB 이고, 로컬 백업에 들어가서 오래된 기록까지 남는 편이라 "이 앱이 이 기기에서 네트워크를 쓴 적이 있나" 를 확인하는 데 씁니다.

## 무엇을 기록하나 · 왜 생기나

이 DB 의 중심은 `ZPROCESS` 와 `ZLIVEUSAGE` 표입니다 [1]. `ZPROCESS` 는 앱·프로세스 식별자(`ZBUNDLENAME`, `ZPROCNAME`)를 담고, `ZFIRSTTIMESTAMP` 는 그 프로세스를 처음 기록한 때, `ZTIMESTAMP` 는 가장 최근 활동으로 보입니다 [1]. `ZLIVEUSAGE` 에는 셀룰러(휴대폰 망) 바이트 칸 `ZWWANIN`·`ZWWANOUT` 이 있고, iOS 11 무렵 자료에는 와이파이 바이트 칸 `ZWIFIIN`·`ZWIFIOUT` 도 있었지만 와이파이 칸은 비어 있어서 이 DB 로는 와이파이 사용량을 알 수 없다는 보고가 있습니다 [1][2].

기록 단위가 앱이 아니라 프로세스라서, 사용자가 설치한 앱뿐만 아니라 확장(`ZEXTENSIONNAME`)이나 번들 ID 가 없는 프로세스도 목록에 나올 수 있습니다. 공개 도구 MVT 의 `Datausage` 모듈은 이 파일에서 프로세스별 네트워크 사용 이력을 뽑고 [2], 비슷한 기록을 담는 `netusage.sqlite` 를 읽는 `Netusage` 모듈은 올바른 번들 ID 가 없는 수상한 프로세스를 찾는 데 중점을 둡니다 [2].

## 위치와 버전별 차이

### 경로

| 파일 | 경로 | 근거 |
|---|---|---|
| `DataUsage.sqlite` | 기기 안 `/private/var/wireless/Library/Databases/DataUsage.sqlite` | [1][2] |
| `DataUsage.sqlite` | 백업 안 `/wireless/Library/Databases/DataUsage.sqlite` | [1] |
| `DataUsage-watch.sqlite` | 백업 안 `/wireless/Library/Databases/DataUsage-watch.sqlite` | [1] |
| `DataUsage.sqlite` | `WirelessDomain :: Library/Databases/DataUsage.sqlite` | |
| `CellularUsage.db` | `WirelessDomain :: Library/Databases/CellularUsage.db` | |
| `netusage.sqlite` | 기기 안 `/private/var/networkd/netusage.sqlite` | [1] |

`netusage.sqlite` 는 iOS 11.1.2 로 시험한 자료에서 파일 시스템 추출로만 얻을 수 있었지만 [1], MVT 문서는 출처를 "Backup & Full filesystem dump" 로 적어서 [2] 두 자료가 어긋나므로 버전과 수집 조건에 따라 다를 수 있다고 봅니다. 관찰한 암호화하지 않은 백업에는 `netusage.sqlite` 가 없었습니다. 백업 도메인 이름을 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 다룹니다.

### 버전별 차이

| 항목 | iOS 11 무렵 [1] | iOS 27.0 |
|---|---|---|
| `ZLIVEUSAGE` 의 와이파이 칸 | `ZWIFIIN`, `ZWIFIOUT` 있음(값 비어 있음) | 없음 |
| `ZLIVEUSAGE` 의 앱 식별자 | `ZPROCESS` 를 거쳐 찾음 | `ZBUNDLENAME`, `ZPROCNAME` 이 직접 있음 |
| 표 구성 | `ZPROCESS`, `ZLIVEUSAGE` 중심 | 진단용으로 보이는 표가 더 있음(아래) |

iOS 15 ~ 18 사이의 칸 구성은 확인하지 못해서, 검체의 iOS 버전을 먼저 적고 칸 이름을 직접 확인합니다.

## 구조

관찰한 iOS 27.0 백업의 표와 칸은 다음과 같습니다. `Z_PK`, `Z_ENT`, `Z_OPT` 칸과 `Z_METADATA`, `Z_MODELCACHE`, `Z_PRIMARYKEY` 표는 Core Data 가 만드는 틀이고, SQLite 자체를 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

| 표 | 칸 |
|---|---|
| `ZPROCESS` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZFIRSTTIMESTAMP`, `ZTIMESTAMP`, `ZBUNDLENAME`, `ZEXTENSIONNAME`, `ZPROCNAME` |
| `ZLIVEUSAGE` | `Z_PK`, `Z_ENT`, `Z_OPT`, `ZKIND`, `ZMETADATA`, `ZTAG`, `ZHASPROCESS`, `ZBILLCYCLEEND`, `ZTIMESTAMP`, `ZWWANIN`, `ZWWANOUT`, `ZBUNDLENAME`, `ZPROCNAME` |
| `ZDEMOLIVEUSAGE` | `ZINCARNATION`, `ZWIFIIN`, `ZWIFIOUT`, `ZWWANIN`, `ZWWANOUT`, `ZTIMESTAMP` |
| `ZPEER` | `ZADDRESS`, `ZDSTPORT`, `ZWITHEVENT`, `ZTIMESTAMP`, `ZFQDN` (그 밖 5칸 가림) |
| `ZEVENT` | `ZHAPPENEDONNET`, `ZHASPEER`, `ZHASSCENE`, `ZTIMESTAMP`, `ZFAILUREIMPACT`, `ZFAILURESTRING`, `ZSYNDROMEID` (그 밖 5칸 가림) |
| `ZEVENTSCENE` | `ZLINKQUALITY`, `ZRSSI`, `ZWITHEVENT`, `ZCOURSE`, `ZLATITUDE`, `ZLOCACCURACY`, `ZLONGITUDE`, `ZSPEED` (그 밖 2칸 가림) |
| `ZCHECKUPEVENT` | `ZTIMESTAMP`, `ZSYNDROMEID` |
| `ZTSHOOTINGDATA` | `ZWITHCHECKUPEVENT`, `ZWITHEVENT`, `ZTIMESTAMP`, `ZPROVIDERS` |
| `ZWIFIDATA` | 와이파이 접속 지점·신호·위치 칸 |

`ZLIVEUSAGE` 의 `ZHASPROCESS` 는 이름으로 보아 `ZPROCESS` 의 행을 가리키는 칸이지만, 이 연결에 정식 외래 키 제약이 있는지는 확인하지 못했습니다. `ZPEER`·`ZEVENT`·`ZEVENTSCENE`·`ZCHECKUPEVENT`·`ZTSHOOTINGDATA` 는 칸 이름으로 보아 연결 문제를 진단하는 표로 보이고, `ZPEER` 에 주소·목적지 포트·도메인 이름(`ZFQDN`) 칸이, `ZEVENTSCENE` 에 위도·경도·속도 칸이 있지만 공개 자료로 칸의 뜻을 확인하지 못했습니다. `ZWIFIDATA` 의 칸 목록과 해석은 [와이파이 기록](wifi.md) 에서 다룹니다.

같은 도메인의 `CellularUsage.db` 에는 `bundle_info`(`ROWID`, `bundle_id`, `flags`), `bundle_uuid`(`ROWID`, `bundle_id`, `macho_uuid`), `subscriber_info` 표가 있고, `subscriber_info` 에는 `subscriber_id`, `subscriber_mdn`, `slot_id`, `last_update_time`, `home_budget`, `roaming_budget`, `user_entered_bill_end_dom`, `low_data_mode`, `smart_data_mode`, `privacy_proxy` 등의 칸이 있습니다. 칸 이름으로 보아 번들 ID 목록과 가입자(유심) 정보를 담는 DB 이지만, 값의 뜻은 확인하지 못했습니다.

`HomeDomain :: Library/Preferences/com.apple.osanalytics.addaily.plist` 에는 `netUsageBaseline` 키가 있고 그 아래 키가 프로세스·번들 이름입니다. 이 목록의 용도는 확인하지 못했지만, DataUsage 에 나온 이름과 대조하는 보조 자료로 쓸 수 있습니다.

## 증거로서 의미

**증명하는 것**

- `ZPROCESS` 에 어떤 번들 ID 나 프로세스 이름이 있으면, 그 프로세스가 이 기기에서 기록된 적이 있다는 사실을 보여 줍니다. 행이 언제 지워지는지는 확인하지 못해서, 지금의 설치 목록과 비교해 차이를 따로 적어 둡니다.
- `ZLIVEUSAGE` 의 `ZWWANIN`·`ZWWANOUT` 에 값이 있으면, 그 프로세스가 셀룰러 망으로 그만큼 주고받은 기록이 있다는 사실까지 말할 수 있습니다.
- 번들 ID 가 없거나 이상한 프로세스 이름은 스파이웨어 점검에서 더 살펴볼 대상이 됩니다 [2].

**증명하지 못하는 것**

- 바이트 수는 무엇을 주고받았는지 알려 주지 않습니다. 파일을 보냈다거나 특정 상대와 통신했다고 쓸 수 없습니다.
- 와이파이 사용량은 이 DB 로 알 수 없어서 [1], 셀룰러 값이 없다고 해서 그 앱이 네트워크를 쓰지 않았다고 결론 내리지 않습니다.
- 프로세스가 뒤에서 통신했을 수 있어서, 사용자가 그 시각에 앱을 직접 썼다는 증거가 아닙니다. 앞에 띄운 기록은 [KnowledgeC](../app-usage/knowledgec/index.md) 나 [바이옴](../app-usage/biome/index.md) 과 맞춰 봅니다.

보고서에는 "이 시간대까지 이 앱 프로세스가 셀룰러로 이만큼 송신한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`ZPROCESS` 의 `ZFIRSTTIMESTAMP` 는 처음 기록한 때, `ZTIMESTAMP` 는 가장 최근 활동으로 보입니다 [1]. 표 모양이 Core Data 라서 시각 칸이 Mac 절대 시각(2001-01-01 UTC 기준 초)일 가능성이 크지만 원문으로 확인하지는 못해서, 값 몇 개를 다른 기록의 시각과 맞춰 기준을 확인한 뒤에 바꿉니다. 기준별 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

바이트 칸은 순간 사용량이 아니라 쌓인 값일 수 있습니다. `ZLIVEUSAGE` 의 한 행이 어느 기간의 합인지, `ZBILLCYCLEEND` 가 요금 청구 주기의 끝을 뜻하는지는 확인하지 못해서, 행 하나의 `ZTIMESTAMP` 를 "그 시각에 그만큼 썼다" 로 읽지 않습니다.

## 함정과 한계

DataUsage.sqlite 는 백업에 들어가서 오래된 기록이 남는 편이고, 글쓴이 기기에서는 2013년 기록까지 있었습니다 [1]. 이전 기기의 백업으로 복원한 기기라면 지금 기기를 쓰기 전의 행이 섞여 있을 수 있으니 [초기화와 복원 흔적](../system-account/erase-restore.md) 을 함께 봅니다.

칸 구성이 버전마다 다릅니다. iOS 11 자료의 칸 설명을 그대로 믿고 `ZWIFIIN` 을 찾으면 iOS 27.0 의 `ZLIVEUSAGE` 에서는 칸이 없어 질의가 실패합니다. 반대로 `ZDEMOLIVEUSAGE` 에는 와이파이 칸이 있지만 이 표가 무엇을 기록하는지는 확인하지 못했습니다.

`netusage.sqlite` 는 수집 방식에 따라 없을 수 있어서, 로컬 백업만 받았다면 한쪽만 보고 있다는 점을 보고서에 적습니다. 수집 방식별 범위는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

SQLite 파일이라 WAL 파일이나 지운 행 조각이 남을 수 있습니다. 행이 비어 있거나 줄었다면 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 와 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름으로 확인합니다.

## 직접 분석해 보기

복사본을 헥스 편집기로 열어 첫 16바이트가 SQLite 헤더인지 먼저 봅니다. 아래는 SQLite 파일 형식 명세로 만든 예시이고 특정 검체의 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F   문자
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

그다음 SQLite 명령행 도구(`sqlite3` 등)로 칸 이름부터 확인합니다. 버전마다 칸이 달라서 이 단계를 건너뛰지 않습니다.

```sql
PRAGMA table_info(ZLIVEUSAGE);
PRAGMA table_info(ZPROCESS);
```

iOS 27.0 처럼 `ZLIVEUSAGE` 에 번들 이름이 직접 있으면 아래처럼 프로세스별 셀룰러 합을 뽑습니다. 시각 칸은 원래 숫자 그대로 두고, 기준을 확인한 뒤에 바꾼 값을 붙입니다.

```sql
SELECT ZBUNDLENAME, ZPROCNAME,
       SUM(ZWWANIN)  AS wwan_in,
       SUM(ZWWANOUT) AS wwan_out,
       MIN(ZTIMESTAMP) AS first_ts,
       MAX(ZTIMESTAMP) AS last_ts
FROM ZLIVEUSAGE
GROUP BY ZBUNDLENAME, ZPROCNAME
ORDER BY wwan_out DESC;
```

`ZPROCESS` 의 처음·마지막 기록 시각은 `SELECT ZBUNDLENAME, ZPROCNAME, ZFIRSTTIMESTAMP, ZTIMESTAMP FROM ZPROCESS;` 로 따로 봅니다. 공개 도구로는 MVT 의 `Datausage`·`Netusage` 모듈이 이 기록을 뽑아 주고 [2], 도구 결과는 위 질의 결과와 행 수를 맞춰 봅니다. 도구 결과를 검증하는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/installed-apps.md) | 이 DB 의 번들 ID 가 지금 설치되어 있는지 |
| [KnowledgeC](../app-usage/knowledgec/index.md) · [바이옴](../app-usage/biome/index.md) | 앱을 앞에 띄운 시각 |
| [화면 사용 시간](../app-usage/screen-time.md) | 앱 사용 시간 |
| [전원 로그](../app-usage/powerlog.md) | 같은 시간대의 기기 상태 |
| [와이파이 기록](wifi.md) | 같은 DB 의 `ZWIFIDATA` 와 와이파이 접속 |
| [VPN 설정](vpn.md) | VPN 앱 프로세스가 기록에 있는지 |
| [충돌·진단 기록](../app-usage/diagnostics.md) | 같은 프로세스 이름의 진단 기록 |

스파이웨어 점검 흐름은 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) 과 [스파이웨어 감염 흔적](../../04-scenarios/incident/spyware.md), 자료 유출 판단은 [자료를 밖으로 보냈나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등)에 아이폰 백업이나 추출이 있으면 아래 질문으로 풀어 봅니다.

1. 검체의 iOS 버전에서 `ZLIVEUSAGE` 에 `ZWIFIIN` 칸이 있습니까? `ZBUNDLENAME` 은 어느 표에 있습니까?
2. `ZPROCESS` 에 있는 번들 ID 가운데 설치 목록에 없는 번들 ID 는 무엇입니까?
3. `ZFIRSTTIMESTAMP` 가 가장 이른 행은 언제입니까? 그 값을 Mac 절대 시각으로 읽으면 기기를 처음 쓴 시기와 맞습니까?
4. 셀룰러 송신량이 가장 큰 프로세스는 무엇이고, 같은 시간대에 KnowledgeC 나 바이옴에 그 앱을 앞에 띄운 기록이 있습니까?
5. 파일 시스템 추출이 있다면 `netusage.sqlite` 와 DataUsage.sqlite 의 프로세스 목록은 어떻게 다릅니까?

## 참고 문헌

1. "Network and Application Usage using netusage.sqlite & DataUsage.sqlite iOS Databases" — mac4n6.com — http://www.mac4n6.com/blog/2019/1/6/network-and-application-usage-using-netusagesqlite-amp-datausagesqlite-ios-databases
2. MVT 문서, "Records extracted by mvt-ios" — https://docs.mvt.re/en/latest/ios/records/
