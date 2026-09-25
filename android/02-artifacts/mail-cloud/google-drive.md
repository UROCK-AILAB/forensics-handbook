---
title: "구글 드라이브"
parent: "아티팩트 · 메일·클라우드"
nav_order: 1100
---

# 구글 드라이브 (Google Drive)

## 한 줄 요약

공개 도구 ALEAPP 는 구글 드라이브 (Google Drive) 앱의 흔적으로 `DocList.db` 의 `EntryView` 를 읽어 파일 이름·주인·생성·수정·열람 시각·MD5 를 보여 주지만 [2], 시험 이미지 10개가 모두 0행이었고 모듈도 2020년 이후 갱신되지 않아서 [2] 요즘 앱에서 이 기록이 채워지는지는 검체마다 직접 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

드라이브 앱은 사용자의 클라우드 저장 공간에 있는 파일 목록을 기기에 받아 두고 보여 줍니다. ALEAPP 의 DocList 모듈이 읽는 `EntryView` 에는 파일마다 제목, 주인, 마지막으로 고친 계정, 종류, 공유 주소, 크기, MD5 와 세 가지 시각이 들어 있습니다 [2]. 목록에 있는 파일이 기기에 내려받아져 있는지와는 다른 이야기라서, 이 기록은 "그 계정의 드라이브에 이런 파일이 있었다" 를 보여 주는 기록으로 읽습니다.

요즘 드라이브 앱의 캐시·오프라인 파일 위치와 업로드 기록 표는 이번에 연 자료에서 확인하지 못했습니다.

Android 기기 백업은 드라이브 앱이 남기는 흔적과는 다른 기록이라서 [구글 백업 (Google Backup)](google-backup.md) 페이지에서 따로 다룹니다.

## 위치와 버전별 차이

ALEAPP 가 구글 드라이브 모듈로 찾는 경로 패턴은 아래 하나입니다 [2]. 패턴 끝의 `*` 는 `-wal` 같은 딸린 파일까지 함께 찾으려는 것입니다.

```
*/com.google.android.apps.docs/databases/DocList.db*
```

앱 데이터 폴더의 짜임은 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md), 다른 앱이나 셸이 이 폴더를 읽을 수 있는지는 [앱 샌드박스와 권한](../../01-foundations/security-model/sandbox-permissions.md) 페이지에서 다룹니다.

버전별 차이는 아래처럼 정리할 수 있습니다 [2].

| 항목 | 내용 |
|---|---|
| 시험 이미지 | 10개, Android 10~16, 삼성 기기 포함 |
| 결과 | 10개 모두 0행 |
| 모듈 마지막 갱신 | 2020-12-21 |
| One UI 에 따른 차이 | 확인한 자료 없음 |

시험 이미지가 모두 0행이라는 것은 최근 앱에서 이 표가 비어 있거나 다른 곳으로 옮겨졌을 가능성을 뜻하지만, 어느 쪽인지는 확인하지 못했습니다.

## 구조

`DocList.db` 는 SQLite 파일이고, 파일 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 페이지에서 다룹니다. ALEAPP 가 읽는 뷰는 `EntryView` 이고 칸은 아래와 같습니다 [2].

| 칸 | 담긴 것 |
|---|---|
| `title` | 파일 이름 |
| `owner` | 주인 |
| `creationTime` | 만든 시각 |
| `lastModifiedTime` | 마지막으로 고친 시각 |
| `lastOpenedTime` | 마지막으로 연 시각 |
| `lastModifierAccountAlias`, `lastModifierAccountName` | 마지막으로 고친 계정 |
| `kind` | 종류 |
| `shareableUri`, `htmlUri` | 공유·웹 주소 |
| `md5Checksum` | MD5 |
| `size` | 크기 |

`EntryView` 는 뷰라서 실제 값은 다른 표에 있습니다. 뷰가 어느 표를 묶는지는 확인하지 못했고, 검체에서는 `sqlite_master` 의 뷰 정의를 읽어 원래 표를 찾습니다.

## 증거로서 의미

**증명하는 것**

`EntryView` 에 행이 있으면 그 이름과 크기의 파일이 기기에 로그인한 계정의 드라이브 목록에 있었다는 기록입니다. `owner` 와 `lastModifierAccountName` 을 보면 공유받은 파일인지, 누가 마지막으로 고쳤는지를 가리는 데 참고할 수 있습니다. `md5Checksum` 은 기기 안이나 다른 매체에서 찾은 파일의 MD5 와 맞춰 보는 데 쓸 수 있어서 [2], 같은 내용의 파일이 드라이브에 있었는지 따질 때 도움이 됩니다.

**증명하지 못하는 것**

목록에 있다는 것만으로 이 기기에서 그 파일을 올렸거나 내려받았다고 할 수 없고, 다른 기기나 웹에서 올린 파일이 동기화로 보였을 수도 있습니다. `lastOpenedTime` 도 어느 기기에서 연 시각인지는 칸 이름만으로 알 수 없습니다. MD5 가 같으면 내용이 같은 파일이라는 뜻이지만, 기기 안의 그 파일이 드라이브에서 왔다는 경로까지 보여 주지는 않습니다.

## 시각 해석

`creationTime`·`lastModifiedTime`·`lastOpenedTime` 은 유닉스 밀리초이고, 값이 0 이면 비어 있는 것으로 봅니다 [2]. 유닉스 시각은 UTC 기준이라 보고서에 현지 시각을 쓸 때는 기기 시간대를 따로 확인합니다. 세 시각이 기기 시계로 찍은 값인지 서버 시각을 받아 온 값인지는 확인하지 못했습니다. 값을 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md), 시간대 확인은 [시간대와 시각 설정 (Time Zone)](../system-account/time-zone.md) 페이지에 있습니다.

## 함정과 한계

첫째, ALEAPP 가 0행을 냈다고 드라이브를 쓰지 않았다고 결론 내리면 안 됩니다. 시험 이미지 전부가 0행이었으니 [2], 도구 결과가 비어 있으면 파일 자체와 `-wal` 을 직접 열어 보고, 앱 데이터 폴더의 다른 DB 에 목록이 옮겨 갔는지 찾습니다.

둘째, 모듈이 오래되어 [2] 칸 이름이 바뀌었을 수 있습니다. 도구가 오류 없이 빈 결과를 내는 경우도 있으니 뷰 정의를 먼저 봅니다.

셋째, 파일을 지우면 목록에서 어떻게 빠지는지, 휴지통에 있는 파일이 따로 표시되는지는 확인하지 못했습니다. SQLite 에서 지운 행이 남을 수 있는 자리는 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md) 페이지에서 다룹니다.

넷째, 드라이브에 있는 파일 전체와 변경 기록은 기기보다 계정 쪽 데이터에서 더 잘 보일 수 있고, 계정 데이터를 받는 절차는 [클라우드 데이터 (Google Takeout 등)](../../03-techniques/acquisition/cloud-data.md) 페이지에서 다룹니다.

## 직접 분석해 보기

### 값으로 한 번

아래는 SQLite 정수 저장 규칙으로 만든 예시이고, 실제 검체에서 나온 값이 아닙니다. `lastModifiedTime` 이 1767261600000 이면 16진수로 `0x019B78FFF900` 이고, SQLite 는 이 크기의 정수를 6바이트 빅 엔디언으로 저장합니다. 1000 으로 나누면 유닉스 초 1767261600 이 되고, UTC 로 2026-01-01 10:00:00, 한국 시각으로 같은 날 19:00 입니다.

```
레코드 본문 속 6바이트   01 9B 78 FF F9 00
정수                     1767261600000 (밀리초)
/ 1000                   1767261600 (초)
UTC                      2026-01-01 10:00:00
한국 시각(UTC+9)         2026-01-01 19:00:00
```

DB 사본에서는 아래처럼 뷰 정의를 먼저 보고 행을 뽑습니다. 질의는 위 구조 표로 만든 예시입니다.

```sql
SELECT sql FROM sqlite_master WHERE name = 'EntryView';

SELECT title, owner, kind, size, md5Checksum,
       datetime(NULLIF(creationTime, 0) / 1000, 'unixepoch')     AS created_utc,
       datetime(NULLIF(lastModifiedTime, 0) / 1000, 'unixepoch') AS modified_utc,
       datetime(NULLIF(lastOpenedTime, 0) / 1000, 'unixepoch')   AS opened_utc,
       lastModifierAccountName
FROM EntryView
ORDER BY lastModifiedTime;
```

### 공개 도구로 한 번

ALEAPP 의 DocList 모듈이 `EntryView` 를 읽어 표로 만들어 줍니다 [2]. 모듈 목록에서 이 모듈이 있다는 것은 따로 확인했습니다 [1]. 결과가 나오면 몇 행을 골라 위 방식으로 시각을 직접 풀어 맞춰 보고, 결과가 비면 앞의 함정 절에 적은 대로 원본을 직접 엽니다. 도구 결과를 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다.

## 교차 검증

| 함께 볼 기록 | 맞춰 볼 것 |
|---|---|
| [계정 (Accounts)](../system-account/accounts/index.md) | 드라이브에 로그인한 구글 계정과 계정을 넣고 뺀 기록 |
| [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) | 계정 동기화에 관한 설정 키 |
| [앱 사용 기록 (usagestats)](../app-usage/usagestats/index.md) | 파일 시각 앞뒤로 드라이브 앱을 앞에 띄운 기록 |
| [데이터 사용량 (netstats)](../network/netstats.md) | 그 시간대에 앱이 주고받은 데이터 양 |
| [미디어 저장소 (MediaStore)](../media/mediastore/index.md) | 같은 이름이나 크기의 파일이 기기에 있는지 |

관찰 기기의 settings global 에는 `master_sync_status`, `synced_account_name` 키가, settings system 에는 `sync_disabled_accounts_with_hash` 키가 있었습니다. 이름으로 보아 계정 동기화와 관련된 키로 보이지만 값의 뜻은 확인하지 못했고, 설정 값을 읽는 법은 [설정 값 (Settings Global·Secure·System)](../system-account/settings.md) 페이지에서 다룹니다. 클라우드로 자료를 내보냈는지 따지는 흐름은 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에 있습니다.

## 실습

NIST CFReDS 같은 공개 안드로이드 검체에 `com.google.android.apps.docs` 앱 데이터가 들어 있으면 아래 질문을 풀어 봅니다.

1. `DocList.db` 가 있습니까? 있다면 `EntryView` 의 뷰 정의는 어떤 표를 묶습니까?
2. `EntryView` 가 비어 있다면 `-wal` 파일이나 같은 폴더의 다른 DB 에 파일 이름이 남아 있습니까?
3. `owner` 가 기기 계정과 다른 행은 몇 개이고, 그 행들의 `lastModifierAccountName` 은 누구입니까?
4. `md5Checksum` 하나를 골라, 기기의 공용 저장 공간에 같은 MD5 의 파일이 있는지 찾아봅니다.

## 참고 문헌

1. ALEAPP 저장소 파일 목록 (GitHub API, git trees, recursive) — https://api.github.com/repos/abrignoni/ALEAPP/git/trees/main?recursive=1
2. ALEAPP — scripts/artifacts/DocList.py — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/DocList.py
