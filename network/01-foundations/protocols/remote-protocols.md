---
title: "SMB와 원격 관리 프로토콜"
parent: "기반 · 프로토콜 기초"
nav_order: 90
---

# SMB와 원격 관리 프로토콜 (SMB·RDP·SSH)

SMB·RDP·SSH 는 내부 PC 끼리 파일을 주고받거나 다른 PC 의 화면·셸을 원격으로 다루는 프로토콜이라서 측면 이동과 원격 침입 조사에서 가장 자주 만납니다. 세 프로토콜은 암호화 정도가 달라 캡처에서 보이는 정보도 다릅니다. 암호화하지 않은 SMB 는 공유 이름·파일 이름·원격 호출까지 드러나지만, RDP 와 SSH 는 대부분 협상 단계만 보입니다. 이 페이지는 선 위에서 각 프로토콜을 알아보는 바이트와, Zeek·Suricata 가 남기는 필드를 어떻게 읽는지 다룹니다.

## 이 형식을 쓰는 아티팩트

SMB2·SMB3 는 모든 방언(dialect)이 Direct TCP 위에서 동작하고, 2.0.2·2.1·3.0·3.0.2 는 NetBIOS over TCP, 3.1.1 은 QUIC 위에서도 동작합니다[1]. 조사에서는 주로 445/tcp 연결로 만나고, Zeek 문서의 NTLM 예시에는 139/tcp 연결도 나옵니다[4]. RDP 의 기본 포트는 3389/tcp 이지만 관리자가 다른 포트로 바꿀 수 있습니다[11]. SSH 서버는 보통 22/tcp 에서 연결을 받습니다[13].

세 프로토콜의 흔적은 아래 기록에 남습니다.

| 기록 | SMB | RDP | SSH |
|---|---|---|---|
| 패킷 캡처 | 암호화하지 않은 SMB 는 헤더·명령·파일 이름·데이터 전부 | 연결 요청(쿠키·요청 보안 프로토콜)과 TLS 핸드셰이크 | 식별 문자열과 키 교환 전 알고리즘 목록 |
| Zeek | `smb_mapping.log`, `smb_files.log`, `dce_rpc.log`, `ntlm.log`, `kerberos.log`, `files.log`, `pe.log`, 패키지에 따라 `notice.log`[4] | `rdp.log`, TLS 를 쓰면 `ssl.log`·`x509.log`[11] | `ssh.log`[14] |
| Suricata EVE | `smb` 기록(`dcerpc` 하위 객체 포함)[8] | `rdp` 기록(협상 단계마다 한 줄)[8] | `ssh` 기록(`client`·`server` 객체)[8] |
| 흐름 기록 | 445·139 포트 흐름의 바이트 수와 시각 | 3389 등 포트 흐름 | 22 등 포트 흐름 |

Zeek 는 SMB 연결을 보면 `conn.log` 의 `service` 에 `gssapi,smb,dce_rpc,krb` 처럼 여러 프로토콜을 함께 적습니다. `gssapi` 는 GSS-API(Generic Security Service API), 곧 인증과 관련된 값이고 `gssapi` 라는 이름의 로그는 생기지 않습니다[4]. Zeek 로그 전체 구조는 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)에서, EVE 공통 필드는 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에서 다룹니다. 호스트에 남는 기록은 [Windows 공유 폴더·네트워크 드라이브](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/network-shares-mapped-drives.html), [Windows 원격 데스크톱 이벤트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/event-logs/rdp-event-logs/), [Linux SSH](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/logins/ssh/) 페이지에 있습니다.

## 구조 — 표와 오프셋

### SMB2 — Direct TCP 헤더와 SMB2 헤더

Direct TCP 로 보낼 때는 TCP 페이로드 앞에 4바이트 헤더가 붙습니다. 첫 바이트는 반드시 0x00 이고, 뒤 3바이트는 뒤따르는 SMB2 메시지 길이를 네트워크 바이트 순서(빅 엔디언)로 적습니다. 이 길이에 4바이트 헤더 자신은 들어가지 않습니다[1].

그 뒤에 오는 SMB2 헤더(SYNC 형식)는 64바이트입니다[2].

| 오프셋 | 크기 | 필드 | 값과 뜻 |
|---|---|---|---|
| 0 | 4 | ProtocolId | 0x424D53FE. 네트워크에서는 `FE 53 4D 42`(0xFE, 'S', 'M', 'B') 순서로 나옵니다 |
| 4 | 2 | StructureSize | 64 |
| 6 | 2 | CreditCharge | 이 요청이 쓰는 크레딧 수. 2.0.2 방언에서는 0 |
| 8 | 4 | (ChannelSequence, Reserved) / Status | 응답에서는 NT 상태 코드. 요청에서는 3.x 가 ChannelSequence 로 씁니다 |
| 12 | 2 | Command | 명령 코드(아래 표) |
| 14 | 2 | CreditRequest / CreditResponse | 요청하거나 내준 크레딧 수 |
| 16 | 4 | Flags | 아래 표 |
| 20 | 4 | NextCommand | 여러 명령을 묶은 복합 요청에서 다음 헤더까지의 거리. 마지막이면 0 |
| 24 | 8 | MessageId | 같은 연결에서 요청과 응답을 짝짓는 번호 |
| 32 | 4 | Reserved | 클라이언트는 0 으로 씁니다(SHOULD) |
| 36 | 4 | TreeId | 어느 공유 연결(tree connect)에 대한 명령인지. TREE_CONNECT 요청에서는 0 |
| 40 | 8 | SessionId | 인증된 세션 번호. NEGOTIATE 요청·응답에서는 0 |
| 48 | 16 | Signature | SIGNED 플래그가 있을 때의 서명. 서명하지 않으면 0 |

위 표는 `Flags` 필드에 ASYNC_COMMAND 비트가 꺼져 있을 때의 동기(SYNC) 형식이고, 이 비트가 켜져 있으면 헤더가 비동기(ASYNC) 형식이라 표와 다릅니다[2].

| Command | 이름 | | Command | 이름 |
|---|---|---|---|---|
| 0x0000 | NEGOTIATE | | 0x000A | LOCK |
| 0x0001 | SESSION_SETUP | | 0x000B | IOCTL |
| 0x0002 | LOGOFF | | 0x000C | CANCEL |
| 0x0003 | TREE_CONNECT | | 0x000D | ECHO |
| 0x0004 | TREE_DISCONNECT | | 0x000E | QUERY_DIRECTORY |
| 0x0005 | CREATE | | 0x000F | CHANGE_NOTIFY |
| 0x0006 | CLOSE | | 0x0010 | QUERY_INFO |
| 0x0007 | FLUSH | | 0x0011 | SET_INFO |
| 0x0008 | READ | | 0x0012 | OPLOCK_BREAK |
| 0x0009 | WRITE | | | |

명령 코드는 명세 기준입니다[2].

| Flags 값 | 이름 | 뜻 |
|---|---|---|
| 0x00000001 | SERVER_TO_REDIR | 응답 메시지(서버가 보낸 것) |
| 0x00000002 | ASYNC_COMMAND | 비동기 헤더 |
| 0x00000004 | RELATED_OPERATIONS | 복합 요청 안의 연결된 명령 |
| 0x00000008 | SIGNED | 서명된 메시지 |
| 0x00000070 | PRIORITY_MASK | 요청 I/O 우선순위(3.1.1 만) |
| 0x10000000 | DFS_OPERATIONS | DFS 명령 |
| 0x20000000 | REPLAY_OPERATION | 재전송한 명령(3.x 만) |

플래그 값은 명세 기준입니다[2]. SERVER_TO_REDIR 비트 하나로 요청과 응답을 구분하므로, 캡처 방향을 모를 때도 누가 보낸 메시지인지 알 수 있습니다.

파일을 다루는 명령 가운데 조사에서 자주 보는 것은 CREATE·READ·WRITE·SET_INFO·QUERY_DIRECTORY 입니다. CREATE 응답에는 파일의 생성·마지막 접근·마지막 쓰기·변경 시각과 16바이트 FileId 가 들어 있고, 뒤따르는 READ·WRITE·CLOSE 는 이 FileId 로 파일을 가리킵니다. SET_INFO 로 FileDispositionInformation 을 설정하면 파일에 삭제 표시가 붙습니다. Wireshark 는 QUERY_DIRECTORY 를 "Find", QUERY_INFO 를 "GetInfo" 로 표시합니다[18].

### SMB3 암호화 — TRANSFORM_HEADER

SMB 3.x 에서 메시지를 암호화하면 암호화한 SMB2 메시지 앞에 52바이트 TRANSFORM_HEADER 가 붙습니다[3].

| 오프셋 | 크기 | 필드 | 값과 뜻 |
|---|---|---|---|
| 0 | 4 | ProtocolId | 0x424D53FD. 네트워크에서는 `FD 53 4D 42` |
| 4 | 16 | Signature | 협상한 암호 알고리즘으로 만든 서명 |
| 20 | 16 | Nonce | CCM 이면 앞 11바이트, GCM 이면 앞 12바이트가 논스이고 나머지는 0 |
| 36 | 4 | OriginalMessageSize | 암호화하기 전 SMB2 메시지 크기 |
| 40 | 2 | Reserved | 0 |
| 42 | 2 | Flags / EncryptionAlgorithm | 3.1.1 은 Flags 0x0001(암호화됨), 3.0·3.0.2 는 0x0001(AES128-CCM) |
| 44 | 8 | SessionId | 암호화한 세션 번호 |

그래서 SMB 페이로드가 `FE 53 4D 42` 로 시작하면 헤더와 명령을 읽을 수 있고, `FD 53 4D 42` 로 시작하면 그 뒤 내용이 암호화된 SMB3 메시지입니다[2][3]. 암호화된 메시지에서도 SessionId 와 OriginalMessageSize 는 평문이라, 어느 세션에서 얼마만 한 메시지가 오갔는지는 알 수 있습니다[3].

### RDP — 연결 요청 (X.224 Connection Request)

RDP 클라이언트가 처음 보내는 메시지는 TPKT 헤더(4바이트), X.224 연결 요청(7바이트), 선택 사항인 라우팅 토큰이나 쿠키 가운데 하나, 선택 사항인 RDP 협상 요청(rdpNegReq, 8바이트)과 상관 정보(36바이트) 순서로 이어집니다[9]. 쿠키는 `Cookie: mstshash=IDENTIFIER` 문자열 뒤에 0x0D 0x0A 가 붙은 형식이고, 라우팅 토큰이 있으면 쿠키는 오지 않습니다[9]. 따라서 3389 가 아닌 포트라도 TCP 페이로드 앞 11바이트 바로 뒤에 `Cookie: mstshash=` 가 보이면 RDP 연결 요청으로 볼 수 있습니다.

rdpNegReq 는 클라이언트가 쓸 수 있는 보안 프로토콜을 알립니다[10].

| 필드 | 크기 | 값과 뜻 |
|---|---|---|
| type | 1 | 0x01(TYPE_RDP_NEG_REQ) |
| flags | 1 | 0x01 제한된 관리 모드 필요(RESTRICTED_ADMIN_MODE_REQUIRED), 0x02 Remote Credential Guard(REDIRECTED_AUTHENTICATION_MODE_REQUIRED), 0x08 상관 정보 있음(CORRELATION_INFO_PRESENT) |
| length | 2 | 0x0008 |
| requestedProtocols | 4 | 0x00 표준 RDP 보안, 0x01 TLS(SSL), 0x02 CredSSP(HYBRID), 0x04 RDSTLS, 0x08 CredSSP 와 Early User Authorization Result PDU(HYBRID_EX), 0x10 RDS-AAD 인증(RDSAAD) |

HYBRID 를 켜면 SSL 도 함께 켜야 하고(SHOULD), HYBRID_EX 를 켜면 HYBRID 도 함께 켜야 합니다(SHOULD)[10]. 제한된 관리 모드와 Remote Credential Guard 는 CredSSP 위에서 자격 증명 없이 로그온(credential-less logon)하는 방식이라서, flags 값으로 클라이언트가 어떤 로그온 방식을 요구했는지 알 수 있습니다[10].

### SSH — 식별 문자열과 이진 패킷

SSH 연결이 맺어지면 양쪽이 먼저 `SSH-protoversion-softwareversion SP comments CR LF` 형식의 식별 문자열을 보냅니다. SSH 2 의 protoversion 은 "2.0" 이고, comments 는 없어도 됩니다. 문자열은 CR LF 를 포함해 최대 255자입니다[13]. 옛 버전과 호환하도록 설정한 서버는 protoversion 을 "1.99" 로 보내고, 클라이언트는 이를 "2.0" 과 같게 다룹니다[13]. 서버는 식별 문자열 전에 다른 줄을 보낼 수 있지만 그 줄은 "SSH-" 로 시작하면 안 됩니다[13].

식별 문자열 바로 뒤에 키 교환이 시작되고, 그 뒤 모든 패킷은 이진 패킷 형식을 씁니다[13]. 이진 패킷은 `packet_length`(4바이트), `padding_length`(1바이트), 페이로드, 무작위 패딩(4~255바이트), MAC 순서입니다[13]. 키 교환이 끝난 뒤에는 이 구조가 암호화되므로, 캡처에서 평문으로 읽을 수 있는 것은 식별 문자열과 키 교환 메시지의 알고리즘 목록까지입니다.

## 읽는 법

### SMB — 헥스로 한 번 따라가기

아래는 명세로 만든 TREE_CONNECT 요청의 앞부분입니다(만든 예시).

```
00 00 00 5A                                      Direct TCP 헤더: 0x00 + 길이 0x00005A(90바이트)
FE 53 4D 42 40 00 01 00 00 00 00 00 03 00 1F 00  ProtocolId, StructureSize=64, CreditCharge=1, 0, Command=0x0003
00 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00  Flags=0(요청), NextCommand=0, MessageId=4
00 00 00 00 00 00 00 00 11 00 00 00 00 10 00 00  Reserved=0, TreeId=0, SessionId
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  Signature(서명하지 않아 0)
```

ProtocolId 값 0x424D53FE 가 `FE 53 4D 42` 로 나오는 것처럼, SMB2 헤더의 숫자 필드는 낮은 바이트부터 적혀 있습니다. 그래서 오프셋 12의 `03 00` 은 0x0003(TREE_CONNECT), 오프셋 24의 `04 00 …` 은 MessageId 4 입니다. 이 요청에는 `\\FS01\c$` 같은 공유 경로가 실리고[8], 같은 MessageId 의 응답에서 서버가 TreeId 를 정해 줍니다[2]. 그 뒤 CREATE 요청에는 이 TreeId 와 파일 이름이 함께 실리므로, TreeId 로 "어느 공유의 어느 파일" 인지를 이어 볼 수 있습니다.

첫 네 바이트 뒤가 `FD 53 4D 42` 이면 읽기를 멈춥니다. 오프셋 36의 OriginalMessageSize 와 오프셋 44의 SessionId 만 기록하고, 같은 SessionId 의 SESSION_SETUP 이 캡처에 있는지 찾습니다[3].

### SMB — Zeek 로그로 읽기

Zeek 에서 공유 연결은 `smb_mapping.log`, 파일 작업은 `smb_files.log`, 명명 파이프 위의 원격 호출은 `dce_rpc.log`, 인증은 `ntlm.log`·`kerberos.log` 에 나뉘어 남고, 모두 `uid` 로 `conn.log` 의 연결과 이어집니다[4].

| 로그 | 주요 필드 | 뜻 |
|---|---|---|
| `smb_mapping.log` | `ts`, `path`, `service`, `native_file_system`, `share_type` | `ts` 는 트리를 연결한 시각, `path` 는 `\\FS01\c$`·`\\FS01\IPC$` 같은 공유 경로, `share_type` 기본값은 "DISK" 이고 파이프면 "PIPE"[4][5] |
| `smb_files.log` | `ts`, `fuid`, `action`, `path`, `name`, `size`, `prev_name`, `times.modified`·`times.accessed`·`times.created`·`times.changed` | `ts` 는 파일을 처음 발견한 시각, `name` 이 공유 루트이면 `<share_root>`, `prev_name` 은 이름을 바꾸기 전 이름[4][5] |
| `dce_rpc.log` | `rtt`, `named_pipe`, `endpoint`, `operation` | 예: `\pipe\lsass` 파이프로 `samr` 인터페이스의 `SamrConnect5` 호출[4][6] |
| `ntlm.log` | `username`, `hostname`, `domainname`, `server_nb_computer_name`, `server_dns_computer_name`, `server_tree_name`, `success` | 앞의 셋은 클라이언트가 보낸 값, `server_*` 는 서버가 CHALLENGE 에 넣은 값[7] |

`action` 값은 FILE_READ, FILE_WRITE, FILE_OPEN, FILE_CLOSE, FILE_DELETE, FILE_RENAME, FILE_SET_ATTRIBUTE 와 파이프용 PIPE_READ·WRITE·OPEN·CLOSE, 프린터용 PRINT_READ·WRITE·OPEN·CLOSE 입니다[5]. 다만 `SMB::logged_file_actions` 의 기본값은 PRINT_CLOSE, FILE_DELETE, FILE_OPEN, FILE_RENAME, PRINT_OPEN 다섯 가지뿐이라서, 기본 설정 센서의 `smb_files.log` 에는 FILE_READ·FILE_WRITE 줄이 없습니다[5].

아래는 관리 공유에 파일을 올린 연결을 요약한 예입니다(만든 예시).

```
smb_mapping.log  ts=1760000000.10  path=\\FS01\c$  share_type=DISK
smb_files.log    ts=1760000000.12  action=SMB::FILE_OPEN  path=\\FS01\c$  name=<share_root>
smb_files.log    ts=1760000000.31  action=SMB::FILE_OPEN  path=\\FS01\c$  name=temp\tool.exe  size=0
```

`jq -c '[."action", ."path", ."name"]' smb_files.log` 처럼 세 필드만 뽑으면 한 연결에서 어느 공유의 어느 파일을 열고 지우고 이름을 바꿨는지 순서대로 볼 수 있습니다[4]. SMB 로 옮긴 파일은 `files.log` 에 `source` 가 "SMB" 로 남고, 실행 파일이면 `pe.log` 도 생깁니다[4]. 파일 내용 꺼내기는 [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md)에서 다룹니다.

원격 호출은 `dce_rpc.log` 의 `endpoint`·`operation` 조합으로 읽습니다. 원격 사용자 목록 조회에서는 `samr` 의 `SamrEnumerateDomainsInSamServer`·`SamrLookupNamesInDomain`·`SamrQueryInformationUser`·`SamrGetGroupsForUser` 가 나오고, 그 사이에 `lsarpc` 의 `LsarLookupNames3` 도 섞입니다[4]. 원격 서비스 생성은 `svcctl` 의 `CreateServiceW`·`StartServiceW`, 예약 작업은 `ITaskSchedulerService` 의 `SchRpcRegisterTask`·`SchRpcRun`, WMI 실행은 `IWbemServices` 의 `ExecMethod` 로 나옵니다[20]. DCE-RPC 는 SMB 없이 TCP 로 바로 오가기도 해서, 135/tcp 의 `epmapper`(`ept_map`)에 물은 뒤 서버가 알려 준 49155/tcp 같은 높은 포트로 `svcctl` 을 호출하는 흐름도 있습니다[4].

`ntlm.log` 의 `success` 는 값이 있을 때만 적히는 선택 필드입니다[7]. Zeek 문서 예시 7줄 가운데 `success: true` 가 있는 줄은 2줄이고 나머지는 이 필드가 아예 없습니다[4].

### SMB — Suricata EVE 로 읽기

Suricata 는 SMB 트랜잭션마다 `smb` 기록을 남기고, `dialect`(예 "2.10"), `command`(예 `SMB2_COMMAND_CREATE`), `status`·`status_code`, `session_id`, `tree_id`, `filename`, `disposition`, `share`, `share_type`, `created`·`accessed`·`modified`·`changed`(epoch 초), `fuid`, `client_dialects` 같은 필드를 씁니다[8]. SMB 위의 DCE-RPC 는 `dcerpc` 하위 객체에 `request`·`response`·`opnum` 과 `interfaces` 를 적습니다[8]. `suricata.yaml` 의 `types` 로 남길 트랜잭션 종류(file, tree_connect, negotiate, dcerpc, create, session_setup, ioctl, rename, set_file_path_info, generic)를 고를 수 있고, 지정하지 않으면 모두 남깁니다[8]. 필드 전체는 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에서 다룹니다.

### RDP — 로그로 읽기

Zeek 의 `rdp.log` 에는 `cookie`, `result`, `security_protocol`, `client_channels`, `keyboard_layout`, `client_build`, `client_name`, `client_dig_product_id`, `desktop_width`·`desktop_height`, `requested_color_depth`, `cert_type`, `cert_count`, `cert_permanent`, `encryption_level`, `encryption_method` 가 남습니다[12]. `cookie` 는 보통 사용자 이름이지만 선 위에서 최대 9자로 잘리는 경우가 많고, `result` 는 RDP 협상 실패 메시지와 GCC 서버 응답 메시지가 섞인 값입니다[12]. Zeek 는 RDP 세션을 처음 알아본 뒤 10초(`RDP::rdp_check_interval`) 동안 지켜보고 한 줄로 기록합니다[12].

새 버전 RDP 는 TLS 로 암호화할 수 있고, 그러면 Zeek `conn.log` 의 `service` 가 `ssl` 로 나오고, 같은 `uid` 의 `ssl.log` 에 서버 인증서의 주체·발급자가 남습니다. `ssl.log` 의 `cert_chain_fuids` 값과 `x509.log` 의 `id` 를 맞추면 인증서 세부 내용도 볼 수 있습니다[11]. Zeek 문서의 TLS 사례에서 `rdp.log` 에 남은 필드는 `cookie`, `result`("encrypted"), `security_protocol`("HYBRID"), `cert_count`(0) 넷뿐이었고, 암호화하지 않은 RDP 에서는 이보다 많은 필드가 채워집니다[11]. 인증서로 서버를 알아보는 방법은 [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md)에서 다룹니다.

Suricata 는 RDP 협상 단계마다 `rdp` 기록을 한 줄씩 남기고, `tx_id` 가 흐름 안에서 하나씩 늘어납니다. `event_type` 은 `initial_request`(쿠키·flags), `initial_response`(선택된 `protocol` 또는 오류 `error_code`·`reason`), `connect_request`(클라이언트 버전·이름·키보드·화면·채널), `connect_response`, `tls_handshake`(`x509_serials`)입니다[8]. 오류 응답의 `reason` 은 "ssl required by server"(0x1)부터 "ssl with user auth required by server"(0x6)까지 여섯 가지입니다[8].

```
"rdp": {"tx_id": 0, "event_type": "initial_request", "cookie": "admin01"}
"rdp": {"tx_id": 1, "event_type": "initial_response", "protocol": "hybrid"}
"rdp": {"tx_id": 2, "event_type": "tls_handshake", "x509_serials": ["0a1b2c3d4e5f60718293a4b5c6d7e8f9"]}
```

위는 Suricata 문서의 형식을 따라 만든 예시입니다[8].

### SSH — 로그로 읽기

Zeek 의 `ssh.log` 에는 `version`(1, 2 또는 없음), `auth_success`(T 성공, F 실패, 없으면 모름), `auth_attempts`, `direction`(INBOUND·OUTBOUND), `client`·`server`(식별 문자열), `cipher_alg`, `mac_alg`, `compression_alg`, `kex_alg`, `host_key_alg`, `host_key`(서버 키 지문)가 남습니다[15]. `direction` 은 내부 호스트가 외부로 접속하면 OUTBOUND, 반대면 INBOUND 입니다[15]. HASSH 패키지를 설치한 센서에서는 `hassh`(클라이언트), `hasshServer`, `hasshAlgorithms` 같은 필드가 더 붙습니다[14].

```
{"ts":"2025-10-09T01:20:30.123456Z","id.orig_h":"10.0.20.15","id.resp_h":"10.0.20.40","id.resp_p":22,
 "version":2,"auth_success":true,"auth_attempts":1,
 "client":"SSH-2.0-OpenSSH_9.6","server":"SSH-2.0-OpenSSH_8.9p1",
 "kex_alg":"curve25519-sha256","host_key_alg":"ssh-ed25519","host_key":"3c:9a:..."}
```

위는 필드 모양을 보이려고 만든 예시입니다. Suricata 는 `ssh` 기록의 `client`·`server` 객체에 `proto_version` 과 `software_version` 을 나눠 적고, `app-layer.protocols.ssh.hassh` 를 `yes` 로 켜면 `hassh.hash`·`hassh.string` 도 남깁니다[8].

SSH 트래픽의 패킷 크기와 개수로 세션 성격을 추정하는 JA4SSH 는 `c(클라이언트 페이로드 길이 최빈값)s(서버 최빈값)_c(클라이언트 패킷 수)s(서버)_c(클라이언트 순수 ACK 수)s(서버)` 형식이고, 공개된 파이썬 구현은 기본으로 SSH 패킷 200개마다 값을 하나 계산합니다[17]. JA4 계열 전반은 [TLS 지문](../../02-artifacts/fingerprints/ja3-ja4.md)에서 다룹니다.

## 포렌식에서 중요한 점

### 증명하는 것

암호화하지 않은 SMB 의 Zeek 로그로는 이 시각에 이 내부 IP 가 이 공유(`\\FS01\c$`, `\\FS01\IPC$`)에 연결했고, 기본 설정에서 이 파일을 열거나 지우거나 이름을 바꿨다는 것을 확인할 수 있습니다[4][5]. `dce_rpc.log` 로는 어느 원격 인터페이스의 어느 연산을 불렀는지, `ntlm.log` 로는 클라이언트가 어떤 사용자 이름·호스트 이름·도메인 이름으로 NTLM 인증을 시도했는지 알 수 있습니다[4][7]. 캡처가 있으면 CREATE 응답에 실린 파일 시각과 SET_INFO 의 삭제 표시까지 볼 수 있어서, 연구에서는 SMB 트래픽만으로 공유 폴더의 파일 시스템과 파일 작업을 되살렸습니다[18].

RDP 는 이 클라이언트가 이 서버에 이 쿠키(사용자 이름 앞부분일 가능성이 큼)로 연결을 협상했고 어떤 보안 프로토콜을 골랐는지를 보여 줍니다[11][12]. SSH 는 이 시각에 두 호스트가 이 식별 문자열과 알고리즘으로 연결했다는 것과, Zeek 가 판정한 인증 결과를 보여 줍니다[14][15].

보고서에는 기록으로 확인되는 만큼만 씁니다. 예: "2025-10-09 01:20:30 UTC 에 10.0.20.15 가 10.0.20.30 의 `C$` 공유에 SMB 로 연결했고, 같은 연결에서 `temp\tool.exe` 를 연 기록이 Zeek `smb_files.log` 에 있다(만든 예시)."

### 증명하지 못하는 것

SMB3 암호화를 쓴 연결은 헤더가 `FD 53 4D 42` 로 시작하고 명령·파일 이름·데이터가 모두 암호화되어, 네트워크 기록만으로는 어떤 파일을 다뤘는지 알 수 없습니다[3]. 기본 설정의 Zeek `smb_files.log` 에는 읽기·쓰기 줄이 없으므로 "파일을 읽지 않았다" 거나 "쓰지 않았다" 는 결론을 낼 수 없습니다[5].

RDP 는 인증과 화면 내용이 TLS·CredSSP 안에 있어서 로그인 성공 여부와 원격 세션에서 한 일이 로그에 없습니다. Zeek 문서 사례에서는 같은 두 호스트 사이 39개 연결의 `rdp.log` 가 모두 똑같아서 어느 연결이 로그인에 성공했는지 `rdp.log` 로는 알 수 없었고, 38개는 바이트 수까지 같은데 1개만 달랐습니다[11]. 뒤이은 대화형 세션은 `conn.log` 에서 109초 동안 서버가 1,823,511바이트를 보낸 연결로 구분됐습니다[11]. 로그인 성공은 [Windows 원격 데스크톱 이벤트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/event-logs/rdp-event-logs/)처럼 서버 쪽 기록으로 확인합니다.

SSH 는 명령과 파일 내용이 모두 암호화되어 캡처로 볼 수 없고, `auth_success` 는 패킷 크기를 분석해 추정한 값입니다[15]. Zeek 는 결과가 조금이라도 의심스러우면 판정을 내리지 않으므로 `auth_success` 가 없는 줄이 생기고, 압축을 쓰는 연결은 인증 결과를 정확히 판정할 수 없습니다[15].

### 시각 해석

Zeek 로그의 `ts` 는 epoch 초로 적히고(`zeek-cut -d` 로 읽기 쉬운 시각으로 바꿉니다), Zeek 문서의 `ssh.log` 예시처럼 `2020-09-16T13:39:18.425492Z` 같은 ISO 8601 문자열로 내보낸 로그도 있습니다[14][23]. 로그마다 `ts` 가 뜻하는 순간이 달라서 `smb_mapping.log` 는 트리를 연결한 시각, `smb_files.log` 는 파일을 처음 발견한 시각, `ssh.log` 는 SSH 연결이 시작된 시각, `rdp.log`·`ntlm.log`·`dce_rpc.log` 는 해당 사건이 일어난 시각입니다[5][6][7][12][15].

`smb_files.log` 의 `times.*` 와 Suricata `smb` 기록의 `created`·`accessed`·`modified`·`changed` 는 네트워크를 관측한 시각이 아니라 서버가 알려 준 파일 시스템 시각입니다[5][8]. Zeek 문서 예시에서도 2017년에 관측한 공유 루트의 `times.created` 가 1247539136(2009-07-14)입니다[4]. 두 종류의 시각을 한 타임라인에 넣을 때는 열을 나눠 둡니다.

패킷 관측 시각은 실제 작업 시각보다 조금 늦습니다. Windows 11 두 대로 한 시험에서 트래픽으로 되살린 `cmd.exe` 명령 시각은 대부분 실제 실행 시각보다 0.1~0.8초 늦었습니다. 이 차이는 네트워크 구성에 따라 크게 달라질 수 있습니다[18]. 시각 기준 전반은 [네트워크 기록의 시각](../records/timestamps.md)에서 다룹니다.

## 함정

**`smb_files.log` 줄 수는 접근 횟수가 아닙니다.** 기본 설정에서는 읽기·쓰기를 남기지 않고, Zeek 는 한 연결 안에서 같은 파일을 되풀이해 적지 않으려고 최근 파일 목록을 따로 둡니다[5]. FILE_WRITE 줄이 있는 로그라면 센서가 `SMB::logged_file_actions` 를 바꿨거나 BZAR 같은 패키지를 설치했을 가능성이 있으니, 센서 설정을 먼저 확인합니다[4][5].

**캡처 손실이 크면 SMB 상태가 초기화됩니다.** `SMB::enable_clear_script_state` 기본값이 T 라서 `smb2_discarded_messages_state` 이벤트가 생길 때마다 Zeek 가 그 연결의 SMB 스크립트 상태를 지웁니다. 캡처 손실이 큰 환경에서 상태가 끝없이 커지는 것을 막으려는 설정입니다[5]. 그 뒤 명령은 공유 경로나 파일 이름 없이 남을 가능성이 있으므로, `conn.log` 의 `missed_bytes` 와 함께 봅니다.

**명명 파이프도 "파일" 로 나옵니다.** `IPC$` 공유의 `atsvc` 같은 파이프는 `smb_files.log` 와 `files.log` 에 파일처럼 나오지만 꺼낼 내용은 없습니다[4]. 파이프 이름을 파일 이름으로 읽으면 안 됩니다.

**`dce_rpc.log` 의 `named_pipe` 에 포트 번호가 들어갈 수 있습니다.** 이 필드는 프로토콜의 보조 주소(sec_addr) 값이라서 TCP 로 바로 오간 호출에서는 "135", "49155" 같은 포트 번호가 들어갑니다[4][6]. 또 `DCE_RPC::ignored_operations` 기본값이 `winreg` 의 `BaseRegOpenKey`·`BaseRegQueryValue`, `spoolss` 의 `RpcSplOpenPrinter`, `wkssvc` 의 `NetrWkstaGetInfo` 같은 연산을 로그에서 빼므로, 이 연산이 없다고 호출이 없었던 것은 아닙니다[6].

**`ntlm.log` 에 `success` 가 없는 줄을 실패로 읽지 않습니다.** 이 필드는 선택 필드라서 값이 없으면 줄에 아예 나오지 않습니다[7].

**같은 대상을 도구마다 다른 말로 부릅니다.** 공유 종류를 Zeek 는 "DISK"·"PIPE", Suricata 는 "FILE"·"PIPE"·"PRINT" 로 적습니다[5][8]. Sigma 의 BZAR 실행 규칙은 한 항목을 `endpoint: 'JobAdd'`, `operation: 'atsvc'` 로 적었는데, Zeek `dce_rpc.log` 는 `endpoint` 에 인터페이스 이름(samr, lsarpc)을, `operation` 에 연산 이름(SamrConnect5)을 쓰므로 이 항목은 필드가 뒤바뀌어 맞지 않을 가능성이 있습니다[4][20].

**RDP 는 3389 가 아닐 수 있고, `ssl` 로만 보일 수 있습니다.** 포트는 관리자가 바꿀 수 있고, TLS 를 쓰는 RDP 는 `conn.log` 에 `ssl` 로 나옵니다[11]. 이때 `ssl.log` 의 `server_name` 에 도메인 대신 서버 IP 가 적히고, 서버가 스스로 서명한 인증서(주체와 발급자가 같은 `CN=호스트이름`)가 나오기도 합니다[11]. 이 인증서의 CN 으로 RDP 서버의 호스트 이름을 추정할 수 있습니다.

**RDP 쿠키는 잘려 있을 수 있습니다.** 선 위의 쿠키는 최대 9자로 잘리는 경우가 많아서 사용자 이름 전체라고 단정하지 않습니다[12].

**Suricata RDP 필드 이름은 문서 본문과 예시가 다릅니다.** 본문은 연결 요청의 채널 목록을 `channel`, 서버가 지원하는 모드를 `flags` 라고 적었지만 예시 기록에는 `channels`, `server_supports` 로 나옵니다[8]. 검색식을 만들기 전에 실제 EVE 파일에서 필드 이름을 확인합니다.

**Zeek `auth_attempts` 가 0이라고 인증 시도가 없었던 것은 아닙니다.** Zeek 문서 사례에서 틀린 비밀번호를 한 번 넣고 빈 비밀번호로 두 번 더 시도한 연결이 `auth_attempts` 0, `auth_success` 없음으로 남았고, 그 연결의 `compression_alg` 는 `zlib@openssh.com` 이었습니다[14]. Zeek 는 압축을 쓰는 연결의 인증 결과를 정확히 판정하지 못하므로, `compression_alg` 가 none 이 아닌 줄은 인증 필드를 믿지 않습니다[15]. `auth_attempts` 가 2 이상이어도 2단계 인증처럼 모두 실패가 아닐 수 있습니다[15].

**`server` 만 있고 `client` 가 없는 SSH 줄이 있습니다.** 22번 포트에 연결만 하고 아무것도 보내지 않으면 서버 식별 문자열만 남고 `auth_attempts` 는 0 입니다[14]. 포트 확인이나 배너 수집일 가능성이 있는 연결입니다. 여러 번 되풀이된 연결을 어떻게 판단하는지는 [비밀번호를 무작위로 넣어 봤나](../../04-scenarios/intrusion/brute-force.md)에서 다룹니다.

**오래 쉬던 SSH 연결은 나뉘어 기록될 수 있습니다.** Zeek 는 22/tcp 연결과 SSH 분석기에 1시간 비활동 시간 제한을 둡니다[16]. 1시간 넘게 패킷이 없던 세션은 `conn.log` 에 여러 연결로 나뉘어 남을 가능성이 있습니다. 연결 추적 전반은 [TCP 연결과 흐름](tcp-sessions.md)에서 다룹니다.

**JA4SSH 는 포트 22 흐름만 계산될 수 있습니다.** 공개된 파이썬 구현은 출발지나 목적지 포트가 22인 TCP 흐름에만 JA4SSH 를 계산하고, 순수 ACK 의 방향도 포트 22를 기준으로 정합니다[17]. 다른 포트에서 동작하는 SSH 는 이 구현으로 값이 나오지 않습니다.

**SMB 가 445 에만 있는 것은 아닙니다.** SMB 3.1.1 은 QUIC 위에서도 동작하므로[1], 445·139 포트만 걸러서 SMB 사용이 없다고 결론 내리지 않습니다.

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| Zeek | `smb_mapping`·`smb_files`·`dce_rpc`·`ntlm`·`kerberos`·`rdp`·`ssh` 로그[4][11][14] |
| BZAR(Zeek 패키지) | SMB·DCE-RPC 패턴을 `notice.log` 로 알림. `zkg install bzar` 로 설치[4] |
| HASSH(Zeek 패키지) | `ssh.log` 에 클라이언트·서버 알고리즘 지문 추가[14] |
| Suricata | EVE `smb`·`rdp`·`ssh` 기록[8] |
| Wireshark·tshark | SMB2 명령 해석, `--export-objects` 로 파일 꺼내기(지원 프로토콜은 `--export-objects help` 로 확인)[22]. 사용법은 [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md) |
| JA4SSH | SSH 세션의 패킷 크기·개수 지문[17] |
| Sigma 규칙 | `smb_files` 의 PsExec 파이프(`-stdin`·`-stdout`·`-stderr`), `IPC$` 의 `atsvc`, 자격 증명 파일 이름(`\lsass`, `\sam`, `\ntds.dit`), 외부에서 온 RDP 탐지[19][20][21]. 활용법은 [탐지 규칙 활용](../../03-techniques/analysis/detection-rules.md) |
| Mount SMB.pcap(연구 도구) | 캡처의 SMB 공유를 파일 시스템처럼 탑재하고 명령 순서로 사용자 행위 복원[18] |

측면 이동 조사 흐름은 [내부에서 다른 PC 로 옮겨 갔나](../../04-scenarios/intrusion/lateral-movement.md)와 [Windows 계정 탈취와 측면 이동](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/credential-theft-lateral-movement/)에서, 원격 접속 흔적은 [Windows 원격 데스크톱 침입 확인](https://urock-ailab.github.io/forensics-handbook/windows/04-scenarios/incident/rdp-intrusion.html), [Windows 원격 데스크톱 접속 기록](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/network/rdp-client-mru.html), [Linux SSH 로 들어왔나](https://urock-ailab.github.io/forensics-handbook/linux/04-scenarios/intrusion/ssh-intrusion.html), [macOS SSH 키와 접속 목록](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/credentials/ssh-keys.html)에서 다룹니다. 암호화된 세션을 흐름 특징으로 보는 방법은 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)에 있습니다.

## 참고 문헌

1. Microsoft, [MS-SMB2] 2.1 Transport. https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/1dfacde4-b5c7-4494-8a14-a09d3ab4cc83
2. Microsoft, [MS-SMB2] 2.2.1.2 SMB2 Packet Header - SYNC. https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/fb188936-5050-48d3-b350-dc43059638a4
3. Microsoft, [MS-SMB2] 2.2.41 SMB2 TRANSFORM_HEADER. https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/d6ce2327-a4c9-4793-be66-7b5bad2175fa
4. Zeek, SMB Logs (plus DCE-RPC, Kerberos, NTLM). https://github.com/zeek/zeek-docs/blob/master/logs/smb.rst
5. Zeek, base/protocols/smb/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smb/main.zeek.rst
6. Zeek, base/protocols/dce-rpc/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/dce-rpc/main.zeek.rst
7. Zeek, base/protocols/ntlm/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ntlm/main.zeek.rst
8. OISF, Suricata EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
9. Microsoft, [MS-RDPBCGR] 2.2.1.1 Client X.224 Connection Request PDU. https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/18a27ef9-6f9a-4501-b000-94b1fe3c2c10
10. Microsoft, [MS-RDPBCGR] 2.2.1.1.1 RDP Negotiation Request (RDP_NEG_REQ). https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-rdpbcgr/902b090b-9cb3-4efc-92bf-ee13373371e3
11. Zeek, rdp.log. https://github.com/zeek/zeek-docs/blob/master/logs/rdp.rst
12. Zeek, base/protocols/rdp/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/rdp/main.zeek.rst
13. T. Ylonen, C. Lonvick, "The Secure Shell (SSH) Transport Layer Protocol", RFC 4253, 2006. https://www.rfc-editor.org/rfc/rfc4253.txt
14. Zeek, ssh.log. https://github.com/zeek/zeek-docs/blob/master/logs/ssh.rst
15. Zeek, base/protocols/ssh/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/ssh/main.zeek.rst
16. Zeek, base/protocols/conn/inactivity.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/inactivity.zeek.rst
17. FoxIO, JA4+ README 와 파이썬 구현(ja4.py, ja4ssh.py). https://github.com/FoxIO-LLC/ja4/blob/main/README.md , https://github.com/FoxIO-LLC/ja4/blob/main/python/ja4ssh.py , https://github.com/FoxIO-LLC/ja4/blob/main/python/ja4.py
18. Jan-Niclas Hilgert, Axel Mahr, Martin Lambertz, "Mount SMB.pcap: Reconstructing file systems and file operations from network traffic", Forensic Science International: Digital Investigation 50, 301807, 2024. doi:10.1016/j.fsidi.2024.301807
19. SigmaHQ, Zeek smb_files 규칙(zeek_smb_converted_win_susp_psexec.yml, zeek_smb_converted_win_atsvc_task.yml, zeek_smb_converted_win_transferring_files_with_credential_data.yml). https://github.com/SigmaHQ/sigma/tree/master/rules/network/zeek
20. SigmaHQ, zeek_dce_rpc_mitre_bzar_execution.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_dce_rpc_mitre_bzar_execution.yml
21. SigmaHQ, zeek_rdp_public_listener.yml. https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_rdp_public_listener.yml
22. Wireshark, tshark(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
23. Zeek, Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
