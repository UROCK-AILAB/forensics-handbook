---
title: "원격 데스크톱 접속 기록"
parent: "아티팩트 · 네트워크"
nav_order: 2350
---

# 원격 데스크톱 접속 기록 (RDP Client MRU)

## 한 줄 요약

원격 데스크톱 연결 (Remote Desktop Connection, mstsc) 로 다른 컴퓨터에 접속하면, 대상 컴퓨터 이름이 사용자 하이브의 `Terminal Server Client\Default` 키에 MRU 목록으로 남습니다. 대상별 하위 키에는 사용자 이름 힌트가 남습니다.

## 무엇을 기록하나 · 왜 생기나

원격 데스크톱 연결 도구로 다른 컴퓨터에 접속하면 그 컴퓨터 이름이 "컴퓨터" 입력 상자의 목록에 추가되는데, 이 목록이 레지스트리의 MRU 값입니다. MRU 는 최근 사용 목록 (Most Recently Used) 입니다. 도구 자체에는 이 목록을 지우거나 한 줄을 빼는 기능이 없고, Microsoft 는 레지스트리에서 지우는 방법을 안내합니다. `Servers` 아래에는 대상 호스트마다 하위 키가 있고, 그 안에 `UsernameHint` 값이 있습니다. 이 값들은 사용자 하이브(NTUSER.DAT)에 있어서 계정마다 따로 남습니다.

접속을 건 쪽(출발 PC)의 흔적이며, 접속을 받은 쪽의 흔적은 [원격 데스크톱 이벤트](../event-logs/rdp-event-logs/index.md) 에서 다룹니다.

## 위치와 버전별 차이

```
HKCU\Software\Microsoft\Terminal Server Client\Default
    MRU0, MRU1, …                    REG_SZ   대상 호스트 (FQDN 또는 IP 주소)

HKCU\Software\Microsoft\Terminal Server Client\Servers\<대상 호스트>
    UsernameHint                              사용자 이름
```

- 오프라인 이미지에서는 사용자 프로필의 NTUSER.DAT 에서 `Software\Microsoft\Terminal Server Client\Default` 와 `Software\Microsoft\Terminal Server Client\Servers` 를 읽습니다.
- Mac 용 원격 데스크톱 연결은 레지스트리가 아니라 `Users:Username:Library:Preferences:Microsoft:RDC Client:Recent Servers` 파일에 목록을 둡니다.
- Microsoft 문서(KB 312169, 2026-02-12 판)는 윈도 버전별 차이를 적지 않습니다. 이번에 연 자료로 버전별 차이는 확인하지 못했습니다.

Windows 11 PC 한 대에서 본 모습은 아래와 같습니다. 원격 데스크톱 연결을 쓴 적이 없는 PC 입니다. (확인 범위: Win11 25H2 한 대)

`HKCU\Software\Microsoft\Terminal Server Client` 키는 없었고, `HKLM\SOFTWARE\Microsoft\Terminal Server Client` 에는 `Default`, `IME Mapping Table`, `TrustedGateways` 하위 키가 있었습니다. 그래서 HKLM 쪽 키가 있다는 사실만으로는 이 도구를 썼다고 볼 수 없습니다.

## 구조

### Default 키

| 값 | 형식 | 내용 |
|---|---|---|
| `MRU0` | REG_SZ | 가장 최근에 접속한 대상 |
| `MRU1`, `MRU2`, … | REG_SZ | 그 앞에 접속한 대상 |

- 값에는 FQDN 이나 IP 주소가 들어가며, Microsoft 문서의 예는 `MRU0` = `192.168.16.60`, `MRU1` = `computer.domain.com` 입니다.
- 새로 접속하면 그 대상이 `MRU0` 이 되고, 기존 값은 번호가 하나씩 뒤로 밀립니다.
- MRU 가 최대 몇 개까지 남는지는 확인하지 못했습니다.
- 대상을 `호스트:포트` 로 입력하면 그대로 저장되는지는 확인하지 못했습니다.

### Servers\<대상 호스트> 키

| 값 | 내용 |
|---|---|
| `UsernameHint` | 사용자 이름 |

- 하위 키 이름이 대상 호스트입니다.
- 같은 키의 `CertHash` 값은 이번에 확인하지 못했습니다.

## 증거로서 의미

### 증명하는 것

- 이 계정의 원격 데스크톱 연결 목록에 이 대상이 있습니다. Microsoft 문서대로라면 이 계정에서 원격 데스크톱 연결로 이 대상에 접속한 적이 있습니다.
- MRU 번호로 목록 안에서 어느 대상이 더 최근인지 알 수 있습니다.
- `UsernameHint` 에서 그 대상 키에 적힌 사용자 이름을 알 수 있습니다.

### 증명하지 못하는 것

- **접속에 성공했는지.** Microsoft 문서는 접속한 뒤 목록에 추가된다고만 적습니다. 실패한 접속도 남는지는 확인하지 못했습니다.
- **언제 접속했는지.** MRU 값에는 시각이 없습니다. 아래 "시각 해석" 절을 봅니다.
- **몇 번 접속했는지.** 번호는 순서일 뿐 횟수가 아닙니다.
- **다른 방법으로 연 접속.** 다른 원격 제어 도구나 `.rdp` 파일을 더블클릭해서 연 접속이 MRU 에 남는지는 확인하지 못했습니다. 목록에 없다고 접속하지 않은 것은 아닙니다. 다른 원격 제어 도구는 [원격 제어 프로그램](remote-access-tools/index.md) 에서 다룹니다.
- **키보드 앞의 사람.** 하이브가 가리키는 것은 계정입니다. 사람을 좁히는 방법은 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

보고서에는 "이 계정의 원격 데스크톱 연결 목록에 이 대상이 MRU0 으로 남아 있고, 대상별 키의 사용자 이름 힌트는 이 이름이다" 처럼 씁니다.

## 시각 해석

MRU 값은 호스트 문자열뿐이라 시각이 없습니다. 공개 도구 RegRipper 의 tsclient 플러그인은 `Default` 키, `Servers` 키, 서버별 하위 키의 마지막 기록 시각 (LastWrite) 을 UTC(Z)로 함께 출력합니다.

- `Default` 키의 LastWrite 는 이 키가 마지막으로 바뀐 때이며, MRU 목록이 바뀐 때도 여기에 들어갑니다. 이 시각을 `MRU0` 에 마지막으로 접속한 때로 읽는 해석이 있습니다. 이번에 연 자료는 이 해석을 적지 않았습니다.
- `Servers\<대상 호스트>` 키의 LastWrite 를 그 대상에 마지막으로 접속한 때로 읽는 해석도 확인하지 못했습니다.
- 두 시각은 "이 무렵에 키가 바뀌었다" 로만 쓰고, 접속 시각은 [원격 데스크톱 이벤트](../event-logs/rdp-event-logs/index.md) 로 맞춰 봅니다.
- LastWrite 의 성질은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 함정과 한계

- **사용자가 지울 수 있습니다.** Microsoft 가 직접 레지스트리에서 지우는 방법을 안내합니다. 목록이 비어 있거나 번호가 이상하면 지운 흔적을 의심합니다.
- **지운 값은 다른 곳에서 찾습니다.** 지운 키와 값, 하이브 로그 반영은 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다. 이전 시점은 [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 봅니다. 조작 흔적을 찾는 흐름은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md) 에 있습니다.
- **LastWrite 는 목록 전체의 마지막 변경입니다.** `MRU1` 이하 대상의 접속 시각이 아닙니다.
- **HKLM 키와 헷갈리지 않습니다.** 원격 데스크톱 연결을 쓴 적이 없는 PC 에도 `HKLM\SOFTWARE\Microsoft\Terminal Server Client` 가 있었습니다. (확인 범위: Win11 25H2 한 대)
- **원격 데스크톱 연결 도구의 목록입니다.** 다른 원격 제어 도구의 접속은 여기 남지 않을 수 있습니다.
- **어느 계정의 하이브인지 먼저 확인합니다.** [사용자 프로필 목록](../system-account/profilelist.md) 으로 NTUSER.DAT 와 계정을 잇습니다.

## 직접 분석해 보기

### 헥스로 한 번

아래 바이트는 예시로 만든 값입니다. 특정 검체에서 꺼낸 값이 아닙니다.

**MRU0 값 데이터 (대상 `10.0.0.5` 로 만든 예시).**

```
오프셋  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
0x00    31 00 30 00 2E 00 30 00 2E 00 30 00 2E 00 35 00
```

1. REG_SZ 값은 UTF-16LE 문자열입니다. 두 바이트가 한 글자입니다.
2. `31 00` 은 `1`, `30 00` 은 `0`, `2E 00` 은 `.` 입니다.
3. 이어 읽으면 `10.0.0.5` 입니다.
4. 문자 인코딩은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md) 에서 다룹니다.

**MRU 번호가 밀리는 모습 (Microsoft 문서의 설명으로 만든 예시).**

| 값 | 접속 전 | `server3` 에 새로 접속한 뒤 |
|---|---|---|
| `MRU0` | `server2` | `server3` |
| `MRU1` | `server1` | `server2` |
| `MRU2` | — | `server1` |

- 이미 목록에 있는 대상에 다시 접속할 때 순서가 어떻게 바뀌는지는 확인하지 못했습니다.

### 공개 도구로 한 번

1. 사용자 프로필에서 NTUSER.DAT 와 하이브 로그를 함께 사본으로 뜹니다.
2. 레지스트리 뷰어로 `Software\Microsoft\Terminal Server Client` 를 엽니다.
3. `Default` 의 MRU 값과 `Servers` 아래 하위 키 이름, `UsernameHint` 를 적습니다.
4. RegRipper 의 tsclient 플러그인으로 같은 내용을 뽑고, 키마다 LastWrite(UTC)를 적습니다.
5. 도구 결과와 레지스트리 뷰어에서 직접 본 값이 같은지 한 번 맞춰 봅니다.

## 교차 검증

아래 흔적의 위치는 JPCERT/CC 의 mstsc 분석 자료를 따릅니다.

| 아티팩트 | 위치 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 원격 데스크톱 비트맵 캐시 | `C:\Users\<사용자>\AppData\Local\Microsoft\Terminal Server Client\Cache\bcache<번호>.bmc` | 원격 화면에서 받은 조각 | [원격 데스크톱 비트맵 캐시](rdp-bitmap-cache.md) |
| 접속 설정 파일 | `C:\Users\<사용자>\Documents\Default.rdp` | 접속 설정 | — |
| 프리페치 | `C:\Windows\Prefetch\MSTSC.EXE-<해시>.pf` | mstsc 실행 횟수와 시각 | [프리페치](../execution/prefetch/index.md) |
| 출발 쪽 이벤트 로그 | Security 로그 4648, RDPClient/Operational 로그 | 출발 PC 쪽 접속 기록 | [원격 데스크톱 이벤트](../event-logs/rdp-event-logs/index.md) |

- `Default.rdp` 가 숨김 파일인지는 확인하지 못했습니다.
- mstsc 의 [점프리스트](../file-folder-usage/jump-lists.md) 에 접속 대상이 남는지는 확인하지 못했습니다.
- 원격 데스크톱 연결을 쓴 적이 없는 Windows 11 PC 한 대에는 `Documents\Default.rdp` 와 `Cache` 폴더가 없었습니다. (확인 범위: Win11 25H2 한 대)

전체 흐름은 [원격 데스크톱 침입 확인](../../04-scenarios/incident/rdp-intrusion.md) 과 [계정 탈취와 측면 이동](../../04-scenarios/incident/credential-theft-lateral-movement/index.md) 에 있습니다.

## 실습

공개 검체(NIST CFReDS 등)에서 사용자 NTUSER.DAT 를 꺼내 아래 질문을 풀어 봅니다.

1. `Terminal Server Client\Default` 키가 있습니까? MRU 값은 몇 개입니까?
2. `MRU0` 의 대상은 무엇입니까? FQDN 입니까, IP 주소입니까?
3. `Servers` 아래 하위 키는 몇 개입니까? MRU 목록의 대상과 모두 겹칩니까?
4. 각 대상의 `UsernameHint` 는 무엇입니까?
5. `Default` 키의 LastWrite 는 언제입니까? 같은 무렵의 mstsc 프리페치 실행 시각과 비교해 봅니다.
6. 같은 사용자 프로필에 비트맵 캐시 파일이 있습니까?

## 참고 문헌

1. Microsoft Learn, *Remove entries from Remote Desktop Connection Computer* (KB 312169, 2026-02-12) (목록이 생기는 방식, 레지스트리 위치, MRU 번호 규칙과 값 형식, 도구에 삭제 기능이 없음, Mac 용 목록 파일). https://learn.microsoft.com/en-us/troubleshoot/windows-server/remote/remove-entries-from-remote-desktop-connection-computer
2. H. Carvey, *RegRipper3.0 plugin tsclient.pl* (20200518) (오프라인에서 읽는 키, `UsernameHint`, 키별 LastWrite 의 UTC 출력). https://raw.githubusercontent.com/keydet89/RegRipper3.0/master/plugins/tsclient.pl
3. JPCERT/CC, *Tool Analysis Result Sheet — mstsc* (`Servers\<대상>\UsernameHint`, `Default.rdp`·비트맵 캐시·프리페치 위치, 출발 쪽 이벤트 로그). https://jpcertcc.github.io/ToolAnalysisResultSheet/details/mstsc.htm
