---
title: "메일 프로토콜"
parent: "기반 · 프로토콜 기초"
nav_order: 80
---

# 메일 프로토콜 (SMTP·IMAP·POP3)

메일은 SMTP 로 보내고 IMAP 이나 POP3 로 받아 읽습니다. 평문 SMTP 를 잡은 캡처나 Zeek·Suricata 로그에는 발신·수신 주소와 제목, 첨부 파일까지 남지만, TLS 로 감싼 연결에는 서버 이름과 주고받은 바이트 수 정도만 남습니다. 이 페이지는 세 프로토콜의 구조와, 각 구조가 네트워크 기록에 어떤 모양으로 남는지를 다룹니다.

## 이 프로토콜을 쓰는 아티팩트

메일 트래픽은 여러 기록에 나뉘어 남습니다. 평문 SMTP 는 Zeek 의 smtp.log 한 줄에 메시지 하나씩 정리되고, 본문과 첨부는 files.log 와 추출 파일로 이어집니다[6][7]. Suricata 는 같은 내용을 EVE 의 `smtp`·`email` 필드로 남기고, POP3 는 명령과 응답을 `pop3` 이벤트로 남깁니다[9][10][11]. 암호화된 연결은 conn.log 와 ssl.log 에서 포트와 서버 이름(SNI)으로만 알아볼 수 있습니다[6].

| 기록 | 남는 것 | 자세한 페이지 |
|---|---|---|
| 패킷 캡처 | 평문이면 명령·응답·메시지 전체, TLS 면 핸드셰이크까지 | [Wireshark·tshark로 읽기](../../03-techniques/analysis/wireshark.md) |
| Zeek smtp.log | 봉투 주소, 주요 헤더, 마지막 서버 응답, TLS 전환 여부 | [Zeek 로그](../../02-artifacts/zeek/zeek-logs/index.md) |
| Zeek conn.log·ssl.log | 465·587·993·995 연결의 서비스 이름과 SNI | [TLS와 인증서](tls.md) |
| Suricata EVE | `smtp.*`, `email.*`, `pop3.*` 필드 | [Suricata EVE 로그](../../02-artifacts/suricata/eve-json/index.md) |
| 흐름 기록 | 포트와 바이트 수만 | [흐름 기록](../records/flow-records.md) |

## 구조

### SMTP: 봉투와 내용

SMTP 가 나르는 메일 객체는 봉투 (envelope) 와 내용 (content) 두 부분으로 나뉩니다[1]. 봉투는 `MAIL FROM` 명령으로 준 발신 주소 하나와 `RCPT TO` 명령으로 준 수신 주소 하나 이상입니다. 내용은 `DATA` 명령 뒤에 보내는 헤더와 본문이고, 헤더 형식은 RFC 5322, 본문 형식은 MIME 이 정합니다[1].

봉투 주소와 헤더 주소 사이에는 정해진 관계가 없습니다[1]. 숨은 참조 (Bcc) 로 받는 사람은 `RCPT TO` 에만 있고 `To`·`Cc` 헤더에는 없으며, 헤더의 `From` 과 봉투의 발신 주소도 서로 다를 수 있습니다[1]. 아래는 받는 사람 한 명이 헤더에 없는 대화 예입니다(만든 예시).

```
S: 220 mx.example.net ESMTP
C: EHLO client01
S: 250-mx.example.net
S: 250-STARTTLS
S: 250 HELP
C: MAIL FROM:<alice@example.com>
S: 250 OK
C: RCPT TO:<bob@example.net>
S: 250 OK
C: RCPT TO:<carol@example.net>
S: 250 OK
C: DATA
S: 354 Start mail input; end with <CRLF>.<CRLF>
C: From: "Alice" <alice@example.com>
C: To: <bob@example.net>
C: Subject: Q3 report
C: Date: Mon, 5 Oct 2026 09:12:30 +0900
C: Message-ID: <20261005091230.1234@example.com>
C:
C: (본문)
C: .
S: 250 OK id=ABC123
C: QUIT
S: 221 mx.example.net closing connection
```

`carol@example.net` 은 봉투에만 있어서 받은 사람들의 메일 헤더에는 나타나지 않습니다. 이런 차이는 네트워크에서 봉투를 잡았을 때만 알 수 있습니다.

서버 응답은 세 자리 숫자로 시작합니다. 조사에서 자주 보는 코드는 아래와 같습니다[1].

| 코드 | 뜻 |
|---|---|
| 220 | 서비스 준비 (연결 첫 응답) |
| 221 | 연결 닫음 |
| 250 | 요청 완료 |
| 354 | 메일 입력 시작, `<CRLF>.<CRLF>` 로 끝냄 |
| 421 | 서비스 불가, 연결 닫음 |
| 450·451·452 | 일시적으로 처리 못 함 |
| 500·501·502·503·504 | 명령·인자 문법 오류, 구현하지 않은 명령, 명령 순서 오류 |
| 550 | 메일박스 없음 또는 정책으로 거부 |
| 552·553·554 | 저장 한도 초과, 메일박스 이름 거부(형식 오류 등), 트랜잭션 실패 |

`DATA` 뒤 메시지 끝은 줄 하나에 점만 있는 줄입니다. 바이트로는 `0D 0A 2E 0D 0A` 이고, `MAIL FROM:` 은 `4D 41 49 4C 20 46 52 4F 4D 3A` 입니다(명세로 만든 예시). 헥스 보기에서 이 두 값을 찾으면 한 TCP 흐름 안에서 메시지 하나의 시작과 끝을 찾을 수 있습니다.

### Received 헤더

SMTP 서버는 메시지를 받을 때마다 내용 맨 앞에 `Received` 줄을 붙여야 하고, 이미 있는 줄은 바꾸거나 지우거나 순서를 바꾸면 안 됩니다[1]. 그래서 맨 위 줄이 마지막으로 거친 서버이고, 맨 아래 줄이 처음 받은 서버입니다. 마지막으로 배달한 서버는 봉투의 발신 주소를 `Return-Path` 헤더로 남깁니다[1].

```
Received: from client01 ([198.51.100.7])
        by mx.example.net with ESMTP id ABC123
        for <bob@example.net>; Mon, 5 Oct 2026 09:12:31 +0900
```

위는 만든 예시입니다. `from` 뒤의 `client01` 은 클라이언트가 `EHLO` 로 스스로 밝힌 이름이고, 괄호 안 주소는 서버가 TCP 연결에서 얻은 주소입니다[1]. 앞의 이름은 클라이언트가 마음대로 적을 수 있지만 괄호 안 주소는 서버가 직접 본 값이라, 발신 위치를 볼 때는 괄호 안 주소를 씁니다. NAT 뒤에서 보냈다면 이 주소는 공인 주소입니다([IP 주소·포트·NAT 해석](../records/ip-nat.md)). 날짜는 시간대 이름 대신 `+0900` 같은 오프셋을 붙인 서버 현지 시각으로 적도록 권고합니다[1].

### 암호화: STARTTLS 와 Implicit TLS

메일 연결을 암호화하는 방법은 두 가지입니다. STARTTLS 는 평문으로 연결한 뒤 명령으로 TLS 를 시작합니다. SMTP 서버가 `EHLO` 응답에 `STARTTLS` 를 내놓고, 클라이언트가 `STARTTLS` 를 보내면 서버가 `220 Ready to start TLS` 로 답한 뒤 TLS 핸드셰이크가 이어집니다[2]. 핸드셰이크가 끝나면 SMTP 는 처음 상태로 돌아가고, 양쪽은 그 전에 주고받은 `EHLO` 인자와 확장 목록을 버리며, 클라이언트는 `EHLO` 를 다시 보냅니다[2]. Implicit TLS 는 연결하자마자 TLS 핸드셰이크부터 시작합니다[3].

| 포트 | 쓰임 | 암호화 | Zeek 에 남는 것 |
|---|---|---|---|
| 25 | 서버 간 전달 | 평문, STARTTLS 가능 | 평문이면 smtp.log 에 헤더까지[6] |
| 587 | 메일 제출 (submission) | STARTTLS | conn.log `service` 가 `ssl,smtp`, smtp.log 에 전환 전 정보만[6] |
| 465 | 메일 제출 | Implicit TLS[3] | conn.log `service` 가 `ssl`, smtp.log 없음[6] |
| 110 | POP3 | 평문[4] | Suricata EVE `pop3` 이벤트[11] |
| 995 | POP3 | Implicit TLS[3] | conn.log `service` 가 `ssl`, ssl.log 의 SNI[6] |
| 143 | IMAP | 평문, STARTTLS[5] | IMAP 분석기는 STARTTLS 전환까지만[8] |
| 993 | IMAP | Implicit TLS[3][5] | conn.log `service` 가 `ssl`, ssl.log 의 SNI[6] |

465 포트는 한때 "smtps" 로 등록됐다가 취소되고 다른 서비스(urd)에 배정됐습니다[3]. RFC 8314 는 기존 배정은 그대로 두고 465 를 Implicit TLS 제출 용도로도 배정했습니다[3]. 한 포트에 두 용도가 등록돼 있으므로 포트만으로 메일이라고 단정하지 않습니다[3][6]. TLS 핸드셰이크 구조는 [TLS와 인증서](tls.md)에 있습니다.

### POP3

POP3 는 TCP 110 을 쓰고, 응답은 대문자 `+OK` 또는 `-ERR` 로 시작합니다[4]. 세션은 인증 (AUTHORIZATION), 처리 (TRANSACTION), 갱신 (UPDATE) 세 상태를 차례로 지납니다[4]. `DELE` 명령은 메시지에 삭제 표시만 하고, 실제 삭제는 처리 상태에서 `QUIT` 을 보내 갱신 상태로 들어갔을 때 일어납니다[4]. `QUIT` 없이 연결이 끊기거나 서버의 무활동 자동 로그아웃 타이머(최소 10분)가 끝나면 갱신 상태로 가지 않으므로 메시지를 지우지 않습니다[4]. `RSET` 은 삭제 표시를 모두 풉니다[4].

### IMAP

현재 IMAP 명세는 IMAP4rev2(RFC 9051)이고 RFC 3501 을 대체합니다[5]. 평문 포트는 143, Implicit TLS 포트는 993 입니다[5]. 클라이언트는 명령마다 `A001` 같은 태그를 붙이고, 서버는 완료 응답에 같은 태그와 `OK`·`NO`·`BAD` 중 하나를 붙입니다[5]. 태그 대신 `*` 로 시작하는 줄은 태그 없는 응답 (untagged response), `+` 로 시작하는 줄은 명령을 이어 보내라는 요청입니다[5].

메시지 상태는 플래그로 남습니다. `\Seen` 은 읽음, `\Answered` 는 답장함, `\Flagged` 는 중요 표시, `\Deleted` 는 지울 예정, `\Draft` 는 작성 중이며, `\Recent` 는 IMAP4rev2 에서 폐지됐습니다[5]. `FETCH` 로 `BODY[]` 를 가져오면 `\Seen` 이 저절로 붙고, `BODY.PEEK[]` 로 가져오면 붙지 않습니다[5]. `\Deleted` 가 붙은 메시지는 `EXPUNGE` 나 `CLOSE` 명령을 받아야 실제로 지워지고, `EXAMINE` 으로 읽기 전용으로 연 메일박스에서는 `CLOSE` 로도 지워지지 않습니다[5].

## 읽는 법

### Zeek smtp.log

smtp.log 는 한 연결 안의 메시지마다 한 줄을 남기고, 같은 연결에서 몇 번째 메시지인지를 `trans_depth` 로 적습니다[7]. 앞의 대화를 Zeek 로 읽으면 아래와 비슷한 줄이 생깁니다(만든 예시, JSON 형식).

```
{"ts":"2026-10-05T00:12:31.204518Z","uid":"CExAmPlE0001","id.orig_h":"10.0.0.15","id.orig_p":50123,
 "id.resp_h":"203.0.113.25","id.resp_p":25,"trans_depth":1,"helo":"client01",
 "mailfrom":"alice@example.com","rcptto":["bob@example.net","carol@example.net"],
 "date":"Mon, 5 Oct 2026 09:12:30 +0900","from":"\"Alice\" <alice@example.com>","to":["<bob@example.net>"],
 "msg_id":"<20261005091230.1234@example.com>","subject":"Q3 report","last_reply":"250 OK id=ABC123",
 "path":["203.0.113.25","10.0.0.15"],"tls":false,"fuids":["FExAmPlE0001"]}
```

| 필드 | 담긴 값 |
|---|---|
| `ts` | 메시지를 처음 본 시각 |
| `helo` | `HELO`·`EHLO` 인자 |
| `mailfrom`, `rcptto` | 봉투 발신 주소, 봉투 수신 주소 집합 |
| `date`, `from`, `to`, `cc`, `reply_to`, `subject` | 같은 이름의 헤더 값 |
| `msg_id`, `in_reply_to` | `Message-ID`, `In-Reply-To` 헤더 |
| `x_originating_ip` | `X-Originating-IP` 헤더 |
| `first_received`, `second_received` | 첫째·둘째 `Received` 헤더 |
| `last_reply` | 서버가 마지막으로 보낸 응답 줄 |
| `path` | 메시지 전달 경로 주소 목록 |
| `user_agent` | 클라이언트의 `User-Agent` 헤더 값, `X-Mailer` 헤더 값이 들어가기도 함[6] |
| `tls` | 연결이 TLS 로 바뀌었는지(기본 `F`) |
| `fuids` | 본문·첨부의 파일 ID, files.log 와 연결 |
| `is_webmail` | 웹메일로 보냈는지(`software.zeek` 를 불러올 때만) |

필드 목록과 설명은 Zeek 의 `SMTP::Info` 에 있습니다[7]. `path` 에 모을 범위는 `SMTP::mail_path_capture` 로 정하고, 기본값 `ALL_HOSTS` 는 전체 경로를, `REMOTE_HOSTS` 는 내부 호스트를 만날 때까지를, `LOCAL_HOSTS` 는 외부 호스트를 만날 때까지를 모으며, `NO_HOSTS` 는 모으지 않습니다[7]. `RCPT TO` 앞에 `MAIL FROM` 이 없는 식의 잘못된 트랜잭션이 한 세션에서 25번(`SMTP::max_invalid_mail_transactions` 기본값) 나오면 SMTP 분석기가 꺼질 수 있습니다[7].

`fuids` 의 ID 로 files.log 를 찾으면 본문과 첨부의 해시·MIME 형식을 볼 수 있고, 파일 추출을 켠 환경이면 `extract_files/SMTP-FExAmPlE0001.txt` 같은 파일이 남습니다[6]. 추출 설정에 따라 일부 형식만 저장되므로 `fuids` 개수와 추출 파일 개수가 다를 수 있습니다[6]. 파일을 꺼내는 방법은 [세션 복원과 파일 꺼내기](../../03-techniques/analysis/file-extraction.md)에 있습니다.

587 연결의 smtp.log 에는 STARTTLS 전에 본 정보만 남습니다. `helo` 에 `[192.168.4.41]` 모양의 주소 리터럴, `last_reply` 에 `220 2.0.0 Ready to start TLS`, `tls` 에 `true` 가 있고, `mailfrom`·`subject` 필드는 없으며 `fuids` 는 빈 목록입니다[6].

### Suricata EVE

Suricata 는 봉투 정보를 `smtp.helo`(첫 `HELO` 인자), `smtp.mail_from`(첫 `MAIL FROM` 인자), `smtp.rcpt_to[]`(`RCPT TO` 인자들)에 남깁니다[9]. 헤더는 `email.from`, `email.to`, `email.cc[]`, `email.subject`, `email.date`, `email.message_id`, `email.x_mailer`, `email.received[]` 에 들어가고, 본문에서 뽑은 URL 은 `email.url[]` 에 들어갑니다[10]. 본문 MD5 인 `email.body_md5` 는 `app-layer.protocols.smtp.mime.body-md5` 설정이 켜져 있거나 `auto` 일 때만 쓸 수 있습니다[10]. `raw-extraction` 을 켜면 SMTP 대화 전체를 `rawmsg` 라는 이름의 파일로 저장하는데, 기본값은 `false` 이고 `decode-mime` 과 함께 켜면 저절로 꺼집니다[12].

POP3 는 `pop3` 이벤트에 `request.command`(예: `USER`, `STAT`), `request.args[]`, `response.success`, `response.status`(`OK` 또는 `ERR`), `response.header`(응답 첫 줄), `response.data[]` 로 남습니다[11]. 이 필드로 `DELE` 뒤에 `QUIT` 과 `+OK` 가 이어졌는지 확인할 수 있습니다.

### 암호화된 메일 연결

465·993·995 연결은 conn.log 의 `service` 가 `ssl` 로만 나오고, ssl.log 의 `server_name` 이 `smtp.example.com`·`imap.example.com` 같은 모양일 때 메일 연결로 볼 수 있습니다[6]. TLS 1.2 연결에서는 서버 인증서가 files.log 에 `source` 가 `SSL` 인 항목으로 남지만, TLS 1.3 연결에서는 files.log·x509.log 에 인증서 기록이 생기지 않습니다[6]. 이때 판단할 근거는 SNI, 서버 주소, 연결 시간, 방향별 바이트 수입니다. 받는 쪽 바이트(`resp_bytes`)가 보낸 쪽보다 훨씬 크면 메일을 내려받았을 가능성이 있고, 보낸 쪽이 크면 메일을 보냈을 가능성이 있습니다. 서버 알아보기는 [인증서로 서버 알아보기](../../02-artifacts/fingerprints/certificates.md), 분석 방법은 [암호화된 트래픽 분석](../../03-techniques/analysis/encrypted-traffic.md)에 있습니다.

## 포렌식에서 중요한 점

### 증명하는 것 / 증명하지 못하는 것

평문 SMTP 기록은 이 시각에 이 클라이언트 주소가 이 서버 주소로, 이 봉투 발신·수신 주소와 이 헤더를 붙인 메시지를 보냈고 서버가 `250` 으로 받았다는 것을 증명합니다[6][7]. 587 연결에서 `tls` 가 `true` 이면 STARTTLS 로 암호화를 시작했다는 것까지 증명합니다[6].

SMTP 는 전송 단계에서 보낸 사람을 인증하지 못하고 봉투와 헤더를 따로 적어서, 헤더의 `From` 이 실제로 보낸 사람이라는 것은 증명하지 못합니다[1]. 465·993·995 연결과 587 의 STARTTLS 뒤 내용도 알 수 없습니다[6]. Zeek IMAP 분석기는 STARTTLS 전환까지만 보고 메일 내용은 읽지 않아서, IMAP 으로 어떤 메일을 읽거나 지웠는지는 Zeek 로그에 남지 않습니다[8]. POP3 에서 `DELE` 가 보여도 뒤에 `QUIT` 과 `+OK` 가 없으면 서버에서 실제로 지워진 것이 아닙니다[4]. `DATA` 뒤의 `250` 응답은 받은 서버가 메시지를 배달하거나 넘길 책임을 맡았다는 뜻일 뿐이고, 받는 사람이 메일을 열었다는 뜻은 아닙니다[1].

보고서에는 "메일을 보냈다" 대신 "2026-10-05 00:12:31 UTC 에 10.0.0.15 가 203.0.113.25:25 로 봉투 발신 주소 alice@example.com, 수신 주소 2개인 메시지를 보냈고 서버가 250 으로 받은 기록이 있다(만든 예시)" 처럼 씁니다.

### 시각 해석

smtp.log 의 `ts` 는 Zeek 가 메시지를 처음 본 시각이고, 연결 시작 시각인 conn.log 의 `ts` 보다 조금 늦습니다[6][7]. `date` 필드는 메일 `Date` 헤더 문자열을 그대로 옮긴 값이라, 보낸 클라이언트의 시계와 오프셋을 따릅니다[6][7]. `Received` 줄의 날짜는 각 서버의 현지 시각에 오프셋을 붙인 값입니다[1]. 네트워크에서 본 `ts`, `Date` 헤더, 첫 `Received` 날짜를 모두 UTC 로 바꿔 비교하면 클라이언트나 서버 시계가 얼마나 어긋났는지 볼 수 있습니다. Zeek JSON 로그의 `ts` 는 `1791159151.204518` 같은 epoch 실수로 나오기도 하고 `2026-10-05T00:12:31.204518Z` 같은 ISO 8601 문자열로 나오기도 합니다(만든 예시)[6]. 그래서 실제 로그에서 형식을 먼저 확인합니다. 로그 시각의 기준은 [네트워크 기록의 시각](../records/timestamps.md)에 있습니다.

### 지운 메일과 끊긴 세션

POP3 와 IMAP 은 삭제 표시와 실제 삭제가 따로 일어납니다. POP3 는 `DELE` 뒤 `QUIT` 로, IMAP 은 `\Deleted` 표시 뒤 `EXPUNGE`·`CLOSE` 로 지웁니다[4][5]. 평문 캡처에서 두 단계가 모두 보여야 서버에서 지웠다고 볼 수 있습니다. 캡처가 세션 중간에 끝났다면 두 번째 단계를 놓쳤을 수 있으므로 캡처 시작·끝 시각과 conn.log 의 연결 상태를 함께 봅니다([TCP 연결과 흐름](tcp-sessions.md)).

## 함정

- Zeek 문서는 `mailfrom` 을 "From 헤더에서 찾은 주소" 라고 설명하지만 헤더 `From` 은 `from` 필드에 따로 들어갑니다[7]. `mailfrom` 은 봉투 값으로 보고, 봉투와 헤더가 다른 메일이 있으면 원본 패킷에서 `MAIL FROM` 줄과 한 번 비교합니다.
- STARTTLS 뒤 클라이언트는 `EHLO` 를 다시 보냅니다[2]. 평문 캡처에서 `EHLO` 가 두 번 보여도 이상한 동작이 아닙니다.
- Zeek 로그 문서에는 IMAP·POP3 연결에서 imap.log·pop.log 가 생기지 않는다고 나와 있고, 스크립트 참조에는 IMAP·POP3 분석기 패키지가 있습니다[6][8]. 쓰는 Zeek 버전의 로그 폴더에서 어떤 파일이 생기는지 직접 확인합니다.
- 평문 SMTP 에서 `AUTH LOGIN` 을 쓰면 인증 값이 base64 로만 바뀐 채 네트워크를 지나갑니다[6]. 보고서에는 "인증 정보가 평문 연결로 오갔다" 는 사실까지만 적고 값은 옮기지 않습니다.
- Suricata `email.*` 규칙 비교는 대소문자를 구분합니다[10]. 로그를 검색할 때도 대소문자를 바꿔 한 번 더 찾습니다.
- 표준이 아닌 포트에서 SMTP 를 쓰면 포트로 분류한 통계에서 빠집니다. 포트 대신 캡처 내용에서 `220` 인사말과 `EHLO`·`MAIL FROM` 줄을 찾아 확인합니다[1].

## 도구

평문 캡처는 Wireshark 의 Follow Stream 이나 `tshark -r capture.pcap -q -z follow,tcp,ascii,0` 으로 대화 하나를 통째로 읽습니다[13][15]. 마지막 숫자는 TCP 흐름 번호이고 0부터 셉니다[13]. `tcpflow -r capture.pcap -o outdir` 는 흐름마다 대화를 파일로 나눠 저장합니다[14]. tshark 의 `--export-objects 프로토콜,디렉터리` 로 객체를 꺼낼 수 있고, 지원하는 프로토콜 목록은 `--export-objects help` 로 확인합니다[13]. 로그는 Zeek 의 smtp.log·files.log·ssl.log 와 Suricata EVE 의 `smtp`·`email`·`pop3` 이벤트를 씁니다[6][9][10][11]. 피싱 메일로 시작한 사건을 따라가는 순서는 [피싱 링크를 눌렀나](../../04-scenarios/user-activity/phishing-click.md)에 있습니다.

## 참고 문헌

1. J. Klensin, RFC 5321 「Simple Mail Transfer Protocol」, 2008. https://www.rfc-editor.org/rfc/rfc5321.txt
2. P. Hoffman, RFC 3207 「SMTP Service Extension for Secure SMTP over Transport Layer Security」, 2002. https://www.rfc-editor.org/rfc/rfc3207.txt
3. K. Moore, C. Newman, RFC 8314 「Cleartext Considered Obsolete: Use of Transport Layer Security (TLS) for Email Submission and Access」, 2018. https://www.rfc-editor.org/rfc/rfc8314.txt
4. J. Myers, M. Rose, RFC 1939 「Post Office Protocol - Version 3」, 1996. https://www.rfc-editor.org/rfc/rfc1939.txt
5. A. Melnikov, B. Leiba, RFC 9051 「Internet Message Access Protocol (IMAP) - Version 4rev2」, 2021. https://www.rfc-editor.org/rfc/rfc9051.txt
6. Zeek 문서, smtp.log. https://github.com/zeek/zeek-docs/blob/master/logs/smtp.rst
7. Zeek 문서, base/protocols/smtp/main.zeek (`SMTP::Info`). https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/smtp/main.zeek.rst
8. Zeek 문서, base/protocols/imap 패키지, base/protocols/pop3 패키지. https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/imap/index.rst , https://github.com/zeek/zeek-docs/blob/master/scripts/base/protocols/pop3/index.rst
9. Suricata 사용자 안내서, SMTP Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/smtp-keywords.rst
10. Suricata 사용자 안내서, Email Keywords. https://github.com/OISF/suricata/blob/main/doc/userguide/rules/email-keywords.rst
11. Suricata 사용자 안내서, EVE JSON Format (Event type: POP3). https://github.com/OISF/suricata/blob/main/doc/userguide/output/eve/eve-json-format.rst
12. Suricata 사용자 안내서, suricata.yaml (SMTP). https://github.com/OISF/suricata/blob/main/doc/userguide/configuration/suricata-yaml.rst
13. Wireshark, tshark 매뉴얼. https://github.com/wireshark/wireshark/blob/master/doc/man_pages/tshark.adoc
14. tcpflow 매뉴얼. https://github.com/simsong/tcpflow/blob/master/doc/tcpflow.1.in
15. Wireshark 사용자 안내서, Following Protocol Streams. https://github.com/wireshark/wireshark/blob/master/doc/wsug_src/wsug_advanced.adoc
