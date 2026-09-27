---
title: "주소 형식"
parent: "기반 · 지갑과 키"
nav_order: 60
---

# 주소 형식 (Address Formats)

암호화폐 주소는 공개 키나 스크립트의 해시에 네트워크 표시와 체크섬을 붙여 글자로 바꾼 값입니다. 모양만 보고도 어느 체인의 어떤 네트워크(메인넷·테스트넷)인지, 비트코인이라면 어떤 스크립트 종류인지 알 수 있고, 체크섬을 계산하면 디스크나 메모리에서 찾은 문자열이 진짜 주소인지 확인할 수 있습니다. 이 페이지는 비트코인의 Base58Check·Bech32·Bech32m 주소와 이더리움 주소의 구조, 주소와 헷갈리기 쉬운 문자열을 구분하는 법을 다룹니다.

## 이 형식을 쓰는 아티팩트

주소는 지갑 파일, 지갑·거래소 앱의 데이터베이스와 설정 파일, 거래소가 내주는 입출금 기록, 블록 탐색기 화면처럼 암호화폐가 닿는 거의 모든 곳에 문자열로 남습니다. 앱마다 저장 위치와 구조가 달라서 위치는 각 아티팩트 페이지에서 다루고, 이 페이지에서는 어디서 나왔든 같은 규칙으로 읽는 주소 문자열 자체만 봅니다.

- 데스크톱 지갑: [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md), [Electrum](../../02-artifacts/desktop/electrum.md), [Exodus](../../02-artifacts/desktop/exodus.md)
- 브라우저 확장 지갑: [MetaMask](../../02-artifacts/browser/metamask/index.md), [다른 확장 지갑](../../02-artifacts/browser/other-extensions.md)
- 모바일: [Android 지갑 앱](../../02-artifacts/mobile/android-wallets.md), [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md), [거래소 앱](../../02-artifacts/mobile/exchange-apps.md)
- 기록: [거래소가 제공하는 자료](../../02-artifacts/records/exchange-records.md), [블록 탐색기 기록 읽기](../../02-artifacts/records/block-explorers.md)

지갑 파일 안에 주소가 어떤 모양으로 들어 있는지는 [지갑 파일과 암호화](wallet-files.md)에서, 복구 문구 하나에서 주소가 여러 개 만들어지는 원리는 [복구 문구와 파생 경로](seed-derivation.md)에서 다룹니다.

## 구조

### 비트코인 주소 한눈에 보기

비트코인 주소는 인코딩 방식에 따라 두 종류입니다. 옛 형식은 Base58Check로 인코딩하고 버전 바이트(version byte)로 네트워크와 스크립트 종류를 구분합니다[1]. 세그윗(SegWit) 주소는 Bech32나 Bech32m으로 인코딩하고, 사람이 읽는 부분(human-readable part, HRP)으로 네트워크를, 증인 버전(witness version)으로 스크립트 세대를 구분합니다[4][5].

| 형식 | 인코딩 | 버전 바이트·HRP (메인넷 / 테스트넷) | 시작 글자 (메인넷 / 테스트넷) | 길이 |
|---|---|---|---|---|
| P2PKH | Base58Check | `0x00` / `0x6f` | `1` / `m`·`n` | 메인넷 26~34자, 대부분 33~34자 |
| P2SH (P2SH-P2WPKH 포함) | Base58Check | `0x05` / `0xc4` | `3` / `2` | 메인넷 34자, 테스트넷 35자 |
| P2WPKH (세그윗 v0) | Bech32 | `bc` / `tb` | `bc1q` / `tb1q` | 42자 |
| P2WSH (세그윗 v0) | Bech32 | `bc` / `tb` | `bc1q` / `tb1q` | 62자 |
| P2TR (세그윗 v1, 탭루트) | Bech32m | `bc` / `tb` | `bc1p` / `tb1p` | 62자 |

버전 바이트와 HRP는 명세 값이고[1][4][5], Base58Check 주소의 시작 글자와 길이는 명세의 인코딩 규칙대로 계산한 값입니다. P2PKH 주소는 해시 앞부분의 값이 작을수록 글자 수가 줄어서 길이가 일정하지 않습니다. 세그윗 v0 주소는 명세상 42자나 62자 둘 중 하나입니다[4].

### Base58Check

P2PKH는 공개 키를, P2SH는 리딤 스크립트(redeem script)를 RIPEMD-160(SHA-256()) 으로 해시해 20바이트 값을 얻습니다[1]. 그 앞에 버전 바이트를 붙이고, 이 21바이트를 SHA-256으로 두 번 해시한 결과의 앞 4바이트를 체크섬(checksum)으로 뒤에 붙인 다음, 전체 25바이트를 Base58로 바꿉니다[1]. Base58 문자표는 `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz` 이고, `0`·`O`·`I`·`l` 은 쓰지 않습니다[1]. 앞쪽의 0 바이트 하나는 `1` 한 글자가 됩니다[1].

| 바이트 위치 | 길이 | 내용 |
|---|---|---|
| 0 | 1 | 버전 바이트 |
| 1 | 20 | 공개 키 해시 또는 스크립트 해시 |
| 21 | 4 | 앞 21바이트를 SHA-256으로 두 번 해시한 값의 앞 4바이트 |

공개 키는 식별 바이트 뒤에 X 좌표 32바이트와 Y 좌표 32바이트가 오는 비압축 형식(`04` 로 시작)과, Y 좌표를 빼고 `02`·`03` 으로 시작하는 압축 형식이 있습니다[3]. 둘은 해시 값이 달라서 같은 키 하나가 서로 다른 P2PKH 주소 두 개에 쓰입니다[3]. Bitcoin Core 는 0.6 이전까지 비압축 키를 썼고, 지금은 압축 키가 기본입니다[3].

### Bech32와 Bech32m

Bech32 문자열은 HRP, 구분자 `1`, 데이터 부분 순서로 이어지고 최대 90자입니다[4]. 데이터 부분은 `1`·`b`·`i`·`o` 를 뺀 영숫자 32자(`qpzry9x8gf2tvdw0s3jn54khce6mua7l`)만 쓰고, 마지막 6자가 체크섬입니다[4]. 이 체크섬은 네 글자 이하가 틀린 오류를 반드시 잡아냅니다[4]. 인코더는 소문자로만 출력하고, 디코더는 대문자와 소문자가 섞인 문자열을 받지 않으며, QR 코드 안에서는 대문자를 쓰도록 권합니다[4].

세그윗 주소의 데이터 부분 첫 글자는 증인 버전이고, 그 뒤가 증인 프로그램(witness program)입니다[4]. 증인 버전 0 은 Bech32로, 1~16 은 Bech32m으로 인코딩합니다[5]. Bech32m은 체크섬 계산 마지막에 XOR 하는 상수를 `1` 에서 `0x2bc830a3` 으로 바꾼 것뿐이고 나머지 규칙은 같습니다[5]. Bech32는 마지막 글자가 `p` 일 때 바로 앞에 `q` 를 몇 개 넣거나 빼도 체크섬이 맞는 약점이 있어서 Bech32m이 나왔습니다[5]. 증인 버전 0 의 프로그램은 20바이트(P2WPKH)나 32바이트(P2WSH)만 허용합니다[4].

| 주소 | 잠금 스크립트 (scriptPubKey) |
|---|---|
| P2PKH (`1…`) | `OP_DUP OP_HASH160` + 공개 키 해시 20바이트 + `OP_EQUALVERIFY OP_CHECKSIG`[2] |
| P2SH (`3…`) | `0xA914` + 스크립트 해시 20바이트 + `0x87`[6] |
| P2WPKH (`bc1q…`, 42자) | `0x0014` + 공개 키 해시 20바이트[7] |
| P2TR (`bc1p…`) | `0x5120` + 출력 키 32바이트[8] |

P2SH-P2WPKH 는 세그윗 스크립트(`0x0014` + 공개 키 해시)를 리딤 스크립트로 넣은 P2SH 라서, 세그윗인데도 `3` 으로 시작하는 Base58Check 주소입니다[6].

다른 코인의 Bech32 HRP 는 SLIP-0173 에 등록돼 있습니다[4].

### 이더리움 주소

이더리움의 외부 소유 계정(externally owned account, EOA) 주소는 공개 키를 Keccak-256으로 해시한 값의 마지막 20바이트 앞에 `0x` 를 붙인 것이라, 헥스 40자에 `0x` 를 더해 42자입니다[10]. 컨트랙트 계정 주소도 똑같이 42자입니다[10]. 컨트랙트 주소는 `CREATE` 로 만들면 생성자 주소와 논스(nonce)로, `CREATE2` 로 만들면 생성자 주소와 솔트(salt), 생성 코드의 해시로 정해지고, `CREATE2` 주소는 컨트랙트를 배포하기 전에도 계산할 수 있습니다[10]. 계정 두 종류의 차이는 [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md)에서 다룹니다.

이더리움 주소에는 따로 체크섬 바이트가 없습니다. 그 대신 EIP-55 는 대소문자로 체크섬을 표시합니다[11]. 소문자 헥스 주소 문자열(`0x` 제외)을 Keccak-256으로 해시하고, 주소의 i 번째 글자가 `a`~`f` 이면서 해시의 i 번째 니블이 8 이상이면 그 글자를 대문자로 씁니다[11]. 길이는 40자 그대로입니다[11]. 해시 값에 따라 글자가 모두 대문자나 모두 소문자로 나오는 주소도 있어서, EIP-55 시험 벡터에도 그런 주소가 들어 있습니다[11].

| 문자열 | 길이 | 설명 |
|---|---|---|
| `0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed` | 42자 | EIP-55 형식 주소 (EIP-55 시험 벡터)[11] |
| `0x` + 헥스 40자 | 42자 | EOA 와 컨트랙트 주소 모두[10] |
| 헥스 64자 | 64자 | 개인 키[10], 트랜잭션 해시·블록 해시(32바이트)[12] |

## 읽는 법

### Base58Check 주소를 바이트로 풀기

BIP-49 시험 벡터의 테스트넷 P2SH-P2WPKH 주소 `2Mww8dCYPUpKHofjgcXcBCEGmniw9CoaiD2` 를 Base58로 풀면 25바이트가 나옵니다(명세로 계산한 값)[6].

```
c4 33 6c aa 13 e0 8b 96 08 0a 32 b5 d8 18 d5 9b 4a b3 b3 67 42 c9 68 5f 65
```

첫 바이트 `c4` 는 테스트넷 P2SH 버전 바이트입니다[1]. 다음 20바이트 `336caa…b36742` 는 BIP-49 에 적힌 리딤 스크립트 해시와 같습니다[6]. 마지막 4바이트 `c9685f65` 는 앞 21바이트를 SHA-256으로 두 번 해시한 값의 앞 4바이트와 같아서 체크섬이 맞습니다[1]. 한 글자라도 바뀐 주소는 이 계산에서 체크섬이 어긋납니다.

### Bech32 주소를 글자 단위로 나누기

BIP-173 시험 벡터 `BC1QW508D6QEJXTDG4Y5R3ZARVARY0C5XW7KV8F3T4` 는 다음처럼 나뉩니다[4].

```
BC   1   Q   W508D6QEJXTDG4Y5R3ZARVARY0C5XW7K   V8F3T4
HRP  구분자 v0  증인 프로그램 32자(20바이트)        체크섬 6자
```

대문자로만 쓴 주소라 올바른 주소이고, 이 주소의 잠금 스크립트는 `0014751e76e8199196d454941c45d1b3a323f1433bd6` 입니다[4]. 앞의 `00` 은 증인 버전 0, `14` 는 뒤따르는 20바이트의 길이이고, 남은 20바이트가 공개 키 해시입니다. 증인 프로그램이 32바이트면 같은 방식으로 62자가 되고, 첫 데이터 글자가 `p`(버전 1)이면 Bech32m 체크섬으로 검증합니다[4][5].

### 복구 문구 하나에서 나온 주소 예

BIP-84·86 시험 벡터는 모두 같은 복구 문구 "abandon ×11 about" 에서 나온 값입니다. 첫 수신 주소는 P2WPKH(m/84'/0'/0'/0/0)가 `bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu`[7], P2TR(m/86'/0'/0'/0/0)가 `bc1p5cyxnuxmeuwuvkwfem96lqzszd02n6xdcjrs20cac6yqjjwudpxqkedrcr`[8] 입니다. 같은 복구 문구에서도 파생 경로가 다르면 주소 형식이 달라진다는 것을 이 두 값으로 알 수 있습니다. 파생 경로는 [복구 문구와 파생 경로](seed-derivation.md)에서 다룹니다.

## 포렌식에서 중요한 점

### 주소만으로 알 수 있는 것과 없는 것

주소 모양과 체크섬으로 확인되는 것은 체인, 네트워크(메인넷·테스트넷), 비트코인의 스크립트 종류(P2PKH·P2SH·세그윗 v0·탭루트)까지입니다[1][4][5]. 테스트넷 주소가 나오면 개발·시험용일 가능성이 있어서 실제 자산과 나눠 봐야 합니다.

주소만 보고 알 수 없는 것도 분명합니다. 누가 주인인지, 거래소가 맡아 관리하는 주소인지 개인이 키를 가진 주소인지는 주소 문자열에 나오지 않습니다. 수탁형과 비수탁형의 차이는 [지갑의 종류](wallet-types.md)에서 다룹니다. 이더리움 주소는 EOA 와 컨트랙트가 같은 42자 모양이라 모양으로는 구분할 수 없습니다[10]. 비트코인 P2SH 주소는 해시만 드러나서, 안에 멀티시그가 있는지 P2WPKH 가 있는지는 그 주소에서 돈을 보낼 때 리딤 스크립트가 블록체인에 올라와야 알 수 있습니다[2]. 같은 개인 키에서 나온 압축·비압축 P2PKH 주소 두 개는 서로 다른 주소처럼 보입니다[3].

### 시각

주소 문자열에는 시각이 들어 있지 않습니다. 주소가 처음 쓰인 시각은 그 주소가 들어간 트랜잭션의 블록 시각으로 확인하고, 기기에서 주소가 저장된 시각은 그 주소를 담은 파일이나 데이터베이스 레코드의 시각으로 따로 봅니다. 블록 시각의 기준은 [블록 시각과 확정](../blockchain/block-time.md)에서 다룹니다.

### 문자열 검색과 카빙

디스크·메모리 이미지에서 주소를 찾을 때는 정규식으로 후보를 모은 다음 체크섬으로 오탐을 걸러 냅니다. Base58Check는 4바이트 체크섬을[1], Bech32·Bech32m은 BCH 체크섬을[4][5] 계산합니다. EIP-55 는 체크섬을 대소문자로만 표시하므로[11], 모두 소문자나 모두 대문자로 저장된 이더리움 주소는 대소문자로 검증할 수 없습니다. 조각난 주소는 체크섬이 맞지 않으므로, 체크섬이 맞는 문자열만 주소로 보고서에 올립니다. 카빙 절차는 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에서 다룹니다.

## 함정

**P2SH-P2WPKH 주소도 세그윗입니다.** `3` 으로 시작하는 Base58Check 주소라 옛 형식처럼 보이지만, 안에 세그윗 스크립트가 들어 있을 수 있습니다[6]. 주소 모양만으로 "세그윗을 쓰지 않았다" 고 판단하면 안 됩니다.

**Bech32 검증기로 탭루트 주소를 검사하면 틀린 주소로 나옵니다.** 증인 버전 0 은 Bech32, 1 이상은 Bech32m 이고, 명세는 두 방식을 모두 시도하거나 둘 다 처리하는 디코더를 쓰고, 디코딩한 증인 버전에 맞는 인코딩인지 확인하도록 합니다[5]. `bc1p` 주소를 Bech32 로만 검사하는 도구는 정상 주소를 버립니다.

**대문자 Bech32 주소도 정상입니다.** QR 코드에서 읽었거나 사람이 옮겨 적은 주소는 대문자일 수 있습니다[4]. 대소문자가 섞인 경우만 잘못된 주소입니다[4].

**이더리움 주소는 대소문자가 앱마다 다릅니다.** 같은 주소가 EIP-55 형식, 전부 소문자, 전부 대문자로 따로 저장될 수 있습니다. iOS Coinbase Wallet 앱은 MMKV 키 안의 주 주소를 대문자로 저장해서, 같은 앱의 다른 데이터에 있는 같은 주소와 대소문자가 다를 수 있습니다[13]. 주소를 서로 맞춰 볼 때는 대소문자를 무시하고 비교합니다.

**헥스 64자는 개인 키일 수도, 트랜잭션 해시일 수도 있습니다.** 이더리움 개인 키는 헥스 64자이고[10], 트랜잭션 해시와 블록 해시도 32바이트라 헥스로 64자입니다[12]. 비트코인 트랜잭션 ID도 32바이트 해시입니다[1]. 모양으로는 구분할 수 없으니 저장된 필드 이름과 앞뒤 문맥으로 판단합니다.

**주소처럼 보이지만 주소가 아닌 문자열이 있습니다.** 아래 문자열은 주소와 같은 Base58Check 방식이라 비슷해 보이지만, 개인 키나 확장 키라서 주소 목록에 넣으면 안 됩니다. 시작 글자와 길이는 명세의 인코딩 규칙대로 계산한 값입니다.

| 문자열 | 시작 글자 | 길이 | 근거 |
|---|---|---|---|
| WIF 개인 키, 비압축 공개 키용 | 메인넷 `5`, 테스트넷 `9` | 51자 | 버전 바이트 `0x80`·`0xef`[3] |
| WIF 개인 키, 압축 공개 키용 | 메인넷 `K`·`L`, 테스트넷 `c` | 52자 | 키 뒤에 `0x01` 추가[3] |
| 미니 개인 키 | `S` | 30자 미만 | [3] |
| 확장 키 | 메인넷 `xpub`·`xprv`, 테스트넷 `tpub`·`tprv` | 111자 | [9] |

WIF·미니 개인 키·`xprv`·`tprv` 가 보이면 그 파일이나 메모리 영역에 개인 키가 평문으로 있을 수 있다는 뜻이라, 증거물을 다룰 때 따로 표시해 둡니다. 확장 키의 식별자인 공개 키 Hash160 은 옛 비트코인 주소에 들어가는 데이터와 같아서, Base58 로 표시하면 주소로 오해할 수 있습니다[9]. 확장 키 접두사는 [복구 문구와 파생 경로](seed-derivation.md)에서 다룹니다.

**모든 주소가 헥스 문자열인 것은 아닙니다.** Android 지갑 앱 논문 한 편은 "모든 암호화폐 주소는 16진 문자열이고 비트코인 주소는 대개 16진 26~35자" 라고 적었지만[16], 명세상 비트코인 주소는 Base58Check 나 Bech32·Bech32m 으로 인코딩합니다[1][4]. 헥스 정규식으로 비트코인 주소를 찾으면 거의 다 놓칩니다.

## 도구

**bstrings / KAPE.** KAPE 모듈 `bstrings_BitCoinWallet` 은 bstrings 의 내장 정규식 `bitcoin` 을 부릅니다[14]. 이 정규식은 `\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b` 라서 `1`·`3` 으로 시작하는 Base58 주소만 잡고, `bc1` 주소와 이더리움 주소는 잡지 못합니다[15]. 같은 도구에 Monero·Aeon·Bytecoin·Dashcoin 주소 정규식도 들어 있습니다[15]. 정규식은 체크섬을 확인하지 않으므로 결과는 후보로만 봅니다.

**Bech32 참조 구현.** BIP-173 이 링크한 `sipa/bech32` 저장소에 C·C++·JavaScript·Go·Python·Haskell·Ruby·Rust 참조 구현이 있습니다[4]. 찾은 `bc1`·`tb1` 문자열의 체크섬과 증인 버전을 이 구현으로 검증할 수 있습니다.

**직접 계산.** Base58Check 체크섬은 SHA-256 두 번과 Base58 변환만 있으면 되고, EIP-55 는 Keccak-256 만 있으면 됩니다[1][11]. 명세에 실린 의사 코드와 시험 벡터로 계산기가 맞게 동작하는지 먼저 확인한 뒤 실제 데이터에 씁니다.

## 참고 문헌

1. Bitcoin Developer Reference, "Transactions — Address Conversion". https://developer.bitcoin.org/reference/transactions.html
2. Bitcoin Developer Guide, "Transactions — P2PKH Script Validation, P2SH Scripts". https://developer.bitcoin.org/devguide/transactions.html
3. Bitcoin Developer Guide, "Wallets — Wallet Import Format, Mini Private Key Format, Public Key Formats". https://developer.bitcoin.org/devguide/wallets.html
4. BIP-173, "Base32 address format for native v0-16 witness outputs". https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki
5. BIP-350, "Bech32m format for v1+ witness addresses". https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki
6. BIP-49, "Derivation scheme for P2WPKH-nested-in-P2SH based accounts". https://github.com/bitcoin/bips/blob/master/bip-0049.mediawiki
7. BIP-84, "Derivation scheme for P2WPKH based accounts". https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki
8. BIP-86, "Key Derivation for Single Key P2TR Outputs". https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki
9. BIP-32, "Hierarchical Deterministic Wallets". https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
10. ethereum.org, "Ethereum accounts". https://github.com/ethereum/ethereum-org-website/blob/dev/public/content/developers/docs/accounts/index.md
11. EIP-55 (ERC-55), "Mixed-case checksum address encoding". https://eips.ethereum.org/EIPS/eip-55
12. ethereum.org, "JSON-RPC API". https://ethereum.org/en/developers/docs/apis/json-rpc/
13. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
14. KapeFiles, `Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape`. https://github.com/EricZimmerman/KapeFiles/blob/master/Modules/EZTools/bstrings/bstrings_BitCoinWallet.mkape
15. bstrings, `bstrings/Program.cs`. https://github.com/EricZimmerman/bstrings/blob/master/bstrings/Program.cs
16. Eugene Chang, Paul Darcy, Kim-Kwang Raymond Choo, Nhien-An Le-Khac, 「Forensic Artefact Discovery and Attribution from Android Cryptocurrency Wallet Applications」, arXiv, 2022, doi:10.48550/arXiv.2205.14611
