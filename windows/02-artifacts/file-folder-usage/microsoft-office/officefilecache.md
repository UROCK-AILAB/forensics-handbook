# 오피스 문서 캐시 (OfficeFileCache)

> 상위 페이지: [오피스 사용 흔적 (Microsoft Office)](index.md)

## 한 줄 요약

오피스는 OneDrive·SharePoint 에 저장할 문서와 그 수정 내용을 사용자 폴더의 `OfficeFileCache` 에 잠시 담아 둡니다. 공개 연구 자료는 이 캐시에서 사용자가 지워 다른 곳에는 없는 문서를 온전히 되살린 사례를 적었습니다. 관찰한 최근 Microsoft 365 PC 에서는 공개 자료가 설명한 파일 구성이 보이지 않았습니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 PC 한 대에서 직접 본 것입니다. 확인 범위: Windows 11 Home 10.0.26200, Microsoft 365 앱 16.0.20326.20158 (클릭 투 런). 다른 버전과 설정에서는 다를 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Arsenal Recon 의 2019년 10월 글은 이 캐시를 이렇게 설명합니다. 오피스 문서 캐시 (Office Document Cache) 는 중간 저장소이고, OneDrive·SharePoint 에 최종 저장할 문서와 그 수정 내용을 잠시 담습니다. 오피스 업로드 센터 (Upload Center) 가 캐시·클라우드·로컬 파일 사이의 동기화를 맡기 때문에 오프라인에서도 작업할 수 있고, 연결이 끊겨도 고친 내용은 나중에 올라갑니다. 문서는 보통 14일 넘게 캐시에 남으며, OneDrive·SharePoint 에 저장한 파일 가운데 오피스 문서가 아닌 파일도 들어가는 경우가 있습니다.

같은 글은 이 캐시가 중요한 까닭을 사례로 보여 줍니다. 사용자가 지워서 다른 곳에는 없는 문서를 FSD 파일에서 온전히 되살린 사례가 있고, FSD 파일 하나에 문서 수정 204건이 들어 있던 사례도 있습니다.

로컬 디스크나 네트워크 공유 폴더에서 연 문서의 백업은 [자동 복구·저장 안 한 문서 (AutoRecover·UnsavedFiles)](autorecover-unsavedfiles.md) 에서 다룹니다.

## 위치와 버전별 차이

```
\Users\<사용자>\AppData\Local\Microsoft\Office\<오피스 버전>\OfficeFileCache
```

- 사용자마다 따로 있습니다.
- 이전 오피스 버전의 `OfficeFileCache` 폴더가 남아 있을 수 있습니다. Arsenal 은 몇 년 전까지 거슬러 갈 수 있다고 적었습니다.
- 볼륨 섀도 복사본에도 남아 있을 수 있습니다.
- KAPE 의 OfficeDocumentCache 타깃은 `C:\Users\%user%\AppData\Local\Microsoft\Office\*\OfficeFileCache\` 를 하위 폴더까지 모읍니다. 버전 폴더 자리가 `*` 라서 옛 버전 폴더도 함께 모입니다.
- 버전 번호가 어느 오피스 제품을 뜻하는지는 [허브 페이지](index.md) 에서 다룹니다.

폴더 안의 파일 구성은 자료와 관찰이 서로 달랐습니다.

| 구분 | 근거 | 파일 구성 |
|---|---|---|
| 공개 자료가 설명한 형식 | Arsenal, kacos2000 | `CentralTable.accdb`, FSF 파일, FSD 파일 |
| 관찰한 형식 | 관찰 (Microsoft 365 앱 16.0.20326.20158) | `0\0\<32자 이름>\` 아래 `.R`·`.P`·`.C4`·`.UR` 파일 |

Arsenal 글은 시험한 오피스 버전을 적지 않았고, 관찰한 형식이 어느 버전부터 쓰였는지와 업로드 센터가 Microsoft 365 에서 없어졌는지는 확인하지 못했습니다.

kacos2000 자료에 따르면 Windows 의 CentralTable 은 Access (`.accdb`) DB 이고, Android·iOS·macOS 에서 가져온 OfficeFileCache 는 SQLite 로 된 `centraltable` 을 씁니다. SQLite 를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에 있습니다.

## 구조

### 공개 자료가 설명한 형식

kacos2000 자료는 세 가지 파일이 이렇게 이어진다고 적었습니다.

| 파일 | 하는 일 |
|---|---|
| `CentralTable.accdb` | FSF 파일 이름에 들어간 GUID 를 가리킵니다. |
| FSF 파일 | 해당 FSD 컨테이너의 GUID 를 담습니다. |
| FSD 파일 (File Store Data) | 문서를 담는 컨테이너입니다. Arsenal 글은 여기서 문서를 되살린 사례를 적었습니다. |

> 그림 자리: `CentralTable.accdb` 의 행이 FSF 파일 이름의 GUID 를 가리키고, FSF 파일이 다시 FSD 컨테이너의 GUID 를 가리키는 세 단계 연결

`CentralTable.accdb` 의 표 이름과 칸 이름은 확인하지 못했습니다. Arsenal 글도 표·칸 이름과 시각 칸의 형식을 적지 않았고, FSF·FSD 의 바이트 배치는 두 자료 모두 적지 않았습니다.

### 관찰한 형식 (관찰)

관찰한 PC 의 `%LOCALAPPDATA%\Microsoft\Office\16.0\OfficeFileCache` 에는 `CentralTable.accdb`, FSD, FSF 파일이 없었습니다. 대신 `0\0\<32자 대문자·숫자 이름>\` 폴더 아래에 파일이 있었습니다. `0\0` 아래 폴더는 18개였습니다.

| 확장자 | 개수 | 관찰한 내용 |
|---|---|---|
| `.R` | 9,535 | 가장 많았습니다. 내용은 확인하지 못했습니다. |
| `.P` | 205 | 파일 안에서 `indexEntries` 문자열이 보였습니다. 그 밖의 내용은 압축됐거나 이진이라 바로 읽히지 않았습니다. |
| `.C4` | 18 | 크기가 32,768바이트였습니다. |
| `.UR` | 17 | 작은 이진 머리 뒤에 JSON 이 있었습니다. |

- 파일 전체 크기는 약 601MB 였습니다.
- 파일 시각은 2026-08-19 부터 2026-09-22 사이였습니다 (로컬 시각).

`.UR` 파일의 JSON 에는 아래 칸이 있었습니다.

`SchemaVersion`, `PoliciesData`, `PolicyType`, `TenantId`, `PolicyVersionToken`, `PolicyMetadata`, `HasDlpPolicyTip`, `RetentionLabelName`, `IsContentReadOnly`, `IsRecord`, `IsLockedRecord`, `IsRegulatoryRecord`

칸 이름으로 보아 보존 레이블과 DLP 정책 정보로 보입니다. 공식 설명은 확인하지 못했습니다.

이 형식의 구조는 확인하지 못했습니다. 여기서 문서 본문을 되살릴 수 있는지도 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것**

FSD 에서 꺼낸 문서는 그 사용자 프로필의 오피스 문서 캐시에 들어 있던 내용이고, 공개 자료의 설명대로라면 OneDrive·SharePoint 에 저장할 문서였습니다. 사용자가 지운 문서의 내용이나 한 문서를 여러 번 고친 내용이 남아 있을 수 있고, 옛 버전 폴더와 섀도 복사본에는 지금보다 앞선 때의 캐시가 남아 있을 수 있습니다.

**증명하지 못하는 것**

- 캐시에 있는 파일마다 사용자가 오피스로 열었다는 것. 오피스 문서가 아닌 파일도 들어갑니다.
- 문서가 클라우드에 실제로 올라갔다는 것. 연결이 끊기면 캐시에 두었다가 나중에 올립니다.
- 누가 문서를 고쳤는지. 캐시는 사용자 프로필 단위로 남을 뿐입니다.
- 언제 고쳤는지. CentralTable 의 시각 칸 형식을 확인하지 못했습니다.
- 캐시에 없다고 그 문서를 쓰지 않았다는 것. 캐시에서 문서를 언제 지우는지 확인하지 못했습니다. 관찰한 형식에서는 문서를 되살릴 수 있는지도 모릅니다.

보고서 문장은 기록이 말하는 만큼만 씁니다.

- 쓰지 않을 문장: "사용자가 report.docx 를 고쳐 SharePoint 에 올렸다."
- 쓸 문장: "사용자 <사용자> 의 `AppData\Local\Microsoft\Office\<버전>\OfficeFileCache` 폴더의 FSD 파일에서 제목이 report 인 Word 문서를 꺼냈다. 이는 그 사용자 프로필의 오피스 문서 캐시에 이 문서의 내용이 있었다는 기록이다." (예시 문장입니다.)

## 시각 해석

| 시각 | 뜻 | 조심할 점 |
|---|---|---|
| `CentralTable.accdb` 안의 시각 | 확인하지 못했습니다. | 공개 자료가 칸 이름과 형식을 적지 않았습니다. 도구가 보여 주는 시각은 칸의 뜻을 확인한 뒤에만 씁니다. |
| 캐시 파일의 파일시스템 시각 | 캐시 파일을 만들고 쓴 때입니다. | 읽는 법은 [마스터 파일 테이블](../../filesystem/mft.md) 에 있습니다. |
| 꺼낸 문서 안의 속성 시각 | 문서 파일 안에 적힌 만든 날짜·고친 날짜입니다. | 캐시에 담긴 때가 아닙니다. [문서 메타데이터](../../embedded-metadata/document-metadata/index.md) 를 봅니다. |

**가장 오래된 캐시 파일 시각을 오피스를 처음 쓴 때로 옮기지 않습니다.** 관찰한 PC 의 캐시 파일은 2026-08-19 이후 것뿐이었습니다. (관찰) 캐시에서 파일을 언제 지우는지 확인하지 못했습니다. 공개 자료는 문서가 보통 14일 넘게 남는다고만 적었습니다.

## 함정과 한계

- **옛 형식을 전제한 도구는 아무것도 못 찾을 수 있습니다.** 관찰한 PC 에는 `CentralTable.accdb`·FSD·FSF 가 없었습니다. (관찰) 도구 결과가 비면 폴더 안 파일 목록부터 봅니다. "결과 없음" 을 "캐시 없음" 으로 적지 않습니다.
- **모든 버전 폴더를 모읍니다.** 이전 오피스 버전의 폴더에 몇 년 치 캐시가 남아 있을 수 있습니다.
- **섀도 복사본을 봅니다.** 지금은 지워진 캐시가 남아 있을 수 있습니다 ([섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)).
- **크기가 클 수 있습니다.** 관찰한 PC 에서는 약 601MB 였습니다. (관찰) 선별 수집 계획에 넣습니다.
- **오피스 문서만 있지 않습니다.** 클라우드에 저장한 다른 파일도 들어갑니다.
- **플랫폼마다 DB 형식이 다릅니다.** Windows 는 Access, Android·iOS·macOS 는 SQLite 입니다.
- **표·칸 이름을 모릅니다.** 도구가 보여 주는 칸 이름을 공식 뜻으로 옮기지 않습니다.
- **`.UR` 에는 조직 정보가 들어 있습니다.** `TenantId`·`RetentionLabelName` 같은 칸을 보고서에 옮길 때 기관의 정보 처리 기준을 따릅니다.

## 직접 분석해 보기

FSF·FSD 의 바이트 배치를 적은 자료를 확인하지 못해 헥스 예시를 싣지 않습니다. 아래 절차는 캐시를 모아 형식을 가리고, 공개 도구로 문서를 꺼내는 데까지입니다.

공개 도구의 예는 아래와 같습니다.

- kacos2000 의 OfficeFileCache.exe 는 CentralTable·FSD·FSF 를 읽는 파서입니다.
- Arsenal 의 ODC Recon 은 FSD 에서 OOXML 문서를 꺼냅니다.

1. 사용자마다 `AppData\Local\Microsoft\Office\` 아래 모든 버전 폴더의 `OfficeFileCache` 를 하위 폴더까지 모읍니다. 섀도 복사본의 같은 폴더도 모읍니다.
2. 폴더 안 파일 목록을 봅니다. `CentralTable.accdb`·FSF·FSD 가 있는지, 관찰한 것처럼 `0\0\` 아래 `.R`·`.P`·`.C4`·`.UR` 만 있는지 가립니다.
3. 공개 자료의 형식이면 도구로 CentralTable 과 FSF·FSD 를 풉니다.
4. FSD 에서 문서를 꺼냅니다. 꺼낸 문서는 격리된 환경에서 엽니다.
5. `CentralTable.accdb` 는 사본을 만들어 Access DB 를 읽는 다른 도구로도 엽니다. 표 목록과 행 수를 도구 결과와 맞춰 봅니다.
6. 관찰한 형식이면 `.UR` 파일의 JSON 부분에서 칸 값을 적습니다. 나머지 파일은 이름·크기·시각을 목록으로 남깁니다.
7. 도구마다 결과가 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [원드라이브](../../cloud-notes/onedrive/index.md) | 같은 문서가 동기화 폴더에 있는지, 어느 계정인지 |
| [오피스 최근 파일 (File MRU·Place MRU)](file-mru-place-mru.md) | 같은 문서를 오피스로 다룬 기록 |
| [신뢰 문서 기록 (Trust Records)](trust-records.md) | https 주소로 남은 클라우드 문서 경로 |
| [백스테이지 캐시 (BackstageInAppNavCache)](backstageinappnavcache.md) | 백스테이지에서 둘러본 클라우드 폴더의 내용 목록 |
| [자동 복구·저장 안 한 문서 (AutoRecover·UnsavedFiles)](autorecover-unsavedfiles.md) | 로컬에서 연 문서의 백업 사본 |
| [문서 메타데이터](../../embedded-metadata/document-metadata/index.md) | 꺼낸 문서 안의 작성자와 시각 |
| [마스터 파일 테이블](../../filesystem/mft.md)·[USN 변경 저널](../../filesystem/usnjrnl.md) | 캐시 파일이 생기고 지워진 기록 |

시나리오로 이어서 보려면 [지운 파일의 흔적 찾기](../../../04-scenarios/activity/deleted-file-traces.md) 와 [자료를 밖으로 빼돌렸나](../../../04-scenarios/exfiltration/data-exfiltration/index.md) 를 봅니다.

## 실습

NIST CFReDS 같은 공개 검체 가운데 오피스를 쓴 사용자 프로필이 있는 이미지를 고릅니다. 오피스와 OneDrive 를 설치한 가상 머신을 직접 만들어도 됩니다.

1. 사용자마다 `AppData\Local\Microsoft\Office\` 아래 버전 폴더를 모두 적습니다. 폴더마다 `OfficeFileCache` 가 공개 자료의 형식인지, 관찰한 형식인지 가립니다.
2. 공개 자료의 형식이면 `CentralTable.accdb` 에서 FSF, FSD 까지 문서 하나를 따라갑니다.
3. FSD 에서 꺼낸 문서 가운데 지금 디스크에 없는 것을 고릅니다.
4. 가상 머신에서 OneDrive 에 저장한 Word 문서를 여러 번 고칩니다. 캐시 폴더에서 어떤 파일이 새로 생기고 바뀌나요?
5. 네트워크를 끊고 문서를 고친 뒤 다시 연결합니다. 캐시 파일의 시각이 어떻게 바뀌나요?
6. 결과로 보고서 문장을 하나 씁니다. "올렸다" 가 아니라 기록이 말하는 만큼만 씁니다.

## 참고 문헌

- Arsenal Recon, "The Office Document Cache and Introducing ODC Recon – Part I" (2019-10). https://arsenalrecon.com/2019/10/the-office-document-cache-and-introducing-odc-recon-part-i/
- kacos2000, OtherStuff / OfficeFileCache Readme. https://raw.githubusercontent.com/kacos2000/OtherStuff/master/OfficeFileCache/Readme.md
- KapeFiles, OfficeDocumentCache.tkape. https://raw.githubusercontent.com/EricZimmerman/KapeFiles/master/Targets/Windows/OfficeDocumentCache.tkape
