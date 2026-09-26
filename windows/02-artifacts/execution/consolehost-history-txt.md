---
title: "PowerShell 명령 기록"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 1070
---

# PowerShell 명령 기록 (ConsoleHost_history.txt)

## 한 줄 요약

PowerShell 의 PSReadLine 모듈은 대화형 콘솔에서 친 명령을 사용자별 글자 파일에 한 줄씩 저장합니다. Windows 의 기본 파일은 `%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt` 입니다. 파일에는 시각이 없습니다. 비밀 값을 뜻하는 단어가 든 명령은 거르기 규칙에 걸리면 파일에 들어가지 않습니다. 규칙은 PSReadLine 버전마다 다릅니다.

## 무엇을 기록하나 · 왜 생기나

PSReadLine 은 PowerShell 콘솔에서 명령 줄 입력을 맡는 모듈이고, 위 화살표 같은 키로 예전 명령을 다시 불러오는 기능도 맡습니다. 불러오기에 쓰려고 모아 둔 명령을 파일에도 저장하는데, 이 파일이 명령 기록입니다. 파일 이름은 `$($Host.Name)_history.txt` 라서 호스트 이름이 다르면 파일도 따로 생깁니다.

| 호스트 | 파일 이름 |
|---|---|
| 일반 콘솔 | `ConsoleHost_history.txt` |
| VS Code 의 PowerShell 확장 콘솔 | `Visual Studio Code Host_history.txt` |

PSReadLine 은 기본 콘솔 호스트, Windows Terminal, VS Code 에서 동작합니다. Windows PowerShell ISE 에서는 동작하지 않아서 ISE 에서 친 명령은 이 파일에 남지 않습니다. 이 기록은 PowerShell 자체의 세션 기록 (`Get-History`) 과 별개입니다.

## 위치와 버전별 차이

### 위치

| OS | 기본 폴더 |
|---|---|
| Windows | `%APPDATA%\Microsoft\Windows\PowerShell\PSReadLine\` |
| Windows 가 아닌 OS | `$Env:XDG_DATA_HOME/powershell/PSReadLine/` 또는 `$HOME/.local/share/powershell/PSReadLine/` |

- `%APPDATA%` 는 사용자 프로필 아래에 있어서 사용자마다 파일이 따로 생깁니다. 프로필 폴더가 어느 계정의 것인지는 [사용자 프로필 목록](../system-account/profilelist.md) 으로 확인합니다.
- `HistorySavePath` 옵션으로 경로를 바꿀 수 있습니다.
- `Set-PSReadLineOption` 으로 바꾼 설정은 그 세션에만 적용됩니다. 계속 쓰려면 사용자가 프로필 스크립트에 넣어야 합니다. 경로가 바뀌었는지 알려면 사용자의 프로필 스크립트를 확인합니다.

### 버전

PowerShell 에 함께 들어간 PSReadLine 버전입니다.

| PowerShell | PSReadLine |
|---|---|
| Windows PowerShell 5.1 | 2.0.0 |
| 7.0.11 | 2.0.4 |
| 7.2.5 | 2.1.0 |
| 7.3.0 | 2.2.6 |
| 7.4.0-rc.1 | 2.3.4 |
| 7.4.2 | 2.3.5 |
| 7.4.7, 7.5.0 | 2.3.6 |
| 7.6.0-rc.1 | 2.4.5 |

- PSReadLine 은 PowerShell 5.1 이상에서만 동작합니다. Windows PowerShell 5.1 에도 새 버전을 따로 설치할 수 있습니다. 5.1 이라고 2.0.0 이라고 단정하지 않습니다.
- 민감한 명령을 거르는 규칙이 PSReadLine 버전마다 다릅니다. 아래 "민감한 명령 거르기" 를 봅니다.
- PowerShell 7 을 따로 설치하지 않은 Windows 에는 Windows PowerShell 5.1(예: 5.1.26100)과 PSReadLine 2.0.0 만 있습니다.
- Windows 버전마다 어떤 PowerShell 이 기본으로 들어 있는지는 이 페이지에서 다루지 않습니다. 검체에 설치된 PowerShell 과 PSReadLine 버전을 먼저 확인합니다.

## 구조

- 글자 파일이고 한 줄에 명령 하나가 들어갑니다.
- 여러 줄에 걸친 명령을 어떻게 저장하는지는 공개 자료가 없어 검체에서 확인합니다.
- 시각 칸이 없습니다.
- Windows 에서 파일은 BOM 없는 UTF-8 이고, 한글도 UTF-8 로 들어갑니다. 줄 끝은 CRLF 입니다.

### 저장 방식을 정하는 설정

| 설정 | 값 | 파일에 미치는 영향 |
|---|---|---|
| `HistorySaveStyle` | `SaveIncrementally` (기본) | 명령을 실행할 때마다 저장합니다. 여러 PowerShell 창이 같은 파일을 함께 씁니다 |
| | `SaveAtExit` | PowerShell 을 끝낼 때 파일에 덧붙입니다 |
| | `SaveNothing` | 파일에 쓰지 않습니다 |
| `HistorySavePath` | 파일 경로 | 파일 위치를 바꿉니다 |
| `HistoryNoDuplicates` | 켬·끔 | 불러올 때만 중복을 숨깁니다. 파일에는 중복 명령이 그대로 들어갑니다 |
| `MaximumHistoryCount` | 문서에는 기본값이 "None" 으로 적혀 있지만[2], PSReadLine 2.0.0 에서는 4096 입니다 | 파일 줄 수에 영향을 주는지는 공개 자료 없음 |
| `AddToHistoryHandler` | 사용자가 정한 스크립트 | 명령마다 저장할지 정합니다. 반환값은 아래 표에 있습니다 |

- `SaveNothing` 으로 바꿨다가 같은 세션에서 `SaveIncrementally` 로 되돌리면, 그동안 친 명령도 모두 저장됩니다.

| `AddToHistoryHandler` 반환값 | 뜻 |
|---|---|
| `MemoryAndFile` | 파일과 세션 기록에 모두 넣습니다 |
| `MemoryOnly` | 지금 세션 기록에만 넣습니다 |
| `SkipAdding` | 어디에도 넣지 않습니다 |
| `$false` | `SkipAdding` 과 같습니다 |
| `$true` | `MemoryAndFile` 과 같습니다 |

### 민감한 명령 거르기

- 명령 줄에 `password`, `asplaintext`, `token`, `apikey`, `secret` 이 들어 있으면 파일에 쓰지 않습니다.
- PSReadLine 2.2.0 은 명령 줄의 구문 트리 (AST, Abstract Syntax Tree) 를 보고 판단합니다.
- 2.2.0 은 SecretManagement 모듈의 안전한 명령은 기록합니다. `Get-Secret`, `Get-SecretInfo`, `Get-SecretVault`, `Register-SecretVault`, `Remove-Secret`, `Set-SecretInfo`, `Set-SecretVaultDefault`, `Test-SecretVault`, `Unlock-SecretVault`, `Unregister-SecretVault` 입니다.
- 2.2.0 에서 기록하지 않는 명령의 예는 아래와 같습니다.
  - `$token = 'abcd'`
  - `Set-Secret abc $mySecret`
  - `ConvertTo-SecureString stringValue -AsPlainText`
  - `Invoke-WebRequest -Token xxx`
- 2.3.4 부터는 속성에 값을 넣는 명령(예: `$a.Secret = $secret`)을 기록합니다. az·gcloud·kubectl 의 토큰 조회 명령도 기록합니다.
- 2.2.0 은 거르기를 개선한 판입니다[1]. 그 전 버전에도 거르기가 있었지만, 2.0.0 의 규칙은 공개 자료에 없어 검체에서 확인합니다.
- PSReadLine 2.0.0 에서도 `AddToHistoryHandler` 가 설정되어 있는 경우가 있습니다.

## 증거로서 의미

### 증명하는 것

- 한 줄은 이 사용자 프로필의 대화형 PowerShell 에서 그 명령 줄을 실행한 기록입니다.
- 파일 안의 줄 순서는 저장된 순서이므로 명령의 앞뒤 관계를 알려 줍니다.
- 파일이 든 프로필 폴더로 어느 사용자 계정의 기록인지 알 수 있습니다.
- 파일 이름으로 어느 호스트의 기록인지 가를 수 있습니다. 예를 들어 VS Code 확장 콘솔의 명령은 따로 된 파일에 있습니다.

### 증명하지 못하는 것

- 명령을 언제 실행했는지는 알 수 없습니다. 줄마다 시각이 없습니다.
- 명령이 성공했는지, 무엇을 출력했는지는 알 수 없습니다.
- 여러 창이 같은 파일에 쓰므로 어느 창·세션에서 친 명령인지는 알 수 없습니다.
- 키보드 앞의 사람이 누구인지는 알 수 없습니다.
- 줄이 없다고 명령을 실행하지 않은 것은 아닙니다. 아래 경우에는 파일에 남지 않습니다.
  - 거르는 단어가 든 명령
  - ISE 에서 친 명령
  - `SaveNothing` 이나 `AddToHistoryHandler` 로 저장을 막은 명령
  - `HistorySavePath` 로 다른 파일에 저장한 명령
  - 대화형 콘솔을 거치지 않은 명령 (아래 "함정과 한계" 참고)

보고서에는 "그 시각에 그 명령을 실행했다" 대신 "사용자 X 의 `ConsoleHost_history.txt` 의 N 번째 줄에 명령 Y 가 있다. 이 파일에는 시각이 없다. 파일의 마지막 수정 시각은 A(UTC) 이다" 처럼 씁니다.

## 시각 해석

- 줄마다 시각이 없습니다. 파일의 마지막 수정 시각은 마지막으로 저장한 때입니다. 기본값 `SaveIncrementally` 이면 마지막 명령을 실행한 무렵입니다. `SaveAtExit` 이면 PowerShell 을 끝낸 무렵입니다.
- 파일 시각은 [마스터 파일 테이블](../filesystem/mft.md) 에서 읽습니다.
- 줄마다 시각을 붙이려면 다른 기록과 맞춥니다.
  - 스크립트 블록 기록 이벤트가 켜져 있으면 그 이벤트의 시각과 내용을 봅니다. [PowerShell 실행 기록](../event-logs/powershell-event-logs-4103-4104.md) 에서 다룹니다.
  - 명령이 띄운 프로그램이나 만든 파일의 시각을 봅니다.
  - [USN 변경 저널](../filesystem/usnjrnl.md) 에 이 파일의 변경 기록이 남아 있으면, 파일이 바뀐 시각을 여러 개 얻을 수 있습니다.
- 줄에 시각을 붙인 뒤에는 앞 줄이 뒤 줄보다 늦은 시각이 되지 않는지 봅니다.

## 함정과 한계

- **파일이 여러 개일 수 있습니다.** 호스트마다 파일이 다릅니다. PSReadLine 폴더의 `*_history.txt` 를 모두 수집합니다.
- **경로가 바뀌었을 수 있습니다.** 사용자의 프로필 스크립트에 `HistorySavePath` 가 있는지 봅니다.
- **스크립트와 원격 실행은 남지 않을 수 있습니다.** 비대화형 PowerShell(`-NonInteractive`) 로 명령을 수십 개 실행해도 파일의 마지막 수정 시각은 바뀌지 않습니다.
- **거른 명령은 처음부터 없습니다.** 비밀 값을 다루는 명령이 없다고 그런 명령을 치지 않았다고 쓰지 않습니다. 검체의 PSReadLine 버전으로 어떤 규칙이 적용됐는지 따져 봅니다.
- **거르지 않은 비밀 값은 평문으로 남습니다.** 거르는 단어가 없는 명령 줄에 든 비밀번호 같은 값은 그대로 파일에 들어갑니다. 보고서에 옮길 때 가립니다.
- **여러 창의 명령이 섞입니다.** 기본값에서는 여러 창이 같은 파일에 씁니다. 앞뒤 줄이 같은 창에서 나왔다고 단정하지 않습니다.
- **중복 명령도 파일에 그대로 있습니다.** `HistoryNoDuplicates` 가 켜져 있어도 마찬가지입니다. 같은 명령이 여러 번 나오면 여러 번 친 것으로 봅니다.
- **`AddToHistoryHandler` 가 있다고 조작을 단정하지 않습니다.** 평범한 PC 에도 설정되어 있는 경우가 있습니다. 설정 내용이 어디서 왔는지 프로필 스크립트에서 확인합니다.
- **지우기와 조작.** 글자 파일이라 줄을 지우거나 고치기 쉽습니다. 파일 전체를 지울 수도 있습니다. `SaveNothing` 인 채로 세션을 끝내면 그 세션의 명령은 파일에 들어가지 않습니다. 지운 파일과 옛 내용은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 과 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 로 찾습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 UTF-8 규칙으로 만든 예시입니다. 특정 검체에서 나온 값이 아닙니다. 명령 `cd 문서` 한 줄입니다.

```
63 64 20 EB AC B8 EC 84 9C 0D 0A    c d (공백) 문 서 CR LF
```

- 영문과 공백은 1바이트입니다.
- 한글은 한 글자에 3바이트입니다. `EB AC B8` 이 "문", `EC 84 9C` 가 "서" 입니다.
- 줄 끝은 `0D 0A` 입니다. `0A` 의 개수가 저장된 명령 줄 수입니다.
- BOM 이 없으면 파일 첫 바이트가 바로 첫 명령의 첫 글자입니다.
- 인코딩 규칙은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에 정리합니다.

### 공개 도구로 한 번

파일을 사본으로 뜬 뒤 Windows PowerShell 5.1 에서 줄 번호를 붙여 읽습니다.

```powershell
$i = 0
Get-Content .\ConsoleHost_history.txt -Encoding UTF8 |
  ForEach-Object { $i++; '{0,5}  {1}' -f $i, $_ }
```

여러 호스트의 파일에서 관심 있는 명령을 찾습니다. 아래 패턴은 예시입니다.

```powershell
Select-String -Path .\*_history.txt -Encoding UTF8 `
  -Pattern 'Invoke-WebRequest|DownloadString|Compress-Archive|Remove-Item'
```

- 줄 번호를 보고서에 함께 적습니다. 원본 파일의 해시도 적어 둡니다.
- 메모장 같은 편집기로 열어도 됩니다. 이때는 인코딩을 UTF-8 로 지정합니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| PowerShell 실행 기록 | 스크립트 블록 내용과 시각 | [PowerShell 실행 기록](../event-logs/powershell-event-logs-4103-4104.md) |
| 프로세스 생성 이벤트 | PowerShell 프로세스가 뜬 시각과 명령 줄 | [프로세스 생성](../event-logs/4688.md) |
| 원격 명령 실행 이벤트 | 대화형 콘솔을 거치지 않은 원격 실행 | [원격 명령 실행 이벤트](../event-logs/winrm-wmi-activity.md) |
| 프리페치 | PowerShell 과 명령이 띄운 프로그램의 실행 시각 | [프리페치](prefetch/index.md) |
| USN 변경 저널 | 기록 파일이 바뀐 시각들 | [USN 변경 저널](../filesystem/usnjrnl.md) |
| 사용자 프로필 목록 | 파일이 든 프로필 폴더의 계정 | [사용자 프로필 목록](../system-account/profilelist.md) |

침해 조사에서 쓰는 흐름은 [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) 와 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.

## 실습

PowerShell 을 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필을 꺼내 풀어 봅니다.

1. 사용자마다 PSReadLine 폴더에 어떤 `*_history.txt` 파일이 있습니까? 각 파일의 줄 수와 마지막 수정 시각은 무엇입니까?
2. 파일을 내려받거나 압축하거나 지우는 명령이 있습니까? 그 줄 앞뒤로 어떤 명령이 있습니까?
3. 같은 시간대의 PowerShell 이벤트 로그에 같은 명령이 있습니까? 있다면 그 명령의 시각으로 앞뒤 줄의 시간 범위를 좁혀 봅니다.
4. 검체의 PSReadLine 버전은 무엇입니까? 그 버전에서 어떤 명령이 파일에 남지 않았을지 따져 봅니다.
5. 사용자의 프로필 스크립트에 `Set-PSReadLineOption` 이 있습니까? 있다면 어떤 설정을 바꿨습니까?

## 참고 문헌

1. Microsoft Learn, *about_PSReadLine* (PowerShell 7.6 문서, 2026-03-18 — 파일 이름 규칙, 동작하는 호스트와 ISE, PowerShell 과 PSReadLine 버전 표, 민감한 명령 거르기). https://learn.microsoft.com/en-us/powershell/module/psreadline/about/about_psreadline
2. Microsoft Learn, *Set-PSReadLineOption* (PowerShell 7.6 문서, 2026-03-04 — 기본 경로, `HistorySavePath`·`HistorySaveStyle`·`HistoryNoDuplicates`·`MaximumHistoryCount`·`AddToHistoryHandler`, 설정 적용 범위). https://learn.microsoft.com/en-us/powershell/module/psreadline/set-psreadlineoption
