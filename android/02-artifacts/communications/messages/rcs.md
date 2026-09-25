---
title: "RCS 메시지"
parent: "문자"
grand_parent: "아티팩트 · 통화·문자·연락처"
nav_order: 580
---

# RCS 메시지 (RCS)

RCS(Rich Communication Services) 채팅이 기기의 어디에 남는지, 이번 조사로 확인한 범위를 정리합니다. RCS 저장 위치를 설명한 AOSP·Android 공식 문서는 열어 보지 못했고, 그래서 이 페이지는 공개 파서 ALEAPP 가 읽는 Google 메시지 앱의 DB 와 삼성 기기의 IMS 서비스 로그를 중심으로 씁니다.

## 한 줄 요약

RCS 대화 본문이 시스템 문자 DB(mmssms.db)에 들어가는지는 확인하지 못했고, 확인한 기록은 Google 메시지 앱의 bugle_db 와 삼성 IMS 서비스(com.sec.imsservice)의 등록 로그인데, bugle_db 에서도 한 메시지가 SMS·MMS·RCS 가운데 무엇으로 오갔는지 가르는 칸은 찾지 못했습니다 [1][2].

## 무엇을 기록하나 · 왜 생기나

Google 메시지 앱(com.google.android.apps.messaging)은 mmssms.db 와 별개로 자기 DB 인 bugle_db 를 두고, ALEAPP 도 이 DB 를 mmssms.db 와 다른 모듈로 읽습니다 [1]. RCS 대화가 시스템 문자 DB 에 들어간다는 근거를 찾지 못했으니, RCS 를 쓸 수 있는 기기라면 문자 앱이 따로 두는 DB 를 반드시 함께 확인합니다. mmssms.db 의 구조는 [문자 DB 구조 (mmssms.db)](mmssms-db.md) 페이지에 있습니다.

삼성 기기에서는 IMS 서비스가 IMS 등록·데이터망·SIM 상태를 로그로 남깁니다. ALEAPP 는 이 로그가 통화나 메시지 내용이 아니라 등록 상태를 기록한다고 적었고 [2], 이 로그와 RCS 채팅의 관계(예: RCS 등록 여부가 로그에 드러나는지)는 확인하지 못했습니다.

## 위치

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| Google 메시지 DB | `*/com.google.android.apps.messaging/databases/bugle_db` (ALEAPP 경로 패턴) | 대화·참여자·메시지 조각 [1] |
| 같은 DB 의 부속 파일 | 같은 폴더의 `bugle_db-wal`, `bugle_db-shm`, `bugle_db-journal` 이 있을 수 있음 | ALEAPP 가 이 셋을 따로 거름 [1] |
| 삼성 IMS 서비스 | com.sec.imsservice 앱 데이터 폴더의 `shared_prefs/saved_impu.xml`, `files/*.log` | SIM 과 IMS 식별자, 등록·망·SIM 상태 [2] |
| 기기 설정 | settings system 의 `rcs_user_setting` 과 번호가 붙은 `rcs_user_setting#` | 값은 가려져 있고 뜻은 공식 문서로 확인하지 못함 (확인 범위: SM-S937N, Android 16, One UI 8.5) |

앱 데이터 폴더의 전체 경로 구성은 [앱 데이터 폴더 구조](../../../01-foundations/storage/app-data-layout.md) 페이지에 있습니다. ALEAPP 공개 표본 13개 가운데 Pixel·Poco 이미지에는 com.sec.imsservice 로그가 없었습니다 [2].

## bugle_db 구조

ALEAPP 가 쓰는 표와 칸은 아래와 같습니다 [1]. DB 에 이보다 많은 표와 칸이 있을 수 있지만 이번 조사에서는 이 범위만 확인했습니다.

| 표 | ALEAPP 가 쓰는 칸 |
|---|---|
| parts | timestamp, content_type, text, file_size_bytes, local_cache_path, conversation_id, message_id |
| messages | _id, sender_id |
| participants | _id, display_destination, sub_id |
| conversations | _id, name |

오래된 bugle_db 에는 parts.file_size_bytes 와 parts.local_cache_path 칸이 없습니다 [1]. file_size_bytes 가 -1 이면 ALEAPP 는 "N/A" 로 표시합니다 [1].

ALEAPP 는 메시지에 딸린 참여자의 sub_id 로 방향을 가립니다 [1]. -2 는 AOSP Messaging 의 OTHER_THAN_SELF_SUB_ID, 곧 기기 주인이 아닌 사람을 뜻합니다 [1].

| participants.sub_id | ALEAPP 판정 |
|---|---|
| -2 | 받은 메시지 |
| 그 밖의 값 | 보낸 메시지 |
| NULL | 방향을 비워 둠 |

## 삼성 IMS 서비스 로그

| 파일 | 내용 |
|---|---|
| `shared_prefs/saved_impu.xml` | SIM 의 IMSI 와, 그 SIM 이 IMS 망에 등록한 공개 식별자(IMPU, sip: 또는 tel: URI)를 짝지어 둠. 시각은 적히지 않음 |
| `files/RegiMgr.log` | IMS 등록 로그. 상태 값의 예는 REGISTERED, CONNECTED, REGISTERING, DEREGISTERING, IDLE, CONFIGURED. 통화·메시지 내용은 없음 |
| `files/PdnController.log` | IMS 데이터망 로그. 인터페이스 이름(rmnet*), 기기 IMS 주소, 통신사 P-CSCF 주소 |
| `files/SimManager_slot*.log` | SIM·통신사(MNO/MVNO) 상태 로그. IMSI 는 * 로 가려져 있고, SIM 이 바뀌면 MNO 이름이 바뀜 |

모두 [2] 기준입니다. files 폴더의 각 로그 첫 줄에는 `> Created (pid: N, binary: ...)` 모양으로 IMS 서비스가 시작한 시각과 펌웨어 빌드가 적혀 있어서, 이 줄을 모으면 펌웨어 갱신 이력처럼 쓸 수 있습니다 [2].

## 증거로서 의미

**증명하는 것.** bugle_db 의 parts 행은 Google 메시지 앱 DB 에 그 대화·시각·내용(또는 첨부 크기와 캐시 경로)으로 된 메시지 조각이 있다는 기록이고, 참여자의 sub_id 로 받은 것인지 보낸 것인지를 ALEAPP 규칙대로 가릴 수 있습니다. saved_impu.xml 은 어떤 SIM 이 어떤 IMS 식별자로 등록했는지를, RegiMgr.log 는 IMS 등록 상태가 언제 바뀌었는지를 보여 줍니다 [2].

**증명하지 못하는 것.** bugle_db 에서 전송 방식을 가르는 칸을 확인하지 못했으니, 행 하나를 두고 "RCS 로 보냈다" 고 쓰지 않습니다. IMS 로그에는 통화나 메시지 내용이 없어서 [2] RCS 채팅이 있었다는 증거로 쓰지 않고, 망 등록 상태의 기록으로만 씁니다. saved_impu.xml 에는 시각이 없어서 그 짝이 언제 생겼는지 알려 주지 않습니다.

## 시각 해석

bugle_db 의 parts.timestamp 는 유닉스 밀리초이고, ALEAPP 는 1000으로 나눠 UTC 로 바꿉니다 [1]. 삼성 IMS 로그의 모든 줄은 `MM/DD/YYYY HH:MM:SS.mmm` 형식의 기기 현지 시각이고 시간대가 적혀 있지 않아서 UTC 로 읽으면 안 됩니다 [2]. 두 기록을 한 시간 축에 놓으려면 기기의 시간대를 먼저 확인합니다. 시간대 기록은 [시간대와 시각 설정 (Time Zone)](../../system-account/time-zone.md), 시각 값을 바꾸는 법은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 함정과 한계

오래된 bugle_db 에는 parts 의 일부 칸이 없어서, 그런 DB 에 새 칸 이름을 넣은 쿼리는 오류가 납니다 [1]. ALEAPP 의 방향 판정은 sub_id 값에 기댄 규칙이고 sub_id 가 NULL 이면 방향을 모릅니다 [1]. IMS 서비스 로그는 삼성 기기에서만 확인됐고 [2], LG 기기용 RCS 모듈(lgRCS.py)이 ALEAPP 에 있지만 내용은 열어 보지 않았습니다 [3]. settings system 의 `rcs_user_setting` 키는 이름만 보고 RCS 를 켰다는 뜻으로 읽지 않습니다. 뜻을 확인하지 못했기 때문입니다.

## 직접 분석해 보기

복사본을 열고 `-wal` 파일이 있으면 함께 복사합니다. 아래 쿼리는 ALEAPP 가 쓰는 칸으로 만든 예시이고, 오래된 DB 에서는 file_size_bytes 와 local_cache_path 를 뺍니다.

```sql
SELECT datetime(p.timestamp / 1000, 'unixepoch') AS time_utc,
       c.name AS conversation, pa.display_destination, pa.sub_id,
       p.content_type, p.text, p.file_size_bytes, p.local_cache_path
FROM parts AS p
LEFT JOIN conversations AS c ON c._id = p.conversation_id
LEFT JOIN messages AS m ON m._id = p.message_id
LEFT JOIN participants AS pa ON pa._id = m.sender_id
ORDER BY p.timestamp;
```

공개 도구로는 ALEAPP 의 googleMessages 모듈이 bugle_db 를, samsungImsService 모듈이 IMS 서비스 로그를 읽습니다 [1][2]. SQLite 파일을 다루는 일반 절차는 [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md) 페이지에 있습니다.

## 교차 검증

같은 기기의 [문자 DB 구조 (mmssms.db)](mmssms-db.md) 와 bugle_db 를 나란히 놓고 같은 상대·같은 시각의 메시지가 양쪽에 있는지 봅니다. 삼성 기기라면 [삼성 메시지 앱 (Samsung Messages)](samsung-messages.md) 페이지를 함께 봅니다. 펌웨어 갱신은 IMS 로그 첫 줄과 [기기 정보와 빌드 (build.prop·Build)](../../system-account/device-build.md) 를 맞춰 봅니다. 대화 상대 중심의 조사 흐름은 [누구와 연락을 주고받았나 (Communication)](../../../04-scenarios/activity/communication.md) 시나리오에 있습니다.

## 실습

1. 공개 검체에서 bugle_db 를 찾아 위 쿼리를 돌리고, participants.sub_id 값별 건수를 세어 받은 메시지와 보낸 메시지의 비율을 확인합니다.
2. 같은 검체의 mmssms.db 와 bugle_db 에서 같은 상대 번호의 메시지를 찾아, 한쪽에만 있는 메시지가 있는지 확인합니다.
3. 삼성 검체라면 IMS 로그 첫 줄의 펌웨어 빌드를 모아 시각 순으로 늘어놓고, 로그 시각이 현지 시각이라는 점을 반영해 UTC 로 바꿔 봅니다.

## 참고 문헌

1. ALEAPP googleMessages.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/googleMessages.py
2. ALEAPP samsungImsService.py — abrignoni/ALEAPP, https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/samsungImsService.py
3. ALEAPP scripts/artifacts 폴더 목록 — abrignoni/ALEAPP (GitHub API), https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
