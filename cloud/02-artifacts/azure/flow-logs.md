---
title: "네트워크 흐름 로그"
parent: "아티팩트 · Azure"
nav_order: 480
---

# 네트워크 흐름 로그 (NSG·VNet Flow Logs)

Azure Network Watcher 가 네트워크 인터페이스(MAC 주소)마다 IP 흐름을 1분 간격으로 요약해 Storage 계정에 JSON 으로 쌓는 기록이고, 어느 주소가 어느 포트로 언제 연결했으며 어느 규칙이 허용·거부했는지와 대략 몇 바이트가 오갔는지를 알려 줍니다.

## 무엇을 기록하나 · 왜 생기나

흐름 로그 (flow log) 는 Network Watcher 의 기능으로, OSI 4계층에서 IP 흐름을 기록합니다[1][2]. 종류는 둘이고, 네트워크 보안 그룹 (network security group, NSG) 단위로 켜는 NSG 흐름 로그와 가상 네트워크 (virtual network, VNet) 단위로 켜는 VNet 흐름 로그가 있습니다[1]. VNet 흐름 로그는 가상 네트워크뿐만 아니라 서브넷이나 네트워크 인터페이스에도 만들 수 있습니다[6].

두 로그 모두 Azure 플랫폼이 1분 간격으로 모으고, 레코드 하나에 흐름이 일어난 인터페이스, 5-튜플(출발지·목적지 주소, 출발지·목적지 포트, 프로토콜), 방향, 허용·거부 결과, 주고받은 양(NSG 흐름 로그는 버전 2 만)을 담습니다[1][2]. 흐름마다 그 흐름을 평가한 NSG 규칙 이름이 붙고, VNet 흐름 로그에는 Virtual Network Manager 보안 관리 규칙과 VNet 암호화 상태까지 붙습니다[1].

기본으로 켜져 있는 로그가 아닙니다. 관리자가 흐름 로그 리소스를 만들어 두지 않았다면 사고 이전 구간의 기록은 없습니다. 흐름 로그는 Network Watcher 에서 가상 네트워크·서브넷·네트워크 인터페이스를 대상으로 흐름 로그 리소스를 만들어 켭니다[6]. 로그 종류 전반은 [로그의 종류](../../01-foundations/logging/log-types.md) 에서 다룹니다.

## 위치와 버전별 차이

### NSG 흐름 로그와 VNet 흐름 로그

NSG 흐름 로그는 2027년 9월 30일에 퇴역하고, 새 NSG 흐름 로그는 이미 만들 수 없습니다[3]. 퇴역한 뒤 Azure 는 구독에 남은 NSG 흐름 로그 리소스를 지우지만, Storage 에 쌓인 레코드는 지우지 않고 설정해 둔 보관 정책을 따르게 둡니다[3]. 그래서 2027년 이후 조사에서도 오래된 NSG 흐름 로그 블롭이 남아 있을 수 있습니다. 포털의 이전 기능은 `MigrationFromNsgToAzureFlowLogging.ps1` 스크립트와 `RegionSubscriptionConfig.json` 을 zip 파일로 내려 주고, 스크립트로 분석을 마치면 스크립트와 같은 폴더에 `AnalysisReport-<subscriptionId>-<region>-<time>.html` 분석 보고서가 생깁니다[5]. 관리자 PC 에서 이 파일들이 보이면 그 무렵 NSG 흐름 로그를 VNet 흐름 로그로 옮기려 했을 가능성이 있고, 실제로 옮겼는지는 흐름 로그 목록과 [활동 로그](activity-log.md) 로 확인합니다.

| 항목 | NSG 흐름 로그 | VNet 흐름 로그 |
|---|---|---|
| 켜는 단위 | NSG | 가상 네트워크·서브넷·네트워크 인터페이스[6] |
| 퇴역 | 2027-09-30[3] | 해당 없음 |
| 상태 없는 흐름의 바이트·패킷 | 기록 안 함 | 기록함[1] |
| VNet 암호화 상태 | 기록 안 함 | 기록함[1] |
| API Management, Application Gateway, Virtual Network Manager, ExpressRoute 게이트웨이, VPN 게이트웨이 | 기록 안 함 | 기록함[1] |
| ExpressRoute FastPath | 기록 안 함 | 기록 안 함[1] |
| 가상 머신 확장 집합 | 기록함 | 기록함[1] |
| D·E·F 계열 v6 VM 크기 | 지원 안 함[2] | 이 크기에는 VNet 흐름 로그를 쓰라고 권함[2] |
| Storage 컨테이너 | `insights-logs-networksecuritygroupflowevent`[2] | `insights-logs-flowlogflowevent`[6] |

같은 서브넷의 NSG 에 NSG 흐름 로그를 켠 채로 그 서브넷이나 상위 VNet 에 VNet 흐름 로그를 켜면, 같은 흐름이 두 번 기록되거나 VNet 흐름 로그에만 남을 수 있습니다[1]. 이전 기간을 조사할 때는 두 컨테이너를 다 봅니다.

### Storage 경로

블롭은 인터페이스 MAC 주소마다 한 시간에 하나씩 생기고 이름은 늘 `PT1H.json` 입니다[2][4]. NSG 흐름 로그의 경로는 아래와 같습니다[2][4].

```text
https://{storageAccountName}.blob.core.windows.net/insights-logs-networksecuritygroupflowevent/resourceId=/SUBSCRIPTIONS/{subscriptionID}/RESOURCEGROUPS/{resourceGroupName}/PROVIDERS/MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/{nsgName}/y={year}/m={month}/d={day}/h={hour}/m=00/macAddress={macAddress}/PT1H.json
```

VNet 흐름 로그의 경로는 Microsoft 문서끼리도 세 가지로 다르게 적혀 있습니다. 흐름 로그 관리 문서의 PowerShell·Azure CLI 절은 첫째 줄 모양, 포털 절은 둘째 줄 모양으로 적고[6], 블록을 읽는 PowerShell 스크립트는 셋째 줄 모양으로 블롭 이름을 만듭니다[4].

```text
insights-logs-flowlogflowevent/flowLogResourceID=/SUBSCRIPTIONS/{subscriptionID}/RESOURCEGROUPS/NETWORKWATCHERRG/PROVIDERS/MICROSOFT.NETWORK/NETWORKWATCHERS/NETWORKWATCHER_{Region}/FLOWLOGS/{FlowlogResourceName}/y={year}/m={month}/d={day}/h={hour}/m=00/macAddress={macAddress}/PT1H.json
insights-logs-flowlogflowevent/flowLogResourceID=/{subscriptionID}_NETWORKWATCHERRG/NETWORKWATCHER_{Region}_{ResourceName}-{ResourceGroupName}-FLOWLOGS/y={year}/m={month}/d={day}/h={hour}/m=00/macAddress={macAddress}/PT1H.json
insights-logs-flowlogflowevent/flowLogResourceID=/{SUBSCRIPTIONID}_NETWORKWATCHERRG/NETWORKWATCHER_{REGION}_{VNETFLOWLOGNAME}/y={year}/m={MM}/d={dd}/h={HH}/m=00/macAddress={macAddress}/PT1H.json
```

경로를 짐작해 받지 말고, 컨테이너의 블롭 목록을 먼저 받아 실제 이름 모양을 확인합니다. Storage 계정은 로그를 남기는 리소스와 같은 리전에 있어야 하고, 구독은 달라도 같은 Microsoft Entra 테넌트에 묶여 있어야 합니다[1][2]. 그래서 다른 구독의 Storage 계정에 흐름 로그가 쌓여 있을 수 있습니다.

### 보관과 요금 (2026년 9월 문서 기준)

| 항목 | NSG 흐름 로그 | VNet 흐름 로그 |
|---|---|---|
| 보관 설정 | 만든 뒤 최대 1년까지 자동 삭제, 범용 v2 계정만[2] | "Retention (days)" 에 일수, 0 이면 직접 지울 때까지 보관, Standard 범용 v2 계정만[6] |
| 흐름 로그 요금 | 모은 GB 당, 구독마다 월 5GB 무료[2] | 모은 GB 당, 구독마다 월 5GB 무료[1] |
| Storage 요금 | 따로 붙음[2] | 따로 붙음[1] |
| Traffic analytics | GB 당 처리 요금, 무료 구간 없음[2] | GB 당 처리 요금, 무료 구간 없음[1] |

흐름 로그 리소스를 지워도 Storage 에 쌓인 데이터는 지워지지 않고, 보관 정책에 따라 지워지거나 누가 지울 때까지 남습니다[6]. 구독에 있는 흐름 로그 리소스와 실제 보관 일수는 포털의 Network Watcher > Flow logs 화면, `Get-AzNetworkWatcherFlowLog`, `az network watcher flow-log list`·`az network watcher flow-log show` 로 확인합니다[6].

## 구조

블롭 하나는 `records` 배열을 담은 JSON 문서이고, 레코드 하나가 대략 1분치 흐름을 담습니다[1][2]. JSON 로그를 읽는 일반 방법은 [JSON 로그 읽기](../../01-foundations/logging/json-logs.md) 에서 다룹니다.

### NSG 흐름 로그 레코드

| 필드 | 뜻 |
|---|---|
| `time` | 이벤트를 기록한 UTC 시각[2] |
| `systemId` | NSG 의 시스템 ID[2] |
| `category` | 늘 `NetworkSecurityGroupFlowEvent`[2] |
| `resourceId` | NSG 의 리소스 ID. 속성 목록에는 `resourceid` 로, 예시 레코드에는 `resourceId` 로 적혀 있음[2] |
| `operationName` | 늘 `NetworkSecurityGroupFlowEvents`[2] |
| `properties.Version` | 스키마 버전, 1 또는 2[2] |
| `properties.flows[].rule` | 흐름을 처리한 규칙 이름[2] |
| `properties.flows[].flows[].mac` | 흐름을 모은 VM 인터페이스의 MAC 주소[2] |
| `properties.flows[].flows[].flowTuples[]` | 쉼표로 가른 흐름 튜플 문자열[2] |

규칙 이름은 기본 규칙이면 `DefaultRule_DenyAllInBound`·`DefaultRule_AllowInternetOutBound` 처럼, 사용자가 만든 규칙이면 `UserRule_default-allow-rdp` 처럼 `UserRule_` 이 앞에 붙습니다[2]. NSG 이름이 80자, 규칙 이름이 65자를 넘으면 기록할 때 잘릴 수 있습니다[2].

튜플은 버전 1 이 8칸, 버전 2 가 13칸입니다[2].

| 칸 | 뜻 | 값 |
|---|---|---|
| 1 | 흐름 시각 | UNIX epoch |
| 2·3 | 출발지 IP·목적지 IP | |
| 4·5 | 출발지 포트·목적지 포트 | |
| 6 | 프로토콜 | `T` TCP, `U` UDP |
| 7 | 방향 | `I` 들어옴, `O` 나감 |
| 8 | 결정 | `A` 허용, `D` 거부 |
| 9 (버전 2) | 흐름 상태 | `B` 시작(통계 없음), `C` 계속(5분 간격 통계), `E` 끝(통계 있음) |
| 10·11 (버전 2) | 보낸 패킷·보낸 바이트 | 출발지에서 목적지로, 지난 갱신 이후 합계 |
| 12·13 (버전 2) | 받은 패킷·받은 바이트 | 목적지에서 출발지로, 지난 갱신 이후 합계 |

바이트는 패킷 헤더와 페이로드를 합친 값입니다[2]. `B` 줄은 통계 칸이 비어 `,,,,` 로 끝납니다[2].

### VNet 흐름 로그 레코드

| 필드 | 뜻 |
|---|---|
| `time` | 이벤트를 기록한 UTC 시각[1] |
| `flowLogVersion` | 흐름 로그 버전. 문서 예시는 4[1] |
| `flowLogGUID` | 흐름 로그 리소스의 GUID[1] |
| `macAddress` | 흐름을 잡은 인터페이스의 MAC 주소[1] |
| `category`, `operationName` | 둘 다 늘 `FlowLogFlowEvent`[1] |
| `flowLogResourceID` | 흐름 로그 리소스 ID[1] |
| `targetResourceID` | 흐름 로그를 건 대상(가상 네트워크 등)의 리소스 ID[1] |
| `flowRecords.flows[].aclID` | 흐름을 평가한 NSG 또는 Virtual Network Manager 의 식별자[1] |
| `flowRecords.flows[].flowGroups[].rule` | 허용하거나 거부한 규칙 이름[1] |
| `flowRecords.flows[].flowGroups[].flowTuples[]` | 쉼표로 가른 흐름 튜플 문자열[1] |

튜플은 13칸이고 NSG 버전 2 와 순서가 다릅니다[1].

| 칸 | 뜻 | 값 |
|---|---|---|
| 1 | 흐름 시각 | UNIX epoch |
| 2·3 | 출발지 IP·목적지 IP | |
| 4·5 | 출발지 포트·목적지 포트 | |
| 6 | 프로토콜 | IANA 번호(6 은 TCP) |
| 7 | 방향 | `I` 들어옴, `O` 나감 |
| 8 | 흐름 상태 | `B` 시작, `C` 계속(5분 간격 통계), `E` 끝, `D` 거부 |
| 9 | 암호화 상태 | 아래 표 |
| 10~13 | 보낸 패킷·보낸 바이트·받은 패킷·받은 바이트 | 지난 갱신 이후 합계 |

VNet 흐름 로그에는 허용·거부 칸이 따로 없고, 흐름 상태 `D` 가 거부를 뜻합니다[1]. 암호화 상태는 기본값이 `NX`(암호화 안 됨)이고, `X` 는 플랫폼이 연결을 암호화한 경우입니다[1]. 나머지 `NX_HW_NOT_SUPPORTED`·`NX_SW_NOT_READY`·`NX_NOT_ACCEPTED`·`NX_NOT_SUPPORTED`·`NX_LOCAL_DST`·`NX_FALLBACK` 은 암호화를 설정했지만 하드웨어·소프트웨어·정책·같은 호스트 같은 이유로 암호화하지 않았거나 패킷을 버린 경우를 가립니다[1]. 암호화 때문에 거부한 흐름은 `aclID` 와 `rule` 이 `unspecified` 로 나옵니다[1].

플랫폼 규칙 (platform rule) 으로 적힌 흐름은 사용자가 만든 규칙이 아니라 Azure 플랫폼이 스스로 처리한 트래픽입니다[1]. 부하 분산 연결을 다시 만들 때나 응답 경로처럼 규칙 평가가 필요 없는 경우에는 평범한 업무 트래픽도 플랫폼 규칙 아래 나올 수 있습니다[1].

아래는 VNet 흐름 로그 레코드의 모양을 보여 주는 만든 예시입니다. 구독 ID·GUID·MAC·주소·시각은 모두 지어낸 값이고, 바깥 주소는 문서용 IP 대역을 썼습니다.

```json
{
  "records": [
    {
      "time": "2026-09-01T03:10:52.1234567Z",
      "flowLogVersion": 4,
      "flowLogGUID": "11bb11bb-cc22-dd33-ee44-55ff55ff55ff",
      "macAddress": "0022480A1B2C",
      "category": "FlowLogFlowEvent",
      "flowLogResourceID": "/SUBSCRIPTIONS/bbbb1b1b-cc2c-dd3d-ee4e-ffffff5f5f5f/RESOURCEGROUPS/NETWORKWATCHERRG/PROVIDERS/MICROSOFT.NETWORK/NETWORKWATCHERS/NETWORKWATCHER_KOREACENTRAL/FLOWLOGS/VNETFLOWLOG",
      "targetResourceID": "/subscriptions/bbbb1b1b-cc2c-dd3d-ee4e-ffffff5f5f5f/resourceGroups/rg-app/providers/Microsoft.Network/virtualNetworks/vnet-app",
      "operationName": "FlowLogFlowEvent",
      "flowRecords": {
        "flows": [
          {
            "aclID": "22cc22cc-dd33-ee44-ff55-66aa66aa66aa",
            "flowGroups": [
              {
                "rule": "DefaultRule_AllowInternetOutBound",
                "flowTuples": [
                  "1788232207412,10.0.1.4,203.0.113.40,50412,443,6,O,B,NX,0,0,0,0",
                  "1788232251880,10.0.1.4,203.0.113.40,50412,443,6,O,E,NX,1840,2412037,905,61880"
                ]
              },
              {
                "rule": "DefaultRule_DenyAllInBound",
                "flowTuples": [
                  "1788232219003,198.51.100.23,10.0.1.4,51544,22,6,I,D,NX,0,0,0,0"
                ]
              }
            ]
          }
        ]
      }
    }
  ]
}
```

첫 두 튜플은 VM(10.0.1.4) 이 203.0.113.40 의 443번 포트로 연 TCP 연결의 시작과 끝이고, 끝 줄에 VM 쪽에서 약 2.4MB 를 보낸 것으로 적혀 있습니다. 셋째 튜플은 바깥에서 22번 포트로 온 연결을 기본 규칙이 거부한 것입니다.

## 증거로서 의미

**증명하는 것.** 이 MAC 주소의 인터페이스에서 이 시각 무렵 이 5-튜플의 흐름이 있었고, 어느 NSG 규칙(VNet 흐름 로그는 Virtual Network Manager 규칙까지)이 그 흐름을 허용하거나 거부했는지를 보여 줍니다[1][2]. 버전 2 NSG 흐름 로그와 VNet 흐름 로그는 `C`·`E` 줄의 패킷·바이트로 오간 양을 보여 주고, VNet 흐름 로그는 연결이 암호화됐는지도 보여 줍니다[1][2]. 나간 쪽 바이트가 큰 흐름은 자료가 밖으로 나갔을 가능성을 가리키는 단서가 됩니다.

**증명하지 못하는 것.** 4계층 기록이라 페이로드, URL, 호스트 이름이 없습니다[1][2]. 어느 프로세스나 어느 Entra 계정이 만든 트래픽인지도 담지 않으므로, 사람과 이어 붙이려면 VM 안의 기록이나 [Entra ID 로그](../m365/entra-logs/index.md) 가 필요합니다. 프라이빗 엔드포인트 (private endpoint) 자체에서는 기록하지 않고, 출발지 VM 쪽에서 목적지 IP 가 프라이빗 엔드포인트 주소인 흐름으로만 남습니다[1][2]. ExpressRoute 게이트웨이 서브넷에 흐름 로그를 걸면 VM 에서 ExpressRoute 회선으로 나간 흐름이 빠질 수 있습니다[1][2]. Container Instances, Container Apps, Logic Apps, Functions, App Service, DNS Private Resolver, MariaDB·MySQL·PostgreSQL, SQL Managed Instance, NetApp Files, Power Platform 은 두 흐름 로그를 다 지원하지 않습니다[1][2]. 그래서 흐름 로그에 없다고 그 통신이 없었다고 쓰면 안 됩니다.

공인 IP 가 없는 VM 에도 인터넷 주소에서 들어온 흐름이 찍힐 수 있습니다[2]. 기본 SNAT 로 받은 포트 범위로 향한 흐름이 기록된 것이고, Azure 는 이 흐름을 VM 까지 들이지 않습니다[2]. 이런 줄을 "바깥에서 접속에 성공했다" 로 읽지 않습니다.

보고서에는 "2026-09-01 03:10 UTC 무렵 MAC 0022480A1B2C 인터페이스(10.0.1.4)에서 203.0.113.40:443 으로 나간 TCP 흐름이 기본 아웃바운드 규칙으로 허용됐고, 이 흐름에서 VM 쪽이 약 2.4MB 를 보낸 기록이 있다" 처럼 레코드가 말하는 만큼만 씁니다(만든 예시). 문장 쓰는 법은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에서 다룹니다.

## 시각 해석

레코드의 `time` 은 ISO 8601 형식의 UTC 시각입니다[1][2]. 레코드는 1분 간격으로 모으므로 `time` 은 흐름이 일어난 시각이 아니라 그 1분치를 기록한 시각입니다[1][2]. 흐름 하나하나의 시각은 튜플 첫 칸의 UNIX epoch 값이고, 이 값도 UTC 기준입니다.

epoch 값의 자릿수는 문서 예시끼리 다릅니다. NSG 예시와 대역폭 계산 예시는 10자리 초(`1487282421`, `1708978215`)이고, VNet 흐름 로그의 예시 레코드는 13자리 밀리초(`1663146003599`)입니다[1][2]. 그래서 한 가지로 가정하지 말고 자릿수를 보고 초인지 밀리초인지 가려서 풉니다. 예를 들어 `1663146003599` 는 밀리초로 풀면 2022-09-14T09:00:03.599Z 이고, 같은 레코드의 `time` 인 2022-09-14T09:00:52Z 보다 조금 앞섭니다[1].

`C` 상태 줄은 5분 간격으로 나오므로, 오래 이어진 연결은 `B` 한 줄, `C` 여러 줄, `E` 한 줄로 나뉩니다[1][2]. `C`·`E` 줄의 숫자는 앞 튜플 이후의 합계라서, 연결 하나의 전체 양은 `C`·`E` 줄을 더해서 구합니다[1][2]. 문서의 대역폭 예시는 패킷 1,021 + 52 + 8,005 + 47 = 9,125개, 바이트 588,096 + 29,952 + 4,610,880 + 27,072 = 5,256,000 으로 계산합니다[1][2].

기록이 Storage 에 나타나는 시각은 따로 있습니다. 한 시간짜리 블롭에 몇 분마다 새 블록이 덧붙고(VNet 흐름 로그는 1분 간격)[1][4], NSG 흐름 로그를 처음 켜면 Storage 에 보이기까지 최대 5분이 걸립니다[2]. 블롭 경로의 `y=`·`m=`·`d=`·`h=` 는 블롭이 맡은 시간대를 가리키므로, 경계 시각 근처의 흐름은 앞뒤 블롭을 함께 봅니다. 여러 로그의 시각을 맞추는 법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 과 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

- **NSG 두 겹.** NSG 가 서브넷과 인터페이스 양쪽에 붙어 있으면 규칙 처리 순서가 플랫폼 상태에 따라 달라지고, 흐름은 마지막으로 처리한 NSG 에 기록됩니다[2]. 거부 규칙은 거부한 NSG 가 기록하고 처리를 멈추며, 허용 규칙은 마지막으로 허용한 NSG 가 기록합니다[2]. 그래서 한쪽 NSG 의 흐름 로그만 보고 "기록이 없다" 고 쓰지 않고 양쪽을 다 봅니다. VM 에 인터페이스가 여러 개면 인터페이스마다 켜야 하고, AKS 클러스터 서브넷에는 AKS 가 기본 NSG 를 붙입니다[2].
- **상태 없는 인바운드 TCP.** NSG 의 기본이 아닌 인바운드 TCP 규칙은 플랫폼 제약으로 상태 없이 동작해서, 이런 흐름은 바이트·패킷 수를 기록하지 않아 NSG 흐름 로그의 바이트·패킷 수가 실제와 다를 수 있습니다[2]. 가상 네트워크의 `FlowTimeoutInMinutes` 가 null 이 아닌 값으로 설정돼 있으면 이 차이가 생기지 않습니다[2].
- **`B` 줄의 통계 칸.** 문서의 VNet 예시 레코드는 `B`·`D` 줄 통계를 `0,0,0,0` 으로, 대역폭 예시는 `B` 줄을 `,,,,` 로 적습니다[1]. 파서는 두 모양을 다 받아야 합니다.
- **기록이 멈춘 구간.** Storage 계정의 액세스 키(NSG 흐름 로그)나 고객 관리 키(VNet 흐름 로그)를 바꾸거나 돌리면 흐름 로그가 멈추고, 흐름 로그를 껐다가 다시 켜야 되살아납니다[1][2]. 트래픽이 없으면 파일도 생기지 않습니다[2]. 트래픽이 많은 VM 은 NSG 흐름 로그 기록에 실패할 수 있습니다[2]. 기록 공백은 이런 원인과 [Storage 계정 기록](storage-logs.md) 의 키 작업 시각을 맞춰 보고 판단합니다.
- **블롭을 건드리면 그 시간이 깨짐.** VNet 흐름 로그를 쓰는 동안 블롭을 고치거나 덮어쓰거나 지우면 그 시간 블롭에 대한 이후 쓰기가 모두 실패할 수 있습니다[1]. 수집할 때는 쓰는 중인 블롭을 고치지 말고 읽기만 합니다.
- **지우기.** 흐름 로그 리소스를 만들고 지우는 작업은 `Microsoft.Network/networkWatchers/flowLogs/write`·`Microsoft.Network/networkWatchers/flowLogs/delete` 권한 작업이고, 대상 리소스에 흐름 로그를 설정하는 작업은 `Microsoft.Network/networkWatchers/configureFlowLog/action` 입니다[7]. 이런 관리 작업은 [활동 로그](activity-log.md) 에서 찾습니다. 흐름 로그 리소스를 지워도 Storage 데이터는 남으므로[6], 기록 자체를 없앴는지는 Storage 쪽 삭제 기록에서 따로 확인합니다. 조사 흐름은 [로그를 끄거나 지웠나](../../04-scenarios/infrastructure/log-tampering.md) 에서 다룹니다.
- **수집 행위도 기록을 남김.** 블록을 읽는 Microsoft 문서의 PowerShell 함수는 `Get-AzStorageAccountKey` 로 계정 키를 받아 접근합니다[4]. 이렇게 모으면 조사관의 키 조회와 블롭 읽기가 [활동 로그](activity-log.md) 와 [Storage 계정 기록](storage-logs.md) 에 남을 수 있으므로, 수집 시각과 방법을 따로 적어 둡니다.
- **도구의 범위.** Untitled Goose Tool 의 `nsg_flow_logs` 옵션은 `insights-logs-networksecuritygroupflowevent` 컨테이너만 받고 `insights-logs-flowlogflowevent` 컨테이너는 받지 않습니다[9][10]. 이 도구는 블롭의 `last_modified` 로 날짜 범위를 거르고, 범위를 주지 않으면 최근 2년을 받으며, 받은 블롭의 `records` 를 풀어 한 줄에 레코드 하나씩 씁니다[9].

## 직접 분석해 보기

**원본 바이트 확인.** 흐름 로그 블롭은 블록 블롭 (block blob) 이고, 블록이 적어도 둘 있습니다[4]. 첫 블록은 12바이트로 JSON 을 여는 괄호를 담고, 마지막 블록은 2바이트로 닫는 괄호를 담으며, 새 항목은 마지막 블록 바로 앞에 붙습니다[4]. 여는 부분이 `{"records":[` 라면 정확히 12바이트이고, 헥스로는 아래와 같습니다(명세로 만든 예시).

```text
00000000: 7b22 7265 636f 7264 7322 3a5b            {"records":[
```

받은 `PT1H.json` 의 처음과 끝이 이 모양인지 확인하면, 블롭이 잘리지 않고 온전히 받아졌는지 가릴 수 있습니다. 새 항목은 닫는 블록 앞에 들어가므로 쓰는 중인 블롭도 닫는 괄호로 끝나고, 블록 사이 이음새 모양은 검체에서 확인합니다.

```bash
xxd -l 12 PT1H.json
tail -c 2 PT1H.json | xxd
jq -e '.records | length' PT1H.json
```

**튜플을 한 줄씩 펼치기.** 레코드 안의 튜플을 규칙·MAC 과 함께 한 줄로 펼치면 grep·awk 로 다루기 쉽습니다. NSG 흐름 로그는 아래처럼 펼칩니다.

```bash
jq -r '.records[] | .time as $t | .properties.flows[] | .rule as $r
  | .flows[] | .mac as $m | .flowTuples[] | [$t, $r, $m, .] | @tsv' PT1H.json
```

VNet 흐름 로그는 경로가 다릅니다.

```bash
jq -r '.records[] | .time as $t | .macAddress as $m | .flowRecords.flows[] | .aclID as $a
  | .flowGroups[] | .rule as $r | .flowTuples[] | [$t, $m, $a, $r, .] | @tsv' PT1H.json
```

튜플 첫 칸을 자릿수에 따라 초나 밀리초로 풀어 UTC 로 바꾸고, VNet 튜플에서 VM 이 보낸 바이트를 목적지별로 더하는 예입니다. 마지막 칸이 튜플 문자열이라는 전제로 씁니다.

```bash
jq -r '.records[].flowRecords.flows[].flowGroups[].flowTuples[]' PT1H.json |
awk -F, '{ts=$1; if (length(ts)>=13) ts=int(ts/1000);
  cmd="date -u -d @" ts " +%FT%TZ"; cmd | getline t; close(cmd);
  print t, $2 ":" $4, "->", $3 ":" $5, "p=" $6, $7, $8, $9, $10, $11, $12, $13}'

jq -r '.records[].flowRecords.flows[].flowGroups[].flowTuples[]' *.json |
awk -F, '$7=="O" && ($8=="C" || $8=="E") {b[$3]+=$11} END {for (d in b) print b[d], d}' | sort -rn | head
```

NSG 버전 2 튜플에 같은 계산을 하려면 방향이 7번째, 흐름 상태가 9번째, 보낸 바이트가 11번째 칸이므로 칸 번호를 바꿉니다.

**공개 도구로 받기.** Untitled Goose Tool 설정 파일의 `[azure]` 절에서 `nsg_flow_logs=True` 로 두면 구독 안의 Storage 계정을 모두 훑어 NSG 흐름 로그 컨테이너를 받습니다[9][10]. VNet 흐름 로그는 `az storage blob download`·`Get-AzStorageBlobContent`·Storage Explorer 로 `insights-logs-flowlogflowevent` 컨테이너에서 받습니다[6]. 한 시간 블롭 전체를 받지 않고 새로 붙은 블록만 읽으려면 Microsoft 문서의 `Get-VNetFlowLogCloudBlockBlob`·`Get-NSGFlowLogCloudBlockBlob` 함수로 블록 목록을 받아 읽습니다[4]. 수집 순서 전반은 [AWS·Azure·GCP 수집](../../03-techniques/acquisition/iaas-collection.md) 과 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 에서 다룹니다.

## 교차 검증

- [활동 로그](activity-log.md) — 흐름 로그 리소스를 만들거나 지운 작업, NSG 규칙을 바꾼 작업을 찾습니다. SigmaHQ 규칙은 `operationName` 이 `MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/SECURITYRULES/WRITE`·`MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/SECURITYRULES/DELETE`·`MICROSOFT.NETWORK/NETWORKSECURITYGROUPS/WRITE` 등인 레코드를 NSG 설정 변경으로 봅니다[8]. 규칙을 바꾼 시각 전후로 흐름 로그의 허용·거부가 바뀌었는지 맞춰 봅니다.
- [Storage 계정 기록](storage-logs.md) — 흐름 로그가 쌓이는 Storage 계정에서 키를 돌리거나 블롭을 지운 기록을 찾아 공백 구간을 설명합니다. 흐름 로그에서 Storage 주소로 큰 흐름이 보이면 같은 시간대의 Storage 요청 기록에서 어느 블롭이었는지 찾습니다.
- [Azure 가상 머신](azure-vm.md) — MAC 주소와 사설 IP 로 VM 을 찾고, VM 안의 기록은 [클라우드 가상 머신 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/cloud-vm.html) 으로 확보해 [인증 로그](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/auth-log.html) 의 SSH 로그인과 맞춰 봅니다.
- [리소스 로그와 진단 설정](resource-logs.md) — 흐름 로그와 별개로 NSG·Application Gateway 같은 리소스가 남기는 진단 로그를 함께 봅니다.
- [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) — 튜플의 바깥 주소를 해석할 때 봅니다.
- [VPC 흐름 로그 (AWS)](../aws/vpc-flow-logs.md), [VPC 흐름 로그 (Google Cloud)](../gcp/vpc-flow-logs.md) — 다른 클라우드의 같은 역할을 하는 기록입니다.
- [클라우드 저장소에서 자료를 빼 갔나](../../04-scenarios/data-leak/storage-exfiltration.md), [채굴용 자원을 만들었나](../../04-scenarios/infrastructure/cryptomining.md) — 이 쪽의 기록을 조사 흐름으로 묶습니다.

## 실습

Microsoft 문서의 예시 레코드[1][2]와 위의 만든 예시로 풀어 봅니다.

1. NSG 버전 1 예시에서 `UserRule_default-allow-rdp` 로 허용된 튜플을 모두 골라 UTC 시각으로 풀고, 레코드 `time` 과 몇 초 차이 나는지 적어 봅니다[2].
2. NSG 버전 2 예시의 `B`·`C`·`E` 줄을 가려, 통계가 있는 줄과 없는 줄이 무엇이고 연결 하나의 전체 바이트를 어떻게 구하는지 적어 봅니다[2].
3. VNet 예시 레코드에서 `D` 상태 튜플의 목적지 포트를 모아, 어느 규칙이 어느 포트를 막았는지 표로 만들어 봅니다[1].
4. 위 만든 예시의 첫 튜플 시각을 밀리초로 풀고, 같은 값을 초로 잘못 풀면 어느 해가 나오는지 확인해 봅니다.
5. 공인 IP 가 없는 VM 의 NSG 흐름 로그에 인터넷 주소에서 들어온 줄이 있을 때, 이 줄을 보고서에 어떻게 적어야 하는지 써 봅니다[2].
6. 실제 구독에서는 Network Watcher 의 흐름 로그 목록을 받아 어느 대상에 어느 종류가 켜져 있고 어느 Storage 계정에 몇 일 보관하는지 표로 만들고, 사고 시각에 기록이 있을 VM 과 없을 VM 을 나눠 봅니다.

## 참고 문헌

1. Microsoft, "Virtual network flow logs", Azure Network Watcher documentation (ms.date 2026-02-10). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/network-watcher/vnet-flow-logs-overview.md
2. Microsoft, "Flow logging for network security groups", Azure Network Watcher documentation (ms.date 2025-12-18). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/network-watcher/nsg-flow-logs-overview.md
3. Microsoft Learn, "Flow logging for network security groups" (Last updated 2026-02-10). https://learn.microsoft.com/en-us/azure/network-watcher/nsg-flow-logs-overview
4. Microsoft, "Read flow logs", Azure Network Watcher documentation (ms.date 2025-08-20). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/network-watcher/flow-logs-read.md
5. Microsoft, "Migrate from network security group flow logs to virtual network flow logs", Azure Network Watcher documentation (ms.date 2026-02-25). https://github.com/MicrosoftDocs/azure-docs/blob/main/articles/network-watcher/nsg-flow-logs-migrate.md
6. Microsoft Learn, "Create, change, enable, disable, or delete virtual network flow logs" (Last updated 2026-01-22). https://learn.microsoft.com/en-us/azure/network-watcher/vnet-flow-logs-manage
7. Microsoft Learn, "Azure permissions for Networking" (Last updated 2026-07-01). https://learn.microsoft.com/en-us/azure/role-based-access-control/permissions/networking
8. SigmaHQ, azure_network_security_modified_or_deleted.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/activity_logs/azure_network_security_modified_or_deleted.yml
9. CISA, Untitled Goose Tool (goosey/azure_dumper.py). https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/azure_dumper.py
10. CISA, Untitled Goose Tool (README.md). https://github.com/cisagov/untitledgoosetool/blob/develop/README.md
