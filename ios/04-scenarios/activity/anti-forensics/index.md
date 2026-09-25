---
title: "증거를 없애려 했나"
parent: "시나리오 · 행위 재구성"
nav_order: 1500
has_children: true
has_toc: false
---

# 증거를 없애려 했나 (Anti-Forensics)

아이폰에서 기기 초기화, 앱 지우기, 메시지·사진 지우기, 기기 시각 바꾸기가 있었는지, 있었다면 언제였는지를 흔적으로 따지는 시나리오 묶음입니다.

## 왜 중요한가

지우거나 바꾸는 행위는 다른 증거를 읽는 전제를 흔듭니다. 앱을 지웠다면 그 앱의 기록이 없는 이유가 설명되고, 시각을 바꿨다면 그 시기 기록의 시각을 모두 다시 따져야 하며, 초기화했다면 초기화 이전 데이터는 암호학적으로 읽을 수 없습니다 [4]. 그래서 초기화 사건에서는 무엇이 지워졌는지보다 언제 초기화했는지가 주로 남고 [1][4], 앱이나 내용을 지운 사건에서는 지운 대상이 아니라 다른 DB·plist·로그에 남은 흔적을 찾습니다 [2].

이 묶음의 페이지는 모두 기록이 말하는 만큼만 씁니다. 지운 기록은 지운 일이 있었다는 사실을 보여 줄 뿐이고, 증거를 없애려 한 의도나 지운 이유는 다른 정황과 함께 판단합니다.

## 한눈에 보기

| 행위 | 주로 볼 곳 | 버전 조건 | 알려 주는 것 |
|---|---|---|---|
| 초기화 | 설정 도우미 plist, 초기화 뒤 첫 부팅에 생기는 파일, containermanagerd 로그 | 흔적 자료는 iOS 13.7·14.2 에서 시험했고 [1], iOS 15 이후는 확인하지 못함 | 새 기기로 설정했는지 복원했는지, 초기화한 무렵 |
| 앱 지우기 | 지운 앱 목록 plist, 앱 상태 DB, 홈 화면 배치 plist, 구입 앱 목록 | 흔적 자료는 2019년 글이고 [2], iOS 15 이후는 확인하지 못함 | 지운 앱과 마지막으로 지운 날짜, 앱 정리와 삭제의 구분 |
| 메시지·사진 지우기 | "최근 삭제된 항목", `sms.db` 와 `Photos.sqlite` 의 삭제·복구 관련 표 | 메시지 복구는 iOS 16 이후이고 30~40일 [3], 사진은 30일 [5] | 지운 항목이 아직 남아 있는지, 삭제 관련 칸의 값(뜻은 검증 필요) |
| 시각 바꾸기 | 시간대 변경 기록, 기록별 시간대 칸, 행 순서와 시각 순서 비교 | 원문으로 확인한 자료가 적음 | 시간대 변경 시점, 기록 시각이 어긋난 구간 |

수집 범위에 따라 볼 수 있는 흔적이 크게 다릅니다. 관찰한 로컬 백업에서는 KnowledgeC·바이옴·PowerLog·installd 로그가 보이지 않았고 (확인 범위: iPhone 13 mini, iOS 27.0), 지운 앱 목록 plist 는 전체 파일 시스템 이미지에서만 얻을 수 있다고 [2] 이 설명합니다. 수집 방법의 차이는 [모바일 증거 확보](../../../03-techniques/acquisition/mobile-acquisition/index.md) 에서 다룹니다.

## 읽는 순서

1. [초기화 (Erase All Content)](erase-reset.md) — 초기화가 데이터에 하는 일과, 초기화 시점을 좁히는 흔적과 순서를 다룹니다.
2. [앱 지우기 (App Removal)](app-removal.md) — 지운 앱과 삭제 날짜를 찾고, 앱 정리(offload)와 삭제를 가르는 법을 다룹니다.
3. [메시지·사진 지우기 (Content Deletion)](content-deletion.md) — "최근 삭제된 항목" 의 조건과, 메시지·사진 DB 에서 삭제 관련 칸을 보는 순서를 다룹니다.
4. [시각 바꾸기 (Time Change)](time-change.md) — 시간대 변경과 시각 변경을 가르고, 기록 시각이 어긋난 구간을 찾는 법을 다룹니다.

초기화 뒤 첫 부팅의 시간대 문제는 1번과 4번에 함께 걸려서, 두 페이지를 이어 읽으면 좋습니다.

## 함께 볼 페이지

- [지운 대화와 사진 찾기 (Deleted Content)](../deleted-content.md) — 지운 내용을 되찾는 쪽
- [초기화와 복원 흔적 (Erase·Restore)](../../../02-artifacts/system-account/erase-restore.md)
- [설치된 앱 (Installed Apps·applicationState.db)](../../../02-artifacts/app-usage/installed-apps.md)
- [시간대와 시각 설정 (Time Zone)](../../../02-artifacts/system-account/time-zone.md)
- [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)
- [포렌식 보고서 (Forensic Report)](../../../03-techniques/reporting/forensic-report.md) — 기록이 말하는 만큼만 쓰는 법

## 참고 문헌

1. Cellebrite, "Upgrade from Null: Detecting iOS Wipe Artifacts" — https://cellebrite.com/en/blog/upgrade-from-null-detecting-ios-wipe-artifacts/
2. D20 Forensics, "iOS - Tracking Traces of Deleted Applications" (2019) — https://blog.d204n6.com/2019/09/ios-tracking-traces-of-deleted.html
3. Apple Support, "Recover deleted text messages on your iPhone or iPad" — https://support.apple.com/en-us/102615
4. Apple Platform Security, "Data Protection in Apple devices" — https://support.apple.com/guide/security/data-protection-sece8608431d/web
5. Apple Support, "Delete photos on your iPhone or iPad" — https://support.apple.com/en-us/104967
