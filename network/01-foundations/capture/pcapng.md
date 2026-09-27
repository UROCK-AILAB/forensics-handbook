---
title: "pcapng 형식"
parent: "기반 · 패킷 캡처"
nav_order: 10
---

# pcapng 형식 (pcapng)

pcapng(PCAP Now Generic)는 패킷을 블록 단위로 이어 붙여 저장하는 캡처 파일 형식입니다. pcap 은 파일 머리에 링크 종류를 하나만 적지만, pcapng 는 한 파일에 여러 인터페이스를 담고 캡처한 프로그램·OS·캡처 필터·버린 패킷 수·주석까지 블록과 옵션으로 함께 저장합니다[1]. 이 페이지에서는 블록 구조와 오프셋, 패킷 시각을 계산하는 법, 이 부가 정보를 증거로 읽을 때 조심할 점을 다룹니다.

## 이 형식을 쓰는 아티팩트

Wireshark 와 함께 배포되는 캡처 도구 dumpcap 은 기본으로 pcapng 파일을 씁니다. pcap 으로 저장하라는 옵션(`-P`, `-F pcap`)을 주어도 여러 인터페이스에서 동시에 캡처하면 그 옵션을 무시하고 pcapng 로 저장합니다[5]. 캡처 파일을 자르고 고치는 editcap 도 출력 형식을 따로 정하지 않으면 pcapng 로 씁니다[6]. 그래서 조사 대상에서 나온 `.pcap` 파일을 editcap 으로 한 번 거치면 pcapng 가 됩니다.

명세가 권하는 확장자는 `.pcapng` 이지만 반드시 지킬 필요는 없어서, 파일 형식은 확장자가 아니라 첫 블록의 Block Type 과 Byte-Order Magic 으로 판별합니다[1]. tcpdump 가 쓰는 libpcap 도 pcapng 를 읽지만 뒤의 "함정" 절에 적은 제한이 있습니다[3]. 캡처에서 SMB 파일 작업을 되살리는 공개 도구 Mount SMB.pcap 처럼 분석 도구도 pcap 과 pcapng 를 함께 받습니다[11].

pcap 파일 머리와 레코드 구조는 [pcap 형식](pcap.md)에, 스냅 길이(SnapLen)로 잘린 패킷은 [캡처 필터와 잘린 패킷](capture-filters.md)에 있습니다.

## 구조

### 블록 공통 구조

파일은 블록을 차례로 이어 붙인 것이고, 모든 블록은 같은 틀로 시작하고 끝납니다[1].

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | Block Type | 블록 종류 코드 |
| 4 | 4 | Block Total Length | 블록 전체 바이트 수. 4의 배수여야 합니다(MUST) |
| 8 | 가변 | Block Body | 블록 본문. 32비트 경계까지 0으로 채웁니다 |
| 끝-4 | 4 | Block Total Length | 앞과 같은 값. 파일을 뒤에서부터 거꾸로 따라갈 때 씁니다 |

본문이 없는 블록의 길이는 12바이트입니다[1]. 읽는 도구는 모르는 블록을 길이만큼 건너뛸 수 있어서, 새 블록 종류가 섞여 있어도 나머지 블록은 읽힙니다[1]. Block Type 의 최상위 비트가 1인 값(0x80000000–0xFFFFFFFF)은 프로그램이 제 용도로 쓰는 지역 코드라 다른 도구와 뜻이 겹칠 수 있습니다[1].

| 코드 | 블록 | 내용 |
|---|---|---|
| 0x0A0D0D0A | Section Header Block (SHB) | 섹션 시작. 파일은 반드시 이 블록으로 시작합니다 |
| 0x00000001 | Interface Description Block (IDB) | 캡처한 인터페이스의 링크 종류·SnapLen·이름·필터 |
| 0x00000006 | Enhanced Packet Block (EPB) | 패킷 하나와 인터페이스 ID·시각·길이 |
| 0x00000003 | Simple Packet Block (SPB) | 패킷 하나. 시각과 인터페이스 ID 가 없습니다 |
| 0x00000004 | Name Resolution Block (NRB) | 캡처 당시의 주소-이름 대응 |
| 0x00000005 | Interface Statistics Block (ISB) | 인터페이스별 받은 수·버린 수·캡처 시작과 끝 시각 |
| 0x0000000A | Decryption Secrets Block (DSB) | 복호화에 쓰는 세션 키 목록 |
| 0x00000BAD / 0x40000BAD | Custom Block | 업체 정의 데이터(복사 허용 / 복사 금지) |
| 0x00000002 | Packet Block (PB) | 폐기된 옛 패킷 블록. 새 파일에 쓰면 안 됩니다 |

이 밖에 systemd 저널(0x00000009)과 Sysdig(0x00000201–0x00000213) 블록 코드도 등록되어 있습니다[1].

### 섹션과 바이트 순서

섹션은 SHB 한 개부터 다음 SHB 직전(또는 파일 끝)까지입니다. pcapng 파일 여러 개를 그대로 이어 붙이면 SHB 가 여러 개인 파일이 생기고, 읽는 도구는 버전을 모르는 섹션을 다음 SHB 까지 건너뜁니다[1]. 숫자 필드는 섹션마다 SHB 가 정한 바이트 순서(캡처한 기계의 순서)로 저장되므로, 한 파일 안에 리틀 엔디언 섹션과 빅 엔디언 섹션이 함께 있을 수 있습니다[1]. 인터페이스 ID 는 섹션 안에서만 유일해서, 섹션이 다르면 같은 ID 가 다른 인터페이스를 가리킵니다[1].

블록은 32비트 경계에만 맞춰져 있어서 64비트 값이 64비트 경계에 놓인다는 보장이 없습니다. 64비트 값 가운데 일부는 64비트 정수 하나로, EPB·ISB 시각처럼 일부는 상위 32비트와 하위 32비트 두 워드로 저장됩니다[1].

### 옵션

대부분의 블록은 본문 끝에 옵션 목록을 둡니다. 옵션은 Option Type(16비트), Option Length(16비트, 채움 바이트를 뺀 길이), Option Value(32비트 경계까지 채움)로 된 TLV 이고, 목록은 opt_endofopt(0)로 끝납니다[1]. 어느 블록에나 올 수 있는 공통 옵션은 opt_comment(1, UTF-8 주석, 여러 개 가능)와 opt_custom(2988·2989·19372·19373)입니다[1].

문자열 옵션은 0으로 끝난다는 보장이 없고, 읽는 쪽은 값 안에 0 바이트가 나오면 거기서 문자열이 끝난 것으로 봐야 합니다[1]. 쓰는 쪽은 올바른 UTF-8 만 써야 하지만, 읽는 쪽은 값이 올바른 UTF-8 이라고 가정하면 안 됩니다[1]. Option Type 의 최상위 비트가 1인 옵션도 지역 코드입니다[1].

### Section Header Block

| 오프셋 | 크기 | 필드 | 값 |
|---|---|---|---|
| 0 | 4 | Block Type | 0x0A0D0D0A |
| 4 | 4 | Block Total Length | |
| 8 | 4 | Byte-Order Magic | 0x1A2B3C4D |
| 12 | 2 | Major Version | 1 |
| 14 | 2 | Minor Version | 0 |
| 16 | 8 | Section Length | 이 섹션의 길이(SHB 제외). 부호 있는 64비트, -1 이면 모름 |
| 24 | 가변 | 옵션 | |

Block Type 0x0A0D0D0A 는 "\n\r\r\n" 네 글자입니다. FTP·HTTP 의 텍스트(ASCII) 모드로 옮기다 줄바꿈이 바뀌면 이 값이 달라져 손상을 알아챌 수 있고, 앞뒤가 같은 값이라 바이트 순서를 모르는 상태에서도 SHB 를 알아볼 수 있습니다[1]. 바이트 순서는 8바이트 뒤의 Byte-Order Magic 으로 정합니다. 쓰는 쪽은 1.0 이외의 버전을 쓰면 안 되고, Minor Version 2 를 쓴 구현이 있었기 때문에 읽는 쪽은 1.2 를 1.0 으로 취급합니다[1].

SHB 전용 옵션은 shb_hardware(2, 하드웨어 설명), shb_os(3, OS 이름), shb_userappl(4, 파일을 만든 프로그램, 예: "dumpcap V0.99.7")입니다[1]. dumpcap 은 SHB 에 CPU 정보, OS 버전, 프로그램 이름과 버전, `--capture-comment` 로 받은 주석을 쓰고 Section Length 는 -1 로 둡니다[4].

### Interface Description Block

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | Block Type | 0x00000001 |
| 8 | 2 | LinkType | 링크 계층 종류(pcap 과 같은 LinkType 목록) |
| 10 | 2 | Reserved | 0 |
| 12 | 4 | SnapLen | 패킷마다 저장하는 최대 바이트. **0 이면 제한 없음** |
| 16 | 가변 | 옵션 | |

인터페이스 ID 는 섹션 안에서 IDB 가 나온 순서대로 0부터 붙습니다. IDB 가 섹션 맨 앞에 모여 있을 필요는 없고, 그 인터페이스를 참조하는 블록보다 앞에만 있으면 됩니다[1]. pcap 은 SnapLen 0 을 금지하지만[2] pcapng IDB 에서는 0 이 "제한 없음" 이라 같은 0 이 두 형식에서 반대 뜻입니다.

| 코드 | 옵션 | 내용 |
|---|---|---|
| 2 | if_name | 장치 이름. 예: "eth0", "\Device\NPF_{GUID}" |
| 3 | if_description | 장치 설명 |
| 4 / 5 | if_IPv4addr / if_IPv6addr | 인터페이스 주소(IPv4 는 주소 4 + 마스크 4바이트, IPv6 는 주소 16 + 프리픽스 길이 1바이트). 여러 개 가능 |
| 6 / 7 | if_MACaddr / if_EUIaddr | 하드웨어 주소 |
| 8 | if_speed | 속도(bps). 송수신 속도가 다르면 if_txspeed(16)·if_rxspeed(17) |
| 9 | if_tsresol | 시각 단위. 아래 "읽는 법" 참고 |
| 10 | if_tzone | 정의가 불충분해 쓰지 않습니다(SHOULD NOT) |
| 11 | if_filter | 캡처 필터. 첫 바이트가 필터 종류, 예: `00` + "tcp port 23 and host 192.0.2.5" |
| 12 | if_os | 인터페이스가 있는 기계의 OS. 원격 캡처면 SHB 의 OS 와 다를 수 있습니다 |
| 13 | if_fcslen | FCS 길이 |
| 14 | if_tsoffset | 모든 시각에 더할 초(부호 있는 64비트) |
| 15 | if_hardware | 인터페이스 하드웨어 설명 |
| 18 | if_iana_tzname | IANA 시간대 이름. 예: "Asia/Kolkata" |

옵션 표의 코드와 예시는 명세[1]에 있습니다. dumpcap 은 IDB 에 인터페이스 이름(또는 `--ifname` 값), 설명, 캡처 필터 문자열, OS, 하드웨어, LinkType, SnapLen 을 쓰고, if_tsresol 은 나노초 캡처면 9, 아니면 6 으로 씁니다[4].

### Enhanced Packet Block

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | Block Type | 0x00000006 |
| 8 | 4 | Interface ID | 이 섹션의 몇 번째 IDB 인지 |
| 12 | 4 | Timestamp (상위) | 64비트 시각의 상위 32비트 |
| 16 | 4 | Timestamp (하위) | 64비트 시각의 하위 32비트 |
| 20 | 4 | Captured Packet Length | 저장한 바이트 수(채움 제외) |
| 24 | 4 | Original Packet Length | 자르지 않았다면 받았을 바이트 수 |
| 28 | 가변 | Packet Data | 링크 계층 헤더부터. 32비트 경계까지 채움 |
| 가변 | 가변 | 옵션 | |

EPB 옵션은 epb_flags(2), epb_hash(3, 첫 바이트가 알고리즘: 2 CRC32, 3 MD5, 4 SHA-1, 5 Toeplitz), epb_dropcount(4, 같은 인터페이스의 직전 패킷 이후 잃은 패킷 수), epb_packetid(5, 여러 인터페이스에서 본 같은 패킷을 잇는 ID), epb_queue(6, 받은 큐 번호), epb_verdict(7, 첫 바이트가 종류: 0 하드웨어, 1 Linux eBPF TC, 2 Linux eBPF XDP), epb_processid_threadid(8, 프로세스 ID·스레드 ID 각 32비트, 0 은 모름)입니다[1].

epb_flags 는 32비트 값이고 비트 0 이 최하위 비트입니다[1].

| 비트 | 뜻 |
|---|---|
| 0–1 | 방향: 00 정보 없음, 01 들어온 패킷, 10 나간 패킷 |
| 2–4 | 받은 종류: 000 미지정, 001 유니캐스트, 010 멀티캐스트, 011 브로드캐스트, 100 무차별 모드 |
| 5–8 | FCS 길이(바이트) |
| 9 | 체크섬 계산 전(체크섬 오프로딩으로 호스트가 아직 채우지 않음) |
| 10 | 체크섬을 이미 검증함 |
| 11 | TCP 분할 오프로딩: 여러 링크 패킷을 합친 패킷이거나 나중에 여러 개로 나뉠 패킷 |
| 16–31 | 링크 오류: 31 심볼, 30 프리앰블, 29 SFD, 28 정렬, 27 프레임 간격, 26 너무 짧음, 25 너무 긺, 24 CRC |

명세의 초기 판에서는 비트 0 이 최상위 비트였지만, 알려진 구현이 모두 최하위 비트를 0 으로 세어서 지금처럼 바뀌었습니다[1].

### Simple Packet Block 과 Packet Block

SPB 에는 Block Type·길이 뒤에 Original Packet Length(오프셋 8)와 Packet Data(오프셋 12)만 있습니다. 인터페이스 ID 가 없어 항상 첫 IDB(ID 0)의 패킷으로 보고, 시각도 없습니다[1]. 시각을 찍는 비용이 커서 뺀 블록이라, 성능이나 저장 공간이 중요한 연속 캡처에 씁니다. 한 파일에 EPB 와 SPB 가 섞일 수 있습니다[1].

Packet Block(0x00000002)은 EPB 이전의 형식으로, 16비트 Interface ID 와 16비트 Drops Count(0xFFFF 는 정보 없음)를 헤더에 둡니다. 폐기되었지만 옛 파일에서 만날 수 있습니다[1].

### Name Resolution Block

NRB 는 캡처 당시 쓰던 주소-이름 대응을 파일에 남겨, 나중에 다시 조회해서 결과가 달라지는 일을 막습니다[1]. 레코드는 nrb_record_ipv4(1, 주소 4바이트 뒤에 0으로 끝나는 이름 하나 이상), nrb_record_ipv6(2), nrb_record_eui48(3), nrb_record_eui64(4)이고 nrb_record_end(0)로 끝납니다. 옵션으로 이름을 조회한 DNS 서버의 이름(ns_dnsname, 2)과 주소(ns_dnsIP4addr 3, ns_dnsIP6addr 4)를 둘 수 있습니다[1]. 같은 주소에 이름 여러 개, 같은 쌍의 반복이 모두 허용되고, NRB 는 파일 어디에나 여러 개 있을 수 있습니다[1]. tshark 는 `-F pcapng -W n` 으로 캡처할 때 NRB 를 씁니다[9].

### Interface Statistics Block

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | Block Type | 0x00000005 |
| 8 | 4 | Interface ID | 통계 대상 인터페이스 |
| 12 | 8 | Timestamp | 통계를 뽑은 시각(EPB 와 같은 형식) |
| 20 | 가변 | 옵션 | |

| 코드 | 옵션 | 내용 |
|---|---|---|
| 2 | isb_starttime | 이 인터페이스에서 캡처를 시작한 시각 |
| 3 | isb_endtime | 캡처를 끝낸 시각 |
| 4 | isb_ifrecv | 인터페이스에서 받은 패킷 수 |
| 5 | isb_ifdrop | 자원이 모자라 인터페이스가 버린 패킷 수 |
| 6 | isb_filteraccept | 필터를 통과한 패킷 수 |
| 7 | isb_osdrop | OS 가 버린 패킷 수 |
| 8 | isb_usrdeliv | 사용자 프로그램에 전달된 패킷 수 |

수치는 모두 캡처 시작부터 센 64비트 값입니다. 캡처가 끝날 때 OS 버퍼에 남은 패킷이 있으면 isb_usrdeliv 가 isb_filteraccept − isb_osdrop 과 다를 수 있습니다[1]. ISB 는 보통 파일 끝에 있지만 위치가 정해져 있지 않고, 같은 인터페이스에 여러 번 나올 수 있습니다[1].

dumpcap 은 파일 하나에 저장할 때만, 캡처를 마치면서 인터페이스마다 ISB 를 씁니다. 이때 주석은 "Counters provided by dumpcap", isb_ifrecv 는 dumpcap 이 받은 수, isb_ifdrop 은 libpcap 이 보고한 버린 수와 dumpcap 자체가 버린 수를 더한 값이고, 통계를 얻지 못하면 두 값을 64비트 최댓값(0xFFFFFFFFFFFFFFFF)으로 씁니다[4]. 여러 파일로 나눠 저장하는 모드(링 버퍼 등)와 파이프 입력에는 이 ISB 를 쓰지 않습니다[4].

### Decryption Secrets Block

DSB 는 오프셋 8 에 Secrets Type(4바이트), 12 에 Secrets Length(4바이트), 16 부터 Secrets Data 를 둡니다. 비밀 값은 그것이 필요한 패킷 블록보다 앞에 두어야 하고(SHOULD), 도구는 앞에 나온 비밀만 쓸 수도 있습니다[1].

| Secrets Type | 내용 |
|---|---|
| 0x544c534b | TLS 키 로그(SSLKEYLOGFILE 과 같은 줄 형식) |
| 0x5353484b | SSH 키 로그 |
| 0x57474b4c | WireGuard 키 로그 |
| 0x55414b4c | OPC UA 키 로그 |
| 0x5a4e574b / 0x5a415053 | ZigBee NWK / APS 키 |
| 0x45535053 | IPsec ESP SA(CSV) |

조사 대상 파일에 DSB 가 이미 들어 있으면 capinfos `-D` 로 개수를 확인하고[7], editcap `--extract-secrets` 로 꺼내 볼 수 있습니다[6]. 키 로그 줄의 뜻과 TLS 해석은 [TLS와 인증서](../protocols/tls.md)에 있습니다.

### Custom Block 과 Custom Option

Custom Block 과 Custom Option 은 값 앞 4바이트에 IANA 기업 번호(PEN)를 두어 업체를 구분합니다. 코드 0x00000BAD 블록과 2988(UTF-8)·2989(바이너리) 옵션은 파일을 다시 쓰는 도구가 새 파일로 복사해도 되는 것이고, 0x40000BAD 블록과 19372·19373 옵션은 복사하지 말라는 표시입니다[1]. 이 표시는 다른 블록의 순서나 ID 에 기대는 데이터가 깨지지 않게 하려는 것이고 개인정보 보호와는 관계가 없습니다. 익명화 도구가 이 블록을 지운다는 보장이 없습니다[1].

## 읽는 법

1. 첫 4바이트가 `0A 0D 0D 0A` 이면 pcapng 입니다. 오프셋 8 의 4바이트가 `4D 3C 2B 1A` 이면 리틀 엔디언, `1A 2B 3C 4D` 이면 빅 엔디언 섹션입니다[1].
2. 오프셋 4 의 길이만큼 다음 블록으로 넘어가며 블록 종류를 확인합니다. 블록 끝 4바이트의 길이가 앞 길이와 같아야 합니다[1].
3. 새 SHB 가 나오면 바이트 순서를 다시 읽고 인터페이스 번호를 0부터 다시 셉니다.
4. IDB 가 나올 때마다 LinkType, SnapLen, if_tsresol, if_tsoffset 을 인터페이스 번호별로 기억해 둡니다.
5. EPB·ISB 의 시각을 아래처럼 계산합니다.

### 시각 계산

EPB 시각은 pcap 처럼 "초 + 소수 부분" 두 값이 아니라, 64비트 정수 하나를 상위 워드와 하위 워드로 나눠 적은 것입니다[1]. 값은 1970-01-01 00:00:00 UTC 이후 흐른 시간 단위 수이고, 단위는 해당 인터페이스 IDB 의 if_tsresol 이 정합니다[1].

- if_tsresol 의 최상위 비트가 0 이면 나머지 비트 n 이 10의 −n 제곱초(6 = 마이크로초, 9 = 나노초), 1 이면 2의 −n 제곱초입니다. 옵션이 없으면 마이크로초입니다[1].
- if_tsoffset 이 있으면 그 초를 더해야 절대 시각이 됩니다. 없으면 0 입니다[1]. libpcap 도 초 = 시각 값 ÷ 초당 단위 수 + if_tsoffset 으로 계산합니다[3].

명세의 예로, isb_starttime 값 `96 c3 04 00 73 89 6a 65`(리틀 엔디언)는 상위 워드 0x0004C396, 하위 워드 0x656A8973 이라 합치면 1340950620834163 마이크로초, 곧 2012-06-29 06:17:00.834163 UTC 입니다[1].

시간대는 선택 옵션인 if_iana_tzname 에만 담기고, if_tzone 은 쓰지 않도록 정해져 있습니다. if_tsoffset 도 현지 시각과 UTC 의 차이를 적는 용도가 아닙니다[1]. 시각 값 자체는 UTC 기준이라 시간대 옵션이 없어도 계산에는 문제가 없지만, 캡처한 장소의 현지 시각은 파일만으로 알 수 없습니다. 인터페이스마다 if_tsresol 이 다를 수 있으므로 여러 인터페이스가 섞인 파일은 인터페이스별로 단위를 따로 적용합니다. 패킷 시각을 다른 기록과 맞추는 법은 [네트워크 기록의 시각](../records/timestamps.md)에 있습니다.

ISB 의 isb_starttime·isb_endtime 은 캡처를 시작하고 끝낸 시각이라, 첫 패킷·마지막 패킷의 시각과 다를 수 있습니다[1]. 캡처 시작 시각과 첫 패킷 시각 사이가 비어 있으면, 그동안 트래픽이 없었을 수도 있고 필터가 걸러 냈을 수도 있습니다.

### 헥스로 따라가기 (명세로 만든 예시)

옵션 없는 SHB(28바이트, 리틀 엔디언, Section Length −1)입니다.

```
0A 0D 0D 0A  1C 00 00 00  4D 3C 2B 1A  01 00 00 00
FF FF FF FF FF FF FF FF  1C 00 00 00
```

옵션 없는 IDB(20바이트, LinkType 1 이더넷, SnapLen 262144)입니다.

```
01 00 00 00  14 00 00 00  01 00 00 00  00 00 04 00  14 00 00 00
```

if_tsresol 이 없거나 6(마이크로초)인 인터페이스에서 2026-01-01 00:00:00.123456 UTC 는 1767225600123456 = 0x0006474846222240 입니다. EPB 오프셋 12 에는 상위 워드 `48 47 06 00`, 오프셋 16 에는 하위 워드 `40 22 22 46` 이 리틀 엔디언으로 들어갑니다.

아래 파이썬 코드는 블록 목록과 EPB·ISB 의 원시 시각 값을 출력하고, 길이가 맞지 않는 블록에서 멈춥니다. if_tsresol·if_tsoffset 적용은 위 계산법대로 따로 합니다.

```python
import struct, sys

NAMES = {0x0A0D0D0A: "SHB", 1: "IDB", 2: "PB", 3: "SPB", 4: "NRB",
         5: "ISB", 6: "EPB", 10: "DSB", 0xBAD: "CB", 0x40000BAD: "CB(no-copy)"}

data = open(sys.argv[1], "rb").read()
off, bo = 0, "<"
while off + 12 <= len(data):
    if data[off:off+4] == b"\x0a\x0d\x0d\x0a":       # SHB 마다 바이트 순서를 다시 정한다
        bo = "<" if data[off+8:off+12] == b"\x4d\x3c\x2b\x1a" else ">"
    btype, blen = struct.unpack(bo + "II", data[off:off+8])
    if blen < 12 or blen % 4 or off + blen > len(data):
        print(f"{off:#010x} truncated or corrupt block (length {blen})")
        break
    tail, = struct.unpack(bo + "I", data[off+blen-4:off+blen])
    line = f"{off:#010x} {NAMES.get(btype, hex(btype)):12} {blen:6}"
    if tail != blen:
        line += f"  trailing length mismatch {tail}"
    if btype in (5, 6):
        iid, hi, lo = struct.unpack(bo + "III", data[off+8:off+20])
        line += f"  if={iid} ts={(hi << 32) | lo}"
    print(line)
    off += blen
```

## 포렌식에서 중요한 점

### 증명하는 것

pcapng 파일은 pcap 파일이 증명하는 것(어느 시각에 어떤 바이트가 캡처되었는지)에 더해, 쓴 도구가 옵션을 채웠다면 다음을 보여 줍니다. 패킷이 어느 인터페이스(if_name·if_description)에서 캡처되었는지, 어떤 캡처 필터(if_filter)가 걸려 있었는지, 캡처 중 버린 패킷이 몇 개로 보고되었는지(ISB, epb_dropcount), 패킷이 들어온 것인지 나간 것인지(epb_flags 방향 비트)를 확인할 수 있습니다. dumpcap 이 만든 파일이라면 IDB 에 캡처 필터 문자열이 들어 있어서, 어떤 트래픽이 처음부터 캡처 대상이 아니었는지도 알 수 있습니다[4].

### 증명하지 못하는 것

SHB 의 shb_hardware·shb_os·shb_userappl 은 파일을 쓴 프로그램이 넣은 문자열일 뿐입니다. 파일을 다시 쓰는 도구가 이 값을 그대로 두는지 바꾸는지는 명세에서도 아직 정하지 못한 문제(Open issue)로 남아 있습니다[1]. dumpcap 은 pcapng 파이프 입력이 하나뿐이면 자기 SHB·IDB 대신 입력 쪽의 SHB·IDB 를 그대로 옮겨 씁니다[4]. 그래서 SHB 문자열만으로 처음 캡처한 도구나 기계를 단정하지 않습니다.

주석은 누구나 넣고 바꾸고 지울 수 있습니다. editcap `-a` 는 지정한 패킷의 기존 주석을 새 주석으로 바꾸고(`--preserve-packet-comments` 를 주면 보존), `--discard-capture-comment`·`--discard-packet-comments` 는 주석을 지웁니다[6]. 같은 방식으로 `--discard-name-resolution` 은 NRB 를, `--discard-all-secrets` 는 DSB 를 없앱니다[6]. 따라서 주석·NRB·DSB 가 없다는 사실만으로는 원래 없었는지 누가 지웠는지 판별할 수 없습니다.

ISB 가 없다고 버린 패킷이 0 인 것도 아닙니다. dumpcap 은 여러 파일 모드나 파이프 입력에서는 ISB 를 쓰지 않습니다[4]. NRB 의 이름은 캡처하던 기계가 그때 조회한 결과이지 캡처 안의 DNS 응답 패킷이 아닙니다. 대상이 실제로 어떤 이름을 조회했는지는 DNS 패킷으로 확인합니다([DNS](../protocols/dns.md)).

### 비정상 종료와 손상

dumpcap 은 캡처를 정상으로 마치는 경로에서 ISB 를 쓰므로[4], 강제로 끝난 캡처 파일은 ISB 없이 끝나고 마지막 블록이 중간에 잘려 있을 가능성이 있습니다. 블록마다 앞뒤에 길이가 있어서, 앞 길이와 뒤 길이가 맞는 마지막 블록까지는 정상으로 읽고 그 뒤를 잘린 부분으로 구분할 수 있습니다. libpcap 은 길이가 4의 배수가 아닌 블록을 만나면 오류로 멈춥니다[3].

첫 블록 값이 `0A 0D 0D 0A` 가 아니고 `0A 0D 0A` 처럼 줄바꿈이 바뀐 모양이면 텍스트 모드 전송으로 손상된 파일일 수 있습니다. 명세는 이런 손상을 알아보려고 0x0A0D0AXX, 0xXX0A0D0A, 0xXX0A0D0D, 0x0D0D0AXX 모양의 블록 코드를 예약해 두었습니다[1].

dumpcap 이 여러 파일로 나눠 저장하는 도중에 pcapng 입력이 새 섹션을 시작해 앞 인터페이스가 쓸모없어지면, 이름 "dummy", 설명 "Dumpcap dummy interface", 주석 "Interface went out of scope" 인 자리만 채우는 IDB 를 씁니다[4]. 이런 IDB 는 조작 흔적이 아니라 도구가 인터페이스 번호를 맞추려고 넣은 것입니다.

### 프로세스 정보

Wireshark 개발 버전(master 브랜치)의 dumpcap 에는 `--process-info[=basic|full]` 옵션이 있습니다[5]. 이 옵션을 쓰면 TCP·UDP 소켓의 패킷에 epb_processid_threadid 옵션으로 프로세스 ID 를 달고, 파일마다 Process Information Block 을 한 번 씁니다[5]. basic 은 프로세스 ID·이름·시작 시각을, full 은 실행 경로·명령줄·부모 프로세스 ID·사용자까지 기록합니다[5]. 운영체제의 소켓 테이블에서 찾기 때문에 아주 짧게 사는 소켓은 빠질 수 있고, 알아낼 수 있는 프로세스 범위는 권한에 따라 다릅니다. Windows 는 전부, Linux 는 자기 프로세스만(root 이거나 CAP_SYS_PTRACE 권한이 있으면 전부), macOS 는 자기 프로세스만(root 면 전부)입니다[5]. 개발 버전 Wireshark 는 이 정보를 frame.process 필드로 보여 주지만[5], 4.6.9 까지의 정식 버전에는 이 필드가 없습니다[10]. editcap `--discard-process-info` 로 지울 수 있습니다[6].

## 함정

- **tcpdump(libpcap)로 못 읽는다고 손상은 아닙니다.** libpcap 은 첫 IDB 와 LinkType 이나 SnapLen 이 다른 IDB 를 만나면 "an interface has a type %u different from the type of the first interface" 같은 오류로 멈추고, 섹션마다 바이트 순서가 다르면 "the file has sections with different byte orders" 로 멈춥니다[3]. 명세는 둘 다 허용합니다[1]. 이런 파일은 Wireshark 계열 도구로 읽습니다.
- **SnapLen 0 의 뜻이 pcap 과 반대입니다.** pcap 은 0 을 금지하고[2], pcapng IDB 에서는 0 이 제한 없음입니다[1].
- **SPB 에는 시각이 없습니다.** SPB 로 저장된 패킷은 시간순 분석에 쓸 수 없습니다[1].
- **파일을 합치면 원래 모습이 바뀝니다.** mergecap 은 입력 파일 안의 패킷이 이미 시간순이라고 가정하고 시각 기준으로 합칩니다(`-a` 면 시각을 무시하고 이어 붙임). IDB 는 기본값 `-I all` 에서 모든 입력의 IDB 가 같을 때만 합쳐지고, 출력에는 "File created by merging:" 로 시작하는 캡처 주석이 붙습니다(`--no-merging-comment` 로 끔)[8]. 작업 방법은 [큰 캡처 파일 다루기](../../03-techniques/acquisition/large-captures.md)에 있습니다.
- **editcap 을 거치면 형식이 바뀝니다.** 출력 형식 기본값이 pcapng 이라 pcap 원본을 자르기만 해도 pcapng 가 됩니다. 원본 형식을 지키려면 `-F` 로 정합니다[6].
- **파이프로 받은 pcapng 는 바이트 순서가 맞아야 합니다.** dumpcap 이 파이프로 받는 pcapng 는 캡처하는 호스트와 바이트 순서가 같아야 합니다[5].
- **복사 금지 표시는 비공개 표시가 아닙니다.** Custom Block 의 복사 금지 코드를 믿고 파일을 넘기면 안의 데이터가 그대로 넘어갈 수 있습니다[1].

## 도구

capinfos 는 파일의 부가 정보를 요약합니다. `-I` 는 인터페이스별 상세 정보(표 형식 출력 불가), `-k` 는 SHB 의 캡처 주석, `-p` 는 패킷 주석, `-n` 은 NRB 로 해석된 IPv4·IPv6 주소 수, `-D` 는 DSB 개수, `-F` 는 추가 파일 정보를 보여 줍니다[7].

tshark 는 `-r 파일 -X read_format:"MIME Files Format" -V` 로 읽으면 패킷 대신 파일 내부 구조를 `file-pcapng` 필드로 보여 줍니다[9]. 블록 오프셋과 옵션 값을 헥스와 맞춰 볼 때 씁니다.

Wireshark 의 frame 필드로 pcapng 정보를 걸러 볼 수 있습니다. 필드가 들어온 Wireshark 버전은 다음과 같습니다[10].

| 필드 | 내용 | 버전 |
|---|---|---|
| frame.section_number | 섹션 번호 | 4.0.0 이후 |
| frame.interface_id | 인터페이스 ID | 1.8.0 이후 |
| frame.interface_name / frame.interface_description | IDB 의 이름·설명 | 2.4.0 이후 |
| frame.comment | 패킷 주석 | 1.10.0 이후 |
| frame.drop_count | epb_dropcount | 3.6.0 이후 |
| frame.packet_flags_direction / frame.packet_flags_reception_type | epb_flags 방향·받은 종류 | 1.10.0 이후 |
| frame.packet_flags_crc_error | epb_flags CRC 오류 비트 | 1.10.0 이후 |
| frame.packet_id | epb_packetid | 3.4.0 이후 |
| frame.hash / frame.hash.value | epb_hash | 4.2.0 이후 |
| frame.verdict | epb_verdict | 3.4.0 이후 |

예를 들어 `frame.interface_id == 1` 로 두 번째 인터페이스의 패킷만, `frame.drop_count > 0` 으로 앞에서 패킷을 잃은 지점만 볼 수 있습니다. 캡처를 만드는 절차는 [패킷 캡처하기](../../03-techniques/acquisition/packet-capture.md)에 있습니다.

## 참고 문헌

1. IETF OPSAWG, "PCAP Now Generic (pcapng) Capture File Format", draft-ietf-opsawg-pcapng. https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap/blob/master/draft-ietf-opsawg-pcapng.md
2. IETF OPSAWG, "PCAP Capture File Format", draft-ietf-opsawg-pcap. https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap/blob/master/draft-ietf-opsawg-pcap.md
3. The Tcpdump Group, libpcap `sf-pcapng.c`. https://github.com/the-tcpdump-group/libpcap/blob/master/sf-pcapng.c
4. Wireshark, `dumpcap.c`. https://github.com/wireshark/wireshark/blob/master/dumpcap.c
5. Wireshark, dumpcap 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/dumpcap.adoc
6. Wireshark, editcap 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
7. Wireshark, capinfos 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/capinfos.adoc
8. Wireshark, mergecap 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/mergecap.adoc
9. Wireshark, tshark 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
10. Wireshark, Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
11. Jan-Niclas Hilgert, Axel Mahr, Martin Lambertz, "Mount SMB.pcap: Reconstructing file systems and file operations from network traffic", Forensic Science International: Digital Investigation 50, 301807, 2024. doi:10.1016/j.fsidi.2024.301807
