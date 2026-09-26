---
title: "사용자 프로필 목록"
parent: "아티팩트 · 시스템·계정"
nav_order: 650
---

# 사용자 프로필 목록 (ProfileList)

SOFTWARE 하이브의 `ProfileList` 키 아래에는 SID 마다 하위 키가 하나씩 있고, 하위 키의 `ProfileImagePath` 값이 그 계정의 프로필 폴더를 가리킵니다. 다른 기록에 SID 만 나올 때, 이 키로 사람 이름과 프로필 폴더를 찾습니다.

## 무엇을 기록하나 · 왜 생기나

윈도의 여러 기록은 사용자를 이름이 아니라 보안 식별자 (Security Identifier, SID) 로 적습니다. SID 는 `S-1-5-21-...-1001` 같은 숫자 열이라 그대로는 누구인지 알 수 없습니다. ProfileList 는 SID 와 프로필 폴더를 잇는 대응표 구실을 합니다.

SID 하위 키마다 `ProfileImagePath` 값이 있고, 이 값은 `C:\Users\<이름>` 같은 프로필 폴더 경로입니다. 폴더 경로의 끝 이름으로 사용자 이름을 얻습니다.

## 위치와 버전별 차이

| 하이브 | 하이브 안의 키 경로 | 값 |
|---|---|---|
| SOFTWARE | `Microsoft\Windows NT\CurrentVersion\ProfileList\<SID>` | ProfileImagePath |

- 실행 중인 PC 에서는 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList` 로 보입니다.
- 하이브 파일 위치는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- 이 페이지는 SID 키 안의 값 가운데 `ProfileImagePath` 만 다룹니다.
- Windows 버전별 차이는 공개 자료에 없습니다.

## 구조

### SID 읽는 법

SID 는 `S-R-X-Y1-...-Yn` 형식입니다.

| 자리 | 뜻 |
|---|---|
| S | SID 라는 표시 |
| R | 버전 (revision) |
| X | 식별 기관 값. 로컬 계정과 도메인 계정은 5 (NT Authority) 입니다 |
| Y1 ~ Yn−1 | 하위 기관 값. 앞부분이 PC 마다, 도메인마다 다릅니다 |
| Yn (마지막 값) | 상대 식별자 (Relative Identifier, RID) |

로컬 계정과 도메인 계정의 SID 는 겉모양이 같습니다.

| 계정 | SID 형식 | 21 뒤의 숫자 세 개 |
|---|---|---|
| 로컬 계정 | `S-1-5-21-<숫자 세 개>-<RID>` | PC 마다 다릅니다 |
| 도메인 계정 | `S-1-5-21-<숫자 세 개>-<RID>` | 같은 도메인 안에서는 모두 같습니다 |

로컬 계정의 RID 는 그 PC 의 SAM 이 겹치지 않게 발급합니다. SID 의 바이트 구조는 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md)에서 다룹니다.

### 잘 알려진 SID

아래 SID 는 사람 계정이 아니라 시스템이 쓰는 계정입니다. ProfileList 에 이 SID 가 보이면 사람 계정으로 세지 않습니다.

| SID | 계정 |
|---|---|
| S-1-5-18 | System (LocalSystem) |
| S-1-5-19 | Local Service |
| S-1-5-20 | Network Service |
| S-1-5-32-544 | Administrators (기본 제공 그룹) |

### RID 로 계정 종류 구분하기

SID 의 마지막 값(RID)으로 계정 종류를 가릴 수 있는 경우가 있습니다.

| RID | 계정 |
|---|---|
| 500 | Administrator. 운영체제 설치 때 처음 만드는 계정입니다. 이 계정은 지울 수 없고 이름은 바꿀 수 있습니다 |
| 501 | Guest |
| 502 | KRBTGT. 도메인 컨트롤러에만 있습니다 |
| 512 | Domain Admins |
| 513 | Domain Users |
| 514 | Domain Guests |
| 515 | Domain Computers |
| 516 | Domain Controllers |

- 512~516 은 도메인 그룹입니다. 권한 기록처럼 SID 가 나오는 다른 기록을 풀 때 씁니다.
- RID 500 계정은 이름을 바꿔도 RID 가 그대로입니다. 이름이 Administrator 가 아니어도 RID 가 500 이면 기본 관리자 계정입니다.

### 로컬 계정과 도메인 계정 가려내기

겉모양만으로는 둘을 구분하지 못합니다. 다음 순서로 구분합니다.

1. [사용자 계정 (SAM)](sam.md)에서 로컬 계정의 RID 와 이름을 읽습니다.
2. ProfileList 에서 끝 값이 그 RID 이고 폴더 이름이 맞는 SID 를 찾습니다.
3. 그 SID 의 앞부분(21 뒤 숫자 세 개)이 이 PC 의 식별자입니다.
4. 앞부분이 다른 `S-1-5-21-...` SID 는 도메인 계정일 수 있습니다. 같은 앞부분이 다른 PC 의 기록에도 나오는지 봅니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 하이브를 마지막으로 쓴 때 이 SID 의 프로필이 등록돼 있었습니다 | 그 계정이 지금도 있는지. SAM 과 맞춰 봐야 합니다 |
| SID 와 프로필 폴더 경로의 짝 | 폴더 이름이 지금 계정 이름인지 |
| | 그 계정이 언제, 몇 번 로그인했는지 |
| | 그 폴더가 지금도 디스크에 있는지 |

폴더 이름은 프로필을 만들 때의 이름일 수 있으며, 지금 계정 이름은 SAM 의 V 값과 맞춰 봅니다. 이 키가 알려 주는 것은 짝이고, 사용 시각은 다른 기록에서 찾습니다.

### 보고서 문장

아래 값은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "ProfileList 에서 SID `S-1-5-21-1111111111-2222222222-3333333333-1001` 의 프로필 폴더는 `C:\Users\user_a` 입니다."
- 쓰면 안 되는 문장: "user_a 라는 사람이 이 PC 를 썼습니다."

## 시각 해석

- `ProfileImagePath` 는 시각이 아닙니다.
- SID 키에도 레지스트리 키마다 있는 마지막 기록 시각(LastWrite)이 있습니다([레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)). 무엇이 이 시각을 바꾸는지는 공개 자료에 없으므로 참고로만 봅니다.
- 이 키로 찾은 프로필 폴더의 NTUSER.DAT 생성 시각은 계정 생성 시각을 추정하는 데 씁니다. 방법과 한계는 [사용자 계정 (SAM)](sam.md)에서 다룹니다.

## 함정과 한계

1. **폴더 이름을 계정 이름으로 단정합니다.** 둘은 다를 수 있습니다. SAM 의 V 값이나 이벤트 로그의 계정 이름과 맞춰 봅니다.
2. **경로를 그대로 따라갑니다.** `ProfileImagePath` 는 그 PC 가 돌 때 기준의 경로입니다. 이미지를 붙인 분석 PC 에서는 드라이브 문자가 다를 수 있습니다.
3. **시스템 SID 를 사람 계정으로 분류합니다.** S-1-5-18·19·20 은 사람 계정이 아닙니다.
4. **로컬 계정과 도메인 계정을 섞습니다.** 둘 다 `S-1-5-21` 로 시작합니다. 위의 순서로 구분합니다.
5. **이름이 Administrator 인지만 봅니다.** 기본 관리자 계정은 이름을 바꿀 수 있습니다. RID 500 인지를 봅니다.
6. **키와 폴더 중 하나만 봅니다.** 키는 남았는데 폴더가 없거나, 폴더는 있는데 키가 없을 수 있습니다. 둘 다 확인합니다.

### 지우기와 조작

- **프로필을 지웁니다.** 키와 폴더가 함께 사라질 수 있습니다. 옛 키는 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 SOFTWARE 하이브나 하이브 안의 빈 공간에서 찾습니다. 지운 폴더의 흔적은 [마스터 파일 테이블](../filesystem/mft.md)에서 찾습니다.
- **`ProfileImagePath` 를 고칩니다.** 레지스트리 값이라 고칠 수 있습니다. 가리키는 폴더가 디스크에 실제로 있는지 확인합니다.

## 직접 분석해 보기

### 손으로 한 번

이 키의 값은 글자라 헥스보다 SID 를 손으로 풀어 보는 편이 쓸모 있습니다. 아래는 SID 규칙을 보고 만든 예시입니다. 실제 데이터에서 뽑은 값이 아닙니다.

| SID 키 | ProfileImagePath |
|---|---|
| `S-1-5-21-1111111111-2222222222-3333333333-500` | `C:\Users\Administrator` |
| `S-1-5-21-1111111111-2222222222-3333333333-1001` | `C:\Users\user_a` |
| `S-1-5-21-4444444444-5555555555-6666666666-1105` | `C:\Users\user_b` |

1. 첫 줄을 자리마다 나눕니다. `S` 는 SID 표시, `1` 은 버전, `5` 는 NT Authority 입니다.
2. `21-1111111111-2222222222-3333333333` 이 앞부분입니다. 마지막 `500` 이 RID 입니다.
3. RID 500 이라 기본 관리자 계정입니다.
4. 둘째 줄은 앞부분이 첫 줄과 같습니다. RID 는 1001 입니다.
5. SAM 에 RID 500 과 1001 계정이 있고 이름도 맞는다면, `1111111111-2222222222-3333333333` 이 이 PC 의 식별자입니다.
6. 셋째 줄은 앞부분이 다릅니다. SAM 에 이 계정이 없다면 도메인 계정일 수 있습니다.
7. 셋째 줄의 앞부분이 같은 조직의 다른 PC 기록에도 나오는지 봅니다. 나온다면 그 도메인의 식별자일 가능성이 높습니다.

> 그림 자리: SID 한 줄을 S·버전·식별 기관·앞부분·RID 로 나눠 색을 칠하고, SAM 의 RID 와 선으로 잇는 그림

### 공개 도구로 한 번

RegRipper 의 `profilelist` 플러그인이 SID 와 `ProfileImagePath` 의 짝을 보여 줍니다. 레지스트리 뷰어로 키를 직접 열어 봐도 됩니다. 도구를 쓸 때는 다음을 확인합니다.

- SID 키가 모두 나왔는지 확인합니다. 레지스트리 뷰어에서 하위 키 수와 맞춰 봅니다.
- 도구가 폴더 이름을 사용자 이름으로 바꿔 보여 준다면, 그 이름이 어디서 왔는지 확인합니다.
- 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md)을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [사용자 계정 (SAM)](sam.md) | 로컬 계정의 RID·이름. 이 PC 의 식별자 |
| [로그온·로그오프](../event-logs/logon-events/index.md) | 이벤트에 적힌 SID 와 계정 이름. 그 계정의 로그온 시각 |
| [계정 생성·변경](../event-logs/account-management-events.md) | 계정을 만들거나 지운 시각 |
| [마스터 파일 테이블](../filesystem/mft.md) | 프로필 폴더와 NTUSER.DAT 의 생성 시각. 지운 프로필 폴더의 흔적 |
| [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) | 바이트로 저장된 SID 를 글자로 바꾸는 법 |

SID 로 사용자를 이어 그 시각의 사용자를 밝히는 흐름은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md)에서 다룹니다. 여러 PC 에서 같은 도메인 계정을 추적하는 흐름은 [계정 탈취와 측면 이동](../../04-scenarios/incident/credential-theft-lateral-movement/index.md)에서 다룹니다.

## 실습

**NIST CFReDS 같은 공개 시험 이미지**에서 SOFTWARE·SAM 하이브를 꺼내 풀어 봅니다.

1. ProfileList 아래의 SID 키는 몇 개입니까? 그중 잘 알려진 SID 는 어느 것입니까?
2. 사람 계정으로 보이는 SID 마다 RID 와 프로필 폴더를 표로 정리해 보십시오.
3. SAM 의 로컬 계정과 맞춰 보십시오. 이 PC 의 식별자(21 뒤 숫자 세 개)는 무엇입니까?
4. SAM 에 없는 `S-1-5-21-...` SID 가 있습니까? 있다면 무엇일 수 있는지 적어 보십시오.
5. 프로필 폴더 이름과 SAM 의 계정 이름이 다른 경우가 있습니까?

**직접 만든 가상 머신**에서도 해 봅니다.

1. 로컬 계정을 만들고 한 번 로그인합니다.
2. ProfileList 에 새 SID 키가 생겼는지 봅니다.
3. 계정 이름을 바꾼 뒤, 프로필 폴더 이름과 SAM 의 이름이 어떻게 되는지 확인합니다.

## 참고 문헌

- keydet89, RegRipper3.0 `profilelist.pl` (`ProfileList\<SID>\ProfileImagePath`) — https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/profilelist.pl
- Microsoft Learn, "Security Identifiers" (SID 구조, RID 표, 잘 알려진 SID) — https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers
