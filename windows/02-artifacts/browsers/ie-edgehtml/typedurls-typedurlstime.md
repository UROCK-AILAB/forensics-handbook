# 주소창 입력 주소 (TypedURLs·TypedURLsTime)

## 한 줄 요약

IE 주소창에 입력한 주소는 사용자 하이브(NTUSER.DAT)의 `TypedURLs` 키에 `url1` 같은 이름의 값으로 남습니다. Windows 8 에서 소개된 `TypedURLsTime` 키에는 같은 번호의 값으로 입력 시각이 FILETIME 으로 남습니다.

## 무엇을 기록하나 · 왜 생기나

- 사용자가 IE 주소창에 입력한 주소를 기록합니다.
- 두 키 모두 사용자 하이브에 있습니다. 로그온한 사용자마다 따로 남습니다.
- `TypedURLs` 는 주소 문자열을 담습니다.
- `TypedURLsTime` 은 주소마다 시각 하나를 담습니다.
- 두 키는 값 이름(`url` 뒤의 번호)으로 짝을 맞춥니다.
- RegRipper 의 `typedurlstime` 플러그인은 `TypedURLsTime` 의 시각을 주소를 주소창에 입력한 때로 해석합니다.
- 같은 플러그인에는 "IE 를 끝내기 전에는 새 항목이 키에 추가되지 않는다" 는 주의가 적혀 있습니다.

## 위치와 버전별 차이

| 키 | 하이브 | 전체 경로 |
|---|---|---|
| `TypedURLs` | NTUSER.DAT | `HKCU\Software\Microsoft\Internet Explorer\TypedURLs` |
| `TypedURLsTime` | NTUSER.DAT | `HKCU\Software\Microsoft\Internet Explorer\TypedURLsTime` |

- 공개 수집 정의(ForensicArtifacts)는 이 키를 `HKEY_USERS\{사용자 SID}\Software\Microsoft\Internet Explorer\TypedURLs\*` 로 적습니다. 사용자 SID 와 계정 이름을 잇는 방법은 [사용자 프로필 목록](../../system-account/profilelist.md) 에서 다룹니다.
- `TypedURLsTime` 은 Windows 8 에서 나온 값으로 소개됐습니다. 그보다 앞선 Windows 검체에는 이 키가 없을 수 있습니다.
- Windows 11 25H2 PC 의 `TypedURLs` 키에는 `url1` 값 하나(REG_SZ)가 있었습니다. `TypedURLsTime` 키는 없었습니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)

하이브 파일의 구조와 수집 방법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

```
HKCU\Software\Microsoft\Internet Explorer\TypedURLs
    url1   = <주소 문자열>
    url2   = <주소 문자열>
    …

HKCU\Software\Microsoft\Internet Explorer\TypedURLsTime
    url1   = <8바이트 FILETIME>
    url2   = <8바이트 FILETIME>
    …
```

- `TypedURLs` 의 값은 문자열입니다. 한 PC 에서 본 값의 형식은 REG_SZ 였습니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)
- `TypedURLsTime` 의 값은 8바이트이고 FILETIME 으로 읽습니다.
- `TypedURLs\url3` 의 시각은 `TypedURLsTime\url3` 에 있습니다. 번호가 같은 값끼리 짝입니다.

## 증거로서 의미

### 증명하는 것

- 이 사용자 하이브의 IE 주소창 입력 기록에 이 주소가 남아 있었습니다.
- `TypedURLsTime` 에 짝이 있으면, 그 주소를 입력한 때로 해석되는 시각이 있습니다.

### 증명하지 못하는 것

- 주소를 입력한 뒤 페이지가 실제로 열렸는지는 알 수 없습니다. 방문 기록과 맞춰 봐야 합니다.
- 누가 키보드 앞에 있었는지는 알 수 없습니다. 하이브가 가리키는 것은 로그온한 계정입니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 값 번호의 순서가 입력 순서라는 해석과 키에 남는 최대 개수는 이번에 연 자료로 확인하지 못했습니다. 번호만 보고 "가장 최근 입력" 을 단정하지 않습니다.
- 이 키는 IE 키 아래에 있습니다. 옛 엣지가 이 키를 쓰는지는 이번에 연 자료로 확인하지 못했습니다. 옛 엣지 사용 흔적으로 읽으려면 따로 근거가 필요합니다.

보고서에는 "이 계정의 NTUSER.DAT 에 있는 IE 주소창 입력 기록에 이 주소가 있고, 짝을 이루는 TypedURLsTime 값은 이 시각이다" 처럼 씁니다.

## 시각 해석

- `TypedURLsTime` 값을 FILETIME 으로 바꿉니다. 변환 방법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 이 시각이 UTC 인지는 참고한 플러그인 설명에 적혀 있지 않습니다. 같은 주소가 [웹캐시 DB](webcachev01-dat.md) 나 [index.dat](index-dat.md) 방문 기록에 있으면 두 시각을 맞춰 봅니다.
- `TypedURLsTime` 이 없는 시스템에서는 입력 시각을 따로 알 수 없습니다.
- `TypedURLs` 키의 마지막 기록 시각 (LastWrite) 을 가장 최근 입력 시각으로 보는 해석이 있습니다. 이 해석은 이번에 연 자료로 확인하지 못했습니다. 키의 마지막 기록 시각은 그 키가 바뀐 때를 말할 뿐, 어느 값이 바뀌었는지는 말하지 않습니다.

## 함정과 한계

- **IE 가 켜진 채로 수집하면 최근 입력이 빠질 수 있습니다.** IE 를 끝내기 전에는 새 항목이 키에 추가되지 않는다는 주의가 있습니다. 라이브 수집에서는 이 점을 기록해 둡니다.
- **`TypedURLsTime` 이 없을 수 있습니다.** Windows 8 에서 소개된 키입니다. Windows 11 PC 한 대에서도 이 키가 없었습니다. (확인 범위: Windows 11 25H2, 빌드 26200 PC 한 대)
- **번호가 같은지 꼭 확인합니다.** 두 키의 값 개수가 다를 수 있습니다. 짝이 없는 값에 다른 번호의 시각을 붙이지 않습니다.
- **값이 없다고 입력이 없었던 것은 아닙니다.** 값은 지우거나 덮일 수 있습니다. 이전 시점의 하이브를 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 에서 꺼내 비교합니다.
- **하이브 사본만 보면 최근 변경이 빠질 수 있습니다.** 하이브 로그를 반영하는 방법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 명세로 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**`TypedURLsTime` 값 8바이트.**

```
00 C0 89 76 45 3C DA 01
```

1. 8바이트를 리틀 엔디언으로 읽으면 `0x01DA3C457689C000` 입니다.
2. 10진수로 바꾸면 133485408000000000 입니다.
3. 이 수는 1601-01-01 부터 센 100나노초 단위의 수입니다.
4. 날짜로 바꾸면 2024-01-01 00:00:00 입니다.

**`TypedURLs` 값의 문자열.** REG_SZ 문자열은 UTF-16LE 로 저장됩니다. `http://` 는 아래처럼 보입니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

```
68 00 74 00 74 00 70 00 3A 00 2F 00 2F 00   h.t.t.p.:././.
```

### 공개 도구로 한 번

1. 사용자 프로필에서 NTUSER.DAT 와 하이브 로그를 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 `Software\Microsoft\Internet Explorer\TypedURLs` 와 `TypedURLsTime` 을 엽니다.
3. RegRipper 의 `typedurlstime` 플러그인처럼 두 키를 짝지어 주는 공개 도구로 결과를 뽑습니다.
4. 도구 결과의 한 줄을 골라 위 헥스 풀이로 시각을 직접 한 번 바꿔 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 웹캐시 DB | 입력한 주소가 실제로 열려 방문 기록에 남았는지 봅니다 | [웹캐시 DB (WebCacheV01.dat)](webcachev01-dat.md) |
| 옛 기록 파일 | IE 9 이전 시스템에서 같은 주소의 방문 기록을 봅니다 | [옛 기록 파일 (index.dat)](index-dat.md) |
| 저장 비밀번호 | 입력한 주소에 저장 비밀번호가 있는지 봅니다 | [저장 비밀번호 (IntelliForms)](intelliforms.md) |
| 탐색기 입력 기록 | 같은 계정이 탐색기 주소창에 입력한 경로를 봅니다 | [탐색기 입력 기록](../../file-folder-usage/typedpaths-wordwheelquery.md) |
| 실행 창 명령 기록 | 실행 창에 주소를 넣어 연 흔적이 있는지 봅니다 | [실행 창 명령 기록](../../execution/runmru.md) |
| 섀도 복사본 | 이전 시점 하이브에 지금은 없는 값이 있는지 봅니다 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 다른 브라우저 | 같은 주소를 다른 브라우저로 열었는지 봅니다 | [크롬 계열 브라우저](../chrome-edge-whale/index.md), [파이어폭스](../firefox/index.md) |

웹 사용 전체를 재구성하는 흐름은 [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) 에 있습니다.

## 실습

IE 를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 NTUSER.DAT 를 꺼내 아래 질문을 풀어 봅니다.

1. 검체의 Windows 버전은 무엇입니까? `TypedURLsTime` 키가 있어야 하는 버전입니까?
2. `TypedURLs` 에 값이 몇 개 있습니까? `TypedURLsTime` 의 값 개수와 같습니까?
3. `url1` 의 시각을 직접 FILETIME 으로 바꿔 봅니다. 도구가 보여 주는 값과 같습니까?
4. 입력한 주소 가운데 방문 기록에 없는 주소가 있습니까?
5. 입력 시각과 같은 주소의 방문 기록 시각은 몇 초 차이 납니까? 시간대 차이만큼 벌어져 있지는 않습니까?

## 참고 문헌

1. ForensicArtifacts, *artifacts/data/webbrowser.yaml* (`HKEY_USERS\{SID}` 기준 수집 경로). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
2. Forensics Wiki, *Internet Explorer* (`TypedURLs` 키 경로). https://forensics.wiki/internet_explorer
3. RegRipper 3.0, *plugins/typedurlstime.pl* (`TypedURLsTime` 키, 값 형식, 짝 맞추기, 시각 해석, IE 종료 전 기록 주의). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/typedurlstime.pl
