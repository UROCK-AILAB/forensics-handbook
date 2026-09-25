---
title: "사용자와 프로필"
parent: "아티팩트 · 시스템·계정"
nav_order: 360
---

# 사용자와 프로필 (Multi-user·users)

한 기기 안에 사용자와 프로필이 몇 개 있었는지, 각각 언제 만들어지고 마지막으로 쓰였는지를 알려 주는 기록을 정리합니다. 값은 현행 AOSP(frameworks/base 의 main 가지) 기준입니다.

## 한 줄 요약

시스템 서비스 UserManagerService 가 `/data/system/users` 폴더에 사용자 목록 파일 `userlist.xml` 과 사용자별 xml 파일을 적고, 각 사용자의 번호·종류·생성 시각·마지막 로그인 시각·그때의 빌드 지문이 여기에 남습니다 [1].

## 무엇을 기록하나 · 왜 생기나

Android 는 한 기기에서 여러 사용자 공간을 나눠 씁니다. 사용자마다 앱 데이터와 일부 설정이 따로 있고, 한 사용자는 다른 사용자의 앱 데이터를 볼 수 없습니다 [2]. 반면 프로필은 Wi-Fi·블루투스 같은 기기 전체 설정 일부를 함께 쓰고, 앱 설치는 모든 사용자에게 영향을 줄 수 있습니다 [2].

사용자 종류는 다음과 같습니다 [2].

| 종류 | 설명 |
|---|---|
| 시스템 사용자 | 처음 만든 사용자이고 공장 초기화 말고는 지울 수 없음 |
| 보조 사용자 (secondary) | 추가로 만든 일반 사용자 |
| 게스트 (guest) | 임시 사용자이고 한 번에 하나만 있음 |
| 관리 프로필 (managed profile) | 업무 프로필이고 프로필 소유자(profile owner)가 관리함 |
| 제한 프로필 (restricted profile) | 태블릿·TV 용 |
| 복제 프로필 (clone profile) | 앱을 두 개 띄울 때 쓰는 프로필 |
| 비공개 프로필 (private profile) | 따로 잠글 수 있는 공간 |

조사에서 이 기록이 중요한 까닭은 데이터가 사용자 번호별로 나뉘어 저장되기 때문입니다. 주 사용자 폴더만 보면 업무 프로필이나 복제 프로필에 있는 메신저 대화와 계정을 놓치고, 반대로 여러 사람이 한 기기를 썼다면 어느 사용자 공간의 기록인지부터 가려야 합니다. 사용자별 앱 데이터 폴더의 구조는 [앱 데이터 폴더 구조 (/data/data·/data/user)](../../01-foundations/storage/app-data-layout.md) 페이지에, 삼성 보안 폴더와 업무 프로필은 [보안 폴더와 작업 프로필 (Secure Folder·Work Profile)](../../01-foundations/security-model/secure-folder-work-profile.md) 페이지에 있습니다.

## 위치와 버전별 차이

사용자 정보는 `/data/system/users` 폴더에 있습니다. 목록 파일은 `userlist.xml` 이고, 사용자마다 사용자 번호에 `.xml` 을 붙인 파일(예: `0.xml`)과 같은 번호의 하위 폴더가 있으며, 하위 폴더에는 `photo.png` 와 이름이 `res_` 로 시작하는 제한(restriction) xml 파일이 들어갑니다 [1]. 사용자별 파일을 고쳐 쓸 때는 이름 끝에 `.backup`, `.reservecopy` 를 붙인 사본도 씁니다 [1]. 두 파일 모두 설정 파일과 같은 `Xml.resolveSerializer` 로 쓰기 때문에 기기 설정에 따라 글자 XML 일 수도 있고 안드로이드 바이너리 XML(ABX)일 수도 있으며 [1], 첫 바이트로 가리는 법은 [설정 값 (Settings Global·Secure·System)](settings.md) 페이지에 있습니다.

사용자 번호 0 이 시스템 사용자이고, 추가 사용자 번호는 10 부터 붙습니다(상수 MIN_USER_ID 가 UserHandle.MIN_SECONDARY_USER_ID 를 따름) [1].

| 항목 | 내용 | 출처·범위 |
|---|---|---|
| 사용자 종류 정의를 정리한 버전 | Android 11 | [2] |
| 헤드리스 시스템 사용자 | `ro.fw.mu.headless_system_user=true` 일 때이고, Android 10 이후 자동차용 | [2] |
| 다중 사용자 켜기 | 기기 설정 `config_multiuserMaximumUsers`(1보다 크게), `config_enableMultiUserUI`(true) | [2] |
| 휴대폰에 다중 사용자가 들어온 버전 | 공개 자료 없음 | |
| 삼성 기기의 두 번째 사용자 | 번호가 세 자리이고 parentId 가 붙은 프로필일 수 있음 | |
| 삼성 보안 폴더·앱 이중 실행이 쓰는 번호 범위 | 공개 자료 없음(검체에서 확인) | |

삼성 기기의 settings 에는 global 표에 `add_users_when_locked`, `lock_add_profile`, `lock_remove_profile`, `lock_reset_profile`, `smartswitch_data_exist_securefolder` 키가, secure 표에 `hide_secure_folder_flag` 키가 있을 수 있습니다. 이름으로 보면 잠금 상태에서 사용자 추가, 프로필 추가·삭제, 보안 폴더와 관련된 값으로 보이지만, 값의 뜻을 밝힌 공개 자료는 없습니다.

## 구조

### 사용자 xml

목록 파일 `userlist.xml` 은 뿌리 태그가 `users` 이고 `nextSerialNumber`, `version`(현행 11), `userTypeConfigVersion` 속성과 사용자별 항목을 담습니다. 사용자별 파일은 뿌리 태그가 `user` 이고, 여기에 적는 속성은 다음과 같습니다(현행 AOSP 기준) [1].

| 속성 | 담긴 것 |
|---|---|
| `id`, `serialNumber` | 사용자 번호와 일련번호 |
| `type`, `flags` | 사용자 종류와 플래그 |
| `created`, `lastLoggedIn`, `lastEnteredForeground` | 시각(유닉스 밀리초) |
| `lastLoggedInFingerprint` | 마지막 로그인 때의 빌드 지문 |
| `profileGroupId`, `profileBadge`, `restrictedProfileParentId` | 프로필이 속한 부모 사용자와 표시 배지 |
| `partial`, `preCreated`, `convertedFromPreCreated`, `guestToRemove` | 만들다 만 사용자, 미리 만든 사용자, 지울 게스트 표시 |
| `seedAccountName`, `seedAccountType` | 사용자를 만들 때 넘겨받은 계정 |
| `icon` | 사용자 사진 경로 |

사용자별 파일에는 속성 말고도 `name`, `restrictions`, `seedAccountOptions`, `userProperties` 같은 하위 태그가 들어갑니다 [1]. "담긴 것" 칸의 일부(부모 사용자, 만들다 만 사용자 등)는 속성 이름으로 짐작한 뜻이고, 소스에 따로 붙은 설명은 없습니다. `type` 에 들어가는 값의 예는 다음과 같습니다 [2].

```
android.os.usertype.full.SYSTEM
android.os.usertype.full.SECONDARY
android.os.usertype.full.GUEST
android.os.usertype.profile.MANAGED
android.os.usertype.system.HEADLESS
```

### 라이브 기기의 dumpsys user

`dumpsys user` 는 adb 일반 셸 권한으로 실행할 수 있습니다. 출력 한 예(789줄)의 앞부분은 다음 모양입니다. 값은 가리고 대표 줄만 실었습니다.

```
Current user: #
Users:
  UserInfo{#:xxx:#c##} serialNo=# isPrimary=true
    Type: <값>
    Flags: <값>
    State: RUNNING_UNLOCKED
    Created: <unknown>
    Last logged in: <값>
    Last logged in fingerprint: <값>
    Start time: <값>
    Unlock time: <값>
    Last entered foreground: <값>
    Has profile owner: <값>
    Restrictions: <값>
    Device policy restrictions: <값>
    Effective restrictions: <값>
    Can have profile: true
    UserProperties: <값>
        mShowInLauncher=#
        mStartWithParent=false
        mMediaSharedWithParent=false
        mCredentialShareableWithParent=false
        mDeleteAppWithParent=false
    Ignore errors preparing storage: <값>
  UserInfo{###:xxx:#####} serialNo=### isPrimary=false parentId=#
    Flags: <값>
```

`Created`·`Last logged in`·`Last logged in fingerprint`·`Last entered foreground` 는 xml 의 같은 이름 속성과 짝을 이루고, `State`·`Start time`·`Unlock time` 은 파일에 적지 않고 메모리에만 있는 현재 실행 상태를 보여 줍니다 [1]. 두 번째 사용자 줄의 `parentId` 가 첫 번째 사용자 번호를 가리켜서 이 사용자가 프로필이라는 점을 알 수 있습니다. `UserProperties` 아래 값들은 프로필이 부모와 미디어·자격 증명을 함께 쓰는지, 부모와 함께 시작하는지 같은 성격을 이름으로 보여 줍니다. `Unlock time` 을 잠금 해제 흔적으로 읽는 방법은 [잠금 화면 설정 (Lock Settings)](lock-settings.md) 페이지에 있습니다. dumpsys 를 뽑는 방법은 [dumpsys 출력 (dumpsys)](../logs/dumpsys.md) 페이지를 봅니다.

## 증거로서 의미

| 기록 | 증명하는 것 | 증명하지 못하는 것 |
|---|---|---|
| 사용자 목록과 번호 | 확보 시점에 그 번호의 사용자·프로필이 기기에 있었다는 것 | 이미 지운 사용자가 있었는지 |
| `type`·`parentId`·`profileGroupId` | 그 공간이 보조 사용자인지, 어느 사용자에 딸린 프로필인지 | 그 공간을 실제로 누가 썼는지 |
| `created` | 기기 시계로 그 시각에 사용자를 만들었다는 것 | 만든 사람이 누구인지 |
| `lastLoggedIn`·`lastEnteredForeground` | 그 사용자 공간이 마지막으로 로그인·전면으로 나온 시각 | 그 전의 로그인 이력 |
| `lastLoggedInFingerprint` | 마지막 로그인 때의 빌드 | 업데이트 이력 전체 |
| seed 계정 속성 | 사용자를 만들 때 넘겨받은 계정이 있었다는 것 | 지금도 그 계정이 등록되어 있는지 |

보고서에는 "사용자 목록에 번호 ###, 종류 관리 프로필, 부모 사용자 0 인 프로필이 있고, 이 프로필의 마지막 로그인 기록은 이 시각이다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

`created`, `lastLoggedIn`, `lastEnteredForeground` 는 System.currentTimeMillis() 로 기록하는 유닉스 밀리초이고, 벽시계 기준이라 UTC 입니다 [1]. 벽시계를 쓰기 때문에 기기 시계가 틀린 동안 만든 사용자는 생성 시각이 실제와 다를 수 있습니다. 사용자를 만들 때 시계가 1970년에서 30년(EPOCH_PLUS_30_YEARS)이 지나지 않은 값이면 `created` 를 0 으로 적습니다 [1].

`dumpsys user` 는 이 값들을 날짜로 찍지 않고 출력한 때로부터 얼마 전인지("... ago")로 찍고, 값이 0 이면 `<unknown>` 으로 찍습니다 [1]. 그래서 날짜로 바꾸려면 dumpsys 를 뽑은 시각을 함께 기록해 둬야 합니다. `Start time` 과 `Unlock time` 은 부팅 뒤 흐른 시간(SystemClock.elapsedRealtime)으로 적는 값이라 [1], 파일에 남지 않고 재부팅하면 사라집니다.

사용자 0 의 `Created:` 가 `<unknown>` 으로 나오는 기기도 있습니다. `created` 값이 0 이라는 뜻이고 [1], 왜 0 이 되었는지 밝힌 공개 자료는 없습니다. 그래서 사용자 0 의 생성 시각으로 기기를 처음 설정한 날을 말하지 않고 [초기화 흔적 (Factory Reset)](factory-reset.md) 페이지의 기록과 함께 봅니다. 숫자를 날짜로 바꾸는 법은 [시각 값 (Unix 밀리초·Chrome 시각·기타)](../../01-foundations/value-decoding/time-values.md) 페이지에 있습니다.

## 함정과 한계

사용자 번호마다 계정·앱 데이터·설정이 따로 있어서 다른 아티팩트를 읽을 때도 번호를 함께 적어야 합니다. `dumpsys account` 출력도 사용자마다 `User UserInfo{...}:` 로 시작하는 블록으로 나뉩니다. 계정 쪽 해석은 [계정 (Accounts)](accounts/index.md) 페이지에 있습니다.

이미 지운 사용자가 목록 파일이나 다른 기록에 흔적을 남기는지는 공개 자료가 없어 검체로 확인해야 합니다. `userlist.xml` 의 `nextSerialNumber` 값과 남아 있는 사용자들의 `serialNumber` 를 비교해 볼 수는 있지만, 번호가 비는 까닭이 소스에 드러나 있지 않아 지운 사용자가 있었다는 근거로 쓰지 않습니다.

비공개 프로필처럼 따로 잠글 수 있는 공간은 확보할 때의 잠금 상태에 따라 읽히는 범위가 달라질 수 있어서, 사용자별 암호화 영역을 설명한 [저장 공간 암호화 (Encryption)](../../01-foundations/storage/encryption/index.md) 페이지를 함께 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

사용자 xml 이 글자 XML 이라면 한 사용자 항목은 다음 모양이 됩니다. 속성 이름은 소스와 같고 [1], 값은 설명하려고 만든 예시이며 실제 기기에서 나온 것이 아닙니다.

```xml
<user id="10" serialNumber="10" type="android.os.usertype.full.SECONDARY"
      created="1700000000000" lastLoggedIn="1700000600000" />
```

`created` 의 1700000000000 은 유닉스 밀리초라서 2023-11-14 22:13:20 UTC 입니다. 파일을 헥스로 열어 첫 바이트가 `3C`(`<`)가 아니고 알아볼 수 없는 바이트로 시작하면 ABX 일 수 있으니 [안드로이드 바이너리 XML (ABX)](../../01-foundations/data-formats/abx.md) 페이지의 방법으로 먼저 글자 XML 로 바꿉니다.

### 공개 도구로 한 번

이미지에서는 `/data/system/users` 폴더를 통째로 복사한 뒤 사용자별 xml 에서 `id`, `type`, `created`, `lastLoggedIn`, `profileGroupId` 를 뽑아 표로 만듭니다. 라이브 기기에서는 다음 명령의 출력을 그대로 보관합니다.

```sh
adb shell dumpsys user > dumpsys_user.txt
grep -E '^  UserInfo|Type:|Created:|Last logged in|Unlock time:' dumpsys_user.txt
```

## 교차 검증

사용자별 계정은 [계정 (Accounts)](accounts/index.md) 에서, 사용자별로 설치된 앱은 [설치된 앱 (packages.xml)](../app-usage/packages/index.md) 에서 봅니다. 마지막 로그인 지문은 [기기 정보와 빌드 (build.prop·Build)](device-build.md) 의 현재 빌드와 비교합니다. 여러 사람이 한 기기를 썼는지 가려야 하면 [그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)](../../04-scenarios/activity/user-attribution.md) 시나리오의 순서를 따릅니다.

## 실습

공개 안드로이드 검체(NIST CFReDS 에 올라온 모바일 이미지 등)를 구해 다음을 풀어 봅니다.

1. `/data/system/users` 폴더에서 사용자 번호를 모두 적고, 각 번호의 `type` 과 부모 사용자를 표로 만듭니다.
2. 각 사용자의 `created`·`lastLoggedIn` 을 UTC 날짜로 바꾸고, 사용자 0 의 생성 시각이 다른 초기 설정 기록과 맞는지 봅니다.
3. `lastLoggedInFingerprint` 가 현재 build.prop 의 지문과 같은지 확인하고, 다르면 무엇을 뜻하는지 기록이 말하는 범위에서 적어 봅니다.

## 참고 문헌

1. UserManagerService.java — AOSP frameworks/base (GitHub 미러, main), https://raw.githubusercontent.com/aosp-mirror/platform_frameworks_base/main/services/core/java/com/android/server/pm/UserManagerService.java
2. Support multiple users — Android Open Source Project, https://source.android.com/docs/devices/admin/multi-user
