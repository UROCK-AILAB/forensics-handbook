---
title: "확보 방법 고르기"
parent: "맥 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1920
---

# 확보 방법 고르기 (T2·Apple Silicon)

T2 칩이 든 인텔 맥과 Apple silicon 맥은 파일볼트(FileVault)를 꺼 두어도 내장 볼륨이 암호화돼 있어서, 확보 방법은 맥이 켜져 있는지, 암호나 복구 키를 아는지, 칩이 무엇인지를 보고 고릅니다 [1][4][5].

## 언제 쓰나

현장에서 맥에 손대기 전에 이 페이지로 방법을 정합니다. 확보 절차 전체의 흐름은 [맥 증거 확보 (Acquisition)](index.md)에서, 조사 전체의 순서는 [조사 절차 (Investigation Process)](../investigation-process.md)에서 봅니다.

올바른 자격 증명이나 복구 키가 없으면 저장 장치를 떼어 다른 컴퓨터에 연결해도 내장 APFS 볼륨은 암호화된 채로 보호됩니다 [1]. 그래서 디스크를 떼어 쓰기 방지 장치에 물린 뒤 이미징하는 전통 방식으로는 이 맥들에서 풀린 데이터를 얻기 어렵습니다.

## 먼저 알아 둘 전제 — 볼륨 암호화

Apple silicon 맥과 T2 맥은 파일볼트 키를 전부 보안 영역(Secure Enclave)에서 처리하고, 암호화 키를 CPU에 직접 내놓지 않습니다 [1]. 파일볼트를 켜고 끈 상태에 따라 볼륨 암호화 키를 지키는 방식이 다릅니다 [1].

| 상태 | 볼륨 | 볼륨 암호화 키를 지키는 것 |
|---|---|---|
| 파일볼트 꺼짐 | 암호화돼 있음 | 보안 영역 안의 하드웨어 UID만 |
| 파일볼트 켜짐 | 암호화돼 있음 | 사용자 암호와 하드웨어 UID를 합친 값 |

파일볼트가 꺼져 있어도 볼륨은 암호화돼 있고, 볼륨 암호화 키는 보안 영역 안의 하드웨어 UID로만 보호됩니다 [1]. 파일볼트를 켤 때는 재사용 방지(anti-replay) 장치가 있어서 하드웨어 UID만으로 만든 옛 키로는 볼륨을 풀 수 없고, 볼륨을 지우면 보안 영역이 그 볼륨의 암호화 키를 안전하게 삭제합니다 [1]. 지운 볼륨은 이미징해도 복구를 기대하기 어렵다고 판단합니다. 시스템·데이터 볼륨 암호화는 macOS 10.15 Catalina와 macOS 11 Big Sur 이후 판에 해당하는 내용이고 [1], 버전별 세부 차이는 판마다 다를 수 있어 분석 대상 맥의 macOS 버전에 맞춰 확인합니다. 키 구조 자체는 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md), 볼륨 배치는 [볼륨 그룹과 펌링크 (Volume Group·Firmlinks)](../../../01-foundations/disk-volume/volume-group-firmlinks.md)에서 다룹니다.

## 칩에 따라 다른 부팅 제한

외부 매체로 부팅해 이미징하려면 칩마다 다른 부팅 보안 설정을 넘어야 합니다.

| 항목 | T2 맥 (인텔) [4] | Apple silicon 맥 [5] |
|---|---|---|
| 설정하는 곳 | macOS 복구로 시동한 뒤 Utilities 메뉴 > Startup Security Utility, 관리자 자격 증명 필요 | 설치된 운영체제마다 따로 두는 보안 정책(LocalPolicy) |
| 보안 단계 | Full Security(기본값, 필요하면 Apple에 연결해 확인하며 인터넷 필요) / Medium Security(Apple·Microsoft 서명만 확인, 인터넷 불필요) / No Security | Full Security(기본값, 그 맥의 ECID에 묶인 개인화 서명) / Reduced Security(Apple의 전역 서명, 옛 macOS·서드파티 kext 실행 가능) / Permissive Security(보안 영역이 로컬에서 서명한 부트 객체 허용) |
| 외부 매체 부팅 | 기본값은 허용하지 않음. 이 유틸리티에서 바꿀 수 있음 | 그 OS 버전을 먼저 recoveryOS에서 인증된 재시작으로 개인화(personalize)해야 함 |
| 그 밖의 장벽 | 펌웨어 암호를 켜 두면 다른 디스크로 부팅할 수 없음 | recoveryOS에 들어가려면 전원 버튼을 길게 눌러야 해서 맥 앞에 있는 사람만 할 수 있음 |

T2 맥에서 외부 부팅으로 이미징하려면 관리자 인증을 거쳐 이 설정을 바꿔야 하고, 펌웨어 암호가 걸려 있으면 그 길이 막힌다고 판단합니다 [4]. Apple silicon 맥은 모든 부팅을 로컬에서 처리하고 [5], 서드파티 부팅 매체(리눅스 기반 포렌식 매체 등)를 쓸 수 있는지는 공개된 자료가 없어 같은 기종의 시험용 맥에서 확인해야 합니다. 서명과 SIP의 관계는 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md)에서 봅니다.

## 절차

1. 맥의 상태를 적습니다. 켜져 있는지, 잠금이 풀려 있는지, 칩이 인텔 T2인지 Apple silicon인지를 확인한 시각과 함께 남깁니다.
2. 켜져 있고 잠금이 풀려 있으면 [논리 수집 (Logical Collection)](logical-collection.md)이나 [라이브 이미징 (Live Imaging)](live-imaging.md)을 먼저 합니다. 맥을 끄면 파일볼트 키가 다시 사용자 암호 뒤로 들어가서, 암호를 모르는 상황이라면 이때가 풀린 데이터를 얻을 기회라고 판단합니다 [1]. 휘발성 정보를 모으는 순서는 [라이브 대응 (Live Response)](../live-response/index.md)을 따릅니다.
3. 꺼져 있고 암호를 알면 칩에 따라 고릅니다. Apple silicon 맥은 공유 디스크 모드를 쓰고 [3], 인텔 맥은 대상 디스크 모드 [2]나 외부 부팅 [4]을 씁니다. 두 모드의 절차는 [공유 모드와 대상 디스크 모드 (Share Disk·Target Disk Mode)](share-disk-target-disk.md)에 있습니다.
4. 꺼져 있고 암호도 복구 키도 모르면 볼륨이 풀리지 않습니다 [1]. 이때 할 수 있는 일은 [암호화된 증거 다루기 (Encrypted Evidence)](../../analysis/encrypted-evidence/index.md)에서 이어 봅니다.
5. 어느 방법을 골랐든 결과물이 파일 수준(논리) 사본인지 블록 수준 사본인지 기록하고, 해시와 보관 기록은 [해시와 증거 보관 (Hash·Chain of Custody)](hash-chain-of-custody.md)을 따릅니다.

위 단계를 한 표로 줄이면 아래와 같습니다.

| 맥 상태 | 암호·복구 키 | 고를 방법 |
|---|---|---|
| 켜짐, 잠금 풀림 | 몰라도 됨 | 논리 수집, 라이브 이미징 |
| 꺼짐 | 앎 | Apple silicon: 공유 디스크 모드 / 인텔: 대상 디스크 모드, 외부 부팅 |
| 꺼짐 | 모름 | 볼륨이 풀리지 않음 |

## 함정과 한계

켜진 맥을 조사하려고 재시작하거나 끄는 순간 2단계의 기회가 사라집니다. 대상 디스크 모드는 켜진 상태에서도 시동 디스크 설정으로 재시작해 들어갈 수 있지만 [2], 재시작하면 잠금이 풀린 상태를 잃는다는 점을 먼저 따져 봅니다.

T2 맥에서 Startup Security Utility 설정을 바꾸면 그 사실이 맥 어디에 흔적으로 남는지는 공개된 분석 자료가 없습니다. 조사 중에 설정을 바꿨다면 바꾼 항목과 시각을 보관 기록에 적어, 나중에 그 변화를 사용자 행위로 오해하지 않게 합니다.

Apple silicon 맥에서 SIP를 끄려면 LocalPolicy 서명 키에 접근할 수 있는 사용자의 인증이 필요하고, kext를 쓰려면 Reduced Security로 낮춘 뒤 Auxiliary Kernel Collection으로 합쳐 재시작해야 합니다 [5]. 커널 확장이 필요한 수집 도구는 이 조건에 걸린다고 판단합니다. 커널 확장의 흔적은 [커널·시스템 확장 (KEXT·System Extension)](../../../02-artifacts/persistence/kext-system-extension.md)에서 봅니다.

## 결과를 어떻게 해석하나

확보 방법은 사본에 무엇이 담겼는지를 정합니다. 켜진 맥에서 논리 수집한 사본에는 도구가 고른 파일만 들어 있고, 공유 디스크 모드로 얻은 사본도 파일 수준이라고 판단합니다(근거는 공유 모드 페이지에 있습니다). 그래서 보고서에는 "Apple silicon 맥이 꺼진 상태에서 공유 디스크 모드로 연결해 데이터 볼륨의 파일을 복사했다" 처럼 맥의 상태와 방법, 사본의 수준을 함께 적습니다. 보고서 문장의 틀은 [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md)에서 다룹니다.

## 참고 문헌

1. Volume encryption with FileVault in macOS (Apple Platform Security) — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
2. Transfer files between two Mac computers using target disk mode (Apple Support HT201462) — https://support.apple.com/HT201462
3. Use macOS Recovery on a Mac with Apple silicon (Mac User Guide) — https://support.apple.com/guide/mac-help/macos-recovery-a-mac-apple-silicon-mchl82829c17/mac
4. About Startup Security Utility on a Mac with the Apple T2 Security Chip (Apple Support 102522) — https://support.apple.com/en-us/102522
5. Startup Disk security policy control for a Mac with Apple silicon (Apple Platform Security) — https://support.apple.com/guide/security/startup-disk-security-policy-control-sec7d92dc49f/web
