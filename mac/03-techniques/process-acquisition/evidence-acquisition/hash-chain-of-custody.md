---
title: "해시와 증거 보관"
parent: "맥 증거 확보"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1960
---

# 해시와 증거 보관 (Hash·Chain of Custody)

해시는 확보한 사본이 그 뒤로 바뀌지 않았음을 보이는 값이고, 증거 보관 기록(Chain of Custody)은 누가 언제 무슨 목적으로 증거를 다루고 넘겼는지 남기는 기록이라서, 맥에서 어떤 방법으로 확보했든 두 가지를 함께 남깁니다 [1].

## 언제 쓰나

확보를 마친 직후부터 사건이 끝날 때까지 씁니다. 확보 방법마다 사본의 수준이 달라서 해시를 계산하는 단위도 달라지고, 방법을 고르는 순서는 [확보 방법 고르기 (T2·Apple Silicon)](choosing-method.md)에 있습니다.

## 증거 보관 기록의 정의와 칸

NIST 용어집은 증거 보관 기록을 NIST SP 800-72에서 가져와 이렇게 정의합니다 [1].

> "A process that tracks the movement of evidence through its collection, safeguarding, and analysis lifecycle by documenting each person who handled the evidence, the date/time it was collected or transferred, and the purpose for the transfer."

NIST SP 800-101 Rev. 1의 정의도 거의 같고, 끝부분만 "the purpose for any transfers" 로 다릅니다 [1]. 정의가 요구하는 칸은 증거를 다룬 사람, 수집하거나 넘긴 날짜와 시각, 넘긴 목적입니다 [1]. 맥 사건에서는 사본이 바뀌지 않았음을 보이고 시각을 다시 읽을 수 있도록 몇 칸을 더 두는 편이 좋다고 판단합니다. 아래 표에서 "출처" 칸은 그 구분을 보여 줍니다.

| 칸 | 적을 내용 | 출처 |
|---|---|---|
| 다룬 사람 | 수집·인계·인수한 사람 | NIST 정의 [1] |
| 날짜·시각 | 수집하거나 넘긴 날짜와 시각 | NIST 정의 [1] |
| 목적 | 넘긴 이유(분석, 보관, 반환 등) | NIST 정의 [1] |
| 해시 | 계산한 알고리즘과 값 | 필자 추가 |
| 도구·버전 | 수집·이미징·해시 계산에 쓴 도구와 버전 | 필자 추가 |
| 시간대 | 날짜·시각을 적은 기준 시간대 | 필자 추가 |
| 확보 방법 | 논리 수집, 라이브 이미징, 공유 디스크 모드 등과 사본의 수준 | 필자 추가 |

기록 한 줄의 틀은 아래와 같습니다. 괄호 안은 실제 값을 넣을 자리이고, 예로 든 값이 아닙니다.

| 순번 | 날짜·시각(시간대) | 넘긴 사람 | 받은 사람 | 목적 | 대상 | 해시(알고리즘) |
|---|---|---|---|---|---|---|
| 1 | (수집 시각, 시간대) | (수집자) | (보관 담당) | 보관 | (파일 이름) | (계산한 값) |

## 절차

1. 확보가 끝나면 곧바로 결과물의 해시를 계산하고, 알고리즘과 값, 계산에 쓴 도구와 버전을 적습니다.
2. 위 칸으로 첫 줄을 씁니다. 날짜·시각에는 기준 시간대를 붙입니다.
3. 증거를 넘길 때마다 한 줄을 더하고, 받은 쪽이 해시를 다시 계산해 첫 값과 같은지 적습니다.
4. 분석은 사본의 사본으로 하고, 분석을 시작하기 전과 마친 뒤에 원래 사본의 해시가 그대로인지 확인합니다.

## 확보 방법별로 해시를 남기는 단위

확보 방법마다 결과물의 모양이 달라서 해시를 계산할 대상도 다릅니다.

| 확보 방법 | 결과물 | 해시를 남기는 단위 |
|---|---|---|
| 논리 수집 — Aftermath | zip 아카이브 하나 [2] | 수집 직후 그 아카이브의 해시 |
| 논리 수집 — UAC | 수집물 | 수집물 전체의 해시를 직접 계산 |
| 공유 디스크 모드 | 복사한 파일들 | 파일별 해시 목록 |
| 라이브 이미징 — 디스크 유틸리티 Read-only(UDRO) | 이미지 파일 | 이미지 파일의 해시 |

UAC는 실행 중인 프로세스와 실행 파일의 해시를 모으지만 [3], 이 값은 수집 대상의 해시이고 수집물 전체의 해시가 아닙니다. 그래서 수집물을 받은 뒤 해시를 따로 계산합니다. 공유 디스크 모드는 파일 수준 접근이라고 판단하고 [4], 그렇다면 디스크 전체의 해시를 낼 수 없어서 복사한 파일마다 해시를 남긴 목록을 만듭니다. 디스크 유틸리티의 Read-only(UDRO) 이미지는 만든 뒤 바뀌지 않는 형식이라서 [5] 증거 사본으로 두기에 맞습니다.

이미지 형식에 내장된 체크섬이 있는지, 그 체크섬을 검증하는 명령, E01 같은 포렌식 이미지 형식에 들어가는 해시, macOS에 기본으로 들어 있는 해시 명령의 사용법은 이번에 확인한 자료에 없어서 싣지 않습니다. 해시 계산 도구를 고르고 결과를 믿을 수 있는지 확인하는 과정은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)에서 다룹니다. 각 방법의 절차는 [논리 수집 (Logical Collection)](logical-collection.md), [공유 모드와 대상 디스크 모드 (Share Disk·Target Disk Mode)](share-disk-target-disk.md), [라이브 이미징 (Live Imaging)](live-imaging.md)에 있습니다.

## 함정과 한계

해시는 계산한 순간부터 사본이 바뀌지 않았음을 보일 뿐이고, 계산하기 전에 사본이 원본과 같았는지는 보여 주지 못합니다. 라이브 상태에서 만든 사본은 원본 맥이 계속 바뀌는 중에 떴기 때문에 원본과 다시 맞춰 볼 수도 없어서, 수집 시각과 방법을 적은 보관 기록이 사본의 신뢰를 받치는 근거가 됩니다.

라이브 수집에서 시각을 무엇을 기준으로 적을지(수집한 맥의 시계인지, 기준 시계와 얼마나 어긋났는지, 어느 시간대인지)는 확인한 자료가 없습니다. 적어도 적은 시각이 어느 시계와 어느 시간대 기준인지 밝혀 둡니다. 맥에 설정된 시간대와 시계 동기화 설정은 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md)에서 확인합니다.

## 결과를 어떻게 해석하나

해시가 일치하면 "이 사본은 기록된 시각에 계산한 값과 같다" 는 뜻이고, 사본 안의 내용이 사실이라는 뜻은 아닙니다. 보고서에는 "수집 직후 계산한 해시와 분석 전후에 계산한 해시가 같다" 처럼 언제 계산한 값끼리 비교했는지 적고, 보관 기록 표를 부록으로 붙입니다. 보고서의 틀은 [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md)에서 다룹니다.

## 참고 문헌

1. NIST CSRC Glossary: chain of custody — https://csrc.nist.gov/glossary/term/chain_of_custody
2. jamf/aftermath README (GitHub) — https://github.com/jamf/aftermath
3. tclahr/uac README (GitHub) — https://github.com/tclahr/uac
4. Use macOS Recovery on a Mac with Apple silicon (Mac User Guide) — https://support.apple.com/guide/mac-help/macos-recovery-a-mac-apple-silicon-mchl82829c17/mac
5. Create a disk image using Disk Utility on Mac (Disk Utility User Guide) — https://support.apple.com/guide/disk-utility/create-a-disk-image-dskutl11888/mac
