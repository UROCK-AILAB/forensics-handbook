# 색인 해석 함정 (색인 범위·재구성)

> 위치: [윈도 검색 색인 DB (Windows Search)](index.md) > 색인 해석 함정

## 한 줄 요약

색인 DB 는 색인 범위 안의 파일만 담습니다. 색인을 초기화하면 DB 를 새로 만들고 처음부터 다시 색인합니다. 그래서 "색인에 없다" 나 "색인 기록이 짧다" 를 그대로 사실로 옮기면 틀릴 수 있습니다. 이 페이지는 색인 범위, 색인 방식, 재구성, 시각, 사용자 구분에서 생기는 오해를 정리합니다.

## 색인 범위 (Crawl Scope)

### 범위는 어떻게 정해지나

색인 범위는 기본으로 더해진 주소에 앱·사용자·그룹 정책이 더한 주소를 보태고, 사용자·그룹 정책이 뺀 주소를 덜어 내어 정해집니다. Microsoft 개발 문서가 적은 기본 범위는 문서·음악·사진·동영상 같은 기본 라이브러리 위치이고, Microsoft 지원 문서는 설정의 두 모드를 설명합니다.

| 모드 | 색인하는 곳 |
|---|---|
| Classic | 문서·사진·음악 폴더와 바탕 화면 |
| Enhanced | 모든 사용자 폴더와 파일을 포함한 PC 전체 |

### 검색 루트와 범위 규칙

검색 루트 (Search Root) 는 프로토콜, 사이트 또는 사용자 SID, 경로로 이루어지고, 범위 규칙 (Scope Rule) 은 검색 루트 안의 주소를 넣거나 뺍니다. 예를 들어 `file:///C:\WorkteamA\ProjectFiles\` 를 넣고, 그 아래 `file:///C:\WorkteamA\ProjectFiles\Prototypes\` 를 뺄 수 있습니다. 범위 규칙은 사용자, 그룹 정책, 제3자 개발자가 정할 수 있습니다. 그룹 정책 규칙은 사용자가 바꿀 수 있는 기본 규칙일 수도 있고, 사용자가 풀 수 없는 강제 제외 규칙일 수도 있습니다. 제어판에 접근할 수 있는 사용자는 기본 색인 범위를 바꿀 수 있습니다.

그래서 "색인에 없다" 는 "파일이 없었다" 는 뜻이 아닙니다. 범위 밖이면 처음부터 색인하지 않습니다.

### 레지스트리에 남은 색인 범위 (관찰)

아래는 Windows 11 25H2 PC 한 대에서 본 내용입니다. (확인 범위: Windows 11 25H2 빌드 26200.9457, PC 한 대)

`HKLM\SOFTWARE\Microsoft\Windows Search\CrawlScopeManager\Windows\SystemIndex` 아래에 세 키가 있었습니다.

| 키 | 그 PC 의 하위 항목 수 |
|---|---|
| `DefaultRules` | 23개 |
| `WorkingSetRules` | 61개 |
| `SearchRoots` | 5개 |

- 규칙 하나마다 `URL`, `Include`, `Default`, `Policy`, `Suppress`, `NoContent`, `Container`, `IntelligentlyAdded` 값이 있었습니다.
- 규칙 URL 은 드라이브 문자 뒤에 볼륨 GUID 를 대괄호로 붙인 꼴이었습니다. 예: `file:///C:\[64b506ce-…]\Users\*\AppData\` (`Include=0`, `Default=1`).
- `WorkingSetRules` 에는 `Default=1` 규칙과 `Default=0` 규칙이 섞여 있었습니다.
- 예를 들어 사용자 폴더의 `.android`, `.aws` 를 빼는 규칙은 `Default=0` 이었습니다.
- `SearchRoots` 에는 `defaultroot://{사용자 SID}/`, `winrt://{사용자 SID}/` 처럼 사용자 SID 가 든 루트가 있었습니다.
- 각 값의 정확한 뜻과 우선순위는 확인하지 못했습니다. 값 이름으로 뜻을 짐작해 보고서에 쓰지 않습니다.

검체에서는 SOFTWARE 하이브의 이 키를 먼저 읽어 둡니다. 조사하는 폴더가 규칙 목록에 들어 있는지, 빠져 있는지를 적습니다. 하이브를 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서, 볼륨 GUID 는 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다.

## 색인 방식 — 속성만, 또는 속성과 본문

색인 방식은 "속성만" 과 "속성과 본문" 두 가지입니다. 기본 설정에서는 글자가 든 파일의 본문도 색인하지만, "속성만" 방식으로 색인한 파일은 본문이 색인에 들어가지 않습니다. 파일 특성에 "본문 색인 안 함" 비트가 켜진 파일도 있습니다. 비트 값은 [파일 속성 되살리기](propertystore.md) 에 있습니다.

그래서 본문 낱말로 찾아지지 않는다고 그 낱말이 파일에 없었다고 말할 수 없습니다. 본문 확인은 파일 자체나 [파일 내용 검색](../../../03-techniques/analysis/content-search/index.md) 으로 합니다.

## 재구성 (Rebuild)

색인 초기화 (Reset) 는 DB 를 다시 만들고 전체 색인을 새로 하므로 오래 걸리고, 초기화하는 동안에는 검색할 수 있는 정보가 거의 없습니다. 처음 색인은 몇 시간까지 걸릴 수 있습니다.

속성 스키마를 다시 등록해 기존 속성 설정을 바꾸면 색인기가 반영하지 않을 수 있습니다. Microsoft 문서가 내놓는 해결책은 색인 재구성입니다.

확인하지 못한 점도 분명히 적습니다.

- 초기화 전 기록이 새 DB 에 이어지는지는 확인한 자료가 없으므로, 색인 기록이 짧다는 것만으로 PC 를 쓴 기간이 짧다고 쓰지 않습니다.
- 레지스트리 `Gather\Windows\SystemIndex` 키의 `CatalogResetSignature` 같은 값으로 재구성 시점을 알 수 있는지도 확인하지 못했습니다. 이 값은 [수집 기록](systemindex-gthr.md) 에서 다룹니다.

### 수집 시각이 몰리는 경우

수집 시각 (GatherTime) 은 색인이 파일을 처리한 시각이고, 처음 색인과 재구성은 전체를 새로 색인하며 몇 시간까지 걸릴 수 있습니다. 두 사실을 합치면, 처음 색인이나 재구성 직후에는 많은 파일의 수집 시각이 몇 시간 안에 몰릴 수 있습니다. 이런 묶음을 사용자가 그 시간에 파일을 많이 다룬 흔적으로 읽지 않습니다. 수집 시각의 정의는 [파일 속성 되살리기](propertystore.md) 에 있습니다.

## 시각 해석 — 다른 페이지에서 다루는 함정

| 함정 | 자세히 |
|---|---|
| 수집 시각을 파일을 연 시각으로 읽는 것 | [파일 속성 되살리기](propertystore.md) |
| XP·7 의 빅엔디언 FILETIME 을 리틀엔디언으로 읽어 엉뚱한 날짜를 얻는 것 | [위치와 형식](windows-edb-windows-db.md) |
| 수집 로그의 상위·하위 32비트 칸을 거꾸로 합치는 것 | [수집 기록](systemindex-gthr.md) |
| 지운 파일 행의 수집 시각을 삭제 시각으로 읽는 것 | [지운 파일·옛 파일 흔적 찾기](deleted-file-traces.md) |

## 크기와 분량

색인 크기는 대략 색인된 파일 크기의 10% 미만인데, 이 비율은 어림값입니다. DB 크기로 색인된 파일 수나 분량을 거꾸로 셈하지 않습니다.

## 사용자 구분

- 한 PC 의 `SearchRoots` 에는 사용자별 SID 가 든 루트가 있었습니다. (확인 범위: Windows 11 25H2, PC 한 대)
- 검색 프로토콜 호스트는 시스템용과 사용자용으로 나뉩니다. 자세한 내용은 [수집 기록](systemindex-gthr.md) 에 있습니다.
- 속성 저장소에는 `System_FileOwner` 칸이 있습니다(LevelBlue).
- 수집 기록 표에는 `SDID`·`RequiredSIDs` 칸이 있습니다(libyal).
- 이 칸들로 색인 기록을 특정 사용자와 잇는 구체적 방법은 확인하지 못했습니다.

그래서 기록마다 "어느 사용자의 파일" 인지 적을 때는 경로(`C:\Users\<이름>\…`)나 SID 루트 같은 근거를 함께 적습니다. 근거가 경로뿐이면 "이 사용자 프로필 폴더 아래의 파일" 이라고만 씁니다. SID 를 계정과 잇는 일은 [사용자 프로필 목록](../../system-account/profilelist.md) 에서 합니다.

## 흔한 오판과 바른 문장

| 흔한 오판 | 왜 틀리나 | 이렇게 씁니다 |
|---|---|---|
| "색인에 없으므로 이 PC 에 그 파일은 없었다." | 범위 밖 폴더는 처음부터 색인하지 않습니다. | "색인 DB 에서 이 파일 기록을 찾지 못했습니다. 그 폴더가 색인 범위에 들어 있었는지는 ○○ 규칙으로 확인했습니다." |
| "수집 시각에 사용자가 파일을 열었다." | 수집 시각은 색인이 파일을 처리한 시각입니다. | "색인이 이 파일의 속성을 ○○ 에 처리한 기록이 있습니다." |
| "색인 기록이 지난달부터 있으니 PC 를 지난달부터 썼다." | 초기화 전 기록이 이어지는지 알 수 없습니다. | "색인 DB 에서 가장 이른 수집 시각은 ○○ 입니다." |
| "본문 검색에 걸리지 않으니 그 낱말은 문서에 없었다." | 속성만 색인한 파일이나 본문 색인 안 함 파일이 있습니다. | "색인에서 그 낱말로 찾은 결과는 없습니다. 파일 본문은 따로 확인했습니다." |
| "소유자 칸이 A 이니 A 가 만든 파일이다." | 소유자 칸을 사용자 행동과 잇는 방법은 확인되지 않았습니다. | "속성 저장소의 소유자 칸 값은 ○○ 입니다." |

## 직접 확인해 보기

1. SOFTWARE 하이브에서 `Microsoft\Windows Search\CrawlScopeManager\Windows\SystemIndex` 키를 엽니다.
2. `DefaultRules`·`WorkingSetRules` 의 규칙마다 `URL`·`Include`·`Default` 값을 표로 적습니다.
3. 규칙 URL 의 대괄호 속 볼륨 GUID 를 적습니다. 같은 이미지의 볼륨 정보와 맞춰 어느 볼륨인지 정합니다.
4. `SearchRoots` 의 SID 를 [사용자 프로필 목록](../../system-account/profilelist.md) 으로 풉니다.
5. 조사하는 폴더가 어느 규칙에 걸리는지 적습니다.
6. 속성 저장소의 수집 시각을 시간 단위로 세어 분포를 봅니다. 몇 시간 안에 크게 몰린 묶음이 있으면 처음 색인이나 재구성의 흔적인지 따져 봅니다.

## 교차 검증

- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) — 색인 범위 규칙이 든 SOFTWARE 하이브를 읽습니다.
- [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) — 규칙 URL 의 볼륨 GUID 와 검색 루트의 SID 를 읽습니다.
- [사용자 프로필 목록](../../system-account/profilelist.md) — SID 를 프로필 폴더와 잇습니다.
- [시스템 기본 정보](../../system-account/os-version-computer-name-install-date-shutdown-t.md) — 설치 날짜와 가장 이른 수집 시각을 비교합니다.
- [파일 내용 검색](../../../03-techniques/analysis/content-search/index.md) — 색인에 기대지 않고 본문을 직접 찾습니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — 수집 시각을 "색인 처리" 로 따로 표시해 넣습니다.
- [이 파일을 누가 언제 열었나](../../../04-scenarios/activity/file-access.md) · [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) — 색인 기록을 사용자 행동과 잇는 조사 흐름입니다.

## 실습

공개 검체(NIST CFReDS 등)에서 Windows 10 또는 11 이미지를 골라 풀어 봅니다.

1. `CrawlScopeManager` 키 아래 규칙은 몇 개입니까? 사용자 폴더 전체가 들어 있습니까, 일부만 들어 있습니까?
2. `Include=0` 인 규칙은 어떤 폴더입니까?
3. 조사 시나리오에 나오는 파일 하나가 색인에 없다면, 그 파일의 폴더는 색인 범위 안이었습니까?
4. 속성 저장소에서 가장 이른 수집 시각은 언제입니까? 운영체제 설치 날짜와 얼마나 떨어져 있습니까?
5. 수집 시각이 몇 시간 안에 크게 몰린 묶음이 있습니까? 그 묶음은 설치 직후입니까, 한참 뒤입니까?
6. `SearchRoots` 의 SID 는 몇 개입니까? 모두 ProfileList 로 풀립니까?

## 참고 문헌

1. Microsoft 지원, "Search indexing in Windows" — https://support.microsoft.com/en-us/windows/search-indexing-in-windows-da061c83-af6b-095c-0f7a-4dfecda4d15a
2. Microsoft Learn, "Indexing process in Windows Search" — https://learn.microsoft.com/en-us/windows/win32/search/-search-indexing-process-overview
3. Microsoft Learn, "Using the Crawl Scope Manager" — https://learn.microsoft.com/en-us/windows/win32/search/-search-3x-wds-extidx-csm
4. Microsoft Learn, "ISearchCatalogManager::Reset" — https://learn.microsoft.com/en-us/windows/win32/api/searchapi/nf-searchapi-isearchcatalogmanager-reset
5. Microsoft Learn, "System.Search.GatherTime" — https://learn.microsoft.com/en-us/windows/win32/properties/props-system-search-gathertime
6. Phalgun Kulkarni·Julia Paluch, "Windows Search Index: The Forensic Artifact You've Been Searching For" (2023-04-26, LevelBlue/Stroz Friedberg 블로그) — https://levelblue.com/blogs/strozfriedberg/windows-search-index-the-forensic-artifact-youve-been-searching-for
7. libyal esedb-kb, "Windows Search" (XP~8 기준) — https://raw.githubusercontent.com/libyal/esedb-kb/main/documentation/Windows%20Search.asciidoc
