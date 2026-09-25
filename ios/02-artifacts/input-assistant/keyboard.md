---
title: "키보드 입력 기록"
parent: "아티팩트 · 입력·음성 비서"
nav_order: 1070
---

# 키보드 입력 기록 (Keyboard)

## 한 줄 요약

아이폰 키보드는 자동 수정과 추천 단어를 위해 사용자가 입력한 낱말, 자주 쓴 이모지, 앱별 입력 문맥을 `Library/Keyboard` 폴더와 몇몇 설정 plist 에 남기고, 분석가는 여기서 "이 기기에서 이런 낱말을 입력한 적이 있다" 는 흔적과 대화별 입력 문맥의 시각을 얻을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

키보드 입력 기록 (Keyboard) 은 기기 키보드가 사용자의 입력 습관을 배우면서 쌓는 자료입니다. 한 파일에 모든 기록이 모여 있지 않고, 역할에 따라 여러 파일로 나뉘어 있습니다. 동적 어휘 파일에는 사용자가 자주 입력한 낱말이 쌓이고, 사용 통계 DB 에는 키와 값, 그리고 만든 시각·고친 시각 칸이 있지만 키와 값에 무엇이 들어가는지 설명한 자료는 없고, 자동 수정 거절 DB 에는 입력한 글자와 그에 대한 자동 수정이 남습니다. 이모지 적응 DB 는 어떤 글자 뒤에 어떤 이모지를 골랐는지를 담는 것으로 보이지만, 칸의 뜻을 설명한 자료는 찾지 못했습니다.

앱 쪽에도 흔적이 생깁니다. `UITextInputContextIdentifiers.plist` 에는 입력 문맥 식별자별로 키보드 언어와 시각이 남고, 식별자 형식은 앱이 정합니다. 메신저 앱은 이 식별자에 대화방 식별자를 넣어서 "어느 대화방의 입력창과 관련된 기록인가" 를 보여 줄 수 있습니다 [2].

키보드가 입력을 도우려고 쌓는 자료라서, 입력한 문장을 순서대로 적은 기록(키 로그)으로 읽으면 안 됩니다.

## 위치와 버전별 차이

파일시스템 추출에서는 사용자 영역의 `mobile/Library/Keyboard/` 아래에 파일이 있고, iLEAPP 는 이 자리를 `*/mobile/Library/Keyboard/...` 형식으로 찾습니다 [1]. 로컬 백업에서는 키보드 파일이 `KeyboardDomain` 도메인 아래 `Library/Keyboard/` 로 보이지만, 이 도메인이 기기의 어느 경로에 대응하는지는 확인하지 못했습니다(확인 범위: iOS 27.0). 백업 도메인과 상대 경로를 읽는 법은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에 있습니다.

| 파일 | 담는 것 | iLEAPP 시험 표본의 iOS 범위 | iOS 27.0 로컬 백업에서 |
|---|---|---|---|
| `*-dynamic.lm/dynamic-lexicon.dat` | 동적 어휘(자주 입력한 낱말) | 12.4 ~ 17.6.1 [1] | 보지 못함 |
| `app_usage_database.plist` | 앱별 키보드 사용 | 12.4 ~ 16.5 [1] | 보지 못함 |
| `user_model_database.sqlite` | 키보드 사용 통계 | 13.3.1 ~ 18.7.8 [1] | 있음 |
| `VulgarWordUsage.db` | 비속어 사용 | 17.6.1·18.0·18.7.8 에서 모두 0행 [1] | 보지 못함 |
| `AutocorrectionRejections.db` | 자동 수정·인라인 완성 거절 | iOS 17.1 이후 11개 이미지에 모두 있음, 16.5.1 이하 10개에는 없음. 가장 최근 표본은 26.5.2 [1] | 보지 못함 |
| `DynamicPhraseLexicon_ko_KR.db` | 언어별 어구 사전으로 보임 | 다룬 자료 없음 | 있음 |
| `emoji_adaptation.db` | 이모지 적응 | 다룬 자료 없음 | 있음 |

마지막 칸은 iOS 27.0 에서 만든 암호화하지 않은 로컬 백업의 `KeyboardDomain` 을 본 결과입니다(확인 범위: iOS 27.0). 이 도메인에는 항목이 6개 있었고 표 이름을 확인한 DB 는 3개였습니다. "보지 못함" 은 관찰 메모에 없다는 뜻이고, 백업에 들어가지 않는다는 뜻인지 메모가 적지 않은 것인지는 가리지 못했습니다. `AutocorrectionRejections.db` 의 경우 iLEAPP 도 표본의 분포가 도입 시점을 밝힌 것은 아니라고 적었습니다 [1].

키보드 폴더 밖에서 함께 볼 자리는 다음과 같습니다(모두 확인 범위: iOS 27.0).

| 백업 경로 | 볼 것 |
|---|---|
| `HomeDomain :: Library/Preferences/.GlobalPreferences.plist` | `AppleKeyboards`, `ApplePasscodeKeyboards`, `AppleKeyboardsExpanded`, `AddingEmojiKeybordHandled`, `AppleLanguages`, `AppleLocale` — 설치한 키보드와 언어 |
| `HomeDomain :: Library/Preferences/UITextInputContextIdentifiers.plist` | 입력 문맥 식별자(키 이름은 가려져 있고 값은 str 과 datetime 이 섞여 있음) |
| `HomeDomain :: Library/Preferences/com.apple.EmojiPreferences.plist` | `EMFDefaultsKey` 아래 `EMFRecentsKey`, `EMFUsageHistoryKey` 등, `GenmojiSuggestions` |
| `HomeDomain :: Library/Application Support/CloudDocs/session/containers/com.apple.TextInput.plist` | `com.apple.InputMethodKit.UserDictionary`, `com.apple.InputMethodKit.TextReplacementService` 등 텍스트 대치와 이어진 iCloud 컨테이너 |
| `com.apple.Accessibility.plist` | `SpeakAutoCorrectionsEnabledByiTunes`, `FullKeyboardAccessEnabled` |
| `com.apple.CloudSubscriptionFeatures.cache.plist` | `ai.keyboard.emoji-generation` |

앱 컨테이너 쪽 입력 문맥 파일은 파일시스템 추출 기준으로 `*/Containers/Data/Application/*/Library/Preferences/UITextInputContextIdentifiers.plist` 에 앱마다 하나씩 있습니다 [2]. 받아쓰기 설정 키(`Dictation Enabled`, `Dictation Allowed`)는 [시리](siri.md) 에서 다룹니다.

## 구조

### 동적 어휘와 앱 사용 plist

`dynamic-lexicon.dat` 는 구조가 공개되지 않은 바이너리 파일입니다. iLEAPP 도 구조를 풀지 않고, 파일을 UTF-8 로 읽어 출력 가능한 글자가 3자 이상 이어진 문자열만 뽑으며 `DynamicDictionary-9` 라는 문자열은 뺍니다 [1]. 그래서 결과에는 낱말만 있고 시각 칸이 없습니다.

`app_usage_database.plist` 에는 앱마다 항목 목록이 있고, 각 항목에 `startDate`, `appTime`, `keyboardTimes` 가 있습니다. iLEAPP 는 `startDate` 를 날짜 문자열로 읽지만, 칸의 단위와 뜻이 문서화되지 않아 값을 저장된 그대로 보고한다고 적었습니다 [1].

### 사용 통계 DB

`user_model_database.sqlite` 에는 다음 표가 있습니다(확인 범위: iOS 27.0).

```
properties: ROWID, key, value
usermodeldurablerecords: ROWID, key, value, creation_date, last_update_date, journaled
usermodeltransientrecords: ROWID, key, input_mode, value, secondary_value, real_value, properties, last_update_date, journaled
sqlite_sequence: name, seq
```

iLEAPP 는 `usermodeldurablerecords` 의 `key`, `value`, `creation_date`, `last_update_date` 를 읽습니다 [1]. `usermodeltransientrecords` 는 읽지 않고, 이 표의 칸 뜻을 설명한 자료는 찾지 못했습니다.

### 자동 수정 거절 DB

`AutocorrectionRejections.db` 의 `rejections` 표 칸은 `typed`, `correction`, `hard_rejections`, `soft_rejections`, `performed_count`, `last_hard_rejection`, `last_soft_rejection`, `journaled` 입니다 [1]. DB 안의 CREATE TABLE 설명에 따르면 `typed` 는 사용자가 처음 입력한 것이고, `correction` 은 수행되었거나 거절된 자동 수정이며, `performed_count` 는 수정을 받아들인(hard acceptance) 횟수입니다 [1]. 소프트 거절과 하드 거절이 어떻게 다른지는 스키마에 정의되어 있지 않습니다 [1]. 같은 DB 의 `inline_completion_rejections` 표도 칸이 같고, 여기서 `correction` 은 수행되었거나 거절된 인라인 완성입니다 [1]. iLEAPP 가 시험한 11개 이미지는 스키마가 모두 같았습니다(`properties.version` 2) [1].

### 비속어 사용 DB

`VulgarWordUsage.db` 의 `vword_usage` 표 칸은 `last_use_timestamp`, `app`, `recipient`, `vword`, `word_reading`, `usage_count`, `journaled` 입니다 [1]. 칸 이름으로는 앱과 받는 사람까지 담을 수 있어 보이지만, 값이 채워진 표본이 없어 실제 모습은 확인되지 않았습니다 [1].

### iOS 27.0 에서 본 두 DB

아래 두 DB 는 iOS 27.0 백업에서 표와 칸 이름만 확인했고, 칸의 뜻을 설명한 자료는 찾지 못했습니다(확인 범위: iOS 27.0).

```
DynamicPhraseLexicon_ko_KR.db
  Assist: Identifier, LastSeedValue, LastUpdateTime, Version
  Words: Identifier, Seed, Reading, Surface

emoji_adaptation.db
  emoji-ko: id, string
  interaction-ko: id, string_id, emoji_id, timestamp
  string-ko: id, string
  sqlite_sequence: name, seq
```

파일 이름과 표 이름 끝의 `ko_KR`, `-ko` 는 언어마다 따로 생긴다는 뜻으로 보이지만, 다른 언어의 파일은 확인하지 못했습니다.

### 입력 문맥 plist

`UITextInputContextIdentifiers.plist` 에서 `ID_<식별자>` 키는 키보드 언어를 담고, `ID_<식별자>_SETTIME` 키는 그 식별자의 시각을 담으며, 시각 키가 없는 식별자도 있습니다 [2]. 식별자 형식은 앱이 정합니다. Messenger 는 `<계정 id>_<스레드 id>_0` 형식을 쓰고 WhatsApp 은 대화의 JID 를 쓰는데, JID 서버 부분이 `s.whatsapp.net` 이면 1:1 대화, `g.us` 이면 그룹, `status@broadcast` 이면 상태, `newsletter` 이면 채널입니다 [2]. 앱 컨테이너 밖의 `mobile/Library/Preferences` 사본에는 `CK_`·`IM_` 형식 식별자가 있고, 해시값이라 대화로 풀리지 않습니다 [2].

iOS 27.0 백업의 `HomeDomain :: Library/Preferences/UITextInputContextIdentifiers.plist` 는 키 이름이 가려져 있었지만 값 종류가 str 과 datetime 으로 섞여 있어, 언어 키와 `_SETTIME` 시각 키가 짝을 이루는 구조와 어긋나지 않습니다(확인 범위: iOS 27.0). 메시지 앱 설정 plist 에는 `CKTextInputIdentifiersMigrated`, `__CK_clearTextInputContextIdentifierKey` 키도 있었습니다(확인 범위: iOS 27.0). plist 형식 자체는 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 을 봅니다.

## 증거로서 의미

**증명하는 것**

동적 어휘나 자동 수정 거절 DB 에 어떤 낱말이 있으면 이 기기의 키보드 자료에 그 낱말이 들어간 적이 있다고 말할 수 있습니다. 사용 통계 DB 의 `key`·`value` 는 무엇을 담는지 문서화되지 않아 [1], 낱말의 근거로 쓰지 않습니다. 자동 수정 거절 DB 의 `typed` 는 실제로 입력한 글자라서, 사건 관련 낱말·이름·계정명을 찾을 때 단서가 됩니다 [1]. 입력 문맥 plist 에 메신저 대화방 식별자와 시각이 있으면 그 시각 무렵 그 대화방의 입력창과 관련된 기록이 남았다고 말할 수 있고, 이 기록은 메시지 저장소가 아니라 앱 설정에 있어서 대화방을 지운 뒤에도 남을 수 있습니다 [2]. `.GlobalPreferences.plist` 의 `AppleKeyboards` 는 어떤 키보드를 설치했는지 보여 줍니다(확인 범위: iOS 27.0).

**증명하지 못하는 것**

키보드 기록만으로는 어떤 문장을 언제, 어느 앱에서, 누구에게 보냈는지 알 수 없습니다. 동적 어휘는 순서·시각·앱이 없는 낱말 모음이고 [1], 사용 통계의 두 시각은 칸 이름으로 보아 레코드를 만들고 고친 때이고, 낱말을 입력한 순간이라고 설명한 자료는 없습니다. 자동 수정 거절 DB 의 행 하나는 수정이 수행되었거나 거절되었다는 뜻이라서, 행이 있다는 것만으로 사용자가 수정을 거절했다고 단정할 수 없습니다 [1]. 입력 문맥의 시각이 대화를 연 때인지 키보드를 쓴 때인지는 밝혀지지 않았습니다 [2]. 누가 입력했는지도 이 기록으로는 가릴 수 없고, 이 문제는 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다른 기록과 함께 봅니다.

## 시각 해석

| 칸 | 기준 | 근거 |
|---|---|---|
| `usermodeldurablerecords.creation_date`, `last_update_date` | 유닉스 시각(1970-01-01 기준 초) | iLEAPP 가 `datetime(...,'unixepoch')` 로 바꿈 [1] |
| `rejections.last_hard_rejection`, `last_soft_rejection` | 유닉스 시각 초. 기본값 -1e10 은 시각 없음 | DB 스키마 설명 [1] |
| `vword_usage.last_use_timestamp` | Mac 절대 시각(2001-01-01 기준)으로 해석하지만 검증되지 않음 | iLEAPP 메모 [1] |
| `app_usage_database.plist` 의 `startDate` | 날짜 문자열로 읽음. 단위·뜻은 문서화 안 됨 | iLEAPP 메모 [1] |
| `UITextInputContextIdentifiers.plist` 의 `_SETTIME` | plist 날짜 값. 무엇이 바뀔 때 적히는지는 밝혀지지 않음 | [2] |
| `interaction-ko.timestamp`, `Assist.LastUpdateTime` | 확인하지 못함 | — |

유닉스 시각과 Mac 절대 시각은 978307200초 차이가 나서, 기준을 잘못 고르면 31년쯤 어긋난 날짜가 나옵니다. 두 기준을 가리는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다. 기준을 확인한 값은 모두 UTC 로 읽고, 보고서에서 현지 시각으로 바꿀 때는 [시간대와 시각 설정](../system-account/time-zone.md) 을 확인합니다.

입력 문맥 시각에 대해 iLEAPP 는 시험 이미지 4개에서 시각이 있는 Messenger 식별자 8개 모두 3~136초 뒤에 같은 스레드로 보낸 메시지가 뒤따랐다고 적었지만, 그 이미지에서 잰 상관일 뿐 일반 규칙은 아닙니다 [2].

## 함정과 한계

동적 어휘 결과는 구조를 푼 것이 아니라 문자열을 긁어 낸 것이라, 두 낱말이 이어져 보여도 실제로 이어서 입력했다는 뜻이 아닙니다 [1]. 자동 수정 거절 DB 의 `hard_rejections`·`soft_rejections` 는 차이가 정의되지 않았으니 보고서에서 두 값을 나눠 해석하지 않습니다 [1]. 비속어 사용 DB 는 공개 표본에서 값이 채워진 적이 없어, 행이 나오더라도 시각 기준부터 다시 검증해야 합니다 [1].

버전 문제도 큽니다. 동적 어휘의 iLEAPP 표본에는 iOS 18 이후가 없고 앱 사용 plist 표본은 16.5 가 마지막이라서 [1], 최신 iOS 에서 이 파일이 없을 때 "지웠다" 고 읽으면 안 됩니다. iOS 27.0 백업에서는 `DynamicPhraseLexicon_ko_KR.db` 와 `emoji_adaptation.db` 처럼 다룬 자료가 없는 DB 가 보였습니다(확인 범위: iOS 27.0).

사용자가 추가한 텍스트 대치(사용자 사전)는 `com.apple.TextInput.plist` 의 컨테이너 키와 푸시 주제 `com.apple.keyboardServices.textReplacementServer.aps` 로 보아 iCloud 와 이어져 있지만(확인 범위: iOS 27.0), 목록 자체를 담은 파일의 이름과 위치는 확인하지 못했습니다. 계정 쪽 자료를 요청하는 방법은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) 에 있습니다.

SQLite 파일은 `-wal`, `-shm` 을 함께 수집해야 최근 기록이 빠지지 않습니다. iLEAPP 도 `user_model_database.sqlite*` 처럼 끝에 `*` 을 붙여 찾습니다 [1]. 지운 레코드가 여유 공간에 남는 문제는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 와 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

키보드 DB 는 모두 SQLite 라서 파일 맨 앞 16바이트가 형식 표지입니다. 아래는 SQLite 명세로 만든 예시이고, 특정 검체에서 뽑은 값이 아닙니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
000010  10 00                                              페이지 크기 0x1000 = 4096
```

`KeyboardDomain` 파일을 백업에서 꺼내 이 표지를 확인한 다음 오프셋 16의 2바이트(빅 엔디언)로 페이지 크기를 읽고, 그 뒤는 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md) 의 순서대로 표를 따라갑니다. `rejections` 표의 두 시각 칸 값을 뽑았다면 먼저 -1e10(기본값)인지 보고, 아니면 유닉스 시각으로 바꿉니다.

### 공개 도구로 한 번

sqlite3 명령줄로 사용 통계를 읽으면 다음과 같습니다.

```sql
SELECT key, value,
       datetime(creation_date, 'unixepoch')     AS created_utc,
       datetime(last_update_date, 'unixepoch')  AS updated_utc
FROM usermodeldurablerecords
ORDER BY last_update_date;
```

iLEAPP 는 키보드 폴더의 여러 파일(`keyboard.py`)과 입력 문맥 plist(`keyboardInputContexts.py`)를 따로 읽어 보고서를 만듭니다 [1][2]. iLEAPP 에는 `textinputTyping.py`, `biomeTextinputses.py`, `biomeEmojiEngagement.py` 스크립트도 있지만 여기서는 이름만 확인했습니다 [3]. 도구 결과를 보고서에 쓰기 전에 같은 파일을 직접 열어 한두 행을 맞춰 보는 절차는 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에 있습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [메시지](../communications/messages/index.md), [왓츠앱](../messengers/whatsapp.md), [페이스북 메신저](../messengers/facebook-messenger.md) | 입력 문맥 식별자의 대화방이 실제 대화 기록에 있는지, 그 시각 무렵 보낸 메시지가 있는지 |
| [바이옴](../app-usage/biome/index.md), [KnowledgeC](../app-usage/knowledgec/index.md) | 입력 문맥 시각 무렵 그 앱이 앞에 떠 있었는지 |
| [설정 값](../system-account/preferences.md) | 설치한 키보드·언어와 입력 기록의 언어가 맞는지 |
| [시리](siri.md) | 받아쓰기를 켰는지(입력이 음성으로 들어왔을 가능성) |

대화 기록을 지웠다고 의심되는 사건에서는 입력 문맥 plist 가 대화방 식별자를 남기는 드문 자리라서, [지운 대화와 사진 찾기](../../04-scenarios/activity/deleted-content.md) 와 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 의 흐름에 넣어 봅니다.

## 실습

공개 iOS 검체(NIST CFReDS 등)의 파일시스템 추출 이미지를 받아 다음 질문을 풀어 봅니다. 검체마다 들어 있는 파일이 다르니, 먼저 `Library/Keyboard` 목록부터 확인합니다.

1. `Library/Keyboard` 에 어떤 파일이 있고, 이 페이지의 버전 표와 비교해 빠지거나 더 있는 파일은 무엇입니까?
2. `usermodeldurablerecords` 에서 `last_update_date` 가 가장 최근인 행 다섯 개의 `key` 는 무엇이고, 그 시각은 UTC 로 언제입니까?
3. `rejections` 표에서 `last_hard_rejection` 이 기본값(-1e10)이 아닌 행은 몇 개이고, 그 행들의 `performed_count` 는 어떻습니까?
4. 앱 컨테이너의 `UITextInputContextIdentifiers.plist` 에서 `_SETTIME` 이 있는 식별자를 골라, 같은 앱의 대화 DB 에 그 대화방이 남아 있는지 확인합니다.

## 참고 문헌

1. iLEAPP `scripts/artifacts/keyboard.py` (Keyboard Dynamic Lexicon, Keyboard Application Usage, Keyboard Usage Stats, Keyboard Vulgar Word Usage, Keyboard Autocorrection Rejections, Keyboard Inline Completion Rejections; 마지막 갱신 2026-08-21) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/keyboard.py
2. iLEAPP `scripts/artifacts/keyboardInputContexts.py` (Keyboard Input Contexts; 마지막 갱신 2026-09-19) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/keyboardInputContexts.py
3. iLEAPP 저장소 파일 목록 (main 브랜치 트리) — https://api.github.com/repos/abrignoni/iLEAPP/git/trees/main?recursive=1
