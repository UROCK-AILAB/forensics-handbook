---
title: "APK 확인"
parent: "악성 앱 흔적 분석"
grand_parent: "기법 · 분석"
nav_order: 1520
---

# APK 확인 (APK Check)

## 한 줄 요약

의심 앱의 APK 파일에서 서명 방식과 서명 인증서를 확인하고, 파일 해시와 인증서를 공개된 침해 지표 (Indicator of Compromise, IOC) 와 대조하는 방법입니다.

## 언제 쓰나

[권한과 설정으로 찾기](permissions-settings.md) 나 [감시 앱 흔적](stalkerware.md) 으로 후보 앱을 추린 뒤, 그 앱이 누가 서명한 파일인지와 알려진 악성 앱과 같은 파일인지 확인할 때 씁니다. 패키지 이름만 맞춰 보는 대조보다 한 걸음 더 들어가서 파일과 서명한 주체를 확인합니다. 매니페스트와 서명 블록의 구조 자체는 [APK 정보 (AndroidManifest·서명)](../../../02-artifacts/embedded-metadata/apk.md) 페이지에 있습니다.

## 서명 방식

Android 의 APK 서명 방식은 버전에 따라 늘어 왔습니다 [1].

| 방식 | 들어온 버전 | 서명 위치 | 보호 범위 |
|---|---|---|---|
| v1 | Android 초기부터 | JAR 서명, `META-INF/` | ZIP 메타데이터 같은 APK 일부를 보호하지 않음 |
| v2 | Android 7.0 | APK 서명 블록 (APK Signing Block) | 파일 전체를 보호해서 ZIP 메타데이터를 바꿔도 서명이 깨짐 |
| v3 | Android 9 | APK 서명 블록 | v2 에 서명 키 교체 (key rotation) 정보를 더함 |
| v4 | Android 11 [5] | APK 옆의 별도 파일 (`파일이름.apk.idsig`) [5] | 단독으로 쓰지 않고 v2 나 v3 서명이 함께 있어야 함 [5] |

v3.1 의 들어온 버전과 구조는 이 페이지의 출처로 확인하지 못했습니다. 공식 문서는 호환성을 위해 v1, v2, v3 을 모두 서명하라고 권합니다 [1].

v1 서명만 있는 APK 는 ZIP 메타데이터 같은 일부가 서명 밖에 있어서, 서명 검증을 통과해도 파일 전체가 서명할 때 그대로라는 뜻까지는 아닙니다. v2 이상은 서명 블록을 뺀 파일 전체를 해시로 확인해서 ZIP 메타데이터를 바꿔도 서명이 깨지니 [1], 검증을 통과했다면 서명 블록 밖은 서명한 뒤로 바뀌지 않았다고 볼 수 있습니다.

## 절차

1. **APK 를 확보하고 해시를 적습니다.** 수집본이나 기기에서 후보 앱의 APK 를 꺼내고, 꺼내자마자 SHA-256 같은 해시를 계산해 수집 기록에 적습니다. APK 가 기기의 어느 폴더에 있는지와 꺼내는 명령은 이 페이지의 출처로 확인하지 못했고, 수집 절차는 [모바일 증거 확보](../../acquisition/mobile-acquisition/index.md) 페이지를 봅니다.
2. **작업 사본으로 서명을 검증합니다.** 원본은 그대로 두고 사본에 apksigner 를 돌립니다. 아래 "apksigner 로 확인하기" 를 봅니다.
3. **서명 인증서를 뽑아 둡니다.** `--print-certs` 로 인증서 정보를 받아 해시와 함께 적습니다.
4. **해시와 인증서를 지표와 대조합니다.** 아래 "해시·인증서 대조" 를 봅니다.
5. **설치·검증을 맡은 앱을 확인합니다.** 아래 "설치와 검증을 맡은 앱" 을 봅니다.
6. **매니페스트를 봅니다.** 패키지 이름, 버전, 요청 권한을 [APK 정보](../../../02-artifacts/embedded-metadata/apk.md) 페이지의 방법으로 읽고, 요청 권한을 [권한과 설정으로 찾기](permissions-settings.md) 의 부여 기록과 맞춥니다.

## apksigner 로 확인하기

apksigner 로 서명을 검증할 때는 아래 형식으로 부릅니다 [2].

```
apksigner verify [options] app-name.apk
```

| 옵션 | 하는 일 |
|---|---|
| `--print-certs` | 서명 인증서 정보를 보여 줌 |
| `--print-certs-pem` | 인증서 정보와 PEM 인코딩을 출력함 |
| `--min-sdk-version`, `--max-sdk-version` | 서명 검증을 확인할 API 수준 범위를 정수로 지정함. 최소값 기본은 매니페스트의 minSdkVersion |
| `-v`, `--verbose` | 자세히 출력함 |
| `-Werr` | 경고를 오류로 처리함 |

verify 는 APK 가 지원하는 모든 Android 버전에서 서명 검증이 통과하는지 확인합니다 [2]. 서명 키를 바꿀 때 쓰는 `rotate` 명령도 따로 있습니다 [2]. 출력 줄의 모양은 문서로 확인하지 못해서 여기에 예를 적지 않고, 받은 출력은 가공하지 않고 그대로 보존합니다.

## 해시·인증서 대조

Echap 의 stalkerware-indicators 저장소에서 `samples.csv` 에는 샘플 해시·패키지 이름·인증서·버전이, `ioc.yaml` 에는 패키지 이름과 Android 인증서가 들어 있어 APK 의 해시·서명 인증서와 맞춰 볼 수 있습니다 [4]. 해시가 다르더라도 `ioc.yaml` 의 인증서와 같으면 패키지 이름이나 버전을 바꾼 변종일 수 있다고 읽을 수 있고, 이 판단은 해석입니다. 저장소의 다른 파일과 규모는 [감시 앱 흔적](stalkerware.md) 페이지에 있습니다.

MVT 는 `--virustotal` 옵션으로 APK 해시를 VirusTotal 에 조회할 수 있고, API 키가 필요합니다 [3]. 문서는 이 옵션이 APK 해시를 VirusTotal 로 보낸다고 밝힙니다 [3]. 파일이 아니라 해시를 보내는 것이지만 사건 정보가 바깥 서비스로 나가는 셈이라, 사건의 외부 조회 방침을 먼저 확인합니다.

## 설치와 검증을 맡은 앱

`dumpsys package` 의 "Known Packages:" 절은 기기에서 역할별로 맡은 패키지를 보여 줍니다. 관찰한 폰에서는 설치·검증 역할을 포함해 아래 줄이 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5).

| 역할 | 패키지 |
|---|---|
| Installer | `com.google.android.packageinstaller` |
| Verifier | `com.android.vending`, `com.samsung.android.sm.devicesecurity` |
| Permission Controller | `com.google.android.permissioncontroller` |
| Developer verification service provider | `com.google.android.verifier` |
| Setup Wizard | `com.google.android.setupwizard` |
| Browser | `com.android.chrome` |
| Recents | `com.sec.android.app.launcher` |

같은 출력의 "Verifiers:" 절에는 "Required:" 줄이 두 개 있었습니다 (확인 범위: SM-S937N, Android 16, One UI 8.5). 이 표는 기기 전체에서 누가 그 역할을 맡는지를 알려 줄 뿐이고, 후보 앱 하나를 어느 앱이 설치했는지는 알려 주지 않습니다. 패키지별 설치 시각과 설치한 앱이 dumpsys 출력에 어떤 모양으로 나오는지는 확인하지 못했고, 앱이 어디서 들어왔는지 따라가는 흐름은 [악성 앱은 어디서 들어왔나](../../../04-scenarios/incident/initial-access.md) 와 [구글 플레이 기록](../../../02-artifacts/app-usage/play-store.md) 페이지에 있습니다.

## 함정과 한계

서명 검증은 서명한 뒤로 서명 범위 안이 바뀌지 않았는지를 확인할 뿐이고, 인증서 주인이 믿을 만한지는 알려 주지 않습니다. 악성 앱도 제 인증서로 서명하면 검증을 통과합니다.

v3 부터 서명 키 교체 정보를 담을 수 있어서 [1], 같은 앱이라도 버전에 따라 서명 인증서가 달라 보일 수 있습니다. 인증서가 지표와 다르다는 것만으로 다른 앱이라고 단정하지 않습니다.

지표에 없다는 결과는 깨끗하다는 뜻이 아닙니다. 공개 목록은 알려진 샘플만 담고, 버전이 바뀌면 파일 해시도 바뀝니다.

## 결과를 어떻게 해석하나

보고서에는 "이 APK 의 SHA-256 해시가 공개 지표 목록의 샘플 해시와 같다", "이 APK 는 v2 서명 검증을 통과했고 서명 인증서는 이것이다" 처럼 확인한 사실만 씁니다. 지표와 인증서만 같고 해시가 다르면 "같은 인증서로 서명한 앱" 까지만 말하고, 앱이 무엇을 했는지는 [감시 앱 흔적](stalkerware.md) 의 활동 흔적이 받쳐 줄 때만 씁니다.

## 참고 문헌

1. APK signature scheme — Android Open Source Project, https://source.android.com/docs/security/features/apksigning
2. apksigner — Android Developers, https://developer.android.com/tools/apksigner
3. MVT Android forensic methodology — Mobile Verification Toolkit docs, https://docs.mvt.re/en/latest/android/methodology/
4. stalkerware-indicators — AssoEchap (GitHub), https://github.com/AssoEchap/stalkerware-indicators
5. APK Signature Scheme v4 — Android Open Source Project, https://source.android.com/docs/security/features/apksigning/v4
