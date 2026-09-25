---
title: "수집 방식 비교"
parent: "모바일 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1170
---

# 수집 방식 비교 (백업·파일 시스템·클라우드)

아이폰 자료를 얻는 길은 로컬 백업, 파일 시스템 추출, 클라우드(iCloud), 진단 자료(sysdiagnose) 넷이 흔하고, 방식마다 담기는 범위와 조건이 달라서 사건마다 어떤 방식을 먼저 쓸지 정해야 합니다.

## 언제 쓰나

압수한 기기에서 무엇을 어디까지 얻을 수 있는지 판단할 때 이 페이지를 봅니다. 수집 도구를 단계로 나누는 NIST 분류(수동·논리·물리)는 상위 허브 [모바일 증거 확보](index.md)에 정리했고, 여기서는 아이폰에서 실제로 쓰는 방식끼리 견줍니다. 이 핸드북은 잠금 해제나 보안 우회를 다루지 않아서, 파일 시스템 추출은 백업과 비교해 무엇이 더 나오는지만 적습니다.

## 한눈에 보기

| 방식 | 담기는 범위 | 조건 | 자세히 |
|---|---|---|---|
| 로컬 백업 | 기기 파일의 일부. 암호화 백업이면 비밀번호·통화 기록 등이 더 들어감 | 기기가 컴퓨터와 데이터 연결을 허락해야 함 | [백업으로 수집](backup-acquisition.md) |
| 파일 시스템 추출 | 백업에 없는 자료까지 | 기종·iOS 버전에 따라 늘 가능하지는 않음 | 이 페이지 |
| 클라우드(iCloud) | 계정에 동기화·백업된 자료 | 항목마다 암호화 방식이 다름 | [클라우드 데이터](../cloud-data.md) |
| sysdiagnose | 통합 로그 스냅숏·크래시 보고서·진단 로그 | 기기에서 직접 만들어야 함 | [sysdiagnose로 수집](sysdiagnose-collection.md) |

## 로컬 백업

로컬 백업은 기기 파일의 일부만 담지만, 수상한 흔적을 찾는 데는 이것만으로 충분한 경우가 많습니다. 모바일 검증 도구 MVT(Mobile Verification Toolkit)의 방법론 문서도 백업을 먼저 쓰라고 권하고, 탈옥으로 전체 파일 시스템을 얻는 방법은 다른 방법을 다 써 본 뒤에만 고려하라고 적습니다. 탈옥은 기기의 기록을 바꾸거나 오작동을 일으킬 수 있기 때문입니다.

백업에서 가장 크게 갈리는 선택은 암호화 여부입니다. 로컬 백업은 기본으로 암호화하지 않고, 사용자가 "로컬 백업 암호화"를 한 번 켜면 그 기기의 이후 백업은 계속 암호화됩니다. 암호화 백업에는 저장된 비밀번호, Wi‑Fi 설정, 웹 사이트 방문 기록, 건강 데이터, 통화 기록이 더 들어가고, MVT 문서도 암호화 백업에 Safari 기록 같은 기록이 더 많이 담긴다고 적습니다. Face ID·Touch ID 자료와 기기 암호는 암호화 백업에도 들어가지 않습니다. 백업 암호를 잊어 재설정하면 이전 암호화 백업은 쓸 수 없어서, 암호화 백업을 만들었다면 그 암호를 수집 기록에 함께 남겨 둡니다.

백업을 만드는 절차와 폴더 구조는 [백업으로 수집](backup-acquisition.md)에서, 백업 형식 자체는 [로컬 백업](../../../01-foundations/backups/local-backup/index.md)에서 다룹니다.

## 파일 시스템 추출

전체 파일 시스템에는 백업에 없는 자료까지 들어 있지만, 기종과 iOS 버전에 따라 이 방식을 늘 쓸 수 있는 것은 아닙니다. 백업이 무엇을 빼는지는 백업 쪽에서만 확인할 수 있는데, 관찰한 백업에는 도메인이 모두 1428개였고 그중 Apple 기본 영역이 1267개였습니다(HomeDomain, MediaDomain, CameraRollDomain, KeychainDomain, WirelessDomain, SysContainerDomain-\*, SysSharedContainerDomain-\*, AppDomain-\*, AppDomainGroup-\*, AppDomainPlugin-\* 등). (확인 범위: iPhone 13 mini, iOS 27.0) 백업에 들어가지 않는 대표 자료의 목록은 이 도메인 목록만으로는 말할 수 없어서, 필요한 아티팩트가 백업에 있는지는 해당 아티팩트 페이지의 위치 절에서 확인합니다.

## 클라우드 (iCloud)

iCloud 자료는 계정의 데이터 보호 설정에 따라 암호화 방식이 달라집니다. 기본값인 표준 데이터 보호에서는 자료를 전송할 때와 저장할 때 모두 암호화하지만 키 일부를 Apple 이 데이터 센터에 둡니다. 고급 데이터 보호(Advanced Data Protection)는 iOS 16.2, iPadOS 16.2, macOS 13.1 이상에서 켤 수 있고, 켜면 종단 간 암호화하는 항목이 늘어납니다.

| 구분 | 종단 간 암호화하는 항목 |
|---|---|
| 표준 데이터 보호(15개) | 암호와 키체인, 건강, 저널, 홈, iCloud 메시지(iCloud 백업을 끈 경우), 결제 정보, Apple Card 거래, 지도·Safari·스크린 타임·Siri 정보, Wi‑Fi 암호, W1·H1 블루투스 키, 미모지 등 |
| 고급 데이터 보호(25개) | 위 항목에 iCloud 백업(기기·메시지 백업 포함), 사진, 메모, iCloud Drive, 미리 알림, Safari 책갈피, 단축어, 음성 메모, 지갑 패스, Freeform 이 더해짐 |

iCloud 메일·연락처·캘린더는 고급 데이터 보호를 켜도 종단 간 암호화하지 않습니다. iCloud 백업은 따로 설정하지 않아도 암호화하고, iCloud 백업을 켜 두면 백업 안에 iCloud 메시지 암호화 키 사본이 들어갑니다. 계정 자료를 요청하는 절차는 [클라우드 데이터](../cloud-data.md)에서, iCloud 백업의 구조는 [아이클라우드 백업](../../../01-foundations/backups/icloud-backup.md)에서 다룹니다.

## 기기에 남는 백업 설정 흔적

어떤 방식으로 백업해 왔는지는 기기 안의 설정 파일에서 단서를 얻을 수 있습니다. 관찰한 백업에서는 아래 두 plist 에 백업 관련 키가 있었습니다. (확인 범위: iPhone 13 mini, iOS 27.0)

```
HomeDomain :: Library/Preferences/com.apple.mobile.ldbackup.plist
  RequiresEncryption (int)
  WillEncrypt (bool)
  CloudBackupEnabled (bool)
  LastCloudBackupDate (int)
  LastCloudBackupTZ (str)
  Version (str)

HomeDomain :: Library/Preferences/com.apple.MobileBackup.plist
  BackupStateInfo: {backupAttemptCount, date, errors, estimatedTimeRemaining,
                    isBackground, isCloud, progress, state}
  AccountEnabledDate (datetime)
```

키 이름으로 보면 로컬 백업 암호화, iCloud 백업 사용 여부, 마지막 iCloud 백업 시각과 관련된 값으로 읽히지만, 각 키의 정확한 뜻과 LastCloudBackupDate 가 어떤 시각 형식인지는 공식 자료로 확인하지 못했습니다. 보고서에는 키 이름과 값을 그대로 옮기고 해석은 다른 기록과 맞춰 본 뒤에 씁니다. 같은 파일의 복원 관련 키는 [백업으로 수집](backup-acquisition.md)에서, plist 를 읽는 법은 [속성 목록 파일](../../../01-foundations/data-formats/plist.md)에서 다룹니다.

## 절차

1. 기기를 [압수와 보관](seizure-handling.md)의 순서대로 격리하고, 데이터 연결이 가능한 상태인지 확인합니다.
2. 로컬 백업을 먼저 만들고, 사용자가 이미 백업 암호화를 켰는지와 새로 켤지를 수집 기록에 적습니다.
3. 통합 로그나 진단 기록이 필요하면 sysdiagnose 를 따로 만듭니다.
4. 계정 쪽 자료가 필요하면 기기 수집과 별도로 클라우드 경로를 밟습니다.
5. 백업에 없는 자료가 조사에 꼭 필요할 때만 파일 시스템 추출을 검토하고, 그 이유를 기록합니다.
6. 얻은 결과물마다 해시를 남깁니다([결과물 형식과 해시](formats-hash.md)).

## 도구

로컬 백업은 macOS 의 Finder, Windows 의 Apple 기기 앱이나 iTunes 로 만들 수 있습니다. 공개 도구 MVT 는 스파이웨어 흔적을 점검하는 도구이고, 위에서 인용한 방법론 문서는 이 도구를 쓸 때의 수집 순서를 설명합니다. 스파이웨어 점검 흐름은 [악성 코드·스파이웨어 흔적](../../analysis/spyware-triage/index.md)에서 다룹니다.

## 함정과 한계

암호화하지 않은 백업에 비밀번호·방문 기록·통화 기록이 없다고 해서 기기에 그런 기록이 없었다고 볼 수는 없고, 수집 방식 때문에 빠진 것일 수 있습니다. 관찰한 백업도 암호화하지 않은 백업이었습니다. (확인 범위: iPhone 13 mini, iOS 27.0) 고급 데이터 보호를 켠 계정이면 iCloud 백업·사진·메모 같은 항목도 종단 간 암호화 대상이 되니, 계정 쪽 자료를 계획할 때 이 설정부터 확인합니다. 파일 시스템을 얻으려고 기기 상태를 바꾸는 방법은 기록 자체를 바꿀 수 있어서, 쓴다면 그 사실과 시각을 보고서에 밝힙니다.

## 결과를 어떻게 해석하나

결과는 늘 "어떤 방식으로 얻은 자료에서 무엇을 찾았다" 로 씁니다. 예를 들어 "암호화하지 않은 로컬 백업에서 통화 기록을 찾지 못했다" 는 기기에 통화 기록이 없었다는 뜻이 아니라, 이 방식으로는 담기지 않는 자료라는 뜻일 수 있습니다. 여러 방식으로 얻은 결과가 서로 다르면 담기는 범위가 다른지부터 확인합니다.

## 참고 문헌

- About encrypted backups on your iPhone, iPad, or iPod touch — Apple Support — https://support.apple.com/en-us/108353
- iOS Forensic Methodology — Mobile Verification Toolkit(MVT) 문서 — https://docs.mvt.re/en/latest/ios/methodology/
- iCloud data security overview — Apple Support — https://support.apple.com/en-us/102651
