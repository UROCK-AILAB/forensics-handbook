---
title: "앱 데이터 폴더 구조"
parent: "기반 · 저장 구조"
nav_order: 130
---

# 앱 데이터 폴더 구조 (/data/data·/data/user)

## 한 줄 요약

앱 하나의 데이터는 사용자마다 CE 영역의 앱 폴더와 DE 영역의 앱 폴더, 그리고 공용 저장 공간 쪽 앱 전용 폴더로 나뉘어 놓이고, 각 앱 폴더 안은 `databases`·`shared_prefs`·`files`·`cache` 같은 정해진 하위 폴더로 짜여 있습니다.

## 이 구조를 쓰는 아티팩트

메신저·브라우저·지도처럼 앱이 직접 남기는 기록은 거의 모두 이 폴더 안에 있고, 아티팩트 사전의 앱 페이지들은 "어느 패키지 폴더의 어느 하위 폴더에 무엇이 있는가" 를 이 페이지의 틀 위에서 설명합니다. 예를 들어 [카카오톡](../../02-artifacts/messengers/kakaotalk/index.md)·[크롬](../../02-artifacts/browsers/chrome/index.md)·[구글 지도](../../02-artifacts/location/google-maps.md) 페이지가 그렇습니다. 하위 폴더 안의 파일 형식은 [SQLite 데이터베이스](../data-formats/sqlite/index.md)와 [설정 XML과 SharedPreferences](../data-formats/shared-preferences.md) 페이지에서 다루고, 폴더를 어떤 순서로 훑는지는 [앱 데이터 분석](../../03-techniques/analysis/app-data-analysis/index.md) 페이지에서 다룹니다.

## 구조

### 경로를 만드는 규칙

앱 폴더 경로는 설치 데몬 installd 가 정해진 규칙으로 만듭니다. AOSP installd 소스의 경로 함수를 정리하면 아래와 같고, 표의 경로는 내부 저장소 기준입니다.

| 폴더 | 경로 | 소스에 적힌 규칙 |
|---|---|---|
| 사용자 0 의 CE 앱 폴더 | `/data/data/<패키지>` | 내부 저장소의 사용자 0 이고 `/data/data` 가 실제 디렉터리이면 `/data/data` 를 돌려줍니다 |
| 그 밖의 사용자 CE 앱 폴더 | `/data/user/<userid>/<패키지>` | 기본 규칙은 `<data 뿌리>/user/<userid>` 입니다 |
| DE 앱 폴더 | `/data/user_de/<userid>/<패키지>` | 사용자 0 도 예외 없이 이 경로입니다 |
| 설치된 앱 코드(APK) | `/data/app` 아래 | `<data 뿌리>/app` 입니다 |
| 공용 저장 공간의 실제 위치 | `/data/media/<userid>` | `<data 뿌리>/media/<userid>` 입니다 |
| SDK 런타임 데이터 | `/data/misc_ce/<userid>/sdksandbox`, `/data/misc_de/<userid>/sdksandbox` | CE·DE 에 하나씩 있습니다 |
| ART 프로필 | 프로필 폴더 아래 `cur/<userid>`, `ref` | 사용자별 현재 프로필과 참조 프로필입니다 |

`<data 뿌리>` 는 내부 저장소면 `/data` 이고, 채택 저장소 (Adoptable Storage) 로 쓰는 외장 볼륨이면 `/mnt/expand/<volume_uuid>` 입니다. 그래서 채택 저장소를 쓰는 기기에서는 같은 폴더 구조가 `/mnt/expand/<volume_uuid>` 아래에도 생길 수 있습니다. `/data/app` 아래 폴더 이름을 붙이는 규칙과 ART 프로필 폴더의 실제 전체 경로는 이 페이지의 출처에서 확인하지 못해 적지 않습니다.

사용자 0 의 CE 앱 데이터는 `/data/data` 에 있고, 사용자 10 이라면 `/data/user/10/<패키지>` 처럼 사용자 번호가 경로에 들어갑니다. 소스 주석은 `/data/data` 를 돌려주는 이유를 옛 시스템과 맞추기 위해서라고만 적고 있어서, `/data/user/0` 이 `/data/data` 를 가리키는 링크인지는 이 출처로 확인하지 못했습니다. CE 와 DE 가 무엇이고 사용자별 CE·DE 경로 전체가 어떻게 되는지는 [저장 공간 암호화](encryption/index.md) 갈래에서 다룹니다.

> 그림 자리: 사용자 0 과 두 번째 사용자 각각에 대해 CE 앱 폴더, DE 앱 폴더, `/data/media/<userid>`, 공용 저장 공간의 `Android/data/<패키지>` 가 어떻게 나란히 놓이는지 보여 주는 폴더 나무

### 앱 폴더 안의 하위 폴더

앱 코드가 저장 위치를 얻는 함수와 실제 하위 폴더 이름은 AOSP 의 ContextImpl 에 정해져 있습니다.

| 하위 폴더 | 앱이 부르는 함수 | 담기는 것 |
|---|---|---|
| `databases` | `getDatabasePath()` | 앱의 SQLite 데이터베이스 |
| `shared_prefs` | SharedPreferences API | SharedPreferences 파일, 이름은 `<이름>.xml` |
| `files` | `getFilesDir()` | 앱이 오래 두는 파일 |
| `no_backup` | `getNoBackupFilesDir()` | 백업에서 빼는 파일 |
| `cache` | `getCacheDir()` | 캐시 파일 |
| `code_cache` | `getCodeCacheDir()` | 코드 캐시 |

`cache` 폴더에는 확장 속성 `user.inode_cache` 를, `code_cache` 폴더에는 `user.inode_code_cache` 를 씁니다. 이 속성을 어디에 쓰는지는 출처에서 확인하지 못했지만, 파일 시스템 이미지에서 확장 속성을 읽을 수 있다면 두 폴더를 알아보는 표시로 쓸 수 있습니다. 이 표에 없는 폴더(`app_` 로 시작하는 폴더 등)와 SharedPreferences 백업 파일, SQLite 부속 파일의 이름 규칙은 이 페이지의 출처에 없어서 다루지 않습니다.

### 공용 저장 공간 쪽 앱 전용 폴더

앱은 `getExternalFilesDir(null)` 과 `getExternalCacheDir()` 로 공용 저장 공간 안에도 자기 전용 폴더를 얻고, 이 폴더는 저장 볼륨의 `Android/data/<패키지>` 아래에 생깁니다. 공식 문서는 내부와 외부 두 곳을 묶어 "앱 전용 저장소 (App-specific Storage)" 라고 부릅니다. 앱이 내부 앱 전용 폴더를 읽고 쓸 때는 권한이 필요 없고, 외부 앱 전용 폴더도 Android 4.4(API 19) 이상이면 권한 없이 씁니다. Android 11 이상에서는 앱이 외부 저장소에 자기 폴더를 직접 만들 수 없어서 시스템이 준 폴더를 씁니다. 다른 앱이 이 폴더에 접근할 수 있었는지는 Android 버전과 권한에 따라 달라지고, 그 규칙은 [공용 저장 공간](shared-storage.md) 페이지에서 다룹니다.

### 사용자가 여럿인 기기

관찰 기기의 `dumpsys user` 출력에는 주 사용자(`isPrimary=true`) 말고도 `parentId` 가 붙은 두 번째 사용자가 있었고, 사용자 번호는 가려져 있어서 그 사용자의 앱 폴더가 `/data/user/` 아래 몇 번인지는 알 수 없습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). 두 번째 사용자가 보안 폴더인지도 이 관찰로는 확인하지 못했습니다. 같은 기기에 설치된 앱은 시스템 앱 486개, 사용자가 설치한 앱 168개였습니다(확인 범위: SM-S937N, Android 16, One UI 8.5). 사용자 목록을 읽는 법은 [사용자와 프로필](../../02-artifacts/system-account/users-profiles.md), 보안 폴더와 작업 프로필은 [보안 폴더와 작업 프로필](../security-model/secure-folder-work-profile.md) 페이지를 봅니다.

## 읽는 법

확보한 파일 시스템에서 앱 하나의 데이터를 빠짐없이 모으려면 아래 순서로 봅니다.

1. 사용자 목록부터 확인합니다. 사용자 0 만 보면 두 번째 사용자나 프로필의 앱 데이터를 놓칩니다.
2. 사용자마다 CE 앱 폴더(사용자 0 은 `/data/data`, 그 밖에는 `/data/user/<userid>`)와 DE 앱 폴더(`/data/user_de/<userid>`)를 짝지어 봅니다.
3. 패키지 이름으로 폴더를 찾고, [설치된 앱](../../02-artifacts/app-usage/packages/index.md) 목록과 대조해 지금 설치된 앱인지, 폴더만 남은 앱인지 가립니다. 패키지 이름과 UID 를 읽는 법은 [패키지 이름과 UID](../value-decoding/package-uid.md) 페이지에 있습니다.
4. 하위 폴더별로 형식을 나눠 읽습니다. `databases` 는 SQLite, `shared_prefs` 는 XML 로 읽고, `files` 와 `cache` 는 앱마다 형식이 다릅니다.
5. 공용 저장 공간의 `Android/data/<패키지>` 도 같은 앱의 데이터로 함께 묶습니다.

관찰 기기에서는 adb 일반 셸 권한으로 `/data` 아래를 읽어 보지 않았습니다. 이 폴더들을 어떤 수집 방식으로 얻는지는 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md) 페이지에서 다룹니다.

## 포렌식에서 중요한 점

공식 문서는 사용자가 앱을 지우면 앱 전용 저장소에 저장한 파일도 지워진다고 적고, 여기에는 내부 폴더와 `Android/data/<패키지>` 둘 다 들어갑니다. 그래서 앱이 지워진 기기에서는 앱 폴더 자체가 없는 것이 정상이고, 지워진 폴더의 내용을 찾는 일은 [삭제 데이터 복구](../../03-techniques/analysis/data-recovery/index.md) 와 [파일 시스템](filesystems/index.md) 페이지의 범위로 넘어갑니다.

`cache` 폴더는 저장 공간이 모자랄 때 시스템이 파일을 지울 수 있는 곳입니다. `getAllocatableBytes()` 가 현재 빈 공간보다 큰 값을 돌려줄 수 있는 것도 시스템이 다른 앱의 캐시에서 지울 수 있는 파일까지 계산에 넣기 때문입니다. 따라서 캐시 파일이 없다는 사실만으로 사용자가 지웠다고 단정할 수 없습니다.

공식 문서는 Android 10 이상에서 내부 앱 전용 위치가 암호화된다고 적고, Android 10 이상으로 출시한 기기는 파일 단위 암호화를 반드시 써야 합니다. 파일 단위 암호화는 파일 내용과 이름을 함께 암호화하고, 키 없이 보면 파일 이름이 base64url 형태의 문자열로 보입니다. 사용자가 잠금을 풀기 전 상태로 확보한 이미지라면 CE 앱 폴더 아래 이름이 패키지 이름이나 `databases` 같은 원래 이름으로 보이지 않을 수 있고, 이때 폴더 구조로 앱을 찾는 방법은 통하지 않습니다. 자세한 조건은 [저장 공간 암호화](encryption/index.md) 갈래를 봅니다.

Android 7.0(API 24) 이상에서는 앱이 `openFileOutput()` 에 `Context.MODE_PRIVATE` 가 아닌 모드를 주면 SecurityException 이 나서, 내부 앱 폴더의 파일을 다른 앱이 읽도록 열어 두는 옛 방식이 막혀 있습니다. 앱 사이의 격리 규칙 전체는 [앱 샌드박스와 권한](../security-model/sandbox-permissions.md) 페이지에서 다룹니다.

## 함정

- **같은 데이터를 두 번 세기.** 추출본에 `/data/data` 와 `/data/user/0` 이 모두 보이면 둘이 같은 곳인지 먼저 확인합니다. 따로 세면 같은 앱의 파일이 두 번 잡힙니다.
- **DE 폴더 빼먹기.** CE 앱 폴더만 보고 `/data/user_de/<userid>/<패키지>` 를 보지 않으면 다이렉트 부트 중에도 쓰는 데이터를 놓칩니다.
- **사용자 0 만 보기.** 두 번째 사용자나 프로필이 있는 기기에서는 `/data/user/<userid>` 아래에 같은 패키지 폴더가 따로 있을 수 있습니다.
- **공용 저장 공간 쪽 폴더 빼먹기.** 같은 앱의 파일이 `Android/data/<패키지>` 에도 있을 수 있어서, 내부 앱 폴더만 보면 한쪽만 보게 됩니다.
- **채택 저장소.** 채택 저장소를 쓰는 기기는 앱 데이터 뿌리가 `/mnt/expand/<volume_uuid>` 로 바뀔 수 있습니다.
- **삼성 기기의 사용자 번호.** 보안 폴더나 듀얼 메신저가 어떤 사용자 번호를 쓰는지는 이 핸드북에서 확인하지 못했습니다. 번호를 짐작해 경로를 고정하지 말고 사용자 목록에서 읽어 옵니다.

## 도구

폴더 구조 자체를 읽는 데는 특별한 도구가 필요 없고, 확보한 이미지나 파일 시스템 추출본을 여는 파일 탐색 도구면 충분합니다. 하위 폴더 안의 파일은 형식별 도구로 읽는데, SQLite 는 [SQLite 데이터베이스](../data-formats/sqlite/index.md) 페이지, SharedPreferences 는 [설정 XML과 SharedPreferences](../data-formats/shared-preferences.md) 페이지에서 읽는 법을 다룹니다. ALEAPP 같은 공개 분석 도구도 추출본에서 패키지 폴더를 찾아 파일을 읽지만, 어떤 경로 패턴(`/data/data`, `/data/user`)으로 찾는지는 도구 버전마다 확인하고 쓰는 편이 안전합니다.

## 참고 문헌

1. Access app-specific files — Android Developers, https://developer.android.com/training/data-storage/app-specific
2. Manage all files on a storage device — Android Developers, https://developer.android.com/training/data-storage/manage-all-files
3. cmds/installd/utils.cpp (main 브랜치) — AOSP frameworks/native, https://android.googlesource.com/platform/frameworks/native/+/refs/heads/main/cmds/installd/utils.cpp
4. core/java/android/app/ContextImpl.java (main 브랜치) — AOSP frameworks/base, https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/app/ContextImpl.java
5. File-based encryption — Android Open Source Project, https://source.android.com/docs/security/features/encryption/file-based
6. Filesystem-level encryption (fscrypt) — docs.kernel.org, https://docs.kernel.org/filesystems/fscrypt.html
