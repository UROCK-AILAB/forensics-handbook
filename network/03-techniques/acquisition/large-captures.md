---
title: "큰 캡처 파일 다루기"
parent: "기법 · 조사 절차·수집"
nav_order: 340
---

# 큰 캡처 파일 다루기 (editcap·mergecap·capinfos)

센서가 오래 저장한 캡처 파일은 크기가 커서 Wireshark 에 한 번에 열거나 분석 엔진에 통째로 넣기 어렵고, 순환 버퍼로 저장했다면 수십~수백 개 파일로 나뉘어 있기도 합니다. 이 페이지에서는 원본을 건드리지 않고 파일 목록과 시간 범위부터 정리한 뒤, 필요한 구간을 잘라 내고, 나누고, 합치고, 중복 패킷을 지워 분석 엔진에 넣는 순서를 다룹니다. 이렇게 가공한 파일은 원본과 해시가 다른 새 파일이라서, 어떤 명령으로 만들었는지를 함께 남겨야 증거로 쓸 수 있습니다.

## 언제 쓰나

캡처 파일이 너무 커서 tshark 두 번 읽기(`-2`)나 Wireshark 가 메모리 부족으로 느려질 때, 사건 시간대만 떼어 다른 분석가나 기관에 넘겨야 할 때 씁니다. SPAN 포트 여러 개나 캡처 지점 여러 곳에서 받은 파일을 한 시간축으로 합쳐 봐야 할 때도 이 순서를 따릅니다. 합치면 같은 패킷이 두 번 들어가거나 센서마다 시계가 달라 순서가 뒤섞이는데, 이런 문제를 합치기 전후에 확인하는 방법까지 함께 봅니다.

캡처를 새로 뜨는 방법과 순환 파일 이름 규칙은 [패킷 캡처하기](packet-capture.md)에, pcap·pcapng 파일 구조는 [pcap 형식](../../01-foundations/capture/pcap.md)과 [pcapng 형식](../../01-foundations/capture/pcapng.md)에 있습니다. 가공을 마친 파일을 읽는 방법은 [Wireshark·tshark로 읽기](../analysis/wireshark.md)에서 이어집니다.

## 절차

아래 예시의 파일 이름, 시각, 숫자는 모두 만든 예시입니다. 명령마다 도구 버전(`editcap -v` 등), 입력 파일 해시, 출력 파일 해시를 작업 기록에 함께 적습니다.

### 1. 원본 해시를 남기고 작업 사본에서만 작업한다

capinfos `-H` 는 파일의 SHA256 과 SHA1 을 출력하고, SHA1 출력은 나중 버전에서 빠질 수 있습니다[5]. 원본의 SHA-256 을 먼저 기록하고, 사본을 만든 뒤 사본의 해시가 같은지 확인한 다음 사본으로만 작업합니다.

```
capinfos -H sensor1_20260302.pcap
```

editcap·mergecap 은 입력이 pcap 이어도 기본으로 pcapng 형식으로 씁니다[1][3]. 그래서 pcap 원본을 이 도구로 한 번이라도 거치면 해시뿐 아니라 파일 형식까지 원본과 달라집니다. 작업 기록에 "pcap 을 pcapng 로 바꿔 저장했다"는 사실도 적습니다.

### 2. 파일 목록과 시간 범위를 표로 정리한다

파일이 여러 개면 capinfos 의 표 형식으로 한 줄에 한 파일씩 정리합니다. `-T` 는 표 형식, `-m` 은 쉼표 구분, `-Q` 는 큰따옴표로 값을 감싸서 CSV 가 됩니다[5]. 개별 항목 옵션을 하나라도 주면 모든 항목을 내는 기본 동작이 꺼지고 고른 항목만 나옵니다[5].

```
capinfos -T -m -Q -t -E -c -s -a -e -S -u -o -l -H sensor1_*.pcap > inventory.csv
```

표에서 먼저 볼 값은 셋입니다. `-o` 가 `False` 이면 시간순이 아닌 패킷이 하나 이상 있다는 뜻이고[5], 이런 파일은 5단계에서 합치기 전에 정렬해야 합니다. `-a`·`-e` 는 가장 이른·가장 늦은 패킷 시각이라 순서가 뒤섞인 파일에서는 첫 패킷·마지막 패킷 시각과 다를 수 있고[5], `-S` 를 함께 주면 이 두 시각을 1970-01-01 이후 초(epoch)로 보여 줍니다[5]. epoch 는 1970-01-01 00:00:00 UTC 부터 센 초라서 분석 PC 의 시간대와 상관없이 파일끼리 비교하기 좋습니다[3]. `-E` 의 링크 유형(encapsulation)이 파일마다 다르면 5단계의 합치기 결과 형식에 영향이 있습니다.

capinfos 는 파일을 열거나 읽다가 오류가 나도 다음 파일로 넘어가고, 오류는 표준 오류(stderr)에 쓰며 끝날 때 오류 상태로 종료합니다[5]. 목록이 조용히 만들어졌어도 표준 오류와 종료 상태를 따로 확인해야 손상된 파일을 놓치지 않습니다. 첫 오류에서 멈추게 하려면 `-C` 를 줍니다[5]. 각 항목을 보고서에 옮기는 방법은 [네트워크 포렌식 보고서](../reporting/forensic-report.md)의 capinfos 표에 있습니다.

### 3. 필요한 구간만 잘라 낸다

시간으로 자를 때는 editcap `-A`(이 시각 이후, 같은 시각 포함)와 `-B`(이 시각 전)를 씁니다[1]. 시각은 ISO 8601 형식 `YYYY-MM-DD HH:MM:SS[.nnnnnnnnn][Z|±hh:mm]` 또는 날짜와 시각 사이에 `T` 를 넣은 형식으로 쓰고, 시간대를 빼면 editcap 을 실행하는 PC 의 현지 시각으로 해석합니다[1]. epoch 형식(초와 나노초를 마침표나 쉼표로 구분)은 UTC 기준입니다[1]. 분석 PC 의 시간대 설정에 결과가 달라지지 않도록 `Z` 나 `+09:00` 을 꼭 붙입니다.

```
editcap -A "2026-03-02 09:00:00+09:00" -B "2026-03-02 10:00:00+09:00" sensor1_work.pcapng sensor1_0900-1000.pcapng
```

패킷 번호로 고를 수도 있습니다. 명령 끝에 번호나 `시작-끝` 범위를 주면 기본으로는 그 패킷을 **빼고** 쓰고, `-r` 을 주면 그 패킷**만** 씁니다[1]. 두 동작이 반대라서 `-r` 을 빠뜨리면 원하는 패킷만 사라진 파일이 만들어집니다.

```
editcap -r sensor1_work.pcapng pkt200-750.pcapng 200-750
```

주소나 프로토콜로 고를 때는 tshark 나 tcpdump 를 씁니다. `tshark -r 입력 -Y 필터 -w 출력` 은 필터에 맞는 패킷뿐 아니라 그 패킷이 의존하는 패킷(IP 조각 등)까지 파일에 씁니다[6]. `tcpdump -r 입력 -w 출력 '식'` 은 식에 맞는 패킷만 쓰고[7], tcpdump 가 쓰는 파일은 pcap 형식입니다[7]. tshark `-Y` 는 표시 필터 문법을, tcpdump 는 캡처 필터 문법을 쓰므로[6][7] [캡처 필터와 잘린 패킷](../../01-foundations/capture/capture-filters.md)을 함께 봅니다.

### 4. 한 번에 다룰 수 있는 크기로 나눈다

editcap `-c 개수` 는 패킷 수로, `-i 초` 는 시간 간격으로 파일을 나누고, 두 옵션은 함께 쓸 수 없습니다[1]. `-i` 에는 0.5 같은 소수도 줄 수 있습니다[1]. 나뉜 파일 이름에는 확장자 앞에 `_nnnnn[_YYYYmmddHHMMSS]` 가 들어갑니다. 번호는 00000 부터 시작하고, 입력 파일에 시각 정보가 없으면 뒤의 일시가 빠집니다[1].

editcap 은 이 일시를 `localtime()` 으로 만들어서, 이름의 일시는 UTC 가 아니라 분석 PC 의 현지 시각입니다[2]. 매뉴얼은 `-c`·`-i` 모두 이 일시가 그 파일 첫 패킷의 시각이라고 적지만[1], 코드에서 그대로 맞는 것은 `-c` 입니다[2]. `-i` 로 나누면 간격의 기준은 입력 파일의 첫 패킷 시각이고, 두 번째 파일부터는 이름에 그 파일 첫 패킷의 시각이 아니라 **간격이 시작하는 시각**을 넣습니다[2]. 패킷이 하나도 없는 간격도 파일을 열었다 닫으므로 빈 파일이 생길 수 있습니다[2].

```
editcap -i 3600 sensor1_work.pcapng hour.pcapng
```
```
hour_00000_20260302090312.pcapng
hour_00001_20260302100312.pcapng
hour_00002_20260302110312.pcapng
```
(만든 예시: 분석 PC 가 UTC+9 이고 첫 패킷이 09:03:12 일 때입니다. 간격은 매시 정각이 아니라 09:03:12 부터 한 시간씩이고, `hour_00001` 의 첫 패킷이 10:15 에 있어도 이름은 10:03:12 입니다.)

그래서 나눈 파일 이름의 일시로 시간대를 판단하지 않고, 파일마다 `capinfos -a -e -S` 로 실제 패킷 시각 범위를 다시 확인합니다. 매시 정각처럼 경계를 정확히 맞춰야 하면 `-i` 대신 3단계의 `-A`·`-B` 로 구간마다 잘라 냅니다.

### 5. 여러 파일을 한 시간축으로 합친다

mergecap 은 기본으로 각 프레임의 시각을 기준으로 시간순으로 합치고, 이때 입력 파일 하나하나는 이미 시간순이라고 가정합니다[3]. 그래서 2단계에서 `-o` 가 `False` 였던 파일은 reordercap 으로 먼저 정렬합니다. reordercap 은 시각이 커지는 순서로 프레임을 다시 쓰고 입력과 같은 형식으로 저장하며, `-n` 을 주면 이미 순서대로인 파일은 출력하지 않습니다[4]. `-a` 를 주면 mergecap 이 시각을 보지 않고 첫 파일의 패킷 전부, 다음 파일의 패킷 전부 순서로 이어 붙입니다[3].

```
reordercap sensor2_work.pcapng sensor2_sorted.pcapng
mergecap -w merged.pcapng sensor1_work.pcapng sensor2_sorted.pcapng
```

입력 파일들의 링크 유형이 모두 같으면 출력도 그 유형이 되고, 다르면 패킷마다 링크 유형이 붙는 방식(WTAP_ENCAP_PER_PACKET)이 됩니다[3]. pcap 형식은 이 방식을 지원하지 않아서 `-F pcap` 으로 쓰면 파일을 만들지 못합니다[3]. 인터페이스 정보 블록(IDB)을 어떻게 합칠지는 `-I none|all|any` 로 정하고, 기본값 `all` 은 모든 입력의 IDB 개수와 내용이 같을 때만 하나로 합칩니다[3]. 캡슐화·이름·속도·시각 정밀도·주석·설명 등이 모두 같아야 같은 IDB 로 봅니다[3].

mergecap 은 기본으로 합친 파일 목록을 담은 캡처 주석 "File created by merging: ..." 을 출력 파일에 넣습니다[3]. 이 주석이 65535바이트를 넘으면 아무 알림 없이 빠지고, `--no-merging-comment` 로 아예 끌 수도 있습니다[3]. 파일이 수천 개면 주석이 없을 수 있으니 합친 파일 목록은 작업 기록에 따로 남깁니다.

센서마다 시계가 다르면 합치기 전에 한쪽 시각을 옮깁니다. `capinfos -aeS` 로 두 파일의 시작·끝 시각을 epoch 로 확인하고, 시차를 알거나 추정할 수 있을 때 `editcap -t 초` 로 한쪽 파일의 모든 패킷 시각을 옮긴 뒤 합칩니다[1][3]. 같은 구간을 두 센서가 함께 잡았다면 `editcap -V -D 0` 으로 두 파일의 패킷마다 번호·길이·MD5 를 뽑아[1] 같은 패킷의 짝을 찾고, 그 시각 차를 시차의 근거로 삼을 수 있습니다. 시차를 모르면 옮기지 않고 합친 뒤 "두 센서의 시계 차이는 확인되지 않았다"고 보고서에 적습니다.

```
capinfos -aeS sensor1_work.pcapng sensor2_sorted.pcapng
editcap -t 3.5 sensor2_sorted.pcapng sensor2_shift.pcapng
mergecap -w merged.pcapng sensor1_work.pcapng sensor2_shift.pcapng
```
(만든 예시: sensor2 의 시계가 3.5초 늦다고 확인된 경우입니다.)

Wireshark 화면에서도 합칠 수 있습니다. 여러 파일을 창에 끌어다 놓으면 시간순으로 합쳐 임시 파일에 담습니다[8]. 캡처할 때 여러 파일로 나눠 저장한 묶음은 "파일 세트(file set)"로 열 수 있는데, Wireshark 는 현재 파일과 같은 폴더에서 접두사·접미사가 같은 파일을 찾아 묶습니다[8]. 같은 접두사·접미사로 만든 세트가 둘 이상이면 하나로 잘못 묶고, 이름을 바꾸거나 여러 폴더에 흩어 두면 일부를 찾지 못합니다[8]. Wireshark 사용자 안내서는 파일 세트 이름 형식을 4.4.0 부터 `접두사_일시_번호`, 그 전에는 `접두사_번호_일시` 로 적지만[8], tshark 매뉴얼은 `접두사_번호_일시` 를 기본으로, `-b nametimenum:2` 를 줄 때만 `접두사_일시_번호` 로 적습니다[6]. 그래서 이름 순서만 보고 Wireshark 버전을 판단하지 않습니다.

### 6. 중복 패킷을 지운다

캡처 지점 여러 곳의 파일을 합치면 같은 패킷이 두 번 이상 들어갈 수 있습니다. editcap 은 패킷의 길이와 MD5 를 비교해 같은 패킷을 건너뜁니다[1].

| 옵션 | 비교 범위 | 참고 |
|---|---|---|
| `-d` | 직전 4개 패킷 | `-D 5` 와 같습니다[1] |
| `-D 창` | 직전 (창 − 1)개 패킷 | 창은 0~1000000 입니다. 창이 크면 처리 시간이 매우 길어집니다[1] |
| `-w 초` | 상대 도착 시각이 이 값 이내인 앞 패킷(최대 1000000개) | 패킷이 시간순이라고 가정하므로 순서가 어긋나면 일부 중복을 놓칩니다[1] |
| `-I 바이트` | 프레임 앞부분을 이 길이만큼 빼고 MD5 계산 | 여러 라우터에서 잡아 MAC 주소 등이 다른 패킷용. 이더넷·IPv4 는 `-I 26` (이더넷 헤더 14 + 출발지·목적지 주소 앞 IPv4 헤더 12)[1] |
| `--skip-radiotap-header` | radiotap 헤더를 빼고 비교 | 같은 채널을 여러 무선 장치로 잡아 합친 파일용[1] |

```
editcap -D 101 -I 26 merged.pcapng merged_dedup.pcapng
```

길이와 MD5 가 모두 같아야 지우므로, 한 지점에서만 VLAN 태그가 붙어 있는 식으로 바이트가 조금이라도 다르면 남습니다. 이더넷 캡처의 VLAN 태그는 `editcap -L -C 12:4` 로 떼어 낼 수 있습니다[1]. `-V` 를 함께 주면 건너뛴 패킷이든 아니든 모든 패킷의 MD5 를 출력합니다[1]. 중복 제거 전후의 패킷 수(`capinfos -c`)를 모두 기록합니다.

### 7. 분석 엔진에 넣는다

tshark 의 두 번 읽기 `-2` 는 '응답 프레임' 처럼 뒤에 올 패킷을 봐야 채우는 필드와 재조립 의존 관계를 계산하고, 첫 번째 읽기가 끝날 때까지 출력을 쌓아 둡니다. 입력을 뒤로 되돌려 읽어야 해서 실시간 캡처나 파이프 입력에는 쓸 수 없습니다[6]. 읽기 필터 `-R` 은 `-2` 와 함께 쓸 때만 뜻이 있고 뒤를 봐야 하는 필드는 쓸 수 없습니다[6]. `-M 개수` 는 그 패킷 수마다 내부 세션을 초기화하는데, `-2` 와 함께 쓸 수 없습니다[6]. 파일이 크면 3·4단계에서 먼저 줄인 뒤 `-2` 를 씁니다. `-z` 통계는 `-Y` 표시 필터와 상관없이 계산하고, 대부분의 통계는 따로 필터 인자를 받습니다[6].

Zeek 는 `zeek -C -r 파일` 로 캡처 파일을 처리하고, `-C` 를 주면 체크섬 오프로딩(checksum offloading) 때문에 생기는 TCP 체크섬 오류를 무시합니다[9]. Zeek 는 명령을 실행한 폴더에 conn.log·dns.log 같은 로그를 만듭니다[9]. 같은 캡처를 TSV 출력과 JSON 출력으로 두 번 처리하면 같은 DNS 연결의 `uid` 가 `CazOhH2qDUiJTWMCY` 와 `CMdzit1AMNsmfAIiQc` 로 다르게 나오듯이, 다시 처리하면 `uid` 가 바뀔 수 있습니다[9]. 보고서에 `uid` 를 쓸 때는 어느 처리 결과에서 나온 값인지 함께 적습니다. 로그 필드와 시각은 [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md)에 있습니다.

Suricata 는 `suricata -r 경로 -l 로그폴더` 로 캡처 파일을 처리합니다[11]. 경로가 폴더면 그 안의 파일을 **수정 시각(mtime) 순서**로 처리하고, 파일 사이에 흐름 상태를 이어 갑니다[11]. 복사 방법에 따라 수정 시각이 복사한 시각으로 바뀌면 처리 순서가 캡처 순서와 달라질 수 있으므로, 넣기 전에 수정 시각 순서와 capinfos 의 첫 패킷 시각 순서가 같은지 확인합니다. `--pcap-file-recursive` 는 하위 폴더를 최대 깊이 255 까지 따라가고 심볼릭 링크는 무시하며, `--pcap-file-continuous` 와 함께 쓸 수 없습니다[10][11]. 체크섬 검사는 `checksum-checks` 설정(기본 `auto`, 통계로 오프로딩을 추정) 또는 `-k` 옵션으로 정합니다[10][11]. 결과 필드는 [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md)에 있습니다.

Suricata 에는 처리한 캡처 파일을 지우는 설정이 있습니다. `pcap-file.delete-when-done` 은 기본값 `false`(지우지 않음)이고, `true` 면 항상, `"non-alerts"` 면 경보가 없던 파일만 지웁니다[10]. 명령줄의 `--pcap-file-delete` 는 이 설정을 무시하고 항상 지웁니다[10][11]. 증거 원본이 든 폴더를 `-r` 에 직접 주지 않고, 사본 폴더를 넣습니다.

Security Onion 의 `so-import-pcap` 은 Suricata 경보와 Zeek 메타데이터를 원래 패킷 시각 그대로 저장합니다[12]. 가져온 캡처 파일의 MD5 로 `/nsm/import/` 아래에 폴더를 만들고, 같은 파일을 다시 넣으면 이미 가져왔다고 알리며 처리하지 않습니다[12]. 다시 처리하려면 그 폴더를 지운 뒤 넣습니다[12]. 여러 파일을 한 번에 넣으면 마지막 파일의 링크만 주고, heavy node 에서는 지원하지 않습니다[12].

### 8. 넘기기 전에 파일 안의 부가 정보를 확인한다

pcapng 파일에는 패킷 말고도 이름 해석 결과, 복호화 비밀, 캡처한 PC 의 프로세스 정보가 들어 있을 수 있습니다. capinfos `-D` 는 복호화 비밀(Decryption Secrets) 개수를, `-n` 은 이름 해석된 IPv4·IPv6 주소 개수를 보여 줍니다[5]. 다른 기관이나 외부에 사본을 넘길 때 이런 정보가 필요 없으면 editcap 으로 지운 사본을 따로 만듭니다.

| 옵션 | 지우는 것 |
|---|---|
| `--discard-all-secrets` | 복호화 비밀 블록(DSB)[1] |
| `--discard-name-resolution` | 이름 해석 블록(NRB), 즉 캡처 때 넣은 호스트 이름과 IP 주소 짝[1] |
| `--discard-process-info` | 캡처한 PC 의 프로세스 정보 블록과 이를 가리키는 패킷 옵션. 프로세스 이름·실행 경로·명령줄·사용자가 들어 있을 수 있습니다[1] |
| `--discard-capture-comment` / `--discard-packet-comments` | 캡처 주석 / 패킷 주석[1] |

쓰는 editcap 에 `--discard-process-info` 가 있는지는 `editcap -h` 로 확인합니다. 지운 사본은 원본과 다른 파일이므로 해시와 지운 항목을 기록합니다.

## 도구

| 도구 | 하는 일 | 출력 형식 | 조심할 점 |
|---|---|---|---|
| capinfos | 파일 정보·시각 범위·해시 출력 | 텍스트(긴 형식 또는 표) | 오류가 나도 다음 파일로 계속합니다[5] |
| editcap | 자르기·나누기·중복 제거·시각 변경·부가 정보 제거 | 기본 pcapng, `-F` 로 지정[1] | 나눈 파일 이름의 일시는 분석 PC 현지 시각입니다[2] |
| mergecap | 여러 파일 합치기 | 기본 pcapng, `-F` 로 지정[3] | 입력마다 시간순이라고 가정합니다[3] |
| reordercap | 시각 순서로 다시 쓰기 | 입력과 같은 형식[4] | |
| tshark | 표시 필터로 뽑기, 통계 | 기본 pcapng, `-F` 로 지정[6] | `-z` 통계는 `-Y` 를 따르지 않습니다[6] |
| tcpdump | 캡처 필터 식으로 뽑기, 개수 세기(`--count`) | pcap[7] | 여러 파일은 `-V 목록파일` 로 읽습니다[7] |

editcap·mergecap·capinfos·reordercap 은 확장자가 없어도 파일 형식과 gzip·zstd·lz4 압축을 알아서 판별합니다[1][3][4][5]. 그래서 압축을 풀지 않은 채로 해시를 확인하고 바로 작업할 수 있습니다. editcap·mergecap 은 `--compress` 나 출력 파일 확장자(.gz 등)로 결과를 압축해 쓸 수도 있습니다[1][3].

## 함정과 한계

- **형식이 바뀌면 정보가 빠질 수 있습니다.** 다른 형식으로 저장하면 주석, 이름 해석, 시각 해상도 같은 정보를 잃을 수 있습니다[8]. 나노초 해상도 pcapng 를 `-F pcap` 으로 쓰기 전에 꼭 필요한지 확인합니다.
- **시간대를 빠뜨린 `-A`·`-B` 는 분석 PC 의 시간대로 해석합니다.**[1] 같은 명령도 분석 PC 가 바뀌면 다른 구간을 잘라 냅니다.
- **파일 이름의 일시는 패킷 시각의 UTC 가 아닙니다.** editcap 이 나눈 파일은 분석 PC 현지 시각[2], dumpcap 순환 파일은 캡처 호스트 현지 시각입니다([패킷 캡처하기](packet-capture.md)). 시각 해석은 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)을 따릅니다.
- **시간순 가정.** mergecap 과 editcap `-w` 는 패킷이 시간순이라고 가정합니다[1][3]. `capinfos -o` 로 먼저 확인합니다.
- **시각을 바꾸는 옵션.** editcap `-t` 는 모든 패킷을 옮기고, `-S` 는 앞 패킷보다 이른 패킷의 시각을 앞 패킷 시각에 지정한 값을 더한 시각으로 바꾸며(음수면 모든 패킷), `-R 번호:시각` 은 한 프레임의 시각을 바꿉니다[1]. 이 옵션을 쓴 파일의 시각은 원래 기록이 아니므로 쓴 값과 이유를 기록합니다.
- **`-T` 는 링크 유형 값만 바꿉니다.** editcap `-T` 는 출력 파일의 링크 유형 값만 바꾸고 패킷 헤더를 변환하지 않습니다[1].
- **`-E` 는 증거 사본에 쓰지 않습니다.** 출력 바이트를 무작위로 바꾸는 퍼징(fuzzing) 시험용 옵션입니다[1].
- **Suricata 의 삭제 옵션과 처리 순서.** `--pcap-file-delete` 와 `delete-when-done` 은 입력 파일을 지우고, 폴더 입력은 수정 시각 순서로 처리합니다[10][11].
- **Zeek `uid` 는 다시 처리하면 바뀔 수 있습니다.**[9]

## 결과를 어떻게 해석하나

잘라 내거나 합치거나 중복을 지우거나 시각을 옮긴 파일은 원본이 아닌 파생 파일입니다. 해시가 원본과 다르므로, 파생 파일에서 찾은 사실은 "원본 파일(SHA-256 값)에서 어떤 명령으로 만든 파일"이라는 연결을 작업 기록으로 보여 줄 수 있어야 합니다. `capinfos -H` 로 원본 해시가 처음 기록한 값과 같다는 것을 보이면 원본이 그대로라는 것까지는 증명됩니다[5].

파생 파일 자체에는 가공 흔적이 남지 않을 수 있습니다. editcap 은 출력 파일의 섹션 헤더 블록에 응용 프로그램 이름이 없을 때만 자기 이름과 버전을 넣고, 이미 있으면(예: dumpcap) 원래 값을 그대로 둡니다[2]. mergecap 의 병합 주석은 끌 수 있고 길면 빠집니다[3]. 그래서 파일 안의 응용 프로그램 이름이나 주석만 보고 가공 여부를 판단하지 않고, 작업 기록으로 확인합니다.

나눈 파일 중 빈 파일이나 패킷이 적은 구간은 그 시간에 캡처 파일에 남은 패킷이 없다는 뜻일 뿐, 네트워크에 통신이 없었다는 뜻은 아닙니다. 캡처가 멈췄거나 캡처 필터로 걸러졌을 수 있으므로 [조사 절차](investigation-process.md)와 [캡처 필터와 잘린 패킷](../../01-foundations/capture/capture-filters.md)에서 수집 범위를 함께 확인합니다. 중복 제거 뒤의 패킷 수·바이트 수는 원본과 다르므로 보고서에는 두 값을 모두 적고, 흐름 기록과 비교할 때는 어느 값을 썼는지 밝힙니다. 시간순으로 합친 여러 파일은 [네트워크 타임라인](../analysis/timeline.md)의 재료가 됩니다.

보고서에는 가공 과정을 다음처럼 씁니다(만든 예시).

> 원본 sensor1_20260302.pcap(SHA-256 `…`)과 sensor2_20260302.pcap(SHA-256 `…`)의 사본을 reordercap 으로 시간순 정렬한 뒤 mergecap 으로 합쳤고, editcap `-D 101 -I 26` 으로 중복 패킷 1,204개를 지웠다. sensor2 의 패킷 시각에는 두 센서가 함께 잡은 패킷 12개의 시각 차를 근거로 3.5초를 더했다. 이 파일에서 2026-03-02 00:00:00Z 부터 01:00:00Z 전까지 10.0.5.23 과 203.0.113.40 사이에 TCP 443 연결 3개가 확인된다.

## 참고 문헌

1. Wireshark, editcap(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
2. Wireshark, editcap.c 소스 코드. https://github.com/wireshark/wireshark/blob/master/editcap.c
3. Wireshark, mergecap(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/mergecap.adoc
4. Wireshark, reordercap(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/reordercap.adoc
5. Wireshark, capinfos(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/capinfos.adoc
6. Wireshark, tshark(1) 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
7. The Tcpdump Group, tcpdump(1) 매뉴얼. https://github.com/the-tcpdump-group/tcpdump/blob/master/tcpdump.1.in
8. Wireshark User's Guide, "File Input, Output, And Printing". https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_io.adoc
9. Zeek Documentation, "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
10. Suricata User Guide, "PCAP File Reading". https://github.com/OISF/suricata/blob/main/doc/userguide/capture-hardware/pcap-file.rst
11. Suricata User Guide, 명령줄 옵션. https://github.com/OISF/suricata/blob/main/doc/userguide/partials/options.rst
12. Security Onion Documentation, "so-import-pcap". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/so-import-pcap.rst
