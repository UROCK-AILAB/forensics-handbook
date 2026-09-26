---
title: "Recall"
parent: "아티팩트 · Windows의 AI 기능"
nav_order: 490
---

# Recall (Recall)

Recall 은 Copilot+ PC 에서 화면 스냅숏을 주기적으로 저장하고 기기 안에서 분석해 자연어로 다시 찾게 해 주는 Windows 기능이고, 사용자 폴더 아래 `CoreAIPlatform.00\UKP` 에 스냅숏 이미지와 주 DB(`ukg.db`), 의미 검색 색인을 남깁니다.

저장 경로와 DB 구조는 Microsoft 가 공개하지 않았고, 2024-06 평문 판과 Windows 11 24H2·25H2 에서 서로 다릅니다[5][6][8].

## 무엇을 기록하나 · 왜 생기나

Recall 을 켠 사용자의 화면 내용이 직전 스냅숏과 달라지면 Windows 가 스냅숏을 한 장 저장합니다. 이어서 로컬 OCR 로 글자를 읽어 이미지와 텍스트를 모두 검색할 수 있게 하고, 스냅숏을 타임라인으로 정리합니다[1]. 저장 간격은 자료마다 다릅니다. 2024 년 Microsoft 소개 문구는 화면 내용이 바뀌는 동안 5초마다 찍는다고 했지만[6], 2025-12 Manage Recall 은 "주기적으로"라고만 합니다[1]. 오디오는 녹음하지 않고 연속 동영상도 남기지 않으며, DRM 콘텐츠와 게임 모드 중의 게임 화면(지원 플랫폼)도 저장하지 않습니다[1]. 검색에 맞춘 언어는 영어, 중국어(간체), 프랑스어, 독일어, 일본어, 스페인어입니다[1].

스냅숏 저장과 분석에는 인터넷이나 클라우드를 쓰지 않고 스냅숏을 Microsoft 로 보내지도 않아서, 원본은 그 기기에만 있고 서버 사본을 요청할 곳이 없습니다[1]. 예외는 세 가지입니다. 타임라인에 보여 줄 파비콘 같은 웹 메타데이터를 스냅숏 URL 의 최상위 도메인에서 가끔 받아 오고, 설정에 따라 일부 진단 데이터를 보내며, 사용자가 피드백을 보내면 첨부한 스크린샷이 함께 갑니다[1]. 서버·기기·동기화로 나눈 일반 설명은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

### 켜지는 조건

Recall 은 Secured-core 기준을 채운 Copilot+ PC 에서만 돌고, 최소 기준은 40 TOPS NPU, 메모리 16GB, 논리 프로세서 8개, 저장소 256GB 입니다[1]. 켜려면 빈 공간이 50GB 이상 있어야 하고, 25GB 밑으로 떨어지면 저장을 스스로 멈춥니다. 장치 암호화나 BitLocker 가 켜져 있어야 하고, Windows Hello 강화 로그인 보안(Enhanced Sign-in Security, ESS)에 얼굴이나 지문을 하나 이상 등록해야 합니다[1].

관리하지 않는 개인 기기에는 Recall 이 들어 있지만 사용자가 직접 켜야 스냅숏을 저장합니다. 같은 PC 를 쓰는 사람마다 따로 켜야 하고, 다른 사용자와 스냅숏을 나누지 않습니다[1][4]. 회사가 관리하는 기기에서는 기본으로 꺼져 있고 구성 요소도 빠져 있으며, 관리자가 사용자 대신 스냅숏 저장을 켤 수는 없습니다[1]. 선택적 기능 이름은 `Recall` 이라서 "Windows 기능 켜기/끄기"나 PowerShell 의 `Enable-WindowsOptionalFeature`·`Disable-WindowsOptionalFeature` 로 통째로 넣거나 뺄 수 있습니다[1][4]. `ms-recall` 프로토콜로 부르면 Recall 이 열리면서 스냅숏을 한 장 찍습니다[1].

### 저장하지 않는 화면

민감 정보 필터(Sensitive information filtering)는 기본으로 켜져 있고, 비밀번호나 신분증 번호, 카드 번호 같은 정보를 감지하면 그 스냅숏을 저장하지 않습니다. 이 감지에는 NPU 와 Microsoft Classification Engine(MCE)을 씁니다[1]. 지원 브라우저의 비공개 창도 저장하지 않습니다. Edge, Firefox, Opera, Chrome 은 사이트 필터와 비공개 창 필터를 모두 지원하고, 그 밖의 Chromium 124 이상 브라우저는 비공개 창 필터만 지원합니다[1]. `edge://`, `chrome://` 같은 브라우저 내부 주소는 기본으로 거릅니다. 다만 거른 사이트라도 다른 페이지에 들어간 콘텐츠나 브라우저 기록, 뒤쪽 탭은 스냅숏에 나올 수 있습니다[1].

원격 데스크톱 클라이언트인 mstsc.exe, VMConnect.exe, Azure Virtual Desktop(MSI), RAIL 의 세션은 기본으로 빠집니다. 다만 클라이언트가 화면 캡처 보호를 구현하지 않으면 저장될 수 있습니다[1]. 앱이 `SetWindowDisplayAffinity` 로 `WDA_EXCLUDEFROMCAPTURE` 나 `WDA_MONITOR` 를 건 창은 스냅숏에 내용이 담기지 않습니다[1][9]. DLP 제품과 연동하면 제공자가 지정한 창만 지우고 나머지 화면은 남기며, 지원하는 DLP 는 Microsoft Purview 하나입니다[1].

캡처 서비스는 찍기 전에 조건 12개를 따집니다[5]. `GameModeActive`, `BatterySaverActive`, `UserActivityIdle`, `UserPresenceIdle`, `StorageLow`, `PrivateWindow`, `BlockedByContentProtection`, `BlockedAppId`, `BlockedExecutable`, `BlockedURL`, `BlockedContentFilePath`, `BitLockerDisabled` 입니다. 조건마다 어떻게 동작하는지는 공개된 설명이 없습니다. 이름으로 보아 절전 모드나 자리 비움도 스냅숏에 빈 구간을 만들 수 있으므로, 검체에서 빈 구간과 전원·자리 비움 기록을 맞춰 보고 판단합니다.

## 위치와 버전별 차이

저장소는 사용자 폴더의 `AppData\Local\CoreAIPlatform.00\UKP\` 아래에 있습니다[5][6][7][8]. 수집 도구도 이 경로를 씁니다. KAPE 타깃 `WindowsCopilotRecall.tkape` 는 `C:\Users\*\AppData\Local\CoreAIPlatform.00\UKP\` 를 하위 폴더까지 모으고[10], Velociraptor 아티팩트는 `UKP\*\ukg.db` 를 찾습니다[7].

```
C:\Users\사용자\AppData\Local\CoreAIPlatform.00\UKP\{GUID}\
    ukg.db                      주 DB (SQLite)
    ImageStore\                 스냅숏 이미지. 파일 이름이 ImageToken 값이고 확장자가 없다
SemanticTextStore.sidb          텍스트 의미 검색 색인 (DiskANN), 들어 있는 폴더는 검체로 확인
SemanticImageStore.sidb         이미지 의미 검색 색인 (DiskANN), 들어 있는 폴더는 검체로 확인
```

`ukg.db` 와 `ImageStore` 는 같은 `{GUID}` 폴더에 있습니다[6][7]. 두 `.sidb` 파일이 어느 폴더에 있는지는 공개 자료가 없습니다[5][8]. 그래서 검체에서는 `UKP` 아래를 통째로 봅니다. 자료마다 예로 든 GUID 값이 서로 다르므로[6][7], GUID 값을 정해 두고 찾지 말고 `UKP\*\` 로 찾습니다.

| 판 | 시기 | 저장 형태 | 근거 |
|---|---|---|---|
| 첫 미리 보기 | 2024-05 발표, 2024-06 공개 분석 | `ukg.db` 가 평문 SQLite, `ImageStore` 파일은 암호화하지 않은 JPEG | TotalRecall 첫 판[6], Velociraptor[7], Securelist(2024 베타 표 설명)[8] |
| 다시 설계한 판 | 2024-11-22 Insider Dev 채널 미리 보기, 2025-04-25 정식 출시 | 스냅숏과 벡터 DB 관련 정보를 늘 암호화 | Microsoft 문서[1][9] |
| 〃 (24H2) | 2025-10 글 | 관리자 권한 없이 `ukg.db` 에 접근은 되지만 암호화돼 있고, 글을 쓸 때 공개된 복호 방법이 없음 | Securelist[8] |
| 〃 (25H2 26300.8155) | 2026-04 글 | `ukg.db` 를 SQLite SEE 의 AES-256-GCM 으로 페이지마다 암호화 | TotalRecall Reloaded[5] |

보호 방식은 다음과 같습니다. 암호화 키는 TPM 이 보호하면서 사용자의 Windows Hello ESS 신원에 묶이고, VBS 엔클레이브 안의 작업만 이 키를 씁니다. Recall 을 열 때와 스냅숏에 접근할 때마다 Windows Hello 로 본인을 확인하고, 그때에만 복호합니다(just in time decryption)[1][4]. 키는 Windows Hello, TPM 에 묶인 NGC 키, 엔클레이브에 봉인된 키를 거쳐 페이지 단위 AES-256-GCM 키로 이어집니다[5]. 이 사슬에는 DPAPI 가 없습니다. 따라서 사용자 암호를 알아도 [DPAPI](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html) 방식으로 디스크 이미지에서 풀 수 있다고 볼 근거가 없고, 공개된 복호 방법도 없습니다[8].

### 설정과 정책

사용자 설정은 설정 → 개인 정보 및 보안 → Recall & snapshots 에 있습니다[4]. 저장 켜기, 필터 목록, 보존 기간 같은 사용자 설정이 어느 파일이나 레지스트리에 들어가는지는 공식 문서와 공개 분석에 없어서 검체로 확인해야 합니다.

조직이 거는 정책은 `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` 키에 들어갑니다. ADMX 는 `WindowsCopilot.admx`, 그룹 정책 경로는 Windows Components → Windows AI 이고, 장치와 사용자 둘 다 되는 항목은 HKLM 과 HKCU 양쪽에 올 수 있습니다[2]. 사용자 하이브의 이 키로도 스냅숏 저장을 켜고 끕니다[8].

| 정책 이름 | 범위 | 값 |
|---|---|---|
| `AllowRecallEnablement` | 장치 | 0 사용 불가, 1 사용 가능 |
| `DisableAIDataAnalysis` | 장치·사용자 | 0 저장 허용(기본), 1 저장 끔 |
| `SetMaximumStorageSpaceForRecallSnapshots` | 장치·사용자, Ent/Edu | MB 단위 0(OS 가 정함, 기본)·10240·25600·51200·76800·102400·153600 |
| `SetMaximumStorageDurationForRecallSnapshots` | 장치·사용자, Ent/Edu | 일 단위 0(OS 가 정함)·30·60·90(기본)·180 |
| `SetDenyAppListForRecall` | 장치·사용자, Ent/Edu | AUMID 나 실행 파일 이름을 세미콜론으로 이은 목록, 재부팅 후 적용 |
| `SetDenyUriListForRecall` | 장치·사용자, Ent/Edu | URI 를 세미콜론으로 이은 목록(하위 도메인·경로까지 거름), 재부팅 후 적용 |
| `AllowRecallExport` | 장치, Ent/Edu, EEA | 0 금지(기본), 1 허용(Insider 빌드 표기) |
| `SetDataLossPreventionProvider` | 장치, Ent/Edu | DLP 제공자의 레지스트리 위치와 DLL 을 적은 문자열(그룹 정책 이름 `SetDataLossPreventionProviderKey`) |
| `DisableRecallDataProviders` | 사용자, Ent/Edu, Insider | 앱 작업 제공자가 주는 추가 정보(예: 회의 참석자)를 보일지, Recall 을 다시 시작해야 적용 |

표의 이름은 CSP 정책 이름입니다. `SetDataLossPreventionProvider` 와 `DisableRecallDataProviders` 를 뺀 일곱 개는 `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` 아래 레지스트리 값 이름이 공개돼 있습니다. 두 정책은 값 이름이 공개되지 않았으므로 검체의 같은 키에서 직접 찾아봅니다[2]. `AllowRecallEnablement`, `DisableAIDataAnalysis`, 저장·필터 정책은 Windows 11 24H2 KB5055627(10.0.26100.3915) 이상에서, `SetDataLossPreventionProvider` 는 KB5065789(10.0.26100.6725) 이상에서 적용됩니다[2].

`AllowRecallEnablement` 의 기본값은 문서 안에서도 엇갈립니다. CSP 값 표는 1(사용 가능)을 기본값으로 적었지만, 같은 CSP 본문은 구성하지 않으면 구성 요소가 꺼진 상태라고 적었고, Manage Recall 은 관리 기기에서 기본으로 꺼지고 제거된다고 적었습니다(CSP 2026-09-10, Manage Recall 2025-12-10)[1][2]. 정책으로 Recall 을 끄거나(`AllowRecallEnablement`=0) 스냅숏 저장을 끄면(`DisableAIDataAnalysis`=1) 이미 있던 스냅숏을 지우고, `AllowRecallEnablement`=0 은 재시작 뒤 구성 요소도 기기에서 지웁니다[1][2]. DLP 정책을 지우면 DLP 제공자를 더 부르지 않을 뿐 이미 저장된 스냅숏은 그대로 둡니다[1].

### 보존과 삭제

최대 용량은 10, 25, 50, 75, 100, 150GB 가운데 고릅니다. 정하지 않으면 디스크 256GB 에서 25GB, 512GB 에서 75GB, 1TB 이상에서 150GB 로 잡고, 최대 용량에 닿으면 가장 오래된 스냅숏부터 지웁니다[1][2]. 보존 기간은 30, 60, 90, 180일 가운데 고르는데, 정하지 않았을 때의 동작은 자료마다 다릅니다.

| 자료 | 날짜 | 보존 기간을 정하지 않았을 때 |
|---|---|---|
| Policy CSP - WindowsAI[2] | 2026-09-10 | 사용자가 따로 정하지 않았으면 90일 |
| Manage Recall[1] | 2025-12-10 | 최대 용량에 닿을 때까지 지우지 않음 |
| TotalRecall Reloaded 설명서[5] | 2026-04 | 25H2 시험 기기의 설정 출력에 "Retention Days 90", 본문에 "기본 90일, 75GB" |

용량과 기간을 둘 다 정하면 먼저 닿는 쪽에서 지웁니다[2]. 사용자는 설정에서 스냅숏을 모두 지울 수 있고, 검색 결과나 스냅숏 화면에서 특정 앱이나 웹사이트의 스냅숏만 모두 지울 수도 있습니다[4]. "Reset Recall" 을 하면 스냅숏과 Recall 설정을 모두 지우지만, 이미 폴더로 내보낸 스냅숏은 지우지 않습니다[11]. 알림 영역 아이콘이 저장 중, 일시 정지, 필터링 상태를 보여 주고, 그 아이콘으로 저장을 잠시 멈출 수 있습니다[4]. 보관 설정과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

폴더를 지우는 주체가 사용자나 Recall 만은 아닙니다. 예약 작업 `\Microsoft\Windows\WindowsAI\Recall\PolicyConfiguration` 은 SYSTEM 권한(taskhostw.exe)으로 돌면서 `UKP` 아래 `{GUID}` 모양 폴더를 찾아 지웁니다(2025-11 기준)[12]. 이 작업 정의의 트리거는 `RecallPolicyCheckUpdateTrigger`, `AADStatusChangeTrigger`, `DisableAIDataAnalysisTrigger`, `UserLoginTrigger`(모두 WNF 상태 변경)와 `SessionUnlockTrigger`(세션 잠금 해제)입니다[12]. 이 작업의 동작은 이후 업데이트에서 바뀌었을 수 있으므로 검체의 작업 정의를 직접 봅니다.

### 내보내기(EEA 한정)

유럽경제지역(EEA) 기기에서만 사용자가 스냅숏을 내보낼 수 있고, 관리 기기는 기본으로 막혀 있습니다[1]. 지난 스냅숏을 한 번 내보내거나(최근 7일, 30일, 전부) 지금부터 계속 내보내게 할 수 있고, 계속 내보내기를 켜 두면 30일마다 켜져 있다고 알려 줍니다[1][11]. 내보내기 전에 Windows Hello 로 본인을 확인하고, 내보낼 폴더는 사용자가 고릅니다. 예를 들면 `C:\Recall\Exported` 입니다[11]. 내보내는 내용은 스냅숏과 저장 시각, 그때 열려 있던 앱 정보 같은 스냅숏 세부 정보입니다[1].

내보낸 파일은 암호화돼 있습니다. 풀려면 Recall 을 처음 설정할 때 한 번만 보여 주는 32자 "Recall export code" 가 있어야 하고, Reset Recall 을 하면 새 코드가 나옵니다[11]. Microsoft 는 파일 구조와 복호 절차, 예제 코드(RecallSnapshotsExport)를 공개했습니다[3][13].

| 순서 | 크기 | 내용 |
|---|---|---|
| 1 | 4바이트 | version, 리틀 엔디언, 값은 2 |
| 2 | 4바이트 | encryptedKeySize |
| 3 | 4바이트 | encryptedContentSize |
| 4 | 4바이트 | contentType |
| 5 | encryptedKeySize | 암호화된 콘텐츠 키: nonce 12바이트 + 키 32바이트 + 태그 16바이트 |
| 6 | encryptedContentSize | 암호화된 콘텐츠: 끝 16바이트가 태그 |

내보내기 코드에서 하이픈을 빼고 16진수를 바이트로 바꾼 뒤 SHA-256 을 구하면 AES-256-GCM 키가 되고, 이 키로 5번을 풀어 콘텐츠 키를 얻습니다. 6번은 콘텐츠 키와 0으로 채운 nonce 로 풉니다[3][13]. 푼 결과는 JPEG 이고, 스냅숏 메타데이터는 EXIF 태그 37500(0x927C, MakerNote)에 직렬화한 PropertySet 으로 들어 있습니다. 예제 코드는 이를 같은 이름의 `.jpg` 와 `.json` 으로 저장합니다[13]. 내보내기 코드는 복호 키와 같으므로 보고서에서는 가립니다. 내보내기 형식의 일반 설명은 [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)에 있습니다.

## 구조

### ukg.db 의 표와 칸

아래 칸 이름은 엔클레이브 바이너리 `storage_support.dll` 안의 CREATE TABLE 문에 있는 것입니다(25H2 26300.8155 기준)[5]. 표 개수는 설명서마다 다릅니다. Securelist 는 `ukg.db` 가 표 20개로 이뤄졌다고 적었지만 어느 판 기준인지는 밝히지 않았고, Reloaded 설명서는 핵심 표 17개를 적었습니다[5][8]. 2024 판 도구가 읽는 `WindowCaptureTextIndex_content` 처럼 FTS5 가 스스로 만드는 표가 있어서 차이가 날 수 있으므로, 검체에서 표 목록을 먼저 뽑아 맞춰 봅니다.

| 표 | 칸 |
|---|---|
| `WindowCapture` | Id, Name, ImageToken, IsForeground, WindowId, WindowBounds, WindowTitle, Properties, IsProcessed, Retry, ActivationUri, ActivityId, FallbackUri, TimeStamp, DwellTime |
| `WindowCaptureAppRelation` | WindowCaptureId, AppId, IsBackground |
| `WindowCaptureWebRelation` | WindowCaptureId, WebId, IsBackground |
| `WindowCaptureFileRelation` | WindowCaptureId, FileId |
| `WindowCaptureTopicRelation` | WindowCaptureId, TopicId, Score |
| `WindowCaptureTextIndex` | FTS5 가상 표(WindowCaptureId, WindowTitle, OcrText) |
| `App` | Id, WindowsAppId, IconUri, Name, Path, TileId, Properties |
| `Web` | Id, Domain, Uri, IconUri, Properties |
| `File` | Id, Path, Name, Extension, Kind, Type, ObjectId, VolumeId |
| `Topic` | Id, Title, Properties |
| `ScreenRegion` | Id, WindowCaptureId, RegionKind, OcrText, Bounds |
| `AppDwellTime` | Id, WindowsAppId, HourOfDay, DayOfWeek, HourStartTimestamp, DwellTime |
| `WebDomainDwellTime` | Domain, HourOfDay, DayOfWeek, HourStartTimestamp, DwellTime |
| `SearchHistory` | SessionId, CorrelationId, TimeStamp, Kind, Text, Language |
| `SearchFeedback` | SessionId, CorrelationId, TimeStamp, Kind, Text, Language, ItemChosenEventId, FeedbackType |
| `IdTable` | NextId |
| `_MigrationMetadata` | Id, Version |

2024 판 기준으로 칸의 뜻은 다음과 같습니다.

- `WindowCapture.Name` 은 사건 종류입니다. `WindowCreatedEvent` 는 창이 처음 생긴 때, `WindowChangedEvent` 는 창이 옮겨지거나 크기가 바뀐 때, `WindowCaptureEvent` 는 스냅숏을 찍은 때(`ImageToken` 이 있음), `WindowDestroyedEvent` 는 창을 닫은 때이고, `ForegroundChangedEvent` 도 있습니다[8]. 스냅숏 이미지가 없어도 창이 생기고 바뀌고 닫힌 흐름이 이 표에 남습니다.
- `WindowCapture.ImageToken` 값이 `ImageStore` 안의 파일 이름입니다[6][7][8].
- `WindowCaptureTextIndex_content` 는 FTS5 가 `WindowCaptureTextIndex` 의 칸을 c0, c1, c2 로 담은 표입니다. 가상 표의 칸 순서(WindowCaptureId, WindowTitle, OcrText)대로라면 c1 은 창 제목입니다[5]. c0 는 `WindowCapture.Id` 와 이어 붙이고 c2 는 OCR 텍스트로 읽으며, 앱 정보는 `WindowCaptureAppRelation.AppId = App.Id` 로 붙입니다[7][8].
- `AppDwellTime` 에는 창을 띄운 프로세스의 전체 경로(`WindowsAppId`), 띄운 날짜와 시각(`HourOfDay`, `DayOfWeek`, `HourStartTimestamp`), 창이 화면에 떠 있던 시간(`DwellTime`)이 있습니다[8]. `WebDomainDwellTime` 에도 같은 시각 칸이 있습니다[5]. 칸 이름으로 보아 시간(hour) 단위로 모은 값이지만, 모으는 단위를 밝힌 공개 자료는 없으므로 검체의 값으로 확인합니다.
- 캡처 입력 구조의 `FileObjectId`, `VolumeId` 는 NTFS 의 영구 파일 식별자이고, `File` 표에도 `ObjectId`, `VolumeId` 칸이 있습니다[5].

### 의미 검색 색인과 이미지

`.sidb` 파일에는 `si_items`, `si_embedding_metadata`, `si_diskann_graph`, `si_diskann_references`, `si_diskann_config`, `si_diskann_info`, `si_application_values` 표가 있습니다[5]. SQLite 파일 구조 자체는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/sqlite/index.html)에서 다룹니다.

2024 판의 `ImageStore` 파일은 확장자 없는 JPEG 이고, TotalRecall 첫 판은 복사본에 `.jpg` 를 붙여 엽니다[6]. 이 JPEG 의 `Exif.Photo.MakerNote`(0x927C) 태그에는 전경 창 경계, 캡처 시각, 창 제목, 창 ID, 창을 띄운 프로세스 전체 경로, 브라우저라면 URI 와 도메인이 들어 있습니다[8]. DB 가 없어도 이미지 한 장에서 이 메타데이터를 얻을 수 있다는 뜻이고, 내보낸 스냅숏도 같은 태그를 씁니다[13]. 다만 이 이미지 설명이 어느 판 기준인지는 밝혀져 있지 않고, 다시 설계한 판은 스냅숏을 늘 암호화합니다[1][8]. 그래서 다시 설계한 판의 `ImageStore` 파일 형식은 검체로 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** `CoreAIPlatform.00\UKP` 아래 파일은 암호화와 상관없이 존재, 크기, 파일 시스템 시각이 MFT 와 USN 저널에 남습니다. Recall 은 계정마다 따로 켜야 저장하므로[1][4], 한 사용자 폴더에 이 파일이 생기고 늘어난 기록은 그 계정에서 스냅숏 저장이 켜져 있던 시기를 가늠하는 단서가 됩니다. 정책 키에 `DisableAIDataAnalysis`=1 이나 `AllowRecallEnablement`=0 이 있으면 조직이 저장을 막았다는 사실과 그 뒤 기존 스냅숏이 지워졌을 가능성을 알려 줍니다. 2024 판처럼 평문 DB 를 얻었다면 창 제목, 프로세스 경로, OCR 텍스트, URL, 파일 경로, 시간대별 머문 시간이 기록으로 남습니다. 보고서에는 "이 사용자 폴더에 Recall 저장소가 있고, 이 기간에 그 안의 파일이 생기고 바뀐 기록이 있다" 처럼 씁니다.

**증명하지 못하는 것.** 다시 설계한 판에서는 디스크 이미지만으로 `ukg.db` 와 스냅숏의 내용을 읽는 공개된 방법이 없습니다(Securelist 2025-10-14 기준)[8]. 폴더가 있어도 무엇이 화면에 떠 있었는지는 알 수 없습니다. 스냅숏이 없다고 그 화면을 보지 않았다는 뜻도 아닙니다. 민감 정보 필터, 비공개 창, DRM, 원격 데스크톱, 앱·URI 차단 목록, 캡처 제외 창, 절전·자리 비움 같은 조건이 저장을 막고, 최대 용량과 보존 기간, 사용자의 삭제, Reset Recall, 정책 변경, 예약 작업이 이미 저장된 스냅숏을 지웁니다. 스냅숏이 있어도 사용자가 그 화면을 읽었다거나 내용을 다른 곳으로 옮겼다는 뜻은 아닙니다. OCR 텍스트는 기계가 읽은 글자라서 원문과 다를 수 있습니다.

## 시각 해석

2024 판 `WindowCapture.TimeStamp` 는 Unix epoch(1970-01-01 UTC)부터 센 밀리초입니다. TotalRecall 첫 판은 값을 1000으로 나눠 초로 바꾸고, Velociraptor 는 `timestamp(epoch=TimeStamp)` 로 읽습니다[6][7]. TotalRecall 첫 판은 Python `datetime.fromtimestamp` 로 바꾸므로 결과 파일의 시각은 분석 PC 의 현지 시각입니다[6]. 보고서에 옮길 때는 UTC 로 다시 적습니다.

다시 설계한 판의 칸 형식은 공개 자료가 없어서 검체로 확인해야 합니다. 공개 자료에 나오는 "100나노초 정밀도" 는 WinRT API 가 돌려주는 시각의 정밀도이고, DB 칸 형식이 아닙니다[5]. `HourStartTimestamp` 의 형식도 공개 자료에 없습니다. 내보낸 스냅숏의 `.json` 에 있는 시각은 Microsoft 예제 코드가 WinRT DateTime 을 Unix epoch 밀리초 문자열로 바꿔 쓴 값입니다[13].

`WindowCapture` 의 시각이 화면을 찍은 순간인지 저장을 마친 순간인지는 공개 자료에 없습니다. 디스크 이미지에서 바로 쓸 수 있는 시각은 파일 시스템 쪽입니다. `ImageStore` 파일의 생성 시각이 스냅숏을 저장한 무렵과 맞는지는 공개 자료가 다루지 않았으므로, 검체에서 DB 시각이나 다른 기록과 맞춰 본 뒤에 추정이라고 밝혀 씁니다. 폴더나 파일이 사라진 USN 기록은 지워진 무렵을 알려 줍니다. 다만 USN 기록만으로는 누가 왜 지웠는지(최대 용량, 보존 기간, 사용자 삭제, Reset Recall, 정책, 예약 작업)를 가를 수 없습니다. 정책 키의 마지막 쓰기 시각은 정책 값이 바뀐 무렵을 알려 줍니다.

## 함정과 한계

- 초기 미리 보기 판과 다시 설계한 판은 보호 방식이 다릅니다. 2024-06 무렵 자료와 도구가 설명하는 평문 DB 분석이 지금 검체에 그대로 통한다고 여기지 않고, 보고서에는 검체의 Windows 빌드를 함께 적습니다.
- 표와 칸 이름은 Microsoft 가 공개하지 않은 내부 구조입니다. 2024 판과 25H2 판 사이에 이름이 이어지는 것을 공개 자료로 볼 수 있지만, 빌드가 바뀌면 달라질 수 있습니다.
- 보존 기간 기본값을 자료마다 다르게 적었으므로, 90일보다 오래된 스냅숏이 있는지 없는지로 결론을 내리기 전에 검체의 정책 값과 설정을 먼저 봅니다.
- 사용자 설정이 어디에 저장되는지 공개 자료가 없으므로, 정책 키가 비어 있다고 Recall 이 꺼져 있었다고 판단하지 않습니다.
- Recall 전용 이벤트 로그 채널은 공개 자료에 나오지 않습니다. 파일 접근 감사를 켜 둔 환경이라면 보안 로그 4663 에 `UKP` 폴더 접근이 남고, Splunk 탐지 규칙(2026-05)은 이 이벤트에서 `aixhost.exe`·`aihost.exe` 가 아닌 프로세스의 접근을 찾습니다[14]. `AIXHost.exe` 는 Recall 타임라인 화면을 띄우는 프로세스이고[5], Microsoft 성능 시험 코드도 Recall 을 닫을 때 이 프로세스를 끝냅니다[15].
- Recall 이 켜진 기기에서는 화면에 떠 있던 다른 AI 서비스의 대화도 스냅숏에 담길 수 있습니다. 대화 원본이 서버에만 있는 서비스라도 화면 기록이 남을 수 있지만, 다시 설계한 판에서는 디스크 이미지에서 그 내용을 읽는 공개된 방법이 없습니다.

## 직접 분석해 보기

**헥스로 한 번.** 먼저 `ukg.db` 사본의 처음 16바이트를 봅니다. 평문 SQLite 파일은 SQLite 명세에 따라 아래 문자열로 시작합니다.

```
명세로 만든 예시(SQLite 파일 머리)
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

이 문자열이 보이면 2024 판처럼 평문 SQLite 로 열어 볼 수 있습니다. 보이지 않으면 암호화된 판일 수 있지만, 암호화된 파일의 머리 모양은 공개 분석 자료가 없어서 검체로 확인해야 합니다. `ImageStore` 파일은 JPEG 명세의 시작 표지 `FF D8 FF` 로 시작하는지 봅니다. 2024 판이라면 이 표지로 시작하고, 그렇지 않으면 암호화된 파일일 수 있습니다.

내보낸 스냅숏 파일은 공개된 구조대로 처음 16바이트에 네 값이 들어 있습니다. 콘텐츠 키 블록은 nonce 12 + 키 32 + 태그 16 이라서 encryptedKeySize 는 60(0x3C)이어야 합니다[13]. 아래는 만든 예시이고, contentSize 와 contentType 값은 지어낸 값입니다(contentType 값의 뜻은 공개되지 않았습니다).

```
만든 예시(내보낸 스냅숏 파일 머리)
00000000  02 00 00 00 3C 00 00 00 00 D0 02 00 01 00 00 00
          version=2   keySize=60  contentSize contentType
```

2024 판 `TimeStamp` 값을 읽는 연습입니다. `1788414012000` 은 만든 예시이고, 1000으로 나눈 1788414012 초를 Unix epoch 로 바꾸면 2026-09-03 05:40:12 UTC 입니다.

```sh
# 만든 예시 값. 결과를 UTC 로 받으려면 -u 를 붙인다
date -u -d @1788414012
```

**공개 도구로 한 번.** 수집은 KAPE 타깃 `WindowsCopilotRecall` 로 `UKP` 폴더를 통째로 모읍니다[10]. 파일 시스템 흔적은 MFTECmd 같은 도구로 `$MFT` 와 `$UsnJrnl:$J` 를 풀어 `CoreAIPlatform.00` 이 들어간 줄만 걸러 봅니다. 정책은 SOFTWARE 하이브와 사용자의 NTUSER.DAT 를 레지스트리 도구로 열어 `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` 의 값과 키의 마지막 쓰기 시각을 적습니다.

평문 SQLite 인 `ukg.db` 가 나온 경우에는 사본을 `sqlite3` 로 열어 표 목록부터 봅니다. Velociraptor 의 `Windows.System.Recall.WindowCaptureEvent` 와 `Windows.System.Recall.AllWindowEvents` 아티팩트는 아래와 같은 이어 붙이기로 사건 시각, 창 제목, 프로세스 경로, OCR 텍스트를 뽑습니다[7]. 두 아티팩트와 TotalRecall 첫 판은 2024 평문 판을 대상으로 만든 것이라서, 암호화된 `ukg.db` 는 이 방법으로 열리지 않습니다.

```sh
# 사본에서만 실행한다. 파일 이름은 만든 예시다
sqlite3 -readonly case-copy-ukg.db ".tables"
sqlite3 -readonly case-copy-ukg.db "
SELECT wc.TimeStamp, wc.Name, wc.WindowTitle, a.Path, t.c2 AS OcrText, wc.ImageToken
FROM WindowCaptureTextIndex_content t
JOIN WindowCapture wc ON wc.Id = t.c0
JOIN WindowCaptureAppRelation r ON r.WindowCaptureId = t.c0
JOIN App a ON a.Id = r.AppId
WHERE wc.Name = 'WindowCaptureEvent';"
```

EEA 기기에서 사용자가 내보낸 폴더와 내보내기 코드를 받았다면, Microsoft 예제 RecallSnapshotsExport 가 폴더 안 파일을 풀어 `.jpg` 와 `.json` 으로 저장합니다[3][13]. 원본 내보내기 폴더는 해시를 떠 둔 사본으로만 다룹니다.

## 교차 검증

Recall 폴더의 파일 시각은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 올려 브라우저 방문 기록, AI 앱 기록과 겹쳐 보고, Windows 타임라인 일반 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)에 있습니다. 평문 DB 의 `Web.Uri` 와 `App.Path` 는 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/index.html) 방문 기록과 맞춰 봅니다. 스냅숏 위에서 도는 [클릭 투 두](click-to-do.md)의 흔적은 그 페이지에서 다룹니다. 화면 기록이 대화 내용을 되살리는 단서가 되는 경우는 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에, 기기에서 이 폴더를 빠뜨리지 않고 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)에 있습니다. 조직의 DLP 설정과 함께 보려면 [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md)을 봅니다.

## 실습

Recall 은 조건을 채운 Copilot+ PC 에서만 돌므로, 시험용 기기를 마련해 다음 질문을 풀어 봅니다.

1. Recall 을 켜기 전과 켠 뒤의 `%LocalAppData%` 파일 목록을 비교해, 새로 생긴 폴더가 이 쪽의 경로와 같은지, `.sidb` 파일이 어느 폴더에 생기는지 봅니다.
2. `ukg.db` 와 `ImageStore` 파일의 처음 16바이트가 평문 SQLite·JPEG 표지로 시작하는지 봅니다.
3. 비공개 창과 일반 창에서 같은 페이지를 연 뒤 `ImageStore` 파일 수가 어떻게 달라지는지 봅니다.
4. 특정 앱의 스냅숏을 "모두 삭제" 한 뒤와 Reset Recall 을 한 뒤 USN 저널에 어떤 기록이 남는지 비교합니다.
5. 정책으로 `DisableAIDataAnalysis` 를 1로 바꾼 뒤 폴더에서 무엇이 사라지고 무엇이 남는지, 정책 키의 마지막 쓰기 시각과 파일 삭제 시각이 어떻게 맞물리는지 봅니다.

## 참고 문헌

1. Microsoft, Manage Recall for Windows clients, Microsoft Learn, ms.date 2025-12-10 — https://learn.microsoft.com/en-us/windows/client-management/manage-recall
2. Microsoft, Policy CSP - WindowsAI, Microsoft Learn, ms.date 2026-09-10 — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai
3. Microsoft, Decrypt exported snapshots from Recall, Microsoft Learn, ms.date 2025-12-01 — https://learn.microsoft.com/en-us/windows/ai/recall/decrypt-exported-snapshots
4. Microsoft, Privacy and control over your Recall experience, Microsoft Support — https://support.microsoft.com/en-us/windows/privacy-and-control-over-your-recall-experience-d404f672-7647-41e5-886c-a3c59680af15
5. xaitax, TotalRecall Reloaded, `README.md`(2026-04 푸시) — https://github.com/xaitax/TotalRecall
6. xaitax, TotalRecall 첫 판, `totalrecall_original_2024/README.md`, `totalrecall_original_2024/totalrecall.py`(2024-06) — https://github.com/xaitax/TotalRecall/tree/main/totalrecall_original_2024
7. Velocidex, `content/exchange/artifacts/Windows.System.Recall.WindowCaptureEvent.yaml`, `Windows.System.Recall.AllWindowEvents.yaml` — https://github.com/Velocidex/velociraptor-docs
8. Kirill Magaskin, "The king is dead, long live the king! Windows 10 EOL and Windows 11 forensic artifacts", Securelist, 2025-10-14 — https://securelist.com/forensic-artifacts-in-windows-11/117680/
9. Microsoft, Recall overview, Microsoft Learn, ms.date 2025-12-01 — https://learn.microsoft.com/en-us/windows/ai/recall/
10. EricZimmerman, KapeFiles, `Targets/Windows/WindowsCopilotRecall.tkape` — https://github.com/EricZimmerman/KapeFiles
11. Microsoft, Export your Recall snapshots, Microsoft Support — https://support.microsoft.com/en-us/topic/680bd134-4aaa-4bf5-8548-a8e2911c8069
12. redpack-kr, CVE-2025-60710, `README.md`(2025-11) — https://github.com/redpack-kr/CVE-2025-60710
13. Microsoft, RecallSnapshotsExport, `RecallSnapshotsExport.cpp`, `JsonHelper.h` — https://github.com/microsoft/RecallSnapshotsExport
14. Splunk, security_content, `detections/endpoint/windows_process_accessing_windows_recall_directory.yml`(2026-05-13) — https://github.com/splunk/security_content
15. Microsoft, HOBL, `scenarios/windows/recall.py` — https://github.com/microsoft/HOBL
