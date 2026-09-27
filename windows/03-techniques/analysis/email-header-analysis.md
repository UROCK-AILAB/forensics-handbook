---
title: "메일 헤더 분석"
parent: "기법 · 분석"
nav_order: 3550
---

# 메일 헤더 분석 (Email Header Analysis)

메일 헤더 분석은 `Received`·`Return-Path` 같은 경유 기록과 인증 결과 헤더를 읽는 방법입니다.
메일이 어느 서버를 거쳐 왔는지, 발신 도메인 확인이 어떻게 나왔는지를 판별합니다.
핵심은 어느 줄부터 믿을지 정하는 일입니다.
받은 조직의 서버가 붙인 줄은 그 조직의 기록과 맞춰 볼 수 있고, 그보다 아래 줄은 보낸 쪽이 적어 넣었을 수 있습니다.
메일 파일의 형식과 `Date`·`Message-ID` 같은 헤더 필드는 [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) 에서 다룹니다.

## 언제 쓰나

- **피싱이나 사칭 메일인지 판별할 때** 씁니다. 보이는 발신자와 실제 경로를 따로 봅니다.
- **메일이 어느 서버·IP 주소에서 들어왔는지 찾을 때** 씁니다.
- **조직 안의 어느 PC 가 보냈는지 찾을 때** 씁니다. 내부에서 보낸 메일의 `Received` 줄에는 내부 호스트 이름이 드러날 수 있습니다.
- **메일 시각을 다른 기록과 한 줄로 놓을 때** 씁니다. 줄마다 시간대가 다를 수 있어 UTC 로 맞춰야 합니다.

## 헤더를 얻는 곳

- EML·MBOX 파일은 글자 파일이라 헤더를 바로 읽습니다. 형식은 [인터넷 메일 형식](../../01-foundations/app-mail-data/eml-mbox-rfc-5322-mime.md) 에 있습니다.
- 아웃룩 저장소에서 인터넷 헤더를 꺼내는 법은 [MAPI 속성](../../01-foundations/app-mail-data/mapi-property.md) 과 [아웃룩](../../02-artifacts/mail/outlook/index.md) 에서 다룹니다.
- 다른 메일 프로그램의 저장 방식은 [썬더버드](../../02-artifacts/mail/thunderbird.md), [새 Outlook](../../02-artifacts/mail/new-outlook.md), [Windows 메일 앱](../../02-artifacts/mail/hxstore.md) 을 봅니다.
- 헤더는 원문 그대로 얻습니다. 메일 프로그램이 풀어서 보여 준 화면은 원문 대신 쓰지 않습니다.

## 봉투와 헤더

SMTP 가 나르는 메일 객체는 봉투 (Envelope) 와 내용 (Content) 으로 나뉩니다.

봉투는 SMTP 명령으로 보내며 발신 주소와 받는 주소 하나 이상 등이 들어갑니다. 봉투의 발신 주소는 오류 보고를 받을 곳입니다. 내용은 `DATA` 명령으로 보내고 헤더 부분과 본문으로 나뉘며, 헤더 형식은 RFC 5322 를 따릅니다.

발신자는 두 곳에 따로 있습니다.

| 발신자 | 다른 이름 | 쓰임 |
|---|---|---|
| `MAIL FROM` 주소 | 5321.MailFrom, P1 발신자, 봉투 발신자 | 반송 메일 (NDR) 을 받는 주소입니다 |
| `From` 헤더 주소 | 5322.From, P2 발신자 | 받는 사람이 메일 프로그램에서 보는 주소입니다 |

두 주소는 다를 수 있으므로 헤더 분석에서는 봉투 발신자와 보이는 발신자를 따로 적습니다.

> 그림 자리: 봉투(MAIL FROM, 받는 주소) 안에 내용(헤더 + 본문)이 든 편지 봉투 그림. 봉투의 MAIL FROM 과 헤더의 From 을 다른 색으로 칠하고, 둘이 다를 수 있다는 표시

## Received 줄 읽기

### 누가 언제 붙이나

SMTP 서버는 메일을 중계하거나 최종 전달하려고 받으면 메일 데이터 맨 위에 기록 줄을 넣는데, 이 줄이 `Received` 줄입니다. 서버는 `Received` 줄을 맨 앞에 덧붙여야 하고, 이미 있는 줄의 순서를 바꾸거나 다른 곳에 넣으면 안 됩니다. 메일 프로그램도 이미 붙은 `Received` 줄을 바꾸거나 지우면 안 됩니다. 그래서 가장 최근에 거친 서버의 줄이 맨 위에 있고 처음 보낸 쪽의 줄이 맨 아래에 있으며, 경로는 아래에서 위로 읽습니다.

### 줄의 모양

`Received` 줄은 아래 순서로 씁니다.

```
Received: FROM ... BY ... [VIA] [WITH] [ID] [FOR] ; 날짜시각
```

| 절 | 있어야 하나 | 규칙 |
|---|---|---|
| `FROM` | 반드시 | 보낸 쪽이 EHLO 에서 댄 이름과, TCP 연결에서 얻은 발신 IP 주소를 함께 적는 것이 권장(SHOULD)입니다 |
| `BY` | 반드시 | 이 줄을 붙인 쪽을 적습니다 |
| `VIA`, `WITH` | 선택 | |
| `ID` | 선택 | `@` 가 들어갈 수 있습니다 |
| `FOR` | 선택 | 있으면 받는 주소 하나만 넣습니다 |
| `;` 뒤 날짜시각 | 반드시 | 시간대 이름 대신 `-0800` 같은 숫자 오프셋이 권장입니다. UT 보다 오프셋을 붙인 현지 시각이 권장입니다 |

`FROM` 절의 두 값은 출처가 다릅니다.

EHLO 이름은 보낸 쪽이 스스로 댄 이름이고, 괄호 안의 TCP 정보 (TCP-info) 는 클라이언트의 EHLO 가 아니라 받은 서버가 TCP 연결에서 얻은 정보입니다. 그래서 괄호 안 IP 주소는 받은 서버가 직접 본 값이라 EHLO 이름보다 믿을 만하지만, 그 줄을 붙인 서버를 믿을 수 있을 때만 그렇습니다.

### 예로 따라가기

아래 헤더는 RFC 5321 의 규칙대로 만든 예시입니다.
도메인·IP 주소·ID 는 모두 지어낸 값이며, 실제 메일에서 뽑은 것이 아닙니다.
받은 조직은 `example.com` 이고, 이 조직의 서버는 `mx1.example.com` 과 `mailbox.example.com` 이라고 둡니다.

```
Return-Path: <bounce@lists.example.net>
Received: from mx1.example.com ([198.51.100.25])
        by mailbox.example.com id 7Q2K9
        for <user@example.com>; 3 Mar 2026 10:15:07 +0900
Received: from mail.example.org ([192.0.2.10])
        by mx1.example.com id 5A1B2C
        for <user@example.com>; 3 Mar 2026 01:15:04 +0000
Received: from WORKPC01 ([10.0.0.5])
        by mail.example.org id 88F1; 2 Mar 2026 20:14:58 -0500
From: Sender <sender@example.org>
To: <user@example.com>
```

아래 줄부터 읽습니다.

| 순서 | 붙인 서버 (`BY`) | 보낸 쪽이 댄 이름 | 붙인 서버가 본 IP | 적힌 시각 | UTC |
|---|---|---|---|---|---|
| 1 (맨 아래) | `mail.example.org` | `WORKPC01` | `10.0.0.5` | 2 Mar 2026 20:14:58 -0500 | 3 Mar 2026 01:14:58 |
| 2 | `mx1.example.com` | `mail.example.org` | `192.0.2.10` | 3 Mar 2026 01:15:04 +0000 | 3 Mar 2026 01:15:04 |
| 3 (맨 위) | `mailbox.example.com` | `mx1.example.com` | `198.51.100.25` | 3 Mar 2026 10:15:07 +0900 | 3 Mar 2026 01:15:07 |

적힌 시각만 보면 순서가 뒤섞여 보이지만 UTC 로 바꾸면 아래에서 위로 시각이 늘어납니다. 받은 조직이 붙인 줄 가운데 가장 아래 줄은 2번이고, 이 줄의 `192.0.2.10` 은 받은 조직의 서버가 직접 본 연결 IP 입니다. 1번 줄은 보낸 쪽 서버 `mail.example.org` 가 붙였으므로 받은 조직의 기록만으로는 확인할 수 없습니다. 1번 줄의 `WORKPC01` 은 보낸 쪽 내부 PC 이름일 수 있지만 보낸 쪽이 적은 값이므로 그대로 확정하지 않습니다. `Return-Path` 의 주소는 `From` 과 다른데, 메일링 리스트에서 흔한 모양입니다. 아래 "Return-Path" 절을 봅니다.

## 어느 줄부터 믿나

SMTP 메일은 전송 단계에서 인증과 무결성을 보장하지 못하고, 흔한 사용자도 다른 곳에서 온 것처럼 보이는 메일을 만들 수 있습니다. 그래서 받은 조직의 서버가 붙인 줄보다 아래 줄은 보낸 쪽이 적어 넣었을 수 있으므로 그대로 믿지 않습니다. 받은 조직의 서버가 붙인 줄은 그 서버의 로그와 맞춰 볼 수 있습니다.

신뢰 경계를 찾는 순서입니다.

1. 맨 위 줄부터 내려가며 `BY` 에 받은 조직의 서버 이름이 있는 줄을 찾습니다.
2. 그런 줄 가운데 가장 아래 줄을 고릅니다.
3. 그 줄의 `FROM` 괄호 안 IP 주소를 "조직 밖에서 처음 연결해 온 주소" 로 적습니다.
4. 그보다 아래 줄은 "보낸 쪽이 적은 기록" 으로 따로 적습니다.

- `Received` 줄을 비교하면 느린 중계 같은 문제를 찾을 수 있습니다. 두 줄 사이의 UTC 시각 차이로 두 서버 사이에 걸린 시간을 추정합니다. 두 서버의 시계가 서로 어긋나 있으면 이 차이도 틀어집니다.
- LAN 안에서 보낸 메일의 `Received` 줄에는 내부 호스트 이름 같은 정보가 드러날 수 있습니다. 조직 안에서 보낸 메일이라면 발신 PC 를 찾는 단서가 됩니다. 그 PC 를 누가 썼는지는 [그 시각에 PC 를 쓴 사람이 누구인가](../../04-scenarios/activity/user-attribution.md) 에서 다룹니다.

## Return-Path

최종 전달 서버가 메일 데이터 맨 앞에 `Return-Path` 줄을 넣고, 이 줄은 `MAIL` 명령의 역경로 (reverse-path) 를 보존하는데 곧 봉투 발신자입니다. 형식은 `Return-Path: <주소>` 입니다. 최종 메일은 `Return-Path` 한 줄, 그 아래 `Received` 줄들, 그 아래 나머지 헤더와 본문 순서입니다. `Return-Path` 주소는 실제로 보낸 사람의 주소와 다를 수 있으며, 메일링 리스트가 오류를 관리자에게 보내게 할 때 흔합니다. 최종 전달 서버는 이미 있던 `Return-Path` 를 지우고 자기 것을 넣을 수 있습니다.

## 인증 결과 헤더 (Microsoft 365)

이 절과 다음 절의 헤더는 Microsoft 365 가 받은 메일에 붙이는 값입니다.
다른 메일 서비스의 헤더 이름과 값은 이 페이지에서 다루지 않습니다.
헤더를 풀어 보여 주는 도구로 Message Header Analyzer 가 있습니다.

### Authentication-Results

이 헤더에는 SPF·DKIM·DMARC 검사 결과가 들어 있습니다. 헤더 형식은 RFC 7001 에 정의돼 있습니다.

SPF 결과는 아래 형식입니다.

```
spf=<pass (IP)|fail (IP)|softfail (이유)|neutral|none|temperror|permerror> smtp.mailfrom=<도메인>
```

| 값 | 뜻 |
|---|---|
| `pass` | 도메인의 SPF 에 발신원이 있습니다 |
| `fail` | 발신원이 없고, 도메인이 거부하라고 지시했습니다(`-all`) |
| `softfail` | 발신원이 없고, 받되 표시하라고 지시했습니다(`~all`) |
| `neutral` | 발신원이 없고, 지시가 없습니다(`?all`) |
| `none` | SPF 레코드가 없습니다 |
| `temperror` | DNS 같은 일시 오류가 났습니다 |
| `permerror` | 잘못된 레코드 같은 영구 오류가 났습니다 |

- `smtp.mailfrom` 은 봉투 발신자 쪽 도메인입니다.

DKIM 결과는 아래 형식입니다.

```
dkim=<pass|fail (이유)|none> header.d=<도메인>
```

- `header.d` 는 DKIM 서명에 적힌 도메인이며, 이 도메인에서 공개 키를 조회합니다.
- `none` 은 서명이 없다는 뜻입니다.

DMARC 결과는 아래 형식입니다.

```
dmarc=<pass|fail|bestguesspass|none> action=<permerror|temperror|oreject|pct.quarantine|pct.reject> header.from=<도메인>
```

- `bestguesspass` 는 그 도메인에 DMARC 레코드가 없지만, 있었다면 통과했을 것이라는 뜻입니다.
- `header.from` 은 `From` 헤더 쪽 도메인입니다.
- SPF 는 봉투 발신자 도메인을, DMARC 는 보이는 발신자 도메인을 기준으로 적습니다. 두 도메인이 다르면 둘 다 적습니다.

### compauth

`compauth` 는 SPF·DKIM·DMARC 와 메시지의 다른 부분을 합친 종합 판정이며 `From` 도메인을 기준으로 봅니다. `compauth` 가 `fail` 이어도 다른 판단에 따라 메일이 배달될 수 있습니다. `reason` 은 `compauth` 의 세 자리 이유 코드입니다.

| `reason` | 뜻 |
|---|---|
| `000` | 명시적 인증 실패. DMARC 가 실패했고 정책이 `p=quarantine` 이나 `p=reject` 입니다 |
| `001` | 암묵적 인증 실패 |
| `1xx` | 통과 |
| `2xx` | 약한 통과 (softpass) |
| `3xx`, `4xx`, `9xx` | 검사하지 않았거나 우회했습니다 (none) |
| `6xx` | 암묵적 실패 |
| `601` | 보낸 도메인이 받은 조직의 허용 도메인입니다(자기 조직 도메인 사칭) |

- 표는 코드 가운데 일부입니다. `7xx`(암묵적 인증 통과), `5xx`(DMARC 를 적용하지 않은 반송 메일) 같은 코드도 있으니 전체 목록은 참고 문헌의 Microsoft 문서에서 찾습니다.

### ARC

- ARC (Authenticated Received Chain) 에 관한 AAR·AMS·AS 필드가 있습니다.
- AS 필드의 `cv=` 는 체인 검증 결과입니다. 값은 `none`, `pass`, `fail` 입니다.

## X-Forefront-Antispam-Report (Microsoft 365)

이 헤더는 세미콜론으로 나뉜 `칸:값` 쌍입니다.
아래는 헤더 예의 일부입니다.

```
...CTRY:;LANG:hr;SCL:1;SRV:;IPV:NLI;SFV:NSPM;PTR:;SFTY:;...
```

| 필드 | 뜻 |
|---|---|
| `CIP` | 연결해 온 IP 주소 |
| `CTRY` | 연결 IP 로 정한 발신 국가·지역. 처음 보낸 IP 의 국가와 다를 수 있습니다 |
| `H` | 연결해 온 메일 서버의 HELO/EHLO 문자열 |
| `PTR` | 발신 IP 의 역방향 DNS 결과 |
| `DIR` | 방향. `INB` 는 들어옴, `OUT` 은 나감, `INT` 는 조직 안 |
| `CAT` | 적용된 정책 분류. 예: `PHSH`(피싱), `SPOOF`(사칭), `MALW`(악성코드), `SPM`(스팸), `HPHSH`·`HPHISH`(확실한 피싱), `UIMP`·`DIMP`·`GIMP`(사칭 계열, Defender for Office 365 전용) |
| `SFV` | `NSPM` 은 스팸 아님으로 배달, `SPM` 은 스팸으로 판정. `SKS`·`SKA`·`SKI`·`SKN`·`SKQ`·`SFE`·`BLK` 는 필터를 건너뛰었거나 차단한 사유별 값 |
| `SCL` | 스팸 신뢰 수준 |
| `SFTY` | `9.19` 도메인 사칭, `9.20` 사용자 사칭, `9.25` 첫 연락 안내 |

- 클라우드 조직에서는 `SCL` 값이 메일 처리 결과를 정하지 않습니다. 어떻게 걸렀는지는 `CAT` 와 `DIR` 로 봅니다.
- `X-Microsoft-Antispam` 헤더의 `BCL` 은 대량 메일 불만 수준입니다. 값이 높을수록 스팸일 가능성이 큽니다.
- 표에 없는 필드는 Microsoft 스팸 대응 팀의 진단용입니다. 뜻을 추측해 보고서에 쓰지 않습니다.
- `CIP` 와 `H` 는 Microsoft 365 가 본 연결 정보입니다. 앞 절의 "받은 조직이 붙인 가장 아래 `Received` 줄" 과 맞춰 봅니다.

## 절차

1. **헤더 전체를 원문 그대로 얻습니다.** 저장한 파일의 해시와 얻은 경로를 적습니다.
2. **발신자를 셋으로 나눠 적습니다.** `From` 주소, `Return-Path`(봉투 발신자), 인증 결과의 `smtp.mailfrom`·`header.from` 도메인입니다.
3. **`Received` 줄에 번호를 붙입니다.** 맨 아래를 1번으로 두고 위로 올라갑니다.
4. **줄마다 붙인 서버, 보낸 쪽이 댄 이름, 괄호 안 IP, 시각을 표로 옮깁니다.**
5. **시각을 UTC 로 바꿉니다.** 바꾼 시각이 아래에서 위로 늘어나는지 봅니다. 시간대 맞추기는 [타임라인 작성](timeline/index.md) 을 봅니다.
6. **신뢰 경계를 정합니다.** 받은 조직의 서버가 붙인 가장 아래 줄을 찾고, 그 아래 줄은 보낸 쪽 기록으로 표시합니다.
7. **인증 결과와 스팸 판정 헤더를 읽습니다.** `compauth` 와 `reason`, `CAT`, `SFV`, `SFTY` 를 적습니다.
8. **다른 기록과 맞춥니다.** 받은 조직의 메일 서버 로그, 같은 메일의 다른 사본, 받은 PC 의 메일 저장소를 비교합니다.

## 도구

아래 도구는 예로만 듭니다.

- **텍스트 편집기**: 헤더 원문을 읽습니다. 원본이 아닌 사본으로 엽니다.
- **Message Header Analyzer**: 헤더를 읽기 쉽게 풀어 줍니다. 결과는 원문과 한 번 맞춰 봅니다.
- **스프레드시트**: `Received` 줄을 표로 옮겨 UTC 로 바꿀 때 씁니다.
- 도구마다 풀어 준 결과가 다르면 [도구 결과 교차 검증](../reporting/tool-validation.md) 을 봅니다.

## 함정과 한계

- **`From` 을 보낸 사람으로 적습니다.** `From` 은 받는 사람에게 보이는 주소입니다. 봉투 발신자와 다를 수 있습니다.
- **맨 아래 `Received` 줄을 발신지로 확정합니다.** 받은 조직의 서버보다 아래 줄은 보낸 쪽이 적어 넣었을 수 있습니다.
- **EHLO 이름을 발신 서버로 적습니다.** EHLO 이름은 보낸 쪽이 댄 이름입니다. 괄호 안 IP 는 받은 서버가 본 값입니다.
- **적힌 시각을 그대로 비교합니다.** 줄마다 오프셋이 다를 수 있습니다. UTC 로 바꿔서 비교합니다.
- **`Return-Path` 를 보낸 사람 주소로 봅니다.** 메일링 리스트처럼 다른 주소일 수 있습니다.
- **`compauth=fail` 인데 받은편지함에 있어 이상하다고 봅니다.** 다른 판단에 따라 배달될 수 있습니다.
- **`SCL` 로 처리 결과를 판단합니다.** 클라우드 조직에서는 `CAT` 와 `DIR` 를 봅니다.
- **`CTRY` 를 처음 보낸 곳의 국가로 적습니다.** `CTRY` 는 연결해 온 IP 의 국가입니다.
- **헤더 한 벌만 봅니다.** 글자 파일은 편집기로 고칠 수 있습니다. 서버 로그나 다른 사본과 맞춰 봅니다.

## 결과를 어떻게 해석하나

| 기록 | 알 수 있는 것 | 알 수 없는 것 |
|---|---|---|
| 받은 조직이 붙인 `Received` 줄 | 그 서버가 그 시각에 그 IP 에서 메일을 받았다는 것 | 그 IP 뒤에서 누가 메일을 썼는지 |
| 보낸 쪽이 붙인 `Received` 줄 | 보낸 쪽이 그렇게 적었다는 것 | 그 경로가 사실이라는 것 |
| `From` | 받는 사람에게 보인 주소 | 실제로 보낸 사람 |
| 인증 결과 | 받은 서비스가 그 도메인을 검사한 결과 | 계정 주인이 직접 보냈다는 것 |
| 내부 호스트 이름 | 그 이름의 호스트를 거쳤다고 적혀 있다는 것 | 그 PC 앞에 누가 있었는지 |

- 메일을 누구와 주고받았는지 묶어 보는 흐름은 [누구와 연락을 주고받았나](../../04-scenarios/activity/communication-reconstruction.md) 에서 다룹니다.
- 메일로 자료를 내보냈는지는 [자료를 밖으로 빼돌렸나](../../04-scenarios/exfiltration/data-exfiltration/index.md) 에서 다룹니다.
- 악성 첨부가 메일로 들어왔는지는 [악성코드는 어디서 들어왔나](../../04-scenarios/incident/initial-access.md) 에서 다룹니다.

보고서에는 줄마다 누가 적은 값인지 밝힙니다.

> 이 메일의 `Received` 줄 가운데 수신 조직 서버 `<서버 이름>` 이 붙인 가장 아래 줄에는 연결 IP `<IP>` 와 시각 `<UTC 시각>` 이 적혀 있다. 그보다 아래 줄은 발신 측 서버가 적은 기록이며, 이 분석에서 따로 확인하지 못했다. `Authentication-Results` 의 DMARC 결과는 `<값>`(header.from=`<도메인>`)이다.

## 참고 문헌

- RFC Editor, RFC 5321 "Simple Mail Transfer Protocol" — https://www.rfc-editor.org/rfc/rfc5321.txt
- Microsoft Learn, "Anti-spam message headers" (Defender for Office 365) — https://learn.microsoft.com/en-us/defender-office-365/message-headers-eop-mdo
