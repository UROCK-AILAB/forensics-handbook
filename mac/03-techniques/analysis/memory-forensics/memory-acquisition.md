---
title: "메모리 확보"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 2090
---

# 메모리 확보 (Acquisition)

실행 중인 맥의 메모리를 파일로 떠내는 단계이고, 인텔 맥과 Apple 실리콘 맥은 커널 확장 제한과 DMA 보호 방식이 달라서 쓸 수 있는 방법도 크게 갈립니다.

## 언제 쓰나

맥이 켜져 있고, 실행 중인 프로세스나 네트워크 연결, 커널에 올라간 확장처럼 메모리에서만 볼 수 있는 상태가 조사에 필요할 때 씁니다. 전원을 끄거나 재시동하면 메모리 내용이 사라지기 때문에 확보 여부는 맥을 끄기 전에 정해야 하고, 그 판단은 [라이브 대응 (Live Response)](../../process-acquisition/live-response/index.md)에서 정하는 수집 순서 안에서 내립니다. 디스크 확보와의 앞뒤 관계는 [맥 증거 확보 (Acquisition)](../../process-acquisition/evidence-acquisition/index.md)에서 다룹니다.

확보 도구와 분석 도구는 따로 준비합니다. Volatility 3는 메모리를 확보하지 못하므로 확보는 별도 도구로 합니다[3]. 확보한 파일을 읽는 방법은 [분석 도구와 한계 (Tools·Limits)](tools-limits.md)에 있습니다.

## 절차

1. **하드웨어와 macOS 버전을 먼저 적습니다.** 인텔 맥인지 Apple 실리콘 맥인지, 인텔 맥이라면 T2 칩이 있는지에 따라 아래 제약이 달라집니다. 확인할 곳은 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../../../02-artifacts/system-account/computer-name-hardware.md)와 [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../../../02-artifacts/system-account/os-version-install-history.md)에 정리되어 있습니다.
2. **확보 도구가 그 버전을 지원하는지 확인합니다.** 확보 도구마다 지원하는 OS 버전이 다릅니다[2]. 후보 도구는 아래 "도구" 절에 있습니다.
3. **도구가 커널 확장(kext)을 올려야 하는지 확인합니다.** 커널 확장이 필요하면 아래 "커널 확장 제약" 절의 조건을 먼저 따지고, Apple 실리콘 맥에서 재시동이 필요해지는 상황이면 메모리 확보 대신 라이브 대응 수집과 [스왑과 잠자기 이미지 (swapfile·sleepimage)](swap-sleepimage.md) 확인으로 방향을 돌립니다.
4. **확보 파일과 무결성 값을 함께 남깁니다.** 확보를 시작하고 끝낸 시각, 도구 이름과 버전, 확보 파일의 해시를 기록합니다. 확보 파일 형식과 해시를 남기는 방식이 도구마다 다를 수 있으니, 도구 문서를 보고 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)의 방식으로 미리 시험해 둡니다.
5. **확보하려고 바꾼 설정을 모두 기록합니다.** 보안 정책을 낮추거나 커널 확장을 허용했다면 그 시각과 조작 내용을 적어 둡니다. 이런 조작도 조사 대상 맥에 기록을 남기고(아래 "커널 확장 제약" 절), 나중에 분석하는 사람이 조사자가 남긴 흔적과 원래 있던 흔적을 가려내야 하기 때문입니다.

## 도구

맥 메모리 확보 도구로는 ATC-NY의 Mac Memory Reader, Mac Memoryze, OSXPmem이 있습니다[2]. 오픈소스 확보 도구인 osxpmem은 아래 주소에서 받을 수 있습니다[3].

```
https://github.com/Velocidex/c-aff4/releases/download/3.2/osxpmem_3.2.zip
```

osxpmem이 지원하는 macOS 버전과 Apple 실리콘 지원 여부, 커널 확장이 필요한지는 쓰기 전에 배포본에서 확인합니다. 상용 도구가 맥 메모리 확보를 어디까지 지원하는지도 도구마다 다르므로, 어느 도구든 조사 대상과 같은 하드웨어와 macOS 버전에서 먼저 시험해 보고 씁니다.

## 커널 확장 제약

확보 도구가 커널 확장에 기대는 경우에 해당하는 절입니다. macOS 11부터는 서드파티 커널 확장을 허용해도 필요한 순간에 바로 커널에 올릴 수 없고, 보조 커널 컬렉션 (Auxiliary Kernel Collection, AuxKC)에 합쳐진 뒤 부팅 과정에서 올라갑니다. AuxKC를 다시 만들려면 사용자 승인과 재시동이 필요합니다[1]. SIP가 켜져 있으면 AuxKC에 넣기 전에 커널 확장의 서명을 검증하고, 꺼져 있으면 검증하지 않습니다[1]. Apple 은 macOS 에서 커널 확장을 더는 권장하지 않습니다[1].

| 항목 | Apple 실리콘 이전 맥 | Apple 실리콘 맥 |
|---|---|---|
| AuxKC를 두는 곳 | 데이터 볼륨 | AuxKC 측정값을 LocalPolicy에 서명해 넣음 |
| 커널 확장을 켜는 조건 | AuxKC를 다시 만들 때 사용자 승인과 재시동 (macOS 11부터) | 전원 버튼을 누른 채 시동해 One True Recovery(1TR)로 들어가 보안 정책을 Reduced Security로 낮추고 "커널 확장 허용"을 체크한 뒤 관리자 암호를 넣고 재시동 |

AuxKC를 만들 때는 실제로 들어간 커널 확장 목록을 담은 kext receipt가 생기고, 그 SHA-384 해시가 LocalPolicy에 들어갑니다[1]. 확보 도구의 커널 확장을 올렸다면 이 기록에도 그 확장이 남는다는 뜻이라서, 조사 뒤에 커널 확장 흔적을 볼 때 조사자가 올린 것인지 먼저 구분해야 합니다. 커널 확장 흔적 자체는 [커널·시스템 확장 (KEXT·System Extension)](../../../02-artifacts/persistence/kext-system-extension.md)에서, SIP는 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md)에서 다룹니다.

커널 확장이 필요한 확보 도구를 Apple 실리콘 맥에서 쓰려면 보안 정책을 낮추고 재시동해야 하고, 재시동하면 확보하려던 메모리가 사라집니다.

## DMA 경로

Thunderbolt 같은 포트에 꽂은 장치가 메모리를 직접 읽는 직접 메모리 접근 (DMA) 경로도 막혀 있습니다. Apple 은 2012년부터 맥에 DMA 보호 기술을 여럿 적용했습니다[1].

| 대상 | DMA 보호 방식 |
|---|---|
| 인텔 맥 (VT-d) | 부팅 아주 이른 시점에 IOMMU를 초기화하고, 켜지는 순간부터 기본 거부(default-deny)로 주변장치 DMA를 막음 |
| T2 칩 맥 (macOS 11부터) | 외부 장치와 짝지을 때 UEFI 드라이버를 제한된 ring 3 환경에서 실행 |
| Apple 실리콘 맥 | PCIe·Thunderbolt 포트를 포함한 DMA 에이전트마다 IOMMU가 있어, 주변장치는 자기에게 매핑된 메모리만 접근할 수 있고 매핑 안 된 메모리에 접근하면 커널 패닉이 남 |

출처는 모두 [1]입니다. 어느 기종이든 주변장치가 허락받지 않은 메모리를 읽지 못하게 설계되어 있어, DMA 장치로 메모리 전체를 떠내는 방법은 기대하기 어렵습니다.

## 휘발성 데이터 수집과 메모리 이미징 구분

현장에서 "램 확보"라고 부르는 일에는 서로 다른 두 가지가 섞여 있습니다. 하나는 로그인된 세션에서 명령과 도구로 프로세스·연결 같은 휘발성 데이터를 모으는 일이고, 다른 하나는 물리 메모리 전체를 파일로 떠내는 메모리 이미징입니다. 앞의 것은 요즘 맥에서도 할 수 있지만, 뒤의 것은 T2 칩 맥과 Apple 실리콘 맥에서 현장에서 할 방법이 없습니다[5]. 물리 메모리를 읽으려면 커널 안에서 코드가 돌아야 하는데, 커널 확장을 올리는 길은 위 "커널 확장 제약" 절처럼 재시동을 거쳐야 하고 주변장치로 읽는 길은 "DMA 경로" 절처럼 막혀 있습니다[1].

방법별 가능 여부는 아래와 같습니다[5].

| 방법 | 요즘 맥에서 |
|---|---|
| 현장에서 물리 메모리 이미징 | T2 칩 맥과 Apple 실리콘 맥에서는 불가능 |
| 미리 설치해 둔 기업용 에이전트로 메모리 확보 | 가능하지만, 사고 전에 에이전트를 배포해 둔 곳에서만 |
| T2 이전 인텔 맥의 물리 메모리 이미징 | 가능했지만 이미 단종된 하드웨어 |
| 콜드 부트 공격 | 메모리가 칩 패키지 안에 있어 불가능 |
| DMA·Thunderbolt 로 메모리 읽기 | IOMMU 와 Secure Enclave 보호로 막힘 |
| 칩오프로 메모리 복구 | 칩 패키지 안의 통합 DRAM 이라 현실적이지 않음 |
| 로그인된 세션에서 휘발성 데이터 수집 | 가능 |

`/dev/mem`·`/dev/kmem` 은 오래전에 없어졌고, 서드파티 확장은 물리 메모리를 매핑할 수 없습니다[5]. 이를 막는 장치로 페이지 보호 계층 (Page Protection Layer, PPL)을 드는 자료도 있지만[5], Apple 은 PPL 이 실행하는 모든 코드에 서명이 필요한 시스템에만 해당해서 macOS 에는 없다고 설명합니다[6]. Apple 실리콘 맥의 커널 코드를 하드웨어로 보호하는 커널 무결성 보호 (KIP)는 [분석 도구와 한계 (Tools·Limits)](tools-limits.md)에서 다룹니다.

잠금이 풀린 채 로그인된 세션에서는 평범한 명령과 도구로 아래 휘발성 데이터를 모을 수 있습니다[5].

- 실행 중인 프로세스와 실행 인자, 부모 프로세스 — [프로세스와 열린 파일 (ps·lsof)](../../process-acquisition/live-response/processes-open-files.md)
- 열린 네트워크 연결과 대기 중인 포트, 라우팅 테이블과 ARP 테이블 — [네트워크 연결 (Connections)](../../process-acquisition/live-response/connections.md)
- 로그인한 사용자와 열린 세션 — [로그인·로그아웃 (Login·Logout)](../../../02-artifacts/logs/unified-log-events/login-logout.md)
- 마운트된 볼륨과 그 가운데 지금 잠금이 풀려 있는 암호화 볼륨 — [암호화된 증거 다루기 (Encrypted Evidence)](../encrypted-evidence/index.md)
- 열린 파일과 그 파일을 쥔 프로세스 — [프로세스와 열린 파일 (ps·lsof)](../../process-acquisition/live-response/processes-open-files.md)
- 클립보드 내용
- 올라가 있는 커널 확장과 시스템 확장 — [커널·시스템 확장 (KEXT·System Extension)](../../../02-artifacts/persistence/kext-system-extension.md)
- Wi-Fi 상태와 최근 접속한 네트워크 — [와이파이 기록 (Wi-Fi)](../../../02-artifacts/network/wifi.md)
- 현재 세션을 담은 통합 로그 — [통합 로그 수집 (log collect)](../../process-acquisition/live-response/log-collect.md)

이렇게 모은 결과는 메모리 이미지가 아니므로 보고서에서 메모리 이미지라고 부르지 않습니다. 그래도 프로세스·연결·풀린 볼륨처럼 메모리 이미지로 답하려던 질문 가운데 상당수는 이 결과로 답할 수 있습니다[5]. 결과를 쓸 외부 저장 장치는 APFS 나 HFS+ 로 포맷해야 파일의 확장 속성이 남고[4][5], 실행한 명령은 그대로 기록합니다[5].

잠금이 풀린 세션은 오래가지 않습니다. 지금 풀려 있는 암호화 볼륨은 세션이 이어지는 동안만 풀려 있어서, 맥이 잠자기에 들거나 잠기거나 꺼지면 다시 암호가 있어야 열립니다. 그래서 화면을 넘겨받으면 바로 잠자기와 화면 잠금을 끄고, 세션을 잃을 수 있는 일보다 수집을 먼저 합니다[5].

## 메모리는 마지막에

Windows 에서는 메모리부터 뜨는 경우가 많지만, 맥에서는 메모리 확보가 커널 패닉을 일으켜 재시동으로 증거를 잃을 수 있습니다[4]. 전체 디스크를 확보하거나 관리자 암호를 얻기 전에 패닉이 나면 조사 전체가 쓸모없어지므로, SWGDE 는 메모리 확보를 다른 확보를 모두 마친 뒤로 미루라고 권합니다[4].

> "conducting a memory acquisition on a Mac may result in a kernel panic, rendering the examination useless if the panic occurs prior to obtaining a full-disk acquisition or the administrator's password. … Because of this propensity to panic, Mac memory acquisitions should be held until all other forensic acquisition actions have been taken by the examiner or when memory acquisition software has been preinstalled on the computer." — SWGDE 23-F-005-1.0, 6.1절[4]

인용문 끝의 "or when … preinstalled" 는 메모리 확보 소프트웨어가 미리 설치되어 있으면 예외라고도 읽힙니다. 기업 사고 대응에서 에이전트를 미리 배포해 둔 경우에도, 메모리는 다른 수집을 모두 마친 뒤에 뜹니다[5]. [휘발성 순서 (Order of Volatility)](../../process-acquisition/live-response/order-of-volatility.md)의 RFC 3227 순서에서는 메모리가 2단계에 들어 있지만, 맥에서는 이 권고에 따라 메모리 확보를 맨 끝으로 미룹니다.

실행 중인 맥에서는 아래 순서로 수집합니다[5].

1. 작업하는 동안 세션이 끝나지 않게 잠자기와 화면 잠금을 끕니다.
2. 관리자 암호가 맞는지 확인합니다.
3. 위 목록의 휘발성 데이터를 모읍니다.
4. APFS 로컬 스냅숏을 목록으로 뽑고 보존합니다. [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../snapshot-diff.md)
5. 키체인과 필요한 논리 증거를 확보합니다. [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md), [논리 수집 (Logical Collection)](../../process-acquisition/evidence-acquisition/logical-collection.md)
6. [전체 디스크 접근 권한 (Full Disk Access)](../../process-acquisition/live-response/full-disk-access.md)을 확인한 뒤 디스크를 확보합니다. [맥 증거 확보 (Acquisition)](../../process-acquisition/evidence-acquisition/index.md)
7. 메모리 확보 에이전트가 미리 설치되어 있을 때만, 이 시점에 메모리 확보를 시도합니다.

현장 사정으로 이 순서를 바꿨다면 바꾼 이유를 함께 기록합니다[5].

## 함정과 한계

도구 목록에 이름이 있다고 해서 조사 대상의 macOS 버전을 지원한다고 보면 안 됩니다. 도구 목록은 버전 확인을 전제로 한 것이고[2], osxpmem도 조사 대상 버전을 지원하는지 먼저 확인해야 합니다.

Apple 실리콘 맥에서 커널 확장을 허용하는 과정에는 재시동이 들어 있어서, 확보를 준비하는 동작이 확보 대상을 지워 버릴 수 있습니다. 확보를 시작하기 전에 도구가 커널 확장을 요구하는지부터 확인해야 하는 이유입니다.

메모리 이미지를 얻어도 모든 비밀이 보이지는 않습니다. Secure Enclave처럼 하드웨어가 따로 보호하는 영역의 한계는 [분석 도구와 한계 (Tools·Limits)](tools-limits.md)에 모아 두었습니다.

## 결과를 어떻게 해석하나

확보한 이미지는 확보를 시작하고 끝낸 사이의 메모리 상태이고, 확보 도구도 실행되는 동안 그 메모리 안에 있습니다. 그래서 이미지에서 찾은 확보 도구의 프로세스나 커널 확장은 조사 행위의 흔적으로 따로 적어 둡니다.

확보에 실패했다는 사실은 메모리에 볼 것이 없었다는 뜻이 아닙니다. 그때는 디스크에 남는 [스왑과 잠자기 이미지 (swapfile·sleepimage)](swap-sleepimage.md)와 라이브 대응 수집 결과로 할 수 있는 만큼만 보완하고, 보고서에는 확보하지 못한 이유를 함께 씁니다.

보고서에는 "몇 시 몇 분부터 몇 시 몇 분까지 어떤 도구의 어떤 버전으로 메모리를 확보했고, 확보 파일의 해시는 이 값이며, 확보를 위해 이런 설정을 바꿨다" 처럼 확보 조건과 조작을 그대로 적습니다. 문장 틀은 [포렌식 보고서 (Forensic Report)](../../reporting/forensic-report.md)를 봅니다.

## 참고 문헌

1. Apple, Apple Platform Security (2026년 8월 판, PDF) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf ("Direct memory access protections for Mac computers", "Reduced Security policy", "Securely extending the kernel in macOS" 절)
2. Volatility 2 위키, Mac — https://github.com/volatilityfoundation/volatility/wiki/Mac
3. Volatility 3 문서, macOS Tutorial — https://volatility3.readthedocs.io/en/latest/getting-started-mac-tutorial.html
4. SWGDE 23-F-005-1.0, Best Practices Apple MacOS Forensic Acquisition (2024-03-15) — https://www.swgde.org/wp-content/uploads/2024/04/2024-03-15-SWGDE-Best-Practices-Apple-MacOS-Forensic-Acquisition-23-F-005-1.0.pdf (6절, 6.1절 "Volatile Data Acquisition and Initial Network Concerns", 8절)
5. SUMURI, Mac Forensics Best Practices Guide, 2026 Edition (2026-09) — https://sumuri.com/ (Section 08 "Volatile Data and Memory")
6. Apple, Apple Platform Security, "Operating system integrity" — https://support.apple.com/guide/security/operating-system-integrity-sec8b776536b/web
