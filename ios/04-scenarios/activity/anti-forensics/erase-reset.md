---
title: "초기화"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1510
---

# 초기화 (Erase All Content)

기기를 "모든 콘텐츠 및 설정 지우기 (Erase All Content and Settings)" 로 초기화했는지, 했다면 언제였는지를 따지는 시나리오입니다. 초기화한 기기에서는 이전 데이터를 암호학적으로 읽을 수 없어서, 이 시나리오의 목표는 지워진 내용을 되찾는 일보다 초기화 시점을 좁히는 일에 가깝습니다.

## 조사 질문

이 기기를 초기화한 적이 있는지, 있다면 초기화한 시각이 사건의 어느 지점에 들어가는지를 묻습니다. 초기화 뒤 새 기기로 설정했는지, 백업에서 복원했는지도 함께 가려야 하고, 이 구분에 따라 볼 흔적이 달라집니다.

## 초기화가 하는 일

Apple 보안 문서는 이 메뉴를 실행하면 기기가 지울 수 있는 키 (effaceable key) 를 즉시 지운다고 설명합니다 [2]. 암호화된 파일 시스템의 키는 Effaceable Storage 에 있는 이 키로 감싸거나 미디어 키 감싸기 방식으로 보호하고, 파일 메타데이터 키를 감싸는 키는 Secure Enclave 만 알며 사용자가 기기를 지울 때마다 바뀝니다 [2]. 이렇게 키가 사라지면 모든 파일을 암호학적으로 읽을 수 없게 되고, 파일 메타데이터 키는 운영체제를 처음 설치할 때나 초기화를 마쳤을 때 새로 만듭니다 [2]. 원격 지우기는 기기 관리 서비스 (MDM), Microsoft Exchange ActiveSync, iCloud 에서 보낼 수 있습니다 [2].

Apple 문서는 "읽을 수 없다" 까지만 말하고, 이 페이지도 초기화 이전 데이터를 되살릴 수 있다고 주장하지 않습니다. 키 구조는 [데이터 보호 (Data Protection)](../../../01-foundations/storage/data-protection/index.md) 에서 다룹니다.

## 먼저 확인할 것

초기화 흔적을 다룬 포렌식 자료 [1] 은 iPhone X, iPhone SE(iOS 13.7), iPhone 6S(iOS 14.2) 로 시험한 것이고, iOS 15 이후에도 같은지는 이 핸드북에서 확인하지 못했습니다. 그래서 아래 흔적은 검체의 iOS 버전에서 다시 확인해 보고 쓰는 편이 안전합니다.

수집 범위도 먼저 봅니다. 아래 표의 `.obliterated` 파일, containermanagerd 로그, `logd.0.log` 는 [1] 이 전체 파일 시스템 수집에서 본 것이고, 로컬 백업에 들어가는지는 확인하지 못했습니다. 로컬 백업만 있다면 plist 쪽 흔적이 중심이 됩니다.

시간대도 확인합니다. 초기화 뒤 첫 부팅은 기본값 UTC-8(미국 태평양 시각)로 찍힌다고 [1] 은 설명하고, 이 시각을 실제 현지 시각으로 착각하면 초기화 시점이 몇 시간씩 어긋납니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 위치 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| 1 | 설정 도우미 plist | `com.apple.purplebuddy.plist`(백업: HomeDomain `Library/Preferences/`) | `SetupState` 로 새 기기 설정인지 복원인지 가르고, `GuessedCountry` 는 초기화 뒤 처음 나오는 "국가 또는 지역 선택" 화면에 해당합니다 [1] | [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md) |
| 2 | 초기화 표시 파일 | `/private/var/root/.obliterated` | 초기화 뒤 처음 켤 때 기기가 만드는 0바이트 파일입니다 [1] | [초기화와 복원 흔적](../../../02-artifacts/system-account/erase-restore.md) |
| 3 | 연락처·통화 DB 파일 | `/private/var/mobile/Library/AddressBook/AddressBook.sqlitedb`, `/private/var/mobile/Library/CallHistoryDB/CallHistory.storedata` | 두 파일의 생성 시각이 초기화 시점을 가리킵니다 [1] | [연락처](../../../02-artifacts/communications/contacts.md), [통화 기록](../../../02-artifacts/communications/call-history.md) |
| 4 | containermanagerd 로그 | `/private/var/root/Library/Logs/MobileContainerManager/containermanagerd.log.0`, `.log.1` … | 숫자가 클수록 오래된 파일이고, 초기화 뒤 첫 부팅 기록에는 OS 빌드 정보가 빠져 있습니다 [1] | — |
| 5 | logd 로그 | `/private/var/db/diagnostics/logd.0.log` | 시간대 변경과 종료가 남아서, containermanagerd 로그 시각을 UTC 로 바꾸는 데 씁니다 [1] | [통합 로그에서 찾을 것](../../../02-artifacts/logs/unified-log-events.md) |

관찰한 백업에는 `com.apple.purplebuddy.plist` 가 HomeDomain `Library/Preferences/` 에 있었고, 키로 `SetupState`(문자열), `SetupDone`, `SetupFinishedAllSteps`, `SetupVersion`, `GuessedCountry`(list), `SetupLastExit`(날짜), `RestoreChoice`, `RestoredMobileSyncSettings`, `setupMigratorVersion`, `CKStartupTime` 이 보였습니다 (확인 범위: iPhone 13 mini, iOS 27.0). [1] 은 `GuessedCountry` 를 시각 근거로 쓰지만, 관찰한 백업에서 이 키는 list 형식이었고 list 안 어디에 시각이 들어 있는지는 확인하지 못했습니다.

같은 백업에는 이름으로 보아 복원·이전과 관련될 만한 값이 더 있습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 아래 값들은 모두 뜻을 확인하지 못했고, 초기화 판단에 쓰이는지도 모릅니다. 검체에서 다른 근거와 맞아떨어질 때만 보조로 씁니다.

| 파일(백업 HomeDomain) | 키·표 이름 |
|---|---|
| `Library/Preferences/com.apple.MobileBackup.plist` | `RestoreInfo`(`BackupBuildVersion`, `DeviceBuildVersion`, `RestoreDate`, `WasCloudRestore`), `RestoreStateInfo`, `BackupStateInfo`, `RestoreCloudFormatInfo`(`LastForegroundRestoreFailureDate` 등), `AccountEnabledDate` |
| `Library/Preferences/com.apple.mobileSMS.plist` | `IMDCKBackupControllerBackupDeviceStateKey` 안의 `IMDSavedDeviceStateDidRestoreFromBackupKey`, `IMDSavedDeviceStateDidRestoreFromCloudBackupKey`, `IMDSavedDeviceStateDidMigrateFromDifferentDeviceKey`, `IMDSavedDeviceStateDateKey` 등 |
| `Library/Preferences/com.apple.springboard.plist` | `SBLastSystemVersion` |
| `Library/Preferences/com.apple.springboard.datamigrator.plist` | `lastBuildVersion` |
| CameraRollDomain `Media/PhotoData/Photos.sqlite` | `ZMIGRATIONHISTORY` 표(`ZMIGRATIONDATE`, `ZINITIALSYNCDATE`, `ZOSVERSION`, `ZMIGRATIONTYPE`, `ZFORCEREBUILDREASON` 등) |

관찰한 백업에 `Library/AddressBook/AddressBook.sqlitedb` 는 있었지만 `CallHistory.storedata` 는 보이지 않았습니다 (확인 범위: iPhone 13 mini, iOS 27.0). 백업 안 파일의 생성 시각을 무엇으로 읽는지는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md) 을 봅니다.

## 분석 흐름

1. `com.apple.purplebuddy.plist` 의 `SetupState` 를 읽습니다. 값이 `SetupUsingAssistant` 이면 [1] 의 방법이 맞고, `RestoredFromiCloudBackup` 이면 날짜가 복원에 쓴 백업의 예전 기기에서 있었던 초기화를 가리킬 수 있어서 다른 근거를 함께 찾아야 합니다 [1].
2. 전체 파일 시스템 수집이라면 `/private/var/root/.obliterated` 가 있는지 보고, 있으면 그 파일을 만든 시각을 초기화 뒤 첫 부팅 무렵으로 적어 둡니다.
3. `AddressBook.sqlitedb` 와 `CallHistory.storedata` 의 파일 생성 시각을 읽고 2단계의 시각과 맞춰 봅니다.
4. containermanagerd 로그에서 OS 빌드 정보가 빠진 부팅 기록을 찾습니다. 이 로그의 시각은 기기 현지 시각이고, 초기화 뒤 첫 부팅은 UTC-8 로 찍힌다는 점을 기억합니다 [1].
5. `logd.0.log` 에서 시간대 변경 기록을 찾아 4단계의 시각을 UTC 로 바꿉니다 [1].
6. 초기화 메뉴를 누른 뒤 새 기기로 켜질 때까지 몇 분이 걸릴 수 있어서 [1], 결과는 한 시점이 아니라 "이 무렵" 의 범위로 적습니다.
7. 좁힌 범위를 새 기기의 첫 사용 흔적과 함께 [타임라인](../../../03-techniques/analysis/timeline/index.md) 에 올리고, 사건의 다른 기록과 앞뒤 관계를 봅니다.

## 흔한 오판

`SetupLastExit` 를 초기화 시각으로 읽는 실수가 흔합니다. 처음 설정할 때 건너뛴 지갑 같은 항목을 나중에 추가하거나 결제 수단 같은 설정을 바꾸면 이 값도 바뀌어서, 초기화 시각의 근거로 좋지 않습니다 [1].

containermanagerd 로그 시각을 UTC 로 읽는 실수도 있습니다. 이 로그는 현지 시각으로 찍히고, 초기화 직후에는 기기 시간대가 기본값 UTC-8 이라서 `logd.0.log` 로 시간대 변경을 확인하기 전에는 시각을 확정하지 않습니다 [1].

백업에서 복원한 기기에 [1] 의 방법을 그대로 쓰면 결과를 잘못 읽을 수 있습니다. `SetupState` 가 복원 값이면 날짜가 예전 기기의 초기화를 가리킬 수 있다고 [1] 이 밝히고 있어서, 1단계를 건너뛰지 않습니다.

초기화 기록은 초기화가 있었다는 사실만 말합니다. 초기화한 이유나 증거를 없애려는 의도는 이 기록만으로 알 수 없고, 보고서에도 그만큼만 씁니다.

## 보고서 문장 예

> `com.apple.purplebuddy.plist` 의 `SetupState` 값은 `SetupUsingAssistant` 이고, `/private/var/root/.obliterated` 파일이 있습니다. 이 파일과 `AddressBook.sqlitedb` 의 생성 시각은 (시각, UTC) 무렵으로 서로 맞고, 이 무렵 기기를 초기화한 뒤 새 기기로 설정한 기록으로 볼 수 있습니다. 초기화 이전 데이터와 초기화한 이유는 이 기록으로 알 수 없습니다.

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](index.md) — 이 시나리오 묶음의 허브
- [시각 바꾸기 (Time Change)](time-change.md) — 시간대 변경과 시각 변경을 가르는 법
- [초기화와 복원 흔적 (Erase·Restore)](../../../02-artifacts/system-account/erase-restore.md)
- [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md)
- [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md) — 전체 파일 시스템 수집과 백업의 차이

## 참고 문헌

1. Cellebrite, "Upgrade from Null: Detecting iOS Wipe Artifacts" — https://cellebrite.com/en/blog/upgrade-from-null-detecting-ios-wipe-artifacts/
2. Apple Platform Security, "Data Protection in Apple devices" — https://support.apple.com/guide/security/data-protection-sece8608431d/web
