---
title: "시각 바꾸기"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 1540
---

# 시각 바꾸기 (Time Change)

기기 시각을 손으로 바꿔서 기록 시각이 실제와 어긋났는지를 따지는 시나리오입니다. 이 주제는 공개된 분석 자료가 적어서, 알려진 사실과 일반 원리, 검체에서 확인해야 할 서술을 나눠 적습니다.

## 조사 질문

사건 기간의 기록 시각이 실제 시각과 맞는지, 누군가 기기 시각을 바꿔 기록 시각을 앞당기거나 늦춘 흔적이 있는지를 묻습니다. 기기 시각이 바뀌었다면 그 시기에 생긴 기록의 시각을 모두 다시 따져야 해서, 다른 시나리오의 결론에도 영향을 줍니다.

## 먼저 확인할 것

시각 변경과 시간대 변경을 먼저 가릅니다. 시간대를 바꾸면 화면에 보이는 현지 시각이 달라지지만, 기기 시각 자체를 바꾸는 일과는 다르고 흔적도 따로 봐야 합니다. 시간대 설정이 어디에 남는지는 [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md) 에서 다룹니다.

각 아티팩트가 시각을 UTC 로 저장하는지 현지 시각으로 저장하는지도 확인합니다. 값의 형식과 기준 시점은 [시각 값](../../../01-foundations/value-decoding/time-values.md) 에서 다루고, 이 구분 없이 두 기록을 비교하면 시간대 차이를 시각 조작으로 잘못 읽게 됩니다.

기기를 초기화한 적이 있다면 그 무렵의 기록을 따로 봅니다. 초기화 뒤 첫 부팅은 기본값 UTC-8(미국 태평양 시각)로 찍히고, `/private/var/db/diagnostics/logd.0.log` 에 시간대 변경이 남습니다(iOS 13.7·14.2 기준)[1]. 자세한 내용은 [초기화 (Erase All Content)](erase-reset.md) 를 봅니다.

## 알려진 것과 검체에서 확인할 것

수동 시각 변경이 PowerLog 에 남는다는 서술이 있고, `PLSTORAGEOPERATOR_EVENTFORWARD_TIMEOFFSET` 이라는 표 이름이 함께 알려져 있습니다. 표의 칸 이름·단위·기록 빈도와 PowerLog 파일 경로는 공개된 분석 자료가 없습니다. 검체에서 이 표를 쓰려면 먼저 시험 기기로 시각을 바꿔 행이 어떻게 생기는지 확인합니다. PowerLog 자체는 [전원 로그 (PowerLog)](../../../02-artifacts/app-usage/powerlog.md) 에서 다룹니다.

설정 메뉴의 자동 시각 설정이 정확히 어떻게 동작하는지, 시각을 맡는 데몬과 그 설정 파일이 어디에 무엇을 남기는지도 공개된 분석 자료가 없습니다. `com.apple.timed.plist`, `com.apple.preferences.datetime.plist`, PowerLog 파일은 로컬 백업에 들어 있지 않을 수 있습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 위치 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| 1 | logd 로그 | `/private/var/db/diagnostics/logd.0.log` | 시간대 변경이 남습니다 [1] | [통합 로그에서 찾을 것](../../../02-artifacts/logs/unified-log-events.md) |
| 2 | 사진 DB 의 시간대 칸 | CameraRollDomain `Media/PhotoData/Photos.sqlite` | `ZADDITIONALASSETATTRIBUTES` 의 `ZTIMEZONEOFFSET`, `ZINFERREDTIMEZONEOFFSET`, `ZDATECREATEDSOURCE`, `ZEXTENDEDATTRIBUTES` 의 `ZTIMEZONEOFFSET`, `ZTIMEZONENAME`, `ZDATECREATED`, `ZMOMENT` 의 `ZTIMEZONEOFFSET` 이 있습니다 | [카메라 사진과 메타데이터](../../../02-artifacts/media/dcim-exif.md) |
| 3 | 미리 알림의 시간대 칸 | AppDomainGroup-group.com.apple.reminders `Container_v#/Stores/Data-*.sqlite` | `ZREMCDREMINDER` 의 `ZTIMEZONE`, `ZDISPLAYDATETIMEZONE`, `ZDISPLAYDATEUPDATEDFORSECONDSFROMGMT` 가 있습니다 | [미리 알림과 캘린더](../../../02-artifacts/mail-cloud/reminders-calendar.md) |
| 4 | 캘린더 부가 DB | HomeDomain `Library/Calendar/Extras.db` | `ZALARM` 표에 `ZENTITYTIMEZONE` 등이 있습니다 | [미리 알림과 캘린더](../../../02-artifacts/mail-cloud/reminders-calendar.md) |
| 5 | 백업 설정 | HomeDomain `Library/Preferences/com.apple.mobile.ldbackup.plist` | `LastCloudBackupDate` 와 `LastCloudBackupTZ` 가 함께 있습니다 | [아이클라우드 백업](../../../01-foundations/backups/icloud-backup.md) |
| 6 | PowerLog | 검체에서 확인 | 수동 시각 변경이 남는다는 서술이 있습니다 | [전원 로그](../../../02-artifacts/app-usage/powerlog.md) |

2~5번은 기록마다 시각과 함께 시간대나 오프셋을 적어 두는 칸입니다. 이 칸들을 기기 시각 조작 판단에 쓰는 방법은 공개된 자료가 없어서, 시간대 변경을 시각 조작과 가르는 데 참고하는 용도로만 씁니다.

## 분석 흐름

아래 2~4단계는 iOS 자료로 따로 검증되지 않은 일반 원리입니다. 결과는 "어긋남이 있다" 까지만 적고, 어긋남의 원인을 단정하지 않습니다.

1. 시간대부터 정리합니다. `logd.0.log` 의 시간대 변경 기록과 2~5번의 시간대 칸을 보고, 조사 기간에 시간대가 바뀐 시점을 적어 둡니다.
2. 한 DB 안에서 행 번호와 시각의 순서를 비교합니다. SQLite 의 `ROWID` 나 Core Data 의 `Z_PK` 는 대개 행을 넣은 순서대로 늘어나서, 번호는 늘어나는데 시각이 거꾸로 가는 구간이 있으면 표시해 둡니다. 행을 지운 뒤 번호를 다시 쓰는 경우도 있어서, 번호 순서를 절대 기준으로 쓰지 않습니다. 구조는 [SQLite 데이터베이스](../../../01-foundations/data-formats/sqlite/index.md) 를 봅니다.
3. 여러 아티팩트를 한 [타임라인](../../../03-techniques/analysis/timeline/index.md) 에 올려, 같은 사건을 가리키는 기록끼리 시각이 크게 어긋나는 곳을 찾습니다.
4. 기기 밖에서 시각을 정한 기록이 있으면 함께 봅니다. 계정 서비스 쪽 기록을 받는 절차는 [클라우드 데이터](../../../03-techniques/acquisition/cloud-data.md) 에서 다룹니다.
5. PowerLog 를 수집했고 시험 기기로 표의 동작을 확인했다면, 2~4단계에서 찾은 구간과 PowerLog 기록이 맞는지 봅니다.
6. 결론은 어긋난 구간과 그 크기, 그리고 다른 설명(시간대 변경, 초기화, 동기화)을 지웠는지까지 함께 적습니다.

## 흔한 오판

시간대 변경을 시각 조작으로 읽는 실수가 가장 흔합니다. 현지 시각으로 저장하는 기록은 시간대가 바뀌면 값이 몇 시간씩 뛰어 보이고, 기기 시각은 그대로입니다.

초기화 직후의 기록을 시각 조작으로 읽는 실수도 있습니다. 초기화 뒤 첫 부팅은 기본값 UTC-8 로 찍혀서 [1], 실제 현지 시간대와 다른 시각이 잠깐 나타날 수 있습니다.

행 번호 순서와 시각 순서가 어긋난 구간 하나를 곧바로 조작의 증거로 적는 일도 조심합니다. 다른 기기에서 동기화해 들어온 기록이나 번호를 다시 쓴 행처럼 다른 설명이 가능한지 먼저 따지고, 그 가능성을 지운 만큼만 보고서에 씁니다.

## 보고서 문장 예

> `Photos.sqlite` 의 (표) 에서 `Z_PK` 가 (번호)~(번호) 인 행의 생성 시각은 앞뒤 행보다 (시간) 이른 값으로 기록되어 있습니다. 조사 기간에 시간대 변경 기록은 (있음·없음) 이고, 이 어긋남이 기기 시각 변경에서 생긴 것인지는 이 기록만으로 알 수 없습니다.

## 함께 볼 페이지

- [증거를 없애려 했나 (Anti-Forensics)](index.md) — 이 시나리오 묶음의 허브
- [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md)
- [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)
- [전원 로그 (PowerLog)](../../../02-artifacts/app-usage/powerlog.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [시각 조작 흔적 (Time Manipulation)](../../../03-techniques/analysis/timeline/time-manipulation.md)
- [이 사진은 언제 어디서 찍었나 (Photo Origin)](../photo-origin.md)

## 참고 문헌

1. Cellebrite, "Upgrade from Null: Detecting iOS Wipe Artifacts" — https://cellebrite.com/en/blog/upgrade-from-null-detecting-ios-wipe-artifacts/
