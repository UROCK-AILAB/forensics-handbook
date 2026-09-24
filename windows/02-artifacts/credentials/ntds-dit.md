---
title: "액티브 디렉터리 DB"
parent: "아티팩트 · 자격증명"
nav_order: 2910
---

# 액티브 디렉터리 DB (NTDS.dit)

## 한 줄 요약

`NTDS.dit` 는 도메인 컨트롤러 (DC) 에만 있는 액티브 디렉터리 데이터베이스입니다. 도메인의 사용자·그룹·컴퓨터 정보와 도메인 계정의 비밀번호 해시가 여기에 들어 있습니다. 저장 엔진은 ESE (Extensible Storage Engine) 이고, 해시를 풀려면 SYSTEM 레지스트리 하이브가 함께 필요합니다.

## 무엇을 기록하나 · 왜 생기나

도메인 컨트롤러는 도메인 전체의 계정 정보를 한 데이터베이스에 담습니다. 이 파일이 `NTDS.dit` 입니다. 로컬 계정 해시가 각 PC 의 SAM 하이브에 있다면, 도메인 계정 해시는 이 DB 에 있습니다.

- DC 에는 `Ntds.dit` 사본이 두 곳에 있습니다.
  - `%SystemRoot%\NTDS\Ntds.dit` — 지금 쓰고 있는 DB 입니다.
  - `%SystemRoot%\System32\Ntds.dit` — DC 를 새로 만들 때 쓰는 배포용 기본 사본입니다.
- 백업 사본에도 같은 자격 정보가 들어 있을 수 있습니다.
- DB 를 기본 경로가 아닌 곳에 둘 수도 있습니다. 실제 경로를 적어 두는 레지스트리 키와 값 이름은 이번 자료로 확인하지 못했습니다. 기본 경로에 없으면 볼륨 전체에서 `Ntds.dit` 를 찾습니다.

ESE 저장 형식 자체는 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. 이 페이지는 NTDS.dit 에 무엇이 어떻게 담기고, 무엇을 증명하며, 복사 흔적이 어떻게 남는지를 다룹니다.

## 위치와 버전별 차이

### 딸린 파일

`NTDS.dit` 는 혼자 쓰지 않습니다. ESE 엔진이 쓰는 로그·체크포인트 파일이 함께 있습니다.

| 파일 | 뜻 |
|---|---|
| `Ntds.dit` | 데이터베이스 본체. ESE (Esent.dll) 가 표·행·열을 관리합니다 |
| `Edb.log` | DB 에 쓰기 전 트랜잭션을 담는 로그. 고정 10MB |
| `Edb00001.log`, `Edb00002.log` … | `Edb.log` 가 차면 더 만드는 로그. 각 10MB |
| `Edb.chk` | 로그의 어디까지가 DB 에 반영됐는지 적는 체크포인트 |
| `Res1.log`, `Res2.log` | `Edb.log` 가 찼을 때를 위한 예비 공간. 각 10MB, 합 20MB |

- ESE 는 최대 16TB 를 다루고, 색인·다중값 속성·트랜잭션·온라인 백업을 지원합니다.
- 위 크기와 이름은 Windows Server 2003 문서 기준입니다. 이후 버전의 로그·예비 파일 이름은 이번 자료로 확인하지 못했습니다. 실물 폴더에서 파일 이름을 직접 확인합니다.

### 세 개의 내부 표

`NTDS.dit` 안에는 표가 세 개 있습니다.

| 표 | 담긴 것 |
|---|---|
| 데이터 표 (data table) | AD 의 모든 객체. 행 하나가 객체 하나 (예: 사용자), 열 하나가 스키마 속성 하나 (예: GivenName) |
| 링크 표 (link table) | 객체가 다른 객체를 가리키는 연결 속성 (예: 사용자의 MemberOf). 데이터 표보다 훨씬 작습니다 |
| SD 표 (security descriptor table) | 상속된 보안 설명자. Windows Server 2003 부터 객체마다 복제하지 않고 이 표에 한 번 두고 연결합니다 |

- ESE 안의 실제 표 이름·열 이름 규칙, 행끼리 부모·자식을 잇는 방식은 이번 자료로 확인하지 못했습니다. 도구로 연 표 목록에서 직접 확인합니다.

## 구조

### 열과 레코드

- 스키마의 속성마다 열이 하나씩 있습니다. 고정 길이 (정수·긴 정수) 와 가변 길이 (주로 유니코드 문자열) 가 있습니다.
- 가변 필드는 필요한 만큼만 공간을 씁니다. 유니코드 한 글자는 16비트입니다.
- 레코드는 DB 페이지를 넘을 수 없어 객체 하나가 8KB 로 제한됩니다 (Windows Server 2003 문서 기준. 이후 버전의 페이지 크기는 확인하지 못했습니다).
- 긴 가변 값은 다른 페이지에 두고 그 자리에는 9바이트 참조만 남깁니다.
- ESE 긴 값이 여러 조각으로 나뉘어 저장되는 점은 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. 경계 계산을 틀리면 오류 없이 값이 망가집니다.

### 지운 객체

- 지운 객체는 UI 에 안 보이는 특수 컨테이너 (Deleted Objects) 로 옮겨져 툼스톤 (tombstone) 으로 남습니다. 나중에 가비지 컬렉션으로 지워집니다.
- 이 컨테이너 내용은 LDAP 컨트롤 `1.2.840.113556.1.4.417` 로 검색하면 보입니다.
- 툼스톤 수명 기본값과 가비지 컬렉션 주기는 이번 자료로 확인하지 못했습니다.

### 비밀번호 해시와 SYSTEM 하이브

`NTDS.dit` 의 비밀번호 해시를 풀려면 SYSTEM 레지스트리 하이브가 함께 필요하지만, 해시가 어떤 키 계층으로 보호되는지는 이번 자료로 확인하지 못했습니다. 이 핸드북에서는 SAM·SECURITY 페이지와 같은 수준에서 "SYSTEM 하이브의 키가 있어야 푼다"까지만 쓰고, 해시를 실제로 꺼내는 절차는 다루지 않습니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 어떤 도메인 계정·그룹·컴퓨터 객체가 있(었)는지 | 각 계정을 실제로 언제 누가 썼는지 (이벤트 로그로 봅니다) |
| 객체 사이의 소속 관계 (링크 표) | 평문 비밀번호 (이 페이지가 확인한 것은 해시가 있다는 사실까지입니다) |
| 지운 객체가 툼스톤으로 남아 있는지 | 파일 하나만으로 해시를 풀 수 있다는 것 (SYSTEM 하이브가 필요합니다) |
| 계정에 비밀번호 해시가 있었다는 사실 | 해시가 언제 설정된 비밀번호의 것인지 (시각 속성을 따로 봅니다) |

`NTDS.dit` 하나만으로는 해시를 풀지 못하고, 같은 DC 의 SYSTEM 하이브가 함께 있어야 합니다. 백업본이나 배포용 사본에도 자격 정보가 있을 수 있으므로, 파일 하나만 보고 "여기에만 있다"고 하지 않습니다.

### 보고서 문장

- 쓸 수 있는 문장: "압수한 DC 이미지의 `%SystemRoot%\NTDS\Ntds.dit` 와 SYSTEM 하이브가 함께 확보됐고, 도메인 계정 N 개의 비밀번호 해시가 이 DB 안에 있습니다."
- 쓰면 안 되는 문장: "공격자가 이 DB 로 모든 도메인 계정의 비밀번호를 알아냈습니다." (해시가 있다는 것과 평문을 알아냈다는 것은 다릅니다.)

## 시각 해석

- `whenCreated`·`whenChanged`·`lastLogonTimestamp`·`pwdLastSet`·`badPasswordTime` 같은 시각 속성이 어느 열에 어떤 형식으로 들어 있는지는 이번 자료로 확인하지 못했습니다.
- `lastLogon` 은 DC 마다 따로이고 복제되지 않는다는 점, `lastLogonTimestamp` 는 복제되지만 지연이 있다는 점은 널리 알려졌으나 이번 자료로 확인하지 못했습니다. 그래서 이 값을 "마지막 로그온 시각"으로 단정하지 않고, 복제 지연을 함께 적습니다.
- `NTDS.dit` 는 DC 가 켜져 있는 동안 계속 쓰는 파일입니다. 그래서 파일시스템 시각은 사건 시각의 근거로 약하다고 봅니다 (자료로 확인한 것이 아니라 추론입니다).
- 시각 속성을 읽을 때는 일반화 시각 형식과 FILETIME 정수 형식을 구분합니다. 형식 계산은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.

## 함정과 한계

1. **사본에서만 작업합니다.** 이미지에서 꺼낸 ESE DB 는 비정상 종료 (dirty) 상태가 많고, 로그 사슬이 끊겨 복구가 안 될 수 있습니다. 원본을 열면 상태가 바뀝니다. (확인 범위: `SRUDB.dat`·`WebCacheV01.dat`·`Windows.edb` 관찰. `NTDS.dit` 자체의 관찰은 없습니다.) 자세한 내용은 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 를 봅니다.
2. **읽는 방식마다 행 수가 다릅니다.** 손상된 ESE DB 는 읽는 방식에 따라 행 수가 달라집니다. 두 방식 이상으로 비교합니다. (확인 범위 위와 같습니다.)
3. **SYSTEM 하이브를 빼먹습니다.** 해시를 풀려면 같은 DC 의 SYSTEM 하이브가 필요합니다. `NTDS.dit` 만 확보하면 해시를 풀지 못합니다.
4. **백업본을 놓칩니다.** 배포용 사본 (`System32\Ntds.dit`) 과 백업본에도 자격 정보가 있을 수 있습니다.
5. **긴 값 경계를 잘못 읽습니다.** 긴 가변 값은 다른 페이지에 조각으로 나뉩니다. 경계를 틀리면 오류 없이 값이 망가집니다. 두 도구로 교차 검증합니다.

### 지우기와 조작

- **객체를 지웁니다.** 지운 객체는 바로 사라지지 않고 툼스톤으로 남습니다. LDAP 컨트롤 `1.2.840.113556.1.4.417` 로 Deleted Objects 컨테이너를 봅니다. 가비지 컬렉션 뒤에는 사라질 수 있습니다.
- **DB 를 몰래 복사합니다.** 사용 중인 `NTDS.dit` 를 복사할 때 볼륨 섀도 복사 (VSS), `ntdsutil.exe`, `esentutl.exe` 같은 내장 기능이 쓰입니다. 복사 자체가 흔적을 남깁니다 (아래 탐지).

## 직접 분석해 보기

### 헥스로 한 번

- `NTDS.dit` 는 ESE 데이터베이스이므로 파일 첫 부분에 ESE 헤더가 옵니다. 헤더 구조와 헥스 읽기는 [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) 에서 다룹니다. 같은 사실을 두 페이지에 쓰지 않으려고 여기서는 링크만 합니다.

### 공개 도구로 한 번

- 오프라인 이미지에서는 ESE 를 읽는 공개 도구로 데이터 표를 엽니다. 표 이름과 열 이름부터 확인합니다.
- 해시를 대상으로 하는 분석은 SYSTEM 하이브를 함께 처리하는 공개 도구로 합니다. 이 핸드북은 해시를 꺼내는 절차 자체는 다루지 않습니다.
- 도구가 보여 준 시각이 UTC 인지, 어떤 시각 속성을 어떤 형식으로 풀었는지 확인합니다.
- 결과 한두 개는 다른 도구와 맞춰 봅니다. 방법은 [도구 결과 교차 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [ESE 데이터베이스](../../01-foundations/database-log-formats/extensible-storage-engine/index.md) | 저장 형식·긴 값 조각·비정상 종료 상태 |
| [레지스트리 속 비밀번호 정보 (SAM·SECURITY)](sam-security/index.md) | 로컬 계정 해시와 도메인 계정 해시의 자리 차이 |
| [로그온·로그오프](../event-logs/logon-events/index.md) | 도메인 계정을 실제로 언제 썼는지 |
| [볼륨 섀도 복사본 구조](../../01-foundations/disk-volume/volume-shadow-copy.md) | DB 를 섀도 복사로 빼낸 흔적 |
| [계정 탈취와 측면 이동](../../04-scenarios/incident/credential-theft-lateral-movement/index.md) | DB 를 노린 공격을 조사하는 흐름 |

### 탐지에서 보는 것

MITRE ATT&CK T1003.003 은 다음을 탐지 대상으로 꼽습니다.

- 섀도 복사 생성 시도.
- `%SystemRoot%\NTDS\ntds.dit` 에 대한 수상한 파일 접근.
- `ntdsutil.exe` 실행이나 볼륨 관리 API 사용.
- DC 에서의 프로세스 실행·파일 접근·VSS 작업.

- `ntdsutil` IFM (Install From Media) 결과 폴더 구조, DB 복사·마운트 때 응용 프로그램 로그에 남는 ESENT 이벤트, 섀도 복사 관련 이벤트는 이번 자료로 확인하지 못했습니다. 탐지 규칙에 넣으려면 실물 확인이 필요합니다.

## 실습

공개된 AD 실습 이미지나 실험용 도메인 컨트롤러에서 다음을 풀어 봅니다.

1. `%SystemRoot%\NTDS\` 폴더에 `Ntds.dit` 와 로그·체크포인트 파일이 모두 있습니까? `Edb.log` 크기가 10MB 입니까?
2. `System32\Ntds.dit` 배포용 사본도 있습니까?
3. 사본을 떠서 ESE 도구로 데이터 표를 엽니다. 표 이름과 열 이름이 이 페이지의 설명과 맞습니까?
4. Deleted Objects 컨테이너에 툼스톤으로 남은 객체가 있습니까?
5. DB 를 복사한 흔적 (VSS 작업, `ntdsutil.exe` 실행) 이 이벤트 로그에 남아 있습니까?

## 참고 문헌

- Microsoft, "How the Data Store Works" (Active Directory, Windows Server 2003, 보관 문서) — https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc772829(v=ws.10)
- MITRE ATT&CK, "T1003.003 OS Credential Dumping: NTDS" — https://attack.mitre.org/techniques/T1003/003/
