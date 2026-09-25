---
title: "암호 건 백업"
parent: "로컬 백업"
grand_parent: "기반 · 백업 형식"
nav_order: 240
---

# 암호 건 백업 (Encrypted Backup)

로컬 백업에 암호를 걸면 암호 없는 백업에 없는 데이터가 더 들어가고, iOS 10.2 베타 때 보고된 뒤로는 파일 목록인 Manifest.db 까지 암호화돼 암호 없이는 무엇이 들어 있는지도 볼 수 없습니다.

이 페이지는 무엇이 암호화되고 백업에 어떤 흔적이 남는지만 다룹니다. 암호를 푸는 방법은 다루지 않습니다.

## 이 형식을 쓰는 아티팩트

Apple 은 암호 건 백업에만 저장된 암호, Wi-Fi 설정, 웹사이트 방문 기록, 건강 데이터, 통화 기록이 들어간다고 안내하고, Face ID·Touch ID·기기 암호 데이터는 암호 건 백업에도 들어가지 않는다고 적습니다 [1]. 그래서 [저장된 암호](../../../02-artifacts/credentials-security/saved-passwords.md), [와이파이 기록](../../../02-artifacts/network/wifi.md) 의 Wi-Fi 설정, [사파리](../../../02-artifacts/browsers/safari/index.md) 의 방문 기록, [건강 데이터](../../../02-artifacts/health-wallet/health.md), [통화 기록](../../../02-artifacts/communications/call-history.md) 을 로컬 백업에서 보려면 암호 건 백업이어야 합니다. 관찰한 암호 없는 백업에도 사파리 앱 도메인(`AppDomain-com.apple.mobilesafari`)은 들어 있었으니, 앱 데이터 전체가 빠지는 것은 아닙니다.

스파이웨어 흔적을 검사하는 MVT(Mobile Verification Toolkit) 문서도 로컬 백업을 만들 때 "로컬 백업 암호화" 를 켜라고 안내합니다 [4].

## 구조

### 무엇이 어떻게 보호되나

Apple Platform Security Guide [3] 의 설명을 암호를 건 경우와 걸지 않은 경우로 나누면 아래와 같습니다.

| | 암호를 걸지 않은 백업 | 암호 건 백업 |
|---|---|---|
| 일반 파일 | 데이터 보호 등급과 상관없이 암호화하지 않음 | 백업 암호로 보호함 |
| 키체인 | 기기 고유 키(UID)에서 나온 키로 보호하고, 새 기기로 옮기지 못함 | 새 기기로 옮길 수 있음. 단, 다른 기기로 옮기지 않는 항목(ThisDeviceOnly)은 UID 에서 나온 키로 싸인 채 남아 원래 기기에만 복원됨 |

백업 키백(Backup Keybag)은 Finder(macOS 10.15 이후)나 iTunes(macOS 10.14 이하)로 암호 건 백업을 만들 때 생기고, 백업한 컴퓨터에 저장됩니다 [3]. 이 키백은 사용자가 정한 암호로 보호되며, 그 암호는 PBKDF2 를 1000만 번 거칩니다 [3]. Apple 이 드는 키백 종류는 사용자, 기기, 백업, 에스크로, 아이클라우드 백업 키백입니다 [3]. 키백과 보호 등급은 [데이터 보호](../../storage/data-protection/index.md), 키체인 항목의 짜임은 [키체인](../../storage/keychain.md) 에서 다룹니다.

### iOS 10.2 에서 달라진 점

2016년 11월 8일, iOS 10.2 베타로 만든 암호 건 백업에서 아래 변화가 보고됐습니다 [2].

| 자리 | 보고된 변화 |
|---|---|
| Manifest.db | 파일 전체가 암호화됨 |
| Manifest.plist | 새 키 ManifestKey 가 생김. 길이 44바이트, 앞 4바이트는 기기가 달라도 `04 00 00 00` |
| 백업 키백 머리 | 새 항목 세 개. DPWT(값 1), DPSL(20바이트 솔트), DPIC(반복 횟수 10,000,000) |

DPIC 의 1000만 번은 Apple 문서 [3] 의 PBKDF2 반복 횟수와 맞습니다. 이 형식이 그 뒤 지금까지 크게 바뀌지 않았다는 설명은 이번에 원문으로 확인하지 못했으니, 최신 iOS 백업을 다룰 때는 실제 파일로 다시 확인합니다.

아래는 보고 [2] 의 내용으로 만든 ManifestKey 의 모양이고, 특정 검체에서 나온 값이 아닙니다. 뒤쪽 40바이트는 기기마다 다른 값이라 `..` 로 적었습니다.

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0000    04 00 00 00 .. .. .. .. .. .. .. .. .. .. .. ..
0010    .. .. .. .. .. .. .. .. .. .. .. .. .. .. .. ..
0020    .. .. .. .. .. .. .. .. .. .. .. ..
        (모두 44바이트, 앞 4바이트만 기기와 상관없이 같음)
```

## 읽는 법

암호가 걸렸는지는 Manifest.plist 의 IsEncrypted 키로 판단합니다 [5]. 관찰한 백업에도 이 키가 있었습니다.

관찰한 백업은 암호를 걸지 않은 백업이었는데, Manifest.plist 에 BackupKeyBag 키는 있었고 ManifestKey 키는 없었습니다. 그래서 BackupKeyBag 키가 있다는 것만으로 암호 건 백업이라고 보지 않습니다. 암호 건 백업의 Manifest.plist 모양은 이번에 관찰하지 못했고, ManifestKey 가 생긴다는 내용은 보고 [2] 에 따른 것입니다.

| 확인할 것 | 암호 없는 백업 | 암호 건 백업 |
|---|---|---|
| Manifest.plist 의 IsEncrypted | 키가 있음(관찰) | 키로 판단 [5] |
| Manifest.plist 의 BackupKeyBag | 있었음(관찰) | 있음 [5] |
| Manifest.plist 의 ManifestKey | 없었음(관찰) | 생김(iOS 10.2 베타 보고 [2]) |
| Manifest.db | SQLite 로 바로 열림(관찰) | 파일 전체가 암호화돼 도메인·경로 목록을 볼 수 없음 [2] |

Manifest.plist 에는 WasPasscodeSet 키도 있었습니다. 이름으로 보면 기기 암호 설정 여부를 담는 것 같지만 값의 뜻은 확인하지 못했으니, 기기 암호에 관한 판단은 [암호와 Face ID 설정 흔적](../../../02-artifacts/system-account/passcode-biometrics.md) 의 다른 기록과 맞춰 봅니다. Info.plist·Status.plist 가 암호 건 백업에서도 평문으로 남는지는 이번에 확인하지 못했으니 실제 파일로 확인합니다.

### 키체인 백업 파일

관찰한 백업의 `KeychainDomain` 에는 `keychain-backup.plist` 가 있었고, 최상위 키는 keybag-uuid, genp, inet, cert, keys 였습니다. 암호를 걸지 않은 백업에서도 이 파일이 들어오지만, Apple 설명 [3] 대로 키체인은 UID 에서 나온 키로 보호되어 파일이 있어도 그 안 항목을 바로 읽을 수는 없습니다. 각 항목이 어떤 상태로 들어 있는지는 이 설명 말고는 확인하지 못했습니다.

### 건강 도메인

관찰한 암호 없는 백업에도 `HealthDomain` 항목이 2개 있었습니다. 그 두 항목이 무엇인지는 확인하지 못했습니다. Apple 은 건강 데이터가 암호 건 백업에만 들어간다고 안내하니 [1], 도메인 이름이 보인다고 해서 건강 기록이 백업에 들어 있다고 보지 않습니다. 도메인 목록은 [도메인과 파일 이름](domains-fileid.md) 에 있습니다.

## 포렌식에서 중요한 점

암호를 모르면 암호 건 백업 안의 파일뿐 아니라 Manifest.db 의 목록도 볼 수 없어, 어떤 앱의 데이터가 들어 있는지조차 확인하기 어렵습니다 [2]. MVT 문서도 암호가 없으면 백업에 접근하거나 백업을 고치거나 복호화할 수 없다며 백업 암호를 안전하게 보관하라고 안내합니다 [4]. 증거를 확보하는 단계에서 암호를 건 백업을 만들었다면 그 암호를 증거 기록과 함께 관리합니다.

백업 암호를 잊으면 Apple 은 아이클라우드 백업을 쓰거나 백업 암호를 재설정하라고 안내합니다 [1]. 재설정하면 새 암호로 새 백업을 만들 수 있지만 이전에 만든 암호 건 백업은 쓸 수 없게 됩니다 [1]. 기기에서 재설정하는 메뉴 위치와 그때 함께 초기화되는 설정은 이번에 확인하지 못했습니다.

## 함정

- 암호 없는 백업에서 저장된 암호·통화 기록 같은 데이터가 보이지 않는다고 기기에 그 데이터가 없었다고 보고하지 않습니다. 백업 종류 때문에 빠진 것일 수 있습니다 [1].
- BackupKeyBag 키는 암호 없는 백업에도 있었습니다. 암호 여부는 IsEncrypted 로 판단합니다.
- ManifestKey·DPWT·DPSL·DPIC 는 iOS 10.2 베타 시절 보고 [2] 에서 나온 이름입니다. 최신 iOS 에서 이름과 길이가 같은지는 실제 암호 건 백업으로 확인합니다.
- 두 단계로 PBKDF2 를 거친다는 설명이나, 파일마다 개별 키와 보호 등급이 Files.file 칸에 들어 있다는 설명도 보이지만 이번에 원문으로 확인하지 못해 여기서는 사실로 적지 않습니다.

## 도구

암호가 걸렸는지는 plist 를 읽는 도구로 Manifest.plist 의 IsEncrypted 만 보면 알 수 있습니다. MVT 문서 [4] 는 검사할 로컬 백업을 만드는 과정을 안내합니다. 공개 도구가 암호 건 백업을 제대로 다루는지는 [도구 검증](../../../03-techniques/reporting/tool-validation.md) 의 방법대로 알려진 백업으로 먼저 확인합니다.

## 참고 문헌

1. Apple Support — About encrypted backups on your iPhone, iPad, or iPod touch (108353) — https://support.apple.com/en-us/108353
2. GitHub horrorho/InflatableDonkey Issue #41 — iOS 10.2 beta new manifest encryption (2016-11-08) — https://github.com/horrorho/InflatableDonkey/issues/41
3. Apple Platform Security Guide — Keybags for Data Protection — https://support.apple.com/guide/security/keybags-for-data-protection-sec6483d5760/web
4. MVT (Mobile Verification Toolkit) 문서 — Backup with iTunes app — https://docs.mvt.re/en/latest/ios/backup/itunes/
5. Rich Infante — Reverse Engineering the iOS Backup (2017-03-16) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
