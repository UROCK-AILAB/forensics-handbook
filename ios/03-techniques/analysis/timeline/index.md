---
title: "타임라인 작성"
parent: "기법 · 분석"
nav_order: 1270
has_children: true
has_toc: false
---

# 타임라인 작성 (Timeline)

아이폰의 여러 기록에서 시각을 뽑아 같은 기준으로 맞추고, 한 줄에 이어 붙이고, 기기 시계를 믿어도 되는지 확인해서 사건의 순서를 정리하는 방법을 모은 곳입니다.

## 왜 중요한가

조사 질문 대부분은 "언제" 를 묻고, 아이폰에서는 그 답이 메시지 DB, 사진 DB, 네트워크 사용량 DB, plist, 통합 로그에 흩어져 있습니다. 이 기록들은 시각을 적는 기준점과 단위가 서로 다르고, 메시지 DB 처럼 한 열 안에서도 초와 나노초가 섞이는 곳이 있어서, 값을 그대로 나란히 놓으면 순서가 뒤집히거나 날짜가 하루씩 밀립니다. 기기 시계를 손으로 바꾼 경우에는 정확히 변환한 값조차 실제와 다를 수 있으니, 맞추고 엮는 작업과 시계를 의심하는 작업을 함께 해야 타임라인을 보고서에 쓸 수 있습니다.

## 한눈에 보기

| 기록 | 위치 | iOS 버전 | 타임라인에서 알려 주는 것 |
|---|---|---|---|
| 메시지 DB | `HomeDomain :: Library/SMS/sms.db` | iOS 11 부터 초·나노초 단위가 섞임, 열 이름은 iOS 27.0 에서 확인 | 메시지를 보내고 받고 읽은 시각, 삭제 시각 열 |
| 사진 DB | `CameraRollDomain :: Media/PhotoData/Photos.sqlite` | 열 이름은 iOS 27.0 에서 확인 | 사진 시각과 함께 남은 시간대 열 |
| 네트워크 사용량 DB | `WirelessDomain :: Library/Databases/DataUsage.sqlite` | 열 이름은 iOS 27.0 에서 확인 | 번들 이름과 시각이 한 행에 있는 사용 기록 |
| 백업 정보 | `Manifest.plist` 의 `Date`, `Info.plist` 의 `Last Backup Date` | 키 이름은 iOS 27.0 에서 확인 | 수집 시각, 곧 타임라인의 끝 |
| 통합 로그 | 로컬 백업에는 없음(iOS 27.0 관찰) | 출처가 시험한 버전을 밝히지 않음 | 날짜·시각을 손으로 바꾼 기록 |

iOS 27.0 행은 iOS 27.0 기기의 암호화하지 않은 로컬 백업에서 이름만 확인한 것입니다.

## 읽는 순서

1. [시각 정규화 (Time Normalization)](time-normalization.md) — 기준점과 단위를 구분해 모든 시각을 UTC 로 바꾸고, 시간대를 따로 적는 순서를 다룹니다.
2. [여러 기록 엮기 (Correlation)](correlation.md) — 수집 시각과 수집 범위를 먼저 적고, 앱 이름과 시간 창으로 여러 기록을 한 흐름에 이어 붙이는 방법입니다.
3. [시각 조작 흔적 (Time Manipulation)](time-manipulation.md) — 시각을 손으로 바꾼 통합 로그 기록과 기록 사이의 앞뒤 모순을 찾아 타임라인을 어디까지 믿을지 정합니다.

## 함께 볼 페이지

- [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md) — 시각 값 형식 자체의 설명
- [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md) — 기기의 시간대 설정 기록
- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md) — 백업에 무엇이 들어가는지
- [통합 로그 형식 (Unified Log·tracev3)](../../../01-foundations/data-formats/unified-log.md) — 통합 로그를 읽는 법
- [폰 사용 시간 재구성 (Usage Time)](../../../04-scenarios/activity/usage-time.md) — 타임라인을 쓰는 조사 시나리오
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md) — 시각 조작을 포함한 증거 인멸 정황
- [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md) — 타임라인을 보고서에 옮기는 법
