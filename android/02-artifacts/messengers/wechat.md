---
title: "위챗"
parent: "아티팩트 · 메신저"
nav_order: 1020
---

# 위챗 (WeChat)

위챗 앱은 메시지·연락처·대화 목록을 계정 폴더 아래 `EnMicroMsg.db` 에 남기는데, 이 DB 는 SQLCipher 로 암호화돼 있어 일반 SQLite 도구로는 열리지 않습니다.

## 무엇을 기록하나 · 왜 생기나

위챗 앱(패키지 이름 `com.tencent.mm`)은 계정마다 폴더를 하나 두고, 그 안의 `EnMicroMsg.db` 에 메시지, 연락처, 대화 목록, 계정 정보를 표로 나눠 저장합니다[1]. 같은 계정 폴더 아래에는 대화에서 오간 이미지, 음성, 스티커 파일이 따로 쌓입니다[1]. 앱 설정 XML 에는 계정 식별값(uin)이 있어서, 이 값으로 어느 폴더가 어느 계정의 것인지를 잇습니다[1].

이 페이지의 사실은 공개 도구 ALEAPP 의 위챗 모듈이 적어 둔 설명을 바탕으로 합니다. 그 모듈의 시험 이미지는 하나뿐이고, 위챗(Tencent) 공식 문서로 확인한 내용은 없습니다. 암호화된 DB 를 여는 키를 만드는 방법은 이 핸드북에서 다루지 않고, 암호화가 분석에 어떤 제약을 주는지만 설명합니다.

## 위치와 버전별 차이

경로는 모두 앱 데이터 폴더 기준이고, 앱 데이터 폴더의 구조는 [앱 데이터 폴더 구조](../../01-foundations/storage/app-data-layout.md) 에서 다룹니다.

| 흔적 | 경로 | 내용 |
|---|---|---|
| 메시지 DB | `MicroMsg/<계정 폴더>/EnMicroMsg.db` | 메시지·연락처·대화 목록·계정 정보 |
| 계정 식별값 | `shared_prefs/auth_info_key_prefs.xml` | uin. 없으면 `shared_prefs/system_config_prefs.xml` |
| 이미지 | `MicroMsg/<계정 폴더>/image2/` | 원본 이미지와 `th_` 로 시작하는 썸네일 |
| 음성 | `MicroMsg/<계정 폴더>/voice2/` | 음성 메시지 파일 |
| 스티커 | `MicroMsg/<계정 폴더>/emoji/` | 스티커 파일 |

계정 폴더 이름은 계정 식별값(uin)에서 만든 32자리 해시이고, ALEAPP 은 설정 XML 의 uin 으로 DB 폴더와 계정을 이어 붙입니다[1]. 해시를 어떻게 계산하는지는 이 페이지에서 다루지 않습니다.

앱 데이터 폴더는 시스템이 다른 앱의 접근을 막는 앱 내부 저장소라서 일반 adb 권한으로는 바로 읽을 수 없고, Android 10(API 29) 이상에서는 이 위치가 암호화됩니다[2]. 이 암호화는 저장 공간 수준의 암호화이고 `EnMicroMsg.db` 자체의 SQLCipher 암호화와는 따로입니다. 저장 공간 암호화는 [저장 공간 암호화](../../01-foundations/storage/encryption/index.md), 확보 방법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

| 항목 | 확인된 범위 |
|---|---|
| 시험 이미지 | kevin_pocox7_a15 하나(Android 15, POCO X7) |
| 시험 이미지의 행 수 | 메시지 602, 연락처 32, 대화 7, 계정 97 |
| 삼성 기기 | 시험 기록 없음 |
| 위챗 앱 버전 | 적혀 있지 않음 |

시험 이미지가 하나뿐이고 앱 버전도 적혀 있지 않아서, 앱 버전에 따라 암호 방식이나 DB 이름이 바뀌었는지는 확인하지 못했습니다[1]. 삼성 One UI 기기에서 경로나 구조가 다르다는 자료도 찾지 못했습니다.

## 구조

### 암호화된 DB

`EnMicroMsg.db` 는 SQLCipher 로 암호화된 DB 라서 일반 SQLite 도구로는 열리지 않습니다[1]. 공개 도구 ALEAPP 은 sqlcipher3 라이브러리가 설치돼 있을 때만 이 DB 를 여는 모듈을 돌립니다[1]. 이 모듈은 키를 계산하는 방식의 출처를 대지 않고, 키가 맞으면 DB 가 열린다는 사실로만 확인한다고 적었습니다[1]. 아래 표·칸 설명은 DB 가 열린 뒤를 기준으로 합니다. SQLite 파일 구조 자체는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 에서 다룹니다.

### message 표

| 칸 | 뜻 |
|---|---|
| `msgId` | 메시지 ID |
| `createTime` | 메시지 시각, 유닉스 밀리초 |
| `isSend` | ALEAPP 은 1 을 "계정이 보냄" 으로 표시(출처 없음) |
| `talker` | 상대 위챗 ID 또는 그룹 ID |
| `type` | 메시지 종류 |
| `content` | 본문. 종류에 따라 XML 문서 |
| `imgPath` | 이미지 경로 |
| `status` | 상태 값 |

시험 이미지에서 `type` 이 1 인 행은 텍스트였고, 나머지 값의 행은 `content` 에 XML 문서가 들어 있었습니다[1]. `type` 전체 코드표의 공식 출처는 찾지 못했다고 모듈에 적혀 있습니다[1]. `content` 가 XML 이면 `title`·`des`·`url` 요소에서 제목·설명·링크를 읽고, 시험 이미지 602행 가운데 587행에서 읽을 수 있는 본문이, 461행에서 링크가 나왔습니다[1]. 나머지 15행은 `img` 요소가 든 이미지 행이었습니다[1].

### 그 밖의 표

`voiceinfo` 표의 `MsgLocalId`·`FileName` 칸은 음성 메시지와 `voice2` 폴더의 파일 이름을 잇습니다[1].

`rcontact` 표는 연락처 표이고 칸은 `username`(위챗 ID), `alias`, `nickname`, `conRemark`(메모 이름), `type`, `verifyFlag`, `createTime` 입니다[1]. 서비스·공식 계정도 개인 연락처와 같은 표에 들어 있습니다[1].

`rconversation` 표는 대화 목록이고 칸은 `conversationTime`, `username`, `msgCount`, `unReadCount`, `digest`, `digestUser`, `status` 입니다[1]. `digest` 는 대화 목록 화면에 보이는 마지막 메시지 미리보기입니다[1].

`userinfo` 표는 `id`, `value` 두 칸으로 된 키-값 표입니다[1]. 시험 이미지에서 `id` 2 는 위챗 ID, 4 는 표시 이름, 6 은 연결된 전화번호였지만, 전체 `id` 목록의 공식 출처는 없습니다[1].

### 미디어 파일

시험 이미지에서 `image2` 의 원본 크기 이미지는 wxgf 컨테이너였고 썸네일은 일반 JPEG 이었습니다[1]. `voice2` 의 음성 파일은 확장자가 amr 이지만 파일 안에는 SILK 헤더(`#!SILK_V3`)가 있었고, `emoji` 의 스티커 2개는 알려진 파일 서명과 맞지 않았습니다[1].

## 증거로서 의미

**증명하는 것.** `message` 표의 행은 그 시각에 그 대화 상대 또는 그룹과 오간 메시지를 앱이 기기에 저장했다는 기록입니다. `rconversation` 표는 기기에 어떤 대화가 목록으로 남아 있었는지와 메시지 수, 읽지 않은 수를 보여 주고, `userinfo` 표는 이 기기에 로그인한 위챗 계정의 ID 와 표시 이름을 보여 줍니다(`id` 뜻은 시험 이미지 하나에서 본 것)[1]. `voiceinfo` 표로 음성 메시지 행과 실제 음성 파일을 잇고 나면, 파일이 기기에 남아 있는지도 확인할 수 있습니다.

**증명하지 못하는 것.** `isSend` 가 1 이면 ALEAPP 이 "계정이 보냄" 으로 표시하지만, 이 뜻의 출처는 없다고 모듈에 적혀 있습니다[1]. 보고서에서 방향을 말할 때는 "ALEAPP 의 해석에 따르면" 처럼 근거의 범위를 함께 적거나, 앱에서 같은 동작을 재현해 확인합니다. 그룹 대화에서는 `talker` 칸에 그룹 ID 가 들어 있어서, 이 칸만으로는 그룹 안의 실제 보낸 사람을 알 수 없습니다[1]. `rcontact` 에 `conRemark`(메모 이름)가 있다고 해서 그 연락처와 일부러 연락했다는 뜻은 아니고, 서비스·공식 계정도 같은 표에 섞여 있습니다[1].

보고서에는 "이 사람에게 메시지를 보냈다" 보다 "이 시각에 이 대화 상대 ID 로 된 메시지 행이 있고, `isSend` 값은 1 이다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

| 값 | 위치 | 단위 |
|---|---|---|
| `createTime` | `message` 표 | 유닉스 밀리초 |
| `conversationTime` | `rconversation` 표 | 유닉스 밀리초 |
| `createTime` | `rcontact` 표 | 유닉스 밀리초(값이 있는 행만) |

유닉스 시각은 1970-01-01 UTC 기준이라서, 현지 시각으로 옮길 때는 기기의 [시간대와 시각 설정](../system-account/time-zone.md) 을 함께 확인합니다. `rcontact` 표의 `createTime` 은 값이 비어 있는 행도 있어서, 값이 있는 행만 밀리초로 바꿉니다[1]. `conversationTime` 이 어떤 동작에서 바뀌는지는 공식 설명이 없습니다. 시각 값 읽는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

## 함정과 한계

DB 가 열리지 않는다고 해서 파일이 손상됐다고 판단하지 않습니다. `EnMicroMsg.db` 는 원래 암호화된 DB 라서 일반 SQLite 도구로는 열리지 않습니다[1]. 반대로 공개 도구로 DB 가 열렸다면 키가 맞았다는 뜻일 뿐이고, 도구가 키를 어떻게 계산했는지는 출처가 없다는 점을 보고서에 함께 적습니다[1].

계정이 여럿이면 `MicroMsg` 아래 계정 폴더도 여럿이고, 설정 XML 의 uin 과 어느 폴더가 이어지는지를 먼저 정리하지 않으면 다른 계정의 대화를 섞게 됩니다. ALEAPP 은 DB 를 읽을 때 `-wal`·`-shm`·`-journal` 짝 파일도 함께 경로에 넣으니, 확보할 때 짝 파일을 모두 복사하고 사본을 엽니다.

미디어 파일은 확장자와 실제 형식이 다를 수 있어서, 시험 이미지에서도 amr 확장자의 음성 파일에 SILK 헤더가 있었고 원본 이미지는 wxgf 컨테이너였습니다[1]. 파일 종류는 확장자가 아니라 파일 앞부분의 서명으로 판단합니다.

`type` 코드표와 `userinfo` 의 `id` 목록은 시험 이미지 하나에서 본 값이라 다른 앱 버전에서는 뜻이 다를 수 있습니다[1]. 시험 이미지가 삼성 기기가 아니었다는 점도 한계입니다.

앱을 지우면 앱 전용 저장소의 파일도 지워져서[2] 이 페이지의 흔적이 남지 않습니다. 이때는 [설치된 앱](../app-usage/packages/index.md) 과 [앱 사용 기록](../app-usage/usagestats/index.md) 으로 앱이 있었는지를 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

먼저 `EnMicroMsg.db` 사본을 헥스 편집기로 열어 첫 16바이트를 봅니다. 일반 SQLite 파일이면 아래처럼 시작합니다. 아래는 SQLite 형식 명세로 만든 예시이고 특정 검체에서 나온 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

이 문자열로 시작하는지를 보면 일반 SQLite 도구로 열 수 있는 파일인지 빠르게 가를 수 있습니다.

다음으로 `voice2` 폴더의 음성 파일 하나를 열어 SILK 헤더를 찾습니다. `#!SILK_V3` 를 바이트로 적으면 아래와 같고, 이 예시는 문자열을 ASCII 로 옮겨 만든 것입니다.

```
23 21 53 49 4C 4B 5F 56 33   #!SILK_V3
```

ALEAPP 은 이 바이트열이 파일 맨 앞에 있는 경우와 앞에 `02` 한 바이트가 붙은 경우를 모두 SILK 로 봅니다[1]. 그래서 오프셋 0 만 보지 말고 앞부분 몇 바이트 안에서 찾고, 보이면 확장자가 amr 이어도 SILK 형식으로 다룹니다. `image2` 의 썸네일은 일반 JPEG 이었으니[1] 썸네일과 원본 파일의 앞부분을 나란히 열어 형식이 어떻게 다른지 비교해 봅니다.

### 공개 도구로 한 번

공개 도구 ALEAPP 의 위챗 모듈은 설정 XML 에서 uin 을 읽어 계정 폴더를 찾고, sqlcipher3 라이브러리가 있을 때 `EnMicroMsg.db` 를 열어 메시지·연락처·대화 목록·계정 정보와 미디어를 보고서로 내놓습니다[1]. DB 가 열린 뒤에는 SQLite 셸로 같은 값을 직접 뽑아 도구 결과와 맞춰 봅니다. 아래는 메시지 시각을 UTC 로 바꿔 보는 예입니다.

```sql
SELECT
  datetime(createTime / 1000, 'unixepoch') AS utc_time,
  talker, isSend, type, substr(content, 1, 100) AS content_head
FROM message
ORDER BY createTime;
```

도구 결과와 직접 확인한 값이 다를 때 가려내는 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 확인할 것 |
|---|---|
| [앱 사용 기록](../app-usage/usagestats/index.md) | 메시지 시각 앞뒤로 위챗 앱이 화면에 올라온 기록이 있는지 |
| [알림 기록](../app-usage/notification-history.md) | 받은 메시지 시각에 위챗 알림이 있었는지 |
| [설치된 앱](../app-usage/packages/index.md) | 앱 설치·업데이트 시각과 DB 기록이 시작된 시점 |
| [연락처](../communications/contacts.md) | `userinfo` 의 전화번호나 `rcontact` 항목이 기기 연락처와 겹치는지 |
| [미디어 저장소](../media/mediastore/index.md) | 대화 이미지를 공용 저장 공간에 저장했는지 |

여러 앱의 대화를 한 흐름으로 세우는 방법은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication.md) 와 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등) 가운데 위챗 앱 데이터가 든 Android 이미지를 골라 아래 질문을 풀어 봅니다.

1. `MicroMsg` 아래 계정 폴더가 몇 개이고, 설정 XML 의 uin 과 어떻게 이어지는지 정리합니다.
2. `EnMicroMsg.db` 가 일반 SQLite 머리 문자열로 시작하는지 헥스로 확인하고, 그 결과를 보고서에 어떻게 적을지 정합니다.
3. `voice2` 폴더의 파일마다 확장자와 파일 앞부분의 서명을 표로 비교합니다.
4. `rconversation` 의 `msgCount` 와 `message` 표에서 같은 대화 상대로 센 행 수가 맞는지 확인하고, 다르면 까닭을 적습니다.
5. 그룹 대화 행 하나를 골라, `talker` 칸으로 말할 수 있는 것과 없는 것을 나눠 적습니다.

## 참고 문헌

1. ALEAPP, `weChat.py` — https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/weChat.py
2. Android Developers, "Access app-specific files" — https://developer.android.com/training/data-storage/app-specific
