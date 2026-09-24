# 즐겨찾기 (Bookmarks)

## 한 줄 요약

크롬 계열 브라우저는 즐겨찾기를 프로필 폴더의 `Bookmarks` 파일에 JSON 글자로 저장합니다. 항목마다 추가한 시각과 마지막으로 연 시각이 있습니다. 폴더에는 마지막으로 바뀐 시각이 하나 더 있습니다. 시각은 모두 1601-01-01 UTC 부터 센 마이크로초입니다. 방문 기록을 지워도 즐겨찾기는 남습니다.

## 무엇을 기록하나 · 왜 생기나

크롬은 이 기능을 "북마크" 라고 부르고, 엣지는 "즐겨찾기" 라고 부릅니다. 파일 이름은 둘 다 `Bookmarks` 입니다. 사용자가 즐겨찾기를 추가하거나 옮기거나 지우면 브라우저가 이 파일을 다시 씁니다. 즐겨찾기를 열기만 해도 마지막으로 연 시각이 바뀌어 파일을 다시 씁니다.

파일에는 다음이 남습니다.

- 즐겨찾기 이름과 URL
- 들어 있는 폴더와 폴더 안의 순서
- 항목을 추가한 시각과 마지막으로 연 시각
- 폴더가 마지막으로 바뀐 시각

동기화를 켜면 다른 기기에서 만든 즐겨찾기도 이 파일에 들어옵니다. 시크릿 창에서 만든 즐겨찾기도 일반 프로필에 저장됩니다. Google 도움말은 시크릿 모드를 나가도 저장한 북마크는 남는다고 적습니다([시크릿 모드로 무엇을 했나](/04-scenarios/activity/private-browsing.md)).

프로필 폴더를 찾고 계열 브라우저를 가리는 법은 [프로필 폴더와 계열 브라우저 구분](/01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)에서 다룹니다. 이 페이지는 즐겨찾기 파일만 다룹니다.

## 위치와 버전별 차이

### 파일 위치

| 브라우저 | 사용자 데이터 폴더 (기본값) |
|---|---|
| Chrome | `%LOCALAPPDATA%\Google\Chrome\User Data` |
| Edge | `%LOCALAPPDATA%\Microsoft\Edge\User Data` |
| Whale | `%LOCALAPPDATA%\Naver\Naver Whale\User Data` |

파일은 그 아래 프로필 폴더에 있습니다. 예를 들면 `...\User Data\Default\Bookmarks` 입니다. 파일에는 확장자가 없습니다. 프로필이 여럿이면 `Profile 1`, `Profile 2` 같은 폴더마다 파일이 따로 있습니다.

사용자 데이터 폴더는 옮길 수 있습니다. 사용자는 `--user-data-dir` 실행 인자로 위치를 바꿀 수 있습니다. 엣지는 그룹 정책 `UserDataDir` 로도 바꿀 수 있습니다. 이 정책은 레지스트리 `SOFTWARE\Policies\Microsoft\Edge` 아래 `UserDataDir` 값(REG_SZ)에 들어갑니다. 기본 위치에 파일이 없으면 바로가기의 실행 인자와 이 정책 값을 확인합니다.

### 한 프로필 안의 즐겨찾기 파일

아래 파일 이름은 Chromium 소스의 상수에서 옮겼습니다.

| 파일 | 내용 |
|---|---|
| `Bookmarks` | 기기에 저장한 즐겨찾기. 동기화를 켰다면 동기화하는 즐겨찾기도 여기 있습니다 |
| `Bookmarks.bak` | `Bookmarks` 의 이전 사본 |
| `AccountBookmarks` | 계정 저장소 (Account Storage) 즐겨찾기. 동기화를 켜지 않고 계정에 로그인한 경우에 씁니다 |
| `AccountBookmarks.bak` | `AccountBookmarks` 의 이전 사본 |
| `EncryptedBookmarks2` · `EncryptedAccountBookmarks2` | 같은 내용을 암호화한 파일 |

`Bookmarks.bak` 은 한 번 실행하는 동안 처음 저장하기 바로 전에 만듭니다. 이때 브라우저는 `Bookmarks` 를 그대로 복사합니다. 그 실행에서 즐겨찾기가 바뀌지 않으면 `.bak` 도 바뀌지 않습니다. 그래서 `.bak` 은 "즐겨찾기가 바뀐 마지막 실행이 시작될 때의 모습" 에 가깝습니다.

### 암호화 파일

현재 Chromium 소스(2026년 9월 main 가지)에는 즐겨찾기 암호화 기능이 기본으로 켜져 있습니다. 기본 단계는 평문 파일과 암호화 파일을 둘 다 쓰고, 읽을 때는 평문 파일만 읽는 단계입니다. 소스에는 암호화 파일만 쓰는 단계도 정의돼 있습니다. 암호화는 쿠키·비밀번호와 같은 운영체제 암호화 계층(OSCrypt)을 씁니다. 키를 구하는 법은 [쿠키·비밀번호 암호화](/01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md)에서 다룹니다.

이 기능이 어느 안정 버전부터 켜졌는지는 확인하지 못했습니다. 엣지·웨일이 같은 설정을 따르는지도 확인하지 못했습니다. 검체에 암호화 파일이 있으면 평문 파일과 저장 시각을 비교합니다. 옛 이름인 `EncryptedBookmarks` · `EncryptedAccountBookmarks` 가 남아 있을 수도 있습니다.

### 버전에 따라 달라지는 칸

파일 형식은 Windows 버전이 아니라 브라우저 버전에 따라 달라집니다.

- 옛 버전이 쓴 파일에는 `guid` 나 `date_last_used` 가 없을 수 있습니다.
- 현재 소스는 파일을 읽을 때 `date_last_used` 가 없으면 0 으로 채웁니다.
- `date_added` 가 없으면 파일을 읽은 순간의 시각으로 채웁니다. 이 값은 다음 저장 때 파일에 적힙니다.
- 동기화 명세에는 마지막으로 연 시각을 동기화하는 칸이 M106 에 들어왔다고 적혀 있습니다.

## 구조

파일은 UTF-8 JSON 글자 파일입니다. 데이터베이스가 아니므로 페이지·레코드 구조가 없습니다.

### 맨 위의 키

| 키 | 뜻 |
|---|---|
| `checksum` | 항목 내용으로 계산한 MD5 값. 16진 소문자 32자리입니다 |
| `checksum_sha256` | SHA-256 값. 기본으로 꺼진 기능이 켜졌을 때만 적습니다 |
| `roots` | 최상위 폴더 셋. `bookmark_bar`(북마크바), `other`(기타), `synced`(모바일) |
| `sync_metadata` | 동기화 상태 정보. 있을 때만 적습니다 |
| `version` | 형식 버전. 현재 1 입니다 |

### 항목(노드)의 키

| 키 | URL 항목 | 폴더 | 뜻 |
|---|---|---|---|
| `id` | ○ | ○ | 프로필 안에서 쓰는 번호. 숫자를 문자열로 적습니다 |
| `guid` | ○ | ○ | 기기 사이에서 같은 항목을 가리키는 식별자 |
| `name` | ○ | ○ | 화면에 보이는 이름 |
| `type` | `url` | `folder` | 항목 종류 |
| `url` | ○ | — | 주소 |
| `date_added` | ○ | ○ | 추가한 시각 |
| `date_last_used` | ○ | 0 | 마지막으로 연 시각. URL 항목만 값을 관리합니다 |
| `date_modified` | — | ○ | 폴더가 마지막으로 바뀐 시각 |
| `children` | — | ○ | 하위 항목 배열. 배열 순서가 화면 순서입니다 |
| `meta_info` | 선택 | 선택 | 브라우저 기능이 덧붙인 키-값 쌍 |

시각 세 칸은 숫자가 아니라 따옴표로 감싼 10진 문자열입니다. 최상위 폴더의 `name` 은 브라우저 화면 언어를 따릅니다. 그래서 폴더를 가릴 때는 이름 대신 `roots` 아래 키를 씁니다.

`checksum` 은 항목을 파일에 적는 순서대로 계산합니다. 순서는 `bookmark_bar` → `other` → `synced` 이고, 폴더는 자기 자신을 먼저 넣고 하위 항목을 넣습니다. 항목마다 넣는 값은 아래와 같습니다.

| 항목 | 넣는 값 (순서대로) |
|---|---|
| URL 항목 | `id`(UTF-8) · `name`(UTF-16LE) · 글자 `url` · `url`(UTF-8) |
| 폴더 | `id`(UTF-8) · `name`(UTF-16LE) · 글자 `folder` |

`guid` 와 시각 세 칸은 계산에 들어가지 않습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 파일을 마지막으로 저장할 때 이 프로필에 이 이름·URL 의 즐겨찾기가 있었습니다 | 이 PC 에서 이 사용자가 직접 추가했는지. 동기화로 들어왔을 수 있습니다 |
| `date_added` 무렵에 이 항목을 만들었습니다 (만든 기기의 시계 기준) | 그 페이지를 실제로 방문했는지. 방문하지 않고 주소만 넣을 수도 있습니다 |
| `date_last_used` 가 0 이 아니면 그 무렵에 이 항목을 열었습니다 | 몇 번 열었는지. 이 기기에서 열었는지 |
| 방문 기록을 지운 뒤에도 사용자가 저장해 둔 주소 | 즐겨찾기를 지운 시각. 지운 항목은 파일에 남지 않습니다 |

### 보고서 문장

아래 이름과 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`Default\Bookmarks` 의 북마크바 폴더에 `https://wiki.example.com/` 즐겨찾기가 있습니다. 추가 시각은 2025-03-14 01:23:45 UTC, 마지막으로 연 시각은 2025-03-20 06:05:10 UTC 로 기록돼 있습니다."
- 쓰면 안 되는 문장: "사용자가 3월 14일 이 PC 에서 사내 위키를 방문해 즐겨찾기에 넣었습니다."

## 시각 해석

### 세 시각이 바뀌는 때

아래는 현재 Chromium 소스(`bookmark_model.cc`)에서 확인한 동작입니다.

| 칸 | 바뀌는 때 | 바뀌지 않는 때 |
|---|---|---|
| `date_added` | 항목을 만들 때. 동기화로 들어온 항목은 원래 기기의 값을 받습니다 | 이름·URL 을 고칠 때, 다른 폴더로 옮길 때 |
| `date_last_used` | 항목을 열 때. 방문 기록을 지우면 그 범위에 든 값이 0 으로 돌아갑니다 | 이름·URL 을 고칠 때 |
| `date_modified` (폴더) | URL 항목을 추가할 때(추가 시각이 기존 값보다 늦으면). 항목을 이 폴더로 옮길 때 | 항목을 지울 때. 이름·URL 을 고칠 때 |

- 방문 기록 삭제는 `ClearLastUsedTimeInRange` 가 처리합니다. 전체 기간으로 지우면 모든 URL 항목의 `date_last_used` 가 0 이 됩니다.
- 동기화 명세에서 `creation_time_us` 는 `date_added` 에 대응합니다. 그래서 다른 기기에서 만든 항목의 `date_added` 는 그 기기 시계의 값입니다.
- `date_last_used` 도 M106 부터 동기화합니다. 다른 기기에서 연 시각일 수 있습니다.

### 단위와 기준

시각은 1601-01-01 00:00:00 UTC 부터 센 마이크로초입니다. 흔히 WebKit 시각이라고 부릅니다. FILETIME(100나노초 단위)과 기준일은 같고 단위만 다릅니다. 바꾸는 법은 [시각 값 형식](/01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)에서 다룹니다. 현지 시각으로 옮길 때는 [시간대 설정](/02-artifacts/system-account/time-zone.md)을 봅니다.

2012-12-14 부터 2044-08-23 까지의 값은 모두 `13` 으로 시작하는 17자리 수입니다. 이 범위를 벗어난 값은 0 이거나 조작·손상을 의심합니다.

### 파일 자체의 NTFS 시각

브라우저는 저장할 때 같은 폴더에 임시 파일을 먼저 씁니다. 그다음 임시 파일로 원래 파일을 바꿔 치웁니다. 저장은 변경이 생긴 뒤 최대 2.5초 안에 한 번 묶어서 합니다.

- `Bookmarks` 의 수정 시각은 마지막 저장 무렵입니다. 즐겨찾기를 열기만 해도 저장이 일어나므로 추가 시각으로 읽지 않습니다.
- 파일 생성 시각은 뜻이 분명하지 않습니다. 첫 즐겨찾기 시각으로 쓰지 않습니다.
- `Bookmarks.bak` 의 시각은 즐겨찾기가 바뀐 마지막 실행의 첫 저장 무렵입니다.

## 함정과 한계

1. **`date_last_used` 가 0 이면 한 번도 안 열었다고 봅니다.** 방문 기록 삭제로 0 이 됐을 수 있습니다. 옛 버전이 쓴 파일에는 이 칸이 아예 없습니다.
2. **동기화 항목을 이 PC 의 행위로 씁니다.** 파일만으로는 항목마다 어느 기기에서 만들었는지 가리기 어렵습니다. `sync_metadata` 가 있으면 동기화를 쓴 프로필입니다.
3. **파일 하나만 봅니다.** 프로필마다 `Bookmarks`, `.bak`, `AccountBookmarks`, 암호화 파일이 있을 수 있습니다. 도구가 어느 파일을 읽었는지 확인합니다.
4. **`date_added` 를 그대로 믿습니다.** 이 칸이 없던 파일은 브라우저가 읽은 순간의 시각으로 채웁니다. 여러 항목의 `date_added` 가 한 시각에 몰려 있으면 가져오기·동기화·파일 복원을 먼저 의심합니다.
5. **`id` 의 빈 번호를 지운 항목으로 단정합니다.** 번호는 새 항목마다 커지지만, 빈 번호가 생기는 까닭은 삭제 말고도 있을 수 있습니다. 단서로만 씁니다.
6. **화면 이름으로 폴더를 찾습니다.** 최상위 폴더 이름은 화면 언어를 따릅니다. `roots` 아래 키로 찾습니다.

### 지우기와 조작

- **즐겨찾기를 지웁니다.** 다음 저장 때 파일에서 항목이 사라집니다. 지우기 전 모습은 `Bookmarks.bak`, [섀도 복사본](/03-techniques/analysis/volume-shadow-copy-analysis.md)에 남을 수 있습니다. 저장할 때마다 파일을 새로 쓰므로 옛 내용이 비할당 영역에 남을 수도 있습니다([레코드 카빙](/03-techniques/analysis/data-recovery/record-carving.md)).
- **방문 기록을 지웁니다.** 즐겨찾기는 남고 `date_last_used` 만 0 이 됩니다. 0 이 많고 방문 기록이 비어 있으면 [방문 기록 삭제](/02-artifacts/browsers/chrome-edge-whale/history.md) 흔적과 함께 봅니다.
- **브라우저를 닫고 파일을 직접 고칩니다.** 현재 Chromium 소스는 파일을 읽을 때 `checksum` 을 검사하지 않습니다. 다음 저장 때 새 값을 계산해 적을 뿐입니다. 그래서 수집한 파일의 `checksum` 이 내용과 안 맞으면, 브라우저가 마지막으로 저장한 뒤 다른 프로그램이 내용을 바꿨다는 뜻입니다. 반대로 값이 맞는다고 조작이 없었다는 증명은 아닙니다. 고친 사람이 값을 다시 계산할 수 있습니다.

## 직접 분석해 보기

### 원시 바이트로 한 번

아래는 Chromium 소스를 보고 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. `guid` 는 줄였습니다.

```json
{
   "checksum": "97789100d7cff469a653540c004789c8",
   "roots": {
      "bookmark_bar": {
         "children": [ {
            "date_added": "13386389025000000",
            "date_last_used": "13386924310000000",
            "guid": "...",
            "id": "4",
            "name": "사내 위키",
            "type": "url",
            "url": "https://wiki.example.com/"
         } ],
         "date_added": "13380595950000000",
         "date_last_used": "0",
         "date_modified": "13386389025000000",
         "guid": "...",
         "id": "1",
         "name": "Bookmarks bar",
         "type": "folder"
      },
      "other": { "children": [ ], "date_added": "13380595950000000", "date_last_used": "0",
                 "date_modified": "0", "guid": "...", "id": "2", "name": "Other bookmarks", "type": "folder" },
      "synced": { "children": [ ], "date_added": "13380595950000000", "date_last_used": "0",
                  "date_modified": "0", "guid": "...", "id": "3", "name": "Mobile bookmarks", "type": "folder" }
   },
   "version": 1
}
```

`date_added` 를 손으로 바꿔 봅니다.

1. `13386389025000000` 을 1,000,000 으로 나눕니다. 1601-01-01 부터 센 초 13,386,389,025 가 나옵니다.
2. 1601-01-01 과 1970-01-01 사이의 초 11,644,473,600 을 뺍니다. 유닉스 시각 1,741,915,425 가 나옵니다.
3. 날짜로 바꾸면 2025-03-14 01:23:45 UTC 입니다. 한국 시각(UTC+9)으로는 같은 날 10:23:45 입니다.
4. `date_last_used` 도 같은 방법으로 읽습니다. 2025-03-20 06:05:10 UTC 입니다.
5. 북마크바의 `date_modified` 는 하위 항목의 `date_added` 와 같습니다. URL 항목을 추가할 때 부모 폴더 시각이 따라 바뀐다는 규칙과 맞습니다.
6. 북마크바의 `date_last_used` 는 0 입니다. 폴더는 이 칸을 관리하지 않습니다.

비할당 영역이나 섀도 복사본에서 옛 파일을 찾을 때는 아래 바이트를 검색합니다. 모두 ASCII 글자입니다.

| 찾을 글자 | 바이트 |
|---|---|
| `"checksum"` | `22 63 68 65 63 6B 73 75 6D 22` |
| `"roots"` | `22 72 6F 6F 74 73 22` |
| `"date_added"` | `22 64 61 74 65 5F 61 64 64 65 64 22` |

`"checksum"` 뒤에 32자리 16진 글자가 오고 가까이에 `"roots"` 가 있으면 즐겨찾기 파일의 시작일 가능성이 큽니다. 찾은 조각은 JSON 으로 읽히는 데까지만 잘라 씁니다.

`checksum` 을 다시 계산해 파일이 바깥에서 바뀌었는지 봅니다. 아래 파이썬 코드는 위 계산 규칙을 옮긴 것입니다. 위 예시 파일에 돌리면 두 값이 같게 나옵니다.

```python
import hashlib, json, sys

d = json.load(open(sys.argv[1], encoding="utf-8"))
m = hashlib.md5()

def walk(n):
    m.update(n["id"].encode("utf-8"))
    m.update(n["name"].encode("utf-16-le"))   # 이름만 UTF-16LE
    if n["type"] == "url":
        m.update(b"url")
        m.update(n["url"].encode("utf-8"))
    else:
        m.update(b"folder")
        for c in n.get("children", []):
            walk(c)

for k in ("bookmark_bar", "other", "synced"):
    walk(d["roots"][k])
print("저장된 값:", d["checksum"])
print("계산한 값:", m.hexdigest())
```

두 값이 다르면 그 파일은 브라우저가 마지막으로 쓴 모습이 아닙니다. 사본을 만들 때 글자 인코딩이나 줄바꿈을 바꾸지 않았는지 먼저 확인합니다.

> 그림 자리: 예시 JSON 에서 `roots` 아래 세 폴더, 폴더와 URL 항목의 키, 시각 세 칸을 색으로 나눠 보여 주는 그림

### 공개 도구로 한 번

글자 파일이므로 JSON 을 읽는 어떤 도구로도 열 수 있습니다. Hindsight 같은 공개 도구는 크롬 계열 프로필을 통째로 읽으면서 즐겨찾기도 뽑아 줍니다. 도구를 쓸 때는 다음을 확인합니다.

- 시각을 UTC 로 보여 주는지, 현지 시각으로 바꿔 보여 주는지 확인합니다.
- `date_last_used` 를 보여 주는지 확인합니다.
- `Bookmarks.bak`, `AccountBookmarks`, 다른 프로필 폴더까지 읽는지 확인합니다.
- 항목 두세 개는 손으로 바꾼 시각과 맞춰 봅니다. 방법은 [도구 결과 교차 검증](/03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [방문·다운로드 기록 (History)](/02-artifacts/browsers/chrome-edge-whale/history.md) | 즐겨찾기 URL 을 실제로 방문했는지, 언제 방문했는지. 방문의 이동 유형에는 `AUTO_BOOKMARK`(2) 값이 있습니다 |
| [세션·탭 복원 (Sessions)](/02-artifacts/browsers/chrome-edge-whale/sessions.md) | `date_last_used` 무렵에 그 주소가 탭에 열려 있었는지 |
| [프로필 폴더와 계열 브라우저 구분](/01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md) | 프로필에 로그인한 계정. 동기화 항목일 가능성을 가립니다 |
| [$MFT](/02-artifacts/filesystem/mft.md) · [$UsnJrnl](/02-artifacts/filesystem/usnjrnl.md) | `Bookmarks` 를 다시 쓴 시각들. 저널이 남은 기간의 저장 이력 |
| [섀도 복사본 활용](/03-techniques/analysis/volume-shadow-copy-analysis.md) | 옛 `Bookmarks`. 지금 파일과 비교해 지운 항목을 찾습니다 |
| [레코드 카빙](/03-techniques/analysis/data-recovery/record-carving.md) | 비할당 영역에 남은 옛 JSON 조각 |
| [시간대 설정](/02-artifacts/system-account/time-zone.md) | UTC 를 현지 시각으로 바꿀 때 쓸 설정 |

여러 기록을 합쳐 읽는 순서는 [웹 사용 행위 재구성](/04-scenarios/activity/web-activity.md)에서 다룹니다.

## 실습

**직접 만든 Windows 10·11 가상 머신**에서 크롬이나 엣지로 해 봅니다.

1. 새 프로필에서 즐겨찾기 셋을 추가하고, 추가한 시각을 적어 둡니다. 브라우저를 닫고 `Bookmarks` 와 `Bookmarks.bak` 을 복사합니다. `.bak` 이 있습니까? 있다면 어느 시점의 모습입니까?
2. 브라우저를 다시 열고 즐겨찾기 하나를 열고, 다른 하나를 지운 뒤 닫습니다. 새 `Bookmarks` 와 `Bookmarks.bak` 은 각각 어느 시점의 모습입니까?
3. 1번에서 적은 시각과 `date_added` 를 비교해 보십시오. 몇 초 차이가 납니까?
4. "지난 1시간" 방문 기록을 지운 뒤 브라우저를 닫습니다. 어느 항목의 `date_last_used` 가 0 이 됐습니까?
5. 브라우저를 닫은 채 메모장으로 즐겨찾기 이름 하나를 고칩니다. 위 파이썬 코드로 `checksum` 이 맞는지 보십시오. 브라우저를 한 번 열고 즐겨찾기를 하나 연 뒤 닫고, 다시 확인해 보십시오.
6. $UsnJrnl 에서 프로필 폴더에 생겼다가 사라진 임시 파일과 `Bookmarks` 의 이름 바꾸기 기록을 찾아보십시오.

**공개 검체(NIST CFReDS 등)** 가운데 크롬 계열 브라우저가 든 이미지에서도 해 봅니다.

1. 프로필마다 즐겨찾기 파일이 몇 개 있습니까?
2. `Bookmarks` 와 `Bookmarks.bak` 의 항목 차이를 표로 만들어 보십시오.
3. `checksum` 이 맞습니까? 맞지 않다면 어떤 설명이 가능합니까?

## 참고 문헌

- Chromium 소스, `components/bookmarks/browser/bookmark_codec.cc` (JSON 키·시각 표현·checksum 계산) — https://github.com/chromium/chromium/blob/main/components/bookmarks/browser/bookmark_codec.cc
- Chromium 소스, `bookmark_storage.cc`·`bookmark_storage.h`·`bookmark_constants.cc`·`bookmark_features.cc` (저장 간격·`.bak` 생성·파일 이름·암호화 파일) — https://github.com/chromium/chromium/blob/main/components/bookmarks/browser/bookmark_storage.cc , https://github.com/chromium/chromium/blob/main/components/bookmarks/common/bookmark_constants.cc , https://github.com/chromium/chromium/blob/main/components/bookmarks/common/bookmark_features.cc
- Chromium 소스, `bookmark_model.cc`·`bookmark_node.h`·`sync/protocol/bookmark_specifics.proto` (시각이 바뀌는 때·동기화 칸) — https://github.com/chromium/chromium/blob/main/components/bookmarks/browser/bookmark_model.cc , https://github.com/chromium/chromium/blob/main/components/sync/protocol/bookmark_specifics.proto
- Chromium 문서, "User Data Directory" — https://chromium.googlesource.com/chromium/src/+/HEAD/docs/user_data_dir.md
- Microsoft Learn, "Microsoft Edge Browser Policy Documentation: UserDataDir" — https://learn.microsoft.com/en-us/deployedge/microsoft-edge-policies/userdatadir
- Google Chrome 고객센터, "How private browsing works in Chrome" — https://support.google.com/chrome/answer/95464
