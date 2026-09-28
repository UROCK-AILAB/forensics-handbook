---
title: "보안 폴더와 작업 프로필"
parent: "기반 · 보안 구조"
nav_order: 300
---

# 보안 폴더와 작업 프로필 (Secure Folder·Work Profile)

작업 프로필 (Work Profile) 은 Android 다중 사용자 구조 위에서 주 사용자에 딸린 보조 사용자로 동작하며 앱 데이터와 계정을 따로 둡니다[1]. 삼성 보안 폴더 (Secure Folder) 도 기기에서 주 사용자에 딸린 사용자로 보일 수 있어서, 실제 기기의 사용자 목록으로 구조를 확인합니다.

## 이 구조가 드러나는 아티팩트

프로필이 있으면 앱 데이터·계정·알림이 사용자마다 나뉘어 남기 때문에, 주 사용자만 보면 프로필 안의 기록을 놓칩니다. 사용자 목록과 사용자별 정보는 [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md) 페이지에서, 사용자별 앱 폴더는 [앱 데이터 폴더 구조](../storage/app-data-layout.md) 페이지에서, 계정은 [계정](../../02-artifacts/system-account/accounts/index.md) 페이지에서, 알림은 [알림 기록](../../02-artifacts/app-usage/notification-history.md) 페이지에서 다룹니다.

## 작업 프로필의 구조

작업 프로필은 관리 프로필 (managed profile) 이라고도 부르고, Android 다중 사용자 구조의 보조 사용자로 동작합니다. 앱의 UID 와 데이터 폴더도 주 사용자와 같은 규칙을 따라서, 사용자 번호(userid)에 따라 UID 가 달라지며 데이터는 `/data/user/<userid>` 아래에 놓입니다. UID 를 계산하는 식은 [앱 샌드박스와 권한](sandbox-permissions.md) 페이지에 있습니다.

같은 앱이 주 사용자와 작업 프로필에 모두 설치되어 있으면 데이터가 따로 있고, 프로필 경계를 넘어 통신하려면 `INTERACT_ACROSS_PROFILES` 권한이나 앱옵스 승인이 있어야 합니다. 작업 프로필의 계정은 주 사용자와 별개라서 자격 증명을 프로필 경계 너머로 읽을 수 없고, 인텐트를 프로필 안팎으로 넘길지는 관리자가 정합니다.

모든 것이 나뉘지는 않습니다. 따로 두는 것과 함께 쓰는 것은 아래와 같습니다[1].

| 구분 | 항목 |
|---|---|
| 따로 두는 것 | 앱 데이터, 계정과 자격 증명 |
| 함께 쓰는 것 | 입력기(IME, 키보드), 접근성 서비스, Wi-Fi, 블루투스, NFC 같은 일부 시스템 설정 |
| 주 사용자 쪽에 보이는 것 | 작업 프로필 앱의 알림(ActivityManagerService 를 거쳐 표시) |

작업 프로필을 관리하는 쪽은 프로필 소유자 (profile owner) 인 기기 정책 클라이언트(DPC) 앱이고, 이 앱이 DevicePolicyManager API 로 정책을 겁니다. 작업 프로필 앱의 아이콘에는 파란 배지가 붙고, Android 9 이상에서 그 색은 `#1A73E8` 입니다. 사용자는 설정이나 빠른 설정에서 작업 프로필을 켜고 끌 수 있습니다. 정책을 거는 앱의 흔적은 [기기 관리자와 접근성 권한](../../02-artifacts/credentials-security/device-admin-accessibility.md) 페이지에서 다룹니다.

작업 프로필에 붙는 userid 값과 프로필마다 남는 파일은 실제 기기에서 확인합니다.

## 보안 폴더에서 확인할 것

보안 폴더를 조사할 때는 아래 질문을 실제 기기에서 확인합니다.

| 질문 | 상태 |
|---|---|
| 보안 폴더가 별도 Android 사용자(프로필)로 만들어지는가, 그렇다면 userid 는 몇인가 | 실제 기기에서 확인 |
| 보안 폴더의 앱 데이터가 `/data/user/<userid>` 아래에 따로 놓이는가 | 실제 기기에서 확인 |
| 보안 폴더가 주 사용자와 다른 암호화 키를 쓰는가 | 실제 기기에서 확인 |
| 보안 폴더를 숨기는 기능이 어떤 흔적을 남기는가 | 실제 기기에서 확인(관련 설정 키는 아래에 있음) |

## 기기에서 보이는 흔적

### 사용자 목록

adb 일반 셸 권한으로 `dumpsys user` 를 읽으면 사용자 목록이 나옵니다. 아래는 사용자가 둘인 기기의 출력에서 필요한 줄만 옮긴 것이고, `#` 와 `<값>` 은 가린 자리입니다.

```
Users:
  UserInfo{#:xxx:#c##} serialNo=# isPrimary=true
    Type: <값>
    Flags: <값>
    State: RUNNING_UNLOCKED
  UserInfo{###:xxx:#####} serialNo=### isPrimary=false parentId=#
    Flags: <값>
```

둘째 사용자는 userid 가 세 자리이고 `parentId` 가 있어서 주 사용자에 딸린 프로필로 보입니다. 이 사용자가 보안 폴더인지 작업 프로필인지는 `Type` 값으로 구분합니다.

사용자 항목에는 `Type`, `Flags`, `State`, `Created`, `Last logged in`, `Last logged in fingerprint`, `Start time`, `Unlock time`, `Last entered foreground`, `Has profile owner`, `Restrictions`, `Device policy restrictions`, `Effective restrictions`, `Can have profile`, `UserProperties`, `Ignore errors preparing storage` 필드가 있습니다. 이 가운데 `Has profile owner` 는 앞에서 말한 프로필 소유자가 있는지와 이름이 이어지고, 각 필드의 뜻과 시각 형식은 [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md) 페이지에서 다룹니다.

`UserProperties` 아래에는 프로필이 주 사용자와 무엇을 나눠 쓰는지 이름으로 드러나는 필드가 있습니다.

```
mShowInLauncher
mStartWithParent
mShowInSettings
mInheritDevicePolicy
mUseParentsContacts
mUpdateCrossProfileIntentFiltersOnOTA
mCrossProfileIntentFilterAccessControl
mCrossProfileIntentResolutionStrategy
mMediaSharedWithParent
mCredentialShareableWithParent
mAuthAlwaysRequiredToDisableQuietMode
mAllowStoppingUserWithDelayedLocking
mDeleteAppWithParent
mAlwaysVisible
mCrossProfileContentSharingStrategy
mProfileApiVisibility
mItemsRestrictedOnHomeScreen
```

이름으로 보면 `mUseParentsContacts` 는 연락처, `mMediaSharedWithParent` 는 미디어, `mCredentialShareableWithParent` 는 자격 증명을 주 사용자와 나눠 쓰는지와 이어져 있어서, 프로필 안의 데이터가 주 사용자 쪽 기록에도 섞였을지 판단할 때 확인할 곳입니다.

### 설정 값

설정 값에는 보안 폴더와 이름이 이어지는 키가 표마다 하나씩 있습니다.

| 설정 표 | 키 |
|---|---|
| secure | `hide_secure_folder_flag` |
| global | `smartswitch_data_exist_securefolder` |
| system | `caller_id_to_show_Secure Folder` |

`hide_secure_folder_flag` 는 이름으로 보면 보안 폴더 숨기기와 이어지고, 값의 뜻은 실제 기기에서 확인해야 합니다. 설정 값을 읽는 법은 [설정 값](../../02-artifacts/system-account/settings.md) 페이지를 봅니다.

### 계정과 알림

`dumpsys account` 는 사용자마다 `User UserInfo{...}:` 머리 아래에 계정 목록과 계정 변경 이력(Accounts History)을 보여 주고, 이력의 필드는 `AccountId, Action_Type, timestamp, UID, TableName, Key` 입니다. 이력 해석은 [계정](../../02-artifacts/system-account/accounts/index.md) 페이지에서 다룹니다.

`dumpsys notification` 의 알림 항목에는 `userId=` 필드가 있고, `userId=-#` 처럼 음수인 값도 나올 수 있습니다. 음수 userId 의 뜻은 실제 기기에서 확인합니다.

## 포렌식에서 중요한 점

작업 프로필은 앱 데이터와 계정을 주 사용자와 따로 두기 때문에, 수집과 분석을 주 사용자 기준으로만 하면 프로필 안의 앱 데이터와 계정을 놓칩니다. 먼저 `dumpsys user` 나 수집한 이미지로 사용자가 몇 명인지 확인하고, 사용자마다 앱 데이터·계정·알림을 따로 봅니다.

반대로 입력기와 접근성 서비스는 프로필과 주 사용자가 함께 쓰고 작업 프로필 앱의 알림은 주 사용자 쪽에 보이기 때문에, 주 사용자 쪽 기록에 프로필 앱의 흔적이 섞여 있을 수 있습니다. 한 기록이 어느 사용자에서 나왔는지는 UID 나 `userId` 필드로 구분해서 보고서에 적습니다.

## 함정

userid 가 세 자리이고 주 사용자에 딸린 프로필이라는 것만으로 그 사용자를 보안 폴더로 단정하지 않습니다. 종류는 `Type` 값으로 구분합니다.

작업 프로필이 꺼져 있을 때 데이터가 어떤 상태로 남는지, 보안 폴더가 잠겨 있을 때 무엇을 읽을 수 있는지는 실제 기기에서 확인합니다. 두 경우 모두 수집 결과에 프로필 데이터가 없다고 해서 프로필에 데이터가 없었다고 말하지 않습니다.

## 도구

adb 일반 셸 권한으로 `dumpsys user`, `dumpsys account`, `dumpsys notification`, `settings list` 를 읽으면 위 필드와 키를 볼 수 있습니다. dumpsys 출력을 읽는 법은 [dumpsys 출력](../../02-artifacts/logs/dumpsys.md) 페이지를, 수집 방식별로 얻을 수 있는 범위는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지를 봅니다.

## 참고 문헌

1. Work profiles (Managed profiles) — Android Open Source Project — https://source.android.com/docs/devices/admin/managed-profiles
