---
title: "계정"
parent: "아티팩트 · 시스템·계정"
nav_order: 320
has_children: true
has_toc: false
---

# 계정 (Accounts)

## 한 줄 요약

Android 의 계정 목록은 시스템 서비스 AccountManagerService 가 관리하고, AccountsDb 가 사용자마다 SQLite 파일 두 개(`accounts_de.db`, `accounts_ce.db`)에 나눠 저장하며, 여기에 구글·삼성 같은 서비스 계정과 여러 앱이 등록한 계정이 이름(name)과 종류(type)의 쌍으로 함께 남습니다 [1][2][3].

## 왜 중요한가

계정 목록을 보면 이 기기에서 어떤 서비스 계정이 쓰였는지 알 수 있어서, 클라우드에 따로 요청할 데이터를 정하거나 앱 데이터의 주인을 가리는 출발점이 됩니다. DE 파일에는 이름·종류와 함께 앱별 권한 부여·가시성, 최대 64줄의 계정 추가·삭제 기록(`debug_table`)이 들어가서 계정을 언제 넣고 뺐는지를 제한된 범위에서 되짚을 수 있습니다 [1]. CE 파일에는 비밀번호와 인증 토큰 같은 민감한 값이 들어가고, 사용자가 잠금을 푼 뒤에야 열립니다 [1][2].

계정 DB 와 따로, 계정과 동기화 대상의 조합마다 동기화 설정과 마지막 성공·실패 시각이 `/data/system/sync/` 아래 파일에 남습니다 [4]. 라이브 기기에서는 adb 일반 셸 권한의 `dumpsys account` 로 계정 목록과 변경 기록(Accounts History)을 볼 수 있었습니다. (확인 범위: Android 16, One UI 8.5)

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| `/data/system_de/<사용자ID>/accounts_de.db` | 현행 AOSP 기준(두 파일로 나뉜 시점은 확인 못 함) | 계정 이름·종류, 바꾸기 전 이름, 앱별 권한 부여·가시성, 최대 64줄의 변경 기록 |
| `/data/system_ce/<사용자ID>/accounts_ce.db` | 현행 AOSP 기준 | 비밀번호·인증 토큰·부가 값(잠금 해제 뒤에 열림) |
| `accounts.db` | Android N 이전(상수 이름 기준) | 두 파일로 나뉘기 전의 한 파일, 경로는 확인 못 함 |
| `/data/system/sync/` (`accounts.xml`, `status`, `stats`) | 현행 AOSP 기준 | 계정·동기화 대상별 설정과 마지막 동기화 상태 |
| `dumpsys account` 출력 | Android 16 에서 관찰 | 사용자별 계정 목록과 Accounts History (확인 범위: Android 16, One UI 8.5) |
| `settings` 의 계정 관련 키 | Android 16 에서 관찰 | 구글·삼성 계정, 동의, 기기 이전과 관련된 이름의 키(뜻은 대부분 확인 못 함) |

계정 DB 두 파일의 전체 경로는 ALEAPP 가 찾는 경로 패턴에서 읽어 냈고, 자세한 근거는 아래 "계정 DB 구조" 페이지에 있습니다.

## 읽는 순서

1. [계정 DB 구조 (accounts_ce.db·accounts_de.db)](accounts-db.md) — 두 파일의 경로와 표·칸, 변경 기록(`debug_table`)의 동작 종류와 64줄 상한, 잠금 해제 때 CE·DE 를 맞추는 과정, 시각 칸의 해석, dumpsys 출력 모양, 헥스와 SQL 로 직접 읽는 법을 다룹니다.
2. [구글 계정 흔적 (Google Account)](google-account.md) — 구글 계정 행을 가리는 법과 주의점, 모든 계정이 함께 쓰는 동기화 파일(`/data/system/sync/`)의 구조, 구글 관련 설정 키와 패키지를 다룹니다.
3. [삼성 계정 흔적 (Samsung Account)](samsung-account.md) — 삼성 기기 설정에 남는 삼성 계정·동의·기기 이전 관련 키와, 이번에 확인하지 못한 삼성 계정 앱 내부 기록의 범위를 다룹니다.

## 함께 볼 페이지

- [사용자와 프로필 (Multi-user·users)](../users-profiles.md), [설정 값 (Settings Global·Secure·System)](../settings.md), [시간대와 시각 설정 (Time Zone)](../time-zone.md) — 계정 DB 를 사용자별로 나누고 시각을 읽을 때 함께 보는 시스템 기록
- [저장 공간 암호화 (Encryption)](../../../01-foundations/storage/encryption/index.md), [SQLite 데이터베이스 (SQLite)](../../../01-foundations/data-formats/sqlite/index.md), [패키지 이름과 UID (Package Name·UID)](../../../01-foundations/value-decoding/package-uid.md) — 파일을 직접 읽을 때 필요한 기초
- [저장된 암호 (Google 비밀번호 관리자·Samsung Pass)](../../credentials-security/saved-passwords.md), [클라우드 데이터 (Google Takeout 등)](../../../03-techniques/acquisition/cloud-data.md) — 계정과 이어지는 자격 증명과 서버 쪽 데이터
- [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../../04-scenarios/activity/user-attribution.md), [계정 탈취 흔적 (Account Takeover)](../../../04-scenarios/incident/account-takeover.md) — 계정 기록을 쓰는 조사 시나리오

## 참고 문헌

1. AccountsDb.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/accounts/AccountsDb.java
2. AccountManagerService.java — AOSP frameworks/base (GitHub 미러, main, 일부만 읽음), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/accounts/AccountManagerService.java
3. AccountManager — Android Developers API 참조, https://developer.android.com/reference/android/accounts/AccountManager
4. SyncStorageEngine.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/content/SyncStorageEngine.java
