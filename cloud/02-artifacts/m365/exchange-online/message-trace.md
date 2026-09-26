---
title: "메시지 추적"
parent: "Exchange Online"
grand_parent: "아티팩트 · Microsoft 365"
nav_order: 240
---

# 메시지 추적 (Message Trace)

Exchange Online 이 메일 한 통을 받고, 걸러 내고, 배달하거나 실패한 과정을 최대 90일 동안 조회할 수 있는 서비스 쪽 메일 흐름 기록입니다.

## 무엇을 기록하나 · 왜 생기나

메시지 추적은 Microsoft 365 조직을 드나드는 메일이 전송 과정에서 거친 일을 기록합니다. 서비스가 메일을 받았는지, 거부했는지, 미뤘는지, 배달했는지를 알 수 있고, 최종 상태에 이르기 전에 어떤 처리를 거쳤는지도 볼 수 있습니다[4]. 사용자가 메일함에서 한 일은 여기에 남지 않고 [메일함 감사](mailbox-auditing.md)에 남으므로, 메시지 추적은 "서버가 메일을 어떻게 옮겼나" 를 보여 주는 기록이라고 보면 됩니다.

조사에서는 주로 세 가지 질문에 씁니다. 특정 계정이 어느 시간대에 어떤 주소로 메일을 보냈는지, 외부에서 들어온 피싱 메일이 누구에게 배달되거나 격리됐는지, [받은편지함 규칙과 전달](inbox-rules.md) 설정이 실제로 메일을 밖으로 내보냈는지입니다.

## 조회 경로와 범위

메시지 추적은 Exchange 관리 센터(EAC)와 Exchange Online PowerShell 로 조회합니다. 조회 경로마다 한 번에 볼 수 있는 기간과 건수가 다릅니다. 아래 값은 2026년 9월 문서 기준입니다(EAC 문서 2026-05-27 갱신).

| 조회 경로 | 조회 가능 기간 | 한 번에 조회하는 기간 | 결과 건수 | 결과 형태 |
|---|---|---|---|---|
| `Get-MessageTraceV2` | 최근 90일(매개변수가 없으면 최근 48시간) | 10일 | 기본 1,000건, 최대 5,000건 | PowerShell 개체[1] |
| `Get-MessageTraceDetailV2` | 최근 90일(90일보다 오래되면 오류) | 10일 | 메시지 한 통의 이벤트 | PowerShell 개체[2] |
| `Start-HistoricalSearch` | 1~4시간 전(환경마다 다름)부터 90일 전까지 | 요청 범위 | CSV 한 파일에 100,000행 | 내려받는 CSV[3] |
| EAC Summary report | 기본 2일, 최대 90일 | 10일 이하 | 20,000건 | 화면 목록(바로 나옴)[4] |
| EAC Enhanced summary report | 최대 90일 | 10일 초과도 가능 | 100,000건 | 내려받는 CSV[4] |
| EAC Extended report | 최대 90일 | 10일 초과도 가능 | 1,000건 | 내려받는 CSV[4] |

EAC 에서는 **메일 흐름 > 메시지 추적**(`https://admin.exchange.microsoft.com/#/messagetrace`)에서 조회를 시작합니다. 권한은 Exchange Online 의 Organization Management 역할 그룹이나 Entra 의 Exchange Administrator 역할이 있으면 됩니다[4].

기간을 10일보다 조금이라도 길게 잡으면 결과는 내려받는 CSV(Enhanced summary 나 Extended)로만 나오고, 보관된 추적 데이터로 만들기 때문에 몇 시간이 걸릴 수 있습니다[4]. Enhanced summary 와 Extended 는 기간과 상관없이 보낸 사람·받는 사람·Message ID 중 하나를 지정해야 하고, CSV 한 파일은 800MB 를 넘을 수 없습니다[4]. `Start-HistoricalSearch` 는 24시간에 250건까지 요청할 수 있고 취소한 요청도 이 한도에 들어갑니다[3]. 보고서 종류(`ReportType`)는 `MessageTrace`, `MessageTraceDetail` 말고도 `TransportRule`, `DLP`, `SPAM`, `Spoof` 등이 있습니다[3].

PowerShell 로는 테넌트마다 5분에 100번까지 조회를 요청할 수 있습니다[1][2][4]. `Get-MessageTraceV2` 를 쓰려면 Exchange Online PowerShell V3 모듈 3.7.0 이상이 필요합니다[4].

## 구조

### 식별자 두 가지

메시지 추적에서 메일을 가리키는 값은 둘입니다[4].

| 값 | 어디서 오나 | 성질 |
|---|---|---|
| Message ID | 메일 머리글의 `Message-ID` 필드(Client ID 라고도 함) | 메일이 사는 동안 바뀌지 않습니다. Microsoft 365·Exchange 에서 만든 메일은 `<GUID@ServerFQDN>` 형식이고 다른 메일 시스템은 형식이 다릅니다. 조회할 때 꺾쇠까지 넣어야 합니다. |
| Network Message ID | 서비스가 붙이는 값(`MessageTraceId` 매개변수가 이 값을 씁니다) | 메일 한 통의 특정 인스턴스를 가리킵니다. 메일이 여러 사본으로 갈라질 때(bifurcation) 값이 어떻게 되는지는 공식 문서끼리도 엇갈립니다. EAC 문서의 한 문단은 사본마다 값이 다르다고 하고, 같은 문서의 비교표·Enhanced summary 열 설명과 `Start-HistoricalSearch` 의 `NetworkMessageId` 설명은 갈라진 사본과 배포 그룹 펼침에 걸쳐 값이 유지된다고 합니다[3][4]. 검체에서 같은 메일의 사본끼리 값을 비교해 확인합니다. 머리글 `X-MS-Exchange-Organization-Network-Message-Id`, `X-MS-Office365-Filtering-Correlation-Id`, `X-MS-Exchange-CrossTenant-Network-Message-Id` 에서 찾을 수 있습니다. |

`MessageTraceId` 는 서비스가 처리한 메일마다 만드는 GUID 값입니다[1]. 받는 사람이 1,000명을 넘는 메일은 `MessageTraceId` 를 지정해야 결과를 모두 받을 수 있습니다[1][4].

### 요약 결과

EAC Summary report 는 날짜(서비스가 메일을 받은 시각), 보낸 사람, 받는 사람, 제목(앞 256자), 상태를 보여 줍니다[4]. 받는 사람이 여럿이면 받는 사람마다 한 줄씩 나오고, 배포 그룹이면 그룹이 첫 줄에 오고 구성원이 한 줄씩 이어집니다[4].

상태 값은 다음과 같습니다[1][4].

| 상태 | 뜻 |
|---|---|
| Delivered | 목적지에 배달됨 |
| Expanded | 배포 그룹이 구성원으로 펼쳐짐(그룹 자체로는 배달 없음) |
| Failed | 배달을 시도했으나 실패 |
| Pending | 배달 중이거나, 미뤄져서 다시 시도하는 중 |
| Quarantined | 격리됨(스팸·대량 메일·피싱) |
| FilteredAsSpam | 스팸으로 판정돼 거부·차단됨(격리 아님) |
| GettingStatus | 방금 받아서 아직 상태 정보가 없음 |
| Recalled | 회수됨(EAC 필터에만 나옴) |

EAC 에서는 Pending, Quarantined, Filtered as spam 을 10일 미만 검색에서만 고를 수 있습니다[4].

### 상세 이벤트

메시지 한 통의 처리 단계는 `Get-MessageTraceDetailV2` 나 EAC 상세 창의 이벤트로 봅니다. 문제없이 배달된 메일 한 통도 이벤트를 여러 개 남깁니다[4].

| 이벤트 | 뜻 |
|---|---|
| RECEIVE | 서비스가 메일을 받음 |
| SEND | 서비스가 메일을 내보냄 |
| DELIVER | 메일함에 배달함 |
| FAIL | 배달 실패 |
| EXPAND | 배포 그룹을 펼침 |
| TRANSFER | 콘텐츠 변환·받는 사람 수 제한·에이전트 때문에 받는 사람을 갈라진 사본으로 옮김 |
| DEFER | 배달을 미룸(나중에 다시 시도) |
| RESOLVE | Active Directory 조회로 받는 사람 주소를 바꿈(원래 주소가 따로 한 줄로 남음) |

EAC 상세 창에는 DLP 규칙 일치, 서버 쪽 민감도 레이블 이벤트도 나옵니다[4]. 상세 창의 From IP 는 메일을 보낸 컴퓨터의 IP 이고 Exchange Online 에서 나가는 메일이면 비어 있으며, To IP 는 서비스가 배달을 시도한 주소이고 Exchange Online 으로 들어오는 메일이면 비어 있습니다[4]. `Get-MessageTraceV2` 의 `FromIP` 는 들어오는 메일이면 보낸 SMTP 서버의 공인 IP 입니다[1].

### 내려받는 보고서의 열

Enhanced summary report CSV 에는 다음 열이 있습니다[4].

| 열 | 내용 |
|---|---|
| `origin_timestamp` | 서비스가 메일을 처음 받은 시각(Enhanced summary 에만) |
| `sender_address` | 보낸 사람 주소 |
| `Recipient_status` | 받는 사람별 상태. `주소##Receive, Deliver` 모양 |
| `message_subject` | 제목 앞 256자 |
| `total_bytes` | 첨부를 포함한 크기(바이트) |
| `message_id` | Message ID |
| `network_message_id` | Network Message ID |
| `original_client_ip` | 보낸 쪽 SMTP 서버 IP |
| `directionality` | 들어온 메일인지 나간 메일인지 |
| `connector_id` | 들어오거나 나간 커넥터 이름 |
| `delivery_priority` | 높음·보통·낮음 우선순위(Enhanced summary 에만) |

Extended report 에는 이벤트 단위의 열이 더 붙습니다. `client_ip`·`client_hostname`(메일을 제출한 서버나 클라이언트), `server_ip`·`server_hostname`, `source`(이벤트를 남긴 구성 요소, 예: `AGENT`, `MAILBOXRULE`, `SMTP`), `source_context`, `event_id`(위 이벤트 값), `internal_message_id`, `recipient_address`(세미콜론으로 구분), `recipient_count`, `related_recipient_address`(EXPAND·REDIRECT·RESOLVE 에서 관련 받는 사람), `reference`, `return_path`, `message_info`, `tenant_id`, `original_server_ip`, `custom_data` 입니다[4].

조사에서 눈여겨볼 열은 셋입니다. `source` 가 `MAILBOXRULE` 인 행의 `reference` 에는 받은편지함 규칙이 새 메일을 만들게 한 원래 수신 메일의 `internal_message_id` 가 들어가고, RECEIVE 행의 `reference` 에는 규칙 같은 다른 처리가 만든 메일이면 관련 메일의 `message_id` 가 들어갈 수 있습니다[4]. `return_path` 는 SMTP `MAIL FROM` 주소이고 비어 있지 않지만 널 발신자 `<>` 일 수 있습니다[4]. `custom_data` 는 `S:SFA`(스팸 필터), `S:AMA`(악성 코드 필터), `S:TRA`(메일 흐름 규칙) 로 시작하는 에이전트별 처리 내용을 담습니다[4].

## 증거로서 의미

**증명하는 것**

- 서비스가 그 시각에 그 보낸 사람·받는 사람 사이의 메일을 받았고, 배달·실패·격리·스팸 차단 중 어떤 결과로 처리했는지[4].
- 메일이 배포 그룹 펼침, 주소 바꿈, 받은편지함 규칙, 메일 흐름 규칙을 거쳤는지(Extended report 의 `source`·`reference`·`custom_data`)[4].
- 메일을 제출한 클라이언트나 보낸 SMTP 서버의 IP(보관 조건은 아래 함정 참고)[4].

**증명하지 못하는 것**

- 본문과 첨부 내용. 메시지 추적에는 제목 앞 256자와 크기까지만 남습니다[4].
- 받는 사람이 메일을 열었거나 읽었는지. 메일함 안의 접근은 [메일함 감사와 MailItemsAccessed](mailbox-auditing.md)에서 봅니다.
- 보낸 사람 계정을 실제로 누가 조작했는지. 보낸 사람 주소는 계정을 가리킬 뿐이므로 로그인 기록과 함께 봐야 합니다.

보고서에는 "2026-09-01 02:14 UTC 에 계정 a@contoso.com 을 보낸 사람으로 하는 메일이 외부 주소로 배달된 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

PowerShell cmdlet 이 내놓는 시각은 UTC 이고, `-StartDate`·`-EndDate` 에 넣은 시각 형식과 다를 수 있습니다[1]. EAC 는 로그인한 관리자의 Exchange 계정 설정 시간대를 기본으로 쓰고, 사용자 지정 시간 범위에서 고른 시간대가 조회 입력과 결과 둘 다에 적용됩니다[4]. 그래서 EAC 화면에서 복사한 시각과 PowerShell 결과를 합칠 때는 시간대부터 맞춥니다.

Summary report 의 날짜와 `origin_timestamp` 는 서비스가 메일을 (처음) 받은 시각입니다[4]. Extended report 의 `message_info` 에는 DELIVER·SEND 이벤트에 한해 메일이 Exchange Online 조직에 처음 들어온 시각이 ISO 8601 UTC(`yyyy-MM-ddThh:mm:ss.fffZ`)로 들어가고, `custom_data` 의 `S:TRA` 항목에 있는 `St=` 는 메일 흐름 규칙이 일치한 UTC 시각입니다[4].

기록이 늦게 보이는 구간도 있습니다. 배달 상태는 실제보다 5~10분 늦게 반영될 수 있고, Enhanced summary·Extended 보고서에는 최근 24시간 데이터가 보통 없으며, `Start-HistoricalSearch` 는 1~4시간 이상 지난 메일부터 조회됩니다[3][4]. `Get-MessageTraceV2` 결과는 받은 시각 내림차순, 같은 시각 안에서는 받는 사람 주소 오름차순으로 정렬됩니다[4].

## 함정과 한계

- **90일이 끝입니다.** 90일이 지난 메일 흐름은 어느 경로로도 조회되지 않습니다[1][2][4]. 사고를 늦게 알았다면 가장 먼저 내려받아 둡니다.
- **한 번에 10일, 최대 5,000건입니다.** `Get-MessageTraceV2` 는 페이지 넘김을 지원하지 않습니다. 앞 결과의 마지막 행 `Received` 값을 다음 조회의 `-EndDate` 로, `RecipientAddress` 값을 `-StartingRecipientAddress` 로 넘겨 이어 받습니다[1][4]. 이 처리를 빠뜨리면 결과가 5,000건에서 잘린 줄 모르고 넘어갑니다.
- **클라이언트 IP 는 10일만 남습니다.** 보낸 쪽 클라이언트 IP 는 10일 동안, 그리고 Enhanced summary·Extended 보고서에서만 볼 수 있습니다[4].
- **배포 그룹으로 조회하면 빠질 수 있습니다.** `Start-HistoricalSearch` 에 배포 그룹을 지정하면 일부 메일이 결과에 나오지 않을 수 있어 개별 받는 사람으로 조회합니다[3].
- **한 통이 여러 행입니다.** 배포 그룹 펼침, 전달, 메일 흐름 규칙이 끼면 한 통의 메일도 여러 기록을 남깁니다[4]. 행 수를 보낸 메일 수로 세지 않고 Message ID 로 묶습니다. 같은 Message ID 를 공유하는 기록은 EAC 의 "관련 항목 찾기(Find related)" 로 모을 수 있습니다[4].
- **아웃바운드 보호 서버 IP 는 없습니다.** 클라우드에서 나가는 메일을 보호하는 서버의 IP 는 SPF 레코드에는 들어 있지만 어떤 메시지 추적 보고서에도 나오지 않습니다. 보고서가 그 서버를 거치기 전에 만들어지기 때문입니다[4].
- **Message ID 는 보낸 쪽이 정합니다.** 고유해야 하는 값이지만 모든 메일 시스템이 이를 지키지는 않고, 외부에서 온 메일에 `Message-ID` 필드가 없거나 비어 있으면 서비스가 임의 값을 붙입니다[4]. 같은 Message ID 가 여러 메일에 나오면 Network Message ID 로 나눕니다.

## 직접 분석해 보기

### PowerShell 로 한 번

보낸 사람과 기간을 좁혀 요약을 받고, 관심 있는 메일은 상세 이벤트까지 봅니다. 아래 주소·ID 는 만든 예시입니다.

```powershell
# 10일 이하 구간, 최대 5,000건
$mt = Get-MessageTraceV2 -SenderAddress a@contoso.com `
      -StartDate '2026-09-01T00:00:00Z' -EndDate '2026-09-08T00:00:00Z' -ResultSize 5000

# 5,000건이 꽉 찼으면 마지막 행을 이어 받기 기준으로 넘긴다
$next = Get-MessageTraceV2 -SenderAddress a@contoso.com `
      -StartDate '2026-09-01T00:00:00Z' -EndDate $mt[-1].Received.ToString("O") `
      -StartingRecipientAddress $mt[-1].RecipientAddress -ResultSize 5000

# 한 통의 처리 단계
Get-MessageTraceV2 -MessageTraceId 0f3c2a1e-5b6d-4e7f-8a9b-0c1d2e3f4a5b `
      -StartDate '2026-09-01T00:00:00Z' -EndDate '2026-09-08T00:00:00Z' | Get-MessageTraceDetailV2
```

`Get-MessageTraceV2` 결과를 파이프로 `Get-MessageTraceDetailV2` 에 넘기면 그 메일의 상세 이벤트를 받습니다[4]. 10일을 넘는 기간은 `Start-HistoricalSearch -ReportType MessageTrace` 로 요청하고, 이때 `MessageID`·`RecipientAddress`·`SenderAddress` 중 하나를 함께 지정해야 합니다[3].

### 공개 도구로 한 번

Microsoft-Extractor-Suite 의 `Get-MessageTraceLog` 는 `Get-MessageTraceV2` 를 부르고, 기간을 10일씩 잘라 조회하면서 한 번에 5,000건씩 받고, 결과가 5,000건이면 마지막 행의 `Received`·`RecipientAddress` 로 이어 받습니다[6]. 시작일을 주지 않으면 90일 전부터 조회하고, 결과는 `Output\MessageTrace\` 아래 CSV 로 저장합니다[6]. Hawk 의 `Get-HawkUserMessageTrace` 는 V2 가 아닌 `Get-MessageTrace -Sender` 로 한 사용자가 보낸 메일을 받아 CSV·JSON 으로 저장합니다[7]. 여러 도구를 함께 쓸 때는 어느 cmdlet 으로 받았는지 결과마다 적어 둡니다. 수집 도구 전반은 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md)에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 연결 값 | 알려 주는 것 |
|---|---|---|
| [받은편지함 규칙과 전달](inbox-rules.md) | 보낸 사람·받는 사람, Extended 의 `MAILBOXRULE` 행 | 전달 설정이 실제로 외부 배달로 이어졌는지 |
| [메일함 감사와 MailItemsAccessed](mailbox-auditing.md) | Message ID(감사 레코드의 InternetMessageId) | 배달된 메일에 누가 메일함 안에서 접근했는지 |
| [Defender 경고와 기록](../defender-xdr.md)의 EmailEvents | `NetworkMessageId`, `InternetMessageId` | 위협 판정·배달 위치. Defender for Office 365 가 있는 조직에서만 채워집니다[5] |
| [통합 감사 로그](../unified-audit-log/index.md) | 계정·시각 | 메일을 보내기 전후의 설정 변경·로그인 |

여러 기록을 한 줄로 늘어놓는 방법은 [클라우드 타임라인](../../../03-techniques/analysis/timeline.md)을 봅니다.

## 실습

시험용 테넌트에서 다음을 해 보고 답을 찾습니다.

1. 한 사용자에게 외부 주소로 전달하는 받은편지함 규칙을 만들고 메일을 한 통 보냅니다. Summary report 에 몇 행이 나오고, Extended report 의 어느 행에서 `source` 가 `MAILBOXRULE` 인지 찾습니다.
2. 배포 그룹으로 메일을 보내고 Expanded 행과 구성원별 Delivered 행을 Message ID 하나로 묶어 봅니다.
3. 같은 구간을 EAC 와 `Get-MessageTraceV2` 로 조회하고, 두 결과의 시각이 시간대 설정에 따라 어떻게 다른지 비교합니다.
4. `-ResultSize 10` 으로 조회한 뒤 `-StartingRecipientAddress` 로 이어 받아 빠진 행이나 겹친 행이 있는지 확인합니다.

## 참고 문헌

1. Microsoft, "Get-MessageTraceV2", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-MessageTraceV2.md
2. Microsoft, "Get-MessageTraceDetailV2", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-MessageTraceDetailV2.md
3. Microsoft, "Start-HistoricalSearch", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Start-HistoricalSearch.md
4. Microsoft Learn, "Message trace in the Exchange admin center in Exchange Online" (2026-05-27 갱신). https://learn.microsoft.com/en-us/exchange/monitoring/trace-an-email-message/message-trace-modern-eac
5. Microsoft Learn, "EmailEvents" (2026-09-02 갱신). https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-emailevents-table
6. Invictus Incident Response, Microsoft-Extractor-Suite, `Scripts/Get-MessageTraceLog.ps1`. https://github.com/invictus-ir/Microsoft-Extractor-Suite
7. T0pCyber, Hawk, `Hawk/functions/User/Get-HawkUserMessageTrace.ps1`. https://github.com/T0pCyber/hawk
