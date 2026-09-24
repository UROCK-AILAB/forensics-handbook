# Sysmon 로그 (Sysmon)

## 한 줄 요약

Sysmon (System Monitor) 은 설정 파일이 정한 시스템 활동을 Windows 이벤트 로그에 남기는 Sysinternals 도구입니다. 프로세스 생성, 네트워크 연결, 파일·레지스트리 변경, 다른 프로세스 접근을 이벤트 번호별로 기록합니다.

## 왜 중요한가

실행, 통신, 파일 변경, 레지스트리 변경, 다른 프로세스 접근이 한 로그에 모이고, 이벤트마다 어느 프로세스가 그 일을 했는지 적힙니다. 프로세스마다 ProcessGuid 가 붙어서 PID 가 다시 쓰여도 이 값으로 한 프로세스의 이벤트를 이어 볼 수 있고, 로그온 세션마다 LogonGuid 도 붙습니다. 프로세스 생성 이벤트에는 명령줄과 실행 파일 해시가 함께 남습니다. 한 번 설치하면 재부팅 뒤에도 기록을 이어 가며, 시각은 UTC 로 남습니다.

이 로그로 증명하지 못하는 것은 다음과 같습니다.

- Sysmon 은 누군가 설치해야 기록합니다. Windows 11 에 들어 있는 Sysmon 도 기본으로 꺼져 있습니다. 그래서 조사하는 PC 에 Sysmon 로그가 있는지부터 확인합니다.
- 무엇을 기록할지는 설정 파일이 정합니다.
- Microsoft 문서는 설정에서 빼서 기록하지 않은 활동은 나중에 되살릴 수 없다고 적습니다. 그래서 로그에 없다는 것만으로 그 일이 없었다고 쓰지 않습니다.
- Sysmon 은 기록만 합니다. 사건을 분석하지 않고, 공격자에게서 자신을 숨기려 하지도 않습니다.
- Sysmon 이 멈췄거나, 설정이 바뀌었거나, 기록이 빠진 구간은 따로 확인합니다. 방법은 [Sysmon 개념과 설정 확인](sysmon-config.md)에서 다룹니다.

## 한눈에 보기

### 위치와 형식

| 항목 | 내용 |
|---|---|
| 채널 (Vista 이후) | Microsoft-Windows-Sysmon/Operational |
| 이벤트 뷰어 위치 | 응용 프로그램 및 서비스 로그 > Microsoft > Windows > Sysmon > Operational |
| Vista 이전 OS | System 로그에 씁니다 |
| 로그 파일 | `%SystemRoot%\System32\winevt\Logs\Microsoft-Windows-Sysmon%4Operational.evtx` (채널 이름 규칙으로 짐작한 경로입니다) |
| 시각 | UTC. 이벤트마다 UtcTime 칸이 있습니다 |
| 이벤트 종류 표시 | 이벤트 뷰어의 "작업 범주" 칸에 아래 필터 태그 이름이 보입니다 |
| 무엇을 남길지 | 설정 파일이 정합니다 |

로그 파일 경로를 짐작한 근거, 설치 흔적, 채널 기본값은 [Sysmon 개념과 설정 확인](sysmon-config.md)에서 다룹니다. EVTX 파일 형식은 [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md)에서 다룹니다.

### Windows 버전

| 구분 | 내용 |
|---|---|
| 따로 받은 Sysmon v15.22 | Windows 11 이상, Windows Server 2019 이상에서 돕니다 |
| 따로 받은 Sysmon 예전 버전 | 어느 OS 까지 지원했는지 확인하지 못했습니다 |
| Windows 11 내장 Sysmon | 선택적 기능입니다. 기본으로 꺼져 있습니다. 따로 받은 Sysmon 과 함께 쓸 수 없고, 같은 채널에 기록합니다 |

### 이벤트 목록

v15.22 기준입니다. 필터 태그는 설정 파일에서 이벤트를 가리키는 이름입니다.

| ID | 필터 태그 | 남는 때 | 다루는 페이지 |
|---|---|---|---|
| 1 | ProcessCreate | 프로세스 생성 | [프로세스 생성](1.md) |
| 2 | FileCreateTime | 파일 생성 시각 변경 | [파일 생성·삭제](11-23-26.md) |
| 3 | NetworkConnect | 네트워크 연결 | [네트워크 연결·DNS 질의](3-22.md) |
| 4 | (필터로 끌 수 없음) | Sysmon 서비스 상태 변경 | [Sysmon 개념과 설정 확인](sysmon-config.md) |
| 5 | ProcessTerminate | 프로세스 종료 | [프로세스 생성](1.md) |
| 6 | DriverLoad | 드라이버 로드 | [이미지 로드·프로세스 접근](7-8-10.md) |
| 7 | ImageLoad | 이미지 (모듈) 로드 | [이미지 로드·프로세스 접근](7-8-10.md) |
| 8 | CreateRemoteThread | 다른 프로세스 안에 스레드 생성 | [이미지 로드·프로세스 접근](7-8-10.md) |
| 9 | RawAccessRead | 원시 읽기 (raw access read) | 이 묶음에서 다루지 않습니다 |
| 10 | ProcessAccess | 다른 프로세스 열기 | [이미지 로드·프로세스 접근](7-8-10.md) |
| 11 | FileCreate | 파일 생성 | [파일 생성·삭제](11-23-26.md) |
| 12 | RegistryEvent | 레지스트리 키·값 생성과 삭제 | [레지스트리 변경](12-13-14.md) |
| 13 | RegistryEvent | 레지스트리 값 설정 | [레지스트리 변경](12-13-14.md) |
| 14 | RegistryEvent | 레지스트리 키·값 이름 바꿈 | [레지스트리 변경](12-13-14.md) |
| 15 | FileCreateStreamHash | 이름 있는 파일 스트림 생성 | [파일 생성·삭제](11-23-26.md) |
| 16 | (필터로 끌 수 없음) | Sysmon 설정 변경 | [Sysmon 개념과 설정 확인](sysmon-config.md) |
| 17 · 18 | PipeEvent | 이름 있는 파이프 생성 · 연결 | 이 묶음에서 다루지 않습니다 |
| 19 · 20 · 21 | WmiEvent | WMI 필터 · 소비자 · 바인딩 | 이 묶음에서 다루지 않습니다 |
| 22 | DnsQuery | DNS 질의 | [네트워크 연결·DNS 질의](3-22.md) |
| 23 | FileDelete | 파일 삭제 (지운 파일 보관) | [파일 생성·삭제](11-23-26.md) |
| 24 | ClipboardChange | 클립보드 변경 | 이 묶음에서 다루지 않습니다 |
| 25 | ProcessTampering | 프로세스 이미지 변조 | 이 묶음에서 다루지 않습니다 |
| 26 | FileDeleteDetected | 파일 삭제 (기록만) | [파일 생성·삭제](11-23-26.md) |
| 27 | FileBlockExecutable | 실행 파일 생성 차단 | [파일 생성·삭제](11-23-26.md) |
| 28 | FileBlockShredding | 파일 파쇄 차단 | [파일 생성·삭제](11-23-26.md) |
| 29 | FileExecutableDetected | 실행 파일 생성 감지 | [파일 생성·삭제](11-23-26.md) |
| 255 | Error | 오류 | [Sysmon 개념과 설정 확인](sysmon-config.md) |

- 어느 스키마 버전에서 어느 이벤트가 처음 나오는지는 [Sysmon 개념과 설정 확인](sysmon-config.md)의 "스키마 버전" 에서 다룹니다.
- 22번 태그 표기가 문서마다 다른 점은 [네트워크 연결·DNS 질의](3-22.md)에서 다룹니다.
- WMI 로 걸어 둔 자동 실행은 [WMI 영구 이벤트 구독](../../persistence/wmi-event-subscription.md)에서 다룹니다.

### 알려 주는 것

| 알 수 있는 것 | 이벤트 | 자세히 |
|---|---|---|
| 어떤 기간에 무엇을 기록하게 돼 있었나, 언제 설정이 바뀌거나 기록이 빠졌나 | 4, 16, 255 | [Sysmon 개념과 설정 확인](sysmon-config.md) |
| 어떤 실행 파일이 어떤 명령줄로 실행됐나, 부모 프로세스는 무엇인가 | 1, 5 | [프로세스 생성](1.md) |
| 어느 프로세스가 어디로 연결했나, 어떤 이름을 물었나 | 3, 22 | [네트워크 연결·DNS 질의](3-22.md) |
| 어느 프로세스가 파일을 만들거나 지웠나, 지운 파일의 사본이 있나 | 11, 23, 26 | [파일 생성·삭제](11-23-26.md) |
| 어느 프로세스가 레지스트리를 바꿨나 | 12, 13, 14 | [레지스트리 변경](12-13-14.md) |
| 어떤 DLL·드라이버가 올라왔나, 다른 프로세스를 열거나 그 안에 스레드를 만들었나 | 6, 7, 8, 10 | [이미지 로드·프로세스 접근](7-8-10.md) |

## 읽는 순서

1. [Sysmon 개념과 설정 확인 (Sysmon Config)](sysmon-config.md) — 설치 흔적, 설정이 남는 레지스트리 값, 설정 파일 읽는 법, 이벤트 4·16·255 를 다룹니다. 다른 이벤트를 읽기 전에 기록 범위부터 이 페이지로 확인합니다.
2. [프로세스 생성 (이벤트 1)](1.md) — 명령줄, 해시, 부모 프로세스를 읽습니다. ProcessGuid 로 프로세스 나무를 잇고, 종료 이벤트 5 로 실행 시간을 구합니다.
3. [네트워크 연결·DNS 질의 (이벤트 3·22)](3-22.md) — 어느 프로세스가 어디로 연결하고 어떤 이름을 물었는지 읽습니다. 호스트 이름 칸을 역방향 조회로 채운다는 점을 조심합니다.
4. [파일 생성·삭제 (이벤트 11·23·26)](11-23-26.md) — 파일을 만들고 지운 프로세스를 찾고, 보관 폴더의 지운 파일 사본을 찾습니다. 이벤트 2·15·27\~29 도 함께 봅니다.
5. [레지스트리 변경 (이벤트 12·13·14)](12-13-14.md) — 키·값의 생성, 삭제, 수정, 이름 바꿈을 읽습니다. Sysmon 이 루트 키를 줄여 적는 방식도 다룹니다.
6. [이미지 로드·프로세스 접근 (이벤트 7·8·10)](7-8-10.md) — 올라온 모듈, 다른 프로세스 열기, 원격 스레드 생성을 읽습니다. 드라이버 로드 (6) 와 GrantedAccess 비트를 푸는 법도 다룹니다.

## 함께 볼 페이지

- [이벤트 로그 형식](../../../01-foundations/database-log-formats/evtx-evt-etl/index.md) — Sysmon 로그 파일을 직접 읽고, 지운·손상 레코드를 찾습니다.
- [감사 정책과 로그 설정](../audit-policy-log-settings.md) — 채널 크기와 보관 방식을 확인합니다.
- [프로세스 생성 (4688)](../4688.md) — Sysmon 이 없거나 꺼져 있던 구간의 실행 기록을 보안 로그에서 찾습니다.
- [이벤트 로그 삭제](../1102-104.md) · [서비스 설치](../7045-4697.md) — Sysmon 채널을 지운 흔적과 Sysmon 을 설치한 흔적을 찾습니다.
- [서비스·드라이버](../../persistence/services-drivers.md) — Sysmon 서비스 키와 드라이버 키를 읽습니다.
- [이벤트 로그 규칙 검색](../../../03-techniques/analysis/sigma-rules.md) — 여러 대의 Sysmon 로그를 규칙으로 훑습니다.
- [타임라인 작성](../../../03-techniques/analysis/timeline/index.md) — Sysmon 이벤트를 다른 기록과 한 줄로 놓습니다.
- [어떤 프로그램을 언제 실행했나](../../../04-scenarios/activity/program-execution.md) · [악성코드 지속성(자동실행) 찾기](../../../04-scenarios/incident/persistence.md) · [계정 탈취와 측면 이동](../../../04-scenarios/incident/credential-theft-lateral-movement/index.md) — 조사에서 Sysmon 로그를 다른 흔적과 함께 읽는 순서입니다.
- [증거를 없애려 했나](../../../04-scenarios/activity/anti-forensics/index.md) — Sysmon 을 멈추거나 로그를 지운 흔적을 다른 흔적과 모아 판단합니다.

## 참고 문헌

- Microsoft Learn, "Sysmon - Sysinternals" — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
- Sysinternals, Sysmon 공식 배포본 v15.22 (Sysmon.zip) — https://download.sysinternals.com/files/Sysmon.zip
- Microsoft Learn, "Enable and configure Sysmon in Windows" (2026-02-03) — https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/how-to-enable-sysmon
- Microsoft Learn, "Sysmon configuration files" (2026-02-03) — https://learn.microsoft.com/en-us/windows/security/operating-system-security/sysmon/sysmon-configuration-files
