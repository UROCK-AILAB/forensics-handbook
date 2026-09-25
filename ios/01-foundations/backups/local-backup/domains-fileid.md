---
title: "도메인과 파일 이름"
parent: "로컬 백업"
grand_parent: "기반 · 백업 형식"
nav_order: 230
---

# 도메인과 파일 이름 (Domain·fileID)

로컬 백업은 기기 파일을 도메인(Domain)과 상대 경로로 나눠 적고, 백업 폴더 안에서는 이 둘을 이어 붙인 문자열의 SHA-1 해시를 파일 이름(fileID)으로 씁니다.

## 이 형식을 쓰는 아티팩트

로컬 백업에서 꺼내는 파일은 모두 도메인과 상대 경로로 가리킵니다. 메시지 데이터베이스는 `HomeDomain` 의 `Library/SMS/sms.db` 이고, 앱이 남긴 파일은 그 앱의 도메인 아래에 있습니다. 아티팩트 페이지가 "백업에서는 이 도메인의 이 경로" 라고 적으면, 이 페이지의 규칙으로 백업 폴더 안 실제 파일을 찾습니다. Manifest.db 의 표와 칸은 [백업 폴더 구조](structure.md) 에서 다룹니다.

## 구조

### fileID 만드는 규칙

fileID 는 도메인 이름, 하이픈 한 개, 상대 경로를 차례로 이은 문자열의 SHA-1 값입니다 [1].

```
fileID = sha1(domain + "-" + relativePath)

예: sha1("HomeDomain-Library/SMS/sms.db")
```

백업 폴더 안에서 이 파일이 놓이는 자리는 백업 형식 버전에 따라 다릅니다.

| 기기 iOS | 형식 버전(예) | 파일 자리 |
|---|---|---|
| iOS 9 기기 | 2.4 | 백업 폴더 바로 아래에 모든 파일 [1] |
| iOS 10·11 기기 | 3.2 | fileID 앞 두 글자로 된 하위 폴더 아래 [1] |

[1] 은 iOS 11 까지를 다룬 글이라 그 뒤 버전은 실제 백업 폴더에서 확인합니다. 두 글자 하위 폴더 형식에서 fileID 가 `ad0009ec04c44b544d37bfc7ab3438697d23d618` 인 파일은 `ad/ad0009ec04c44b544d37bfc7ab3438697d23d618` 에 있습니다 [2]. 이 예에서 보듯 백업 폴더 안 파일에는 확장자가 붙지 않고 fileID 만 이름으로 씁니다. Files 표에 올라 있는 폴더 항목도 실제 파일로 저장되는지는 이번에 확인하지 못했습니다.

### 도메인 이름의 짜임

관찰한 백업의 도메인은 모두 1428개였고, 그중 Apple 기본 영역이 1267개, 설치한 앱 등 나머지가 161개였습니다(확인 범위: iOS 27.0). Apple 기본 영역 1267개를 이름 앞부분으로 나누면 아래와 같습니다.

| 이름 앞부분 | 도메인 수 | 이름 예 |
|---|---|---|
| `AppDomain-` | 237 | `AppDomain-com.apple.mobilesafari`, `AppDomain-com.apple.MobileSMS` |
| `AppDomainGroup-` | 92 | `AppDomainGroup-group.com.apple.notes` |
| `AppDomainPlugin-` | 875 | `AppDomainPlugin-com.apple.Health.HealthBalanceWidgetExtension` |
| `SysContainerDomain-` | 19 | `SysContainerDomain-com.apple.springboard` |
| `SysSharedContainerDomain-` | 29 | `SysSharedContainerDomain-systemgroup.com.apple.bluetooth` |
| 앞부분 없는 고정 도메인 | 15 | 아래 표 |

앱 도메인은 앞부분 뒤에 번들 ID 나 앱 그룹 이름이 붙는 짜임이고, 다른 회사 앱도 `AppDomain-com.deere.mowerplus`, `AppDomain-ch.threema.iapp`, `AppDomain-com.agilebits.onepassword-ios` 처럼 같은 짜임을 따릅니다 [2]. 번들 ID 와 앱 그룹을 읽는 법은 [번들 ID와 앱 그룹](../../value-decoding/bundle-id-app-group.md) 에서 다룹니다.

### 고정 도메인

관찰한 백업의 고정 도메인 15개와 Manifest.db 에 올라 있던 항목 수입니다(확인 범위: iOS 27.0). 항목 수는 기기와 사용 상태에 따라 달라지니 도메인이 무엇을 담는지 가늠하는 데만 씁니다.

| 도메인 | 항목 수 | 관찰한 대표 파일 |
|---|---|---|
| CameraRollDomain | 173 | |
| DatabaseDomain | 9 | |
| HealthDomain | 2 | |
| HomeDomain | 1979 | `Library/SMS/sms.db` |
| InstallDomain | 6 | `Library/MobileInstallation/BackedUpState/SystemAppInstallState.plist`, `BackupSystemAppInstallState.plist` |
| KeyboardDomain | 6 | |
| KeychainDomain | 2 | `keychain-backup.plist` |
| ManagedPreferencesDomain | 4 | |
| MediaDomain | 303 | |
| MobileDeviceDomain | 3 | `ProvisioningProfiles/mis.db` |
| ProtectedDomain | 8 | |
| RootDomain | 58 | `Library/Caches/locationd/consolidated.db`, `Library/Caches/locationd/clients.plist`, `Library/Preferences/` 아래 여러 plist |
| SystemPreferencesDomain | 11 | |
| TonesDomain | 4 | |
| WirelessDomain | 21 | |

`KeychainDomain` 의 키체인 백업 파일과 `HealthDomain` 항목을 어떻게 해석하는지는 [암호 건 백업](encrypted-backup.md) 에서 다룹니다.

기기 안의 백업 설정 파일(`com.apple.MobileBackup.plist`)의 PreflightSizing 아래에는 NetworkDomain 이라는 이름도 나오지만, 같은 백업의 Manifest.db 도메인 목록에는 NetworkDomain 이 없었습니다(확인 범위: iOS 27.0). 설정 파일에 도메인 이름이 있다고 해서 그 도메인이 백업에 들어 있다고 보지 않습니다. 이 설정 파일은 [백업 폴더 구조](structure.md) 에서 다룹니다.

각 도메인이 기기 안의 어느 폴더에 대응하는지는 이번에 연 자료로 확인하지 못해 적지 않습니다. 도메인 안의 위치는 relativePath 로 판단합니다.

## 읽는 법

찾을 파일의 도메인과 경로를 알면 두 가지 방법으로 백업 폴더 안 파일에 닿습니다.

1. Manifest.db 에서 찾기. 도메인과 경로로 Files 표를 조회해 fileID 를 얻습니다.

```sql
SELECT fileID, flags
FROM Files
WHERE domain = 'HomeDomain' AND relativePath = 'Library/SMS/sms.db';
```

2. 직접 계산하기. Manifest.db 를 쓸 수 없을 때는 규칙대로 해시를 계산합니다. 아래 코드는 규칙을 보여 주는 예시이고, 결과 값은 적지 않았습니다.

```python
import hashlib
fid = hashlib.sha1("HomeDomain-Library/SMS/sms.db".encode("utf-8")).hexdigest()
print(fid[:2] + "/" + fid)   # 두 글자 하위 폴더 형식의 파일 자리
```

앱 하나의 파일을 모두 보려면 도메인 이름으로 묶어 조회합니다.

```sql
SELECT domain, relativePath, fileID
FROM Files
WHERE domain LIKE 'AppDomain%com.apple.mobilesafari%'
ORDER BY domain, relativePath;
```

`AppDomain-`, `AppDomainGroup-`, `AppDomainPlugin-` 은 서로 다른 도메인이라 앱 본체 도메인만 보면 앱 그룹이나 확장 기능 쪽 파일을 놓칩니다.

## 포렌식에서 중요한 점

fileID 는 도메인과 경로만으로 정해져서, 같은 도메인·경로의 파일은 백업이 달라도 fileID 가 같습니다. 여러 백업을 나란히 놓고 같은 파일을 비교할 때 이 성질을 씁니다.

도메인 목록 자체도 단서가 됩니다. 앱 도메인 이름에는 번들 ID 가 들어 있어, 백업을 만든 시점에 어떤 앱의 데이터가 백업 대상이었는지를 파일을 열기 전에 목록만으로 볼 수 있습니다. 다만 도메인이 있다는 것은 그 앱의 데이터가 백업에 들어왔다는 기록일 뿐이고, 앱을 언제 설치하고 썼는지는 [설치된 앱](../../../02-artifacts/app-usage/installed-apps.md) 같은 다른 기록으로 확인합니다.

## 함정

- 해시는 입력 글자와 바이트가 조금만 달라도 값이 달라집니다. 도메인과 경로 사이 하이픈, 경로 앞 `/` 유무, 대소문자를 Manifest.db 에 적힌 그대로 맞춥니다.
- 계산한 fileID 로 파일을 찾지 못하면 해당 항목이 백업에서 빠졌거나 경로를 잘못 적은 것일 수 있으니, 먼저 Manifest.db 로 항목이 있는지 확인합니다.
- 암호 건 백업은 Manifest.db 자체가 암호화돼 있어 도메인·경로 목록을 볼 수 없습니다([암호 건 백업](encrypted-backup.md)).
- 항목 수와 도메인 수는 관찰한 기기 하나의 값입니다. 다른 기기에서 도메인이 더 많거나 적어도 이상한 일이 아닙니다.

## 도구

SQLite 를 여는 도구로 Manifest.db 를 조회하고, 해시는 Python 의 hashlib 처럼 SHA-1 을 계산하는 도구면 충분합니다. [2] 는 R 로 Manifest.db 를 조회하고 fileID 로 파일 자리를 만드는 과정을 보여 줍니다.

## 참고 문헌

1. Rich Infante — Reverse Engineering the iOS Backup (2017-03-16) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
2. rud.is — Trawling Through iOS Backups For Treasure (2019-06-02) — https://rud.is/b/2019/06/02/trawling-through-ios-backups-for-treasure-a-k-a-how-to-fish-for-target-files-in-ios-backups-with-r/
