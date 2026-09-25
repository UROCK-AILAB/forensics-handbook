---
title: "대화 DB 구조와 암호화"
parent: "카카오톡"
grand_parent: "아티팩트 · 메신저"
nav_order: 920
---

# 대화 DB 구조와 암호화 (KakaoTalk.db)

`KakaoTalk.db` 는 대화 기록 표 `chat_logs` 와 대화방 표 `chat_rooms` 가 들어 있는 SQLite 파일이고, 파일 전체가 아니라 메시지 본문·첨부 정보·마지막 메시지 같은 일부 칸만 암호문으로 들어 있습니다.

## 무엇을 기록하나 · 왜 생기나

카카오톡은 주고받은 메시지를 한 행씩 `chat_logs` 에 쌓고, 대화방 정보를 `chat_rooms` 에 둡니다. 파일 위치와 함께 확보해야 하는 `-wal`·`-shm` 파일은 [저장 위치와 파일](paths-files.md)에서 다룹니다.

이 페이지의 표 구조는 공개 포렌식 도구 CARPE 의 스키마 파일과 코드, 암호화 칸 목록은 공개 스크립트 kakaodecrypt 의 코드에서 가져왔습니다. CARPE 스키마가 어느 앱 버전을 기준으로 만든 것인지는 확인하지 못했고, 앱 버전이 바뀌면 칸이 늘거나 바뀔 수 있습니다.

## 구조

### chat_logs

CARPE 스키마에는 칸이 12개 있고, CARPE 코드도 한 행에서 `row[0]` 부터 `row[11]` 까지 그대로 옮기므로 칸 수가 맞습니다. 칸 순서와 뜻은 다음과 같습니다. 뜻은 대부분 칸 이름으로 짐작한 것이고, 공식 설명은 없습니다.

| 순서 | 칸 | 뜻 | 암호화 |
|---|---|---|---|
| 0 | `_id` | 확인 못 함 | |
| 1 | `id` | 확인 못 함 | |
| 2 | `type` | 메시지 종류 번호로 보이지만 값의 뜻은 확인 못 함 | |
| 3 | `chat_id` | `chat_rooms` 의 대화방과 연결하는 값 | |
| 4 | `user_id` | 보낸 사람 ID | |
| 5 | `message` | 메시지 본문 | 암호화 |
| 6 | `attachment` | 첨부 정보 | 암호화 |
| 7 | `created_at` | 시각 | |
| 8 | `deleted_at` | 시각. 어떤 경우에 채워지는지는 확인 못 함 | |
| 9 | `client_message_id` | 확인 못 함 | |
| 10 | `prev_id` | 확인 못 함 | |
| 11 | `v` | JSON 문자열. 안에 `"enc"` 값이 들어 있음 | |

`attachment` 칸을 받은 파일 쪽에서 어떻게 보는지는 [받은 파일](received-files.md)에서 다룹니다.

### chat_rooms

CARPE 는 `chat_rooms` 에서 한 행에 29칸(`row[0]`~`row[28]`)을 옮깁니다. 칸 이름 목록은 이번 조사에서 열지 않았고, 그 가운데 `last_message` 칸이 암호화 대상이라는 점만 kakaodecrypt 코드로 확인했습니다.

## 암호화

`KakaoTalk.db` 는 보통 SQLite 파일로 열리고, 암호화된 칸의 값만 Base64 문자열로 들어 있습니다. 파일 전체를 잠그는 방식이 아니라서 표 구조와 암호화되지 않은 칸(`chat_id`, `user_id`, `created_at` 등)은 그대로 읽을 수 있지만, 본문과 첨부 정보는 풀기 전에는 읽을 수 없습니다.

| 표 | 암호화된 칸 (공개 도구 기준) |
|---|---|
| `chat_logs` | `message`, `attachment` |
| `chat_rooms` | `last_message` |

kakaodecrypt 코드로 보면 방식은 AES-CBC 이고, 키는 사용자 ID 와 "enc" 번호에 따라 달라집니다. 이 핸드북은 키를 만드는 절차를 다루지 않습니다. `chat_logs` 에는 `enc` 칸이 따로 없어서 도구는 `v` 칸의 JSON 안에 있는 `"enc"` 값을 쓰고, 각 행의 `user_id` 칸 값을 사용자 ID 로 씁니다. 암호화된 값이 없는 행은 건너뛰도록 2024-04-23 커밋("Handle rows without encrypted data")에서 고쳤고, 어느 표의 어떤 행이 이런 경우인지는 커밋 제목만으로는 알 수 없습니다.

도구가 모르는 enc 번호를 만나면 "Unsupported encoding type" 오류를 냅니다. 앱이 새 enc 번호를 쓰기 시작하면 예전 도구로는 그 행을 읽지 못한다는 뜻이고, kakaodecrypt 의 마지막 커밋이 2024-04-23 이라 요즘 앱 버전에서 그대로 통하는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것.** `chat_logs` 에 행이 있으면 그 `chat_id` 대화방에 그 `user_id` 로 적힌 메시지 기록이 DB 에 저장돼 있었다는 뜻입니다. 본문을 풀지 못해도 대화방별 메시지 수, 보낸 사람 ID, 시각 칸의 흐름은 읽을 수 있어서 연락 상대와 대화 시간대를 정리할 수 있습니다.

**증명하지 못하는 것.** 본문을 풀기 전에는 무슨 말을 주고받았는지 알 수 없습니다. `user_id` 가 보낸 사람이라는 해석은 칸 이름에서 나온 것이고, `type` 값의 뜻과 `deleted_at` 이 채워지는 조건도 확인하지 못했으므로, `deleted_at` 에 값이 있다는 이유만으로 "사용자가 메시지를 지웠다" 고 쓰지 않습니다.

## 시각 해석

`chat_logs` 에는 `created_at` 과 `deleted_at` 두 시각 칸이 있습니다. 이 값이 유닉스 초인지 밀리초인지는 이번 출처로 확인하지 못했고, kakaodecrypt 예시도 `created_at` 을 정렬 기준으로만 씁니다. UTC 인지 현지 시각인지도 확인하지 못했습니다. 값의 자릿수로 단위를 가늠하는 방법은 [시각 값](../../../01-foundations/value-decoding/time-values.md)을 보고, 알림 기록처럼 시각 기준이 알려진 다른 기록과 한 건 이상 맞춰 본 뒤 보고서에 씁니다.

## 함정과 한계

kakaodecrypt 는 원래 표를 건드리지 않고 `chat_logs_dec` 처럼 이름 끝에 `_dec` 가 붙은 표를 DB 파일 안에 새로 만듭니다. CARPE 도 내부에서 `chat_logs_dec`, `chat_rooms_dec` 표를 만들어 읽습니다. 도구가 DB 파일에 표를 더하므로 원본이 아닌 사본에서 작업하고, 작업 전후 해시를 기록합니다.

사본을 열 때는 `-wal`·`-shm` 을 같은 폴더에 함께 두고, 그래야 하는 까닭은 [저장 위치와 파일](paths-files.md)에서 설명합니다.

칸 목록은 CARPE 스키마 한 가지를 기준으로 한 것이라, 실제 파일의 표 구조를 먼저 확인하고 칸 수나 이름이 다르면 그대로 기록해 둡니다.

## 직접 분석해 보기

**헥스로 한 번.** 사본을 헥스 편집기로 열어 파일이 SQLite 헤더로 시작하는지 봅니다. 헤더 구조는 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md)에서 설명합니다. 파일 전체가 암호화돼 있지 않으므로 헤더가 그대로 보이고, `chat_logs` 가 저장된 페이지를 따라가면 `message` 칸 자리에 읽을 수 있는 문장 대신 Base64 문자열이 들어 있는 모습을 볼 수 있습니다.

**공개 도구로 한 번.** SQLite 뷰어로 사본을 열어 `chat_logs` 의 칸 수와 이름이 위 표와 같은지, `v` 칸 JSON 에 `"enc"` 값이 있는지 확인합니다. 암호화된 칸은 kakaodecrypt 나 CARPE 로 `_dec` 표를 만들어 읽을 수 있고, 친구 쪽 표를 풀 때 필요한 기기 주인의 사용자 ID 는 [계정과 친구 목록](account-friends.md)에서 다룹니다. 도구 결과는 원래 표의 행 수와 맞춰 보고, 오류로 건너뛴 행이 있으면 enc 번호와 함께 적어 둡니다. 도구 결과를 검증하는 방법은 [도구 검증](../../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

- [계정과 친구 목록 (Account·Friends)](account-friends.md) — `user_id` 를 친구 목록의 이름과 맞춰 봅니다.
- [알림 기록 (Notification History)](../../app-usage/notification-history.md) — 메시지 알림이 남았다면 시각과 보낸 사람을 DB 행과 맞춰 봅니다.
- [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md) — 메시지 시각에 앱이 화면에 떠 있었는지 봅니다.
- [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) — 지운 행을 SQLite 빈 공간과 `-wal` 에서 찾는 방법입니다.
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 단위를 확인한 시각 칸을 다른 기록과 한 줄로 늘어놓을 때 봅니다.

## 실습

카카오톡이 설치된 공개 검체나 직접 만든 시험 기기 이미지로 다음 질문을 풀어 봅니다.

1. `chat_logs` 의 칸 수와 이름이 위 표와 같습니까? 다르다면 무엇이 늘거나 바뀌었습니까?
2. `v` 칸 JSON 의 `"enc"` 값은 어떤 번호들이 나옵니까? `"enc"` 가 없는 행도 있습니까?
3. 시험 기기에서 메시지를 보낸 시각을 적어 두고, 그 행의 `created_at` 값과 비교해 단위와 시간대를 밝힐 수 있습니까?
4. `deleted_at` 에 값이 있는 행이 있다면, 시험 기기에서 어떤 동작을 했을 때 생겼습니까?

## 참고 문헌

1. jiru/kakaodecrypt — README.md. https://github.com/jiru/kakaodecrypt
2. jiru/kakaodecrypt — kakaodecrypt.py. https://github.com/jiru/kakaodecrypt/blob/HEAD/kakaodecrypt.py
3. jiru/kakaodecrypt — 커밋 기록(최근 커밋 2024-04-23 "Handle rows without encrypted data"). https://github.com/jiru/kakaodecrypt/commits
4. dfrc-korea/carpe — modules/kakaotalk_mobile_decrypt_connector.py. https://github.com/dfrc-korea/carpe/blob/HEAD/modules/kakaotalk_mobile_decrypt_connector.py
5. dfrc-korea/carpe — modules/schema/kakaotalk_mobile/lv1_app_kakaotalk_mobile_chatlogs.yaml. https://github.com/dfrc-korea/carpe/blob/HEAD/modules/schema/kakaotalk_mobile/lv1_app_kakaotalk_mobile_chatlogs.yaml
