---
title: "메모리 분석"
parent: "기법 · 분석"
nav_order: 2080
has_children: true
has_toc: false
---

# 메모리 분석 (Memory Forensics)

실행 중인 맥의 메모리와 디스크로 내려온 메모리 조각을 다루는 영역이고, 어떻게 확보하는지와 어떤 도구로 읽는지, 무엇을 믿을 수 없는지를 세 페이지로 나눠 설명합니다.

## 왜 중요한가

실행 중인 프로세스와 네트워크 연결, 커널에 올라간 확장처럼 맥이 켜져 있는 동안의 상태는 전원을 끄면 사라지고, 디스크 아티팩트로는 흔적만 뒤늦게 볼 수 있습니다. 공개 도구로는 Volatility 3가 `mac.*` 플러그인으로 이런 상태를 읽어 내지만, macOS 지원은 더는 활발히 관리되지 않습니다[4]. 게다가 Apple 실리콘 맥은 하드웨어 보호와 커널 확장 제한 때문에 인텔 맥 시절의 확보 방법이 그대로 통하지 않습니다[1]. 그래서 맥 메모리 분석은 도구를 돌리기 전에 "이 맥에서 메모리를 얻을 수 있는가"부터 따지고, 얻지 못했을 때는 디스크에 남는 스왑 파일과 잠자기 이미지로 무엇을 알 수 있는지까지 함께 봐야 합니다.

## 한눈에 보기

| 대상 | 위치 | macOS 버전·기종 | 알려 주는 것 | 자세히 |
|---|---|---|---|---|
| 실행 중인 메모리 | 켜져 있는 맥의 RAM | Apple 실리콘은 커널 확장 제한과 IOMMU 때문에 확보가 어려움 | 프로세스·네트워크·커널 확장 같은 실행 상태 | [메모리 확보](memory-acquisition.md), [분석 도구와 한계](tools-limits.md) |
| 스왑 파일 | `/System/Volumes/VM/swapfile` 뒤에 번호 (현재 xnu 소스 기준)[3] | 10.15부터 VM 볼륨에 둠[1] | 암호화되어 있어 파일의 존재·개수·크기·시각 수준 | [스왑과 잠자기 이미지](swap-sleepimage.md) |
| 잠자기 이미지 | `pmset` 의 `hibernatefile` 이 가리키는 파일[2] | `hibernatemode` 3·25이고 `standby`·`autopoweroff` 조건이 맞을 때 씀[2], Apple 실리콘에서 쓰는지는 실제 기기에서 확인 | 마지막 hibernate 시점의 단서 | [스왑과 잠자기 이미지](swap-sleepimage.md) |

인텔 맥과 Apple 실리콘 맥의 차이는 두 부분으로 나뉩니다. 확보 쪽에서는 커널 확장을 켜는 조건과 DMA 보호 방식이 다르고, 이 내용은 [메모리 확보 (Acquisition)](memory-acquisition.md)에 표로 정리했습니다. 분석 쪽에서는 Apple 실리콘의 하드웨어 커널 보호와 Secure Enclave 때문에 결과를 읽는 방법이 달라지고, 이 내용은 [분석 도구와 한계 (Tools·Limits)](tools-limits.md)에 있습니다.

## 읽는 순서

1. [메모리 확보 (Acquisition)](memory-acquisition.md) — 확보 도구를 고르는 기준과 커널 확장·DMA 보호가 확보를 어떻게 막는지, 확보할 때 무엇을 기록하는지 다룹니다.
2. [스왑과 잠자기 이미지 (swapfile·sleepimage)](swap-sleepimage.md) — 디스크에 남는 스왑 파일의 위치·크기·암호화와 잠자기 이미지의 설정·헤더 구조를 다룹니다.
3. [분석 도구와 한계 (Tools·Limits)](tools-limits.md) — Volatility 3로 심볼을 맞추고 플러그인을 돌리는 절차와, Apple 실리콘에서 결과를 믿을 수 있는 범위를 다룹니다.

## 함께 볼 페이지

- [라이브 대응 (Live Response)](../../process-acquisition/live-response/index.md) — 켜져 있는 맥에서 메모리를 포함해 무엇을 어떤 순서로 모을지
- [맥 증거 확보 (Acquisition)](../../process-acquisition/evidence-acquisition/index.md) — 디스크 확보 전반
- [커널·시스템 확장 (KEXT·System Extension)](../../../02-artifacts/persistence/kext-system-extension.md) — 메모리의 커널 확장 목록과 대조할 디스크 흔적
- [전원·잠자기 기록 (pmset)](../../../02-artifacts/logs/power-events.md) — 잠자기 이미지 시각과 나란히 볼 기록
- [악성 코드 흔적 분석 (Malware Triage)](../malware-triage/index.md) — 메모리에서 찾은 수상한 프로세스를 이어서 분석
- [암호화된 증거 다루기 (Encrypted Evidence)](../encrypted-evidence/index.md) — FileVault와 암호화된 스왑·이미지를 만났을 때

## 참고 문헌

1. Apple, Apple Platform Security (2026년 8월 판, PDF) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf
2. pmset(1) man page (Xcode man page 미러, keith.github.io — Apple 호스팅 아님) — https://keith.github.io/xcode-man-pages/pmset.1.html
3. Apple xnu osfmk/vm/vm_compressor_backing_store_internal.h — https://raw.githubusercontent.com/apple-oss-distributions/xnu/main/osfmk/vm/vm_compressor_backing_store_internal.h
4. Volatility 3 문서, macOS Tutorial — https://volatility3.readthedocs.io/en/latest/getting-started-mac-tutorial.html
