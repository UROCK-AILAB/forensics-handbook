---
title: "Exchange Online"
parent: "아티팩트 · Microsoft 365"
nav_order: 210
has_children: true
has_toc: false
---

# Exchange Online (Exchange Online)

Exchange Online 에서는 메일함 안에서 일어난 작업, 받은편지함 규칙과 전달 설정, 메일이 오간 경로가 각각 다른 곳에 따로 남습니다. 이 페이지는 그 기록들이 어디에 있고 무엇을 알려 주는지 정리한 입구입니다.

## 왜 중요한가

메일 계정을 빼앗긴 사건에서는 "누가 어느 메일을 열어 봤나", "메일을 몰래 밖으로 빼돌리는 규칙을 만들었나", "그 메일이 실제로 나갔나" 를 차례로 물어야 하고, 세 질문의 답은 서로 다른 기록에 있습니다.

메일함 안의 작업은 메일함 감사 (Mailbox Auditing) 가 기록하고, 이 기록은 통합 감사 로그 (Unified Audit Log) 에서 검색합니다[1]. cmdlet 을 실행해 바꾼 설정은 Exchange 관리 감사 레코드로 남습니다[2]. 메일이 들어오고 나간 사실은 감사 로그가 아니라 메시지 추적 (Message Trace) 으로 확인합니다[6][7].

기록마다 남는 기간이 짧거나 따로 정해져 있다는 점도 중요합니다. 메시지 추적은 최근 90일까지만 조회할 수 있고[6], 복구 가능한 항목 폴더 (Recoverable Items) 의 삭제 항목은 기본 14일이 지나면 지워집니다[8]. 사건을 알게 되면 이 기록부터 내려받아 두는 편이 안전합니다. 순서는 [로그부터 지키기](../../../03-techniques/acquisition/log-preservation.md)에 있습니다.

## 한눈에 보기

아래 기간과 기본값은 2026년 9월 문서 기준입니다.

| 기록 | 어디서 보나 | 알려 주는 것 | 남는 기간·조건 |
|---|---|---|---|
| 메일함 감사 | 통합 감사 로그. RecordType `ExchangeItem`(항목 하나), `ExchangeItemGroup`(여러 항목), `ExchangeItemAggregated`(MailItemsAccessed)[2] | 소유자·위임자·관리자가 메일함에서 한 작업(삭제, 지운 편지함으로 옮기기, 보내기, 받은편지함 규칙 변경 등)[1] | 모든 조직에서 기본으로 켜져 있습니다[1]. 보관 기간은 메일함 속성 `AuditLogAgeLimit` 가 아니라 Purview 감사 보존 정책이 정합니다[1]. |
| MailItemsAccessed | 통합 감사 로그, 작업 이름 `MailItemsAccessed`[3] | 어느 세션·IP·클라이언트로 어떤 폴더를 동기화했는지(Sync), 어떤 메시지에 접근했는지(Bind)[3] | Audit (Standard) 기능이고, Office 365·Microsoft 365 E3/E5 사용자에게 기본으로 켜져 있습니다[3]. |
| Exchange 관리 감사 | 통합 감사 로그, RecordType `ExchangeAdmin`[2] | 실행한 cmdlet 이름(Operation)과 넘긴 값(Parameters)[2]. 예: `Set-Mailbox` 로 바꾼 전달 주소, `New-InboxRule` 로 만든 규칙[12] | 통합 감사 로그 보존 기간을 따릅니다. [보관 기간과 라이선스](../../../01-foundations/logging/retention-licensing.md) 참고 |
| 받은편지함 규칙·전달 설정의 현재 상태 | `Get-InboxRule`(숨긴 규칙은 `-IncludeHidden`)[4], `Get-Mailbox` 의 `ForwardingAddress`·`ForwardingSmtpAddress`·`DeliverToMailboxAndForward`[5] | 수집한 그 순간에 켜져 있는 규칙과 전달 주소 | 지운 규칙은 보이지 않으므로 바뀐 이력은 감사 로그로 봅니다. |
| 외부 자동 전달 차단 | 아웃바운드 스팸 정책의 자동 전달 설정[9] | 조직이 외부 전달을 막았는지. 막혔으면 보낸 사람이 `5.7.520` NDR 을 받습니다[9]. | 기본값 Automatic - System-controlled 는 조직마다 켜짐·꺼짐 가운데 하나로 동작합니다[9]. |
| 메시지 추적 | Exchange 관리 센터, `Get-MessageTraceV2`·`Get-MessageTraceDetailV2`[6][7] | 서비스가 메시지를 받고 보내고 처리한 결과(전달됨·실패·격리 등)[7]. 보낸 쪽 클라이언트 IP 는 최근 10일 안의 Enhanced summary·Extended 보고서에만 나옵니다[7] | 최근 90일, 한 번에 10일치까지 조회합니다[6]. 결과 시각은 UTC 입니다[6]. |
| 복구 가능한 항목 폴더 | 메일함 안의 숨은 폴더: Deletions, Versions, Purges, DiscoveryHolds, Calendar Logging, SubstrateHolds 등[8] | 사용자가 지운 메일, 보존 중 바뀐 항목의 원본[8] | 삭제 항목 보관 기본 14일, 최대 30일로 늘릴 수 있습니다[8]. 소송 보존(Litigation Hold)을 걸면 자동 삭제가 멈춥니다[8]. |
| Defender 이메일 기록 | 고급 헌팅 `EmailEvents` 테이블[11] | 메일 처리 이벤트와 `ForwardingInformation`(전달한 사용자·전달 유형)[11] | Microsoft Defender for Office 365 가 있어야 남습니다[11]. [Defender 경고와 기록](../defender-xdr.md) 참고 |

감사 레코드는 일이 일어난 뒤 바로 검색되지 않습니다. Exchange 같은 핵심 서비스는 보통 60~90분 뒤에 검색 결과에 나타납니다[10]. 레코드의 시각 필드와 UTC 처리는 [통합 감사 로그](../unified-audit-log/index.md)와 [클라우드 로그의 시각](../../../01-foundations/logging/timestamps.md)에서 다룹니다.

수집 도구는 기록과 함께 현재 설정도 떠 둡니다. Untitled Goose Tool 은 `Get-Mailbox`, `Get-CASMailbox`, `Get-MailboxPermission`, `Get-MailboxFolderPermission`, `Get-InboxRule`, `Get-MailboxAuditBypassAssociation`, `Get-TransportRule`, `Get-MobileDevice` 등의 결과를 함께 저장합니다[13]. 이 가운데 `Get-MailboxAuditBypassAssociation` 은 특정 계정의 메일함 작업이 감사에서 빠지도록 설정됐는지 보여 주므로, 감사 기록이 비어 있을 때 먼저 확인합니다[1]. 도구별 차이는 [Microsoft 365 수집 도구](../../../03-techniques/acquisition/m365-collection.md)에 있습니다.

## 읽는 순서

1. [메일함 감사와 MailItemsAccessed (Mailbox Auditing)](mailbox-auditing.md) — 기본으로 감사하는 작업, 로그온 유형, MailItemsAccessed 의 Sync·Bind 구분과 묶음 규칙, 감사를 끄거나 우회한 흔적을 다룹니다.
2. [받은편지함 규칙과 전달 (Inbox Rules·Forwarding)](inbox-rules.md) — 규칙과 메일함 전달의 현재 상태를 뽑는 방법, 만들고 바꾼 이력이 남는 작업 이름, 외부 전달 차단 설정을 다룹니다.
3. [메시지 추적 (Message Trace)](message-trace.md) — 조회 기간과 건수 제한, Message ID 와 Network Message ID 의 차이, 보고서 열의 뜻을 다룹니다.

## 함께 볼 페이지

- [통합 감사 로그 (Unified Audit Log)](../unified-audit-log/index.md) — 메일함 감사와 Exchange 관리 감사가 실제로 들어가는 로그
- [Entra ID 로그 (Entra ID Logs)](../entra-logs/index.md) — 메일함에 접근한 세션이 어디서 로그인했는지
- [Purview eDiscovery와 보존 (eDiscovery·Retention)](../purview-ediscovery.md) — 지운 메일과 보존 중인 메일함 내용 확보
- [Defender 경고와 기록 (Microsoft Defender XDR)](../defender-xdr.md) — 메일 처리 이벤트와 전달 정보
- [메일 계정을 빼앗겨 송금 사기를 당했나 (BEC)](../../../04-scenarios/account-compromise/bec.md) — 이 기록들을 엮어 쓰는 조사 흐름
- [클라우드 타임라인 (Timeline)](../../../03-techniques/analysis/timeline.md)

## 참고 문헌

1. Microsoft, "Manage mailbox auditing", Microsoft Learn, 2026-06-19 갱신. https://learn.microsoft.com/en-us/purview/audit-mailboxes
2. Microsoft, "Office 365 Management Activity API schema", Microsoft Learn, 2026-08-26 갱신. https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
3. Microsoft, "Use MailItemsAccessed to investigate compromised accounts", Microsoft Learn, 2026-06-24 갱신. https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
4. Microsoft, "Get-InboxRule", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-InboxRule.md
5. Microsoft, "Set-Mailbox", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Set-Mailbox.md
6. Microsoft, "Get-MessageTraceV2", office-docs-powershell. https://github.com/MicrosoftDocs/office-docs-powershell/blob/main/exchange/exchange-ps/ExchangePowerShell/Get-MessageTraceV2.md
7. Microsoft, "Message trace in the modern Exchange admin center", Microsoft Learn, 2026-05-27 갱신. https://learn.microsoft.com/en-us/exchange/monitoring/trace-an-email-message/message-trace-modern-eac
8. Microsoft, "Recoverable Items folder in Exchange Online", Microsoft Learn, 2026-07-13 갱신. https://learn.microsoft.com/en-us/exchange/security-and-compliance/recoverable-items-folder/recoverable-items-folder
9. Microsoft, "Outbound spam policies - external email forwarding", Microsoft Learn, 2026-08-18 갱신. https://learn.microsoft.com/en-us/defender-office-365/outbound-spam-policies-external-email-forwarding
10. Microsoft, "Search the audit log", Microsoft Learn, 2026-06-19 갱신. https://learn.microsoft.com/en-us/purview/audit-search
11. Microsoft, "EmailEvents", Microsoft Learn, 2026-09-02 갱신. https://learn.microsoft.com/en-us/defender-xdr/advanced-hunting-emailevents-table
12. T0pCyber, Hawk. https://github.com/T0pCyber/hawk
13. CISA, Untitled Goose Tool. https://github.com/cisagov/untitledgoosetool
