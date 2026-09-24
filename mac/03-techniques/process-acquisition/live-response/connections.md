---
title: "네트워크 연결"
parent: "라이브 대응"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 2000
---

# 네트워크 연결 (Connections)

켜진 맥의 네트워크 연결은 `lsof -i` 로 소켓을 쥔 프로세스와 함께 모으고, `netstat` 으로 소켓 상태·라우팅 테이블·인터페이스 통계를 모읍니다.

## 언제 쓰나

원격 접속이나 자료 유출이 의심될 때, 지금 이 맥이 어디와 연결돼 있고 어떤 프로세스가 그 연결을 쥐고 있는지 볼 때 씁니다. 라우팅 테이블과 연결 목록은 RFC 3227 휘발성 순서의 2단계에 들어가고 [1], 순서 전체는 [휘발성 순서 (Order of Volatility)](order-of-volatility.md)에 있습니다.

연결을 끊을지는 이 목록을 뜬 다음에 정합니다. RFC 3227은 네트워크만 끊어도 공격자가 심어 둔 데드맨 스위치 (dead man switch)가 증거를 지울 수 있다고 경고하고 [1], 이 위험과 피해가 번질 위험을 함께 따져 결정한 뒤 그 시각과 까닭을 수집 기록에 남깁니다.

## 절차

1. root 권한으로 소켓을 쥔 프로세스를 모읍니다. `lsof -i` 는 네트워크 파일을 가진 프로세스를 COMMAND·PID·USER 와 함께 보여 주고, TYPE 칸에 IPv4·IPv6, NAME 칸에 로컬·원격 주소가 나옵니다 [2]. 다른 사용자 프로세스의 소켓까지 보려면 root 가 필요합니다 [2]. `-nP` 로 이름 조회를 막는 까닭은 [프로세스와 열린 파일 (ps·lsof)](processes-open-files.md)에 있습니다.

   ```
   lsof -i -nP
   ```

2. 모든 소켓의 상태를 숫자 주소로, 자르지 않고 모읍니다. 기본 출력에서는 서버 프로세스의 소켓이 빠져서 `-a` 를 주고, `-n` 은 주소를 숫자로, `-W` 는 주소를 자르지 않게 합니다 [3]. IPv6 주소를 모두 보려면 `-l` 을 더합니다 [3].

   ```
   netstat -anW
   ```

3. 라우팅 테이블을 모읍니다. `-r` 이 라우팅 테이블이고, `-a` 와 함께 주면 프로토콜이 복제한 경로까지 나옵니다 [3].

   ```
   netstat -rn
   ```

4. 인터페이스 상태와 입출력 바이트 수, 프로토콜별 통계를 모읍니다 [3].

   ```
   netstat -ib
   netstat -s
   ```

5. 의심 주소나 포트가 나오면 좁혀 봅니다. `-i` 뒤에 `[46][protocol][@hostname|hostaddr][:service|port]` 꼴로 조건을 붙이고 [2], 아래 줄은 man 페이지의 예를 옮긴 것입니다.

   ```
   lsof -nP -iTCP:25
   lsof -nP -i@1.2.3.4
   lsof -nP -i6
   ```

6. 출력 파일마다 수집 시각을 적고, 해시를 떠 둡니다. 기록과 해시 절차는 [라이브 대응 (Live Response)](index.md)에 있습니다.

## 도구

`netstat` 에서 라이브 대응에 쓰는 옵션을 모으면 아래와 같습니다 [3].

| 옵션 | 하는 일 |
|---|---|
| `-a` | 모든 소켓 상태. 빼면 서버 소켓이 빠짐 |
| `-n` | 주소를 숫자로 출력 |
| `-W` | 주소를 자르지 않음 |
| `-l` | IPv6 주소를 모두 출력 |
| `-p protocol` | 그 프로토콜의 통계 |
| `-f address_family` | 주소 계열(inet, inet6 등)로 제한 |
| `-r` | 라우팅 테이블 |
| `-i` | 인터페이스 상태. `-b` 를 함께 주면 입출력 바이트 수 |
| `-s` | 프로토콜별 통계 |
| `-A` | PCB 주소와 flow hash(디버깅용) |
| `-v` | 자세히 |

`netstat` 의 기본 출력에는 로컬·원격 주소, 송수신 큐 크기(바이트), 프로토콜, 프로토콜 안의 상태가 나옵니다 [3].

## 함정과 한계

`netstat` man 페이지에는 소켓을 가진 PID나 프로세스 이름을 보여 주는 옵션 설명이 없어서 [3], 연결과 프로세스를 잇는 일은 `lsof -i` 로 합니다. `-v` 가 PID 칸을 더하는지는 확인하지 못했으니 기대지 않습니다. `lsof` 를 root 없이 돌리면 자기 프로세스의 소켓만 나와서 [2] 목록이 비어 보여도 연결이 없다는 뜻이 아닙니다.

ARP 캐시, DNS 설정, 인터페이스 설정을 보는 명령은 이 페이지의 참고 문헌으로 옵션과 출력을 확인하지 못해서 싣지 않았습니다. 디스크에 남은 설정은 [네트워크 인터페이스와 설정 (SystemConfiguration)](../../../02-artifacts/network/network-interfaces.md)과 [hosts와 DNS 설정 (hosts·DNS)](../../../02-artifacts/network/hosts-dns.md)에서 봅니다.

## 결과를 어떻게 해석하나

연결 한 줄은 수집 시각에 그 프로세스가 그 주소와 소켓을 열어 두고 있었다는 기록이고, 누가 먼저 연결을 걸었는지나 무엇을 얼마나 보냈는지는 이 줄만으로 알 수 없습니다. `netstat -ib` 의 바이트 수도 인터페이스 단위라 프로세스별 송수신량으로 읽지 않습니다 [3]. 보고서에는 "수집 시각에 이 프로세스가 이 원격 주소와 연결돼 있었다" 까지만 쓰고, 앱별 송수신량은 [앱별 네트워크 사용량 (netusage)](../../../02-artifacts/network/netusage.md)에서, 방화벽이 허용하거나 막은 기록은 [방화벽 (Application Firewall)](../../../02-artifacts/network/application-firewall.md)에서, 원격 접속 설정은 [원격 접속 (Remote Access)](../../../02-artifacts/network/remote-access/index.md)에서 찾아 맞춰 봅니다. 연결을 쥔 프로세스의 명령줄과 열린 파일은 같은 PID로 [프로세스와 열린 파일 (ps·lsof)](processes-open-files.md)의 출력과 잇습니다.

조사 흐름으로 이어 보려면 [원격 접속 침입 확인 (Remote Intrusion)](../../../04-scenarios/incident/remote-intrusion.md)과 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)를 봅니다.

## 참고 문헌

1. RFC 3227 / BCP 55, Guidelines for Evidence Collection and Archiving (D. Brezinski, T. Killalea, 2002-02) — https://www.rfc-editor.org/rfc/rfc3227
2. lsof(8) man page, revision 4.91 (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/lsof.8.html
3. netstat(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/netstat.1.html
