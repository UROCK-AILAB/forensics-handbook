---
title: "그 시각에 폰을 쓴 사람이 누구인가"
parent: "시나리오 · 행위 재구성"
nav_order: 1480
---

# 그 시각에 폰을 쓴 사람이 누구인가 (User Attribution)

기기에 남은 기록은 기기가 어떤 상태였는지를 보여 줄 뿐이고, 그 순간 누가 손에 들고 있었는지는 직접 말하지 않습니다. 이 시나리오는 특정 시각의 기기 사용을 사람과 이을 근거를 모으고, 그 근거가 어디까지 말하는지를 나눠 적는 방법을 다룹니다. 사용 구간을 찾는 법은 [폰 사용 시간 재구성 (Usage Time)](usage-time.md) 에서 다룹니다.

## 조사 질문

특정 시각의 메시지 발송이나 사진 촬영, 앱 사용을 기기 소유자가 했는지 다른 사람이 했는지를 묻습니다. 가족이 함께 쓰는 기기나 암호를 아는 사람이 여럿인 기기, 소유자가 "그 시각에는 다른 사람이 폰을 쓰고 있었다" 고 주장하는 사건에서 이 질문이 나옵니다.

## 먼저 확인할 것

**iOS 버전과 시간대**를 먼저 적습니다. 잠금·화면 켜짐을 보여 주는 기록이 iOS 15 이하에서는 knowledgeC.db 에 있지만, iOS 16 이후 바이옴에서 대응하는 스트림 이름은 이 핸드북에서 확인하지 못했습니다. 버전별 차이는 [폰 사용 시간 재구성](usage-time.md) 의 버전 표를 따릅니다.

**기기에 연결된 계정**을 확인합니다. 기기에 로그인한 Apple 계정은 [애플 계정](../../02-artifacts/system-account/apple-account.md) 에서, 기기 자체를 가리키는 식별값은 [기기 식별자](../../01-foundations/value-decoding/device-identifiers.md) 에서 봅니다. 계정 명의자와 실제 사용자가 다를 수 있다는 점을 처음부터 전제로 둡니다.

**Face ID·Touch ID 가 사람에 대해 무엇을 남기지 않는지**도 알고 시작합니다. Apple 보안 문서에 따르면 Touch ID 지문 자료는 Apple 로 보내지 않고 기기 백업에도 넣지 않으며, Face ID 등록 자료는 얼굴의 수학적 표현으로 Secure Enclave 에 보관합니다 [2]. 그래서 백업을 아무리 살펴도 등록된 얼굴이나 지문이 누구 것인지는 알 수 없습니다. 같은 문서에는 잠금 해제 시도나 성공을 기록하는 로그에 대한 설명도 없습니다 [2].

**암호가 필요한 상황**도 정리해 둡니다. 기기를 켠 직후와 재시동 뒤에는 Face ID·Touch ID 대신 암호를 넣어야 하고, 기기 암호를 바꾸거나 지문 등록을 지우거나 새로 만들 때도 암호가 필요합니다 [2]. 48시간 동안 쓰지 않았을 때 같은 다른 조건과 대체 외모·지문을 몇 개까지 등록할 수 있는지는 이번에 연 문서에 없어서 확인하지 못했습니다.

## 볼 아티팩트와 순서

아래 3~5번의 키와 칸은 관찰한 백업에서 이름만 확인했고, 값의 뜻은 문서로 확인하지 못했습니다.

| 순서 | 아티팩트 | 알려 주는 것 | 자세히 |
|---|---|---|---|
| 1 | knowledgeC.db 의 `/device/isLocked`, `/display/isBacklit` 스트림 (iOS 15 이하에서 중심) | 그 시각에 기기가 잠금이 풀린 상태였는지, 화면이 켜져 있었는지 [1] | [KnowledgeC](../../02-artifacts/app-usage/knowledgec/index.md) |
| 2 | 스크린 타임 DB (`RMAdminStore-Local.sqlite`) | 도구 화면에 Apple ID, DSID, Given Name, Family Name, Device ID, Platform 항목이 기기·사용자 단위로 나옵니다 [4]. 동기화가 켜져 있으면 가족 공유 계정의 다른 기기 기록이 섞일 수 있습니다 [3] | [화면 사용 시간](../../02-artifacts/app-usage/screen-time.md) |
| 3 | 암호 설정 흔적 — `Manifest.plist` 의 `WasPasscodeSet` | 이름으로 보아 백업 당시 암호가 설정돼 있었는지와 관련된 키로 짐작하지만 확인하지 못했습니다 | [로컬 백업](../../01-foundations/backups/local-backup/index.md), [암호와 Face ID 설정 흔적](../../02-artifacts/system-account/passcode-biometrics.md) |
| 4 | 생체 인증 이름이 붙은 설정 키 — AppDomain-com.apple.mobilesafari `Library/Preferences/com.apple.mobilesafari.plist` 의 `BiometricAuthenticationIsAvailable`(bool)·`BiometricAuthenticationTypeIfAvailable`(int)·`PasscodeIsAvailable`(bool), HomeDomain `Library/Preferences/com.apple.AppleMediaServices.plist` 의 `AMSDeviceBiometricsState`(int)·`AMSDeviceBiometricsIdentities`(list) | 생체 인증을 쓸 수 있는 상태였는지와 관련된 이름입니다. 지문 자료는 백업에 넣지 않고 Face ID 등록 자료는 Secure Enclave 에 보관한다는 [2] 에 비추어 보면 이 키들로 누구의 얼굴·지문인지는 알 수 없습니다 | [암호와 Face ID 설정 흔적](../../02-artifacts/system-account/passcode-biometrics.md) |
| 5 | 첫 잠금 해제·부팅 이름이 붙은 키 — HomeDomain `Library/Preferences/com.apple.NanoRegistry.NRLaunchNotificationController.volatile.plist` 의 `com.apple.mobile.keybagd.first_unlock.enabled`(int), `__BOOTTIME`(float) | 부팅 시각이나 첫 잠금 해제와 관련될 수 있는 이름이지만, 그렇게 써도 되는지는 확인하지 못했습니다 | [설정 값](../../02-artifacts/system-account/preferences.md) |
| 6 | 메시지 DB — HomeDomain `Library/SMS/sms.db` 의 `message` 표 `is_from_me` 칸 | 이름으로 보아 이 기기 쪽에서 보낸 메시지인지와 관련된 칸이지만, 이 조사 묶음에서 뜻을 따로 확인하지는 않았으니 [메시지](../../02-artifacts/communications/messages/index.md) 의 설명과 대조합니다 | [메시지](../../02-artifacts/communications/messages/index.md) |
| 7 | 사진 DB — CameraRollDomain `Media/PhotoData/Photos.sqlite` 의 `ZEXTENDEDATTRIBUTES` 표 `ZCAMERAMAKE`, `ZCAMERAMODEL`, `ZLENSMODEL`, `ZDATECREATED` 칸 | 촬영 기기 정보로 보이는 칸이지만, 이 칸으로 "이 기기에서 찍은 사진" 을 가를 수 있는지는 확인하지 못했습니다 | [이 사진은 언제 어디서 찍었나](photo-origin.md) |

백업에는 `AppDomainPlugin-com.apple.BiometricKit.BioLogDiagnostic`, `AppDomainPlugin-com.apple.PasscodeAndBiometricsSettingsAppIntentsExtension` 도메인도 이름으로 보입니다. 두 도메인 안에 인증 기록이 있는지는 확인하지 못해서, 이름만 보고 "생체 인증 로그" 라고 부르지 않습니다.

## 분석 흐름

1. 쟁점이 된 행위와 시각을 한 줄로 적습니다. "(시각) 에 (대화 상대) 에게 메시지를 보냈다" 처럼 기록으로 확인할 대상을 좁혀야 뒤 단계에서 볼 기록이 정해집니다.
2. 그 행위 자체의 기록을 확인합니다. 메시지라면 `sms.db` 의 해당 행과 `is_from_me` 칸을, 사진이라면 `Photos.sqlite` 의 촬영 정보 칸을 봅니다. 여기까지는 "이 기기와 이 계정에서 일어났다" 까지만 말합니다.
3. 같은 시각의 기기 상태를 봅니다. iOS 15 이하라면 knowledgeC.db 의 `/device/isLocked` 와 `/display/isBacklit` 으로 잠금이 풀려 있었는지와 화면이 켜져 있었는지를 확인합니다 [1]. 잠금이 풀린 채 행위가 일어났다면, 그 기기의 잠금을 풀 수 있었던 사람이 그 순간 기기를 다뤘을 가능성이 높다는 해석까지 할 수 있습니다.
4. 잠금이 언제 어떻게 풀렸는지를 좁힙니다. 재시동 직후에는 생체 인증 대신 암호가 필요해서 [2], 다른 기록으로 재시동 시각을 확인할 수 있고 그 뒤 첫 잠금 해제가 쟁점 시각 가까이에 있다면 "암호를 아는 사람이 풀었다" 는 추론이 가능합니다. 이 추론은 [2] 의 조건에 기댄 해석이라서 보고서에는 해석이라고 밝혀 씁니다.
5. 스크린 타임 DB 를 쓸 수 있다면 기록의 Apple ID·Device ID 항목 [4] 으로 이 기기의 기록인지부터 가립니다. 동기화가 켜져 있으면 다른 기기의 사용이 섞여 보일 수 있어서 [3], 기기 단위로 나눈 뒤에 사람 이야기를 합니다.
6. 기기 밖의 근거와 맞춰 봅니다. 같은 시각의 위치 기록은 [그 시각에 어디 있었나](location.md) 에서, 대화 상대와 흐름은 [누구와 연락을 주고받았나](communication.md) 에서 확인합니다. 진술, 다른 사람의 기기, 영상 같은 수사 자료가 기기 기록과 맞을 때 사람과의 연결이 단단해집니다.
7. 모든 근거를 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 근거마다 "기기 상태", "계정", "사람" 중 어디까지 말하는지 표시해 둡니다.

## 흔한 오판

잠금 해제 기록을 "소유자가 썼다" 로 옮기는 실수가 가장 흔합니다. `/device/isLocked` 는 잠금 상태를 보여 줄 뿐 누가 풀었는지는 보여 주지 않아서, 암호를 아는 사람이 여럿이면 기록만으로 사람을 고를 수 없습니다.

Face ID 가 켜져 있었으니 소유자만 풀 수 있었다고 보는 실수도 있습니다. 백업에는 등록된 얼굴·지문 자료가 없어서 [2] 누가 등록했는지 알 수 없고, 재시동 뒤처럼 암호로 여는 경우도 있습니다 [2]. 대체 외모나 지문을 여러 개 등록할 수 있는지와 그 개수는 이 핸드북에서 확인하지 못했습니다.

스크린 타임에 나오는 이름이나 Apple ID 를 실제 사용자로 적는 실수도 있습니다. 이 항목은 계정 명의를 보여 주는 값이고, 가족 공유로 동기화가 켜져 있으면 다른 기기의 사용 기록까지 함께 보일 수 있습니다 [3][4].

설정 키 이름을 뜻으로 옮겨 적는 일도 조심합니다. `WasPasscodeSet`, `AMSDeviceBiometricsState`, `__BOOTTIME` 은 이름이 뜻을 말해 주는 것처럼 보이지만 값의 뜻을 확인하지 않았으니, 시험 기기로 값이 바뀌는 모습을 확인하거나 공개 도구의 해석과 대조한 뒤에만 씁니다. 방법은 [도구 검증](../../03-techniques/reporting/tool-validation.md) 을 봅니다.

## 보고서 문장 예

> (시각, UTC) 에 이 기기의 `sms.db` 에 `is_from_me` 값이 (값) 인 메시지가 기록되어 있고, 같은 시각 knowledgeC.db 의 `/device/isLocked` 스트림은 기기가 잠금이 풀린 상태였음을 보여 줍니다. 이 기록은 해당 메시지가 잠금이 풀린 이 기기에서 보내졌다는 것까지 보여 주며, 그 순간 기기를 다룬 사람이 누구인지는 보여 주지 않습니다.

> 이 기기의 백업에는 Face ID·Touch ID 에 등록된 얼굴·지문 자료가 들어 있지 않아서 (Apple Platform Security), 등록된 생체 정보가 누구의 것인지는 기기 기록으로 확인할 수 없습니다.

더 넓은 보고서 작성 원칙은 [포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 를 봅니다.

## 함께 볼 페이지

- [폰 사용 시간 재구성 (Usage Time)](usage-time.md) — 사용 구간 찾기
- [암호와 Face ID 설정 흔적 (Passcode·Biometrics)](../../02-artifacts/system-account/passcode-biometrics.md)
- [애플 계정 (Apple Account)](../../02-artifacts/system-account/apple-account.md)
- [KnowledgeC (knowledgeC.db)](../../02-artifacts/app-usage/knowledgec/index.md)
- [화면 사용 시간 (Screen Time)](../../02-artifacts/app-usage/screen-time.md)
- [그 시각에 어디 있었나 (Location)](location.md)
- [데이터 보호 (Data Protection)](../../01-foundations/storage/data-protection/index.md)

## 참고 문헌

1. Sarah Edwards (mac4n6), "Knowledge is Power! Using the macOS/iOS knowledgeC.db Database to Determine Precise User and Application Usage" (2018-08) — https://www.mac4n6.com/blog/2018/8/5/knowledge-is-power-using-the-knowledgecdb-database-on-macos-and-ios-to-determine-precise-user-and-application-usage
2. Apple Platform Security, "Face ID and Touch ID security" — https://support.apple.com/guide/security/face-id-and-touch-id-security-sec067eb0c9e/web
3. Magnet Forensics, "Getting Evidence from iOS Screen Time Artifacts" — https://www.magnetforensics.com/blog/getting-evidence-from-ios-screen-time-artifacts/
4. Forensafe, "Apple Screen Time" — https://forensafe.com/blogs/apple-screen-time.html
