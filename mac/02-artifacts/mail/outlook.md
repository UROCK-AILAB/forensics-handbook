---
title: "아웃룩"
parent: "아티팩트 · 메일"
nav_order: 1320
---

# 아웃룩 (Outlook for Mac)

맥용 아웃룩은 사용자 그룹 컨테이너 안의 프로필 폴더에 메타데이터 DB `Outlook.sqlite` 와 메시지별 `.olk15` 계열 파일을 함께 두고, 헤더 정보는 DB 에, 본문은 캐시 파일에 따로 나눠 저장합니다 [1].

## 무엇을 기록하나 · 왜 생기나

프로필 폴더의 `Data` 폴더에는 메일 목록과 헤더 정보를 담은 SQLite DB 가 있고, 그 옆에 본문 캐시·원본 MIME·떼어 낸 첨부가 메시지마다 파일 하나씩 따로 저장됩니다 [1]. DB 의 `Mail` 표에는 데이터 파일 경로와 헤더 정보가 들어 있고, 본문은 `.olk15Message` 파일에 들어 있어서 메일 한 통을 온전히 보려면 DB 행과 파일을 이어서 읽어야 합니다 [1].

원본 MIME 파일은 모든 메시지에 있지 않습니다. 도구 작성자의 실물 사례에서는 원본 MIME 파일(`.olk15MsgSource`)이 있는 메시지가 약 7% 였고, 본문 캐시는 열어 본 메일에 모두 있었습니다 [1]. 한 사례의 비율이라 다른 검체에 그대로 옮길 수는 없지만, 대부분의 메시지에서 보낸 사람·받는 사람 같은 헤더는 DB 에만 남는다고 보고 분석을 시작합니다.

이 구조는 공개 도구가 읽는 방식이고, Microsoft 가 공개한 문서는 없습니다 [1][2]. 칸 이름과 파일 구성은 검체에서 한 번 더 확인하고 씁니다.

## 위치와 버전별 차이

```
~/Library/Group Containers/UBF8T346G9.Office/Outlook/Outlook 15 Profiles/Main Profile/
```

위 경로가 프로필 폴더입니다 [1]. `UBF8T346G9` 는 Office 앱들이 함께 쓰는 그룹 컨테이너 식별자(팀 ID)로 알려져 있습니다. 이런 식별자를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에 있습니다.

`Main Profile` 은 기본 프로필 폴더 이름입니다 [1]. 프로필을 여러 개 만들면 폴더가 어떻게 생기는지는 공개 자료가 없어서, 검체에서는 `Outlook 15 Profiles` 아래의 폴더를 모두 목록으로 남기고 하나씩 봅니다.

| 아웃룩 버전 | 저장 방식 | 근거 |
|---|---|---|
| `Outlook 15 Profiles` 를 쓰는 버전 | 위 경로, `Outlook.sqlite` 와 `.olk15` 계열 파일 | 경로와 파일 구성은 공개 도구 README [1]. 어느 버전부터 이 이름을 썼는지는 공개 자료 없음 |
| Outlook 2011 for Mac | 다른 위치와 다른 형식을 썼다고 알려짐 | 공개 자료 없음 |
| 새 Outlook | 같은 DB·파일을 쓰는지, 로컬에 어디까지 캐시하는지 | 공개 자료 없음 |

macOS 버전에 따라 이 위치가 달라지는지는 공개 자료가 없어서, 검체에서는 macOS 버전과 함께 설치된 아웃룩 버전과 실제 폴더 구성을 먼저 적어 둡니다. 라이브 시스템에서 이 폴더를 읽는 데 필요한 권한도 공개 자료가 없습니다. 수집 순서는 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 구조

### Data 폴더

| 위치 (`Data/` 아래) | 확장자 | 내용 |
|---|---|---|
| `Outlook.sqlite` | — | 메타데이터 DB (SQLite) [1] |
| `Messages/` | `.olk15Message` | 본문 캐시 [1] |
| `Message Sources/` | `.olk15MsgSource` | 원본 MIME [1] |
| `Message Attachments/` | `.olk15MsgAttachment` | 떼어 내 저장한 첨부 [1] |

폴더 안의 파일 이름은 UUID 형태이고, 같은 메일이 본문 캐시와 원본 MIME 에 서로 다른 UUID 로 들어 있습니다 [1]. 파일 이름만으로 두 파일을 짝지을 수 없어서, 짝은 DB 의 연결 표로 찾습니다. UUID 표기는 [식별자 읽기 (UUID·UID·GUID)](../../01-foundations/value-decoding/uuid-uid.md)에서 다룹니다.

파일을 하위 폴더로 나눠 두는 규칙(폴더 이름과 깊이)은 공개 자료가 없습니다. 일정·연락처처럼 메일이 아닌 항목을 담는 폴더도 `Data` 안에 더 있을 수 있어서, `Data` 아래를 끝까지 훑어 폴더와 확장자 목록을 남깁니다.

### 파일 형식

`.olk15Message` 는 HTML·RTF·iCalendar 본문을 담는 캐시이고, 메일 헤더는 들어 있지 않습니다 [1]. 본문 인코딩은 UTF-16 과 UTF-8 이 섞여 있어서, 공개 도구 하나는 chardet 로 인코딩을 추정해 읽습니다 [1].

`.olk15MsgSource` 는 헤더·본문·MIME 구조를 모두 담은 원본이지만, 파일 앞에 이진 머리 부분이 붙어 있어서 이 부분을 떼어 내야 MIME 으로 읽힙니다 [1]. 머리 부분의 길이와 매직 바이트는 공개 자료가 없습니다. 이 파일에서 메일을 뽑을 때는 줄바꿈 문자를 정규화해야 합니다 [1].

`.olk15MsgAttachment` 는 MIME 인코딩된 첨부 파일입니다 [1]. 원래 파일로 보려면 MIME 인코딩을 풀어야 합니다.

### Outlook.sqlite 표

| 표 | 내용 [1] |
|---|---|
| `Mail` | 데이터 파일 경로(`PathToDataFile`)와 헤더 정보 |
| `Blocks` | 파일 경로 |
| `Mail_OwnedBlocks` | 메시지와 원본 파일을 잇는 연결 표. 첨부는 `BlockTag=1098151011` 로 구분 |

위 이름은 도구 README 의 표현이라 실제 칸 이름과 대소문자·표기가 다를 수 있습니다 [1]. 메일함 이름과 계정을 담는 표, 받은 시각·보낸 시각·읽음 표시 같은 칸의 실제 이름도 공개 자료가 없어서, 검체 DB 에서 `.schema` 로 표와 칸을 먼저 뽑고 이 표와 맞춰 봅니다. SQLite 파일을 여는 순서와 쓰기 앞 기록 (WAL) 처리는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 수집 시점에 이 프로필의 `Outlook.sqlite` 에 메시지 행이 있었고, 그 행에 어떤 헤더 정보와 `Message-ID` 가 적혀 있었는지를 보여 줍니다 [1]. `Message-ID` 는 서버나 받는 쪽 사본에 남은 같은 메일과 맞춰 볼 수 있는 값이고, 원본 MIME 파일이 남아 있는 메시지는 헤더 전체와 MIME 구조까지 볼 수 있습니다 [1]. 본문 캐시 파일이 있으면 그 메일 본문이 이 맥에 내려와 있었다는 흔적이 됩니다.

**증명하지 못하는 것.** 본문 캐시에는 헤더가 없어서 캐시 파일 하나만으로는 누가 누구에게 보낸 메일인지 말할 수 없습니다 [1]. 헤더를 다시 만들려면 `Outlook.sqlite` 가 온전해야 해서, DB 를 잃으면 본문 캐시만으로 보낸 사람·받는 사람을 되살리기 어렵습니다 [1]. 원본 MIME 파일은 일부 메시지에만 있어서, 특정 메일에 원본 MIME 이 없다는 사실만으로 조작이나 삭제를 말할 수는 없습니다 [1]. 사용자가 메일을 언제 읽었는지, 지웠는지를 나타내는 칸은 공개 자료가 없어 검체에서 확인해야 합니다.

보고서에는 "`Outlook.sqlite` 의 이 행에 이 `Message-ID` 와 이 발신 주소가 기록되어 있고, 이 행과 이어진 본문 캐시 파일이 있다" 처럼 행과 파일을 그대로 적고, 칸의 뜻은 어느 도구의 해석인지 함께 밝힙니다.

## 시각 해석

`Outlook.sqlite` 의 시각 칸이 유닉스 시각인지 맥 절대 시각 (Mac Absolute Time)인지는 공개 자료가 없어서 검체에서 정합니다. 원본 MIME 파일이 남은 메시지를 골라 DB 의 시각 값을 두 기준으로 모두 풀어 보고, MIME 의 `Date` 헤더와 가까운 쪽을 고릅니다. 두 기준의 차이와 변환식은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

값을 UTC 로 저장하는지, 보낸 쪽 시간대를 그대로 두는지도 공개 자료가 없습니다. `Date` 헤더에는 보낸 쪽의 시간대 표기가 붙어 있어서, 비교할 때는 두 값을 모두 UTC 로 바꾼 뒤에 맞춰 봅니다.

## 함정과 한계

본문 캐시와 원본 MIME 의 짝은 파일 이름이 아니라 DB 로 찾습니다. 같은 메일이 두 형식에 서로 다른 UUID 로 저장되어서, 이름이 같은 파일끼리 묶으면 짝이 틀립니다 [1].

본문 캐시는 UTF-16 과 UTF-8 이 섞여 있어서, 키워드를 한 가지 인코딩으로만 찾으면 일부 메일을 놓칩니다 [1]. 키워드 검색은 두 인코딩으로 모두 돌리고, 방법은 [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md)을 따릅니다.

같은 메일이 원본 MIME 과 본문 캐시에 모두 있을 때, 내보내기 도구는 원본 MIME 을 먼저 뽑고 같은 `Message-ID` 헤더를 가진 본문 캐시는 건너뛰어 중복을 지웁니다 [1]. 다른 도구 결과나 서버 사본과 건수를 맞출 때는 도구마다 중복을 어떤 기준으로 지웠는지 먼저 확인해야 건수 차이를 바로 읽을 수 있습니다.

공개 도구들은 모두 소규모 개인 저장소입니다 [2]. 내보내기 도구는 README 에서 스스로 "실험 단계" 라고 하고, 특정 Outlook 15 프로필 하나에 맞춰 만들어졌습니다 [1]. 도구가 보여 주는 칸 이름과 해석은 검체의 `.schema` 와 원본 MIME 몇 건으로 한 번 더 확인하고, 검증 절차는 [도구 검증 (Tool Validation)](../../03-techniques/reporting/tool-validation.md)을 따릅니다.

아웃룩은 받는 사람 자동 완성에 쓰는 최근 주소 파일도 남기고, 이 파일(Outlook 2015 for OS X Recent Address files)을 읽는 공개 도구가 두 개 있습니다 [2]. 파일 이름과 위치는 공개 자료가 없어 검체에서 찾아야 합니다.

DB 에서 지운 행이나 지운 캐시 파일을 되살리는 방법은 [삭제 데이터 복구 (Data Recovery)](../../03-techniques/analysis/data-recovery/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 확인하기

`Outlook.sqlite` 는 헥스로 앞부분을 열어 SQLite 파일인지 먼저 확인하고, 머리글 필드는 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에 따라 읽습니다.

`.olk15MsgSource` 는 앞의 이진 머리 부분 길이가 알려져 있지 않아서, 파일마다 헥스로 열어 MIME 헤더 글자가 시작되는 지점을 찾습니다. `From:`·`Message-ID:`·`Date:` 같은 헤더 이름이 처음 나오는 줄의 오프셋을 적어 두고, 그 앞 바이트를 잘라 낸 사본을 MIME 으로 엽니다. 여러 파일에서 그 오프셋이 같은지, 머리 부분 앞쪽 바이트가 같은지를 비교하면 이 검체의 머리 구조를 짐작할 수 있지만, 이 결과는 관찰로 적고 확인 범위(아웃룩 버전)를 붙입니다.

`.olk15Message` 는 영문 글자 사이마다 `00` 바이트가 끼어 있으면 UTF-16 이고, 그렇지 않으면 UTF-8 로 보고 엽니다.

연결 표의 첨부 구분 값 `1098151011` 은 16진수로 `0x41747463` 이고, 이 네 바이트를 ASCII 로 읽으면 `Attc` 입니다. 첨부를 뜻하는 네 글자 코드로 보이지만, 이 뜻을 밝힌 공개 명세는 없습니다.

```
10진수   1098151011
16진수   41 74 74 63
ASCII    A  t  t  c
```

### 공개 도구로 읽기

증거 사본의 `Outlook.sqlite` 를 `sqlite3` 명령 줄 도구로 읽기 전용으로 열고, 표와 칸을 먼저 뽑습니다. 아래 칸 이름은 README 표현이라 `.schema` 결과에 맞춰 고칩니다.

```sql
.tables
.schema Mail
.schema Mail_OwnedBlocks

SELECT * FROM Mail LIMIT 5;

SELECT * FROM Mail_OwnedBlocks WHERE BlockTag = 1098151011 LIMIT 5;
```

`Data` 폴더 전체를 메일 형식으로 내보내는 공개 도구로는 `thomasmaerz/olk15-export`(EML·Mbox·Maildir 로 내보내기)가 있고, 이 도구는 읽기 전용이라 프로필을 바꾸지 않습니다 [1][2]. 그 밖에 `MSAdministrator/osx-outlook-recovery`(olk15 메시지 복구), `kezzier/olk15DataExtraction`(Data 폴더에서 메일·첨부 추출)과 같은 기능을 상용 포렌식 도구의 확장 모듈로 만든 `kezzier/XT_olk15DataExtraction`, 최근 주소 파일을 읽는 `slategroup/olk15RecentAddresses`·`amliebsch/ps-olk15` 가 있습니다 [2]. 어느 도구든 증거 사본의 프로필 폴더를 통째로 복사한 것에 돌립니다.

## 교차 검증

`Message-ID` 로 같은 메일이 [애플 메일 (Apple Mail)](apple-mail/index.md)이나 [썬더버드 (Thunderbird)](thunderbird.md)에도 있는지 맞춰 보고, 받는 사람 주소는 [연락처 (Contacts)](../cloud-apps/contacts.md)와 맞춰 사람을 짚습니다. 첨부로 받은 파일이 디스크의 다른 곳에 저장되었는지는 [이 파일은 어디서 왔나 (File Origin)](../../04-scenarios/activity/file-origin.md) 흐름으로 확인합니다. 메일 시각은 다른 아티팩트와 함께 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)에 올리고, 연락 상대 분석은 [누구와 연락을 주고받았나 (Communication)](../../04-scenarios/activity/communication.md)로 묶습니다.

## 실습

아웃룩 계정을 연결한 시험용 맥이나 공개 검체로 아래 질문을 풀어 봅니다.

1. `Outlook 15 Profiles` 아래에 프로필 폴더가 몇 개 있고, 각 폴더의 `Data` 아래에는 어떤 하위 폴더와 확장자가 있는가?
2. `Messages/` 의 파일 수와 `Message Sources/` 의 파일 수를 세어 보고, 원본 MIME 이 있는 메시지의 비율을 구한다.
3. 원본 MIME 이 있는 메시지 하나를 골라 이진 머리 부분이 끝나는 오프셋을 찾고, 같은 메일의 본문 캐시 파일을 DB 연결 표로 찾아낸다.
4. 같은 메시지의 DB 시각 값을 유닉스 시각과 맥 절대 시각으로 모두 풀어 보고, `Date` 헤더와 맞는 기준을 고른다.

## 참고 문헌

1. thomasmaerz/olk15-export README — https://raw.githubusercontent.com/thomasmaerz/olk15-export/main/README.md
2. GitHub 저장소 검색 결과 "olk15" — https://api.github.com/search/repositories?q=olk15&sort=stars
