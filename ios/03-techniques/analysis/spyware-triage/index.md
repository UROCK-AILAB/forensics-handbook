---
title: "악성 코드·스파이웨어 흔적"
parent: "기법 · 분석"
nav_order: 1350
has_children: true
has_toc: false
---

# 악성 코드·스파이웨어 흔적 (Malware·Spyware Triage)

아이폰에서 스파이웨어나 감시 앱이 의심될 때 백업과 sysdiagnose 에 남은 흔적으로 감염·감시 여부를 점검하는 방법을 모은 허브입니다.

## 왜 중요한가

아이폰 스파이웨어는 두 갈래로 나눠 보면 조사 방향이 정해집니다. 하나는 Pegasus·Predator 같은 국가·용병형 스파이웨어이고, 다른 하나는 가까운 사람이 설치하는 감시 앱(스토커웨어, stalkerware)입니다. 앞의 것은 공개 지표와 프로세스 기록을 보는 [스파이웨어 흔적 찾기 (MVT)](spyware-mvt.md) 가, 뒤의 것은 계정·공유·권한을 보는 [감시 앱 흔적 (Stalkerware)](stalkerware.md) 이 맡습니다. 구성 프로파일은 두 갈래 모두에서 보기 때문에 [구성 프로파일과 설정으로 찾기 (Profiles·Settings)](profiles-settings.md) 에 따로 모았습니다.

Apple 은 용병형 스파이웨어가 언론인·활동가·정치인·외교관 같은 극소수 특정 인물을 노리고, 막대한 자금이 들며, 오래 쓰이지 않아 탐지가 어렵다고 설명합니다 [4]. 조사의 계기가 되는 경우가 많은 Apple 위협 알림(threat notification)은 아이폰 잠금 화면과 설정 앱, Apple 계정에 연결된 이메일, account.apple.com 에 로그인한 뒤 뜨는 배너로 옵니다 [4]. 이 알림은 링크 클릭, 파일 열기, 앱이나 프로파일 설치, Apple 계정 암호 입력을 절대 요구하지 않습니다 [4]. 알림을 사칭한 메시지를 가를 때 이 기준을 씁니다. 2026년 8월 13일 게시로 표시된 문서에는 알림 이메일 발신 주소가 threat-notifications@email.apple.com 이라고 적혀 있습니다 [4]. Apple 은 알림을 특정 공격자나 지역과 연결 짓지 않고, 2021년부터 150개가 넘는 나라의 사용자에게 알림을 보냈으며, 받은 사람에게 차단 모드(Lockdown Mode)를 켜고 Access Now 의 Digital Security Helpline 같은 전문 지원에 연락하라고 권합니다 [4].

조사의 출발 자료는 로컬 백업(가능하면 암호화 백업), sysdiagnose 압축 파일, 가능한 경우 전체 파일 시스템 추출이고, MVT 는 셋을 모두 입력으로 받습니다 [1]. 통화 기록이나 Safari 방문 기록처럼 백업에서는 암호화 백업일 때만 나오는 기록이 있고 [1], 모듈별 차이는 MVT 페이지에 정리했습니다.

## 한눈에 보기

"관찰" 은 암호화하지 않은 로컬 백업에서 이름만 확인했다는 뜻입니다.

| 흔적 | 위치 | iOS 버전 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| 구성 프로파일 기록 | 백업 `SysSharedContainerDomain-systemgroup.com.apple.configurationprofiles` | 관찰 | 설치된 프로파일 목록, 제한 설정 | [Profiles·Settings](profiles-settings.md) |
| 앱 권한 | 백업 `HomeDomain :: Library/TCC/TCC.db` | 관찰 | 마이크·카메라·위치 권한의 허용·거부 | [Profiles·Settings](profiles-settings.md) |
| 위치를 요청한 앱 | 백업 `RootDomain :: Library/Caches/locationd/clients.plist` | 관찰 | 위치 서비스를 요청한 앱 | [Profiles·Settings](profiles-settings.md) |
| 프로세스별 셀룰러 사용량 | 백업 `WirelessDomain :: Library/Databases/DataUsage.sqlite` | 관찰. Amnesty 사례는 iOS 14.6 까지 [2] | 프로세스 이름과 사용량, 표 사이 불일치 | [MVT](spyware-mvt.md) |
| shutdown.log | sysdiagnose | iOS 18 이하는 누적, iOS 26 부터 재부팅마다 덮어씀 [3] | 재부팅 때 남아 있던 프로세스의 경로 | [MVT](spyware-mvt.md) |
| IDStatusCache | `com.apple.identityservices.idstatuscache.plist` | 백업에서는 iOS 14.7 이전만 [1] | 앱이 조회한 Apple ID 기록 [2] | [MVT](spyware-mvt.md) |
| 안전 확인 | 설정 → 개인정보 보호 및 보안 → 안전 확인 | iOS 16 이상 [5] | 사람·앱과의 공유, 연결 기기, 앱 권한 | [Stalkerware](stalkerware.md) |

## 읽는 순서

1. [구성 프로파일과 설정으로 찾기 (Profiles·Settings)](profiles-settings.md) — 구성 프로파일, 제한 설정, App Store 밖 서명, 권한과 위치 요청 기록을 백업에서 읽는 순서입니다.
2. [스파이웨어 흔적 찾기 (MVT)](spyware-mvt.md) — MVT 모듈과 공개 지표로 대조하고, 프로세스 기록과 shutdown.log 에서 이상한 실행 흔적을 찾습니다.
3. [감시 앱 흔적 (Stalkerware)](stalkerware.md) — 안전 확인 화면과 공유·위치·자동화 기록으로 가까운 사람의 감시를 점검합니다.

## 함께 볼 페이지

조사 전체 흐름과 보고서 문장은 [스파이웨어 감염 흔적](../../../04-scenarios/incident/spyware.md) 시나리오에 있고, 링크나 메시지로 들어온 경로는 [악성 코드는 어디서 들어왔나](../../../04-scenarios/incident/initial-access.md) 와 [스미싱 흔적](../../../04-scenarios/incident/smishing.md) 에서, 계정 쪽은 [계정 탈취 흔적](../../../04-scenarios/incident/account-takeover.md) 에서 다룹니다. 자료 형식은 [로컬 백업](../../../01-foundations/backups/local-backup/index.md), [sysdiagnose 묶음](../../../01-foundations/backups/sysdiagnose.md), [sysdiagnose 안의 로그](../../../02-artifacts/logs/sysdiagnose-logs.md) 에, 개별 아티팩트는 [구성 프로파일과 MDM](../../../02-artifacts/credentials-security/configuration-profiles.md), [앱별 데이터 사용량](../../../02-artifacts/network/data-usage.md), [충돌·진단 기록](../../../02-artifacts/app-usage/diagnostics.md) 에 있습니다.

## 참고 문헌

1. Records extracted by mvt-ios — Mobile Verification Toolkit — https://docs.mvt.re/en/latest/ios/records/
2. Forensic Methodology Report: How to catch NSO Group's Pegasus — Amnesty International Security Lab (2021-07) — https://securitylab.amnesty.org/latest/2021/07/forensic-methodology-report-how-to-catch-nso-groups-pegasus/
3. Key IOCs for Pegasus and Predator Spyware Cleaned With iOS 26 Update — iVerify — https://iverify.com/blog/key-iocs-for-pegasus-and-predator-spyware-cleaned-with-ios-26-update
4. About Apple threat notifications and protecting against mercenary spyware — Apple Support — https://support.apple.com/en-us/102174
5. Safety Check for an iPhone with iOS 16 or later — Apple Personal Safety User Guide — https://support.apple.com/guide/personal-safety/safety-check-iphone-ios-16-ips2aad835e1/web
