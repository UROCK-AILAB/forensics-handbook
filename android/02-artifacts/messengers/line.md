---
title: "라인"
parent: "아티팩트 · 메신저"
nav_order: 970
---

# 라인 (LINE)

라인 Android 앱은 대화 DB 를 확장자 없는 파일 `naver_line` 에 두고, 표 구조를 다룬 공개 자료가 적어서 파일을 직접 열어 구조부터 확인해야 하는 앱입니다.

## 무엇을 기록하나 · 왜 생기나

라인은 주고받은 대화를 기기의 DB 파일 `naver_line` 에 저장합니다[1]. 이 파일 이름과 위치를 알려 주는 공개 자료에는 앱 버전·Android 버전이 적혀 있지 않아서, 요즘 앱 버전에서도 같은지는 검체마다 파일을 열어 확인합니다[1].

라인을 다루는 공개 포렌식 도구 저장소는 드물고, ALEAPP 의 모듈 목록에도 라인 모듈이 보이지 않습니다[2][3]. 공개 도구의 자동 추출에 기대기 어렵다는 점을 전제로 분석을 계획합니다.

## 위치와 버전별 차이

Android 패키지 이름은 `jp.naver.line.android` 입니다. 라인 데이터가 있는 경로는 다음 두 곳입니다[1].

```
/data_mirror/data_ce/null/0/jp.naver.line.android/databases     (대화 DB 폴더, 루팅한 기기에서 본 경로)
storage/Android/data/jp.naver.line.android/storage/               (외부 저장소 쪽 폴더)
```

첫 줄은 루팅한 기기에서 본 경로입니다. Android 11 이후의 `/data_mirror` 는 앱 데이터 폴더(`/data/data`, `/data/user_de` 등)를 비춰 보이는 폴더로 알려져 있어서, 일반적으로 쓰는 `/data/data/jp.naver.line.android/databases/naver_line` 과 같은 파일을 가리킬 가능성이 높습니다. 두 경로의 관계를 판단할 때는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md)를 봅니다. 둘째 줄은 외부 저장소 쪽 경로로 사진 같은 파일이 있는 곳으로 보이지만, 안에 무엇이 들어 있는지는 공개된 자료가 없어 검체로 확인합니다. 외부 저장소 경로를 읽는 법은 [공용 저장 공간](../../01-foundations/storage/shared-storage.md)에서 다룹니다.

| 항목 | 알려진 것 | 검체에서 확인할 것 |
|---|---|---|
| 대화 DB | 파일 이름 `naver_line`, 확장자 없음 | 표 이름, 칸 이름, 시각 단위 |
| DB 위치 | 루팅 기기 경로 `/data_mirror/data_ce/null/0/…/databases` | 일반 경로와 같은 파일인지 |
| 외부 저장소 | `Android/data/jp.naver.line.android/storage/` 경로가 있음 | 안에 무엇이 있는지 |
| 암호화·백업 | | DB 암호화 여부, 클라우드 백업 흔적 위치 |
| Android 버전·One UI | | 버전·제조사별 차이 |

## 구조

`naver_line` 의 표 이름과 칸 이름은 공개된 자료가 없어서, 표 이름을 짐작해 쿼리를 짜지 말고 검체에서 직접 확인합니다. 파일이 SQLite 인지도 공개 자료로는 알 수 없으니, 아래 "직접 분석해 보기" 의 순서대로 머리글부터 확인합니다.

파일이 SQLite 로 확인되면 표 목록과 각 표의 칸을 뽑아 기록하고, 다음 기준으로 대화 기록 표를 찾아 갑니다.

1. 행 수가 가장 많고 시각처럼 보이는 정수 칸이 있는 표를 찾습니다.
2. 그 표에서 텍스트 칸에 알려진 대화 한두 건의 내용이 보이는지 확인합니다.
3. 대화방을 가리키는 것으로 보이는 칸이 다른 표의 키와 이어지는지 확인합니다.

이렇게 찾은 표 이름과 칸 뜻은 검체의 앱 버전과 함께 보고서에 적고, "라인은 이런 구조다" 가 아니라 "이 버전의 이 검체에서 이렇게 확인했다" 로 씁니다. 모르는 앱의 DB 를 읽어 가는 일반 절차는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `jp.naver.line.android` 폴더와 `naver_line` 파일이 있으면 그 기기에 라인이 설치돼 대화 DB 를 만든 적이 있다는 뜻입니다. 표 구조를 확인한 뒤라면 대화방·상대·시각의 흐름을 기록 그대로 정리할 수 있습니다.

**증명하지 못하는 것.** 표 구조를 확인하기 전에는 어떤 칸이 보낸 사람이고 어떤 칸이 본문인지 말할 수 없습니다. 기기에 남은 대화가 계정의 대화 전체인지도 알 수 없고, 다른 기기나 백업에서 옮겨 온 대화인지 이 기기에서 주고받은 대화인지도 파일만으로는 가를 근거가 없습니다.

## 시각 해석

시각 칸의 이름과 단위는 공개된 자료가 없어 검체에서 확인합니다. 오래 안 연 대화를 다시 열면 시각이 "1970/1/1" 로 보이는 문제가 있습니다[1]. 유닉스 시각 0 은 1970-01-01 00:00:00 UTC 이라서, 화면이나 도구에 이 날짜가 보이면 실제 시각이 아니라 시각 칸이 비었거나 0 인 행일 가능성을 먼저 의심합니다. 자릿수로 초와 밀리초를 가르는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md)을 보고, 현지 시각으로 바꿀 때는 [시간대와 시각 설정](../system-account/time-zone.md)을 함께 봅니다.

## 함정과 한계

- 확장자가 없어서 파일 이름으로 찾는 도구나 사람이 DB 를 놓치기 쉽습니다. `databases` 폴더의 모든 파일을 머리글로 가려 봅니다.
- 루팅 기기 경로(`/data_mirror/…`)와 일반 경로가 같은 파일인지 공식 설명이 없으므로, 경로를 보고서에 쓸 때는 실제로 파일을 얻은 경로를 그대로 적습니다.
- 공개 도구 지원이 적어서 자동 추출 결과가 비어 있을 수 있고, 결과가 없다는 사실만으로 대화가 없었다고 쓰지 않습니다.
- DB 가 암호화돼 있는지는 공개된 자료가 없습니다. 머리글이 SQLite 가 아니면 풀어 보려 하지 말고 "그대로는 읽을 수 없는 파일" 로 기록합니다.

## 직접 분석해 보기

### 헥스로 한 번

`naver_line` 의 맨 앞 16바이트를 봅니다. SQLite 명세에 따라 평문 SQLite 라면 다음처럼 보입니다(명세로 만든 예시).

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

이 글자가 보이면 SQLite 도구로 열고, 다른 값이 보이면 암호화됐거나 다른 형식인 파일로 적어 둡니다. 시각 칸을 찾은 뒤에는 "1970/1/1" 로 보이는 행의 값을 헥스로 봅니다. SQLite 레코드 머리에서 자료형 번호 8 은 정수 0 을 뜻하고, 값 바이트 없이 머리에만 0x08 이 적힙니다. 그래서 그 칸이 0 이면 레코드 머리에 `08`, NULL 이면 `00` 이 보이고, 둘을 구분해 두면 "시각이 없음" 과 "0 을 적음" 을 나눠 쓸 수 있습니다. 레코드 머리를 읽는 법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### 공개 도구로 한 번

`sqlite3` 명령행 도구로 사본을 열어 구조부터 뽑습니다.

```sql
.tables
.schema
SELECT name, (SELECT COUNT(*) FROM pragma_table_info(name)) AS columns
FROM sqlite_master WHERE type = 'table' ORDER BY name;
```

각 표의 행 수는 `SELECT COUNT(*) FROM 표이름;` 으로 셉니다. 이렇게 뽑은 표·칸 목록을 보존해 두면 같은 앱의 다른 버전 검체와 비교할 때 쓸 수 있습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/packages/index.md) | 라인 설치 여부와 앱 버전(구조를 적을 때 함께 기록) |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 대화 시각 무렵 라인 화면이 앞에 있었는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 알림의 제목과 시각. 표 구조를 모를 때 시각 기준을 맞추는 데 씁니다 |
| [미디어 저장소](../media/mediastore/index.md) | 외부 저장소 쪽 라인 폴더의 파일이 언제 색인됐는지 |

여러 메신저를 한 시간선에 모으는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 라인이 설치된 Android 이미지를 골라 다음 질문을 풀어 봅니다.

1. `databases` 폴더의 파일 가운데 머리글이 SQLite 인 것은 무엇인가요? `naver_line` 은 그중 하나인가요?
2. `naver_line` 의 표 목록을 뽑고, 행 수가 가장 많은 표 세 개와 각 표의 칸 이름을 적어 보세요.
3. 대화 기록으로 보이는 표에서 시각 칸을 골라 자릿수로 단위를 판단하고, 값이 0 인 행이 몇 개인지 세어 보세요.
4. 알림 기록의 라인 알림 시각과 DB 의 시각 칸 값을 한 건 이상 맞춰 볼 수 있나요?

## 참고 문헌

1. NumesSanguis/naver_line_restore_chat_root — README.md. https://raw.githubusercontent.com/NumesSanguis/naver_line_restore_chat_root/main/README.md
2. GitHub 저장소 검색 "naver_line android forensic"(결과 0건). https://api.github.com/search/repositories?q=naver_line+android+forensic
3. ALEAPP — scripts/artifacts 폴더 목록(GitHub API). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
