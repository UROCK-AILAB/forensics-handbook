# 메모리 분석 (Memory Forensics)

## 한 줄 요약

메모리 분석은 물리 메모리를 파일로 떠서, 디스크에 남지 않는 실행 상태를 읽는 기법입니다.
켜진 PC 에서 뜬 메모리 이미지와, 디스크에 남은 메모리 조각을 함께 다룹니다.
디스크에 남는 조각은 최대 절전 파일, 페이지 파일, 크래시 덤프입니다.

## 왜 중요한가

RFC 3227 (2002년 2월, BCP 55) 은 증거를 휘발성이 큰 것부터 모으라고 합니다 [1].
원문은 "Proceed from the volatile to the less volatile" 입니다 [1].
이 문서가 적은 휘발성 순서는 아래와 같습니다 [1].

1. 레지스터, 캐시
2. 라우팅 표, ARP 캐시, 프로세스 표, 커널 통계, 메모리
3. 임시 파일 시스템
4. 디스크
5. 원격 로그와 모니터링 자료
6. 물리 구성과 네트워크 구조
7. 보관 매체

- 메모리는 두 번째 묶음에 듭니다. 그래서 디스크보다 먼저 모읍니다 [1].
- 프로세스 표와 라우팅 표, ARP 캐시도 같은 묶음에 듭니다 [1]. 전원이 꺼지면 이 내용은 사라집니다.
- 전원이 꺼진 뒤에도 디스크에 남는 메모리 조각이 있습니다. 최대 절전 파일 [2], 페이지 파일 [3], 커널 크래시 덤프 [4], 사용자 모드 크래시 덤프 [5] 입니다.
- 메모리 이미지는 확보한 순간의 상태만 담습니다. 디스크에 남은 조각은 Windows 가 그 파일을 쓴 순간의 상태입니다. 무엇을 증명하고 무엇을 증명하지 못하는지는 하위 페이지마다 따로 적었습니다.

## 한눈에 보기

| 자료 | 위치 | Windows 버전 | 알려 주는 것 |
|---|---|---|---|
| 물리 메모리 이미지 | 확보 도구가 만든 파일 | 확보 도구의 지원 범위를 따릅니다 | 확보한 순간의 프로세스·연결·메모리 내용 |
| 최대 절전 파일 | 파일 이름 hiberfil.sys [2] | 빠른 시작은 Windows 8 부터 있습니다 [2] | 최대 절전이나 빠른 시작으로 끌 때의 메모리 |
| 페이지 파일 | 설정 값: `Memory Management\PagingFiles` [4] | 참고한 문서의 적용 대상은 Windows 10 입니다 [3] | 물리 메모리에서 내보낸 페이지 조각 [3] |
| swapfile.sys | 이 글의 참고 문헌으로 확인하지 못함 | 이 글의 참고 문헌으로 확인하지 못함 | 페이지 파일과 같은 부류로 흔히 묶습니다 |
| 커널 크래시 덤프 | `%SystemRoot%\Memory.dmp`, `%SystemRoot%\Minidump` [4] | 버전별 기본값은 이 글의 참고 문헌으로 확인하지 못함 | 버그 체크 순간의 메모리. 담는 범위는 덤프 종류에 따라 다릅니다 [4] |
| 사용자 모드 크래시 덤프 | 기본 `%LOCALAPPDATA%\CrashDumps` [5] | Windows Vista SP1·Server 2008 부터 [5] | 죽은 프로그램의 메모리 |

공개 도구는 아래를 예로 듭니다.

| 도구 | 쓰임 |
|---|---|
| Volatility 3 | 메모리 이미지를 분석합니다. 프로세스·DLL·핸들·네트워크·주입 탐지·레지스트리 해시 추출 플러그인이 있습니다 [6] |
| WinPmem (Apache License 2.0) | 물리 메모리를 확보합니다 [7] |
| WinDbg (Windows 디버거) | 완전·커널 크래시 덤프를 엽니다 [4] |

## 읽는 순서

1. [메모리 덤프 확보 (Memory Acquisition)](memory-acquisition.md) — 켜진 PC 에서 물리 메모리를 뜨는 원칙과 절차입니다. 확보 기록을 남기는 법도 다룹니다.
2. [프로세스와 DLL 분석 (Process Analysis)](process-analysis.md) — 이미지에서 프로세스 목록, 명령줄, DLL, 핸들을 읽습니다. 플러그인 이름을 읽는 법도 여기 있습니다.
3. [메모리 속 네트워크 흔적 (Network Artifacts)](network-artifacts.md) — 메모리에 남은 연결과 수신 대기 흔적을 찾아 프로세스에 잇습니다.
4. [코드 주입·숨긴 프로세스 탐지 (Injection·Rootkit)](injection-rootkit.md) — 정상 프로세스 안에 들어간 코드와, 목록에서 숨긴 프로세스·모듈을 찾습니다.
5. [메모리 속 문자열·자격증명·암호 키 (Strings·Credentials·Keys)](strings-credentials-keys.md) — 문자열 검색, 계정 해시와 비밀, Credential Guard 가 켜진 PC 의 차이를 다룹니다.
6. [최대 절전 파일 (hiberfil.sys)](hiberfil-sys.md) — 최대 절전·빠른 시작 때 남는 파일의 서명과 헤더를 읽고 해석합니다.
7. [페이지 파일 (pagefile.sys·swapfile.sys)](pagefile-sys-swapfile-sys.md) — 물리 메모리에서 내보낸 페이지를 검색하는 법과 그 한계입니다.
8. [크래시 덤프 (MEMORY.DMP·Minidump)](memory-dmp-minidump.md) — 커널·사용자 모드 덤프의 종류, 설정 레지스트리, 찾는 순서입니다.

## 함께 볼 페이지

- [라이브 응답](../../process-acquisition/live-response/index.md) — 켜진 PC 에서 메모리 말고 무엇을 먼저 모으는지 다룹니다.
- [증거 획득](../../process-acquisition/evidence-acquisition/index.md) — 해시와 확보 기록을 남기는 방법입니다.
- [포렌식 조사 절차](../../process-acquisition/investigation-process.md) — 메모리 분석이 조사 전체에서 어디에 오는지 다룹니다.
- [암호화 증거 다루기](../encrypted-evidence/index.md) — 암호화 볼륨이 열린 PC 를 끄기 전에 정할 것을 다룹니다.
- [의심 실행 파일 선별](../code-signing-yara.md) — 메모리 검색에 쓰는 YARA 규칙을 다룹니다.
- [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) — 메모리에 남은 자격증명 흔적을 쓰는 조사 시나리오입니다.
- [도구 결과 교차 검증](../../reporting/tool-validation.md) — 도구마다 결과가 다를 때 확인하는 법입니다.

## 참고 문헌

1. IETF, RFC 3227 "Guidelines for Evidence Collection and Archiving" (BCP 55, 2002-02) — https://www.rfc-editor.org/rfc/rfc3227
2. Microsoft Learn, "Distinguishing Fast Startup from Wake-from-Hibernation" (2025-02-21) — https://learn.microsoft.com/en-us/windows-hardware/drivers/kernel/distinguishing-fast-startup-from-wake-from-hibernation
3. Microsoft Learn, "Introduction to the page file" (2026-02-12) — https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file
4. Microsoft Learn, "Memory dump file options" (KB 254649, 2026-02-12) — https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/memory-dump-file-options
5. Microsoft Learn, "Collecting User-Mode Dumps" (2024-07-18) — https://learn.microsoft.com/en-us/windows/win32/wer/collecting-user-mode-dumps
6. Volatility 3 documentation, "volatility3.plugins.windows package" (latest) — https://volatility3.readthedocs.io/en/latest/volatility3.plugins.windows.html
7. Velocidex, WinPmem README (GitHub) — https://github.com/Velocidex/WinPmem
