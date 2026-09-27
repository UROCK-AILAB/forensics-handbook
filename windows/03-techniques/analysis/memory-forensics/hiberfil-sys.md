---
title: "최대 절전 파일"
parent: "메모리 분석"
grand_parent: "기법 · 분석"
nav_order: 3230
---

# 최대 절전 파일 (hiberfil.sys)

최대 절전 파일 (Hibernation File) 은 Windows 가 최대 절전이나 빠른 시작으로 꺼질 때 메모리 내용을 써 두는 파일이며, 파일 이름은 hiberfil.sys 입니다.
전원이 꺼진 PC 에서도 이 파일로 꺼지기 전 메모리의 일부를 볼 수 있습니다.

## 언제 쓰나

- 전원이 꺼진 채 들어온 PC 에서 메모리 흔적을 찾을 때 씁니다. 켜진 PC 라면 먼저 [메모리 덤프 확보](memory-acquisition.md) 를 봅니다.
- 켜진 PC 에서 뜬 메모리 이미지가 있어도 씁니다. 이 파일에는 그보다 앞선 시점의 메모리가 들어 있을 수 있습니다.
- PC 가 최대 절전이나 빠른 시작을 썼는지 확인할 때 씁니다.

## 최대 절전과 빠른 시작

Windows 가 시작하는 방식은 세 가지입니다 [1].

| 시작 방식 | 설명 |
|---|---|
| 콜드 시작 (Cold Boot) | 전통적인 시작 방식입니다 |
| 최대 절전에서 깨어나기 (Wake from Hibernation) | 최대 절전 상태에서 다시 켜는 방식입니다 |
| 빠른 시작 (Fast Startup) | 앞의 두 방식을 합친 것입니다. Windows 8 부터 있습니다 |

빠른 시작은 최대 절전 파일을 메모리에 올려 시작합니다 [1].
빠른 시작으로 끌 때 Windows 는 아래 순서를 밟습니다 [1].

1. 전체 종료처럼 모든 프로그램을 닫고 모든 사용자 세션을 로그오프합니다.
2. 드라이버에 최대 절전을 준비하라고 알립니다.
3. 커널 메모리 이미지를 hiberfil.sys 에 저장하고 전원을 끕니다. 이 이미지에는 올라와 있던 커널 모드 드라이버도 들어 있습니다.

이 순서가 분석에서 뜻하는 것은 아래와 같습니다.

빠른 시작으로 만든 파일에는 사용자 세션을 로그오프한 뒤의 커널 쪽 메모리만 들어 있을 가능성이 크고, 그래서 사용자 프로그램의 메모리는 기대하기 어렵습니다.
사용자가 최대 절전을 골라 끄면 세션을 닫지 않으므로 사용자 프로그램의 메모리도 담긴다고 알려져 있습니다.
두 경우는 담긴 범위가 다르므로 어느 쪽으로 만든 파일인지 먼저 구분합니다. PC 가 꺼지고 켜진 기록은 [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) 에서 봅니다.

## 위치와 설정

파일 위치는 공개 문서에 나오지 않으므로 [1], 디스크 이미지의 파일 목록에서 hiberfil.sys 라는 이름으로 찾습니다.

### powercfg 로 켜고 끄기

`powercfg /hibernate` (줄여서 `/H`) 로 최대 절전을 켜고 끄고, 파일 크기를 정합니다 [2].

```
powercfg /hibernate on
powercfg /hibernate off
powercfg /hibernate /size <퍼센트>
powercfg /hibernate /type reduced
powercfg /hibernate /type full
```

- `/size` 는 전체 메모리 대비 파일 크기의 비율입니다 [2].
- `/size` 를 주면 최대 절전도 함께 켜집니다 [2].
- `/type reduced` 로 만든 파일은 빠른 시작 (hiberboot) 만 지원합니다 [2].
- 크기를 따로 정했거나 HiberFileSizePercent 값이 40 이상이면 full 로 봅니다 [2].
- HiberFileSizePercent 는 `HKLM\SYSTEM\CurrentControlSet\Control\Power` 에 있습니다 [2].
- reduced 로 바꾸려면 `powercfg /hibernate /size 0` 을 먼저 하고 `powercfg /hibernate /type reduced` 를 합니다 [2].
- 최대 절전에 들어가기까지 기다리는 시간(분)은 `powercfg /change` 의 `hibernate-timeout-ac`·`hibernate-timeout-dc` 로 정합니다 [2].

디스크 이미지에서 떼어 낸 SYSTEM 하이브를 읽을 때는 경로의 `CurrentControlSet` 부분을 실제로 쓰던 제어 집합으로 바꿔 읽습니다.
방법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에 있습니다.

### 켜진 PC 에서 확인하기

라이브 응답 중이라면 아래 두 명령도 참고합니다 [2].

| 명령 | 보여 주는 것 |
|---|---|
| `powercfg /availablesleepstates` | 쓸 수 있는 절전 상태와 쓸 수 없는 이유 |
| `powercfg /lastwake` | 마지막으로 절전에서 깨운 원인 |

이 명령은 대상 PC 의 프로그램이라서 실행한 시각과 명령을 그대로 적습니다.
전체 순서는 [라이브 응답](../../process-acquisition/live-response/index.md) 을 따릅니다.

## 구조 (Windows 2000 ~ 7)

아래 구조는 Windows 2000, XP, 2003, Vista, 7 의 것입니다 [3].
Windows 8 이후 형식은 공개된 형식 문서에 아직 정리되어 있지 않습니다 [3].

### 서명

파일 오프셋 0 의 4바이트는 서명 (Signature) 입니다 [3].
서명을 보면 파일 상태를 알 수 있습니다.

| 서명 | 뜻 |
|---|---|
| `hibr` | 유효한 파일 (XP 이하) |
| `HIBR` | 유효한 파일 (Vista 이상) |
| `wake` | 무효한 파일 (XP 이하) |
| `WAKE` | 무효한 파일 (Vista 이상) |
| `RSTR` | 복원(깨어나기) 중인 상태 |

### 헤더

모든 버전에 공통인 필드는 아래와 같습니다 [3].

| 오프셋 | 크기 (바이트) | 내용 |
|---|---|---|
| 0 | 4 | 서명 |
| 4 | 4 | 이미지 종류. Windows 7 64비트에서는 9 입니다 |
| 8 | 4 | 체크섬 |
| 12 | 4 | 크기 |
| 20 | 4 | 페이지 크기. 모든 버전에서 4096 입니다 |

시스템 시각 (System time) 필드는 8바이트 FILETIME 이고 [3], 이 필드의 위치는 버전마다 다릅니다.
바로 뒤 8바이트는 인터럽트 시각 (Interrupt time) 입니다.

| Windows 버전 | 시스템 시각 오프셋 | 헤더 크기 |
|---|---|---|
| 2000 SP4 (32비트) | 32 | 96 바이트 |
| XP·2003 (32비트) | 32 | 168 바이트 |
| XP·2003 (64비트) | 32 | 192 바이트 |
| Vista SP0·7 (32비트) | 24 | 224 바이트 |
| 7 (64비트) | 32 | 296 바이트 |

Vista 64비트 값은 실제 파일로 확인해야 합니다 [3].

최대 절전이 켜져 있어도 실제로 들어가지 않고 보통 종료했다면 헤더 페이지 전체가 0 일 수 있습니다 [3].

### 압축 블록

메모리 페이지는 압축 블록에 들어 있습니다 [3].

| 블록 안 오프셋 | 크기 (바이트) | 내용 |
|---|---|---|
| 0 | 8 | 서명 `\x81\x81xpress` |
| 8 | 1 | 블록에 든 페이지 수 − 1 |
| 9 | 4 | (압축 크기 × 4) − 1 |
| 13 | 19 | 뜻을 알 수 없는 값 |
| 32 | — | LZ XPRESS 로 압축한 자료 |

- 블록 끝은 8바이트 단위로 맞춥니다 [3].
- XPRESS 압축을 푸는 법은 [윈도 압축 형식](../../../01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md) 에 있습니다.
- Windows 8 이후로는 압축 방식과 구조가 바뀌었다고 알려져 있어, 위 표를 그대로 대지 않습니다.

## 헥스로 따라가기

아래는 위 필드 정의로 만든 예시입니다 [3].
실제 파일에서 뜬 값이 아니며 Windows 7 64비트 파일을 가정했습니다. `xx` 는 파일마다 다른 바이트입니다.
x86·x64 에서 정수는 낮은 자리 바이트부터 적습니다 (리틀 엔디언, Little-endian).

```
오프셋     00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
00000000   48 49 42 52 09 00 00 00  xx xx xx xx xx xx xx xx   HIBR....
00000010   xx xx xx xx 00 10 00 00  xx xx xx xx xx xx xx xx
00000020   xx xx xx xx xx xx xx xx  xx xx xx xx xx xx xx xx
```

1. 0x00~0x03 의 `48 49 42 52` 는 ASCII 로 `HIBR` 입니다. Vista 이상에서 만든 유효한 파일입니다.
2. 0x04~0x07 의 `09 00 00 00` 은 9 입니다. Windows 7 64비트의 이미지 종류 값입니다.
3. 0x08~0x0B 는 체크섬 필드입니다.
4. 0x0C~0x0F 는 크기 필드입니다.
5. 0x14~0x17 의 `00 10 00 00` 은 0x1000, 곧 4096 입니다. 페이지 크기 필드입니다.
6. 0x20~0x27 은 시스템 시각입니다. 8바이트 FILETIME 으로 읽습니다. 읽는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에 있습니다.
7. 0x28~0x2F 는 인터럽트 시각입니다.

첫 4바이트가 모두 `00` 이면 헤더 페이지가 비어 있는 파일일 수 있으며, 앞 절에서 본 "최대 절전에 들어가지 않고 보통 종료한 경우" 를 떠올립니다.

압축 블록은 아래 바이트로 시작하므로, 파일에서 이 바이트열을 찾으면 블록이 시작하는 곳을 찾을 수 있습니다.

```
블록 안 오프셋  00 01 02 03 04 05 06 07  08 09 0A 0B 0C
+00            81 81 78 70 72 65 73 73  nn ss ss ss ss
```

- `78 70 72 65 73 73` 은 ASCII 로 `xpress` 입니다.
- `nn` 은 블록에 든 페이지 수에서 1 을 뺀 값입니다.
- `ss ss ss ss` 는 (압축 크기 × 4) − 1 값이 든 필드입니다.
- 압축 자료는 블록 안 오프셋 32 (0x20) 부터 나옵니다.

## 시각 해석

헤더의 시스템 시각은 FILETIME 값이지만 이 필드의 뜻을 설명한 공개 문서가 없으므로 [3], 이 값을 최대 절전에 들어간 시각이라고 단정하지 않습니다.
이 값이 UTC 인지 현지 시각인지도 알려져 있지 않습니다.
이 값을 쓰려면 PC 가 꺼진 기록과 맞대 봅니다. [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) 과 [PC 사용 시간 재구성](../../../04-scenarios/activity/system-usage-time.md) 을 봅니다.
파일 시스템에 남은 hiberfil.sys 의 시각도 함께 적으며, 이 시각이 무엇에 따라 바뀌는지는 [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) 에 있습니다.

## 절차

1. 디스크 이미지에서 hiberfil.sys 를 찾아 꺼냅니다. 꺼낸 도구·방법과 해시를 적습니다. 방법은 [증거 획득](../../process-acquisition/evidence-acquisition/index.md) 에 있습니다.
2. 운영체제 버전을 확인합니다. [시스템 기본 정보](../../../02-artifacts/system-account/os-version-computer-name-install-date-shutdown-t.md) 를 봅니다.
3. Windows 2000 ~ 7 이면 위 구조를 그대로 댑니다. Windows 8 이후라면 쓰는 도구가 그 버전을 지원하는지 먼저 확인합니다.
4. SYSTEM 하이브의 Power 키에서 HiberFileSizePercent 를 읽습니다. full 인지 reduced 인지 추정합니다.
5. 첫 4바이트 서명을 봅니다. 헤더 페이지가 모두 0 인지도 봅니다.
6. 헤더의 시스템 시각을 읽어 적습니다. 뜻은 켜짐·꺼짐 기록과 맞대 본 뒤에 정합니다.
7. 도구로 압축 블록을 풀어 메모리 이미지처럼 엽니다.
8. 풀어 낸 내용에서 프로세스·연결·문자열을 봅니다. 방법은 [프로세스와 DLL 분석](process-analysis.md), [메모리 속 네트워크 흔적](network-artifacts.md), [메모리 속 문자열·자격증명·암호 키](strings-credentials-keys.md) 에 있습니다.
9. 켜진 PC 에서 뜬 메모리 이미지가 있으면 둘을 비교합니다. 두 파일은 서로 다른 시점의 메모리입니다.

## 도구

아래 도구는 예로만 듭니다.

| 도구 | 쓰임 |
|---|---|
| libhibr (libyal, 공개) | hiberfil.sys 형식 문서를 낸 프로젝트입니다 [3] |
| Volatility 3 (공개) | Windows 플러그인 목록에는 이름에 hibernation 이 든 플러그인이 없습니다 [4]. 이 파일을 읽을 수 있는지는 쓰는 버전의 도움말로 확인합니다 |
| 헥스 편집기 | 서명과 헤더 필드를 직접 봅니다 |

## 함정과 한계

- **형식 문서는 Windows 7 까지만 다룹니다** [3]. Windows 8 이후 파일에 위 오프셋을 그대로 대지 않습니다.
- **빠른 시작 파일에는 사용자 프로그램 메모리가 없을 수 있습니다.** 빠른 시작은 사용자 세션을 로그오프한 뒤 커널 메모리 이미지를 저장합니다 [1].
- **서명이 무효라고 해서 쓸모없는 파일로 단정하지 않습니다.** 깨어난 뒤 Windows 10·11 이 헤더를 지우거나 서명을 바꾸는지를 설명한 공개 문서는 없습니다. 파일 안에서 압축 블록 서명을 따로 찾아봅니다.
- **문서 안에 서로 어긋나는 문장이 있습니다.** powercfg 문서의 `/size` 설명에는 "기본 크기는 50 보다 작을 수 없다" 는 문장이 있습니다 [2]. 같은 문서는 40 이상이면 full 로 본다고도 적습니다 [2]. 크기 비율 하나로 full·reduced 를 단정하지 않습니다.
- **헤더 시각의 뜻은 알려져 있지 않습니다.** 필드 이름만 있습니다 [3]. 다른 기록과 맞대 보기 전에는 보고서에 "최대 절전에 들어간 시각" 으로 쓰지 않습니다.

## 결과를 어떻게 해석하나

증명하는 것은 아래와 같습니다.

- 파일에서 풀어 낸 내용은 Windows 가 이 파일을 쓴 시점에 메모리에 있던 내용입니다.
- 서명이 유효하면 이 PC 가 최대 절전이나 빠른 시작으로 꺼진 적이 있다고 볼 수 있습니다.

증명하지 못하는 것은 아래와 같습니다.

- 헤더만으로는 파일을 쓴 정확한 시각을 정할 수 없습니다. 시스템 시각 필드의 뜻이 알려져 있지 않습니다.
- 빠른 시작 파일에 사용자 프로그램의 흔적이 없다고 해서 그 프로그램을 쓰지 않았다는 뜻은 아닙니다.
- 이 파일만으로는 그때 PC 를 쓴 사람을 알 수 없습니다. [그 시각에 PC 를 쓴 사람이 누구인가](../../../04-scenarios/activity/user-attribution.md) 를 봅니다.

보고서 문장 예입니다.

- 쓰지 않을 문장: "피조사자가 ○○ 시각에 PC 를 최대 절전으로 바꿨습니다."
- 쓸 문장: "디스크 이미지의 hiberfil.sys (SHA-256 ○○) 첫 4바이트는 `HIBR` 입니다. 헤더의 시스템 시각 필드 값은 ○○ 입니다. 형식 문서에 이 필드의 뜻 설명이 없어, 켜짐·꺼짐 이벤트와 맞대 본 결과를 함께 적습니다. 파일에서 풀어 낸 내용에 ○○ 가 있습니다. 이 기록은 Windows 가 이 파일을 쓴 시점에 이 내용이 메모리에 있었음을 보여 줍니다."

## 함께 볼 페이지

- [메모리 덤프 확보](memory-acquisition.md) — 켜진 PC 에서 메모리를 뜨는 절차입니다.
- [페이지 파일](pagefile-sys-swapfile-sys.md) · [크래시 덤프](memory-dmp-minidump.md) — 디스크에 남는 다른 메모리 조각입니다.
- [윈도 압축 형식](../../../01-foundations/value-decoding/lznt1-xpress-xpress-huffman.md) — 압축 블록을 푸는 법입니다.
- [켜짐·꺼짐](../../../02-artifacts/event-logs/power-on-off-events.md) — 최대 절전·빠른 시작을 쓴 시점을 맞대 봅니다.

## 참고 문헌

1. Microsoft Learn, "Distinguishing Fast Startup from Wake-from-Hibernation" (2025-02-21) — https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/distinguishing-fast-startup-from-wake-from-hibernation
2. Microsoft Learn, "Powercfg command-line options" (2017-10-27, 갱신 2021-12-15) — https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options
3. Joachim Metz, "Windows Hibernation File (hiberfil.sys) format", libyal/libhibr documentation — https://github.com/libyal/libhibr/blob/main/documentation/Windows%20Hibernation%20File%20(hiberfil.sys)%20format.asciidoc
4. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
