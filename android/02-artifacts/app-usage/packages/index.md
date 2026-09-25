---
title: "설치된 앱"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 410
has_children: true
has_toc: false
---

# 설치된 앱 (packages.xml)

## 한 줄 요약

패키지 관리자(PackageManager)는 `/data/system/` 의 `packages.xml` 과 `packages.list` 에 설치된 앱의 목록과 설치 정보를 적고, 사용자별 설치 상태와 권한 부여 상태는 사용자별 파일에 따로 적습니다 [1].

## 왜 중요한가

앱 데이터 폴더만 봐서는 그 앱이 언제, 어떤 경로로 들어왔는지 알기 어렵습니다. 이 파일들에는 앱마다 이름·코드 경로·버전·설치자·시각·서명이 적혀 있고, 사용자별 파일에는 첫 설치 시각과 설치 이유, 앱이 받은 런타임 권한이 적혀 있습니다 [1]. 그래서 "이 앱은 어디서 들어왔나", "이 사용자에게 언제 처음 설치됐나", "이 앱에 위치 권한이 있었나" 같은 질문에 앱 자체의 데이터와 따로 답할 수 있는 시스템 쪽 기록이 됩니다.

다만 현행 AOSP 는 이 설정 파일들을 기본적으로 안드로이드 바이너리 XML(ABX)로 저장하기 때문에 [1][2], 먼저 일반 XML 로 풀어야 읽을 수 있습니다. 라이브 기기에서는 `dumpsys package` 로 같은 정보를 볼 수 있습니다. adb 일반 셸 권한으로도 실행되고, 시스템 앱 486개와 사용자가 설치한 앱 168개가 있는 폰에서는 약 192,000 줄이 나옵니다. 루팅되지 않은 기기에서 adb 일반 권한으로 `packages.xml` 을 직접 읽을 수 있다는 공개 자료는 없습니다.

## 한눈에 보기

| 위치 | Android 버전 | 알려 주는 것 |
|---|---|---|
| `/data/system/packages.xml` (사본 `packages-backup.xml`, `packages.xml.reservecopy`) | 현행 AOSP 기준 | 설치 앱 목록, 코드 경로, 버전, 설치자, 업데이트 시각, 서명 [1] |
| `/data/system/packages.list` | 현행 AOSP 기준 | 앱마다 UID·데이터 경로·설치자를 한 줄로 적은 요약 [1] |
| `/data/system/users/<사용자ID>/package-restrictions.xml` | 현행 AOSP 기준 | 사용자별 설치 여부, 첫 설치 시각, 설치 이유, 실행한 적 없음 표시 [1] |
| `/data/system/users/<사용자ID>/runtime-permissions.xml` | Android 10 이하 [5] | 사용자별 런타임 권한 부여 상태와 flags [1] |
| `/data/misc_de/<사용자ID>/apexdata/com.android.permission/runtime-permissions.xml` | Android 11 부터 [5] | 위와 같은 권한 기록(요소 이름은 다름) [3] |
| `dumpsys package` 출력 | Android 16 기준 | 라이브 기기의 같은 정보 |

공개 도구로는 ALEAPP 에 packageInfo, permissions, runtimePerms, packageRestrictions, packageUserStates, installSessions 모듈이 있습니다 [4]. 이 가운데 packageInfo·permissions·runtimePerms 가 무엇을 읽는지는 아래 하위 페이지에서 다룹니다.

## 읽는 순서

1. [패키지 목록 구조 (packages.xml·packages.list)](packages-xml.md) — `/data/system/` 의 파일 구성과 사본, ABX 저장, `packages.xml` 의 요소와 속성, `packages.list` 의 칸, 라이브 기기의 dumpsys 출력 모양을 다룹니다.
2. [설치 출처와 설치 시각 (Installer·Install Time)](install-source-time.md) — 설치자·설치 요청 앱·원 출처 칸의 뜻, 사용자별 첫 설치 시각과 설치 이유, 기기에서 본 설치 관련 앱을 정리합니다.
3. [앱 권한 부여 기록 (Runtime Permissions)](runtime-permissions.md) — `runtime-permissions.xml` 의 두 위치와 구조, flags 비트의 뜻, 부여 상태를 읽을 때의 함정을 다룹니다.

## 함께 볼 페이지

- [안드로이드 바이너리 XML (ABX)](../../../01-foundations/data-formats/abx.md), [패키지 이름과 UID](../../../01-foundations/value-decoding/package-uid.md), [시각 값](../../../01-foundations/value-decoding/time-values.md) — 파일을 직접 읽을 때 필요한 기초
- [앱 샌드박스와 권한 (Sandbox·Permissions)](../../../01-foundations/security-model/sandbox-permissions.md) — 권한 체계 자체
- [앱 사용 기록 (usagestats)](../usagestats/index.md), [구글 플레이 기록 (Play Store)](../play-store.md), [APK 정보 (AndroidManifest·서명)](../../embedded-metadata/apk.md) — 설치된 앱을 다른 쪽에서 남기는 기록
- [dumpsys 출력 (dumpsys)](../../logs/dumpsys.md) — 라이브 기기에서 서비스 상태를 뽑는 방법
- [악성 앱은 어디서 들어왔나 (Initial Access)](../../../04-scenarios/incident/initial-access.md), [몰래 설치된 감시 앱 (Stalkerware)](../../../04-scenarios/incident/stalkerware.md) — 이 기록을 쓰는 조사 시나리오

## 참고 문헌

1. Settings.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/Settings.java
2. Xml.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/core/java/android/util/Xml.java
3. ALEAPP runtimePerms.py — abrignoni/ALEAPP, https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/runtimePerms.py
4. ALEAPP scripts/artifacts 목록 — GitHub API, https://api.github.com/repos/abrignoni/ALEAPP/contents/scripts/artifacts
5. D20 Forensics, "Android - Roles and Permissions (Android 10/11)", https://blog.d204n6.com/2021/01/android-roles-and-permissions-android.html
