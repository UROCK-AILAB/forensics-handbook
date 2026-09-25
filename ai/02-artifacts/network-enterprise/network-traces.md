---
title: "AI 서비스 도메인과 네트워크 기록"
parent: "아티팩트 · 네트워크·기업 기록"
nav_order: 690
---

# AI 서비스 도메인과 네트워크 기록 (DNS·Proxy·SNI)

## 한 줄 요약

AI 서비스에 접속하면 기기 안의 DNS 질의 기록, 네트워크 장비의 TLS 기록, 프록시 기록, 앱의 네트워크 폴더에 "어느 도메인에 언제 붙었는지" 가 남고, 이 기록들은 대화 내용 없이 접속 사실과 시간대만 알려 줍니다.

확인 날짜는 2026-09입니다. 근거는 Microsoft Learn 문서 두 편(Purview 지원 AI 사이트 목록 2025-12-15·갱신 2026-06-25, Sysmon 2026-09-10)과 Zeek 문서(master 판)이고, 앱 폴더는 이 핸드북의 기기 관찰(Windows 11, 2026-09)에서 확인했습니다.

## 무엇을 기록하나 · 왜 생기나

웹 브라우저든 데스크톱 앱이든 AI 서비스와 통신하려면 먼저 도메인 이름을 IP 주소로 바꾸는 DNS 질의를 하고, 그 뒤 TLS 로 암호화한 연결을 엽니다. 대화 본문은 암호화된 연결 안에 들어 있어서 네트워크 쪽에서는 보이지 않지만, 어느 도메인을 찾았고 어느 서버에 연결했는지는 여러 곳에 흔적으로 남습니다.

흔적이 남는 곳은 네 갈래입니다. 기기 안에서는 Sysmon 같은 감시 도구를 설치해 두었을 때 프로세스별 DNS 질의와 연결이 이벤트 로그에 남습니다. 네트워크 경계에서는 Zeek 같은 분석 도구가 TLS 연결을 열 때 클라이언트가 밝힌 도메인 이름, 곧 SNI (Server Name Indication) 를 기록합니다. 조직이 웹 프록시나 보안 접근 서비스(SASE/SSE)를 거치게 해 두었다면 그 제품의 로그에 접속 기록이 남고, 이 갈래는 [보안 제품이 남기는 AI 사용 기록](dlp-casb.md)에서 다룹니다. 마지막으로 Electron 으로 만든 데스크톱 앱은 앱 폴더 안에 쿠키와 네트워크 상태 파일을 따로 둡니다.

이 페이지는 도메인 목록, DNS, SNI, 앱 네트워크 폴더를 다루고, 조직의 관리 콘솔에 남는 감사 기록은 같은 묶음의 다른 페이지에서 다룹니다.

## 위치와 버전별 차이

### 어떤 도메인을 AI 서비스로 볼 것인가

Microsoft Purview 는 데이터 보호 기능이 알아보는 "지원 생성형 AI 사이트" 목록을 도메인 와일드카드로 공개합니다. 서비스를 가려내는 출발점으로 쓸 만한 항목은 아래와 같고, 문서는 이 목록이 시간이 지나며 늘어난다고 밝힙니다.

| 서비스 | 목록에 나온 도메인 |
|---|---|
| ChatGPT | `*.chatgpt.com`, `*.chat.com`, `*.openai.com` |
| Claude | `*.claude.ai`, `*.anthropic.com` |
| Gemini | `*.gemini.google.com`, `*.bard.google.com` |
| Microsoft Copilot | `*.copilot.microsoft.com`, `*.bing.com/chat` |
| 그 밖의 대화형 서비스 | `*.perplexity.ai`, `*.deepseek.com`, `*.grok.com`, `*.poe.com`, `*.character.ai`, `*.meta.ai`, `*.qwen.ai`, `*.doubao.com` |
| 개발·로컬 도구 | `*.cursor.com`, `*.github.com/features/copilot`, `*.ollama.ai` |
| 그 밖의 도구 | `*.notebooklm.cloud.google.com` |

같은 목록에는 공식 서비스와 이름만 비슷한 제3자 사이트(예: `*.chatgpt4online.org`, `*.ai-claude.net`)도 들어 있습니다. 도메인에 서비스 이름이 들어 있다고 해서 공식 서비스를 썼다고 단정하지 않고, 목록에서 그 도메인이 어느 쪽인지 먼저 확인합니다. 각 서비스가 API 호출에 쓰는 도메인의 공식 목록은 이번에 공급사 문서로 확인하지 못해서 이 페이지에 적지 않습니다.

### 기기 안: Sysmon

| 기록 | 이벤트 | 기본 상태 | 담는 것 |
|---|---|---|---|
| DNS 질의 | 이벤트 ID 22 `DNSEvent (DNS query)`, 필터 태그 `DnsQuery` | 설정 파일에 따라 다름 | 프로세스가 한 DNS 질의. 성공·실패, 캐시 여부와 관계없이 기록 |
| 네트워크 연결 | 이벤트 ID 3 `Network connection` | 꺼져 있음 | TCP/UDP 연결. `ProcessId`·`ProcessGuid`, 출발지·목적지 호스트 이름, IP, 포트 |

Sysmon 은 Sysinternals 도구라서 조직이 설치해 두지 않았으면 기록이 없고, 기본 설정으로 설치하면 네트워크 감시를 하지 않습니다. 이벤트 3 은 설정 파일로 켜야 남고, 설정 항목 `DnsLookup`(역방향 DNS 조회)은 기본값이 True 입니다. 이벤트 22 는 Windows 8.1 에 추가된 원격 측정을 쓰기 때문에 Windows 7 이하에서는 생기지 않습니다. 기록은 `Applications and Services Logs/Microsoft/Windows/Sysmon/Operational` 에 쌓이고, 2026-09-10 판 문서는 실행 환경을 클라이언트 Windows 11 이상, 서버 Windows Server 2019 이상으로 적습니다.

Windows 기본 DNS Client 이벤트 로그의 이벤트 번호와 기본 활성 여부, `ipconfig /displaydns` 캐시의 보존 시간은 이번에 확인하지 못했습니다.

### 네트워크 경계: Zeek `ssl.log`

Zeek 는 TLS 트래픽을 분석해 `ssl.log` 에 남기고, `server_name` 칸에 클라이언트가 요청한 도메인(SNI)을 적습니다. 운영체제와 관계없이 네트워크를 지나는 모든 기기의 연결이 대상이라서 Windows·macOS·Android·iOS 기기를 한꺼번에 볼 수 있지만, 조직이 미리 수집 장비를 두었을 때만 기록이 있습니다.

### 기기 안: 데스크톱 앱의 네트워크 폴더

Claude 데스크톱(스토어 앱) 폴더에서는 아래 파일을 확인했습니다(확인 범위: Windows 11, 2026-09). 앱 버전은 관찰 메모에 기록되지 않았고, 아래 경로의 `%USERPROFILE%\Packages` 는 관찰 메모의 표기를 그대로 옮긴 것입니다. 패키지 앱이 `AppData` 에 쓴 파일은 사용자·패키지별 전용 위치로 옮겨 저장되므로, 수집할 때는 경로를 짐작하지 말고 사용자 프로필에서 `LocalCache\Roaming\Claude` 가 들어 있는 패키지 폴더를 찾습니다. 자세한 위치는 [Claude](../chat-services/claude/windows.md) Windows 페이지에서 다룹니다.

```
%USERPROFILE%\Packages\<Claude 패키지>\LocalCache\Roaming\Claude\Network\
    Cookies
    Cookies-journal
    Network Persistent State
    NetworkDataMigrated
    TransportSecurity
%USERPROFILE%\Packages\<Claude 패키지>\LocalCache\Roaming\Claude\Partitions\<이름>\Network\Cookies
```

크롬 계열 앱이 쓰는 이 폴더 구조와 `Network Persistent State`·`TransportSecurity` 가 담는 내용은 공통 원리라서 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)에서 다루고, 이 페이지에서는 되풀이하지 않습니다. ChatGPT·Copilot 데스크톱 앱의 네트워크 폴더와 macOS·Android·iOS 앱의 해당 위치는 이번에 확인하지 않았습니다. 앱별 저장 위치는 [ChatGPT](../chat-services/chatgpt/index.md), [Claude](../chat-services/claude/index.md), [Microsoft Copilot](../chat-services/copilot/index.md) 페이지를 봅니다.

## 구조

### `ssl.log` 에서 볼 칸

| 칸 | 뜻 |
|---|---|
| `server_name` | 클라이언트가 TLS 연결을 열며 밝힌 도메인(SNI) |
| `version` | TLS 버전 |
| `cipher` | 합의한 암호 방식 |
| `curve` | 키 교환에 쓴 곡선 |
| `established` | 연결이 성립했는지 |
| `ja3`, `ja3s` | 클라이언트·서버 TLS 핸드셰이크의 지문. 기본 칸이 아니라 JA3·JA3S 패키지를 설치했을 때 붙는 칸 |

TLS 1.3 은 서버 인증서를 수동 관찰에서 숨기고, ESNI/ECH (Encrypted Client Hello) 를 쓰는 연결은 `server_name` 이 비어서 Zeek 문서도 이런 연결의 `ssl.log` 에는 식별 정보가 없다고 설명합니다. 각 AI 서비스가 ECH 를 쓰는지는 확인하지 못했습니다.

### 앱의 `Cookies` DB

`Partitions\<이름>\Network\Cookies` 를 SQLite 로 열었을 때 표 두 개가 보였습니다(확인 범위: Windows 11, 2026-09).

| 표 | 칸 |
|---|---|
| `cookies` | `creation_utc`, `host_key`, `top_frame_site_key`, `name`, `value`, `encrypted_value`, `path`, `expires_utc`, `is_secure`, `is_httponly`, `last_access_utc`, `has_expires`, `is_persistent`, `priority`, `samesite`, `source_scheme`, `source_port`, `last_update_utc`, `source_type`, `has_cross_site_ancestor` |
| `meta` | `key`, `value` |

칸 이름으로 보면 `host_key` 에는 쿠키를 설정한 도메인이, `creation_utc`·`last_access_utc`·`last_update_utc` 에는 쿠키를 만든 시각과 마지막으로 쓰고 바꾼 시각이 들어갑니다. 값을 읽는 방법과 `encrypted_value` 의 보호 방식은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)와 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)에서 다룹니다. 기본 `Network\Cookies` 는 관찰할 때 열리지 않았는데(OperationalError), 앱이 실행 중이라 파일을 잠갔을 가능성이 있습니다.

## 증거로서 의미

**증명하는 것.** Sysmon 이벤트 22 는 특정 프로세스가 특정 시각에 AI 서비스 도메인을 찾았다는 사실을, 이벤트 3 은 그 프로세스가 어느 IP·포트로 연결했는지를 보여 줍니다. 두 기록 모두 프로세스와 묶여 있어서 브라우저로 접속했는지, 데스크톱 앱이나 개발 도구가 접속했는지를 나눌 수 있습니다. `ssl.log` 의 `server_name` 은 어느 기기가 어느 도메인으로 TLS 연결을 열었는지를 보여 주고, 앱의 `Cookies` 는 그 앱 안에서 어느 도메인이 쿠키를 설정했는지를 보여 줍니다.

**증명하지 못하는 것.** 이 기록들에는 대화 내용이 없어서 무엇을 물었는지, 파일을 올렸는지는 알 수 없습니다. DNS 질의는 사람이 직접 접속하지 않아도 생기는데, 페이지에 들어 있는 다른 사이트의 자원이나 앱의 백그라운드 통신도 질의를 만듭니다. 도메인과 연결 기록은 기기나 계정 단위의 사실이라서 그 시각에 누가 자판 앞에 있었는지는 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)의 방법으로 따로 밝힙니다.

보고서 문장은 "이 시간대에 이 기기의 이 프로세스가 이 도메인을 질의하고 연결한 기록이 있다" 처럼 기록이 말하는 범위에서 씁니다.

## 시각 해석

Sysmon 이벤트의 시각은 UTC 입니다. 이벤트 22 는 질의 한 번마다 생기는 기록이라서 연결이 이어진 시간이 아니라 이름을 찾은 순간을 가리키고, 연결이 얼마나 이어졌는지는 이벤트 3 이나 네트워크 장비 기록으로 봅니다. `Cookies` 표의 시각 칸은 이름에 `utc` 가 붙어 있고, 저장 형식과 바꾸는 법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html)를 따릅니다. `ssl.log` 의 시각 칸은 `ts` 이고, 문서 예시에는 유닉스 시각(초)과 끝에 `Z` 가 붙은 UTC 문자열 두 모양이 모두 나옵니다. 어느 모양으로 남는지는 수집 장비의 출력 설정에 따라 다르므로 받은 파일에서 확인합니다. 여러 기록을 한 줄로 세우는 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

- **감시 도구가 없으면 기록도 없다.** Sysmon 은 기본 설치가 아니고, 설치해도 네트워크 감시는 설정 파일로 켜야 합니다. Zeek·프록시도 조직이 미리 둔 경우에만 기록이 있어서, 기록이 없다는 사실이 접속하지 않았다는 뜻은 아닙니다.
- **비슷한 이름의 도메인.** 지원 사이트 목록 자체에 공식 서비스를 흉내 낸 제3자 도메인이 섞여 있습니다. 도메인을 서비스 이름으로 바꿔 적을 때 공식 여부를 따로 적습니다.
- **ECH 와 TLS 1.3.** ECH 를 쓰는 연결은 `server_name` 이 비고, TLS 1.3 에서는 인증서도 보이지 않습니다. 이런 연결은 DNS 기록이나 목적지 IP 와 묶어서 봐야 합니다.
- **공유 도메인.** `*.bing.com/chat` 처럼 경로까지 붙은 항목은 DNS·SNI 에서 경로가 보이지 않아서 도메인만으로는 AI 기능을 썼는지 검색만 했는지 나누지 못합니다. `*.github.com/features/copilot` 도 같습니다.
- **잠긴 파일.** 앱이 실행 중이면 `Cookies` 가 열리지 않을 수 있어서, `Cookies-journal` 과 함께 복사한 사본으로 봅니다. 기기에서 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)를 따릅니다.
- **지우기.** 사용자가 기기에서 앱 폴더를 지워도 기기 밖의 Zeek·프록시 기록과 이미 중앙으로 모은 이벤트 로그 사본은 그대로 남습니다. 기기 안 기록과 기기 밖 기록이 서로 맞지 않으면 그 차이를 지운 흔적의 단서로 적습니다.

## 직접 분석해 보기

**헥스로 한 번.** 앱의 `Cookies` 파일이 SQLite DB 인지 먼저 확인합니다. SQLite 파일은 첫 16바이트가 정해진 문자열이라서, 파일 앞부분이 아래와 같으면 SQLite 도구로 열 수 있습니다. 아래는 SQLite 파일 형식 명세로 **만든 예시**이고 특정 검체에서 뽑은 값이 아닙니다.

```
오프셋    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00   SQLite format 3.
```

머리 뒤의 페이지 구조와 지운 행을 찾는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html)에서 다룹니다.

**공개 도구로 한 번.** 파일을 복사한 뒤 DB Browser for SQLite 같은 공개 도구로 열고, 아래처럼 AI 서비스 도메인이 설정한 쿠키만 뽑아 봅니다. 도메인 조건은 위 표에서 조사할 서비스에 맞게 고칩니다.

```sql
SELECT host_key, name, creation_utc, last_access_utc
FROM cookies
WHERE host_key LIKE '%claude.ai' OR host_key LIKE '%anthropic.com'
ORDER BY last_access_utc;
```

패킷 캡처 파일이 있다면 Zeek 로 읽어 `ssl.log` 를 만들고 `server_name` 칸에서 같은 도메인을 찾습니다. 아래는 칸 이름만 맞춘 **만든 예시**입니다.

| `server_name` | `version` | `established` | `ja3`(패키지 설치 시) |
|---|---|---|---|
| `claude.ai` | `TLSv13` | `T` | (32자리 16진수 지문) |
| (빈 칸) | `TLSv13` | `T` | (32자리 16진수 지문) |

두 번째 줄처럼 `server_name` 이 빈 연결은 같은 시각의 DNS 기록과 목적지 IP 를 맞춰 봐야 어느 서비스인지 짐작할 수 있습니다.

## 교차 검증

- [보안 제품이 남기는 AI 사용 기록](dlp-casb.md) — 프록시·SASE/SSE·DLP 가 같은 접속을 기록했는지
- [Microsoft Purview로 본 Copilot 기록](purview-copilot.md) — 조직 계정으로 Copilot 을 쓴 감사 기록
- [Claude 기업용 감사 로그](claude-enterprise.md) — 같은 시간대의 로그인 기록과 `ip_address`
- [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) — 브라우저 방문 기록으로 어느 페이지를 열었는지
- [회사가 허용하지 않은 AI를 썼나](../../04-scenarios/data-leak/shadow-ai.md) — 도메인 기록을 조사 질문에 쓰는 흐름

## 실습

공개 검체(NIST CFReDS 등)에 AI 서비스 접속 기록이 들어 있는지는 확인하지 않았습니다. 시험용 PC 와 패킷 캡처 도구로 아래 질문을 직접 풀어 봅니다.

1. Sysmon 을 기본 설정으로 설치하고 AI 서비스에 접속한 뒤, 이벤트 22 와 이벤트 3 이 각각 남는지 확인합니다. 설정 파일로 이벤트 3 을 켠 뒤 다시 비교합니다.
2. 브라우저와 데스크톱 앱으로 같은 서비스에 접속하고, 이벤트 22 의 프로세스로 두 접속을 나눌 수 있는지 봅니다.
3. 같은 접속을 패킷으로 잡아 Zeek 로 `ssl.log` 를 만들고, `server_name` 이 위 도메인 표의 어느 항목과 맞는지 적습니다.
4. 데스크톱 앱에서 로그아웃한 뒤 `Cookies` 에서 사라진 행과 남은 행을 비교합니다.

## 참고 문헌

1. Supported AI sites by Microsoft Purview for data security and compliance protections — Microsoft Learn (2025-12-15, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/ai-microsoft-purview-supported-sites
2. Sysmon — Sysinternals, Microsoft Learn (2026-09-10) — https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
3. ssl.log — Zeek documentation (master) — https://docs.zeek.org/en/master/logs/ssl.html
4. Understanding how packaged desktop apps run on Windows — Microsoft Learn (2025-09-09, 갱신 2026-01-28) — https://learn.microsoft.com/en-us/windows/msix/desktop/desktop-to-uwp-behind-the-scenes
