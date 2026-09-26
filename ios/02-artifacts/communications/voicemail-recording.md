---
title: "음성 사서함과 통화 녹음"
parent: "아티팩트 · 통화·메시지·연락처"
nav_order: 520
---

# 음성 사서함과 통화 녹음 (Voicemail·Call Recording)

## 한 줄 요약

비주얼 음성 사서함(Visual Voicemail)은 메시지마다 `voicemail.db` 의 한 행과 음성 파일·받아쓰기 파일을 남기고 지운 메시지도 표시로 남기며, iOS 18 부터 생긴 통화 녹음은 저장 위치를 밝힌 공개 자료가 없어 설정 흔적과 메모 앱 쪽을 함께 살펴야 합니다.

## 무엇을 기록하나 · 왜 생기나

통신사의 음성 사서함 메시지를 아이폰이 받아 오면 메시지마다 `voicemail.db` 의 `voicemail` 표에 한 행이 생기고, 같은 폴더에 음성 파일(`.amr`)과 받아쓰기 파일(`.transcript`)이 생깁니다 [1]. 행에는 보낸 번호, 다시 걸 번호, 받은 시각, 길이, 휴지통으로 옮긴 시각, 상태 값(`flags`)이 들어갑니다 [1]. 통화 기록에는 "받지 않은 통화" 로만 남는 사건도 음성 사서함에는 상대가 남긴 말과 그 받아쓰기로 남을 수 있어서, 부재중 통화의 뒷이야기를 채울 때 봅니다.

통화 녹음(Call Recording)은 iOS 18 부터 전화와 FaceTime 음성 통화를 녹음하는 기능입니다 [2]. 녹음 파일과 받아쓰기가 어디에 어떤 구조로 남는지는 공개 문서에 나와 있지 않아, 아래에서는 설정 흔적과 실제 기기에서 확인할 단서를 나눠 적습니다.

## 위치와 버전별 차이

### 음성 사서함

기기 안에서는 `/private/var/mobile/Library/Voicemail/` 폴더이고, 이 폴더에 `voicemail.db`, `*.amr`, `*.transcript` 가 있습니다 [1]. 로컬 백업에서는 `HomeDomain :: Library/Voicemail/voicemail.db` 에 있습니다. 같은 백업에 `.amr`·`.transcript` 파일이 들어가는지는 실제 백업으로 확인합니다.

| 구분 | 내용 | 출처 |
|---|---|---|
| 예전 열 구성 | `map` 표 없이 `voicemail` 표의 `sender`, `callback_num` 등으로 읽습니다 | [1] |
| `map` 표가 있는 구성 | `voicemail.label` 과 `map.label` 로 `map`(`ROWID`, `account`, `label`)을 이어 붙여 어느 계정(회선)의 메시지인지 읽고, `callback_num` 대신 `receiver` 를 보여 줍니다 | [1] |
| iOS 27.0 | `voicemail`, `deleted`, `map`, `sqlite_sequence`, `_SqliteDatabaseProperties` 표가 있습니다 | |

`map` 표가 어느 iOS 부터 생겼는지, 라이브 음성 사서함(Live Voicemail)이 남긴 메시지가 이 DB 에 어떻게 기록되는지는 실제 데이터로 확인합니다. 설정 파일에는 `ShowLiveVoicemailOnboarding` 키가 있습니다.

### 통화 녹음

iOS 18 부터 전화와 FaceTime 음성 통화를 녹음할 수 있습니다 [2]. `HomeDomain :: Library/Preferences/com.apple.TelephonyUtilities.plist` 에는 `StartRecordingDisclosureUtterance`, `EndRecordingDisclosureUtterance`, `StartRecordingBeepChecksum` 키가 있고, 이름으로 보면 녹음 시작·끝의 안내 문구와 알림음에 관련된 설정 같습니다.

## 구조

### voicemail.db

`voicemail` 표와 `deleted` 표의 열은 똑같이 `ROWID`, `remote_uid`, `date`, `token`, `sender`, `callback_num`, `duration`, `expiration`, `trashed_date`, `flags`, `receiver`, `label`, `uuid` 입니다. 주요 열의 뜻은 다음과 같습니다 [1].

| 열 | 뜻 |
|---|---|
| `ROWID` | 행 번호. 음성 파일 이름과 이어집니다 |
| `date` | 받은 시각. UNIX 시각 |
| `sender`, `callback_num` | 보낸 번호, 다시 걸 번호 |
| `duration` | 길이(초) |
| `trashed_date` | 휴지통으로 옮긴 시각. 0 이 아니면 Mac 절대 시각 |
| `flags` | 상태 값. 67 = 들은 메시지, 75 = 삭제, 3 = 새 메시지 |

iLEAPP 는 `trashed_date` 가 0 이고 `flags` 가 75 이면 "삭제됨", `trashed_date` 가 0 이고 그 밖의 `flags` 이면 "삭제 안 됨" 으로, 0 이 아니면 그 시각을 보여 줍니다 [1]. `flags` 는 여러 표시를 비트로 합친 값일 가능성이 높지만 비트마다의 뜻은 알려져 있지 않으니, 세 값 말고 다른 값이 나오면 숫자 그대로 보고합니다. `deleted` 표에 무엇이 언제 들어가는지는 공개 자료가 없고 iLEAPP 도 이 표를 읽지 않습니다 [1]. 열이 `voicemail` 표와 같으므로 행이 있다면 따로 뽑아 두고, 뜻은 실제 데이터에서 `voicemail` 표와 비교해 판단합니다.

### 음성 파일과 받아쓰기 파일

음성 파일 이름은 행 번호를 따라 `{ROWID}.amr` 이고, 받아쓰기는 `{ROWID}.transcript` 라는 plist 파일입니다 [1]. 받아쓰기 plist 에는 `transcriptionString`(받아쓴 글)과 `confidence`(확신도) 값이 들어 있습니다 [1]. DB 가 없으면 iLEAPP 는 `.amr` 과 `.transcript` 를 파일 이름끼리 맞추고 시각은 파일 시스템 시각을 씁니다 [1]. plist 읽는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

### 음성 사서함 곁의 설정 파일

음성 사서함과 관련된 설정 파일에는 다음 키가 있습니다. 값의 뜻을 밝힌 공개 자료는 없습니다.

| 파일 | 보인 키 |
|---|---|
| `AppDomain-com.apple.mobilephone :: Library/com.apple.MobilePhone/VoicemailAccountCache.plist` | `anyAccountSubscribed`, `online`, `isMessageWaiting`, `storageUsage`, `transcriptionEnabled`, `accounts` |
| `HomeDomain :: Library/Preferences/com.apple.visualvoicemail.preferences.plist` | `LastBootTime`, `AccountsToRefreshIfNeeded`, `LastActiveAccounts` |
| `HomeDomain :: Library/Preferences/com.apple.TelephonyUtilities.plist` | `mostRecentVoicemailDate`, `ShowLiveVoicemailOnboarding`, `GreetingsChecksums`, `BeepChecksum` |
| `HomeDomain :: Library/Preferences/com.apple.mobilephone.plist` | `VoicemailShouldBeHidden`, `FTMS.estimatedVoicemailCount` |

`mostRecentVoicemailDate` 는 이름대로라면 가장 최근 음성 사서함의 시각이라서 DB 의 마지막 행과 맞춰 볼 만하지만, 이 뜻도 밝혀지지 않았으니 단서로만 씁니다.

### 통화 녹음의 단서

통화 녹음 파일의 저장 위치를 밝힌 공개 자료는 없습니다. 메모 앱의 음성 녹음은 iOS 18 에서 메모 안에 오디오 개체로 들어가고 받아쓰기 글과 사용자가 바꾼 파일 이름이 메모 DB 의 `ZICCLOUDSYNCINGOBJECT` 표에 남는다는 분석이 있지만, 이 분석은 메모 앱에서 직접 녹음한 경우를 다루고 통화 녹음을 따로 구분하지 않았습니다 [3]. 통화 녹음도 같은 구조인지는 실제 데이터로 확인할 가설로 다룹니다. 메모 DB 는 백업에서 `AppDomainGroup-group.com.apple.notes :: NoteStore.sqlite` 에 있고 `ZICCLOUDSYNCINGOBJECT` 표에 `ZNEEDSTRANSCRIPTION`, `ZFILESIZE` 열이 있습니다. 메모 DB 의 구조는 [메모](../mail-cloud/notes.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `voicemail` 행은 기록된 시각에 이 번호에서 이 길이의 음성 사서함 메시지가 기기에 내려왔다는 사실을 보여 주고, `flags` 와 `trashed_date` 는 사용자가 메시지를 들었는지, 휴지통으로 옮겼는지에 대한 기록을 남깁니다 [1]. 음성 파일이 남아 있다면 상대가 남긴 말 자체가 증거가 됩니다.

**증명하지 못하는 것.** `sender` 는 기록된 발신 번호일 뿐이라서 실제로 말한 사람이 그 번호의 명의자라는 뜻은 아닙니다. 받아쓰기는 자동 변환 결과라서 틀릴 수 있으니 확신도(`confidence`)를 함께 봅니다 [1]. 통화 녹음 기능이 있다는 사실만으로 특정 통화가 녹음되었다고 볼 수 없고, 녹음 파일이 실제로 나와야 합니다.

보고서에는 "voicemail.db 에 번호 X 가 보낸 길이 N초의 메시지가 T 에 받은 것으로 기록되어 있고, flags 값은 75 이다" 처럼 쓰고, 받아쓰기를 인용할 때는 자동 받아쓰기라는 점과 확신도를 함께 적습니다.

## 시각 해석

한 표 안에 두 가지 기준이 섞입니다. `date` 는 UNIX 시각(1970-01-01 00:00:00 UTC 부터 초)이고, `trashed_date` 는 0 이 아니면 Mac 절대 시각(2001-01-01 00:00:00 UTC 부터 초)입니다 [1]. `trashed_date` 를 `date` 처럼 UNIX 시각으로 읽으면 두 기준의 차이인 978307200초(정확히 31년)만큼 앞당겨져서, 휴지통 시각이 받은 시각보다 앞서는 것처럼 보입니다. 두 기준 모두 UTC 이고 바꾸는 법은 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 있습니다.

`duration` 은 초 단위이고 iLEAPP 는 시:분:초로 바꿔 보여 줍니다 [1]. DB 가 없어 파일 시스템 시각을 쓸 때는 [1], 그 시각이 메시지를 받은 시각과 같다는 근거가 없으니 단정하지 않습니다. 파일 시스템 시각의 뜻은 [iOS의 파일 시스템](../../01-foundations/storage/filesystem/index.md) 에서 다룹니다.

## 함정과 한계

- **시각 기준 혼동.** 위처럼 `date` 와 `trashed_date` 의 기준이 다릅니다 [1].
- **삭제 표시와 실제 삭제.** `flags` 75 나 `trashed_date` 는 삭제 동작의 기록이고, 음성 파일이 지워졌는지는 파일이 있는지로 따로 확인합니다. `deleted` 표의 동작은 알려져 있지 않습니다.
- **파일과 행의 짝 맞춤.** 음성 파일은 `ROWID` 로 행과 이어지므로 [1], DB 를 다시 만들었거나 행이 빠지면 짝이 어긋날 수 있습니다. 파일만 남고 행이 없는 경우는 따로 목록으로 만듭니다.
- **백업 범위.** 음성 파일이 백업에 들어가는지는 실제 백업으로 확인합니다.
- **통화 녹음 위치.** 저장 위치가 밝혀지지 않았으니 메모 앱 구조를 근거 없이 통화 녹음에 적용하지 않습니다 [3].

지운 SQLite 행을 찾는 방법은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 SQLite 파일 형식 명세로 만든 예시이고 실제 데이터 값이 아닙니다. `date` 가 4바이트 정수(형식 번호 4, 빅 엔디언)로 들어 있다면 레코드 본문에서 이렇게 보입니다.

```
date      : 6A 18 A5 00
          = 1780000000 (UNIX 초)
          = 2026-05-28 20:26:40 UTC

같은 순간을 Mac 절대 시각으로 적으면
            1780000000 - 978307200 = 801692800
```

`trashed_date` 열에서 801692800 근처의 값을 UNIX 시각으로 잘못 읽으면 1995년으로 나옵니다. 헥스로 행을 읽을 때 두 열의 기준을 따로 적어 두면 이런 실수를 피할 수 있습니다.

### 공개 도구로 한 번

사본을 `sqlite3` 로 엽니다.

```sql
SELECT v.ROWID,
       datetime(v.date, 'unixepoch') AS received_utc,
       v.sender, v.callback_num, v.duration, v.flags,
       CASE WHEN v.trashed_date = 0 THEN NULL
            ELSE datetime(v.trashed_date + 978307200, 'unixepoch') END AS trashed_utc
FROM voicemail v
ORDER BY v.date;

SELECT * FROM map;
```

iLEAPP 는 `map` 표가 있으면 이어 붙여 계정을 함께 보여 줍니다 [1]. `map` 의 내용을 따로 뽑아 두고 도구 결과의 계정 열과 맞춰 본 뒤, 같은 질의를 `deleted` 표에도 돌려 둡니다. 그다음 `{ROWID}.amr` 파일이 있는지 확인하고, `{ROWID}.transcript` 를 plist 도구로 열어 `transcriptionString` 과 `confidence` 를 꺼냅니다 [1]. iLEAPP 의 음성 사서함 모듈 결과와 행 수·시각을 맞춰 봅니다.

## 교차 검증

[통화 기록](call-history.md) 에서 같은 번호, 가까운 시각의 통화 행이 있는지 찾고, 번호의 이름은 [연락처](contacts.md) 에서 붙입니다. 새 음성 사서함 알림은 [알림 기록](../app-usage/notifications.md) 에서, 통화 녹음 단서는 [메모](../mail-cloud/notes.md) 에서 확인합니다. FaceTime 음성 통화 녹음이라면 [페이스타임](facetime.md) 과도 이어 봅니다.

## 실습

NIST CFReDS 등에 공개된 iOS 시험 데이터로 풀어 봅니다.

1. `voicemail.db` 에 `map` 표가 있습니까? 없다면 iLEAPP 는 어떤 열 구성으로 읽습니까?
2. `flags` 값별로 행이 몇 개입니까? 67·75·3 이 아닌 값이 있다면 그 행들의 공통점은 무엇입니까?
3. `trashed_date` 를 UNIX 기준과 Mac 기준으로 각각 바꿔 보고, 어느 쪽이 `date` 와 앞뒤가 맞는지 확인해 보십시오.
4. 음성 파일은 있는데 행이 없는 `ROWID` 가 있습니까?
5. 받아쓰기의 확신도가 가장 낮은 메시지를 골라 음성과 받아쓰기를 비교해 보십시오.

## 참고 문헌

1. iLEAPP, `scripts/artifacts/voicemail.py` — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/voicemail.py
2. Apple 지원, "How to record and transcribe a call on iPhone" (121583) — https://support.apple.com/en-us/121583
3. Ciofeca Forensics, "Apple Notes in iOS 18" (2024-12-10) — https://www.ciofecaforensics.com/2024/12/10/ios18-notes/
