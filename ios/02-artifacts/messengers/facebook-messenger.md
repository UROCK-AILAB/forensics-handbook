---
title: "페이스북 메신저"
parent: "아티팩트 · 메신저"
nav_order: 880
---

# 페이스북 메신저 (Messenger)

메신저 대화함 DB 는 메신저 앱의 앱 그룹과 페이스북 앱의 앱 그룹 두 곳에 있을 수 있고, 메신저 앱이 없는 기기에도 페이스북 앱 쪽 사본만 남아 있을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

메신저는 대화 목록·메시지·연락처·첨부 정보를 대화함 (msys) SQLite DB 에 저장합니다 [1]. 페이스북 앱 쪽에도 같은 형식의 대화함 사본이 있어서, 한 계정의 대화가 기기 안 두 DB 에 함께 남을 수 있습니다 [1]. 종단간 암호화 대화는 별도 표(`client_messages` 등)에 들어가고, 그 첨부는 별도 폴더에 저장됩니다 [1].

## 위치와 버전별 차이

아래 경로는 전체 파일 시스템 추출 기준입니다 [1]. 두 앱 그룹 ID 는 컨테이너 메타데이터에 적힌 값입니다 [1]. 앱 그룹 개념은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 을 봅니다.

| 앱 그룹 | 경로 | 내용 |
|---|---|---|
| `group.com.facebook.Messenger` | `lightspeed-userDatabases/*.db` | 메신저 앱의 대화함 DB [1] |
| `group.com.facebook.Facebook` | `cask/<계정 ID>/FBMessagingMailboxCaskStore/<n>/fb-msys-<계정 ID>.db` | 페이스북 앱 쪽 대화함 사본 [1] |
| 검체에서 확인 | `lightspeed-TAMStorage/media_bank/AdvancedCrypto/*/persistent/*.jpg` | 종단간 암호화 대화의 첨부 [1] |

iLEAPP 시험 표본 25개 가운데 4개는 페이스북 앱 쪽 사본만 있었고, 그중 2개는 메신저 앱 자체가 없었습니다 [1]. 메신저 앱이 설치돼 있지 않다고 해서 메신저 대화가 기기에 없다고 판단하지 않습니다.

로컬 백업에서는 앱 그룹 공유 폴더가 `AppDomainGroup-` 으로 시작하는 도메인으로 따로 나뉩니다. 메신저 앱의 번들 ID 와 백업 도메인 이름, 두 앱 그룹이 백업에 들어가는지는 공개 자료가 없어 검체에서 확인합니다([로컬 백업](../../01-foundations/backups/local-backup/index.md)).

| 항목 | 확인된 범위 |
|---|---|
| 시험 표본 iOS | 12.4 ~ 26.6 [1] |
| 시험 표본 메신저 앱 | 405.0 ~ 570.0.0 [1] |
| 행이 나온 표본 | iOS 15.3.1, 16.5, 17.x, 18.x, 26.5.2 일부 [1] |
| 버전별 표 차이 | 공개 자료 없음 |

## 구조

대화함 DB 의 주요 표와 뷰는 다음과 같습니다 [1].

| 표·뷰 | 주요 칸과 쓰임 |
|---|---|
| `thread_messages`(뷰) | `timestamp_ms` |
| `threads` | `last_activity_timestamp_ms` |
| `thread_participant_detail`(뷰) | — |
| `contacts` | — |
| `attachments`, `attachment_items` | — |
| `_user_info` | — |
| `secure_messages` | 옛 비밀 대화. `timestamp_ms` |
| `client_messages` | 종단간 암호화 대화 메시지. `display_ts_ms`, `authoritative_ts_ms`, `thread_pk`, `sender_contact_pk`, `message_content_type` |
| `client_threads` | `transport_key` |
| `client_contacts` | — |
| `fb_transport_contacts` | `client_contact_pk`, `server_contact_id` |
| `client_attachments` | `filename` |
| `client_attachment_store_keys` | `persisted_path` |
| `mi_act_mapping_table` | — |

"—" 는 칸과 쓰임을 설명한 공개 자료가 없는 표입니다.

`client_messages` 의 행은 `client_threads.transport_key` 가 `AdvancedCrypto` 인 종단간 암호화 대화였고, 시험 표본에서는 이 표의 본문이 평문으로 저장돼 있었습니다 [1]. 저장 형식은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 를 봅니다.

`sender_contact_pk` 는 페이스북 사용자 ID 가 아니라 이 DB 안에서만 쓰는 연락처 키라서, `fb_transport_contacts` 로 사용자 ID(`server_contact_id`)를 찾아 바꿉니다 [1]. 시험 표본 9개 가운데 5개는 두 값이 같았고 4개는 달랐습니다 [1].

종단간 암호화 대화의 첨부 파일 이름은 `att.` 또는 `prev.` 에 저장한 바이트의 SHA-256 해시(base64url)와 확장자를 붙인 것이라서, 보낸 사람이 붙인 원래 파일 이름이 아닙니다 [1]. `client_attachments.filename` 은 시험 표본의 모든 행에서 비어 있었습니다 [1].

`secure_messages` 는 표본 16개 가운데 15개 DB 에 있었지만 행은 하나도 없었고, 값은 암호화된 채로 저장됩니다 [1].

## 증거로서 의미

**증명하는 것.** 대화함 DB 의 메시지 행은 이 기기의 메신저 또는 페이스북 앱 데이터에 그 메시지가 남아 있다는 기록입니다 [1]. 페이스북 앱 쪽 사본에서 나온 행이라면 경로의 계정 ID 로 어느 계정의 대화함인지 알 수 있습니다 [1]. 종단간 암호화 대화도 시험 표본에서는 `client_messages` 에 본문이 평문으로 남아 있었으므로, 같은 조건이면 이 기기에서 본문을 읽을 수 있습니다 [1].

**증명하지 못하는 것.** 페이스북 앱 쪽 사본에 대화가 있어도 메신저 앱을 썼다는 뜻은 아닙니다 [1]. 종단간 암호화 첨부의 파일 이름은 원래 이름이 아니라서, 파일 이름으로 "어떤 문서를 보냈다" 고 말할 수 없습니다 [1]. `sender_contact_pk` 를 사용자 ID 로 착각하면 엉뚱한 사람을 보낸 사람으로 적게 되니, 반드시 `fb_transport_contacts` 로 바꾼 값을 씁니다 [1].

## 시각 해석

`timestamp_ms` 처럼 `_ms` 로 끝나는 칸은 Unix 밀리초이고 UTC 기준입니다 [1]. `threads.last_activity_timestamp_ms` 는 칸 이름대로라면 대화의 마지막 활동 시각이라서, 메시지 하나의 시각은 메시지 쪽 칸에서 읽습니다 [1].

`client_messages.display_ts_ms` 에 시각이 없으면 64비트 정수의 최솟값(또는 그보다 1 큰 값) 같은 표시값이 들어가고, 실제 시각이 아닙니다 [1]. 이 값을 그대로 변환하면 터무니없는 날짜가 나오니 걸러 냅니다. 변환 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

## 함정과 한계

두 사본에 같은 대화가 있어도 대화 키(`thread_pk`)는 DB 마다 따로 매겨져 값이 다릅니다 [1]. 두 DB 의 메시지를 합칠 때 `thread_pk` 로 중복을 가리면 같은 대화가 두 번 세어지므로, 시각과 본문, 상대로 맞춰 봅니다.

`secure_messages` 표가 있어도 시험 표본에서는 행이 없었고 값도 암호화돼 있어서 [1], 이 표가 비었다고 비밀 대화를 쓰지 않았다고 판단할 근거는 되지 않습니다.

행이 나온 표본이 iOS 15.3.1 이후 일부 버전에 몰려 있어서 [1], 그보다 옛 버전이나 표본에 없는 버전에서는 표 구성이 다를 수 있습니다. 도구 결과가 비면 스키마부터 확인합니다([도구 검증](../../03-techniques/reporting/tool-validation.md)).

## 직접 분석해 보기

**헥스로 한 번.** 아래는 명세로 만든 예시이고 실제 검체에서 나온 값이 아닙니다. SQLite 레코드에서 8바이트 정수는 빅엔디언으로 저장되므로, `display_ts_ms` 에 64비트 최솟값이나 그보다 1 큰 값이 들어 있으면 다음 바이트로 보입니다.

```
80 00 00 00 00 00 00 00   → -9,223,372,036,854,775,808
80 00 00 00 00 00 00 01   → -9,223,372,036,854,775,807
```

시각 칸에서 이 두 값이 보이면 실제 시각이 아닌 표시값으로 보고 걸러 냅니다.

**공개 도구로 한 번.** iLEAPP 의 메신저 분석기로 두 사본을 함께 읽어 보고서를 만들고 [1], SQLite 뷰어로 종단간 암호화 메시지를 직접 확인합니다.

```sql
SELECT datetime(m.display_ts_ms / 1000, 'unixepoch') AS utc,
       m.thread_pk, f.server_contact_id, m.message_content_type
FROM client_messages m
LEFT JOIN fb_transport_contacts f ON m.sender_contact_pk = f.client_contact_pk
WHERE m.display_ts_ms > 0
ORDER BY m.display_ts_ms;
```

`WHERE m.display_ts_ms > 0` 은 표시값을 거르는 조건입니다.

## 교차 검증

- [설치된 앱](../app-usage/installed-apps.md) — 메신저 앱과 페이스북 앱 가운데 어느 쪽이 설치돼 있었는지 봅니다.
- [알림 기록](../app-usage/notifications.md) — 받은 메시지가 알림으로도 남았는지 봅니다.
- [KnowledgeC](../app-usage/knowledgec/index.md), [바이옴](../app-usage/biome/index.md) — 메시지 시각에 어느 앱을 쓰고 있었는지 봅니다.
- [앱별 데이터 사용량](../network/data-usage.md) — 같은 시간대 앱의 송수신량을 봅니다.
- [사진 보관함](../media/photos/index.md) — 종단간 암호화 첨부 사진이 사진 보관함에도 있는지 봅니다.
- [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md)

## 실습

공개 검체(NIST CFReDS 등) 가운데 메신저나 페이스북 앱이 설치된 iOS 전체 파일 시스템 이미지를 골라 풀어 봅니다.

1. 두 앱 그룹 가운데 어느 쪽에 대화함 DB 가 있습니까? 둘 다 있다면 각각의 경로를 적어 보십시오.
2. 두 사본에 같은 대화가 있다면, 각 DB 의 `thread_pk` 값을 비교해 보십시오.
3. `client_messages` 에서 `display_ts_ms` 가 표시값인 행은 몇 건입니까?
4. `sender_contact_pk` 와 `fb_transport_contacts.server_contact_id` 가 다른 행이 있습니까?
5. `media_bank/AdvancedCrypto/` 아래 파일 이름에서 `att.` 과 `prev.` 로 시작하는 파일은 각각 몇 개입니까?

## 참고 문헌

1. iLEAPP, scripts/artifacts/facebookMessenger.py — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/facebookMessenger.py
