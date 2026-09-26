---
title: "권한과 설정으로 찾기"
parent: "악성 앱 흔적 분석"
grand_parent: "기법 · 분석"
nav_order: 1500
---

# 권한과 설정으로 찾기 (Permissions·Settings)

앱이 받은 권한과 기기의 민감한 설정 값을 살펴서, 화면·알림·설치 같은 민감한 기능에 손이 닿는 앱을 먼저 추려 내는 방법입니다.

## 언제 쓰나

악성 앱이나 감시 앱이 의심되지만 어느 앱인지 모를 때 가장 먼저 씁니다. 설치된 앱이 수백 개인 기기에서 앱을 하나씩 열어 보기는 어렵고, 권한과 설정은 앱이 무엇을 하도록 허락받았는지 보여 주는 기록이라서 후보를 좁히는 첫 거름망으로 쓸 수 있습니다. 여기서 추린 후보는 [감시 앱 흔적](stalkerware.md) 에서 실제로 움직인 흔적과 맞춰 보고, [APK 확인](apk-check.md) 에서 파일과 서명을 확인합니다.

## 권한의 종류

Android 권한은 설치 시 권한 (install-time permissions), 런타임 권한 (runtime permissions), 특수 권한 (special permissions) 세 가지로 나뉩니다 [1]. 설치 시 권한 가운데 normal 권한은 보호 수준이 `normal` 이고, signature 권한은 권한을 정의한 앱이나 운영체제와 같은 인증서로 서명한 앱에만 줍니다 [1]. 런타임 권한은 위험 권한 (dangerous permissions) 이라고도 부르고 보호 수준이 `dangerous` 이며, 앱이 실행 중에 사용자에게 요청해야 받을 수 있습니다 [1]. 특수 권한은 특정 앱 동작에 대응하는 권한으로 플랫폼과 제조사만 정의할 수 있고 보호 수준은 `appop` 입니다 [1]. SMS 보내기와 받기처럼 서로 관련된 권한은 권한 그룹 (permission group) 으로 묶어 다룹니다 [1].

샌드박스와 권한 모델 전체는 [앱 샌드박스와 권한](../../../01-foundations/security-model/sandbox-permissions.md) 페이지에 있습니다.

## 버전·제조사별 차이

| 항목 | 적용 범위 | 근거 |
|---|---|---|
| 설치 시·런타임·특수 권한 구분 | 문서에 버전 표기 없음 | [1] |
| 제한된 설정 (Restricted settings) | 일부 단계는 Android 13 이상에서만 동작 | [2] |
| 아래 표의 공통 설정 키 | 값 형식은 실제 기기로 확인 | |
| `rampart_`·`appprotection_` 계열 키 | 삼성 기기 | |

## 절차

1. **읽을 수 있는 범위를 정합니다.** 루팅하지 않은 폰에서는 adb 일반 셸 권한(UID 2000)으로 dumpsys 와 settings 출력을 읽을 수 있고, /data/system 아래 파일은 파일 시스템 수집본이 있어야 읽을 수 있습니다. 파일 시스템 수집본이 있으면 2단계까지, 없으면 3단계부터 진행합니다. 수집 방법은 [모바일 증거 확보](../../acquisition/mobile-acquisition/index.md) 페이지를 봅니다.
2. **권한 부여 기록을 뽑습니다.** 수집본의 packages.xml 에서 앱마다 받은 권한과 부여 여부를 꺼냅니다. 아래 "packages.xml 의 권한 기록" 을 봅니다.
3. **민감한 설정 키를 확인합니다.** 접근성·알림 접근·입력기·출처를 알 수 없는 앱 설치처럼 앱에 넓은 권한을 주는 설정 키를 먼저 읽습니다. 아래 "살펴볼 설정 키" 를 봅니다.
4. **제한된 설정이 풀린 앱이 있는지 봅니다.** 아래 "제한된 설정" 을 봅니다.
5. **사용자와 관리 상태를 확인합니다.** 프로필 사용자와 기기 정책 제한이 있는지 봅니다. 아래 "사용자와 기기 관리" 를 봅니다.
6. **후보 목록을 만들어 다음 단계로 넘깁니다.** 패키지 이름, 걸린 권한과 설정 키, 읽은 시각을 한 줄에 적고 [감시 앱 흔적](stalkerware.md) 과 [APK 확인](apk-check.md) 으로 넘깁니다.

## packages.xml 의 권한 기록

공개 도구 ALEAPP 의 permissions 모듈은 경로 패턴 `*/system/packages.xml` 에 맞는 파일 하나를 읽어 보고서 세 개를 만듭니다 [3].

| 보고서 | 열 |
|---|---|
| Permission Trees | Name, Package |
| Permissions | Name, Package, Protection |
| Package and Shared User | Type, Package, Permission, Granted? |

이 모듈이 읽는 XML 요소는 `permission-trees`, `permissions`, `perms` 이고, 속성은 `name`, `package`, `protection`, `granted` 입니다 [3]. Permissions 보고서의 Protection 열로 위험 권한을 고른 뒤, Package and Shared User 보고서에서 그 권한을 받은 패키지를 찾으면 후보가 나옵니다. Permissions 보고서에는 권한을 정의한 패키지도 함께 나와서, 처음 보는 앱이 자기 권한을 정의해 두었는지도 여기서 확인합니다.

Protection 열 값의 표기, 이 파일의 전체 경로, 권한 기록이 이 파일에만 남는지와 파일 형식은 Android 버전마다 다를 수 있어 실제 기기로 확인합니다. 도구가 권한을 하나도 내지 않으면 파일을 직접 열어 형식부터 확인합니다. 파일 전체 구조는 [설치된 앱 (packages.xml)](../../../02-artifacts/app-usage/packages/index.md) 페이지에 있습니다.

## 살펴볼 설정 키

settings 출력에서 악성 앱 분석과 관련 있는 키를 이름으로 묶으면 아래와 같습니다. 각 키의 값 형식과 정확한 뜻을 설명한 공개 자료는 없어서 실제 기기로 확인해야 합니다.

| 묶음 | 이름공간 | 키 |
|---|---|---|
| 접근성 | secure | `accessibility_enabled`, `enabled_accessibility_services`, `accessibility_shortcut_target_service`, `notified_non_accessibility_category_services` |
| 알림 접근 | secure | `enabled_notification_listeners` |
| 입력기 | secure | `default_input_method`, `enabled_input_methods` |
| 자동 완성·음성 비서 | secure | `autofill_service`, `voice_interaction_service`, `assistant` |
| 위치 | secure | `location_mode`, `mock_location` |
| 출처를 알 수 없는 앱 | secure | `install_non_market_apps`, `unknown_sources_default_reversed` |
| 기타 | secure | `secure_overlay_settings`, `trust_agents_initialized`, `known_trust_agents_initialized`, `trusted_locations_count` |
| 개발자 옵션·adb | global | `adb_enabled`, `adb_wifi_enabled`, `adb_allowed_connection_time`, `development_settings_enabled` |
| 앱 검증 | global | `package_verifier_user_consent`, `verifier_timeout`, `verifier_timeout_samsung`, `art_verifier_verify_debuggable` |
| 초기 설정 | global | `device_provisioned` |

삼성 폰에는 `rampart_` 로 시작하는 키가 secure 에 `rampart_main_switch_enabled`, `rampart_blocked_unknown_apps`, `rampart_blocked_adb_cmd`, `rampart_blocked_at_cmd`, `rampart_blocked_commands`, `rampart_blocked_keystring`, `rampart_enabled_message_guard`, `rampart_is_reset_by_at_command`, `rampart_misc_settings`, `rampart_snapshot_adb_enabled`, `rampart_snapshot_adb_wifi_enabled`, `rampart_strict_protection_switch_enabled` 가 있고, global 에 `rampart_boot_complete_count`, system 에 `rampart_suw_main_on` 이 있습니다. 키 이름으로 보면 삼성 자동 차단 (Auto Blocker) 기능의 설정일 가능성이 있습니다. secure 에는 `appprotection_auto_scan_updated`, `appprotection_package_uid`, `appprotection_permission_function_agree_or_disagree`, `appprotection_permission_function_background_auto_scan_agreed`, `appprotection_permission_function_install_auto_scan_agreed`, `appprotection_permission_function_usage`, `appprotection_permission_scloud_function_usage`, `appprotection_permission_scloud_usage_user_decided` 도 있는데, 어느 삼성 기능의 키인지 밝힌 공개 자료는 없습니다.

접근성 설정은 먼저 봅니다. 접근성 설정에 접근한 앱은 화면 내용을 읽고 사용자 대신 다른 앱을 조작할 수 있습니다 [2]. 설정 값을 읽는 법은 [설정 값 (Settings Global·Secure·System)](../../../02-artifacts/system-account/settings.md), 접근성 서비스와 기기 관리자 기록 자체는 [기기 관리자와 접근성 권한](../../../02-artifacts/credentials-security/device-admin-accessibility.md) 페이지에 있습니다.

## 제한된 설정

앱을 설치하면 일부 기기 설정이 제한될 수 있고, 사용자가 제한된 설정을 허용하기 전에는 그 설정을 바꿀 수 없습니다 [2]. 대표 예가 접근성 설정입니다 [2]. 허용하는 곳은 설정의 앱 목록에서 해당 앱을 열고 더보기 메뉴에 있는 "Allow restricted settings" 이고, 이 단계 가운데 일부는 Android 13 이상에서만 됩니다 [2]. 신뢰하는 개발자의 앱이 아니면 허용하지 않도록 안내합니다 [2].

분석에서는 어떤 앱에 제한된 설정이 허용되어 있다면 누군가 기기에서 그 메뉴를 눌렀다고 볼 수 있습니다. 다만 이는 해석일 뿐이고, 허용 상태가 어느 파일이나 키에 남는지, 제한이 따로 설치한 앱에만 걸리는지, 알림 접근도 제한 대상인지는 실제 기기로 확인해야 합니다.

## 사용자와 기기 관리

`dumpsys user` 출력에는 사용자마다 "Has profile owner:", "Restrictions:", "Device policy restrictions:", "Effective restrictions:" 필드가 있습니다. 필드 이름대로라면 프로필 소유자 (profile owner) 가 있는지와 기기 정책으로 걸린 제한이 나오는 필드라서, 관리 앱이 들어온 기기인지 판단할 때 봅니다. 같은 출력에 주 사용자 말고 `parentId=` 가 붙은 사용자가 나오면 보안 폴더나 작업 프로필 같은 프로필 사용자일 수 있습니다. 프로필 사용자가 있으면 권한과 설정을 사용자별로 따로 봐야 하고, 자세한 내용은 [사용자와 프로필](../../../02-artifacts/system-account/users-profiles.md) 과 [보안 폴더와 작업 프로필](../../../01-foundations/security-model/secure-folder-work-profile.md) 페이지에 있습니다.

## 도구

파일 시스템 수집본이 있으면 ALEAPP 의 permissions 모듈로 packages.xml 의 권한 기록을 표로 뽑을 수 있습니다 [3]. 수집본이 없으면 adb 로 dumpsys 와 settings 출력을 텍스트로 받아 두고 키 이름으로 찾습니다. MVT 와 AndroidQF 로 수집하는 흐름은 [악성 앱 흔적 분석](index.md) 허브에 정리해 두었습니다.

## 함정과 한계

dumpsys 와 settings 는 읽은 순간의 값만 보여 주고, 언제 그 값으로 바뀌었는지는 알려 주지 않습니다. 설정이 켜진 시점을 알아야 하면 [감시 앱 흔적](stalkerware.md) 의 활동 기록이나 [타임라인 작성](../timeline/index.md) 으로 넘어가 주변 기록과 맞춰 봐야 합니다.

권한을 받았다는 기록은 앱이 그 권한을 실제로 썼다는 뜻이 아닙니다. 설정 키에 이름이 올랐다는 것만으로 악성이라고 할 수도 없어서, 같은 앱의 서명·설치 출처·사용 흔적을 함께 봐야 합니다.

`rampart_` 처럼 제조사가 정한 키는 이름만으로 기능을 단정하지 않습니다. 제조사 키의 뜻과 목록은 One UI 버전과 기기마다 다를 수 있습니다.

## 결과를 어떻게 해석하나

이 단계의 결과는 "살펴볼 앱 목록" 이지 "악성 앱 목록" 이 아닙니다. 보고서에는 "수집 시점 설정에 이 앱의 접근성 서비스가 켜진 것으로 기록되어 있다", "packages.xml 에 이 앱이 이 권한을 받은 것으로 기록되어 있다" 처럼 기록으로 확인되는 만큼만 쓰고, "이 앱이 화면을 엿봤다" 처럼 행위를 단정하는 문장은 활동 흔적으로 뒷받침될 때만 씁니다.

## 참고 문헌

1. Permissions on Android — Android Developers, https://developer.android.com/guide/topics/permissions/overview
2. Allow restricted settings — Android Help (Google), https://support.google.com/android/answer/12623953?hl=en
3. ALEAPP scripts/artifacts/permissions.py — abrignoni/ALEAPP (GitHub), https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/artifacts/permissions.py
