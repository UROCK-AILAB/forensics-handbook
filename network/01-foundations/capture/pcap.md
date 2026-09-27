---
title: "pcap 형식"
parent: "기반 · 패킷 캡처"
nav_order: 0
---

# pcap 형식 (pcap)

pcap 은 tcpdump 와 libpcap 이 캡처한 패킷을 파일로 저장하는 형식입니다. 24바이트 파일 헤더 뒤에 패킷마다 16바이트 헤더와 패킷 바이트가 이어지는 단순한 구조라서, 헤더 몇 개만 읽으면 패킷 시각·잘림 여부·링크 계층 종류를 직접 확인할 수 있습니다. 대신 캡처한 인터페이스, 캡처 필터, 버려진 패킷 수, 시간대는 파일 어디에도 남지 않습니다.

## 이 형식을 쓰는 아티팩트

pcap 은 tcpdump 가 `-w` 로 저장하는 기본 형식이고, libpcap 을 쓰는 프로그램 대부분이 읽고 씁니다[1][6]. 형식 버전은 2.4이고, IETF 초안은 이 형식을 "역사적(historic)" 문서로 두었습니다. 이 형식에는 새 확장이 더 나오지 않을 예정이고, 후속 형식은 pcapng 입니다[1]. 조사 현장에서는 tcpdump 로 뜬 캡처, 센서·보안 장비가 내보낸 캡처, pcapng 를 pcap 으로 변환한 파일에서 이 형식을 만납니다. 캡처 장비별 저장 위치는 [어디서 캡처하나](capture-points.md)에, 캡처 명령은 [패킷 캡처하기](../../03-techniques/acquisition/packet-capture.md)에 있습니다.

권장 확장자는 `.pcap` 이고, 다른 확장자는 피하는 것이 좋습니다. 특히 `.cap` 은 여러 캡처 형식이 함께 쓰는 확장자라서 형식을 헷갈리기 쉽습니다[1]. tcpdump 는 확장자를 보지 않고 헤더의 매직 번호(magic number)로 형식을 판별하며, 저장할 때 확장자를 붙이지도 않습니다. 흔히 쓰는 확장자는 `.pcap`, `.cap`, `.dmp` 이고, IANA 에 등록된 MIME 형식은 `application/vnd.tcpdump.pcap` 입니다[6]. 그래서 확장자가 없거나 엉뚱한 파일도 첫 4바이트로 pcap 인지 확인합니다.

## 구조 — 표와 오프셋

파일은 파일 헤더(File Header) 하나와 패킷 레코드(Packet Record) 0개 이상으로 이뤄집니다. 두 개 이상 바이트로 된 숫자 필드는 모두 파일을 쓴 기계의 바이트 순서(리틀 엔디언 또는 빅 엔디언)로 저장됩니다[1][2].

### 파일 헤더 (24바이트)

| 오프셋 | 크기 | 필드 | 값과 뜻 |
|---|---|---|---|
| 0 | 4 | Magic Number | 0xA1B2C3D4 이면 시각이 초·마이크로초, 0xA1B23C4D 이면 초·나노초 |
| 4 | 2 | Major Version | 2 |
| 6 | 2 | Minor Version | 4 |
| 8 | 4 | Reserved1 | 0 으로 쓰고, 읽는 쪽은 무시해야 합니다(MUST). 옛 구현은 "GMT to local correction" 또는 "time zone offset" 으로 문서화했고 0 이 아닌 값을 쓴 도구도 있습니다 |
| 12 | 4 | Reserved2 | 0 으로 쓰고 무시합니다. 옛 구현은 "accuracy of timestamps" 로 문서화했습니다 |
| 16 | 4 | SnapLen | 패킷 하나에서 저장하는 최대 바이트 수. 0 이면 안 됩니다(MUST NOT) |
| 20 | 4 | LinkType 과 부가 정보 | 하위 16비트가 LinkType, 상위 비트에 FCS len(4비트)·R·P·Reserved3(10비트) |

표의 오프셋과 필드 정의는 명세 기준입니다[1][2].

매직 번호도 쓴 기계의 바이트 순서로 저장되므로, 파일 첫 4바이트를 보면 바이트 순서와 시각 단위를 함께 알 수 있습니다[1].

| 첫 4바이트 | 바이트 순서 | 초 아래 단위 |
|---|---|---|
| `A1 B2 C3 D4` | 빅 엔디언 | 마이크로초 |
| `A1 B2 3C 4D` | 빅 엔디언 | 나노초 |
| `D4 C3 B2 A1` | 리틀 엔디언 | 마이크로초 |
| `4D 3C B2 A1` | 리틀 엔디언 | 나노초 |

pcapng 파일은 첫 4바이트가 `0A 0D 0D 0A` 라서 위 네 값과 겹치지 않고, 두 형식을 자동으로 구분할 수 있습니다[1]. pcapng 구조는 [pcapng 형식](pcapng.md)에서 다룹니다.

FCS len 은 LinkType 필드의 P 비트가 켜져 있을 때만 쓰는 값이고, 패킷마다 끝에 붙은 FCS(프레임 검사 순서, Frame Check Sequence) 길이를 16비트 워드 단위로 나타냅니다. 이더넷의 4바이트 FCS 는 2입니다. R 비트와 Reserved3 는 0이어야 하고, 읽는 쪽은 0이 아니면 오류로 다루는 것이 좋습니다(SHOULD)[1]. 자주 만나는 LinkType 값은 아래와 같습니다[3].

| 값 | 이름 | 패킷 데이터가 시작하는 곳 |
|---|---|---|
| 0 | LINKTYPE_NULL | BSD 루프백 헤더 |
| 1 | LINKTYPE_ETHERNET | 이더넷 헤더 |
| 101 | LINKTYPE_RAW | 링크 헤더 없이 IP 헤더 |
| 105 | LINKTYPE_IEEE802_11 | 무선 LAN 헤더 |
| 113 | LINKTYPE_LINUX_SLL | 리눅스 cooked 캡처 헤더(16바이트) |
| 127 | LINKTYPE_IEEE802_11_RADIOTAP | Radiotap 헤더 뒤 무선 LAN 헤더 |
| 228 / 229 | LINKTYPE_IPV4 / IPV6 | 링크 헤더 없이 IPv4 / IPv6 헤더 |
| 276 | LINKTYPE_LINUX_SLL2 | 리눅스 cooked 캡처 헤더 v2(20바이트) |

리눅스에서 `any` 인터페이스로 캡처하면 LINUX_SLL 이나 LINUX_SLL2 가 나옵니다[12]. 이 헤더에는 이더넷 목적지 MAC 이 없고 보낸 쪽 링크 주소만 있습니다. 대신 packet type 필드로 방향을 알 수 있어서, 0은 이 호스트로 온 패킷, 1은 브로드캐스트, 2는 멀티캐스트, 3은 다른 호스트끼리 오간 패킷, 4는 이 호스트가 보낸 패킷입니다[7]. SLL2 에는 캡처한 기계의 인터페이스 인덱스(4바이트)도 들어 있습니다[8]. 두 헤더의 숫자 필드는 파일 바이트 순서와 상관없이 빅 엔디언입니다[7][8].

### 패킷 레코드 (16바이트 헤더 + 데이터)

| 오프셋 | 크기 | 필드 | 뜻 |
|---|---|---|---|
| 0 | 4 | Timestamp (Seconds) | 1970-01-01 00:00:00 UTC 이후 초, 부호 없는 32비트 |
| 4 | 4 | Timestamp (Microseconds or nanoseconds) | 그 초 이후 마이크로초 또는 나노초. 단위는 매직 번호가 정합니다 |
| 8 | 4 | Captured Packet Length | 파일에 저장된 바이트 수. 원래 길이와 SnapLen 중 작은 값 |
| 12 | 4 | Original Packet Length | 잘리지 않았다면 받았을 바이트 수 |
| 16 | 가변 | Packet Data | 링크 계층 헤더부터 시작하는 패킷 바이트 |

레코드 정의는 명세 기준입니다[1][2]. 레코드는 4바이트 경계로 맞추지 않아서 패킷 데이터 뒤에 채움 바이트가 없고, 다음 레코드는 바로 이어서 시작합니다[1]. 원래 길이는 캡처 길이보다 작으면 안 됩니다(SHOULD NOT). 예외는 그런 값이 이미 들어 있는 파일에서 옮겨 쓸 때뿐이고, 읽는 쪽은 그런 값을 캡처 길이 이상으로 바꿔 읽어도 됩니다(MAY)[1].

## 읽는 법

파일 헤더에서 먼저 매직 번호로 바이트 순서와 시각 단위를 정하고, SnapLen 과 LinkType 을 읽습니다. 그다음 24바이트 지점부터 레코드 헤더 16바이트를 읽고, 캡처 길이만큼 패킷 데이터를 건너뛰면 다음 레코드 헤더가 나옵니다. 이 과정을 파일 끝까지 되풀이하면 됩니다.

시각은 초 필드와 초 아래 필드를 합쳐 계산합니다. 초 필드는 UTC 기준 epoch 초이고 파일 어디에도 시간대 정보가 없습니다[1][2]. 부호 없는 32비트라서 2106년까지 나타낼 수 있습니다. 이 시각은 캡처 도구가 패킷을 본 시각의 근사값이고, 들어오는 패킷은 도착 시각, 나가는 패킷은 송신 시각입니다[5]. 여러 기록의 시각을 맞추는 방법은 [네트워크 기록의 시각](../records/timestamps.md)에서 다룹니다.

libpcap 은 파일이 나노초 단위여도 기본으로 마이크로초 단위까지만 넘겨주고 나머지 자릿수는 버립니다[5]. tcpdump 도 `--time-stamp-precision` 기본값이 `micro` 라서, 나노초 파일을 읽을 때는 `--nano` 를 줘야 나노초까지 보입니다[6]. 반대로 나노초로 캡처해 저장하면 매직 번호가 0xA1B23C4D 로 바뀌고, 이 파일을 읽지 못하는 프로그램도 있습니다[1][6].

### 헥스로 따라가기 (명세로 만든 예시)

아래 40바이트는 명세대로 만든 예시입니다. 리틀 엔디언, 마이크로초, 버전 2.4, SnapLen 262144, 이더넷 파일의 헤더와 첫 레코드 헤더입니다.

```
오프셋  바이트
0000    D4 C3 B2 A1 02 00 04 00 00 00 00 00 00 00 00 00
0010    00 00 04 00 01 00 00 00 00 B9 55 69 40 E2 01 00
0020    60 00 00 00 EA 05 00 00
```

- 0x00 `D4 C3 B2 A1`: 리틀 엔디언, 마이크로초 단위입니다.
- 0x04 `02 00` / 0x06 `04 00`: 버전 2.4입니다.
- 0x08–0x0F: Reserved1·Reserved2 가 모두 0입니다.
- 0x10 `00 00 04 00`: SnapLen 0x00040000 = 262144바이트입니다.
- 0x14 `01 00 00 00`: LinkType 1(이더넷)이고 P 비트는 꺼져 있습니다.
- 0x18 `00 B9 55 69`: 0x6955B900 = 1767225600초 = 2026-01-01 00:00:00 UTC 입니다.
- 0x1C `40 E2 01 00`: 0x0001E240 = 123456마이크로초라서, 패킷 시각은 2026-01-01 00:00:00.123456 UTC 입니다.
- 0x20 `60 00 00 00`: 캡처 길이 96바이트입니다.
- 0x24 `EA 05 00 00`: 원래 길이 1514바이트입니다. 캡처 길이가 더 작으므로 이 패킷은 96바이트에서 잘렸습니다.

같은 파일을 빅 엔디언 기계가 썼다면 첫 4바이트는 `A1 B2 C3 D4` 이고 나머지 숫자 필드도 모두 반대 순서로 저장됩니다[1].

### 공개 도구로 확인하기

`capinfos` 는 형식(`-t`), 링크 계층 종류(`-E`), SnapLen(`-l`), 패킷 수(`-c`), 가장 이른 시각과 가장 늦은 시각(`-a`, `-e`), 캡처 기간(`-u`), 시간순 여부(`-o`), 파일 해시(`-H`, SHA256·SHA1)를 보여 줍니다[9]. `-l` 은 헤더의 SnapLen 과 실제로 잘린 레코드를 함께 보고 판단하고, `-S` 는 가장 이른 시각과 가장 늦은 시각을 epoch 초로 보여 줍니다[9].

```
capinfos -t -E -l -c -a -e -o -H 사건.pcap
tcpdump -r 사건.pcap -tt -n -c 5 -XX
```

tcpdump 의 `-tt` 는 epoch 초(UTC)와 소수점 아래 값을 그대로 찍고, `-XX` 는 링크 계층 헤더를 포함한 패킷 바이트를 헥스로 보여 줍니다[6]. `-tttt` 는 날짜와 시각을 찍는데, 어느 시간대로 찍히는지는 같은 패킷의 `-tt` 값과 비교해 확인합니다[6]. Wireshark 에서는 `frame.time_epoch`(epoch 도착 시각), `frame.time_utc`(UTC 도착 시각, 4.2.0 이상), `frame.cap_len`(캡처 길이), `frame.len`(원래 길이), `frame.encap_type`(링크 계층 종류), `frame.file_off`(파일 안 오프셋) 필드로 같은 값을 봅니다[11]. `frame.file_off` 로 헥스 편집기 위치와 패킷 번호를 이어 볼 수 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것

pcap 파일은 캡처 지점을 지나간 패킷의 바이트를 SnapLen 범위 안에서 그대로 담고 있습니다. 패킷마다 캡처 도구가 매긴 시각이 있고, 캡처 길이가 원래 길이보다 작으면 그 패킷이 잘렸다는 것도 알 수 있습니다[1]. 링크 계층이 LINUX_SLL·SLL2 이면 packet type 필드로 캡처한 호스트가 보낸 패킷인지 받은 패킷인지도 알 수 있습니다[7][8].

### 증명하지 못하는 것

파일 헤더에는 캡처한 기계, 인터페이스 이름, 캡처 필터, 캡처 도구가 버린(drop) 패킷 수가 들어갈 필드가 없습니다[1]. 그래서 pcap 파일만으로는 "이 캡처에 없는 트래픽은 없었다" 고 말할 수 없습니다. 필터에 걸러졌거나, 캡처 지점 밖을 지나갔거나, 장비가 과부하로 버렸을 수 있기 때문입니다. 캡처 필터와 잘림은 [캡처 필터와 잘린 패킷](capture-filters.md)에서 다룹니다. 캡처 호스트의 시계가 맞았는지, 현지 시간대가 무엇이었는지도 파일로는 알 수 없습니다.

pcap 에는 무결성 값이 없어서 편집 도구로 흔적 없이 바꿀 수 있습니다. 예를 들어 editcap `-t` 는 선택한 패킷의 시각을 초 단위로 옮기고, `-C` 는 패킷 앞이나 뒤의 바이트를 잘라 내며, `-L` 을 함께 주면 원래 길이까지 줄입니다[10]. `-L` 로 줄인 파일은 처음부터 작은 패킷을 캡처한 것처럼 보입니다. 그러므로 수집 직후 `capinfos -H` 나 별도 해시 도구로 해시를 기록해 두고, 분석은 사본으로 합니다.

### 손상과 비정상 종료

레코드에는 길이 정보만 있고 레코드 경계를 알리는 표시가 없어서, 캡처 길이 필드 하나가 깨지면 그 뒤 레코드를 잘못 읽게 됩니다. 캡처 길이는 SnapLen 을 넘을 수 없으므로, SnapLen 보다 큰 캡처 길이는 파일 손상이나 조작, 쓴 프로그램의 버그를 뜻할 가능성이 큽니다. libpcap 은 링크 종류별 최대치를 넘는 캡처 길이를 만나면 "invalid packet capture length" 오류를 내고 멈춥니다. 최대치 안이지만 SnapLen 보다 큰 레코드는 SnapLen 까지만 읽고 나머지를 버립니다. 이런 레코드는 Solaris 2.3 의 BUFMOD 문제, 스냅샷 길이를 잘못 기록한 libpcap 버전, 손상된 파일, 퍼징 도구가 만들거나 고친 파일에서 나옵니다[4]. 이런 레코드를 만나면 도구가 넘겨준 값만 믿지 말고 헥스로 레코드 헤더를 직접 확인합니다.

tcpdump 의 `-w` 출력은 버퍼를 거쳐 기록되므로, 캡처가 강제로 끝나면 마지막 패킷 몇 개가 파일에 없거나 마지막 레코드가 중간에서 끊겨 있을 가능성이 있습니다[6]. 파일 끝에서 레코드 헤더의 캡처 길이만큼 데이터가 남아 있지 않으면 비정상 종료를 먼저 의심합니다.

## 함정

**Reserved1 로 시간대를 추정하지 않습니다.** 옛 도구가 이 필드에 시간대 보정값을 쓴 적이 있지만, 읽는 쪽은 이 값을 무시해야 합니다(MUST)[1][2]. 레코드 시각은 언제나 UTC epoch 초로 해석합니다.

**파일 안 순서가 시간순이라는 보장이 없습니다.** 여러 CPU 코어가 시각을 찍으면 찍힌 순서와 파일에 들어간 순서가 달라질 수 있고, 시스템 시계에 맞춘 시각은 시계가 뒤로 조정되면 같이 뒤로 갑니다[5]. 그래서 첫 패킷과 마지막 패킷이 가장 이른 시각과 가장 늦은 시각이 아닐 수 있고, `capinfos -o` 로 시간순 여부를, `-a`·`-e` 로 실제 범위를 따로 확인합니다[9].

**패킷 간 시각 차이가 실제 간격과 다를 수 있습니다.** 인터럽트·폴링 지연, 타이머 해상도, 시계 동기화 조정 때문에 호스트가 찍은 시각에는 오차가 들어갑니다[5]. 캡처 장치(adapter)가 찍는 시각은 더 정밀하지만 호스트 시계와 맞춰져 있지 않을 수 있습니다[5]. 밀리초 단위 순서를 근거로 삼을 때는 이 오차를 감안합니다.

**나노초 파일을 마이크로초로 읽으면 자릿수가 사라집니다.** 도구 기본값이 마이크로초라서 나노초 파일의 아래 세 자리가 보고서에서 빠질 수 있습니다[5][6]. 매직 번호로 단위를 먼저 확인합니다.

**매직 번호가 네 가지만 있는 것은 아닙니다.** libpcap 은 Alexey Kuznetzov 가 고친 변형 형식(0xA1B2CD34)도 읽고, 소스에는 0xA1B234CD, 0xA12B3C4D(Navtel, 나노초) 같은 값도 정의되어 있습니다. Kuznetzov 변형은 레코드 헤더가 16바이트보다 깁니다. 매직 번호는 그대로 둔 채 레코드 헤더만 바꾼 변형과 레코드 헤더에 디버깅 정보를 더 넣은 변형도 있는데, libpcap 은 이런 변형을 구분하지 않습니다. Wireshark 는 처음 두 패킷을 레코드 헤더 형식마다 읽어 보는 방법으로 구분합니다[4]. 명세의 네 값이 아닌 매직을 만나면 레코드 헤더 길이부터 확인합니다.

**한 파일에는 링크 계층 종류가 하나뿐입니다.** 인터페이스가 여러 개이거나 링크 종류가 다른 캡처는 pcap 하나에 담기 어렵고, 파일 헤더가 레코드와 모양이 달라 파일 두 개를 단순히 이어 붙일 수도 없습니다[1]. 합친 파일이 필요하면 도구로 병합하는데, 방법은 [큰 캡처 파일 다루기](../../03-techniques/acquisition/large-captures.md)에서 다룹니다. editcap 은 기본 출력이 pcapng 라서, pcap 파일을 editcap 으로 처리하면 `-F pcap` 을 주지 않는 한 결과 파일은 pcapng 가 됩니다[10].

**옛 캡처는 SnapLen 이 작을 수 있습니다.** 현재 tcpdump 의 기본 SnapLen 은 262144바이트이고 `-s 0` 도 262144입니다[6]. 옛 버전으로 만든 파일은 훨씬 작은 값으로 잘려 있을 수 있으니, 본문을 복원하기 전에 `capinfos -l` 로 SnapLen 을 확인합니다[9]. 자세한 내용은 [캡처 필터와 잘린 패킷](capture-filters.md)에 있습니다.

**체크섬 오류와 큰 패킷은 캡처 위치 때문일 수 있습니다.** 캡처 호스트 자신이 보낸 패킷은 네트워크 카드가 체크섬을 채우기 전에 캡처되어 체크섬이 틀린 것처럼 보이고, 세그먼트 오프로딩 때문에 MTU 보다 큰 패킷이 보이기도 합니다. 원인과 확인 방법은 [어디서 캡처하나](capture-points.md)에서 다룹니다.

## 도구

| 도구 | 쓰는 곳 |
|---|---|
| capinfos | 형식·링크 종류·SnapLen·시각 범위·시간순 여부·해시 확인[9] |
| tcpdump | `-r` 로 읽기, `-tt` 로 UTC epoch 시각, `-XX` 로 헥스 출력, `--nano` 로 나노초 표시[6] |
| Wireshark·tshark | `frame.*` 필드로 시각·길이·파일 오프셋 확인[11] |
| editcap | 형식 변환(`-F pcap`), 시각 이동·자르기(원본이 아닌 사본에만)[10] |
| 헥스 편집기 | 파일 헤더와 레코드 헤더를 직접 확인 |

## 참고 문헌

1. G. Harris, M. Richardson, "PCAP Capture File Format", draft-ietf-opsawg-pcap. https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap/blob/master/draft-ietf-opsawg-pcap.md
2. The Tcpdump Group, pcap-savefile(5) 매뉴얼. https://github.com/the-tcpdump-group/libpcap/blob/master/pcap-savefile.manfile.in
3. IETF OPSAWG, LinkType 목록(linktypes.csv). https://github.com/IETF-OPSAWG-WG/draft-ietf-opsawg-pcap/blob/master/linktypes.csv
4. The Tcpdump Group, libpcap 소스 sf-pcap.c. https://github.com/the-tcpdump-group/libpcap/blob/master/sf-pcap.c
5. The Tcpdump Group, pcap-tstamp(7) 매뉴얼. https://github.com/the-tcpdump-group/libpcap/blob/master/pcap-tstamp.manmisc.in
6. The Tcpdump Group, tcpdump(1) 매뉴얼. https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.1.in
7. The Tcpdump Group, LINKTYPE_LINUX_SLL. https://www.tcpdump.org/linktypes/LINKTYPE_LINUX_SLL.html
8. The Tcpdump Group, LINKTYPE_LINUX_SLL2. https://www.tcpdump.org/linktypes/LINKTYPE_LINUX_SLL2.html
9. Wireshark, capinfos(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/capinfos.adoc
10. Wireshark, editcap(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
11. Wireshark, Display Filter Reference: Frame. https://www.wireshark.org/docs/dfref/f/frame.html
12. The Tcpdump Group, pcap-filter(7) 매뉴얼. https://github.com/the-tcpdump-group/libpcap/blob/master/pcap-filter.manmisc.in
