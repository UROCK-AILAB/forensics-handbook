---
title: "바이옴"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 700
has_children: true
has_toc: false
---

# 바이옴 (Biome)

바이옴 (Biome)은 앱 사용·기기 상태 같은 사건을 스트림별 폴더에 SEGB 형식 이진 파일로 쌓아 두는 Apple의 사건 기록 저장소이고, 기록 안의 데이터는 대개 protobuf라서 공개 도구로 필드 번호를 기준 삼아 풀어 읽습니다 [5][6].

## 왜 중요한가

iOS에서는 knowledgeC가 하던 일을 Biome이 점차 넘겨받았다는 관찰이 있습니다. iOS 13의 knowledgeC에는 스트림이 50개 넘게 있었지만 iOS 16부터 활성 스트림이 약 20개로 줄었고, 연구자는 이를 두고 iOS 16부터 Biome이 knowledgeC 역할을 넘겨받고 있다고 결론지었습니다 [4]. 같은 연구자는 iOS에서 포렌식 가치가 있는 스트림 84개를 추려 기기 상태, 연결 기기·네트워크, 위치, 앱 사용, 앱 데이터의 다섯 갈래로 나눴습니다 [3]. 그래서 iOS 16 이후 기기에서 앱 사용을 재구성할 때는 knowledgeC와 Biome을 함께 봅니다.

macOS 쪽 자료는 아직 적습니다. 공개 도구 가운데 mac_apt가 macOS의 Biome 위치를 읽고 [6], ccl_segb는 SEGB 파일을 "iOS, macOS 등에서 발견되는" 파일로 설명하지만 [1], macOS가 어느 버전부터 Biome을 쓰는지와 기록을 얼마나 오래 두는지는 확인한 자료가 없습니다. 형식과 필드의 뜻도 Apple 문서가 아니라 공개 도구 코드와 연구자 글에서 나온 해석이라서, 보고서에는 어느 도구로 읽었는지 함께 적습니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 (macOS) | 시스템 `/private/var/db/biome/streams/`, 사용자별 `~/Library/Biome/streams/` (mac_apt가 보는 경로) [6] |
| 위치 (iOS, 비교용) | 시스템 `/private/var/db/biome/streams/`, 사용자 `/private/var/mobile/Library/Biome/streams/` [3][4][6] |
| 형식 | 스트림 폴더 안 `local` 폴더에 SEGB 파일(v1·v2), 기록 안 데이터는 대개 protobuf [1][5] |
| macOS 버전 | 도입 버전과 SEGB v1→v2 전환 버전 모두 확인 못 함 |
| 보존 기간 | iOS에서 대부분 스트림 28일로 관찰, macOS는 확인 못 함 [3] |
| 알려 주는 것 | 스트림에 따라 앱 사용, 기기 상태, 연결 기기·네트워크, 위치 같은 사건과 그 기록 시각 [3] |
| 알려 주지 않는 것 | 값의 공식 의미(필드 이름과 값의 뜻은 도구 저자의 해석) [2][6] |
| 공개 도구 | ccl_segb(SEGB 읽기) [1], iLEAPP(iOS) [2], mac_apt BIOME 플러그인(macOS·iOS) [6] |

iOS에서 관찰된 흐름은 아래와 같습니다. 두 자료가 SEGB를 처음 본 버전을 다르게 적고 있어서 둘 다 옮깁니다.

| iOS | 관찰 |
|---|---|
| 13 | SEGB·Biome 스트림이 관찰되지 않음 [4] |
| 14 | SEGB 파일이 꾸준히 관찰된 최초 버전 [4] |
| 15 | SEGB v1 등장 [5] |
| 16 | 시스템 수준 Biome 저장소 `/private/var/db/biome` 처음 등장 [4], SEGB v1이 주요 포렌식 자료가 됨 [5] |
| 17 | SEGB v2 도입 [5] |

## 읽는 순서

1. [저장 위치와 스트림 (Streams)](streams.md) — 스트림 폴더 구조와 `local`·`remote` 폴더의 차이, SEGB v1·v2 파일 안에서 기록과 상태 값을 찾는 법, 파일 이름과 기록 시각을 읽는 법을 다룹니다.
2. [앱 사용 스트림 (App.InFocus)](app-infocus.md) — 앱이 앞으로 나오고 물러난 기록을 담은 스트림의 protobuf 필드와 두 가지 시각, 도구마다 다른 해석과 증거로 쓸 때의 한계를 다룹니다.

## 함께 볼 페이지

- [SEGB 형식 (SEGB)](../../../01-foundations/data-formats/segb.md) — Biome 파일의 저장 형식
- [KnowledgeC (knowledgeC.db)](../knowledgec/index.md) — Biome 이전부터 앱 사용을 기록해 온 데이터베이스
- [화면 사용 시간 (Screen Time)](../screen-time.md) — 앱 사용 시간을 다른 쪽에서 확인할 때
- [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md) — 기록 시각을 풀 때
- [어떤 앱을 언제 썼나 (App Usage)](../../../04-scenarios/activity/app-usage.md)
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md)

## 참고 문헌

1. ccl-segb (CCL Forensics, Alex Caithness) — README, ccl_segb1.py, ccl_segb2.py, ccl_segb_common.py — https://github.com/cclgroupltd/ccl-segb
2. iLEAPP — scripts/artifacts/biomeInfocus.py, biomeDKInfocus.py, biomeStreams.py, scripts/ilapfuncs.py — https://github.com/abrignoni/iLEAPP
3. Mattia Epifani, "84 Streams Later, Part 2: Inside Apple Biome" (2026-07-27) — https://blog.digital-forensics.it/2026/07/84-streams-later-part-2-inside-apple.html
4. Mattia Epifani, "84 Streams Later: Exploring the Evolution of Apple Biome in iOS" (2026-07-26) — https://blog.digital-forensics.it/2026/07/84-streams-later-exploring-evolution-of.html
5. Shai Shapira (Cellebrite), "Understanding and Decoding the Newest iOS SEGB Format" (2023-10-16) — https://cellebrite.com/en/understanding-and-decoding-the-newest-ios-segb-format/
6. mac_apt (Yogesh Khatri), plugins/biome.py v1.1 — https://github.com/ydkhatri/mac_apt/blob/master/plugins/biome.py
