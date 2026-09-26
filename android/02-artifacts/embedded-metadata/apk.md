---
title: "APK 정보"
parent: "아티팩트 · 파일 내장 메타데이터"
nav_order: 1270
---

# APK 정보 (AndroidManifest·서명)

APK 파일은 ZIP 묶음 안에 이진 형식으로 컴파일한 매니페스트(AndroidManifest.xml)와 리소스를 담고, 서명 방식에 따라 META-INF 디렉터리나 APK 서명 블록(APK Signing Block)에 서명 인증서를 담아서, 파일 하나만 있어도 패키지 이름·요청 권한과 이 파일에 서명한 키의 인증서를 확인할 수 있습니다 [1][2][3].

## 무엇을 기록하나 · 왜 생기나

앱의 매니페스트와 리소스는 앱을 만들 때 AAPT2 가 이진(binary) 형식으로 컴파일하고, AAPT2 는 링크(link) 단계에서 리소스 표, 이진 XML 파일, 처리한 PNG 같은 결과물을 APK 하나로 묶습니다 [3]. 그래서 APK 를 ZIP 으로 풀어도 AndroidManifest.xml 을 텍스트 편집기로 바로 읽을 수 없고, 이진 XML 을 풀어 주는 도구를 거쳐야 패키지 이름과 권한이 보입니다.

서명은 파일이 서명한 뒤로 바뀌지 않았는지 확인하려고 붙입니다. v1(JAR 서명)은 서명을 META-INF 디렉터리에 두지만 ZIP 메타데이터 같은 APK 의 일부를 보호하지 않고, v2 이후 방식은 서명 결과를 APK 서명 블록에 담아 APK 안에 끼워 넣습니다 [1]. 블록 안의 서명자(signer) 블록에는 서명한 데이터(다이제스트 목록, X.509 인증서 체인, 추가 속성)와 서명 값, 공개 키(SubjectPublicKeyInfo, ASN.1 DER)가 들어 있어서 [2], 기기에서 꺼낸 APK 한 개만으로도 서명 인증서를 뽑아 볼 수 있습니다. 인증서에서 발급자·주체·유효기간을 읽는 법은 X.509 일반 규칙을 따릅니다.

설치한 앱의 APK 는 기기 안의 설치 코드 디렉터리에 남습니다. 현행 AOSP 에서는 기본 APK 를 `base.apk` 라는 이름으로 복사합니다 [4]. 기기에 설치된 앱 목록과 설치 시각, 설치한 앱은 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 페이지에서 다루고, 이 페이지는 APK 파일 자체에 들어 있는 정보를 다룹니다.

## 위치와 버전별 차이

| 항목 | 내용 | 범위 |
|---|---|---|
| 설치 코드 디렉터리 이름 | `targetDir/~~[randomStrA]/[packageName]-[randomStrB]` 형식 | 현행 AOSP 기준 [4] |
| 앱 설치 디렉터리 | 데이터 디렉터리 아래 `app`, 곧 `/data/app` | 현행 AOSP 기준 [5] |
| 첫 단계 디렉터리 이름 | RANDOM_DIR_PREFIX(`~~`) 뒤에 16바이트 난수를 URL-safe Base64(줄바꿈 없음, 패딩 `==` 는 남음)로 붙임 | 현행 AOSP 기준 [4][5] |
| 난수 | 설치할 때마다 SecureRandom 으로 새로 만들고, 같은 이름이 이미 있으면 다시 뽑음 | 현행 AOSP 기준 [4] |
| 기본 APK 파일 이름 | `base.apk` | 현행 AOSP 기준 [4] |
| v1 서명 | META-INF 디렉터리 | [1] |
| v2 서명 | APK 서명 블록 | Android 7.0 부터 [1] |
| v3 서명 | APK 서명 블록, v2 에 키 교체(key rotation)용 정보를 더함 | Android 9 부터 [1] |

RANDOM_DIR_PREFIX 는 PackageManagerService 에 `"~~"` 로 정의돼 있고, 같은 클래스가 앱 설치 디렉터리를 데이터 디렉터리 아래 `app` 으로 잡습니다 [5]. 두 단계 디렉터리 구조가 들어온 Android 버전과 분할 APK(split APK) 파일의 이름 규칙은 실제 기기에서 확인합니다. 호환성을 위해 v1, v2, v3 을 차례로 모두 서명하도록 권장됩니다 [1].

`dumpsys package` 의 패키지별 줄(codePath 와 서명 관련 줄)에 서명 정보가 찍히는 모양과, adb 일반 권한으로 설치 코드 디렉터리 아래 APK 를 읽거나 꺼낼 수 있는지는 기기에서 확인합니다. 역할별 설치·검증 담당 패키지와 설치 관련 설정 키는 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 페이지에 있습니다.

## 구조

### 파일의 네 구역

v2 서명을 한 APK 는 네 구역으로 나뉘고, 서명 블록은 ZIP Central Directory 바로 앞에 들어갑니다 [2].

| 순서 | 구역 | v2 서명이 보호하는 범위 |
|---|---|---|
| 1 | ZIP 항목 내용(파일 처음부터 APK 서명 블록 앞까지) | 구역 전체 |
| 2 | APK 서명 블록 | 블록 안의 서명한 데이터 |
| 3 | ZIP Central Directory | 구역 전체 |
| 4 | ZIP End of Central Directory | 구역 전체 |

v2 의 다이제스트는 파일을 1MB 조각으로 나눠 두 단계 머클 트리(Merkle tree) 방식으로 계산합니다 [2].

### APK 서명 블록

블록 안의 숫자는 모두 리틀 엔디언입니다 [2].

| 순서 | 크기 | 내용 |
|---|---|---|
| 1 | 8바이트 | 블록 크기(이 필드 자신은 빼고 셈) |
| 2 | 가변 | ID-값 쌍 여러 개. ID 는 uint32, 값은 길이가 정해져 있지 않음 |
| 3 | 8바이트 | 1번과 같은 블록 크기 |
| 4 | 16바이트 | 매직 문자열 `APK Sig Block 42` |

v2 서명 블록의 ID 는 `0x7109871a` 입니다 [2].

### 서명을 떼어 낸 흔적

v2 서명과 v1 서명을 함께 둔 APK 는 META-INF 의 매니페스트 파일에 `X-Android-APK-Signed` 속성을 넣고 지원하는 서명 방식 ID 를 적어야 합니다. 이 속성은 v2 서명을 떼어 내고 v1 만으로 검증받게 만드는 일을 막습니다 [2]. 그래서 v1 서명만 남은 APK 의 META-INF 매니페스트에 이 속성이 있으면 원래 있던 v2 블록을 누군가 떼어 냈을 가능성을 의심할 수 있습니다.

### 매니페스트와 리소스

컴파일한 매니페스트와 리소스 표는 `aapt2 dump` 로 읽고, 명령 형식은 `aapt2 dump sub-command filename.apk [options]` 입니다 [3]. 주요 하위 명령은 다음과 같습니다 [3].

| 하위 명령 | 출력 |
|---|---|
| `badging` | APK 매니페스트에서 뽑은 정보 |
| `packagename` | APK 의 패키지 이름 |
| `permissions` | 매니페스트에서 뽑은 권한 |
| `xmltree` | APK 안의 컴파일한 XML 을 트리로 |
| `xmlstrings` | 컴파일한 XML 의 문자열 |
| `resources` | 리소스 표 내용 |
| `strings` | 리소스 표의 문자열 풀 |
| `configurations` | 리소스가 쓰는 모든 구성 |
| `overlayable`, `styleparents`, `apc` | overlayable 리소스, 스타일 부모, AAPT2 컨테이너 내용 |

기기의 설정 파일이 쓰는 이진 XML 은 [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) 페이지에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| APK 서명 블록이나 META-INF 에 들어 있는 인증서의 키로 이 파일에 서명했다는 것 | 인증서 주인이 누구인지, 믿을 만한지 |
| v2 이상 서명이 검증을 통과하면 보호 범위 안이 서명한 뒤로 바뀌지 않았다는 것 | 이 앱이 무엇을 했는지 |
| 매니페스트에 이 패키지 이름과 권한이 선언돼 있다는 것 | 그 권한을 실제로 받았는지(부여 기록은 설치된 앱 페이지) |
| 설치 코드 디렉터리에 이 APK 가 있다는 것 | 언제, 어디서 받아 누가 설치했는지 |
| v1 만 남은 APK 에 `X-Android-APK-Signed` 속성이 있다는 것 | v2 블록을 누가, 왜 떼어 냈는지(떼어 냈다는 판단 자체도 추론) |

보고서에는 "이 앱을 설치했다" 보다 "설치 코드 디렉터리의 base.apk 는 v2 서명 블록을 담고 있고, 서명 인증서는 이것이며, 매니페스트는 이 권한을 요청한다" 처럼 파일로 확인되는 만큼만 씁니다.

## 시각 해석

APK 파일 안의 시각 값(ZIP 항목의 시각, 인증서 유효기간)으로 설치 시각이나 제작 시각을 판단하지 않습니다. 설치 시각과 마지막 갱신 시각은 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 페이지에서 읽습니다.

시각은 아니지만 시간 순서에 쓸 만한 단서는 설치 코드 디렉터리 이름입니다. 현행 AOSP 는 설치할 때마다 난수를 새로 뽑아 디렉터리 이름을 만드니 [4], 같은 패키지인데 수집본마다 디렉터리 이름이 다르면 그 사이에 다시 설치했거나 업데이트했을 수 있습니다. 업데이트 때도 이름이 바뀌는지는 실제 기기에서 확인합니다.

## 함정과 한계

- 설치 코드 디렉터리 이름에는 설치마다 바뀌는 난수가 들어가서 [4], 경로 문자열로 앱을 식별하거나 다른 수집본과 맞추면 안 됩니다. 패키지 이름과 서명 인증서로 맞춥니다.
- v1 서명만 있는 APK 는 ZIP 메타데이터 같은 일부가 서명 밖에 있어서 [1], v1 검증을 통과해도 파일 전체가 서명할 때 그대로라는 뜻은 아닙니다.
- v3 은 키 교체용 정보를 더한 방식이라 [1], 같은 앱이라도 버전에 따라 서명 인증서가 달라 보일 수 있습니다.
- ZIP 으로 푼 AndroidManifest.xml 은 이진 형식이라 [3], 문자열 검색으로 권한 이름을 못 찾았다고 권한이 없다고 판단하지 않습니다.
- v4 서명이 별도 파일이라는 설명은 [악성 앱 흔적 분석 (Malicious App Triage)](../../03-techniques/analysis/malicious-app-triage/index.md) 페이지에서 다룹니다.

## 직접 분석해 보기

작업은 해시를 적어 둔 사본으로 합니다. 확보와 해시 기록은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

**헥스로 서명 블록 찾기.** 서명 블록은 ZIP Central Directory 바로 앞에 있고, 8바이트 크기와 16바이트 매직 문자열로 끝납니다 [2]. 헥스 편집기에서 ASCII 문자열 `APK Sig Block 42` 를 찾으면 그 바로 뒤가 Central Directory 의 시작이고, 매직 바로 앞 8바이트가 블록 크기입니다. 크기 필드는 자기 자신을 빼고 세니, 블록 시작 위치는 "Central Directory 시작 위치 − 블록 크기 − 8" 로 계산합니다. 아래는 명세로 만든 예시이고, 실제 파일에서 나온 값이 아닙니다.

```text
(Central Directory 바로 앞 24바이트)
00 10 00 00 00 00 00 00                            블록 크기 0x1000 = 4096 (리틀 엔디언)
41 50 4B 20 53 69 67 20 42 6C 6F 63 6B 20 34 32   "APK Sig Block 42"
해석: 블록 시작 = Central Directory 시작 - 4096 - 8
      블록 맨 앞 8바이트도 같은 값 00 10 00 00 00 00 00 00 이어야 함

v2 서명 블록 ID 0x7109871a 는 파일 안에서 1A 87 09 71 순서로 보임
```

블록 맨 앞과 맨 끝의 크기가 다르거나 매직 문자열이 없으면 v2 이후 서명이 없거나 블록이 손상됐을 수 있으니, META-INF 디렉터리에 v1 서명 파일이 있는지 봅니다.

**공개 도구로 매니페스트 읽기.** Android SDK 의 AAPT2 로 패키지 이름과 요청 권한을 읽습니다 [3].

```text
aapt2 dump packagename base.apk
aapt2 dump permissions base.apk
aapt2 dump badging base.apk
```

`badging` 으로 받은 출력은 고치지 않고 그대로 보존합니다. apksigner 로 서명을 검증하고 인증서를 뽑아 공개 지표와 맞추는 절차는 [악성 앱 흔적 분석 (Malicious App Triage)](../../03-techniques/analysis/malicious-app-triage/index.md) 페이지에 있습니다.

## 교차 검증

- [설치된 앱 (packages.xml)](../app-usage/packages/index.md) — 이 APK 의 경로, 버전, 설치 시각, 설치한 앱을 기기 쪽 기록과 맞춥니다.
- [앱 샌드박스와 권한 (Sandbox·Permissions)](../../01-foundations/security-model/sandbox-permissions.md) — 매니페스트가 요청한 권한과 실제로 부여된 권한을 나눠 봅니다.
- [구글 플레이 기록 (Play Store)](../app-usage/play-store.md) — 같은 패키지를 스토어에서 받은 기록이 있는지 봅니다.
- [크롬 (Chrome for Android)](../browsers/chrome/index.md) — 웹에서 APK 파일을 받은 기록이 있는지 봅니다.
- [패키지 이름과 UID (Package Name·UID)](../../01-foundations/value-decoding/package-uid.md) — 매니페스트의 패키지 이름을 다른 기록의 UID 와 잇습니다.
- [악성 앱은 어디서 들어왔나 (Initial Access)](../../04-scenarios/incident/initial-access.md), [몰래 설치된 감시 앱 (Stalkerware)](../../04-scenarios/incident/stalkerware.md) — 이 기록을 쓰는 조사 시나리오입니다.

## 실습

공개 데이터 세트(NIST CFReDS 등)에서 Android 이미지를 구할 수 있으면 다음을 풀어 봅니다.

1. 사용자가 설치한 앱 하나의 설치 코드 디렉터리를 찾아 디렉터리 이름이 `~~` 로 시작하는 두 단계 구조인지, 그 안에 `base.apk` 가 있는지 확인합니다.
2. 그 base.apk 에서 `APK Sig Block 42` 를 찾아 블록 앞뒤의 크기 값이 같은지 확인하고, 블록 안에서 v2 ID 바이트(`1A 87 09 71`)를 찾습니다.
3. `aapt2 dump packagename` 결과가 packages.xml 의 패키지 이름과 같은지, `aapt2 dump permissions` 의 권한 가운데 실제로 부여된 것이 무엇인지 비교합니다.
4. META-INF 에 v1 서명 파일이 있는 APK 를 골라, 매니페스트 파일에 `X-Android-APK-Signed` 속성이 있는지와 v2 블록이 함께 있는지 확인합니다.

## 참고 문헌

1. APK signature scheme — Android Open Source Project, https://source.android.com/docs/security/features/apksigning
2. APK Signature Scheme v2 — Android Open Source Project, https://source.android.com/docs/security/features/apksigning/v2
3. AAPT2 — Android Developers, https://developer.android.com/tools/aapt2
4. PackageManagerServiceUtils.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/PackageManagerServiceUtils.java
5. PackageManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/PackageManagerService.java
