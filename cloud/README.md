---
title: Cloud 개요
nav_order: -100
permalink: /
---

# 클라우드 디지털 포렌식 핸드북

Microsoft 365·Google Workspace·AWS·Azure·Google Cloud 와 업무용 SaaS 에 어떤 기록이 남는지, 그 기록을 어떻게 모으고 읽고 해석하는지 정리한 한국어 핸드북입니다.

클라우드 사건은 PC 한 대가 아니라 계정과 로그로 풀립니다. 그래서 로그인·권한·설정 변경·파일 접근 기록을 중심에 두고, 로그가 사라지기 전에 지키는 방법과 서비스마다 다른 보관 기간·라이선스 조건을 함께 다룹니다.

## 구성

핸드북은 네 부분으로 나뉩니다.

| 분류 | 다루는 것 |
|---|---|
| **기반 구조** | 책임 공유와 조사 범위, 테넌트·구독·계정 구조, 계정·역할·OAuth 동의·토큰·MFA, 로그 종류·보관 기간·JSON 형식·시각 |
| **아티팩트 사전** | Microsoft 365(통합 감사 로그·Entra·Exchange·SharePoint·Teams), Google Workspace, AWS(CloudTrail·IAM·S3·VPC Flow Logs), Azure, Google Cloud, Slack·GitHub·Okta 같은 업무용 SaaS |
| **분석 기법** | 로그 보존, 수집 도구, 데이터 요청, 가상 머신 수집, 타임라인, 이상한 로그인 가려내기, 권한 변화 따라가기, 탐지 규칙 활용 |
| **조사 시나리오** | "메일 계정을 빼앗겨 송금 사기를 당했나", "액세스 키가 새어 나갔나", "퇴사자가 자료를 가져갔나" 같은 질문 하나에 여러 기록을 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 어디서 보나 — 콘솔·API·내보내기, 보관 기간과 라이선스 조건
3. 구조 — 레코드 필드, 작업(이벤트) 이름
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 어떤 기준 시각을 쓰고, 기록이 늦게 들어오는지
6. 함정과 한계 — 켜야만 남는 기록, 자주 하는 오해
7. 직접 분석하기 — 레코드를 직접 읽어 한 번, 공개 도구로 한 번
8. 함께 볼 기록 — 다른 로그와 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 [기록은 어디에 남나](01-foundations/model/where-records-live.md)와 [보관 기간과 라이선스](01-foundations/logging/retention-licensing.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 먼저 [로그부터 지키기](03-techniques/acquisition/log-preservation.md)를 보고, 조사 시나리오에서 질문을 고르면 됩니다. 예: [메일 계정을 빼앗겨 송금 사기를 당했나](04-scenarios/account-compromise/bec.md), [액세스 키가 새어 나갔나](04-scenarios/infrastructure/leaked-keys.md)
- 특정 서비스만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 서비스 화면과 기본값은 2026년 9월 기준입니다. 보관 기간·라이선스처럼 자주 바뀌는 값은 그 자리에 기준 날짜를 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 테넌트 설정마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 로그 예시는 문서를 보고 만든 예시입니다. 실제 조직의 값이 아닙니다.
- 특정 회사 제품을 편들지 않고 같은 기준으로 씁니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.

# 목차


## 기반 구조

### 클라우드 조사의 구조

- [책임 공유와 조사 범위 (Shared Responsibility)](01-foundations/model/shared-responsibility.md)
- [테넌트·구독·계정·프로젝트 (Tenant·Subscription·Account·Project)](01-foundations/model/tenancy.md)
- [기록은 어디에 남나 (Where Records Live)](01-foundations/model/where-records-live.md)

### 계정과 인증

- [클라우드 계정과 역할 (Users·Roles·Service Accounts)](01-foundations/identity/users-roles.md)
- [OAuth 앱과 동의 (OAuth Apps·Consent)](01-foundations/identity/oauth-consent.md)
- [토큰과 세션 (Tokens·Sessions)](01-foundations/identity/tokens-sessions.md)
- [다단계 인증과 조건부 접근 (MFA·Conditional Access)](01-foundations/identity/mfa-conditional-access.md)
- [페더레이션과 SSO (Federation·SSO)](01-foundations/identity/federation-sso.md)

### 로그 체계

- [로그의 종류 (관리·데이터·로그인·흐름)](01-foundations/logging/log-types.md)
- [보관 기간과 라이선스 (Retention·Licensing)](01-foundations/logging/retention-licensing.md)
- [JSON 로그 읽기 (JSON Log Records)](01-foundations/logging/json-logs.md)
- [클라우드 로그의 시각 (Timestamps·Time Zones)](01-foundations/logging/timestamps.md)
- [IP·사용자 에이전트·위치 정보 (IP·User Agent·Geo)](01-foundations/logging/ip-ua-geo.md)

## 아티팩트 사전

### Microsoft 365

- [통합 감사 로그 (Unified Audit Log)](02-artifacts/m365/unified-audit-log/index.md)
  - [레코드 구조 (AuditData)](02-artifacts/m365/unified-audit-log/record-structure.md)
  - [검색과 내보내기 (Search·Export)](02-artifacts/m365/unified-audit-log/search-export.md)
  - [주요 작업 이름 (Operations)](02-artifacts/m365/unified-audit-log/operations.md)
- [Entra ID 로그 (Entra ID Logs)](02-artifacts/m365/entra-logs/index.md)
  - [로그인 로그 (Sign-in Logs)](02-artifacts/m365/entra-logs/sign-in-logs.md)
  - [감사 로그 (Audit Logs)](02-artifacts/m365/entra-logs/audit-logs.md)
  - [위험 탐지 (Identity Protection)](02-artifacts/m365/entra-logs/identity-protection.md)
- [Exchange Online (Exchange Online)](02-artifacts/m365/exchange-online/index.md)
  - [메일함 감사와 MailItemsAccessed (Mailbox Auditing)](02-artifacts/m365/exchange-online/mailbox-auditing.md)
  - [받은편지함 규칙과 전달 (Inbox Rules·Forwarding)](02-artifacts/m365/exchange-online/inbox-rules.md)
  - [메시지 추적 (Message Trace)](02-artifacts/m365/exchange-online/message-trace.md)
- [SharePoint·OneDrive (SharePoint·OneDrive)](02-artifacts/m365/sharepoint-onedrive.md)
- [Teams (Teams)](02-artifacts/m365/teams.md)
- [Purview eDiscovery와 보존 (eDiscovery·Retention)](02-artifacts/m365/purview-ediscovery.md)
- [Defender 경고와 기록 (Microsoft Defender XDR)](02-artifacts/m365/defender-xdr.md)

### Google Workspace

- [관리 콘솔 감사 로그 (Admin Audit)](02-artifacts/google-workspace/admin-audit.md)
- [로그인 기록 (Login Audit)](02-artifacts/google-workspace/login-audit.md)
- [Drive 기록 (Drive Audit)](02-artifacts/google-workspace/drive-audit.md)
- [Gmail 기록과 메일 검색 (Gmail Log Search)](02-artifacts/google-workspace/gmail.md)
- [OAuth 토큰 기록 (Token Audit)](02-artifacts/google-workspace/token-audit.md)
- [Vault와 Takeout (Vault·Takeout)](02-artifacts/google-workspace/vault-takeout.md)

### AWS

- [CloudTrail (CloudTrail)](02-artifacts/aws/cloudtrail/index.md)
  - [레코드 구조 (Event Record)](02-artifacts/aws/cloudtrail/record-structure.md)
  - [관리 이벤트와 데이터 이벤트 (Management·Data Events)](02-artifacts/aws/cloudtrail/event-types.md)
  - [트레일과 이벤트 기록 (Trails·Event History·Lake)](02-artifacts/aws/cloudtrail/trails.md)
- [IAM 사용자·역할·액세스 키 (IAM)](02-artifacts/aws/iam.md)
- [S3 접근 기록 (S3 Server Access Logs)](02-artifacts/aws/s3-access-logs.md)
- [VPC 흐름 로그 (VPC Flow Logs)](02-artifacts/aws/vpc-flow-logs.md)
- [GuardDuty (GuardDuty)](02-artifacts/aws/guardduty.md)
- [CloudWatch Logs (CloudWatch Logs)](02-artifacts/aws/cloudwatch-logs.md)
- [EC2 인스턴스와 스냅숏 (EC2·EBS Snapshots)](02-artifacts/aws/ec2-ebs.md)
- [Lambda·컨테이너 서비스 기록 (Lambda·ECS·EKS)](02-artifacts/aws/lambda-containers.md)

### Azure

- [활동 로그 (Activity Log)](02-artifacts/azure/activity-log.md)
- [리소스 로그와 진단 설정 (Resource Logs·Diagnostic Settings)](02-artifacts/azure/resource-logs.md)
- [네트워크 흐름 로그 (NSG·VNet Flow Logs)](02-artifacts/azure/flow-logs.md)
- [Storage 계정 기록 (Storage Logs)](02-artifacts/azure/storage-logs.md)
- [Key Vault 기록 (Key Vault Logs)](02-artifacts/azure/key-vault.md)
- [Azure 가상 머신 (Azure VM)](02-artifacts/azure/azure-vm.md)

### Google Cloud

- [Cloud Audit Logs (Cloud Audit Logs)](02-artifacts/gcp/cloud-audit-logs.md)
- [VPC 흐름 로그 (VPC Flow Logs)](02-artifacts/gcp/vpc-flow-logs.md)
- [Cloud Storage 기록 (Cloud Storage)](02-artifacts/gcp/cloud-storage.md)
- [IAM과 서비스 계정 키 (IAM·Service Account Keys)](02-artifacts/gcp/iam-keys.md)

### 업무용 SaaS

- [Slack 감사 로그 (Slack)](02-artifacts/saas/slack.md)
- [Dropbox·Box 기록 (Dropbox·Box)](02-artifacts/saas/dropbox-box.md)
- [GitHub 감사 로그 (GitHub)](02-artifacts/saas/github.md)
- [Okta 시스템 로그 (Okta)](02-artifacts/saas/okta.md)
- [Zoom 기록 (Zoom)](02-artifacts/saas/zoom.md)
- [Notion·Atlassian 기록 (Notion·Jira·Confluence)](02-artifacts/saas/notion-atlassian.md)

## 분석 기법

### 조사 절차·증거 확보

- [조사 절차 (Investigation Process)](03-techniques/acquisition/investigation-process.md)
- [로그부터 지키기 (Log Preservation)](03-techniques/acquisition/log-preservation.md)
- [Microsoft 365 수집 도구 (Microsoft-Extractor-Suite 등)](03-techniques/acquisition/m365-collection.md)
- [AWS·Azure·GCP 수집 (Cloud Log Collection)](03-techniques/acquisition/iaas-collection.md)
- [서비스 회사에 대한 데이터 요청 (Legal Requests)](03-techniques/acquisition/legal-requests.md)
- [클라우드 가상 머신 수집 (VM·Disk Acquisition)](03-techniques/acquisition/vm-acquisition.md)

### 분석

- [클라우드 타임라인 (Timeline)](03-techniques/analysis/timeline.md)
- [이상한 로그인 가려내기 (Suspicious Sign-ins)](03-techniques/analysis/suspicious-sign-ins.md)
- [권한 변화 따라가기 (Permission Changes)](03-techniques/analysis/permission-changes.md)
- [탐지 규칙으로 로그 검색하기 (Sigma·KQL)](03-techniques/analysis/detection-rules.md)

### 보고

- [클라우드 포렌식 보고서 (Forensic Report)](03-techniques/reporting/forensic-report.md)

## 조사 시나리오

### 계정 침해

- [메일 계정을 빼앗겨 송금 사기를 당했나 (BEC)](04-scenarios/account-compromise/bec.md)
- [악성 OAuth 앱에 동의했나 (Illicit Consent)](04-scenarios/account-compromise/illicit-consent.md)
- [토큰을 훔쳐 로그인했나 (Token Theft)](04-scenarios/account-compromise/token-theft.md)
- [MFA 피로 공격을 당했나 (MFA Fatigue)](04-scenarios/account-compromise/mfa-fatigue.md)

### 인프라 침해

- [액세스 키가 새어 나갔나 (Leaked Access Keys)](04-scenarios/infrastructure/leaked-keys.md)
- [권한을 올렸나 (Privilege Escalation)](04-scenarios/infrastructure/privilege-escalation.md)
- [채굴용 자원을 만들었나 (Cryptomining)](04-scenarios/infrastructure/cryptomining.md)
- [로그를 끄거나 지웠나 (Log Tampering)](04-scenarios/infrastructure/log-tampering.md)

### 자료 유출

- [클라우드 저장소에서 자료를 빼 갔나 (Storage Exfiltration)](04-scenarios/data-leak/storage-exfiltration.md)
- [퇴사자가 자료를 가져갔나 (Departing Employee)](04-scenarios/data-leak/departing-employee.md)
- [외부 공유 링크로 새어 나갔나 (External Sharing)](04-scenarios/data-leak/external-sharing.md)
