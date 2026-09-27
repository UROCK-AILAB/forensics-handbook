---
title: "디스코드"
parent: "아티팩트 · 메신저"
nav_order: 900
---

# 디스코드 (Discord)

iOS 디스코드는 메시지를 서버 응답을 저장해 둔 캐시 형태로 남기고, 공개 도구는 `fsCachedData` 폴더의 JSON 텍스트 파일과 `kv-storage` 아래 `a` 라는 이름의 SQLite 에서 메시지를 읽으며, 시각은 끝이 `Z` 인 ISO 8601 문자열(UTC)입니다.

## 무엇을 기록하나 · 왜 생기나

앱이 서버에서 받아 온 응답과 화면에 보여 준 데이터를 캐시로 저장해 두는데, 그 안에 메시지 본문·보낸 사람·채널·시각·첨부 정보가 들어 있습니다[2]. 분석 대상이 되는 흔적은 메시지·사진·음성과 영상 통화·반응입니다[1]. 폴더 이름에 쓰인 `com.hammerandchisel.discord` 는 앱 번들 ID 와 같은 이름으로 보입니다[1][2].

## 위치와 버전별 차이

앱 데이터 컨테이너의 아래 두 파일에 디스코드 데이터가 있습니다[1].

```
/private/var/mobile/Containers/Data/Application/<GUID>/Library/Caches/com.hammerandchisel.discord/Cache.db
/private/var/mobile/Containers/Data/Application/<GUID>/Documents/mmkv/mmkv.default
```

iLEAPP 의 디스코드 분석기는 아래 위치를 찾습니다[2].

| 찾는 위치(파일 시스템 추출 기준) | 담긴 것 |
|---|---|
| `*/com.hammerandchisel.discord/fsCachedData/*` | 서버 응답을 줄 단위 JSON 텍스트로 저장한 파일입니다 |
| `*/Library/Caches/kv-storage/@account*/a*` | 이름이 `a` 인 SQLite 이고 `messages0` 표에 메시지가 있습니다 |
| `*/Library/Caches/com.hackemist.SDImageCache/default/*` | 캐시된 이미지입니다 |
| `*/activation_record.plist` | 도구가 함께 읽는 plist 입니다 |

앱 버전별 차이는 공개 자료가 없고, 알려진 iOS 버전은 iOS 15 입니다[1]. 캐시 구조는 앱 업데이트마다 바뀔 수 있어서 위 경로는 "도구가 찾는 위치" 로 보고 실제 기기에서 직접 확인합니다.

## 구조

### `a` 파일의 `messages0` 표

`a` 는 확장자가 없지만 SQLite 파일이고, 메시지는 `messages0` 표의 `data` 열(blob)에 들어 있습니다[2]. `a` 파일을 담은 `@account…` 폴더 이름이 계정마다 달라서, 한 기기에 계정이 여럿이면 폴더도 여럿일 수 있습니다.

### 메시지 필드

메시지의 주요 필드는 아래와 같습니다[2]. 서버 응답의 필드 이름이 그대로 쓰입니다.

| 필드 | 담긴 것 |
|---|---|
| `id`, `channel_id` | 메시지 ID 와 채널 ID 입니다 |
| `type` | 메시지 종류입니다 |
| `content` | 본문입니다 |
| `timestamp` | 보낸 시각입니다 |
| `edited_timestamp` | 수정한 시각이고 수정하지 않은 메시지에는 없습니다 |
| `author` | `id`, `username`, `global_name`(또는 `globalName`), `display_name`, `bot` 을 묶은 객체입니다 |
| `call.ended_timestamp` | 통화가 끝난 시각입니다 |
| `attachments` | `filename`, `url`, `proxy_url`, `width`, `height` 를 묶은 첨부 목록입니다 |
| `embeds` | `url`, `description`, `author`, `footer` 를 묶은 링크 미리보기입니다 |

`author` 의 이름은 `global_name` 과 `globalName` 두 표기로 나올 수 있어서[2], 직접 파싱할 때 둘 다 찾아봅니다.

## 증거로서 의미

**증명하는 것.** 캐시에 남은 메시지 레코드는 이 기기의 디스코드 앱이 이 채널의 이 메시지를 서버에서 받아 저장했다는 사실을 보여 주고, `author` 로 서버가 붙인 보낸 사람 계정을 알 수 있습니다. `edited_timestamp` 가 있는 메시지는 수정된 기록이 있는 메시지로 볼 수 있고, 이 해석은 필드 이름에서 나온 것입니다[2]. `attachments` 의 `url`·`proxy_url` 로 `fsCachedData` 의 첨부 정보와 `SDImageCache` 의 캐시 이미지를 이어 볼 수 있습니다[2].

**증명하지 못하는 것.** 캐시는 앱이 받아 온 데이터이지 사용자가 읽은 기록이 아니라서, 레코드가 있다고 사용자가 그 메시지를 봤다고 단정하지 않습니다. 캐시는 앱이 비우거나 덮어쓸 수 있어서 레코드가 없다고 대화가 없었다고 볼 수도 없습니다. `edited_timestamp` 는 수정 시각만 알려 주고, 수정 전 본문은 같은 메시지의 옛 레코드가 캐시 어딘가에 따로 남아 있을 때만 볼 수 있습니다.

## 시각 해석

메시지의 시각 필드는 ISO 8601 문자열이고 끝의 `Z` 가 UTC 를 뜻합니다[2]. Mac 절대 시각이나 Unix 시각 같은 숫자가 아니라서 기준을 따로 맞출 필요는 없지만, 현지 시각으로 보려면 시간대를 따로 적용합니다. 필드 이름으로 보면 `timestamp` 는 보낸 시각, `edited_timestamp` 는 수정한 시각, `call.ended_timestamp` 는 통화가 끝난 시각입니다[2]. 이 값들은 레코드가 캐시에 저장된 시각과 다릅니다. 캐시 파일의 파일 시스템 시각은 앱이 캐시를 쓴 때를 가리킬 뿐이라서, 메시지를 보낸 시각으로 쓰지 않습니다. 시각 값 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

iOS 15 시험에서는 지운 메시지를 시험한 도구 어느 것도 되살리지 못했고, 도구 하나는 메시지를 아예 파싱하지 못했습니다[1]. 그래서 도구 하나의 결과만으로 "메시지 없음" 이라고 쓰지 않고 캐시 파일을 직접 열어 확인합니다. 도구끼리 결과를 맞춰 보는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)에 있습니다.

`fsCachedData` 의 한 파일에는 여러 줄의 JSON 이 들어 있고[2], 메시지 수를 셀 때는 같은 `id` 가 여러 줄이나 파일에 겹쳐 있는지 먼저 확인합니다. `Cache.db` 는 내부 구조를 설명한 공개 자료가 없어 실제 파일로 확인해야 합니다[1]. `mmkv.default` 는 MMKV 저장소라서 키와 값을 읽는 방법은 공개되어 있지만[3], 디스코드가 어떤 키를 쓰는지는 실제 파일로 확인해야 합니다. MMKV 형식은 [iOS 지갑 앱](https://urock-ailab.github.io/forensics-handbook/crypto/02-artifacts/mobile/ios-wallets.html) 에서 다룹니다. iLEAPP 의 경로는 파일 시스템 추출 기준이고, 로컬 백업에 이 캐시 파일들이 들어가는지는 공개 자료가 없습니다. 백업만 확보했다면 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../01-foundations/backups/local-backup/index.md)의 `Manifest.db` 에서 먼저 파일이 있는지 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`kv-storage` 아래의 `a` 파일은 확장자가 없어서, 앞 16바이트로 SQLite 인지 먼저 확인합니다. SQLite 파일은 `SQLite format 3` 과 NUL 한 바이트로 시작합니다. `fsCachedData` 의 파일은 JSON 텍스트라서 `{` 로 시작하는 줄이 이어집니다. 아래는 명세로 만든 예시이고 실제 기기에서 나온 값이 아닙니다.

```
a 파일 앞 16바이트
53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.

fsCachedData 파일 한 줄의 앞부분
7B 22 69 64 22 3A 22 ...                          {"id":"...
```

### 질의로 한 번

```sql
-- kv-storage/@account.../a 에서 실행한다
SELECT rowid, length(data) AS len, hex(substr(data, 1, 16)) AS head16
FROM messages0
LIMIT 20;
```

`head16` 으로 `data` 가 어떤 형식으로 들어 있는지 먼저 보고, 텍스트라면 `CAST(data AS TEXT)` 로 필드를 확인합니다.

### 공개 도구로 한 번

iLEAPP 의 디스코드 분석기는 `fsCachedData` 와 `a` 파일에서 메시지를 뽑고 첨부와 캐시 이미지를 함께 보여 줍니다[2]. 보고서의 메시지 수를 `id` 기준 중복 제거 수와 맞춰 보고, `edited_timestamp` 가 있는 메시지가 보고서에 수정 표시로 나오는지 확인합니다.

## 교차 검증

메시지가 오간 시각에 디스코드 알림이 떴는지는 [알림 기록 (Notifications)](../app-usage/notifications.md)에서, 그 시각에 앱을 쓰고 있었는지는 [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../app-usage/biome/index.md)에서 봅니다. 통화 시간대에 앱이 데이터를 얼마나 썼는지는 [앱별 데이터 사용량 (DataUsage.sqlite)](../network/data-usage.md)과 맞춰 봅니다. 캐시 이미지가 사진 보관함에도 저장됐는지는 [사진 보관함 (Photos Library)](../media/photos/index.md)에서 찾고, 다른 연락 수단과 시간순으로 합치는 방법은 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md)에 있습니다.

## 실습

공개된 iOS 시험 이미지 가운데 디스코드가 설치된 것으로 아래를 풀어 봅니다.

1. `fsCachedData` 의 모든 줄에서 메시지 `id` 를 모아 중복을 뺀 수와 전체 줄 수를 비교해 봅니다.
2. `edited_timestamp` 가 있는 메시지를 찾아 `timestamp` 와의 차이를 계산해 봅니다.
3. 첨부가 있는 메시지 하나를 골라 `proxy_url` 로 `SDImageCache` 에 캐시된 이미지를 찾아봅니다.

## 참고 문헌

1. digital-forensics.it, "iOS 15 Image Forensics Analysis and Tools Comparison - Communication and Social Networking Apps" (2023-11) — https://blog.digital-forensics.it/2023/11/ios-15-image-forensics-analysis-and.html
2. abrignoni/iLEAPP, `scripts/artifacts/discordChats.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/discordChats.py
3. abrignoni/iLEAPP, `scripts/mmkv_parser.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/mmkv_parser.py
