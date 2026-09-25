---
title: "악성 코드는 어디서 들어왔나"
parent: "시나리오 · 침해 사고"
nav_order: 1610
---

# 악성 코드는 어디서 들어왔나 (Initial Access)

## 조사 질문

아이폰에 스파이웨어나 악성 코드가 들어온 흔적이 보일 때, 처음 들어온 길이 메시지 첨부인지, 웹 방문인지, 구성 프로파일이나 App Store 밖에서 설치한 앱인지를 가립니다. 들어온 시점을 좁혀 두면 그 뒤에 무엇이 바뀌었는지를 타임라인에서 차례로 따라갈 수 있습니다. 이 페이지는 공개 사례에 남은 흔적과 그 해석만 다루고, 침투 방법은 다루지 않습니다. 감염 여부 자체를 판단하는 절차는 [스파이웨어 감염 흔적](spyware.md)에 있습니다.

공개 사례에서 확인된 초기 침투 경로 (initial access)는 크게 세 갈래입니다. 첫째는 사용자가 아무것도 누르지 않아도 되는 무클릭 (zero-click) 메시지 첨부이고, Operation Triangulation 과 FORCEDENTRY 가 이 경우입니다. Triangulation 은 iMessage 로 익스플로잇이 든 첨부를 보냈고, 형식이 깨진 메시지라 알림이 뜨지 않은 채 코드 실행으로 이어졌습니다 [1]. 둘째는 Safari 방문과 리디렉션이고, Amnesty 는 Pegasus 조사에서 Safari 방문 기록·파비콘 캐시·SessionResourceLog 로 이 길을 찾았습니다 [4]. 셋째는 구성 프로파일과 App Store 밖에서 서명한 앱(기업용·개발용 서명)인데, 이 길이 실제 사고에서 쓰인 공개 사례는 여기서 인용한 자료에 없습니다. 이 경우 설치 흔적은 [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md) 페이지를 따라 봅니다.

## 먼저 확인할 것

먼저 기기의 iOS 버전과 업데이트 이력을 확인합니다. 공개된 사례마다 영향을 받은 버전이 다르고, 막는 장치가 들어간 버전도 달라서 버전을 알아야 어떤 사례와 견줄지 정할 수 있습니다.

| 항목 | iOS 버전 | 조사에서 뜻하는 것 |
|---|---|---|
| BlastDoor | iOS 14 이상 | Messages·IDS 로 들어오는 믿을 수 없는 데이터를 격리된 곳에서 파싱·변환·검증합니다. 특히 무클릭 공격을 막으려고 넣은 장치이고, Messages 는 아는 발신자와 모르는 발신자의 트래픽을 다르게 다룹니다 [2] |
| FORCEDENTRY (CVE-2021-30860) | iOS 14.8 이전 버전이 영향을 받음 | Citizen Lab 이 2021-09-13 에 공개했습니다. macOS Big Sur 11.6 이전과 watchOS 7.6.2 이전도 영향을 받았습니다 [3] |
| Operation Triangulation | 확인된 가장 최신 대상은 iOS 15.7 | Securelist 는 다른 버전도 영향을 받았을 수 있다고 적었고, 관련 취약점 하나(CVE-2022-46690 으로 추정)는 iOS 16.2 에서 고쳐졌다고 적었습니다 [1] |
| 차단 모드 (Lockdown Mode) | iOS 16 이상 | 켜져 있던 기간에는 들어올 수 있는 길이 좁아집니다(아래 설명) [7] |
| 재부팅 때 남는 기록(shutdown.log) | 버전에 따라 누적 여부가 다름 | 수집 전에 재부팅하면 안 되는 까닭은 [스파이웨어 감염 흔적](spyware.md)에 정리했습니다 |

BlastDoor 가 들어간 iOS 14 이후 버전도 FORCEDENTRY(14.8 이전)와 Triangulation(15.7 까지 확인) 사례의 대상 범위에 들어갑니다. 버전이 높다는 사실만으로 무클릭 경로를 지우지 않습니다.

차단 모드가 켜져 있으면 메시지 첨부는 일부 이미지·영상·오디오 말고 대부분 막히고, 복잡한 웹 기술 일부도 막힙니다. 최근 30일 안에 전화한 적 없는 상대의 FaceTime 수신도 막히고, 구성 프로파일 설치·MDM 등록·감독도 할 수 없습니다. 액세서리나 다른 컴퓨터를 연결하려면 잠금을 해제해야 하고, 보안이 안 된 Wi-Fi 에는 붙지 않으며 2G/3G 는 꺼집니다. 켜져 있는 동안에는 Safari 에 배너가 뜹니다 [7]. 백업에는 `HomeDomain :: Library/Preferences/com.apple.lockdownmoded.plist` 가 있고 키 `LDMExemptCNHistoryToken` 이 보였습니다. 다만 차단 모드가 켜졌는지를 담는 키는 확인하지 못했습니다. MVT 의 GlobalPreferences 모듈은 `.GlobalPreferences.plist` 에서 차단 모드 상태를 뽑는다고 적었지만 [5], 관찰한 백업의 `.GlobalPreferences.plist` 키 가운데 LDM 이 들어간 이름은 없었습니다. 켜짐 여부는 사용자 진술과 Safari 배너 같은 다른 근거로 맞춰 봅니다.

수집 범위도 먼저 적어 둡니다. 로컬 백업(가능하면 암호화), sysdiagnose, 가능하면 전체 파일 시스템을 받고, MVT 는 이 셋을 모두 입력으로 받습니다 [5]. 무엇을 어떤 순서로 보존하는지는 [스파이웨어 감염 흔적](spyware.md)과 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)를 따릅니다. 시각은 모두 UTC 로 맞추고, 사용자가 진술한 현지 시각은 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md)을 보고 바꿉니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 메시지 첨부 폴더(`Library/SMS/Attachments`)와 `sms.db` 의 `attachment` 표 | 수정 시각만 남은 빈 디렉터리, 확장자와 실제 형식이 다른 첨부 | [메시지](../../02-artifacts/communications/messages/index.md) |
| 2 | 앱별 데이터 사용량 `DataUsage.sqlite` | 첨부를 받는 프로세스 뒤에 평소 나오지 않는 프로세스가 나타난 시각 | [앱별 데이터 사용량](../../02-artifacts/network/data-usage.md) |
| 3 | 충돌 기록 | 첨부를 변환하는 프로세스가 되풀이해 충돌한 흔적 | [충돌·진단 기록](../../02-artifacts/app-usage/diagnostics.md) |
| 4 | 설정 plist | 공개 사례에서 바뀐 설정 파일, 업데이트를 막은 흔적 | [설정 값](../../02-artifacts/system-account/preferences.md) |
| 5 | Safari 방문 기록·캐시 | 웹 방문과 리디렉션으로 들어온 흔적 | [사파리](../../02-artifacts/browsers/safari/index.md) |
| 6 | 구성 프로파일·프로비저닝 프로파일 | 프로파일 설치와 App Store 밖 앱 서명 흔적 | [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md) |

## 분석 흐름

1. **타임라인을 먼저 만듭니다.** Triangulation 을 찾은 분석가들은 mvt-ios 로 백업에서 시간순 이벤트 파일(`timeline.csv`)을 만들어 분석했습니다 [1]. 공개 도구가 만든 타임라인은 출발점으로 쓰고, 아래 단계에서 원본 표를 직접 열어 확인합니다. 만드는 법은 [타임라인 작성](../../03-techniques/analysis/timeline/index.md)에 있습니다.

2. **메시지 첨부 폴더를 봅니다.** Triangulation 에서는 `Library/SMS/Attachments` 아래 디렉터리들이 수정 시각만 있고 파일은 없었고, 악성 코드는 실행 뒤 처음 받은 메시지와 첨부 속 익스플로잇을 지웠습니다 [1]. 그래서 메시지와 첨부가 없다는 사실만으로 무클릭 경로를 지울 수 없고, 빈 디렉터리의 수정 시각이 들어온 시점의 후보가 됩니다. 로컬 백업에서 첨부는 `HomeDomain` 이 아니라 `MediaDomain` 에 들어가고, 파일 ID 는 `SHA1("MediaDomain-Library/SMS/Attachments/...")` 로 정해집니다 [6]. 관찰한 백업에서는 `MediaDomain` 항목이 303개 있었지만 첨부 경로 목록은 따로 확인하지 않았습니다.

3. **확장자와 실제 형식을 견줍니다.** FORCEDENTRY 는 2021년 3월에 받은 iTunes 백업을 다시 분석해 찾았습니다. 첨부 폴더에 확장자가 `.gif` 인 파일이 있었는데, 27개는 같은 파일로 실제로는 748바이트짜리 Adobe PSD 였고 이름은 무작위 열 글자였습니다. 나머지 4개는 실제로는 JBIG2 스트림을 담은 PDF 였습니다 [3]. `sms.db` 의 `attachment` 표에는 `filename`, `uti`, `mime_type`, `transfer_name`, `total_bytes`, `created_date`, `is_outgoing` 칸이 있어서, 이 칸이 말하는 형식과 실제 파일 머리의 시그니처를 나란히 놓으면 이런 불일치를 찾을 수 있습니다.

4. **데이터 사용량 타임라인을 봅니다.** Triangulation 에서는 데이터 사용량 기록에 `BackupAgent` 프로세스가 나왔는데, 평소 쓰지 않는(deprecated) 바이너리라서 정상 사용 중에는 타임라인에 나오면 안 된다고 Securelist 가 적었습니다. 그 바로 앞에 첨부를 받는 `IMTransferAgent` 가 나오는 경우가 많았습니다 [1]. 관찰한 백업에서는 `WirelessDomain :: Library/Databases/DataUsage.sqlite` 에 `ZPROCESS` 와 `ZLIVEUSAGE` 표가 있었습니다. 이 표의 `ZTIMESTAMP` 가 어떤 기준 시각인지는 확인하지 못해서, 다른 기록의 시각과 맞춰 보고 나서 기준을 정합니다. 칸 구성과 프로세스 이름 대조는 [스파이웨어 감염 흔적](spyware.md)에서 다룹니다.

5. **충돌 기록을 봅니다.** FORCEDENTRY 에서는 PSD 파일마다 `IMTranscoderAgent` 충돌이 기기에 남았습니다 [3]. 관찰한 백업에는 `HomeDomain :: Library/Preferences/com.apple.ReportCrashService.plist`(키 `memoryExceptionProcesses.bootUUID`, `patternMatchServiceCrashes.bootUUID`)와 `com.apple.ReportCrash.plist`(키 `TrialCache`)가 있었지만, 충돌 로그 파일(`.ips`) 자체가 백업에 들어가는지는 확인하지 못했습니다. 충돌 로그는 sysdiagnose 에서도 찾습니다([sysdiagnose 안의 로그](../../02-artifacts/logs/sysdiagnose-logs.md)).

6. **바뀐 설정 파일을 봅니다.** Triangulation 은 `com.apple.ImageIO.plist`, `com.apple.locationd.StatusBarIconManager.plist`, `com.apple.imservice.ids.FaceTime.plist` 를 바꿨고, `com.apple.softwareupdateservicesd.plist` 를 바꿔 iOS 업데이트를 막았습니다 [1]. 관찰한 백업과 견주면 다음과 같습니다.

   | 파일(`HomeDomain :: Library/Preferences/`) | 관찰한 백업 | 보인 키 이름 |
   |---|---|---|
   | `com.apple.locationd.StatusBarIconManager.plist` | 있음 | `ShowSystemServices` |
   | `com.apple.imservice.ids.FaceTime.plist` | 있음 | `ActiveAccounts`, `Status`, `OnlineAccounts` |
   | `com.apple.softwareupdateservicesd.plist` | 있음 | 이름을 가린 키 1개 |
   | `com.apple.ImageIO.plist` | plist 목록에 없음 | — |

   세 파일은 정상 기기에도 있어서 파일이 있다는 것만으로는 수상하지 않고, 수정 시각이 들어온 시점 후보와 겹치는지를 봅니다. 업데이트 쪽으로는 `com.apple.softwareupdateservices.security.plist`(`SUSUIFailedAttemptCountsWhileUnlocked`), `com.apple.softwareupdateservices.ui.ios.plist`(`SUSUISoftwareUpdateOSVersion`, `SUSUISoftwareUpdateState`, `SUSUIState`, `SUSUIOSVersion`), `com.apple.softwareupdatesettings.plist`(`SUCachedScanResultsFingerprint`, `SUCachedScanResultsTTL`)도 같은 폴더에 있었습니다. 업데이트를 막은 흔적으로 이 가운데 어떤 값을 봐야 하는지는 확인하지 못해서, 키 이름만 보고 단정하지 않습니다.

7. **웹 경로를 봅니다.** Amnesty 는 Safari 방문 기록과 파비콘 캐시, SessionResourceLog 를 썼고, 방문 기록에는 리디렉션 경로 전체가 남지 않는다고 적었습니다 [4]. 방문 기록 파일이 암호화 백업에만 들어가는 점과 암호화하지 않은 백업에서 볼 수 있는 도메인 기록은 [스미싱 흔적](smishing.md)에 정리했습니다.

8. **프로파일과 앱 서명을 봅니다.** 관찰한 백업에는 구성 프로파일 기록 `MCProfileEvents.plist` 와 프로비저닝 프로파일 DB `MobileDeviceDomain :: ProvisioningProfiles/mis.db` 가 있었습니다. 읽는 법은 [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md)과 [설치된 앱](../../02-artifacts/app-usage/installed-apps.md)을 따릅니다.

9. **들어온 시점 후보를 적습니다.** 빈 첨부 디렉터리의 수정 시각, 데이터 사용량의 첫 이상 프로세스 시각, 첫 충돌 시각, 설정 파일 수정 시각을 한 줄에 놓고 가장 이른 시각을 후보로 삼습니다. 공개 지표(명령 서버 도메인 등)와의 대조는 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md)을 따릅니다. Triangulation 의 명령 서버 도메인 15개는 원문 [1]에 있습니다.

## 흔한 오판

- **메시지와 첨부가 없으니 무클릭 경로가 아니라고 봅니다.** Triangulation 은 처음 메시지와 첨부를 스스로 지웠고, 남은 것은 빈 디렉터리의 수정 시각이었습니다 [1].
- **확장자로 형식을 판단합니다.** FORCEDENTRY 의 `.gif` 는 실제로 PSD 와 PDF 였습니다 [3]. 파일 머리를 직접 확인합니다.
- **공개 사례의 설정 파일이 있으니 감염됐다고 봅니다.** `FaceTime.plist` 같은 파일은 정상 기기에도 있습니다. 파일이 있다는 사실보다 언제 바뀌었는지를 봅니다.
- **iOS 14 이후라 BlastDoor 가 있으니 무클릭은 아니라고 봅니다.** 공개된 두 사례 모두 BlastDoor 가 들어간 버전을 대상 범위에 포함합니다.
- **암호화하지 않은 백업에 방문 기록이 없으니 웹 경로가 아니라고 봅니다.** 방문 기록 파일은 암호화 백업에만 들어갑니다. 수집 범위가 무엇을 빠뜨리는지부터 적습니다.

## 보고서 문장 예

> 기기의 `sms.db` `attachment` 표에서 `transfer_name` 확장자는 `.gif` 인데 파일 머리는 PDF 형식인 첨부가 (건수)건 있었다. 첫 첨부의 `created_date` 는 (UTC 시각)이다.

> `DataUsage.sqlite` 의 `ZPROCESS` 표에 `BackupAgent` 프로세스 행이 있고, 그 `ZFIRSTTIMESTAMP` 는 `IMTransferAgent` 행의 시각 바로 뒤다. 이 기록은 두 프로세스가 그 시각에 네트워크 사용 기록을 남겼다는 것까지 보여 주며, 침투 방법을 보여 주지는 않는다.

> 메시지 첨부 폴더에 파일 없이 수정 시각만 남은 디렉터리가 (개수)개 있었다. 첨부가 지워졌을 가능성을 배제하지 못해서, 이 시각을 초기 침투 시점 후보로 적는다.

## 함께 볼 페이지

- [스파이웨어 감염 흔적](spyware.md) — 감염 여부 판단과 보존 순서
- [스미싱 흔적](smishing.md) — 문자 속 링크와 웹 방문 기록
- [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) — 공개 도구와 지표 대조
- [메시지](../../02-artifacts/communications/messages/index.md) · [앱별 데이터 사용량](../../02-artifacts/network/data-usage.md) · [충돌·진단 기록](../../02-artifacts/app-usage/diagnostics.md)
- [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md) · [로컬 백업](../../01-foundations/backups/local-backup/index.md)

## 참고 문헌

1. Securelist (Kaspersky), Operation Triangulation: iOS devices targeted with previously unknown malware — https://securelist.com/operation-triangulation/109842/
2. Apple Platform Security, BlastDoor for Messages and IDS — https://support.apple.com/guide/security/blastdoor-for-messages-and-ids-secd3c881cee/web
3. Citizen Lab, FORCEDENTRY: NSO Group iMessage Zero-Click Exploit Captured in the Wild (2021-09-13) — https://citizenlab.ca/2021/09/forcedentry-nso-group-imessage-zero-click-exploit-captured-in-the-wild/
4. Amnesty International, Forensic Methodology Report: How to catch NSO Group's Pegasus (2021-07) — https://securitylab.amnesty.org/latest/2021/07/forensic-methodology-report-how-to-catch-nso-groups-pegasus/
5. MVT, Records extracted by mvt-ios — https://docs.mvt.re/en/latest/ios/records/
6. ChatExport/ChatExportKnowledge, attachments.md — https://raw.githubusercontent.com/ChatExport/ChatExportKnowledge/main/attachments.md
7. Apple Support, About Lockdown Mode (105120, 2026-09-14) — https://support.apple.com/en-us/105120
