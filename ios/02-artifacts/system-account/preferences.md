---
title: "설정 값"
parent: "아티팩트 · 시스템·계정"
nav_order: 290
---

# 설정 값 (Preferences)

## 한 줄 요약

iOS 의 시스템과 앱은 설정과 내부 상태를 `Library/Preferences/` 아래 plist 파일에 키와 값으로 적어 두고, 로컬 백업에서는 이 파일들이 사용자·시스템·통신·네트워크·관리 설정 도메인과 앱 도메인으로 나뉘어 들어오기 때문에, 어느 도메인의 어느 파일인지부터 가려야 값을 바르게 읽을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

설정 파일은 plist 로 `Library/Preferences/` 아래에 있고, RealityNet 목록은 일반 설정 위치로 `/mobile/Library/Preferences/` 를 듭니다[8]. 여기에는 사용자가 설정 앱에서 고른 값만 있는 것이 아니라, 시스템 구성 요소가 마지막으로 돈 버전, 마지막으로 무엇을 한 날짜, 이전(migration)을 마쳤는지 같은 내부 상태도 함께 들어 있습니다. 관찰한 백업에서도 키 종류가 문자열(str), 정수(int), 실수(float), 참거짓(bool), 날짜(datetime), 바이트(bytes), 목록(list), 사전으로 섞여 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

이 페이지는 설정 파일이 어디에 어떻게 나뉘어 있는지와 읽을 때의 함정을 다루고, 주제별 설정은 해당 페이지로 넘깁니다. 기기 버전을 적는 키는 [기기 정보](device-info.md), 계정 상태 키는 [애플 계정](apple-account.md), 시간대 키는 [시간대와 시각 설정](time-zone.md), 암호·생체 인증 키는 [암호와 Face ID 설정 흔적](passcode-biometrics.md) 에서 봅니다. plist 형식 자체는 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 위치와 버전별 차이

### 로컬 백업의 도메인별 위치

관찰한 로컬 백업에서 설정 파일은 아래 자리에 모여 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

| 백업 도메인 :: 경로 | 담긴 설정 |
|---|---|
| `HomeDomain :: Library/Preferences/` | 사용자 쪽 시스템 설정과 Apple 기본 기능 설정 |
| `RootDomain :: Library/Preferences/` | 시스템(root) 쪽 설정 |
| `WirelessDomain :: Library/Preferences/` | 휴대 통신 설정 |
| `SystemPreferencesDomain :: SystemConfiguration/` | 네트워크 구성 |
| `ManagedPreferencesDomain :: mobile/` | 관리(제한) 설정 |
| `AppDomain-<번들 ID> :: Library/Preferences/<번들 ID>.plist` | 앱이 자기 컨테이너에 두는 설정 |

앱 설정의 예로 `AppDomain-com.apple.mobilesafari :: Library/Preferences/com.apple.mobilesafari.plist` 가 있었습니다. 백업의 `HomeDomain :: Library/Preferences/` 는 이름으로 보아 RealityNet 목록의 `/mobile/Library/Preferences/`[8] 와 같은 자리이지만, 도메인과 기기 안 경로를 짝짓는 규칙은 [로컬 백업](../../01-foundations/backups/local-backup/index.md) 에서 확인합니다. 번들 ID 로 앱을 가리는 법은 [번들 ID와 앱 그룹](../../01-foundations/value-decoding/bundle-id-app-group.md) 에서 다룹니다.

iOS 버전마다 어떤 설정 파일이 새로 생기거나 없어지는지는 이번 자료로 확인하지 못했습니다. 이 페이지의 파일 이름과 키 이름은 iOS 27.0 백업 하나에서 본 것이니, 다른 버전 검체에서는 같은 이름이 있는지부터 확인합니다.

### 자주 보는 설정 파일

아래는 관찰한 백업에서 조사에 자주 쓰일 만한 파일과 키이고 (확인 범위: iPhone 13 mini, iOS 27.0), 따로 적지 않은 파일은 `HomeDomain :: Library/Preferences/` 아래에 있습니다. 뜻은 키 이름으로 짐작한 것이고 값은 보지 않았습니다.

| 파일 | 관찰한 키 예 | 이름으로 짐작되는 내용 |
|---|---|---|
| `.GlobalPreferences.plist` | `AppleLanguages` (list), `AppleLocale` (str), `AppleKeyboards` (list), `AppleKeyboardsExpanded` (int), `AppleLanguagesSchemaVersion` (int), `AKLastLocale` (str), `AddingEmojiKeybordHandled` (bool), `PKKeychainVersionKey` (int), `com.apple.gms.availability.` 로 시작하는 키 여러 개 | 기기 언어·지역·키보드 |
| `.GlobalPreferences_m.plist` | `AppleLocale`, `Sig_AppleLocale`, `AppleLanguages`, `Sig_AppleLanguages` | 언어·지역. `_m` 파일과 `Sig_` 키의 뜻은 확인하지 못함 |
| `com.apple.springboard.plist` | `SBShowBatteryPercentage`, `SBEnableAlwaysOn`, `SBReachabilityEnabled`, `SBParentalControlsEnabled`, `SBRecentLocale`, `SBLockScreenWallpapers`, `SBHomeScreenWallpapers` | 홈 화면·잠금 화면 설정 |
| `com.apple.Preferences.plist` | `VPNConnectivity` (int), `VPNHasRelayConnections` (bool), `CellularSimIsRequired` (bool), `PersonalHotspotDiabled` (bool), `PSCoreSpolightIndexerLastIndexDate` (datetime) | 설정 앱 상태 |
| `com.apple.ScreenTimeAgent.plist` | `ScreenTimeEnabled` (bool), `SyncEnabled` (bool), `UsageGenesisDate` (datetime), `LastCheckinDate` (datetime), `LastViewedAllActivityDate` (datetime) | 스크린 타임 |
| `ManagedPreferencesDomain :: mobile/.GlobalPreferences.plist` | `com.apple.content-rating.AppRating`, `com.apple.content-rating.MovieRating`, `com.apple.content-rating.TVShowRating`, `com.apple.content-rating.ExplicitBooksAllowed`, `com.apple.content-rating.ExplicitMusicPodcastsAllowed`, `com.apple.system.SpellCheckAllowed`, `com.apple.system.AutoCorrectionAllowed` | 콘텐츠 등급 제한과 입력 제한 |
| `ManagedPreferencesDomain :: mobile/com.apple.webcontentfilter.plist` | `restrictWeb`, `useContentFilter`, `filterBlacklist`, `filterWhitelist`, `whitelistEnabled`, `limitWebProxies`, `noOverridingAllowed`, `useContentFilterOverrides`, `useTransitiveTrust` | 웹 콘텐츠 제한 |

`PersonalHotspotDiabled` 와 `PSCoreSpolightIndexer…` 는 철자가 틀린 것처럼 보이지만 관찰한 키 이름 그대로입니다. 검색할 때 바른 철자로 찾으면 걸리지 않으니 이름을 고쳐 적지 않습니다. 홈 화면 배치는 `HomeDomain :: Library/SpringBoard/IconState.plist` 와 `DesiredIconState.plist` 에 따로 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

스크린 타임 자료로 RealityNet 목록은 `/mobile/Library/Application Support/com.apple.remotemanagmentd/RMAdminStore-Cloud.sqlite` 와 `RMAdminStore-Local.sqlite` 를 듭니다(폴더 철자는 목록에 적힌 그대로)[8]. 사용 시간 기록 자체는 [화면 사용 시간](../app-usage/screen-time.md), VPN 과 핫스폿은 [VPN 설정](../network/vpn.md) 과 [개인용 핫스폿](../network/hotspot.md) 에서 다룹니다.

### 구성 프로파일과 제한 설정

구성 프로파일과 제한 설정이 모인 파일은 두 곳에 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0).

```
HomeDomain :: Library/UserConfigurationProfiles/EffectiveUserSettings.plist
HomeDomain :: Library/UserConfigurationProfiles/UserSettings.plist
HomeDomain :: Library/UserConfigurationProfiles/Truth.plist
HomeDomain :: Library/UserConfigurationProfiles/PublicInfo/Truth.plist
HomeDomain :: Library/UserConfigurationProfiles/PublicInfo/PublicEffectiveUserSettings.plist
HomeDomain :: Library/UserConfigurationProfiles/PublicInfo/NamespacedUserSettings.plist
HomeDomain :: Library/UserConfigurationProfiles/PublicInfo/MCMeta.plist

SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles :: Library/ConfigurationProfiles/
    ClientTruth.plist  CloudConfigurationDetails.plist  MCProfileEvents.plist
    MCSettingsEvents.plist  ProfileTruth.plist  PayloadManifest.plist  UserSettings.plist
```

`UserConfigurationProfiles` 쪽 파일에는 최상위 키 `restrictedBool`, `restrictedValue`, `intersection`, `union` 이 있었고, 두 `Truth.plist` 에는 빈 사전인 `assignedObject` 도 있었으며 `UserSettings.plist` 는 키가 없는 빈 파일이었습니다. 이름으로 보면 켜고 끄는 제한, 값으로 거는 제한, 여러 프로파일의 목록을 합치는 방식이 나뉘어 있는 것 같지만 확인한 자료는 없습니다. `MCProfileEvents.plist` 와 `MCSettingsEvents.plist` 도 이름으로는 프로파일·설정 변경 기록처럼 보이지만 확인하지 못했습니다. 프로파일 설치 흔적은 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md) 에서, 이 파일 안의 암호 정책 키는 [암호와 Face ID 설정 흔적](passcode-biometrics.md) 에서 다룹니다.

## 구조

설정 파일 하나는 최상위가 사전인 plist 이고, 키 이름 아래 값이 들어가며 값이 다시 사전이나 목록일 수 있습니다. 관찰한 파일 가운데는 키가 하나도 없는 빈 파일도 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 어느 파일이 이진 plist 이고 어느 파일이 XML plist 인지는 관찰 메모에 적지 않았으니, 파일마다 첫 바이트로 확인합니다.

바이트(bytes) 형 값 안에는 다시 plist 나 보관 객체가 들어 있을 수 있어서, `SBLockPoster` 나 `SBSystemActionConfiguredActionArchive` 같은 bytes 값은 첫 바이트를 보고 한 번 더 풀어 봅니다. 이 두 값의 속 내용은 이번에 확인하지 못했습니다. 보관 객체(NSKeyedArchiver)를 푸는 법은 [속성 목록 파일](../../01-foundations/data-formats/plist.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것.** 설정 파일은 수집 시점, 더 정확히는 그 파일이 마지막으로 저장된 때의 설정 상태를 보여 줍니다. 예를 들어 관리 설정 도메인에 콘텐츠 등급 키가 있고 값이 제한 쪽이면 그 기기에 제한이 걸려 있었다는 기록이 되고, 언어·지역 키 값은 사용자가 쓴 언어 환경을 보여 줍니다. 보고서에는 "수집한 설정 파일의 이 키 값이 이렇다" 처럼 파일과 키를 밝혀 씁니다.

**증명하지 못하는 것.** plist 는 키 값 옆에 그 값이 바뀐 시각을 붙이지 않아서, 설정을 언제 바꿨는지는 파일의 수정 시각이나 다른 기록으로 좁혀야 합니다. 값을 누가 바꿨는지도 말해 주지 않고, 제한 설정은 사용자가 직접 걸었을 수도, 프로파일이나 보호자 설정으로 걸렸을 수도 있습니다. 키가 없다고 그 기능을 끈 것이라고 단정하지 않고, 키가 있다고 그 기능을 쓴 것이라고도 단정하지 않습니다.

## 시각 해석

설정 파일 안의 시각은 형이 제각각입니다. 관찰한 백업에서 같은 성격의 값이 어떤 키는 날짜(datetime), 어떤 키는 실수(float), 어떤 키는 정수(int)로 적혀 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 실수·정수로 적힌 시각이 2001-01-01 기준 Mac 절대 시각인지 1970-01-01 기준 유닉스 시각인지는 키마다 다르고 확인한 자료가 없으니, 자릿수를 보고 [시각 값](../../01-foundations/value-decoding/time-values.md) 에 따라 가립니다.

파일 전체의 수정 시각은 설정 파일 안이 아니라 파일 시스템이나 백업 목록(`Manifest.db`)의 메타데이터에서 봅니다. 파일 수정 시각은 그 파일의 어떤 키든 하나가 바뀌면 함께 바뀔 수 있어서, 특정 설정을 바꾼 시각으로 바로 쓰지 않습니다.

## 함정과 한계

**대소문자만 다른 파일이 따로 있습니다.** 관찰한 백업에는 `com.apple.SpringBoard.plist`(대문자 B)와 `com.apple.springboard.plist`(소문자)가 둘 다 있었고 대문자 쪽은 키가 비어 있었습니다. `com.apple.Preferences.plist` 와 `com.apple.preferences.plist` 도 둘 다 있었고 소문자 쪽이 비어 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 대소문자를 가리지 않는 Windows 폴더로 꺼내면 한쪽이 다른 쪽을 덮어쓸 수 있으니, 꺼낼 때 fileID 이름을 그대로 두거나 도메인별 폴더를 따로 만듭니다.

**같은 이름의 파일이 여러 도메인에 있습니다.** `com.apple.mobilesafari.plist` 는 `AppDomain-com.apple.mobilesafari` 와 그 확장 도메인에 같은 이름으로 있었고, `com.apple.AuthKit.plist` 도 여러 앱 도메인에 있었습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 파일 이름과 함께 도메인을 꼭 적습니다.

**키 이름을 뜻으로 바꿔 읽지 않습니다.** 대부분의 키는 공식 설명이 없어서 이름으로 짐작할 뿐입니다. 보고서에는 키 이름과 값을 그대로 적고, 뜻은 같은 기기에서 설정을 바꿔 보는 시험이나 공개된 자료로 확인한 경우에만 풀어 씁니다.

**지우기와 조작.** 설정 파일은 초기화하면 새로 만들어지고, 백업으로 복원하면 백업한 기기의 값이 옮겨 올 수 있습니다. 설정 값이 다른 기록과 맞지 않으면 [초기화와 복원 흔적](erase-restore.md) 을 함께 보고, 조작 가능성은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 이진 plist 명세로 만든 예시이고 특정 검체에서 나온 바이트가 아닙니다. 이진 plist 는 `bplist00` 으로 시작하고, 파일 맨 끝 32바이트가 꼬리말(trailer)입니다. 꼬리말은 앞 6바이트를 비워 두고, 이어서 오프셋 표 칸 크기 1바이트, 객체 참조 크기 1바이트, 객체 개수 8바이트, 최상위 객체 번호 8바이트, 오프셋 표 시작 위치 8바이트가 옵니다.

```
파일 시작
00000000  62 70 6C 69 73 74 30 30  ...                      bplist00...

파일 끝 32바이트(예시 값)
          00 00 00 00 00 00 01 01                           비움 6 · 오프셋 크기 1 · 참조 크기 1
          00 00 00 00 00 00 00 03                           객체 3개
          00 00 00 00 00 00 00 00                           최상위 객체 0번
          00 00 00 00 00 00 00 1A                           오프셋 표는 0x1A 에서 시작
```

꼬리말에서 오프셋 표 위치를 읽고, 표에서 최상위 객체(0번)의 위치를 찾아가면 최상위 사전이 나옵니다. 사전의 표시 바이트 상위 4비트는 `1101` 이고 하위 4비트가 항목 수입니다. 파일이 잘렸거나 일부만 복구된 경우에도 꼬리말이 남아 있으면 이 순서로 따라갈 수 있습니다.

### 공개 도구로 한 번

Python 표준 라이브러리 `plistlib` 로 한 도메인의 설정 파일을 모두 열어 키와 형을 목록으로 뽑습니다. 원본이 아니라 꺼낸 사본에서 실행합니다.

```python
import plistlib, pathlib

for p in sorted(pathlib.Path("HomeDomain/Library/Preferences").glob("*.plist")):
    try:
        with p.open("rb") as f:
            data = plistlib.load(f)
    except Exception as e:
        print(p.name, "열지 못함:", e)
        continue
    print(p.name)
    for k, v in data.items():
        print("   ", k, type(v).__name__)
```

macOS 에서는 `plutil -p 파일이름` 으로 한 파일의 내용을 사람이 읽을 수 있게 볼 수 있습니다. 도구마다 날짜 형을 표시하는 시간대가 다를 수 있으니, 날짜 값은 도구 두 개로 맞춰 봅니다. 도구 검증은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 에서 다룹니다.

## 교차 검증

설정 값만으로는 언제 바뀌었는지 모르기 때문에, 시각이 있는 기록과 나란히 봅니다. 스크린 타임과 제한 설정은 [화면 사용 시간](../app-usage/screen-time.md) 과 [구성 프로파일과 MDM](../credentials-security/configuration-profiles.md), 언어·키보드 설정은 [키보드 입력 기록](../input-assistant/keyboard.md), 사파리 설정은 [사파리](../browsers/safari/index.md) 와 맞춰 봅니다. 설정을 바꾼 흔적이 로그에 남는지는 [통합 로그에서 찾을 것](../logs/unified-log-events.md) 에서, 여러 기록을 한 줄로 엮는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md) 에서 다룹니다.

## 실습

공개 검체(NIST CFReDS 등의 iOS 이미지나 백업)로 다음 질문을 풀어 봅니다.

1. `HomeDomain :: Library/Preferences/` 아래 plist 는 몇 개이고, 그 가운데 키가 없는 빈 파일은 몇 개입니까?
2. `.GlobalPreferences.plist` 의 `AppleLanguages` 와 `AppleLocale` 값은 무엇이고, `.GlobalPreferences_m.plist` 의 같은 키와 값이 같습니까?
3. 대소문자만 다른 설정 파일 쌍이 있습니까? 있다면 어느 쪽에 키가 들어 있습니까?
4. 관리 설정 도메인에 콘텐츠 등급 제한 키가 있습니까? 있다면 값은 무엇입니까?
5. 설정 파일 안의 실수(float)·정수(int) 시각 키 하나를 골라, Mac 절대 시각과 유닉스 시각 가운데 어느 쪽으로 풀어야 검체 사용 기간에 들어오는지 확인합니다.

## 참고 문헌

- [8] iOS-Forensics-References README — RealityNet (GitHub) — https://github.com/RealityNet/iOS-Forensics-References/blob/main/README.md
