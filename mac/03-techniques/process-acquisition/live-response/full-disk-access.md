---
title: "전체 디스크 접근 권한"
parent: "라이브 대응"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 2020
---

# 전체 디스크 접근 권한 (Full Disk Access)

macOS 10.15부터 앱이 보호된 폴더를 읽으려면 사용자 동의가 필요해서, 라이브 수집 도구를 돌리기 전에 전체 디스크 접근 권한을 확인해야 하고, 권한을 준 기록은 시스템 TCC 데이터베이스에 남습니다.

## 언제 쓰나

켜진 맥에서 스크립트나 수집 도구로 사용자 자료를 모으기 전에 씁니다. macOS 10.15부터 앱이 Documents, Downloads, Desktop, iCloud Drive, 네트워크 볼륨의 파일에 접근하려면 사용자 동의가 필요하고 [1], 전체 디스크 접근 권한 (Full Disk Access, 이하 FDA)은 이 보호를 한꺼번에 넘는 권한입니다. FDA에 해당하는 서비스는 메일·메시지·사파리 같은 앱의 데이터에 접근하는 권한입니다 [3].

조사 대상 맥에서 어떤 앱이 FDA를 받았는지 따질 때도 이 페이지를 씁니다. 정보 탈취 악성 코드나 권한 우회를 조사할 때 이 기록이 단서가 되고, 조사 흐름은 [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](../../../04-scenarios/incident/privilege-tcc-bypass.md)과 [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md)에 있습니다.

## 버전별 차이

| macOS | 내용 |
|---|---|
| 10.15 Catalina 이후 | Documents, Downloads, Desktop, iCloud Drive, 네트워크 볼륨의 파일 접근에 사용자 동의가 필요 [1] |
| 12 Monterey 이하 | 저장 장치 전체에 접근해야 하는 앱은 시스템 환경설정에 직접 추가 [1] |
| 13 Ventura 이후 | 같은 일을 시스템 설정에서 함 [1] |
| 27 Golden Gate 이후 | 앱이 로컬 TCC 데이터베이스에 직접 접근할 수 없고, MDM 이 실행해도 되는 앱과 바이너리를 정할 수 있음 [7]. 앱 데이터 보호는 아래 "macOS 27 에서 수집할 때 확인할 점" 절 |

데스크탑·문서·다운로드·네트워크 볼륨·이동식 볼륨을 폴더 단위로 묶은 "파일 및 폴더" 권한은 사용자가 개인정보 설정에서 바꿀 수 있습니다 [1].

## 절차

1. 수집 도구를 무엇으로 띄울지 정합니다. Aftermath는 도구를 띄우는 터미널 앱에 FDA를 주면 됩니다 [5]. 원격 셸로 돌릴 때 어느 프로세스를 기준으로 권한을 따지는지 알려면 같은 macOS 버전의 시험용 맥에서 보호 폴더가 읽히는지 미리 확인합니다.
2. 도구에 필요한 권한을 확인합니다. 공개 수집 도구의 예로 Jamf Aftermath는 root 권한과 FDA를 둘 다 요구합니다 [5]. 이 요구는 root 만으로는 보호 영역을 다 읽지 못한다는 뜻으로 보이므로, root 로 돌린 결과에 보호 폴더가 비어 있으면 FDA부터 의심합니다.
3. FDA를 새로 주어야 하면 관리자 인증을 거쳐 줍니다. FDA를 주려면 관리자 인증이 필요하고 FDA 기록은 시스템 TCC 데이터베이스에 들어가서 [2], 권한을 주는 순간 조사 대상 맥의 이 데이터베이스가 바뀝니다. 준 시각, 앱 이름, 준 사람을 수집 기록에 적어 두어야 나중에 분석할 때 조사자가 만든 기록을 가려낼 수 있습니다.
4. 수집을 마친 뒤 권한을 거둘지는 기관 절차에 따릅니다. 거두는 일도 데이터베이스를 바꾸니 마찬가지로 시각을 적고, 조사 중에는 `tccutil reset` 을 쓰지 않습니다(아래 도구 절).

## macOS 27 에서 수집할 때 확인할 점

macOS 27 Golden Gate 에서는 FDA 를 준 것만으로 필요한 폴더를 다 읽는다고 볼 수 없습니다. SUMURI 지침서는 이 버전에서 다른 앱의 데이터 컨테이너에 접근하는 권한이 기본으로 거부되고, 이때 알림창도 뜨지 않으며, 사용자가 시스템 설정의 개인정보 보호 및 보안에서 관리한다고 봅니다 [6]. 같은 지침서는 XProtect 가 악성 코드가 자주 노리는 앱 데이터라고 판단한 곳의 접근을 따로 더 막을 수 있다고 보고, 베타 버전에서는 샌드박스를 쓰지 않는 서드파티 앱의 `Application Support` 폴더, 그중 브라우저 프로필 폴더까지 막혔다고 설명합니다 [6]. XProtect 가 막는 목록은 Apple 이 공개하지 않았습니다 [6].

SUMURI 지침서는 권한이 없는 도구가 오류를 내지 않고 그 폴더를 건너뛴다고 봅니다 [6]. 그래서 수집 전에 필요한 앱 폴더가 실제로 읽히는지 시험합니다. 이미 실행 중인 앱에는 바뀐 권한이 적용되지 않으므로, FDA 를 준 뒤에는 도구를 끝냈다가 다시 띄운 다음 시험합니다 [6].

기관이 관리하는 맥에서는 MDM 이 실행해도 되는 앱과 바이너리를 정할 수 있습니다 [7]. 수집 도구가 실행 허용 대상인지는 현장에 가기 전에 관리자와 확인합니다 [6].

macOS 27 에서는 앱이 로컬 TCC 데이터베이스에 직접 접근할 수 없어서 [7], 권한 기록을 실행 중인 맥에서 복사해 읽는 방법도 달라집니다. 위치 변화와 확인 방법은 [권한 DB 구조 (TCC.db)](../../../02-artifacts/credentials/tcc/tcc-db.md) 에 있습니다.

## 권한이 남는 곳

TCC 데이터베이스는 사용자별 `~/Library/Application Support/com.apple.TCC/TCC.db` 와 시스템 전체의 `/Library/Application Support/com.apple.TCC/TCC.db` 두 가지가 있고, FDA(`kTCCServiceSystemPolicyAllFiles`)는 시스템 쪽에만 들어갑니다 [2]. 한 기록에는 서비스, 클라이언트 식별자, 클라이언트 형식, 허가 값, 허가 이유, 허가 버전, 코드 요구사항, 수정 시각이 담깁니다 [2]. 열 이름과 값의 뜻, 수정 시각을 읽는 법은 [개인 정보 보호 권한 (TCC)](../../../02-artifacts/credentials/tcc/index.md)에서 다룹니다.

기관이 관리하는 맥이라면 MDM으로 권한 설정을 미리 내려보냈을 수 있습니다. 이때 쓰는 PPPC (Privacy Preferences Policy Control) 페이로드는 식별자가 `com.apple.TCC.configuration-profile-policy` 이고 macOS 전용입니다. 기기 관리 서비스로 설치하고 사용자 승인이 필요하며, 여러 개가 겹치면 가장 제한적인 설정이 적용됩니다 [3]. FDA에 해당하는 서비스 키는 `SystemPolicyAllFiles` 이고, 관리자용 파일 접근은 `SystemPolicySysAdminFiles` 입니다 [3]. 앱마다 적는 항목은 아래와 같습니다 [3].

| 키 | 뜻 |
|---|---|
| `Identifier` | 앱 식별자 |
| `IdentifierType` | 식별자가 번들 ID인지 경로인지 |
| `CodeRequirement` | 코드 요구사항. `codesign -dr -` 로 얻음 |
| `Allowed` | 허용 여부(참/거짓) |
| `Comment` | 설명 |

권한은 프로파일로도 줄 수 있어서, FDA의 출처를 따질 때는 TCC 데이터베이스와 함께 설치된 프로파일도 봅니다. 프로파일은 [구성 프로파일 (Configuration Profiles·MDM)](../../../02-artifacts/persistence/configuration-profiles.md)에서 다룹니다.

## 도구

`tccutil reset` 은 한 서비스에 대한 모든 결정을 지워 다음 접근 때 다시 묻게 하고, 번들 ID를 주면 그 앱의 결정만 지웁니다 [4]. 설명서에 나온 명령은 `reset` 하나이고, 서비스의 예로는 `AddressBook`, 번들 ID의 예로는 `com.apple.Terminal` 이 있습니다 [4]. macOS 27 에는 관리되는 기기에서 지정한 서비스나 앱의 현재 권한을 보여 주는 `tccutil list` 가 새로 생겼습니다 [7].

```
tccutil reset <서비스> [번들 ID]
```

이 명령은 TCC 기록을 바꾸니 조사 중에는 쓰지 않습니다. 반대로 조사 대상 맥에서 누군가 이 명령을 썼다면 그 전에 있던 결정이 사라졌을 수 있습니다.

## 함정과 한계

root 로 돌렸다고 보호 폴더까지 다 모았다고 보지 않습니다. 수집 결과에서 메일이나 메시지 폴더가 비어 있으면 원래 없었는지, FDA가 없어 못 읽었는지를 수집 기록과 도구 오류 출력으로 먼저 구분합니다.

FDA 없이 수집해도 도구가 뚜렷한 오류 없이 끝날 수 있고, 그러면 메일, 메시지, 사진 보관함, 사파리 기록과 데이터, 연락처와 캘린더, 메모, Time Machine 백업, `~/Library` 의 상당 부분이 빠진 이미지가 남습니다 [6]. 끝내 FDA 를 얻지 못했다면 그 사실과 그 때문에 이미지에서 빠진 영역을 수집 기록과 보고서에 적습니다 [6].

PPPC 페이로드에서 카메라·마이크·화면 기록은 거부만 할 수 있고 [3], FDA에 해당하는 `SystemPolicyAllFiles` 는 `Allowed` 값으로 허용할 수 있습니다 [3]. 그래서 관리되는 맥에서는 사용자가 설정 화면에서 켜지 않았어도 앱에 FDA가 있을 수 있습니다.

## 결과를 어떻게 해석하나

시스템 TCC 데이터베이스에 FDA 기록이 있으면 그 앱이 FDA를 받은 적이 있다는 뜻이고, 그 앱이 실제로 어떤 파일을 읽었는지까지는 알 수 없습니다. 보고서에는 "이 시각 기준으로 이 앱에 FDA가 허용된 기록이 있다" 까지만 쓰고, 실행 흔적은 [통합 로그의 프로세스 실행 기록 (Process Events)](../../../02-artifacts/execution/unified-log-process.md)과 맞춰 봅니다. 반대로 기록이 없다고 FDA를 준 적이 없다고 단정하지 않는데, `tccutil reset` 으로 결정이 지워졌을 수도 있고 [4] 프로파일로 설정했을 수도 있습니다.

## 참고 문헌

1. Apple Platform Security — Controlling app access to files — https://support.apple.com/guide/security/controlling-app-access-to-files-secddd1d86a6/web
2. Huntress, Full Transparency: Controlling Apple's TCC — https://www.huntress.com/blog/full-transparency-controlling-apples-tcc
3. Apple Platform Deployment — Privacy Preferences Policy Control payload settings — https://support.apple.com/guide/deployment/privacy-preferences-policy-control-payload-dep38df53c2a/web
4. tccutil(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/tccutil.1.html
5. Jamf, Aftermath README (GitHub) — https://github.com/jamf/aftermath
6. SUMURI, Mac Forensics Best Practices Guide, 2026 Edition (2026-09) — https://sumuri.com/
7. Apple Support, "What's new for enterprise in macOS Golden Gate 27" (2026-09-14) — https://support.apple.com/en-us/148830
