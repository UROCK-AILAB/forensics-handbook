# 캐시 (cache2)

## 한 줄 요약

파이어폭스는 내려받은 웹 자원을 프로필 로컬 폴더의 `cache2` 폴더에 저장합니다. 항목마다 본문 데이터와 메타데이터가 한 파일에 들어갑니다. 메타데이터에는 항목을 몇 번 열었는지, 마지막으로 언제 열고 언제 고쳤는지가 남습니다.

## 무엇을 기록하나 · 왜 생기나

- 브라우저는 페이지를 열 때 받은 이미지·스크립트·문서를 디스크에 저장해 둡니다. 같은 자원을 다시 받지 않으려는 것입니다.
- 캐시 항목 하나에는 자원의 본문과 함께 메타데이터 (metadata) 가 붙습니다. 메타데이터에는 원래 주소, 항목을 연 횟수, 시각 값이 들어갑니다.
- 캐시가 있다는 것은 그 자원을 실제로 받았다는 기록입니다. 방문 기록이 지워져도 캐시가 남아 있으면 무엇을 받았는지 볼 수 있습니다.

## 위치와 버전별 차이

- 디스크 캐시 버전 2(`cache2`)는 Firefox 32 부터입니다. 그 전 버전 1 은 같은 로컬 프로필 폴더 아래 `Cache` 폴더를 썼습니다.
- 캐시는 프로필 로컬 폴더 쪽에 있습니다. 본 폴더와 로컬 폴더의 차이는 [프로필 구조 (profiles.ini·prefs.js)](/02-artifacts/browsers/firefox/profiles-ini-prefs-js.md) 에서 다룹니다.

| Windows 판 | `cache2` 폴더 경로 예 |
|---|---|
| Vista·7 | `C:\Users\%USERNAME%\AppData\Local\Mozilla\Firefox\Profiles\%PROFILE%.default\cache2\` |
| XP | `C:\Documents and Settings\%USERNAME%\Local Settings\Application Data\Mozilla\Firefox\Profiles\%PROFILE%.default\cache2\` |

- 아래 항목 파일 구조는 파이어폭스 소스의 개발 중인 최신 코드(main 가지, 2026-09-23)에서 확인한 것입니다. 이때 항목 버전 상수는 4 입니다. 소스 주석은 버전 3 과 헤더 배치가 같다고 적었습니다.

## 구조

### 메타데이터 헤더

- 항목 파일 안에는 메타데이터 헤더 (CacheFileMetadataHeader) 가 있습니다. 헤더의 칸은 모두 32비트 정수입니다.
- 헤더는 네트워크 바이트 순서, 곧 빅엔디언 (big-endian) 으로 저장됩니다.

| 순서 | 칸 | 뜻 |
|---|---|---|
| 1 | `mVersion` | 항목 버전입니다 |
| 2 | `mFetchCount` | 캐시 항목을 연 횟수입니다 |
| 3 | `mLastFetched` | 캐시 항목을 마지막으로 연 시각입니다 |
| 4 | `mLastModified` | 캐시 항목을 마지막으로 고친 시각입니다. 서버의 `Last-Modified` 가 아닙니다 |
| 5 | `mFrecency` | 자주·최근 사용을 셈한 점수입니다 |
| 6 | `mExpirationTime` | 만료 시각입니다 |
| 7 | `mKeySize` | 키 문자열의 길이입니다 |
| 8 | `mFlags` | 플래그입니다 |

### 플래그

| 값 | 이름 | 뜻 |
|---|---|---|
| `1 << 0` | kCacheEntryIsPinned | 고정된 항목입니다 |
| `1 << 1` | kCacheEntryIsEncrypted | 데이터 조각과 메타데이터를 암호화해 저장합니다 |

- 암호화된 항목은 메타데이터 전체를 한 덩어리로 암호화합니다. 파일 끝의 오프셋 값에 암호화 표시를 싣습니다. 이 암호화가 어느 출시판부터 켜지는지, 기본으로 켜지는지는 확인하지 못했습니다.

### 정규화된 메타데이터 모양

소스가 설명하는 메타데이터의 모양은 아래와 같습니다. 파일 끝의 오프셋 워드는 떼어 낸 뒤입니다.

```
[hash32][hashes][header][key][elements]
```

- `header` 는 위의 메타데이터 헤더입니다.
- `key` 는 이 항목의 키 문자열입니다. 원래 주소가 여기에 들어갑니다.
- `elements` 는 이름·값 쌍의 묶음입니다. 요청 방식이나 응답 헤더가 여기에 담기는 것으로 알려져 있습니다. 다만 이번 조사에서 elements 의 키 이름과 값 형식은 확인하지 못했습니다.

### 확인하지 못한 것

- 항목 파일 전체의 정확한 배치입니다. 소스는 "파일 끝의 오프셋 워드" 만 언급합니다. 본문 데이터와 메타데이터의 크기·위치를 정확히 설명하지 않습니다.
- `cache2` 폴더 안의 구성입니다. `entries` 폴더, 색인 파일, 삭제 예정 항목 폴더의 이름과 역할을 확인하지 못했습니다.
- 항목 파일 이름이 키의 해시라는 것입니다.
- 조각(chunk) 크기와 해시 크기 상수입니다. 참고한 헤더 파일에는 없습니다.

## 증거로서 의미

### 증명하는 것

- 캐시 항목이 있다는 것은 그 자원을 이 브라우저가 실제로 받았다는 기록입니다.
- `key` 에 원래 주소가 남으므로, 어떤 자원을 받았는지 알 수 있습니다.
- `mFetchCount` 는 캐시 항목을 몇 번 열었는지 알려 줍니다. 네트워크에서 몇 번 받았는지와는 다릅니다.
- 본문 데이터가 남아 있으면 그때 받은 이미지·문서의 실제 내용을 볼 수 있습니다.

### 증명하지 못하는 것

- 캐시 항목이 있다고 사용자가 그 주소를 직접 열었다는 뜻은 아닙니다. 페이지 안에 끼워 넣은 이미지·스크립트도 캐시를 남깁니다.
- 사용자가 그 이미지를 화면에서 보았는지, 얼마나 오래 보았는지는 알 수 없습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 캐시가 없다고 받지 않은 것은 아닙니다. 캐시는 용량을 넘으면 항목을 지웁니다.

보고서에는 "그 이미지를 보았다" 대신 "이 프로필의 캐시에 그 주소의 자원이 있고, 이 항목을 마지막으로 연 시각은 X(UTC) 이다" 처럼 씁니다.

## 시각 해석

- 메타데이터 헤더의 시각 칸은 32비트 정수입니다. 헤더는 빅엔디언으로 저장됩니다.
- `mLastFetched`·`mLastModified`·`mExpirationTime` 은 1970년 1월 1일 (UTC) 부터 센 초입니다. 캐시 인터페이스 정의(nsICacheEntry.idl)의 설명에서 확인했습니다.
- `mLastFetched` 는 항목을 열 때, `mLastModified` 는 항목을 고칠 때 바뀝니다. 서버 쪽 수정 시각은 응답 헤더에서 따로 봅니다.
- 여러 기록을 한 시간 축에 놓을 때는 [타임라인 작성](/03-techniques/analysis/timeline/index.md) 을 따릅니다.

## 함정과 한계

- **암호화된 항목이 있습니다.** `kCacheEntryIsEncrypted` 플래그가 선 항목은 메타데이터와 데이터가 암호화되어 있습니다. 헥스로 바로 읽히지 않습니다.
- **`mLastModified` 를 서버 수정 시각으로 읽지 않습니다.** 이 값은 캐시 항목을 고친 시각입니다.
- **캐시는 용량을 넘으면 항목을 지웁니다.** 어떤 항목부터 지우는지는 이번 조사에서 확인하지 못했습니다. 캐시가 없다고 받지 않은 것은 아닙니다.
- **지운 항목은 되살리기 어렵습니다.** 옛 캐시를 찾으려면 [삭제 데이터 복구](/03-techniques/analysis/data-recovery/index.md), 섀도 복사본, 메모리도 봅니다.
- **버전 1 캐시일 수 있습니다.** Firefox 32 전 검체는 `Cache` 폴더를 씁니다. `cache2` 만 찾고 끝내지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

메타데이터 헤더는 32비트 정수 여덟 개입니다. 헤더는 빅엔디언입니다. 아래는 명세대로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다.

```
00 00 00 04    mVersion       = 4
00 00 00 03    mFetchCount    = 3 (항목을 세 번 엶)
65 92 00 80    mLastFetched   = 1704067200 초 → 2024-01-01 00:00:00 UTC
.. .. .. ..    mLastModified  (1970 기준 초)
.. .. .. ..    mFrecency
.. .. .. ..    mExpirationTime
00 00 00 2A    mKeySize       = 42 (키 문자열 길이)
00 00 00 00    mFlags         = 0 (고정 아님, 암호화 아님)
```

- `mFlags` 의 최하위 비트가 1 이면 고정된 항목입니다. 그다음 비트가 1 이면 암호화된 항목입니다.
- 빅엔디언이므로 앞쪽 바이트가 큰 자리입니다. 리틀엔디언으로 읽으면 값이 뒤집혀 엉뚱한 수가 나옵니다.

### 공개 도구로 한 번

- `cache2` 폴더를 통째로 사본으로 뜬 뒤, 파이어폭스 캐시 전용 공개 도구로 항목 목록과 원래 주소를 뽑습니다.
- 도구가 뽑은 주소·시각을 헤더에서 직접 읽은 값과 맞춰 봅니다. 도구가 초 단위 값을 UTC 로 바꿨는지 확인합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문·다운로드·즐겨찾기 | 캐시에 남은 자원의 주소를 방문 기록과 맞춰 봅니다 | [places.sqlite](/02-artifacts/browsers/firefox/places-sqlite.md) |
| 쿠키 | 같은 도메인의 쿠키가 언제 생겼는지 봅니다 | [쿠키 (cookies.sqlite)](/02-artifacts/browsers/firefox/cookies-sqlite.md) |
| 세션 복원 | 캐시를 남긴 시각에 열려 있던 탭을 봅니다 | [세션 복원 (sessionstore.jsonlz4)](/02-artifacts/browsers/firefox/sessionstore-jsonlz4.md) |
| 다른 브라우저 캐시 | 같은 자원을 다른 브라우저로 받았는지 봅니다 | [크롬 계열 캐시](/02-artifacts/browsers/chrome-edge-whale/cache.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](/04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

파이어폭스를 쓴 공개 검체(NIST CFReDS 등)에서 프로필 로컬 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. `cache2` 폴더가 있습니까, `Cache` 폴더가 있습니까? 어느 캐시 버전입니까?
2. 항목 파일 하나를 헥스로 열어 메타데이터 헤더의 `mFetchCount` 와 `mFlags` 를 읽어 봅니다.
3. `mFlags` 의 암호화 비트가 선 항목이 있습니까? 그런 항목의 메타데이터가 헥스로 읽힙니까?
4. 캐시에 남은 자원의 주소를 방문 기록의 주소와 맞춰 봅니다. 방문 기록에 없는데 캐시에만 있는 주소는 무엇입니까?

## 참고 문헌

1. Mozilla, *CacheFileMetadata.h* (파이어폭스 소스, main 가지 — 항목 버전, 헤더 칸, 바이트 순서, 플래그, 정규화된 메타데이터 모양). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/netwerk/cache2/CacheFileMetadata.h
2. *Mozilla Firefox — Forensics Wiki* (캐시 버전 2 도입, 폴더 위치). https://forensics.wiki/mozilla_firefox/
3. Mozilla, *nsICacheEntry.idl* (파이어폭스 소스, main 가지 — 연 횟수·시각 칸의 뜻과 단위). https://raw.githubusercontent.com/mozilla-firefox/firefox/main/netwerk/cache2/nsICacheEntry.idl
