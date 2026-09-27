---
title: "조사 절차"
parent: "기법 · 조사 절차·수집"
nav_order: 260
---

# 조사 절차 (Investigation Process)

암호화폐 사건은 기기에 남은 지갑 흔적, 누구나 볼 수 있는 블록체인 원장, 거래소가 가진 계정 기록을 차례로 맞춰 보는 조사입니다. 지갑 흔적 가운데 일부는 앱을 잠그거나 끄면 몇 분 안에 메모리에서 사라지고, 증거 사본에서 지갑 앱을 실행하면 파일이 지워지거나 조사 중인 주소가 밖으로 나갈 수 있어서 수집 순서와 조회 수단을 미리 정해 둬야 합니다. 이 페이지는 현장 수집부터 원장 조회, 거래소 자료 요청까지의 순서와 단계마다 놓치기 쉬운 점을 다룹니다.

## 언제 쓰나

- 압수·임의 제출한 컴퓨터나 휴대폰에서 지갑 사용 여부를 확인하고, 거래 내역을 블록체인과 거래소 기록으로 뒷받침해야 할 때 씁니다.
- 수사 목표에 자산 압류가 들어 있을 때 씁니다. 다른 사람이 압류 전에 자금을 옮길 수 있어서 압류에 필요한 흔적을 찾는 일은 시간이 급하고, 행동 순서도 이 목표에 맞춰 정해야 합니다[1]. 압류·이전 자체의 법적·기술적 절차는 이 페이지에서 다루지 않고, 그 절차는 착수 전에 기관 방침에 따라 따로 정합니다[1].
- 기기 수집의 일반 원칙(쓰기 방지, 해시, 조치 기록)은 운영체제별 조사 절차 페이지와 같습니다. [Windows](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/process-acquisition/investigation-process.html)·[Mac](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/process-acquisition/investigation-process.html)·[Linux](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/investigation-process.html)·[Android](https://urock-ailab.github.io/forensics-handbook/android/03-techniques/acquisition/investigation-process.html)·[iOS](https://urock-ailab.github.io/forensics-handbook/ios/03-techniques/acquisition/investigation-process.html) 핸드북을 먼저 보고, 이 페이지는 암호화폐 때문에 달라지는 점만 봅니다.

## 절차

1. **켜진 기기는 켠 채로 둡니다.** 암호화폐 관련 증거가 있을 수 있는 기기를 켜진 상태로 발견하면 전원을 유지하고 잠기지 않게 합니다[1]. 휴대폰이 켜져 있고 잠금이 풀려 있으면 풀린 상태를 유지하거나, 분류 검사에 쓸 수 있게 잠금 암호·패턴을 확보합니다[1]. 기기를 끄거나 앱을 닫으면 암호화된 데이터에 접근하기 어려워지므로, 메모리·암호화 키·지갑 흔적처럼 실행 중일 때 가장 쉽게 얻는 것부터 수집합니다[1].

2. **현장에서 보이는 것을 기록합니다.** 암호화폐·암호화 관련 앱, 화면에 보이는 지갑 주소와 암호, 암호화 키, 지갑 설정·데이터 파일이 있는지 기록합니다[1]. 사용자 이름·암호·주소는 텍스트 파일, 이미지, 문서뿐 아니라 종이에도 있을 수 있어 주변 물건까지 살펴봅니다[1]. 복구 문구(seed phrase)와 개인 키는 자금을 옮기는 데 쓸 수 있으므로 권한 없는 사람이 볼 수 없게 기록·보관합니다[1]. 복구 문구의 구조는 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에 있습니다.

3. **하드웨어 지갑은 저장 장치처럼 다루지 않습니다.** 일부 하드웨어 지갑은 연결이 제대로 되지 않거나 쓰기 방지 장치 같은 읽기 전용 장치에 연결하면 초기화되므로, USB 저장 매체처럼 이미징하지 않습니다[1]. 하드웨어 지갑의 자금에 접근하려면 지갑 소프트웨어가 설치된 컴퓨터나 휴대폰도 함께 필요할 수 있어서, 현장에서 그 기기를 찾지 못하면 지갑의 존재 자체를 모르고 지나갈 수 있습니다[1]. 연결 기록과 연동 앱 흔적은 [하드웨어 지갑과 연결 흔적](../../02-artifacts/hardware/hardware-wallets.md)에 있습니다.

4. **메모리를 먼저 수집합니다.** 하드웨어 지갑 연동 앱의 메모리 흔적은 오래 남지 않습니다. Ledger Live 1.18.2 를 Windows 7 에서 Nano X(펌웨어 1.2.4)와 함께 쓴 시험에서는 앱을 잠그고 6분 뒤 확장 공개 키(extended public key) 14개와 명령 이벤트 1개만 남았고, 가장 많을 때는 각각 1,700개와 40개를 넘었습니다[3]. 같은 시험에서 프로세스를 끝내고 6분 안에 남은 흔적이 모두 덮어써져 분석 도구가 찾지 못했습니다[3]. 브라우저에서 쓰는 Trezor Wallet 은 탭을 닫은 뒤에도 확장 공개 키가 손상 없이 메모리에 남았고, Chrome 에서는 사용자가 정한 암호(passphrase)가 메모리의 같은 위치에 평문으로 남았다가 앱을 끄자 곧바로 덮어써졌습니다[3]. Trezor Bridge 는 사용자 Application Data 폴더의 로그에 USB 장치 연결 시각을 트레저가 아닌 장치까지 적고, 브리지가 실행 중인 동안 이 파일이 열려 있어 메모리 덤프에서 Volatility 의 `dumpfiles` 로 꺼낼 수 있습니다[3]. Monero CLI·GUI 0.18.3.4 는 CLI 를 끝내는 즉시 키를 담은 객체를 지우지만, GUI 를 닫은 뒤에도 지갑 암호가 메모리에 남아 있을 수 있습니다[4]. 메모리 수집과 분석 원리는 [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/), [Mac 메모리 분석](https://urock-ailab.github.io/forensics-handbook/mac/03-techniques/analysis/memory-forensics/), [Linux 메모리 수집](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/acquisition/memory-acquisition.html)에 있습니다.

5. **증거 사본에서 지갑 앱을 실행하지 않습니다.** 지갑 앱은 시작할 때 데이터를 바꿉니다. Ledger Live 데스크톱은 시작할 때 사용자 데이터 폴더에서 이름이 정규식 `^app\.json\..+$` 에 맞는 파일을 지웁니다[9]. Bitcoin Core 는 `-debug` 없이 시작하면 `debug.log` 가 11,000,000바이트를 넘을 때 마지막 10,000,000바이트만 남기고 앞부분을 잘라 냅니다[8]. MetaMask 의 기본 블록체인 제공자인 Infura 는 IP 주소와 지갑 주소를 수집한다고 방침에 밝혔고, 2023년에 시험한 브라우저 확장 지갑 100개 가운데 13개가 사용자 지갑 주소를 제3자에게 보냈습니다[5]. 압수한 기기에서 지갑 앱을 켜면 조사 중인 주소가 같은 경로로 밖에 알려질 가능성이 있습니다. 앱 화면을 꼭 봐야 하면 증거 사본을 한 번 더 복제해 네트워크와 끊은 환경에서 열고, 그 조치를 기록합니다.

6. **곁 파일까지 함께 수집합니다.** Bitcoin Core 의 `wallet.dat-journal` 은 `wallet.dat` 의 SQLite 롤백 저널로, 보통 시작할 때 생기고 종료할 때 지워지며 `wallet.dat` 만큼 안전하게 보관해야 합니다[7]. 복사하는 동안 지갑이 갱신되면 파일이 손상될 수 있어서 지갑 복사는 `backupwallet` 호출로 해야 합니다[7]. 그래서 실행 중인 시스템에서 파일만 떠 올 때는 어떤 방법으로 복사했는지 기록합니다. BRD(breadwallet) Android 앱의 `platform.db` 는 내용 전체가 WAL 파일에만 있는 경우가 있어 `-wal`·`-shm` 없이 읽으면 표에 행이 하나도 없습니다[11]. Electrum 은 지갑을 저장할 때 `경로.tmp.프로세스ID` 이름의 임시 파일에 먼저 쓰고 원래 파일과 바꿔서[10], 비정상 종료 뒤에는 이런 임시 파일이 남아 있을 가능성이 있습니다. 파일 형식은 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있습니다.

7. **휴대폰은 추출 방식별 차이를 적습니다.** Galaxy S9+(Android 8.0, SIM 없음)를 Cellebrite UFED Touch 2.0 으로 추출한 연구에서는 추출을 한 번에 하나씩만 할 수 있어 물리, 파일 시스템, 고급 논리 순서로 추출했습니다[6]. 루팅하지 않은 기기에서는 물리 추출이 실패했고, 비밀번호 파일 208개는 루팅한 기기의 물리 추출에서만 나왔습니다[6]. 클라우드 추출 도구는 거래소 앱 하나(Coinbase)만 지원했고, 로그인 정보와 2단계 인증 수단이 모두 있어야 했으며, 비트코인 거래 4건은 가져왔지만 Dogecoin 거래와 트랜잭션 ID 는 가져오지 못했습니다[6]. 앱별 흔적은 [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md)에 있습니다.

8. **찾을 값의 목록을 만들어 추출물 전체를 검색합니다.** 이미 알려진 트랜잭션 해시와 지갑 주소를 키워드로 정리해 두고 추출물 전체에서 검색하면, 지갑 앱이 캐시 폴더에 트랜잭션 해시를 파일 이름으로 남긴 경우까지 찾을 수 있습니다[6]. 앱 폴더를 찾는 방법은 [기기에서 지갑 흔적 찾기](artifact-search.md), 비할당 영역과 메모리에서 주소·TXID 를 뽑는 방법은 [주소와 트랜잭션 ID 찾기](address-carving.md)에 있습니다.

9. **원장 조회 수단을 정합니다.** 암호화폐 거래 조사가 포렌식으로 믿을 만하려면 완전성(Completeness), 무결성(Integrity), 기밀성(Confidentiality)을 갖춰야 한다고 BlockQuery 연구진은 제안합니다[2]. 완전성은 공개 키나 주소 하나로 그것을 쓴 트랜잭션을 모두 찾는 것이고, 무결성은 조회하는 원장이 네트워크가 합의한 원장과 같은 것이며, 기밀성은 어떤 거래를 조사하는지 뜻하지 않게 드러내지 않는 것입니다[2]. 제3자가 운영하는 조회 사이트를 쓰면 조사 중인 계정이 운영자에게 알려지고, 운영자는 수사기관 IP 주소와 조회한 지갑을 연결할 수 있습니다[2]. 응답이 틀리거나 빠지거나 오래됐을 수 있고, 이런 오류는 로컬 원장 사본과 비교해야만 알 수 있습니다[2]. 그래서 연구진은 자체 풀 노드(bitcoind)에 제3자 서버와 통신하지 않는 색인기(electrs)를 붙였는데, bitcoind 에는 주소 하나가 참여한 트랜잭션을 모두 돌려주는 API 가 없어서 색인기가 필요합니다[2]. Blockstream 의 Esplora API 는 서버를 직접 운영할 수 있고, 그러면 공개 서버를 쓸 때보다 개인정보 보호와 보안이 낫습니다[13]. Etherscan API 는 호출마다 쿼리 파라미터 `apikey` 에 자기 API 키를 넣어야 하므로[14], 조회 내역이 그 키에 묶인다는 점을 기록해 둡니다. 2022년 기준 비트코인 블록체인은 약 350 GB, 이더리움은 1 TB 에 가까워서, 자원이 부족한 기관은 주·연방 수사기관이나 대학처럼 믿을 수 있는 기관이 운영하는 조회 서비스를 쓰는 방법도 있습니다[2]. 조회 화면 읽는 법은 [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)에 있습니다.

10. **확장 공개 키는 조회 범위를 넓게 잡습니다.** 확장 공개 키 하나로 흩어진 주소를 한 지갑으로 묶을 수 있지만, 조회 범위가 좁으면 거래가 빠집니다. BIP-44 에서 지갑 소프트웨어는 연속으로 20개의 미사용 주소를 만나면 더 이상 쓴 주소가 없다고 보고 검색을 멈추며, 내부 체인(거스름돈, change 1)은 외부 체인(change 0)에서 온 코인만 받는다는 이유로 외부 체인만 검색합니다[12]. BIP-44 의 이 규칙은 지갑을 복구할 때 계정을 찾는 방법이고, BlockQuery 연구진은 조사에서 입출금 흐름을 모두 보려면 내부·외부 체인을 둘 다 조회해야 한다고 봅니다[2]. 간격 한도 20 을 따르지 않아도 유효한 주소를 만들 수 있고, 간격을 크게 벌리거나 아주 큰 인덱스에서 시작하면 한도를 가정한 도구는 그 주소를 찾지 못합니다[2]. 경로 하나에서 나올 수 있는 자식 주소는 2^31 개입니다[2]. 2022년 BlockQuery 연구진이 xpub 을 받는 공개 조회 도구 7개를 시험한 결과 6개가 xpub 에서 SegWit 주소를 자동으로 만들지 못했고, 로컬 원장을 조회할 수 있는 도구는 2개였습니다[2]. 메모리에서 공개 키가 한 가지 표현으로만 나와도 Legacy·Nested SegWit·Native SegWit 주소를 모두 만들어 조회합니다[2]. 파생 경로는 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md), 주소 형식은 [주소 형식](../../01-foundations/wallets/address-formats.md), 조회 범위를 보고서에 적는 방법은 [암호화폐 포렌식 보고서](../reporting/forensic-report.md)에 있습니다.

11. **거래소에 자료를 요청합니다.** 요청서에는 거래소가 계정을 바로 찾을 수 있는 값을 적습니다. Binance.US 에 TXID 로 요청할 때는 금액·입력 주소·출력 주소·UTC 시각을, 지갑 주소로 요청할 때는 TXID·UTC 시각·금액을 함께 적고, 요청서는 편집할 수 있는 형식으로 보냅니다[15]. 제공하는 기록은 고객확인(KYC) 정보, 잔액, 은행 계좌, 거래·입금·출금 내역, IP 내역, 기기 내역, 고객과 주고받은 연락입니다[15]. 몰수 대상이라고 믿을 상당한 이유가 있으면 동결을 요청할 수 있고, 검토 뒤 계정을 2주 동결할 수 있습니다[15]. Binance.US(BAM Trading)와 Binance(Binance Holdings)는 다른 회사라 서로의 기록이 없고, Binance.US Web3 Wallet 기록은 BAM Technology Services 앞으로 따로 요청합니다[15]. 국내 가상자산사업자는 고객확인자료와 송금인·수취인 정보를 금융거래 관계가 끝난 때부터 5년간 보존하고, 관계가 끝난 때는 고객과 가상자산거래로 생긴 채권채무관계를 정산한 날입니다[16]. 요청 시점이 이 기간 안인지 확인합니다. 사업자 제도는 [거래소와 가상자산사업자](../../01-foundations/ecosystem/exchanges.md), 회신 자료의 구조는 [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md)에 있습니다.

12. **기기 흔적, 원장, 거래소 기록을 서로 맞춰 봅니다.** 기기에서 찾은 트랜잭션 해시를 원장에서 조회해 입력·출력 주소와 시각을 확인하고, 추적 도구로 출처가 거래소임을 알아내면 그 거래소에 KYC 자료를 요청하는 영장으로 이어질 수 있습니다[6]. 이런 흔적이 곧바로 사람을 특정해 주지는 않지만, 잠복 감시나 위장 수사로 기록한 거래를 기기에서 나온 TXID 와 시각으로 뒷받침할 수 있습니다[6]. 원장 흐름을 따라가는 방법은 [비트코인 거래 따라가기](../analysis/bitcoin-tracing.md), 거래소 자료를 합치는 방법은 [거래소 자료 분석](../analysis/exchange-analysis.md)에 있습니다.

## 도구

- **bitcoind 와 electrs:** 자체 풀 노드와, 제3자 서버와 통신하지 않는 색인기입니다. BlockQuery 는 이 둘에 웹 앱을 붙인 오픈소스 조회 시스템이고, 파생 깊이와 내부·외부 체인 선택을 사용자가 정합니다[2].
- **Esplora:** 비트코인 블록 탐색기 API 로, 서버를 직접 운영할 수 있습니다[13].
- **LedgerHQ/xpub-scan:** xpub 하나로 세 주소 형식을 모두 만들고 인덱스 범위를 바꿀 수 있지만 Ledger 서버로 조회합니다[2].
- **Volatility 와 FORESHADOW:** FORESHADOW 는 Ledger Live·Trezor Wallet 의 메모리 구조를 찾는 Volatility 플러그인입니다[3].
- **iLEAPP·ALEAPP·RLEAPP:** 모바일 추출물과 제출 자료를 분석합니다. iLEAPP 는 fs(폴더)·zip·tar·gz·iTunes 백업·단일 파일을, ALEAPP·RLEAPP 는 zip·tar·fs·gz·raw 를 입력으로 받습니다[17]. RLEAPP 는 Coinbase 가 법 집행 기관에 낸 자료도 읽습니다[18].

## 함정과 한계

- **공개 조회 사이트를 그냥 쓰는 것:** 조사 대상이 운영자에게 알려지고, 응답이 맞는지 따로 확인할 수 없습니다[2].
- **조회 범위를 좁게 잡는 것:** 주소 형식 하나만 만들거나, 간격 한도 20 까지만 보거나, 외부 체인만 보면 거래가 빠집니다[2][12]. 이때 "거래가 없다" 는 결론은 조회한 범위 안에서만 맞습니다.
- **증거 사본에서 지갑 앱을 켜는 것:** 파일 삭제, 로그 잘림, 외부 통신이 생깁니다[5][8][9].
- **메모리 수집을 미루는 것:** Ledger Live 시험에서는 잠금이나 종료 뒤 몇 분 안에 흔적이 사라졌습니다[3]. Monero 지갑을 복원(restore)하면 캐시 파일에 복원 높이 이후 거래만 들어가서 그 전 기록이 없을 수 있습니다[4].
- **추출 방식 하나에 기대는 것:** 루팅하지 않은 Android 는 물리 추출이 실패했고, 클라우드 추출은 지원 앱이 적고 로그인 정보와 2단계 인증이 필요했습니다[6].
- **같은 상표를 한 회사로 보는 것:** Binance.US 와 Binance, Binance.US Web3 Wallet 은 요청할 곳이 다릅니다[15].
- **UTXO 를 거스름돈으로 이해하는 것:** UTXO 는 아직 쓰지 않은 트랜잭션 출력이고, 트랜잭션에 넣은 UTXO 는 전액을 쓰거나 수수료로 내야 합니다[19]. 그래서 대부분의 트랜잭션에는 남는 금액을 보낸 사람에게 돌려주는 거스름돈 출력(change output)이 따로 있습니다[19]. 자세한 내용은 [비트코인의 UTXO](../../01-foundations/blockchain/utxo.md)에 있습니다.

## 결과를 어떻게 해석하나

기기 흔적, 원장 기록, 거래소 기록이 맞물리면 "이 기기의 지갑 데이터에 이 주소가 있고, 이 주소가 관여한 트랜잭션이 블록체인에 있으며, 거래소가 이 계정 명의로 같은 거래를 기록했다" 까지 쓸 수 있습니다.

원장만으로는 사람을 특정하지 못합니다. 한 연구에서 기기의 트랜잭션에 나온 주소 하나는 2021년 7월 기준 1,361번 거래하고 1억 달러 넘게 주고받은 주소라 그 기기 사용자만의 주소가 아니었습니다[6]. 추적 도구는 출처를 거래소로 지목해도 그 결론에 이른 방법을 보여 주지 않아서, 영장 같은 사법 허가를 청구할 때 정확성의 근거를 대기 어려울 수 있습니다[6]. 조회 도구가 만들지 않은 주소 형식이나 간격 밖의 주소에 거래가 더 있을 수 있고[2], 거래소는 제출 기록의 정확성과 완전성을 보증하지 않으며 나중에 정보가 새로 생겨도 회신을 고칠 의무가 없습니다[15]. 그래서 거래소 기록은 원장과 기기 흔적으로 다시 확인합니다.

시각은 출처마다 기준이 다릅니다. 거래소에 요청할 때는 UTC 로 적습니다[15]. Coinbase 회신 자료(`compliance_report.csv`)의 시각에는 오프셋(-0800, Z)이나 시간대 약어가 붙기도 하고 아무 표시가 없기도 해서, RLEAPP 는 표시가 있을 때만 UTC 로 바꾸고 없으면 그대로 둡니다[18]. 한 연구의 표에서는 같은 트랜잭션 해시가 UTC 로 2021년 6월 14일 03:14, 기기 파일 경로 표에서는 기준을 밝히지 않은 채 6월 13일 23:15 로 적혀 약 4시간 차이가 납니다[6]. 이렇게 기준이 빠지면 같은 거래가 다른 날짜로 보이므로 시각마다 UTC·현지 시각·기기 시계 가운데 무엇인지 함께 적습니다. 블록 시각과 기기 시각의 차이는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md), 여러 출처의 시각을 합치는 방법은 [암호화폐 타임라인](../analysis/timeline.md)에 있습니다.

## 참고 문헌

1. SWGDE, "Tech Notes on Cryptocurrency", 23-F-006-1.1, Version 1.1, 2024-12-09. https://www.swgde.org/wp-content/uploads/2025/01/2024-12-09-Tech-Notes-on-Cryptocurrency-23-F-006-1.1.pdf
2. Tyler Thomas, Tiffanie Edwards, Ibrahim Baggili, "BlockQuery: Toward forensically sound cryptocurrency investigation", Forensic Science International: Digital Investigation 40, 2022. doi:10.1016/j.fsidi.2022.301340
3. Tyler Thomas, Mathew Piscitelli, Ilya Shavrov, Ibrahim Baggili, "Memory FORESHADOW: Memory FOREnSics of HArDware CryptOcurrency wallets – A Tool and Visualization Framework", Forensic Science International: Digital Investigation 33, 2020. doi:10.1016/j.fsidi.2020.301002
4. Jeongin Lee, Geunyeong Choi, Jihyo Han, Jungheum Park, "Advanced Monero wallet forensics: Demystifying off-chain artifacts to trace privacy-preserving cryptocurrency transactions", Forensic Science International: Digital Investigation 54, 2025. doi:10.1016/j.fsidi.2025.301988
5. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, "Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3", arXiv, 2023. doi:10.48550/arXiv.2306.08170
6. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, "Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications", arXiv, 2022. doi:10.48550/arXiv.2205.14611
7. Bitcoin Core, doc/files.md. https://github.com/bitcoin/bitcoin/blob/master/doc/files.md
8. Bitcoin Core, src/logging.cpp · src/init/common.cpp. https://github.com/bitcoin/bitcoin/blob/master/src/logging.cpp , https://github.com/bitcoin/bitcoin/blob/master/src/init/common.cpp
9. Ledger Live Desktop, src/main/index.ts · src/main/cleanupUserData.ts. https://github.com/LedgerHQ/ledger-live/blob/develop/apps/ledger-live-desktop/src/main/index.ts
10. Electrum, electrum/storage.py. https://github.com/spesmilo/electrum/blob/master/electrum/storage.py
11. ALEAPP, scripts/artifacts/breadWallet.py. https://github.com/abrignoni/ALEAPP/blob/main/scripts/artifacts/breadWallet.py
12. BIP 44, Multi-Account Hierarchy for Deterministic Wallets. https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
13. Blockstream, Esplora HTTP REST API. https://github.com/Blockstream/esplora/blob/master/API.md
14. Etherscan API, Get Normal Transactions By Address (txlist). https://docs.etherscan.io/api-reference/endpoint/txlist.md
15. Binance.US, Law Enforcement Guide. https://support.binance.us/en/articles/9842980-binance-us-law-enforcement-guide
16. 특정 금융거래정보의 보고 및 이용 등에 관한 법률 제5조의4. https://www.law.go.kr/법령/특정금융거래정보의보고및이용등에관한법률
17. iLEAPP·ALEAPP·RLEAPP, README.md. https://github.com/abrignoni/iLEAPP/blob/main/README.md , https://github.com/abrignoni/ALEAPP/blob/main/README.md , https://github.com/abrignoni/RLEAPP/blob/main/README.md
18. RLEAPP, scripts/artifacts/coinbaseComplianceReport.py. https://github.com/abrignoni/RLEAPP/blob/main/scripts/artifacts/coinbaseComplianceReport.py
19. Bitcoin Developer Guide, Transactions. https://developer.bitcoin.org/devguide/transactions.html
