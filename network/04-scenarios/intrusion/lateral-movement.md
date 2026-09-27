---
title: "내부에서 다른 PC 로 옮겨 갔나"
parent: "시나리오 · 침입"
nav_order: 460
---

# 내부에서 다른 PC 로 옮겨 갔나 (Lateral Movement)

침입자가 PC 한 대를 차지한 뒤에는 관리 공유에 파일을 올리고, 원격으로 서비스나 예약 작업을 만들고, 훔친 계정으로 다른 PC 에 로그인하면서 내부로 퍼집니다. 이 페이지에서는 Zeek 의 SMB·DCE-RPC·Kerberos·NTLM·RDP·SSH 로그와 Suricata 경보, 흐름 기록으로 "누가 어느 PC 에서 어느 PC 로 무엇을 했는지" 를 확인하는 순서를 다룹니다. 각 로그의 필드 설명은 아티팩트 페이지에 있고, 여기서는 어느 필드를 어떤 순서로 보는지만 씁니다.

## 조사 질문

- 이 내부 호스트가 다른 내부 호스트의 관리 공유(`ADMIN$`, `C$`)나 `IPC$` 에 붙었나?
- 공유에 실행 파일을 올렸나, 아니면 거기서 파일을 가져왔나?
- 서비스 생성, 예약 작업 등록, WMI 메서드 실행처럼 원격 실행에 쓰이는 RPC 호출이 있었나?
- 어떤 계정 이름으로 Kerberos 티켓을 받았거나 NTLM 인증을 했나?
- RDP·SSH 로 다른 내부 호스트에 들어갔나?
- 같은 출발지가 한 대에서 멈췄나, 여러 대로 이어졌나?

## 먼저 확인할 것

**센서가 내부 간 트래픽을 봤는지부터 확인합니다.** 인터넷 경계에 둔 센서는 같은 스위치 안의 PC 끼리 주고받은 패킷을 보지 못합니다. 캡처 지점이 어디였는지, 내부 구간(서버망·사용자망 사이)을 지나는 트래픽이 들어오는지 먼저 확인합니다. 캡처 지점별로 보이는 범위는 [어디서 캡처하나](../../01-foundations/capture/capture-points.md) 에 있습니다. 센서 로그에 `id.orig_h` 와 `id.resp_h` 가 둘 다 내부 주소인 conn.log 줄이 거의 없다면, 측면 이동이 없었다기보다 센서가 그 구간을 보지 못했을 가능성이 큽니다.

**센서 설정을 확인합니다.** 같은 트래픽이라도 설정에 따라 로그에 남는 양이 크게 다릅니다.

| 확인할 설정 | 기본값 | 해석에 주는 영향 |
|---|---|---|
| Zeek `SMB::logged_file_actions` | `PRINT_CLOSE`, `FILE_DELETE`, `FILE_OPEN`, `FILE_RENAME`, `PRINT_OPEN`[2] | `FILE_READ`·`FILE_WRITE` 가 기본 목록에 없어서, 공유에 파일을 쓴 동작이 smb_files.log 에 안 남을 수 있습니다. |
| BZAR 패키지 설치 여부 | 기본 설치 아님(`zkg install bzar` 로 설치)[1] | BZAR 가 있으면 관리 공유에 쓴 파일을 떼어 저장하고 notice.log 에 `ATTACK::` 로 시작하는 알림을 남깁니다[1]. |
| Zeek `DCE_RPC::ignored_operations` | spoolss·wkssvc 일부와 winreg 의 `BaseRegOpenKey`·`BaseRegQueryValue`·`BaseRegEnumKey` 등 여러 동작[3] | 원격 레지스트리를 읽은 흔적 일부가 dce_rpc.log 에 없습니다. |
| Zeek `Site::local_nets` | 정의하지 않으면 conn.log `local_orig`·`local_resp` 가 늘 비어 있음[10] | 이 값이 있어야 내부↔내부 연결을 필드 하나로 골라낼 수 있습니다. |
| Suricata `HOME_NET` / `EXTERNAL_NET` | `[192.168.0.0/16,10.0.0.0/8,172.16.0.0/12]` / `!$HOME_NET`[11] | `$EXTERNAL_NET -> $HOME_NET` 로 쓴 규칙은 내부 사이 트래픽에 걸리지 않습니다. Security Onion 은 내부 측면 이동을 잡으려고 `EXTERNAL_NET` 기본값을 `any` 로 둡니다[12]. |

**시각과 주소의 기준을 맞춥니다.** Zeek 로그의 `ts` 는 로그마다 뜻이 다릅니다. smb_mapping.log 는 공유(트리)를 연결한 시각, smb_files.log 는 파일을 처음 발견한 시각이고[2], dce_rpc.log·kerberos.log·ntlm.log·rdp.log 는 이벤트가 일어난 시각입니다[3][5][6][7]. ssh.log 는 SSH 연결이 시작된 시각입니다[9]. smb_files.log 의 `times.modified`·`times.accessed`·`times.created`·`times.changed` 는 센서 시계가 아니라 서버가 SMB 응답에 담아 보낸 파일 시스템 시각이라[2][23], 대상 PC 의 시계를 따릅니다. 로그 형식(TSV·JSON)과 UTC 여부는 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서 확인합니다. 내부 IP 가 DHCP 로 바뀌는 환경이면 그 시각에 그 IP 를 쓴 PC 를 [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md) 로 먼저 확인합니다.

## 볼 아티팩트와 순서

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| conn.log (또는 흐름 기록) | 내부↔내부 445/tcp(SMB), 135/tcp(RPC 엔드포인트 매퍼), 3389/tcp(RDP), 22/tcp(SSH) 연결의 출발지·목적지·시각·크기 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md), [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md) |
| smb_mapping.log | 어느 공유에 붙었는지(`path`), 공유 종류(`share_type` 이 `DISK` 또는 `PIPE`)[1][2] | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| smb_files.log | 공유 안에서 연 파일·파이프 이름(`name`), 동작(`action`), 크기, 이름 바꾸기 전 이름(`prev_name`)[2] | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| files.log · pe.log | SMB 로 오간 파일의 방향(`is_orig`)·MIME 형식·해시, 실행 파일의 컴파일 시각[1] | [files.log](../../02-artifacts/zeek/zeek-logs/files-log.md), [파일 꺼내기](../../03-techniques/analysis/file-extraction.md) |
| dce_rpc.log | 부른 RPC 인터페이스(`endpoint`)와 동작(`operation`)[3] | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| kerberos.log · ntlm.log | 인증에 쓴 계정 이름, 요청한 서비스, 성공 여부[5][6] | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| rdp.log · ssh.log | RDP 쿠키(대개 사용자 이름), SSH 인증 결과 추정[7][9] | [원격 프로토콜](../../01-foundations/protocols/remote-protocols.md) |
| notice.log (BZAR) · Suricata alert | 규칙이 측면 이동·원격 실행으로 분류한 사건[1] | [notice·weird 로그](../../02-artifacts/zeek/zeek-logs/notice-weird-log.md), [EVE alert](../../02-artifacts/suricata/eve-json/alert.md) |
| 원본 패킷(pcap) | 로그에 없는 RPC 인자, 응답 상태 코드 | [Wireshark·tshark 로 읽기](../../03-techniques/analysis/wireshark.md) |

## 분석 흐름

1. **내부↔내부 연결을 골라냅니다.** conn.log 에서 출발지와 목적지가 둘 다 내부 주소이고 목적지 포트가 445·135·3389·22 인 연결만 남깁니다. `Site::local_nets` 가 설정돼 있으면 `local_orig` 와 `local_resp` 가 둘 다 `T` 인 줄을 고르면 됩니다[10]. 출발지별로 목적지 수를 세어, 평소 서버에만 붙던 사용자 PC 가 여러 PC 의 445/tcp 에 붙기 시작한 시각을 찾습니다. SMB 연결의 conn.log `service` 에는 `smb`, `dce_rpc`, `krb`, `gssapi` 가 섞여 나올 수 있습니다[1]. TLS 로 암호화한 RDP 는 `service` 가 `ssl` 로 나옵니다[8].

2. **관리 공유에 붙었는지 봅니다.** smb_mapping.log 에서 `path` 가 `ADMIN$`·`C$`·`IPC$` 로 끝나는 줄을 찾습니다. 공유 이름은 `\\admin-pc\c$` 처럼 소문자로도, `\\admin-pc\ADMIN$` 처럼 대문자로도 남으므로[1] 소문자로 바꿔서 비교합니다.

   ```bash
   # JSON 형식 Zeek 로그 기준
   jq -c 'select(.path != null and (.path|ascii_downcase|test("\\\\(admin|c|ipc)\\$$")))
          | [.ts, ."id.orig_h", ."id.resp_h", .path, .share_type]' smb_mapping.log
   ```

   `share_type` 이 `DISK` 이면 파일 공유이고, `PIPE` 이면 `IPC$` 를 거쳐 명명된 파이프(원격 RPC 통로)를 쓰려는 연결입니다[1].

3. **공유 안에서 무엇을 열었는지 봅니다.** 같은 `uid` 의 smb_files.log 를 시간순으로 늘어놓습니다.

   ```bash
   jq -c '[.ts, .uid, .action, .path, .name, .size]' smb_files.log
   ```

   아래는 서비스 설치형 원격 실행 도구가 남기는 모양을 `[.action, .path, .name]` 세 필드만 뽑아 보인 것입니다(만든 예시, 순서는 PsExec 실행 기록을 따름[1]).

   ```text
   ["SMB::FILE_OPEN",  "\\\\ws-02\\ADMIN$", "SVCX.exe"]
   ["SMB::FILE_WRITE", "\\\\ws-02\\ADMIN$", "SVCX.exe"]
   ["SMB::FILE_WRITE", "\\\\ws-02\\ADMIN$", "SVCX.exe"]
   ["SMB::FILE_OPEN",  "\\\\ws-02\\ADMIN$", "SVCX.exe"]
   ["SMB::FILE_DELETE","\\\\ws-02\\ADMIN$", "SVCX.exe"]
   ```

   실행 파일을 열어 쓰고, 다시 연 뒤 지우는 순서입니다. PsExec 를 쓰면 `ADMIN$` 에 `PSEXESVC.exe` 가 이 순서로 남고[1], 실행 자체는 5단계의 `svcctl` 호출로 확인합니다. `IPC$` 에서 `name` 이 파이프 이름이면 어떤 원격 서비스를 불렀는지 알 수 있습니다. `atsvc` 는 예약 작업(At 서비스)이고[1], `PSEXESVC` 로 시작하지 않는데 `-stdin`·`-stdout`·`-stderr` 로 끝나는 파이프 이름은 서비스 이름을 바꾼 PsExec 류 도구의 흔적으로 봅니다[14]. `samr`·`lsarpc`·`winreg`·`srvsvc`·`svcctl`·`spoolss` 같은 흔한 파이프가 아닌 이름은 처음 보는 원격 파이프로 따로 확인합니다[16]. `name` 이 `\ntds.dit`·`\sam`·`\security`·`\lsass`·`\windows\minidump\` 같은 값이거나[18] `.kirbi`·`.dmp`·`.pst`·`.rdp` 로 끝나면[19] 자격 증명이나 민감한 자료를 옮겼을 가능성이 있습니다. `ADMIN$` 에서 `name` 에 `SYSTEM32\` 가 들어 있고 `.tmp` 로 끝나는 파일은 AD 자격 증명을 원격으로 빼내는 도구(Impacket secretsdump)가 남기는 모양입니다[20].

4. **파일이 어느 방향으로 갔는지 files.log 로 정합니다.** smb_files.log 만으로는 올렸는지 받았는지 알기 어려운 경우가 있습니다. 공유에서 파일을 받아 오면 smb_files.log 에 `FILE_OPEN` 두 줄만 남을 수 있는데, 이때 files.log 의 `is_orig` 가 `false` 이면 연결을 받은 쪽(대상 PC)이 연결을 연 쪽으로 파일을 보낸 것입니다[1]. `is_orig` 가 `true` 이면 연결을 연 쪽이 대상 PC 에 파일을 올린 것입니다[1]. 같은 줄의 `mime_type` 이 `application/x-dosexec` 이면 Windows 실행 파일이고, 해시와 pe.log 의 `compile_ts` 로 실행 파일을 특정합니다[1]. 떼어 낸 파일 다루는 법은 [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md) 에 있습니다.

5. **원격 실행 RPC 를 찾습니다.** dce_rpc.log 에서 아래 인터페이스·동작을 찾습니다. 이름은 Zeek 의 상수표에 있는 그대로입니다[4].

   | `endpoint` | `operation` | 뜻 |
   |---|---|---|
   | `svcctl` | `CreateServiceW`, `CreateServiceA`, `CreateServiceWOW64W`, `CreateServiceWOW64A`, `StartServiceW`, `StartServiceA` | 원격으로 서비스를 만들고 시작 |
   | `atsvc` | `NetrJobAdd` | At 서비스로 예약 작업 추가 |
   | `ITaskSchedulerService` | `SchRpcRegisterTask`, `SchRpcRun` | 작업 스케줄러에 작업 등록·실행 |
   | `IWbemServices` | `ExecMethod`, `ExecMethodAsync` | WMI 메서드 실행 |

   ```bash
   jq -c 'select(.endpoint=="svcctl" or .endpoint=="atsvc"
                 or .endpoint=="ITaskSchedulerService" or .endpoint=="IWbemServices")
          | [.ts, ."id.orig_h", ."id.resp_h", .named_pipe, .endpoint, .operation]' dce_rpc.log
   ```

   SMB 를 거치지 않고 TCP 로 곧바로 RPC 를 부르면 먼저 135/tcp 에서 `epmapper`·`ept_map` 이 나오고, 이어 대상 PC 의 동적 포트(예: 49155)에서 `svcctl` 의 `OpenSCManagerW` → `CreateServiceWOW64W` → `StartServiceW` → … → `DeleteService` 가 이어집니다[1]. 이때 `named_pipe` 에는 파이프 이름 대신 `135`·`49155` 같은 포트 번호가 들어갑니다[1][3].

6. **어떤 계정이었는지 봅니다.** SMB 연결 안에서 나온 kerberos.log 줄에는 연결 정보만 있고 계정 이름이 없는 경우가 많습니다[1]. 계정 이름은 같은 출발지가 비슷한 시각에 도메인 컨트롤러 88/tcp 로 보낸 TGS 요청에 남습니다. 서로 다른 연결이라 `uid` 가 다르므로 출발지 IP 와 시각으로 이어 붙입니다[1].

   ```json
   {"ts":1767225600.52,"id.orig_h":"10.0.5.21","id.resp_h":"10.0.0.10","id.resp_p":88,
    "request_type":"TGS","client":"user01/EXAMPLE.COM","service":"HOST/ws-02",
    "success":true,"cipher":"aes256-cts-hmac-sha1-96"}
   ```

   (만든 예시) 이 줄로 `user01` 계정이 `ws-02` 의 HOST 서비스 티켓을 받았다는 것을 알 수 있습니다. `cipher` 가 `rc4-hmac` 인 TGS 요청은 `service` 가 `$` 로 시작하지 않으면 따로 확인합니다[22]. NTLM 을 쓰는 환경에서는 ntlm.log 의 `username`·`domainname`·`hostname`(클라이언트가 스스로 밝힌 이름)과 `server_nb_computer_name`(대상 서버 이름)을 봅니다[6]. `success` 필드가 없는 줄도 나오므로[1], 필드가 비었다고 실패로 읽지 않습니다.

7. **RDP·SSH 로 들어갔는지 봅니다.** 내부↔내부 3389/tcp 연결은 rdp.log 의 `cookie`(대개 사용자 이름이지만 전송 중 최대 9자로 잘림)와 `client_name` 을 봅니다[7]. 암호화된 RDP 는 rdp.log `result` 가 `encrypted` 로만 남아 로그인 성공 여부를 알 수 없으므로[8], conn.log 에서 짧고 크기가 같은 연결이 반복되다가 길고 큰 연결이 하나 나오는 모양을 봅니다. 이 모양의 해석은 [비밀번호를 무작위로 넣어 봤나](brute-force.md) 에 있습니다. 22/tcp 는 ssh.log 의 `auth_success`(T 성공, F 실패, 비어 있으면 알 수 없음)를 보되[9], `direction` 필드는 로컬 호스트와 외부 호스트 사이의 방향만 정의돼 있어[9] 내부 사이 연결에서 어떤 값이 찍히는지는 실제 로그로 확인합니다.

8. **경보와 맞춰 봅니다.** BZAR 가 설치돼 있으면 notice.log 에 `ATTACK::Lateral_Movement`(관리 공유에 `FILE_WRITE`), `ATTACK::Lateral_Movement_Extracted_File`(쓴 파일을 떼어 저장함), `ATTACK::Execution`(`svcctl::CreateServiceWOW64W` 같은 원격 실행), `ATTACK::Lateral_Movement_and_Execution`(한 대상 호스트에 대한 점수 합계, 10분 창)이 남습니다[1]. 경보가 이 흐름과 맞는지 확인하고, 경보가 없더라도 1~7단계의 로그로 판단합니다. Sigma 규칙을 쓰는 법은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) 에 있습니다.

9. **원본 패킷에서 인자를 확인합니다.** 로그에 없는 내용은 pcap 으로 봅니다. At 서비스 요청은 tshark 에 `-O atsvc` 를 주고 `JobAdd` 요청 프레임을 열면 예약한 명령 경로(`Command`)가 보이고, 응답의 `NT Error: STATUS_SUCCESS (0x00000000)` 로 작업이 등록됐는지 알 수 있습니다[1]. 반면 `svcctl` 요청은 `Encrypted stub data` 로만 보일 수 있고, 그러면 서비스 이름이나 실행 명령을 읽을 수 없습니다[1]. SMB2 응답 헤더의 4바이트 상태 필드가 0 이면 성공입니다[23].

10. **호스트 기록과 시간순으로 합칩니다.** 네트워크 기록으로는 "무엇을 부르고 무엇을 옮겼는가" 까지 알 수 있습니다. 서비스가 실제로 실행됐는지, 어떤 프로세스가 떴는지는 대상 PC 의 이벤트 로그로 확인합니다. Windows 쪽은 [계정 탈취와 측면 이동](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/credential-theft-lateral-movement/) 에, 합치는 방법은 [네트워크 타임라인](../../03-techniques/analysis/timeline.md) 에 있습니다. 옮겨 간 PC 에서 다시 다른 PC 로 이어졌는지 1단계부터 되풀이합니다.

## 흔한 오판

**dce_rpc.log 가 없으니 원격 실행도 없었다.** At 서비스로 작업을 등록한 연결에서 conn.log `service` 가 `dce_rpc,smb` 인데도 dce_rpc.log 가 생기지 않고, smb_files.log 에 `name` 이 `atsvc` 인 `FILE_OPEN`·`FILE_WRITE` 만 남는 경우가 있습니다[1]. 이 줄에는 `path` 필드도 없습니다[1]. dce_rpc.log 가 비어도 smb_files.log 의 파이프 이름을 봅니다.

**smb_files.log 에 `FILE_WRITE` 가 없으니 파일을 올리지 않았다.** `FILE_WRITE` 는 기본 기록 동작이 아닙니다[2]. Zeek 문서 예시에서 `FILE_WRITE` 줄이 남은 캡처는 모두 BZAR 를 설치한 상태로 처리했습니다[1]. 센서 설정을 확인하고, 방향은 files.log `is_orig` 로 판단합니다.

**경보가 하나도 없으니 측면 이동이 없었다.** 기본 Suricata 설정의 `EXTERNAL_NET` 은 `!$HOME_NET` 이라 내부 사이 트래픽을 외부 출발로 가정한 규칙은 걸리지 않습니다[11]. RITA 기본 설정은 내부↔내부 연결을 가져올 때 버리므로[13] 측면 이동 분석에 그대로 쓰면 빈 결과가 나옵니다. 센서가 내부 구간을 보지 못했을 수도 있습니다.

**Sigma 규칙이 걸리지 않았으니 해당 행위가 없었다.** Sigma 의 BZAR 실행 규칙에는 `endpoint: 'JobAdd'`, `operation: 'atsvc'` 조건이 있는데[17], 이 값은 Zeek 가 실제로 남기는 `endpoint: atsvc`, `operation: NetrJobAdd`[4] 와 자리와 이름이 다릅니다. 같은 규칙의 `svcctl` 조건에는 `CreateServiceA`·`CreateServiceW`·`StartServiceA`·`StartServiceW` 만 있어[17] PsExec 실행에서 나오는 `CreateServiceWOW64W`[1] 는 걸리지 않고 `StartServiceW` 만 걸립니다. `path` 조건도 규칙마다 `\IPC$` 포함[14], `\\\*\IPC$` 일치[15] 처럼 적는 방식이 달라서, 실제 로그의 `path` 문자열(JSON 에서는 `"\\\\admin-pc\\IPC$"`[1])과 맞는지 먼저 확인합니다.

**`svcctl` 호출이 있으니 서비스가 실행됐다.** `CreateService`·`StartService` 호출 기록으로는 요청이 오갔다는 사실까지만 알 수 있습니다. 요청 내용이 암호화돼 있으면 서비스 이름·명령·결과를 패킷으로도 읽을 수 없습니다[1]. 실행 여부는 대상 PC 의 기록으로 확인합니다.

**`named_pipe` 값이 이상하다.** 이 필드는 프로토콜의 보조 주소(sec_addr) 값이라 파이프 이름 대신 포트 번호가 들어갈 수 있습니다[3].

**관리 공유 접속은 모두 공격이다.** 관리자 작업, 관리 스크립트, 백업 소프트웨어도 같은 흔적을 남깁니다[17][18][19]. 도메인 컨트롤러가 프린터 서버를 겸하면 `spoolss` 파이프 사용도 흔합니다[21]. 평소 그 출발지가 그 대상에 같은 동작을 했는지 이전 기간 로그와 비교합니다.

**kerberos.log `client` 나 rdp.log `cookie` 에 나온 이름이 그 사람이다.** 로그에 남는 것은 계정 이름이고, 그 계정을 누가 쓰고 있었는지는 알 수 없습니다. `cookie` 는 9자로 잘릴 수 있습니다[7].

## 증명하는 것 / 증명하지 못하는 것

네트워크 기록으로 증명할 수 있는 것은 이 시간대에 내부 호스트 A 가 내부 호스트 B 의 어느 공유에 붙었고, 어떤 이름의 파일·파이프를 열고 쓰고 지웠으며, 어떤 RPC 인터페이스의 어떤 동작을 불렀고, 어떤 계정 이름의 Kerberos 티켓·NTLM 인증이 오갔는지입니다. files.log 가 있으면 파일이 어느 방향으로 얼마나 오갔는지와 해시까지 확인됩니다.

증명하지 못하는 것은 원격으로 실행한 명령의 내용(요청이 암호화된 경우), 서비스·작업이 실제로 실행되고 성공했는지, 그 계정을 실제로 쓴 사람입니다. 이것들은 대상 PC 의 이벤트 로그와 파일 시스템 기록이 있어야 확인됩니다. 센서가 보지 못한 구간에서 일어난 이동은 네트워크 기록에 아예 없습니다.

## 보고서 문장 예

아래 문장의 주소·이름·시각은 모두 만든 예시입니다.

- 2026-01-01 00:00:00~00:00:02(UTC)에 10.0.5.21 이 10.0.5.32 의 445/tcp 로 연결해 `\\ws-02\ADMIN$` 공유를 연결하고 `SVCX.exe` 를 열고, 쓰고, 지운 기록이 Zeek smb_files.log 에 있다.
- 같은 시간대에 10.0.5.21 이 10.0.5.32 의 동적 포트로 `svcctl` 인터페이스의 `CreateServiceWOW64W` 와 `StartServiceW` 를 호출한 기록이 dce_rpc.log 에 있다. 요청 내용은 암호화돼 있어 서비스 이름과 실행 명령은 네트워크 기록으로 확인되지 않는다.
- 직전 00:00:00(UTC)에 10.0.5.21 이 도메인 컨트롤러 10.0.0.10 에 `user01/EXAMPLE.COM` 계정으로 `HOST/ws-02` 서비스 티켓을 요청해 성공한 기록이 kerberos.log 에 있다. 이 기록으로 계정 이름은 확인되지만 계정을 사용한 사람은 확인되지 않는다.
- files.log 에서 이 연결로 10.0.5.21 에서 10.0.5.32 로 옮겨진 실행 파일(`is_orig: true`, `application/x-dosexec`)의 SHA-256 이 확인되며, 대상 PC 에서 실행됐는지는 해당 PC 의 이벤트 로그로 확인해야 한다.

## 함께 볼 페이지

- [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) · [conn.log](../../02-artifacts/zeek/zeek-logs/conn-log.md) · [files.log](../../02-artifacts/zeek/zeek-logs/files-log.md) · [notice·weird 로그](../../02-artifacts/zeek/zeek-logs/notice-weird-log.md)
- [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)
- [SMB와 원격 관리 프로토콜](../../01-foundations/protocols/remote-protocols.md)
- [어디서 캡처하나](../../01-foundations/capture/capture-points.md) · [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md)
- [흐름 기록 분석](../../03-techniques/analysis/flow-analysis.md) · [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) · [네트워크 타임라인](../../03-techniques/analysis/timeline.md)
- [악성 코드가 C2 서버와 통신했나](c2-communication.md) · [비밀번호를 무작위로 넣어 봤나](brute-force.md) · [자료를 밖으로 보냈나](../exfiltration/data-exfiltration.md)
- [VPN 서버 로그](../../02-artifacts/devices/vpn-logs.md) — 원격 접속 사용자가 내부로 옮겨 간 경우
- Windows 핸드북: [계정 탈취와 측면 이동](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/credential-theft-lateral-movement/) · [원격 데스크톱 이벤트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/event-logs/rdp-event-logs/) · [원격 데스크톱 침입 확인](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/rdp-intrusion.html) · [공유 폴더·네트워크 드라이브](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/network-shares-mapped-drives.html)
- Linux 핸드북: [SSH](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/ssh/) · [SSH 로 들어왔나](https://urock-ailab.github.io/forensics-handbook/linux/04-scenarios/intrusion/ssh-intrusion.html)

## 참고 문헌

1. Zeek Documentation, "SMB Logs (plus DCE-RPC, Kerberos, NTLM)". https://github.com/zeek/zeek-docs/blob/master/logs/smb.rst
2. Zeek Documentation, base/protocols/smb/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smb/main.zeek.rst
3. Zeek Documentation, base/protocols/dce-rpc/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dce-rpc/main.zeek.rst
4. Zeek Documentation, base/protocols/dce-rpc/consts.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dce-rpc/consts.zeek.rst
5. Zeek Documentation, base/protocols/krb/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/krb/main.zeek.rst
6. Zeek Documentation, base/protocols/ntlm/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ntlm/main.zeek.rst
7. Zeek Documentation, base/protocols/rdp/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/rdp/main.zeek.rst
8. Zeek Documentation, "RDP Logs". https://github.com/zeek/zeek-docs/blob/master/logs/rdp.rst
9. Zeek Documentation, base/protocols/ssh/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssh/main.zeek.rst
10. Zeek Documentation, base/protocols/conn/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
11. OISF Suricata, suricata.yaml.in. https://github.com/OISF/suricata/blob/main/suricata.yaml.in
12. Security Onion Documentation, "Suricata". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/suricata.rst
13. Active Countermeasures RITA, default_config.hjson. https://github.com/activecm/rita/blob/main/default_config.hjson
14. SigmaHQ, zeek_smb_converted_win_susp_psexec.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_smb_converted_win_susp_psexec.yml
15. SigmaHQ, zeek_smb_converted_win_atsvc_task.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_smb_converted_win_atsvc_task.yml
16. SigmaHQ, zeek_smb_converted_win_lm_namedpipe.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_smb_converted_win_lm_namedpipe.yml
17. SigmaHQ, zeek_dce_rpc_mitre_bzar_execution.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dce_rpc_mitre_bzar_execution.yml
18. SigmaHQ, zeek_smb_converted_win_transferring_files_with_credential_data.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_smb_converted_win_transferring_files_with_credential_data.yml
19. SigmaHQ, zeek_smb_converted_win_susp_raccess_sensitive_fext.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_smb_converted_win_susp_raccess_sensitive_fext.yml
20. SigmaHQ, zeek_smb_converted_win_impacket_secretdump.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_smb_converted_win_impacket_secretdump.yml
21. SigmaHQ, zeek_dce_rpc_smb_spoolss_named_pipe.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dce_rpc_smb_spoolss_named_pipe.yml
22. SigmaHQ, zeek_susp_kerberos_rc4.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_susp_kerberos_rc4.yml
23. Jan-Niclas Hilgert, Axel Mahr, Martin Lambertz, "Mount SMB.pcap: Reconstructing file systems and file operations from network traffic", Forensic Science International: Digital Investigation, 2024. doi:10.1016/j.fsidi.2024.301807
