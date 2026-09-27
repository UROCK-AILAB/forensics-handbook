---
title: "복구 문구와 파생 경로"
parent: "기반 · 지갑과 키"
nav_order: 70
---

# 복구 문구와 파생 경로 (BIP-39·BIP-32·BIP-44)

계층 결정적 지갑 (HD wallet) 은 단어 12~24개로 된 복구 문구 하나에서 키와 주소를 모두 계산해 냅니다. 복구 문구를 시드로 바꾸는 규칙은 BIP-39, 시드에서 키 나무를 만드는 규칙은 BIP-32, 나무의 어느 가지를 어떤 주소에 쓰는지는 BIP-44·49·84·86 이 정합니다. 이 페이지는 기기에서 나온 복구 문구·확장 공개 키·파생 경로 문자열을 알아보고, 그것으로 어떤 주소까지 확인할 수 있는지를 다룹니다.

## 이 형식을 쓰는 아티팩트

복구 문구 자체는 보통 암호화되어 저장되지만, 확장 공개 키와 파생 경로는 평문으로 남는 경우가 많습니다. 지갑별로 남는 파생 정보는 다음과 같습니다.

| 지갑·도구 | 남는 것 | 자세한 페이지 |
|---|---|---|
| Electrum 지갑 파일 | 키스토어의 `xpub`, `derivation`(파생 경로), `root_fingerprint`(마스터 키 지문)[13] | [Electrum](../../02-artifacts/desktop/electrum.md) |
| MetaMask 볼트 안 HD 키링 | `hdPath`, `numberOfAccounts`(볼트는 암호화되어 있음)[14] | [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| MetaMask 의 Ledger 연동 키링 | `hdPath`, 주소별 `accountDetails`(`bip44`·`hdPath`), `implementFullBIP44`. 개인 키 없이 경로만 저장[15] | [MetaMask](../../02-artifacts/browser/metamask/index.md) |
| Coinbase Wallet (iOS) | `address` 표의 `derivationPath` 열, MMKV 저장소의 `BIP44XpubKey_` 항목(확장 공개 키)[18] | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md) |
| Trust keystore (옛 Trust Wallet iOS 라이브러리) | `activeAccounts` 안의 `derivationPath`, `extendedPublicKey`, `addressData`[19] | [iOS 지갑 앱](../../02-artifacts/mobile/ios-wallets.md) |
| Bitcoin Core 디스크립터 | `[지문/경로]xpub…` 형식의 키 출처 표기[16] | [Bitcoin Core](../../02-artifacts/desktop/bitcoin-core.md) |
| Ledger Live 프로세스 메모리 | 동기화된 확장 공개 키, 파생 경로, 새 주소[20] | [하드웨어 지갑](../../02-artifacts/hardware/hardware-wallets.md) |

지갑 파일이 어떤 모양으로 암호화되는지는 [지갑 파일과 암호화](wallet-files.md) 에서 다룹니다.

## 구조

### 복구 문구 (BIP-39)

복구 문구 (mnemonic) 는 난수(엔트로피)를 사람이 옮겨 적기 쉬운 단어로 바꾼 것입니다. 엔트로피는 128~256비트이고 32비트 단위로만 늘어납니다. 엔트로피의 SHA-256 해시 앞부분을 엔트로피 길이의 1/32 만큼 떼어 체크섬으로 붙이고, 전체를 11비트씩 잘라 0~2047 번호로 만든 뒤 단어 목록에서 그 번호의 단어를 고릅니다[1].

| 엔트로피(비트) | 체크섬(비트) | 단어 수 |
|---|---|---|
| 128 | 4 | 12 |
| 160 | 5 | 15 |
| 192 | 6 | 18 |
| 224 | 7 | 21 |
| 256 | 8 | 24 |

단어 목록은 2048개이고, 영어 목록은 앞 네 글자만으로 단어가 하나로 정해지게 만들었습니다[1]. 공식 목록은 영어·일본어·한국어·스페인어·중국어 간체·중국어 번체·프랑스어·이탈리아어·체코어·포르투갈어 열 가지입니다[2]. 다만 지갑 대부분은 영어 목록만 지원합니다[1]. 일본어는 단어 사이를 전각 공백(U+3000)으로 띄우고, 중국어는 ASCII 공백(0x20)으로 띄웁니다[2].

단어 목록은 UTF-8 NFKD(호환 분해형)로 저장합니다[1]. 한국어 목록도 한글을 초성·중성·종성 자모로 풀어 저장하고 있어서, 첫 단어 "가격" 은 목록 파일 안에서 15바이트이고 보통 입력하는 완성형(NFC)으로는 6바이트입니다[3]. 아래 바이트는 두 정규화 형식으로 계산한 값입니다.

```
"가격" NFC  (완성형, 6바이트)   : EA B0 80 EA B2 A9
"가격" NFKD (목록 파일, 15바이트): E1 84 80 E1 85 A1 E1 84 80 E1 85 A7 E1 86 A8
```

### 시드와 마스터 키

복구 문구를 시드로 바꿀 때는 PBKDF2 를 HMAC-SHA512 로 2048번 돌립니다. 비밀번호 자리에는 복구 문구(UTF-8 NFKD)를, 솔트 자리에는 문자열 `mnemonic` 뒤에 패스프레이즈 (passphrase) 를 붙인 값을 넣고, 결과는 512비트(64바이트) 시드입니다. 패스프레이즈가 없으면 빈 문자열을 씁니다[1]. 패스프레이즈는 무엇을 넣어도 유효한 시드가 나오고, 그 시드마다 서로 다른 지갑이 됩니다[1].

BIP-32 는 이 시드를 키 `Bitcoin seed` 로 HMAC-SHA512 해 64바이트를 얻고, 왼쪽 32바이트를 마스터 개인 키, 오른쪽 32바이트를 마스터 체인 코드 (chain code) 로 씁니다[4]. 키에 체인 코드를 붙인 것을 확장 키 (extended key) 라고 합니다. 확장 개인 키가 있으면 그 아래 모든 개인 키·공개 키를 계산할 수 있고, 확장 공개 키가 있으면 그 아래 일반(비강화) 자식 공개 키를 모두 계산할 수 있습니다[4].

자식 번호는 0~2³¹−1 이 일반 자식, 2³¹~2³²−1 이 강화 자식 (hardened) 입니다[4]. 경로 표기에서 `44'` 처럼 작은따옴표가 붙은 단계가 강화 파생이고, Bitcoin Core 디스크립터는 `'` 대신 `h` 도 받습니다[5][16]. 공개 키만으로는 강화 자식을 계산할 수 없습니다[4].

### 확장 키 직렬화

확장 키는 78바이트로 직렬화하고, 이중 SHA-256 체크섬 4바이트를 붙여 Base58 로 바꾸면 정확히 111자가 됩니다[4].

| 오프셋 | 크기 | 필드 | 값 |
|---|---|---|---|
| 0 | 4 | 버전 | 아래 접두사 표 |
| 4 | 1 | 깊이 | 마스터 0x00, 한 단계 아래 0x01 … |
| 5 | 4 | 부모 키 지문 | 마스터면 0x00000000 |
| 9 | 4 | 자식 번호 | 빅엔디언. 강화 자식이면 0x80000000 이상. 마스터면 0 |
| 13 | 32 | 체인 코드 | |
| 45 | 33 | 키 | 공개 키(압축형 02·03 시작) 또는 0x00 + 개인 키 32바이트 |
| 78 | 4 | 체크섬 | 앞 78바이트의 이중 SHA-256 앞 4바이트 |

키 지문 (fingerprint) 은 공개 키의 Hash160(SHA-256 뒤 RIPEMD-160) 앞 32비트입니다. 지문은 부모를 빨리 찾으려는 값이라 서로 다른 키의 지문이 같을 수 있습니다[4].

버전 바이트에 따라 Base58 문자열 앞 네 글자가 정해집니다.

| 접두사(공개/개인) | 버전(공개/개인) | 네트워크 | 주로 쓰는 주소 형식 | 정한 곳 |
|---|---|---|---|---|
| xpub / xprv | 0x0488B21E / 0x0488ADE4 | 메인넷 | P2PKH 또는 P2SH | [4] |
| tpub / tprv | 0x043587CF / 0x04358394 | 테스트넷 | P2PKH 또는 P2SH | [4] |
| ypub / yprv | 0x049D7CB2 / 0x049D7878 | 메인넷 | P2WPKH-in-P2SH | [6] |
| upub / uprv | 0x044A5262 / 0x044A4E28 | 테스트넷 | P2WPKH-in-P2SH | [6] |
| zpub / zprv | 0x04B24746 / 0x04B2430C | 메인넷 | P2WPKH | [7] |
| vpub / vprv | 0x045F1CF6 / 0x045F18BC | 테스트넷 | P2WPKH | [7] |
| Ypub / Yprv | 0x0295B43F / 0x0295B005 | 메인넷 | 다중 서명 P2WSH-in-P2SH | [10] |
| Zpub / Zprv | 0x02AA7ED3 / 0x02AA7A99 | 메인넷 | 다중 서명 P2WSH | [10] |

직렬화에는 코인 종류가 들어 있지 않습니다. 다른 코인의 버전 바이트(예: 라이트코인 `Ltub`)는 SLIP-0132 에 모여 있고, 그로스톨코인은 비트코인과 같은 `xpub`·`ypub`·`zpub` 을, 시스코인은 `zpub` 을 그대로 씁니다[10]. 주소 형식은 [주소 형식](address-formats.md) 에서 다룹니다.

### 파생 경로 (BIP-44·49·84·86)

BIP-44 는 경로를 다섯 단계로 나눕니다[5].

```
m / purpose' / coin_type' / account' / change / address_index
```

앞의 세 단계(목적·코인 종류·계정)는 강화 파생이고, 뒤의 두 단계는 일반 파생입니다. `change` 가 0 이면 받는 주소를 만드는 외부 체인, 1 이면 거스름돈 주소를 만드는 내부 체인입니다[5]. 거스름돈이 무엇인지는 [비트코인의 UTXO](../blockchain/utxo.md) 에서 다룹니다.

| purpose | 주소 형식 | 첫 받는 주소 경로(비트코인 메인넷) | 정한 곳 |
|---|---|---|---|
| 44' | P2PKH (`1…`) | `m/44'/0'/0'/0/0` | [5] |
| 49' | P2WPKH-in-P2SH (`3…`) | `m/49'/0'/0'/0/0` | [6] |
| 84' | P2WPKH (`bc1q…`) | `m/84'/0'/0'/0/0` | [7] |
| 86' | 단일 키 P2TR (`bc1p…`) | `m/86'/0'/0'/0/0` | [8] |

BIP-49·84·86 은 일부러 BIP-44 와 다른 계정 나무를 씁니다. 그래서 이 방식을 모르는 지갑에 같은 복구 문구를 넣으면 잔액 일부가 아니라 계정 자체가 보이지 않습니다[6][7][8].

코인 종류 번호는 SLIP-0044 에 등록되어 있습니다[9].

| coin_type | 코인 |
|---|---|
| 0 | 비트코인 |
| 1 | 모든 코인의 테스트넷 |
| 2 | 라이트코인 |
| 60 | 이더 |
| 61 | 이더 클래식 |
| 144 | XRP |
| 195 | 트론 |
| 501 | 솔라나 |
| 714 | 바이낸스 |
| 966 | 매틱 |

BIP-32 명세 자체가 예로 든 구조는 `m/iH/0/k`(외부), `m/iH/1/k`(내부)로, purpose·coin_type 단계가 없습니다[4]. 이 모양의 경로는 BIP-44 이전 방식을 따른 지갑일 가능성이 있습니다.

### 이더리움 지갑의 경로

이더리움 지갑은 같은 복구 문구에서도 앱마다 경로를 다르게 씁니다. MetaMask HD 키링은 `m/44'/60'/0'/0` 아래에 번호를 붙여 `m/44'/60'/0'/0/n` 을 씁니다[14]. MetaMask 의 Ledger 연동 키링은 기본값이 `m/44'/60'/0'` 이고 뒤에 번호를 붙여 `m/44'/60'/0'/n` 이 됩니다. `hdPath` 가 `m/44'/60'/0'/0/0` 이면 Ledger Live 방식으로 보고 계정 단계를 늘려 `m/44'/60'/n'/0/0` 을 씁니다[15]. 이더리움 주소를 공개 키에서 계산하는 방법은 [이더리움의 계정과 로그](../blockchain/ethereum-accounts.md) 에서 다룹니다.

### Electrum 시드

Electrum 이 새로 만드는 시드는 BIP-39 가 아닙니다. Electrum 은 문구를 키 `Seed version` 으로 HMAC-SHA512 한 헥스 값이 어떤 접두사로 시작하는지로 시드 종류를 구분합니다[11][12]. 파생 시작점은 종류마다 다릅니다[13].

| 접두사 | 종류 | 파생 시작점 |
|---|---|---|
| `01` | standard | `m/` |
| `100` | segwit | `m/0'/` (다중 서명은 `m/1'/`) |
| `101` | 2FA | — |
| `102` | 2FA segwit | — |

시드를 바이너리로 바꿀 때도 PBKDF2-HMAC-SHA512 2048회는 같지만 솔트가 `electrum` + 패스프레이즈입니다[11]. 이보다 오래된 'old' 형식은 단어 12개 또는 24개, 혹은 16·32바이트 헥스 문자열입니다[11]. Electrum 에서 BIP-39 문구로 키스토어를 만들 때는 파생 경로를 따로 받고, 경로 첫 단계(`44'`·`49'`·`84'`)로 주소 형식을 정합니다. 기본 경로는 `m/purpose'/coin'/account'` 모양입니다[13].

## 읽는 법

### 확장 공개 키를 헥스로 풀기

`xpub`·`zpub` 같은 문자열을 찾으면 Base58 로 풀어 82바이트를 얻고, 위 직렬화 표대로 나눕니다. 아래는 SLIP-0132 시험 벡터(복구 문구 "abandon" 11개 + "about", 경로 `m/44'/0'/0'`)의 xpub 을 명세대로 푼 값입니다[10].

```
xpub6BosfCnifzxcFwrSzQiqu2DBVTshkCXacvNsWGYJVVhhawA7d4R5WSWGFNbi8Aw6ZRc1brxMyWMzG3DSSSSoekkudhUd9yLb6qx39T9nMdj

0488b21e                                                           버전 (xpub)
03                                                                 깊이 3 = m/44'/0'/0'
155bca59                                                           부모 키 지문
80000000                                                           자식 번호 0x80000000 = 0' (강화)
3da4bc190a2680111d31fadfdc905f2a7f6ce77c6f109919116f253d43445219   체인 코드
03774c910fcf07fa96886ea794f0d5caed9afe30b44b83f7e213bb92930e7df4bd 공개 키 (압축형)
c84b94ea                                                           체크섬
```

깊이 3 과 자식 번호 `0'` 로 이 키가 계정 단계(`m/purpose'/coin'/0'`)의 키라는 것을 알 수 있습니다. 다만 purpose 와 coin_type 은 직렬화에 들어 있지 않아서, 접두사(`xpub`·`ypub`·`zpub`)와 함께 저장된 경로 문자열로 판단합니다. 같은 시험 벡터의 `m/44'/0'/0'/0/0` 주소는 `1LqBGSKuX5yYUonjxT5qGfpUsXKYYWeabA` 입니다[10]. 공개 키 헤더가 02·03 이 아니거나, 깊이가 0 인데 부모 지문이 0 이 아닌 값은 잘못된 확장 키입니다[4].

### 경로와 지문 표기 읽기

Bitcoin Core 디스크립터의 `pkh([d34db33f/44'/0'/0']xpub…/1/*)` 는 "지문이 `d34db33f` 인 마스터 키에서 `44'/0'/0'` 로 내려온 xpub 의, 내부 체인(`1`) 아래 모든 주소" 를 뜻합니다[16]. Electrum 지갑 파일의 `root_fingerprint` 와 `derivation` 도 같은 두 정보를 따로 적은 것입니다[13]. 서로 다른 지갑 파일이나 기기에서 나온 확장 공개 키의 마스터 지문과 경로가 같으면 같은 복구 문구에서 나왔을 가능성이 있습니다. 지문은 32비트라 우연히 같을 수 있으므로[4], 확장 공개 키 전체나 계산한 주소로 한 번 더 비교합니다.

### 복구 문구 문자열 검색

영어 복구 문구는 목록 2048단어 중 12~24개가 이어진 문자열로 검색할 수 있고, 앞 네 글자만 적은 메모도 단어가 하나로 정해집니다[1]. 한국어 문구는 사용자가 적은 파일과 지갑 목록의 정규화 형식이 달라 바이트 검색이 서로 맞지 않습니다. 검색어를 NFC 와 NFKD 두 형식으로 모두 만들어 찾습니다. 문구를 찾은 뒤 개인 키를 계산하는 일은 이 핸드북에서 다루지 않습니다.

## 포렌식에서 중요한 점

**증명하는 것.** 기기에서 찾은 확장 공개 키와 경로가 있으면, 개인 키 없이도 그 계정 아래 주소를 다시 계산해 블록체인 기록과 비교할 수 있습니다[4]. 계정별 확장 공개 키를 감사인에게 넘기면 감사인은 개인 키 없이 모든 입출금을 볼 수 있습니다[4]. 하드웨어 지갑을 써도 연결 프로그램(Ledger Live, Trezor Wallet)이 실행 중이면 메모리에 동기화된 확장 공개 키가 남고, 이 키로 주소와 거래 내역을 다시 찾을 수 있습니다[20]. 다만 Ledger Live 는 앱을 잠그거나 종료하면 이 흔적이 몇 분 안에 대부분 덮어써진 실험 결과가 있습니다[20].

**증명하지 못하는 것.** 복구 문구 문자열이 기기에 있다는 것만으로 그 사람이 지갑을 만들었거나 썼다는 것은 알 수 없습니다. 누가 적었는지, 패스프레이즈를 함께 썼는지는 문구에 나와 있지 않습니다[1]. 경로를 모르면 확장 공개 키나 문구에서 계산한 주소가 그 지갑이 쓴 주소 전부라고 할 수 없습니다. 확장 공개 키로는 강화 자식을 계산할 수 없어서, 계정 단계 xpub 하나로는 같은 시드의 다른 계정 주소를 알 수 없습니다[4]. 앱이 파생해 둔 주소가 쓰였거나 돈이 들어왔다는 뜻도 아닙니다[18].

**시각.** BIP-39 문구와 BIP-32 직렬화에는 시각 필드가 없습니다[1][4]. 지갑을 언제 만들었는지는 지갑 파일이나 앱 DB 의 기록, 또는 그 주소들이 처음 등장한 블록 시각으로 판단합니다. 블록 시각을 읽는 법은 [블록 시각과 확정](../blockchain/block-time.md) 에서 다룹니다.

**주소 탐색 범위.** BIP-44 지갑은 복구할 때 계정 0 의 외부 체인부터 주소를 살펴보고, 연속 20개가 쓰이지 않았으면 그 뒤에 쓴 주소가 없다고 보고 멈춥니다(gap limit 20). 외부 체인에 거래가 있으면 다음 계정으로 넘어가고, 거래가 없는 계정을 만나면 탐색을 끝냅니다. 내부 체인은 살펴보지 않습니다[5]. 분석 도구로 주소를 다시 계산할 때도 이 범위만 보면 사용자가 20개 넘게 건너뛰어 만든 주소를 놓칠 수 있으므로 범위를 넓혀 계산합니다. iLEAPP 의 시험 이미지 두 개에서는 Coinbase Wallet 이 파생해 둔 주소 번호가 0~19 였습니다[18].

**Bitcoin Core 의 버전 차이.** Bitcoin Core 는 0.13 부터 HD 지갑을 만들었고, 그 전 지갑은 서로 관계없는 개인 키 모음이라 경로로 주소를 되살릴 수 없습니다[17]. 옛 지갑을 디스크립터 지갑으로 옮기면(`migratewallet`) 같은 시드를 쓰지만 새 주소는 BIP-44·49·84·86 표준 경로로 만듭니다[17]. 같은 지갑 안에서도 이전 전후로 경로 모양이 달라질 수 있습니다.

## 함정

- **패스프레이즈.** 같은 12단어라도 패스프레이즈가 다르면 완전히 다른 지갑이 됩니다[1]. 문구로 계산한 주소에 거래가 없다고 그 문구로 만든 지갑이 비어 있다고 결론 내리지 않습니다.
- **Electrum 시드와 BIP-39.** 같은 단어 12개라도 Electrum 시드인지 BIP-39 문구인지에 따라 솔트와 파생 시작점이 달라 주소가 전혀 다릅니다[11][13].
- **이더리움 경로.** MetaMask HD 키링과 Ledger Live 방식은 첫 주소(`m/44'/60'/0'/0/0`)만 같고 두 번째 주소부터 다릅니다. MetaMask Ledger 키링의 기본 경로(`m/44'/60'/0'/n`)로 만든 주소는 둘 다와 다릅니다[14][15].
- **접두사만 다른 확장 키.** `ypub`·`zpub` 은 버전 바이트만 다를 뿐 `xpub` 과 구조가 같습니다. BIP-49 는 처음에 `xpub` 접두사를 그대로 써서 혼란이 생겼고, 다른 코인이 비트코인과 같은 접두사를 쓰기도 합니다[10].
- **짧은 체크섬.** 12단어 문구의 체크섬은 4비트뿐이라 단어 하나를 잘못 옮겨 적어도 체크섬이 맞을 수 있습니다[1].
- **단어 목록을 바꾸면 다른 시드.** 시드는 엔트로피가 아니라 문구 문자열로 계산하므로, 같은 엔트로피를 다른 언어 목록으로 옮기면 시드가 달라집니다[1].
- **한국어 정규화.** 한국어 목록은 NFKD 로 저장되어 있어 완성형으로 적은 메모와 바이트가 다릅니다[1][3].
- **확장 키 식별자.** 확장 키의 Hash160 을 Base58 로 표시하면 주소처럼 보여서 그렇게 표시하지 않도록 권합니다[4]. 주소 모양 문자열이 실제로 받는 주소인지는 문맥으로 확인합니다.

## 도구

- **헥스 편집기와 Base58 디코더.** 확장 공개 키는 Base58 을 풀면 82바이트이고, 위 표대로 나눠 체크섬까지 확인할 수 있습니다[4].
- **Bitcoin Core `deriveaddresses` RPC.** 확장 공개 키를 넣은 디스크립터에서 주소 목록을 계산합니다. 체크섬이 붙은 디스크립터를 요구하므로 `getdescriptorinfo` 로 체크섬을 먼저 얻습니다[16].
- **iLEAPP `coinbaseWallet.py`.** Coinbase Wallet(iOS)의 주소·파생 경로·확장 공개 키를 표로 뽑습니다[18].
- 기기에서 이런 문자열을 찾는 절차는 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md) 와 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md) 에서 다룹니다. 지갑 종류별 차이는 [지갑의 종류](wallet-types.md) 에 있습니다.

## 참고 문헌

1. BIP-39, *Mnemonic code for generating deterministic keys* — https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki
2. BIP-39 단어 목록 안내, *bip-0039-wordlists.md* — https://github.com/bitcoin/bips/blob/master/bip-0039/bip-0039-wordlists.md
3. BIP-39 한국어 단어 목록, *korean.txt* — https://github.com/bitcoin/bips/blob/master/bip-0039/korean.txt
4. BIP-32, *Hierarchical Deterministic Wallets* — https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
5. BIP-44, *Multi-Account Hierarchy for Deterministic Wallets* — https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki
6. BIP-49, *Derivation scheme for P2WPKH-nested-in-P2SH based accounts* — https://github.com/bitcoin/bips/blob/master/bip-0049.mediawiki
7. BIP-84, *Derivation scheme for P2WPKH based accounts* — https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki
8. BIP-86, *Key Derivation for Single Key P2TR Outputs* — https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki
9. SLIP-0044, *Registered coin types for BIP-0044* — https://github.com/satoshilabs/slips/blob/master/slip-0044.md
10. SLIP-0132, *Registered HD version bytes for BIP-0032* — https://github.com/satoshilabs/slips/blob/master/slip-0132.md
11. Electrum 소스, `electrum/mnemonic.py` — https://github.com/spesmilo/electrum/blob/master/electrum/mnemonic.py
12. Electrum 소스, `electrum/version.py` — https://github.com/spesmilo/electrum/blob/master/electrum/version.py
13. Electrum 소스, `electrum/keystore.py` — https://github.com/spesmilo/electrum/blob/master/electrum/keystore.py
14. MetaMask 소스, `packages/keyring-eth-hd/src/hd-keyring.ts` — https://github.com/MetaMask/accounts/blob/main/packages/keyring-eth-hd/src/hd-keyring.ts
15. MetaMask 소스, `packages/keyring-eth-ledger-bridge/src/ledger-keyring.ts` — https://github.com/MetaMask/accounts/blob/main/packages/keyring-eth-ledger-bridge/src/ledger-keyring.ts
16. Bitcoin Core 문서, `doc/descriptors.md` — https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md
17. Bitcoin Core 문서, `doc/managing-wallets.md` — https://github.com/bitcoin/bitcoin/blob/master/doc/managing-wallets.md
18. iLEAPP, `scripts/artifacts/coinbaseWallet.py` — https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
19. Trust keystore 소스, `Sources/KeystoreKey.swift`, `Sources/Account.swift` — https://github.com/trustwallet/trust-keystore/blob/master/Sources/KeystoreKey.swift
20. Tyler Thomas, Mathew Piscitelli, Ilya Shavrov, Ibrahim Baggili, "Memory FORESHADOW: Memory FOREnSics of HArDware CryptOcurrency wallets – A Tool and Visualization Framework", *Forensic Science International: Digital Investigation*, 2020, doi:10.1016/j.fsidi.2020.301002
