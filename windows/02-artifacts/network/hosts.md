---
title: "hosts 파일"
parent: "아티팩트 · 네트워크"
nav_order: 2460
---

# hosts 파일 (hosts)

> 이 페이지의 기본 값은 Windows 11 Home 25H2(빌드 26200.9457) 기준입니다. 다른 버전에서는 값이 다를 수 있습니다.

hosts 는 호스트 이름과 IP 주소를 한 줄에 짝지어 적는 텍스트 파일입니다. 기본 파일은 모든 줄이 주석입니다. 주석이 아닌 줄이 있으면 설치 뒤 누군가 이름과 주소를 짝지어 두었다는 단서입니다. 파일 안에는 시각이 없어서, 언제 고쳤는지는 파일 시스템 기록으로 추정합니다.

## 무엇을 기록하나 · 왜 생기나

hosts 는 로그가 아니라 설정 파일이며, 관리자나 프로그램이 이름을 특정 주소로 보내려고 줄을 적어 넣습니다. 기본 파일은 윈도 설치 이미지에 들어 있습니다.

이 파일로 아래 질문에 답합니다.

- 어떤 이름을 어느 주소로 짝지어 두었나
- 기본 파일에서 바뀌었나
- 바뀌었다면 언제쯤인가

윈도가 이름을 풀 때 hosts 를 DNS 보다 먼저 본다는 설명이 흔합니다. 이 페이지는 그 순서가 아니라 파일에 무엇이 적혀 있는지와 그 해석을 다룹니다.

## 위치와 버전별 차이

| 항목 | 위치 | 메모 |
|---|---|---|
| hosts | `%SystemRoot%\System32\drivers\etc\hosts` | 기본 위치입니다[1]. 확장자가 없습니다 |
| Lmhosts | 같은 폴더 | hosts 와 함께 수집 대상입니다[1] |
| 같은 폴더의 다른 파일 | `lmhosts.sam`(예시 파일), `networks`, `protocol`, `services` | 기본 설치에는 확장자 없는 `lmhosts` 가 없습니다 |
| 폴더 경로 설정 | SYSTEM `CurrentControlSet\Services\Tcpip\Parameters` 의 `DataBasePath` | 기본 값은 `C:\WINDOWS\System32\drivers\etc` 입니다 |

- `DataBasePath` 값이 기본 폴더와 다르면 그 폴더의 hosts 도 함께 봅니다.
- 오프라인 SYSTEM 하이브에서는 `Select` 키가 가리키는 `ControlSet00n` 을 읽습니다. 하이브 구조는 [레지스트리 하이브 구조](../../01-foundations/database-log-formats/registry-hive/index.md)에서 다룹니다.
- 기본 파일의 첫 줄은 `# Copyright (c) 1993-2009 Microsoft Corp.` 입니다.

## 구조

### 형식

기본 파일 주석에 적힌 규칙은 이렇습니다.

- 한 줄에 항목 하나를 씁니다.
- IP 주소를 첫 필드에 쓰고, 호스트 이름을 다음 필드에 씁니다.
- 두 필드 사이는 공백 하나 이상으로 띄웁니다.
- `#` 뒤는 주석입니다. 줄 앞에도, 항목 뒤 줄 끝에도 붙일 수 있습니다.

### 기본 내용

- 기본 파일은 824바이트이고, 인코딩은 ASCII, 줄바꿈은 CRLF 입니다. 모든 줄이 `#` 로 시작하는 주석입니다.
- 주석 안에 예시 줄이 두 개 있으며, `#` 뒤에 아래 내용이 적혀 있습니다. 줄 앞에 `#` 이 있어 쓰이지 않는 줄입니다.

```
102.54.94.97     rhino.acme.com          # source server
38.25.63.10     x.acme.com              # x client host
```

- 파일 끝에는 `# localhost name resolution is handled within DNS itself.` 줄이 있습니다. 그 아래 `127.0.0.1 localhost` 와 `::1 localhost` 도 주석 처리돼 있습니다.

### 권한

| 대상 | 권한 |
|---|---|
| SYSTEM, Administrators | 전체 제어 |
| Users, ALL APPLICATION PACKAGES | 읽기·실행 |



파일을 고치려면 관리자 권한이 필요합니다. 권한이 위와 다르면 권한을 바꾼 흔적으로 따로 봅니다.

## 증거로서 의미

**증명하는 것**

- 주석이 아닌 줄 하나는 수집 시점에 그 이름을 그 주소로 짝지어 두었다는 기록입니다.
- 기본 파일은 모든 줄이 주석입니다. 그래서 주석이 아닌 줄은 설치 뒤에 누군가 넣었을 가능성이 높습니다.
- 파일 수정 시각이 윈도 설치 시각보다 뒤라면 설치 뒤 누군가 파일을 고쳤을 가능성이 있습니다.
- 권한이 기본과 같다면 파일을 고친 쪽은 관리자나 SYSTEM 권한으로 실행됐을 가능성이 높습니다.

**증명하지 못하는 것**

- 줄이 있다고 그 이름으로 실제 접속했다는 뜻은 아닙니다.
- 줄마다 언제 넣었는지 알려 주지 않습니다.
- 누가 고쳤는지 알려 주지 않습니다.
- 윈도가 실제로 이 파일로 이름을 풀었는지는 이 파일만으로 알 수 없습니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "hosts 파일에 주석이 아닌 줄 한 개(`<주소> <이름>`)가 있다. 파일의 마지막 수정 시각은 … UTC 로 윈도 설치 시각보다 뒤이다. 줄을 넣은 계정과 시각은 이 파일만으로 알 수 없다." 처럼 씁니다.

## 시각 해석

- 파일 안에는 줄마다 시각이 없습니다. 언제 줄을 넣었는지는 파일 시스템 시각과 USN 저널로만 추정합니다.
- 2026-06-26T18:07:41Z 에 설치한 Windows 11 Home 25H2 에서 hosts 수정 시각은 2024-04-01T07:24:05Z 입니다. 수정 시각이 설치보다 2년 넘게 앞서고, 같은 폴더의 다른 파일도 수정 시각이 같습니다.
- 즉 손대지 않은 hosts 의 수정 시각은 설치한 날이 아니라 윈도 설치 이미지를 만든 무렵의 시각으로 보입니다.
- 같은 폴더의 다른 파일과 수정 시각을 나란히 봅니다. hosts 만 시각이 다르면 hosts 만 따로 고쳤다는 단서가 됩니다.
- NTFS 시각은 UTC 입니다. 파일 시각을 읽는 법은 [마스터 파일 테이블](../filesystem/mft.md)에서 다룹니다. 설치 시각은 [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md)에서 확인합니다.
- 수정 시각은 마지막으로 고친 때 하나뿐이라서, 여러 번 고쳤다면 앞선 수정 시각은 [USN 변경 저널](../filesystem/usnjrnl.md)이나 [섀도 복사본](../../03-techniques/analysis/volume-shadow-copy-analysis.md) 속 예전 파일에서 찾습니다.

## 함정과 한계

1. **줄 끝 주석을 잘라 읽습니다.** 항목 뒤에 `#` 주석이 붙을 수 있습니다. 주석까지 이름으로 읽으면 안 됩니다.
2. **필드 사이 공백이 하나가 아닐 수 있습니다.** 공백 여러 개로 띄운 줄이 기본 파일에도 있습니다. 공백 한 개로만 나누면 필드가 어긋납니다.
3. **설치 이미지 시각을 설치 시각으로 읽지 않습니다.** 기본 파일의 수정 시각은 설치 시각보다 앞설 수 있습니다.
4. **파일 시스템 시각은 바꿀 수 있습니다.** 수정 시각 하나만 보고 판단하지 않습니다. USN 저널과 함께 봅니다. 시각 조작을 가려내는 법은 [증거를 없애려 했나](../../04-scenarios/activity/anti-forensics/index.md)에서 다룹니다.
5. **지금 내용이 예전 내용과 같다는 보장이 없습니다.** 줄을 넣었다가 지웠을 수 있습니다. 섀도 복사본 속 예전 hosts 와 비교합니다.
6. **같은 폴더의 다른 파일도 봅니다.** Lmhosts 도 수집 대상입니다[1]. 기본 설치에는 예시 파일 `lmhosts.sam` 만 있습니다.
7. **흔히 듣는 설명도 따로 확인합니다.** 아래 설명은 흔히 듣지만 이 페이지의 참고 문헌에는 근거가 없습니다. 보고서에 쓰려면 실제 데이터로 따로 확인합니다.
   - 윈도가 이름을 풀 때 hosts 를 DNS 보다 먼저 본다는 순서
   - hosts 항목이 DNS 클라이언트 캐시(`ipconfig /displaydns`)에 나타난다는 점
   - Microsoft Defender 가 hosts 변조를 탐지한다는 점과 탐지 이름
   - 악성코드가 보안 업데이트 서버 이름을 127.0.0.1 로 돌려 막는다는 사례

## 직접 분석해 보기

### 헥스로 한 번

아래는 기본 파일 형식(ASCII, CRLF)대로 만든 예시입니다. 실제 기기에서 뽑은 바이트가 아닙니다.

기본 파일의 첫 줄 `# Copyright (c) 1993-2009 Microsoft Corp.` 는 이렇게 시작합니다.

```
00  23 20 43 6F 70 79 72 69 67 68 74 20 28 63 29 20   # Copyright (c)
```

- 첫 바이트가 `23`(`#`)입니다. 앞에 BOM 이 없습니다.
- 파일이 `EF BB BF` 나 `FF FE` 로 시작하면 기본 파일과 인코딩이 다릅니다. 다른 편집기로 다시 저장했을 가능성을 봅니다. 인코딩을 판별하는 법은 [문자 인코딩](../../01-foundations/value-decoding/utf-16le-utf-8-cp949.md)에서 다룹니다.

기본 파일의 예시 줄에서 `#` 을 떼고 공백을 하나로 줄이면 쓰이는 줄이 됩니다. 그 줄은 바이트로 이렇게 보입니다.

```
00  31 30 32 2E 35 34 2E 39 34 2E 39 37 20 72 68 69   102.54.94.97 rhi
10  6E 6F 2E 61 63 6D 65 2E 63 6F 6D 0D 0A            no.acme.com..
```

1. `31 30 32 2E 35 34 2E 39 34 2E 39 37` 은 주소 `102.54.94.97` 입니다.
2. `20` 은 필드를 나누는 공백입니다.
3. `72 68 69 6E 6F 2E 61 63 6D 65 2E 63 6F 6D` 는 이름 `rhino.acme.com` 입니다.
4. `0D 0A` 는 CRLF 줄바꿈입니다.
5. 줄 첫 바이트가 `23`(`#`)이 아니므로 주석이 아닌 줄입니다.

### 공개 도구로 한 번

수집한 hosts 에서 주석이 아닌 줄만 뽑습니다. 파일 크기와 앞 바이트도 함께 봅니다.

```python
path = r"E:\mount\Windows\System32\drivers\etc\hosts"   # 마운트한 경로로 바꿉니다
data = open(path, "rb").read()
print("크기:", len(data), "바이트")          # 조사 PC 기본 파일은 824바이트였습니다
print("앞 4바이트:", data[:4].hex(" "))      # BOM 이 있는지 봅니다
for no, line in enumerate(data.decode("utf-8-sig", "replace").splitlines(), 1):
    body = line.split("#", 1)[0].strip()    # '#' 뒤는 주석입니다
    if body:
        ip, *names = body.split()           # 공백 여러 개도 한 번에 나눕니다
        print(f"{no}줄: {ip} -> {' '.join(names)}")
```

- 출력이 없으면 주석이 아닌 줄이 없습니다.
- 크기가 기본 파일과 달라도 바뀐 것이 주석뿐일 수 있습니다. 출력된 줄로 판단합니다.
- 파일 시각을 읽는 법은 [마스터 파일 테이블](../filesystem/mft.md)에서 다룹니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 마스터 파일 테이블 | hosts 와 같은 폴더 파일들의 시각 | [마스터 파일 테이블](../filesystem/mft.md) |
| USN 변경 저널 | hosts 에 쓴 기록과 그 시각 | [USN 변경 저널](../filesystem/usnjrnl.md) |
| 섀도 복사본 | 예전 hosts 내용 | [섀도 복사본 활용](../../03-techniques/analysis/volume-shadow-copy-analysis.md) |
| 라이브 응답 | 수집 시점의 DNS 캐시와 연결 목록 | [라이브 응답](../../03-techniques/process-acquisition/live-response/index.md) |
| Sysmon 로그 | 이름 조회와 연결 기록 | [Sysmon 로그](../event-logs/sysmon/index.md) |
| 크롬 계열 브라우저 | hosts 에 적힌 이름을 방문한 기록 | [크롬 계열 브라우저](../browsers/chrome-edge-whale/index.md) |
| 디펜더 검사 로그 | 같은 시기에 탐지 기록이 있는지 | [디펜더 검사 로그·격리 파일](../execution/mplog-detectionhistory-quarantine.md) |
| PowerShell 명령 기록 | hosts 를 고친 명령이 남았는지 | [PowerShell 명령 기록](../execution/consolehost-history-txt.md) |
| 시스템 기본 정보 | 윈도 설치 시각 | [시스템 기본 정보](../system-account/os-version-computer-name-install-date-shutdown-t.md) |

hosts 변경을 침해 흐름 안에서 보는 법은 [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md)에서 다룹니다. 방문 기록과 맞춰 보는 법은 [웹 사용 행위 재구성](../../04-scenarios/activity/web-activity.md)에서 다룹니다.

## 실습

공개 시험 이미지(NIST CFReDS 등) 가운데 윈도 이미지를 골라 아래 질문을 풀어 봅니다.

1. hosts 의 크기와 인코딩은 무엇입니까? 앞에 BOM 이 있습니까?
2. 주석이 아닌 줄이 있습니까? 어떤 이름을 어느 주소로 짝지었습니까?
3. hosts 의 수정 시각은 같은 폴더의 `networks`·`protocol`·`services` 와 같습니까?
4. 수정 시각은 윈도 설치 시각보다 앞입니까, 뒤입니까?
5. USN 저널에 hosts 에 쓴 기록이 있습니까? 그 시각에 어떤 프로그램이 실행됐습니까?
6. SYSTEM 하이브의 `DataBasePath` 는 기본 폴더를 가리킵니까?

## 참고 문헌

1. ForensicArtifacts/artifacts, artifacts/data/windows.yaml (main, 커밋 b4108448). https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/windows.yaml
