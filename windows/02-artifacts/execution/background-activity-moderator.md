---
title: "BAM·DAM"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 950
---

# BAM·DAM (Background Activity Moderator)

## 한 줄 요약

Windows 10 1709 무렵부터 SYSTEM 하이브의 `Services\bam` 키 아래에 사용자 SID 마다 실행 파일 경로와 시각 하나가 남습니다. 시각은 프로세스가 만들어질 때와 끝날 때 바뀝니다. dfir.ru 에 따르면 부팅 때 7일이 지난 항목은 지워집니다.

## 무엇을 기록하나 · 왜 생기나

BAM (Background Activity Moderator) 은 커널 드라이버입니다. Windows 11 PC 한 대에서 드라이버 파일은 `%SystemRoot%\System32\drivers\bam.sys`, 설명은 "BAM Kernel Driver" 였습니다. (확인 범위: Win11 25H2 한 대) 같은 PC 에는 짝을 이루는 DAM 드라이버 `dam.sys`(설명 "DAM Kernel Driver")도 있었습니다. (확인 범위: Win11 25H2 한 대)

libyal 에 따르면 `UserSettings` 키 아래에 사용자 SID 마다 하위 키가 있고, 하위 키에는 추적한 실행 파일마다 값이 하나씩 있습니다. 값 하나에는 실행 파일 경로(값 이름)와 시각(값 데이터)이 들어 있습니다. 드라이버가 이 기록을 어떤 목적으로 남기는지는 이번에 연 자료에 나오지 않습니다.

## 위치와 버전별 차이

| 경로 | 비고 |
|---|---|
| `HKLM\SYSTEM\CurrentControlSet\Services\bam\UserSettings\{SID}` | libyal 이 적은 경로 |
| `HKLM\SYSTEM\CurrentControlSet\Services\bam\State\UserSettings\{SID}` | libyal 이 적은 경로. Windows 11 PC 한 대에는 이 경로만 있었습니다 (확인 범위: Win11 25H2 한 대) |

- libyal 은 BAM 키가 Windows 10 1709 이후에 생긴 것으로 "보인다" 고 적습니다. 도입 버전을 단정하지 않습니다.
- 어느 빌드부터 `State` 가 붙는지는 확인하지 못했습니다. 두 경로를 모두 확인합니다.
- 오프라인 하이브에서는 `CurrentControlSet` 대신 `ControlSet00X` 아래에서 찾습니다. 이 점은 [심캐시](shimcache-appcompatcache.md) 의 위치 절에서 다룹니다.
- 보존 기간을 바꾸는 설정 값이 있습니다. dfir.ru 는 `\REGISTRY\MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\BAM` 키의 `UserSettingsLifetimeMs` 값을 듭니다. Windows 11 PC 한 대에는 이 `Session Manager\BAM` 키가 없었습니다. (확인 범위: Win11 25H2 한 대)
- DAM 의 레지스트리 경로와 값 구조는 이번에 연 자료 어디에도 없습니다. Windows 11 PC 한 대의 `Services\dam` 키에는 `PowerEvents` 하위 키 하나만 있었습니다. `dam\State\UserSettings` 는 없었습니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 에서 `bam`·`dam` 서비스는 둘 다 Type=1(커널 드라이버), Start=1(System) 이었고 실행 중이었습니다. 서비스 키 읽는 법은 [서비스·드라이버](../persistence/services-drivers.md) 에서 다룹니다. (확인 범위: Win11 25H2 한 대)

하이브 파일의 구조와 수집 방법은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

```
...\Services\bam\State\UserSettings\
    {SID}\
        Version          REG_DWORD
        SequenceNumber   REG_DWORD
        \Device\HarddiskVolume1\Windows\System32\WindowsPowerShell\v1.0\powershell.exe   REG_BINARY 24바이트
        <패키지 패밀리 이름>                                                          REG_BINARY 24바이트
```

- 값 이름은 드라이브 문자가 아니라 장치 경로 (device path) 입니다. 위 예는 libyal 이 든 값 이름입니다.
- Windows 11 PC 한 대에서는 패키지 앱 항목의 값 이름이 `이름_게시자ID` 형태의 패키지 패밀리 이름 (package family name) 이었습니다. (확인 범위: Win11 25H2 한 대)

**값 데이터 (24바이트, REG_BINARY)**

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 | 8 | 시각 (FILETIME) |
| 8 | 8 | 알 수 없음 (빈 값) |
| 16 | 4 | "Windows app" 인지 나타내는 플래그 |
| 20 | 4 | 알 수 없음 (항상 2) |

- 표는 libyal 의 정리이고, dfir.ru 도 값이 24바이트(0x18) REG_BINARY 이며 앞 8바이트가 FILETIME 이라고 적습니다.
- Windows 11 PC 한 대에서 실행 파일 경로 항목은 오프셋 16 이 0, 패키지 앱 항목은 1 이었습니다. 오프셋 20 은 모두 2, 오프셋 8~15 는 모두 0 이었습니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 의 SID 키마다 DWORD 값 `Version`(모두 1)과 `SequenceNumber`(키마다 다름, 624~4886)가 있었습니다. 두 값의 뜻은 확인하지 못했습니다. (확인 범위: Win11 25H2 한 대)
- 같은 PC 의 `UserSettings` 아래에는 SID 키가 네 개 있었습니다. `S-1-5-18` 하나, 로컬 계정 `S-1-5-21-…` 두 개, `S-1-5-90-0-…` 하나입니다. `S-1-5-90-0` 계정의 뜻은 확인하지 못했습니다. (확인 범위: Win11 25H2 한 대)

SID 의 짜임과 잘 알려진 SID 는 [윈도 식별자 형식](../../01-foundations/value-decoding/sid-guid-clsid-known-folder-id.md) 에서, SID 를 계정 이름과 잇는 방법은 [사용자 프로필 목록](../system-account/profilelist.md) 에서 다룹니다.

## 증거로서 의미

### 증명하는 것

- 이 SID 키에 이 경로의 값이 있으면, BAM 이 그 계정 문맥에서 그 실행 파일을 추적한 기록이 있습니다.
- dfir.ru 실험에서 값의 시각은 프로세스가 만들어질 때와 끝날 때 바뀌었습니다. 그래서 시각이 있으면 그 무렵에 그 실행 파일의 프로세스가 있었다고 읽습니다.
- 값 이름이 경로이므로, 그 시점에 프로그램이 어느 볼륨의 어느 폴더에 있었는지 알 수 있습니다.

### 증명하지 못하는 것

- **처음 실행한 때와 실행 횟수.** 값마다 시각이 하나뿐입니다.
- **시각이 시작인지 끝인지.** 프로세스를 만들 때와 끝낼 때 모두 바뀝니다. 한 번 실행하는 동안에도 여러 번 바뀔 수 있습니다.
- **기록되지 않는 실행.** dfir.ru 에 따르면 이동식 매체(FILE_REMOVABLE_MEDIA)와 네트워크 공유(FILE_REMOTE_DEVICE)의 실행 파일은 기록하지 않습니다. 명령줄 세션에서 띄운 콘솔 프로그램도 기록되지 않는 경우가 있었습니다. dfir.ru 도 이 동작은 더 살펴봐야 한다고 적습니다. 값이 없다고 실행하지 않은 것은 아닙니다.
- **7일보다 오래된 실행.** 부팅 때 오래된 항목이 지워집니다. 아래 "함정과 한계" 를 봅니다.
- **키보드 앞의 사람.** SID 가 가리키는 것은 계정입니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

보고서에는 "이 SID 의 BAM 키에 이 경로의 값이 있고, 값의 시각은 이 시각이다. 이 시각은 프로세스가 만들어지거나 끝날 때 바뀐다" 처럼 씁니다. "이 시각에 실행을 시작했다" 고 쓰지 않습니다.

## 시각 해석

- 오프셋 0 의 8바이트는 FILETIME 이고 UTC 로 읽습니다. 변환은 [시각 값 형식](../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- dfir.ru 실험은 빌드 19592·18363 에서 했습니다. 같은 글은 "It's too early to make conclusions about possible cases when the FILETIME timestamp can be updated" 라고 적습니다. 시각이 바뀌는 조건은 아직 다 밝혀지지 않았습니다.
- 부팅 때 지우는 규칙이 있으므로 시각은 마지막 부팅 시각과 함께 봅니다. 부팅 시각은 [켜짐·꺼짐](../event-logs/power-on-off-events.md) 에서 찾습니다.
- Windows 11 PC 한 대에서 실행 파일 경로 항목 44개는 모두 마지막 부팅 7일 전 이후의 시각이었습니다. 44개 가운데 39개는 마지막 부팅 뒤의 시각이었습니다. (확인 범위: Win11 25H2 한 대)

## 함정과 한계

- **부팅 때 7일이 지난 항목이 지워집니다.** dfir.ru 는 "BAM entries older than 7 days are removed during the boot" 라고 적습니다. 기본 보존 기간은 7일(604,800초)입니다. 수집 전에 재부팅하면 기록이 줄 수 있습니다. 켜진 PC 는 [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) 절차로 먼저 수집합니다.
- **한 번에 몇 개가 지워지는지는 모릅니다.** dfir.ru 도 이 점이 불분명하다고 적습니다.
- **7일 규칙이 모든 항목에 들어맞지는 않았습니다.** Windows 11 PC 한 대에서 패키지 앱 항목 13개는 마지막 부팅 7일 전보다 오래됐는데도 남아 있었습니다. 가장 오래된 것은 약 석 달 전 시각이었습니다. (확인 범위: Win11 25H2 한 대)
- **파일이 없으면 부팅 때 항목이 지워질 수 있습니다.** dfir.ru 는 여기에 특정 DWORD 가 0 일 때라는 조건을 붙입니다. 이번 조사에서는 그 조건을 정확히 확인하지 못했습니다. Windows 11 PC 한 대에서 실행 파일 경로 항목 44개는 모두 그 경로에 파일이 있었습니다. (확인 범위: Win11 25H2 한 대)
- **보존 기간 설정을 확인합니다.** `Session Manager\BAM` 의 `UserSettingsLifetimeMs` 로 보존 기간을 바꿀 수 있습니다. 이 값이 있으면 누가 언제 넣었는지 따로 봅니다. 조작 흔적을 찾는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.
- **장치 경로를 드라이브 문자로 바꿔야 합니다.** `\Device\HarddiskVolumeN` 이 어느 드라이브인지 맞추는 방법은 이번에 연 자료로 확인하지 못했습니다. 번호를 짐작으로 드라이브 문자에 붙이지 않습니다.
- **섀도 복사본 안의 프로그램도 기록됩니다.** dfir.ru 가 확인한 점입니다. 경로가 낯설면 섀도 복사본 안의 파일을 실행했는지 봅니다. 섀도 복사본 구조는 [볼륨 섀도 복사본 구조](../../01-foundations/disk-volume/volume-shadow-copy.md) 에서 다룹니다.
- **띄운 방법에 따라 기록 여부가 달라집니다.** dfir.ru 는 콘솔 프로그램을 PowerShell 에서 띄웠는지 직접 띄웠는지에 따라 결과가 달랐다고 적습니다.
- **DAM 은 아직 모르는 부분이 많습니다.** 경로와 값 구조를 확인한 자료가 없습니다. DAM 에서 실행 기록을 찾았다고 쓰려면 근거를 따로 세웁니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 24바이트는 libyal 명세로 만든 예시입니다. 특정 검체에서 꺼낸 값이 아닙니다.

```
00 C0 89 76 45 3C DA 01    오프셋 0   시각 (FILETIME)
00 00 00 00 00 00 00 00    오프셋 8   알 수 없음 (빈 값)
00 00 00 00                오프셋 16  "Windows app" 플래그 = 0
02 00 00 00                오프셋 20  알 수 없음 (2)
```

1. 앞 8바이트를 리틀 엔디언으로 읽으면 `0x01DA3C457689C000` 입니다.
2. FILETIME 으로 바꾸면 2024-01-01 00:00:00(UTC) 입니다. 이 시각은 프로세스가 만들어지거나 끝난 무렵입니다.
3. 오프셋 16 이 0 이므로 "Windows app" 이 아닌 항목으로 읽습니다. 값 이름도 장치 경로인지 봅니다.
4. 오프셋 20 이 2 인지 확인합니다. 다른 값이면 형식이 달라졌을 수 있으니 따로 기록해 둡니다.

### 공개 도구로 한 번

1. SYSTEM 하이브와 하이브 로그를 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 사본을 열고 쓸 `ControlSet00X` 를 고릅니다.
3. `Services\bam\UserSettings` 와 `Services\bam\State\UserSettings` 를 모두 엽니다.
4. SID 키마다 값 이름과 앞 8바이트 시각을 목록으로 뽑습니다. BAM 을 풀어 주는 공개 레지스트리 도구를 써도 됩니다.
5. 도구 결과의 한 줄을 골라 위 헥스 풀이대로 시각을 직접 한 번 바꿔 봅니다.
6. SID 를 계정 이름과 잇고, 시각을 마지막 부팅 시각과 나란히 놓습니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 심캐시 | 같은 경로의 파일이 시스템에 있었는지 봅니다 | [심캐시](shimcache-appcompatcache.md) |
| UserAssist | 같은 계정이 탐색기로 띄운 횟수와 마지막 실행 시각을 봅니다 | [UserAssist](userassist.md) |
| 작업표시줄 사용 기록 | 같은 계정이 작업 표시줄에서 그 앱을 다룬 횟수를 봅니다 | [작업표시줄 사용 기록](featureusage.md) |
| 프리페치 | 실행 횟수와 여러 번의 실행 시각을 봅니다 | [프리페치](prefetch/index.md) |
| 프로세스 생성 이벤트 | 프로세스 시작 시각을 이벤트로 확인합니다 | [프로세스 생성](../event-logs/4688.md) |
| 켜짐·꺼짐 | 7일 규칙을 적용할 마지막 부팅 시각을 찾습니다 | [켜짐·꺼짐](../event-logs/power-on-off-events.md) |
| USB 저장장치 흔적 | BAM 에 남지 않는 이동식 매체 실행을 다른 흔적으로 찾습니다 | [USB 저장장치 흔적](../external-devices/usb-storage-artifacts/index.md) |
| 공유 폴더·네트워크 드라이브 | BAM 에 남지 않는 네트워크 공유 실행을 다른 흔적으로 찾습니다 | [공유 폴더·네트워크 드라이브](../network/network-shares-mapped-drives.md) |
| PowerShell 명령 기록 | BAM 에 남지 않을 수 있는 콘솔 프로그램 실행을 봅니다 | [PowerShell 명령 기록](consolehost-history-txt.md) |
| 스토어 앱 설치 목록 | 패키지 패밀리 이름이 어떤 앱인지 봅니다 | [스토어 앱 설치 목록](../system-account/appx-staterepository.md) |

실행 흔적 전체를 엮는 흐름은 [어떤 프로그램을 언제 실행했나](../../04-scenarios/activity/program-execution.md) 에 있습니다.

## 실습

Windows 10 1709 이후 공개 검체(NIST CFReDS 등)의 SYSTEM 하이브로 아래 질문을 풀어 봅니다.

1. `bam\UserSettings` 와 `bam\State\UserSettings` 가운데 어느 쪽에 값이 있습니까?
2. SID 키는 몇 개입니까? 각 SID 는 어느 계정입니까?
3. 가장 오래된 값의 시각은 마지막 부팅보다 7일 넘게 앞섭니까? 그렇다면 그 값은 실행 파일 경로입니까, 패키지 앱입니까?
4. `\Device\HarddiskVolumeN` 경로가 어느 드라이브인지 다른 근거로 맞출 수 있습니까?
5. BAM 의 시각과 같은 실행 파일의 프리페치 실행 시각은 얼마나 차이 납니까?
6. `Session Manager\BAM` 키가 있습니까? 있다면 `UserSettingsLifetimeMs` 값은 얼마입니까?

## 참고 문헌

1. libyal, *winreg-kb: Background activity moderator (BAM)* (도입 시기, 두 경로, SID 하위 키, 장치 경로 값 이름, 24바이트 값 구조). https://raw.githubusercontent.com/libyal/winreg-kb/main/docs/sources/system-keys/Background-activity-moderator.md
2. Maxim Suhanov, *BAM internals*, dfir.ru, 2020-04-08 (값 크기, 시각이 바뀌는 때, 기록하지 않는 실행, 섀도 복사본, 7일 삭제와 `UserSettingsLifetimeMs`, 파일이 없을 때의 삭제). https://dfir.ru/2020/04/08/bam-internals/
