---
title: "주소와 트랜잭션 ID 찾기"
parent: "기법 · 조사 절차·수집"
nav_order: 280
---

# 주소와 트랜잭션 ID 찾기 (Address·TXID Carving)

지갑 앱의 데이터베이스를 해석하지 못하거나 파일이 지워져 비할당 영역에 조각만 남았을 때는, 디스크·메모리 이미지에서 주소와 트랜잭션 ID(TXID) 모양의 문자열을 직접 찾습니다. 정규식으로 후보를 모으고, 체크섬으로 오탐을 걸러 내고, 앞뒤 문맥으로 그 값이 무엇인지 정한 다음 블록체인에서 조회하는 순서로 진행합니다. 이 페이지는 비트코인·이더리움 계열에서 이 과정을 밟을 때 알아야 할 문자열 모양, 바이트 순서, 도구의 기본 동작과 한계를 다룹니다.

## 언제 쓰나

- 지갑 앱이 무엇인지 모르거나, 앱 형식을 해석하는 도구가 없을 때 씁니다. 앱별 저장 위치를 먼저 보는 방법은 [기기에서 지갑 흔적 찾기](artifact-search.md)에 있고, 이 페이지는 그 다음 단계이거나 그것으로 찾지 못한 부분을 메우는 방법입니다.
- 지운 파일, 잘려 나간 로그, 페이지 파일, 메모리 덤프처럼 파일 구조가 온전하지 않은 곳에서 값을 건져야 할 때 씁니다. Bitcoin Core 는 `-debug` 없이 시작하면 `debug.log` 가 약 11 MB(11 × 1,000,000 바이트)를 넘을 때 마지막 10,000,000 바이트만 남기고 줄입니다[15]. 잘려 나간 앞부분은 비할당 영역에 남아 있을 가능성이 있습니다.
- 사건에서 이미 알려진 주소·TXID 가 있을 때, 그 값이 이 기기에 있었는지 확인하려고 씁니다. 수집을 준비하면서 거래 해시와 지갑 주소를 검색어로 적어 두면, 추출물 전체를 그 값으로 검색할 수 있습니다[24].

## 절차

1. **검색할 범위를 정하고 사본에서 작업합니다.** 파일 단위(지갑 폴더, 앱 데이터베이스와 `-wal`·`-journal` 같은 곁 파일, 로그), 이미지 전체(비할당 영역 포함), 메모리 덤프를 따로 검색합니다. 값이 어디서 나왔는지에 따라 해석이 달라지므로 결과도 따로 둡니다. 증거 사본에서 지갑 앱을 실행하면 로그가 줄어드는 등 원본이 바뀔 수 있으니, 수집 순서와 주의점은 [조사 절차](investigation-process.md)를 따릅니다.

2. **ASCII 와 UTF-16 두 가지로 문자열을 뽑습니다.** 같은 주소라도 앱에 따라 1바이트 문자(ASCII·UTF-8)나 UTF-16 으로 저장되고, UTF-16 으로 저장된 주소는 바이트 그대로 정규식을 걸면 한 글자마다 `00` 이 끼어 있어 맞지 않습니다. 아래는 EIP-55 명세의 시험 벡터 `0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed`[5] 앞 네 글자를 두 인코딩으로 바꾼 값입니다(명세 값을 인코딩 규칙대로 바꾼 예).

   ```text
   ASCII      30 78 35 61
   UTF-16LE   30 00 78 00 35 00 61 00
   ```

   bstrings 는 기본으로 ASCII(코드 페이지 1252, `0x20`~`0x7E`)와 유니코드 문자열을 둘 다 뽑고, 최소 길이는 3자, 한 번에 읽는 크기는 512 MB 입니다[18]. `--off` 를 주면 문자열마다 오프셋과 인코딩(A=1252, U=Unicode)을 붙여 주고, `--ro` 를 켜야 정규식에 맞은 부분만 출력하며, 끄면 그 부분이 들어 있는 문자열 전체를 출력합니다[18]. 두 옵션 모두 기본값은 꺼짐입니다[18].

3. **정규식으로 후보를 모읍니다.** 아래 표는 명세의 문자 집합과 길이로 만든 예입니다. BIP-84·BIP-86 의 메인넷 주소 시험 벡터[26][27], BIP-173 의 메인넷 v0 주소 시험 벡터[1], EIP-55 시험 벡터[5], BIP-32 시험 벡터의 xpub[3] 은 각각 이 패턴 가운데 하나에만 맞습니다. 세그윗 패턴은 증인 버전 0·1 의 표준 길이 주소만 잡아서, 명세 시험 벡터에 있는 v2~v16 주소나 길이가 다른 v1 주소, 테스트넷 `tb1` 주소는 잡지 않습니다[1][2]. 문자 집합과 길이의 근거는 [주소 형식](../../01-foundations/wallets/address-formats.md)과 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에 있습니다.

   | 찾는 값 | 정규식 (명세로 만든 예) | 근거 |
   |---|---|---|
   | 비트코인 Base58 주소 (`1`·`3`) | `\b[13][1-9A-HJ-NP-Za-km-z]{25,34}\b` (대소문자 구분) | Base58 문자표 |
   | 비트코인 세그윗 주소 (`bc1q`·`bc1p`) | `\bbc1[qp][02-9ac-hj-np-z]{38}\b`, `\bbc1[qp][02-9ac-hj-np-z]{58}\b` 와 같은 패턴의 전부 대문자판 | 데이터 부분은 `1`·`b`·`i`·`o` 를 뺀 영숫자, 전체 최대 90자[1] |
   | 이더리움 주소 | `\b0x[0-9a-fA-F]{40}\b` | 20바이트 |
   | ABI 인자·로그 토픽 안의 이더리움 주소 | `0{24}[0-9a-fA-F]{40}` | 앞을 0 으로 채운 32바이트 워드[6][8] |
   | 32바이트 해시 (TXID·블록 해시·이더리움 트랜잭션 해시) | `\b(0x)?[0-9a-fA-F]{64}\b` | 32바이트 = 헥스 64자[7][10] |
   | 확장 공개 키 | `\b[xyztuvYZUV]pub[1-9A-HJ-NP-Za-km-z]{107}\b` | 정확히 111자[3], 접두사 목록[4] |

   세그윗 주소는 인코더가 소문자로 내놓지만 QR 코드 안에서는 대문자를 쓰도록 권하므로[1] 대문자판도 함께 찾습니다. 이더리움 컨트랙트 호출 데이터는 4바이트 함수 선택자 뒤에 인자가 32바이트 워드로 이어지고, 주소 같은 정수 값은 앞을 0 으로 채워 넣습니다[6]. 로그의 `topics` 도 32바이트 값이라 주소가 앞에 0 24자를 달고 들어갑니다[8]. 그래서 `0x` 와 40자를 찾는 패턴만 쓰면 이 주소들을 놓칩니다. 구조는 [이더리움의 계정과 로그](../../01-foundations/blockchain/ethereum-accounts.md)에 있습니다. 문자열이 JSON 안에 다시 JSON 문자열로 들어 있는 경우도 있습니다. MetaMask iOS 앱의 `persist-root` 는 `engine` 필드 값이 JSON 문자열이라 두 번 풀어야 안의 계정·트랜잭션 값이 나옵니다[21]. 카빙한 조각에서는 따옴표가 `\"` 로 이스케이프된 상태로 보입니다.

4. **알고 있는 값은 여러 모양으로 바꿔 검색합니다.** 비트코인 블록·트랜잭션 안의 해시는 내부 바이트 순서(internal byte order)로 들어 있고, Bitcoin Core RPC 와 많은 블록 탐색기는 바이트를 뒤집은 RPC 바이트 순서(RPC byte order)로 표시합니다[9]. 원시 트랜잭션의 outpoint TXID 도 내부 바이트 순서입니다[10]. 그래서 탐색기에서 가져온 TXID 로 원시 바이트(블록 파일, 원시 트랜잭션, 메모리)를 검색할 때는 헥스 문자열을 바이트로 바꾼 값과 그것을 뒤집은 값을 모두 검색합니다. 반대로 원시 바이트에서 떼어 낸 32바이트는 뒤집어서 탐색기에 넣습니다. 뒤집는 예는 [블록과 트랜잭션](../../01-foundations/blockchain/blocks-transactions.md)과 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에 있습니다. 같은 주소도 저장된 곳마다 대소문자가 다를 수 있습니다. iOS Coinbase Wallet 앱은 MMKV 키에 들어가는 계정의 주 주소를 대문자로 바꿔 저장해서, 같은 주소가 앱의 다른 곳과 대소문자가 다르게 나옵니다[20]. 그래서 주소는 대소문자를 무시하고 찾습니다. 웹 페이지와 제3자 스크립트는 지갑 주소를 인코딩하거나 해시해서 요청·쿠키에 싣기도 합니다[23]. 알려진 주소가 있으면 Base64·URL 인코딩·LZString 같은 인코딩과 MD5·SHA256·MurmurHash3 같은 해시로 미리 바꾼 값의 집합을 만들고, 쿠키·HTTP 요청·WebSocket 본문을 `=`·`&` 같은 구분 문자로 잘라 그 집합과 비교합니다. 이 비교는 인코딩·디코딩을 3단계까지 되풀이합니다[23].

5. **체크섬으로 후보를 거릅니다.** Base58Check 주소와 확장 키는 뒤 4바이트 체크섬을, Bech32·Bech32m 주소는 BCH 체크섬을 계산합니다. 계산 방법은 [주소 형식](../../01-foundations/wallets/address-formats.md)에 있습니다. 세그윗 주소는 증인 버전 0 이면 Bech32(상수 1), 1~16 이면 Bech32m(상수 `0x2bc830a3`)으로 맞아야 하고, 디코딩한 증인 버전과 인코딩이 어긋나면 무효입니다[2]. 이더리움 주소의 EIP-55 체크섬은 헥스 글자(`a`~`f`)를 대문자로 쓸지 소문자로 쓸지로 나타내고, 무작위로 만든 주소를 잘못 입력했을 때 우연히 체크섬을 통과할 확률은 0.0247% 입니다[5]. 그래서 대소문자가 섞인 주소는 체크섬으로 거를 수 있습니다. 전부 소문자이거나 전부 대문자인 주소는 체크섬 없이 저장된 것일 수 있어서, 체크섬이 맞지 않는다고 틀린 주소로 버리지 않습니다. 명세 시험 벡터에도 체크섬을 적용한 결과가 전부 대문자나 전부 소문자가 된 주소가 있습니다[5]. 검증기를 실제 데이터에 쓰기 전에 명세의 시험 벡터로 먼저 돌려 봅니다. 예를 들어 BIP-173 시험 벡터 `BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4` 는 유효한 주소로 나와야 합니다[1].

6. **앞뒤 문맥으로 값의 뜻을 정합니다.** 헥스 64자는 모양만으로 TXID, 블록 해시, 이더리움 트랜잭션 해시, 로그 토픽, 개인 키 중 무엇인지 알 수 없습니다[7][8][28]. 그래서 같은 레코드의 필드 이름(`transactionHash`·`hash` 등), 파일 이름, 로그 문구로 판단합니다. Bitcoin Core `debug.log` 의 지갑 줄은 `[지갑이름] AddToWallet TXID 상태 트랜잭션상태` 형식이고, 상태 자리에는 `new`·`update`·`new, update`·`no-change` 중 하나가 들어갑니다[14]. 이 TXID 는 Bitcoin Core 가 바이트를 뒤집어 헥스로 만든 값이라[11] 탐색기에 그대로 넣을 수 있습니다. 개인 키일 수 있는 값(헥스 64자, WIF, 확장 개인 키)은 위치만 기록하고 값을 결과표나 보고서에 옮기지 않습니다. 주소와 헷갈리는 문자열 목록은 [주소 형식](../../01-foundations/wallets/address-formats.md)에 있습니다.

7. **중복을 정리하고 출처를 적습니다.** 한 앱 안에서도 같은 주소가 여러 번 나옵니다. iOS Coinbase Wallet 앱은 한 주소를 여러 자산 아래에서 파생해 저장해서, iOS 16.5 시험 이미지 하나의 주소 테이블은 491행에 고유 주소가 270개였습니다[20]. 결과표에는 값마다 파일 경로(또는 이미지 오프셋), 인코딩, 문맥, 체크섬 결과를 적고, 개수는 중복을 뺀 값으로 셉니다.

8. **체인에서 조회합니다.** 체크섬을 통과한 주소·TXID 만 조회합니다. 공개 조회 서비스에 넣으면 어떤 주소를 조사하는지 운영자에게 드러나므로[25] 자체 노드나 자체 호스팅한 색인기로 조회합니다. 조회 방식과 기록할 항목은 [조사 절차](investigation-process.md)에 있습니다. Esplora API 는 `GET /address-prefix/:prefix` 로 접두사가 같은 주소를 최대 10개까지 찾아 주므로[17], 뒷부분이 깨진 주소 조각의 후보를 좁힐 때 자체 호스팅 서버에서 쓸 수 있습니다. 주소의 확정 거래 목록은 한 번에 25건씩 오고, 마지막으로 본 txid 를 넘겨야 다음 목록이 옵니다[17]. 목록 끝까지 받았는지 확인합니다.

## 도구

- **bstrings 와 KAPE 모듈:** KAPE 의 `bstrings_CryptoWallets` 묶음은 Aeon·BitCoin·ByteCoin·DashCoin(두 가지)·FantomCoin·Monero·SumoKoin 모듈을 차례로 돌립니다[19]. 각 모듈은 `bstrings.exe -d 원본폴더 -o 출력폴더 --lr 이름` 형식으로 내장 정규식 하나를 쓰고, `--ro`·`--off` 를 주지 않습니다[19]. 그래서 결과에는 주소가 들어 있는 문자열 전체가 나오고 오프셋은 나오지 않습니다. bstrings 는 내장 정규식이든 `--lr`·`--fr` 로 넘긴 정규식이든 모두 `RegexOptions.IgnoreCase` 로 컴파일합니다[18]. 그래서 `bitcoin` 정규식 `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b`[18] 은 대소문자를 무시하고, Base58 에서 빠지는 `I`·`O`·`l` 이 든 문자열에도 맞습니다. `bc1` 주소와 이더리움 주소 정규식은 내장되어 있지 않아서 3단계의 패턴을 `--lr` 이나 `--fr` 로 따로 넘기는데[18], 이때도 대소문자 구분이 사라지므로 5단계의 체크섬 검증을 거칩니다.
- **YARA 와 Volatility:** 메모리에서는 FORESHADOW(Volatility 플러그인)가 YARA 정규식 검색으로 Ledger Live·Trezor Wallet 의 JSON 구조를 찾고, 정해진 구조 밖에 흩어진 확장 공개 키까지 마지막 정규식 검색으로 모읍니다[22]. 지갑 주소는 API 요청 URL 의 파라미터로 메모리에 많이 남아 있어서, 깨진 구조를 복원하지 않아도 꾸준히 복구됐습니다[22]. MultiBit 클라이언트의 macOS 메모리 덤프에서 비트코인 키와 주소를 정규식으로 찾는 Volatility 플러그인(Gurkok, 2015)도 있습니다[22]. 메모리 분석 일반은 [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)을 봅니다.
- **체크섬 검증 구현:** BIP-173 이 링크한 `sipa/bech32` 참조 구현[1], EIP-55 명세 안의 Python·JavaScript 코드[5]로 검증합니다.
- **Esplora 자체 호스팅:** 공개 인스턴스도 있지만 직접 호스팅하면 개인정보 보호와 보안이 더 낫습니다[17].

## 함정과 한계

- **Bitcoin Core 28.0 이후 블록 파일은 원시 바이트로 검색되지 않습니다.** 블록 파일은 기본으로 XOR 처리되고 키는 blocksdir 의 `xor.dat` 에 있습니다[12][13]. 28.0 이전에 만든 파일이나 키가 0 인 파일에서만 트랜잭션 바이트가 그대로 보입니다. 자세한 내용은 [블록과 트랜잭션](../../01-foundations/blockchain/blocks-transactions.md)에 있습니다.
- **압축된 저장소는 이미지 전체 문자열 검색에 잘 걸리지 않습니다.** 브라우저 확장 지갑이 쓰는 LevelDB 는 블록을 압축해 저장하므로, 그 파일은 앱 형식으로 풀어서 다시 검색합니다. 형식은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)를 봅니다.
- **TXID 바이트 순서를 한 가지만 검색합니다.** 원시 바이트에는 내부 바이트 순서로, 사람이 읽는 출력에는 뒤집은 순서로 들어 있습니다[9][10][11]. 한 방향만 검색하면 있는 값을 없다고 판단하게 됩니다.
- **접두사만으로 코인을 정하지 않습니다.** 그로스톨코인은 비트코인과 같은 `xpub`·`ypub`·`zpub` 을 쓰고, `vpub` 은 비트코인 테스트넷과 카일라코인 테스트넷이 같이 쓰며, 넥사 테스트넷도 `xpub` 을 씁니다[4]. 확장 키 식별자(Hash160)는 옛 비트코인 주소에 들어가는 데이터와 같아서, Base58 로 표시된 식별자는 주소로 오해할 수 있습니다[3].
- **정규식 결과는 후보일 뿐입니다.** 패턴에 맞아도 체크섬을 통과하지 못하면 주소로 쓰지 않습니다. 조각난 주소는 체크섬이 맞지 않으므로, 접두사 조회로 후보를 찾았더라도 보고서에는 "조각" 이라고 적습니다.
- **평문 검색만으로는 인코딩·해시된 주소를 찾지 못합니다.** 웹 쪽 흔적(쿠키, 캐시된 요청)에는 주소가 인코딩되거나 해시된 채 남을 수 있습니다[23]. 해시된 값은 알고 있는 주소가 있어야만 대조할 수 있습니다.

## 결과를 어떻게 해석하나

**증명하는 것.** 이 이미지의 이 파일(또는 이 오프셋)에 이 문자열이 있었다는 것은 확인됩니다. 체크섬을 통과하면 형식상 유효한 주소나 키이고, 체인에서 조회되면 그 주소·TXID 가 실제 거래에 쓰였다는 것까지 말할 수 있습니다. 보고서 문장은 "이 이미지의 비할당 영역 오프셋 0x… 에 체크섬이 맞는 비트코인 주소가 UTF-16 으로 있고, 이 주소가 관여한 트랜잭션이 블록체인에 있다" 처럼 씁니다.

**증명하지 못하는 것.** 카빙한 주소가 이 사용자의 것이라는 것은 증명하지 못합니다. Coinbase 의 송금 알림 메일 제목에도 받는 주소가 들어가고[24], 웹 페이지와 제3자 스크립트도 지갑 주소를 요청·쿠키에 실어 보냅니다[23]. 주소 하나가 여러 사람의 거래에 쓰일 수도 있습니다. Android 지갑 앱 시험에서 쓴 거래의 출력 주소 하나는 2021년 7월까지 1,361번 거래한 주소였습니다[24]. TXID 는 해시일 뿐이라 보냈는지 받았는지는 체인 기록과 지갑 데이터로 따로 확인해야 하고, 비할당 영역 조각은 어느 파일·앱에서 왔는지 모를 수 있습니다. 주소를 묶어 주체를 추정하는 방법과 한계는 [주소 묶기와 그 한계](../analysis/clustering.md)에 있습니다.

**시각.** 카빙한 문자열에는 시각이 없습니다. 시각은 같은 레코드 안의 필드, 파일 시스템 시각, 체인의 블록 시각에서 따로 가져오고 어느 것을 썼는지 적습니다. Bitcoin Core `debug.log` 는 기본으로 줄마다 `YYYY-MM-DDThh:mm:ssZ` 형식의 UTC 시각(초 단위)을 붙입니다[15][16]. Esplora 의 트랜잭션 상태에 있는 `block_time` 은 확정된 트랜잭션에만 있고 미확정이면 `null` 입니다[17]. 블록 시각의 기준은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에, 여러 출처의 시각을 합치는 방법은 [암호화폐 타임라인](../analysis/timeline.md)에 있습니다.

## 참고 문헌

1. BIP-173, "Base32 address format for native v0-16 witness outputs". https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
2. BIP-350, "Bech32m format for v1+ witness addresses". https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki
3. BIP-32, "Hierarchical Deterministic Wallets". https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
4. SLIP-0132, "Registered HD version bytes for BIP-0032". https://github.com/satoshilabs/slips/blob/master/slip-0132.md
5. EIP-55, "Mixed-case checksum address encoding". https://eips.ethereum.org/EIPS/eip-55
6. ethereum.org, "Transactions". https://ethereum.org/en/developers/docs/transactions/
7. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
8. Etherscan API, "getLogs". https://docs.etherscan.io/api-reference/endpoint/getlogs.md
9. Bitcoin Developer Glossary, "Internal byte order", "RPC byte order". https://developer.bitcoin.org/glossary.html
10. Bitcoin Developer Reference, "Transactions". https://developer.bitcoin.org/reference/transactions.html
11. Bitcoin Core, `src/uint256.cpp`. https://github.com/bitcoin/bitcoin/blob/master/src/uint256.cpp
12. Bitcoin Core 28.0 Release Notes. https://github.com/bitcoin/bitcoin/blob/master/doc/release-notes/release-notes-28.0.md
13. Bitcoin Core, `doc/files.md`. https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
14. Bitcoin Core, `src/wallet/wallet.cpp`, `src/wallet/wallet.h`. https://github.com/bitcoin/bitcoin/blob/master/src/wallet/wallet.cpp
15. Bitcoin Core, `src/logging.cpp`, `src/logging.h`, `src/init/common.cpp`. https://github.com/bitcoin/bitcoin/blob/master/src/logging.cpp , https://github.com/bitcoin/bitcoin/blob/master/src/logging.h , https://github.com/bitcoin/bitcoin/blob/master/src/init/common.cpp
16. Bitcoin Core, `src/util/time.cpp`. https://github.com/bitcoin/bitcoin/blob/master/src/util/time.cpp
17. Blockstream Esplora, "HTTP REST API". https://github.com/Blockstream/esplora/blob/master/API.md
18. bstrings, `bstrings/Program.cs`. https://github.com/EricZimmerman/bstrings/blob/master/bstrings/Program.cs
19. KapeFiles, `Modules/Compound/bstrings_CryptoWallets.mkape`, `Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape`. https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/Compound/bstrings_CryptoWallets.mkape , https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape
20. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
21. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
22. Tyler Thomas, Mathew Piscitelli, Ilya Shavrov, Ibrahim Baggili, 「Memory FORESHADOW: Memory FOREnSics of HArDware CryptOcurrency wallets – A Tool and Visualization Framework」, Forensic Science International: Digital Investigation 33, 2020, doi:10.1016/j.fsidi.2020.301002
23. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, 「Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3」, arXiv, 2023, doi:10.48550/arXiv.2306.08170
24. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, 「Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications」, arXiv, 2022, doi:10.48550/arXiv.2205.14611
25. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, 「BlockQuery: Toward forensically sound cryptocurrency investigation」, Forensic Science International: Digital Investigation 40, 2022, doi:10.1016/j.fsidi.2022.301340
26. BIP-84, "Derivation scheme for P2WPKH based accounts". https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki
27. BIP-86, "Key Derivation for Single Key P2TR Outputs". https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki
28. ethereum.org, "Ethereum accounts". https://ethereum.org/en/developers/docs/accounts/
