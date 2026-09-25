---
title: "메모리 덤프 확보"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 3180
---

# 메모리 덤프 확보 (Memory Acquisition)

> 상위 허브: [메모리 분석 (Memory Forensics)](index.md)

## 한 줄 요약

켜져 있는 PC 의 물리 메모리 (Physical Memory) 를 파일로 떠 두는 단계이고, 이렇게 뜬 파일을 메모리 이미지 (Memory Image) 라고 부릅니다.
전원이 꺼지면 메모리 내용은 사라지므로 메모리는 디스크보다 먼저 확보합니다.

## 언제 쓰나

- PC 가 아직 켜져 있을 때 씁니다.
- 실행 중인 프로세스, 열려 있는 네트워크 연결, 디스크에 파일로 남지 않은 코드를 봐야 할 때 씁니다.
- 암호화된 볼륨이 열려 있다면 끄기 전에 어떻게 할지 먼저 정합니다. [암호화 증거 다루기](../encrypted-evidence/index.md) 를 봅니다.
- 전원이 이미 꺼졌다면 이 페이지의 절차를 쓸 수 없습니다. 아래 "전원이 이미 꺼졌을 때" 로 갑니다.

## 확보 원칙

증거 수집 원칙 가운데 메모리 확보에 바로 닿는 것은 아래와 같습니다 [1].

- 휘발성이 큰 것부터 모읍니다 [1].
- 이 순서에서 메모리는 디스크보다 앞에 옵니다 [1]. 순서 전체는 [메모리 분석](index.md) 허브에 있습니다.
- 모으는 동안 자료를 바꾸는 일을 줄입니다. 파일·폴더의 접근 시각을 바꾸지 않는 것까지 여기에 듭니다 [1].
- 증거를 다 모으기 전에는 시스템을 끄지 않습니다 [1]. 끄면 증거를 잃고, 공격자가 종료 스크립트나 서비스를 바꿔 두었다면 끄는 순간 증거가 지워질 수 있습니다.
- 대상 PC 에 있는 프로그램을 믿지 않습니다. 보호된 매체에 담아 온 프로그램을 씁니다 [1].
- 네트워크를 끊을 때도 조심합니다. 연결이 끊기면 증거를 지우는 장치, 곧 데드맨 스위치 (Dead Man Switch) 가 있을 수 있습니다 [1].

## 절차

1. 현장 상태를 적습니다. 화면에 보이는 것, 시각, 확보하는 사람을 적습니다. 라이브 응답 전체 순서는 [라이브 응답](../../process-acquisition/live-response/index.md) 에 있습니다.
2. 확보 도구를 보호된 외부 매체에 담아 갑니다. 대상 PC 에 설치하지 않습니다.
3. 이미지를 저장할 곳을 대상 PC 의 디스크 밖으로 정합니다. 대상 디스크에 쓰면 그 디스크가 바뀝니다.
4. 확보 도구를 실행합니다. 실행한 시각과 명령을 그대로 적습니다.
5. 확보가 끝나면 출력 파일의 해시를 계산해 적습니다. 해시를 남기는 방법은 [증거 획득](../../process-acquisition/evidence-acquisition/index.md) 에 있습니다.
6. 도구 이름·버전·읽기 방법·출력 형식을 적습니다. 나중에 결과를 다시 확인할 때 이 기록을 씁니다.
7. 확보한 이미지를 분석 도구로 한 번 열어 봅니다. 예를 들어 Volatility 3 에는 windows.info 플러그인이 있습니다 [5]. 이미지를 읽지 못하면 PC 가 켜져 있는 동안 다시 뜰 수 있습니다.
8. 그다음 디스크를 확보합니다. 페이지 파일과 최대 절전 파일도 함께 챙깁니다(아래 "함정과 한계" 참고).

## 확보 방법 고르기

| 방법 | 담는 범위 | 참고 |
|---|---|---|
| 물리 메모리 확보 도구 (예: WinPmem) | 물리 메모리 전체 | 아래 절 [2] |
| 작업 관리자의 "Create live memory dump file" (Windows 11) | 커널 모드 또는 사용자 모드 라이브 덤프 | 프로세스를 오른쪽 클릭해 만듭니다 [3] |
| Sysinternals ProcDump | 사용자 모드 프로세스 하나 | 프로세스 하나만 필요할 때 씁니다 [3] |
| 버그 체크 (Bug Check) 때 남는 덤프 | 설정한 덤프 종류에 따라 다릅니다 | 설정 값은 [크래시 덤프](memory-dmp-minidump.md) 에 있습니다 |
| 키보드로 일부러 덤프를 만드는 기능 | — | 설정 방법은 KB 244139 에 있습니다 [4] |

### 크래시 덤프로 메모리 전체를 받으려 할 때

버그 체크 때 완전 메모리 덤프를 받으려면 레지스트리 설정과 충분한 크기의 페이지 파일이 함께 맞아야 하고 [4], 값은 [크래시 덤프](memory-dmp-minidump.md) 에 있습니다.
바뀐 덤프 설정은 재부팅해야 적용되는데 [4], 재부팅하면 지금 메모리 내용이 사라집니다. 그래서 이미 켜져 있는 증거 PC 에서 설정을 새로 바꿔 이 방법을 쓰기는 어렵습니다.

## WinPmem 으로 확보하기 (공개 도구 예)

공개 도구의 예로만 듭니다 [2].

- WinPmem 은 물리 메모리 확보 도구입니다. 처음에는 Google 에서 만들었고 Apache License 2.0 으로 배포합니다.
- 지원 범위는 Windows 7 ~ Windows 10, x86·x64 입니다. Windows 11 은 이 범위에 없습니다.
- 메모리를 읽는 방법이 세 가지, 전체 덤프를 만드는 방법이 두 가지 있습니다. `-1` 옵션을 주면 MmMapIoSpace 방식으로 읽습니다.
- 나머지 읽기 방법의 이름과 기본 방법은 도구 도움말로 확인하고, 실제로 쓴 방법을 적어 둡니다.
- 지금 출력 형식은 raw 이미지입니다. AFF4 지원은 새 드라이버에 맞춰 아직 고쳐지지 않았습니다. 형식 차이는 [증거 이미지·가상 디스크 형식](../../../01-foundations/disk-volume/e01-raw-aff4-vhdx-vmdk.md) 에 있습니다.
- 서명된 배포본은 드라이버의 쓰기 기능이 꺼져 있는데, 확보에는 읽기만 쓰므로 서명된 배포본으로 충분합니다.
- 쓰기 기능은 드라이버를 테스트 서명으로 다시 빌드해야 쓸 수 있고, 이때 `bcdedit -set TESTSIGNING ON` 을 하고 재부팅해야 합니다. 재부팅하면 지금 메모리가 사라지고 부팅 설정도 바뀌므로 증거 PC 에서는 이렇게 하지 않습니다.

실행 예입니다 [2].

```
winpmem_mini_x64.exe physmem.raw
winpmem.exe -1 myimage.raw
```

첫 줄은 물리 메모리를 raw 이미지 `physmem.raw` 로 저장합니다. 둘째 줄은 MmMapIoSpace 방식으로 읽어 `myimage.raw` 로 저장합니다.
출력 파일은 대상 PC 의 디스크가 아닌 외부 매체 경로로 줍니다.

## 전원이 이미 꺼졌을 때

전원이 꺼진 뒤에도 디스크에 메모리 조각이 남을 수 있습니다. 디스크 이미지에서 아래 파일을 찾습니다.

- [최대 절전 파일 (hiberfil.sys)](hiberfil-sys.md)
- [페이지 파일 (pagefile.sys·swapfile.sys)](pagefile-sys-swapfile-sys.md)
- [크래시 덤프 (MEMORY.DMP·Minidump)](memory-dmp-minidump.md)

각 파일이 무엇을 담는지는 해당 페이지에 있습니다.
이 파일들은 확보한 순간이 아니라 Windows 가 파일을 쓴 순간의 메모리를 담습니다.

## 함정과 한계

- **확보 도구도 메모리를 바꿉니다.** 도구를 실행하면 도구의 프로세스와 드라이버가 메모리에 올라옵니다. 확보 원칙에서 변경을 줄이라고 하는 까닭과 같은 문제입니다 [1]. 바꾼 만큼 기록합니다.
- **이미지는 한순간을 찍은 사진이 아닙니다.** 확보하는 동안에도 메모리는 계속 바뀝니다. 그래서 이미지의 앞부분과 뒷부분이 서로 다른 순간의 상태일 수 있다고 알려져 있습니다.
- **작업 관리자는 대상 PC 의 프로그램입니다.** 확보 원칙대로라면 대상 PC 의 프로그램은 믿지 않습니다 [1]. 작업 관리자 덤프는 외부 도구를 쓸 수 없을 때의 차선책으로 봅니다.
- **지원 범위를 벗어난 PC 가 있습니다.** WinPmem 의 지원 범위에는 Windows 11 이 없습니다 [2]. 메모리 무결성(HVCI) 같은 보안 기능이 켜진 PC 에서 확보 드라이버가 막히는지는 공개 자료가 없습니다. 현장에 쓰기 전에 같은 버전·같은 설정의 시험 PC 에서 먼저 돌려 봅니다.
- **물리 메모리 이미지에 없는 내용이 있습니다.** 페이지 파일로 내보낸 내용은 물리 메모리 이미지에 없습니다. 그래서 [페이지 파일](pagefile-sys-swapfile-sys.md) 도 함께 확보합니다.
- **이미지를 네트워크로 보내면 그 연결도 메모리에 보일 수 있습니다.** 네트워크 흔적을 분석할 때 이 연결을 가려내야 합니다. [메모리 속 네트워크 흔적](network-artifacts.md) 을 봅니다.

## 결과를 어떻게 해석하나

- 메모리 이미지는 확보하던 동안의 상태만 담으므로, 이미지에 없다고 해서 그 프로세스나 연결이 없었다는 뜻은 아닙니다. 확보하기 전에 끝났을 수 있습니다.
- 확보 도구 자신의 프로세스가 이미지 안에 보일 수 있습니다. 절차 4단계에서 적은 시각과 도구 이름으로 가려냅니다. 프로세스 목록을 읽는 법은 [프로세스와 DLL 분석](process-analysis.md) 에 있습니다.
- 분석 결과는 확보 기록과 함께 보고합니다. 도구 이름·버전·읽기 방법·시각·해시가 없으면 다른 사람이 결과를 다시 확인할 수 없습니다. [도구 결과 교차 검증](../../reporting/tool-validation.md) 을 봅니다.

보고서 문장 예입니다.

- 쓰지 않을 문장: "PC 의 메모리를 그대로 복사했습니다."
- 쓸 문장: "○○(UTC) 에 외부 매체에 담아 간 확보 도구 ○○(버전 ○○) 로 물리 메모리를 raw 형식으로 확보했습니다. 읽기 방법은 ○○ 입니다. 확보한 파일의 SHA-256 은 ○○ 입니다. 확보하는 동안 확보 도구의 프로세스와 드라이버가 대상 PC 의 메모리에 올라왔습니다."

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| WinPmem (공개, Apache License 2.0) | 물리 메모리 전체를 raw 이미지로 확보합니다 [2] |
| 작업 관리자 (Windows 11) | 커널 모드·사용자 모드 라이브 덤프를 만듭니다 [3] |
| ProcDump (Sysinternals) | 사용자 모드 프로세스 덤프를 만듭니다 [3] |
| Volatility 3 (공개) | 확보한 이미지를 열어 읽히는지 확인합니다 [5] |

## 함께 볼 페이지

- [메모리 분석 (Memory Forensics)](index.md) — 휘발성 순서와 하위 페이지 길잡이입니다.
- [라이브 응답](../../process-acquisition/live-response/index.md) — 켜진 PC 에서 메모리 말고 무엇을 먼저 모으는지 다룹니다.
- [증거 획득](../../process-acquisition/evidence-acquisition/index.md) — 해시와 확보 기록을 남기는 방법입니다.
- [포렌식 조사 절차](../../process-acquisition/investigation-process.md) — 확보가 조사 전체에서 어디에 오는지 다룹니다.
- [최대 절전 파일](hiberfil-sys.md) · [페이지 파일](pagefile-sys-swapfile-sys.md) · [크래시 덤프](memory-dmp-minidump.md) — 디스크에 남는 메모리 조각입니다.

## 참고 문헌

1. IETF, RFC 3227 "Guidelines for Evidence Collection and Archiving" (BCP 55, 2002-02) — https://www.rfc-editor.org/rfc/rfc3227
2. Velocidex, WinPmem README (GitHub) — https://github.com/Velocidex/WinPmem
3. Microsoft Learn, "Collecting User-Mode Dumps" (2024-07-18) — https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps
4. Microsoft Learn, "Memory dump file options" (KB 254649, 2026-02-12) — https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/memory-dump-file-options
5. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
