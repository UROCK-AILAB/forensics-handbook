---
title: Network 개요
nav_order: -100
permalink: /
---

# Network 개요

패킷 캡처, 흐름 기록, 네트워크 장비와 서버 로그에 어떤 흔적이 남는지, 그 흔적을 어떻게 모으고 읽고 해석하는지 정리한 한국어 핸드북입니다.

침입과 자료 유출 조사에서 PC·서버·클라우드에 남은 기록은 네트워크 기록과 맞춰 볼 때 앞뒤가 이어집니다. 그래서 pcap·pcapng 형식과 프로토콜 기초에서 시작해 Zeek·Suricata 로그, 방화벽·프록시·DNS·DHCP·VPN 로그를 다루고, 암호화된 트래픽에서 알 수 있는 것과 없는 것을 나눠 적었습니다.

## 구성

핸드북은 네 부분으로 나뉩니다.

| 분류 | 다루는 것 |
|---|---|
| **기반 구조** | pcap·pcapng 형식, 캡처 지점과 필터, TCP·DNS·HTTP·TLS·메일·원격 관리 프로토콜, 흐름 기록(NetFlow·IPFIX), 로그 종류, 시각, IP·NAT 해석 |
| **아티팩트 사전** | Zeek 로그(conn·dns·http·ssl·files·notice), Suricata EVE 로그, 방화벽·프록시·DNS 서버·DHCP·VPN 로그, TLS 지문(JA3·JA4)과 인증서 |
| **분석 기법** | 조사 절차, 패킷 캡처와 큰 캡처 파일 다루기, 로그 보존, Wireshark·tshark, 파일 꺼내기, 암호화된 트래픽, 흐름 분석, 비컨·DNS 분석, 탐지 규칙, 타임라인 |
| **조사 시나리오** | "악성 코드가 C2 서버와 통신했나", "자료를 밖으로 보냈나", "이 시각에 이 IP 를 누가 썼나" 같은 질문 하나에 여러 기록을 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 어디에 남나 — 저장 위치, 켜야만 남는 기록, 도구 버전에 따른 차이
3. 구조 — 필드, 로그 줄 모양
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 어떤 기준 시각을 쓰고, 언제 기록되는지
6. 함정과 한계 — 자주 하는 오해, 놓치기 쉬운 곳
7. 직접 분석하기 — 기록을 직접 읽어 한 번, 공개 도구로 한 번
8. 함께 볼 기록 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 [pcap 형식](01-foundations/capture/pcap.md)과 [네트워크 로그의 종류](01-foundations/records/log-types.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 먼저 [로그 수집과 보존](03-techniques/acquisition/log-collection.md)을 보고, 조사 시나리오에서 질문을 고르면 됩니다. 예: [악성 코드가 C2 서버와 통신했나](04-scenarios/intrusion/c2-communication.md), [자료를 밖으로 보냈나](04-scenarios/exfiltration/data-exfiltration.md)
- 특정 로그만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 도구는 Zeek 7, Suricata 7, Wireshark 4 계열을 기준으로 씁니다. 버전에 따라 달라지는 것은 그 자리에 버전을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 장비·설정마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 패킷·로그 예시는 명세를 보고 만든 예시입니다. 실제 조직의 값이 아닙니다.
- 특정 회사 제품을 편들지 않고 같은 기준으로 씁니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.

# 목차


## 기반 구조

### 패킷 캡처

- [pcap 형식 (pcap)](01-foundations/capture/pcap.md)
- [pcapng 형식 (pcapng)](01-foundations/capture/pcapng.md)
- [어디서 캡처하나 (SPAN·TAP·호스트)](01-foundations/capture/capture-points.md)
- [캡처 필터와 잘린 패킷 (Capture Filter·Snaplen)](01-foundations/capture/capture-filters.md)

### 프로토콜 기초

- [TCP 연결과 흐름 (TCP Sessions)](01-foundations/protocols/tcp-sessions.md)
- [DNS (DNS)](01-foundations/protocols/dns.md)
- [HTTP (HTTP)](01-foundations/protocols/http.md)
- [TLS와 인증서 (TLS·X.509)](01-foundations/protocols/tls.md)
- [메일 프로토콜 (SMTP·IMAP·POP3)](01-foundations/protocols/mail-protocols.md)
- [SMB와 원격 관리 프로토콜 (SMB·RDP·SSH)](01-foundations/protocols/remote-protocols.md)

### 기록 체계

- [흐름 기록 (NetFlow·IPFIX·sFlow)](01-foundations/records/flow-records.md)
- [네트워크 로그의 종류 (Network Log Types)](01-foundations/records/log-types.md)
- [네트워크 기록의 시각 (Timestamps)](01-foundations/records/timestamps.md)
- [IP 주소·포트·NAT 해석 (IP·Port·NAT)](01-foundations/records/ip-nat.md)

## 아티팩트 사전

### Zeek

- [Zeek 로그 (Zeek Logs)](02-artifacts/zeek/zeek-logs/index.md)
  - [연결 기록 (conn.log)](02-artifacts/zeek/zeek-logs/conn-log.md)
  - [DNS 기록 (dns.log)](02-artifacts/zeek/zeek-logs/dns-log.md)
  - [HTTP 기록 (http.log)](02-artifacts/zeek/zeek-logs/http-log.md)
  - [TLS·인증서 기록 (ssl.log·x509.log)](02-artifacts/zeek/zeek-logs/ssl-x509-log.md)
  - [파일 기록 (files.log)](02-artifacts/zeek/zeek-logs/files-log.md)
  - [경고와 이상 기록 (notice.log·weird.log)](02-artifacts/zeek/zeek-logs/notice-weird-log.md)

### Suricata

- [Suricata EVE 로그 (EVE JSON)](02-artifacts/suricata/eve-json/index.md)
  - [경고 기록 (alert)](02-artifacts/suricata/eve-json/alert.md)
  - [프로토콜 기록 (dns·http·tls·flow)](02-artifacts/suricata/eve-json/protocol-events.md)
  - [파일 추출 (filestore)](02-artifacts/suricata/eve-json/filestore.md)

### 네트워크 장비와 서버 로그

- [방화벽 로그 (iptables·nftables·pf)](02-artifacts/devices/firewall-logs.md)
- [웹 프록시 로그 (Squid)](02-artifacts/devices/proxy-logs.md)
- [DNS 서버 로그 (BIND·Windows DNS)](02-artifacts/devices/dns-server-logs.md)
- [DHCP 로그 (DHCP)](02-artifacts/devices/dhcp-logs.md)
- [VPN 서버 로그 (OpenVPN·WireGuard)](02-artifacts/devices/vpn-logs.md)

### 식별 정보

- [TLS 지문 (JA3·JA4)](02-artifacts/fingerprints/ja3-ja4.md)
- [인증서로 서버 알아보기 (Certificates)](02-artifacts/fingerprints/certificates.md)

## 분석 기법

### 조사 절차·수집

- [조사 절차 (Investigation Process)](03-techniques/acquisition/investigation-process.md)
- [패킷 캡처하기 (tcpdump·dumpcap)](03-techniques/acquisition/packet-capture.md)
- [큰 캡처 파일 다루기 (editcap·mergecap·capinfos)](03-techniques/acquisition/large-captures.md)
- [로그 수집과 보존 (Log Collection)](03-techniques/acquisition/log-collection.md)

### 분석

- [Wireshark·tshark로 읽기 (Wireshark)](03-techniques/analysis/wireshark.md)
- [세션 복원과 파일 꺼내기 (Reassembly·File Extraction)](03-techniques/analysis/file-extraction.md)
- [암호화된 트래픽 분석 (Encrypted Traffic)](03-techniques/analysis/encrypted-traffic.md)
- [흐름 기록 분석 (nfdump)](03-techniques/analysis/flow-analysis.md)
- [비컨 찾기 (Beacon Detection)](03-techniques/analysis/beaconing.md)
- [DNS 분석 (DNS Analysis)](03-techniques/analysis/dns-analysis.md)
- [탐지 규칙 활용 (Suricata·Sigma)](03-techniques/analysis/detection-rules.md)
- [네트워크 타임라인 (Timeline)](03-techniques/analysis/timeline.md)

### 보고

- [네트워크 포렌식 보고서 (Forensic Report)](03-techniques/reporting/forensic-report.md)

## 조사 시나리오

### 침입

- [악성 코드가 C2 서버와 통신했나 (C2 Communication)](04-scenarios/intrusion/c2-communication.md)
- [내부에서 다른 PC 로 옮겨 갔나 (Lateral Movement)](04-scenarios/intrusion/lateral-movement.md)
- [웹 서버의 취약점을 노렸나 (Web Exploitation)](04-scenarios/intrusion/web-exploitation.md)
- [비밀번호를 무작위로 넣어 봤나 (Brute Force)](04-scenarios/intrusion/brute-force.md)

### 자료 유출

- [자료를 밖으로 보냈나 (Data Exfiltration)](04-scenarios/exfiltration/data-exfiltration.md)
- [DNS 로 몰래 보냈나 (DNS Tunneling)](04-scenarios/exfiltration/dns-tunneling.md)

### 사용자 행위

- [피싱 링크를 눌렀나 (Phishing Click)](04-scenarios/user-activity/phishing-click.md)
- [이 시각에 이 IP 를 누가 썼나 (IP Attribution)](04-scenarios/user-activity/ip-attribution.md)
