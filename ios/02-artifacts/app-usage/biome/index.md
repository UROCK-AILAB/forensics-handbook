---
title: "바이옴"
parent: "아티팩트 · 앱 설치·사용 흔적"
nav_order: 370
has_children: true
has_toc: false
---

# 바이옴 (Biome)

## 한 줄 요약

바이옴은 앱 사용과 기기 활동 기록을 스트림별 폴더에 SEGB 라는 이진 파일로 쌓는 저장소이고, iOS 16 부터 KnowledgeC.db 에 있던 앱 사용 기록 같은 핵심 기록이 이쪽으로 옮겨졌습니다.

## 왜 중요한가

iOS 16 에서 KnowledgeC.db 의 일부 핵심 기록이 바이옴으로 옮겨져서[1][7], 요즘 아이폰에서 어떤 앱을 언제 썼는지 물으려면 KnowledgeC.db 만 봐서는 부족하고 바이옴을 함께 봐야 합니다. 한 연구자는 최근 기기의 사용자 영역에서 300개가 넘는 스트림 폴더 가운데 84개가 포렌식에 쓸모 있는 정보를 담는다고 정리했고, 그 범위는 앱 사용, Safari 활동, 방문 장소, 알림, 지갑 거래, Siri, 메시지 활동, Apple Intelligence 까지 이어집니다[2].

다만 Apple 은 바이옴 구조를 공식 문서로 공개하지 않아서 경로와 형식은 모두 연구자와 도구 자료에 기대고 있고, 형식도 iOS 17 에서 SEGB v2 로 한 번 바뀌었습니다[2][3][6]. 로컬 백업에는 바이옴 파일이 드러나지 않는다는 자료가 있어서[3][7] 수집 방식부터 확인해야 합니다. 같은 Apple 계정의 다른 기기에서 동기화된 기록이 한 폴더 안에 섞여 들어오는 점[1][7]도 해석할 때 먼저 가려야 합니다.

## 한눈에 보기

| 무엇 | 위치 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 스트림 폴더 | `/private/var/mobile/Library/Biome/streams/` (사용자 영역), `/private/var/db/biome/streams/` (시스템 영역)[1][7] | iOS 14–15 는 사용자 영역 중심, 시스템 영역 `restricted` 는 iOS 16 에서 생김[2] | 스트림마다 `local`(이 기기), `remote`(동기화된 다른 기기), `tombstone`(기간이 지난 파일)으로 나뉜 기록[1][3][7] |
| SEGB 파일 | 각 스트림 폴더 안 | v1 은 iOS 16 까지, v2 는 iOS 17 부터[2][3][6] | 기록마다 시각과 상태(Written·Deleted), protobuf 페이로드[1][3][6] |
| 동기화 DB | `/private/var/mobile/Library/Biome/sync/sync.db`[1] | iOS 16 조사 | 동기화한 기기와 마지막 동기화 시각[1] |
| 앱 사용 스트림 | `/private/var/db/biome/streams/restricted/_DKEvent.App.InFocus`(iOS 16)[1], iLEAPP 는 `App.InFocus`[5] | iOS 16 이후(iOS 15 까지는 KnowledgeC.db) | 어느 앱이 언제 화면 앞에 나오고 들어갔는지, 번들 ID, 전환 이유[1][3][5] |
| 바이옴 관련 설정 | 백업 HomeDomain `Library/Preferences/` 의 `com.apple.biomed.plist`, `com.apple.biomesyncd.plist` 등(확인 범위: iPhone 13 mini, iOS 27.0) | — | 이름에 바이옴이 들어간 설정 키. 뜻은 확인하지 못했습니다 |

> 그림 자리: 두 바이옴 폴더 아래 스트림 폴더와 `local`·`remote`·`tombstone`, `sync.db` 가 어떻게 놓이는지

공개 도구로는 스트림별 파서를 둔 iLEAPP[2][5], SEGB v1·v2 파일을 모두 읽는 파이썬 모듈 ccl_segb[4], crush[3]가 있고, 상용 분석 도구들도 바이옴과 SEGB v2 해석을 지원한다고 발표했습니다[6][7].

## 읽는 순서

1. [저장 위치와 스트림 (Streams)](streams.md) — 두 바이옴 폴더의 버전별 위치, 스트림 폴더의 `local`·`remote`·`tombstone` 구조, 동기화 DB, SEGB v1·v2 의 차이와 수집 범위를 다룹니다.
2. [앱 사용 스트림 (App.InFocus)](app-infocus.md) — KnowledgeC.db 에서 옮겨 온 앱 전경 사용 기록의 위치, 필드 해석 두 가지, 시각과 전환 이유 읽는 법을 다룹니다.

## 함께 볼 페이지

iOS 15 까지의 앱 사용 기록과 iOS 16 이후에도 남은 기록은 [KnowledgeC (knowledgeC.db)](../knowledgec/index.md)에서, 사용 시간 합계는 [화면 사용 시간 (Screen Time)](../screen-time.md)에서, 알림 스트림과 이어지는 기록은 [알림 기록 (Notifications)](../notifications.md)에서 다룹니다.

파일을 읽는 바탕은 [SEGB 형식 (SEGB)](../../../01-foundations/data-formats/segb.md), [프로토콜 버퍼 (Protocol Buffers)](../../../01-foundations/data-formats/protobuf.md), [시각 값 (Mac 절대 시각·Unix·기타)](../../../01-foundations/value-decoding/time-values.md)에 있고, 수집 방식은 [모바일 증거 확보 (Acquisition)](../../../03-techniques/acquisition/mobile-acquisition/index.md)에서 다룹니다.

조사 흐름은 [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md), [폰 사용 시간 재구성 (Usage Time)](../../../04-scenarios/activity/usage-time.md), [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)에서 이어집니다.

## 참고 문헌

1. D20 Forensics, "iOS 16 - Now You 'C' It, Now You Don't -- Breaking Down The Biomes Part 1" (2022-09) — https://blog.d204n6.com/2022/09/ios-16-now-you-c-it-now-you-dont.html
2. digital-forensics.it, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
3. Be-binary 4n6, "Beyond the C — SEGB and Biome Forensics with crush" (2026-05) — https://bebinary4n6.blogspot.com/2026/05/beyond-c-segb-and-biome-forensics-with.html
4. CCL Group, ccl-segb README — https://github.com/cclgroupltd/ccl-segb
5. iLEAPP, `scripts/artifacts/biomeInfocus.py` (마지막 갱신 2026-09-03) — https://raw.githubusercontent.com/abrignoni/iLEAPP/main/scripts/artifacts/biomeInfocus.py
6. Cellebrite, "Understanding and Decoding the Newest iOS SEGB Format" — https://cellebrite.com/en/blog/understanding-and-decoding-the-newest-ios-segb-format/
7. Magnet Forensics, "Bringing it Back With Biome Data" — https://www.magnetforensics.com/blog/bringing-it-back-with-biome-data/
