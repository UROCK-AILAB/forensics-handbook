---
title: "외부 공유 링크로 새어 나갔나"
parent: "시나리오 · 자료 유출"
nav_order: 830
---

# 외부 공유 링크로 새어 나갔나 (External Sharing)

SharePoint·OneDrive, Google Drive, Box, Dropbox, Slack, GitHub 에서 파일이나 저장소가 공유 링크·외부 계정 초대로 조직 밖에 열렸는지, 그 링크로 실제로 누가 들어왔는지를 로그로 가려내는 순서를 다룹니다. S3 버킷 정책, 스냅숏 공개, Cloud Storage 의 `allUsers` 같은 IaaS 저장소 공개 설정은 [클라우드 저장소에서 자료를 빼 갔나](storage-exfiltration.md) 에서 다룹니다.

## 조사 질문

- 이 파일(폴더·사이트·저장소)은 언제, 어느 계정이 공유했나?
- 공유 범위는 어디까지였나? 링크가 있는 누구나 (Anyone), 조직 구성원, 지정한 사람, 외부 계정 가운데 무엇이었나?
- 범위를 나중에 넓히거나 좁혔나? 부모 폴더의 설정이 바뀌어 딸려서 바뀐 것인가?
- 그 링크나 권한으로 실제로 들어온 기록이 있나? 들어온 사람을 특정할 수 있나?
- 링크는 언제 없어졌나? 만료 설정이 있었나?

공유 링크 조사는 링크의 일생을 네 단계로 나눠 보면 서비스가 달라도 같은 틀로 정리됩니다. 만들기, 범위 바꾸기, 쓰기(접근), 없애기입니다. 링크를 만든 기록은 "열어 두었다" 까지만 말하고, 누가 들어왔는지는 쓰기 단계의 기록이 따로 있어야 말할 수 있습니다.

## 먼저 확인할 것

**어느 서비스에 무엇이 남는지부터 정합니다.** 서비스마다 기록이 남는 조건과 보관 기간이 다르고, 공유가 오래전에 일어났으면 보관 기간이 먼저 끝나 만든 시각을 잃습니다. 아래 표는 2026년 9월 문서 기준이고, 서비스 전체 표는 [보관 기간과 라이선스](../../01-foundations/logging/retention-licensing.md) 에 있습니다. 보관 기간이 곧 끝나는 기록은 [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md) 의 순서로 먼저 받아 둡니다.

| 서비스 | 공유 기록이 남는 곳 | 남는 조건 | 보관 기간 |
|---|---|---|---|
| Microsoft 365 (SharePoint·OneDrive) | 통합 감사 로그, 레코드 유형 14 `SharePointSharingOperation`[6] | 감사가 켜진 테넌트 | Audit (Standard) 180일(2023년 10월 17일 이전 기록은 90일). 활동한 사용자에게 E5 등 라이선스가 있으면 기본 정책으로 1년[7] |
| Google Workspace | Drive 로그 이벤트 | 대부분의 Drive 감사 이벤트는 지원 에디션 사용자가 소유한 파일에만 남음[10] | 6개월[12] |
| Box | 기업 이벤트(`admin_logs`, `admin_logs_streaming`) | — | `admin_logs` 1년, `admin_logs_streaming` 2주, 관리 콘솔 내보내기 보고서 7년[13] |
| Dropbox | 팀 이벤트 로그 | — | [Dropbox·Box 기록](../../02-artifacts/saas/dropbox-box.md) 참고 |
| Slack | 감사 로그 API | Enterprise 요금제 조직만[15] | [Slack 감사 로그](../../02-artifacts/saas/slack.md) 참고 |
| GitHub | 조직·엔터프라이즈 감사 로그 | — | 최근 180일, Git 이벤트 7일[17] |

**설정이 언제 어떻게 바뀌었는지도 같은 기간으로 받습니다.** 공유 정책이 조사 기간 중에 바뀌었으면 같은 동작이 날짜에 따라 막히기도 하고 통과하기도 합니다. Microsoft 365 는 관리자가 공유 정책을 바꾸면 `SharingPolicyChanged` 가 남고 바뀐 정책은 `ModifiedProperties` 에 들어갑니다[1].

**시각 기준을 맞춥니다.** 통합 감사 로그의 `CreationTime` 은 기록이 생긴 UTC 시각이고[5], 핵심 서비스의 감사 기록은 보통 60~90분 뒤에 검색에 나타나며 보장된 시간은 없습니다[8]. Google 관리 콘솔 화면의 시각은 보는 사람 브라우저의 기본 시간대로 표시됩니다[10]. Drive 로그 이벤트는 몇 분 안에 들어오지만, 링크 공유 상태를 보여 주는 Drive 보고서는 1~3일 늦습니다[12]. 그래서 보고서 화면의 숫자와 로그 이벤트의 숫자가 어긋날 수 있습니다. 서비스별 시각 표기는 [클라우드 로그의 시각](../../01-foundations/logging/timestamps.md) 에 모았습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 공유 설정 변경 기록: `SharingPolicyChanged`, `WebMembersCanShareModified`, `SharingInheritanceBroken`, Google 관리 콘솔 감사 | 조사 기간에 외부 공유가 허용됐는지, 언제 바뀌었는지 | [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md) |
| 2 | 링크 만들기·권한 주기: `AnonymousLinkCreated`·`SecureLinkCreated`·`SharingSet`, Drive `change_document_visibility`·`change_user_access`, Box `SHARE`, Dropbox `shared_link_create` | 누가 언제 어떤 범위로 열었나 | [SharePoint·OneDrive](../../02-artifacts/m365/sharepoint-onedrive.md), [Drive 기록](../../02-artifacts/google-workspace/drive-audit.md), [Dropbox·Box 기록](../../02-artifacts/saas/dropbox-box.md) |
| 3 | 범위 바꾸기: `AnonymousLinkUpdated`, Drive `old_value`·`new_value`, Dropbox `shared_link_change_visibility`, Box `ITEM_SHARED_UPDATE` | 좁은 공유가 나중에 넓어졌는지 | 위와 같음 |
| 4 | 링크 쓰기: `AnonymousLinkUsed`·`SecureLinkUsed`·`CompanyLinkUsed`, 외부인의 `FileAccessed`, Drive 의 anonymous 행위자, Box 사용자 ID `2`, Dropbox `shared_link_view`·`shared_link_download` | 링크로 실제 접근한 기록이 있는지, 접근자를 어디까지 특정할 수 있는지 | 위와 같음, [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) |
| 5 | 링크 없애기: `AnonymousLinkRemoved`·`SecureLinkDeleted`·`SharingRevoked`, Box `UNSHARE`, Dropbox `shared_link_disable`, Slack `file_public_link_revoked` | 노출이 끝난 시각 | 위와 같음, [Slack 감사 로그](../../02-artifacts/saas/slack.md) |
| 6 | 공유 뒤의 내려받기·복사 | 링크를 연 뒤 자료를 가져갔는지 | [클라우드 저장소에서 자료를 빼 갔나](storage-exfiltration.md) |

## 분석 흐름

1. **대상과 기간을 정합니다.** 문제의 파일이 정해져 있으면 그 파일의 식별자를 먼저 적습니다. Microsoft 365 공유 기록의 `ObjectId` 는 파일의 전체 경로이고 `SiteUrl`, `SourceRelativeUrl`, `SourceFileName` 을 이어 붙인 값과 같습니다[6]. Google Drive 는 `doc_id` 로 찾습니다[9]. 파일이 정해져 있지 않으면 조사 기간 전체에서 "밖으로 열린 공유" 를 모두 뽑은 뒤 좁힙니다.

2. **Microsoft 365 에서 링크를 만든 기록을 찾습니다.** 공유 방식마다 남는 작업 이름이 다르므로 아래 표의 작업을 모두 검색합니다.

   | 공유 방식 | 만들기 | 쓰기(접근) | 없애기·바꾸기 |
   |---|---|---|---|
   | 링크가 있는 누구나 (Anyone) — 인증 없이 열림, 전달 가능[3] | `AnonymousLinkCreated`[1] | `AnonymousLinkUsed`. 사용자 신원은 모를 수 있지만 IP 같은 정보는 남음[1] | `AnonymousLinkRemoved`, `AnonymousLinkUpdated`(바뀐 필드는 `EventData`)[1] |
   | 조직 구성원 (People in your organization) — 구성원만, 게스트 불가[1] | `CompanyLinkCreated` | `CompanyLinkUsed` | `CompanyLinkRemoved`[1] |
   | 지정한 사람 (Specific people) — 지정한 사람 말고는 열리지 않음[3] | `SecureLinkCreated` 와 거의 같은 시각의 `AddedToSecureLink`. 대상은 `AddedToSecureLink` 의 `TargetUserOrGroupName`[2] | `SecureLinkUsed`[1]. 외부 사용자가 쓰면 `FileAccessed`[2] | `SecureLinkDeleted`, `RemovedFromSecureLink`[1] |
   | 디렉터리에 있는 사용자(게스트 계정 포함)에게 직접 | `SharingSet` 과 `AddedToGroup`[2] | 일반 파일 작업 | `SharingRevoked`[1] |
   | 디렉터리에 없는 외부인에게 초대 | `SharingInvitationCreated`(사이트를 공유할 때만 남음)[2] | 수락하면 `SharingInvitationAccepted`[2] | `SharingInvitationRevoked`. 도메인 제한에 막히면 `SharingInvitationBlocked`[1] |

   외부로 나간 공유만 추리려면 `SharingInvitationCreated`, `AnonymousLinkCreated`, `SecureLinkCreated`, `AddedToSecureLink` 를 고르고, `TargetUserOrGroupType` 이 `Guest` 인 줄을 봅니다[2]. 감사 검색 결과를 내보낸 CSV 에서는 이 값들이 `AuditData` 열의 JSON 안에 들어 있어서 먼저 속성별 열로 펼쳐야 합니다[2]. 공유 기록에는 대상 사용자·그룹의 `TargetUserOrGroupName`·`TargetUserOrGroupType`, 후속 정보를 담은 `EventData`, 공유마다 붙는 `UniqueSharingId` 가 있습니다[6]. `SecureLinkCreated` 와 `AddedToSecureLink` 는 시각이 거의 같으므로[2] 타임라인에서 한 번의 공유로 묶습니다. 수집은 Microsoft-Extractor-Suite 의 `Get-UAL -Group Sharepoint` 처럼 `SharePointSharingOperation` 레코드 유형을 포함해 받습니다[18]. 수집 도구 전반은 [Microsoft 365 수집 도구](../../03-techniques/acquisition/m365-collection.md) 에 있습니다.

3. **Google Drive 에서 공유 범위가 바뀐 기록을 찾습니다.** 링크 공유 범위는 `change_document_visibility`, 링크로 주는 권한 종류는 `change_document_access_scope`, 사용자·그룹·도메인에 준 권한은 `change_user_access` 로 남습니다[9]. `visibility_change` 가 `external` 이면 파일의 전체 공개 범위가 조직 안에서 밖으로 바뀐 것이고[9], `change_document_visibility` 의 `new_value` 가 `people_with_link` 나 `public_on_the_web` 이면 링크만 있으면 조직 밖에서도 열 수 있게 된 것입니다[9]. 관리 콘솔의 보안 조사 도구에서는 데이터 원본을 Drive 로그 이벤트로 고르고, 조건을 Visibility change = External, Actor = 조사 대상 계정, Date 이후로 걸면 공유 시각·문서 ID·유형·공개 범위·제목·이벤트·행위자·소유자가 표로 나옵니다[11]. 한 번에 여러 사람에게 공유하면 받는 사람마다 `primary_event` 가 참인 접근 변경 이벤트가 생기므로[9], 공유 건수를 셀 때는 받는 사람 수만큼 늘어난다는 점을 감안합니다. 이벤트별 매개변수와 값 목록 전체는 [Drive 기록](../../02-artifacts/google-workspace/drive-audit.md) 에 있습니다.

4. **다른 SaaS 의 공유 기록을 같은 네 단계로 맞춥니다.**

   | 서비스 | 만들기 | 범위 바꾸기 | 쓰기(접근) | 없애기 |
   |---|---|---|---|---|
   | Box | `SHARE`(공유 링크 켬), `SHARED_LINK_SEND`(링크를 메일로 보냄), `COLLABORATION_INVITE`[13] | `ITEM_SHARED_UPDATE`, `SHARE_EXPIRATION`, `UPDATE_SHARE_EXPIRATION`, `COLLABORATION_ROLE_CHANGE`[13] | `DOWNLOAD`, `PREVIEW`. 로그인하지 않은 사용자는 사용자 ID `2`[13] | `UNSHARE`, `COLLABORATION_REMOVE`[13] |
   | Dropbox | `shared_link_create`(`shared_link_access_level`: `none`·`reader`·`writer`), `shared_content_add_member`[14] | `shared_link_change_visibility`(`new_value`·`previous_value`: `no_one`·`password`·`public`·`team_only`), `shared_link_settings_change_audience`, `shared_link_settings_change_expiration`[14] | `shared_link_view`, `shared_link_download`, `shared_link_copy`[14] | `shared_link_disable`[14] |
   | Slack | `file_public_link_created`, `file_shared`, `external_shared_channel_invite_created`, `external_shared_channel_connected`[15] | — | — | `file_public_link_revoked`[15] |
   | GitHub | `repo.access`(저장소 공개 범위 바뀜), `repo.pages_public`(Pages 사이트가 공개로 바뀜)[16] | `project.update_user_permission`[16] | — | `org.remove_outside_collaborator`[16] |

   Dropbox 의 `shared_link_access_level`·`previous_value` 와 `shared_link_view` 의 `shared_link_owner` 는 과거 자료의 빈틈 때문에 빠져 있을 수 있습니다[14]. Slack 의 `file_public_link_created`·`file_shared` 에는 행위자가 속한 팀의 식별자가 들어 있어서, 외부 조직과 함께 쓰는 공유 채널에서 누가 했는지 가려내는 데 씁니다[15]. GitHub 의 외부 협력자 변경은 Sigma 규칙 "Github Outside Collaborator Detected" 가 `org.remove_outside_collaborator`·`project.update_user_permission` 으로 잡습니다[19].

5. **링크로 실제 들어온 기록을 찾습니다.** Microsoft 365 는 `AnonymousLinkUsed`·`CompanyLinkUsed`·`SecureLinkUsed` 를 찾고, 외부인이 지정한 사람 링크를 쓴 경우는 `FileAccessed` 도 함께 찾습니다[1][2]. Google Drive 에서는 개인이나 특정 그룹으로 명시해 공유받은 경우가 아니면 도메인 밖 사용자가 anonymous 로 보이고, 로그인하지 않은 사용자의 편집·내려받기·보기도 기록됩니다[10]. 외부 사용자가 조직 소유 항목을 보거나 편집·내려받기·인쇄·삭제하면 기록은 우리 조직에만 남습니다[10]. Box 는 사용자 ID `2` 의 `DOWNLOAD` 를 찾고 같은 항목의 `SHARE` 시각과 맞춰 봅니다[13]. 접근 기록의 IP 해석은 [IP·사용자 에이전트·위치 정보](../../01-foundations/logging/ip-ua-geo.md) 를 봅니다.

6. **노출 기간을 계산합니다.** 노출 기간은 링크를 만든(또는 범위를 넓힌) 시각부터 없앤 시각이나 만료 시각까지입니다. Microsoft 365 에서 누구나 링크의 최대 만료 기간을 줄이면 기존 링크도 새 기간으로 짧아지고, 늘리면 기존 링크는 원래 만료 시각을 유지합니다[4]. 조직 구성원 링크에 만료 정책을 켜면 기존 링크는 바로 바뀌지 않고, 접근할 때 원래 만든 날짜를 기준으로 만료 여부를 판정합니다[3]. 외부 공유를 줄이거나 끄면 게스트는 보통 1시간 안에 접근을 잃고, 껐던 외부 공유를 다시 켜면 게스트가 접근을 되찾습니다[4]. 설정 변경 시각과 실제 접근 차단 시각 사이에 틈이 있다는 뜻이므로, 차단 직후의 접근 기록도 버리지 않고 봅니다.

7. **공유가 사용자의 동작인지, 설정이 물려준 결과인지 구분합니다.** Drive 에서 부모 폴더의 설정이 바뀌어 딸려서 바뀐 권한은 `change_document_visibility_hierarchy_reconciled`, `change_user_access_hierarchy_reconciled` 처럼 이름 끝에 `_hierarchy_reconciled` 가 붙은 이벤트로 남습니다[9]. Microsoft 365 에서 항목이 부모의 공유 권한을 더 이상 물려받지 않게 되면 `SharingInheritanceBroken` 이 남습니다[1]. 권한이 언제 누구에게서 이어졌는지 따라가는 방법은 [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md) 에 있습니다.

8. **공유 뒤에 자료를 가져갔는지 이어 봅니다.** 공유 링크로 연 사람이 내려받거나 동기화한 기록, 조직 밖으로 복사한 기록은 [클라우드 저장소에서 자료를 빼 갔나](storage-exfiltration.md) 에서 다룹니다. 조사 대상이 퇴사 예정자이고 개인 계정으로 공유한 경우라면 [퇴사자가 자료를 가져갔나](departing-employee.md) 의 기준선 비교를 함께 씁니다. 모든 기록은 [클라우드 타임라인](../../03-techniques/analysis/timeline.md) 한 줄로 합칩니다.

## 증명하는 것과 증명하지 못하는 것

공유 기록으로는 어느 계정이 언제 어느 항목을 어떤 범위로 열었거나 넓혔는지(작업 이름과 바뀌기 전후 값), 그리고 그 링크나 권한으로 접근한 기록이 남았는지를 증명할 수 있습니다. 지정한 사람 링크와 초대는 `TargetUserOrGroupName` 으로 대상 계정을 보여 줍니다[2][6].

증명하지 못하는 것은 링크를 받은 사람이 누구였는지입니다. 누구나 링크는 인증 없이 열리고 전달할 수 있으며, 조직 구성원 링크도 전달할 수 있습니다[3]. 링크가 어느 경로로 누구에게 넘어갔는지는 공유 기록에 없습니다. Google Drive 는 도메인 밖 사용자가 시작한 이벤트에 IP 를 기록하지 않아서[10] 외부 접근자를 IP 로도 좁히기 어렵습니다. 링크를 만든 기록만 있고 쓰기 기록이 없으면 "열어 두었다" 까지만 말할 수 있습니다. 링크를 없애면 그 링크로는 더 이상 열 수 없지만[3], 링크가 유효하던 동안 받은 사본이 받은 쪽에 남았을 가능성은 로그로 판단할 수 없습니다.

출처끼리 설명이 다른 곳이 두 군데 있습니다. SharePoint 링크 종류 문서는 누구나 링크로 한 접근은 감사할 수 없다고 적었고[3], 감사 활동 목록은 `AnonymousLinkUsed` 에 신원은 몰라도 IP 같은 정보가 남는다고 적었습니다[1]. 실제 로그에 `AnonymousLinkUsed` 가 있으면 그 IP 를 쓰되 사람을 특정한 근거로 쓰지 않습니다. 또 `TargetUserOrGroupType` 값을 공유 감사 문서는 Member, Guest, SharePointGroup, SecurityGroup, Partner 로[2], 관리 활동 API 스키마는 Member, Guest, Group, Partner 로[6] 적었으므로, 걸러 내기 전에 로그에 실제로 나오는 값을 먼저 세어 봅니다.

## 흔한 오판

- **`SharingInvitationCreated` 가 없으니 외부 공유도 없었다고 봅니다.** 이 작업은 사이트를 공유할 때만 남고, 파일을 외부인에게 공유하면 `SecureLinkCreated`·`AddedToSecureLink` 나 `AnonymousLinkCreated` 로 남습니다[2].
- **수집 도구의 기본 목록만 봅니다.** DFIR-O365RC 의 `Get-O365Light` 이 SharePoint·OneDrive·Teams 에서 고르는 작업 목록(`OneDrive_Sharepoint_Teams_YammerOnly_operations`)에는 `AnonymousLinkCreated`·`AnonymousLinkUsed`·`SharingInvitationAccepted`·`SharingInvitationBlocked`·`SharingPolicyChanged` 는 있지만 `SecureLinkCreated`·`AddedToSecureLink`·`CompanyLinkCreated`·`SharingSet` 은 없습니다[20]. 지정한 사람 링크까지 보려면 `Get-O365Full` 로 레코드 유형 단위로 받습니다[20].
- **`GroupAdded`·`AddedToGroup` 을 권한 상승으로 읽습니다.** 사용자가 처음 파일 공유 링크를 만들면 그 사용자의 OneDrive 사이트에 시스템 그룹이 생기면서 `GroupAdded` 가 남고, 편집 권한 링크를 만들 때도 생길 수 있습니다[1]. `AddedToGroup` 도 공유에 딸려 생길 수 있습니다[1].
- **"Shared externally" 표시를 외부인이 봤다는 뜻으로 읽습니다.** 외부 공유를 꺼 둔 상태에서 외부 사용자를 허용하는 그룹과 공유하면, 그룹에 외부 구성원이 없어도 로그에 Shared externally 로 표시되고 외부 사용자는 실제로 열 수 없습니다[10].
- **부모 폴더 공유로 바뀐 권한을 파일마다 따로 공유한 것으로 봅니다.** `_hierarchy_reconciled` 이벤트는 사용자가 파일마다 공유한 동작이 아닙니다[9].
- **초대받은 주소와 수락한 주소를 같은 사람으로 봅니다.** `SharingInvitationAccepted` 에는 초대받은 사용자와 수락에 쓴 이메일 주소가 함께 들어 있고, 둘은 다를 수 있습니다[1].
- **Drive 의 `target_user` 를 공유에 쓴 주소로 봅니다.** 한 Google 계정에 이메일 주소가 여럿이면 `target_user` 에는 공유에 쓴 주소가 아니라 표시 이메일이 들어갑니다[9]. 행위자도 별칭이 아니라 기본 주소로 남습니다[10].
- **`ClientIP` 를 공유한 사람의 기기 IP 로 단정합니다.** 일부 서비스에서는 사용자 대신 서비스를 부른 웹용 Office 같은 앱의 IP 가 들어갑니다[5].

## 보고서 문장 예

아래 계정·파일·시각은 만든 예시입니다. 보고서 전반의 틀은 [클라우드 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 에 있습니다.

- "2026년 3월 4일 01:12(UTC)에 계정 kim@contoso.com 으로 파일 `plan.xlsx` 에 대해 `AnonymousLinkCreated` 기록이 있고, 같은 파일에 대한 `AnonymousLinkRemoved` 기록은 3월 11일 08:40(UTC)에 있습니다. 이 기간에 `AnonymousLinkUsed` 기록이 3건 있고 IP 는 198.51.100.7 과 203.0.113.50 입니다. 이 기록으로는 링크를 연 사람을 특정할 수 없습니다."
- "Google Drive 로그 이벤트에 2026년 3월 5일 계정 lee@example.com 이 문서 ID 로 식별되는 파일의 링크 공유 범위를 `private` 에서 `people_with_link` 로 바꾼 `change_document_visibility` 기록이 있습니다. 그 뒤 같은 문서에 행위자가 anonymous 인 `download` 기록이 2건 있으며, 도메인 밖 사용자의 이벤트에는 IP 가 기록되지 않습니다."
- "조사 기간(2026년 1월 1일~3월 31일)에 SharePoint 공유 정책 변경(`SharingPolicyChanged`) 기록은 없습니다."

## 함께 볼 페이지

- 같은 분류: [클라우드 저장소에서 자료를 빼 갔나](storage-exfiltration.md), [퇴사자가 자료를 가져갔나](departing-employee.md)
- 아티팩트: [통합 감사 로그](../../02-artifacts/m365/unified-audit-log/index.md), [SharePoint·OneDrive](../../02-artifacts/m365/sharepoint-onedrive.md), [Drive 기록](../../02-artifacts/google-workspace/drive-audit.md), [관리 콘솔 감사 로그](../../02-artifacts/google-workspace/admin-audit.md), [Dropbox·Box 기록](../../02-artifacts/saas/dropbox-box.md), [Slack 감사 로그](../../02-artifacts/saas/slack.md), [GitHub 감사 로그](../../02-artifacts/saas/github.md)
- 기법: [권한 변화 따라가기](../../03-techniques/analysis/permission-changes.md), [클라우드 타임라인](../../03-techniques/analysis/timeline.md), [로그부터 지키기](../../03-techniques/acquisition/log-preservation.md)
- 다른 판: [보안 제품이 남기는 AI 사용 기록 (DLP·CASB)](https://urock-ailab.github.io/forensics-handbook/ai/02-artifacts/network-enterprise/dlp-casb.html), [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)

## 참고 문헌

1. Microsoft, "Audit log activities", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-activities
2. Microsoft, "Use sharing auditing in the audit log", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-sharing
3. Microsoft, "How shareable links work in OneDrive and SharePoint in Microsoft 365". https://learn.microsoft.com/en-us/sharepoint/shareable-links-anyone-specific-people-organization
4. Microsoft, "Manage sharing settings for SharePoint and OneDrive in Microsoft 365". https://learn.microsoft.com/en-us/sharepoint/turn-external-sharing-on-or-off
5. Microsoft, "Detailed properties in the audit log", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-detailed-properties
6. Microsoft, "Office 365 Management Activity API schema". https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-schema
7. Microsoft, "Manage audit log retention policies", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
8. Microsoft, "Search the audit log", Microsoft Purview. https://learn.microsoft.com/en-us/purview/audit-search
9. Google, "Drive Audit Activity Events", Admin SDK Reports API. https://developers.google.com/workspace/admin/reports/v1/appendix/activity/drive
10. Google, "Drive log events", Google Workspace Admin Help. https://support.google.com/a/answer/4579696
11. Google, "Investigate file sharing", Google Workspace Admin Help. https://knowledge.workspace.google.com/admin/security/investigate-file-sharing
12. Google, "Data retention and lag times", Google Workspace Admin Help. https://support.google.com/a/answer/7061566
13. Box, Box Developer Documentation, 기업 이벤트 안내(Enterprise events, for-enterprise). https://developer.box.com/guides/events/enterprise-events/for-enterprise/
14. Dropbox, dropbox-api-spec, team_log.stone. https://github.com/dropbox/dropbox-api-spec/blob/main/team_log.stone
15. Slack, "Audit Logs API" 와 "Actions" 목록. https://api.slack.com/admins/audit-logs , https://api.slack.com/admins/audit-logs-call
16. GitHub, "Audit log events for your organization". https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/audit-log-events-for-your-organization
17. GitHub, "Audit log for an enterprise", GitHub Enterprise Cloud Docs. https://docs.github.com/en/enterprise-cloud@latest/admin/monitoring-activity-in-your-enterprise/reviewing-audit-logs-for-your-enterprise/about-the-audit-log-for-your-enterprise
18. Invictus Incident Response, Microsoft-Extractor-Suite, Scripts/Get-UAL.ps1. https://github.com/invictus-ir/Microsoft-Extractor-Suite/blob/main/Scripts/Get-UAL.ps1
19. SigmaHQ, github_outside_collaborator_detected.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/application/github/audit/github_outside_collaborator_detected.yml
20. ANSSI, DFIR-O365RC, DFIR-O365RC/Get-O365.ps1 와 README.md. https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/DFIR-O365RC/Get-O365.ps1 , https://github.com/ANSSI-FR/DFIR-O365RC/blob/main/README.md
