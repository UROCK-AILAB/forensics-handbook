---
title: "오피스 사용 흔적"
parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1330
has_children: true
has_toc: false
---

# 오피스 사용 흔적 (Microsoft Office)

## 한 줄 요약

Word·Excel·PowerPoint 같은 오피스 앱은 사용자가 다룬 문서의 경로와 시각을 사용자 레지스트리에 남깁니다. 사용자 폴더에는 폴더 내용 목록과 문서 사본을 남깁니다. 이 흔적을 묶어 읽으면 어느 사용자가 어떤 문서를 오피스로 다뤘는지, 지운 문서의 내용이 어디에 남았는지를 찾을 수 있습니다.

> 이 페이지와 하위 페이지에서 "(관찰)" 을 붙인 내용은 PC 한 대에서 직접 본 것입니다. 확인 범위: Windows 11 Home 10.0.26200, Microsoft 365 앱 16.0.20326.20158 (클릭 투 런). 다른 버전과 설정에서는 다를 수 있습니다.

## 왜 중요한가

오피스 흔적은 크게 두 곳에 남습니다. 하나는 사용자 레지스트리 (NTUSER.DAT) 의 `Software\Microsoft\Office\<버전>\...` 이고, 다른 하나는 사용자 폴더의 `AppData\Local\Microsoft\...` 와 `AppData\Roaming\Microsoft\...` 입니다. 두 곳 모두 사용자마다 따로 있어서 어느 사용자 프로필에서 문서를 다뤘는지 알려 줍니다.

레지스트리 쪽에는 문서 경로와 시각이 앱마다 따로 남고, 파일 쪽에는 폴더 내용 목록과 문서 사본이 남습니다. 사본에는 저장하지 않은 작업이나 지운 문서의 내용이 남아 있을 수 있습니다. 신뢰 문서 기록은 문서를 지운 뒤에도 남을 수 있으며, 로컬 경로만 남는 것은 아닙니다. 관찰한 PC 의 신뢰 문서 기록에는 https 주소도 있었습니다. (관찰)

해석할 때 자주 틀리는 점도 있습니다. 자세한 내용은 각 하위 페이지에 있습니다.

- 최근 파일 목록의 시각이 연 시각인지 닫은 시각인지는 공식 설명이 없습니다.
- 신뢰 문서 기록이 있다고 매크로를 켰다는 뜻은 아닙니다.
- 백스테이지 캐시의 파일 목록은 오피스로 연 파일 목록이 아닙니다.
- 읽던 위치의 시각은 로컬 시각이고, 최근 파일 목록의 시각은 UTC 입니다.
- 관찰한 최근 PC 의 오피스 문서 캐시는 공개 자료가 설명한 모양과 달랐습니다. (관찰)

## 한눈에 보기

> 그림 자리: NTUSER.DAT 의 `Software\Microsoft\Office\<버전>` 아래 앱별 키 (File MRU·Place MRU·User MRU·Reading Locations·Security\Trusted Documents) 와, 사용자 폴더의 `AppData\Local\Microsoft\Office\16.0` (BackstageInAppNavCache·OfficeFileCache) 과 `AppData\Roaming\Microsoft\<앱>` (AutoRecover) 을 한 장에 나란히 보여 주는 그림

### 위치와 알려 주는 것

| 흔적 | 위치 | 버전 (확인 범위) | 알려 주는 것 |
|---|---|---|---|
| [최근 파일 (File MRU·Place MRU)](file-mru-place-mru.md) | NTUSER.DAT `...\<버전>\<앱>\File MRU`·`Place MRU`, `...\<앱>\User MRU\<하위 키>\...` | 15.0 경로 예가 있습니다. 16.0 은 관찰입니다. | 앱에서 다룬 파일·폴더 경로와 FILETIME 시각 |
| [신뢰 문서 기록 (Trust Records)](trust-records.md) | NTUSER.DAT `...\<버전>\<앱>\Security\Trusted Documents\TrustRecords` | 14.0·15.0 Word 로 시험한 자료가 있습니다. 16.0 은 관찰입니다. | 경고 단추를 누른 문서 경로, 매크로를 켰는지 |
| [읽던 위치 (Reading Locations)](reading-locations.md) | NTUSER.DAT `...\<버전>\Word\Reading Locations\<하위 키>` | 15.0 경로 예가 있습니다. 16.0 은 관찰입니다. | Word 문서 경로와 분 단위 로컬 시각 |
| [백스테이지 캐시 (BackstageInAppNavCache)](backstageinappnavcache.md) | `AppData\Local\Microsoft\Office\16.0\BackstageInAppNavCache` | 공개 자료의 경로는 16.0 입니다. | [파일] 탭 화면에서 둘러본 폴더의 내용 목록 |
| [자동 복구·저장 안 한 문서 (AutoRecover·UnsavedFiles)](autorecover-unsavedfiles.md) | `AppData\Roaming\Microsoft\Word`, `AppData\Local\Microsoft\Office\UnsavedFiles` | Microsoft 365 기준 안내입니다. | 로컬에서 작업한 문서의 백업 사본 |
| [오피스 문서 캐시 (OfficeFileCache)](officefilecache.md) | `AppData\Local\Microsoft\Office\<버전>\OfficeFileCache` | 옛 버전 폴더도 남습니다. 16.0 은 모양이 달랐습니다 (관찰). | OneDrive·SharePoint 문서의 로컬 사본 |

레지스트리 값을 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

### 오피스 버전 키

경로의 `<버전>` 자리에는 오피스 버전 번호 키가 들어갑니다. 위치는 Windows 버전보다 이 오피스 버전에 따라 달라집니다. 공개 자료는 Windows 버전에 따른 차이를 적지 않았습니다.

| 버전 키 | 확인한 내용 | 근거 |
|---|---|---|
| 14.0 | az4n6 블로그가 이 버전 키의 Word (Office 2010) 로 신뢰 문서 기록을 시험했습니다. | az4n6 |
| 15.0 | az4n6 블로그가 이 버전 키의 Word 로도 시험했습니다. Registry Explorer 플러그인 주석에도 15.0 Word 경로 예가 있습니다. | az4n6, Registry Explorer |
| 16.0 | 관찰한 PC 의 Microsoft 365 앱은 16.0 키 하나만 썼습니다. | 관찰 |

- 16.0 이 Office 2016·2019·2021·2024·Microsoft 365 를 모두 뜻하는지는 확인하지 못했습니다.
- 버전 키가 여럿이면 어느 것을 지금 쓰는지 가려야 합니다. RegRipper 의 msoffice 플러그인은 숫자로 시작하는 하위 키 가운데 `User Settings` 하위 키가 있는 가장 높은 번호를 쓰는 버전으로 봅니다.
- 옛 버전 키와 옛 버전 폴더에도 기록이 남아 있을 수 있습니다. 가장 높은 번호만 보지 않습니다.

### 로그인 계정

- RegRipper 의 msoffice 플러그인은 `Common\Identity\Identities` 아래 `FriendlyName`·`EmailAddress` 값으로 오피스에 로그인한 계정을 뽑습니다.
- 최근 파일 목록은 계정마다 나뉘어 있을 수 있습니다. 관찰한 PC 의 `User MRU` 아래에는 계정별 하위 키가 두 개 있었습니다. (관찰) 자세한 내용은 [오피스 최근 파일](file-mru-place-mru.md) 에 있습니다.

### 관찰한 PC 의 구성 (관찰)

- `HKCU\Software\Microsoft\Office` 아래 버전 키는 16.0 하나였습니다.
- `16.0\Word` 아래에는 `File MRU`, `Place MRU`, `User MRU`, `Reading Locations`, `Security`, `Resiliency` 키가 있었습니다. `Resiliency` 키는 이 묶음에서 다루지 않습니다.
- `%LOCALAPPDATA%\Microsoft\Office\16.0\` 아래에는 `BackstageInAppNavCache`, `OfficeFileCache`, `MruServiceCache` 폴더가 있었습니다.
- kacos2000 자료는 `MruServiceCache` 폴더에 JSON 파일이 있고, Office 16 이후에만 있다고 소개합니다. 이 폴더를 다루는 하위 페이지는 아직 없습니다.

## 읽는 순서

1. [오피스 최근 파일 (File MRU·Place MRU)](file-mru-place-mru.md) — 앱마다 최근에 다룬 파일·폴더 경로와 FILETIME 시각을 읽습니다. 계정별 `User MRU` 와 시각의 뜻이 엇갈리는 문제를 다룹니다.
2. [신뢰 문서 기록 (Trust Records)](trust-records.md) — 경고 단추를 누른 문서 경로와 매크로를 켰는지를 읽습니다. 값 안의 시각이 매크로를 켠 때가 아니라는 점을 다룹니다.
3. [읽던 위치 (Reading Locations)](reading-locations.md) — Word 문서의 경로와 분 단위 로컬 시각을 읽습니다. 최근 파일 목록의 UTC 시각과 맞추는 법을 다룹니다.
4. [백스테이지 캐시 (BackstageInAppNavCache)](backstageinappnavcache.md) — [파일] 탭 화면에서 둘러본 폴더의 내용 목록을 JSON 에서 읽습니다. 연 파일 목록이 아니라는 점과 UTF-16LE 인코딩을 다룹니다.
5. [자동 복구·저장 안 한 문서 (AutoRecover·UnsavedFiles)](autorecover-unsavedfiles.md) — 로컬에서 작업한 문서의 백업 사본을 찾습니다. 공식 안내의 경로와 관찰한 실제 모양의 차이를 다룹니다.
6. [오피스 문서 캐시 (OfficeFileCache)](officefilecache.md) — OneDrive·SharePoint 문서의 로컬 캐시에서 문서를 되살립니다. 공개 자료의 형식과 최근 PC 에서 본 다른 형식을 다룹니다.

## 함께 볼 페이지

- [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) · [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) — 레지스트리 값과 FILETIME 을 직접 풉니다.
- [시간대 설정](../../system-account/time-zone.md) — 로컬 시각으로 남은 값을 UTC 로 옮길 때 봅니다.
- [오피스 경고](../../event-logs/oalerts.md) — 이벤트 로그 쪽의 오피스 기록입니다.
- [오피스 매크로](../../embedded-metadata/vba-macro.md) · [문서 메타데이터](../../embedded-metadata/document-metadata/index.md) — 문서 파일 안에 남은 매크로와 속성을 봅니다.
- [바로가기 파일](../lnk.md) · [점프리스트](../jump-lists.md) · [최근 문서](../recentdocs.md) — 오피스 밖에서 윈도가 남기는 문서 사용 기록입니다.
- [원드라이브](../../cloud-notes/onedrive/index.md) — 클라우드 문서의 동기화 기록을 봅니다.
- [이 파일을 누가 언제 열었나](../../../04-scenarios/activity/file-access.md) · [이 문서의 날짜를 믿을 수 있나](../../../04-scenarios/activity/document-date-verification.md) · [악성코드는 어디서 들어왔나](../../../04-scenarios/incident/initial-access.md) — 오피스 흔적을 다른 기록과 묶어 읽는 조사 흐름입니다.

## 참고 문헌

- RegRipper 3.0, msoffice.pl 플러그인 (H. Carvey, 버전 20200518). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/msoffice.pl
- az4n6 블로그, 트러스트 레코드·매크로 글 (2016-02). http://az4n6.blogspot.com/2016/02/more-on-trust-records-macros-and.html
- Eric Zimmerman, Registry Explorer 플러그인 OfficeMRU.cs (버전 0.5). https://raw.githubusercontent.com/EricZimmerman/RegistryPlugins/master/RegistryPlugin.OfficeMRU/OfficeMRU.cs
- Arsenal Recon, Backstage Parser README. https://raw.githubusercontent.com/ArsenalRecon/BackstageParser/master/README.md
- Arsenal Recon, "The Office Document Cache and Introducing ODC Recon – Part I" (2019-10). https://arsenalrecon.com/2019/10/the-office-document-cache-and-introducing-odc-recon-part-i/
- kacos2000, OtherStuff / OfficeFileCache Readme. https://raw.githubusercontent.com/kacos2000/OtherStuff/master/OfficeFileCache/Readme.md
- Microsoft Learn, "How to recover unsaved Word documents" (보관 문서). https://learn.microsoft.com/en-us/office/troubleshoot/word/recover-lost-unsaved-corrupted-document
