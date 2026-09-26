---
title: "스파이웨어 감염 흔적"
parent: "시나리오 · 침해 사고"
nav_order: 1620
---

# 스파이웨어 감염 흔적 (Spyware)

## 조사 질문

기기가 스파이웨어에 감염됐는지, 감염됐다면 언제부터였는지를 판별합니다. 스파이웨어는 크게 두 종류로 나눠 봅니다. 하나는 특정 인물을 노리는 용병 스파이웨어 (mercenary spyware)이고, 다른 하나는 가까운 사람이 몰래 감시하려고 쓰는 스토커웨어 (stalkerware)입니다. 두 경우 모두 이 페이지는 감염이 의심될 때 무엇을 먼저 보존하고 무엇을 어떤 순서로 볼지를 다루고, 아티팩트별 세부는 링크한 페이지에 맡깁니다. 처음 들어온 길을 찾는 일은 [악성 코드는 어디서 들어왔나](initial-access.md)에서 다룹니다.

## 의심 계기

가장 분명한 계기는 Apple 위협 알림 (threat notification)입니다. Apple 은 이 알림을 잠금 화면과 설정 앱, Apple 계정 이메일, account.apple.com 배너로 보냅니다. 알림은 링크를 누르거나 파일을 열거나 앱·프로파일을 설치하거나 암호를 입력하라고 요구하지 않고, iMessage 나 SMS 로 오지도 않습니다 [6]. 그래서 문자로 온 "위협 알림" 은 오히려 [스미싱 흔적](smishing.md)으로 따로 봅니다. 알림을 받았다면 차단 모드를 켜고 Access Now Digital Security Helpline 같은 전문 지원을 받습니다 [6]. 차단 모드가 무엇을 막는지는 [악성 코드는 어디서 들어왔나](initial-access.md)에 정리했습니다.

사용자가 "업데이트가 이상하게 되지 않는다" 고 말하면 그 진술도 적어 둡니다. Triangulation 은 설정 파일을 바꿔 iOS 업데이트를 막았고 [1], 어떤 파일인지는 위 초기 침투 페이지에 있습니다.

## 먼저 확인할 것 — 보존 순서

스파이웨어 조사에서는 기기를 만지기 전에 보존 순서를 정합니다. 재부팅이나 업데이트 한 번으로 사라지는 기록이 있어서, 수집보다 먼저 전원을 끄거나 업데이트하면 안 됩니다.

1. **재부팅하지 않은 상태에서 sysdiagnose 를 받습니다.** sysdiagnose 안의 `shutdown.log` 는 재부팅할 때 끝나지 않고 남은 프로세스를 PID 와 경로로 적습니다. Pegasus·Reign·Predator 는 `/private/var/db/` 아래 경로에서, Predator 는 `/private/var/tmp/` 에서 실행된 흔적이 남았습니다 [4]. iOS 18 이하에서는 이 파일이 누적되지만 iOS 26 부터는 재부팅마다 덮어써서, iOS 26 이후 기기를 재부팅하면 예전 기록이 사라집니다. 그래서 iOS 26 으로 올리기 전에 sysdiagnose 를 받아 둡니다 [5]. iOS 27 에서도 덮어쓰는지는 실제 기기로 확인해야 합니다. 파일 구성은 [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md)과 [sysdiagnose 안의 로그](../../02-artifacts/logs/sysdiagnose-logs.md)에 있습니다.
2. **암호화 백업을 받습니다.** 통화 기록, Safari 방문 기록, interactionC, Analytics 같은 기록은 암호화 백업에서만 나옵니다 [2]. 암호화하지 않은 백업만 받았다면 보고서에 그 범위를 적습니다.
3. **가능하면 전체 파일 시스템을 받습니다.** MVT 는 로컬 백업, sysdiagnose, 전체 파일 시스템을 모두 입력으로 받습니다 [2]. 수집 방법의 선택은 [모바일 증거 확보](../../03-techniques/acquisition/mobile-acquisition/index.md)를 따릅니다.
4. **재부팅 이력을 적습니다.** Pegasus 는 iOS 기기에서 더는 지속성을 유지하지 않는 것으로 보입니다 [3]. 알림을 받은 뒤 사용자가 재부팅했는지, 몇 번 했는지를 물어 둡니다.

그다음 OS 버전과 시간대를 확인합니다. 공개된 Pegasus 공격은 2014년부터 2021년 7월까지에 걸쳐 있고, 2021년 7월에는 모든 패치를 적용한 iOS 14.6 의 iPhone 12 에서도 무클릭 공격이 성공했습니다 [3]. 최신 버전이라는 사실만으로 감염 가능성을 지우지 않습니다. 시각은 UTC 로 맞추고, 진술 속 현지 시각은 [시간대와 시각 설정](../../02-artifacts/system-account/time-zone.md)을 보고 바꿉니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | sysdiagnose 의 `shutdown.log` | 재부팅 때 남은 프로세스와 실행 경로 | [sysdiagnose 안의 로그](../../02-artifacts/logs/sysdiagnose-logs.md) |
| 2 | `DataUsage.sqlite` | 사용량 행은 남았는데 프로세스 행이 사라진 불일치, 의심 프로세스 이름 | [앱별 데이터 사용량](../../02-artifacts/network/data-usage.md) |
| 3 | 메시지 첨부·충돌 기록·설정 plist | 공개 사례에서 확인된 침투 흔적 | [악성 코드는 어디서 들어왔나](initial-access.md) |
| 4 | 공개 지표(STIX2) 대조 | 알려진 도메인·프로세스 이름과 일치하는 기록 | [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) |
| 5 | 구성 프로파일·권한·공유 설정 | 가까운 사람이 감시하려고 바꾼 설정 | [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md) |

## 분석 흐름

1. **`shutdown.log` 에서 낯선 경로를 찾습니다.** 재부팅 때 남은 프로세스 가운데 `/private/var/db/` 나 `/private/var/tmp/` 아래에서 실행된 것이 있는지 봅니다 [4]. 덮어쓰는 버전이라면 파일에 마지막 재부팅 한 번의 기록만 있다는 점을 함께 적습니다.

2. **데이터 사용량 표 둘을 비교합니다.** `WirelessDomain :: Library/Databases/DataUsage.sqlite` 에는 다음 두 표가 있습니다.

   ```
   ZPROCESS:   ZFIRSTTIMESTAMP, ZTIMESTAMP, ZBUNDLENAME, ZPROCNAME …
   ZLIVEUSAGE: ZTIMESTAMP, ZWWANIN, ZWWANOUT, ZBUNDLENAME, ZPROCNAME …
   ```

   Pegasus 에 감염된 기기에서는 `ZPROCESS` 에서 악성 프로세스 이름이 지워졌는데 `ZLIVEUSAGE` 에는 사용량 행이 남아 있는 불일치가 나타났고, 깨끗한 기기에서는 이런 불일치가 나타나지 않았습니다 [3]. MVT 의 Datausage 모듈은 유효한 번들 ID 가 없는 프로세스를 따로 표시합니다 [2]. 두 표에서 번들 ID 없이 프로세스 이름만 있는 행과, 사용량 행은 있는데 대응하는 프로세스 행이 없는 경우를 골라 시각순으로 놓습니다.

3. **프로세스 이름을 대조합니다.** Pegasus 가 쓴 프로세스 이름에는 `bh`, `roleaccountd`, `stagingd`, `msgacntd` 등이 있고, 정상 프로세스와 비슷하게 지은 이름(`aggregated` 와 비슷한 `aggregatenotd` 등)도 있었습니다 [3]. Triangulation 에서 데이터 사용량 기록에 나온 프로세스는 [악성 코드는 어디서 들어왔나](initial-access.md)에 정리했습니다. 이름만 보고 판단하지 말고, 같은 이름이 정상 기기에도 나오는지 견줘 봅니다.

4. **공개 지표와 대조합니다.** MVT 는 `mvt download-iocs` 로 STIX2 지표를 내려받고, AmnestyTech/investigations 와 mvt-project/mvt-indicators 저장소에 공개 지표가 있습니다 [7]. Triangulation 의 명령 서버 도메인 15개는 [1] 에 공개돼 있습니다. 대조 절차는 [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md)을 따릅니다.

5. **백업에 없는 기록을 적어 둡니다.** 네트워크 사용량 DB `netusage.sqlite` 는 백업에 들어가지 않습니다 [3]. `com.apple.identityservices.idstatuscache.plist` 는 iOS 14.7 이전 백업에만 있습니다 [2]. 이런 기록이 필요하면 전체 파일 시스템 수집을 검토합니다.

6. **가까운 사람의 감시를 따로 봅니다.** 공개된 스토커웨어 지표는 주로 Android 용이라서 [7], iOS 에서는 지표 대조보다 계정·구성 프로파일·앱 권한·위치 공유를 점검하는 쪽이 중심이 됩니다. iOS 16 이상에는 이런 공유와 접근을 점검하는 안전 점검 (Safety Check)이 있습니다 [8]. 권한 기록은 백업의 `HomeDomain :: Library/TCC/TCC.db` 에 있습니다. 계정 쪽 흔적은 [계정 탈취 흔적](account-takeover.md)에서 봅니다.

## 흔한 오판

- **재부팅해서 증상이 사라졌으니 괜찮다고 봅니다.** Pegasus 는 재부팅 뒤 지속하지 않는 것으로 보이고 [3], iOS 26 이후에는 재부팅으로 `shutdown.log` 의 예전 기록도 사라집니다 [5]. 증상이 사라진 것과 흔적이 없는 것은 다릅니다.
- **지표에 걸리지 않았으니 감염이 없다고 씁니다.** Triangulation 은 처음 메시지와 첨부를 스스로 지웠습니다 [1]. 지표 대조 결과는 "공개 지표와 일치하는 기록을 찾지 못했다" 까지만 말합니다.
- **공개 사례에 나온 설정 파일이 있으니 감염이라고 봅니다.** Triangulation 이 바꾼 `com.apple.imservice.ids.FaceTime.plist` 는 정상 기기 백업에도 있습니다. 파일이 있다는 것보다 수정 시각과 다른 흔적의 시각이 겹치는지를 봅니다.
- **스토커웨어 지표에 걸리지 않았으니 감시가 없다고 봅니다.** 공개 지표는 주로 Android 용입니다 [7].

## 보고서 문장 예

> 수집 전 기기의 재부팅 이력은 사용자 진술로 (횟수)회였고, iOS 버전은 (버전)이다. 이 버전에서는 `shutdown.log` 에 마지막 재부팅 기록만 남을 수 있어서, 그 이전 재부팅 때 남은 프로세스는 확인하지 못했다.

> `DataUsage.sqlite` 의 `ZLIVEUSAGE` 표에 (UTC 시각) 사용량 행이 있지만 대응하는 `ZPROCESS` 행은 없었다. 이 불일치는 공개된 Pegasus 조사에서 보고된 형태와 같으며, 이것만으로 특정 악성 코드를 가리키지는 않는다.

> 공개 지표(출처와 내려받은 날짜)와 대조한 결과 일치하는 도메인·프로세스 이름을 찾지 못했다. 이 결과는 공개 지표 범위 안에서만 뜻이 있다.

## 함께 볼 페이지

- [악성 코드·스파이웨어 흔적](../../03-techniques/analysis/spyware-triage/index.md) — 공개 도구와 지표 대조의 세부
- [악성 코드는 어디서 들어왔나](initial-access.md) — 초기 침투 흔적과 차단 모드
- [계정 탈취 흔적](account-takeover.md) · [스미싱 흔적](smishing.md)
- [sysdiagnose 묶음](../../01-foundations/backups/sysdiagnose.md) · [앱별 데이터 사용량](../../02-artifacts/network/data-usage.md) · [구성 프로파일과 MDM](../../02-artifacts/credentials-security/configuration-profiles.md)
- [포렌식 보고서](../../03-techniques/reporting/forensic-report.md)

## 참고 문헌

1. Securelist (Kaspersky), Operation Triangulation: iOS devices targeted with previously unknown malware — https://securelist.com/operation-triangulation/109842/
2. MVT, Records extracted by mvt-ios — https://docs.mvt.re/en/latest/ios/records/
3. Amnesty International, Forensic Methodology Report: How to catch NSO Group's Pegasus (2021-07) — https://securitylab.amnesty.org/latest/2021/07/forensic-methodology-report-how-to-catch-nso-groups-pegasus/
4. Securelist, Detecting iOS malware via Shutdown.log file — https://securelist.com/shutdown-log-lightweight-ios-malware-detection-method/111734/
5. iVerify, Key IOCs for Pegasus and Predator Spyware Cleaned With iOS 26 Update — https://iverify.com/blog/key-iocs-for-pegasus-and-predator-spyware-cleaned-with-ios-26-update
6. Apple Support, About Apple threat notifications and protecting against mercenary spyware — https://support.apple.com/en-us/102174
7. MVT, Indicators of Compromise — https://docs.mvt.re/en/latest/iocs/
8. Apple Personal Safety, Safety Check for an iPhone with iOS 16 or later — https://support.apple.com/guide/personal-safety/safety-check-iphone-ios-16-ips2aad835e1/web
