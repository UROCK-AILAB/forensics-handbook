---
title: "계정 탈취 흔적"
parent: "시나리오 · 침해 사고"
nav_order: 1640
---

# 계정 탈취 흔적 (Account Takeover)

## 조사 질문

사용자의 Apple 계정이나 기기에 등록한 다른 계정을 남이 가로챘는지, 기기에 그 흔적이 남았는지를 가립니다. 계정 탈취 (account takeover)의 핵심 기록인 로그인 내역과 계정에 연결된 기기 목록은 사용자가 account.apple.com 에서 봅니다 [1]. 이 기록이 기기 파일에도 남는다는 공개 자료는 없습니다. 그래서 기기 포렌식은 서버 기록을 대신하지 못하고, 기기 쪽에서 계정이 추가·변경된 흔적과 사용자 진술을 맞춰 보는 데까지 다룹니다. 서버 쪽 자료를 받는 일은 [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md)에 있습니다.

## 먼저 확인할 것

**사용자가 겪은 징후**를 아래 탈취 징후 목록에 맞춰 묻습니다 [1]. 아래 표는 징후마다 기기에서 대조해 볼 곳을 함께 적은 것이고, 오른쪽 칸은 대조해 볼 후보일 뿐이라서, 대조 결과만으로 탈취를 단정하지 않습니다.

| 탈취 징후 [1] | 기기에서 대조해 볼 곳 |
|---|---|
| 알아보지 못하는 계정 활동 알림(알림 또는 이메일) | [알림 기록](../../02-artifacts/app-usage/notifications.md), [메일 앱](../../02-artifacts/mail-cloud/apple-mail.md) |
| 요청하지 않은 2단계 인증 코드를 받음 | 받은 시각을 진술로 확보, 신뢰하는 전화번호로 왔다면 [메시지](../../02-artifacts/communications/messages/index.md) |
| 보내지 않은 메시지, 지우지 않았는데 지워진 항목, 바꾸지 않은 계정 정보 | `sms.db` 의 보낸 메시지, 계정 DB |
| 추가하지 않았거나 모르는 신뢰하는 기기, 모르는 구입 내역 | 서버 쪽 기기 목록, [앱 스토어 기록](../../02-artifacts/app-usage/app-store.md) |
| 암호가 더는 맞지 않음 | 사용자 진술 |
| 본인이 아닌 누가 기기를 잠그거나 분실 모드로 바꿈 | [나의 찾기](../../02-artifacts/location/find-my.md) 설정 plist |

**사용자가 이미 한 조치와 그 시각**도 적습니다. 탈취가 의심될 때 권하는 조치는 계정 암호를 강하고 고유한 것으로 바꾸고(이미 바뀌었으면 재설정), account.apple.com 에서 틀린 개인·보안 정보를 고치고, 모르는 기기를 계정에서 지우고, 이메일 제공자와 통신사에 확인해 모든 이메일 주소와 전화번호를 본인이 통제하는지 확인하는 것입니다. 2단계 인증, 보안 키, 도난 기기 보호도 권합니다 [1]. 조치한 시각을 알아야 기기에 남은 변경이 탈취한 쪽의 것인지 사용자의 조치인지를 나눌 수 있습니다.

**2단계 인증이 어떻게 동작하는지**를 알고 진술을 듣습니다. 새 기기나 웹에서 로그인할 때는 Apple 계정 암호와 함께 6자리 확인 코드가 필요하고, 코드는 신뢰하는 기기에 자동으로 뜨거나 신뢰하는 전화번호로 옵니다. iCloud 의 종단 간 암호화 데이터를 쓰면 기기 중 하나의 암호를 추가로 물을 수 있습니다. 한 번 로그인한 기기는 완전히 로그아웃하거나, 기기를 지우거나, 보안 때문에 암호를 바꾸지 않는 한 코드를 다시 묻지 않습니다 [2]. 확인 코드는 새 기기나 웹에서 로그인할 때 요구하는 코드라서, 요청하지 않은 코드를 받았다면 그 시각을 적어 두고 계정 쪽 로그인 기록과 맞춰 봅니다. Apple 이 로그인이나 "허용" 을 요구하지 않는다는 점은 [스미싱 흔적](smishing.md)에 있습니다.

**도난 기기 보호 (Stolen Device Protection)가 켜져 있었는지**도 묻습니다. iOS 17.3 이상에서 설정의 "Face ID 및 암호" 안에서 켜고, 기본으로는 집이나 직장처럼 위치 서비스가 중요 위치로 판단한 익숙한 장소 밖에서만 작동하지만 보안 지연을 "항상" 요구하도록 바꿀 수도 있습니다. 이 기능은 기본으로 켜져 있을 수 있어서, 사용자가 켠 적이 없다고 해도 꺼져 있었다고 단정하지 않습니다 [3]. 켜져 있으면 다음 동작에 제한이 걸립니다 [3].

| 제한 | 해당 동작 |
|---|---|
| 기기 암호 대신 Face ID·Touch ID 만 됨 | 키체인의 암호·패스키 사용, Safari 자동 완성의 결제 수단 사용, 분실 모드 끄기, 잠긴 앱 열기, 모든 콘텐츠 및 설정 지우기, 빠른 시작으로 새 기기 설정, eSIM 설정·이전 등 |
| 1시간 보안 지연 | Apple 계정 암호 변경, Apple 계정 로그아웃, 계정 보안 설정 변경, Face ID·Touch ID 추가·제거, 기기 암호 변경, 모든 설정 재설정, MDM 등록, 도난 기기 보호 끄기 |

이 기능이 켜졌는지, 지연이 걸렸는지를 담는 파일과 키는 공개 자료가 없어서 사용자 진술과 설정 화면으로 확인합니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 계정 DB `Accounts3.sqlite` | 기기에 등록된 계정과 그 종류, 사용자 이름 | [애플 계정](../../02-artifacts/system-account/apple-account.md) |
| 2 | Apple 계정 상태 plist | 로그인 상태 | [애플 계정](../../02-artifacts/system-account/apple-account.md) |
| 3 | 나의 찾기 plist | 나의 찾기 계정과 분실 모드 관련 값 | [나의 찾기](../../02-artifacts/location/find-my.md) |
| 4 | `sms.db` 의 보낸 메시지 | 사용자가 보내지 않았다는 메시지 | [메시지](../../02-artifacts/communications/messages/index.md) |
| 5 | 구성 프로파일 기록 | 모르는 프로파일·MDM 등록 | [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md) |
| 6 | 키체인·암호 유출 경고 plist | 저장된 암호가 있는 곳 | [저장된 암호](../../02-artifacts/credentials-security/saved-passwords.md) |

## 분석 흐름

1. **계정 DB 에서 모르는 계정을 찾습니다.** 기기에서는 `/private/var/mobile/Library/Accounts/Accounts3.sqlite` 에 있고 [4], 로컬 백업에서는 `HomeDomain :: Library/Accounts/Accounts#.sqlite` 와 `HomeDomain :: Library/Accounts/VerifiedBackup/Accounts#.sqlite` 로 보입니다(`#` 자리에 숫자가 들어감). 표와 칸은 다음과 같습니다.

   ```
   ZACCOUNT:        ZACTIVE, ZAUTHENTICATED, ZACCOUNTTYPE, ZPARENTACCOUNT, ZDATE,
                    ZLASTCREDENTIALRENEWALREJECTIONDATE, ZACCOUNTDESCRIPTION,
                    ZIDENTIFIER, ZOWNINGBUNDLEID, ZUSERNAME …
   ZACCOUNTTYPE:    ZACCOUNTTYPEDESCRIPTION, ZIDENTIFIER …
   ZCREDENTIALITEM: ZEXPIRATIONDATE, ZACCOUNTIDENTIFIER, ZSERVICENAME …
   ```

   이 DB 에서 계정을 추가한 시각, 사용자 이름, 계정 종류 등을 뽑을 수 있습니다 [4]. `ZDATE` 가 그 추가 시각인지와 어떤 기준 시각인지는 공개 자료로 정해지지 않아서, 사용자가 계정을 추가했다고 기억하는 시각과 먼저 맞춰 봅니다. 사용자가 모르는 `ZUSERNAME` 의 메일·클라우드 계정이 있으면 탈취한 쪽이 추가했을 가능성을 두고 조사하되, 사용자가 잊은 계정일 수도 있어서 진술로 확인합니다.

2. **Apple 계정 상태를 봅니다.** `HomeDomain :: Library/Preferences/com.apple.appleaccount.informationcache.plist` 에 `AAAccountFullName`, `AAIsAccountSignedIn`, `AAPrimaryAccountSignInState`, `AAProfilePictureCacheURL` 키가 있습니다. 이름과 로그인 상태가 사용자 진술과 다른지 봅니다.

3. **분실 모드와 나의 찾기 계정을 봅니다.** 남이 기기를 분실 모드로 바꾼 것은 탈취 징후입니다 [1]. 백업에는 다음 파일이 있습니다.

   | 파일 | 키 이름 |
   |---|---|
   | `HomeDomain :: Library/Preferences/com.apple.icloud.findmydeviced.FMIPAccounts.plist` | `addTime`, `osVersion`, `versionHistory`, `lowBatteryLocate`, `dsid`, `enableContext` |
   | `SysSharedContainerDomain-systemgroup.com.apple.icloud.findmydevice.managed :: Library/Preferences/FMIPStateInfo.plist` | `fmipActive`, `fmipLostModeType` |

   `fmipLostModeType` 은 이름으로 보아 분실 모드와 관련된 값이지만 값의 뜻을 밝힌 공개 자료가 없습니다. `addTime` 의 기준 시각도 공개 자료가 없습니다. 같은 기기에서 분실 모드를 켜지 않은 상태의 값과 견주고, 해석 근거를 보고서에 적습니다.

4. **보내지 않았다는 메시지를 봅니다.** `sms.db` 의 `message.is_from_me` 가 1 인 행이 보낸 메시지이고 [5], 사용자가 보내지 않았다고 말한 메시지와 시각·상대를 맞춰 봅니다. 이 값은 사용자 쪽에서 보낸 메시지라는 것까지만 말하고, 누가 보냈는지는 말하지 않습니다. 누가 기기를 쓰고 있었는지는 [그 시각에 폰을 쓴 사람이 누구인가](../activity/user-attribution.md)를 따릅니다.

5. **2단계 인증 화면의 흔적을 적어 둡니다.** 백업에는 `AppDomainPlugin-com.apple.AuthKitUI.AKSecondFactorAlert`, `AKSecondFactorEntryAlert`, `AKLocationSignInAlert`, `AKFollowUpServerUIExtension` 플러그인 도메인과 `AppDomain-com.apple.AuthKitUIService` 도메인이 있습니다. 이름으로 보아 2단계 인증 알림 화면과 관련 있어 보이지만, 안의 파일에 로그인 시도 기록이 남는지는 공개 자료가 없어 검체로 확인해야 합니다.

6. **프로파일과 MDM 등록을 봅니다.** 도난 기기 보호가 켜져 있으면 MDM 등록에 1시간 보안 지연이 걸립니다 [3]. 백업에는 `SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles :: Library/ConfigurationProfiles/MCProfileEvents.plist` 가 있습니다. 사용자가 모르는 프로파일 설치나 MDM 등록이 있는지 [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md)에서 봅니다.

7. **저장된 암호가 어디 있는지 적습니다.** 백업에는 `KeychainDomain :: keychain-backup.plist`(키 `keybag-uuid`, `genp`, `inet`, `cert`, `keys`)와 `HomeDomain :: Library/Preferences/com.apple.Safari.PasswordBreachAgent.plist` 가 있습니다. 암호화하지 않은 백업에서 키체인 항목을 읽을 수 있는지와 암호 유출 경고 plist 의 키·동작은 검체에서 확인합니다. 구조는 [키체인](../../01-foundations/storage/keychain.md)과 [저장된 암호](../../02-artifacts/credentials-security/saved-passwords.md)에 있습니다.

## 흔한 오판

- **기기에서 로그인 내역을 찾으려 합니다.** Apple 계정의 로그인 내역과 기기 목록은 account.apple.com 에서 봅니다 [1]. 기기 쪽 흔적이 없다는 사실은 로그인이 없었다는 뜻이 아닙니다.
- **사용자의 조치와 탈취한 쪽의 변경을 섞습니다.** 암호 변경·기기 제거 같은 조치를 한 시각을 먼저 받아 두지 않으면 두 변경을 나눌 수 없습니다.
- **키 이름만 보고 값을 해석합니다.** `fmipLostModeType`, `ZDATE`, `addTime` 은 뜻이나 기준 시각이 밝혀지지 않은 칸입니다. 보고서에는 값과 해석 근거를 함께 적습니다.
- **키체인 파일이 있으니 저장된 암호를 봤다고 씁니다.** 파일이 있다는 것과 항목을 읽을 수 있다는 것은 다릅니다.

## 보고서 문장 예

> 계정 DB `ZACCOUNT` 표에 사용자가 모른다고 진술한 사용자 이름 (이름)의 계정 행이 있었다. 이 행의 `ZDATE` 값은 (값)이지만, 이 칸이 계정 추가 시각인지는 확인하지 못했다.

> `FMIPStateInfo.plist` 의 `fmipLostModeType` 값은 (값)이다. 이 값이 분실 모드의 어떤 상태를 뜻하는지는 확인하지 못했고, 분실 모드 여부는 서버 쪽 기록으로 확인해야 한다.

> Apple 계정의 로그인 내역과 연결된 기기 목록은 account.apple.com 에서 보는 서버 쪽 기록이라서 이 기기 분석 범위에 들어가지 않는다.

## 함께 볼 페이지

- [스미싱 흔적](smishing.md) — 가짜 로그인 페이지로 이어진 문자
- [스파이웨어 감염 흔적](spyware.md) — 계정 탈취가 기기 감염과 겹칠 때
- [애플 계정](../../02-artifacts/system-account/apple-account.md) · [나의 찾기](../../02-artifacts/location/find-my.md) · [저장된 암호](../../02-artifacts/credentials-security/saved-passwords.md)
- [클라우드 데이터](../../03-techniques/acquisition/cloud-data.md) — 서버 쪽 기록
- [그 시각에 폰을 쓴 사람이 누구인가](../activity/user-attribution.md)

## 참고 문헌

1. Apple Support, If you think your Apple Account has been compromised (102560, 2025-12-05) — https://support.apple.com/en-us/102560
2. Apple Support, Two-factor authentication for Apple Account (102660, 2026-08-13) — https://support.apple.com/en-us/102660
3. Apple Support, About Stolen Device Protection for iPhone (120340, 2026-07-31) — https://support.apple.com/en-us/120340
4. Forensafe, Apple Accounts — https://forensafe.com/blogs/AppleAccounts.html
5. iLEAPP, scripts/artifacts/sms.py — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/sms.py
