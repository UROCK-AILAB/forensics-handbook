---
title: "메일 계정을 빼앗겨 송금 사기를 당했나"
parent: "시나리오 · 계정 침해"
nav_order: 730
---

# 메일 계정을 빼앗겨 송금 사기를 당했나 (BEC)

기업 메일 침해 (Business Email Compromise, BEC) 는 거래처나 임원의 메일 계정에 들어가 대화를 엿본 뒤, 계좌가 바뀌었다는 메일을 보내 돈을 다른 곳으로 보내게 하는 사기입니다. 이 쪽은 Microsoft 365 와 Google Workspace 메일 계정을 중심으로, 로그인부터 받은 편지함 규칙·전달 설정·메일 열람·보낸 메일까지 어느 기록을 어떤 순서로 보는지 다룹니다.

## 조사 질문

- 누가, 언제, 어디서 이 메일함에 로그인했나?
- 들어와서 어떤 메일에 접근했나?
- 받은 편지함 규칙 (inbox rule) 이나 전달 (forwarding) 설정을 만들어 답장을 숨기거나 메일을 밖으로 빼돌렸나?
- 이 메일함에서 사기 메일이 나갔나, 나갔다면 누구에게 언제 나갔나?
- 같은 공격이 다른 계정으로 번졌나?

송금을 지시한 메일이 이 메일함에서 나갔는지, 비슷한 도메인의 다른 메일함에서 왔는지도 먼저 가립니다. 앞의 경우가 이 쪽의 범위이고, 뒤의 경우는 받은 메일의 헤더와 메시지 추적으로 발신 경로만 확인하게 됩니다.

## 먼저 확인할 것

**현재 설정부터 건드리지 않고 받아 둡니다.** Exchange PowerShell 로 받은 편지함 규칙을 만들거나, 바꾸거나, 지우거나, 켜고 끄면 Outlook 이 꺼 둔 클라이언트 쪽 규칙과 보내는 규칙이 지워집니다[9]. 조사자가 수상한 규칙을 끄는 순간 다른 증거가 사라질 수 있으므로, 규칙·전달 설정·메일함 권한 목록을 먼저 받고 로그를 확보한 다음에 조치합니다. 확보 순서는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md), 수집 도구는 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) 에 있습니다.

**보관 기간과 라이선스를 확인합니다.** BEC 는 돈이 빠져나간 뒤에야 알아채는 경우가 많아서, 로그인 기록이 먼저 사라지기 쉽습니다. 아래 표는 2026년 9월 문서 기준이고, 서비스 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다.

| 기록 | 기본 보관·조회 범위 | 조건 |
|---|---|---|
| Entra 로그인 로그·감사 로그 | Free 7일, P1·P2 30일[7] | Free 에서 P1 으로 올려도 지난 기록은 최대 7일치만 보임[7] |
| 통합 감사 로그 (Unified Audit Log, UAL), Audit (Standard) | 2023년 10월 17일 이후 생성분 180일, 그 전 생성분 90일[5] | E5 가 아닌 사용자와 게스트의 기록도 180일[5] |
| UAL, Audit (Premium) 기본 정책 | Exchange·SharePoint·OneDrive·Entra 기록 1년[5] | 활동한 사용자에게 E5 또는 Purview Suite·E5 eDiscovery and Audit 추가 라이선스가 있을 때만[5] |
| 메시지 추적 (`Get-MessageTraceV2`) | 최근 90일, 한 번에 10일치[10] | 인자 없이 부르면 최근 48시간[10] |
| 과거 메시지 추적 (`Start-HistoricalSearch`) | 1~4시간 지난 것부터 90일까지[11] | 24시간에 250건까지 요청[11] |
| Google Workspace Gmail 로그 이벤트 | 6개월[29] | Email log search 는 30일[29] |
| Okta 시스템 로그 | 90일이 넘은 기록은 조회되지 않음[31] | |

**메일 열람 기록이 켜져 있었는지 확인합니다.** 메일 접근 기록 `MailItemsAccessed` 는 Audit (Standard) 기능이고, Office 365·Microsoft 365 E3/E5 사용자에게 기본으로 켜집니다[3]. 조직 기본값으로 메일함 감사가 켜져 있으면 `Get-Mailbox` 의 `AuditEnabled` 는 늘 `True` 로 보이므로, 기본 동작 집합이 실제로 적용됐는지는 `Get-Mailbox -Identity 메일함 | Format-List DefaultAuditSet` 로 봅니다[1]. `DefaultAuditSet` 이 비어 있으면 세 로그온 유형의 감사 동작을 모두 바꾼 메일함입니다[1].

**시각 기준을 맞춥니다.** UAL 레코드의 `CreationTime` 은 UTC 이고[4], Purview 감사 검색 화면의 날짜 범위와 결과 "Date (UTC)" 도 UTC 입니다[6]. 메시지 추적 결과도 UTC 이고, `-StartDate`·`-EndDate` 에 넣은 시간 형식과 다르게 보일 수 있습니다[10]. 피해자가 말하는 "오후 3시 송금" 은 대개 현지 시각이므로 표를 만들기 전에 한쪽으로 맞춥니다([클라우드 로그의 시각](../../01-foundations/logging/timestamps.md)).

**기록이 들어오기까지 시간이 걸립니다.** UAL 은 Exchange·SharePoint·OneDrive·Teams 기록이 보통 60~90분 뒤에 검색되지만 Microsoft 는 시간을 보장하지 않습니다[6]. Google Workspace 는 Gmail 로그 이벤트와 로그인 이벤트가 수 분, 사용자 계정 이벤트가 수십 분 걸립니다[29]. 방금 만든 규칙이 검색되지 않는다고 없는 것으로 보지 않습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 현재 규칙·전달 설정: `Get-InboxRule`, `Get-Mailbox` 전달 필드, `Get-TransportRule` | 지금 살아 있는 규칙과 전달 주소 | [Exchange Online](../../02-artifacts/m365/exchange-online/index.md) |
| 2 | 로그인 기록: Entra 로그인 로그, Google Workspace 로그인 이벤트 | 누가 언제 어느 IP·장치로 들어왔나, 세션 식별자 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [로그인 기록](../../02-artifacts/google-workspace/login-audit.md) |
| 3 | 규칙·전달 변경 기록: UAL `New-InboxRule`·`Set-InboxRule`·`UpdateInboxRules`·`Set-Mailbox`, Google Workspace `email_forwarding_out_of_domain` | 규칙과 전달이 언제 어떤 값으로 생겼나 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| 4 | 메일 접근 기록: `MailItemsAccessed` | 어느 메시지·폴더에 접근했나 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md) |
| 5 | 보낸 메일: UAL `Send`·`SendAs`·`SendOnBehalf`, 메시지 추적, Gmail 로그 | 사기 메일이 이 메일함에서 언제 누구에게 나갔나 | [Exchange Online](../../02-artifacts/m365/exchange-online/index.md), [Gmail 기록과 메일 검색](../../02-artifacts/google-workspace/gmail.md) |
| 6 | 서비스의 탐지: ID Protection 위험 탐지, Defender 경고 | 서비스가 이상한 규칙·발송을 감지했나 | [Defender 경고와 기록](../../02-artifacts/m365/defender-xdr.md) |

## 분석 흐름

1. **현재 상태를 받습니다.** `Get-InboxRule` 에는 숨긴 규칙까지 돌려주는 `-IncludeHidden` 스위치가 있습니다[8]. 도구마다 이 스위치를 쓰는지가 다릅니다. Untitled Goose Tool 은 `Get-InboxRule` 을 `IncludeHidden` 을 켜고 불러 `EXO_InboxRules_PowerShell.json` 에 저장하지만[22], Hawk 의 `Get-HawkUserInboxRule` 과 Microsoft-Extractor-Suite 의 `Get-MailboxRules` 는 `-IncludeHidden` 없이 부릅니다[14][20]. 메일함 전달은 `Get-Mailbox` 의 `ForwardingSMTPAddress`·`ForwardingAddress`·`DeliverToMailboxAndForward` 에 있고, Hawk 는 두 전달 주소 중 하나라도 채워진 메일함을 `WhenChangedUTC` 와 함께 `_Investigate_Users_WithForwarding` 파일로 뽑습니다[16]. 조직 전체에 걸리는 전송 규칙 (transport rule) 은 `Get-TransportRule` 로 받고, Microsoft-Extractor-Suite 는 `Name`·`Description`·`CreatedBy`·`WhenChanged`(UTC 로 바꿈)·`State`·`Priority`·`Mode` 를 남깁니다[20].

2. **로그인을 가립니다.** 피해 계정의 로그인에서 평소와 다른 IP·국가·사용자 에이전트·장치를 찾고, 그 로그인의 세션 식별자를 적어 둡니다. 판별 방법은 [이상한 로그인 가려내기](../../03-techniques/analysis/suspicious-sign-ins.md) 에 있습니다. 비밀번호 없이 세션 토큰으로 들어온 흔적은 [토큰을 훔쳐 로그인했나](token-theft.md), 반복된 MFA 요청 끝의 승인은 [MFA 피로 공격을 당했나](mfa-fatigue.md), 메일을 읽는 앱에 권한을 준 경우는 [악성 OAuth 앱에 동의했나](illicit-consent.md) 로 넘어갑니다. 여기서 적어 둔 세션 식별자는 5단계에서 메일 접근 기록과 짝짓는 데 씁니다.

3. **규칙이 언제 생겼는지 찾습니다.** UAL 에서 받은 편지함 규칙은 만든 경로에 따라 작업 이름이 다릅니다. Outlook 웹에서 새로 만들면 `New-InboxRule`, Outlook 웹에서 고치면 `Set-InboxRule`, Outlook 클라이언트로 만들거나 고치거나 지우면 `UpdateInboxRules` 입니다[2]. `UpdateInboxRules` 는 관리자·대리인·소유자 로그온 모두 기본으로 기록되는 메일함 감사 동작입니다[1]. Hawk 의 `Get-HawkTenantAdminInboxRuleCreation` 은 `Search-UnifiedAuditLog -RecordType ExchangeAdmin -Operations 'New-InboxRule'` 로 생성 기록을 받습니다[15]. Exchange 관리 레코드의 `Parameters` 는 cmdlet 에 넘긴 매개변수의 이름·값 쌍 목록입니다[4]. 아래는 만든 예시 레코드(필드만 남김)입니다.

   ```json
   {
     "CreationTime": "2026-09-01T06:41:12",
     "Operation": "New-InboxRule",
     "ResultStatus": "True",
     "UserId": "finance@contoso.com",
     "ClientIP": "203.0.113.40",
     "Parameters": [
       { "Name": "Name", "Value": ".." },
       { "Name": "SubjectOrBodyContainsWords", "Value": "invoice;payment" },
       { "Name": "MoveToFolder", "Value": "RSS Feeds" },
       { "Name": "MarkAsRead", "Value": "True" }
     ]
   }
   ```

   규칙의 이름이나 조건보다 동작의 조합을 봅니다. `New-InboxRule` 의 동작 매개변수에는 `ForwardTo`·`RedirectTo`·`ForwardAsAttachmentTo`(밖으로 보내기), `DeleteMessage`·`SoftDeleteMessage`(지우기), `MoveToFolder`·`MarkAsRead`(옮기고 읽음 표시), `StopProcessingRules` 가 있고, 조건에는 `From`·`SubjectContainsWords`·`SubjectOrBodyContainsWords`·`FromAddressContainsWords` 같은 것이 있습니다[9]. 거래처 이름이나 "송금"·"계좌" 같은 단어를 조건으로 걸고 메일을 잘 보지 않는 폴더로 옮기며 읽음 표시까지 하는 규칙은 피해자가 거래처의 답장을 보지 못하게 하는 모양입니다. 도구가 걸러 주는 기준도 다릅니다. Hawk 는 `DeleteMessage` 가 참이거나 `ForwardAsAttachmentTo`·`ForwardTo`·`RedirectTo` 가 채워진 규칙만 `_Investigate_InboxRules` 로 뽑고[14], Microsoft-Extractor-Suite 는 `MoveToFolder`·`SoftDeleteMessage` 까지 출력합니다[20]. 옮기기만 하는 규칙은 Hawk 의 조사 대상 파일에 들어가지 않으므로 전체 규칙 목록을 직접 봅니다.

4. **메일함 전달 변경을 찾습니다.** 규칙이 아니라 메일함 속성으로 거는 전달은 `Set-Mailbox` 같은 관리 작업으로 남습니다. Hawk 의 `Get-HawkTenantAdminEmailForwardingChange` 는 `-RecordType ExchangeAdmin` 에서 `Set-Mailbox`·`Set-MailUser`·`Set-RemoteMailbox`·`Enable-RemoteMailbox` 를 받은 뒤, `Parameters` 의 이름이 `ForwardingAddress`·`ForwardingSMTPAddress`·`ExternalEmailAddress`·`PrimarySmtpAddress`·`RedirectTo`·`DeliverToMailboxAndForward`·`DeliverToAndForward` 인 레코드를 거릅니다[17]. Google Workspace 에서는 로그인 로그와 사용자 계정 로그 모두 이벤트 유형 `email_forwarding_change` 아래 이벤트 이름 `email_forwarding_out_of_domain` 이 도메인 밖 전달을 켠 기록이고, 관리 콘솔에는 "{actor} has enabled out of domain email forwarding to {email_forwarding_destination_address}." 로 보입니다[27][28]. Sigma 규칙 `gcp_gworkspace_out_of_domain_email_forwarding` 은 `protoPayload.serviceName` 이 `login.googleapis.com` 이고 `protoPayload.metadata.event.eventName` 이 `email_forwarding_out_of_domain` 인 레코드를 찾습니다[30].

5. **어떤 메일에 접근했는지 봅니다.** `MailItemsAccessed` 는 POP·IMAP·MAPI·EWS·Exchange ActiveSync·REST 로 메일에 접근한 기록이고, 접근 방식은 `OperationProperties` 의 `MailAccessType` 값 `Sync` 와 `Bind` 로 나뉩니다[3]. `Sync` 는 Windows·Mac 데스크톱 Outlook 으로 메일함에 접근할 때만 남고, 메시지마다가 아니라 폴더마다 한 건이 생기므로 그 폴더의 메일 전체가 넘어간 것으로 봅니다[3]. `Bind` 는 메시지 하나에 대한 접근이고, 2분 안의 접근을 한 레코드의 `Folders` 에 `InternetMessageId` 로 모으며 모은 개수를 `OperationCount` 에 적습니다[3]. 공격자의 접근과 평소 접근은 `ClientIPAddress`·`ClientInfoString`(프로토콜과 클라이언트)·`SessionId` 로 가릅니다[3]. 먼저 공격자 맥락(같은 IP·프로토콜)의 `Sync` 가 있는지 보고, 그다음 `Bind` 레코드의 `InternetMessageId` 로 접근한 메시지 목록을 만듭니다[3].

   ```powershell
   Search-UnifiedAuditLog -StartDate 2026-08-25 -EndDate 2026-09-02 -UserIds finance@contoso.com -Operations MailItemsAccessed -ResultSize 1000 |
     Where-Object { $_.AuditData -like '*"MailAccessType","Value":"Bind"*' }
   ```

   같은 메시지에 대한 `Bind` 는 한 시간 안에 되풀이되면 중복으로 지우고 `Sync` 도 한 시간 간격으로 거르지만, `ClientIPAddress`·`ClientInfoString`·`ParentFolder`·`Logon_type`(소유자 0, 관리자 1, 대리인 2)·`MailAccessType`·`MailboxUPN`·`User`·`SessionId` 중 하나라도 다르면 새 레코드가 생깁니다[3]. 그래서 공격자와 피해자가 같은 시간대에 같은 메일을 열어도 레코드는 따로 남습니다.

6. **사기 메일이 나갔는지 봅니다.** 메일함 감사 동작 `Send` 는 메일을 보내거나 답장·전달한 기록으로 관리자·소유자 로그온에서 기본으로 남고, `SendAs`·`SendOnBehalf` 는 다른 사람의 권한으로 보낸 기록으로 관리자·대리인 로그온에서 기본으로 남습니다[1]. Hawk 의 `Get-HawkUserMailSendActivity` 는 사용자에게 `Send` 동작이 켜져 있는지 먼저 확인한 뒤 `Search-UnifiedAuditLog -Operations 'Send' -UserIds` 로 받습니다[18]. 보낸 메일의 수신자와 전달 상태는 메시지 추적으로 확인하고, `Get-MessageTraceV2` 에는 `-SenderAddress`·`-RecipientAddress`·`-FromIP`·`-Status` 같은 거름 조건이 있습니다[10]. 90일이 지난 메일은 추적되지 않으므로 그 전에 결과를 받아 둡니다[10][11]. Google Workspace 의 발송 기록은 [Gmail 기록과 메일 검색](../../02-artifacts/google-workspace/gmail.md) 에서 봅니다.

7. **서비스의 탐지를 확인합니다.** Microsoft Entra ID Protection 의 `suspiciousInboxForwarding`(모든 메일을 외부 주소로 복사해 보내는 규칙 같은 수상한 전달)과 `mcasSuspiciousInboxManipulationRules`(메시지·폴더를 지우거나 옮기는 수상한 규칙)는 Defender for Cloud Apps 정보로 오프라인 계산되는 탐지입니다[13]. `suspiciousSendingPatterns` 는 Defender for Office 365 정보로, 수상한 메일을 보내 발송이 제한되었거나 제한될 위험이 있는 사용자를 중간 위험으로 올리며 Defender for Office 365 를 배포한 조직에서만 나옵니다[13]. Entra ID P2 가 없으면 이런 탐지는 세부 없이 `generic`("Additional risk detected")으로만 보입니다[13]. 탐지 규칙으로 찾을 때는 Sigma `azure_identity_protection_inbox_forwarding_rule`(`riskEventType: suspiciousInboxForwarding`)[23], `azure_identity_protection_inbox_manipulation`(`riskEventType: mcasSuspiciousInboxManipulationRules`)[24], `microsoft365_susp_inbox_forwarding`(`eventSource: SecurityComplianceCenter`, `eventName: Suspicious inbox forwarding`)[25], `microsoft365_user_restricted_from_sending_email`(`eventName: User restricted from sending email`)[26] 을 씁니다. 규칙을 쓰는 법은 [탐지 규칙으로 로그 훑기](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

   | 탐지 | 필요한 라이선스(2026년 4월 문서 기준) |
   |---|---|
   | `suspiciousInboxForwarding`, `mcasSuspiciousInboxManipulationRules`, `suspiciousSendingPatterns` | Entra ID P2 와 Defender for Cloud Apps 단독 라이선스, 또는 Microsoft 365 E5 와 Enterprise Mobility + Security E5[13] |
   | 세 탐지의 세부 | P2 가 없으면 `generic` 으로만 보임[13] |

8. **피해자 PC 의 Outlook 도 봅니다.** 규칙 동작이 응용 프로그램을 실행하도록 만든 규칙이나 `IPM.Note.` 로 시작하는 사용자 지정 폼은 공격자가 발판을 유지하는 지속성 (persistence) 수단입니다[12]. Microsoft 가 안내하는 `Get-AllTenantRulesAndForms.ps1` 은 `MailboxRulesExport-yyyy-MM-dd.csv` 를 만들고, `ActionType` 이 `ID_ACTION_CUSTOM` 이거나 `IsPotentiallyMalicious` 가 `TRUE` 인 줄이 의심 대상입니다[12]. 피해자 PC 의 `HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook\Security\EnableUnsafeClientMailRules` 가 1 이면 규칙의 "응용 프로그램 시작" 동작을 막는 보안 패치가 무력화된 상태입니다(Outlook 2013 은 `15.0`)[12]. PC 쪽 조사는 [[windows] 포렌식 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html) 를 따릅니다.

9. **번졌는지 보고 타임라인을 닫습니다.** 공격자 로그인의 IP·사용자 에이전트로 다른 계정의 로그인을 다시 검색하고, 같은 시간대에 다른 메일함에서 규칙이 생겼는지 3단계 검색을 사용자 제한 없이 한 번 더 돌립니다. 피해 메일함에서 내부 직원에게 나간 메일이 있으면 그 수신자들도 대상에 넣습니다. 로그인, 규칙 생성, 메일 접근, 사기 메일 발송, 송금 요청 시각을 한 줄로 늘어놓는 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다.

## 흔한 오판

- **"지금 규칙 목록에 없으니 규칙은 없었다."** `Get-InboxRule` 은 지금 있는 규칙만 보여 주고, 공격자가 지운 규칙은 보이지 않습니다. 반대로 UAL 의 생성 기록은 그 규칙이 지금도 있는지 확인해 주지 않습니다[15]. 두 쪽을 짝지어 봅니다. 숨긴 규칙은 `-IncludeHidden` 없이 받은 목록에서 빠집니다[8].
- **"`MailItemsAccessed` 가 있으니 공격자가 메일을 읽었다."** 이 기록은 메일이 읽혔다는 표시가 없어도 접근만으로 남습니다[3]. `Bind` 는 "이 메시지에 접근했다" 까지, `Sync` 는 "이 폴더를 내려받았다" 까지 보여 줍니다. 내려받은 메일을 네트워크를 끊고 읽은 것은 기록되지 않습니다[3].
- **"`MailItemsAccessed` 가 한 건도 없으니 메일을 보지 않았다."** 기본으로 켜지는 대상은 E3/E5 사용자이고[3], 메일함의 기본 감사 동작을 바꿨으면 빠질 수 있습니다[1]. 기록이 없을 때는 먼저 라이선스와 `DefaultAuditSet` 을 봅니다.
- **"`Send` 레코드가 있으니 공격자가 직접 썼다."** `Send` 와 메시지 추적은 메일이 이 메일함에서 나갔다는 사실까지 보여 줍니다. 사람이 보냈는지, 규칙이나 앱이 보냈는지는 `ClientInfoString` 과 UAL 의 `AppAccessContext`(`ClientAppId`·`ClientAppName`·`AADSessionId`)로 따로 봅니다[4]. `AppAccessContext` 는 필수 필드가 아니라서 모든 레코드에 채워지지는 않습니다[4].
- **"도구가 7일치만 준다."** 메시지 추적 범위는 도구 설명마다 다릅니다. Hawk 의 `Get-HawkUserMessageTrace` 는 옛 `Get-MessageTrace` 로 최근 7일만 받는다고 적었고[19], Microsoft-Extractor-Suite 의 `Get-MessageTraceLog` 는 도움말에 10일이라고 적었지만 코드의 기본 시작일은 90일 전입니다[21]. `Get-MessageTraceV2` 문서는 90일 조회, 한 번에 10일치입니다[10].
- **"UAL 보관이 90일이다."** Audit (Standard) 기본 보관은 2023년 10월 17일 이후 생성분부터 180일입니다[5]. 90일은 그 전에 생성된 기록의 값입니다.
- **"탐지 경고가 없으니 규칙은 정상이다."** ID Protection 의 받은 편지함 탐지는 Defender for Cloud Apps 정보와 라이선스가 있어야 나옵니다[13]. 경고가 없다는 것은 탐지가 돌지 않았을 가능성을 포함합니다.

## 보고서 문장 예

- "2026년 9월 1일 06:41:12(UTC)에 finance@contoso.com 계정 맥락으로 `New-InboxRule` 이 실행된 기록이 UAL 에 있다. 이 규칙은 제목이나 본문에 'invoice' 또는 'payment' 가 들어간 메일을 'RSS Feeds' 폴더로 옮기고 읽음으로 표시하는 조건이며, 요청 IP 는 203.0.113.40 이다." (만든 예시)
- "같은 날 06:55(UTC)부터 07:20(UTC)까지 IP 203.0.113.40 에서 `MailItemsAccessed`(`MailAccessType` Bind) 레코드 12건이 있고, 여기에 적힌 `InternetMessageId` 는 거래처 contoso.com 과 주고받은 메시지 34건이다." (만든 예시)
- "이 메일함의 규칙 목록을 2026년 9월 5일에 받았을 때 위 규칙은 없었다. 규칙을 지운 기록은 UAL 에서 따로 확인한다." (만든 예시)
- 쓰지 않을 문장: "공격자가 메일을 모두 읽고 사기 메일을 보냈다." 기록은 이 계정 맥락에서 규칙이 만들어지고, 메시지에 접근하고, 메일이 나갔다는 것까지 보여 줍니다. 키보드 앞에 누가 있었는지와 메일을 실제로 읽었는지는 보여 주지 않습니다.

보고서 전체의 틀은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

## 함께 볼 페이지

- 같은 갈래: [악성 OAuth 앱에 동의했나](illicit-consent.md), [토큰을 훔쳐 로그인했나](token-theft.md), [MFA 피로 공격을 당했나](mfa-fatigue.md)
- 아티팩트: [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [Exchange Online](../../02-artifacts/m365/exchange-online/index.md), [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [Google Workspace 로그인 기록](../../02-artifacts/google-workspace/login-audit.md), [Gmail 기록과 메일 검색](../../02-artifacts/google-workspace/gmail.md), [Okta 시스템 로그](../../02-artifacts/saas/okta.md)
- 개념: [토큰과 세션](../../01-foundations/identity/tokens-sessions.md), [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md)
- 다른 판: [[windows] 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)

## 참고 문헌

1. Microsoft, "Manage mailbox auditing", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-mailboxes
2. Microsoft, "Audit log activities", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-activities
3. Microsoft, "Use MailItemsAccessed to investigate compromised accounts", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
4. Microsoft, "Office 365 Management Activity API schema". https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
5. Microsoft, "Manage audit log retention policies", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
6. Microsoft, "Search the audit log", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-search
7. Microsoft, "Microsoft Entra data retention" (reference-reports-data-retention.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
8. Microsoft, "Get-InboxRule", Exchange PowerShell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-InboxRule.md
9. Microsoft, "New-InboxRule", Exchange PowerShell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/New-InboxRule.md
10. Microsoft, "Get-MessageTraceV2", Exchange PowerShell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-MessageTraceV2.md
11. Microsoft, "Start-HistoricalSearch", Exchange PowerShell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Start-HistoricalSearch.md
12. Microsoft, "Detect and remediate Outlook rules and custom forms injections attacks", Microsoft Defender for Office 365. https://learn.microsoft.com/en-us/defender-office-365/detect-and-remediate-outlook-rules-forms-attack
13. Microsoft, "What are risk detections?", Microsoft Entra ID Protection. https://learn.microsoft.com/en-us/entra/id-protection/concept-identity-protection-risks
14. T0pCyber, Hawk, Get-HawkUserInboxRule.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserInboxRule.ps1
15. T0pCyber, Hawk, Get-HawkTenantAdminInboxRuleCreation.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantAdminInboxRuleCreation.ps1
16. T0pCyber, Hawk, Get-HawkUserEmailForwarding.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserEmailForwarding.ps1
17. T0pCyber, Hawk, Get-HawkTenantAdminEmailForwardingChange.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantAdminEmailForwardingChange.ps1
18. T0pCyber, Hawk, Get-HawkUserMailSendActivity.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserMailSendActivity.ps1
19. T0pCyber, Hawk, Get-HawkUserMessageTrace.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/User/Get-HawkUserMessageTrace.ps1
20. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-Rules.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-Rules.ps1
21. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-MessageTraceLog.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-MessageTraceLog.ps1
22. CISA, Untitled Goose Tool, goosey/m365_datadumper.py. https://github.com/cisagov/untitledgoosetool/blob/develop/goosey/m365_datadumper.py
23. SigmaHQ, azure_identity_protection_inbox_forwarding_rule.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/identity_protection/azure_identity_protection_inbox_forwarding_rule.yml
24. SigmaHQ, azure_identity_protection_inbox_manipulation.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/azure/identity_protection/azure_identity_protection_inbox_manipulation.yml
25. SigmaHQ, microsoft365_susp_inbox_forwarding.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_susp_inbox_forwarding.yml
26. SigmaHQ, microsoft365_user_restricted_from_sending_email.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_user_restricted_from_sending_email.yml
27. Google, "Login Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
28. Google, "User Accounts Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/user-accounts
29. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566?hl=en
30. SigmaHQ, gcp_gworkspace_out_of_domain_email_forwarding.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/gworkspace/login/gcp_gworkspace_out_of_domain_email_forwarding.yml
31. Okta, "System Log query". https://developer.okta.com/docs/reference/system-log-query/
