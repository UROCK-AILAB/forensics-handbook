---
title: "퇴사자가 자료를 가져갔나"
parent: "시나리오 · 자료 유출"
nav_order: 820
---

# 퇴사자가 자료를 가져갔나 (Departing Employee)

퇴사를 앞둔 사람이 회사 계정으로 자료를 개인 기기·개인 계정·외부 서비스로 옮겼는지를 클라우드 로그로 가려내는 순서를 다룹니다. 이 조사에는 다른 유출 조사와 다른 점이 두 가지 있습니다. 계정을 지우는 순간부터 자료와 로그가 사라지는 시계가 돌기 시작하고, 내려받기·동기화처럼 평소 업무에서도 늘 생기는 동작을 퇴사 전의 행동과 구별해야 합니다.

## 조사 질문

- 퇴사를 결정하거나 통보한 뒤, 이 계정으로 회사 자료를 개인 기기에 내려받거나 동기화한 기록이 있나?
- 계정 전체를 통째로 내보낸 기록(Google Takeout, Slack 내보내기, 저장소 ZIP 내려받기)이 있나?
- 메일이 개인 주소로 자동 전달되도록 설정을 바꿨나?
- 그 양과 빈도가 같은 사람의 평소 모습과 다른가?
- 관리자가 퇴사 처리를 하면서 남긴 기록과 퇴사자 본인의 기록을 나눌 수 있나?

로그가 답하는 것은 "이 계정으로 이 시각에 이런 작업을 한 기록이 있다" 까지입니다. 받은 자료가 지금 어느 기기에 남아 있는지, 그 내용이 영업 비밀인지는 로그 밖의 질문입니다.

## 먼저 확인할 것

**먼저 주요 날짜를 표로 정리합니다.** 퇴사 결정일, 통보일, 마지막 근무일, 로그인 차단일, 라이선스 회수일, 계정 삭제일을 한 표에 적고 모두 UTC 로 맞춥니다. 이 표가 있어야 "결정 전 몇 주" 와 "결정 후" 를 나눠 비교할 수 있습니다. 시간대를 맞추는 방법은 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 있습니다.

**계정이 지금 어떤 상태인지 확인합니다.** 계정 처리도 로그에 남습니다. Microsoft Entra ID 감사 로그에는 UserManagement 범주의 `Disable account`, `Change user license`, `Delete user`, `Hard Delete user`, `Restore user` 가 있습니다[2]. Google Workspace 관리 로그에는 `SUSPEND_USER`, `ARCHIVE_USER`, `DELETE_USER`, `UNDELETE_USER` 가 있고[14], 문서 소유권을 다른 사람에게 넘기면 `TRANSFER_DOCUMENT_OWNERSHIP` 이 `Owner of documents changed from {USER_EMAIL} to {NEW_VALUE}` 모양으로 남습니다[15]. Slack 은 `user_deactivated` 로 남습니다[26].

**자료와 로그가 사라지는 시계를 확인합니다.** 아래 표는 2026년 9월 문서 기준입니다. 서비스 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다.

| 서비스 | 계정 자료가 사라지는 시계 | 로그 보관 |
|---|---|---|
| Microsoft 365 OneDrive | 시계는 Entra ID 에서 계정을 지울 때만 시작하고, 로그인 차단·라이선스 제거로는 시작하지 않음. 지운 사용자는 관리 센터에 30일 보이고, OneDrive 기본 보존 기간도 30일(`Set-SPOTenant -OrphanedPersonalSitesRetentionPeriod` 로 바꿈). 그 뒤 사이트 모음 휴지통에서 93일[1] | 통합 감사 로그: Audit (Standard) 180일(2023년 10월 17일 이전 기록은 90일). 1년 기본 정책은 작업한 사용자에게 E5 등 라이선스가 있을 때만[4] |
| Microsoft 365 OneDrive(라이선스 없음) | 라이선스 없는 OneDrive 는 93일째 자동 보관(archive), 유료 보관 12개월 뒤에는 보존 정책·보류와 상관없이 지워질 수 있음[1] | 같음 |
| Microsoft Entra ID | — | 감사 로그·로그인 로그 Free 7일, P1·P2 30일[3] |
| Google Workspace | 계정을 지운 뒤 20일 안에는 복구할 수 있지만, 삭제 표시된 데이터는 보존 규칙·보류(hold)의 보호를 받지 못하고 복구해도 돌아오지 않음. 보류 중인 계정은 지울 수 없음[16] | Drive·관리·Gmail·토큰·사용자 로그 이벤트 6개월, Email log search 30일, Vault 로그 기한 없음, 표에 따로 없는 로그는 대체로 6개월. 관리자가 로그를 지우거나 보관 기간을 바꿀 수 없음[17] |
| Slack | — | Audit Logs API 는 Enterprise 요금제 조직만 씀[27] |
| GitHub(엔터프라이즈) | — | 최근 180일, Git 이벤트는 7일[29] |
| Box | — | `admin_logs` 1년, `admin_logs_streaming` 2주, 관리 콘솔 내보내기 보고서 7년[30] |

OneDrive 를 지키려면 삭제 전에 보존 정책이나 eDiscovery 보류를 걸어 둡니다. 사이트 모음 휴지통은 색인되지 않아서 eDiscovery 보류가 그 안의 내용을 찾지 못하고, 보존 정책·보존 레이블은 OneDrive 기본 삭제 절차보다 우선합니다[1]. Google Workspace 는 삭제 전에 Archived User 라이선스로 바꾸거나 Vault 로 내보냅니다[16]. 보존 조치의 순서는 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md), Google 쪽 보류와 내보내기는 [Vault와 Takeout](../../02-artifacts/google-workspace/vault-takeout.md) 에 있습니다.

**라이선스를 거둬도 이미 쌓인 감사 기록의 보관 기간은 줄지 않습니다.** 통합 감사 로그 항목의 만료 시각은 기록이 파이프라인에 들어갈 때 그때의 라이선스와 보존 정책으로 정해지고, 뒤에 라이선스를 바꾸면 그 뒤에 들어오는 기록에만 적용됩니다[4]. Entra ID 라이선스를 바꿔도 통합 감사 로그 보관에는 영향이 없습니다[3].

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | Entra ID 감사 로그, Google 관리 로그 | 계정 차단·삭제·보관 처리 시각, 관리자가 한 조치 | [Entra ID 로그](../../02-artifacts/m365/entra-logs/index.md), [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| 2 | Google Takeout 로그, Slack·GitHub 내보내기 기록 | 계정을 통째로 내보냈는지, 어디로 보냈는지 | [Vault와 Takeout](../../02-artifacts/google-workspace/vault-takeout.md), [Slack 감사 로그](../../02-artifacts/saas/slack.md), [GitHub 감사 로그](../../02-artifacts/saas/github.md) |
| 3 | SharePoint·OneDrive 내려받기·동기화, Drive 내려받기·동기화, Box·Dropbox 내려받기 | 파일 단위로 무엇을 어느 기기로 가져갔나 | [SharePoint·OneDrive](../../02-artifacts/m365/sharepoint-onedrive.md), [Drive 기록](../../02-artifacts/google-workspace/drive-audit.md), [Dropbox·Box 기록](../../02-artifacts/saas/dropbox-box.md) |
| 4 | 메일 자동 전달 설정, `MailItemsAccessed`, Gmail 전달·내려받기 기록 | 메일이 밖으로 나가는 길을 열었나, 메일함을 통째로 받았나 | [Exchange Online](../../02-artifacts/m365/exchange-online/index.md), [Gmail 기록과 메일 검색](../../02-artifacts/google-workspace/gmail.md), [로그인 기록](../../02-artifacts/google-workspace/login-audit.md) |
| 5 | 공유 링크·외부 공유 기록 | 개인 계정이나 외부인에게 파일을 열어 줬나 | [외부 공유 링크로 새어 나갔나](external-sharing.md) |
| 6 | eDiscovery 검색·내보내기 기록(관리자 권한이 있던 사람) | 남의 메일함까지 PST 로 내보냈나 | [Purview eDiscovery와 보존](../../02-artifacts/m365/purview-ediscovery.md) |
| 7 | 로그인 기록 | 위 작업을 한 세션의 IP·기기·앱이 본인의 평소 것과 같은가 | [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) |

클라우드 콘솔 권한이 있던 사람이면 AWS·Azure·Google Cloud 의 저장소를 따로 봐야 합니다. 버킷·블롭·Cloud Storage 에서 읽어 간 흔적과 그 기록이 애초에 켜져 있었는지는 [클라우드 저장소에서 자료를 빼 갔나](storage-exfiltration.md) 에서, 퇴사자 이름으로 만든 액세스 키·서비스 계정 키가 퇴사 뒤에도 쓰였는지는 [액세스 키가 새어 나갔나](../infrastructure/leaked-keys.md) 에서 다룹니다.

## 분석 흐름

1. **로그부터 확보합니다.** 계정을 지우기 전에 보존 조치를 걸고, 보관 기간이 짧은 로그(Entra ID 감사 로그, GitHub Git 이벤트, Gmail 로그 검색)부터 받습니다. 보고서에는 계정 삭제일과 각 로그를 조사할 수 있는 첫날을 함께 적습니다.

2. **기준선을 만듭니다.** 같은 사람의 퇴사 결정 전 몇 주를 기준 기간으로 잡고, 하루 내려받기 건수, 동기화한 기기 수, 로그인 IP, 자주 여는 사이트를 셉니다. 결정 뒤 기간을 같은 방식으로 세어 나란히 놓습니다. 평소에도 OneDrive 를 동기화하던 사람이면 동기화 기록 자체가 아니라 새 기기, 평소 안 열던 사이트, 갑자기 늘어난 양이 판단 근거가 됩니다.

3. **계정을 통째로 내보낸 기록을 찾습니다.** Google Workspace 에서는 Reports API 의 `applicationName=takeout` 을 봅니다. 이벤트는 `STARTED_USER_TAKEOUT`, `COMPLETED_USER_TAKEOUT`, `DOWNLOADED_USER_TAKEOUT`, `SCHEDULED_USER_TAKEOUT` 이고, 매개변수 `TAKEOUT_DESTINATION` 이 `BOX`, `DRIVE`, `DROPBOX`, `EMAIL`(메일로 받은 링크로 로컬에 내려받음), `ONEDRIVE`, `UNKNOWN` 중 어디로 보냈는지를, `PRODUCTS_REQUESTED` 가 어느 서비스를 요청했는지를, `TAKEOUT_STATUS` 가 `CANCELED`·`COMPLETED`·`FAILED`·`IN_PROGRESS` 중 어디까지 갔는지를 알려 줍니다[18]. 관리 콘솔 Takeout 로그에는 Takeout 을 실행한 사용자의 IP 주소와 예약 Takeout 의 만료일·주기도 보입니다[19]. Takeout 으로 받은 파일은 Drive 의 Download 이벤트로 남지 않으므로 Drive 로그만 봐서는 빠집니다[21]. ALFA 의 기본 수집 목록에도 `takeout` 이 없어서[25] 따로 받아야 합니다. Takeout 을 쓸 수 있었는지는 관리자 설정이고, Drive·Gmail 같은 대부분의 서비스는 서비스마다 나누지 못하고 한 스위치로 함께 허용하거나 막습니다[20].
   Slack Enterprise 에서는 `manual_export_started`·`manual_export_downloaded`(표준·기업 내보내기), `manual_user_export_downloaded`, `channels_export_downloaded` 를 찾습니다[26]. GitHub 에서는 `repo.download_zip`(저장소 소스를 ZIP 으로 내려받음)과 `git.clone` 을 찾는데, `git.clone` 은 웹 화면에 나오지 않고 REST API·감사 로그 스트리밍·JSON/CSV 내보내기로만 받습니다[28]. 이 두 이벤트에는 `actor`, `repo`, `user_agent`, `hashed_token`, `token_id`, `programmatic_access_type` 필드가 있어서 사람이 직접 받았는지 토큰으로 받았는지를 가르는 데 씁니다[28].

4. **파일 단위 내려받기·동기화를 기간별로 셉니다.** 작업 이름과 필드의 뜻은 [클라우드 저장소에서 자료를 빼 갔나](storage-exfiltration.md) 와 각 아티팩트 쪽에 있고, 여기서는 퇴사자 관점에서 보는 것만 적습니다.
   - Microsoft 365: `FileDownloaded` 는 사이트에서 문서를 내려받은 것이고, `FileSyncDownloadedFull` 은 OneDrive 동기화 앱(OneDrive.exe)으로 컴퓨터에 내려받은 것입니다[6]. 동기화 요청에 기기 정보가 있으면 `MachineId`·`MachineDomainInfo` 가 채워지므로[7] 결정 뒤에 처음 보이는 기기를 찾습니다. `UnmanagedSyncClientBlocked` 는 조직 도메인에 속하지 않았거나, 문서 라이브러리에 접근할 수 있는 도메인 목록(안전 수신자 목록, safe recipients list)에 없는 도메인의 컴퓨터에서 동기화하려다 막힌 기록입니다[6].
   - Google Drive: Drive for desktop 으로 Drive 와 로컬 기기 사이에 파일을 복사하면 Download 와 Item content synced 가 함께 남고, Item content synced 는 2024년 7월 1일 이후 활동부터 있습니다[21].
   - Box 는 `DOWNLOAD`, `ITEM_SYNC`(폴더 동기화), `CONTENT_ACCESS`(권한 있는 사용자가 파일을 열었거나 Box 앱이 프로그램으로 접근)를[30], Dropbox 는 `file_download`, `file_copy`, `shared_content_download`, `device_link_success`(기기 연결)를 봅니다[31]. Slack 의 `file_downloaded` 는 Slack 안에서 파일을 내려받거나 본 것입니다[26].

5. **메일이 밖으로 나가는 길을 봅니다.** Microsoft 365 의 자동 전달은 사용자가 만드는 받은편지함 규칙과 관리자가 거는 사서함 전달(SMTP 전달) 두 가지입니다[9]. 관리자 쪽 설정은 감사 기록에서 `Set-Mailbox`, `Set-MailUser`, `Set-RemoteMailbox`, `Enable-RemoteMailbox` 명령의 `ForwardingAddress`, `ForwardingSMTPAddress`, `RedirectTo`, `DeliverToMailboxAndForward` 매개변수로 찾고[10], Defender 경고 `Suspicious inbox forwarding` 도 봅니다[11]. 받은편지함 규칙을 읽는 법은 [메일 계정을 빼앗겨 송금 사기를 당했나](../account-compromise/bec.md) 에 있습니다. 조직의 아웃바운드 스팸 정책이 외부 자동 전달을 막고 있었으면 전달은 `5.7.520 Access denied, Your organization does not allow external forwarding` 반송으로 끝납니다[9].
   Google Workspace 에서는 로그인 로그의 `email_forwarding_out_of_domain`(유형 `email_forwarding_change`)이 도메인 밖 전달을 켠 기록이고, 콘솔 메시지는 `{actor} has enabled out of domain email forwarding to {email_forwarding_destination_address}.` 모양입니다[23]. Sigma 규칙은 `protoPayload.serviceName: login.googleapis.com` 과 `protoPayload.metadata.event.eventName: email_forwarding_out_of_domain` 으로 이 기록을 잡습니다[24]. Gmail 로그(`applicationName=gmail`, 이벤트 이름은 늘 `delivery`)는 `event_info.mail_event_type` 으로 실제 동작을 가르는데, 1 은 보냄, 10 은 처음 전달, 11 은 계정 전달 설정에 따른 자동 전달, 17 은 첨부 내려받기, 18 은 첨부를 Drive 에 저장, 32 는 메시지 내려받기, 33 은 앱이 사용자 대신 메시지에 접근한 것입니다[22]. Gmail 로그는 요청할 때 `startTime`·`endTime` 을 반드시 주고 그 간격이 30일을 넘지 못합니다[22].

6. **메일함을 통째로 받았는지 봅니다.** `MailItemsAccessed` 는 Audit (Standard) 기능이고 E3·E5 사용자에게 기본으로 켜져 있습니다[8]. Windows·Mac 용 데스크톱 Outlook 이 메일을 한꺼번에 받으면 메시지마다가 아니라 폴더마다 한 건이 남고, `OperationProperties` 의 `MailAccessType` 이 `Sync` 입니다[8]. 결정 뒤에 새 IP·새 클라이언트에서 여러 폴더의 `Sync` 가 잇따르면 메일함을 통째로 내려받았을 가능성이 있습니다. 관리자 권한이 있던 사람이면 eDiscovery 검색을 PST 로 내보낸 기록도 봅니다. Sigma 규칙은 `SecurityComplianceCenter` 경고 `eDiscovery search started or exported` 를 잡거나[12], Payload 에 `New-ComplianceSearchAction`·`Export`·`pst` 가 함께 들어간 기록을 잡습니다[13].

7. **관리자의 퇴사 처리와 퇴사자의 행동을 나눕니다.** 관리자가 사용자 프로필을 고쳐 남의 OneDrive 에 접근권을 받으면 `SiteCollectionAdminAdded` 가 남습니다[6]. `app@sharepoint` 사용자는 SharePoint App-Only 권한을 받은 앱이 한 작업이고, 보존 정책을 적용할 때 검색·파일 접근 기록을 대량으로 만듭니다[6]. 접근 위임(access delegation)이 켜져 있으면 계정을 지울 때 그 사용자의 상사(manager)나, 상사가 없을 때 지정한 보조 소유자가 OneDrive 접근권을 자동으로 받으므로[1], 삭제일 뒤의 파일 작업은 누가 했는지 `UserId` 를 먼저 확인합니다.

8. **타임라인으로 합칩니다.** 날짜 표, 계정 처리 기록, 내보내기·내려받기·전달 기록을 시간순으로 합치고 결정일 앞뒤로 나눕니다. 방법은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다. 개인 PC·휴대 기기를 함께 조사하면 [[windows] 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html) 의 순서로 기기 쪽 흔적과 맞춥니다.

## 흔한 오판

- **"평소에도 동기화하던 사람의 `FileSyncDownloadedFull` 이 많으니 유출이다."** 동기화 앱은 평소 업무에서도 이 기록을 계속 만듭니다. 기준 기간과 비교하지 않은 건수는 근거가 되지 못합니다.
- **"Drive 로그에 Download 가 없으니 가져간 것이 없다."** Takeout 으로 받은 파일, 오프라인 브라우저 캐시, Gmail 에서 첨부로 보낸 Drive 항목은 Download 로 남지 않습니다[21]. Takeout 로그를 따로 봅니다.
- **"로그인을 막고 라이선스를 거뒀으니 OneDrive 는 그대로 있다."** 삭제 시계는 Entra ID 삭제로만 시작하지만, 라이선스 없는 OneDrive 는 93일째 따로 보관 절차에 들어갑니다[1].
- **"계정부터 지우고 나중에 조사해도 20일 안에 되살리면 된다."** Google Workspace 는 계정을 복구해도 삭제 표시된 데이터가 돌아오지 않습니다[16].
- **"`Sync` 기록에 없는 메시지는 가져가지 않았다."** `Sync` 는 폴더 단위라 메시지 목록이 없고, 한 시간 간격으로 걸러서 남깁니다. 메일을 받은 뒤 인터넷을 끊고 로컬에서 읽으면 감사 기록이 생기지 않습니다[8].
- **"관리 콘솔의 시각을 그대로 옮겼다."** Google 관리 콘솔과 Takeout 로그 화면은 브라우저 기본 시간대로 시각을 보여 줍니다[19][21]. 통합 감사 로그의 `CreationTime` 은 UTC 입니다[7].
- **"퇴사 처리로 주소를 바꿔도 기록은 그대로 찾을 수 있다."** Google Workspace 에서 사용자 이름을 바꾸면 옛 이름과 관련된 이벤트가 조사 결과에 나오지 않습니다[19][21]. 퇴사자 주소를 바꾸거나 다른 사람에게 넘기기 전에 기록부터 받아 둡니다.
- **"방금 한 작업이 검색에 안 나오니 없었다."** 통합 감사 로그는 Exchange·SharePoint·OneDrive·Teams 기록이 검색에 보이기까지 보통 60~90분 걸리고 시간을 보장하지 않습니다[5]. Takeout 완료 이벤트는 자료 크기에 따라 며칠 늦게 들어오고, 토큰 로그는 몇 시간 늦습니다[17].

## 보고서 문장 예

- "2026년 8월 28일 14:02(UTC)에 계정 kim@example.com 으로 Google Takeout 이 시작되었고, `TAKEOUT_DESTINATION` 값은 `DROPBOX`, 요청한 서비스에는 Drive 와 Gmail 이 있다. 같은 Takeout ID 의 완료 이벤트는 8월 29일에 `COMPLETED` 상태로 기록되어 있다." (만든 예시)
- "퇴사 통보일 이후 7일 동안 이 계정의 `FileSyncDownloadedFull` 기록은 3,410건이며, 통보 전 4주의 하루 평균은 22건이다. 통보 이후 기록의 `MachineId` 는 통보 전 기간에 나타나지 않은 값 하나다." (만든 예시)
- "2026년 9월 2일 09:15(UTC)에 이 사서함에 `Set-Mailbox` 로 `ForwardingSMTPAddress` 가 설정된 기록이 있고, 작업한 계정은 관리자 admin@contoso.com 이다." (만든 예시)
- 쓰지 않을 문장: "퇴사자가 영업 비밀을 개인 드롭박스로 빼돌렸다." 로그는 이 계정으로 내보내기를 요청하고 목적지가 Dropbox 였다는 것까지 보여 주고, 계정을 누가 쓰고 있었는지, 받은 자료가 지금 어디 있는지, 그 내용이 무엇인지는 보여 주지 않습니다.

## 함께 볼 페이지

- 같은 갈래: [클라우드 저장소에서 자료를 빼 갔나](storage-exfiltration.md), [외부 공유 링크로 새어 나갔나](external-sharing.md)
- 계정을 남이 썼을 가능성: [토큰을 훔쳐 로그인했나](../account-compromise/token-theft.md), [악성 OAuth 앱에 동의했나](../account-compromise/illicit-consent.md)
- 수집: [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) — Microsoft-Extractor-Suite 의 `Get-UAL` 은 `-UserIds` 로 한 사용자의 기록만 받고 `-Group Sharepoint` 로 SharePoint 파일·공유 작업 레코드 유형을 묶어 받습니다[32]. 같은 도구의 `Get-MailboxRules`(Get-Rules.ps1), `Get-Sessions`·`Get-MessageIDs`(Get-MailItemsAccessed.ps1)로 받은편지함 규칙과 `MailItemsAccessed` 를 받습니다[33]. Google Workspace 는 ALFA 가 Reports API(`admin.reports.audit.readonly` 범위)로 drive·login·token·admin 등을 받고, Gmail 은 30일 제한 때문에 기본 목록에서 빠져 있습니다[25].
- 보고: [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)
- 다른 판: [[ai] 계정 데이터 내보내기 형식](https://urock-ailab.github.io/forensics-handbook/ai/01-foundations/storage-model/data-export-formats.html), [[ai] 보안 제품이 남기는 AI 사용 기록 (DLP·CASB)](https://urock-ailab.github.io/forensics-handbook/ai/02-artifacts/network-enterprise/dlp-casb.html), [[windows] 포렌식 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html)

## 참고 문헌

1. Microsoft, "OneDrive retention and deletion". https://learn.microsoft.com/en-us/sharepoint/retention-and-deletion
2. Microsoft, "Microsoft Entra audit log activity reference" (reference-audit-activities.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-audit-activities.md
3. Microsoft, "Microsoft Entra data retention" (reference-reports-data-retention.md). https://github.com/MicrosoftDocs/entra-docs/blob/main/docs/identity/monitoring-health/reference-reports-data-retention.md
4. Microsoft, "Manage audit log retention policies". https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
5. Microsoft, "Search the audit log". https://learn.microsoft.com/en-us/purview/audit-search
6. Microsoft, "Audit log activities". https://learn.microsoft.com/en-us/purview/audit-log-activities
7. Microsoft, "Office 365 Management Activity API schema". https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
8. Microsoft, "Use MailItemsAccessed to investigate compromised accounts". https://learn.microsoft.com/en-us/purview/audit-log-investigate-accounts
9. Microsoft, "Control automatic external email forwarding from cloud mailboxes". https://learn.microsoft.com/en-us/defender-office-365/outbound-spam-policies-external-email-forwarding
10. T0pCyber, Hawk, Get-HawkTenantAdminEmailForwardingChange.ps1. https://github.com/T0pCyber/hawk/blob/master/Hawk/functions/Tenant/Get-HawkTenantAdminEmailForwardingChange.ps1
11. SigmaHQ, microsoft365_susp_inbox_forwarding.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_susp_inbox_forwarding.yml
12. SigmaHQ, microsoft365_pst_export_alert.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_pst_export_alert.yml
13. SigmaHQ, microsoft365_pst_export_alert_using_new_compliancesearchaction.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/m365/threat_management/microsoft365_pst_export_alert_using_new_compliancesearchaction.yml
14. Google, "Admin Audit Activity Events - User Settings", Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-user-settings
15. Google, "Admin Audit Activity Events - Docs Settings", Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/admin-docs-settings
16. Google, "Delete a user with data on hold". https://knowledge.workspace.google.com/vault/holds/delete-a-user-with-data-on-hold
17. Google, "Data retention and lag times". https://support.google.com/a/answer/7061566
18. Google, "Takeout Audit Activity Events", Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/takeout
19. Google, "Takeout log events". https://knowledge.workspace.google.com/admin/reports/takeout-log-events
20. Google, "Allow or block Google Takeout". https://knowledge.workspace.google.com/admin/users/advanced/allow-or-block-google-takeout
21. Google, "Drive log events". https://support.google.com/a/answer/4579696
22. Google, "Gmail Audit Activity Events", Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/gmail
23. Google, "Login Audit Activity Events", Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/login
24. SigmaHQ, gcp_gworkspace_out_of_domain_email_forwarding.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/cloud/gcp/gworkspace/login/gcp_gworkspace_out_of_domain_email_forwarding.yml
25. Invictus Incident Response, ALFA, alfa/config/config.yml. https://github.com/invictus-ir/ALFA/blob/main/alfa/config/config.yml
26. Slack, "Audit Logs API actions". https://api.slack.com/admins/audit-logs-call
27. Slack, "Audit Logs API". https://api.slack.com/admins/audit-logs
28. GitHub, "Audit log events for your organization". https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization
29. GitHub, "About the audit log for your enterprise". https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise
30. Box, "Enterprise events". https://developer.box.com/guides/events/enterprise-events/for-enterprise/
31. Dropbox, dropbox-api-spec, team_log.stone. https://github.com/dropbox/dropbox-api-spec/blob/main/team_log.stone
32. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-UAL.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UAL.ps1
33. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-Rules.ps1, Scripts/Get-MailItemsAccessed.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/tree/main/Scripts
