---
title: "자료를 밖으로 보냈나"
parent: "시나리오 · 정보 유출"
nav_order: 1550
has_children: true
has_toc: false
---

# 자료를 밖으로 보냈나 (Data Exfiltration)

아이폰에 있던 자료가 메신저·클라우드·메일·에어드롭·PC 동기화 가운데 어느 경로로 기기 밖에 나갔는지를 흔적으로 따지는 시나리오 묶음입니다.

## 왜 중요한가

정보 유출 사건에서는 "보냈다" 는 결론보다 어느 경로로, 언제, 얼마만큼 나갔는지가 중요합니다. 경로마다 흔적이 남는 곳이 달라서 메시지 DB 만 보고 끝내면 클라우드 업로드나 에어드롭 전송을 놓치고, 에어드롭 기록을 찾을 통합 로그는 sysdiagnose 로 따로 얻어 `log show` 로 봐야 합니다 [2]. 수집 방법도 결과를 바꿉니다. Wi-Fi 와 셀룰러 사용량을 함께 담는 `netusage.sqlite` 는 파일 시스템 추출에서만 얻을 수 있고 [1], 암호화한 로컬 백업이어야 저장 비밀번호·Wi-Fi 설정·웹사이트 방문 기록·통화 기록 같은 항목이 들어갑니다 [5]. 수집 방법의 차이는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

경로 하나를 고르기 전에 앱별 데이터 사용량 DB 인 `DataUsage.sqlite` 로 어느 앱이 셀룰러로 많이 보냈는지를 먼저 보면 범위를 좁힐 수 있습니다 [1]. 관찰한 백업에서도 `WirelessDomain :: Library/Databases/DataUsage.sqlite` 로 보였지만 (확인 범위: iOS 27.0), 이 DB 는 Wi-Fi 사용량을 기록하지 않습니다 [1]. 표 구조와 시각 해석은 [앱별 데이터 사용량 (DataUsage.sqlite)](../../../02-artifacts/network/data-usage.md) 에서 다룹니다.

이 묶음의 페이지는 모두 기록이 말하는 만큼만 씁니다. 송신량이나 업로드 기록은 그 시간대에 그 앱이 무엇을 보냈다는 기록일 뿐이고, 어떤 파일을 누구에게 넘겼는지나 넘긴 의도는 다른 흔적과 함께 판단합니다.

## 한눈에 보기

| 경로 | 주로 볼 곳 | 버전 조건 | 알려 주는 것 |
|---|---|---|---|
| 메신저 | `sms.db` 의 `attachment`·`message` 표, 다른 회사 메신저는 앱 DB 와 `DataUsage.sqlite` | `sms.db` 칸 이름은 관찰로 확인 (확인 범위: iOS 27.0) | 보낸 첨부의 이름·형식·크기, 앱 DB 를 못 읽을 때는 앱별 셀룰러 송신량과 시각 [1] |
| 클라우드 | iCloud Drive 의 `client.db`·`server.db`, `Photos.sqlite` 의 업로드·공유 표, iCloud 백업 설정 plist | `client.db` 해석 자료는 iOS 13.7 에서 시험했고 [3], 표와 칸 이름은 관찰로 확인 (확인 범위: iOS 27.0) | 파일 앱으로 iCloud Drive 에 올린 흔적 [3], 공유 참여자, iCloud 백업을 켰는지와 마지막 백업 시각 값 |
| 메일 | 기본 메일 앱의 `Envelope Index`·`Protected Index` 와 `.emlx` 파일, 계정·메일함 설정 plist | DB 해석 자료는 iOS 12·13 을 다뤘고 [4], 관찰한 백업에는 이 DB 가 보이지 않음 (확인 범위: iOS 27.0) | 보낸편지함에 있는 메일의 겉봉 정보와 받는 사람, 본문 앞부분 [4] |
| 에어드롭 | sysdiagnose 의 통합 로그(AirDrop 범주), `com.apple.sharingd.plist` | 로그 해석 자료는 iOS 15.3.1 에서 시험 [2] | 받는 쪽 기기에서 보낸 사람 전화번호 후보 [2], 보낸 쪽에 남는 기록은 확인하지 못함 |
| PC 동기화 | "이 컴퓨터를 신뢰하겠습니까" 알림과 신뢰 기록, 백업 폴더의 `Info.plist`·`Manifest.plist`, `com.apple.MobileBackup.plist` | iOS 16 이상은 백업할 때도 신뢰 알림이 뜸 [6] | 신뢰한 컴퓨터가 콘텐츠에 접근할 수 있었는지 [6], 백업을 만든 기기와 시각 |

## 읽는 순서

1. [메신저로 (Messenger)](messenger.md) — 기본 메시지 앱에서 보낸 첨부를 가리는 칸과, 다른 회사 메신저의 DB 를 못 읽을 때 송신량으로 대신 보는 법을 다룹니다.
2. [클라우드로 (Cloud)](cloud.md) — iCloud Drive 업로드 기록, iCloud 사진의 업로드·공유 표, iCloud 백업 설정을 차례로 봅니다.
3. [메일로 (Email)](email.md) — 메일 DB 두 개가 나눠 담는 정보와, 백업만 있을 때 볼 수 있는 계정·메일함 설정을 다룹니다.
4. [에어드롭으로 (AirDrop)](airdrop.md) — 에어드롭이 상대를 찾는 원리와, 받는 쪽 로그에서 보낸 사람을 좁히는 흔적을 다룹니다.
5. [PC 동기화로 (PC Sync)](pc-sync.md) — 신뢰한 컴퓨터와 로컬 백업이 기기와 백업 폴더에 남기는 흔적을 다룹니다.

클라우드와 PC 동기화는 둘 다 백업 기록을 보는데, iCloud 백업은 2번, 컴퓨터로 만든 로컬 백업은 5번에서 다룹니다.

## 함께 볼 페이지

- [앱별 데이터 사용량 (DataUsage.sqlite)](../../../02-artifacts/network/data-usage.md) — 경로를 고르기 전에 먼저 볼 송신량
- [메시지 (iMessage·SMS)](../../../02-artifacts/communications/messages/index.md)
- [아이클라우드 드라이브 (iCloud Drive)](../../../02-artifacts/mail-cloud/icloud-drive.md)
- [메일 앱 (Apple Mail)](../../../02-artifacts/mail-cloud/apple-mail.md)
- [에어드롭 (AirDrop)](../../../02-artifacts/network/airdrop.md)
- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md)
- [sysdiagnose 묶음 (sysdiagnose)](../../../01-foundations/backups/sysdiagnose.md)
- [누구와 연락을 주고받았나 (Communication)](../../activity/communication.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [포렌식 보고서 (Forensic Report)](../../../03-techniques/reporting/forensic-report.md) — 기록이 말하는 만큼만 쓰는 법

## 참고 문헌

1. mac4n6.com, "Network and Application Usage using netusage.sqlite & DataUsage.sqlite iOS Databases" — http://www.mac4n6.com/blog/2019/1/6/network-and-application-usage-using-netusagesqlite-amp-datausagesqlite-ios-databases
2. 4n6 Ninja, "(Air)Dropping some Knowledge: Using RLEAPP to Identify the Phone Number Used in an AirDrop Transfer" — https://gforce4n6.blogspot.com/2022/03/airdropping-some-knowledge-using-rleapp.html
3. D20 Forensics, "iOS - The Files App" — https://blog.d204n6.com/2020/09/ios-files-app.html
4. DoubleBlak (Ian Whiffin), "iOS Mail" — https://www.doubleblak.com/blogPost.php?k=iosmail
5. Apple Support, "About encrypted backups on your iPhone, iPad, or iPod touch" (108353) — https://support.apple.com/en-us/108353
6. Apple Support, "About the 'Trust This Computer' alert" (109054) — https://support.apple.com/en-us/109054
