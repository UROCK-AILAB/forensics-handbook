---
title: "읽던 위치"
parent: "오피스 사용 흔적"
grand_parent: "아티팩트 · 파일·폴더 사용 흔적"
nav_order: 1360
---

# 읽던 위치 (Reading Locations)

Word 는 `Reading Locations` 키 아래에 문서마다 하위 키를 하나씩 두고 문서 경로와 시각을 적습니다. 이 시각은 분 단위 로컬 시각이고 시간대 표시가 없습니다. 키 이름으로 보면 문서에서 읽던 자리를 적는 곳으로 보이지만, 공개된 공식 설명은 없습니다.

> 16.0 의 값 모양은 Microsoft 365 앱 16.0.20326.20158 (클릭 투 런) 기준입니다.

## 무엇을 기록하나 · 왜 생기나

하위 키 하나가 문서 하나를 가리킵니다. 하위 키마다 `File Path` (문서 경로) 와 `Datetime` 값이 있습니다. 16.0 에는 `Position` 값도 있습니다.

이 기록은 Word 에만 있고, Excel·PowerPoint 아래에는 이 키가 없습니다. Word 로 연 문서가 모두 여기 남지도 않습니다. [최근 파일 목록 (File MRU)](file-mru-place-mru.md) 에 있는 Word 문서 가운데 일부만 Reading Locations 에 남습니다.

## 위치와 버전별 차이

```
HKCU\Software\Microsoft\Office\<버전>\Word\Reading Locations\<하위 키>
```

사용자마다 NTUSER.DAT 에 있습니다. 하이브를 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다. 버전 키가 어느 오피스 제품을 뜻하는지는 [허브 페이지](index.md) 에서 다룹니다.

| 버전 키 | 내용 |
|---|---|
| 15.0 (Office 2013) | 이 키가 있습니다. |
| 16.0 | 키와 세 값 (`File Path`, `Datetime`, `Position`) 이 있습니다. |

15.0 보다 앞선 버전 키가 있으면 그 아래에도 `Word\Reading Locations` 가 있는지 확인합니다.

## 구조

**하위 키 이름.** `Document 0`, `Document 7` 처럼 `Document <번호>` 형식이며, 중간 번호가 빠질 수 있습니다. 예를 들어 `Document 0`, `Document 7` ~ `Document 14` 로 1~6 번이 빠진 9개가 남기도 합니다.

**값.** 세 값은 모두 REG_SZ (문자열) 입니다.

| 값 | 예 | 뜻 |
|---|---|---|
| `File Path` | (문서 경로) | 문서의 경로입니다. |
| `Datetime` | `2026-07-20T15:30` | 로컬 시각입니다. 초가 없고 분까지만 적습니다. |
| `Position` | `1143631699 4583`, `1164032630 0` | 공백으로 나뉜 수 두 개입니다. 뜻은 단정하지 않습니다. |

RegRipper 는 `File Path` 와 `Datetime` 만 보여 줍니다. `Position` 은 16.0 에서 보이는 값입니다.

## 증거로서 의미

**증명하는 것**

그 사용자 프로필의 Word 가 그 경로의 문서를 다룬 적이 있습니다. `Datetime` 은 그 문서에 적힌 분 단위 로컬 시각 하나이고, 하위 키의 마지막 쓰기 시각 (UTC) 은 그 키에 마지막으로 무언가를 쓴 때입니다. `Datetime` 을 UTC 로 옮기면 같은 파일의 File MRU T 값과 몇 분 안에서 맞을 수 있고, 그러면 두 기록이 같은 사용 시점을 가리킬 수 있습니다.

**증명하지 못하는 것**

- 문서의 어디까지 읽었는지.
- 문서를 고쳤는지.
- `Datetime` 이 연 때인지 닫은 때인지. 어떤 동작 때 이 값을 적는지 공개된 공식 설명이 없습니다.
- Word 로 연 문서가 모두 여기 남는다는 것. 여기 없다고 열지 않았다고 말할 수 없습니다.
- 초 단위의 앞뒤. 분까지만 적기 때문입니다.

보고서 문장은 기록으로 확인되는 만큼만 씁니다.

- 쓰지 않을 문장: "사용자가 2024-03-15 11:19 에 report.docx 를 읽었다."
- 쓸 문장: "사용자 kim 의 NTUSER.DAT, Word `Reading Locations` 의 한 하위 키에 File Path `C:\Users\kim\Documents\report.docx` 와 Datetime `2024-03-15T11:19` 이 있다. Datetime 에는 시간대 표시가 없다. 이 PC 의 시간대(UTC+9)로 옮기면 2024-03-15 02:19 UTC 이다." (예시 문장이며 숫자는 아래 헥스 예시와 같습니다.)

## 시각 해석

이 기록에서 읽을 수 있는 시각은 두 가지입니다.

| 시각 | 형식 | 근거와 뜻 |
|---|---|---|
| `Datetime` 값 | 문자열, 분 단위, 로컬 시각 | 분 단위 로컬 시스템 시각이라는 해석이 있습니다. 시간대가 UTC+9 인 PC 에서는 같은 파일의 File MRU T 값 (UTC) 에 9시간을 더한 값과 몇 분 안에서 맞습니다. 예: T 02:19:30Z, Datetime 11:19. |
| 하위 키의 마지막 쓰기 시각 | FILETIME, UTC | RegRipper 는 이 시각을 `Datetime` 과 함께 보여 줍니다. Registry Explorer 는 이 시각을 문서의 `lastOpen` 열에 넣습니다. |

**Registry Explorer 의 `lastOpen`.** Registry Explorer 는 File MRU 항목마다 `Reading Locations` 에서 `File Path` 가 같은 하위 키를 찾습니다. 찾으면 그 하위 키의 마지막 쓰기 시각을 그 문서의 `lastOpen` 열에 넣습니다. `lastOpen` 은 도구가 붙인 이름입니다. 키 시각은 그 키에 마지막으로 무언가를 쓴 때일 뿐입니다. 어떤 동작이 그 쓰기를 일으켰는지는 키만으로 알 수 없습니다.

**시간대.** `Datetime` 에는 `Z` 나 `+09:00` 같은 시간대 표시가 없습니다. 먼저 그 PC 의 [시간대 설정](../../system-account/time-zone.md) 을 확인합니다. UTC 로 옮긴 값을 [타임라인](../../../03-techniques/analysis/timeline/index.md) 에 넣습니다.

## 함정과 한계

- **UTC 타임라인에 그대로 넣으면 어긋납니다.** `Datetime` 은 로컬 시각입니다. 시간대가 UTC+9 이면 9시간이 어긋납니다.
- **분 단위입니다.** 초 단위 기록과 앞뒤를 가릴 때 쓰지 않습니다.
- **하위 키 번호가 빠집니다.** 빠진 번호를 지운 흔적으로 단정하지 않습니다.
- **Word 에만 있습니다.** Excel·PowerPoint 문서는 이 키로 볼 수 없습니다.
- **`Position` 을 짐작으로 풀지 않습니다.** "몇 페이지까지 읽었다" 같은 문장을 쓰지 않습니다.
- **도구의 열 이름은 뜻이 아닙니다.** `lastOpen` 을 "마지막으로 연 시각" 으로 옮겨 적지 않습니다. "하위 키의 마지막 쓰기 시각" 이라고 씁니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 위 값 형식으로 만든 예시입니다. 실제 데이터에서 나온 값이 아닙니다. 같은 문서를 가리키는 File MRU 값과 Reading Locations 하위 키가 있다고 합시다.

- File MRU 값 데이터: `[F00000000][T01DA767F3603E500][O00000000]*C:\Users\kim\Documents\report.docx` (형식은 [오피스 최근 파일](file-mru-place-mru.md) 에 있습니다)
- Reading Locations 하위 키의 `File Path`: `C:\Users\kim\Documents\report.docx`

`Datetime` 값 데이터를 헥스로 보면 아래와 같습니다. REG_SZ 라 UTF-16LE 입니다 ([문자 인코딩](../../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)).

```
오프셋    00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000  32 00 30 00 32 00 34 00  2D 00 30 00 33 00 2D 00   2.0.2.4.-.0.3.-.
00000010  31 00 35 00 54 00 31 00  31 00 3A 00 31 00 39 00   1.5.T.1.1.:.1.9.
```

1. 글자마다 00 을 건너뛰면 `2024-03-15T11:19` 입니다. 16글자, 32바이트입니다.
2. 초 자리가 없습니다. `Z` 나 `+09:00` 같은 시간대 표시도 없습니다.
3. File MRU 의 T 값 0x01DA767F3603E500 을 풀면 2024-03-15 02:19:30 UTC 입니다 ([시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md)).
4. T 값에 9시간을 더하면 11:19:30 입니다. `Datetime` 의 11:19 와 분까지 같습니다.
5. 그 PC 의 시간대가 UTC+9 라면 두 기록은 같은 때를 가리킨다고 볼 수 있습니다.

### 공개 도구로 한 번

- RegRipper 의 msoffice 플러그인은 하위 키마다 마지막 쓰기 시각 (UTC) 과 `Datetime` 을 함께 보여 줍니다.
- Registry Explorer 의 OfficeMRU 플러그인은 File MRU 결과의 `lastOpen` 열에 이 키의 시각을 넣습니다.

1. NTUSER.DAT 과 트랜잭션 로그 (.LOG1·.LOG2) 를 함께 뽑습니다.
2. RegRipper 결과에서 `Datetime` 과 하위 키 시각을 나란히 적습니다.
3. Registry Explorer 의 `lastOpen` 이 어느 하위 키의 시각인지 `File Path` 로 확인합니다.
4. `Position` 은 레지스트리 뷰어로 직접 봅니다. RegRipper 결과에는 이 값이 나오지 않습니다.
5. 도구 결과와 직접 읽은 값이 다르면 [도구 결과 교차 검증](../../../03-techniques/reporting/tool-validation.md) 을 따릅니다.

## 교차 검증

| 아티팩트 | 맞춰 볼 것 |
|---|---|
| [오피스 최근 파일 (File MRU·Place MRU)](file-mru-place-mru.md) | 같은 문서의 T 값 (UTC) |
| [시간대 설정](../../system-account/time-zone.md) | `Datetime` 을 UTC 로 옮길 때의 시간대 |
| [바로가기 파일](../lnk.md)·[점프리스트](../jump-lists.md) | 같은 문서를 연 다른 기록 |
| [문서 메타데이터](../../embedded-metadata/document-metadata/index.md) | 문서 안에 적힌 시각 |
| [마스터 파일 테이블](../../filesystem/mft.md) | 문서 파일의 수정 시각 |

시나리오로 이어서 보려면 [이 파일을 누가 언제 열었나](../../../04-scenarios/activity/file-access.md) 를 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 이미지 가운데 오피스를 쓴 사용자 프로필이 있는 이미지를 고릅니다. 오피스를 설치한 가상 머신을 직접 만들어도 됩니다.

1. Word 버전 키마다 `Reading Locations` 하위 키 이름을 모두 적습니다. 빠진 번호가 있나요?
2. 각 `File Path` 를 File MRU 목록과 맞춥니다. File MRU 에만 있는 Word 문서는 몇 개인가요?
3. 같은 문서의 `Datetime` 과 T 값을 견줘 시간 차이를 셈합니다. 시간대 설정과 맞나요?
4. 하위 키의 마지막 쓰기 시각과 `Datetime` 을 비교합니다.
5. 가상 머신에서 긴 문서를 열어 가운데까지 내려 본 뒤 닫습니다. `Position` 의 두 수가 어떻게 바뀌는지 적습니다.
6. 결과로 보고서 문장을 하나 씁니다. "읽었다" 가 아니라 기록으로 확인되는 만큼만 씁니다.

## 참고 문헌

- H. Carvey, RegRipper 3.0 msoffice.pl 플러그인 (버전 20200518). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/msoffice.pl
- E. Zimmerman, Registry Explorer 플러그인 OfficeMRU.cs (버전 0.5). https://raw.githubusercontent.com/EricZimmerman/RegistryPlugins/master/RegistryPlugin.OfficeMRU/OfficeMRU.cs
