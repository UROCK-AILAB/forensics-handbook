---
title: "파일 시스템 이벤트"
parent: "아티팩트 · 파일 시스템"
nav_order: 930
has_children: true
has_toc: false
---

# 파일 시스템 이벤트 (FSEvents)

파일 시스템 이벤트 (FSEvents)는 볼륨에서 어떤 경로가 만들어지고 지워지고 바뀌었는지를 fseventsd 데몬이 `.fseventsd` 폴더에 남긴 기록이고, 레코드에 시각이 없어서 날짜는 다른 단서로 어림해야 합니다.

## 왜 중요한가

FSEvents 이벤트는 재부팅한 뒤에도 남고 [4], 지금은 없는 파일이나 폴더의 경로도 지워진 기록(Removed 플래그)과 함께 남아 있을 수 있습니다. Mac 본체뿐 아니라 Mac에 꽂았던 외장 저장 장치에서도 기록이 나오고, 이벤트 파일이 GZIP 형식이라서 비할당 영역에서 지워진 이벤트 파일을 카빙해 찾을 수도 있습니다 [6]. 윈도우의 $UsnJrnl처럼 무엇이 바뀌었는지를 적는 기록이지만 레코드에 시각 필드가 없다는 점이 다릅니다 [1].

해석은 조심해야 합니다. fseventsd는 짧은 시간 안에 한 디렉터리에서 여러 번 일어난 알림을 하나로 합치고 [3], 레코드에는 시각이 없어서 날짜는 이벤트 파일의 수정 시각이나 기록 속 로그 파일 이름으로 어림합니다 [1][2][6]. 그래서 FSEvents만으로는 "언제, 누가" 를 단정하지 않고, "이 경로에 이런 변경이 기록됐다" 를 확인하는 데 씁니다.

## 한눈에 보기

| 항목 | 내용 |
|---|---|
| 위치 | `/.fseventsd`, `/System/Volumes/Data/.fseventsd` (공개 도구가 보는 경로) [2], 외장 저장 장치의 볼륨 [6] |
| 형식 | 여러 멤버로 된 GZIP 파일 안에 디스크 로그 스트림(페이지)이 이어짐 [1] |
| macOS 버전 | 레코드 버전 1(`1SLD`) Mac OS X 10.5 ~ macOS 10.12, 버전 2(`2SLD`) macOS 10.13 High Sierra부터, 버전 3(`3SLD`) macOS 14 Sonoma부터(FSEventsParser 코드 주석 기준) [1][2] |
| 알려 주는 것 | 바뀐 경로, 변경 종류와 대상 종류(플래그), 이벤트 ID로 본 순서, 버전에 따라 노드 ID·UID |
| 알려 주지 않는 것 | 사건 시각, 바꾼 프로그램이나 사람, 합쳐지기 전의 개별 동작 |
| 공개 도구 | FSEventsParser(1SLD·2SLD·3SLD) [2], plaso `fseventsd` 파서(코드 설명상 1SLD·2SLD) [5] |

## 읽는 순서

1. [파일 형식 (.fseventsd)](format.md) — GZIP을 푼 뒤의 페이지 헤더와 버전별 레코드 구조를 오프셋 표와 헥스 예시로 따라갑니다.
2. [이벤트 플래그 읽기 (Flags)](flags.md) — 플래그 비트의 뜻과, 도구마다 16진수가 다르게 보이는 이유, 커널·API 이름과 섞지 말아야 할 이유를 정리합니다.
3. [해석 함정 (Pitfalls)](pitfalls.md) — 날짜 추정, 이벤트 합치기, 빠진 기록과 지운 기록, 카빙 결과를 읽을 때의 주의점과 보고서 문장 예를 다룹니다.

## 함께 볼 페이지

- [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md) — 데이터 볼륨 쪽 `.fseventsd` 경로를 이해할 때
- [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md) — 기록이 남는 볼륨의 구조
- [USB 저장 장치 (USB Storage)](../../external-devices/usb/index.md) — 외장 장치에서 나온 기록을 연결 기록과 맞춰 볼 때
- [삭제 데이터 복구 (Data Recovery)](../../../03-techniques/analysis/data-recovery/index.md) — 지워진 이벤트 파일을 카빙할 때
- [타임라인 작성 (Timeline)](../../../03-techniques/analysis/timeline/index.md) — 시각 없는 기록을 다른 기록과 한 시간축에 놓을 때
- [지운 파일의 흔적 찾기 (Deleted File Traces)](../../../04-scenarios/activity/deleted-file-traces.md)
- [증거를 없애려 했나 (Anti-Forensics)](../../../04-scenarios/activity/anti-forensics/index.md)

## 참고 문헌

1. libyal dtformats — MacOS File System Events Disk Log Stream format — https://github.com/libyal/dtformats/blob/main/documentation/MacOS%20File%20System%20Events%20Disk%20Log%20Stream%20format.asciidoc
2. FSEventsParser 4.1 소스 (Nicole Ibrahim) — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/FSEParser_V4.1.py
3. Apple, File System Events Programming Guide — Technology Overview (2012-12-13) — https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/TechnologyOverview/TechnologyOverview.html
4. Apple, File System Events Programming Guide — Using the File System Events API — https://developer.apple.com/library/archive/documentation/Darwin/Conceptual/FSEvents_ProgGuide/UsingtheFSEventsFramework/UsingtheFSEventsFramework.html
5. plaso fseventsd 파서 소스 — https://raw.githubusercontent.com/log2timeline/plaso/main/plaso/parsers/fseventsd.py
6. FSEventsParser README — https://raw.githubusercontent.com/dlcowen/FSEventsParser/master/README.md
