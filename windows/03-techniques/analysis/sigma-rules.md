---
title: "이벤트 로그 규칙 검색"
parent: "기법 · 분석"
nav_order: 3540
---

# 이벤트 로그 규칙 검색 (Sigma Rules)

> 위치: 분석 기법 > 분석

## 한 줄 요약

Sigma 는 로그에서 찾을 조건을 YAML 파일로 적는 규칙 형식입니다. 규칙은 그대로 실행되지 않고, 변환 도구가 검색 도구의 질의 언어로 바꿔야 돌릴 수 있습니다.
Windows 이벤트 로그를 규칙 여러 개로 한꺼번에 훑어, 사람이 먼저 볼 이벤트를 고를 때 씁니다.
이벤트 로그 파일의 구조는 [이벤트 로그 형식](../../01-foundations/database-log-formats/evtx-evt-etl/index.md) 에서 다룹니다.

## 언제 쓰나

- **이벤트가 너무 많아 하나씩 볼 수 없을 때** 씁니다. 규칙에 걸린 이벤트부터 봅니다.
- **알려진 행위 모양을 여러 로그에서 한꺼번에 찾을 때** 씁니다. 프로세스 생성, PowerShell, 서비스 설치 같은 로그를 규칙 하나하나로 훑습니다.
- **찾은 조건을 다른 분석가와 나눌 때** 씁니다. 같은 규칙 파일을 다른 검색 도구에 맞게 다시 변환할 수 있습니다.

## 규칙 파일의 형식

이 페이지는 Sigma 규칙 명세 (Sigma Rules Specification) v2.1.0 을 따릅니다.

### 파일 규칙

| 항목 | 규칙 |
|---|---|
| 형식 | YAML |
| 문자 인코딩 | UTF-8 |
| 줄바꿈 | LF |
| 들여쓰기 | 공백 4칸 |
| 키 | 소문자 |
| 문자열 값 | 작은따옴표로 감쌉니다 |

### 칸

| 구분 | 칸 |
|---|---|
| 반드시 있어야 함 | `title`, `logsource`, `detection`(그 안의 `condition`) |
| 있어도 되고 없어도 됨 | `id`, `name`, `related`, `taxonomy`, `status`, `description`, `license`, `references`, `author`, `date`, `modified`, `fields`, `falsepositives`, `level`, `tags`, `scope` |

`status` 와 `level` 에 쓸 수 있는 값은 정해져 있습니다.

| 칸 | 값 |
|---|---|
| `status` | `stable`, `test`, `experimental`, `deprecated`, `unsupported` |
| `level` | `informational`, `low`, `medium`, `high`, `critical` |

- 두 칸 모두 규칙을 쓴 사람이 붙인 값입니다.
- `falsepositives` 칸에는 규칙이 잘못 걸릴 수 있는 경우를 적습니다. 결과를 볼 때 함께 읽습니다.

### logsource: 어느 로그를 볼지

- `logsource` 의 하위 칸은 `category`, `product`, `service`, `definition` 입니다.
- 값은 소문자로 쓰고, 공백은 밑줄로 바꿉니다.

Windows 쪽 예입니다.

| 하위 칸 | 예 |
|---|---|
| `product` | `windows`. 이 값은 Security·System·Application 같은 로그를 모두 포함합니다 |
| `category` | `process_creation` |

- `service` 에 쓸 Windows 값의 목록은 이 명세 본문에 없습니다. 쓰는 규칙 모음과 변환 설정에서 확인합니다.

`category` 값이 실제로 어느 채널의 어느 이벤트로 이어지는지는 규칙 파일이 아니라 변환 도구의 설정, 곧 매핑 (Mapping) 이 정하므로, 같은 규칙도 매핑이 다르면 다른 로그를 검색합니다.

- 프로세스 생성을 기록하는 로그는 [프로세스 생성](../../02-artifacts/event-logs/4688.md) 과 [Sysmon 로그](../../02-artifacts/event-logs/sysmon/index.md) 에서 다룹니다. 쓰는 매핑이 이 가운데 어느 것을 가리키는지 확인합니다.

### detection: 무엇을 찾을지

- `detection` 안에 검색 식별자를 두고, 그 아래에 조건을 적습니다. 식별자 이름의 예는 `selection`, `filter` 입니다.
- 키와 값을 여러 개 적은 맵 (Map) 은 모두 맞아야 합니다(AND).
- 값을 여러 개 적은 목록 (List) 은 하나만 맞아도 됩니다(OR).
- `condition` 에는 식별자를 `and`, `or`, `not`, 괄호로 묶어 적습니다.
- 식별자를 한꺼번에 가리킬 때는 `1 of selection*`, `all of selection*`, `1 of them`, `all of them` 을 씁니다.

값에는 수식어를 파이프(`|`)로 붙입니다.
수식어 목록은 명세의 부록 "Sigma Modifiers" 에 있습니다. 아래 표는 그 가운데 일부입니다.

```
필드이름|수식어1|수식어2: 값
```

| 수식어 | 뜻 |
|---|---|
| `contains` | 값을 포함합니다 |
| `startswith` | 값으로 시작합니다 |
| `endswith` | 값으로 끝납니다 |
| `all` | 목록의 값이 모두 맞아야 합니다 |
| `re` | 정규식으로 찾습니다 |
| `base64`, `base64offset` | base64 로 바꾼 값을 찾습니다 |
| `cidr` | IP 주소 범위로 찾습니다 |
| `exists` | 참거짓 값으로 필드가 있어야 하는지, 없어야 하는지 정합니다 |
| `windash` | 값 안의 `-`, `/`, 엔 대시(–), 엠 대시(—), 가로 막대(―) 를 서로 바꾼 모든 형태를 찾습니다 |

### 예시 규칙

아래 규칙은 명세의 문법으로 만든 예시이며, 공개 규칙 모음에서 가져온 규칙이 아닙니다. VssAdmin 으로 섀도 복사본을 지우는 명령이 실행된 기록을 찾는 모양입니다.
`delete shadows` 는 섀도 복사본을 지우는 VssAdmin 명령입니다. 섀도 복사본은 [섀도 복사본 활용](volume-shadow-copy-analysis.md) 에서 다룹니다.

```yaml
title: 'Shadow copy deletion with vssadmin (wiki example)'
status: 'experimental'
description: 'Example rule written from the Sigma specification syntax'
author: 'wiki example'
logsource:
    category: 'process_creation'
    product: 'windows'
detection:
    selection:
        Image|endswith: '\vssadmin.exe'
        CommandLine|contains|all:
            - 'delete'
            - 'shadows'
    condition: 'selection'
falsepositives:
    - 'Administrators removing shadow copies on purpose'
level: 'high'
```

- `selection` 아래 두 줄은 맵이라 둘 다 맞아야 합니다.
- `CommandLine|contains|all` 은 목록의 두 값이 모두 명령줄에 들어 있어야 맞습니다.
- `Image`, `CommandLine` 은 설명하려고 넣은 필드 이름입니다. 실제로 쓸 필드 이름과 대소문자는 로그 원천과 변환 설정을 따릅니다.
- `falsepositives` 에는 관리자가 일부러 섀도 복사본을 지운 경우를 적었습니다. 규칙에 걸린 이벤트는 이 경우인지 먼저 가립니다.

## 절차

1. **로그가 남아 있는지 먼저 봅니다.** 어떤 채널이 켜져 있었는지, 로그 크기가 얼마였는지, 언제부터 남아 있는지 적습니다. 설정은 [감사 정책과 로그 설정](../../02-artifacts/event-logs/audit-policy-log-settings.md) 에서 봅니다.
2. **로그와 맞는 규칙을 고릅니다.** 규칙의 `logsource` 와 확보한 로그가 맞지 않으면 규칙을 돌려도 걸리지 않습니다.
3. **매핑을 확인합니다.** 쓰는 변환 설정이 `category` 를 어느 채널과 이벤트로 잇는지 적습니다.
4. **`status` 를 확인합니다.** `experimental`, `deprecated`, `unsupported` 규칙을 쓸지 정하고, 쓴다면 결과에 표시합니다.
5. **규칙을 돌립니다.** 변환한 질의를 검색 도구에서 돌리거나, EVTX 파일을 읽는 도구로 돌립니다.
6. **걸린 이벤트를 원래 이벤트에서 확인합니다.** 도구가 보여 준 필드를 EVTX 원래 레코드와 맞춰 봅니다.
7. **`falsepositives` 와 주변 이벤트를 봅니다.** 같은 시각 앞뒤의 로그온, 프로세스 생성, 서비스 설치를 함께 봅니다.
8. **타임라인에 넣습니다.** 이벤트마다 걸린 규칙의 제목과 판을 붙입니다. 방법은 [타임라인 작성](timeline/index.md) 에 있습니다.

## 도구

아래 도구는 예로만 듭니다.

- **텍스트 편집기와 YAML 검사기**: 규칙 파일을 읽고 문법을 확인합니다.
- **변환 도구**: Sigma 규칙을 검색 도구의 질의 언어로 바꿉니다. 변환에 쓴 설정(매핑)을 함께 보관합니다.
- **EVTX 에 규칙을 바로 돌리는 도구**: Chainsaw, Hayabusa 같은 공개 도구가 있습니다. 도구마다 매핑 방식은 설정 파일에서 확인합니다.
- 두 도구의 결과 수가 다르면 [도구 결과 교차 검증](../reporting/tool-validation.md) 의 방법으로 원래 레코드와 맞춰 봅니다.

## 함정과 한계

- **로그가 없는데 0건을 "없었다" 로 씁니다.** 0건은 그 로그가 켜져 있었고 남아 있을 때만 뜻이 있습니다.
- **로그가 지워진 것을 놓칩니다.** 규칙 결과가 비었으면 로그 삭제 흔적을 확인합니다. [이벤트 로그 삭제](../../02-artifacts/event-logs/1102-104.md) 를 봅니다.
- **규칙에 걸린 것을 침해로 씁니다.** `level` 과 `status` 는 규칙 작성자가 붙인 값입니다. `falsepositives` 를 함께 읽습니다.
- **매핑을 확인하지 않습니다.** `category` 가 어느 로그로 이어지는지는 변환 설정이 정합니다. 매핑과 확보한 로그가 맞지 않으면 걸려야 할 이벤트가 빠질 수 있습니다.
- **필드 이름이 로그와 다릅니다.** 규칙의 필드 이름이 로그의 필드 이름과 다르면 일치가 빠질 수 있습니다. 걸려야 할 표본 이벤트로 규칙을 먼저 시험해 봅니다.
- **규칙 판을 적지 않습니다.** 규칙 모음은 바뀝니다. 어떤 판의 규칙을 돌렸는지 적어야 결과를 다시 얻습니다.

## 결과를 어떻게 해석하나

| 결과 | 말해 주는 것 | 말해 주지 못하는 것 |
|---|---|---|
| 규칙에 걸림 | 이벤트 레코드가 규칙의 조건과 맞았다는 것 | 그 행위가 악의였는지, 누가 했는지 |
| 규칙에 안 걸림 | 남아 있는 로그에서 조건과 맞는 레코드를 찾지 못했다는 것 | 그 행위가 없었다는 것 |
| `level: critical` | 규칙 작성자가 중요도를 높게 매겼다는 것 | 사건의 심각도 |

- 규칙은 로그에 적힌 것만 봅니다. 로그를 켜지 않은 행위, 로그가 덮어쓴 기간의 행위는 찾지 못합니다.
- 걸린 이벤트는 다른 아티팩트와 맞춰 봅니다. PowerShell 이면 [PowerShell 실행 기록](../../02-artifacts/event-logs/powershell-event-logs-4103-4104.md), 서비스면 [서비스 설치](../../02-artifacts/event-logs/7045-4697.md) 를 봅니다.

보고서에는 규칙과 매핑과 로그 범위를 함께 씁니다.

> `<채널>` 로그(`<처음 레코드 시각>` ~ `<마지막 레코드 시각>`, UTC)에 Sigma 규칙 `<규칙 제목>`(판 `<판>`, 변환 설정 `<설정 이름>`)을 적용했다. `<시각>` 의 레코드 `<레코드 번호>` 가 규칙 조건과 맞았다. 이 레코드는 `<필드>` 가 `<값>` 인 프로세스 생성을 기록한다.

## 참고 문헌

- SigmaHQ, "Sigma Rules Specification" v2.1.0 (2025-08-02) — https://raw.githubusercontent.com/SigmaHQ/sigma-specification/main/specification/sigma-rules-specification.md
- SigmaHQ, "Sigma Modifiers" (명세 부록) — https://raw.githubusercontent.com/SigmaHQ/sigma-specification/main/specification/sigma-appendix-modifiers.md
- Microsoft Learn, "Volume Shadow Copy Service (VSS)" — https://learn.microsoft.com/en-us/windows-server/storage/file-server/volume-shadow-copy-service
