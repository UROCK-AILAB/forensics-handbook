---
title: "시리"
parent: "아티팩트 · 입력·음성 비서"
nav_order: 1080
---

# 시리 (Siri)

## 한 줄 요약

아이폰의 시리 흔적은 켜고 끈 설정을 담은 plist, 메시지·통화·미디어 인텐트를 담은 `siriremembers` DB, 시리 화면이 떴다 닫힌 때를 적은 바이옴 스트림으로 나뉘고, 이 셋을 맞춰 보면 "그 시각 무렵 시리를 썼나" 에 기록이 말하는 만큼 답할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

시리 (Siri) 는 음성 비서이고, 받아쓰기 (Dictation) 도 같은 설정 묶음 안에서 관리됩니다. 기기에는 세 종류의 흔적이 쌓입니다.

첫째는 설정입니다. 시리를 켰는지, 음성 데이터 공유에 동의했는지, 어떤 목소리와 언어를 쓰는지, iCloud 동기화를 켰는지가 `com.apple.assistant.*` plist 에 남습니다. 둘째는 사용 기록입니다. `siriremembers` DB 는 인텐트를 시각·방향·앱과 함께 담고, iLEAPP 는 그 가운데 메시지·통화·미디어 도메인을 골라 보여 줍니다 [1]. 바이옴의 `Siri.UI` 스트림에는 iLEAPP 시험 데이터 기준으로 시리 화면이 나타날 때와 닫힐 때 기록이 하나씩 남았습니다 [2]. 셋째는 주변 흔적입니다. 시리 지표를 모아 두는 DB, 앱이 시리에 알린 동작·문구 목록, 사파리가 무시한 시리 추천 사이트처럼 이름에 시리가 들어간 자료가 여러 앱과 도메인에 흩어져 있습니다.

`siriremembers` 에 `donated_by_siri` 칸이 있다는 점으로 보아, 이 DB 는 시리를 거친 동작뿐 아니라 앱이 시스템에 알린(기부한) 인텐트도 담는 것으로 읽힙니다 [1]. 칸의 정확한 뜻은 확인하지 못했습니다.

## 위치와 버전별 차이

| 기록 | 위치 | iOS 범위 |
|---|---|---|
| `siriremembers.sqlite3` | 파일시스템 추출 기준 `*/mobile/Library/com.apple.siri.inference/siriremembers*` [1] | iLEAPP 시험 표본 14.3 ~ 18.7.8 [1] |
| 바이옴 `Siri.UI` | 파일시스템 추출 기준 `*/streams/*/Siri.UI/local/*` [2] | iLEAPP 표본 iOS 17, 18, 26.5.2 [2] |
| 시리 설정 plist | 백업 `HomeDomain :: Library/Preferences/` 아래 | iOS 27.0 백업에서 확인 |
| 시리 지표 DB | 백업 `AppDomainGroup-group.com.apple.feedbacklogger` 아래 | iOS 27.0 백업에서 확인 |
| 앱 인텐트 목록 | 백업 `SysContainerDomain-com.apple.linkd` 아래 | iOS 27.0 백업에서 확인 |

iOS 27.0 에서 만든 암호화하지 않은 로컬 백업에는 `AppDomainGroup-group.com.apple.siri.inference` 도메인이 있었지만 `siriremembers` 파일은 관찰 메모에 없었고, 바이옴 `streams` 경로도 없었습니다(확인 범위: iPhone 13 mini, iOS 27.0). 두 기록이 로컬 백업에 들어가는지는 가리지 못했으니, 사용 기록까지 보려면 파일시스템 추출을 전제로 계획합니다. 수집 범위를 정하는 법은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 에 있습니다.

같은 백업에는 `AppDomain-com.apple.siri`, `AppDomainGroup-group.com.apple.assistant.shared`, `AppDomainGroup-group.com.apple.siri.sirisuggestions`, `AppDomainGroup-group.com.apple.SiriTTS`, `AppDomain-com.apple.DictationExperience`, `AppDomain-com.apple.SystemVoiceAssistant` 도메인도 있었고 각각 항목이 3~4개였지만, 안에 든 파일은 관찰 메모에 없습니다(확인 범위: iPhone 13 mini, iOS 27.0).

## 구조

### 설정 plist

아래 키는 모두 iOS 27.0 백업에서 이름과 값 종류만 확인했습니다(확인 범위: iPhone 13 mini, iOS 27.0). 값의 뜻, 예를 들어 옵트인 상태 숫자가 무엇을 가리키는지나 "Linwood" 가 무엇인지는 확인하지 못했습니다.

| 파일 (`HomeDomain :: Library/Preferences/`) | 주요 키 |
|---|---|
| `com.apple.assistant.support.plist` | `Assistant Enabled`(bool), `Siri Data Sharing Opt-In Status`(int), `Allow Explicit Content`, `Quick Type Gesture Enabled`, `Suppress Dictation Opt In`, `Dictation Allowed`, `Dictation Enabled`(bool), `Offline Dictation Status`(언어 코드별 사전, ko-KR 포함 30개 언어) |
| `com.apple.assistant.backedup.plist` | `Cloud Sync Enabled`(bool), `Cloud Sync Enabled Modification Date`(datetime), `Session Language`(str), `Output Voice`{Custom, Footprint, Gender, Language, Name}, `SiriAvailability`{isAvailable, siriLocale, status, restrictionReasons, unavailabilityReasons 등}, `Siri Data Sharing Opt-In Status History`(list), `Home Accessories Siri Data Sharing Opt-In Change Log`(list), `MultiUser VoiceIdentification Enabled`, `Always Show Recognized Speech`, `Enable Offline Mode For Apple Intelligence`, `Linwood Enabled Me Device`(bool) |
| `com.apple.SiriViewService.plist` | `SiriIsActive`(bool), `NumberOfTimesSetupSiriShown`(int), `LastKnownInterfaceOrientation`(int) |
| `com.apple.AssistantServices.plist` | `CKPerBootTasks`, `CloudKitAccountInfoCache`, `CC_OncePerBootBackingData`, `CKStartupTime` |
| `com.apple.corespeechdatacollection.plist` | `SiriAttentionAndInvocation`(bytes), `SiriAttentionAndInvocationPluginLastRunDate`(datetime) |
| `com.apple.UIKit.plist` | `Dictation Enabled`, `Dictation Allowed`(bool) |
| `.GlobalPreferences.plist` | `com.apple.gms.enhancedSiri.lastUpdated`(datetime), `com.apple.gms.enhancedSiri.reasons`(list) |
| `com.apple.Accessibility.plist` | `HomeButtonAssistantPreference`(int) |

"시리야" 음성 등록과 이어져 보이는 기록도 있습니다. `AppDomainPlugin-com.apple.SiriSetup.SiriSetupSettingsIntents :: Library/Preferences/com.apple.voicetrigger.notbackedup.plist` 에 `EnrollmentId Voice Profile iCloud Enrollment`(str) 와 이름이 가려진 datetime 키가 하나 있고, `AppDomainGroup-group.com.apple.tipsnext :: tips-device-profile.plist` 의 `deviceCapabilities` 에는 `SiriEnabled`, `HeySiriAvailable`, `HeySiriEnabled`, `HeySiriEverUsed`, `SiriLanguageMatchesSystemLanguage` 키가 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). 앞의 plist 가 음성 등록과 관련이 있는지는 확인하지 못했습니다.

사용 빈도를 짐작하게 하는 키도 있습니다. `AppDomainPlugin-com.apple.siri.SiriSuggestionsLightHousePlugin :: Library/Preferences/com.apple.siri.DialogEngine.plist` 에는 `SiriAutoComplete`{count, timestamp} 와 이름이 가려진 {count, timestamp} 항목들이 있고, `AppDomainGroup-group.com.apple.siri.userfeedbacklearning :: Segment/SegmentStore.plist` 에는 `activitySegment`(str), `segmentFlags`(list), `membershipCheckedAt`(datetime), `assistantFirstEnabled`{longTermEnabled} 가 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 을, 설정 plist 전반은 [설정 값](../system-account/preferences.md) 을 봅니다.

### siriremembers DB

주 표는 `intents` 이고 칸은 `start_date`, `direction`, `donated_by_siri`, `dkevent_uuid`, `id`, `uuid`, `duration_seconds` 입니다 [1]. 여기에 `intent_entities`, `parameter_names`, `entities`, `domains`, `verbs`, `apps`, `groups` 표가 이어져 있고, iLEAPP 는 `domains.name` 이 'Messages', 'Calls', 'Media' 인 것을 골라 메시지·통화·미디어 보고서를 따로 만듭니다 [1]. 보고서에는 시각, 받는 사람·보낸 사람, 방향(보냄·받음), `donated_by_siri`, 앱 번들 ID, 도메인·동사·인텐트 ID 가 나오고, 통화에는 길이(HH:MM:SS)가, 미디어에는 제목이 더 붙습니다 [1]. 번들 ID 로 앱을 가리는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에 있습니다.

### 바이옴 Siri.UI 스트림

`Siri.UI` 는 SEGB 파일이고 기록마다 protobuf 로 풉니다 [2]. 각 형식은 [SEGB 형식](../../01-foundations/data-formats/segb.md) 과 [프로토콜 버퍼](../../01-foundations/data-formats/protobuf.md) 에 있습니다.

| 필드 | 뜻 (iLEAPP 시험 데이터 기준) |
|---|---|
| 2 | 세션 식별자. 한 쌍의 두 기록에서 값이 같음 |
| 3 | presentation 값. 표본에서 늘 같았고 뜻은 풀지 못함 |
| 4 | 닫힌 이유. 관찰된 값은 `HardwareButton`, `Punchout`, `Timeout`, `TapOutsideOfContent` |
| 5 | 1 은 나타남, 0 은 닫힘 |
| 7 | 관련 ID |

시험 데이터에서 기록은 짝을 이루었습니다. 필드 5 가 1 이고 닫힌 이유가 없는 기록이 먼저 오고, 이어서 필드 5 가 0 이고 닫힌 이유가 있는 기록이 오며, 시리 화면이 떴다가 닫힌 흐름과 맞습니다 [2]. 바이옴 전반은 [바이옴](../app-usage/biome/index.md) 에 있습니다.

### 시리 지표 DB

`AppDomainGroup-group.com.apple.feedbacklogger` 아래에 `com.apple.siri.ODDIMetricsExtension/data.sqlite`, `com.apple.siri.metrics.MetricsExtension/data.sqlite`, `com.apple.siri.metrics.SiriAttentionAndInvocationExtension/data.sqlite`, `com.apple.siri.telemetry/data.sqlite`, `com.apple.siriknowledged/data.sqlite` 등 이름이 비슷한 DB 가 9개 있었고, 표는 모두 같았습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
batchStatus: batchId, timestampRefId, status, processedAttempts, dateCreated, dateUploaded, dateLastProcessed
fileUploads: uploadId, payload, timestampRefId, status, processedAttempts, dateCreated, dateUploaded, dateLastProcessed
records: batchId, payload, dateCreated
```

이름과 칸으로 보아 지표를 모아 올려 보내기 전에 쌓아 두는 곳으로 보이지만, `payload` 내용과 시각 칸의 기준은 확인하지 못했습니다.

### 앱 인텐트 목록과 그 밖의 자리

`SysContainerDomain-com.apple.linkd :: database/linkd.metadatastore.sqlite` 에는 `assistantAppEntity`, `assistantIntent`, `assistantIntentNegativePhrases`, `assistantSuggestionPhrases`(bundleIdentifier, actionAndBundleIdentifier, assistantSuggestionPhrase), `appShortcuts`, `examplePhrases` 표가 있고, 같은 도메인의 `index/appintents.sqlite` 에는 `assistant_entity`, `assistant_intent`, `assistant_intent_negative_phrases`, `assistant_suggestion_phrases` 표가 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). 앱이 시리에 알린 동작과 문구 목록으로 보이며, 사용 기록인지는 확인하지 못했습니다.

사파리의 `AppDomain-com.apple.mobilesafari :: Library/Safari/IgnoredSiriSuggestedSites.db` 에는 `ignored_siri_suggested_sites`(id, siriSuggestedSiteURL, query, profile, timestamp, visitedURL, ignoreCount) 표가 있고, 시계 앱 DB 의 `ZMTCDALARM`, `ZMTCDTIMER` 표에는 `ZSIRICONTEXT` 칸이 있습니다(확인 범위: iPhone 13 mini, iOS 27.0).

## 증거로서 의미

**증명하는 것**

설정 plist 는 키 이름으로 보아 수집 시점에 시리와 받아쓰기가 켜져 있었는지, 어떤 언어와 목소리를 골랐는지, iCloud 동기화를 켰는지를 보여 줍니다. `Cloud Sync Enabled Modification Date` 는 이름으로 보아 그 설정이 마지막으로 바뀐 때로 읽히지만, 이를 설명한 자료는 찾지 못했습니다(확인 범위: iPhone 13 mini, iOS 27.0). `siriremembers` 의 `intents` 행은 그 시각에 어떤 앱으로 누구와 메시지·통화·미디어 인텐트가 있었다는 기록이고 [1], `Siri.UI` 의 짝 기록은 시리 화면이 그 시각에 떴다가 어떤 이유로 닫혔다는 기록입니다 [2]. 둘을 같은 시각대에 놓으면 "이 시간대에 시리 화면이 열려 있었고, 같은 무렵 이 앱으로 이 상대에게 보내는 메시지 인텐트가 기록되어 있다" 처럼 쓸 수 있습니다.

**증명하지 못하는 것**

설정은 켜져 있었다는 사실일 뿐 실제로 썼다는 증거가 아닙니다. `siriremembers` 의 행은 앱이 기부한 인텐트일 수 있어서 `donated_by_siri` 를 보지 않고 "시리로 보냈다" 고 쓸 수 없고, 그 칸의 정확한 뜻도 확인되지 않았습니다 [1]. 인텐트 기록은 메시지 본문이나 전송 성공을 보장하지 않으니 [메시지](../communications/messages/index.md) 나 [통화 기록](../communications/call-history.md) 과 맞춰 봐야 합니다. `Siri.UI` 는 화면이 떴다는 기록이라 무엇을 말했는지는 알 수 없습니다 [2]. 누가 말했는지도 이 기록으로 가릴 수 없으며, `MultiUser VoiceIdentification Enabled` 같은 설정 키가 있다고 해서 사용자를 식별했다는 뜻은 아닙니다.

## 시각 해석

| 값 | 기준 | 근거 |
|---|---|---|
| `intents.start_date` | 유닉스 시각(1970-01-01 기준 초). Mac 절대 시각이 아님 | iLEAPP 가 `datetime(intents.start_date, 'UNIXEPOCH')` 로 바꿈 [1] |
| `intents.duration_seconds` | 초 단위 길이. iLEAPP 가 HH:MM:SS 로 보여 줌 | [1] |
| `Siri.UI` 기록 시각 | SEGB 기록의 timestamp1, UTC | [2] |
| plist 의 datetime 값 | 바이너리 plist 날짜 형식(2001-01-01 UTC 기준 초) | plist 명세 |
| 수집 시각 float 키 | 기준을 확인하지 못함 | — |
| 지표 DB 의 `dateCreated` 등 | 기준을 확인하지 못함 | — |

수집 시각 float 키는 `com.apple.siri.PostSiriEngagement.plist` 의 `PostSiriEngagementMetricsCollectorLastCollectedTime`, `com.apple.lighthouse.siri.IFTranscriptIngestor.plist` 의 `IntelligenceFlow.IFRequestTelemetryLastCollectionEndTime`, `com.apple.siri.cache.manager.plist` 의 `LLMCache.CacheManagerTelemetryLastLogCollectionEndTime`, `com.apple.analyticsagent.plist` 의 `ODDAssistantLLMSiriDigestSyncTime` 입니다(확인 범위: iPhone 13 mini, iOS 27.0). 이 값들은 지표를 모은 때로 보이며 사용자가 시리를 쓴 때와 같다고 볼 근거가 없습니다.

`Siri.UI` 에서 화면이 떠 있던 시간은 기록을 시각순으로 정렬해 세션 식별자(필드 2)로 묶고, 나타남 기록과 닫힘 기록의 시각 차로 잽니다 [2]. 시각 기준 전반은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에, 현지 시각으로 바꿀 때 볼 자리는 [시간대와 시각 설정](../system-account/time-zone.md) 에 있습니다.

## 함정과 한계

`Siri.UI` 에서 SEGB 상태가 Deleted 인 기록은 iLEAPP 가 시각과 위치만 보고하고, `tombstone` 경로의 파일은 건너뜁니다 [2]. 도구 결과에 시각만 있고 필드가 빈 행이 있으면 지운 기록일 수 있으니, 원본 SEGB 에서 다시 확인합니다. 닫힌 이유 값은 iLEAPP 시험 데이터에서 관찰된 네 가지뿐이라 다른 값이 나올 수 있습니다 [2].

Apple 이 시리·받아쓰기 기록을 기기에 얼마나 두는지, 서버로 무엇을 보내는지, "시리 및 받아쓰기 기록 삭제" 설정이 기기 파일에 어떤 영향을 주는지는 공식 문서로 확인하지 못했습니다. 그래서 기록이 비어 있을 때 사용자가 지웠다고 판단하지 않고, 버전과 수집 방식 차이부터 의심합니다. KnowledgeC 에 시리 관련 스트림이 iOS 몇 버전까지 남았는지, 통합 로그의 어느 서브시스템에 시리 호출이 남는지도 확인하지 못했습니다.

지표 DB 와 `linkd` 목록은 이름에 시리가 들어갈 뿐 사용 기록이라는 근거가 없으니, 보고서에서 "시리를 썼다" 는 근거로 쓰지 않습니다. 사파리의 `ignored_siri_suggested_sites` 는 사파리 기록이라 [사파리](../browsers/safari/index.md) 흐름에서 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

`com.apple.assistant.backedup.plist` 의 `Cloud Sync Enabled Modification Date` 같은 날짜 값은 바이너리 plist 에서 표지 바이트 0x33 뒤에 8바이트 빅 엔디언 부동소수가 오는 형식입니다. 아래는 plist 명세로 만든 예시이고, 특정 검체에서 뽑은 값이 아닙니다.

```
62 70 6C 69 73 74 30 30                 "bplist00" 파일 표지
...
33 41 C6 92 5E 80 00 00 00              0x33 = 날짜, 뒤 8바이트 = 757382400.0
                                        2001-01-01 00:00:00 UTC + 757382400초
                                        = 2025-01-01 00:00:00 UTC
```

실제 파일에서는 오프셋 표를 따라 키 이름 `Cloud Sync Enabled Modification Date` 와 짝을 이루는 값 객체를 찾은 다음, 첫 바이트가 0x33 인지 확인하고 뒤 8바이트를 부동소수로 읽어 978307200 을 더하면 유닉스 시각이 됩니다. 오프셋 표 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에 있습니다.

### 공개 도구로 한 번

파일시스템 추출에서 `siriremembers.sqlite3` 를 찾았다면 sqlite3 명령줄로 주 표부터 봅니다.

```sql
SELECT id, uuid,
       datetime(start_date, 'unixepoch') AS start_utc,
       direction, donated_by_siri, duration_seconds, dkevent_uuid
FROM intents
ORDER BY start_date;
```

상대·앱·도메인까지 붙인 보고서는 iLEAPP 의 `SiriRemembers.py` 가 만들고 [1], 바이옴 `Siri.UI` 는 `biomeSiriUI.py` 가 읽습니다 [2]. iLEAPP 에는 `biomeSiriRemembersAssistantSuggestions.py`, `biomeSiriRemembersAudioHistory.py`, `biomeSiriRemembersCallHistory.py`, `biomeSiriRemembersInteractionHistory.py`, `biomeSiriRemembersMessageHistory.py` 스크립트도 있지만 여기서는 이름만 확인했습니다 [3].

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [메시지](../communications/messages/index.md), [통화 기록](../communications/call-history.md) | `siriremembers` 의 메시지·통화 인텐트와 같은 시각·상대의 실제 기록이 있는지 |
| [바이옴](../app-usage/biome/index.md), [KnowledgeC](../app-usage/knowledgec/index.md) | 시리 화면이 뜬 시각 무렵 어떤 앱이 앞에 있었는지. `intents.dkevent_uuid` 가 KnowledgeC 이벤트와 이어지는지는 확인되지 않았으니 맞춰 보며 검증 |
| [키보드 입력 기록](keyboard.md) | 받아쓰기로 들어온 입력과 타이핑 흔적을 구분 |
| [연락처](../communications/contacts.md) | 인텐트의 받는 사람·보낸 사람이 누구인지 |

사용 시간을 재구성할 때는 `Siri.UI` 의 화면 시간을 [폰 사용 시간 재구성](../../04-scenarios/activity/usage-time.md) 의 흐름에 넣고, 기기를 쓴 사람을 가릴 때는 [그 시각에 폰을 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 를 함께 봅니다.

## 실습

공개 iOS 검체(NIST CFReDS 등)의 파일시스템 추출 이미지를 받아 다음 질문을 풀어 봅니다. 검체마다 iOS 버전과 들어 있는 파일이 다르니 먼저 경로가 있는지부터 확인합니다.

1. `com.apple.assistant.support.plist` 에서 `Assistant Enabled` 와 `Dictation Enabled` 의 값은 무엇입니까?
2. `siriremembers.sqlite3` 가 있다면 `domains.name` 별로 인텐트가 몇 개이고, `donated_by_siri` 값은 어떻게 나뉩니까?
3. 가장 최근 통화 인텐트의 시각(UTC)과 길이는 무엇이고, 통화 기록 DB 에 같은 통화가 있습니까?
4. 바이옴 `Siri.UI` 에서 세션 식별자로 짝을 묶어, 화면이 가장 오래 떠 있던 세션의 시작 시각과 닫힌 이유를 찾습니다.

## 참고 문헌

1. iLEAPP `scripts/artifacts/SiriRemembers.py` (siriRemembersMessages/Calls/Media; 작성 James McGee, 2024-01-29, 갱신 2026-06-24) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/SiriRemembers.py
2. iLEAPP `scripts/artifacts/biomeSiriUI.py` (Biome - Siri UI; 작성 @abrignoni, @mattiaepi, 2026-07-26, 갱신 2026-08-20) — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/biomeSiriUI.py
3. iLEAPP 저장소 파일 목록 (main 브랜치 트리) — https://api.github.com/repos/abrignoni/iLEAPP/git/trees/main?recursive=1
