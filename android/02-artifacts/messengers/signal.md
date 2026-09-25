---
title: "시그널"
parent: "아티팩트 · 메신저"
nav_order: 980
---

# 시그널 (Signal)

시그널 Android 앱은 대화를 SQLite 파일 `signal.db` 에 저장하지만 SQLCipher 로 파일 전체를 암호화하고, 그 비밀값을 Android KeyStore 로 봉인해 두어서 파일만 복사해서는 내용을 읽을 수 없습니다.

## 무엇을 기록하나 · 왜 생기나

시그널은 대화에 딸린 정보를 `signal.db` 한 파일의 여러 표에 나눠 저장합니다. 앱의 공개 소스(signalapp/Signal-Android)에서 이 DB 를 다루는 코드 클래스는 `MessageTable`, `ThreadTable`, `RecipientTable`, `AttachmentTable`, `CallTable`, `GroupTable`, `ReactionTable`, `MentionTable`, `DraftTable`, `IdentityTable`, `SessionTable` 등 40여 개이고, 클래스 이름으로 보면 메시지·대화방·상대·첨부·통화·그룹·반응·멘션·임시 저장 글·상대 신원 정보가 각각 표로 나뉩니다. 이 페이지의 내용은 모두 2026-09 조사 시점의 소스 기준이고, 앱이 자주 바뀌므로 검체의 앱 버전을 함께 적습니다.

이 페이지는 암호화된 DB 가 증거로서 무엇을 말해 주고 무엇을 말해 주지 못하는지를 다루고, 암호를 풀거나 보안 장치를 넘는 절차는 다루지 않습니다.

## 위치와 버전별 차이

소스의 코드 패키지 경로는 `org.thoughtcrime.securesms` 입니다. Play 스토어의 패키지 이름도 같다고 알려져 있지만 이번 조사에서 매니페스트로 확인하지는 않았고, 검체에서는 [설치된 앱](../app-usage/packages/index.md) 기록으로 실제 패키지 이름을 먼저 확인합니다. 메인 DB 파일 이름은 `signal.db` 이고, 전체 경로는 다음 꼴로 짐작하지만 확인하지 못했습니다.

```
/data/data/org.thoughtcrime.securesms/databases/signal.db   (추정)
```

| 항목 | 조사 시점에 확인한 것 | 확인 못 한 것 |
|---|---|---|
| 메인 DB | `signal.db`, SQLCipher 로 파일 전체 암호화 | 전체 경로 |
| 비밀값 보관 | Android KeyStore 로 봉인해 설정 저장소에 둠 | 설정 저장소 파일의 위치와 키 이름 |
| 다른 DB | 예전 표 `key_value`, `megaphone`, `job_spec`, `constraint_spec`, `dependency_spec` 를 지우는 코드가 있음 | 이 정보가 옮겨 간 곳, 별도 DB 파일이 있는지 |
| 첨부 파일 | | 저장 위치 |
| 백업 | | 암호화 백업 파일의 위치와 형식 |
| One UI | | 삼성 기기에서의 차이 |

## 구조

### 암호화

소스는 DB 를 열 때 `net.zetetic.database.sqlcipher.SQLiteDatabase` 를 씁니다. SQLCipher 는 SQLite 파일을 통째로 암호화하는 라이브러리라서, 파일을 얻어도 일반 SQLite 도구로는 열리지 않습니다.

DB 비밀값은 처음 만들 때 32바이트 난수로 만들고, `KeyStoreHelper.seal` 로 봉인한 상태로 평문 설정 저장소(`PlainTextKeyValueStore`)에 둡니다. 예전 방식처럼 봉인하지 않은 비밀값이 남아 있으면, 소스는 그 값을 봉인해 다시 저장하고 봉인하지 않은 값은 지웁니다. Android KeyStore 키는 기기 밖으로 꺼낼 수 없게 만들어져 있어서, 이 핸드북은 이 구조를 "파일만 복사해서는 열 수 없다" 는 해석까지만 씁니다. 기기 저장 공간 자체의 암호화는 이것과 다른 층이고, [저장 공간 암호화](../../01-foundations/storage/encryption/index.md)에서 다룹니다.

### message 표

메시지 표 이름은 `message` 이고, 소스의 `MessageTable.kt` 로 본 주요 칸은 다음과 같습니다. 뜻 칸은 칸 이름으로 짐작한 것입니다.

| 칸 | 뜻(짐작) |
|---|---|
| `_id`, `thread_id` | 메시지 번호, 대화방 번호 |
| `from_recipient_id`, `to_recipient_id`, `from_device_id` | 보낸 상대, 받는 상대, 보낸 기기 |
| `date_sent`, `date_received`, `date_server`, `receipt_timestamp`, `notified_timestamp`, `scheduled_date` | 시각 |
| `body` | 본문 |
| `type` | 메시지 종류 |
| `read` | 읽음 여부 |
| `view_once` | 한 번 보기 메시지 |
| `expires_in`, `expire_started` | 사라지는 메시지 설정 |
| `remote_deleted`, `deleted_by` | 상대가 "모두에게서 삭제" 한 메시지 |
| `starred` | 별표 표시 |

이 표는 암호화된 파일 안에 있어서 칸 목록은 DB 를 연 상태에서만 바로 쓸 수 있지만, 이 앱이 메시지마다 어떤 정보를 기록하는지 가늠하는 데는 쓸 수 있습니다.

## 증거로서 의미

**증명하는 것.** `org.thoughtcrime.securesms` 폴더와 `signal.db` 가 있으면 그 기기에 시그널이 설치돼 DB 를 만든 적이 있다는 뜻입니다. 파일 크기와 파일 시스템의 수정 시각은 암호화와 상관없이 읽을 수 있어서, DB 가 대략 언제까지 바뀌었는지는 볼 수 있습니다. 파일 시스템 시각이 무엇이 바뀔 때 바뀌는지는 [파일 시스템](../../01-foundations/storage/filesystems/index.md)에서 다룹니다.

**증명하지 못하는 것.** DB 를 열지 못하면 누구와 무슨 말을 몇 건 주고받았는지 말할 수 없습니다. 파일 크기가 크다고 대화가 많았다고 쓸 수도 없는데, 한 파일 안에 메시지 말고도 여러 종류의 표가 들어 있기 때문입니다. `remote_deleted`, `expires_in`, `view_once` 는 칸 이름으로 짐작한 뜻이라서, DB 를 열었더라도 알려진 메시지 몇 건으로 값의 뜻을 확인하기 전에는 "상대가 지웠다", "사라지는 메시지였다" 고 쓰지 않습니다.

## 시각 해석

`message` 표의 날짜 칸(`date_sent`, `date_received`, `date_server` 등)은 유닉스 밀리초이고, 소스는 받은 시각 등을 적을 때 `System.currentTimeMillis()` 값을 씁니다. 이 값은 1970-01-01 00:00:00 UTC 부터 센 밀리초라서 UTC 기준이고, 현지 시각으로 바꿀 때는 [시간대와 시각 설정](../system-account/time-zone.md)을 봅니다. 칸 이름으로 보면 `date_sent` 는 보낸 쪽 시각, `date_received` 는 이 기기가 받은 시각, `date_server` 는 서버 시각이지만, 각 칸이 정확히 언제 채워지는지는 확인하지 못했습니다. 변환은 [시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

- 파일을 얻었다고 대화를 얻은 것이 아닙니다. 확보 계획을 세울 때 "`signal.db` 확보" 와 "대화 내용 확보" 를 따로 적습니다.
- 조사 시점의 ALEAPP 모듈 목록에서 시그널 모듈은 찾지 못했습니다(목록을 요약으로 읽어서 빠졌을 가능성은 남습니다).
- 소스에는 예전 표를 지우는 코드가 있어서, 앱 버전에 따라 설정·작업 목록 같은 정보가 다른 파일로 옮겨 갔을 수 있습니다. `databases` 폴더의 파일 목록을 통째로 기록해 둡니다.
- 사라지는 메시지와 "모두에게서 삭제" 가 있는 앱이라서, DB 에 없는 메시지를 사용자가 지웠다고 단정할 수 없습니다. 이런 해석은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md)에서 다른 흔적과 함께 판단합니다.

## 직접 분석해 보기

### 헥스로 한 번

`signal.db` 사본의 맨 앞 16바이트를 봅니다. 평문 SQLite 라면 SQLite 명세에 따라 다음처럼 보입니다(명세로 만든 예시).

```
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

`signal.db` 는 파일 전체가 암호화되므로 이 글자가 보이지 않는 것이 소스와 맞는 모습입니다. 반대로 이 글자가 보이면 파일 이름만 같은 다른 파일이거나 조사 시점과 다른 방식의 앱일 수 있어서, 앱 버전과 경로를 다시 확인합니다. 머리글 구조는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### 공개 도구로 한 번

`sqlite3` 로 사본을 열어 `.tables` 를 실행하면, 암호화된 파일은 표 목록 대신 데이터베이스가 아니라는 오류를 냅니다. 이 오류 메시지를 그대로 기록해 두면 "도구로 열어 보았고 열리지 않았다" 는 사실을 보고서에 남길 수 있습니다. 대화 내용 대신 볼 수 있는 흔적은 아래 교차 검증의 아티팩트에서 찾습니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [설치된 앱](../app-usage/packages/index.md) | 설치·업데이트 시각, 앱 버전 |
| [앱 사용 기록](../app-usage/usagestats/index.md) | 시그널 화면을 언제 얼마나 썼는지 |
| [알림 기록](../app-usage/notification-history.md) | 메시지 알림이 온 시각 |
| [데이터 사용량](../network/netstats.md) | 그 시간대에 앱이 주고받은 데이터 양 |
| [배터리 사용 기록](../app-usage/batterystats.md) | 앱이 동작한 시간대 |
| [최근 앱 화면](../app-usage/recents-snapshots.md) | 마지막으로 본 화면이 남았는지 |

DB 를 열 수 없는 메신저에서 연락 흐름을 재구성하는 방법은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 시그널이 설치된 Android 이미지를 골라 다음 질문을 풀어 봅니다.

1. `databases` 폴더에 어떤 파일들이 있고, 각 파일의 머리글이 평문 SQLite 인가요?
2. `signal.db` 의 파일 시스템 수정 시각과, 앱 사용 기록에서 시그널을 마지막으로 쓴 시각은 얼마나 차이 나나요?
3. 알림 기록에서 시그널 알림이 몇 건 보이고, 제목·본문 칸에 무엇이 남아 있나요?
4. 대화 내용을 열지 못한 상태에서 보고서에 쓸 수 있는 문장을 세 개 적어 보세요.

## 참고 문헌

1. signalapp/Signal-Android — SignalDatabase.kt. https://raw.githubusercontent.com/signalapp/Signal-Android/main/app/src/main/java/org/thoughtcrime/securesms/database/SignalDatabase.kt
2. signalapp/Signal-Android — MessageTable.kt. https://raw.githubusercontent.com/signalapp/Signal-Android/main/app/src/main/java/org/thoughtcrime/securesms/database/MessageTable.kt
3. signalapp/Signal-Android — DatabaseSecretProvider.java. https://raw.githubusercontent.com/signalapp/Signal-Android/main/app/src/main/java/org/thoughtcrime/securesms/crypto/DatabaseSecretProvider.java
4. ALEAPP — scripts/artifacts 폴더 목록(GitHub API). https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
