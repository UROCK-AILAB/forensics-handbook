# 세션·탭 복원 (Sessions)

## 한 줄 요약

크롬 계열 브라우저는 창과 탭의 상태를 프로필 폴더의 `Sessions` 폴더에 SNSS 형식으로 적습니다. `Session_<숫자>` 파일에는 열려 있던 탭과 탭마다의 뒤로 가기 목록이 남습니다. `Tabs_<숫자>` 파일에는 최근에 닫은 탭과 창이 남습니다. 파일 이름의 숫자는 그 파일을 만든 시각입니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 Windows 11(빌드 26200) PC 한 대의 Chrome 153·Edge 151 에서 본 것입니다. 다른 판이나 다른 PC 에서는 다를 수 있습니다. 표시가 없는 내용은 2026년 9월 크로미엄 (Chromium) 소스 기준입니다.

## 무엇을 기록하나 · 왜 생기나

브라우저를 다시 켤 때 창과 탭을 되살리려고 이 파일을 씁니다. `Session_` 파일은 세션 복원 (Session Restore) 에 쓰고, `Tabs_` 파일은 탭 복원 서비스 (Tab Restore Service) 가 최근에 닫은 탭과 창을 다시 열 때 씁니다.

파일 안에는 명령 (Command) 이라는 레코드가 차례로 이어집니다. 명령 하나에는 "이 탭은 이 창에 있다", "이 탭의 탐색 항목은 이것이다", "이 탭을 이 시각에 닫았다" 같은 사실이 하나씩 들어갑니다. 탐색 항목 (Navigation Entry) 은 탭 안에서 연 페이지 하나이고 주소와 제목이 함께 적힙니다. 한 탭의 탐색 항목은 순번 0, 1, 2… 로 차례로 있어서 탭마다 뒤로 가기 목록을 되살릴 수 있습니다 (관찰).

사용자가 닫은 탭을 다시 열면 그 사실도 `Tabs_` 파일에 명령으로 적힙니다. 브라우저는 파일을 비우라는 요청 (truncate) 이 오면 새 파일을 만들며, `Tabs_` 는 항목 40개(`kEntriesPerReset`)마다 파일을 비우고 전부 다시 씁니다.

이름이 비슷한 `Session Storage` 폴더는 다른 것입니다. 이 폴더에는 웹 페이지의 sessionStorage 값이 LevelDB 형식으로 들어 있고, 관찰한 PC 에서도 `Sessions` 와 따로 있었습니다. 이 폴더는 [웹 저장소](local-storage-indexeddb.md) 에서 다룹니다.

## 위치와 버전별 차이

세션 파일은 Windows 버전보다 브라우저 판에 따라 달라집니다. 브라우저별 `User Data` 위치와 Windows 버전별 폴더 위치는 [크롬 계열 브라우저](index.md) 에 있습니다.

### 파일 위치 (프로필 폴더 기준)

| 위치 | 담긴 것 | 있는 곳 |
|---|---|---|
| `Sessions\Session_<숫자>` | 열려 있는 창·탭 | Chrome·Edge (관찰) |
| `Sessions\Tabs_<숫자>` | 최근에 닫은 탭·창 | Chrome·Edge (관찰) |
| `Sessions_Encrypted\Session_<숫자>`, `Tabs_<숫자>` | `Sessions` 와 같은 구성의 암호화 파일 | Chrome 153 에만 있었습니다 (관찰) |
| `EdgeSessions\SessionRestoreLog` | 세션 복원 과정을 한 줄씩 적은 글자 파일 | Edge 에만 있었습니다 (관찰) |

크로미엄 소스에는 평문 폴더 상수(`kSessionsDirectory`)와 암호화 폴더 상수(`kEncryptedSessionsDirectory`)가 따로 있습니다. 관찰한 Chrome 153 에는 `Sessions` 와 `Sessions_Encrypted` 가 함께 있었고 두 폴더의 파일 구성(Session_ 3개, Tabs_ 3개)이 같았지만, Edge 151 에는 `Sessions_Encrypted` 가 없었습니다.

### 판에 따른 차이

| 항목 | 내용 |
|---|---|
| 옛 파일 이름 | 옛 판은 프로필 폴더 바로 아래에 `Current Session`·`Last Session`·`Current Tabs`·`Last Tabs` 를 두었습니다. 현재 소스에는 이 이름이 나오지 않습니다. `Sessions` 폴더로 바뀐 판 번호는 확인하지 못했습니다. |
| SNSS 버전 | 현재 소스는 버전 1·2·4 를 더 이상 지원하지 않습니다. 평문 파일은 버전 3, 암호화 파일은 버전 5 입니다. |
| 암호화 폴더 | `Sessions_Encrypted` 가 어느 판부터 생겼는지는 확인하지 못했습니다. 앞으로 평문 `Sessions` 를 없앨지도 확인하지 못했습니다. |
| Whale | Whale 이 같은 폴더와 형식을 쓰는지는 확인하지 못했습니다. |

### 폴더에 남는 파일 수

옛 세션 파일을 지우는 함수(`DeleteLastSessionFiles`)는 가장 최근의 지난 파일 하나만 남기고, 마커가 온전한 파일은 "지난 것" 과 "그 앞 것" 두 개까지 기억합니다. 마커는 아래 "구조" 절에서 다룹니다. 관찰한 PC 에는 Chrome 에 `Session_`·`Tabs_` 가 3개씩, Edge 에 2개씩 있었습니다.

## 구조

> 그림 자리: SNSS 파일 한 개를 머리(8바이트) → 레코드(크기·명령 ID·내용) 반복 → 마커(ID 255) → 덧붙인 레코드 순서로 그린 그림. 옆에 같은 파일의 암호화 판(uint32 길이 + `v20` 내용) 을 나란히 놓습니다.

### 파일 이름

이름의 숫자는 1601-01-01 00:00 UTC 부터 센 마이크로초입니다. 새 파일 이름의 시각이 앞 파일보다 같거나 작으면 브라우저는 1마이크로초를 더해 이름이 겹치지 않게 합니다. 평문 파일과 짝이 되는 암호화 파일은 이름의 숫자가 몇 마이크로초에서 몇 밀리초 달랐습니다 (관찰).

### 파일 머리

| 오프셋 | 크기 | 뜻 |
|---|---|---|
| 0 | 4 | 서명 (int32). 상수 값은 `0x53534E53` 입니다. 파일에는 `53 4E 53 53`("SNSS") 순서로 적혀 있습니다 (관찰). |
| 4 | 4 | 버전 (int32) |

정수는 리틀 엔디언으로 적힙니다. 서명 상수가 파일 첫머리에 낮은 바이트부터 적혀 있는 것으로 알 수 있습니다.

| 버전 | 소스 이름 | 뜻 |
|---|---|---|
| 1·2·4 | — | 더 이상 지원하지 않습니다 |
| 3 | `kFileVersionWithMarker` | 평문입니다. `Sessions` 폴더의 파일이 이 버전이었습니다 (관찰) |
| 5 | `kFileVersionEncryptedWithOSCrypt` | 레코드를 암호화합니다. `Sessions_Encrypted` 폴더의 파일이 이 버전이었습니다 (관찰) |

### 레코드 — 평문 (버전 3)

머리 뒤로 레코드가 파일 끝까지 이어집니다.

| 크기 | 뜻 |
|---|---|
| 2 | 레코드 크기 (uint16). 명령 ID 1바이트와 내용을 합한 길이입니다 |
| 1 | 명령 ID (uint8) |
| 크기 − 1 | 내용 |

소스에서 크기와 ID 의 자료형 이름은 `SessionCommand::size_type`·`id_type` 이고, 각각의 바이트 수는 관찰로 확인했습니다. 예를 들어 크기가 25 이면 ID 1바이트와 내용 24바이트입니다. 이 규칙으로 읽으면 관찰한 파일 세 개 모두 파일 끝에서 정확히 맞아떨어졌습니다.

명령 ID 255 는 초기 상태를 다 썼다는 표시인 마커(`kInitialStateMarkerCommandId`)이고, 브라우저는 파일을 읽을 때 이 마커까지 읽어 파일이 온전한지 확인합니다(`ReadToMarker`). 관찰한 `Session_` 파일 하나에서 마커는 레코드 133개 중 61번째에 한 번 있었고 내용은 비어 있었습니다. 마커 앞은 파일을 만들 때 쓴 전체 상태이고 마커 뒤는 그 뒤에 덧붙인 변경으로 보이지만, 이 해석은 소스로 확인하지 못했습니다.

### 레코드 — 암호화 (버전 5)

- 버전 5 파일은 `os_crypt_async` 의 Encryptor 로 암호화합니다. 브라우저는 먼저 암호화와 복호화가 되는지 확인합니다.
- 어떤 알고리즘과 키를 쓰는지는 이 소스 파일에 적혀 있지 않습니다.
- 레코드마다 uint32 길이와 내용이 이어졌습니다 (관찰).
- 모든 레코드의 내용이 `v20`(`76 32 30`) 으로 시작했습니다 (관찰).
- 레코드 수는 짝이 되는 평문 파일과 같았습니다(133=133, 207=207, 79=79) (관찰).
- 레코드 길이는 짝이 되는 평문 레코드의 크기보다 모든 레코드에서 정확히 31바이트 길었습니다 (관찰).
- 31바이트는 [쿠키](cookies.md) 페이지에 적은 `v20` 값의 덧붙는 길이(접두사·논스·태그)와 같습니다. 다만 쿠키와 같은 키(`app_bound_encrypted_key`)를 쓰는지는 확인하지 못했습니다.

### Session_ 명령 ID

소스 `session_service_commands.cc` 기준입니다. 아래 표에는 분석에 자주 쓰는 명령만 적습니다.

| ID | 소스 이름 | 내용 | 분석에서 보는 점 |
|---|---|---|---|
| 0 | `kCommandSetTabWindow` | 창 ID, 탭 ID | 어느 탭이 어느 창에 있었는지 |
| 2 | `kCommandSetTabIndexInWindow` | 탭 ID, 창 안 위치 (int32) | 창 안에서 탭의 순서 |
| 6 | `kCommandUpdateTabNavigation` | 탐색 항목 하나 | 주소·제목 |
| 7 | `kCommandSetSelectedNavigationIndex` | ID, index (int32) | 탭에서 지금 보이는 탐색 항목 |
| 8 | `kCommandSetSelectedTabInIndex` | ID, index (int32) | 창에서 선택한 탭 |
| 9 | `kCommandSetWindowType` | 창 ID, int32 | 창 종류 |
| 12 | `kCommandSetPinnedState` | | 탭을 고정했는지 |
| 16 | `kCommandTabClosed` | ID, close_time (int64) | 탭을 닫은 시각 |
| 17 | `kCommandWindowClosed` | ID, close_time (int64) | 창을 닫은 시각 |
| 21 | `kCommandLastActiveTime` | 탭 ID, last_active_time (int64) | 탭이 마지막으로 활성 상태였던 시각 |
| 25 | `kCommandSetTabGroup` | | 탭 그룹 |
| 255 | `kInitialStateMarkerCommandId` | 없음 | 마커 |

- 관찰한 파일의 ID 7·8 레코드는 크기가 9(ID 1 + 내용 8)였습니다. 소스의 내용 모양(ID + int32 index)과 길이가 맞습니다.
- ID 16·21 레코드의 내용은 16바이트였습니다. 탭 ID 4바이트, 빈칸 4바이트, int64 시각 8바이트 순서입니다 (관찰).
- 그 밖의 ID 는 다음과 같습니다(이름 앞의 `kCommand` 는 뺐습니다). 13 SetExtensionAppID, 14 SetWindowBounds3, 15 SetWindowAppName, 18 SetTabUserAgentOverride(지금은 쓰지 않고 29 로 바뀜), 19 SessionStorageAssociated, 20 SetActiveWindow, 23 SetWindowWorkspace2, 24 TabNavigationPathPruned, 27 SetTabGroupMetadata2, 28 SetTabGuid, 29 SetTabUserAgentOverride2, 30 SetTabData, 31 SetWindowUserTitle, 32 SetWindowVisibleOnAllWorkspaces, 33 AddTabExtraData, 34 AddWindowExtraData, 35 SetPlatformSessionId, 36 SetSplitTab, 37 SetSplitTabData.
- 지금은 쓰지 않는 옛 ID 도 있습니다. 1 SetWindowBounds, 5 TabNavigationPathPrunedFromBack, 10 SetWindowBounds2, 11 TabNavigationPathPrunedFromFront, 22 SetWindowWorkspace, 26 SetTabGroupMetadata 입니다.
- 관찰한 `Session_` 파일 하나에 나온 ID 와 개수는 다음과 같았습니다. 0×7, 2×22, 6×28, 7×10, 8×6, 9×1, 12×15, 14×4, 16×3, 19×7, 21×12, 23×1, 25×15, 32×1, 255×1.

### Tabs_ 명령 ID

소스 `tab_restore_service_impl.cc` 기준입니다.

| ID | 소스 이름 | 분석에서 보는 점 |
|---|---|---|
| 1 | `kCommandUpdateTabNavigation` | 닫은 탭의 탐색 항목입니다. `Session_` 의 ID 6 과 같은 배치(탭 ID, index, 주소 … timestamp)로 읽혔습니다 (관찰) |
| 2 | `kCommandRestoredEntry` | 사용자가 닫은 항목을 다시 열었습니다. 내용(`RestoredEntryPayload`)은 int32 입니다 |
| 4 | `kCommandSelectedNavigationInTab` | 내용(`SelectedNavigationInTabPayload2`)은 SessionID, int32 index, int64 timestamp 입니다. timestamp 는 항목을 닫은 시각입니다 |
| 5 | `kCommandPinnedState` | 고정 탭이었는지. 내용(`PinnedStatePayload`)은 bool 입니다 |
| 9 | `kCommandWindow` | 닫은 창 |
| 10 | `kCommandSetTabGroupData` | 탭 그룹 정보 |
| 13 | `kCommandCreateGroup` | 탭 그룹 |

- 그 밖의 ID 는 다음과 같습니다. 3 WindowDeprecated, 6 SetExtensionAppID, 7 SetWindowAppName, 8 SetTabUserAgentOverride, 11 SetTabUserAgentOverride2, 12 SetWindowUserTitle, 14 AddTabExtraData, 15 CreateSplit, 16 SetTabSplitData.
- 옛 창 정보(`WindowPayloadObsolete2`)에는 window_id, selected_tab_index, num_tabs 와 int64 timestamp 가 들어 있습니다.
- 같은 숫자라도 두 파일에서 뜻이 다릅니다. 예를 들어 6 은 `Session_` 에서 탐색 항목이고, `Tabs_` 에서는 확장 앱 ID 입니다.
- `Tabs_` 에 남기는 항목 수의 상한은 `TabRestoreServiceHelper::kMaxEntries` 입니다. 값은 25 입니다(`tab_restore_service_helper.h`). 상한을 넘으면 오래된 항목부터 지웁니다.
- ID 4 레코드의 내용은 16바이트였습니다. 일부 레코드는 timestamp 가 0(1601-01-01)이었습니다 (관찰).
- 관찰한 `Tabs_` 파일 하나에 나온 ID 와 개수는 다음과 같았습니다. 1×160, 4×36, 6×5, 9×5, 255×1.

### 탐색 항목의 내용 (Pickle)

탐색 항목은 `SerializedNavigationEntry` 클래스가 Pickle 형식으로 직렬화합니다. 레코드 내용의 첫머리에는 아래 두 값이 먼저 옵니다 (관찰).

| 순서 | 값 |
|---|---|
| 1 | uint32 Pickle 내용 길이. 레코드 내용 크기에서 4를 뺀 값입니다(예: 내용 1600바이트이면 1596) |
| 2 | int32 탭 ID |

그 뒤로 `WriteToPickle` 이 아래 순서로 값을 씁니다.

| 순서 | 값 | 자료형 |
|---|---|---|
| 1 | index (탭 안 탐색 순번) | int |
| 2 | virtual URL (주소) | string |
| 3 | title (제목) | string16 |
| 4 | encoded_page_state | string |
| 5 | transition_type | int |
| 6 | type_mask (지금은 HAS_POST_DATA = 1 하나만 씀) | int |
| 7 | referrer_url | string |
| 8 | 옛 referrer policy 자리 (호환용) | int |
| 9 | original_request_url | string |
| 10 | is_overriding_user_agent | bool |
| 11 | timestamp (1601 기준 마이크로초) | int64 |
| 12 | 빈 값 (지운 search_terms 자리) | string16 |
| 13 | http_status_code | int |
| 14 | referrer_policy | int |
| 15 | 확장 정보 (개수, 키·값 문자열) | 맵 |
| 16 | task_id, parent_task_id, root_task_id, 자식 task 수 0 | int64 3개, int |

값을 읽는 규칙은 다음과 같습니다 (관찰).

- string 은 int32 바이트 수 뒤에 바이트가 옵니다. 그 뒤를 4바이트 경계까지 채웁니다.
- string16 은 int32 글자 수 뒤에 UTF-16LE 글자가 옵니다. 그 뒤를 4바이트 경계까지 채웁니다.
- 이 규칙으로 주소·제목·timestamp·http_status_code(200) 까지 제자리에서 읽혔습니다.
- 제목은 UTF-16LE 로 풀어야 합니다. 콘솔 기본 코드 페이지로 찍으면 한글이 깨졌습니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.
- 탭마다 저장하는 탐색 항목 수의 상한은 확인하지 못했습니다.

### Edge 의 SessionRestoreLog

Edge 프로필 폴더의 `EdgeSessions\SessionRestoreLog` 는 한 줄에 JSON 하나를 적은 글자 파일입니다 (관찰). Chrome 에는 이 파일이 없었습니다.

| 줄 모양 | 키 |
|---|---|
| 시작·끝 표시 | `logTime`, `session`(`"START"` 또는 `"END"`) |
| 내용 줄 | `logTime`, `level`, `location`, `message` |

- `logTime` 은 `"MMDD/HHMMSS"` 꼴입니다. 연도가 없습니다.
- `message` 에는 아래 같은 글이 적혀 있었습니다.

| message 예 | 알려 주는 것 |
|---|---|
| `Previous Session Exit Type: PreviousSessionExitType::kNormal` | 직전 세션이 어떻게 끝났는지 |
| `Browser Open Behavior: 2` | 브라우저를 열 때의 동작 설정 값 |
| `Valid session file found: SessionRestore` | 되살릴 세션 파일을 찾았는지 |
| `Delete session file Session_<숫자>, for SessionType SessionRestore` | 어떤 세션 파일을 지웠는지 |

- 지운 `Session_` 파일의 이름이 이 로그에 남습니다. 이름의 숫자가 곧 만든 시각이므로, 지금은 없는 옛 파일을 언제 만들었는지 알 수 있습니다.
- `START`·`END` 가 정확히 1시간 간격으로 찍힌 곳이 있었습니다. 그래서 이 표시가 브라우저 시작·종료를 뜻하는지는 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

- `Session_` 에 탐색 항목이 있으면, 이 파일을 쓰는 동안 이 프로필의 어느 탭에 그 주소와 제목이 있었습니다.
- 한 탭의 index 0, 1, 2… 는 그 탭 안에서 페이지를 연 순서입니다. 뒤로 가기 목록을 이 순서대로 되살릴 수 있습니다.
- ID 0 과 ID 2 로 어느 창의 몇 번째 탭이었는지 맞출 수 있습니다.
- `Session_` 의 ID 16·17 은 탭·창을 닫은 시각입니다. ID 21 은 탭이 마지막으로 활성 상태였던 시각입니다.
- `Tabs_` 에 항목이 있으면 이 프로필에서 그 탭이나 창을 닫은 적이 있습니다. ID 4 의 timestamp 가 닫은 시각입니다.
- `Tabs_` 에 ID 2(`kCommandRestoredEntry`)가 있으면 닫은 항목을 다시 연 적이 있습니다.
- 파일 이름의 숫자는 그 파일을 만든 시각입니다.
- Edge 의 `SessionRestoreLog` 에는 지운 `Session_` 파일 이름과 직전 세션이 끝난 형태가 남습니다.

### 증명하지 못하는 것

- 키보드 앞에 누가 있었는지는 남지 않습니다.
- 탭에 주소가 있었다는 것은 그 페이지를 읽었다는 뜻이 아닙니다.
- 기록이 없다고 그 페이지를 열지 않은 것은 아닙니다. 브라우저는 새 파일을 만들 때 내용을 비우고 다시 씁니다. 옛 파일은 몇 개만 남기고 지웁니다. `Tabs_` 는 상한을 넘은 오래된 항목을 지웁니다.
- 마커 앞뒤가 "처음 상태" 와 "그 뒤 변경" 이라는 해석은 소스로 확인하지 못했습니다. 이 구분을 근거로 순서를 단정하지 않습니다.
- 시크릿 창 (Incognito) 의 흔적은 [시크릿 모드로 무엇을 했나](../../../04-scenarios/activity/private-browsing.md) 에서 다룹니다.

보고서에는 "이 사이트를 보았다" 대신 이렇게 씁니다. "이 프로필의 `Session_<숫자>` 파일에 탭 ID 5 의 탐색 항목으로 A 주소가 있고, 같은 탭의 닫은 시각(ID 16)은 X(UTC) 이다."

## 시각 해석

모든 시각 값은 1601-01-01 00:00 UTC 부터 센 마이크로초입니다. 현지 시각이 아닙니다. 0 은 값이 없다는 뜻으로 봅니다. 바꾸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

| 값 | 있는 곳 | 뜻 | 주의할 점 |
|---|---|---|---|
| 파일 이름의 숫자 | `Session_`·`Tabs_` 이름 | 파일을 만든 시각 | 앞 파일과 겹치면 1마이크로초를 더합니다 |
| close_time | `Session_` ID 16·17 | 탭·창을 닫은 시각 | |
| last_active_time | `Session_` ID 21 | 탭이 마지막으로 활성 상태였던 시각 | |
| timestamp | 탐색 항목 11번째 값 | 탐색 항목에 붙은 시각 | 어떤 동작의 시각인지는 이 페이지에서 확인하지 못했습니다. [방문 기록](history.md) 의 방문 시각과 맞춰 본 뒤 씁니다 |
| timestamp | `Tabs_` ID 4 | 항목을 닫은 시각 | 0 인 레코드도 있었습니다 (관찰) |
| `logTime` | Edge `SessionRestoreLog` | 로그를 적은 시각 | 연도가 없습니다. UTC 로 보입니다 (관찰) |

- 파일 이름의 숫자를 UTC 로 바꾸면 파일을 만든 시각과 맞았습니다. 파일 수정 시각은 이보다 뒤였습니다(예: 이름 21:53:31, 수정 21:54:30 UTC) (관찰).
- `Tabs_` 는 항목 40개마다 파일을 새로 씁니다. 그래서 `Tabs_` 파일을 만든 시각이 처음 탭을 닫은 시각은 아닐 수 있습니다.
- `SessionRestoreLog` 의 `logTime` 이 UTC 로 보이는 근거는 다음과 같습니다. 새 `Session_` 파일 이름의 시각(UTC 02:39:12)과 그 줄의 `logTime`(023912)이 같았습니다. 그 PC 의 시간대는 한국 표준시였습니다 (관찰).
- `logTime` 에는 연도가 없으므로, 같은 줄에 나온 `Session_` 이름의 시각으로 연도를 채웁니다.
- 여러 기록을 한 시간 축에 놓는 법은 [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 함정과 한계

- **`Session Storage` 폴더와 헷갈리지 않습니다.** 이름이 비슷하지만 웹 페이지의 저장소입니다.
- **실행 중에는 최신 파일이 잠깁니다.** 브라우저가 열려 있는 동안 가장 최근 `Session_`·`Tabs_` 는 잠겨서 읽히지 않았습니다(Device or resource busy) (관찰). 라이브 수집은 [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md) 절차를 따릅니다.
- **원본 프로필로 브라우저를 띄우지 않습니다.** 브라우저는 새 세션 파일을 만들고 옛 파일을 지우는 동작을 합니다. 원본을 열면 지금 남은 파일이 사라질 수 있습니다. 해시를 기록한 사본을 읽습니다.
- **명령 ID 의 뜻은 파일마다 다릅니다.** `Session_` 과 `Tabs_` 는 ID 목록이 따로 있습니다. 같은 6 이라도 뜻이 다릅니다.
- **판마다 ID 가 바뀝니다.** 옛 ID(1·5·10·11·22·26)는 지금 쓰지 않습니다. 한 판에 맞춘 파서가 다른 판 파일을 잘못 읽을 수 있습니다.
- **옛 이름만 찾는 도구가 있습니다.** `Current Session` 같은 옛 이름만 찾는 도구는 요즘 판 프로필에서 아무것도 찾지 못합니다.
- **암호화 파일은 그대로 읽을 수 없습니다.** 버전 5 파일은 키를 풀기 전에는 레코드 길이와 개수만 알 수 있습니다. 관찰한 Chrome 153 에는 평문 짝 파일이 함께 있었으므로 먼저 평문 폴더를 봅니다. 브라우저 암호화의 바탕은 [DPAPI 구조](../../../01-foundations/protection/data-protection-api/index.md) 에서 다룹니다.
- **지운 파일도 찾아봅니다.** 옛 `Session_`·`Tabs_` 파일은 지워도 디스크에 남을 수 있습니다. [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) 와 [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 을 함께 씁니다.
- **Whale 은 따로 확인합니다.** 이 페이지의 구조는 Chrome·Edge 에서 확인한 것입니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 모두 이 페이지의 규칙으로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다. `pp` 는 4바이트 경계를 맞추는 채움 바이트이고, 값은 읽지 않습니다.

**파일 머리.** 평문 파일(버전 3)과 암호화 파일(버전 5)의 첫 8바이트입니다.

```
53 4E 53 53 03 00 00 00    서명 "SNSS" + 버전 3 (평문)
53 4E 53 53 05 00 00 00    서명 "SNSS" + 버전 5 (암호화)
```

**마지막 활성 시각 (Session_ ID 21).** 탭 ID 5 가 2024-01-01 00:00:00 UTC 에 마지막으로 활성 상태였다는 레코드입니다.

```
11 00                      레코드 크기 17 (ID 1 + 내용 16)
15                         명령 ID 21
05 00 00 00                탭 ID 5
pp pp pp pp                빈칸 4바이트
00 60 A7 58 6D 6C 2F 00    int64 = 13348540800000000 → 2024-01-01 00:00:00 UTC
```

**탐색 항목 첫머리 (Session_ ID 6).** 탭 ID 5 의 첫 탐색 항목으로 주소 `https://a.com/`, 제목 "예시" 가 들어간 레코드의 앞부분입니다.

```
ss ss                      레코드 크기
06                         명령 ID 6
LL LL LL LL                Pickle 내용 길이 (레코드 내용 크기 − 4)
05 00 00 00                탭 ID 5
00 00 00 00                index 0 (이 탭의 첫 탐색 항목)
0E 00 00 00                주소 길이 14바이트
68 74 74 70 73 3A 2F 2F    "https://"
61 2E 63 6F 6D 2F pp pp    "a.com/" + 채움 2바이트
02 00 00 00                제목 글자 수 2
08 C6 DC C2                "예시" (UTF-16LE)
..                         encoded_page_state, transition_type … 이 이어집니다
```

**암호화 레코드 첫머리 (버전 5).**

```
LL LL LL LL                레코드 길이 (uint32) = 짝 평문 레코드 크기 + 31
76 32 30                   "v20"
..                         나머지 (풀기 전에는 읽을 수 없음)
```

### 공개 도구로 한 번

Python 만으로 평문 파일(버전 3)의 레코드를 훑을 수 있습니다. 아래 스크립트는 탐색 항목의 탭 ID·index·주소·제목을 뽑습니다. `Session_` 에서는 ID 16·21 의 시각을, `Tabs_` 에서는 ID 4 의 닫은 시각을 함께 뽑습니다. 끝에 명령 ID 별 개수를 찍습니다.

```python
import os, struct, sys, datetime as dt
from collections import Counter

EPOCH = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)

def when(v):
    return (EPOCH + dt.timedelta(microseconds=v)).isoformat() if v else '-'

def read_str(b, p, wide=False):
    n = struct.unpack_from('<i', b, p)[0] * (2 if wide else 1)
    s = b[p + 4:p + 4 + n].decode('utf-16-le' if wide else 'utf-8', 'replace')
    return s, p + 4 + ((n + 3) & ~3)  # 4바이트 경계까지 건너뜁니다

path = sys.argv[1]
data = open(path, 'rb').read()
sig, ver = struct.unpack_from('<ii', data, 0)
if sig != 0x53534E53 or ver != 3:
    sys.exit(f'평문 SNSS(버전 3)가 아닙니다: 서명 {sig:#x}, 버전 {ver}')

tabs_file = os.path.basename(path).startswith('Tabs_')
nav_id = 1 if tabs_file else 6
count, pos = Counter(), 8
while pos + 3 <= len(data):
    size = struct.unpack_from('<H', data, pos)[0]
    cid, body = data[pos + 2], data[pos + 3:pos + 2 + size]
    pos += 2 + size
    count[cid] += 1
    if cid == nav_id:
        tab, index = struct.unpack_from('<ii', body, 4)
        url, p = read_str(body, 12)
        title, _ = read_str(body, p, wide=True)
        print('탐색', tab, index, url, title, sep='\t')
    elif not tabs_file and cid in (16, 21):
        tab, t = struct.unpack_from('<i4xq', body)
        print('탭 닫음' if cid == 16 else '마지막 활성', tab, when(t), sep='\t')
    elif tabs_file and cid == 4:
        entry, index, t = struct.unpack('<iiq', body)
        print('닫은 시각', entry, index, when(t), sep='\t')
print('명령 ID별 개수', sorted(count.items()))
```

- 사본 파일에 `python -X utf8 snss_list.py Session_<숫자> > out.txt` 처럼 실행합니다. `-X utf8` 을 주면 한글 제목을 파일에 그대로 씁니다.
- 파일 이름이 `Tabs_` 로 시작하면 `Tabs_` 의 ID 목록으로 읽습니다. 이름을 바꿔 저장했다면 원래 이름을 살려 둡니다.
- 마지막 줄의 ID 별 개수로 이 판에 모르는 ID 가 있는지 봅니다.
- SNSS 를 읽는 공개 파서도 있습니다. 판이 바뀌면 명령 ID 와 내용이 달라지므로, 도구 결과를 이 스크립트나 헥스와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문 기록 | 탐색 항목의 주소를 실제로 방문한 시각과 횟수 | [방문·다운로드 기록](history.md) |
| 캐시 | 탭에 있던 페이지의 사본 | [캐시](cache.md) |
| 쿠키 | 세션 복원 설정 때문에 남은 세션 쿠키 | [쿠키](cookies.md) |
| 웹 저장소 | 이름이 비슷한 `Session Storage` 의 값 | [웹 저장소](local-storage-indexeddb.md) |
| 확장 프로그램 | `Session_` ID 13(SetExtensionAppID)에 적힌 확장 앱 ID 가 어느 확장인지 | [확장 프로그램](extensions.md) |
| $MFT·$UsnJrnl | 세션 파일을 만들고 지운 시각. 이름의 시각과 맞춰 봅니다 | [마스터 파일 테이블](../../filesystem/mft.md), [USN 변경 저널](../../filesystem/usnjrnl.md) |
| 프리페치 | 브라우저를 실행한 시각 | [프리페치](../../execution/prefetch/index.md) |
| 켜짐·꺼짐 이벤트 | Edge 로그의 직전 종료 형태와 PC 종료 기록 | [켜짐·꺼짐](../../event-logs/power-on-off-events.md) |

웹 사용 전체를 한 흐름으로 묶는 순서는 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다. 같은 파일 구조를 쓰는 다른 앱은 [크롬 계열 앱 공통 구조](../../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다.

## 실습

크롬이나 엣지를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. 프로필 폴더에 옛 이름(`Current Session` 등)과 `Sessions` 폴더 가운데 어느 것이 있습니까? `Sessions_Encrypted` 도 있습니까?
2. `Session_`·`Tabs_` 파일 이름의 숫자를 UTC 로 바꾸면 언제입니까? $MFT 의 파일 생성 시각과 같습니까?
3. 각 파일 머리의 버전은 몇입니까?
4. `Session_` 에서 명령 ID 별 개수를 세어 봅니다. 마커(255)는 몇 번째 레코드에 있습니까?
5. 탭 하나를 골라 index 0 부터 차례로 주소를 적어 봅니다. 방문 기록에 같은 주소가 같은 순서로 있습니까?
6. `Tabs_` 의 닫은 시각(ID 4)을 모아 시간 축에 놓습니다. 0 인 값은 몇 개입니까?
7. Edge 검체라면 `SessionRestoreLog` 에서 지운 `Session_` 이름을 모두 찾습니다. 그 가운데 디스크에 남아 있는 파일이 있습니까?

## 참고 문헌

1. Chromium 소스, *components/sessions/core/command_storage_backend.cc* (파일 머리·버전·마커·파일 이름·암호화 폴더·옛 파일 정리). https://chromium.googlesource.com/chromium/src/+/HEAD/components/sessions/core/command_storage_backend.cc
2. Chromium 소스, *components/sessions/core/session_service_commands.cc* (`Session_` 명령 ID 와 내용). https://chromium.googlesource.com/chromium/src/+/HEAD/components/sessions/core/session_service_commands.cc
3. Chromium 소스, *components/sessions/core/serialized_navigation_entry.cc* (탐색 항목을 쓰는 순서). https://chromium.googlesource.com/chromium/src/+/HEAD/components/sessions/core/serialized_navigation_entry.cc
4. Chromium 소스, *components/sessions/core/tab_restore_service_impl.cc* (`Tabs_` 명령 ID, 닫은 시각, 다시 쓰는 주기). https://chromium.googlesource.com/chromium/src/+/HEAD/components/sessions/core/tab_restore_service_impl.cc
5. Chromium 소스, *components/sessions/core/tab_restore_service_helper.h* (항목 상한 `kMaxEntries`). https://chromium.googlesource.com/chromium/src/+/HEAD/components/sessions/core/tab_restore_service_helper.h
