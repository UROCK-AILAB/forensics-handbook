---
title: "슬랙과 팀즈"
parent: "아티팩트 · 메신저"
nav_order: 920
---

# 슬랙과 팀즈 (Slack·Teams)

## 한 줄 요약

업무용 메신저인 슬랙과 팀즈는 둘 다 Core Data 형식(표 이름이 Z 로 시작)의 SQLite 에 메시지를 남기지만, 슬랙은 시각을 Unix 초로, 팀즈는 Mac 절대 시각(2001-01-01 기준 초)으로 저장해서 표 모양만 보고 시각 기준을 짐작하면 안 됩니다.

## 무엇을 기록하나 · 왜 생기나

두 앱 모두 워크스페이스나 조직의 대화를 기기에 받아 두고 화면에 보여 주는데, 그 사본이 앱 컨테이너의 DB 에 남습니다. 슬랙 DB 에는 메시지·사용자·채널·파일·워크스페이스 정보가 있고[2], 팀즈 DB 에는 메시지·대화방·사용자와 함께 통화 기록과 위치 공유 카드가 메시지 속성으로 들어 있습니다[3]. 업무 계정이라 조직의 서버에도 같은 기록이 있을 수 있어서, 기기 기록은 조직 쪽 기록과 맞춰 보는 출발점이 됩니다.

## 위치와 버전별 차이

### 슬랙

번들 ID 는 `com.tinyspeck.chatlyio` 입니다[1]. DB 는 옛 구조와 새 구조 두 가지가 있습니다[2]. 어느 앱 버전부터 새 구조로 바뀌었는지는 공개 자료가 없어서 아래 표는 구조 기준으로 나눕니다.

| 구조 | 찾는 위치(파일 시스템 추출 기준) | 표 |
|---|---|---|
| 옛 구조 | `*/mobile/Containers/Data/Application/*/Library/Application Support/Slack/*/*/main_db*` | 접두어 `ZSLK` 또는 `ZSLKDEPRECATED` |
| 새 구조 | `*/mobile/Containers/Shared/AppGroup/*/*/ModelDatabase/db.sqlite*` | `ZCOREDATAMESSAGE` 등 |

옛 구조의 전체 경로는 아래와 같고, `<DB-ID>` 폴더 이름이 워크스페이스 식별자입니다[1]. 새 구조는 앱 데이터 컨테이너가 아니라 앱 그룹 컨테이너에 있어서[2] 찾는 곳이 다릅니다. 컨테이너 종류는 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../01-foundations/value-decoding/bundle-id-app-group.md)에서 다룹니다.

```
/private/var/mobile/Containers/Data/Application/<UUID>/Library/Application Support/Slack/<DB-ID>/Database/main_db
```

### 팀즈

DB 와 내려받은 이미지는 앱 그룹 컨테이너에 있습니다[3].

```
*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/*/Skype*.sqlite*
*/mobile/Containers/Shared/AppGroup/*/SkypeSpacesDogfood/Downloads/*/Images/*
```

`SkypeSpacesDogfood` 는 폴더 이름 그대로입니다. 개인용과 업무용을 합친 새 팀즈에서도 같은 이름을 쓰는지, 두 앱이 iOS 버전에 따라 달라지는지는 공개 자료가 없어 검체에서 확인합니다.

## 구조

### 슬랙 표

주요 표와 칸은 아래와 같습니다[2]. 옛 구조 표 이름의 `…` 자리에 `ZSLK` 나 `ZSLKDEPRECATED` 가 붙습니다.

| 옛 구조 표 | 새 구조 표 | 읽는 칸 |
|---|---|---|
| `…MESSAGE` | `ZCOREDATAMESSAGE` | `ZTIMESTAMP`, `ZUSERID`, `ZTEXT`, 옛 구조는 `ZCHANNELID`·`ZFILEIDS`, 새 구조는 `ZCONVERSATIONID` |
| `…COREDATAUSER` | `ZCOREDATAUSER` | `ZREALNAME`, `ZTSID`, 옛 구조는 `ZFIRSTNAME`·`ZLASTNAME`·`ZTIMEZONE`, 새 구조는 `ZISME`·`ZTEAMID`·`ZEMAIL`·`ZPHONE` 등 |
| `…BASECHANNEL` | `ZCOREDATACONVERSATION` | `ZNAME`, `ZTSID`, `ZCREATED`, 옛 구조는 `ZTSID1`·`ZPURPOSETEXT`·`ZTOPICTEXT`, 새 구조는 `ZFIRSTMESSAGETIMESTAMP`·`ZTYPE`·`ZIMUSERID` |
| `…FILE` | | `ZTITLE`, `ZSIZE`, `ZPERMALINKURL`, `ZPRIVATEDOWNLOADURL` |
| `…TEAM` | | `ZNAME`, `ZDOMAIN`, `ZAUTHUSERID`, `ZTSID` |

슬랙 ID 는 첫 글자로 종류를 알 수 있어서, 사용자는 `U`, 채널은 `C`, 1:1 대화(DM)는 `D` 로 시작합니다[1]. 메시지의 `ZUSERID` 를 사용자 표의 `ZTSID` 와 이어 이름을 찾습니다. 2018년 당시 `main_db` 의 표는 21개였습니다[1].

### 팀즈 표

| 표 | 읽는 칸 |
|---|---|
| `ZSMESSAGE` | `ZARRIVALTIME`, `ZCOMPOSETIME`, `ZIMDISPLAYNAME`, `ZCONTENT`, `ZFROM`, `ZTHREADID`, `ZTHREADTYPE`, `ZTS_MESSAGEBASETYPE`, `ZTS_MESSAGECONTENTTYPE`, `ZTS_ISSENTBYME`, `ZTSID` |
| `ZTHREAD` | `ZTSID`, `ZTHREADTOPIC` |
| `ZUSER` | `ZDISPLAYNAME`, `ZTELEPHONENUMBER`, `ZTS_LASTSYNCEDAT` |
| `ZDEVICECONTACTHASH` | `ZDISPLAYNAME`, `ZEMAIL`, `ZPHONENUMBER` |
| `ZMESSAGEPROPERTIES` | `ZPROPERTIES` |

메시지는 `ZSMESSAGE.ZTHREADID = ZTHREAD.ZTSID` 로 대화방과 잇고, `ZCONTENT` 는 HTML 이라서 이모지도 `itemtype="http://schema.skype.com/Emoji"` 가 붙은 img 태그로 들어 있습니다[3]. `ZDEVICECONTACTHASH` 는 기기 연락처와 관련된 표입니다[3].

통화 기록과 위치 공유는 `ZMESSAGEPROPERTIES.ZPROPERTIES` 에 plist 로 들어 있고, `ZSMESSAGE.ZTSID` 로 메시지와 잇습니다[3]. 이 plist 는 NSKeyedArchiver 형식이고[3], 원리는 [속성 목록 파일 (plist·NSKeyedArchiver)](../../01-foundations/data-formats/plist.md)에 있습니다.

| plist 키 | 안의 키 |
|---|---|
| `call-log` | `startTime`, `connectTime`, `endTime`, `callDirection`, `callType`, `callState`, `originator`, `target`, `originatorParticipant.displayName`, `targetParticipant.displayName` |
| `cards` | `selectAction.url`, `selectAction.title`, 그리고 card id 안의 위도·경도·`expiresAt`·`deviceId` |

## 증거로서 의미

**증명하는 것.** 슬랙 메시지 행은 이 기기의 슬랙 DB 에 어느 채널(또는 대화)에서 어떤 사용자 ID 가 보낸 것으로 기록된 메시지가 이 시각과 함께 남아 있다는 사실을 보여 주고, 파일 표로 공유된 파일의 제목·크기·링크를 알 수 있습니다[2]. 팀즈에서는 `ZTS_ISSENTBYME` 로 이 계정이 보낸 메시지를 가를 수 있고, `call-log` 로 통화의 방향·종류·상태와 시작·연결·종료 시각을, `cards` 로 공유된 위치와 만료 시각을 볼 수 있습니다[3]. `ZTS_ISSENTBYME` 의 뜻은 칸 이름에서 나온 것이라, 보낸 것이 분명한 메시지와 한 번 맞춰 봅니다.

**증명하지 못하는 것.** 파일 표의 링크는 파일이 공유됐다는 기록일 뿐이라서, 이 기기에서 그 파일을 열거나 내려받았는지는 따로 확인해야 합니다. 팀즈의 위치 카드는 위치를 공유한 메시지의 기록이지 그 시각에 이 기기가 그 자리에 있었다는 기록이 아닙니다. 두 앱 모두 기기에 받아 둔 사본만 보이기 때문에, 행이 없다고 대화가 없었다고 볼 수 없습니다.

## 시각 해석

두 앱은 표 모양이 비슷해도 시각 기준이 다릅니다[2][3].

| 앱 | 칸 | 기준 | iLEAPP 변환 |
|---|---|---|---|
| 슬랙 | `ZTIMESTAMP` 등 | Unix 초(1970-01-01 기준) | `datetime(col, 'unixepoch')` |
| 팀즈 | `ZARRIVALTIME`, `ZTS_LASTSYNCEDAT` | Mac 절대 시각(2001-01-01 기준 초) | `datetime('2001-01-01', col \|\| ' seconds')` |

슬랙 옛 구조의 첨부 표에서는 `ZTIMESTAMPNUMBER` 칸을 씁니다[2]. 두 기준 모두 UTC 라서, 현지 시각은 바꾼 뒤에 시간대를 따로 적용합니다. 팀즈의 `ZARRIVALTIME` 과 `ZCOMPOSETIME` 은 이름대로라면 도착 시각과 작성 시각이지만 iLEAPP 는 `ZARRIVALTIME` 만 변환하고 통화·위치 보고서에서는 `ZCOMPOSETIME` 을 바꾸지 않고 그대로 읽어서[3], `ZCOMPOSETIME` 은 기준을 검체에서 확인한 뒤에 씁니다. 시각 값 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

## 함정과 한계

Core Data 표라서 시각이 Mac 절대 시각이라고 넘겨짚으면 슬랙 시각이 31년 가까이 어긋납니다. 슬랙은 앱 버전에 따라 표 접두어와 DB 위치가 바뀌므로[2], 한 경로만 보면 DB 를 놓칠 수 있어 두 구조를 모두 찾아봅니다.

2018년 당시 슬랙의 `Library/Caches/com.tinyspeck.chatlyio/Cache.db` 네트워크 캐시의 `cfurl_cache_blob_data` 표에 로그인 정보가 평문으로 남았습니다[1]. 지금 버전에서도 그런지는 검체에서 확인하고, 캐시 파일에 민감한 값이 남을 수 있다고 보고 증거를 다룰 때 접근을 제한합니다. 이미지 캐시는 2018년 기준으로 `Library/Application Support/Library/Caches/default/com.hackemist.SDWebImageCache.default/` 에 있었습니다[1]. 팀즈의 내려받은 이미지는 CacheFile plist 가 이미지 URL 과 로컬 경로를 이어 줍니다[3].

위 경로는 파일 시스템 추출 기준이고, 로컬 백업에 이 파일들이 들어가는지는 공개 자료가 없습니다. 백업만 확보했다면 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../01-foundations/backups/local-backup/index.md)의 `Manifest.db` 에서 먼저 파일이 있는지 확인합니다. 지운 메시지를 찾는 일반적인 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)에 있습니다.

## 직접 분석해 보기

### 헥스로 한 번

같은 크기의 정수라도 기준에 따라 전혀 다른 날짜가 됩니다. 아래는 명세로 만든 예시 값이고 실제 검체에서 나온 값이 아닙니다.

| 앱·칸 | 예시 값 | Unix 초로 읽으면(UTC) | Mac 절대 시각으로 읽으면(UTC) |
|---|---|---|---|
| 슬랙 `ZTIMESTAMP` | 1780000000 | 2026-05-28 20:26:40 | 2057-05-28 20:26:40 |
| 팀즈 `ZARRIVALTIME` | 800000000 | 1995-05-09 06:13:20 | 2026-05-09 06:13:20 |

수집 시각에서 먼 쪽이 나오면 기준을 잘못 고른 것입니다.

### 질의로 한 번

```sql
-- 슬랙 새 구조 (db.sqlite)
SELECT datetime(m.ZTIMESTAMP, 'unixepoch') AS sent_utc,
       m.ZUSERID, u.ZREALNAME, m.ZCONVERSATIONID, m.ZTEXT
FROM ZCOREDATAMESSAGE m
LEFT JOIN ZCOREDATAUSER u ON u.ZTSID = m.ZUSERID
ORDER BY m.ZTIMESTAMP DESC
LIMIT 20;

-- 팀즈 (Skype*.sqlite)
SELECT datetime('2001-01-01', m.ZARRIVALTIME || ' seconds') AS arrival_utc,
       m.ZIMDISPLAYNAME, m.ZTS_ISSENTBYME, t.ZTHREADTOPIC, m.ZCONTENT
FROM ZSMESSAGE m
LEFT JOIN ZTHREAD t ON t.ZTSID = m.ZTHREADID
ORDER BY m.ZARRIVALTIME DESC
LIMIT 20;
```

### 공개 도구로 한 번

iLEAPP 의 슬랙 분석기는 옛 구조와 새 구조를 모두 읽고[2], 팀즈 분석기는 메시지·사용자·통화 기록·위치 카드와 내려받은 이미지를 보고서로 만듭니다[3]. 위 질의로 본 최근 메시지의 시각이 보고서와 같은지, 보고서의 통화 기록 수가 `call-log` 가 있는 행 수와 같은지 맞춰 봅니다. 도구 결과를 검증하는 방법은 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)에 있습니다.

## 교차 검증

메시지 시각에 앱 알림이 떴는지는 [알림 기록 (Notifications)](../app-usage/notifications.md)에서, 그 시각에 앱을 쓰고 있었는지는 [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../app-usage/biome/index.md)에서 봅니다. 파일을 올리거나 받은 시간대의 송수신량은 [앱별 데이터 사용량 (DataUsage.sqlite)](../network/data-usage.md)과 맞춰 보고, 업무 자료가 밖으로 나갔는지 조사한다면 [자료를 밖으로 보냈나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md)의 흐름을 따릅니다. 조직 서버 쪽 기록을 받는 방법은 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../03-techniques/acquisition/cloud-data.md)에 있습니다.

## 실습

공개된 iOS 검체 가운데 슬랙이나 팀즈가 설치된 것으로 아래를 풀어 봅니다.

1. 슬랙 DB 가 옛 구조인지 새 구조인지, 표 접두어가 `ZSLK` 인지 `ZSLKDEPRECATED` 인지 확인해 봅니다.
2. 슬랙 메시지의 `ZUSERID` 첫 글자가 모두 `U` 인지, 대화 ID 가운데 `D` 로 시작하는 것이 몇 개인지 세어 봅니다.
3. 팀즈 `call-log` 하나를 골라 `startTime`·`connectTime`·`endTime` 으로 통화 시간을 계산해 봅니다.

## 참고 문헌

1. Alexis Brignoni, "Finding Slack app messages in iOS" (2018-10-14) — https://abrignoni.blogspot.com/2018/10/finding-slack-app-messages-in-ios.html
2. abrignoni/iLEAPP, `scripts/artifacts/slack.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/slack.py
3. abrignoni/iLEAPP, `scripts/artifacts/teams.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/teams.py
