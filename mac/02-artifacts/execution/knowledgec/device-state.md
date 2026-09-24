---
title: "화면·잠금 상태"
parent: "KnowledgeC"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 690
---

# 화면·잠금 상태 (Display·Device Lock)

knowledgeC.db의 `/display/isBacklit` 과 `/device/isLocked` 스트림은 화면이 켜져 있었는지, 기기가 잠겨 있었는지를 0과 1로 된 구간으로 남기고, 앱 사용 기록과 겹쳐 보면 그 시간대의 Mac 상태를 좁히는 데 쓸 수 있습니다.

## 무엇을 기록하나

상태형 스트림은 값을 `ZVALUEINTEGER` 칸에 0 또는 1로 적고, 그 값이 이어진 구간을 `ZSTARTDATE` 와 `ZENDDATE` 로 남깁니다. 칸 전체와 표 관계는 [표와 스트림 구조 (ZOBJECT·Stream)](structure.md)에 있습니다.

| 스트림 | 기록하는 것 | 0 | 1 | 근거 |
|---|---|---|---|---|
| `/display/isBacklit` | 화면 백라이트가 켜져 있었는지 | 꺼짐("NO") | 켜짐("YES") | [1][3] |
| `/device/isLocked` | 기기가 잠겨 있었는지 | "UNLOCKED" | "LOCKED" | [4] |
| `/device/isPluggedIn` | 전원이 연결되어 있었는지 | 거짓 | 참 | [1] |

표에서는 `/device/isPluggedIn` 도 다른 두 스트림처럼 0을 거짓, 1을 참으로 읽었고, 블로그 글은 이 스트림의 `ZVALUEINTEGER` 에 참·거짓이 들어간다고만 적고 있습니다 [1].

## 버전별 차이

| 스트림 | 확인 범위(macOS) | 근거 |
|---|---|---|
| `/display/isBacklit` | 10.13 블로그 목록, APOLLO 목록 10.13·10.14·10.15·10.16 | [1][3] |
| `/device/isLocked` | APOLLO 목록 10.15·10.16 | [4] |
| `/device/isPluggedIn` | 10.13 블로그 목록 | [1] |

`/device/isLocked` 는 10.13·iOS 11 기준 블로그 글에서 iOS 쪽 목록에만 있었고 [1], APOLLO `knowledge_device_locked` 모듈의 버전 목록에서 macOS는 10.15부터 나옵니다 [4]. 그래서 10.14 이전 검체에 이 스트림이 없더라도 이상하게 볼 일이 아닙니다. APOLLO 목록에 적힌 macOS 번호는 10.16까지라서, 그 뒤 버전에서는 `ZSTREAMNAME` 목록으로 스트림이 있는지 먼저 봅니다. 목록 읽는 법은 [표와 스트림 구조](structure.md)에 있습니다.

## 증거로서 의미

### 증명하는 것

`/display/isBacklit` 이 1인 구간은 그 시간대에 화면이 켜져 있었다는 기록이고 [1][3], `/device/isLocked` 가 0인 구간은 그 시간대에 기기 잠금이 풀려 있었다는 기록입니다 [4]. 두 구간을 [앱 사용 기록 (App Usage)](app-usage.md)의 앱 구간과 한 타임라인에 겹쳐 놓으면, 앱이 앞에 있던 시간 중 화면이 꺼져 있었거나 잠겨 있던 부분을 가려낼 수 있습니다. 이렇게 겹쳐 보는 방법은 참고 자료가 제시한 것이 아니라 이 핸드북이 권하는 읽는 법이라서, 결론은 각 기록이 말하는 만큼만 씁니다.

### 증명하지 못하는 것

화면이 켜져 있고 잠금이 풀려 있었다는 기록이 누가 그 앞에 있었는지를 알려 주지는 않습니다. 잠금이 화면 보호기에서 생겼는지, 잠자기나 로그아웃에서 생겼는지도 참고 자료로 확인하지 못해서 잠긴 이유를 이 기록만으로 적지 않습니다.

보고서에는 "사용자가 자리에 있었다" 대신 "2020-01-06 10:40:00부터 10:52:30(UTC)까지 `/display/isBacklit` 값이 1이고 `/device/isLocked` 값이 0인 구간이 기록되어 있다" 처럼 씁니다(시각은 설명용 예시).

## 시각 해석

구간 시각은 맥 절대 시각이고 UTC 기준이며, 현지 시각은 같은 행의 `ZSECONDSFROMGMT` 로 구합니다 [1][3][4]. APOLLO의 두 모듈은 시작 시각과 함께 구간 길이(초·분)와 요일, GMT 차, DB에 쓴 시각(ENTRY CREATION)을 같이 뽑습니다 [3][4]. 바꾸는 법과 계산 예시는 [표와 스트림 구조](structure.md)에 있습니다.

## 함정과 한계

잠금 관련 APOLLO 모듈은 `knowledge_device_locked.txt` 말고도 `knowledge_device_locked_imputed.txt`, `knowledge_device_keybag_locked.txt` 가 저장소에 있지만 [2], 이번에 내용을 열어 보지 않아서 무엇을 뽑는지와 macOS에서 쓰이는지는 확인하지 못했습니다. 같은 저장소의 `knowledge_device_pluggedin.txt`, `knowledge_user_first_backlight_after_wakeup.txt`, `knowledge_system_userwakingevent.txt` 도 이름만 확인한 모듈입니다 [2].

ZOBJECT에 약 4주치 기록이 들어 있었다는 10.13 관찰은 표 전체의 이야기라서 이 스트림에도 걸리고, 오래된 사건이면 구간이 비어 있는 것을 "화면을 켜지 않았다" 로 읽지 않습니다. 보관 기간 관찰의 범위는 [앱 사용 기록](app-usage.md)에 적었습니다.

## 직접 분석해 보기

DB 사본을 `sqlite3` 같은 공개 도구로 열고, APOLLO `knowledge_device_is_backlit` 모듈(조건 `ZSTREAMNAME is "/display/isBacklit"`)과 `knowledge_device_locked` 모듈(조건 `ZSTREAMNAME LIKE "/device/isLocked"`)처럼 값을 글자로 바꿔 뽑습니다 [3][4]. 아래는 두 스트림을 한 번에 시간순으로 보는 예시입니다.

```sql
SELECT
  datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS start_utc,
  datetime(ZOBJECT.ZENDDATE   + 978307200, 'unixepoch') AS end_utc,
  ZOBJECT.ZSTREAMNAME,
  CASE
    WHEN ZOBJECT.ZSTREAMNAME = '/display/isBacklit'
      THEN CASE ZOBJECT.ZVALUEINTEGER WHEN 0 THEN 'NO' WHEN 1 THEN 'YES' END
    WHEN ZOBJECT.ZSTREAMNAME = '/device/isLocked'
      THEN CASE ZOBJECT.ZVALUEINTEGER WHEN 0 THEN 'UNLOCKED' WHEN 1 THEN 'LOCKED' END
  END                                                   AS state,
  ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE                 AS seconds,
  ZOBJECT.ZSECONDSFROMGMT / 3600                        AS gmt_offset_hours,
  ZSOURCE.ZDEVICEID,
  ZOBJECT.Z_PK
FROM ZOBJECT
LEFT JOIN ZSOURCE ON ZOBJECT.ZSOURCE = ZSOURCE.Z_PK
WHERE ZOBJECT.ZSTREAMNAME IN ('/display/isBacklit', '/device/isLocked')
ORDER BY ZOBJECT.ZSTARTDATE;
```

결과에서 `ZDEVICEID` 가 여러 값으로 나오면 한 기기의 기록이 아닐 수 있으니, 이 칸을 읽는 주의는 [표와 스트림 구조](structure.md)를 따릅니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [앱 사용 기록 (App Usage)](app-usage.md) | 화면이 켜지고 잠금이 풀린 구간에 어떤 앱이 앞에 있었는지 |
| [전원·잠자기 기록 (pmset)](../../logs/power-events.md) | 화면이 꺼진 때가 잠자기와 맞물리는지 |
| [전원 로그 (PowerLog)](../powerlog.md) | 전원 상태를 다른 기록으로 맞춰 보기 |
| [로그인 창 설정 (loginwindow)](../../system-account/loginwindow.md) | 로그인 창 관련 설정 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../../logs/unified-log-events/index.md) | 같은 시각의 시스템 이벤트 |

시나리오로 엮는 방법은 [맥 사용 시간 재구성 (켜짐·잠자기·로그인) (Usage Time)](../../../04-scenarios/activity/usage-time.md)과 [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md)에서 다룹니다.

## 실습

macOS 공개 검체(NIST CFReDS 등)에서 knowledgeC.db를 찾았다면 아래 질문을 풀어 봅니다.

1. 검체의 macOS 버전에서 `/device/isLocked` 스트림이 있는가, 없다면 버전 표와 맞는가?
2. 하루 동안 `/display/isBacklit` 값이 1인 구간을 모두 더하면 몇 시간인가?
3. 앱 사용 구간 가운데 `/device/isLocked` 값이 1인 구간과 겹치는 것이 있는가, 있다면 어떻게 설명할 수 있는가?

## 참고 문헌

1. Sarah Edwards, "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (mac4n6.com, 2018-08-05) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. APOLLO 저장소 modules 폴더 목록 (GitHub API) — https://api.github.com/repos/mac4n6/APOLLO/contents/modules
3. APOLLO 모듈 knowledge_device_is_backlit.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_device_is_backlit.txt
4. APOLLO 모듈 knowledge_device_locked.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_device_locked.txt
