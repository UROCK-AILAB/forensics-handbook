---
title: "알려진 파일 대조와 YARA"
parent: "기법 · 분석"
nav_order: 1010
---

# 알려진 파일 대조와 YARA (Hash·YARA)

파일과 프로세스의 해시를 알려진 목록과 맞춰 정상 파일을 걸러 내고, 남은 파일과 메모리를 YARA 규칙으로 훑어 특정 바이트 패턴이 있는 곳을 찾는 방법입니다.

## 언제 쓰나

서버 한 대에도 실행 파일이 수만 개 있어서 하나씩 열어 볼 수는 없습니다. 해시 대조 (hash matching) 로 "배포판이 설치한 그대로인 파일" 과 "널리 알려진 정상 파일" 을 먼저 빼면 사람이 볼 파일이 크게 줄어듭니다. 그다음 YARA 규칙으로 남은 파일과 프로세스 메모리에서 이미 알려진 악성 코드의 문자열이나 바이트 배열을 찾습니다.

아래와 같은 때 씁니다.

- 채굴기·웹셸·백도어처럼 공개된 표본이나 규칙이 있는 위협이 들었는지 넓게 훑어볼 때
- 패키지가 설치한 시스템 파일(`/usr/bin`, `/usr/lib` 등)이 바뀌었는지 볼 때
- [루트킷 찾기](rootkit-detection.md)나 [메모리 분석](memory-analysis.md)에서 뽑아낸 모듈·실행 파일이 무엇인지 판별할 때
- 한 시스템에서 찾은 파일의 해시로 다른 시스템에도 같은 파일이 있는지 찾을 때

이 쪽은 대조 절차 전반을 다룹니다. dpkg·rpm 이 설치할 때 남긴 해시와 비교하는 방법, 그 출력 글자의 뜻은 [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md)에 있습니다. Windows 판의 같은 주제(서명 확인과 YARA)는 [의심 실행 파일 선별](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/code-signing-yara.html)에 있습니다.

## 절차

1. **무엇과 대조할지 정합니다.** 기준은 셋입니다. 첫째는 패키지 관리자가 설치할 때 기록한 해시이고, 같은 시스템 안에 들어 있습니다. 둘째는 알려진 정상 파일 목록(NSRL, CIRCL hashlookup 등)이고, 셋째는 알려진 악성 파일의 해시 목록과 YARA 규칙입니다. 앞의 둘은 빼는 데 쓰고, 셋째는 찾는 데 씁니다.

2. **해시를 모읍니다.** 디스크 이미지는 읽기 전용으로 붙인 뒤 계산합니다([디스크 이미징](../acquisition/disk-imaging.md)). 켜져 있는 시스템에서는 UAC 의 `hash_executables` 가 `/` 부터 내려가며 `proc` 파일 시스템을 빼고, 소유자·그룹·기타 가운데 하나라도 실행 비트가 선 일반 파일(`permissions` 값 `-001`, `-010`, `-100`)의 해시를 떠서 `/hash_executables` 폴더에 둡니다[1]. `hash_running_processes` 는 Linux 에서 `/proc/[0-9]*/exe`, 곧 실행 중인 프로세스의 실행 파일 해시를 뜹니다[1]. UAC 해시 수집기의 알고리즘은 설정 파일 `config/uac.conf` 의 `hash_algorithm` 으로 정하고, `md5`, `sha1`, `sha256` 을 받으며 기본값은 `[md5, sha1]` 입니다[1]. Velociraptor 의 `Linux.Search.FileFinder` 는 글롭(기본 `/home/*`)으로 파일을 찾으면서 `Calculate_Hash` 로 해시를, `YaraRule` 로 내용 검사를 함께 할 수 있습니다[2]. 이 아티팩트는 `ExcludePathRegex` 기본값 `^/(proc|sys|run|snap)` 에 걸리는 폴더로 내려가지 않고, `LocalFilesystemOnly` 기본값 `Y` 라서 네트워크 파일 시스템은 건너뜁니다[2]. 타임라인과 함께 보려면 plaso 에서 `log2timeline.py --hashers md5` 처럼 해시를 계산해 저장해 둡니다[3].

3. **패키지 기준값으로 걸러 냅니다.** 패키지가 설치한 파일은 패키지 관리자 데이터베이스의 해시와 비교합니다. 배포판별 차이는 아래와 같고, 출력을 읽는 법은 [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md)에 있습니다.

   | 항목 | Ubuntu 24.04 (dpkg) | RHEL 9 (rpm) |
   |---|---|---|
   | 기준값 | `/var/lib/dpkg/info/이름.md5sums` 또는 `이름:아키텍처.md5sums`[9] | rpm 데이터베이스[5] |
   | 해시 | MD5, 한 줄에 32자리 16진 값 + 공백 두 칸 + 경로[4] | 파일 다이제스트(예전 이름 MD5 sum)[5] |
   | 명령 | `dpkg -V` (`--verify`)[4] | `rpm -V` (`--verify`)[5] |
   | 이미지에 대고 돌릴 때 | `--root`, `--admindir`[4] | `--root`[5] |

   `dpkg -V` 가 실제로 하는 검사는 파일 내용의 MD5 비교 하나뿐이고, 데이터베이스에 MD5 가 있는 파일만 검사합니다[4]. `rpm -V` 는 크기·다이제스트·권한·종류·소유자·그룹 등을 비교하고, 기본으로는 다른 점이 있는 파일만 보여 줍니다[5].

4. **알려진 정상 목록으로 걸러 냅니다.** plaso 의 `nsrlsvr` 분석 플러그인은 해시를 nsrlsvr 서버(예: `nsrlsvr -f /fullpath/NSRLFile.txt` 로 띄우고 9120 포트로 묻는 구성)에 물어 목록에 있는 파일의 이벤트에 태그를 붙입니다[3]. 해시는 서버가 받는 종류(예: MD5)로 `log2timeline.py` 에서 미리 계산해 둡니다[3]. `bloom` 분석 플러그인은 서버 없이 블룸 필터 (bloom filter) 파일에 해시가 있는지 보고, 태그 기본값은 `bloom_present` 입니다[3]. CIRCL hashlookup 이 이 형식의 필터 파일을 내려받을 수 있게 제공하고, `hashlookup-full.bloom` 을 쓰는 예에서는 해시를 SHA-1 로 계산합니다[3]. 직접 필터를 만들 때는 해시를 대문자로 넣어야 합니다[3].

5. **남은 파일에 YARA 를 돌립니다.** YARA 규칙은 문자열(`strings`)과 이를 묶는 참·거짓 조건(`condition`)으로 이뤄지고, 문자열에는 텍스트와 16진 바이트 배열을 쓸 수 있습니다[6]. 아래는 모양만 보이려고 만든 예시 규칙입니다.

   ```yara
   rule example_marker : demo
   {
       meta:
           description = "만든 예시 규칙"
       strings:
           $a = "example-marker-2026"
           $b = { 65 78 61 6D 70 6C 65 }
       condition:
           $a or $b
   }
   ```

   명령 모양은 `yara [OPTIONS] RULES_FILE TARGET` 이고 대상은 파일·폴더·프로세스를 받습니다[6]. 폴더는 기본으로 그 안의 파일만 보고 하위 폴더로 내려가지 않으므로, 붙인 이미지를 훑을 때는 `-r` 을 줍니다[6]. `-r` 은 심볼릭 링크를 따라가므로 `-N` 을 함께 주고, 일치한 문자열을 보려면 `-s`, 메타데이터와 태그를 보려면 `-m`, `-g` 를 줍니다[6]. 예: `yara -r -N -s rules.yar /mnt/evidence` (만든 예시 경로). 큰 파일은 `-z 크기`(4.2.0 부터)로 건너뛰고, `-p` 로 스레드 수를, `-a 초` 로 시간 제한을 정하며, `--scan-list` 로 파일 목록만 검사할 수 있습니다[6]. 3·4단계에서 걸러 내고 남은 파일 목록을 `--scan-list` 로 넘기면 그 파일만 검사합니다.

6. **프로세스 메모리에 YARA 를 돌립니다.** 디스크에서 지워졌거나 메모리에서만 풀리는 코드는 파일 검사로 잡히지 않습니다. 켜져 있는 시스템에서는 Velociraptor `Linux.Detection.Yara.Process` 가 `proc_yara` 로 프로세스 메모리를 검사합니다[2]. 규칙은 URL 로 받거나 직접 넣고, 수집하는 Velociraptor 자신의 PID 는 빼며, 일치한 프로세스의 메모리를 올려받을 수도 있습니다[2]. 메모리 덤프에서는 Volatility 3 의 `linux.vmayarascan` 이 `pslist` 로 얻은 작업마다 가상 메모리 영역 (VMA) 을 읽어 검사하고, `Offset`, `PID`, `Rule`, `Component`, `Value` 칸을 출력합니다[8]. 덤프를 다루는 준비(심볼 표 등)는 [메모리 분석](memory-analysis.md)에 있습니다.

7. **기록합니다.** 쓴 규칙 파일의 해시, 도구 이름과 판(YARA 인지 YARA-X 인지), 옵션, 걸러 낸 기준 목록의 판을 남깁니다. 같은 규칙이라도 옵션에 따라 검사 범위가 달라지기 때문입니다(아래 함정 참고).

## 도구

| 도구 | 하는 일 | 참고 |
|---|---|---|
| UAC `hash_executables`, `hash_running_processes` | 실행 파일·실행 중 프로세스의 해시 수집 | 기본 MD5·SHA-1[1] |
| Velociraptor `Linux.Search.FileFinder` | 글롭으로 찾고 해시·YARA·올려받기 | 기본 글롭 `/home/*`[2] |
| Velociraptor `Linux.Detection.Yara.Process` | 프로세스 메모리 YARA 검사 | 기본 한 건에서 멈춤[2] |
| plaso `nsrlsvr`, `bloom` 분석 플러그인 | 알려진 해시에 태그 | 해시는 `log2timeline.py --hashers` 로 미리 계산[3] |
| `dpkg -V`, `rpm -V` | 패키지 기준값과 비교 | [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md) |
| YARA (`yara`, `yarac`) | 파일·폴더·프로세스를 규칙으로 검사 | 저장소는 유지 보수 상태[6] |
| YARA-X | YARA 를 대신하려고 새로 만든 도구 | 규칙 모양은 같은 틀, 규칙 수준 차이는 따로 정리됨[7] |
| Volatility 3 `linux.vmayarascan` | 메모리 덤프의 프로세스 영역 검사 | Intel32·Intel64 커널[8] |

YARA 저장소는 유지 보수 상태 (maintenance mode) 로 바뀌었고, 버그 수정과 작은 기능만 더해지며 새 모듈 같은 큰 기능은 YARA-X 쪽에서 나옵니다[6][7]. YARA-X 는 YARA 를 대신하는 것을 목표로 합니다[7]. 두 도구의 결과를 섞어 쓰면 어느 쪽으로 돌린 결과인지 기록에 적어 둡니다.

## 함정과 한계

**UAC 기본 설정에는 SHA-256 이 없습니다.** 기본값이 `[md5, sha1]` 이라서[1], SHA-256 으로 공유되는 위협 정보와 맞추려면 수집 전에 `hash_algorithm` 을 바꾸거나 파일을 다시 계산해야 합니다. 기준 목록마다 쓰는 해시도 다릅니다. dpkg 의 `md5sums` 는 MD5 만 담고[4], plaso 는 `--hashers` 로 고른 것만 계산합니다[3].

**패키지 해시 비교는 같은 시스템의 기록과 비교합니다.** 공격자가 파일과 데이터베이스를 함께 바꾸면 차이가 나지 않습니다. `md5sums` 와 `--verify` 는 무결성 확인용이고 보안 검증 수단이 아닙니다[4]. 설정 파일은 원래 바뀌는 파일이라서 다르게 나와도 그 자체로는 이상이 아닙니다([패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md)).

**블룸 필터의 "있음" 은 틀릴 수 있습니다.** 블룸 필터는 없는 것을 있다고 하는 경우(거짓 양성)가 만들 때 정한 확률로 생기고, 있는 것을 없다고 하지는 않습니다[3]. 그래서 `bloom_present` 태그만 보고 파일을 정상으로 빼면 드물게 악성 파일이 같이 빠질 수 있습니다. 직접 만든 필터는 해시를 대문자로 넣었는지 확인합니다[3].

**`yara -r` 은 심볼릭 링크를 따라갑니다[6].** 붙인 이미지 안에 절대 경로를 가리키는 링크(예: `/etc` 를 가리키는 링크)가 있으면 분석 컴퓨터의 파일까지 검사해 결과에 섞일 가능성이 있으므로, 링크를 따라가지 않는 `-N` 을 함께 줍니다[6].

**남이 준 컴파일된 규칙은 쓰지 않습니다.** YARA 3.9 부터 컴파일된 규칙은 `-C` 로 따로 밝혀야 하는데, 믿을 수 없는 곳에서 온 컴파일 규칙이 분석 컴퓨터에서 악성 코드를 실행할 수 있기 때문입니다[6]. 규칙은 원문으로 받아 직접 `yarac` 로 컴파일합니다.

**메모리 검사 도구는 전부를 보지 않습니다.** Velociraptor `Linux.Detection.Yara.Process` 는 `NumberOfHits` 기본값 1 이라 첫 일치에서 멈추고, 문자열이 여럿인 규칙도 한 줄에 한 문자열만 보여 줍니다[2]. `linux.vmayarascan` 은 1 GB 가 넘는 VMA 를 건너뛰고, 읽을 수 없는 페이지는 0 으로 채워 검사하며(`pad=True`), 커널 스레드처럼 프로세스 영역이 없는 작업도 건너뜁니다[8]. `pslist` 가 따라가는 작업 목록에서 숨긴 프로세스는 검사 대상에 들어가지 않으므로, 숨은 프로세스 찾기는 [루트킷 찾기](rootkit-detection.md)에서 따로 합니다[8].

**크기·시간 제한은 빠진 파일을 만듭니다.** `-z` 로 건너뛴 큰 파일과 `-a` 로 중간에 끊긴 검사는 "일치 없음" 과 구별해 기록합니다[6].

## 결과를 어떻게 해석하나

### 증명하는 것

- 해시가 같으면 파일 내용이 같습니다. 단, 고른 알고리즘에서 충돌이 없다는 전제가 붙습니다.
- 패키지 기준값과 다르면, 설치 뒤 그 파일의 내용(또는 `rpm -V` 가 보는 다른 속성)이 바뀌었습니다[4][5].
- YARA 가 일치하면, 그 파일이나 메모리 영역에 규칙이 적은 바이트 패턴이 들어 있습니다. `-s` 출력이나 `Offset` 칸으로 어디에 있는지도 알 수 있습니다[6][8].

### 증명하지 못하는 것

- 패키지 기준값과 같다고 해서 변조가 없었다는 뜻은 아닙니다. 데이터베이스까지 바꿨을 수 있습니다[4].
- 알려진 정상 목록에 없다고 악성인 것은 아닙니다. 직접 빌드한 프로그램, 사내 도구, 목록보다 새 판은 모두 목록에 없습니다.
- YARA 일치는 규칙이 찾는 패턴이 있다는 것까지만 말합니다. 규칙이 넓으면 정상 파일에도 걸리고, 일치가 없어도 규칙이 모르는 변종일 수 있습니다.
- 해시나 YARA 결과만으로는 언제 들어왔는지, 누가 실행했는지 알 수 없습니다.

### 시각

해시와 YARA 결과에는 파일 자체의 시각이 들어 있지 않습니다. 파일이 언제 생기고 바뀌었는지는 파일 시스템 시각과 로그로 따로 보고([타임라인 만들기](timeline.md)), 검사를 돌린 시각은 분석 컴퓨터 시각이라 UTC 로 적어 둡니다. plaso 의 `nsrlsvr`·`bloom` 태그는 이미 있는 이벤트에 붙으므로, 태그된 행의 시각은 그 이벤트(파일 시스템 시각 등)의 시각입니다[3].

### 보고서 문장 예

기록이 말하는 만큼만 씁니다. "악성 코드가 설치되었다" 가 아니라 "`/usr/local/bin/example`(만든 예시 경로)의 SHA-256 이 어느 패키지 기준값에도 없고, 규칙 파일(SHA-256 기록)의 `example_marker` 규칙과 오프셋 0x1A40 에서 일치했다(만든 예시)" 처럼 씁니다. 걸러 낸 기준 목록과 판, 건너뛴 파일의 수와 이유도 함께 적습니다.

## 함께 볼 페이지

- [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md), [dpkg·apt 기록](../../02-artifacts/packages/dpkg-apt.md), [rpm·dnf·yum 기록](../../02-artifacts/packages/rpm-dnf.md)
- [라이브 응답 수집](../acquisition/live-response.md), [메모리 분석](memory-analysis.md), [루트킷 찾기](rootkit-detection.md)
- [채굴기가 돌았나](../../04-scenarios/intrusion/cryptominer.md), [랜섬웨어가 돌았나](../../04-scenarios/intrusion/ransomware.md)

## 참고 문헌

1. tclahr, UAC — `artifacts/hash_executables/hash_executables.yaml`, `artifacts/live_response/process/hash_running_processes.yaml`, `config/uac.conf`. https://github.com/tclahr/uac/tree/main/artifacts , https://github.com/tclahr/uac/blob/main/config/uac.conf
2. Velociraptor, `Linux.Search.FileFinder`, `Linux.Detection.Yara.Process` 아티팩트 정의. https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Search/FileFinder.yaml , https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Detection/Yara/Process.yaml
3. plaso, 사용자 문서 `Analysis-plugin-nsrlsvr.md`, `Analysis-plugin-bloom.md`. https://github.com/log2timeline/plaso/tree/main/docs/sources/user
4. dpkg, `man/deb-md5sums.pod` (deb-md5sums(5)), `man/dpkg.pod` (dpkg(1) `--verify`, `--root`, `--admindir`). https://github.com/guillemj/dpkg/tree/main/man
5. RPM, `docs/man/rpm.8.scd` (rpm(8) `--verify`). https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpm.8.scd
6. VirusTotal, YARA `README.md`, `docs/commandline.rst`. https://github.com/VirusTotal/yara/blob/master/README.md , https://github.com/VirusTotal/yara/blob/master/docs/commandline.rst
7. VirusTotal, YARA-X `README.md`. https://github.com/VirusTotal/yara-x/blob/main/README.md
8. Volatility Foundation, Volatility 3 `volatility3/framework/plugins/linux/vmayarascan.py`, `doc/source/getting-started-linux-tutorial.rst`. https://github.com/volatilityfoundation/volatility3/blob/develop/volatility3/framework/plugins/linux/vmayarascan.py , https://github.com/volatilityfoundation/volatility3/blob/develop/doc/source/getting-started-linux-tutorial.rst
9. Fox-IT, dissect.target `dissect/target/plugins/os/unix/linux/debian/dpkg.py`. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/debian/dpkg.py
