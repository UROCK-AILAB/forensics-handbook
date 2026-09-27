---
title: "경고와 이상 기록"
parent: "Zeek 로그"
grand_parent: "아티팩트 · Zeek"
nav_order: 200
---

# 경고와 이상 기록 (notice.log·weird.log)

Zeek 에는 평소와 다른 일을 적는 로그가 둘 있습니다. notice.log 는 스크립트가 "살펴볼 만하다" 고 판단해 올린 알림을, weird.log 는 분석기가 트래픽을 프로토콜 규칙대로 해석하지 못한 이상을 기록합니다[1]. 두 로그 모두 같은 일이 되풀이되면 줄을 줄여 쓰기 때문에, 줄 수는 실제로 일어난 횟수가 아니고 알림이 없다고 해서 그런 일이 없었다고 볼 수도 없습니다.

## 무엇을 기록하나 · 왜 생기나

알림 (notice) 은 Zeek 스크립트가 `NOTICE` 함수를 불러 `Notice::Info` 레코드 하나를 넘길 때 생깁니다[2]. 레코드마다 알림 종류(`note`)가 있고, 대개 관련 연결·호스트·파일 정보가 함께 붙습니다[2][3]. Zeek 는 스크립트가 찾은 상황을 "관심을 둘 만할 수 있다" 고만 표시하고, 실제로 대응할 일인지는 현장 설정에 맡깁니다[2]. 그래서 Zeek 에서 IDS 경고에 가장 가까운 기록이 notice.log 이지만, 한 줄 한 줄이 곧 공격 탐지는 아닙니다[1][2]. 알림은 기본 스크립트뿐 아니라 추가 패키지도 올릴 수 있습니다[1].

어떤 알림이 나오는지는 센서가 불러온 스크립트에 달려 있습니다. 배포본 `site/local.zeek` 은 인증서 검증(`protocols/ssl/validate-certs`), SSH 무차별 대입 탐지(`protocols/ssh/detect-bruteforcing`), SQL 삽입 탐지(`protocols/http/detect-sql-injection`), 취약한 소프트웨어 버전 탐지(`frameworks/software/vulnerable`), 악성 코드 해시 목록 대조(`frameworks/files/detect-MHR`) 같은 스크립트를 불러옵니다[8]. ZeekControl 은 이 파일을 기본으로 불러옵니다[6]. `zeek -r` 로 pcap 을 처리할 때 이 스크립트들을 불러오지 않으면, 같은 트래픽이라도 알림이 나오지 않을 수 있습니다.

이상 기록 (weird) 은 분석기가 트래픽을 자기 프로토콜로 해석하다가 예상하지 못한 일을 만났을 때 남습니다. 이상의 이름은 그 분석기를 만든 사람이 코드에 정해 둔 것이고, 스크립트가 올리는 경우는 드뭅니다[1]. TCP 상태 흐름에 어긋나는 패킷, 흔치 않은 HTTP 헤더 조합, RFC 범위를 벗어난 DNS 메시지 같은 것이 여기에 들어갑니다[2]. 형식이 틀린 연결, 규칙을 따르지 않는 트래픽, 고장 나거나 설정이 잘못된 장비, 센서를 헷갈리게 하려는 시도가 모두 이상 기록을 만들 수 있어서 맥락 없이는 의미를 판단하기 어렵습니다[4]. 그래서 이상 기록은 그 자체를 보안 탐지로 보지 않고, 사건을 해석할 때 덧붙는 단서로 씁니다[2].

## 위치와 버전별 차이

파일 이름은 `notice.log`·`weird.log` 이고 저장 위치, 교대(rotation) 규칙, TSV·JSON 형식은 다른 Zeek 로그와 같습니다([Zeek 로그](index.md)). 알림 동작에 `Notice::ACTION_ALARM` 이 붙은 알림은 `notice_alarm.log` 에도 한 번 더 기록되고, 메일 주소(`Notice::mail_dest`)가 설정돼 있으면 이 내용을 모아 메일로 보냅니다[2][3]. `policy/misc/weird-stats` 스크립트를 불러온 센서에는 이상 종류별 개수를 시간 구간마다 요약한 `weird_stats.log` 가 생깁니다[7].

| 버전 | 바뀐 점 |
|---|---|
| Bro 2.5.5·2.6 | 이상 기록에 표본 추출을 기본으로 적용. `Weird::sampling_*` 옵션과 `weird_stats.log` 추가[7] |
| Zeek 3.0.0 | 기본 notice.log 에서 `dropped` 필드가 빠짐[7] |
| Zeek 4.0.0 | 특정 이상 이름을 연결·흐름별이 아니라 센서 전체 기준으로 표본 추출하는 `Weird::sampling_global_list` 추가[7] |
| Zeek 7.1.0 | DNS 분석기가 처리할 수 없는 opcode 를 받으면 `DNS_unknown_opcode` 이상을 남김[7] |
| Zeek 8.0.0 | 새 `detect-sql-injection` 스크립트가 공격한 호스트를 `src`, 공격받은 호스트를 `dst` 에 쓰고 처음 표본으로 잡은 연결의 `uid` 를 넣음. 이전 `detect-sqli` 스크립트는 공격받은 호스트를 `src` 에 씀. 알림 종류 이름은 같음[7] |
| Zeek 8.1.0 | 클러스터에서 알림 억제 정보를 최대 10밀리초 동안 모아서 다른 노드에 보냄(`Notice::suppression_batch_period`·`Notice::suppression_batch_max_size`)[3][7] |

공식 문서의 2018년 notice.log 예시에는 `dropped` 와 `remote_location.*` 필드가 있지만 현재 기본 `Notice::Info` 에는 두 필드가 없습니다[2][3]. 옛 센서의 로그를 받았다면 머리의 `#fields` 줄로 어떤 필드가 있는지부터 확인합니다.

## 구조

### notice.log 한 줄의 모양

인증서 검증에 실패한 연결에 대해 `validate-certs` 스크립트가 올린 알림을 JSON 으로 쓰면 다음과 같은 모양입니다.

```json
{"ts":1772431201.577311,"uid":"CpR7tW2nXe5HsJ4qL8","id.orig_h":"192.168.1.20","id.orig_p":51602,"id.resp_h":"203.0.113.45","id.resp_p":8443,"fuid":"FhT4nQ8sVb2Kc6RzA","proto":"tcp","note":"SSL::Invalid_Server_Cert","msg":"SSL certificate validation failed with (self signed certificate)","sub":"CN=device.example.com,O=Example Devices","src":"192.168.1.20","dst":"203.0.113.45","p":8443,"actions":["Notice::ACTION_LOG"],"suppress_for":3600}
```

(만든 예시)

### notice.log 필드

`Notice::Info` 에서 로그에 쓰는 필드는 다음과 같습니다[3]. 연결 정보가 있는 알림이면 `uid`·`id` 를 채우고, 거기서 `src`(발신 주소)·`dst`(응답 주소)·`p`(응답 포트)를 자동으로 채웁니다[3]. 포트가 있으면 `proto` 도 포트에서 가져옵니다[3].

| 필드 | 뜻 | 비고 |
|---|---|---|
| `ts` | 알림이 생긴 시각 | 스크립트가 따로 정하지 않으면 알림을 올린 때의 네트워크 시각[3] |
| `uid`·`id.*` | 관련 연결의 ID 와 주소·포트 | 호스트 단위 알림에는 없음[2] |
| `fuid`·`file_mime_type`·`file_desc` | 관련 파일의 ID·MIME 유형·설명 | 파일 알림일 때 채움. `file_desc` 는 HTTP 로 받은 파일이면 요청 URL 같은 값[3] |
| `proto` | 전송 프로토콜 | 연결이나 `p` 가 있을 때 채움[3] |
| `note` | 알림 종류(예: `SSL::Invalid_Server_Cert`) | 반드시 있음[2][3] |
| `msg` | 사람이 읽는 메시지 | [2][3] |
| `sub` | 보조 메시지 | 알림 정책에서 조건으로 쓰는 값이 자주 들어감[2] |
| `src`·`dst`·`p` | 관련 주소와 포트 | 호스트 단위 알림은 `src` 만 채우기도 함[2] |
| `n` | 알림과 관련된 숫자나 상태 코드 | [2][3] |
| `peer_descr` | 알림을 올린 노드 이름 | 클러스터로 운영할 때만 자동으로 채움[3] |
| `actions` | 적용한 동작 집합 | 기본으로 `Notice::ACTION_LOG` 가 들어감[3] |
| `email_dest` | 메일을 보낸 주소 | 메일 동작이 붙었을 때[3] |
| `suppress_for` | 같은 알림을 다시 올리지 않는 기간 | 기본 1시간(3600초)[3] |

같은 알림인지 판단하는 `identifier` 필드는 레코드 안에만 있고 로그에는 쓰지 않습니다[3]. 그래서 로그만 보고는 어떤 값으로 중복을 판단했는지 알 수 없고, 알림을 올린 스크립트의 코드에서 확인해야 합니다.

### weird.log 한 줄의 모양

HTTP 요청에 알려지지 않은 메서드 `WEIRD` 가 쓰이면 TSV 로 다음과 같은 줄이 남습니다[6].

```
#fields	ts	uid	id.orig_h	id.orig_p	id.resp_h	id.resp_p	name	addl	notice	peer	source
1772431200.114502	CaB3xK9mPq2LdY7wE1	192.168.1.20	51544	203.0.113.45	8080	unknown_HTTP_method	WEIRD	F	zeek	-
```

(만든 예시)

### weird.log 필드

| 필드 | 뜻 | 비고 |
|---|---|---|
| `ts` | 이상이 생긴 시각 | 이상 이벤트가 난 때의 네트워크 시각[4] |
| `uid`·`id.*` | 관련 연결 | 연결 단위 이상일 때 채움. 연결 없이 두 주소 사이의 흐름 단위 이상이면 `uid` 가 없고 포트는 0 으로 씀. 네트워크 단위 이상에는 둘 다 없음[4] |
| `name` | 이상의 이름(예: `unknown_HTTP_method`) | 반드시 있음[4] |
| `addl` | 추가 정보 | `unknown_HTTP_method` 이면 메서드 이름[9]. 파일 단위 이상이면 파일 ID 뒤에 추가 정보를 붙임[4] |
| `notice` | 이 이상을 알림으로도 올렸는지 | 기본 `F`[4] |
| `peer` | 이상을 보고한 노드 | 단독 실행이면 `zeek`, 클러스터면 `worker` 같은 노드 이름[4][6] |
| `source` | 이상을 보고한 분석기 이름 | 분석기가 보고할 때 채움[4]. `unknown_HTTP_method` 처럼 스크립트가 올린 이상은 비어 있을 수 있음[6][9] |

이상을 알림으로 올리도록 설정된 이름은 notice.log 에 알림 종류 `Weird::Activity` 로 한 번 더 남고, 이때 `msg` 에 이상 이름, `sub` 에 추가 정보가 들어갑니다[2][4]. 이상 이름마다 기본 동작은 `Weird::actions` 표에 있고, 표에 없는 이름은 매번 기록(`ACTION_LOG`)이 기본입니다[4]. 표의 동작은 무시(`ACTION_IGNORE`), 기록(`ACTION_LOG`), 한 번만·연결마다 한 번·발신 호스트마다 한 번 기록(`ACTION_LOG_ONCE`·`ACTION_LOG_PER_CONN`·`ACTION_LOG_PER_ORIG`), 그리고 같은 방식으로 알림을 올리는 `ACTION_NOTICE` 계열로 나뉩니다[4]. 예를 들어 `unsolicited_SYN_response`·`spontaneous_FIN`·`spontaneous_RST` 는 기본으로 무시하고, `bad_IP_checksum`·`bad_TCP_checksum` 같은 체크섬 오류는 발신 호스트마다 한 번, `FIN_storm`·`SYN_after_partial` 은 발신 호스트마다 한 번 알림으로 올립니다[4].

### 같은 일이 되풀이될 때

두 로그 모두 같은 일이 되풀이되면 줄을 덜 씁니다. 이 규칙을 모르고 줄 수를 세면 사건의 규모를 잘못 추정하게 됩니다.

알림은 `note` 와 `identifier` 가 같으면 같은 알림으로 보고, 처음 올린 뒤 `suppress_for` 동안(기본 `Notice::default_suppression_interval = 1hrs`) 다시 올리지 않습니다[2][3]. `identifier` 는 스크립트 작성자가 정하는데, `SSL::Invalid_Server_Cert` 는 응답 주소·응답 포트·검증 결과·인증서 해시를 합친 값을 씁니다[2]. 그래서 같은 서버의 같은 인증서라면 한 시간 동안 클라이언트 여러 대가 접속해도 알림은 처음 한 번만 남습니다. `identifier` 를 주지 않은 알림은 억제하지 않습니다[2]. 설정으로 알림 종류마다 억제 기간을 바꾸거나(`Notice::type_suppression_intervals`), 억제를 끄거나(`Notice::not_suppressed_types`), 아예 기록하지 않게(`Notice::ignored_types`) 할 수 있습니다[2]. 클러스터에서는 관리 노드가 억제 정보를 나눠 주는데, 전달이 늦는 사이에 같은 알림이 여러 노드에서 중복으로 생길 수 있습니다[2].

이상 기록은 두 단계를 거칩니다. 먼저 Zeek 코어가 표본 추출 (sampling) 을 합니다. 같은 이름의 이상이 25번(`Weird::sampling_threshold`)까지는 모두 스크립트로 넘기고, 그 뒤로는 1000번에 한 번(`Weird::sampling_rate`)만 넘깁니다[5]. 이 개수는 연결 단위 이상이면 연결마다, 흐름 단위 이상이면 주소 쌍마다, 네트워크 단위 이상이면 이름마다 따로 세고, 10분(`Weird::sampling_duration`)이 지나면 다시 처음부터 셉니다[5]. 다음으로 `weird.zeek` 스크립트가 중복을 줄입니다. 같은 이름과 같은 식별자(연결 단위면 연결의 주소·포트)의 이상은 10분 동안 한 번만 기록하고, 한 번만·연결마다·발신 호스트마다 기록하는 동작은 그 기록 여부를 하루 동안 기억합니다[4]. 체크섬 오류 네 종류는 10분 중복 규칙에서 빠지지만 기본 동작이 발신 호스트마다 한 번이라서, 결국 발신 호스트마다 하루에 한 번 정도 남습니다[4]. 연결 정보가 없는 네트워크 단위·파일 단위 이상은 식별자가 비어 있어서 같은 이름이면 센서 전체에서 10분에 한 번만 남습니다[4].

## 증거로서 의미

**증명하는 것.** notice.log 한 줄은 "이 센서에서 이 스크립트가 이 네트워크 시각에 자기 조건이 맞는 상황을 봤다" 는 기록입니다. `SSL::Invalid_Server_Cert` 라면 센서에 있는 인증 기관 목록으로 이 서버 인증서를 검증했을 때 `msg` 의 이유로 실패했다는 뜻입니다[2]. weird.log 한 줄은 이 분석기가 이 연결이나 흐름에서 자기 프로토콜 규칙과 다른 데이터를 봤다는 기록입니다[1]. 둘 다 `uid` 가 있으면 같은 연결의 다른 로그와 이어 볼 수 있습니다.

**증명하지 못하는 것.** 알림이나 이상 기록이 있다고 해서 공격이었다고 쓸 수는 없습니다. Zeek 스크립트는 상황을 "관심을 둘 만할 수 있다" 고 표시할 뿐이고, 어느 환경에서는 공격인 일이 다른 환경에서는 정상 업무일 수 있습니다[2]. 이상 기록은 대개 보안과 관계없는 이상한 동작입니다[2]. 인증서 검증 실패 알림만으로는 클라이언트가 경고를 무시하고 통신을 이어 갔는지 알 수 없으므로, 같은 연결의 `ssl.log`·`conn.log` 로 확인합니다[2]. 반대로 알림이나 이상 기록이 없다고 해서 그런 일이 없었다고 쓸 수도 없습니다. 억제와 표본 추출, `Notice::ignored_types` 나 `Weird::ignore_hosts` 같은 설정, 불러오지 않은 스크립트, 센서에 닿지 않은 트래픽 때문에 기록이 빠질 수 있습니다[2][4]. 알림이 남긴 주소가 어떤 사용자나 프로세스였는지도 이 로그로는 알 수 없습니다.

보고서에는 "2026-03-02 06:00:01 UTC 에 Zeek 의 인증서 검증 스크립트가 192.168.1.20 에서 203.0.113.45:8443 으로 가는 연결의 서버 인증서를 자체 서명 인증서라서 검증하지 못했다는 알림을 남겼다. 같은 조건의 알림은 기본 1시간 동안 다시 남지 않는다" 처럼 씁니다(만든 예시).

## 시각 해석

두 로그의 `ts` 는 모두 네트워크 시각(패킷 시각)을 기준으로 한 UTC 에포크 초이고, JSON 에서는 센서 설정에 따라 ISO 8601 문자열로 쓰기도 합니다([Zeek 로그](index.md)). 기록한 시각이 무엇을 뜻하는지는 두 로그가 다릅니다.

weird.log 의 `ts` 는 분석기가 이상을 알아챈 때의 네트워크 시각입니다[4]. 요청을 해석하는 순간 남는 이상이라면 다른 로그와 시각이 같게 나옵니다. 빠른 시작 안내서의 quickstart.pcap 을 처리하면 `unknown_HTTP_method` 이상과 같은 요청의 http.log 줄이 둘 다 `1747147654.311012` 로 나옵니다[6].

notice.log 의 `ts` 는 스크립트가 판단을 끝내고 알림을 올린 때입니다[3]. 그래서 관련 연결의 시작이나 이상 기록보다 늦을 수 있습니다. 공식 문서 예시에서 같은 `uid` 의 이상 기록은 04:59:21.582639, 알림은 04:59:23.038713 로 약 1.5초 늦습니다[1]. 여러 연결을 보고 판단하는 알림은 그 차이가 더 큽니다. `SSH::Password_Guessing` 은 한 호스트의 로그인 실패가 정해진 횟수를 넘은 때 올라가므로, 알림 시각은 첫 시도가 아니라 기준을 넘은 시각입니다[2]. 첫 시도 시각은 같은 `src` 의 conn.log·ssh 기록에서 찾습니다.

억제 때문에 같은 알림의 첫 시각만 남는다는 점도 시간 해석에 영향을 줍니다. 알림이 06:00 에 한 번 있고 그 뒤로 없다면 06:00 부터 07:00 사이에 같은 일이 되풀이됐을 수 있습니다. 여러 기록을 한 시간순으로 합치는 방법은 [네트워크 타임라인](../../../03-techniques/analysis/timeline.md)에 있습니다.

## 함정과 한계

**`uid` 가 없는 알림.** 여러 연결에 걸친 호스트 단위 알림은 연결 정보 없이 `src` 만 채우는 것이 권장 방식입니다[2]. 공식 문서의 `SSH::Password_Guessing` 예시도 `uid`·`id` 가 모두 `-` 이고 `msg`·`sub`·`src` 만 채워져 있습니다[2]. 이런 알림은 `uid` 로 잇지 못하므로 `src` 와 시간 구간으로 conn.log 를 찾습니다.

**파일 알림의 연결.** 파일과 관련된 알림은 파일이 여러 연결로 오갔을 때 그중 하나만 골라 `uid`·`id` 를 채웁니다[3]. 그 파일이 오간 연결 전체는 `fuid` 로 [files.log](files-log.md)에서 찾습니다.

**`src` 와 `dst` 의 뜻은 스크립트마다 다릅니다.** SQL 삽입 알림은 Zeek 8.0.0 에서 `src` 가 공격받은 호스트에서 공격한 호스트로 바뀌었습니다[7]. 알림 종류 이름은 그대로라서, 어느 스크립트가 올렸는지는 `uid`·`dst` 가 채워져 있는지로 구분합니다[7]. 버전이 섞인 로그에서 공격 방향을 잘못 읽지 않도록 센서 버전부터 확인합니다.

**conn.log 에 없는 연결.** 알림이나 이상 기록에는 있는데 conn.log 에는 같은 `uid` 가 없는 경우가 있습니다. 로그 기간 안에 끝나지 않은 긴 연결일 가능성이 있습니다[1].

**캡처 품질 문제로 생긴 이상 기록.** 체크섬 오류 이상은 체크섬이 틀린 패킷에서 생기는데, 체크섬 오프로딩을 쓰는 기계에서 캡처한 패킷은 체크섬이 채워지지 않은 상태입니다[6]. 그래서 한 호스트나 한 노드에서 체크섬 이상이 몰려 있다면 공격보다 캡처 환경 문제일 가능성을 먼저 봅니다. 클러스터에서 `peer` 필드는 어느 노드가 문제를 겪는지 확인하려고 둔 것이므로[4], 이상 기록이 특정 워커에만 몰리면 그 워커의 캡처 위치와 설정을 확인합니다. 캡처 위치에 따른 차이는 [어디서 캡처하나](../../../01-foundations/capture/capture-points.md)에 있습니다.

**줄 수는 발생 횟수가 아닙니다.** 앞에서 본 억제와 표본 추출 때문에 알림 한 줄 뒤에 같은 일이 수백 번 있었을 수 있습니다. 공식 문서의 한 가정망 24시간 예시에서도 `window_recision` 이상이 553번, `SSL::Invalid_Server_Cert` 알림이 654번 기록될 만큼 흔한 기록이 많습니다[1]. 개수를 비교할 때는 같은 센서, 같은 설정, 같은 기간끼리만 비교합니다.

**설정 확인.** 센서에서 알림 종류나 이상 이름을 빼는 설정(`Notice::ignored_types`, `Weird::ignore_hosts`, `Weird::actions` 재정의)이 있으면 그 기록은 처음부터 남지 않습니다[2][4]. Security Onion 은 MITRE BZAR 스크립트를 함께 넣어 두지만 기본으로 꺼 두므로, BZAR 알림이 없다고 해서 그 행위가 없었다고 볼 수 없습니다[10]. 로그를 해석하기 전에 센서의 `local.zeek` 과 현장 스크립트를 받아 둡니다.

## 직접 분석해 보기

### 헥스로 한 번

`unknown_HTTP_method` 이상이 어떤 바이트에서 나오는지 따라가 봅니다. HTTP 요청 줄 `WEIRD / HTTP/1.1` 을 바이트로 쓰면 다음과 같습니다.

```
57 45 49 52 44 20 2f 20 48 54 54 50 2f 31 2e 31 0d 0a
W  E  I  R  D  sp /  sp H  T  T  P  /  1  .  1  CR LF
```

(HTTP 요청 줄 형식으로 만든 예시)

첫 공백(`20`) 앞의 `57 45 49 52 44` 가 메서드 `WEIRD` 입니다. Zeek 의 HTTP 스크립트는 이 값을 http.log 의 `method` 에 그대로 쓰고, 알려진 메서드 목록 `HTTP::http_methods`(GET·POST·HEAD·OPTIONS·PUT·DELETE·TRACE·CONNECT 와 WebDAV 메서드 등)에 없으면 연결 단위 이상 `unknown_HTTP_method` 를 올리면서 메서드 이름을 추가 정보로 넘깁니다[9]. 그래서 weird.log 의 `addl` 에 `WEIRD` 가 들어갑니다[6]. 이 이상은 스크립트가 올린 것이라 `source` 는 비어 있습니다[6]. http.log 쪽 해석은 [HTTP 기록](http-log.md)에 있습니다.

### 공개 도구로 한 번

먼저 어떤 이름이 얼마나 있는지 봅니다. TSV 로그는 `zeek-cut` 으로 필드를 골라 셉니다[11].

```
zeek-cut name < weird.log | sort | uniq -c | sort -rn
zeek-cut note msg < notice.log | sort | uniq -c | sort -rn
```

JSON 로그는 jq 로 필드를 뽑아 셉니다[11]. 공식 문서의 가정망 예시 목록과 같은 모양이 나옵니다[1].

```
jq -c '[.name, .notice]' weird.log | sort | uniq -c
jq -c '[.note, .msg]' notice.log | sort | uniq -c
```

다음으로 눈에 띄는 줄의 `uid` 로 같은 연결의 다른 로그를 찾습니다.

```
jq -c 'select(.uid == "CaB3xK9mPq2LdY7wE1")' conn.log http.log weird.log notice.log
```

(만든 예시)

`uid` 가 없는 알림이면 `src` 로 시간 구간을 좁혀 conn.log 를 찾습니다. 압축된 로그는 `zcat` 으로 풀어 파이프로 넘깁니다([Zeek 로그](index.md)).

## 교차 검증

| 함께 볼 기록 | 확인할 것 | 페이지 |
|---|---|---|
| conn.log | 같은 `uid` 의 연결 상태·바이트 수. 알림 뒤에도 통신이 이어졌는지, 연결이 로그에 없다면 긴 연결인지 | [연결 기록](conn-log.md) |
| http.log | `unknown_HTTP_method`·파이프라이닝 이상과 같은 `uid` 의 요청 | [HTTP 기록](http-log.md) |
| ssl.log·x509.log | 인증서 검증 실패 알림의 `sub` 와 인증서 주체, 핸드셰이크가 끝났는지 | [TLS·인증서 기록](ssl-x509-log.md) |
| files.log | 파일 알림의 `fuid` 로 파일이 오간 연결 전체와 해시 | [파일 기록](files-log.md) |
| dns.log | 알림의 `dst` 주소를 그 전에 어떤 이름으로 물었는지 | [DNS 기록](dns-log.md) |
| Suricata EVE | 같은 흐름의 경고. notice.log 에 커뮤니티 ID 를 쓰는 `policy/frameworks/notice/community-id` 는 배포본 `local.zeek` 에서 주석 처리돼 있어[8], 없으면 5-튜플과 시각으로 맞춤 | [Suricata EVE 로그](../../suricata/eve-json/index.md) |

알림을 탐지 규칙의 결과와 함께 해석하는 방법은 [탐지 규칙 활용](../../../03-techniques/analysis/detection-rules.md)에 있습니다.

## 실습

Zeek 빠른 시작 안내서의 quickstart.pcap 을 `zeek -r quickstart.pcap LogAscii::use_json=T` 로 처리하면 conn.log·http.log·weird.log 가 생깁니다[6].

1. weird.log 의 `unknown_HTTP_method` 줄에서 `uid` 를 찾아 conn.log·http.log 의 줄과 잇고, 세 로그의 `ts` 가 각각 연결의 어느 순간인지 설명합니다.
2. weird.log 의 `peer`·`source` 값은 무엇이고, 왜 그 값이 나왔습니까?
3. 같은 pcap 을 TSV 로 다시 처리해 `zeek-cut name addl < weird.log` 결과를 확인하고, 두 실행의 `uid` 가 같은지 비교합니다.
4. 다른 pcap 하나를 처리해 weird.log 의 이름별 개수를 세고, 많이 나온 이름이 있는 연결의 conn.log `history`·`missed_bytes` 를 보면서 캡처 품질 문제인지 판단합니다.

## 참고 문헌

1. Zeek Project, Zeek 문서 "weird.log and notice.log". https://github.com/zeek/zeek-docs/blob/master/logs/weird-and-notice.rst
2. Zeek Project, Zeek 문서 "Notice Framework". https://github.com/zeek/zeek-docs/blob/master/frameworks/notice.rst
3. Zeek Project, 스크립트 base/frameworks/notice/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/notice/main.zeek
4. Zeek Project, 스크립트 base/frameworks/notice/weird.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/frameworks/notice/weird.zeek
5. Zeek Project, 스크립트 base/init-bare.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/init-bare.zeek
6. Zeek Project, Zeek 문서 "Quick Start Guide". https://docs.zeek.org/en/master/quickstart.html
7. Zeek Project, NEWS(버전별 변경 사항). https://github.com/zeek/zeek/blob/master/NEWS
8. Zeek Project, 스크립트 site/local.zeek. https://github.com/zeek/zeek/blob/master/scripts/site/local.zeek
9. Zeek Project, 스크립트 base/protocols/http/main.zeek. https://github.com/zeek/zeek/blob/master/scripts/base/protocols/http/main.zeek
10. Security Onion Solutions, Security Onion 2.4 문서 "Zeek". https://github.com/Security-Onion-Solutions/securityonion-docs/blob/2.4/zeek.rst
11. Zeek Project, Zeek 문서 "Zeek Log Formats and Inspection". https://github.com/zeek/zeek-docs/blob/master/log-formats.rst
