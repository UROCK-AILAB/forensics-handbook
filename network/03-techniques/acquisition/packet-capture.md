---
title: "패킷 캡처하기"
parent: "기법 · 조사 절차·수집"
nav_order: 330
---

# 패킷 캡처하기 (tcpdump·dumpcap)

조사 중에 새로 패킷을 잡아야 할 때 tcpdump 나 dumpcap 으로 캡처하는 절차를 다룹니다. 캡처 파일을 증거로 쓰려면 어디서 무엇을 얼마나 잡았는지, 도중에 버린 패킷이 있는지, 파일이 나중에 바뀌지 않았는지를 함께 남겨야 합니다. 두 도구의 저장·파일 나누기·통계 옵션이 파일 내용과 시각 해석에 어떤 영향을 주는지도 정리합니다.

## 언제 쓰나

패킷 캡처로는 이미 지나간 트래픽을 되살릴 수 없습니다. 의심 활동이 계속되거나 간헐적으로 되풀이될 때만 추가 캡처로 새 데이터를 얻을 수 있고, 활동이 이미 끝났으면 더 모을 것이 없습니다[1]. 예를 들어 IDS 경보에 두 호스트 사이의 이상한 통신이 나왔다면, 두 호스트가 주고받는 패킷을 모두 기록해 경보 한 줄보다 많은 정보를 얻을 수 있습니다[1]. 지나간 활동은 흐름 기록·Zeek 로그·방화벽 로그처럼 이미 쌓인 기록으로 봅니다([로그 수집과 보존](log-collection.md)).

캡처를 시작하기 전에 권한과 범위부터 정리합니다. 패킷에는 암호나 메일 본문 같은 민감한 정보가 의도치 않게 들어갈 수 있고, 이런 데이터를 오래 보관하면 조직의 보존 정책을 어길 수 있습니다[1]. 특정 사용자가 주고받는 패킷을 모두 기록하는 일은 공식 요청과 승인 절차를 마친 뒤에만 시작하고, 캡처하면서 한 일은 모두 기록합니다[1]. 수집 우선순위와 증거물 관리 연속성 (chain of custody) 은 [조사 절차](investigation-process.md) 에서 다룹니다.

## 절차

### 1. 캡처 지점과 범위를 정한다

호스트에서 잡는지, 스위치의 포트 미러링 (SPAN) 이나 네트워크 탭 (TAP) 에서 잡는지에 따라 파일에 빠지는 패킷이 달라집니다. 지점별 차이는 [어디서 캡처하나](../../01-foundations/capture/capture-points.md) 에 있습니다. 캡처 필터로 거른 패킷과 스냅 길이 (SnapLen) 밖의 바이트는 파일에 아예 남지 않아서 나중에 되살릴 수 없으므로, 필터는 디스크와 처리 속도가 허락하는 한 넓게 잡습니다. 필터 문법과 기본 스냅 길이는 [캡처 필터와 잘린 패킷](../../01-foundations/capture/capture-filters.md) 에서 다룹니다.

### 2. 도구 버전과 인터페이스를 기록한다

`tcpdump --version` 은 tcpdump 와 libpcap 의 버전 문자열을, `dumpcap -v` 는 전체 버전 정보를 출력합니다[2][4]. 두 도구 모두 `-D` 로 캡처할 수 있는 인터페이스 목록을 번호·이름·설명과 함께 보여 주고, `-i` 에는 이름 대신 이 번호를 넣을 수 있습니다[2][4]. Windows 는 인터페이스 이름이 길고 대개 GUID 가 들어 있어서 번호가 편합니다[4].

`-i` 를 빼면 tcpdump 는 켜져 있는 인터페이스 중 번호가 가장 낮은 것(루프백 제외)을, dumpcap 은 첫 번째 비루프백 인터페이스를 고릅니다[2][4]. 도구가 고른 인터페이스가 의도한 것과 다를 수 있으니 `-i` 는 늘 적습니다. Linux 와 최근 macOS·Solaris 의 tcpdump 에서 `-i any` 는 OS 의 일반 인터페이스를 모두 잡는 가상 인터페이스이고, 이때는 무차별 모드 (promiscuous mode) 로 캡처하지 않습니다[2]. 인터페이스에서 패킷을 읽으려면 특별한 권한이 필요할 수 있지만, 저장된 파일을 읽을 때는 필요 없습니다[2].

### 3. 저장 옵션을 고른다

두 도구는 기본 형식과 크기 단위가 달라서 같은 숫자를 넣어도 결과가 다릅니다.

| 항목 | tcpdump | dumpcap |
|---|---|---|
| 저장 형식 | pcap[2] | pcapng. `-F` 로 pcap 가능, 여러 인터페이스를 잡으면 `-F` 와 상관없이 pcapng[4] |
| 저장 파일 | `-w 파일`, `-w -` 는 표준 출력[2] | `-w 파일`. 없으면 임시 폴더에 무작위 이름으로 저장[4] |
| 스냅 길이 | `-s`, 기본 262144바이트[2] | `-s`, 기본 0 = 262144바이트[4] |
| 캡처 버퍼 | `-B`, KiB 단위[2] | `-B`, MiB 단위, 기본 2 MiB[4] |
| 크기로 파일 나누기 | `-C`, 기본 단위 1,000,000바이트, k·m·g 를 붙이면 1024 계열[2] | `-b filesize:값`, kB 단위, 최대 2 TB[4] |
| 시간으로 파일 나누기 | `-G 초`[2] | `-b duration:초`, `-b interval:초`(정확히 배수인 시각에 전환)[4] |
| 파일 개수 제한 | `-W 개수`[2] | `-b files:개수`(100000 미만)[4] |
| 닫힌 파일 처리 | `-z 명령`, Windows 에서는 쓸 수 없음[2] | `-b printname:파일`(stdout·stderr 가능)[4] |
| 자동 정지 | `-c 개수`, 그 외에는 SIGINT·SIGTERM 까지[2] | `-a duration·files·filesize·packets`, `-c 개수`[4] |

tcpdump 의 `--time-stamp-precision` 은 기본값이 micro 이고, nano 로 저장하면 파일의 매직 번호가 바뀌어 읽지 못하는 프로그램이 있습니다[2]. dumpcap 의 `-f`·`-s`·`-B` 는 첫 `-i` 앞에 쓰면 모든 인터페이스의 기본값이 되고, `-i` 뒤에 쓰면 그 인터페이스에만 적용됩니다[4].

### 4. 캡처를 시작한다

아래 명령은 모두 만든 예시입니다. tcpdump 로 한 파일에 저장할 때는 필터 식을 옵션 뒤 `--` 다음에 따옴표로 묶은 한 덩어리로 씁니다[2]. Windows cmd.exe 에서는 작은따옴표 대신 큰따옴표를 씁니다[2].

```sh
# 만든 예시: 한 파일에 저장, 패킷마다 바로 파일에 쓰기
tcpdump -i eth0 -U -w /cases/2026-001/edge01.pcap -- 'host 192.0.2.10'

# 만든 예시: 1시간마다 새 파일, 파일 이름에 strftime 형식 사용
tcpdump -i eth0 -G 3600 -w '/cases/2026-001/edge01_%Y%m%d_%H%M%S.pcap' -- 'host 192.0.2.10'
```

`-w` 출력은 파일이나 파이프로 쓸 때 버퍼를 거쳐서, 패킷을 받은 뒤 한동안 파일에 나타나지 않을 수 있습니다[2]. `-U` 를 주면 패킷을 저장할 때마다 바로 파일에 씁니다[2]. `-G` 를 쓸 때 파일 이름에 시각 형식이 없으면 새 파일이 앞 파일을 덮어쓰고, 만들어진 이름이 겹쳐도 덮어쓰므로 나누는 주기보다 거친 시각 형식은 쓰지 않습니다[2].

dumpcap 은 `--capture-comment` 로 사건 번호나 캡처 지점을 파일 안에 적을 수 있습니다. 이 옵션은 한 파일로 저장할 때만 쓸 수 있고, 여러 번 줄 수 있지만 Wireshark 는 첫 주석만 보여 줍니다[4]. `--ifname`·`--ifdescr` 로 파일에 기록할 인터페이스 이름과 설명을 정할 수도 있습니다[4].

```bat
:: 만든 예시: 한 파일에 저장하고 주석 남기기
dumpcap -i 2 -f "host 192.0.2.10" --capture-comment "case 2026-001, core switch SPAN port" -w D:\cases\2026-001\edge01.pcapng

:: 만든 예시: 매시 정각에 새 파일, 닫힌 파일 이름을 표준 출력으로
dumpcap -i 2 -f "host 192.0.2.10" -b interval:3600 -b printname:stdout -w D:\cases\2026-001\edge01.pcapng
```

두 번째 명령처럼 `-b files:` 없이 나누면 정지 조건에 걸리거나 디스크가 찰 때까지 새 파일을 계속 만듭니다[4]. 파일 이름은 기본으로 `edge01_00001_20260927090000.pcapng`(만든 예시)처럼 `-w` 이름 뒤에 다섯 자리 번호와 파일을 만든 날짜·시각이 붙습니다[4][6]. tshark 에 `-b nametimenum:2` 를 주면 날짜·시각이 번호 앞에 와서 이름순 정렬이 만든 순서와 같아집니다[7].

### 5. 캡처 중 손실을 지켜본다

dumpcap `-S` 는 인터페이스별 통계를 1초마다 출력합니다[4]. tcpdump 는 `-w` 로 저장하면서 `-v` 를 주면 1초마다 잡은 패킷 수를 stderr 로 출력하지만, Solaris·FreeBSD 등에서는 이 출력이 커널에서 tcpdump 로 가는 패킷을 잃게 할 수 있습니다[2]. SIGINFO 를 지원하는 BSD·macOS 에서는 상태 문자(보통 Ctrl-T)로, 그렇지 않은 곳에서는 SIGUSR1 로 캡처를 멈추지 않고 중간 통계를 볼 수 있습니다[2]. 버린 패킷이 생기면 캡처 버퍼(`-B`)를 늘려 볼 수 있지만, 시스템이나 인터페이스가 지정한 값을 조용히 낮추거나 높일 수 있습니다[4].

### 6. 정상 종료하고 통계를 기록한다

tcpdump 는 `-c` 개수를 채우거나 SIGINT(Ctrl-C)·SIGTERM 을 받으면 멈춥니다[2]. 끝날 때 세 가지 수를 출력합니다[2].

| 출력 | 뜻 |
|---|---|
| captured | tcpdump 가 받아서 처리한 패킷 수 |
| received by filter | OS 에 따라 뜻이 다름. 필터와 상관없이 세거나, 필터에 맞은 것만 세거나, 필터에 맞고 tcpdump 가 처리한 것만 셈 |
| dropped by kernel | 버퍼가 모자라 OS 의 캡처 기능이 버린 수. OS 가 알려 주지 않으면 0 |

pcap 파일에는 이 수를 적을 곳이 없으므로 화면 출력을 그대로 보관합니다([pcap 형식](../../01-foundations/capture/pcap.md)). dumpcap 은 한 파일로 저장한 pcapng 에만 캡처를 마치면서 받은 수와 버린 수를 인터페이스 통계 블록 (ISB) 으로 적고, `-b` 로 나눠 저장하면 ISB 를 쓰지 않습니다[5]. 나눠 저장했다면 종료 때 화면에 나온 개수를 따로 남깁니다. ISB 의 필드는 [pcapng 형식](../../01-foundations/capture/pcapng.md) 에 있습니다.

### 7. 해시를 계산하고 사본으로 분석한다

캡처를 마치면 원본과 사본의 해시를 계산해 같은지 확인하고, 분석은 사본으로만 합니다[1]. `capinfos -H` 는 SHA256 과 SHA1 해시를 출력합니다[8]. 여러 파일로 나눠 저장할 때는 dumpcap `printname` 이나 tcpdump `-z` 로 방금 닫힌 파일을 알 수 있으므로, 닫히는 대로 다른 곳에 옮기고 해시를 계산합니다[2][4]. 파일을 합치거나 나누는 방법은 [큰 캡처 파일 다루기](large-captures.md) 에 있습니다.

### 8. 캡처 기록을 남긴다

캡처 파일과 함께 다음을 적어 둡니다. 실행한 명령 전체, 도구와 libpcap 버전, 캡처 지점과 인터페이스, 캡처 필터, 캡처 호스트의 시간대와 시계 동기 상태, 시작·종료 시각, 종료 통계, 파일 이름과 해시입니다. pcap 파일에는 인터페이스 이름과 캡처 필터가 남지 않습니다([pcap 형식](../../01-foundations/capture/pcap.md)). dumpcap 이 만든 pcapng 는 섹션 헤더에 캡처 주석·CPU 정보·OS·dumpcap 이름과 버전을, 인터페이스 설명 블록에 인터페이스 이름(`--ifname` 우선)·설명·캡처 필터 문자열·OS 를 적지만[5], 캡처 지점과 시계 상태는 파일에 없으므로 따로 적어야 합니다.

## 도구

| 도구 | 쓰임 |
|---|---|
| tcpdump | libpcap 기반 캡처. pcap 으로 저장하고 `-C`·`-G`·`-W` 로 파일을 나눔[2] |
| dumpcap | Wireshark 배포판에 들어 있는 캡처 도구. pcapng 기본, 파일 안에 인터페이스·필터·통계를 남김[4][5] |
| tshark | `-b`·`-a` 로 파일 나누기와 자동 정지를 설정하고, `-b` 에는 `nametimenum` 이 있음. 실시간 캡처로 쓸 수 있는 형식은 pcapng·pcap 뿐[7] |
| capinfos | 해시(`-H`), 가장 이른 패킷 시각(`-a`), 가장 늦은 패킷 시각(`-e`), 캡처 기간(`-u`) 확인[8] |
| editcap | 공유 전에 프로세스 정보 지우기(`--discard-process-info`)[9] |

tshark 로 캡처하면서 파일에 저장할 때는 디스플레이 필터를 쓸 수 없습니다[7]. 저장 없이 실시간 캡처에 디스플레이 필터를 걸면 처리가 밀려 패킷을 잃을 가능성이 커지므로, 거르는 일은 캡처 필터로 합니다[7]. 저장한 파일을 읽는 방법은 [Wireshark·tshark로 읽기](../analysis/wireshark.md) 에서 다룹니다.

## 함정과 한계

**순환 버퍼는 오래된 파일을 지웁니다.** tcpdump 에 `-C` 와 `-W` 를 함께 주면 개수에 이른 뒤 첫 파일부터 덮어쓰고[2], dumpcap `-b files:` 도 개수에 이르면 첫 파일의 데이터를 버리고 그 파일에 다시 씁니다[4]. dumpcap 은 다음 파일을 열기 전에 재사용할 옛 파일을 지웁니다[6]. 증거로 쓸 캡처는 파일 개수를 제한하지 않거나, 닫힌 파일을 바로 다른 곳으로 옮깁니다.

**`-C` 는 두 도구에서 뜻이 다릅니다.** tcpdump `-C` 는 파일 크기 기준이지만[2], dumpcap `-C` 는 캡처한 패킷을 메모리에 담아 두는 바이트 한도입니다[4]. dumpcap 에서 크기로 나누려면 `-b filesize:` 를 씁니다.

**`-w` 없는 dumpcap 은 임시 폴더에 저장합니다.** UNIX 계열은 `$TMPDIR`(없으면 보통 `/tmp`), Windows 는 `%TEMP%`(보통 `%USERPROFILE%\AppData\Local\Temp`)이고 `--temp-dir` 로 바꿀 수 있습니다[4]. 임시 폴더를 정리하면 캡처 파일이 함께 사라질 수 있습니다.

**tcpdump 를 강제로 끝내면 마지막 패킷이 빠질 수 있습니다.** `-w` 출력은 버퍼가 찰 때 파일에 쓰이므로[2], 정상 종료 없이 프로세스가 끝나면 버퍼에 남은 패킷이 파일에 없을 가능성이 있습니다. `-U` 를 쓰거나, `-w` 와 함께 쓸 때 SIGUSR2 로 버퍼를 파일에 강제로 쓴 뒤 SIGINT·SIGTERM 으로 끝냅니다[2]. dumpcap 이 강제로 끝나면 ISB 없이 파일이 끝납니다([pcapng 형식](../../01-foundations/capture/pcapng.md)).

**tcpdump `-G` 는 정확한 경계에서 나누지 않습니다.** 지정한 초가 지난 뒤 첫 패킷이 올 때 파일을 바꿉니다[3]. 트래픽이 뜸하면 파일 이름의 시각과 나누는 경계가 어긋납니다. dumpcap `-b interval:` 은 정확히 배수인 시각에 전환합니다[4].

**호스트에서 잡은 나가는 패킷의 체크섬이 틀려 보일 수 있습니다.** 체크섬 계산을 하드웨어에 맡기는 인터페이스에서 캡처하면 나가는 TCP 체크섬이 모두 불량으로 표시될 수 있습니다[2]. 조작 흔적으로 읽지 않습니다. tcpdump `-K` 는 체크섬 검증을 끕니다[2].

**캡처 파일에 민감한 정보가 들어갈 수 있습니다.** dumpcap 의 `--process-info=full` 은 패킷을 주고받은 프로세스의 명령줄과 사용자까지 파일에 그대로 넣어서, 명령줄에 들어 있던 암호나 토큰이 파일에 남을 수 있습니다[4]. 공유 전에 editcap `--discard-process-info` 로 지웁니다[9]. 옵션이 있는지는 `dumpcap -h` 로 확인합니다.

**조사자의 설정도 장비 기록에 남습니다.** 스위치에서 캡처를 설정하면 장비 로그에 명령이 남고, Sigma 규칙 "Cisco Sniffing" 처럼 `monitor capture point`·`set span`·`set rspan` 명령을 탐지하는 규칙에 걸릴 수 있습니다[10]. 나중에 다른 분석가가 이를 공격자 흔적으로 오해하지 않도록 설정한 시각과 명령을 기록합니다.

**USB 로 연결한 네트워크 어댑터는 시각이 부정확합니다.** 패킷이 USB 를 거쳐 커널에 닿은 뒤에 시각이 찍혀서, 정밀한 시각이 필요하면 쓰지 않습니다[11].

## 결과를 어떻게 해석하나

### 증명하는 것 / 증명하지 못하는 것

캡처 파일은 캡처한 시간 동안 그 지점을 지나가고 캡처 필터를 통과한 패킷을 스냅 길이만큼 담고 있다는 것을 증명합니다. dumpcap 이 한 파일로 저장한 pcapng 라면 ISB 의 받은 수와 버린 수로 캡처 도중 호스트에서 버린 패킷이 있었는지도 확인할 수 있습니다[5].

캡처 시작 전과 종료 뒤의 트래픽, 캡처 지점을 지나지 않은 트래픽, SPAN 포트처럼 캡처 호스트보다 앞에서 버려진 패킷은 파일에 없고, 없었다는 증거도 되지 않습니다. 패킷 시각은 캡처 호스트의 시계를 따르므로, 시각이 정확한지도 파일만으로는 알 수 없습니다. pcap 파일이나 여러 파일로 나눈 dumpcap 파일에는 버린 패킷 수가 없어서, 종료 때 기록한 통계가 없으면 손실 여부를 확인할 수 없습니다.

보고서에는 "이 시간대에 이 캡처 지점에서, 이 필터로 잡은 패킷 중에 192.0.2.10 과 203.0.113.5 사이의 흐름이 있다(만든 예시)" 처럼 캡처 조건과 함께 씁니다. "이 호스트는 그 밖의 통신을 하지 않았다" 는 캡처 범위가 그 호스트의 모든 경로를 덮고 버린 패킷이 0 일 때만 쓸 수 있습니다.

### 시각

패킷 시각은 캡처 호스트의 커널이 패킷을 처리할 때 찍은 도착 시각이고, pcap 형식에는 UTC 로 저장됩니다[11]. Windows 에서는 Npcap 이 시스템 시간대 설정으로 UTC 를 계산하므로, 시간대가 잘못 설정돼 있으면 화면의 현지 시각이 맞아 보여도 저장된 UTC 가 틀릴 수 있습니다[11]. Wireshark 는 파일을 여는 컴퓨터의 현지 시각으로 보여 주므로, 캡처한 곳과 시간대가 다르면 표시 시각도 달라집니다[11]. tcpdump 는 일광 절약 시간 전환을 가로지르는 캡처에서 시간 변경을 무시해서 시각이 어긋나 보입니다[2]. 시각 스탬프 형식과 정밀도는 [pcap 형식](../../01-foundations/capture/pcap.md)·[pcapng 형식](../../01-foundations/capture/pcapng.md), 여러 기록의 시각을 맞추는 방법은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md) 에서 다룹니다.

파일 이름에 붙은 시각은 패킷 시각이 아닙니다. tcpdump `-G` 는 파일을 바꾸는 시점의 시각을 캡처 호스트의 현지 시각(`localtime()`)으로 이름에 넣고[3], dumpcap `-b` 는 파일을 여는 시점의 현지 시각을 `%Y%m%d%H%M%S` 형식으로 넣습니다[6]. 둘 다 UTC 가 아니므로, 파일 안의 실제 범위는 `capinfos -a`·`-e` 로 가장 이른 패킷과 가장 늦은 패킷 시각을 보고 확인합니다[8]. 캡처를 시작하고 끝낸 시각은 패킷이 없던 구간까지 포함해 ISB 의 시작·종료 시각에 남습니다([pcapng 형식](../../01-foundations/capture/pcapng.md)).

## 참고 문헌

1. Karen Kent, Suzanne Chevalier, Tim Grance, Hung Dang, "Guide to Integrating Forensic Techniques into Incident Response", NIST Special Publication 800-86, 2006. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
2. The Tcpdump Group, tcpdump(1). https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.1.in
3. The Tcpdump Group, tcpdump.c. https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.c
4. Wireshark, dumpcap(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/dumpcap.adoc
5. Wireshark, dumpcap.c. https://github.com/wireshark/wireshark/blob/master/dumpcap.c
6. Wireshark, ringbuffer.c. https://github.com/wireshark/wireshark/blob/master/ringbuffer.c
7. Wireshark, tshark(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
8. Wireshark, capinfos(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/capinfos.adoc
9. Wireshark, editcap(1). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
10. SigmaHQ, Cisco Sniffing (cisco_cli_net_sniff.yml). https://github.com/SigmaHQ/sigma/blob/master/rules/network/cisco/aaa/cisco_cli_net_sniff.yml
11. Wireshark User's Guide, Time Stamps · Time Zones. https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_advanced.adoc
