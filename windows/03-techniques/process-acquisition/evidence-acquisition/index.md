---
title: "증거 획득"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 3040
has_children: true
has_toc: false
---

# 증거 획득 (Evidence Acquisition)

증거 획득은 원본 매체를 바꾸지 않고 사본을 만드는 일이며, 사본이 원본과 같다는 것은 해시로, 누가 증거를 다뤘는지는 보관 기록으로 보입니다.
데이터 획득은 계획 세우기, 획득, 무결성 검증의 세 단계로 나뉩니다.

## 왜 중요한가

분석은 사본으로만 하고, 원본은 필요할 때 사본을 다시 만들 수 있게 보관합니다.
원본을 직접 열면 내용이 바뀔 수 있는데, 비정상 종료 상태의 ESE 데이터베이스는 JET API 로 열려면 트랜잭션 로그로 먼저 복구해야 하고 이 복구가 파일 내용을 바꿉니다.

증거를 법적·징계 절차에 쓸지는 데이터를 모으기 전에 정하며, 보존할지 분명하지 않으면 보존하는 쪽을 기본으로 삼습니다.
모든 단계와 쓴 도구를 자세히 적어 두면 다른 분석가가 나중에 같은 과정을 되풀이할 수 있습니다.
획득은 로컬에서 할 수도 있고 네트워크로 할 수도 있는데, 통제하기 쉬운 로컬 획득이 대개 낫습니다.

## 한눈에 보기

> 그림 자리: 계획 세우기 → 획득 → 무결성 검증의 세 단계 위에, 쓰기 방지(획득 중)·해시(검증)·보관 기록(처음부터 끝까지)이 어디에 붙는지 보여 주는 흐름

### 단계와 하위 페이지

| 단계 | 하는 일 | 남는 것 | 자세히 |
|---|---|---|---|
| 계획 | 예상 가치·휘발성·드는 노력으로 우선순위를 정합니다 | 수집 목록 | [선별 수집](triage-collection.md) |
| 획득 | 원본 매체를 비트 단위로 복사합니다 | 이미지 파일 또는 사본 매체 | [디스크 이미징](disk-imaging.md) |
| 획득 | 미리 고른 파일만 복사합니다 | 파일 모음 | [선별 수집](triage-collection.md) |
| 획득 | 가상 디스크 파일을 복사하거나 클라우드 디스크 스냅숏을 뜹니다 | 가상 디스크 사본, 스냅숏 | [가상 머신·클라우드 디스크 확보](vm-cloud-disk.md) |
| 획득 중 보호 | 연결한 매체에 컴퓨터가 쓰지 못하게 막습니다 | 쓴 장치와 설정 기록 | [쓰기 방지](write-blocker.md) |
| 검증 | 원본과 사본의 해시를 계산해 비교합니다 | 해시 값과 계산 시각 | [해시로 무결성 검증](hash-verification.md) |
| 처음부터 끝까지 | 누가 언제 어디서 다뤘고 어떻게 넘겼는지 적습니다 | 보관 기록 | [증거 보관 연속성](chain-of-custody.md) |

### 어떤 방식을 고르나

매체에서 파일을 복사하는 방식은 논리 백업 (Logical Backup) 과 비트 스트림 이미징 (Bit Stream Imaging) 으로 나뉩니다.
논리 백업에는 지운 파일과 슬랙 공간의 잔여 데이터가 들어가지 않지만, 비트 스트림 이미징은 빈 공간과 슬랙 공간까지 담는 대신 저장 공간과 시간이 더 듭니다.

| 상황 | 먼저 볼 방식 |
|---|---|
| 증거로 쓸 가능성이 있습니다 | [디스크 이미징](disk-imaging.md) |
| 지운 파일과 슬랙 공간을 봐야 합니다 | [디스크 이미징](disk-imaging.md) |
| 파일 시각이 중요합니다 | [디스크 이미징](disk-imaging.md) |
| 데이터 출처가 너무 많습니다 | [선별 수집](triage-collection.md) |
| 시스템을 멈출 수 없습니다 | [선별 수집](triage-collection.md) |
| 가상 머신이나 클라우드 인스턴스입니다 | [가상 머신·클라우드 디스크 확보](vm-cloud-disk.md) |

### 휘발성 순서에서 이 묶음이 맡는 범위

증거는 빨리 사라지는 것부터 모읍니다. 순서는 아래와 같습니다.

레지스터·캐시 → 라우팅 표·ARP 캐시·프로세스 표·커널 통계·메모리 → 임시 파일 시스템 → **디스크** → 원격 로그·감시 데이터 → 물리 구성·네트워크 구조 → 보관 매체

이 묶음은 디스크부터 아래 단계를 다룹니다. 디스크보다 먼저 사라지는 데이터는 [라이브 응답](../live-response/index.md) 에서 다루고, 메모리를 뜨고 분석하는 법은 [메모리 분석](../../analysis/memory-forensics/index.md) 에 있습니다.

## 읽는 순서

1. [디스크 이미징 (Disk Imaging)](disk-imaging.md) — 원본 매체를 비트 단위로 복사하는 절차를 다룹니다. 켜진 시스템을 끌지 정하는 기준과 E01 세그먼트·머리 정보 확인도 다룹니다.
2. [쓰기 방지 (Write Blocker)](write-blocker.md) — 하드웨어·소프트웨어 쓰기 방지를 연결하는 순서를 다룹니다. Windows diskpart 의 읽기 전용 속성을 대신 쓸 때 따질 점도 봅니다.
3. [해시로 무결성 검증 (Hash Verification)](hash-verification.md) — 이미징 전후로 원본과 사본의 해시를 비교하는 절차입니다. 알고리즘을 고르는 법과 해시가 달라지는 경우도 모읍니다.
4. [선별 수집 (Triage Collection)](triage-collection.md) — 미리 고른 파일만 모을 때의 우선순위와 절차를 다룹니다. 수집물로 말할 수 있는 범위도 정리합니다.
5. [가상 머신·클라우드 디스크 확보 (VM·Cloud Disk)](vm-cloud-disk.md) — Hyper-V·VMware 가상 디스크 파일과 클라우드 디스크 스냅숏을 확보합니다. 차등 디스크의 부모 파일까지 모으는 법을 다룹니다.
6. [증거 보관 연속성 (Chain of Custody)](chain-of-custody.md) — 증거를 누가 언제 어디서 다뤘고 어떻게 넘겼는지 적는 법입니다. 이미지 머리 정보와 클라우드 감사 로그를 보관 기록과 맞춰 보는 법도 다룹니다.

## 함께 볼 페이지

- [포렌식 조사 절차](../investigation-process.md) — 획득 앞뒤로 이어지는 조사 전체 흐름입니다.
- [라이브 응답](../live-response/index.md) — 켜진 시스템에서 디스크보다 먼저 사라지는 데이터를 모읍니다.
- [증거 이미지·가상 디스크 형식](../../../01-foundations/disk-volume/e01-raw-aff4-vhdx-vmdk.md) — 획득 결과로 남는 E01·VHDX·VMDK 파일의 구조입니다.
- [암호화 증거 다루기](../../analysis/encrypted-evidence/index.md) — 암호화한 볼륨을 뜨거나 넘겨받았을 때 봅니다.
- [도구 결과 교차 검증](../../reporting/tool-validation.md) · [분석 보고서 작성](../../reporting/forensic-report.md) — 획득 기록을 보고서의 근거로 옮길 때 봅니다.

## 참고 문헌

- Karen Kent, Suzanne Chevalier, Tim Grance, Hung Dang, *NIST SP 800-86: Guide to Integrating Forensic Techniques into Incident Response* (2006-08) — https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
- D. Brezinski, T. Killalea, *RFC 3227: Guidelines for Evidence Collection and Archiving* (BCP 55, 2002-02) — https://www.rfc-editor.org/rfc/rfc3227
