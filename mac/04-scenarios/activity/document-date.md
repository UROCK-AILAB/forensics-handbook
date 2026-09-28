---
title: "이 문서의 날짜를 믿을 수 있나"
parent: "시나리오 · 행위 재구성"
nav_order: 2380
---

# 이 문서의 날짜를 믿을 수 있나 (Document Date)

문서에 적힌 날짜나 파일 목록에 보이는 날짜가 실제로 그 문서를 만들고 고친 때를 가리키는지 묻는 조사를 다룹니다. APFS 아이노드 시각, 확장 속성, 스포트라이트 메타데이터, 문서 안 메타데이터를 차례로 읽어 UTC 로 바꾸고, 파일 시스템 이벤트·문서 버전·스냅숏·첨부 기록에서 같은 파일이 나타난 시각을 찾습니다. 모든 값을 한 표에 올려 순서가 뒤집힌 곳을 표시하고, 복사·다운로드 같은 평범한 원인으로 설명되지 않으면 조작 흔적을 찾습니다.

## 조사 질문

문서에 적힌 날짜나 파일 목록에 보이는 날짜가 실제로 그 문서가 만들어지고 고쳐진 때를 가리키는지 묻습니다. 맥에서는 한 파일의 날짜가 파일 시스템, 확장 속성, 스포트라이트 메타데이터, 문서 안 메타데이터처럼 여러 층에 따로 기록되고 층마다 적는 주체와 시각 기준이 달라서, 이 페이지는 층별 날짜를 한 기준으로 맞춘 뒤 서로 모순되는 곳을 찾는 순서를 다룹니다.

## 먼저 확인할 것

먼저 확인하려는 날짜가 어느 층의 값인지 정합니다. 파인더나 도구에 보이는 "만든 날짜" 가 파일 시스템 값인지, 스포트라이트 값인지, 문서 안에 적힌 값인지에 따라 비교할 대상이 달라집니다.

다음으로 파일이 어디에 있는지와 볼륨 형식을 확인합니다. 아래 파일 시스템 시각 설명은 APFS 기준이고, 볼륨 구조는 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)에 있습니다. 시간대도 확인해 모든 값을 UTC 로 맞추며, 시간대는 [시간대와 시계 설정 (Time Zone·NTP)](../../02-artifacts/system-account/time-zone.md)에서 봅니다. 시스템 시계를 바꾼 흔적이 있으면 모든 층의 날짜가 함께 틀어질 수 있어서, [시스템 시각 바꾸기 (Time Change)](anti-forensics/time-change.md)도 먼저 확인합니다.

## 날짜가 기록되는 층

### 파일 시스템 (APFS)

APFS 는 아이노드 값 (j_inode_val_t) 안에 시각 네 개를 두고, 디렉터리 레코드 값 (j_drec_val_t) 안에 추가된 날짜를 둡니다 [1].

| 구조 | 오프셋 | 크기 | 값 [1] |
|---|---|---|---|
| 아이노드 값 | 16 | 8 | 생성 시각 |
| 아이노드 값 | 24 | 8 | 수정 시각 |
| 아이노드 값 | 32 | 8 | 아이노드 변경 시각 |
| 아이노드 값 | 40 | 8 | 접근 시각 |
| 디렉터리 레코드 값 | 8 | 8 | 추가된 날짜 (date added) |

모든 값은 1970-01-01 00:00:00 UTC 부터 센 나노초이고, 1970년 이전 날짜도 담을 수 있도록 부호 있는 정수입니다 [1]. mac_apt 는 APFS 시각을 늘 10^9 로 나눠 1970-01-01 에 더합니다 [3].

명세로 만든 예시로 값 하나를 읽어 보면, 생성 시각 필드의 정수가 1700000000000000000(16진수 `0x17979CFE362A0000`)이라면 10^9 로 나눈 1700000000 초가 되고, 이 값은 2023-11-14 22:13:20 UTC 입니다. 이 값은 설명을 위해 만든 것이고 실제 기기에서 나온 값이 아닙니다. 디스크에 놓이는 바이트 순서는 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)를 따릅니다.

### 확장 속성

날짜와 관련된 확장 속성으로 `com.apple.metadata:kMDItemDownloadedDate`, `com.apple.metadata:kMDItemWhereFroms`, `com.apple.quarantine`, `com.apple.lastuseddate#PS` 가 알려져 있습니다 [1]. 격리 속성 값의 두 번째 필드는 유닉스 시각을 16진수로 적은 값이고, 읽는 법은 [격리 속성과 다운로드 기록 (Quarantine)](../../02-artifacts/filesystem/quarantine/index.md)에 있습니다. `com.apple.lastuseddate#PS` 의 내부 형식은 단정할 수 없어서, 이 속성은 있는지만 보고서에 적습니다.

### 스포트라이트 메타데이터

날짜·출처와 관련된 스포트라이트 속성은 아래와 같고, 모두 OS X 10.4 에 도입됐습니다 [2].

| 속성 | 설명 [2] | 형 |
|---|---|---|
| `kMDItemContentCreationDate` | 내용이 만들어진 날짜·시각 | CFDate |
| `kMDItemContentModificationDate` | 내용이 수정된 날짜·시각 | CFDate |
| `kMDItemFSCreationDate` | "Date that the contents of the file were created." | CFDate |
| `kMDItemFSContentChangeDate` | 파일 내용이 마지막으로 바뀐 날짜 | CFDate |
| `kMDItemLastUsedDate` | 마지막으로 쓴 날짜. LaunchServices 가 파일을 열 때마다 자동으로 갱신 | CFDate |
| `kMDItemWhereFroms` | 얻은 곳(다운로드 URL, 메일로 받은 파일이면 보낸 사람 주소·제목 등) | CFString 배열 |

`kMDItemContentCreationDate` 는 내용 쪽 속성이고 `kMDItemFSCreationDate` 는 파일 시스템 쪽 속성이라서 서로 다른 값입니다 [2]. 복사하거나 내려받은 뒤 두 값이 다르면 "다르다" 는 사실만 적고 어느 쪽이 맞는지는 다른 층과 맞춰 판단합니다. `kMDItemDateAdded`, `kMDItemUseCount`, `kMDItemUsedDates` 는 Apple 문서에 정의가 없습니다 [2]. 스포트라이트 저장소를 읽는 법은 [스포트라이트 (Spotlight)](../../02-artifacts/file-folder-usage/spotlight/index.md)에 있습니다.

### 문서 안 메타데이터

Office·PDF·iWork 문서는 파일 안에도 만든 날짜·고친 날짜를 적고, 그 필드를 읽는 법은 [문서 메타데이터 (iWork·Office)](../../02-artifacts/embedded-metadata/iwork-office.md)에 있습니다. 문서 안 날짜는 문서를 저장한 앱이 적는 값이라서 파일 시스템 날짜와 따로 움직일 수 있습니다.

### 시각 기준 맞추기

| 층 | 기준 | 단위 |
|---|---|---|
| APFS 아이노드 시각, 추가된 날짜 | 1970-01-01 UTC [1] | 나노초 [1] |
| 격리 속성 두 번째 필드 | 1970-01-01 UTC | 초, 16진수 표기 |
| 스포트라이트·plist·대부분의 앱 데이터베이스 | 2001-01-01 UTC (맥 절대 시각) | 초 또는 나노초. mac_apt 는 값 크기로 가림 [3] |

기준점이 두 가지라서, 값을 옮겨 적기 전에 어느 기준인지부터 적어 둡니다. 두 기준의 차이와 변환은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | APFS 아이노드·디렉터리 레코드 | 생성·수정·변경·접근 시각과 추가된 날짜 [1] | [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md) |
| 2 | 확장 속성 | 내려받은 날짜, 출처, 격리 시각 [1] | [다운로드 출처 속성 (kMDItemWhereFroms)](../../02-artifacts/filesystem/where-froms.md) |
| 3 | 스포트라이트 메타데이터 | 내용 쪽·파일 시스템 쪽 날짜, 마지막으로 연 날짜 [2] | [스포트라이트 (Spotlight)](../../02-artifacts/file-folder-usage/spotlight/index.md) |
| 4 | 문서 안 메타데이터 | 앱이 적은 만든·고친 날짜 | [문서 메타데이터 (iWork·Office)](../../02-artifacts/embedded-metadata/iwork-office.md) |
| 5 | 파일 시스템 이벤트 | 파일이 생기고 바뀐 기록 | [파일 시스템 이벤트 (FSEvents)](../../02-artifacts/filesystem/fsevents/index.md) |
| 6 | 문서 버전 | 저장된 이전 버전 | [문서 버전 (DocumentRevisions-V100)](../../02-artifacts/file-folder-usage/document-revisions.md) |
| 7 | 스냅숏·타임 머신 백업 | 그 시점에 파일이 있었는지와 그때의 값 | [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md) |
| 8 | 메일·메시지 첨부 | 문서를 주고받은 시각 | [누구와 연락을 주고받았나 (Communication)](communication.md) |

1~4번은 파일에 붙어 다니는 날짜이고, 5~8번은 파일 밖에 따로 남는 기록입니다. 파일에 붙은 날짜를 바꾸는 방법이 있더라도 파일 밖 기록까지 함께 맞추기는 어려워서, 판단의 무게는 5~8번과의 대조에 둡니다.

## 분석 흐름

1. 확인할 날짜가 어느 층의 값인지 적고, 조사 대상 파일의 경로와 볼륨을 적습니다.
2. APFS 아이노드에서 시각 네 개를, 디렉터리 레코드에서 추가된 날짜를 읽어 UTC 로 바꿉니다. 도구 결과 하나는 헥스로 직접 읽어 변환이 맞는지 확인합니다.
3. 확장 속성 목록을 뽑아 내려받은 날짜·출처·격리 속성이 있는지 보고, 있으면 값을 UTC 로 바꿉니다.
4. 스포트라이트 메타데이터에서 내용 쪽 날짜와 파일 시스템 쪽 날짜, `kMDItemLastUsedDate` 를 읽습니다.
5. 문서 안 메타데이터를 읽습니다.
6. 파일 시스템 이벤트, 문서 버전, 스냅숏·백업, 첨부 기록에서 같은 파일이 나타난 시각을 찾습니다.
7. 모든 값을 한 표에 올리고, 순서가 뒤집힌 곳(만든 날짜가 받은 날짜보다 늦거나, 파일 밖 기록이 파일에 적힌 날짜보다 앞서는 곳)을 표시합니다. 표는 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)을 따릅니다.
8. 뒤집힌 곳마다 복사·다운로드·백업 복원 같은 평범한 원인으로 설명되는지 먼저 보고, 설명되지 않으면 [증거를 없애려 했나 (Anti-Forensics)](anti-forensics/index.md)의 방법으로 조작 흔적을 찾습니다.

> 그림 자리: 한 파일의 날짜를 층별(문서 안, 스포트라이트, 확장 속성, APFS, 파일 밖 기록)로 한 시간 축에 찍고, 순서가 뒤집힌 점을 표시한 도표

## 흔한 오판

날짜 하나만 보고 문서의 날짜를 정하는 경우가 가장 흔합니다. 층마다 적는 주체가 달라서 한 값만으로는 그 값이 원래 값인지, 복사하면서 새로 생긴 값인지, 누가 고친 값인지 가릴 수 없습니다.

`kMDItemContentCreationDate` 와 `kMDItemFSCreationDate` 를 같은 값으로 보는 것도 오판입니다. Apple 문서의 `kMDItemFSCreationDate` 설명에 "contents" 라는 말이 들어 있어 헷갈리기 쉽지만, 두 속성은 서로 다른 속성입니다 [2].

맥 절대 시각을 유닉스 시각으로 읽거나 그 반대로 읽으면 날짜가 수십 년 어긋납니다. APFS 시각은 1970년 기준 나노초 [1], 스포트라이트와 대부분의 앱 데이터베이스는 2001년 기준이라서, 값을 옮길 때 기준을 함께 적습니다.

파일에 붙은 날짜가 서로 맞는다고 해서 날짜를 믿을 수 있다고 결론짓지도 않습니다. 파일에 붙은 값끼리만 맞고 파일 밖 기록이 없으면 "파일에 적힌 값들은 서로 모순되지 않는다" 까지만 말합니다.

## 보고서 문장 예

- "문서 X 의 APFS 생성 시각은 YYYY-MM-DD HH:MM:SS UTC 이고, `com.apple.metadata:kMDItemDownloadedDate` 속성 값도 같은 날입니다. 문서 안에 적힌 만든 날짜는 이보다 N일 앞서며, 이 차이는 문서를 다른 곳에서 만든 뒤 내려받은 경우와 모순되지 않습니다."
- "문서 X 의 파일 시스템 수정 시각은 YYYY-MM-DD 로 적혀 있으나, 같은 파일의 문서 버전 기록과 스냅숏에는 그보다 늦은 내용 변경이 남아 있습니다. 이 결과로 볼 때 파일 시스템 수정 시각만으로는 마지막 수정 시점을 판단할 수 없습니다."

## 함께 볼 페이지

- [시스템 시각 바꾸기 (Time Change)](anti-forensics/time-change.md) — 시계 자체가 틀어졌을 때
- [이 파일은 어디서 왔나 (File Origin)](file-origin.md) — 받은 날짜와 출처를 따라갈 때
- [이 파일을 누가 언제 열었나 (File Access)](file-access.md) — 연 날짜를 따로 볼 때
- [사진 메타데이터 (EXIF·HEIC)](../../02-artifacts/embedded-metadata/exif-heic.md) — 사진 파일의 촬영 날짜

## 참고 문헌

1. libyal libfsapfs — Apple File System (APFS) 형식 문서 — https://raw.githubusercontent.com/libyal/libfsapfs/main/documentation/Apple%20File%20System%20(APFS).asciidoc
2. Apple Developer 문서 보관소 — MDItem Common Metadata Attribute Keys — https://developer.apple.com/library/archive/documentation/CoreServices/Reference/MetadataAttributesRef/Reference/CommonAttrs.html
3. mac_apt `plugins/helpers/common.py` (ReadMacAbsoluteTime·ReadAPFSTime·ReadUnixTime) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/helpers/common.py
