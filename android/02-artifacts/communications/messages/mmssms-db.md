---
title: "문자 DB 구조"
parent: "문자"
grand_parent: "아티팩트 · 통화·문자·연락처"
nav_order: 570
---

# 문자 DB 구조 (mmssms.db)

Android 시스템 문자 저장소인 mmssms.db 의 표와 칸, 값의 뜻, 시각 단위를 정리합니다. 표와 칸 이름은 현행 AOSP(main 가지) 소스 기준이고, 실제 폰에서 본 내용에는 확인 범위를 붙였습니다.

## 한 줄 요약

mmssms.db 는 시스템 제공자 패키지 com.android.providers.telephony 가 관리하는 SQLite DB 로, SMS 는 sms 표에, MMS 는 pdu·part·addr 표에 나눠 담고 두 종류가 threads 표의 대화 번호(thread_id)를 함께 쓰며, MMS 첨부 파일은 DB 밖의 app_parts 폴더에 따로 둡니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

Android 의 SMS·MMS 는 시스템 제공자 패키지 com.android.providers.telephony 가 mmssms.db 에 저장합니다 [1][2]. SMS 한 건은 sms 표의 한 행이고, MMS 한 건은 본체(pdu 표) 한 행에 조각(part 표)과 주소(addr 표) 여러 행이 딸린 모양입니다. 보낸 메시지에는 그 메시지를 만든 앱이 creator 칸에 남는데, 이 칸은 제공자가 채우고 앱이 바꿀 수 없습니다 [1].

Google 메시지 앱은 자기 DB(bugle_db)를 따로 두고, RCS 대화 본문이 이 DB 에 들어가는지는 확인하지 못했습니다. 두 내용은 [RCS 메시지 (RCS)](rcs.md) 페이지에서 다룹니다.

## 위치와 버전별 차이

| 대상 | 경로 | 근거 |
|---|---|---|
| DB | `/data/user_de/0/com.android.providers.telephony/databases/mmssms.db` | 첨부 폴더 경로와 ALEAPP 경로 패턴으로 미루어 본 위치이고, 이 전체 경로를 한 줄로 적은 공식 문서는 열어 보지 못함 [2][3] |
| MMS 첨부 폴더 | `/data/user_de/0/com.android.providers.telephony/app_parts` | 제공자 소스 주석 [2] |
| 같은 파일의 다른 경로 | `data_mirror/data_de/null/0/...` | ALEAPP 주석, 같은 파일이 `data/user_de/0/...` 와 이 경로 두 곳에 보일 수 있음 [3] |

경로의 `user_de` 는 기기 암호화(DE) 저장 영역이고, 저장 영역의 구분은 [저장 공간 암호화 (Encryption)](../../../01-foundations/storage/encryption/index.md) 와 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다. ALEAPP 는 `*/com.android.providers.telephony/databases/mmssms*`, `*/com.android.providers.telephony/app_parts/*`, `*/com.android.providers.telephony/parts/*` 세 패턴으로 파일을 찾습니다 [3]. `parts` 폴더가 어느 버전에서 쓰였는지는 확인하지 못했습니다.

| 구분 | 차이 | 근거 |
|---|---|---|
| DB 스키마 버전 | 소스 main 가지의 DATABASE_VERSION 은 69이고, Android 버전별 값은 확인하지 못함 | [2] |
| Android 7(N) 으로 올린 기기 | 파일 기반 암호화(FBE)를 쓰지 않던 기기를 N 으로 올리면 첨부 파일을 `/data/data` 에서 `/data/user_de` 로 옮기고 part._data 에 적힌 경로도 새 경로로 고침(upgradeDatabaseToVersion62) | [2] |
| 자동차 기기 | sms_changes 표(읽음 변경·삭제를 적는 트리거 포함)는 FEATURE_AUTOMOTIVE 기기에서만 만들고 휴대폰에는 없음 | [2] |
| LG 기기 | sms.type 에 7·8·19 같은 확장 값을 씀. ALEAPP 는 lgeSiid 칸이 있을 때만 이 값을 풀지만, 제조사 문서 근거가 없어 검증되지 않은 뜻이라고 스스로 적음 | [3] |
| 삼성 기기 | spam_sms 표가 있을 수 있고 ALEAPP 는 이 표를 sms 표와 같은 방식으로 읽음. 칸 구성과 언제 쓰이는지는 확인하지 못함 | [3] |

adb 일반 권한으로 mmssms.db 를 읽을 수 있는지는 관찰하지 않았습니다. 관찰한 폰의 설정 값에는 문자 관련 이름의 키가 있지만 값은 가려져 있고 뜻도 공식 문서로 확인하지 못했습니다. settings secure 에는 `backup_enabled:com.android.providers.telephony`, `mms_backup_enabled`, `mms_backup_in_progress`, `mms_backup_last_completed` 가 있고, settings global 에는 `multi_sim_sms`, `multi_sim_sms_slot`, `multi_sim_psim_sms`, `multi_sim_existing_sms`, `sms_short_codes_content_url`, `sms_short_codes_metadata_url`, `cdma_cell_broadcast_sms` 가 있습니다 (확인 범위: Android 16, One UI 8.5). 설정 값을 읽는 법은 [설정 값 (Settings Global·Secure·System)](../../system-account/settings.md) 페이지에 있습니다.

## 구조

### 표 한눈에 보기

| 표·뷰 | 담는 것 |
|---|---|
| sms | SMS 한 건에 한 행 |
| pdu | MMS 본체 한 건에 한 행 |
| part | MMS 조각(글·그림·SMIL 등) |
| addr | MMS 보낸 사람·받는 사람 주소 |
| threads | 대화 목록, SMS 와 MMS 가 함께 씀 |
| canonical_addresses | 대화 상대 주소에 번호를 매긴 표 |
| raw | 여러 조각으로 나뉜 SMS 가 다 올 때까지 조각을 잡아 두는 표 |
| attachments, sr_pending, pending_msgs | 첨부 대응, 전송 결과 보고 대기, 보내거나 받을 대기열 |
| words | 검색용 FTS3 가상 표 |
| sms_restricted (뷰) | sms 중 type 이 1(받음) 또는 2(보냄)인 행만 보여 줌 |

모든 표 이름과 칸은 [2] 의 CREATE 문 기준입니다.

### sms 표

```
_id, thread_id, address, person, date, date_sent(기본 0), protocol, read(기본 0),
status(기본 -1), type, reply_path_present, subject, body, service_center,
locked(기본 0), sub_id(기본 INVALID_SUBSCRIPTION_ID), error_code, creator, seen(기본 0)
```

| 칸 | 뜻 |
|---|---|
| address | 상대방 주소(번호) [1] |
| person | 보낸 사람의 연락처 ID, 있을 때만 [1] |
| date / date_sent | 받은 시각 / 보낸 시각, 둘 다 INTEGER [1]. 단위는 "시각 해석" 절에 정리 |
| type | 메시지 상자, 아래 표 [1] |
| status | 전송 상태(TP-Status), 아래 표 [1] |
| read | 읽었는지(0/1) [1] |
| seen | 사용자가 봤는지, 알림을 띄울지를 이 값으로 정함 [1] |
| body | 본문 |
| protocol | 프로토콜 식별 코드(INTEGER), 값의 뜻은 소스에 적혀 있지 않음 [1] |
| sub_id | 메시지가 속한 SIM 가입 번호, 알 수 없으면 0보다 작은 값. 칸 이름은 `subscription_id` 가 아니라 `sub_id` [1] |
| creator | 보낸 메시지를 만든 앱, 보통 패키지 이름이고 제공자가 채우는 읽기 전용 칸 [1] |
| locked | 잠긴 메시지인지(0/1) [1] |
| error_code | 보내거나 받을 때 난 오류 코드 [1] |

| type 값 | 뜻 |
|---|---|
| 0 | ALL |
| 1 | INBOX, 받음 |
| 2 | SENT, 보냄 |
| 3 | DRAFT, 임시 저장 |
| 4 | OUTBOX, 보내는 중 |
| 5 | FAILED, 실패 |
| 6 | QUEUED, 나중에 보냄 |

| status 값 | 뜻 |
|---|---|
| -1 | 상태를 받지 못함 |
| 0 | 완료 |
| 32 | 대기 |
| 64 | 실패 |

### pdu 표 (MMS 본체)

```
_id, thread_id, date, date_sent(기본 0), msg_box, read(기본 0), m_id, sub, sub_cs,
ct_t, ct_l, exp, m_cls, m_type, v, m_size, pri, rr, rpt_a, resp_st, st, tr_id,
retr_st, retr_txt, retr_txt_cs, read_status, ct_cls, resp_txt, d_tm, d_rpt,
locked(기본 0), sub_id, seen(기본 0), creator, text_only(기본 0)
```

위 칸 이름은 CREATE 문 기준이고 [2], 이 가운데 _id·thread_id·date·date_sent·msg_box·read·m_id·sub·ct_t·ct_l·m_cls·m_type·v·m_size·rr·st·d_rpt·locked·sub_id·seen·creator·text_only 는 공개 상수 값과도 맞춰 봤습니다 [1]. 나머지 칸의 상수는 따로 보지 않았습니다. sub 칸은 MMS 제목입니다 [1].

msg_box 는 SMS 의 type 과 같은 번호를 쓰지만 6(QUEUED)이 없습니다 [1][3].

| msg_box 값 | 뜻 |
|---|---|
| 0 | ALL |
| 1 | INBOX |
| 2 | SENT |
| 3 | DRAFTS |
| 4 | OUTBOX |
| 5 | FAILED |

m_type 은 MMS 메시지 종류이고, 제공자는 대화 목록의 안 읽음 수를 셀 때 아래 세 값만 셉니다 [2].

| m_type 값 | 뜻 |
|---|---|
| 128 | SEND_REQ, 보낸 MMS |
| 130 | NOTIFICATION_IND, 받을 MMS 가 있다는 알림 |
| 132 | RETRIEVE_CONF, 받은 MMS |

### part 표 (MMS 조각)

```
_id, mid, seq(기본 0), ct, name, chset, cd, fn, cid, cl, ctt_s, ctt_t, _data, text, sub_id
```

mid 는 pdu._id 를 가리키고, ct 는 조각의 콘텐츠 형식, text 는 글 조각의 본문, _data 는 파일 조각의 파일 시스템 경로입니다 [1]. 첨부 파일 본체는 DB 에 없고 _data 가 가리키는 app_parts 폴더의 파일이라서, DB 만 뽑으면 첨부 파일이 빠집니다.

### addr 표 (MMS 주소)

```
_id, msg_id, contact_id, address, type, charset, sub_id
```

msg_id 는 주소가 딸린 MMS(pdu._id)이고, type 은 PduHeaders 의 FROM·TO·CC·BCC 중 하나입니다 [1]. ALEAPP 쿼리가 쓰는 값은 아래와 같습니다 [3].

| type 값 | 뜻 |
|---|---|
| 0x89 (137) | FROM, 보낸 사람 |
| 0x97 (151) | TO, 받는 사람 |
| 0x82 (130) | CC |
| 0x81 (129) | BCC |

### threads·canonical_addresses 표

```
threads: _id, date(기본 0), message_count(기본 0), recipient_ids, snippet, snippet_cs(기본 0),
         read(기본 1), archived(기본 0), type(기본 0), error(기본 0), has_attachment(기본 0), sub_id
canonical_addresses: _id(AUTOINCREMENT), address, sub_id
```

recipient_ids 는 canonical_addresses 표의 _id 들을 숫자 순으로 공백으로 이어 붙인 문자열입니다 [1][2]. 받는 사람 묶음이 같고 제목이 같거나 비어 있으면 같은 대화로 묶입니다 [2]. canonical_addresses 는 주소를 처음 본 순서대로 번호를 매기고, AUTOINCREMENT 라서 주소가 지워져도 그 번호를 다시 쓰지 않습니다 [2]. archived 는 대화를 보관 처리했는지를 나타냅니다 [1].

### 그 밖의 표와 트리거

raw 표의 칸은 `_id, date, reference_number, count, sequence, destination_port, address, sub_id, pdu, deleted(기본 0), message_body, display_originating_addr` 이고, pending_msgs 에는 proto_type·msg_id·msg_type·err_type·err_code·retry_index·due_time·last_try 같은 칸이 있습니다 [2]. attachments 의 칸은 sms_id·content_url·offset·sub_id 입니다 [2].

words 는 `_id, index_text, source_id, table_to_use, sub_id` 로 된 FTS3 가상 표이고, sms 나 part 가 바뀌거나 지워지면 트리거(sms_words_update·sms_words_delete·mms_words_update·mms_words_delete)가 words 의 행도 함께 고치거나 지웁니다 [2]. pdu 가 지워지면 part_cleanup·addr_cleanup 트리거가 딸린 part·addr 행을 같이 지우고, 메시지가 지워지면 threads.snippet 을 남은 메시지 가운데 가장 최근 것으로 다시 계산합니다 [2].

## 증거로서 의미

**증명하는 것.** sms 행 하나는 이 기기의 시스템 문자 저장소에 그 상대 주소, 메시지 상자(type), 시각, 본문으로 된 문자 기록이 있다는 뜻입니다. 보낸 메시지의 creator 는 앱이 바꿀 수 없는 칸이라서 [1], 어떤 패키지가 그 메시지를 만들었는지 보여 주는 단서가 됩니다. MMS 는 addr 의 FROM·TO 로 상대를, part 의 _data 로 첨부 파일 위치를 알 수 있습니다. sub_id 로는 다중 SIM 기기에서 어느 SIM 가입으로 오간 메시지인지 가릴 수 있습니다 [1].

**증명하지 못하는 것.** read 가 1 이어도 사람이 본문을 읽었다는 뜻은 아니고, 읽음 처리가 된 상태라는 뜻입니다. seen 은 알림을 띄울지 정하는 값이라서 [1] 이것만으로 사용자가 내용을 확인했다고 쓰지 않습니다. 누가 기기를 조작해 보냈는지도 이 DB 는 말하지 않습니다. RCS 대화가 이 DB 에 들어가는지 확인하지 못했으니, mmssms.db 에 없다고 해서 문자 대화가 없었다고 결론 내리지 않습니다.

## 시각 해석

| 칸 | 단위 | 뜻 |
|---|---|---|
| sms.date | 유닉스 밀리초 | 받은 시각 [1] |
| sms.date_sent | 이번 조사에서 단위를 확인하지 못함 | 보낸 시각 [1] |
| pdu.date | 유닉스 초 | MMS 시각 |
| pdu.date_sent | 확인하지 못함 | 보낸 시각 |
| threads.date | 유닉스 밀리초 | 트리거가 돈 순간의 기기 시각이거나, 제공자가 다시 계산했을 때는 대화의 가장 최근 메시지 시각 [2] |

sms.date 가 밀리초이고 pdu.date 가 초라는 근거는 제공자의 합치기 쿼리입니다. 이 쿼리는 `SELECT date * 1000 AS date ... FROM pdu UNION SELECT date ... FROM sms` 로 pdu.date 에만 1000을 곱합니다 [2]. ALEAPP 도 SMS date 는 밀리초, MMS pdu.date 는 초라고 적고 그에 맞춰 UTC 로 바꿉니다 [3]. threads.date 는 sms·pdu 가 들어오거나 바뀔 때 트리거가 `strftime('%s','now') * 1000` 으로 채우니 초 단위 값에 1000을 곱한 모양이고, 그 순간의 기기 시계를 따릅니다 [2]. 제공자의 updateThreads 가 돌면 이 값을 위 합치기 쿼리로 찾은 가장 최근 메시지의 시각으로 다시 쓰기 때문에 [2], threads.date 가 메시지 시각과 같은지 다른지만으로 무엇이 일어났는지 단정하지 않습니다.

유닉스 시각은 UTC 기준이지만 값 자체는 기기 시계가 정합니다. 기기 시계를 바꾼 흔적이 있으면 [시간대와 시각 설정 (Time Zone)](../../system-account/time-zone.md) 을 함께 보고, 값을 바꾸는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 함정과 한계

ALEAPP 는 MMS 한 건을 SMIL 이 아닌 조각마다 한 줄로 보여 주기 때문에, 조각이 여러 개인 MMS 는 같은 MSG ID 가 여러 줄에 나옵니다 [3]. 줄 수를 메시지 수로 세지 않습니다. 첨부 파일도 파일 이름만으로 맞추지 않고 _data 에 적힌 전체 경로(저장 구역·사용자 번호·패키지·파일 이름)로 맞추며, 어떤 part 행도 가리키지 않는 app_parts 파일과 pdu 행 없이 남은 part 행은 따로 표시합니다 [3]. 그런 상태가 왜 생기는지는 확인하지 못했고, 이런 파일과 행을 곧바로 지운 메시지의 흔적이라고 단정하지 않습니다.

words 표는 트리거가 sms·part 와 함께 지우니 [2], 지운 문자 본문이 words 에 남아 있기를 기대하지 않습니다. threads.snippet 도 메시지를 지우면 남은 메시지 기준으로 다시 계산되니 [2], 대화 목록의 미리보기 글이 지운 메시지를 보여 주지 않습니다. 지운 행이 SQLite 빈 페이지나 WAL 파일에 남는지는 이번 조사로 확인하지 못했고, 일반적인 복구 방법은 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 페이지에 있습니다.

canonical_addresses 의 번호가 중간에 비어 있으면 그 번호를 쓰던 행이 있었을 수 있지만, 번호만으로 어떤 주소였는지나 왜 없어졌는지는 알 수 없습니다. 읽음 변경과 삭제를 적는 sms_changes 표는 자동차 기기에만 있어서 [2] 휴대폰에서 찾지 않습니다. LG 기기의 확장 type 값은 뜻이 검증되지 않았고 [3], 삼성 spam_sms 표도 칸 구성을 확인하지 못했으니 이 두 곳에서 뽑은 값은 보고서에 그 한계를 함께 적습니다.

## 직접 분석해 보기

원본을 건드리지 않도록 복사본을 열고, 같은 폴더에 `-wal` 이나 `-journal` 파일이 있으면 함께 복사합니다. SQLite 파일을 다루는 일반 절차는 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다. 아래 쿼리는 이 페이지의 칸 이름으로 만든 예시이고, 공개 도구인 sqlite3 셸에서 그대로 돌릴 수 있습니다.

```sql
-- SMS: date 는 밀리초라서 1000으로 나눈다. date_sent 는 단위를 확인하지 못해 원래 값으로 둔다.
SELECT _id, thread_id, address, type, status,
       datetime(date / 1000, 'unixepoch') AS date_utc,
       date_sent, read, seen, sub_id, creator, body
FROM sms
ORDER BY date;
```

```sql
-- MMS: pdu.date 는 초. 조각이 여러 개면 한 MMS 가 여러 줄로 나온다.
SELECT p._id, p.thread_id, p.msg_box, p.m_type,
       datetime(p.date, 'unixepoch') AS date_utc,
       p.sub, pt.seq, pt.ct, pt.text, pt._data
FROM pdu AS p
LEFT JOIN part AS pt ON pt.mid = p._id
ORDER BY p.date, pt.seq;

-- MMS 주소: 137=FROM, 151=TO, 130=CC, 129=BCC
SELECT msg_id, type, address FROM addr ORDER BY msg_id;
```

```sql
-- 대화와 상대 주소
SELECT _id, recipient_ids, message_count, snippet, archived FROM threads;
SELECT _id, address FROM canonical_addresses ORDER BY _id;
```

MMS 첨부는 part._data 경로의 파일을 app_parts 폴더에서 찾아 맞춥니다. 공개 도구로는 ALEAPP 의 smsmms 모듈이 sms·pdu·part·addr 를 읽고, 삼성 기기의 spam_sms 표와 app_parts 파일 대응까지 보고합니다 [3]. 도구 결과와 위 쿼리 결과의 건수를 맞춰 보는 방법은 [도구 검증](../../../03-techniques/reporting/tool-validation.md) 페이지에 있습니다. SQLite 레코드를 헥스로 따라가는 법은 SQLite 페이지에서 다룹니다.

## 교차 검증

sms.person 과 addr.contact_id 는 연락처 ID 라서 [연락처 (contacts2.db)](../contacts.md) 와 맞춰 보고, 같은 상대와의 통화는 [통화 기록 (calllog.db)](../call-log.md) 에서 확인합니다. 문자가 들어온 시각은 알림 쪽 기록과도 맞춰 볼 수 있습니다. 관찰한 폰의 `dumpsys usagestats` 이벤트에는 `type=NOTIFICATION_INTERRUPTION ... channelId=CHANNEL_ID_SMS_MMS` 줄이 2개 있었지만 패키지가 가려져 있어 어느 앱의 알림인지는 알 수 없습니다. `dumpsys notification` 의 알림 기록에는 `android.title=<값> [length=##]`, `android.text=<값> [length=##]` 칸이 있는데, 이 알림이 문자 알림인지도 가려져 있어 알 수 없습니다 (확인 범위: Android 16, One UI 8.5). 이 기록들은 [앱 사용 기록 (usagestats)](../../app-usage/usagestats/index.md), [알림 기록 (Notification History)](../../app-usage/notification-history.md), [dumpsys 출력 (dumpsys)](../../logs/dumpsys.md) 페이지에 있습니다.

Google 메시지를 쓰는 기기라면 [RCS 메시지 (RCS)](rcs.md) 페이지의 bugle_db 와, 삼성 기기라면 [삼성 메시지 앱 (Samsung Messages)](samsung-messages.md) 페이지와 함께 봅니다. 문자를 중심으로 조사하는 흐름은 [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md) 와 [스미싱 흔적 (Smishing)](../../../04-scenarios/incident/smishing.md) 시나리오에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)의 Android 이미지에서 mmssms.db 를 찾아 아래 질문을 풀어 봅니다.

1. sms 표에서 type 값별 건수를 세고, 2(SENT) 행의 creator 에 어떤 패키지가 나오는지 확인합니다.
2. MMS 한 건을 골라 pdu·part·addr 를 이어 보고, part._data 가 가리키는 파일이 app_parts 폴더에 실제로 있는지 확인합니다.
3. threads.date 와 그 대화의 가장 최근 메시지 시각을 비교하고, 두 값이 왜 다를 수 있는지 설명합니다.
4. ALEAPP 결과의 MMS 줄 수와 pdu 행 수를 비교하고, 차이가 조각 수로 설명되는지 확인합니다.

## 참고 문헌

1. Telephony.java — AOSP frameworks/base (main), https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/provider/Telephony.java
2. MmsSmsDatabaseHelper.java — AOSP packages/providers/TelephonyProvider (main), https://android.googlesource.com/platform/packages/providers/TelephonyProvider/+/refs/heads/main/src/com/android/providers/telephony/MmsSmsDatabaseHelper.java
3. ALEAPP smsmms.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/smsmms.py
