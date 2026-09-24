---
title: "경로 해시로 실행 위치 구분하기"
parent: "프리페치"
grand_parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 830
---

# 경로 해시로 실행 위치 구분하기 (Path Hash)

> 상위 허브: [프리페치 (Prefetch)](index.md)

## 한 줄 요약

프리페치 파일 이름 끝의 16진수 8자리는 실행 파일의 경로로 계산한 해시입니다. 이름이 같은 프로그램이라도 실행한 위치가 다르면 `.pf` 파일이 따로 생깁니다. 후보 경로로 해시를 다시 계산하면 어느 위치에서 실행했는지 맞춰 볼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

프리페치 파일 이름은 `<실행 파일 이름>-<경로 해시>.pf` 꼴이며, 예를 들면 `NOTEPAD.EXE-189578DA.pf` 입니다. 이름은 보통 대문자로 적고, 실행 파일 이름은 29자까지만 남습니다.

경로 해시 (Path Hash)는 실행 파일의 전체 경로로 계산한 32비트 값입니다. 파일 이름에는 이 값을 16진수 8자리로 적습니다. 프리페처 (Prefetcher)는 해시가 다르면 다른 프로그램으로 보고 파일을 따로 만듭니다. 그래서 같은 `notepad.exe` 라도 다른 폴더나 다른 볼륨에서 실행하면 `.pf` 가 하나 더 생깁니다.

분석에서는 이 성질로 이름은 같지만 다른 위치에서 실행된 프로그램을 가려내고, `svchost.exe` 처럼 시스템 파일 이름을 흉내 내어 다른 폴더에서 실행한 파일을 찾아냅니다.

> 그림 자리: 이름이 `NOTEPAD.EXE` 로 같고 해시만 다른 `.pf` 파일 세 개와, 각 파일이 가리키는 실행 경로를 선으로 잇는 그림

## 해시를 계산하는 방법

### 해시 입력 만들기

형식 명세(libyal)가 적은 순서는 다음과 같습니다.

1. 실행 파일의 전체 경로를 구합니다. 예: `C:\Windows\notepad.exe`
2. 드라이브 문자를 볼륨의 장치 경로 (Device Path)로 바꾸고, 전체를 대문자로 씁니다. 예: `\DEVICE\HARDDISKVOLUME1\WINDOWS\NOTEPAD.EXE`
3. UTF-16LE 바이트열로 바꿉니다. 바이트 순서 표시(BOM)와 끝의 0 두 바이트는 넣지 않습니다.
4. 윈도 버전에 맞는 해시 함수에 넣습니다.

장치 경로는 드라이브 문자가 가리키는 커널 쪽 이름입니다. 윈도는 `C:` 같은 이름을 `\Device\HarddiskVolume1` 같은 장치 이름에 연결해 둡니다. 실행 중인 시스템에서는 `QueryDosDevice` API 로 이 연결을 조회할 수 있습니다.

해시 입력에는 드라이브 문자가 아니라 볼륨 번호가 들어갑니다. 그래서 같은 폴더의 같은 파일이라도 볼륨 번호가 다르면 해시가 달라집니다.

네트워크 공유에서 실행하면 입력이 달라지는데, Windows XP 실험에서는 매핑한 드라이브의 파일을 실행했을 때 `\DEVICE\LANMANREDIRECTOR\<서버>\<공유>\...` 꼴 경로로 해시를 계산했고, 가상 머신의 공유 폴더에서는 `\DEVICE\HGFS\...` 꼴이었습니다. (확인 범위: Windows XP, Hexacorn 실험)

### 버전별 해시 함수

| Windows | 프리페치 형식 버전 | 해시 함수 (명세의 이름) | 비고 |
|---|---|---|---|
| XP·Server 2003 | 17 | SCCA XP | 마지막에 314159269 를 곱하고 1000000007 로 나눈 나머지를 씁니다 |
| Vista | 23 | SCCA Vista | |
| 7 | 23 | SCCA 2008 | 결과는 Vista 함수와 같습니다 |
| 8·8.1 | 26 | SCCA 2008 | 결과는 Vista 함수와 같습니다 |
| 10 | 30 | SCCA Vista | |
| 11 | 31 | 명세에 적혀 있지 않습니다 | Vista 함수로 맞았습니다 (확인 범위: Windows 11 빌드 26200 한 대) |

명세는 Server 2008 도 SCCA 2008 함수를 쓴다고 적었습니다.

명세는 SCCA Vista 함수와 SCCA 2008 함수를 따로 적지만 두 함수는 같은 값을 냅니다. SCCA 2008 함수는 Vista 함수를 8바이트씩 묶어 풀어 쓴 형태입니다. 함수 안의 상수 442596621 은 37의 7제곱을 2³²로 나눈 나머지입니다. 상수 803794207 을 곱해 빼는 것은 37의 8제곱을 곱해 더하는 것과 2³² 나머지로 같습니다. 이 글을 쓰며 두 함수에 무작위 입력 1,000개를 넣어 결과가 모두 같은 것을 확인했습니다. 따라서 Vista 이후 버전은 한 계산식으로 다뤄도 됩니다. XP·2003 의 값은 이와 다릅니다.

Windows 11 에서는 시스템 폴더의 실행 파일 여덟 개로 확인했습니다. 파일 이름의 해시와 Vista 함수로 계산한 값이 모두 같았습니다. (확인 범위: Windows 11 빌드 26200 한 대, `\DEVICE\HARDDISKVOLUME3` 기준)

### 호스팅 프로그램은 명령줄도 넣는다

`rundll32.exe`, `mmc.exe` 같은 호스팅 프로그램 (Hosting Application)은 다른 코드를 불러 실행하는 프로그램입니다. 이런 프로그램은 명령줄까지 해시에 넣고, 새 버전 윈도는 `dllhost.exe`, `svchost.exe` 도 여기에 넣습니다. 일반 프로그램은 명령줄을 해시에 넣지 않아서 `notepad.exe` 와 `notepad.exe 1.txt` 는 같은 `.pf` 에 기록됩니다.

호스팅 프로그램의 해시는 두 값을 더해 만듭니다.

1. 장치 경로로 계산한 해시
2. 실행할 때 쓴 경로와 명령줄을 이어 붙여 계산한 해시

두 값을 더하고 32비트를 넘는 부분은 버립니다. 두 번째 입력은 대문자로 바꾸지 않으므로 명령줄의 대소문자 하나, 공백 하나만 달라도 해시가 달라지며, 버전마다 두 번째 입력의 모양도 다릅니다. XP·Vista·Windows 7 32비트는 경로를 따옴표로 감쌉니다. Windows 7 64비트·Server 2008 은 따옴표 없이 경로 뒤에 공백을 하나 더 붙입니다. Hexacorn 이 공개한 `rundll32.exe` 예시 값 세 개(XP·Windows 7 32비트·Windows 7 64비트)를 명세의 함수로 다시 계산해 같은 값을 얻었습니다.

이 글을 쓰며 확인한 Windows 11 한 대에는 `SVCHOST.EXE-*.pf` 가 수십 개, `DLLHOST.EXE-*.pf` 와 `RUNDLL32.EXE-*.pf` 가 각각 열 개 넘게 있었습니다. (확인 범위: Windows 11 빌드 26200 한 대)

`/prefetch:<숫자>` 옵션도 해시를 바꿉니다. 명세와 Hexacorn 이 인용한 Microsoft 개발자 블로그 글은 이 숫자를 해시에 더한다고 적었으며, 한 프로그램이 여러 용도로 쓰일 때 용도마다 `.pf` 를 따로 두려는 기능입니다. 명세는 Windows 10 1903·2004 에서 0~8 만 반영되고 9 이상은 0 과 같게 처리된다고 적었습니다.

## 파일 안에 적힌 해시

해시는 파일 이름뿐 아니라 파일 헤더에도 있습니다. 헤더의 자리는 다음과 같습니다. 파일 구조 전체는 [파일 구조와 버전](format-versions-mam.md)을 봅니다.

| 오프셋 | 크기 | 내용 |
|---|---|---|
| 0 (0x00) | 4 | 형식 버전 |
| 4 (0x04) | 4 | 시그니처 `SCCA` |
| 16 (0x10) | 60 | 실행 파일 이름 (UTF-16LE, 끝에 0) |
| 76 (0x4C) | 4 | 경로 해시 (리틀 엔디언, Little-endian) |

명세는 오프셋 76 의 값이 파일 이름의 해시와 같아야 한다고 적었습니다. Windows 10 부터는 `.pf` 가 MAM 형식으로 압축되어 있어서 압축을 풀어야 이 헤더가 보입니다.

`.pf` 안의 볼륨 정보에는 볼륨 장치 경로 문자열도 있습니다. Windows 10 은 이 문자열을 `\VOLUME{...}` 꼴로 적지만, 명세는 해시를 `\DEVICE\HARDDISKVOLUME<번호>` 로 계산하는 것으로 보인다고 적었습니다. 따라서 Windows 10 이후에는 `.pf` 안의 문자열만으로 볼륨 번호를 알 수 없습니다.

## 증거로서 의미

**증명하는 것**

- 같은 실행 파일 이름으로 `.pf` 가 둘 이상 있으면, 해시 입력이 서로 달랐다는 뜻입니다. 즉 경로가 달랐거나, 호스팅 프로그램의 명령줄이 달랐거나, `/prefetch` 값이 달랐습니다.
- 후보 경로로 계산한 값이 파일 이름의 해시와 같으면, 그 장치 경로에서 실행했다는 설명과 맞습니다.

**증명하지 못하는 것**

- 해시로 경로를 되돌려 구할 수 없습니다. 후보를 넣어 맞춰 보는 방법뿐입니다.
- 해시는 32비트입니다. 서로 다른 경로가 같은 값을 낼 수 있습니다. 해시 일치는 다른 기록과 함께 쓰는 근거입니다.
- 해시는 드라이브 문자를 알려 주지 않습니다. 볼륨 번호만 반영합니다.
- 해시는 경로로만 계산합니다. 같은 경로에 다른 파일을 두어도 해시는 같습니다. 파일 내용이 같은지는 해시로 알 수 없습니다.
- 누가 실행했는지, 언제 실행했는지는 해시에 없습니다.

보고서에는 기록이 말하는 만큼만 씁니다. 예를 들면 "`<장치 경로>` 로 계산한 프리페치 해시가 `<파일 이름>` 의 해시와 같다. 이 프로그램이 해당 경로에서 실행되었다는 설명과 맞는다." 처럼 씁니다.

## 시각 해석

해시에는 시각이 없습니다. 대신 경로마다 `.pf` 가 따로 있어서 실행 횟수와 마지막 실행 시각도 경로마다 따로 쌓이고, 그래서 같은 이름의 프로그램을 어느 위치에서 언제 실행했는지 나누어 볼 수 있습니다. 시각을 읽는 법은 [실행 횟수와 실행 시각 읽기](run-count-last-run-times.md)를 봅니다. `.pf` 파일 자체의 만든 시각을 해석할 때 주의할 점은 [프리페치 해석 함정](pitfalls.md)을 봅니다.

## 함정과 한계

- **볼륨 번호를 짐작해야 합니다.** Windows 7 은 숨은 예약 파티션이 1번을 차지해서 `C:` 가 흔히 2번입니다. 예약 파티션이 없으면 1번입니다. 이 글을 쓰며 확인한 Windows 11 한 대에서는 `C:` 가 3번이었습니다. 번호를 모르면 1번부터 차례로 넣어 계산합니다.
- **같은 파일도 여는 길에 따라 해시가 다릅니다.** XP 실험에서 같은 파일을 `subst` 로 만든 드라이브에서 실행했을 때 대상 폴더를 로컬 경로로 적으면 원래 볼륨 경로가 쓰였습니다. 대상을 `\\127.0.0.1\c$` 로 적으면 `\DEVICE\LANMANREDIRECTOR\127.0.0.1\C$\...` 로 계산되었습니다. 이동식 저장 장치도 볼륨 번호가 다르면 해시가 다릅니다.
- **호스팅 프로그램은 미리 표를 만들기 어렵습니다.** 명령줄의 대소문자와 공백까지 반영되기 때문입니다. 증거 안에서 실제 명령줄을 찾아 그대로 넣어 계산합니다.
- **버전에 맞는 함수를 써야 합니다.** XP·2003 과 Vista 이후는 같은 경로에도 다른 값이 나옵니다.
- **영문 밖의 문자가 든 경로는 조심합니다.** 계산 도구의 대문자 변환이 윈도와 다르면 값이 맞지 않습니다. 계산이 안 맞을 때 먼저 의심할 부분입니다.
- **대체 데이터 스트림으로 실행하면 이름 규칙이 깨집니다.** 명세의 예에서는 `notepad.exe:evil.exe` 를 실행하자 `Prefetch` 폴더에 `notepad.exe:evil.pf` 가 생겼습니다. 해시가 붙은 이름이 아닙니다. 대체 데이터 스트림 (ADS)은 [대체 데이터 스트림](../../../01-foundations/disk-volume/ntfs/ads.md)을 봅니다.
- **파일 이름의 해시와 헤더의 해시가 다르면 따져 봅니다.** 명세상 두 값은 같아야 합니다. 다르면 파일 이름을 바꾼 것은 아닌지 확인할 단서로 씁니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시입니다. 실제 검체에서 뽑은 값이 아닙니다. XP 형식(버전 17) 헤더 84바이트이고, 파일 크기 칸(0x0C)은 0 으로 두었습니다.

```
00000000  11 00 00 00 53 43 43 41 0f 00 00 00 00 00 00 00  |....SCCA........|
00000010  4e 00 4f 00 54 00 45 00 50 00 41 00 44 00 2e 00  |N.O.T.E.P.A.D...|
00000020  45 00 58 00 45 00 00 00 00 00 00 00 00 00 00 00  |E.X.E...........|
00000030  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  |................|
00000040  00 00 00 00 00 00 00 00 00 00 00 00 da 78 95 18  |.............x..|
00000050  00 00 00 00                                      |....|
```

1. 0x00 의 `11 00 00 00` 은 형식 버전 17 입니다.
2. 0x04 의 `53 43 43 41` 은 `SCCA` 입니다.
3. 0x10 부터 UTF-16LE 로 `NOTEPAD.EXE` 가 적혀 있습니다.
4. 0x4C 의 `da 78 95 18` 을 리틀 엔디언으로 읽으면 `0x189578DA` 입니다.
5. 이 값은 파일 이름 `NOTEPAD.EXE-189578DA.pf` 의 해시와 같습니다.

해시 입력 `\DEVICE\HARDDISKVOLUME1\WINDOWS\NOTEPAD.EXE` 를 UTF-16LE 로 바꾸면 `5c 00 44 00 45 00 56 00 ...` 로 시작합니다. 이 바이트열을 XP 함수에 넣으면 `0x189578DA` 가 나옵니다. 명세가 든 예시 값과 같습니다.

### 계산 코드로 한 번

명세의 함수를 짧게 옮기면 다음과 같습니다. 호스팅 프로그램의 명령줄 해시는 넣지 않았습니다.

```python
def pf_hash_vista(path):   # Vista 이후 (7·8·10, Windows 11 관찰 포함)
    h = 314159
    for b in path.upper().encode("utf-16-le"):
        h = (h * 37 + b) & 0xFFFFFFFF
    return h

def pf_hash_xp(path):      # XP·2003
    h = 0
    for b in path.upper().encode("utf-16-le"):
        h = (h * 37 + b) & 0xFFFFFFFF
    h = (h * 314159269) & 0xFFFFFFFF
    if h > 0x80000000:
        h = 0x100000000 - h
    return h % 1000000007

print("%08X" % pf_hash_xp(r"\DEVICE\HARDDISKVOLUME1\WINDOWS\NOTEPAD.EXE"))  # 189578DA

# 볼륨 번호를 모를 때: 1번부터 넣어 파일 이름의 해시와 비교한다
target, rel = "D8414F97", r"\WINDOWS\SYSTEM32\NOTEPAD.EXE"
for n in range(1, 9):
    if "%08X" % pf_hash_vista(r"\DEVICE\HARDDISKVOLUME%d" % n + rel) == target:
        print("볼륨", n)   # 볼륨 2
```

아래 값은 이 코드로 계산한 예입니다. 검체에서 나온 값이 아닙니다. 폴더가 다르거나 볼륨 번호만 달라도 해시가 달라지는 것을 볼 수 있습니다.

| 해시 입력 (장치 경로) | Vista 이후 해시 |
|---|---|
| `\DEVICE\HARDDISKVOLUME2\WINDOWS\SYSTEM32\NOTEPAD.EXE` | `D8414F97` |
| `\DEVICE\HARDDISKVOLUME3\WINDOWS\SYSTEM32\NOTEPAD.EXE` | `C5670914` |
| `\DEVICE\HARDDISKVOLUME3\USERS\PUBLIC\NOTEPAD.EXE` | `19E20D58` |

### 공개 도구로 한 번

libyal 의 libscca, Eric Zimmerman 의 PECmd 같은 공개 파서는 `.pf` 를 풀어 실행 파일 이름과 참조 파일 목록을 보여 줍니다. Hexacorn 이 공개한 `prefhashcalc.pl` 에는 버전별 계산식과 호스팅 프로그램 계산이 들어 있습니다. 도구 하나의 결과만 믿지 말고, 헤더의 해시·파일 이름의 해시·직접 계산한 값을 서로 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 프리페치 참조 파일 목록 | `.pf` 안에 실행 파일의 전체 경로가 남습니다. 해시 계산에 넣을 첫 후보입니다 | [참조 파일·폴더 목록 활용](referenced-files.md) |
| BAM·DAM | 경로를 `\Device\HarddiskVolume<번호>\...` 꼴로 적습니다(확인 범위: Windows 11 빌드 26200). 볼륨 번호 단서입니다 | [BAM·DAM](../background-activity-moderator.md) |
| AmCache | 실행 파일의 전체 경로와 SHA1 이 남습니다. 그 경로에 어떤 파일이 있었는지 봅니다 | [실행 파일 항목](../amcache-hve/inventoryapplicationfile.md) |
| 심캐시 | 전체 경로가 남습니다 | [심캐시](../shimcache-appcompatcache.md) |
| 프로세스 생성 이벤트 | 명령줄이 남습니다. 호스팅 프로그램 해시 계산에 넣습니다 | [프로세스 생성 (4688)](../../event-logs/4688.md), [Sysmon 이벤트 1](../../event-logs/sysmon/1.md) |
| $MFT | 후보 경로에 그 파일이 있었는지 봅니다 | [마스터 파일 테이블](../../filesystem/mft.md) |
| MountedDevices | 드라이브 문자가 어느 볼륨이었는지 봅니다 | [드라이브 문자 매핑](../../external-devices/usb-storage-artifacts/mounteddevices.md) |

## 실습

Windows 7 이후 공개 검체(NIST CFReDS 등)에서 `Prefetch` 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. 실행 파일 이름이 같은데 `.pf` 가 둘 이상인 프로그램을 모두 찾습니다.
2. 각 `.pf` 의 참조 파일 목록에서 실행 파일 경로를 찾습니다. 그 경로로 해시를 계산해 파일 이름과 맞춰 봅니다. 볼륨 번호가 몇 번일 때 맞습니까?
3. 파일 이름의 해시와 헤더 오프셋 76 의 해시가 같은지 확인합니다.
4. `svchost.exe` 처럼 시스템 파일 이름인데 시스템 폴더 밖에서 실행된 기록이 있습니까?
5. `RUNDLL32.EXE` 의 `.pf` 하나를 골라, 이벤트 로그에서 찾은 명령줄로 해시를 맞춰 볼 수 있습니까?

## 참고 문헌

1. libyal, *Windows Prefetch File (PF) format* (libscca 문서). https://github.com/libyal/libscca/blob/main/documentation/Windows%20Prefetch%20File%20(PF)%20format.asciidoc
2. Hexacorn, *Prefetch Hash Calculator + a hash lookup table xp/vista/w7/w2k3/w2k8* (2012). https://www.hexacorn.com/blog/2012/06/13/prefetch-hash-calculator-a-hash-lookup-table-xpvistaw7w2k3w2k8/
3. Hexacorn, *Prefetch file names and UNC paths* (2012). https://www.hexacorn.com/blog/2012/10/29/prefetch-file-names-and-unc-paths/
4. TrustedSec, *Prefetch: The Little Snitch That Tells on You*. https://trustedsec.com/blog/prefetch-the-little-snitch-that-tells-on-you
5. Microsoft Learn, *QueryDosDeviceW function (fileapi.h)*. https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-querydosdevicew
