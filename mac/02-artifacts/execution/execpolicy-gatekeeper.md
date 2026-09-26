---
title: "실행 정책 평가 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 740
---

# 실행 정책 평가 기록 (ExecPolicy·Gatekeeper)

`/var/db/SystemPolicyConfiguration/ExecPolicy` 데이터베이스의 `provenance_tracking` 표에는 격리를 통과한 앱의 코드 서명 해시(cdhash)·번들 식별자·팀 ID 가 남고, macOS 13 Ventura 부터 파일에 붙는 `com.apple.provenance` 확장 속성이 이 표의 행을 가리켜서, 디스크의 앱 하나를 실행 정책 기록과 이어 볼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Gatekeeper 는 앱을 실행하기 전에 서명과 공증을 검사하는 macOS 기능이고, 서명·공증의 구조는 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../01-foundations/protection/codesign-notarization-sip.md)에서 다룹니다. macOS 13 Ventura 는 이 검사의 범위를 넓혔고, 그 핵심 부분으로 새 확장 속성 `com.apple.provenance` 를 들여왔습니다 [1]. 이 속성은 앱이 격리를 통과할 때 붙고, 초기 Ventura 는 앱 안의 모든 폴더·파일에 붙였지만 13.2.1 에서는 `.app` 폴더 하나에만 붙었습니다 [1]. 이 속성을 쓰는 바이너리는 Quarantine.kext 와 `syspolicyd` 뿐이고, `syspolicyd` 안에서도 Gatekeeper 가 아니라 ExecManager 기능이 다룬다는 분석이 있습니다 [1].

ExecPolicy 데이터베이스 안의 `provenance_tracking` 표에는 cdhash(코드 서명 해시), 번들 식별자, 팀 ID 가 들어 있고, 표의 기본 키 열 이름은 `pk` 입니다 [1]. 파일에 붙은 `com.apple.provenance` 값의 마지막 8바이트는 리틀엔디언 정수이고, 이 정수가 `provenance_tracking.pk` 값입니다 [1]. 이 표 구조는 글 본문이 아니라 글에 달린 댓글에서 나온 설명이라서, 실제 데이터로 한 번 더 확인하고 씁니다.

## 위치와 버전별 차이

```
/var/db/SystemPolicyConfiguration/ExecPolicy
```

| macOS 버전 | 차이 |
|---|---|
| 10.15 Catalina ~ 12 Monterey | `com.apple.provenance` 가 아직 없음 [1]. 이 버전에 ExecPolicy 데이터베이스가 있는지는 실제 데이터로 확인 |
| 13 Ventura 이후 | 격리를 통과한 앱에 `com.apple.provenance` 가 붙고, 그 값이 `provenance_tracking.pk` 를 가리킴 [1]. 13.2.1 에서는 `.app` 폴더에만 붙음 [1] |

`provenance_tracking` 말고 다른 표와 각 표의 열은 버전마다 다를 수 있어 실제 데이터베이스에서 `.tables`·`.schema` 로 확인합니다. 같은 폴더의 `SystemPolicy` 데이터베이스는 `spctl` 정책을 담는 다른 파일이고, [악성 코드 흔적 분석 (Malware Triage)](../../03-techniques/analysis/malware-triage/index.md)에서 다룹니다. 라이브 맥에서 이 데이터베이스가 읽히지 않으면 디스크 이미지에서 파일을 꺼내 읽습니다.

## 구조

데이터베이스 형식은 [SQLite 데이터베이스 (SQLite)](../../01-foundations/data-formats/sqlite/index.md)에서 다룹니다. 공개된 구조는 아래가 전부입니다 [1].

| 대상 | 내용 |
|---|---|
| 표 `provenance_tracking` | cdhash, 번들 식별자, 팀 ID 가 들어 있음 |
| 열 `pk` | 이 표의 기본 키 |
| 확장 속성 `com.apple.provenance` 의 마지막 8바이트 | 리틀엔디언 정수. `provenance_tracking.pk` 값 |

cdhash·번들 식별자·팀 ID 를 담는 열의 실제 이름과 형은 `.schema provenance_tracking` 으로 확인합니다. 번들 식별자와 팀 ID 를 읽는 법은 [번들 ID와 팀 ID (Bundle ID·Team ID)](../../01-foundations/value-decoding/bundle-team-id.md)에서, 확장 속성 값 전체의 구성과 격리 속성과의 관계는 [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `provenance_tracking` 에 행이 있으면 이 맥의 실행 정책 기록에 그 cdhash·번들 식별자·팀 ID 가 올라 있다는 뜻입니다 [1]. 파일의 `com.apple.provenance` 값에서 읽은 정수와 같은 `pk` 행을 찾으면, 디스크의 그 파일과 그 기록이 이어져 있다고 쓸 수 있습니다 [1]. 앱 번들을 지웠더라도 표의 행이 남아 있으면, 한때 이 맥에서 그 번들 식별자·팀 ID 의 코드를 다룬 기록으로 읽을 수 있습니다. 행이 지워지는 조건은 공개 자료에 없습니다.

**증명하지 못하는 것.** 행이 생기는 조건(첫 실행인지, 검사만 했는지)이 알려져 있지 않아서, 행 하나를 "앱을 실행했다" 로 바로 옮기지 않습니다. 실행 여부는 [통합 로그의 프로세스 실행 기록 (Process Events)](unified-log-process.md)과 [어떤 앱을 언제 썼나 (App Usage)](../../04-scenarios/activity/app-usage.md)의 기록으로 따로 확인합니다. 누가 앱을 받았는지, 어디서 받았는지도 이 표에는 없어서 격리 속성과 다운로드 기록으로 채웁니다.

보고서에는 "이 앱 번들의 `com.apple.provenance` 값이 가리키는 `provenance_tracking` 행에 이 번들 식별자와 팀 ID 가 기록되어 있다" 처럼 파일과 행의 연결만 씁니다.

## 시각 해석

ExecPolicy 데이터베이스 안의 시각 열과 그 기준을 설명한 공개 자료는 없습니다. 실제 데이터베이스에서 시각처럼 보이는 열을 찾으면 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)의 기준들로 바꿔 보고, 같은 앱의 다른 기록(다운로드 시각, 첫 실행 로그)과 맞는 기준만 씁니다. 판단 시각을 이 데이터베이스만으로 정하지 말고, Gatekeeper 가 남긴 통합 로그 항목과 함께 봅니다. Gatekeeper 로그를 찾는 조건은 [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md)에서 다룹니다.

## 함정과 한계

- **알려진 구조가 적음.** 구조가 공개된 표는 `provenance_tracking` 하나이고, 그 설명도 글 댓글에서 나왔습니다 [1]. 도구가 다른 표를 해석해 보여 주면 그 해석의 근거를 따로 확인합니다.
- **속성이 지워질 수 있음.** 글 본문은 `com.apple.provenance` 를 SIP 가 보호해서 다른 볼륨에 복사하지 않으면 지울 수 없다고 하지만, 댓글에는 macOS 13.2.1 에서 `xattr -d` 로 쉽게 지워졌다는 보고가 있습니다 [1]. 파일에 속성이 없다는 사실만으로 Gatekeeper 를 거치지 않았다고 결론 내리지 않고, 표에 같은 번들 식별자·팀 ID 의 행이 있는지 거꾸로 찾아봅니다.
- **Ventura 이전 파일.** macOS 13 이전에 들어온 파일에는 이 속성이 없어서 [1], 파일과 표를 잇는 방법이 없습니다.
- **사본의 확장 속성.** 확장 속성은 파일 내용과 따로 저장되어서, 수집 방식에 따라 사본에서 빠질 수 있습니다. 확보 절차는 [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

명세로 만든 예시로, `com.apple.provenance` 값의 마지막 8바이트가 아래와 같다고 합니다. 앞쪽 바이트의 뜻은 알려져 있지 않아 `xx` 로 적었습니다.

```
xx ... xx | 2a 00 00 00 00 00 00 00
          | 마지막 8바이트 (리틀엔디언)
```

리틀엔디언이라서 낮은 자리 바이트가 앞에 오고, `2a 00 00 00 00 00 00 00` 은 0x2a, 곧 42 입니다 [1]. 이 값이 `provenance_tracking.pk` 라서 `pk = 42` 인 행을 찾습니다. 라이브 맥이나 마운트한 사본에서는 `xattr -px com.apple.provenance 앱경로` 로 값을 헥스로 볼 수 있습니다.

### SQL로 한 번

데이터베이스 사본을 `sqlite3` 같은 공개 도구로 엽니다. `pk` 말고는 열 이름이 알려져 있지 않아서, 먼저 구조를 보고 `SELECT *` 로 행을 봅니다.

```sql
.tables
.schema provenance_tracking

SELECT * FROM provenance_tracking WHERE pk = 42;
```

거꾸로 번들 식별자에서 파일을 찾을 때는 `.schema` 로 확인한 번들 식별자 열로 행을 고르고, 그 `pk` 를 리틀엔디언 8바이트로 바꿔 디스크의 파일들에 붙은 `com.apple.provenance` 값과 맞춰 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [격리 속성과 다운로드 기록 (Quarantine)](../filesystem/quarantine/index.md) | 같은 파일의 격리 속성과 다운로드 출처 |
| [다운로드 출처 속성 (kMDItemWhereFroms)](../filesystem/where-froms.md) | 파일을 받은 주소 |
| [앱 번들 정보 (Info.plist·Code Signature)](../embedded-metadata/app-bundle.md) | 번들의 서명 정보가 표의 번들 식별자·팀 ID 와 같은지 |
| [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md) | Gatekeeper 평가를 남긴 로그 항목과 시각 |
| [보안 도구 기록 (XProtect)](../logs/xprotect.md) | 같은 파일에 대한 악성 코드 검사 기록 |
| [악성 코드는 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md) | 앱이 들어온 경로를 묶어 읽는 순서 |

## 실습

공개 시험 자료(NIST CFReDS 등) 가운데 macOS 13 이후 이미지로 풀어 봅니다.

1. `/var/db/SystemPolicyConfiguration/` 폴더에 어떤 파일이 있는지 적어 보세요.
2. ExecPolicy 데이터베이스의 `.tables` 결과를 적고, `provenance_tracking` 의 열 이름을 확인해 보세요.
3. `/Applications` 의 앱 하나에서 `.app` 폴더에 붙은 `com.apple.provenance` 값을 읽어 마지막 8바이트를 정수로 바꾸고, 같은 `pk` 행을 찾아보세요.
4. 찾은 행의 팀 ID 가 그 앱의 서명 정보와 같은지 확인해 보세요.

## 참고 문헌

1. Howard Oakley, "Ventura has changed app quarantine with a new xattr" (The Eclectic Light Company, 2023-03-13) — https://eclecticlight.co/2023/03/13/ventura-has-changed-app-quarantine-with-a-new-xattr/
