---
title: "Azure 가상 머신"
parent: "아티팩트 · Azure"
nav_order: 510
---

# Azure 가상 머신 (Azure VM)

Azure 가상 머신의 흔적은 두 층에 남습니다. 누가 VM 을 만들고 끄고 디스크를 떼어 가고 스크립트를 밀어 넣었는지는 활동 로그에, 그 스크립트가 VM 안에서 무엇을 했는지는 게스트 OS 의 에이전트 로그와 디스크에 남습니다.

## 무엇을 기록하나 · 왜 생기나

VM 을 다루는 관리 작업은 Azure Resource Manager(ARM)를 거치므로 [활동 로그](./activity-log.md)에 작업 이름(`operationName`)으로 남습니다[2]. 조사에서 자주 찾는 작업 이름은 다음과 같습니다[1].

| 작업 이름 | 뜻 |
|---|---|
| `Microsoft.Compute/virtualMachines/write`, `/delete` | VM 만들기·수정, 삭제 |
| `Microsoft.Compute/virtualMachines/start/action`, `/powerOff/action`, `/deallocate/action`, `/restart/action` | 시작, 끄기(요금 계속 부과), 끄고 컴퓨팅 자원 반납, 다시 시작 |
| `Microsoft.Compute/virtualMachines/runCommand/action` | 미리 정한 스크립트를 VM 에서 실행(동작형 Run Command) |
| `Microsoft.Compute/virtualMachines/runCommands/write`, `/read`, `/delete` | 관리형 Run Command 리소스 만들기·수정, 조회, 삭제 |
| `Microsoft.Compute/virtualMachines/diagnosticRunCommand/action` | 진단 스크립트 실행 |
| `Microsoft.Compute/virtualMachines/extensions/write` | 확장(Custom Script Extension 등) 설치·변경 |
| `Microsoft.Compute/virtualMachines/attachDetachDataDisks/action` | 기존 데이터 디스크 붙이기·떼기 |
| `Microsoft.Compute/virtualMachines/capture/action` | 가상 디스크를 복사해 비슷한 VM 을 만들 템플릿 만들기 |
| `Microsoft.Compute/virtualMachines/retrieveBootDiagnosticsData/action` | 부트 진단 로그 블롭 URI 받기 |
| `Microsoft.Compute/disks/beginGetAccess/action`, `/endGetAccess/action` | 디스크를 내려받을 SAS URI 받기, 회수 |
| `Microsoft.Compute/snapshots/write`, `/delete` | 스냅숏 만들기·수정, 삭제 |
| `Microsoft.Compute/snapshots/beginGetAccess/action`, `/endGetAccess/action` | 스냅숏을 내려받을 SAS URI 받기, 회수 |

활동 로그의 Resource Health 범주에도 VM 상태 변화가 남습니다. 사용자가 VM 을 시작하면 `details` 가 `VirtualMachineStartInitiatedByControlPlane`, `cause` 가 `UserInitiated` 인 이벤트가 남고, 플랫폼이 일으킨 변화면 `cause` 가 `PlatformInitiated` 입니다[2][3]. VM 이 꺼져 있던 이유가 사용자 작업인지 플랫폼 사건인지 구분할 때 씁니다.

VM 안쪽에는 Azure VM 에이전트 (VM Agent) 가 남기는 기록이 있습니다. Run Command 와 확장은 이 에이전트를 통해 스크립트를 실행하므로[8][10][14], 활동 로그에 `runCommand/action` 이나 `extensions/write` 가 있으면 게스트 쪽에도 짝이 되는 로그와 스크립트 파일이 생깁니다.

## 위치와 버전별 차이

### 게스트 OS 안의 경로

| 기록 | Windows | Linux |
|---|---|---|
| 동작형 Run Command 로그 | `C:\WindowsAzure\Logs\Plugins\Microsoft.CPlat.Core.RunCommandWindows\{version}\RunCommandExtension.log`[8] | `/var/log/azure/run-command/handler.log`[9] |
| Custom Script Extension 로그 | `C:\WindowsAzure\Logs\Plugins\Microsoft.Compute.CustomScriptExtension\{HandlerVersion}\CustomScriptHandler.log*`[12] | `/var/log/azure/custom-script/handler.log`[11] |
| Custom Script Extension 이 받은 스크립트·출력 | 받은 파일은 `C:\Packages\Plugins\Microsoft.Compute.CustomScriptExtension\1.*\Downloads\{n}\`, 출력은 `C:\WindowsAzure\Logs\Plugins\Microsoft.Compute.CustomScriptExtension` 아래 파일[12] | `/var/lib/waagent/custom-script/download/{n}/`(`stdout`, `stderr` 파일 포함)[11] |
| 에이전트 로그 | — | `/var/log/waagent.log`(logrotate 로 순환)[13] |
| 에이전트 프로세스 | `WindowsAzureGuestAgent.exe`[14] | `waagent`[13] |

Windows 의 `{n}` 은 실행마다 바뀔 수 있는 10진수이고, `1.*` 에는 확장의 실제 처리기 버전(예: `1.8`)이 들어갑니다[12]. Linux 에서 설정에 인라인으로 넣은 스크립트는 `/var/lib/waagent/custom-script/#/script.sh` 로 저장된 뒤 `/bin/sh -c` 로 실행됩니다[11]. Linux 에이전트는 마지막으로 프로비저닝한 사용자 정보를 `/var/lib/waagent` 에 둡니다[13].

Linux 는 배포판 이미지에 따라 에이전트 대신 cloud-init 이 프로비저닝을 맡기도 합니다. cloud-init 을 쓰는 Ubuntu 클라우드 이미지에서는 `/etc/waagent.conf` 의 `Provisioning.Enabled` 기본값이 `n` 입니다[13]. 같은 설정 파일의 `Provisioning.ExecuteCustomData` 가 `y` 면 에이전트가 프로비저닝 뒤 사용자 지정 데이터 (CustomData) 를 실행하고, `Provisioning.DeleteRootPassword`·`Provisioning.RegenerateSshHostKeyPair` 는 루트 암호 삭제와 SSH 호스트 키 재생성을 정합니다[13]. 프로비저닝 때 루트 암호가 지워졌는지, SSH 호스트 키가 새로 만들어졌는지 판단할 때 이 값을 봅니다.

Windows 에서 에이전트 설치 여부는 VM 구성의 `OSProfile` 아래 `ProvisionVMAgent` 값으로 확인합니다[14]. 에이전트가 없으면 확장을 실행할 수 없습니다[14].

### Run Command 두 가지

| 항목 | 동작형 (action) | 관리형 (managed) |
|---|---|---|
| 활동 로그 작업 | `runCommand/action` | `runCommands/write`·`/delete` |
| 실행 계정 | Windows 는 System, Linux 는 기본으로 권한 상승 사용자[8][9] | `RunAsUser` 로 다른 사용자를 지정할 수 있음[10] |
| 출력 | 마지막 4,096바이트만 호출자에게 돌려줌[8][9] | 인스턴스 뷰에 마지막 4KB, 전체는 `outputBlobUri`·`errorBlobUri` 로 지정한 append blob 에 쓸 수 있음[10] |
| 실행 방식 | 한 번에 하나, 최대 90분, 취소 불가[8][9] | 여러 개 병렬·순차, 시간 제한 지정, 몇 시간·며칠짜리도 가능[10] |
| 남는 리소스 | — | Run Command 리소스가 VM 아래 남음(`az vm run-command list`)[10] |

관리형 Run Command 는 리소스로 남아 있어서, 지워지지 않았다면 인스턴스 뷰에서 실행 상태(`ExecutionState`), 종료 코드(`ExitCode`), 출력, 시작·끝 시각을 볼 수 있습니다[10].

### 부트 진단

부트 진단 (boot diagnostics) 은 VM 이 켜지는 동안 시리얼 로그와 화면 스크린숏을 모읍니다. 시리얼 로그에는 커널 메시지가 들어갑니다[16]. 포털에서 VM 을 만들면 관리형 스토리지 계정으로 기본으로 켜집니다[16]. 관리형 계정은 직접 접근할 수 없고, 보관 기간을 정할 수 없으며, 합계가 1GB 를 넘으면 덮어씁니다[16]. 사용자 지정 스토리지 계정을 쓸 수도 있는데, 이때는 VM 과 같은 지역·구독에 있어야 합니다[16].

## 구조

VM 구성 자체는 ARM 리소스 JSON 입니다. 조사 시점의 구성을 남기려면 VM 을 인스턴스 뷰와 함께 조회합니다. Untitled Goose Tool 은 `[azure]` 설정의 `configs=True` 일 때 구독마다 모든 VM 을 `expand='instanceView'` 로 조회해 `{구독 ID}/azure_configs/vm_configs.json` 에 VM 하나당 한 줄로 씁니다[17][18]. 같은 폴더에 NIC·NSG·공인 IP·Bastion 같은 네트워크 구성도 따로 받습니다[17].

게스트 로그의 줄 모양은 다음과 같습니다. 두 줄 모두 문서 형식에 맞춰 만든 예시입니다.

```text
/var/log/waagent.log (만든 예시)
2026/09/20 01:15:42.120301 INFO [Microsoft.Azure.Extensions.customScript-2.1.6] [Enable] current handler state is: notinstalled

/var/log/azure/custom-script/handler.log (만든 예시)
time=2026-09-20T01:15:43Z version=v2.1.6/git@0000000-clean operation=enable seq=0 file=0 event="download start"
```

`waagent.log` 줄은 날짜·시각, 수준(`INFO`), 대괄호 안의 확장 이름·버전, 메시지 순서로 적힙니다[11]. `[Enable]` 은 명령이 실행되기 시작한 때이고, 같은 로그의 `op=Download` 는 확장 패키지를 Azure 에서 받은 일이지 `fileUris` 의 스크립트를 받은 일이 아닙니다[11]. `handler.log` 줄은 `time=`·`version=`·`operation=`·`seq=`·`event=` 같은 `키=값` 을 늘어놓은 모양입니다[11]. Run Command 의 Linux `handler.log` 도 줄마다 `seq=#` 가 붙고, `Awaiting completion...` 줄과 `Command existed with code: #` 줄은 Windows 로그에만 있습니다[9].

## 증거로서 의미

**증명하는 것.** 활동 로그는 어느 주체가 언제 어느 VM 에 Run Command 실행, 확장 설치, 디스크 분리, 디스크·스냅숏 SAS 발급, 스냅숏 생성을 요청했고 결과가 어땠는지 보여 줍니다[1][2]. `disks/beginGetAccess/action` 은 디스크를 내려받을 수 있는 SAS URI 를 받았다는 사실까지 보여 줍니다[1]. 게스트 쪽 로그와 `Downloads`·`download` 폴더는 에이전트를 통해 어떤 스크립트가 언제 실행됐고 무엇을 출력했는지 보여 줍니다[8][9][11][12].

**증명하지 못하는 것.** 활동 로그만으로는 Run Command 스크립트 내용과 출력을 알 수 없습니다. 동작형의 출력은 호출자에게 4,096바이트만 돌아갑니다[8]. SAS URL 로 디스크를 실제로 내려받았는지는 활동 로그에 없으므로, 보고서에는 "이 시각에 이 계정으로 디스크 SAS 발급을 요청한 기록이 있다" 까지만 씁니다. 부트 진단은 1GB 를 넘으면 덮어써서 오래된 부팅 기록이 없을 수 있습니다[16]. 레코드가 가리키는 것은 계정이나 서비스 주체이고, 키보드 앞의 사람이 아닙니다. 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 시각 해석

활동 로그 쪽 시각(`eventTimestamp`, UTC, 보통 3~20분 늦게 조회 가능)은 [활동 로그](./activity-log.md)에서 다룹니다. 게스트 로그는 형식이 서로 다릅니다.

| 기록 | 형식 | 시간대 |
|---|---|---|
| `/var/log/azure/custom-script/handler.log` | `time=YYYY-MM-DDTHH:MM:SSZ` | 끝의 `Z` 로 UTC[11] |
| `/var/log/waagent.log` | `YYYY/MM/DD HH:MM:SS.ffffff` | 표기 없음[11] |
| 관리형 Run Command 인스턴스 뷰 | 예시 출력이 `10/27/2022 9:10:52 PM` 형식 | 표기 없음[10] |

`waagent.log` 는 시간대 표기가 없으므로, 같은 실행의 `handler.log` 줄(`Z` 가 붙은 UTC)과 나란히 놓아 몇 초 안에 맞는지 보고 기준을 정합니다. 시간대를 맞추는 원칙은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)에 있습니다.

스냅숏은 스냅숏을 만든 순간의 디스크 상태입니다. 실행 중인 VM 의 스냅숏은 전원을 껐다 켜거나 비정상으로 멈춘(crash) 순간과 같은 상태라서, 실행 중이던 애플리케이션이 이런 중단을 견디지 못하면 문제가 생길 수 있습니다[5][6]. 데이터 디스크가 하나라도 있으면 VM 을 멈춘 뒤 스냅숏을 뜹니다[5][6].

## 함정과 한계

- **Run Command 작업 이름이 문서마다 다릅니다.** 동작형 Windows 문서는 `runCommand/action`[8], 동작형 Linux 문서는 `runCommands/write`[9], 관리형 Windows 문서는 `runCommand/write`(단수)[10] 권한이 필요하다고 적었습니다. 권한 목록에는 `runCommand/write`(단수)가 없고 `runCommand/action` 과 `runCommands/write`(복수)가 있습니다[1]. 활동 로그에서는 `runCommand/action` 과 `runCommands/write` 를 둘 다 찾습니다.
- **플러그인 폴더가 없을 수 있습니다.** `RemoveRunCommandWindowsExtension`·`RemoveRunCommandLinuxExtension` 명령으로 Run Command 확장을 지울 수 있고, 다음 실행 때 자동으로 다시 설치됩니다[8][9]. 게스트에 로그 폴더가 없거나 새로 만들어진 흔적이 있으면 이 명령이 쓰였을 가능성이 있습니다. 이 명령도 Run Command 로 실행하므로 활동 로그에 `runCommand/action` 이 남습니다.
- **Custom Script Extension 은 같은 설정이면 다시 실행하지 않습니다.** Windows 에서 재실행을 막으면 `CustomScriptHandler.log*` 에 "Current sequence number ... is not greater than the sequence number of the most recently executed configuration" 경고가 남습니다[12]. `extensions/write` 가 여러 번 있어도 스크립트가 그만큼 실행됐다고 단정하지 않고 게스트 로그로 확인합니다.
- **임시 OS 디스크는 스냅숏이 안 됩니다.** 임시 OS 디스크 (ephemeral OS disk) 는 VM 호스트에만 있어 스냅숏을 지원하지 않습니다[7]. 스냅숏으로 증거를 모으려면 먼저 VM 구성에서 OS 디스크 종류를 확인합니다.
- **디스크 SAS 가 살아 있으면 VM 을 켤 수 없습니다.** 조사자가 SAS 를 발급한 채 두면 "There is an active shared access signature outstanding for disk" 오류로 VM 이 시작되지 않습니다[5]. 디스크의 활성 SAS 여부는 `DiskState` 속성으로 확인하고, 받은 뒤에는 `Revoke-AzDiskAccess`·`az disk revoke-access` 로 회수합니다[5][6]. 2025년 2월 15일부터 디스크·스냅숏 SAS 는 최대 60일(5,184,000초)입니다[5][6].
- **실행 중에는 VHD 를 받을 수 없습니다.** 실행 중인 VM 에 붙은 디스크는 내려받을 수 없어서, VM 을 Stopped (deallocated) 로 만들거나 스냅숏을 떠서 받습니다[5][6]. 끄면 메모리가 사라지므로 순서는 [클라우드 가상 머신 수집](../../03-techniques/acquisition/vm-acquisition.md)을 따릅니다.
- **IMDS 요청은 네트워크 기록에 잘 남지 않습니다.** 인스턴스 메타데이터 서비스 (IMDS) 는 VM 안에서만 `169.254.169.254` 로 부르고, 통신이 호스트 밖으로 나가지 않으며, 프록시를 거치지 않고 불러야 합니다[15]. 이 주소를 부른 흔적은 VM 안의 명령 기록·프로세스 기록에서 찾아야 할 가능성이 큽니다.
- **Windows 에이전트가 지원용 로그 묶음을 만듭니다.** `CollectGuestLogs.exe` 가 이벤트 로그·OS 로그·Azure 로그·일부 레지스트리 키를 ZIP 으로 묶어 호스트로 보냅니다[14]. 디스크에서 이 ZIP 이나 프로세스 흔적을 보면 지원용 수집일 수 있으니 공격 도구로 오해하지 않습니다.

## 직접 분석해 보기

**게스트 로그와 활동 로그를 한 번 맞춰 보기.** Linux VM 디스크 이미지에서 `/var/log/azure/custom-script/handler.log` 를 열고 `operation=enable` 이면서 `event=start` 인 줄의 `time=` 과 `seq=` 를 적습니다. 같은 `seq` 의 `event="creating output directory"` 줄에 `path=/var/lib/waagent/custom-script/download/0` 처럼 출력 폴더가 나오므로[11], 그 폴더의 스크립트와 `stdout`·`stderr` 를 확보합니다. 그다음 활동 로그에서 같은 VM 의 `extensions/write` 를 찾아, `eventTimestamp` 가 `handler.log` 의 `time=` 보다 앞서는지 봅니다. 활동 로그의 작업 시각 바로 뒤에 게스트 쪽 `enable` 이 시작하고 VM 이 같으면 두 기록을 한 사건으로 묶을 수 있습니다.

Log Analytics 로 활동 로그를 보내 두었다면 VM 에 스크립트를 밀어 넣은 작업을 한 번에 뽑을 수 있습니다[2].

```kusto
AzureActivity
| where tolower(OperationNameValue) in (
    "microsoft.compute/virtualmachines/runcommand/action",
    "microsoft.compute/virtualmachines/runcommands/write",
    "microsoft.compute/virtualmachines/extensions/write",
    "microsoft.compute/virtualmachines/attachdetachdatadisks/action",
    "microsoft.compute/disks/begingetaccess/action",
    "microsoft.compute/snapshots/write")
| project TimeGenerated, Caller, CallerIpAddress, OperationNameValue, ActivityStatusValue, _ResourceId, CorrelationId
| order by TimeGenerated asc
```

같은 값이 대소문자만 다르게 들어오는 일이 있어서 `tolower()` 로 바꿔 비교합니다([활동 로그](./activity-log.md)의 함정과 한계).

**공개 도구.** 구성은 Untitled Goose Tool 의 `configs=True` 로 `vm_configs.json` 을, `bastion_logs=True` 로 Bastion 감사 로그 컨테이너 `insights-logs-bastionauditlogs` 를 받습니다[17][18]. Goose 는 디스크 이미지를 받지 않습니다[17]. 관리형 Run Command 는 `az vm run-command list --vm-name ... --resource-group ...` 로 목록을, `az vm run-command show ... --expand instanceView` 나 `Get-AzVMRunCommand ... -Expand InstanceView` 로 실행 결과를 봅니다[10]. 디스크 사본은 `New-AzSnapshotConfig -CreateOption copy` 와 `New-AzSnapshot`, 또는 `az snapshot create` 로 만듭니다[4]. 스냅숏은 원본 디스크와 독립된 읽기 전용 전체 사본이고, 종류는 Full·Incremental 가운데 고릅니다[4][5].

증거 관리 연속성 (chain of custody) 을 갖춘 수집 구조로 Microsoft 참조 아키텍처가 있습니다. 별도 SOC 구독의 Automation 하이브리드 러너 워커가 `Copy-VmDigitalEvidence` 런북으로 OS·데이터 디스크 스냅숏을 떠서 법적 보존 (legal hold) 이 걸린 불변 블롭과 임시 파일 공유에 옮기고, 해시(MD5·SHA256·SKEIN·KECCAK(SHA3))를 계산해 SOC 의 Key Vault 에 저장한 뒤 불변 사본 말고는 지웁니다[7]. 스냅숏을 누가 언제 떴는지는 감사 로그에 남고, 조사자에게는 8시간 뒤 만료되는 읽기 전용 SAS 를 주는 예를 듭니다[7]. 받은 디스크의 파일 시스템 분석은 [Linux 판의 클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html)과 [디스크 이미징](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/disk-imaging.html)으로 이어집니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [활동 로그](./activity-log.md) | Run Command·확장·디스크 SAS·스냅숏 작업의 주체와 시각. Sigma 규칙은 `Microsoft.Compute/snapshots/write` 를 드문 작업으로[19], `virtualMachines/write` 와 `Microsoft.Resources/deployments/write` 의 대량 발생을 이상 징후로 봅니다[20] |
| [리소스 로그와 진단 설정](./resource-logs.md) | Bastion 감사 로그 같은 리소스 로그가 켜져 있는지 |
| [네트워크 흐름 로그](./flow-logs.md) | VM 의 NIC·사설 IP 로 드나든 연결 |
| [Storage 계정 기록](./storage-logs.md) | 관리형 Run Command 출력 블롭, 사용자 지정 부트 진단 계정 접근 |
| [Linux 인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html) | 게스트에 SSH 로 들어온 계정과 시각 |
| [EC2 인스턴스와 스냅숏](../aws/ec2-ebs.md) | AWS 에서 같은 질문을 풀 때의 대응 기록 |

여러 기록을 시간순으로 합치는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md)에 있습니다.

## 실습

1. 시험 구독에서 Linux VM 에 동작형 Run Command 로 `RunShellScript` 를 한 번 실행합니다. 활동 로그에 남는 `operationName` 은 `runCommand/action` 과 `runCommands/write` 가운데 어느 쪽이고, 게스트의 `/var/log/azure/run-command/handler.log` 에는 몇 초 뒤에 첫 줄이 생기나요?
2. 같은 VM 에 관리형 Run Command 를 만든 뒤 지웁니다. 활동 로그에 `runCommands/delete` 가 남은 뒤에도 게스트 쪽 로그로 실행 사실을 확인할 수 있나요?
3. Custom Script Extension 을 같은 설정으로 두 번 배포합니다. 활동 로그의 `extensions/write` 는 몇 번 남고, 게스트의 `download` 폴더는 몇 개 생기나요?
4. 디스크에 `az disk grant-access` 로 SAS 를 발급하고 회수하지 않은 채 VM 을 시작해 봅니다. 활동 로그에는 어떤 결과가 남고, `DiskState` 값은 무엇인가요?
5. `waagent.log` 의 `[Enable]` 줄과 `handler.log` 의 `event=start` 줄 시각을 견줘, 이 VM 에서 `waagent.log` 가 UTC 로 적히는지 판단합니다.

## 참고 문헌

1. Microsoft, "Azure permissions for Compute" (2026-07-01). https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/compute
2. Microsoft, "Activity Log in Azure Monitor", azure-monitor-docs (ms.date 2026-05-04). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log.md
3. Microsoft, "Azure Activity Log event schema", azure-monitor-docs (ms.date 2026-03-17). https://github.com/MicrosoftDocs/azure-monitor-docs/blob/main/articles/azure-monitor/fundamentals/activity-log-schema.md
4. Microsoft, "Create a snapshot of an Azure managed disk" (2026-09-19). https://learn.microsoft.com/en-us/azure/virtual-machines/snapshot-copy-managed-disk
5. Microsoft, "Download a Windows VHD from Azure" (2026-09-03). https://learn.microsoft.com/en-us/azure/virtual-machines/windows/download-vhd
6. Microsoft, "Download a Linux VHD from Azure" (2026-09-03). https://learn.microsoft.com/en-us/azure/virtual-machines/linux/download-vhd
7. Microsoft, "Computer forensics chain of custody in Azure", Azure Architecture Center. https://learn.microsoft.com/en-us/azure/architecture/example-scenario/forensics/
8. Microsoft, "Run scripts in your Windows VM by using action Run Commands" (2025-12-13). https://learn.microsoft.com/en-us/azure/virtual-machines/windows/run-command
9. Microsoft, "Run scripts in your Linux VM by using action Run Commands" (2025-08-27). https://learn.microsoft.com/en-us/azure/virtual-machines/linux/run-command
10. Microsoft, "Run scripts in your Windows VM by using managed Run Commands" (2025-12-13). https://learn.microsoft.com/en-us/azure/virtual-machines/windows/run-command-managed
11. Microsoft, "Use the Azure Custom Script Extension Version 2 with Linux virtual machines" (2025-08-18). https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-linux
12. Microsoft, "Custom Script Extension for Windows" (2025-08-18). https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/custom-script-windows
13. Microsoft, "Azure Linux VM Agent overview" (2026-05-11). https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/agent-linux
14. Microsoft, "Azure Windows VM Agent overview" (2025-12-08). https://learn.microsoft.com/en-us/azure/virtual-machines/extensions/agent-windows
15. Microsoft, "Azure Instance Metadata Service" (2025-07-29). https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
16. Microsoft, "Azure boot diagnostics" (2025-12-01). https://learn.microsoft.com/en-us/azure/virtual-machines/boot-diagnostics
17. CISA, Untitled Goose Tool, azure_dumper.py. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/azure_dumper.py
18. CISA, Untitled Goose Tool, README.md. https://github.com/cisagov/untitledgoosetool/blob/develop/README.md
19. SigmaHQ, azure_rare_operations.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_rare_operations.yml
20. SigmaHQ, azure_creating_number_of_resources_detection.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_creating_number_of_resources_detection.yml
