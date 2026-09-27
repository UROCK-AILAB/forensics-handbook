---
title: "네트워크 포렌식 보고서"
parent: "기법 · 보고"
nav_order: 440
---

# 네트워크 포렌식 보고서 (Forensic Report)

네트워크 포렌식 보고서는 캡처 파일과 로그에서 확인한 사실을, 분석에 참여하지 않은 사람도 같은 과정을 다시 따라가 볼 수 있게 정리한 문서입니다. 네트워크 기록은 처음부터 빠진 부분이 있고 도구마다 시각을 적는 방식이 달라서, 무엇을 받았는지, 무엇이 빠졌는지, 어떤 시각 기준으로 읽었는지를 먼저 밝혀야 결론을 믿을 수 있습니다. 이 페이지에서는 보고서에 넣을 항목과 순서, 캡처 파일 정보와 손실 통계를 옮기는 방법, 기록으로 확인되는 만큼만 쓰는 문장을 다룹니다.

## 언제 쓰나

포렌식 과정은 수집(collection), 검사(examination), 분석(analysis), 보고(reporting)의 네 단계로 나누고, 보고는 분석 결과를 정리해 전하는 마지막 단계입니다[2]. 그렇다고 분석이 끝난 뒤에 처음 쓰기 시작하는 문서는 아닙니다. 보고서는 감정인이 모아 둔 사진, 그림, 사건 노트, 도구가 만든 결과물을 바탕으로 씁니다[1]. 노트에는 날짜와 시각을 적고, 노트와 출력물에는 서명과 날짜를 남깁니다[3]. 증거와 도구와 방법은 모두 법정에서 다툼의 대상이 될 수 있어서, 기술 기록은 관련 지식과 기술이 있는 다른 검토자가 무엇을 했는지 평가하고 데이터를 해석할 수 있을 만큼 자세해야 합니다[1].

읽는 사람에 따라 필요한 깊이가 다릅니다. 수사기관이 관여하는 사건은 수집한 정보를 모두 자세히 적고 증거 데이터 사본까지 요구할 수 있습니다. 시스템 관리자는 트래픽과 통계를 자세히 보고 싶어 하고, 경영진은 무슨 일이 있었는지와 같은 일을 막으려면 무엇을 할지를 간단한 그림과 함께 보고 싶어 합니다[2]. 어느 경우든 결과는 비전문가가 읽어도 뜻이 하나로 읽히게 쓰고, 어떤 과정을 거쳤는지 개요를 함께 적습니다[1].

분석 도구에 딸린 보고서 기능은 그 도구가 한 일만 적고 감정 전체 범위를 적지 않습니다. 그래서 도구 보고서는 감정 보고서의 보조 문서나 부록으로 붙입니다[1]. 수집 단계의 절차는 [조사 절차](../acquisition/investigation-process.md)와 [로그 수집과 보존](../acquisition/log-collection.md)에 있고, 같은 사건의 호스트·클라우드 쪽 보고서는 [Windows](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/reporting/forensic-report.html), [Linux](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/reporting/forensic-report.html), [클라우드](https://urock-ailab.github.io/forensics-handbook/cloud/03-techniques/reporting/forensic-report.html) 핸드북의 보고서 페이지를 따릅니다.

## 절차

아래 순서는 디지털·멀티미디어 증거 감정 보고서의 최소 항목[1]에 네트워크 기록에서 따로 밝혀야 할 것(수집 범위·손실·시각 기준·파생 파일)을 더한 것입니다. 최소 항목에는 들어갈 내용만 있고 레이아웃은 없어서, 형식은 감정인이 정하거나 기관 정책이나 법원 규칙을 따릅니다[1].

### 1. 보고서 머리와 의뢰 내용을 적는다

머리에는 "감정 보고서", "수정 보고서" 같은 제목, 감정 기관의 이름과 주소, 사건 식별자, 페이지 번호와 전체 페이지 수, 보고서 날짜(최종 서명본 날짜)를 적습니다[1]. 일반인이 흔히 쓰지 않는 약어는 처음 나올 때 풀어 씁니다[1]. 네트워크 보고서에는 pcap·IDS·NAT 같은 약어가 많아서 이 항목을 빠뜨리기 쉽습니다.

이어서 의뢰 날짜, 의뢰자 이름과 소속, 의뢰 내용과 목적과 범위, 그리고 의뢰의 권한 근거(동의·영장·계약 등)를 적습니다[1]. 네트워크 조사에서는 "어느 구간의 트래픽을, 어느 기간에 대해" 보라는 요청인지가 범위가 됩니다. 공격자의 신원까지 밝혀야 하는지도 조사 초기에 정해야 할 일입니다. 신원 확인은 시간이 많이 들고 어려워서, 필요한지 여부를 처음에 적절한 사람들이 정합니다[2].

### 2. 받은 증거를 목록으로 만들고 해시를 남긴다

제출받거나 수집한 항목마다 받은 날짜, 전달·수집 방법, 제출자, 그리고 항목을 하나씩 구분할 정보(모델·일련번호·표시·해시값 등)를 목록으로 적습니다. 감정하지 않은 항목도 목록에 넣습니다[1]. 로그가 증거로 쓰일 수 있으면 원본 로그 파일, 중앙 수집 서버에 모인 로그, 해석된 로그 데이터의 사본을 모두 받아 두면 복사·해석 과정의 충실도를 나중에 따질 수 있습니다[2].

캡처 파일은 capinfos 로 해시와 기본 정보를 한 번에 뽑아 목록에 붙입니다. capinfos 는 확장자와 상관없이 파일 형식과 gzip·zstd·lz4 압축을 알아서 판별하고, 옵션 없이 실행하면 모든 정보를 사람이 읽는 "long" 형식으로 냅니다[4]. `-T` 를 주면 스프레드시트나 DB 로 옮기기 좋은 표 형식이 되고, `-m -Q` 를 더하면 쉼표로 나누고 큰따옴표로 감싼 CSV 가 됩니다[4]. 개별 정보 옵션을 하나라도 주면 모든 정보를 내는 기본 동작이 꺼지고 고른 항목만 나옵니다[4].

```
capinfos -T -m -Q -t -E -c -s -a -e -u -o -l -H evidence01.pcapng evidence02.pcapng > evidence_list.csv
```
(만든 예시: 파일 이름은 지어낸 값입니다.)

| 옵션 | 보고서에 옮기는 값 | 주의할 점 |
|---|---|---|
| `-H` | 파일의 SHA256 과 SHA1 | SHA1 출력은 나중 버전에서 빠질 수 있습니다[4] |
| `-a` / `-e` | 가장 이른 / 가장 늦은 패킷 시각 | 패킷 순서가 뒤섞인 파일이면 첫 패킷·마지막 패킷과 다를 수 있습니다[4] |
| `-S` | 위 두 시각을 1970-01-01 이후 초(epoch)로 | editcap `-t` 로 시각을 맞출 때 씁니다[4] |
| `-u` | 캡처 기간(초) | 가장 이른 패킷과 가장 늦은 패킷의 시각 차입니다[4] |
| `-o` | 시간순 정렬 여부(True/False) | 하나라도 순서가 어긋나면 False 입니다[4] |
| `-c` / `-s` / `-d` | 패킷 수 / 파일 크기 / 원래 길이 기준 전체 바이트 | `-d` 는 잘려서 저장된 패킷도 원래 길이로 셉니다[4] |
| `-l` | 스냅 길이(snaplen) | 파일 헤더와 잘린 레코드로 판단합니다[4] |
| `-E` / `-t` | 링크 유형 / 캡처 파일 형식 | |
| `-k` / `-p` | 캡처 주석 / 패킷별 주석 | pcapng 의 캡처 주석은 섹션 헤더 블록의 주석입니다[4] |
| `-D` | 복호화 비밀(Decryption Secrets) 개수 | 표 형식에서는 나오지 않습니다(`-I` 인터페이스 정보도 같음)[4] |

해시는 보고서의 주 해시로 SHA-256 을 적고, SHA-1·MD5 는 다른 도구가 낸 값과 맞춰 볼 때만 함께 적습니다. Security Onion 의 Cases 기능은 첨부 파일마다 SHA256·SHA1·MD5 를 자동으로 만들어 줍니다[22]. NIST SP 800-86(2006)은 MD5 와 SHA-1 을 가장 흔한 두 알고리즘으로 들고 연방기관에 SHA-1 을 권합니다. 하지만 같은 문서 각주에서 NIST 는 2010년까지 SHA-224·SHA-256 같은 더 강한 알고리즘으로 옮길 계획을 세우라고 했으므로, SHA-1 권고는 지금 그대로 따를 내용이 아닙니다[2]. 해시값은 읽기 전용이나 한 번만 쓸 수 있는 매체에 저장하거나 인쇄해서 안전한 곳에 보관합니다[2].

pcap·pcapng 파일의 구조와 주석 블록은 [pcapng 형식](../../01-foundations/capture/pcapng.md)에, 큰 파일을 나누고 합치는 방법은 [큰 캡처 파일 다루기](../acquisition/large-captures.md)에 있습니다.

### 3. 수집 범위와 빠진 데이터를 밝힌다

네트워크 트래픽 데이터는 대부분의 경우 일부가 기록되지 않은 채 사라집니다. 그래서 분석은 남은 데이터와, 빠진 데이터에 대한 기술적 근거가 있는 가정을 함께 써서 결론을 만드는 과정입니다[2]. 보고서에는 이 가정의 바탕이 되는 수집 범위를 먼저 적습니다. 센서가 어디에 붙어 있었는지([어디서 캡처하나](../../01-foundations/capture/capture-points.md)), 어떤 캡처 필터를 썼는지([캡처 필터와 잘린 패킷](../../01-foundations/capture/capture-filters.md)), 그리고 도구가 스스로 남긴 손실 통계가 여기에 들어갑니다.

| 기록 | 보고서에 옮길 값 | 읽는 법 |
|---|---|---|
| Zeek `capture_loss.log` | `ts`, `ts_delta`, `peer`, `gaps`, `acks`, `percent_lost` | TCP 순서 번호에서 빈틈(gap)을 찾아 손실로 봅니다. `percent_lost` 가 `0.4123` 이면 0.41% 이지 41% 가 아닙니다[11] |
| Zeek `reporter.log` | `ts`, `level`, `message`, `location` | `received termination signal` 은 Zeek 가 종료 신호를 받은 시각, `BPFConf filename set: …` 은 Zeek 가 BPF 필터 설정 파일을 지정했다는 메시지입니다[11] |
| Zeek `conn.log` | `missed_bytes` | 내용 빈틈으로 놓친 바이트 수로 패킷 손실을 나타냅니다. 0 이 아니면 프로토콜 분석이 보통 실패하지만, 손실 전까지는 일부 분석이 됐을 수 있습니다[10] |
| Suricata `stats.log` | `capture.kernel_packets`, `capture.kernel_drops` | 캡처 모드마다 뜻이 다릅니다. AF_PACKET 에서 `kernel_packets` 는 사용자 공간으로 넘긴 패킷 수이고, PF_RING 에서는 본 패킷 전체 수입니다[14]. `kernel_drops` 는 `kernel_packets` 의 1% 미만이 바람직하고, 높으면 이벤트와 경보가 줄어들 수 있습니다[15] |
| Suricata `stats.log` | `tcp.reassembly_gap` | TCP 스트림에서 빠진 데이터 수입니다. 0 이 이상적이고, 패킷 손실 말고도 잘못된 체크섬이나 스트림 엔진 메모리 부족으로 늘어납니다[14] |
| nfcapd 설정·흐름 레코드 | 샘플링 여부와 비율 | 아래 문단 참고 |

흐름 기록으로 "보낸 양" 을 적을 때는 샘플링을 함께 적습니다. nfcapd 의 `-s` 기본값은 1(샘플링 없음)이고, 양수는 장비가 샘플링 정보를 보내지 않을 때만 쓰며, 음수는 장비가 보낸 정보를 무시하고 모든 레코드에 강제합니다[16]. 샘플링 비율은 레코드의 패킷·바이트 수에 곱해지지만 흐름 수에는 곱하지 않고, 샘플링을 설정해도 샘플링 정보를 내보내지 않는 장비가 있습니다[17]. 그래서 샘플링된 흐름의 패킷·바이트 수는 SNMP 같은 다른 출처의 수치와 다를 수 있습니다[16]. 흐름 기록 형식은 [흐름 기록](../../01-foundations/records/flow-records.md)에 있습니다.

통계로 드러나지 않는 사각도 적습니다. 보안 장비가 연결의 모든 패킷을 처리하지 못하는 이유로는 장비 장애, 과부하, 그리고 들어오는 패킷과 나가는 패킷이 다른 경로를 타는 비대칭 라우팅이 있습니다. 비대칭 라우팅에서 한 경로만 감시하면 연결의 일부만 보입니다[2].

### 4. 시각 기준을 하나로 맞춘다

보고서의 모든 시각에는 UTC 인지 현지 시각인지를 표시하고, 각 시스템 시계가 UTC 와 얼마나 차이 났는지, 시계가 얼마나 어긋나 있었는지(clock drift)를 적습니다[3]. 여러 출처의 사건을 맞춰 볼 때는 시계가 동기화돼 있어야 쉽고 정확합니다[2]. 보고서 본문은 UTC 로 통일하고, 현지 시각이 필요한 곳에는 오프셋을 붙여 함께 적는 방법이 가장 덜 헷갈립니다.

도구마다 기본 표기가 달라서 출력물을 그대로 복사하면 기준이 섞입니다. 각 기록의 시각이 언제 찍히는지는 [네트워크 기록의 시각](../../01-foundations/records/timestamps.md)에 있고, 보고서에 옮길 때 확인할 것은 아래와 같습니다.

| 출처 | 기본 표기 | 보고서에 옮길 때 |
|---|---|---|
| tshark·Wireshark `-t` | 기본은 첫 패킷부터 지난 시간(relative)입니다[7] | `-t ud`(UTC, 날짜 포함, `Z` 접미사)나 `-t e`(epoch)처럼 기준이 분명한 형식으로 뽑습니다. `a`·`ad` 는 분석 PC 의 현지 시간대입니다[7] |
| Zeek 로그 `ts` | epoch 초(예: `1591367999.306059`)입니다[9] | `zeek-cut -d` 는 `%Y-%m-%dT%H:%M:%S%z` 형식으로 바꾸고, UTC 로 바꾸는 옵션은 `-u` 로 따로 있습니다. 형식은 `-D`·`-U` 로 바꿉니다[9]. 오프셋(`%z`)을 남기거나 `-u` 를 씁니다 |
| Zeek TSV 헤더 `#open`·`#close` | `2020-06-05-14-48-32` 형식입니다[9] | 로그 파일을 연·닫은 시각이라 패킷 시각이 아닙니다. 저장된 pcap 을 나중에 읽으면 패킷 `ts` 는 14:39:59 인데 `#open` 은 14:48:32 처럼 달라집니다[9] |
| Suricata EVE `timestamp` | ISO 8601 에 시간대 오프셋이 붙습니다(예: `2017-04-07T22:24:37.251547+0100`)[12] | 오프셋까지 옮기고 UTC 로 바꾼 값을 함께 적습니다 |
| Security Onion Alerts·Dashboards | 브라우저에서 현지 시간대를 감지해 표시하고, 직접 지정할 수도 있습니다[20][21] | 화면 캡처를 넣을 때 표시 시간대를 적습니다. Cases 도 Options 에서 시간대를 정합니다[22] |
| editcap `-A`·`-B` | ISO 8601 에서 오프셋을 빼면 현지 시각으로 봅니다. epoch 는 UTC 기준입니다[5] | 잘라 낸 구간을 적을 때 `Z` 나 `±hh:mm` 을 붙인 값으로 적습니다. `-A` 는 그 시각 이상, `-B` 는 그 시각 미만입니다[5] |

한 로그 안에서도 줄 순서가 시간순이 아닐 수 있습니다. 예를 들어 Zeek dns.log 에서 `1591367999.306059` 줄이 `1591367999.305988` 줄보다 먼저 나올 수 있습니다[9]. 보고서의 표는 `ts` 로 다시 정렬해서 만듭니다. Suricata EVE 의 이상(anomaly) 이벤트에는 `1969-12-31T16:04:21.000000-0800`(epoch 261초)처럼 실제 시각일 수 없는 값이 찍힐 수 있습니다[12].

장비 사이의 시계 차이를 알고 있어서 editcap `-t` 로 패킷 시각을 옮긴 파일을 만들었다면(`-t 3600` 은 1시간 앞으로, `-t -0.5` 는 0.5초 뒤로[5]), 옮긴 양과 그 근거, 원본 파일 해시와 보정한 파일 해시를 모두 적습니다. 보정은 사본에만 합니다. 여러 출처를 하나의 시간순 목록으로 합치는 방법은 [네트워크 타임라인](../analysis/timeline.md)에 있습니다.

### 5. 발견 사항은 기록으로 확인되는 만큼 쓴다

발견 사항 문장은 사람의 행동이 아니라 기록된 사실로 씁니다.

- 기록보다 앞서 나간 문장: "직원 A 가 설계 파일을 외부로 유출했다."
- 기록만큼 쓴 문장: "2026-03-02 01:10:05Z 부터 01:52:40Z(UTC)까지 내부 주소 10.0.5.23 에서 203.0.113.50 의 443번 포트로 나간 TCP 연결이 3건 기록돼 있고, Zeek conn.log 의 `orig_bytes` 합계는 1,204,331,008 바이트입니다. 같은 시각 DHCP 로그에서 10.0.5.23 은 MAC 주소 00:00:5e:00:53:01 인 기기에 할당돼 있었습니다." (만든 예시)

기록만큼 쓴 문장에는 시각 기준, 출처 로그, 수치를 뽑은 필드가 모두 들어 있어서 다른 분석가가 같은 값을 다시 뽑아 볼 수 있습니다. IP 주소는 동적으로 할당되고, NAT 장비가 주소를 바꾸고, 위조되거나 익명화 서버를 거칠 수 있어서, 그 시각 그 주소를 쓴 기기까지만 좁힐 수 있습니다[2]. 주소를 기기와 사람으로 좁혀 가는 과정은 [IP 주소·포트·NAT 해석](../../01-foundations/records/ip-nat.md)과 [이 시각에 이 IP 를 누가 썼나](../../04-scenarios/user-activity/ip-attribution.md)에 있습니다. DHCP 기록도 MAC·IP 위조 가능성이 있다는 점은 [DHCP 로그](../../02-artifacts/devices/dhcp-logs.md)에 있습니다.

IDS·SEM(보안 이벤트 관리) 경보는 원본 데이터를 해석한 결과라서, 원시 패킷 같은 다른 데이터로 확인하기 전에는 사실로 적지 않습니다. 원본 데이터 출처를 정규화(수정)된 데이터를 받는 출처보다 더 믿습니다[2]. 반대로 보안 장비가 악성으로 보고하지 않았다고 해서 그 활동이 무해하다고 쓰지 않습니다[2]. 탐지 규칙 결과를 읽는 법은 [탐지 규칙 활용](../analysis/detection-rules.md)에 있습니다.

### 6. 다른 설명을 함께 다룬다

정보가 불완전하면 무슨 일이 있었는지 하나로 확정하지 못할 수 있습니다. 그럴듯한 설명이 둘 이상이면 각각을 보고서에서 다루고, 각 설명을 증명하거나 반증하려고 체계적으로 확인합니다[2]. 예를 들어 이상한 연결 시도는 공격자, 악성 코드, 잘못 설정한 소프트웨어, 사람의 입력 실수 가운데 어느 것에서도 생길 수 있습니다[2]. 보고서에는 설명마다 확인한 기록과 그 결과(맞음·틀림·판단할 기록 없음)를 적습니다. 의도는 기록만으로 판단하기 매우 어려워서 결론에 넣을 때는 근거를 따로 적습니다[1][2].

의견이나 결론을 넣는다면 그 근거를 함께 적습니다[1]. 조사 중에 새 정보원을 찾게 해 준 단서(연락처 목록 같은 것)나 앞으로의 피해를 막을 정보(백도어, 예정된 웜 확산, 악용될 수 있는 취약점)도 보고서에 넣습니다[2]. 정책 결함이나 절차 오류처럼 고칠 문제, 그리고 다음 조사에 필요한 데이터를 더 남기려면 감사·로깅·IDS 설정을 어떻게 바꿀지도 적습니다[2].

### 7. 파생 파일과 부록을 정리한다

분석하면서 만든 파일은 모두 원본이 아닌 파생물(derivative works)입니다. 파생 파일마다 만든 도구와 명령, 입력 파일과 그 해시, 결과 파일의 해시를 적고, 보고서 수치가 어느 파일을 기준으로 나왔는지 밝힙니다.

- mergecap 은 기본으로 프레임 시각 순서로 합치고 입력 파일이 이미 시간순이라고 가정합니다. `-a` 를 주면 시각을 무시하고 파일 순서대로 이어 붙입니다. 출력 기본 형식은 pcapng 입니다[6]. 합치기 전에 capinfos `-o` 로 각 파일이 시간순인지 확인합니다[4].
- editcap `-d` 는 길이와 MD5 가 직전 4개 패킷과 같은 패킷을 건너뛰어 중복을 지웁니다(`-D 5` 와 같음)[5]. 결과 파일의 패킷 수는 원본과 다릅니다.
- editcap `-a` 는 프레임에 주석을 달고, `--capture-comment` 는 파일 주석을 기존 주석 뒤에 붙입니다. Wireshark 는 파일의 첫 주석만 보여 줍니다[5]. 주석을 달면 파일 내용이 바뀌어 해시가 달라지므로 사본에만 답니다.
- Wireshark 의 "Export Specified Packets" 는 고른 패킷만 새 파일로 저장합니다. 패킷 범위 기본값은 Displayed 라서 현재 표시 필터에 맞는 패킷만 저장되고, 전체를 저장하려면 Captured 를 고릅니다[8]. 부록 파일을 이렇게 만들었다면 표시 필터 식을 함께 적습니다.
- "Export Packet Dissections" 는 패킷 목록·상세·바이트를 평문, CSV, JSON 등으로 저장해서 부록 표를 만들 때 씁니다[8].

부록의 흐름 표에는 Community ID 를 함께 적으면 다른 도구나 다른 분석가가 같은 흐름을 찾기 쉽습니다. Community ID 는 출발·도착 주소와 포트, 프로토콜, 시드(seed, 기본 0)를 SHA1 로 해시해 base64 로 적고 앞에 `1:` 을 붙인 값이고, 작은 쪽 IP:port 가 먼저 오게 정렬해서 방향과 상관없이 같은 값이 나옵니다[19]. Suricata 는 `community-id: true` 로 `community_id` 필드를 더하고, `community-id-seed` 는 이 값을 내는 모든 도구에서 같아야 합니다[13]. Suricata 이벤트끼리는 `flow_id` 로 같은 흐름의 alert·fileinfo·http·anomaly·flow 이벤트를 묶을 수 있습니다[12]. 같은 5-튜플을 다른 시각에 다시 쓴 흐름도 같은 Community ID 를 받으므로 표에는 흐름 시각을 함께 적습니다[19].

부록 파일을 넘기기 전에는 안에 든 정보를 확인합니다. pcapng 에 editcap `--inject-secrets` 로 넣은 복호화 비밀 블록(DSB)이 있으면 받는 사람도 암호화된 내용을 풀어 볼 수 있습니다[5]. capinfos `-D` 로 개수를 확인하고, 들어 있으면 보고서에 적습니다[4]. 키 로그 형식은 [암호화된 트래픽 분석](../analysis/encrypted-traffic.md)에 있습니다. 조사 목적과 관계없는 정보가 원래 볼 권한이 없는 사람에게 넘어가지 않게 하고, 로그만으로도 사용자의 행동 패턴이 드러날 수 있다는 점을 고려합니다[3]. 외부와 나누려고 nfanon 으로 흐름 파일의 IP 주소를 접두사 보존 익명화(CryptoPAn)할 때, `-w` 로 출력 파일을 주지 않으면 원본 파일을 덮어씁니다[18]. 반드시 사본에 돌리고 출력 파일을 따로 지정합니다.

### 8. 처분·승인·보관 기록을 남기고, 고칠 일이 생기면 새 보고서를 낸다

보고서에는 원본과 파생물을 어떻게 처분했는지(폐기·반환·보관)와 보고서 승인자의 이름과 서명(자필·디지털·전자 서명)을 넣습니다[1]. 증거 관리 연속성(chain of custody)에는 어디서·언제·누가 증거를 발견하고 수집했는지, 누가 다루고 검사했는지, 어느 기간 누가 어떻게 보관했는지, 보관자가 바뀔 때 언제 어떻게 넘겼는지(운송 번호 포함)를 적습니다[3].

최종본을 낸 뒤 고칠 일이 생기면 원래 보고서를 고치지 않고 새 보고서를 냅니다. 새 보고서에는 고친 곳을 표시해 설명하고 원래 보고서를 참조합니다[1].

## 도구

| 도구 | 보고서에서 쓰는 곳 |
|---|---|
| capinfos | 증거 목록의 해시·패킷 수·시각 범위·시간순 여부·복호화 비밀 개수[4] |
| editcap | 시각 범위로 잘라 내기(`-A`·`-B`), 시각 보정(`-t`), 중복 제거(`-d`), 주석, 복호화 비밀 넣고 꺼내기[5] |
| mergecap | 여러 캡처를 시간순으로 합치기[6] |
| tshark·Wireshark | 기준이 분명한 시각 형식으로 뽑기(`-t ud`), 부록용 패킷·해석 결과 내보내기[7][8] |
| zeek-cut | Zeek TSV 로그에서 필드를 뽑고 epoch 를 읽을 수 있는 시각으로 바꾸기[9] |
| jq | EVE JSON 에서 같은 `flow_id` 이벤트 모으기, 예: `jq 'select(.flow_id==1234567890123456)' eve.json` (만든 예시 값)[12] |
| nfdump·nfcapd·nfanon | 흐름 기록 집계, 샘플링 설정 확인, 외부 공유용 IP 익명화[16][17][18] |
| Security Onion Cases | 사례별 댓글·첨부(해시 자동 생성)·관찰 대상(IP·도메인·해시)·변경 이력(History)[22] |
| pycommunityid | Community ID 참조 구현. 새로 구현할 때 기준으로 씁니다[19] |

## 함정과 한계

- tshark 를 기본값으로 쓰면 첫 패킷부터 지난 상대 시각이 나옵니다. 이 값을 그대로 보고서에 옮기면 실제 시각이 아닙니다[7].
- `zeek-cut -d` 와 UTC 로 바꾸는 `-u` 는 서로 다른 옵션입니다. 출력에 붙은 `%z` 오프셋을 확인합니다[9].
- Zeek `percent_lost` 는 이미 퍼센트 값입니다. 100 을 곱하지 않습니다[11].
- Suricata `kernel_packets`·`kernel_drops` 는 캡처 모드마다 뜻이 달라서, 손실률을 적을 때 캡처 모드도 함께 적습니다[14].
- Security Onion 의 집계 화면에서 사례로 올리면(escalate) 집계된 행만 넘어가 세부 정보가 적습니다. 집계를 펼쳐 개별 항목을 올립니다[22].
- 흐름 기록의 패킷·바이트 수는 샘플링 비율을 곱한 값일 수 있고, 흐름 수에는 샘플링 비율을 곱하지 않습니다[17].
- Community ID 는 충돌할 수 있고, IP in IP 같은 중첩이나 VLAN·MPLS 캡슐화를 어떻게 처리할지 정해져 있지 않습니다. v1 은 아직 시험판(prototype)입니다[19]. 충돌한 흐름은 흐름 시각과 도구 고유 ID 로 구분합니다[19].
- Security Onion Cases 의 History 탭에는 사례에 대한 사용자별 변경 이력이 남습니다[22]. 보고서의 사례 기록은 이 이력과 맞아야 합니다.

## 결과를 어떻게 해석하나

기록이 있는 시간 범위 안에서 특정 주소와 포트 사이에 특정 흐름과 바이트 수가 기록됐다는 사실과, 해시로 확인되는 파일의 동일성까지는 증명할 수 있습니다. 기록이 있는 시간 범위는 capinfos `-a`·`-e`[4]나 로그의 `ts` 로 적습니다.

사람의 신원은 증명하지 못합니다. IP 주소는 사람이나 기기와 1:1 로 대응하지 않아서, DHCP·NAT 기록으로 좁혀도 "그 시각 그 주소를 할당받은 기기" 까지입니다[2]. 연결의 원인이 여럿일 수 있어서 기록만으로 의도를 단정하지도 못합니다[2].

기록에 없다고 해서 그 활동이 없었다고 할 수도 없습니다. 캡처 손실, 샘플링, 감시하지 않은 경로가 있고, 경보가 없었다는 사실도 무해의 증거가 아닙니다[2][11][14][17]. IDS 경보는 해석 결과라서 원시 데이터로 확인하기 전에는 사실로 쓰지 않습니다[2].

증거는 법정 규칙을 충족하고(Admissible), 사건과 확실히 연결되고(Authentic), 한쪽 관점만이 아니라 전체를 보여 주고(Complete), 수집·취급에 의심의 여지가 없고(Reliable), 법정이 믿고 이해할 수 있어야(Believable) 합니다[3]. 수집 방법은 투명하고 재현할 수 있어야 하고, 쓴 도구의 진정성과 신뢰성을 증언할 준비를 합니다[3]. 그래서 위 절차에서 해시, 손실 통계, 시각 기준, 파생 파일 기록을 빠짐없이 남깁니다.

## 참고 문헌

1. SWGDE, "SWGDE Requirements for Report Writing in Digital and Multimedia Forensics", Version 1.0, 2018-11-20. https://www.swgde.org/wp-content/uploads/2023/11/2018-11-20-SWGDE-Requirements-for-Report-Writin.pdf
2. Karen Kent, Suzanne Chevalier, Tim Grance, Hung Dang, "Guide to Integrating Forensic Techniques into Incident Response", NIST SP 800-86, 2006-08. https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-86.pdf
3. D. Brezinski, T. Killalea, "Guidelines for Evidence Collection and Archiving", RFC 3227 (BCP 55), 2002-02. https://www.rfc-editor.org/rfc/rfc3227.txt
4. Wireshark, capinfos 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/capinfos.adoc
5. Wireshark, editcap 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/editcap.adoc
6. Wireshark, mergecap 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/mergecap.adoc
7. Wireshark, 해석 옵션(tshark 매뉴얼에 포함). https://github.com/wireshark/wireshark/blob/master/doc/man_pages/dissection-options.adoc
8. Wireshark User's Guide, File Input, Output, and Printing. https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_io.adoc
9. Zeek 문서, Zeek Log Formats and Inspection. https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
10. Zeek 문서, base/protocols/conn/main.zeek. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/conn/main.zeek.rst
11. Zeek 문서, capture_loss.log and reporter.log. https://github.com/zeek/zeek-docs/blob/master/logs/capture-loss-and-reporter.rst
12. Suricata User Guide, EVE JSON Format. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
13. Suricata User Guide, EVE JSON Output. https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-output.rst
14. Suricata User Guide, Statistics. https://github.com/OISF/suricata/blob/main/doc/userguide/performance/statistics.rst
15. Suricata User Guide, Performance Analysis. https://github.com/OISF/suricata/blob/main/doc/userguide/performance/analysis.rst
16. nfdump, nfcapd 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfcapd.1
17. nfdump, README. https://github.com/phaag/nfdump/blob/master/README.md
18. nfdump, nfanon 매뉴얼. https://github.com/phaag/nfdump/blob/master/man/nfanon.1
19. Corelight, Community ID Flow Hashing 명세. https://github.com/corelight/community-id-spec/blob/master/README.md
20. Security Onion 문서, Alerts. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/alerts.rst
21. Security Onion 문서, Dashboards. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/dashboards.rst
22. Security Onion 문서, Cases. https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/cases.rst
