---
title: "앱 사용 기록"
parent: "KnowledgeC"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 680
---

# 앱 사용 기록 (App Usage)

knowledgeC.db의 `/app/inFocus` 와 `/app/usage` 스트림은 어느 GUI 앱이 언제부터 언제까지 쓰이고 있었는지를 초 단위 구간으로 남기고, `/app/activity` 와 `/safari/history` 는 앱 안에서 무엇을 보고 있었는지를 덧붙입니다.

## 무엇을 기록하나

`/app/inFocus` 는 어느 앱이 그 시각에 앞에 나와 쓰이고 있었는지를 기록합니다. `ZSTARTDATE` 는 앱이 앞으로 온 때이고 `ZENDDATE` 는 뒤로 간 때라서, 둘의 차이가 그 구간의 사용 시간(초)이 됩니다 [1][4]. 앱은 `ZVALUESTRING` 에 번들 ID로 들어 있어서 앱 이름을 알려면 번들 ID를 설치된 앱과 맞춰 봅니다.

`/app/usage` 는 시작·끝·번들 ID·사용 시간을 담고, `ZSOURCE.ZDEVICEID` 와 ZCUSTOMMETADATA 표의 이름·값을 함께 이어 읽을 수 있습니다 [3]. `/app/inFocus` 와 구간을 끊는 기준이 어떻게 다른지는, 두 스트림이 모두 있으면 같은 시간대를 나란히 놓고 비교해 확인합니다.

`/app/activity` 는 앱 안에서 무엇을 했는지를 남기고, ZSTRUCTUREDMETADATA 표의 활동 종류(`…ACTIVITYTYPE`)와 제목(`…TITLE`) 열에 보고 있던 항목이나 편집하던 항목이 들어갑니다 [1]. `/safari/history` 는 `ZVALUESTRING` 에 URL을 남깁니다 [1].

표와 열의 전체 구조, 열 이름의 원래 모양은 [표와 스트림 구조 (ZOBJECT·Stream)](structure.md)에 있습니다.

## 버전별 차이

| 스트림 | 확인 범위(macOS) | 근거 |
|---|---|---|
| `/app/inFocus` | 10.13 블로그 목록, APOLLO 목록 10.13·10.14·10.15·10.16 | [1][4] |
| `/app/usage` | APOLLO 목록 10.14·10.15·10.16 | [3] |
| `/app/activity` | 10.13 블로그 목록 | [1] |
| `/safari/history` | 10.13 블로그 목록 | [1] |

APOLLO 목록은 iOS 번호와 macOS 번호를 섞어 쓰고 macOS 쪽은 10.16까지만 적혀 있습니다. 목록을 읽는 법은 [표와 스트림 구조](structure.md)에서 설명하고, 그 뒤 버전은 실제 데이터에서 `ZSTREAMNAME` 목록을 뽑아 직접 확인합니다.

## 증거로서 의미

### 증명하는 것

`/app/inFocus` 구간이 있으면 그 시간대에 그 번들 ID의 GUI 앱이 앞에 나와 쓰이고 있었다는 기록이 있다고 말할 수 있고, 구간 길이로 얼마나 오래 앞에 있었는지도 셀 수 있습니다 [1][4]. `/app/activity` 의 제목이나 `/safari/history` 의 URL이 있으면 그 시각에 앱 안에서 어떤 항목을 다뤘는지까지 좁힐 수 있습니다 [1].

### 증명하지 못하는 것

기록은 GUI 앱만 남아서 터미널은 번들 ID로만 보이고 어떤 명령을 쳤는지는 남지 않으며, 백그라운드 프로세스가 실행됐는지도 여기서는 알 수 없습니다 [1]. 앱이 앞에 있었다는 기록이 사람이 화면 앞에 있었다는 뜻은 아니라서, 사람이 있었는지는 [화면·잠금 상태 (Display·Device Lock)](device-state.md)와 다른 기록을 함께 보고 판단합니다. 누가 그 계정으로 앱을 썼는지도 이 기록만으로는 가려내지 못합니다.

보고서에는 "사용자가 이 앱으로 작업했다" 대신 "2020-01-06 10:40:00부터 10:52:30(UTC)까지 이 번들 ID의 앱이 앞에 나와 있던 구간이 `/app/inFocus` 에 기록되어 있다" 처럼 기록으로 확인되는 만큼만 씁니다(시각은 설명용 예시).

## 시각 해석

시작·끝·기록 시각은 모두 맥 절대 시각이고 UTC 기준이라서, 현지 시각으로 보여 줄 때는 행마다 들어 있는 `ZSECONDSFROMGMT` 를 씁니다 [1][3]. 바꾸는 법과 계산 예시는 [표와 스트림 구조](structure.md)에 있고, 여행이나 설정 변경으로 시간대가 바뀐 기간은 [시간대와 시계 설정 (Time Zone·NTP)](../../system-account/time-zone.md)과 맞춰 봅니다.

## 함정과 한계

macOS 10.13에서는 ZOBJECT에 약 4주치 기록이 들어 있었습니다 [1]. 공개된 보관 정책이 없으므로 10.15 이후 버전은 실제 데이터로 확인합니다. 사건이 수집 시점보다 한참 전이라면 기록이 이미 사라졌을 수 있으니, 기록이 없다는 것을 "앱을 쓰지 않았다" 로 읽지 않습니다.

`/app/inFocus` 의 LAUNCHREASON 열 값은 뜻이 정해져 있지 않으므로, 값을 그대로 옮겨 적되 "이렇게 실행됐다" 는 해석은 붙이지 않습니다. ZCUSTOMMETADATA의 이름·값도 같은 방식으로 다룹니다.

## 직접 분석해 보기

DB 사본을 `sqlite3` 같은 공개 도구로 열고, APOLLO `knowledge_app_inFocus` 모듈이 뽑는 열을 따라 쿼리를 짭니다 [4]. 모듈의 조건은 `ZSTREAMNAME IS "/app/inFocus"` 이고, 아래는 그 모양을 줄인 예시입니다.

```sql
SELECT
  datetime(ZOBJECT.ZSTARTDATE + 978307200, 'unixepoch') AS start_utc,
  datetime(ZOBJECT.ZENDDATE   + 978307200, 'unixepoch') AS end_utc,
  ZOBJECT.ZVALUESTRING                                  AS bundle_id,
  ZOBJECT.ZENDDATE - ZOBJECT.ZSTARTDATE                 AS seconds,
  ZSTRUCTUREDMETADATA.Z_DKAPPLICATIONMETADATAKEY__LAUNCHREASON AS launch_reason,
  ZOBJECT.ZSECONDSFROMGMT / 3600                        AS gmt_offset_hours,
  datetime(ZOBJECT.ZCREATIONDATE + 978307200, 'unixepoch') AS written_utc,
  ZOBJECT.ZUUID,
  ZOBJECT.Z_PK
FROM ZOBJECT
LEFT JOIN ZSTRUCTUREDMETADATA
  ON ZOBJECT.ZSTRUCTUREDMETADATA = ZSTRUCTUREDMETADATA.Z_PK
WHERE ZOBJECT.ZSTREAMNAME = '/app/inFocus'
ORDER BY ZOBJECT.ZSTARTDATE;
```

`/app/usage` 는 Z_4EVENT와 ZCUSTOMMETADATA를 더 붙여야 해서 연결 방법은 [표와 스트림 구조](structure.md)를 따릅니다. 공개 도구 APOLLO에는 이 페이지의 스트림에 맞는 `knowledge_app_inFocus.txt`, `knowledge_app_usage.txt` 모듈이 있고, 같은 저장소에 `knowledge_app_activity.txt`, `knowledge_app_intents.txt`, `knowledge_safari_browsing.txt` 모듈도 있습니다 [2].

저장된 시각 값 하나를 손으로 푸는 예시는 [표와 스트림 구조](structure.md)에 있습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [화면·잠금 상태 (Display·Device Lock)](device-state.md) | 앱 사용 구간에 화면이 켜져 있었고 잠금이 풀려 있었는지 |
| [터미널 명령 기록 (zsh_history·bash_sessions)](../shell-history.md) | 터미널이 앞에 있던 구간에 어떤 명령을 쳤는지 |
| [통합 로그의 프로세스 실행 기록 (Process Events)](../unified-log-process.md) | GUI가 아닌 프로세스의 실행 |
| [화면 사용 시간 (Screen Time)](../screen-time.md) | 앱 사용 구간을 다른 기록과 맞춰 보기 |
| [바이옴 (Biome)](../biome/index.md) | 같은 분류(프로그램 실행 흔적)의 다른 기록 |
| [사파리 (Safari)](../../browsers/safari/index.md) | `/safari/history` URL을 사파리 방문 기록과 맞춰 보기 |
| [설치한 앱과 영수증 (Applications·Receipts)](../../system-account/installed-apps-receipts.md) | 번들 ID가 가리키는 앱 |

여러 기록을 한 줄로 엮는 방법은 [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)과 [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md)에서 다룹니다.

## 실습

macOS 공개 시험 자료(NIST CFReDS 등)에서 knowledgeC.db를 찾았다면 아래 질문을 풀어 봅니다.

1. `ZSTREAMNAME` 목록을 뽑았을 때 `/app/inFocus` 와 `/app/usage` 가 둘 다 있는가, 그렇다면 같은 시간대의 구간이 어떻게 다른가?
2. 사용 시간이 가장 긴 번들 ID 세 개는 무엇이고, 현지 시각으로 바꾸면 주로 어느 시간대에 쓰였는가?
3. 터미널 번들 ID가 앞에 있던 구간에 셸 기록에는 어떤 명령이 남아 있는가?
4. 가장 오래된 행의 시작 시각과 수집 시각 사이는 며칠인가?

## 참고 문헌

1. Sarah Edwards, "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (mac4n6.com, 2018-08-05) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. APOLLO 저장소 modules 폴더 목록 (GitHub API) — https://api.github.com/repos/mac4n6/APOLLO/contents/modules
3. APOLLO 모듈 knowledge_app_usage.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_usage.txt
4. APOLLO 모듈 knowledge_app_inFocus.txt — https://raw.githubusercontent.com/mac4n6/APOLLO/master/modules/knowledge_app_inFocus.txt
