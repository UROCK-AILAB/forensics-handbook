---
title: "악성 코드가 지갑을 노렸나"
parent: "시나리오 · 기기 사용"
nav_order: 380
---

# 악성 코드가 지갑을 노렸나 (Wallet Stealer)

정보 탈취 악성 코드(인포스틸러, infostealer)는 브라우저 확장 지갑의 저장소와 데스크톱 지갑 파일을 모아 공격자 서버로 보내고, 클립보드 바꿔치기 악성 코드는 사용자가 복사한 받는 주소를 공격자 주소로 바꿉니다. 이 페이지는 기기에 있던 지갑 목록에서 출발해 유입·실행·수집·전송 흔적을 시간순으로 합치고, 블록체인에서 빠져나간 거래와 대조하는 순서를 다룹니다. "악성 코드가 지갑을 노렸는가" 와 "그래서 자산이 빠져나갔는가" 는 근거가 달라서 따로 판단합니다.

## 조사 질문

- 이 기기에서 지갑 데이터를 노리는 악성 코드가 실행됐는가.
- 그 악성 코드가 어떤 지갑 파일·확장 저장소를 읽었거나 모아 보냈는가(피해 범위).
- 그 뒤 자산이 빠져나간 거래가 있는가. 있다면 키가 새서 남이 서명한 것인가, 사용자가 바뀐 주소나 바뀐 거래 내용에 직접 서명한 것인가.

## 먼저 확인할 것

피해 범위는 기기에 어떤 지갑이 있었는지에서 정해집니다. 그래서 먼저 [이 기기로 지갑을 썼나](wallet-use.md)의 방법으로 사용자 계정·브라우저 프로필마다 지갑 앱, 확장 지갑, 키 파일 목록을 만듭니다. Chromium 계열 브라우저의 확장 지갑은 프로필 폴더의 `Local Extension Settings` 아래 확장 ID 이름의 폴더에 있고, Chrome 기본 프로필의 MetaMask 는 `%localappdata%\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn\` 입니다[18]. 이 폴더는 LevelDB 형식이라 `.ldb`·`.log` 파일로 이뤄지며, 저장 형식은 [Windows 핸드북의 LevelDB 페이지](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)에 있습니다.

다음으로 로그가 어디까지 남는 환경이었는지 확인합니다. 파일을 누가 읽었는지는 Windows 기본 설정의 이벤트 로그에 남지 않습니다. Microsoft-Windows-Kernel-File ETW(Event Tracing for Windows) 공급자를 수집하는 도구가 있었거나, "Audit File System" 감사 하위 범주를 켜고 대상 파일마다 읽기 감사를 설정했어야 합니다[10][12][13]. 이때 남는 보안 로그 이벤트는 [Windows 파일 접근 감사 (4656·4663·4660)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/event-logs/4656-4663-4660.html)에서 다룹니다. 보안 제품(EDR)·프록시·방화벽 기록이 있는지도 이때 확인합니다.

수집 범위에는 메모리를 넣습니다. LummaC2 는 C2(명령 제어) 서버와 주고받지 않으면 디스크에 파일을 만들지 않고 메모리에서만 실행되며 시스템 정보를 모아 보냅니다[1]. 기기 시간대와 시계 오차도 기록해 둡니다. 유입·실행·전송 시각은 기기 시계로 남고, 도난 거래는 블록 시각으로 남아서 둘을 같은 기준으로 맞춰야 합니다.

## 노리는 방식 세 가지

**정보 탈취형**은 지갑 파일과 확장 저장소, 브라우저에 저장된 암호·쿠키를 모아 보냅니다. 지갑 파일이 암호화돼 있어도 안전하다고 할 수 없습니다. Bitcoin Core 의 `wallet.dat` 은 기본값이 암호화하지 않은 상태이고, 암호화해도 키로거를 설치해 암호를 얻는 공격은 막지 못할 수 있습니다[17]. InvisibleFerret 처럼 키 입력을 기록하는 기능이 함께 있는 악성 코드도 있습니다[4]. 확장 저장소의 LevelDB 에서는 현재 볼트뿐 아니라 덮어쓴 옛 볼트까지 나올 수 있어서[18], `.ldb` 파일을 통째로 가져간 경우 옛 볼트도 도난 범위에 들어갈 수 있습니다. 볼트와 지갑 파일의 모양은 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있습니다.

**클립보드 바꿔치기형**(clipper)은 지갑 파일을 건드리지 않습니다. 클립보드를 감시하다가 암호화폐 주소가 복사되면 공격자 주소로 덮어쓰고, 사용자는 바뀐 주소로 직접 서명해 보냅니다. Metamorfo 는 클립보드의 비트코인 주소를 공격자 주소로 덮어쓰고, Melcoz 는 암호화폐 주소를 공격자 주소로 바꾸며, Mispadu 는 클립보드의 비트코인 지갑 데이터를 잡아 바꿉니다[8][9]. Windows 에서는 `clip.exe` 나 `Get-Clipboard` 로도 클립보드를 읽을 수 있습니다[8].

**지갑 앱 변조형**은 지갑 프로그램 자체를 바꿉니다. GlassWorm 은 Ledger Live·Trezor Suite 가 설치됐는지 확인하고, 하드웨어 지갑 앱을 변조해 서명 전에 거래 내용을 가로채 바꿀 수 있습니다[5][9]. 그래서 하드웨어 지갑을 썼다는 사실만으로 이 경로를 뺄 수 없습니다.

지갑을 노리는 악성 코드와 조사에 쓸 흔적을 아래 표로 정리합니다. macOS 정보 탈취 악성 코드(AMOS 등)는 [macOS 핸드북의 정보 탈취 악성 코드 페이지](https://urock-ailab.github.io/forensics-handbook/mac/04-scenarios/incident/infostealer.html)에 있습니다.

| 악성 코드 | 지갑과 관련된 행동 | 조사에 쓸 흔적 |
|---|---|---|
| LummaC2 (Lumma Stealer) | 개인정보·금융 자격 증명·암호화폐 지갑·브라우저 확장·MFA 정보를 빼냅니다. 2022년부터 서비스형 악성 코드(MaaS)로 팔렸습니다[1][2] | 스피어피싱 링크·첨부, 가짜 CAPTCHA 가 시키는 실행 창(Win+R) 붙여 넣기와 Base64 PowerShell, 인기 소프트웨어로 위장한 설치 파일로 들어옵니다. 대상 목록은 C2 가 JSON 설정으로 내려주고, `ad` 값이 참이면 자기 삭제합니다[1] |
| RedLine Stealer | 암호화폐 지갑 데이터, 브라우저와 확장 정보, 브라우저에 저장된 카드 정보를 모읍니다. Windows 용이고 2020년 처음 확인됐습니다[6] | MSI 설치 파일로 설치되고, 예약 작업으로 지속합니다[6] |
| Raccoon Stealer | 암호화폐 지갑 관련 저장소와 Telegram 정보를 모읍니다. C2 에서 받은 설정에 적힌 파일·폴더를 수집합니다[7] | 크랙 소프트웨어로 퍼졌고, `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid` 로 호스트를 식별합니다[7] |
| BeaverTail | 암호화폐 지갑 확장을 찾아 확장 폴더의 `.ldb`·`.log` 파일을 모읍니다. 사용자 폴더의 Solana 키 `.config/solana/id.json`[20], macOS 로그인 키체인 `/Library/Keychains/login.keychain`, Linux `/.local/share/keyrings`, Firefox `key3.db`·`key4.db`·`logins.json` 도 가져갑니다[3]. 로그인 키체인 파일이 실제로 있는 사용자 폴더 경로는 [macOS 키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/)에 있습니다 | 코드 저장소·NPM 패키지·첨부 파일, `MiroTalk.msi`·`MiroTalk.dmg` 로 위장한 설치 파일로 들어옵니다. 임시 폴더에 모아 zip 으로 묶고, 보낸 뒤 파일을 지웁니다. C2 포트는 1224·1244 입니다[3] |
| InvisibleFerret | Chrome·Brave·Opera·Yandex·Edge 에 저장된 로그인·자동완성·지갑·결제 정보, 이름에 secret·wallet·private·password 가 든 파일, 클립보드 내용을 모읍니다[4] | BeaverTail 이 내려받습니다. 7zip·RAR·zip 으로 묶어 Telegram·FTP 로 보내고, Windows 시작 프로그램 폴더의 `queue.bat`, macOS LaunchAgent `com.avatar.update.wake.plist` 로 지속합니다[4] |
| GlassWorm | 데스크톱 지갑 데이터와 Desktop·Documents·Downloads 폴더 문서를 모으고, 하드웨어 지갑 앱을 변조합니다[5] | VS Code 확장·GitHub 프로젝트로 퍼집니다. `/tmp/ijewf` 에 모으고 `/tmp/out.zip` 으로 묶으며, HKCU·HKLM 의 `Software\Microsoft\Windows\CurrentVersion\Run` 키나 macOS LaunchAgent 로 지속합니다. 실행을 15분(900,000 밀리초) 늦춥니다[5] |

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 기기에 있던 지갑·확장·키 파일 목록 | 피해 범위 후보 | [이 기기로 지갑을 썼나](wallet-use.md), [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md) |
| 2 | 유입 경로 | 피싱 메일, 내려받은 설치 파일, 가짜 CAPTCHA 붙여 넣기, NPM 패키지, VS Code 확장 | [피싱 링크를 눌렀나](https://urock-ailab.github.io/forensics-handbook/network/04-scenarios/user-activity/phishing-click.html), [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) |
| 3 | 실행과 지속 흔적 | 실행 파일, Run 키, 시작 프로그램 폴더, LaunchAgent, 예약 작업, 자기 삭제 | [Windows 조사 절차](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html), [macOS 악성 코드 흔적 분석](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/malware-triage/) |
| 4 | 파일 접근 로그 | 지갑·브라우저 파일을 어느 프로세스가 읽었나(로그를 켰을 때만) | 아래 "파일 접근 로그와 탐지 규칙" |
| 5 | 모아 둔 흔적 | 임시 폴더의 zip·스테이징 폴더 | [암호화폐 타임라인](../../03-techniques/analysis/timeline.md) |
| 6 | 메모리 | 디스크에 파일을 남기지 않는 악성 코드, 실행 중 프로세스 | [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/), [macOS 메모리 분석](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/memory-forensics/), [Linux 메모리 분석](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/memory-analysis.html) |
| 7 | 네트워크 기록 | C2 로 보낸 시각과 양 | [네트워크 타임라인](https://urock-ailab.github.io/forensics-handbook/network/03-techniques/analysis/timeline.html) |
| 8 | 지갑 앱 무결성 | Ledger Live·Trezor Suite 같은 호스트 앱이 바뀌었나 | [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md) |
| 9 | 블록체인 | 도난 뒤 빠져나간 거래, 받는 주소가 바뀌었나 | [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md), [비트코인 거래 따라가기](../../03-techniques/analysis/bitcoin-tracing.md), [이더리움 거래 따라가기](../../03-techniques/analysis/ethereum-tracing.md) |

## 분석 흐름

1. **피해 범위 후보를 정리합니다.** 계정·프로필마다 지갑 앱, 확장 ID, 키 파일 경로를 표로 정리합니다. Bitcoin Core 는 이름 있는 지갑이 `wallets\지갑이름\wallet.dat` 에 있고[15], Windows 기본 데이터 폴더가 28.0 부터 `AppData\Roaming\Bitcoin` 에서 `AppData\Local\Bitcoin` 으로 바뀌었지만 옛 폴더가 있으면 그대로 씁니다[16]. 두 곳을 다 봅니다.

2. **유입 시각을 찾습니다.** 메일 첨부, 브라우저 다운로드, 실행 창에 붙여 넣은 PowerShell 명령, 소프트웨어로 위장한 설치 파일, 개발 도구 패키지(NPM·VS Code 확장)가 후보입니다[1][3][5]. 가짜 CAPTCHA 는 사용자가 직접 실행 창을 열고 붙여 넣게 해서[1], 사용자가 스스로 실행한 흔적처럼 보입니다. 실행 창에 친 명령이 남는 곳은 [Windows 실행 창 명령 기록](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/execution/runmru.html)에 있습니다.

3. **실행·지속 흔적과 파일 접근 흔적을 시간순으로 합칩니다.** 유입 뒤 실행된 프로세스, 새로 생긴 지속 항목, 지갑 경로와 브라우저 자격 증명 파일에 접근한 기록을 한 타임라인에 올립니다. 파일 접근 로그가 없으면 이 단계는 실행 흔적과 모아 둔 흔적으로만 판단합니다.

4. **모아서 보냈을 가능성을 판단합니다.** 임시 폴더의 zip, 스테이징 폴더, 같은 시각대의 외부 전송을 찾습니다. BeaverTail 은 보낸 뒤 파일을 지워서[3] 파일 자체보다 파일 시스템 메타데이터나 삭제 기록에서 흔적이 나올 수 있습니다. LummaC2 는 C2 가 opcode 0 명령으로 경로(`p`)·확장자(`m`)·출력 폴더(`z`)를 지정할 수 있어서[1], 출력 폴더가 디스크에 생겼는지도 확인합니다.

5. **도난 가능 지갑의 주소를 뽑아 그 시각 뒤의 체인 거래를 확인합니다.** 주소를 뽑는 법은 각 지갑 아티팩트 페이지에, 자금 흐름은 [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md)에 있습니다.

6. **누가 서명한 거래인지 구분합니다.** 키가 샜다면 사용자가 모르는 시각에 사용자가 쓰지 않은 기기에서 서명한 거래가 나올 수 있습니다. 클립보드 바꿔치기라면 사용자가 보내려던 주소(메신저 대화, 송장, 거래소 입금 주소 화면)와 실제 트랜잭션의 받는 주소가 다릅니다. 지갑 앱 변조도 사용자가 서명한 거래의 내용이 바뀐 경우라서 같은 비교를 합니다. 피싱 사이트에서 서명을 받아 가는 드레이너는 [피싱 사이트에 서명했나](../fraud/wallet-drainer.md)에서 다룹니다.

## 파일 접근 로그와 탐지 규칙

공개 탐지 규칙 모음인 Sigma 에는 지갑과 브라우저 파일 접근을 찾는 규칙이 있고, 이 규칙이 보는 경로를 알면 로그에서 무엇을 찾을지 정할 수 있습니다. 반대로 규칙이 보지 않는 위치도 분명해집니다.

"Access To Crypto Currency Wallets By Uncommon Applications" 규칙(2024-07-29, 수준 medium)은 Kernel-File ETW 공급자의 파일 접근 로그를 봅니다[10]. 경로에 `\AppData\Roaming\Ethereum\keystore\`, `\AppData\Roaming\EthereumClassic\keystore\`, `\AppData\Roaming\monero\wallets\` 가 들어 있거나, 경로가 `\AppData\Roaming\` 아래 Bitcoin·BitcoinABC·BitcoinSV·DashCore·DogeCoin·Litecoin·Ripple·Zcash 폴더의 `wallet.dat` 으로 끝나면 걸립니다[10]. `System` 프로세스, `C:\Program Files`·`C:\Program Files (x86)`·`C:\Windows\system32`·`C:\Windows\SysWOW64` 에서 실행된 프로세스, Defender 프로세스는 뺍니다[10]. 백신, 백업 소프트웨어, C 드라이브가 아닌 곳에 설치한 정상 프로그램, everything.exe 같은 검색 프로그램이 오탐 원인으로 적혀 있습니다[10].

"Suspicious File Access to Browser Credential Storage" 규칙(2025-05-22, 실험 단계, 수준 low)은 브라우저가 아닌 프로세스가 40여 개 브라우저 폴더의 `\User Data` 나 `\Profiles\` 아래 `Login Data`·`Cookies`·`logins.json`·`key4.db` 같은 자격 증명 파일을 열 때 걸립니다[11]. 확장 지갑이 있는 `Local Extension Settings` 는 이 파일 목록에 없습니다[11]. 같은 내용을 Kernel-File ETW 로 보는 위협 헌팅 규칙[12]과, Security 로그 이벤트 4663(ObjectType `File`, AccessMask `0x1`)으로 보는 규칙도 있습니다[13]. `where.exe` 명령줄에 `places.sqlite`·`logins.json`·`key4.db`·`Login Data`·`Cookies` 같은 이름이 들어가면 걸리는 프로세스 생성 규칙도 있어서[14], 브라우저 파일을 찾는 명령 흔적은 프로세스 생성 로그에서도 볼 수 있습니다.

규칙에 걸리지 않았다고 접근이 없었다는 뜻은 아닙니다. 지갑 규칙의 Bitcoin Core 경로는 `AppData\Roaming\Bitcoin\wallet.dat` 으로 끝나야 해서 28.0 이후 새로 설치한 기본 위치(`AppData\Local\Bitcoin`)[16]와 이름 있는 지갑(`wallets\지갑이름\wallet.dat`)[15]은 빠집니다. Electrum·Exodus·Ledger Live 폴더와 브라우저 확장 저장소도 두 규칙 목록에 없습니다[10][11]. 이더리움 keystore 위치는 출처끼리 다릅니다. Sigma 규칙은 `\AppData\Roaming\Ethereum\keystore\` 를 보고[10], Web3 Secret Storage 문서는 Windows 위치를 `~/AppData/Web3/keystore` 로 적습니다[19]. 실제 기기에서 keystore JSON 파일이 있는 폴더를 찾아 그 경로로 로그를 검색합니다. 또 System32 같은 제외 폴더의 프로그램이 읽은 접근은 규칙 결과에 나오지 않으므로, 규칙 결과만 보지 말고 원래 로그를 지갑 경로로 직접 검색합니다.

## 증명하는 것과 증명하지 못하는 것

흔적이 있으면 아래를 증명할 수 있습니다.

- 파일 접근 로그: 특정 프로세스가 특정 시각에 지갑·브라우저 파일을 읽었다.
- 파일 시스템: 수집물 zip 이 만들어졌다.
- 네트워크 기록: 그 시각에 외부로 데이터를 보냈다.

악성 코드가 실행됐다는 것만으로는 지갑을 가져갔다고 할 수 없습니다. LummaC2·Raccoon 은 대상 목록을 C2 설정으로 받아서[1][7] 그 실행에서 무엇을 노렸는지는 설정이나 네트워크 기록이 있어야 알 수 있습니다. 볼트와 암호화된 `wallet.dat` 은 암호가 없으면 개인 키가 보이지 않아서, 파일을 읽었다는 것만으로 개인 키가 넘어갔다고 할 수도 없습니다. 반대로 키로거로 암호를 얻을 수 있어서, 암호화돼 있었다고 안전했다고 할 수도 없습니다[17]. 블록체인 거래로는 올바른 키로 서명됐다는 것만 알 수 있고, 누가 어느 기기에서 서명했는지는 알 수 없습니다.

## 시각 맞추기

유입·실행·파일 접근·전송 시각은 각 로그를 기록한 기기의 시계를 따르고, 도난 거래는 블록 시각을 따릅니다. 로그 원천마다 UTC 인지 현지 시각인지 확인해 모두 UTC 로 바꾼 뒤 한 타임라인에 올립니다. 블록 시각의 성질은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md), 기기 쪽 타임라인은 [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/)에 있습니다.

유입과 수집 사이 간격을 해석할 때는 악성 코드의 지연을 생각합니다. GlassWorm 은 실행을 15분 늦추므로[5] 설치 직후에 아무 일이 없었다고 무관하다고 볼 수 없습니다. LummaC2 는 C2 와 주고받지 않으면 파일을 만들지 않아서[1] 파일 시각이 아예 없을 수 있습니다.

## 흔한 오판

- **실행 파일 문자열에 지갑 경로가 없으니 지갑을 노리지 않았다.** LummaC2 는 확장·대상 목록을 C2 의 JSON 설정 `ex` 키로 받습니다[1]. Raccoon 도 설정 파일에 따라 수집합니다[7].
- **탐지 규칙 결과가 없으니 접근이 없었다.** 파일 접근 로그는 기본으로 남지 않고[10][12][13], 규칙이 보지 않는 지갑 위치와 제외 폴더가 있습니다.
- **수집물이 디스크에 없으니 보내지 않았다.** BeaverTail 은 보낸 뒤 지우고, LummaC2 는 자기 삭제할 수 있습니다[1][3].
- **지갑 파일이 암호화돼 있었으니 피해가 없다.** 키로거로 암호를 얻을 수 있습니다[17].
- **지갑 파일 접근 흔적이 없으니 악성 코드와 무관하다.** 클립보드 바꿔치기는 지갑 파일을 건드리지 않습니다[8][9].
- **하드웨어 지갑을 썼으니 안전했다.** 호스트 앱이 변조되면 서명 전 거래 내용이 바뀔 수 있습니다[5].
- **백신이나 백업 프로그램의 지갑 파일 접근을 악성 행위로 본다.** 규칙에도 오탐 원인으로 적혀 있습니다[10][11].

## 보고서 문장 예

아래 시각·경로·주소는 모두 만든 예시입니다.

- "사용자 계정 A 의 다운로드 폴더에 있던 `setup.exe` 가 2026-03-02 01:14:07 UTC 에 실행됐고, 같은 날 01:15:30 UTC 에 이 프로세스가 Chrome 기본 프로필의 `Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn\` 폴더 `.ldb` 파일을 읽은 기록이 Kernel-File ETW 로그에 있다. (만든 예시)"
- "이 기록으로 해당 프로세스가 MetaMask 저장소 파일을 읽었다는 것은 확인된다. 그 내용이 외부로 전송됐는지는 이 기간의 네트워크 기록이 없어 확인되지 않는다. (만든 예시)"
- "위 MetaMask 저장소에 있던 주소 A 에서 블록 시각 2026-03-02 03:40:12 UTC 에 주소 B 로 자산을 보낸 트랜잭션이 이더리움 블록체인에 있다. 이 트랜잭션을 서명한 기기가 어느 것인지는 체인 기록으로 확인되지 않는다. (만든 예시)"
- "메신저 대화에 적힌 받는 주소는 주소 C 인데, 같은 날 이 기기의 지갑이 보낸 트랜잭션의 받는 주소는 주소 D 다. (만든 예시)"

보고서 전체 구성은 [암호화폐 포렌식 보고서](../../03-techniques/reporting/forensic-report.md)에 있습니다.

## 함께 볼 페이지

- [이 기기로 지갑을 썼나](wallet-use.md) — 피해 범위 후보가 되는 지갑 목록을 만드는 순서
- [빼앗긴 자산은 어디로 갔나](../asset-flow/stolen-funds.md) — 도난 뒤 자금 흐름 추적
- [피싱 사이트에 서명했나](../fraud/wallet-drainer.md) — 사용자가 속아 서명한 경우
- [MetaMask](../../02-artifacts/browser/metamask/index.md), [다른 확장 지갑](../../02-artifacts/browser/other-extensions.md) — 확장 저장소의 구조
- [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md), [Electrum](../../02-artifacts/desktop/electrum.md), [Exodus](../../02-artifacts/desktop/exodus.md) — 데스크톱 지갑 파일 위치
- [주소 형식](../../01-foundations/wallets/address-formats.md) — 바뀐 주소를 비교할 때
- [macOS 정보 탈취 악성 코드](https://urock-ailab.github.io/forensics-handbook/mac/04-scenarios/incident/infostealer.html), [macOS 키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/)

## 참고 문헌

1. FBI·CISA, "Threat Actors Deploy LummaC2 Malware to Exfiltrate Sensitive Data from Organizations" (AA25-141B), 2025-05-21. https://www.cisa.gov/news-events/cybersecurity-advisories/aa25-141b
2. MITRE ATT&CK, Lumma Stealer (S1213). https://attack.mitre.org/software/S1213/
3. MITRE ATT&CK, BeaverTail (S1246). https://attack.mitre.org/software/S1246/
4. MITRE ATT&CK, InvisibleFerret (S1245). https://attack.mitre.org/software/S1245/
5. MITRE ATT&CK, GlassWorm (S9010). https://attack.mitre.org/software/S9010/
6. MITRE ATT&CK, RedLine Stealer (S1240). https://attack.mitre.org/software/S1240/
7. MITRE ATT&CK, Raccoon Stealer (S1148). https://attack.mitre.org/software/S1148/
8. MITRE ATT&CK, Clipboard Data (T1115). https://attack.mitre.org/techniques/T1115/
9. MITRE ATT&CK, Data Manipulation: Transmitted Data Manipulation (T1565.002). https://attack.mitre.org/techniques/T1565/002/
10. SigmaHQ, Access To Crypto Currency Wallets By Uncommon Applications. https://github.com/SigmaHQ/sigma/blob/master/rules/windows/file/file_access/file_access_win_susp_crypto_currency_wallets.yml
11. SigmaHQ, Suspicious File Access to Browser Credential Storage. https://github.com/SigmaHQ/sigma/blob/master/rules/windows/file/file_access/file_access_win_susp_process_access_browser_cred_files.yml
12. SigmaHQ, Access To Browser Credential Files By Uncommon Applications. https://github.com/SigmaHQ/sigma/blob/master/rules-threat-hunting/windows/file/file_access/file_access_win_browsers_credential.yml
13. SigmaHQ, Access To Browser Credential Files By Uncommon Applications - Security. https://github.com/SigmaHQ/sigma/blob/master/rules-threat-hunting/windows/builtin/security/win_security_file_access_browser_credential.yml
14. SigmaHQ, Suspicious Where Execution. https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_where_browser_data_recon.yml
15. Bitcoin Core, doc/files.md. https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
16. Bitcoin Core, 28.0 Release Notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
17. Bitcoin Core, doc/managing-wallets.md. https://github.com/bitcoin/bitcoin/blob/master/doc/managing-wallets.md
18. btcrecover, Extract Scripts. https://github.com/3rdIteration/btcrecover/blob/master/docs/Extract_Scripts.md
19. ethereum.org, Web3 Secret Storage Definition. https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/data-structures-and-encoding/web3-secret-storage/index.md
20. ESET Research, "DeceptiveDevelopment targets freelance developers", 2025-02-20. https://www.welivesecurity.com/en/eset-research/deceptivedevelopment-targets-freelance-developers/
