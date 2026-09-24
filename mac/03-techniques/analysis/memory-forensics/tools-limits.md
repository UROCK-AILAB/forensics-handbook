---
title: "분석 도구와 한계"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 2110
---

# 분석 도구와 한계 (Tools·Limits)

맥 메모리 이미지는 공개 도구 가운데 Volatility를 중심으로 분석하고, 결과를 어디까지 믿을지는 커널에 꼭 맞는 심볼 테이블을 구했는지와 Apple 실리콘의 하드웨어 보호에 따라 달라집니다.

## 언제 쓰나

확보한 메모리 이미지에서 프로세스와 네트워크, 커널 확장 같은 실행 상태를 읽어 낼 때 씁니다. 이미지를 얻는 단계는 [메모리 확보 (Acquisition)](memory-acquisition.md)에서, 디스크에 남는 스왑과 잠자기 이미지는 [스왑과 잠자기 이미지 (swapfile·sleepimage)](swap-sleepimage.md)에서 다룹니다.

## 절차 (Volatility 3)

1. **커널 배너를 확인합니다.** 먼저 `banners.Banners` 플러그인으로 이미지 속 커널 버전을 확인합니다[9]. 기본 사용법은 아래와 같습니다.

   ```
   python3 vol.py -f <메모리 이미지> banners.Banners
   ```

2. **맞는 심볼 테이블을 준비합니다.** Volatility Foundation이 미리 만들어 둔 맥 심볼 묶음(`https://downloads.volatilityfoundation.org/volatility3/symbols/mac.zip`)을 받아 `volatility3/symbols/` 아래에 둡니다[9]. 심볼 파일의 배너는 버전 번호만이 아니라 컴파일 시각 같은 요소까지 이미지의 배너와 정확히 맞아야 합니다[4].
3. **묶음에 없으면 심볼을 직접 만듭니다.** 배너와 정확히 맞는 디버그 커널을 구해 dwarf2json으로 JSON 심볼 파일을 만들고, 심볼 디렉터리의 `mac` 폴더에 둡니다. Volatility 3 문서는 리눅스 예시의 `linux` 를 `mac` 으로 바꿔 `dwarf2json mac ...` 형태로 실행하라고 적습니다[4]. 같은 문서는 맥이 리눅스보다 커널 종류가 훨씬 적고 배포판이 하나라서 맞는 심볼을 찾기 쉽다고 설명합니다[4].
4. **플러그인을 실행합니다.** 튜토리얼은 `mac.pslist`, `mac.pstree`, `mac.ifconfig` 를 예로 듭니다[9].

   ```
   python3 vol.py -f <메모리 이미지> mac.pslist
   python3 vol.py -f <메모리 이미지> mac.pstree
   python3 vol.py -f <메모리 이미지> mac.ifconfig
   ```

5. **디스크 흔적과 대조합니다.** 메모리에서 나온 결과는 아래 "결과를 어떻게 해석하나" 절의 방식으로 디스크 아티팩트와 맞춰 봅니다.

## 도구

### Volatility 3

Volatility 3에는 `mac.*` 플러그인이 23개 있습니다[5]. 문서의 플러그인 설명은 요약을 거친 것이라 이 페이지에는 이름만 옮깁니다.

```
mac.bash.Bash
mac.check_syscall.Check_syscall
mac.check_sysctl.Check_sysctl
mac.check_trap_table.Check_trap_table
mac.dmesg.Dmesg
mac.ifconfig.Ifconfig
mac.kauth_listeners.Kauth_listeners
mac.kauth_scopes.Kauth_scopes
mac.kevents.Kevents
mac.list_files.List_Files
mac.lsmod.Lsmod
mac.lsof.Lsof
mac.malfind.Malfind
mac.mount.Mount
mac.netstat.Netstat
mac.proc_maps.Maps
mac.psaux.Psaux
mac.pslist.PsList
mac.pstree.PsTree
mac.socket_filters.Socket_filters
mac.timers.Timers
mac.trustedbsd.Trustedbsd
mac.vfsevents.VFSevents
```

Volatility 3 문서는 "parity release 이후 macOS 분석 지원은 더는 활발히 관리되지 않는다. 기존 플러그인은 남지만 앞으로 갱신·버그 수정이 없을 수 있다"고 적습니다[9]. Volatility 3가 지원하는 macOS 버전 범위와 Apple 실리콘(arm64) 메모리 이미지 지원 여부는 문서에서 찾지 못했습니다(확인 필요).

### Volatility 2 (역사적 참고)

Volatility 2 위키에는 10.5 Leopard(32비트)부터 10.9 Mavericks(10.9.1–10.9.4, 64비트)까지 미리 만든 프로필이 있고, 그 뒤 버전은 프로필 저장소 목록을 보라고 적혀 있습니다[6]. 프로필은 Apple 개발자 사이트에서 Kernel Debug Kit를 받아 만듭니다. 커널 `.dSYM` 에서 `dwarfdump` 로 디버그 정보를 뽑고 `dsymutil` 로 심볼을 만든 뒤, `.vtypes` 와 `.symbol.dsymutil` 파일을 ZIP으로 묶습니다[6]. 이 책이 주로 다루는 10.15 이후 버전에서는 옛 자료를 읽을 때 참고하는 정도로 봅니다.

## 함정과 한계

Apple 실리콘 맥은 커널을 하드웨어로 보호합니다. 커널 무결성 보호 (Kernel Integrity Protection, KIP)가 켜지면 부팅 뒤 메모리 컨트롤러가 커널과 커널 확장을 올린 보호 영역에 쓰기를 거부하고, 이 설정을 담당하는 하드웨어는 부팅 뒤 잠깁니다[1]. SIP는 커널 권한으로 중요한 시스템 파일의 쓰기를 제한하는 기능이고, 하드웨어 기능인 KIP와는 별개입니다[1]. SIP 자체는 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md)에서 다룹니다.

| 항목 | 인텔 맥 | Apple 실리콘 맥 |
|---|---|---|
| 커널 코드 보호 | SIP(소프트웨어) | SIP와 하드웨어 KIP |

필자 판단으로는, `mac.check_syscall`·`mac.check_trap_table` 같은 커널 무결성 점검 플러그인은 인텔 시절의 루트킷 기법을 겨냥한 것으로 보입니다. Apple 실리콘에서는 그런 변조가 어려워진 만큼 이 플러그인이 "이상 없음"을 내도 예상된 결과일 뿐 깨끗하다는 증거가 아닙니다. 플러그인의 설계 의도는 확인하지 못했습니다.

Secure Enclave는 DRAM의 전용 영역에서 돌고, 메모리 보호 엔진 (Memory Protection Engine)이 그 영역을 암호화하고 인증합니다. Secure Enclave 밖에서는 암호화된 메모리만 보입니다[1]. 그래서 메모리 이미지를 얻어도 Secure Enclave 안의 키는 볼 수 없다고 봐야 합니다(필자 판단). 암호화된 자료 전반은 [암호화된 증거 다루기 (Encrypted Evidence)](../encrypted-evidence/index.md)에서 다룹니다.

메모리 압축기(compressor)로 압축된 페이지를 Volatility가 풀어서 보여 주는지는 확인하지 못했습니다. 압축된 페이지에 있던 내용이 결과에 빠질 수 있으니, 문자열 검색이나 프로세스 메모리 결과가 비어 있을 때 곧바로 "없었다"고 쓰지 않습니다.

## 결과를 어떻게 해석하나

배너와 맞지 않는 심볼로 얻은 결과는 쓰지 않습니다. 문서는 배너가 컴파일 시각 같은 요소까지 정확히 맞아야 한다고 적고 있어서[4], 보고서에는 이미지의 배너와 쓴 심볼 파일을 함께 적습니다.

플러그인이 오류를 내거나 빈 결과를 내면 먼저 도구 쪽 문제를 의심합니다. macOS 지원이 더는 활발히 관리되지 않는다는 점[9]과 지원 버전 범위를 확인하지 못했다는 점을 함께 적고, 같은 이미지를 다른 버전의 도구로도 돌려 봅니다. 검증 방식은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)을 따릅니다.

메모리에서 얻은 결과는 디스크 흔적과 맞춰 본 뒤에 보고서에 씁니다. 프로세스 목록은 [통합 로그의 프로세스 실행 기록 (Process Events)](../../../02-artifacts/execution/unified-log-process.md)과, 커널 확장 목록은 [커널·시스템 확장 (KEXT·System Extension)](../../../02-artifacts/persistence/kext-system-extension.md)과, 네트워크 결과는 [네트워크 인터페이스와 설정 (SystemConfiguration)](../../../02-artifacts/network/network-interfaces.md)과 대조합니다. 메모리에만 있고 디스크에 흔적이 없는 프로세스를 찾았다면 [악성 코드 흔적 분석 (Malware Triage)](../malware-triage/index.md)으로 넘깁니다.

보고서 문장은 "메모리 이미지에서 이 도구의 이 버전과 이 심볼 파일로 mac.pslist를 실행한 결과, 이 이름의 프로세스가 이 PID로 나타났다" 처럼 도구와 조건, 기록이 말하는 만큼만 씁니다.

## 참고 문헌

1. Apple, Apple Platform Security (2026년 8월 판, PDF) — https://help.apple.com/pdf/security/en_US/apple-platform-security-guide.pdf ("Memory Protection Engine", "Kernel Integrity Protection", "System Integrity Protection" 절)
4. Volatility 3 문서, Creating New Symbol Tables — https://volatility3.readthedocs.io/en/latest/symbol-tables.html
5. Volatility 3 문서, volatility3.plugins.mac 패키지 — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.mac.html
6. Volatility 2 위키, Mac — https://github.com/volatilityfoundation/volatility/wiki/Mac
9. Volatility 3 문서, macOS Tutorial — https://volatility3.readthedocs.io/en/latest/getting-started-mac-tutorial.html
