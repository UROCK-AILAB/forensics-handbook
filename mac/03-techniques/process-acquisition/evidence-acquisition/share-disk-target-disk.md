---
title: "공유 모드와 대상 디스크 모드"
parent: "맥 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1940
---

# 공유 모드와 대상 디스크 모드 (Share Disk·Target Disk Mode)

대상 디스크 모드(Target Disk Mode)는 인텔 맥을, 공유 디스크 모드(Share Disk)는 Apple silicon 맥을 케이블로 다른 맥에 이어 그 맥의 내장 디스크 내용을 읽게 하는 기능이고, 꺼진 맥의 암호를 알 때 확보 방법으로 씁니다 [1][2].

## 언제 쓰나

맥이 꺼져 있고 사용자 암호를 알 때 고르는 방법입니다. 켜진 맥이라면 다른 방법이 먼저라서, 판단 순서는 [확보 방법 고르기 (T2·Apple Silicon)](choosing-method.md)에서 먼저 봅니다. Apple silicon 맥에서는 대상 디스크 모드 대신 macOS 복구로 시동해 공유 디스크 모드로 파일을 옮깁니다 [1]. 두 기능은 칩에 따라 갈리고 쓰는 법도 다릅니다.

| 항목 | 대상 디스크 모드 [1] | 공유 디스크 모드 [2] |
|---|---|---|
| 대상 맥 | 인텔 맥 | Apple silicon 맥 |
| 들어가는 법 | 꺼진 상태면 T 키를 누른 채 켬. 켜진 상태면 시스템 설정 > 일반 > 시동 디스크에서 "Restart in Target Disk Mode" | macOS 복구로 시동한 뒤 Recovery 앱의 Utilities > Share Disk |
| 케이블 | Thunderbolt | USB, USB-C, Thunderbolt |
| 다른 맥에서 보이는 모습 | 바탕화면에 디스크 아이콘, Finder 사이드바에서 접근 | Finder 사이드바 Locations 아래 Network에서 그 맥에 Guest로 접속 |
| 끝내는 법 | Finder 사이드바에서 Control-클릭 > Eject 후 전원 버튼으로 끔 | 분석용 맥에서 볼륨을 꺼낸 뒤 Stop Sharing |

## 절차

### 대상 디스크 모드 (인텔 맥)

1. 대상 맥이 꺼져 있으면 T 키를 누른 채 켭니다 [1]. 켜져 있으면 시스템 설정 > 일반 > 시동 디스크에서 "Restart in Target Disk Mode" 를 고릅니다 [1]. 켜진 맥이라면 재시작하기 전에 [확보 방법 고르기](choosing-method.md)의 2단계를 확인합니다.
2. 두 맥을 Thunderbolt 케이블로 잇습니다 [1].
3. 분석용 맥의 바탕화면에 디스크 아이콘이 나타나고, Finder 사이드바에서 접근합니다 [1].
4. 복사를 마치면 Finder 사이드바에서 디스크를 Control-클릭해 Eject를 고르고, 대상 맥은 전원 버튼으로 끕니다 [1].

### 공유 디스크 모드 (Apple silicon 맥)

1. 시스템 볼륨과 Options 버튼이 나타날 때까지 전원 버튼을 길게 누른 뒤 Options를 고르고 Continue를 누릅니다 [2].
2. 두 맥을 USB, USB-C, Thunderbolt 케이블 가운데 하나로 잇습니다 [2].
3. Recovery 앱에서 Utilities > Share Disk를 고르고, 공유할 볼륨을 고른 뒤 Start Sharing을 누릅니다 [2]. 공유 디스크 절차에는 잠금을 풀거나 암호를 넣는 단계가 없습니다 [2].
4. 분석용 맥의 Finder 사이드바에서 Locations 아래 Network를 열고, 공유 디스크를 연 맥을 두 번 클릭한 뒤 Connect As에서 Guest로 접속합니다 [2].
5. 복사를 마치면 분석용 맥에서 볼륨을 꺼내고, 대상 맥의 Share Disk 앱에서 Stop Sharing을 누른 뒤 Share Disk > Quit Share Disk로 닫습니다 [2].

같은 Recovery 앱의 Utilities 메뉴에는 Share Disk와 함께 Terminal과 Startup Security Utility도 있습니다 [2]. 복구 환경에서 어떤 메뉴를 열었는지는 모두 보관 기록에 적습니다.

## 함정과 한계

공유 디스크 모드는 분석용 맥이 Finder의 Network 항목에서 Guest로 접속해 파일을 읽는 방식이라서, 블록 단위 물리 이미지를 만들 수 없는 파일 수준 접근으로 보입니다 [2]. 결과가 파일 수준이면 디스크 전체의 해시를 낼 수 없어서, 해시를 남기는 방법이 달라집니다. 그 방법은 [해시와 증거 보관 (Hash·Chain of Custody)](hash-chain-of-custody.md)에 있습니다.

대상 디스크 모드에서 파일볼트 볼륨을 열 때 암호를 묻는지, 내장 디스크가 블록 장치로 보여 블록 이미징이 되는지, T2 맥의 내장 디스크를 이 모드로 붙였을 때 풀린 데이터가 읽히는지, 공유 디스크 모드를 지원하는 최소 macOS 버전이 무엇인지는 공개된 분석 자료가 없습니다. 그래서 이 두 기능을 현장에 쓰기 전에는 같은 기종과 같은 macOS 버전의 시험용 맥으로 결과를 확인하고 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에 따라 기록합니다. 암호가 걸린 볼륨을 여는 조건은 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md)와 [암호화된 증거 다루기 (Encrypted Evidence)](../../analysis/encrypted-evidence/index.md)에서 이어 봅니다.

분석용 맥이 대상 디스크를 올리는 동안 원본에 무엇을 쓰는지도 공개된 자료가 없어서, 연결한 시각과 끊은 시각, 열어 본 폴더를 적어 두면, 나중에 그 시간대의 파일 시스템 변화가 조사자의 조작인지 가를 수 있습니다. 파일 시스템 변화 기록은 [파일 시스템 이벤트 (FSEvents)](../../../02-artifacts/filesystem/fsevents/index.md)에서 봅니다.

## 결과를 어떻게 해석하나

분석용 맥의 Finder로 복사한 파일은 파일 시스템 수준의 시각이나 속성이 복사 과정에서 그대로 옮겨졌는지 따로 확인해야 합니다. 보고서에는 "Apple silicon 맥을 공유 디스크 모드로 열고, 분석용 맥에서 Guest로 접속해 이 볼륨의 파일을 복사했다" 처럼 모드·볼륨·접속 방식을 적고, 결과물이 블록 단위 이미지가 아니라 파일 복사본이라는 점을 밝힙니다.

## 참고 문헌

1. Transfer files between two Mac computers using target disk mode (Apple Support HT201462) — https://support.apple.com/HT201462
2. Use macOS Recovery on a Mac with Apple silicon (Mac User Guide) — https://support.apple.com/guide/mac-help/macos-recovery-a-mac-apple-silicon-mchl82829c17/mac
