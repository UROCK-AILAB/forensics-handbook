---
title: "백스테이지 캐시"
parent: "오피스 사용 흔적"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1370
---

# 백스테이지 캐시 (BackstageInAppNavCache)

> 상위 페이지: [오피스 사용 흔적 (Microsoft Office)](index.md)

## 한 줄 요약

오피스의 [파일] 탭 화면에서 둘러본 폴더의 내용 목록이 JSON 파일로 남습니다. 오피스로 연 파일만이 아니라 그 폴더에 있던 다른 파일의 이름과 수정 시각도 남습니다. 지금은 없는 로컬·원격 폴더의 경로가 남아 있을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

백스테이지 보기 (Backstage view) 는 오피스 프로그램을 시작하거나 [파일] 탭을 누르면 나오는 화면입니다. 새 파일 만들기, 열기, 인쇄, 저장, 옵션 같은 일을 이 화면에서 합니다.

캐시의 `Files` 목록에는 `.exe`, `.zip`, `.msi`, `.mp4`, `.png` 같은 오피스 문서가 아닌 파일도 들어 있습니다. 그래서 오피스로 연 파일 목록이 아니라 백스테이지에서 둘러본 폴더의 내용 목록으로 보입니다.

지금은 없는 로컬·원격 폴더의 경로도 이 캐시에 남을 수 있습니다.

## 위치와 버전별 차이

```
\Users\<사용자>\AppData\Local\Microsoft\Office\16.0\BackstageInAppNavCache
```

이 캐시는 Office 16 이후에 있고, 경로의 버전 폴더는 16.0 입니다. 다른 버전 번호 폴더에도 생기는지는 알려져 있지 않습니다.

Microsoft 365 앱 16.0.20326.20158 (클릭 투 런) 에서는 이 폴더 아래에 다음 하위 폴더가 생깁니다.

| 하위 폴더 이름 | 내용 |
|---|---|
| `MyComputer` | JSON 의 `ContainerUrl` 이 로컬 경로입니다. |
| `OD-<개인 Microsoft 계정>` | 이름 뒤에 개인 Microsoft 계정이 붙습니다. |
| `ODB-<회사 계정>` | 이름 뒤에 회사 계정이 붙습니다. |
| `SharePoint-<회사 계정>` | JSON 의 `ContainerUrl` 이 https 주소입니다. |

하위 폴더 안의 파일 이름은 `<64자 16진수>.json` 입니다. 사용자 프로필 하나에 모두 5개가 있는 예가 있습니다. 64자 이름을 만드는 방식은 알려져 있지 않습니다.

## 구조

아래 구조는 Microsoft 365 앱 16.0.20326.20158 기준입니다. 각 필드의 공식 설명은 알려져 있지 않습니다.

**인코딩.** JSON 은 UTF-16LE 로 저장됩니다. 첫 바이트는 `7B 00 22 00` 이고 BOM 이 없습니다. UTF-8 로 읽으면 깨집니다. 인코딩은 [문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

**맨 위 필드.**

| 필드 | 내용 |
|---|---|
| `LCID` | 언어 코드입니다. 예: 1042 (한국어) |
| `ContainerUrl` | 백스테이지에서 본 폴더 경로입니다. |
| `LastReadOn` | FILETIME 을 10진 정수로 적은 값입니다. 그 JSON 파일의 마지막 수정 시각과 같습니다. |
| `Folders` | 폴더 항목 배열입니다. |
| `Files` | 파일 항목 배열입니다. |
| `FetchedUrl`, `RetryAfter`, `ContainerIsDefaultDrive`, `ContainerResourceId`, `Metadata` | 뜻이 알려져 있지 않습니다. |

**`Files`·`Folders` 항목의 필드.** `Url`, `DisplayName`, `Author`, `ResourceId`, `RootResourceId`, `LastModified`, `SharingLevelDescription`, `OneNoteItem`, `RemoteItem`, `ThumbnailUrl`, `IsDefaultDrive`, `IsTeamChannel`, `IsPrivateChannel`, `IsSharedChannel` 이 있습니다.

`LastModified` 도 FILETIME 을 10진 정수로 적은 값입니다. 실제 파일의 수정 시각 (UTC) 과 1초 안에서 맞습니다 (`MyComputer` JSON 의 파일 39개 모두).

## 증거로서 의미

**증명하는 것**

- 캐시를 쓸 때 `ContainerUrl` 폴더에 `Files`·`Folders` 의 이름들이 있었습니다.
- 그때 그 파일들의 수정 시각을 알려 줍니다.
- 하위 폴더 이름으로 그 사용자의 오피스에 어떤 계정의 저장소가 보였는지 알 수 있습니다. (위 하위 폴더 이름 모양 기준)
- 지금은 없는 폴더나 파일의 경로가 남아 있을 수 있습니다.

**증명하지 못하는 것**

- `Files` 에 있는 파일을 열었다는 것. 폴더 내용 목록일 뿐입니다.
- 사용자가 그 폴더를 직접 골라 열었다는 것. 어떤 동작 때 캐시를 쓰는지 알려져 있지 않습니다.
- 캐시가 지금 상태라는 것. 캐시가 두 달 넘게 그대로인 경우가 있습니다 (아래 "시각 해석").
- 폴더를 둘러본 정확한 때. `LastReadOn` 은 목록을 받아 둔 시각으로 보일 뿐 공식 근거가 없습니다.

보고서 문장은 기록으로 확인되는 만큼만 씁니다.

- 쓰지 않을 문장: "사용자가 오피스로 setup.exe 를 열었다."
- 쓸 문장: "사용자 kim 의 `BackstageInAppNavCache\MyComputer` 아래 JSON 파일에 ContainerUrl `C:\Users\kim\Downloads` 와 Files 항목 `setup.exe` 가 있다. 이 JSON 의 LastReadOn 은 2026-07-07 00:26:16 UTC 이다. 이는 그 무렵 오피스 백스테이지 캐시에 이 폴더의 내용 목록이 있었다는 기록이다." (예시 문장입니다. 시각은 아래 풀이 예와 같습니다.)

## 시각 해석

| 시각 | 형식 | 뜻 |
|---|---|---|
| `LastReadOn` | FILETIME 을 10진 정수로 적음 (UTC) | JSON 파일의 마지막 수정 시각과 같습니다. 목록을 받아 둔 시각으로 보입니다. |
| `Files[].LastModified` | 같은 형식 (UTC) | 실제 파일의 수정 시각과 1초 안에서 맞습니다. |
| JSON 파일의 파일시스템 시각 | [$MFT](../../filesystem/mft.md) 의 시각 | 캐시 파일을 쓴 때입니다. |

**캐시는 오피스를 쓸 때마다 바뀌지 않습니다.** 9월까지 오피스를 계속 써서 File MRU 의 가장 최근 T 값이 2026-09-21 이어도, 캐시 파일 5개의 마지막 수정 시각은 모두 2026-07-07 에 머물 수 있습니다. 언제 캐시를 새로 쓰는지는 알려져 있지 않습니다.

캐시가 그대로인 동안 실제 파일이 바뀌면 `LastModified` 와 지금 파일의 시각이 달라질 수 있습니다. 두 시각이 다르면 캐시를 쓴 뒤 파일이 바뀐 것인지 먼저 따집니다.

FILETIME 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.

## 함정과 한계

- **UTF-8 검색으로는 못 찾습니다.** BOM 없는 UTF-16LE 입니다. 파일 이름이나 경로를 키워드로 찾을 때 두 인코딩으로 모두 찾습니다 ([파일 내용 검색](../../../03-techniques/analysis/content-search/index.md)).
- **연 파일 목록이 아닙니다.** `Files` 항목을 "오피스로 열었다" 로 옮기지 않습니다.
- **캐시가 오래됐을 수 있습니다.** `LastReadOn` 을 보고 캐시가 언제 적 목록인지 먼저 적습니다.
- **필드 목록은 달라질 수 있습니다.** 위 필드 목록은 Microsoft 365 앱 16.0.20326.20158 기준이라, 버전과 계정 종류에 따라 필드가 다를 수 있습니다.
- **폴더 이름에 계정이 들어갑니다.** 보고서에 옮길 때 개인정보 처리 기준을 따릅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 위 첫 바이트 모양과 필드 이름으로 만든 예시입니다. 실제 파일의 필드 순서와 값은 다를 수 있습니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  7B 00 22 00 4C 00 43 00  49 00 44 00 22 00 3A 00   {.".L.C.I.D.".:.
00000010  31 00 30 00 34 00 32 00  2C 00 22 00 43 00 6F 00   1.0.4.2.,.".C.o.
00000020  6E 00 74 00 61 00 69 00  6E 00 65 00 72 00 55 00   n.t.a.i.n.e.r.U.
00000030  72 00 6C 00 22 00 3A 00  22 00                     r.l.".:.".
```

1. 첫 두 바이트가 `7B 00` 입니다. `{` 뒤에 00 이 붙은 UTF-16LE 입니다.
2. 파일 맨 앞에 UTF-16LE BOM (`FF FE`) 이 없습니다.
3. 글자마다 00 을 건너뛰면 `{"LCID":1042,"ContainerUrl":"` 가 읽힙니다.

`LastReadOn` 값은 이렇게 풉니다. 아래 수는 실제 캐시 파일에서 가져온 값입니다.

1. `134278575766480000` 은 1601-01-01 UTC 부터 센 100나노초 수입니다.
2. 10,000,000 으로 나누면 13,427,857,576.648 초입니다.
3. 1601-01-01 부터 1970-01-01 까지의 11,644,473,600 초를 빼면 유닉스 시각 1,783,383,976.648 입니다.
4. 풀면 2026-07-07 00:26:16 UTC 입니다.

### 공개 도구로 한 번

- Arsenal BackstageParser 는 파이썬 도구입니다. 파일 하나나 폴더 전체를 읽고 CSV·TSV·PSV·JSON 으로 내보냅니다.
- kacos2000 의 Backstage.ps1·Backstagex64.exe 는 폴더 안 JSON 파일을 읽습니다.
- 도구 없이도 읽을 수 있습니다. 예를 들어 파이썬에서는 `json.load(open(경로, encoding="utf-16-le"))` 로 엽니다.

1. `BackstageInAppNavCache` 폴더를 하위 폴더까지 통째로 수집합니다.
2. 도구로 `ContainerUrl`, `LastReadOn`, `Files` 의 `DisplayName`·`LastModified` 를 뽑습니다.
3. JSON 파일 하나를 직접 열어 도구 결과와 항목 수, 시각을 맞춰 봅니다.
4. `LastReadOn` 을 그 JSON 파일의 파일시스템 수정 시각과 비교합니다.
5. 결과가 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [오피스 최근 파일 (File MRU·Place MRU)](file-mru-place-mru.md) | 오피스로 실제 연 파일, 최근 위치 폴더 |
| [셸백](../shellbags/index.md) | 탐색기로 다룬 같은 폴더 |
| [열기·저장 대화상자 기록](../comdlg32-opensavepidlmru-lastvisitedpidlmru-cids.md) | 다른 앱에서 같은 폴더를 연 기록 |
| [원드라이브](../../cloud-notes/onedrive/index.md) | `OD-`·`ODB-` 폴더 이름의 계정 |
| [마스터 파일 테이블](../../filesystem/mft.md)·[USN 변경 저널](../../filesystem/usnjrnl.md) | `Files` 항목의 지금 상태, 지우기·이름 바꾸기 기록 |

시나리오로 이어서 보려면 [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) 를 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 오피스를 쓴 사용자 프로필이 있는 이미지를 고릅니다. 오피스를 설치한 가상 머신을 직접 만들어도 됩니다.

1. 사용자마다 `BackstageInAppNavCache` 의 하위 폴더 이름을 적습니다. 어떤 계정이 보이나요?
2. JSON 파일 하나를 UTF-8 과 UTF-16LE 로 각각 열어 봅니다.
3. `MyComputer` 의 `ContainerUrl` 과 `Files` 목록을 뽑고, 지금 디스크에 없는 파일을 고릅니다.
4. `LastModified` 와 $MFT 의 수정 시각을 비교합니다.
5. `LastReadOn` 과 File MRU 의 가장 최근 T 값을 비교합니다. 캐시가 마지막 오피스 사용보다 오래됐나요?
6. 결과로 보고서 문장을 하나 씁니다. "열었다" 가 아니라 기록으로 확인되는 만큼만 씁니다.

## 참고 문헌

- Arsenal Recon, Backstage Parser README. https://raw.githubusercontent.com/ArsenalRecon/BackstageParser/master/README.md
- kacos2000, OtherStuff / OfficeFileCache Readme. https://raw.githubusercontent.com/kacos2000/OtherStuff/master/OfficeFileCache/Readme.md
