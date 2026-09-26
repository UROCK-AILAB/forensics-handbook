---
title: "클라우드 데이터"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1220
---

# 클라우드 데이터 (iCloud·계정 데이터 요청)

아이폰 사용자의 계정 자료 가운데 Apple 서버에 있는 것은 계정 주인이 직접 사본을 받거나 수사기관이 법적 절차로 요청해서 얻고, 받을 수 있는 범위는 계정의 데이터 보호 설정과 서버의 보관 기간에 따라 달라집니다.

## 언제 쓰나

기기를 확보하지 못했거나, 기기에는 없고 서버에만 있는 자료(계정 로그인 기록, iCloud 연결 기록 등)가 조사에 필요할 때 이 길을 씁니다. 사고 대응에서는 피해를 입은 사람이나 조직이 본인 계정의 자료를 직접 받아 볼 수 있어서 [2], [계정 탈취 흔적](../../04-scenarios/incident/account-takeover.md)을 살필 때 기기 분석과 함께 쓸 수 있습니다.

클라우드 쪽 데이터는 법과 규정 때문에 확보가 더 어려워질 수 있어서, 기관의 클라우드 포렌식 지침을 따릅니다 [3]. PC 의 브라우저 캐시처럼 주변 장비에 남은 클라우드 흔적도 함께 봅니다 [3].

이 페이지에서 요청 요건으로 드는 내용은 Apple 이 미국 안의 정부·수사기관을 위해 낸 법적 절차 지침(2025년 10월판)에 근거합니다 [1]. 한국 수사기관이 요청하는 경로와 요건은 이 페이지에서 다루지 않습니다. 계정 자격 증명으로 Apple 서버에서 iCloud 백업을 직접 내려받는 방법도 다루지 않습니다.

## 한눈에 보기

| 경로 | 누가 | 무엇을 받나 | 조건 |
|---|---|---|---|
| 데이터 사본 요청 (privacy.apple.com) | 계정 주인 본인 | 계정 정보와 로그인 기록, iCloud 콘텐츠, 앱 사용 정보, 구입 기록 등 | 본인 확인, 준비된 뒤 14일 안에 내려받기 [2] |
| 법적 절차 요청 | 정부·수사기관 | 고객 정보, 연결 기록, 메일 기록, iCloud 콘텐츠 등 | 자료 종류에 따라 소환장, 법원 명령, 수색 영장, 고객 동의 [1] |
| 기기 안 흔적 확인 | 조사자 | 기기에 등록된 계정 종류, 동기화 상태, iCloud 백업 설정 | 기기나 로컬 백업을 확보한 경우 |

## 절차

1. **기기에서 계정과 동기화 흔적을 먼저 봅니다.** 기기나 로컬 백업이 있으면 어떤 계정이 등록돼 있는지, iCloud 백업과 iCloud Drive 를 썼는지를 먼저 확인합니다(아래 "기기에 남는 계정·클라우드 흔적" 절). 이 결과로 요청할 서비스와 기간을 좁힙니다.
2. **계정을 특정합니다.** Apple 에 iCloud 자료를 요청하려면 Apple ID(계정 이메일)가 필요하고, 모르면 이름과 전화번호, 또는 이름과 주소로 계정을 식별합니다 [1].
3. **데이터 보호 설정을 따집니다.** 계정이 고급 데이터 보호를 켰는지에 따라 Apple 이 내줄 수 있는 콘텐츠가 달라집니다(아래 "데이터 보호 설정에 따라 달라지는 것" 절). 기기의 어느 기록에서 이 설정을 읽을 수 있는지 설명한 공개 문서는 없습니다.
4. **보존 요청을 서두릅니다.** 미국 지침의 보존 요청(18 U.S.C. §2703(f))은 요청한 시점에 있던 데이터를 한 번 떠서 90일 동안 보존하고, 다시 요청하면 90일을 한 번 더 늘릴 수 있습니다 [1]. 같은 계정에 두 번째 보존 요청을 보내면 Apple 은 새 보존이 아니라 연장으로 처리합니다 [1]. 연결 기록처럼 최대 25일만 보관하는 자료가 있어서 [1], 늦게 요청할수록 받을 수 있는 기간이 줄어듭니다.
5. **요건에 맞춰 요청합니다.** 자료 종류마다 필요한 법적 절차가 다르고(아래 표), 콘텐츠는 긴급 상황을 빼면 상당한 이유가 있는 수색 영장이나 고객 동의가 있어야 Apple 이 제공합니다 [1].
6. **동의로 받는 경우 본인이 사본을 요청합니다.** 계정 주인이 privacy.apple.com 에 로그인해 "데이터 사본 요청" 을 고르고 본인 확인을 거치면 Apple 이 데이터를 정리해 줍니다 [2]. 준비가 끝나면 14일 안에 내려받아야 하고, 그 뒤에는 삭제됩니다 [2].
7. **받은 자료를 증거로 보존합니다.** 받은 파일에 해시를 남기고 받은 날짜, 요청 방법, 참고한 지침의 판을 기록합니다. 해시를 남기는 방법은 [모바일 증거 확보](mobile-acquisition/index.md)에서 다룹니다.

### 데이터 보호 설정에 따라 달라지는 것

기본값인 표준 데이터 보호에서 Apple 은 자료를 전송할 때와 저장할 때 암호화하지만 키를 Apple 데이터 센터에 두고, 계정 복구를 도우려고 복호할 수 있습니다 [4]. 복호할 수 있는 데이터의 키는 Apple 의 미국 데이터 센터에 있고, 종단 간 암호화 (End-to-End Encryption) 데이터의 키는 Apple 이 받지도 보관하지도 않습니다 [1]. 고급 데이터 보호 (Advanced Data Protection, ADP)를 켜면 종단 간 암호화하는 항목이 늘어나는데, 어떤 항목이 더해지는지와 켜는 데 필요한 iOS 버전은 [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md)에서 다룹니다.

두 설정에서 Apple 이 내줄 수 있는 자료의 차이는 아래와 같습니다.

| 자료 | 표준 데이터 보호 | ADP |
|---|---|---|
| iCloud 메일, 연락처, 캘린더 콘텐츠 | 수색 영장 또는 고객 동의로 제공 [1] | 영장 등으로 제공 가능 [1]. 이 셋은 ADP 를 켜도 종단 간 암호화하지 않음 [4] |
| 사진, iCloud Drive, iOS 기기 백업, 메모, Safari 책갈피 | 수색 영장 또는 고객 동의로 제공 [1] | Apple 이 복호할 수 없음. 경우에 따라 이 서비스들에 관한 제한된 정보가 남아 있으면 2703(d) 명령이나 영장으로 제공 [1] |
| iMessage, FaceTime 내용 | 종단 간 암호화라 Apple 이 복호하거나 가로챌 수 없음 [1] | 같음 [1] |

ADP 를 켜도 일부 메타데이터는 Apple 이 키를 지닌 표준 암호화로 남습니다 [4]. 어떤 메타데이터가 여기에 드는지는 원문을 요청 시점에 다시 확인하고, 이 페이지의 설명만으로 항목을 단정하지 않습니다.

### 법적 절차로 받을 수 있는 자료

아래 표는 미국 안에서 요청할 때의 iCloud 쪽 자료와 요건, 보관 기간입니다(2025년 10월 기준) [1].

| 자료 | 필요한 절차 | 보관 기간 |
|---|---|---|
| 고객 정보, iCloud 기능 연결 기록(IP 주소 포함) | 소환장 (Subpoena) 이상 | 연결 기록은 최대 25일 |
| 메일 기록(시각, 날짜, 보낸 사람과 받는 사람 주소) | 2703(d) 명령 또는 수색 영장 | 최대 25일 |
| 메일 본문과 기타 iCloud 콘텐츠(사진 보관함, iCloud Drive, 연락처, 캘린더, 책갈피, Safari 방문 기록, 지도 검색 기록, 메시지, iOS 기기 백업) | 수색 영장 또는 고객 동의 | 서버에서 지운 콘텐츠는 보관하지 않음 |
| 나의 찾기 연결 기록 | 소환장 이상 | 최대 25일 |
| 나의 찾기 원격 잠금·지우기 요청 기록 | 2703(d) 명령 또는 수색 영장 | 공개 자료 없음 |

iOS 기기 백업에는 카메라 롤 사진과 비디오, 기기 설정, 앱 데이터, iMessage·Business Chat·SMS·MMS 메시지, 음성 사서함이 들어 있을 수 있습니다 [1]. 이 밖에 AirTag 페어링 기록, iMessage 가능 여부 조회 기록, FaceTime 통화 초대 기록도 최대 25일 보관하고 [1], App Store 같은 Apple 미디어 서비스의 IP 정보는 최근 18개월까지로 제한될 수 있습니다 [1].

나의 찾기는 기기를 잃어버리기 전에 켜 두어야 동작하고, 원격으로나 수사기관 요청으로 켤 수 없습니다 [1]. 기기 위치는 각 기기에 저장되고 Apple 이 특정 기기에서 가져올 수 없어서 [1], 위치 흔적은 기기 쪽 [나의 찾기](../../02-artifacts/location/find-my.md) 페이지를 봅니다. iCloud 비공개 릴레이 (iCloud Private Relay)의 릴레이 IP 로는 계정을 찾을 수 없고, 이 기능은 iOS 15 이상과 iCloud+ 가입이 필요합니다 [1].

### 본인이 받는 데이터 사본

privacy.apple.com 의 데이터 사본 요청으로 받을 수 있는 범주는 계정 정보와 로그인 기록, iCloud 콘텐츠(연락처, 캘린더, 메모, 책갈피, 사진, 비디오, 문서), 앱 사용 정보, App Store·iTunes Store·Apple Books 의 구입과 다운로드 기록, Apple Store 와 지원 거래 기록, 마케팅 수신과 설정입니다 [2]. EU, 영국, 일본 거주자는 App Store 정보와 앱 설치·푸시 알림 활동을 따로 요청할 수 있습니다 [2].

파일은 원래 형식이나 업계 표준 형식으로 옵니다. 사진과 비디오는 원래 형식이고, 연락처와 캘린더는 .vcf, .ics, .html, .eml 같은 형식이며, 앱 사용 정보는 표나 .json, .csv, .pdf 로 옵니다 [2]. 나라와 지역에 따라 이 기능을 쓰지 못할 수 있습니다 [2]. 준비에 걸리는 기간과 로그인 기록에 들어 있는 필드(IP 주소, 기기 등)은 받은 파일에서 확인합니다.

## 기기에 남는 계정·클라우드 흔적

요청할 자료를 고르려면 기기 쪽에서 어떤 계정과 동기화 서비스를 썼는지 먼저 봅니다. 로컬 백업에는 아래 파일이 있습니다. 경로의 `#` 는 숫자가 들어가는 자리입니다.

| 위치(도메인 :: 경로) | 표·키 | 단서가 되는 것 | 자세히 |
|---|---|---|---|
| `HomeDomain :: Library/Accounts/Accounts#.sqlite` | `ZACCOUNT`(`ZACCOUNTTYPE`, `ZUSERNAME`, `ZACCOUNTDESCRIPTION`, `ZACTIVE`, `ZAUTHENTICATED`, `ZDATE`, `ZOWNINGBUNDLEID` 등), `ZACCOUNTTYPE`(`ZACCOUNTTYPEDESCRIPTION`, `ZIDENTIFIER`), `ZACCOUNTPROPERTY`, `ZCREDENTIALITEM`(`ZSERVICENAME`, `ZEXPIRATIONDATE`), `ZAUTHORIZATION`(`ZBUNDLEID`, `ZGRANTEDPERMISSIONS`) | 기기에 등록된 계정의 종류와 사용자 이름 | [애플 계정](../../02-artifacts/system-account/apple-account.md) |
| `HomeDomain :: Library/Accounts/VerifiedBackup/Accounts#.sqlite` | 위와 같은 표 구조 | 같은 구조의 사본. 용도는 공개 자료 없음 | [애플 계정](../../02-artifacts/system-account/apple-account.md) |
| `HomeDomain :: Library/Preferences/com.apple.accountsd.plist` | `AuthenticationPluginCache`(`com.apple.account.AppleAccount`, `com.apple.account.CloudKit`, `com.apple.account.DeviceLocator`, `com.apple.account.Google`, `com.apple.account.IMAP` 등), `LastSystemVersion`, `LastMigrationSystemVersion` | 계정 종류 식별자 목록 | [애플 계정](../../02-artifacts/system-account/apple-account.md) |
| `HomeDomain :: Library/Preferences/com.apple.mobile.ldbackup.plist`, `com.apple.MobileBackup.plist` | `CloudBackupEnabled`, `LastCloudBackupDate`, `BackupStateInfo` 등 | iCloud 백업 사용 여부와 마지막 백업 | [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md) |
| `HomeDomain :: Library/Application Support/CloudDocs/session/db/client.db`, `server.db` | `client_items`, `server_items`, `devices`, `users`, `boot_history` 등 | iCloud Drive 에 동기화한 파일과 기기 | [아이클라우드 드라이브](../../02-artifacts/mail-cloud/icloud-drive.md) |
| `HomeDomain :: Library/Preferences/com.apple.AuthKit.plist` | `_AKBAACertMarkerKey`, `timeCfg` | 인증 설정. 같은 이름의 파일이 여러 앱 도메인에도 있음 | [애플 계정](../../02-artifacts/system-account/apple-account.md) |

동기화를 쓰는 Apple 앱의 데이터베이스에는 CloudKit 관련 열도 남습니다. 메시지의 `HomeDomain :: Library/SMS/sms.db` `chat` 표에는 `cloudkit_record_id` 와 `ck_sync_state` 가, 단축어의 `HomeDomain :: Library/Shortcuts/Shortcuts.sqlite` 에는 `ZCLOUDKITRECORDMETADATA` 가, Freeform 의 `AppDomainGroup-group.com.apple.freeform :: Boards/boards.db` 에는 `last_cloudkit_fetch_version` 이 있습니다. 이 열들은 항목이 클라우드와 동기화됐는지 추정하는 단서가 될 수 있지만, 값의 뜻은 실제 데이터로 확인해야 합니다. 메시지 쪽 해석은 [메시지](../../02-artifacts/communications/messages/index.md)에서 다룹니다.

## 도구

계정 자료를 받는 데는 따로 도구가 필요하지 않고, 본인 사본은 privacy.apple.com 에서 요청합니다 [2]. 받은 .json, .csv 파일과 기기 쪽 SQLite·plist 파일은 범용 뷰어로 열어 볼 수 있으며, 여는 방법은 [SQLite 데이터베이스](../../01-foundations/data-formats/sqlite/index.md)와 [속성 목록 파일](../../01-foundations/data-formats/plist.md)에서 다룹니다. `Accounts#.sqlite` 는 `Z_PK`, `Z_ENT`, `Z_OPT` 열이 있는 Core Data 형식의 표이고, 열 이름이 `Z` 로 시작합니다.

## 함정과 한계

서버 자료는 보관 기간이 짧습니다. 연결 기록, 메일 기록, 나의 찾기 연결 기록은 최대 25일이고 [1], 서버에서 지운 콘텐츠는 Apple 이 보관하지 않습니다 [1]. iCloud 백업을 끈 뒤 서버 사본이 얼마나 남는지는 [아이클라우드 백업](../../01-foundations/backups/icloud-backup.md)에서 다룹니다. 본인 사본도 준비된 뒤 14일 안에 내려받지 않으면 삭제됩니다 [2].

Apple 은 법이 막거나 긴급한 위험이 있는 경우 등을 빼고 요청 사실을 고객에게 알립니다 [1]. 계정 주인이 요청을 알게 될 수 있다는 점을 조사 계획에 넣어 둡니다.

기기 등록 정보는 iOS 8 이후 기기를 iCloud Apple ID 에 연결할 때 Apple 이 받는 정보이고, 정확하지 않거나 실제 주인과 다를 수 있습니다 [1]. 이 정보만으로 기기 소유자를 단정하지 않습니다.

기기 쪽 흔적에도 한계가 있습니다. `com.apple.accountsd.plist` 의 `AuthenticationPluginCache` 목록에는 Google, Yahoo 같은 여러 계정 종류가 올라 있을 수 있는데, 이 목록이 기기가 지원하는 인증 플러그인 목록인지 실제로 로그인한 계정 목록인지 설명한 공개 문서는 없습니다. 실제 등록 계정은 `Accounts#.sqlite` 의 `ZACCOUNT` 표와 맞춰 봅니다. `ZDATE`, `LastCloudBackupDate`, CloudDocs 값들의 시각 기준도 공개 문서에 나와 있지 않으니, 시각 형식을 가려내는 방법은 [시각 값](../../01-foundations/value-decoding/time-values.md)에서 다룹니다.

이 페이지의 요건과 보관 기간은 2025년 10월판 미국 지침 기준입니다 [1]. Apple 은 정책을 바꿀 수 있어서, 실제 요청 때는 그때의 판을 확인하고 보고서에 그 판을 적습니다.

## 결과를 어떻게 해석하나

서버에서 받은 자료는 요청한 시점에 서버에 남아 있던 것입니다. 보존 요청도 요청 시점의 데이터를 한 번 떠 두는 방식이라서 [1], 그 뒤에 생긴 자료는 들어 있지 않습니다. 받은 자료에 어떤 기록이 없다고 해서 그런 일이 없었다고 쓰지 않고, 보관 기간이 지났거나 사용자가 지웠을 가능성을 함께 적습니다.

iMessage 쪽에는 통신 기록이 없고 "iMessage 가능 여부 조회" 기록만 있는데, 이 기록은 실제로 메시지를 주고받았다는 뜻이 아닙니다 [1]. FaceTime 도 통화 초대 기록만 있고 실제로 통화했다는 뜻이 아닙니다 [1]. 보고서에는 "이 시각에 이 계정에서 저 연락처의 iMessage 가능 여부를 조회한 기록이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

연결 기록의 IP 주소는 어느 네트워크에서 iCloud 에 접속했는지를 보여 주지만, 비공개 릴레이를 거친 접속이면 그 IP 로 계정을 거슬러 올라가 찾을 수 없습니다 [1]. 서버 쪽 기록은 기기 쪽 흔적과 시각을 맞춰 [타임라인 작성](../analysis/timeline/index.md)에 넣고, 서로 어긋나는 곳이 있으면 시간대와 시각 기준부터 다시 확인합니다.

## 참고 문헌

1. Apple — Legal Process Guidelines: Government & Law Enforcement within the United States (2025년 10월판) — https://www.apple.com/legal/privacy/law-enforcement-guidelines-us.pdf
2. Apple Support — Get a copy of the data associated with your Apple Account (102208, 2026-09-11) — https://support.apple.com/en-us/102208
3. NIST — SP 800-101 Rev.1, Guidelines on Mobile Device Forensics (2014년 5월) — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
4. Apple Support — iCloud data security overview (102651, 2026-01-05) — https://support.apple.com/en-us/102651
