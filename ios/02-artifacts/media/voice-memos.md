---
title: "음성 메모"
parent: "아티팩트 · 사진·미디어"
nav_order: 600
---

# 음성 메모 (Voice Memos)

아이폰 음성 메모 앱은 녹음마다 `.m4a` 파일 하나와 `CloudRecordings.db` 의 `ZCLOUDRECORDING` 표 한 행을 남기고, 이 행에 녹음 시각·길이·이름·파일 경로가 들어 있습니다. 녹음을 지우면 "최근 삭제된 항목" 에 기본 30일 동안 머무르므로[7], 지운 녹음도 행과 파일이 함께 남아 있을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

음성 메모 앱으로 녹음하면 오디오 파일이 `Recordings` 폴더에 만들어지고, 앱이 쓰는 Core Data SQLite DB 에 그 녹음의 정보가 행으로 들어갑니다[1]. 행에는 녹음 시각(`ZDATE`), 길이(`ZDURATION`), 사용자에게 보이는 이름, 녹음 파일 이름(`ZPATH`)이 있고[1][6], 녹음마다 붙는 고유 ID(`ZUNIQUEID`)와 오디오 요약 값(`ZAUDIODIGEST`)도 있습니다[5]. 그래서 파일이 있으면 녹음 내용을, 파일이 없어도 행을 읽어 언제 얼마 동안 녹음했는지 따라가 볼 수 있습니다.

녹음 기록은 사용자가 어느 시각에 어느 장소에 있었는지 확인하는 단서로 쓰입니다[4]. 녹음 파일이 조작되었는지를 판단하는 절차도 따로 연구되어 있습니다[8].

음성 사서함과 통화 녹음은 [음성 사서함과 통화 녹음 (Voicemail·Call Recording)](../communications/voicemail-recording.md)에서 다룹니다.

## 위치와 버전별 차이

녹음 파일과 DB 는 같은 `Recordings` 폴더에 있습니다[1]. 이 폴더의 위치는 자료에 따라 두 곳이 나옵니다.

| 구분 | 위치 | 출처 |
|---|---|---|
| 앱 그룹 컨테이너 | 앱 그룹 `group.com.apple.VoiceMemos.shared` 의 `Recordings/` (iOS 26.5.2 로컬 백업 사례) | [3] |
| 애플리케이션 지원 폴더 | `/Library/Application Support/com.apple.voicememos/Recordings/` 아래 `CloudRecordings.db`, `Recordings.db` | [4] |

기기에서 앱 그룹 컨테이너는 `/private/var/mobile/Containers/Shared/AppGroup/` 아래 UUID 이름 폴더라서, 폴더 안의 메타데이터 plist 로 어느 앱 그룹인지 확인합니다. 방법은 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../01-foundations/value-decoding/bundle-id-app-group.md)에 있습니다. 분석 대상에서는 두 경로를 모두 찾아봅니다.

iOS 27.0 로컬 백업에는 `AppDomainGroup-group.com.apple.VoiceMemos.shared` 와 `AppDomain-com.apple.VoiceMemos` 도메인이 있습니다. 녹음 파일과 DB 가 어느 도메인에 들어가는지는 Manifest.db 에서 파일 이름으로 조회해 확인합니다. 백업 도메인을 읽는 법은 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

iLEAPP 는 `Recordings` 폴더에서 `CloudRecordings.db`, `Recordings.db`, `.m4a`, `.qta` 파일을 찾고, `CloudRecordings.db` 가 있으면 `ZCLOUDRECORDING` 표를, 없으면 `Recordings.db` 의 `ZRECORDING` 표를 읽습니다[1]. 두 DB 는 이름 열이 다릅니다.

| DB | 표 | iLEAPP 가 이름으로 읽는 열 | 출처 |
|---|---|---|---|
| `CloudRecordings.db` | `ZCLOUDRECORDING` | `ZCUSTOMLABELFORSORTING` | [1] |
| `Recordings.db` | `ZRECORDING` | `ZCUSTOMLABEL` | [1] |

## 구조

### ZCLOUDRECORDING 표

녹음 하나가 한 행입니다. 공개 도구가 읽는 열은 다음과 같습니다.

| 열 | 뜻 | 출처 |
|---|---|---|
| `Z_PK` | 행 번호 | [5] |
| `ZDATE` | 녹음 시각. Mac 절대 시각(Core Data 시각) | [1][5] |
| `ZDURATION` | 길이(초, 소수) | [1][5] |
| `ZCUSTOMLABELFORSORTING` | iLEAPP 가 녹음 이름으로 보여 주는 열 | [1] |
| `ZPATH` | 녹음 파일 이름. 비어 있을 수 있음 | [1][6] |
| `ZUNIQUEID` | 녹음 고유 ID. `.m4a` 안의 `voice-memo-uuid` 태그와 같은 값 | [5] |
| `ZAUDIODIGEST` | 오디오 요약 값(BLOB) | [5] |
| `ZEVICTIONDATE` | "최근 삭제된 항목" 에 든 녹음의 삭제 예정 시각. 지우지 않은 녹음은 NULL (macOS) | [6] |
| `ZENCRYPTEDTITLE` | 녹음 이름. 열 이름과 달리 평문으로 저장됨 (macOS) | [6] |

녹음 이름이 어느 열에 있는지는 출처마다 다릅니다. iLEAPP 는 `ZCUSTOMLABELFORSORTING` 을 이름으로 보여 주고[1], macOS 의 같은 DB 를 다룬 글은 `ZENCRYPTEDTITLE` 을 이름 열로 적었습니다[6]. 두 열이 모두 있으면 둘 다 뽑아 앱 화면의 이름과 맞춰 봅니다. `ZEVICTIONDATE` 와 `ZENCRYPTEDTITLE` 도 macOS 에서 확인된 열이라서, iOS 데이터에서는 먼저 `PRAGMA table_info(ZCLOUDRECORDING);` 로 열이 있는지 봅니다.

### 녹음 파일 (.m4a)

`ZPATH` 에 파일 이름이 있으면 iLEAPP 는 그 파일을 찾아 보고서에 붙이고, 비어 있으면 "기기 안 경로가 기록되지 않음" 으로 표시합니다[1]. 경로 없는 행은 녹음이 iCloud 에만 있고 기기에는 내려받지 않은 상태일 가능성이 있으므로, `Recordings` 폴더에 파일이 실제로 있는지 따로 확인합니다.

파일 이름은 녹음 날짜와 시각으로 시작합니다. 예를 들면 `20260415 113326-ABCD1234.m4a` 같은 모양입니다[5][6]. 파일 안에는 `----:com.apple.iTunes:voice-memo-uuid` 태그로 녹음 고유 ID가, `©too` 태그로 만든 앱과 기기 OS 판이 들어 있고, 앱 이름은 `com.apple.VoiceMemos` 로 시작합니다[5]. 예를 들면 `com.apple.VoiceMemos (iPhone Version 17.2.1 (Build 21C66))` 같은 값입니다[5].

### 편집한 녹음의 manifest.plist

녹음 파일 옆에 `파일이름.composition/manifest.plist` 가 생기는 녹음이 있습니다[2][5]. 이 plist 에는 녹음 이름(`RCSavedRecordingTitle`), 녹음 고유 ID(`RCSavedRecordingUUID`), 합성된 오디오 경로(`RCComposedAVURL`)가 들어 있습니다[2][5]. 생성 시각 키는 도구마다 다르게 읽는데, iLEAPP 의 이전 판은 `RCSavedRecordingCreationTime` 을[2], voice-memo-forensics 는 `RCSavedRecordingCreationDate` 를 읽습니다[5]. 분석 대상의 plist 를 열어 어느 키가 있는지 확인합니다.

iOS 26.5.2 아이폰에서 시험 녹음 6개를 만든 사례에서는 앱에서 잘라 내기(trim) 편집을 한 녹음 하나에만 `manifest.plist` 가 생겼습니다[3]. 그래서 이 plist 만 읽으면 녹음 대부분이 빠집니다. 다른 사례에서는 녹음 174개 가운데 18개에만 이 plist 가 있었습니다[3]. iLEAPP 는 이 문제 때문에 2026년 7월부터 plist 대신 DB 를 읽습니다[1][3]. plist 읽는 법은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../01-foundations/data-formats/plist.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** `ZCLOUDRECORDING` 행은 수집 시점에 음성 메모 앱에 그 녹음이 등록되어 있었다는 사실과, 앱이 기록한 녹음 시각·길이·이름을 보여 줍니다[1]. `.m4a` 파일이 있으면 녹음된 소리 자체가 증거가 되고, 파일의 `voice-memo-uuid` 태그가 행의 `ZUNIQUEID` 와 같으면 그 파일과 행이 같은 녹음이라는 사실도 확인됩니다[5]. macOS 에서는 `ZEVICTIONDATE` 에 값이 있으면 그 녹음이 "최근 삭제된 항목" 에 들어가 있었다는 뜻입니다[6].

**증명하지 못하는 것.** 녹음 이름은 사용자가 바꿀 수 있어서 녹음 장소나 내용과 맞는다는 보장이 없습니다. 녹음이 이 기기에서 만들어졌다는 결론은 행 하나로 내리지 않습니다. 같은 애플 계정으로 로그인하고 iCloud 설정에서 음성 메모를 켠 아이폰·아이패드·Mac 은 녹음을 서로 맞춰 두므로[10], 다른 기기에서 만든 녹음도 이 목록에 들어올 수 있습니다. 그래서 `©too` 태그의 기기 종류와 OS 판을 분석 대상 기기와 맞춰 봅니다[5]. 녹음 파일이 편집되지 않은 원본인지도 행만으로는 알 수 없습니다. 앱에서 편집한 녹음은 원본을 덮어쓰거나 새 녹음으로 저장할 수 있습니다[7].

보고서에는 "CloudRecordings.db 에 길이 N초, 이름 X 인 녹음이 T 에 녹음된 것으로 기록되어 있고, 같은 고유 ID 의 .m4a 파일이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

`ZDATE` 는 Mac 절대 시각(2001-01-01 00:00:00 UTC 부터 흐른 초)이고, 978307200 을 더하면 UTC 기준 UNIX 시각이 됩니다[1][5]. iLEAPP 도 이 방식으로 바꿔 UTC 로 보여 줍니다[1]. 시간대 값은 이 열에 없어서, 현지 시각으로 쓸 때는 기기의 시간대 설정을 따로 확인합니다. 시각 형식 전반은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

`ZDATE` 를 녹음 시작 시각으로 읽으면 녹음은 `ZDATE` 부터 `ZDURATION` 초 동안 이어진 것이 되는데, 시작 시각인지 끝난 시각인지는 그 시각 앞뒤의 앱 사용 기록과 맞춰 본 뒤에 씁니다. 파일 이름 앞의 날짜·시각은 이름만 보고 UTC 인지 현지 시각인지 알 수 없으므로, `ZDATE` 를 UTC 로 바꾼 값과 비교해 차이를 확인하고 보고서의 기준 시각으로는 `ZDATE` 를 씁니다.

`ZDURATION` 과 `.m4a` 파일에서 잰 길이는 조금 다를 수 있습니다. voice-memo-forensics 는 기본값으로 0.15초까지의 차이를 같은 길이로 봅니다[5]. iLEAPP 는 `time(ZDURATION, 'unixepoch')` 로 길이를 시:분:초로 바꿔서 1초 아래가 잘리고, 24시간이 넘는 녹음은 시간이 0부터 다시 셉니다[1]. 정확한 길이는 초 값 그대로 봅니다.

macOS 에서 `ZEVICTIONDATE` 는 삭제 예정 시각이라서[6] 사용자가 지운 순간과 같지 않습니다. "최근 삭제된 항목" 보관 기간은 기본 30일이고 설정 → 앱 → 음성 메모 → Clear Deleted(영어 화면 기준) 에서 바꿀 수 있어서[7], 이 값에서 30일을 빼 삭제 시각을 계산하면 틀릴 수 있습니다.

## 함정과 한계

- **manifest.plist 만 읽는 도구.** 편집한 녹음에만 plist 가 생기는 사례가 있어서[3], plist 기반 도구 결과는 녹음 수가 크게 적을 수 있습니다. DB 행 수와 `.m4a` 파일 수를 먼저 세어 봅니다.
- **지운 녹음이 목록에 섞임.** 지운 녹음은 "최근 삭제된 항목" 에 기본 30일 동안 남고[7], macOS 에서는 이 기간에 행과 `.m4a` 파일이 그대로 있습니다[6]. `ZEVICTIONDATE` 로 나눠 보지 않으면 지운 녹음을 사용 중인 녹음으로 보고하게 됩니다. iLEAPP 결과에는 이 열이 없습니다[1].
- **열 이름이 판마다 다름.** iLEAPP 는 없는 열을 NULL 로 바꿔 읽기 때문에[1], 결과의 빈칸이 "값이 없음" 인지 "열이 없음" 인지 구분되지 않습니다. `PRAGMA table_info` 로 열을 확인합니다.
- **완전히 지운 녹음.** "최근 삭제된 항목" 에서도 지운 녹음의 행은 SQLite 빈 페이지(freelist)나 WAL 에 남아 있을 수 있습니다. 찾는 방법은 [SQLite 레코드 되살리기 (SQLite)](../../03-techniques/analysis/data-recovery/sqlite-records.md)에서 다룹니다.
- **편집 흔적.** iOS 14 를 설치한 서로 다른 모델의 아이폰 5대로 녹음 100개를 만들어 AAC·ALAC 로 저장한 연구에서는, 녹음을 조작하면 비트레이트·샘플링 레이트·시각 같은 인코딩 값이 원본과 달라지고, 파일 시스템의 임시 파일에 원본 녹음의 흔적이 남았습니다[8]. 이 연구는 나중에 조작된 녹음의 원본을 이 임시 파일에서 되살릴 가능성도 제시했습니다[8]. 다른 iOS 판에서도 같은 임시 파일이 남는지는 분석 대상에서 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`ZDATE`·`ZDURATION` 이 8바이트 실수(형식 번호 (serial type) 7, 빅 엔디언 IEEE 754)로 저장되어 있으면 레코드 본문에서 아래처럼 보입니다[9]. 아래는 SQLite 파일 형식 명세로 만든 예시이고, 특정 기기에서 나온 값이 아닙니다(만든 예시).

```text
ZDATE     : 41 C7 E4 6E 40 40 00 00
          = 801692800.5 (Mac 절대 시각)
          + 978307200  = 1780000000.5 (UNIX 초)
          = 2026-05-28 20:26:40.5 UTC

ZDURATION : 40 54 D0 00 00 00 00 00
          = 83.25 (초)
```

REAL 친화도 열의 값이 소수점 아래 없이 정수로 바뀔 수 있으면 SQLite 는 그 값을 정수 형식 번호로 저장할 수 있습니다[9]. 그래서 같은 열이라도 행마다 형식 번호가 다를 수 있습니다. 레코드 헤더와 형식 번호는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다.

### 공개 도구로 한 번

`CloudRecordings.db` 를 `-wal`·`-shm` 파일과 함께 복사한 사본을 sqlite3 로 엽니다. 먼저 `PRAGMA table_info(ZCLOUDRECORDING);` 로 아래 열이 있는지 보고, 없는 열은 질의에서 뺍니다.

```sql
SELECT Z_PK,
       datetime(ZDATE + 978307200, 'unixepoch') AS recorded_utc,
       ZDURATION AS duration_sec,
       ZCUSTOMLABEL, ZCUSTOMLABELFORSORTING, ZENCRYPTEDTITLE,
       ZPATH, ZUNIQUEID,
       datetime(ZEVICTIONDATE + 978307200, 'unixepoch') AS eviction_utc
FROM ZCLOUDRECORDING
ORDER BY ZDATE;
```

`eviction_utc` 가 NULL 이 아닌 행은 "최근 삭제된 항목" 에 든 녹음으로 따로 분류합니다(macOS 기준)[6]. 그다음 `ZPATH` 의 파일이 `Recordings` 폴더에 있는지 보고, 파일의 메타데이터 태그를 읽어 `voice-memo-uuid` 가 `ZUNIQUEID` 와 같은지 확인합니다[5]. voice-memo-forensics 는 이 비교(길이·생성 시각·고유 ID·만든 앱)를 한 번에 해 줍니다[5].

iLEAPP 의 Voice Memos 모듈은 녹음 시각(UTC)·길이·이름·경로 기록 여부·오디오 파일을 표로 냅니다[1]. 도구 결과의 행 수와 시각을 위 질의 결과와 맞춰 보고, 도구가 보여 주지 않는 `ZEVICTIONDATE` 는 질의 결과로 보충합니다.

## 교차 검증

녹음 시각 앞뒤로 음성 메모 앱을 실제로 쓰고 있었는지는 [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../app-usage/biome/index.md)의 앱 사용 기록으로 확인합니다. 녹음 장소를 따질 때는 같은 시각의 [중요 위치 (Significant Locations)](../location/significant-locations.md)를 함께 봅니다. 녹음이 다른 기기에서 iCloud 로 들어왔는지는 `©too` 태그와 [클라우드 데이터 (iCloud·계정 데이터 요청)](../../03-techniques/acquisition/cloud-data.md)로 확인하고, 지운 녹음을 찾는 흐름은 [지운 대화와 사진 찾기 (Deleted Content)](../../04-scenarios/activity/deleted-content.md)를 따릅니다. 통화를 녹음한 기록이라면 [음성 사서함과 통화 녹음 (Voicemail·Call Recording)](../communications/voicemail-recording.md)과 나눠 봅니다.

## 실습

NIST CFReDS 같은 곳에 공개된 iOS 시험 이미지로 아래를 풀어 봅니다.

1. `Recordings` 폴더가 앱 그룹 컨테이너와 애플리케이션 지원 폴더 가운데 어디에 있습니까? `CloudRecordings.db` 와 `Recordings.db` 가 둘 다 있습니까?
2. `ZCLOUDRECORDING` 의 행 수, `.m4a` 파일 수, `manifest.plist` 수를 각각 세어 보십시오. 서로 다르다면 어느 녹음이 어느 쪽에만 있습니까?
3. `ZEVICTIONDATE` 열이 있습니까? 값이 있는 행의 `.m4a` 파일은 아직 남아 있습니까?
4. 녹음 하나를 골라 `ZDATE` 를 UTC 로 바꾸고, 파일 이름 앞의 날짜·시각과 비교해 보십시오.
5. `.m4a` 파일의 `©too` 태그에 적힌 OS 판이 분석 대상 기기의 iOS 판과 같습니까?

## 참고 문헌

1. iLEAPP, `scripts/artifacts/voiceRecordings.py` (Anna-Mariya Mateyna, Johann-PLW) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/voiceRecordings.py
2. iLEAPP, `scripts/artifacts/voiceRecordings.py` 이전 판(커밋 00c2b1c, manifest.plist 를 읽던 판) — https://raw.githubusercontent.com/abrignoni/iLEAPP/00c2b1cfe9de7efa2a2fee1f9b3b57e73bc8c868/scripts/artifacts/voiceRecordings.py
3. iLEAPP 이슈 #1717, "iLEAPP - voiceRecordings (voiceRecordings.py) does not identify all recordings" — https://github.com/abrignoni/iLEAPP/issues/1717
4. Forensafe, "iOS Voice Memos" — https://www.forensafe.com/blogs/iOSVoiceMemos.html
5. Francesco de Lorenzi, voice-memo-forensics, `audit_voice_memos.py`·`README.md` — https://github.com/fdelorenzi/voice-memo-forensics
6. Matsubo Tech Blog, "会議の録音を ElevenLabs Scribe で自動 transcribe する CLI を Go で作った — vmt" (2026-04-25, macOS) — https://blog.teraren.com/posts/2026-04-25-voice-memo-stt/
7. Apple 지원, "Edit or delete a recording in Voice Memos on iPhone" — https://support.apple.com/guide/iphone/edit-or-delete-a-recording-iphc9bdaee83/ios
8. Nam In Park, Kyu-Sun Shim, Ji Woo Lee, Jin-Hwan Kim, Seong Ho Lim, Jun Seok Byun, Yong Jin Kim, Oc-Yeub Jeon, "Advanced forensic procedure for the authentication of audio recordings generated by Voice Memos application of iOS14", Journal of Forensic Sciences 67(4), 1534–1549, 2022. doi:10.1111/1556-4029.15016 — https://doi.org/10.1111/1556-4029.15016
9. SQLite, "Database File Format" — https://www.sqlite.org/fileformat2.html
10. Apple 지원, "Keep recordings up to date in Voice Memos on iPhone" — https://support.apple.com/guide/iphone/keep-recordings-up-to-date-iph38b91c7af/ios
