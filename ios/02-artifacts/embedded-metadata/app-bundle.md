---
title: "앱 번들 정보"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 1130
---

# 앱 번들 정보 (IPA·Info.plist)

## 한 줄 요약

아이폰 앱은 코드 서명과 팀 식별자로 누가 서명했는지 가를 수 있고, 관찰한 로컬 백업에서는 앱 번들이 보이지 않아 번들 ID 별 데이터 도메인과 백업 Info.plist·Manifest.plist 의 앱 관련 키, 설치 상태 plist 로 앱 정보를 읽습니다(확인 범위: iPhone 13 mini, iOS 27.0).

## 무엇을 기록하나 · 왜 생기나

앱 번들 (app bundle) 은 앱의 실행 파일과 자원을 묶은 폴더이고, iOS 는 실행할 때 코드 서명을 검사합니다. Apple 기본 앱(Mail·Safari 등)은 Apple 이 서명하고, 다른 회사 앱은 Apple Developer Program 에 가입한 개발자가 서명하며, 가입할 때 Apple 이 개발자의 실제 신원을 확인합니다[1]. 기업 내부용 앱은 Apple Developer Enterprise Program (ADEP) 에 가입한 조직이 서명합니다[1]. 그래서 앱 하나를 두고 "누가 서명했는가" 를 물으면 Apple 기본 앱, 스토어용 개발자 앱, 기업 내부용 앱 가운데 어디에 속하는지 가를 수 있습니다.

조사 현장에서 앱 정보를 직접 읽는 곳은 주로 로컬 백업입니다. 로컬 백업에는 앱 목록 키와 번들 ID 별 앱 데이터 도메인이 있어서(확인 범위: iPhone 13 mini, iOS 27.0), 번들 파일을 열지 않고도 어떤 번들 ID 의 앱 데이터가 백업에 들어갔는지 알 수 있습니다. 백업 형식 전체는 [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../01-foundations/backups/local-backup/index.md)에서, 번들 ID 를 읽는 법은 [번들 ID와 앱 그룹 (Bundle ID·App Group)](../../01-foundations/value-decoding/bundle-id-app-group.md)에서 다룹니다.

이번 판에서는 앱 번들 안의 파일 구성, 번들 Info.plist 의 키 이름, 앱 배포 파일 (IPA) 의 내부 구성과 구매 정보 파일을 공식 출처로 확인하지 못했습니다. 그래서 이 페이지는 서명의 뜻과 백업에 남는 앱 정보만 다루고, 번들 내부 구조는 확인한 뒤에 채웁니다.

## 위치와 버전별 차이

아래 위치는 모두 한 기기의 로컬 백업에서 이름만 확인한 것이고, 값은 읽지 않았습니다.

| 대상 | 위치 | 확인 범위 |
|---|---|---|
| 백업 Info.plist | 백업 폴더 최상위 `Info.plist` | iPhone 13 mini, iOS 27.0 |
| Manifest.plist | 백업 폴더 최상위 `Manifest.plist` | iPhone 13 mini, iOS 27.0 |
| 파일 목록 DB | 백업 폴더 최상위 `Manifest.db`(`-shm`·`-wal` 함께 있음) | iPhone 13 mini, iOS 27.0 |
| 기본 앱 설치 상태 | InstallDomain :: `Library/MobileInstallation/BackedUpState/SystemAppInstallState.plist`, 같은 폴더의 `BackupSystemAppInstallState.plist` | iPhone 13 mini, iOS 27.0 |
| 설치 관련 설정 | HomeDomain :: `Library/Preferences/com.apple.mobile.installation.plist` | iPhone 13 mini, iOS 27.0 |
| 앱 상태 DB | HomeDomain :: `Library/FrontBoard/applicationState.db` | iPhone 13 mini, iOS 27.0 |
| 설치 도우미 로그 도메인 | `SysSharedContainerDomain-systemgroup.com.apple.mobile.installationhelperlogs`(항목 5개) | iPhone 13 mini, iOS 27.0 |

iOS 15 이후 버전마다 이 위치가 어떻게 달라졌는지는 확인하지 못했습니다. 다른 버전의 백업을 볼 때는 같은 경로가 있는지부터 Manifest.db 로 확인합니다.

## 구조

### 서명과 팀 식별자

팀 식별자 (Team ID) 는 영문과 숫자로 된 10자리 문자열(예: `1A2B3C4D5F`)입니다[1]. 앱은 같은 팀 식별자로 서명한 라이브러리나 시스템 라이브러리에만 연결 (link) 할 수 있고, 프로세스가 실행될 때 iOS 는 연결하는 동적 라이브러리의 코드 서명을 모두 검사하며, 이때 Apple 이 발급한 인증서에서 뽑은 팀 식별자를 씁니다[1]. 필수 코드 서명은 서명 없는 코드를 불러오거나 스스로 바뀌는 코드를 쓰지 못하게 막습니다[1].

기업 내부용 앱은 흐름이 다릅니다. ADEP 조직은 프로비저닝 프로필 (provisioning profile) 을 받아 자체 앱을 허가한 기기에서 돌릴 수 있고, 이때 사용자가 프로필을 설치해야 하며, 자체 앱을 처음 실행할 때 기기가 Apple 로부터 실행을 허용받아야 합니다[1]. 이 사실을 탐지 쪽에서 읽으면, 기업 서명 앱이나 설치된 프로필은 App Store 밖에서 앱이 들어온 흔적이 됩니다. 이 해석은 [1] 의 사실에서 끌어낸 추론이고, 프로필이 기기 어디에 남는지는 [구성 프로파일과 MDM (Configuration Profiles·MDM)](../credentials-security/configuration-profiles.md)에서 다룹니다.

### 백업 Info.plist 와 Manifest.plist 의 앱 관련 키

백업 폴더 최상위의 `Info.plist` 는 기기 앱 번들 안의 Info.plist 와 다른 파일입니다. 관찰한 백업에서 두 plist 에 있던 키 가운데 앱과 관련된 것은 아래와 같습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 파일 | 앱 관련 키 | 그 밖의 키(일부) |
|---|---|---|
| 백업 `Info.plist` | `Applications`, `Installed Applications`, `iTunes Files`, `iTunes Settings` | `Build Version`, `Product Version`, `Product Type`, `Last Backup Date`, `Serial Number`, `IMEI`, `MEID`, `Unique Identifier`, `Target Identifier` |
| `Manifest.plist` | `Applications` | `IsEncrypted`, `Version`, `Containers`, `Date`, `SystemDomainsVersion`, `WasPasscodeSet`, `Lockdown`, `BackupKeyBag` |

관찰할 때 값과 하위 키는 읽지 않았으므로, `Applications` 아래에 어떤 하위 키가 있는지는 여기서 밝히지 않습니다. 기기 식별 키는 [기기 정보 (Device Info·Lockdown)](../system-account/device-info.md)에서 다룹니다.

### 도메인 이름 규칙

Manifest.db 의 `Files` 표(`fileID`, `domain`, `relativePath`, `flags`, `file`)는 백업에 들어간 파일마다 한 행이고, `domain` 칸의 이름으로 앱을 가를 수 있습니다(확인 범위: iPhone 13 mini, iOS 27.0).

```
AppDomain-<번들 ID>          앱 데이터
AppDomainGroup-<그룹 ID>     앱 그룹 공유 데이터
AppDomainPlugin-<번들 ID>    앱 확장(플러그인)
```

관찰한 백업에는 도메인이 모두 1428개 있었고, 여기에는 HomeDomain·InstallDomain 같은 시스템 도메인도 들어 있습니다(확인 범위: iPhone 13 mini, iOS 27.0). 앱 하나가 앱 데이터·앱 그룹·확장 도메인을 여러 개 만들 수 있어서, `AppDomain` 으로 시작하는 도메인 수를 그대로 앱 수로 세면 부풀려집니다.

### 설치 상태 파일

InstallDomain 에는 항목이 6개 있었고, 그 가운데 `SystemAppInstallState.plist` 와 `BackupSystemAppInstallState.plist` 는 Apple 기본 앱의 번들 ID(`com.apple.iBooks`, `com.apple.DocumentsApp`, `com.apple.mobilesafari` 등)를 키로, int 를 값으로 적습니다(확인 범위: iPhone 13 mini, iOS 27.0). int 값이 설치됨·삭제됨 같은 상태를 뜻하는지는 확인하지 못했습니다. HomeDomain 의 `com.apple.mobile.installation.plist` 에는 `ExtensionDataContainerParentIDUpdateVersion`(int) 키 하나만 보였습니다(확인 범위: iPhone 13 mini, iOS 27.0).

`applicationState.db` 는 번들 ID 와 앱 상태 값을 잇는 DB 이고, 표 구조와 해석은 [설치된 앱 (Installed Apps·applicationState.db)](../app-usage/installed-apps.md)에서 다룹니다. 설치 도우미 로그 도메인 안의 파일 형식은 관찰 메모에 없어서 이번 판에서는 도메인 이름만 적어 둡니다.

## 증거로서 의미

**증명하는 것**

`AppDomain-` 도메인에 어떤 번들 ID 가 있으면, 백업을 만든 시점에 그 번들 ID 의 앱 데이터가 백업에 들어갔다는 사실을 말할 수 있습니다. 앱 번들의 서명을 직접 읽을 수 있는 경우라면, Apple 기본 앱, 개발자 앱, 기업 내부용 앱 가운데 어디서 서명했는지와, 개발자 앱이면 Apple 이 신원을 확인한 개발자 계정으로 서명했다는 점을 말할 수 있습니다[1]. 로컬 백업만으로는 이 부분을 읽지 못하는 점은 아래에 적었습니다.

**증명하지 못하는 것**

도메인이 있다고 해서 사용자가 그 앱을 실행했거나 언제 설치했는지까지 알 수는 없고, 누가 설치했는지도 이 기록만으로는 알 수 없습니다. 실행과 사용은 [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md)와 [바이옴 (Biome)](../app-usage/biome/index.md)으로, 내려받기는 [앱 스토어 기록 (App Store)](../app-usage/app-store.md)으로 따로 확인합니다. 관찰한 백업에서는 앱 번들 경로가 보이지 않았으므로(확인 범위: iPhone 13 mini, iOS 27.0), 백업만으로 번들의 서명 인증서나 팀 식별자를 직접 읽을 수 있다고 쓰지 않습니다.

보고서에는 "백업에 이 번들 ID 의 앱 데이터 도메인이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

관찰한 파일에서 시각으로 보이는 키는 아래와 같고, 모두 뜻이나 기준이 확인되지 않았습니다(확인 범위: iPhone 13 mini, iOS 27.0).

| 키 | 위치 | 주의 |
|---|---|---|
| `Last Backup Date` | 백업 `Info.plist` | 이름으로 보아 백업 시각이지만, UTC 인지 현지 시각인지 확인하지 못했습니다. |
| `Date` | `Manifest.plist` | 키 이름만 확인했습니다. |
| `LastOSInstallDate`(datetime) | HomeDomain :: `Library/Preferences/com.apple.appstored.plist` | 이름으로 보아 앱이 아니라 OS 설치 날짜이고, 뜻은 확인하지 못했습니다. |
| `lastAppInstallDate`(datetime) | HomeDomain :: `Library/Preferences/com.apple.siri.sirisuggestions.plist` | 앱 설치 기록 파일이 아니라 시리 제안 설정 파일에 있고, 뜻은 확인하지 못했습니다. |

plist 의 날짜 값을 읽는 법은 [시각 값 (Mac 절대 시각·Unix·기타)](../../01-foundations/value-decoding/time-values.md)에서 다룹니다. 앱별 설치 시각은 이 표의 키로 정하지 말고 설치된 앱·앱 스토어 페이지의 기록과 함께 봅니다.

## 함정과 한계

가장 흔한 혼동은 이름이 같은 두 Info.plist 입니다. 백업 폴더의 `Info.plist` 는 백업 정보를 담은 파일이고 앱 번들의 Info.plist 와 다른 파일이라서, 여기서 읽은 값을 앱이 스스로 적은 번들 정보로 보고하면 안 됩니다.

`LastOSInstallDate` 와 `lastAppInstallDate` 는 이름만 보면 설치 시각처럼 읽히지만, 앞의 것은 OS 쪽 키로 보이고 뒤의 것은 시리 제안 설정 파일에 들어 있습니다. 두 키 모두 뜻이 확인되지 않았으므로 앱 설치 시각의 근거로 쓰지 않습니다. `SystemAppInstallState.plist` 의 int 값도 같은 이유로 해석하지 않고 그대로 인용합니다.

도메인이 없다는 사실만으로 앱이 없었다고 말하지 않습니다. 앱 도메인이 백업에서 빠지는 조건은 이번 판에서 확인하지 못했습니다. 앱을 지운 뒤에 백업에 무엇이 남는지는 이번 판에서 확인하지 못했고, 지우기 흔적 전반은 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.

## 직접 분석해 보기

**헥스로 한 번.** 백업 폴더의 `Info.plist` 와 `Manifest.plist` 를 헥스 편집기로 열어 첫 바이트를 보면 XML plist 인지 바이너리 plist 인지 가를 수 있습니다. 형식별 머리 바이트와 바이너리 plist 의 객체 표 읽는 법은 [속성 목록 파일 (plist·NSKeyedArchiver)](../../01-foundations/data-formats/plist.md)에 있고, 이 페이지에서는 검체에서 나온 바이트를 예로 들지 않습니다. 형식을 가린 뒤 `Applications` 와 `Installed Applications` 키 문자열이 어디 있는지 찾아 두면 도구 출력과 맞춰 볼 수 있습니다.

**공개 도구로 한 번.** SQLite 명령줄 도구 `sqlite3` 로 Manifest.db 를 열어 앱 관련 도메인과 항목 수를 뽑습니다. 원본을 바꾸지 않도록 사본을 엽니다.

```sql
-- AppDomain, AppDomainGroup, AppDomainPlugin 을 모두 잡는다
SELECT domain, COUNT(*) AS items
FROM Files
WHERE domain LIKE 'AppDomain%'
GROUP BY domain
ORDER BY domain;

-- 설치 상태 파일이 있는 InstallDomain 항목
SELECT fileID, relativePath, flags
FROM Files
WHERE domain = 'InstallDomain';
```

`fileID` 로 백업 폴더 안의 실제 파일을 찾는 법과 `flags` 의 뜻은 로컬 백업 페이지에서 다룹니다. 찾은 plist 는 공개 plist 도구로 키와 값을 확인합니다.

## 교차 검증

| 확인할 것 | 볼 페이지 |
|---|---|
| 번들 ID 별 앱 상태 | [설치된 앱 (Installed Apps·applicationState.db)](../app-usage/installed-apps.md) |
| 내려받기·구매 기록 | [앱 스토어 기록 (App Store)](../app-usage/app-store.md) |
| App Store 밖 설치에 쓰인 프로필 | [구성 프로파일과 MDM (Configuration Profiles·MDM)](../credentials-security/configuration-profiles.md) |
| 실행과 사용 | [KnowledgeC (knowledgeC.db)](../app-usage/knowledgec/index.md), [바이옴 (Biome)](../app-usage/biome/index.md) |
| 수상한 앱 가려내기 | [악성 코드·스파이웨어 흔적 (Malware·Spyware Triage)](../../03-techniques/analysis/spyware-triage/index.md), [악성 코드는 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md) |

## 실습

공개 검체(NIST CFReDS 등에서 받을 수 있는 아이폰 로컬 백업)나 직접 만든 시험 기기의 백업으로 아래 질문을 풀어 봅니다.

1. Manifest.db 에서 `AppDomain-` 도메인은 몇 개이고, `AppDomainGroup-`·`AppDomainPlugin-` 까지 합치면 몇 개인가? 두 숫자의 차이는 무엇 때문인가?
2. 백업 `Info.plist` 의 `Installed Applications` 에 있는 번들 ID 가운데 `AppDomain-` 도메인이 없는 것이 있는가? 있다면 어떤 이유를 생각해 볼 수 있는가?
3. `SystemAppInstallState.plist` 와 `BackupSystemAppInstallState.plist` 에서 같은 번들 ID 의 값이 다른 항목이 있는가? 값의 뜻을 확인하지 못했다면 보고서에 어떻게 적겠는가?
4. `Last Backup Date` 를 백업 폴더의 파일 시스템 시각과 비교해 시간대 기준을 추정해 본다.

## 참고 문헌

1. Apple, "App code signing process in iOS and iPadOS", Apple Platform Security — https://support.apple.com/guide/security/app-code-signing-process-sec7c917bf14/web
