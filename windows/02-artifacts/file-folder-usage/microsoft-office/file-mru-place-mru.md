---
title: "오피스 최근 파일"
parent: "오피스 사용 흔적"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1340
---

# 오피스 최근 파일 (File MRU·Place MRU)

> 상위 페이지: [오피스 사용 흔적 (Microsoft Office)](index.md)

Word·Excel·PowerPoint 같은 오피스 앱은 최근에 쓴 파일과 폴더를 사용자 레지스트리에 목록으로 적어 둡니다. 목록의 값 하나에는 경로 하나와 FILETIME 시각 하나가 들어 있습니다. 이 시각이 연 시각인지 닫은 시각인지는 공식 설명이 없습니다.

> 16.0 의 값 모양은 Microsoft 365 앱 16.0.20326.20158 (클릭 투 런) 기준입니다.

## 무엇을 기록하나 · 왜 생기나

MRU 는 "가장 최근에 쓴 것 (Most Recently Used)" 을 줄인 말입니다. 오피스의 MRU 목록은 두 가지입니다.

| 목록 | 담는 것 |
|---|---|
| 최근 파일 목록 (File MRU) | 앱에서 다룬 파일의 경로 |
| 최근 위치 목록 (Place MRU) | 앱에서 다룬 폴더의 경로 |

목록은 앱마다 따로 있습니다.

목록은 사용자마다 NTUSER.DAT 에 있습니다. 그래서 어느 사용자 프로필에서 그 파일을 다뤘는지 알려 줍니다.

## 위치와 버전별 차이

값은 NTUSER.DAT (HKCU) 아래 두 곳에 있습니다. 하이브를 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

```
Software\Microsoft\Office\<버전>\<앱>\File MRU
Software\Microsoft\Office\<버전>\<앱>\Place MRU
Software\Microsoft\Office\<버전>\<앱>\User MRU\<하위 키>\File MRU
Software\Microsoft\Office\<버전>\<앱>\User MRU\<하위 키>\Place MRU
```

위치는 Windows 버전이 아니라 오피스 버전 키 (`<버전>`) 에 따라 달라집니다. 버전 키가 어느 오피스 제품을 뜻하는지는 [허브 페이지](index.md) 에서 다룹니다.

| 버전 키 | 내용 |
|---|---|
| 15.0 (Office 2013) | Word 도 User MRU 아래에 목록을 둡니다. |
| 16.0 | 파일 목록은 User MRU 아래에만 있습니다. User MRU 밖의 `Word\File MRU`·`Word\Place MRU` 에는 `FOLDERID_Desktop`, `FOLDERID_Documents` 값 두 개만 있고 `Item` 값은 없습니다. |

**User MRU 하위 키.** 하위 키 이름은 아래 두 모양입니다.

- `ADAL_<64자 16진수>`: 회사 계정 목록으로 보입니다.
- `LiveId_<64자 16진수>`: 개인 Microsoft 계정 목록으로 보입니다.

이 구분은 이름으로 짐작한 것이며 공개된 공식 설명은 없습니다. 계정마다 목록이 따로 있고, 같은 파일이 두 목록에 모두 나올 수 있습니다. 이때 두 목록의 시각은 서로 다를 수 있습니다.

오피스에 로그인한 계정 이름을 찾는 법은 [허브 페이지](index.md) 에 있습니다.

## 구조

**값 이름.** `Item 1`, `Item 2` … 처럼 번호가 붙습니다. RegRipper 는 이름이 `Item` 으로 시작하는 값만 읽습니다. Registry Explorer 는 `Item` 값을 풀고, `FOLDER` 로 시작하는 값은 시각 없이 따로 넣습니다.

**값 형식.** REG_SZ (문자열) 입니다.

**값 데이터.** 값 데이터는 아래 모양입니다.

```
[F00000000][T01D005C5B44B6300][O00000000]*C:\Users\eric\Desktop\aa\Out\Deduplicated.tsv
```

| 부분 | 예 | 뜻 |
|---|---|---|
| `[F…]` | `F00000000` | 뜻은 공개 자료에 없습니다. 값은 흔히 `F00000000` 입니다. |
| `[T…]` | `T01D005C5B44B6300` | 16자리 16진수로 적은 FILETIME 입니다. |
| `[O…]` | `O00000000` | 뜻은 공개 자료에 없습니다. 값은 흔히 `O00000000` 입니다. |
| `*` 뒤 | `C:\Users\…` | File MRU 는 파일 경로, Place MRU 는 폴더 경로입니다. |

Place MRU 값도 형식이 같습니다. Place MRU 경로는 `\` 로 끝납니다.

**`FOLDER` 로 시작하는 값.** `FOLDERID_Desktop` 같은 값에는 시각이 없고 폴더 경로만 있습니다. Registry Explorer 는 이 값을 `Item` 값과 따로 다룹니다. `FOLDERID_` 이름은 [윈도 식별자 형식](../../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서 다룹니다.

**순서.** `Item 1` 의 T 값이 가장 최근이고, 번호가 커질수록 T 값이 오래됩니다. 목록에 몇 개까지 남는지는 공개 자료에 없습니다.

## 증거로서 의미

**증명하는 것**

- 그 사용자 프로필의 그 앱 목록에 그 경로가 올라 있었습니다.
- User MRU 아래 값이면 어느 계정 하위 키의 목록인지 압니다.
- T 값은 그 항목에 지금 적혀 있는 시각 하나입니다.
- Place MRU 값은 그 앱의 최근 위치 목록에 그 폴더가 있었다는 기록입니다.

**증명하지 못하는 것**

- 파일을 처음 연 때. T 값이 파일 생성 시각보다 몇 주 늦을 수 있습니다.
- 파일을 고쳤는지.
- T 값이 연 시각인지 닫은 시각인지.
- 파일을 연 횟수. 이 형식에서 횟수를 뜻한다고 밝혀진 필드는 없습니다.
- 그 파일이 지금도 그 경로에 있는지, 내용이 그때와 같은지.
- 그때 PC 앞에 누가 있었는지. 이 문제는 [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.
- 목록에 없는 파일을 열지 않았다는 것. 목록 크기가 알려지지 않았고, 클라우드 문서의 https 주소는 File MRU 에 남지 않을 수 있습니다. 아래 "함정과 한계" 를 봅니다.

보고서 문장은 기록으로 확인되는 만큼만 씁니다.

- 쓰지 않을 문장: "사용자가 2024-03-15 02:19 UTC 에 report.docx 를 처음 열었다."
- 쓸 문장: "사용자 kim 의 NTUSER.DAT, `Software\Microsoft\Office\16.0\Word\User MRU\<하위 키>\File MRU` 의 `Item 1` 값에 `C:\Users\kim\Documents\report.docx` 경로가 있다. 이 값의 시각 필드는 2024-03-15 02:19:30 UTC 이다. 이 시각은 목록 항목에 적힌 시각이며, 처음 연 시각이나 수정 시각으로 확인한 값이 아니다." (예시 문장입니다. 같은 예를 [읽던 위치](reading-locations.md) 페이지에서도 씁니다.)

## 시각 해석

- T 값은 FILETIME 이고 UTC 입니다. RegRipper 는 이 값을 UTC 로 풀어 보여 줄 뿐 뜻을 붙이지 않습니다. 푸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
- Registry Explorer 플러그인 설명은 "최근 문서 이름과 마지막으로 열거나 닫은 시각" 을 뽑는다고 적었습니다. 그런데 코드는 T 값을 `firstOpen` 열에 넣습니다. 같은 자료 안에서도 뜻이 엇갈립니다.
- Registry Explorer 의 `lastOpen` 열은 T 값이 아닙니다. 이 열이 어디서 오는지는 [읽던 위치 (Reading Locations)](reading-locations.md) 에 있습니다.

T 값을 파일시스템 시각과 비교하면 아래와 같은 경우가 나옵니다.

| 견줄 것 | 나오는 모양 |
|---|---|
| 파일 생성 시각 | 생성 08-13, T 09-07 처럼 몇 주 늦은 경우가 있습니다. |
| 파일 마지막 수정 시각 | T 가 대개 수정 시각보다 수 초~수십 초 뒤입니다. |
| 수정 뒤 며칠 지난 T | 수정 08-23, T 08-27 인 경우가 있습니다. 고치지 않고 열기만 해도 T 가 바뀌는 것으로 보입니다. |
| 수정 시각보다 이른 T | 1분쯤 이른 경우도 있습니다. |

그래서 T 값을 "처음 연 시각" 으로 읽지 않습니다. "목록 항목에 지금 적힌 시각" 으로 두고, 다른 기록과 맞춰 봅니다.

User MRU 의 두 목록에 같은 파일이 있으면 시각이 서로 다를 수 있습니다. 목록마다 시각을 따로 적는 것으로 보입니다. 두 값을 모두 적어 둡니다.

## 함정과 한계

- **User MRU 밖만 보면 목록이 비어 보입니다.** 16.0 에서는 파일 목록이 User MRU 아래에만 있습니다. 쓰는 도구가 User MRU 를 읽는지 확인합니다.
- **계정 목록이 여럿입니다.** 같은 파일이 여러 하위 키에 나오면 시각도 따로 봅니다.
- **클라우드 문서가 빠질 수 있습니다.** 신뢰 문서 기록에 https 주소로 남은 문서가 File MRU 에는 없고 로컬 경로만 남을 수 있습니다. 클라우드 문서는 [신뢰 문서 기록 (Trust Records)](trust-records.md) 과 [백스테이지 캐시 (BackstageInAppNavCache)](backstageinappnavcache.md) 도 봅니다.
- **도구의 열 이름은 뜻이 아닙니다.** `firstOpen` 은 도구가 붙인 이름입니다. 보고서에는 열 이름 대신 "T 필드의 시각" 이라고 씁니다.
- **목록 크기가 알려지지 않았습니다.** 목록에 몇 개까지 남는지는 공개 자료에 없습니다.
- **`[F…]`·`[O…]` 필드의 뜻이 알려지지 않았습니다.** 값은 흔히 0 입니다. 0 이 아닌 값을 만나도 짐작으로 풀지 않습니다.
- **경로 끝의 `\`.** Place MRU 경로를 다른 기록과 문자열로 맞출 때 끝의 `\` 까지 맞춥니다.
- **시간대.** T 는 UTC 입니다. 로컬 시각으로 적힌 기록과 나란히 볼 때는 [시간대 설정](../../system-account/time-zone.md) 을 먼저 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 위 값 데이터 예를 REG_SZ 형식 (UTF-16LE) 으로 옮겨 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. 앞 0x60 바이트만 보입니다.

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  5B 00 46 00 30 00 30 00  30 00 30 00 30 00 30 00   [.F.0.0.0.0.0.0.
00000010  30 00 30 00 5D 00 5B 00  54 00 30 00 31 00 44 00   0.0.].[.T.0.1.D.
00000020  30 00 30 00 35 00 43 00  35 00 42 00 34 00 34 00   0.0.5.C.5.B.4.4.
00000030  42 00 36 00 33 00 30 00  30 00 5D 00 5B 00 4F 00   B.6.3.0.0.].[.O.
00000040  30 00 30 00 30 00 30 00  30 00 30 00 30 00 30 00   0.0.0.0.0.0.0.0.
00000050  5D 00 2A 00 43 00 3A 00  5C 00 55 00 73 00 65 00   ].*.C.:.\.U.s.e.
```

| 값 오프셋 | 바이트 | 뜻 |
|---|---|---|
| 0x00 | `5B 00 46 00` | `[F`. 글자 하나가 2바이트인 UTF-16LE 문자열입니다 ([문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)). |
| 0x16 | `5B 00 54 00` | `[T`. 시각 필드가 시작합니다. |
| 0x1A~0x39 | `30 00 31 00 … 30 00` | 16글자 `01D005C5B44B6300` |
| 0x3A | `5D 00` | `]`. 시각 필드가 끝납니다. |
| 0x52 | `2A 00` | `*`. 바로 뒤 0x54 부터 경로입니다. |

시각 필드는 이렇게 풉니다.

1. 16글자는 16진수를 글자로 적은 것입니다. 바이트 순서를 뒤집지 않고 그대로 수로 읽습니다. 0x01D005C5B44B6300 입니다.
2. 10진수로는 130,610,735,885,280,000 입니다. 1601-01-01 UTC 부터 센 100나노초 수입니다.
3. 풀면 2014-11-21 19:59:48.528 UTC 입니다.

### 공개 도구로 한 번

- RegRipper 의 msoffice 플러그인은 `Software\Microsoft\Office` 아래 File MRU·Place MRU 를 User MRU 안팎에서 읽습니다. T 값은 UTC 로 풀어 보여 줍니다.
- Registry Explorer 의 OfficeMRU 플러그인은 같은 값을 표로 보여 줍니다. T 값은 `firstOpen` 열에 넣습니다.

1. NTUSER.DAT 과 트랜잭션 로그 (.LOG1·.LOG2) 를 함께 뽑습니다.
2. 두 도구를 모두 돌립니다.
3. 앱마다, User MRU 하위 키마다 항목 수가 같은지 봅니다.
4. 항목 하나를 골라 위 헥스 절차로 T 값을 직접 풀고 도구 결과와 맞춰 봅니다.
5. 두 결과가 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [읽던 위치 (Reading Locations)](reading-locations.md) | 같은 Word 문서의 로컬 시각 (분 단위) 과 하위 키 시각 |
| [신뢰 문서 기록 (Trust Records)](trust-records.md) | 같은 문서의 신뢰 기록, File MRU 에 없는 https 문서 |
| [백스테이지 캐시 (BackstageInAppNavCache)](backstageinappnavcache.md) | 오피스 [파일] 탭에서 둘러본 폴더와 그 안의 파일 목록 |
| [자동 복구·저장 안 한 문서 (AutoRecover·UnsavedFiles)](autorecover-unsavedfiles.md) | 같은 문서 이름의 백업 파일 |
| [바로가기 파일](../lnk.md)·[점프리스트](../jump-lists.md) | 같은 파일을 연 다른 기록 |
| [최근 문서](../recentdocs.md) | 탐색기 쪽 최근 문서 목록 |
| [마스터 파일 테이블](../../filesystem/mft.md) | 파일의 생성·수정 시각과 T 값의 앞뒤 |
| [시간대 설정](../../system-account/time-zone.md) | 로컬 시각 기록과 나란히 볼 때의 시간대 |

시나리오로 이어서 보려면 [이 파일을 누가 언제 열었나](../../../04-scenarios/activity/file-access.md) 를 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 오피스를 쓴 사용자 프로필이 있는 이미지를 고릅니다. 오피스를 설치한 가상 머신을 직접 만들어도 됩니다.

1. NTUSER.DAT 의 `Software\Microsoft\Office` 아래 버전 키를 모두 적습니다.
2. 앱마다 File MRU·Place MRU 를 User MRU 안과 밖으로 나눠 봅니다. `Item` 값은 어느 쪽에 있나요?
3. User MRU 하위 키가 여럿이면 같은 파일이 두 목록에 있는지, 시각이 같은지 봅니다.
4. `Item 1` 파일을 골라 $MFT 의 생성·수정 시각과 T 값을 비교합니다. 위 시각 비교 표의 어느 줄과 같나요?
5. 가상 머신에서 문서 하나를 고치지 않고 열었다 닫습니다. T 값과 `Item` 번호가 어떻게 바뀌는지 적습니다.
6. 결과로 보고서 문장을 하나 씁니다. "처음 열었다" 가 아니라 기록으로 확인되는 만큼만 씁니다.

## 참고 문헌

- H. Carvey, RegRipper 3.0 msoffice.pl 플러그인 (버전 20200518). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/msoffice.pl
- E. Zimmerman, Registry Explorer 플러그인 OfficeMRU.cs (버전 0.5). https://raw.githubusercontent.com/EricZimmerman/RegistryPlugins/master/RegistryPlugin.OfficeMRU/OfficeMRU.cs
