---
title: "다른 확장 지갑"
parent: "아티팩트 · 브라우저 확장 지갑"
nav_order: 190
---

# 다른 확장 지갑 (Phantom·Coinbase Wallet 등)

MetaMask 말고도 Phantom, Coinbase Wallet, Binance Wallet, Ronin Wallet 같은 지갑이 브라우저 확장으로 나와 있고, Chromium 계열 브라우저에서는 모두 프로필의 `Local Extension Settings` 아래 확장 ID 이름의 LevelDB 폴더에 데이터를 둡니다. 그래서 확장 ID 만 알면 지갑 종류와 상관없이 같은 방법으로 폴더를 찾을 수 있습니다. 다만 MetaMask 와 달리 내부 저장 구조를 공개한 지갑이 드물어서, 폴더 안의 키 이름과 필드 뜻은 실제 데이터와 테스트넷 재현으로 확인해야 합니다.

## 무엇을 기록하나 · 왜 생기나

브라우저 확장 지갑은 키를 기기에 두는 자기 보관 지갑 (self-custodial wallet)입니다. Phantom 은 Solana·Ethereum·Polygon 을 지원하는 자기 보관 지갑이고, Ledger 하드웨어 지갑을 연결해 쓸 수 있습니다[1]. Coinbase Wallet 확장은 Ethereum 과 EVM 호환 네트워크, Solana 와 SPL 토큰을 지원하는 자기 보관 지갑입니다[2]. 키를 기기에 두기 때문에 확장은 암호화한 키(볼트)와 계정·설정을 브라우저가 확장에 내주는 로컬 저장소에 씁니다. 자기 보관 지갑과 거래소 보관 지갑의 차이는 [지갑의 종류](../../01-foundations/wallets/wallet-types.md)에 있습니다.

확장 지갑은 방문한 웹 페이지에 자바스크립트 객체를 넣어서, 사이트가 지갑이 설치됐는지 알아보고 연결을 요청할 수 있게 합니다. 이 객체는 페이지 안에만 있고 디스크에 남는 흔적은 아니지만, 사이트 쪽 스크립트가 어떤 지갑을 찾았는지 해석할 때 필요합니다.

| 지갑 | 페이지에 넣는 객체와 표시 |
|---|---|
| MetaMask | `window.ethereum` 의 `isMetaMask: true`[7] |
| Coinbase Wallet | `window.ethereum` 의 `isCoinbaseWallet: true`[7] |
| Binance Wallet | `window.BinanceChain`[7] |
| Phantom | `window.phantom.solana` 의 `isPhantom`, 옛 방식으로 `window.solana` 도 씀[6] |

Phantom 의 확장과 모바일 앱 안의 브라우저는 `https://` 사이트, `localhost`, `127.0.0.1` 에만 `phantom` 객체를 넣고, `http://` 사이트와 iframe 에는 넣지 않습니다[6].

## 위치와 버전별 차이

Chromium 계열 브라우저는 확장마다 로컬 저장소를 프로필 폴더의 `Local Extension Settings\확장 ID\` 에 LevelDB 로 둡니다. 프로필 폴더 구조와 확장 설정 파일은 Windows 핸드북의 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)에, LevelDB 파일 형식은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)에 있습니다. Windows 의 Chrome 기본 프로필이라면 경로는 아래와 같습니다[3].

```
%localappdata%\Google\Chrome\User Data\Default\Local Extension Settings\확장 ID\
```

Phantom 은 Linux 에서 `/home/$USER/.config/google-chrome/Default/Local Extension Settings/bfnaelmomeimhlpmgjnjophhpkkoljpa/`, macOS 에서 `Library/Application Support/Google/Chrome/Default/Local Extension Settings/bfnaelmomeimhlpmgjnjophhpkkoljpa` 에 있습니다[8]. Brave 같은 다른 Chromium 계열 브라우저는 앞부분 경로만 다르고 마지막 확장 ID 폴더 이름은 같습니다[3]. 프로필이 여럿이면 `Default`, `Profile 1` 처럼 프로필 폴더마다 따로 생기므로 모두 찾습니다.

Chrome 에서 쓰는 확장 ID 는 아래와 같습니다. 이 ID 들은 모두 정보 탈취 악성 코드 탐지 규칙의 문자열에도 들어 있습니다[5].

| 지갑 | Chrome 확장 ID | 근거 |
|---|---|---|
| MetaMask | `nkbihfbeogaeaoehlefnkodbefgpgknn` | [12][13] |
| Phantom | `bfnaelmomeimhlpmgjnjophhpkkoljpa` | [1][5][8] |
| Coinbase Wallet | `hnfanknocfeofbddgcijnmhnfnkdnaad` | [2][5] |
| Binance Wallet | `fhbohimaelbohpjbbldcngcnapndodjp` | [3][5] |
| Ronin Wallet | `fnjhmkhhmkbjkkabndcnnogagogbneec` | [3][5] |

확장 ID 는 스토어마다 다를 수 있어서, 표에 없는 브라우저(예: Edge 의 자체 스토어)에서는 ID 를 외워서 찾지 않습니다. 대신 `Secure Preferences` 의 `extensions.settings` 에 있는 확장 목록에서 manifest 의 이름을 읽어 확장 ID 를 확인하고, 그 ID 로 `Local Extension Settings` 폴더를 찾습니다. 설치 목록을 읽는 방법은 Windows 핸드북의 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)에 있습니다.

Firefox 의 지갑 확장은 설치 파일 이름으로도 찾을 수 있습니다. 같은 탐지 규칙에는 `webextension@metamask.io.xpi`, `ronin-wallet@axieinfinity.com.xpi` 처럼 Firefox 확장 ID 뒤에 `.xpi` 를 붙인 이름 2개와, 중괄호 GUID 형식의 `.xpi` 이름 9개가 들어 있습니다[5]. MetaMask 의 Firefox 확장 ID 는 `webextension@metamask.io` 입니다[12]. Firefox 의 확장 저장소는 확장 ID 가 아니라 기기마다 만든 UUID 로 이어지므로, 찾는 순서는 [MetaMask 저장 위치와 구조](metamask/storage.md)의 Firefox 부분을 따릅니다. Firefox 프로필 구조는 Windows 핸드북의 [파이어폭스](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/)에 있습니다.

스토어의 버전은 자주 바뀝니다. 2026년 9월 기준 Chrome 웹 스토어에는 Phantom 26.30.2(2026-09-17 갱신), Coinbase Wallet 확장 3.148.0(2026-09-24 갱신)이 올라 있고, Coinbase Wallet 확장의 개발자 이름은 Toshi Holdings Pte. Ltd 입니다[1][2]. 분석 대상의 설치 버전은 스토어가 아니라 그 프로필의 `Secure Preferences` 에 있는 manifest 버전으로 확인합니다.

## 구조

### 공통: 확장 폴더의 LevelDB

확장 폴더의 파일 구성과, 값을 덮어쓴 뒤에도 옛 레코드가 파일에 남는 방식은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 페이지에서 다룹니다. 한 공개 복구 도구는 이 폴더의 LevelDB 레코드를 모두 읽어, 키에 `"vault` 나 `encryptedVault`(Ronin Wallet 의 `.log` 파일) 가 들어 있고 값에 `"salt"` 가 있는 레코드를 볼트로 봅니다[4]. 지갑마다 볼트를 담는 키 이름이 다르다는 뜻입니다.

### Phantom

Phantom 의 볼트 형식은 공식 문서로 공개되지 않았습니다. 개인이 공개한 추출 도구의 README 에 시험용 볼트의 모양이 실려 있지만, 한 사람의 분석이라 굳은 사실은 아닙니다[8]. 그 모양을 값만 줄여 옮기면 아래와 같습니다.

```json
{"encryptedKey":{"digest":"sha256","encrypted":"...","iterations":10000,"kdf":"pbkdf2","nonce":"...","salt":"..."},"version":1}
```

옛 형식은 `kdf` 가 `pbkdf2` 이고, 새 형식은 `scrypt` 입니다[8]. 두 형식 모두 `encryptedKey` 안에 `digest`·`encrypted`·`iterations`·`kdf`·`nonce`·`salt` 필드가 있고, 바깥에 `version` 이 있습니다. 볼트 안에 든 것은 암호문이라 어떤 계정이 들어 있는지는 이 모양만으로 알 수 없습니다. 값의 인코딩은 공개된 자료가 없습니다. 볼트를 일반적으로 어떻게 읽는지는 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있습니다.

Phantom 이 주로 다루는 Solana 의 계정 주소는 32바이트이고, Ed25519 공개 키이거나 프로그램 파생 주소 (PDA, Program Derived Address)입니다[9]. 주소의 문자열 표기는 [주소 형식](../../01-foundations/wallets/address-formats.md)에서 다룹니다.

### Coinbase Wallet

Coinbase Wallet 확장의 내부 키 이름과 필드는 공식 문서나 공개 분석기로 공개된 것이 없습니다. 그래서 확장 폴더의 LevelDB 를 파서로 열어 키 목록부터 확인하고, 테스트용 프로필에 같은 버전의 확장을 설치해 무엇을 할 때 어떤 키가 바뀌는지 재현해서 뜻을 정합니다.

이름이 같은 iOS 앱(번들 ID `org.toshi.distribution`)은 `Documents/default/wallet-rn-v2.sqlite` 와 `Documents/mmkv/CBStore.plaintext` 에 데이터를 두고, iLEAPP 이 이 파일을 읽습니다[10]. 이 파일은 확장과 다른 제품의 저장소입니다. 확장 개발자 이름(Toshi Holdings)과 모바일 번들 ID(`org.toshi`)가 같은 계열이라는 점은 확인되지만, 저장 구조가 같다는 근거는 없습니다. 모바일 앱의 구조는 [iOS 지갑 앱](../mobile/ios-wallets.md)에 있습니다.

## 증거로서 의미

**증명하는 것.** 프로필 폴더에 지갑 확장 ID 이름의 `Local Extension Settings` 폴더가 있거나 `Secure Preferences` 의 확장 목록에 그 ID 가 있으면, 이 브라우저 프로필에 그 지갑 확장이 설치된 적이 있다는 것을 알 수 있습니다. LevelDB 에 볼트 모양의 값이 있으면 그 확장에서 지갑을 만들었거나 가져온 적이 있다는 근거가 됩니다. LevelDB 값에 평문 주소가 보이면 그 주소를 [블록 탐색기 기록](../records/block-explorers.md)과 대조해 거래를 확인할 수 있습니다.

**증명하지 못하는 것.** 폴더가 있다는 것만으로는 지갑을 만들었는지, 자산이 있었는지 알 수 없습니다. 볼트는 암호문이라 그 안에 어떤 주소가 있는지, 누가 비밀번호를 알았는지도 알 수 없습니다. 구조가 공개되지 않은 지갑의 키와 필드는 뜻을 단정할 수 없어서, 보고서에는 "이 프로필의 Phantom 확장 폴더 LevelDB 에 `encryptedKey` 필드가 들어 있는 값이 있다" 처럼 확인한 모양까지만 씁니다.

## 시각 해석

확장 설치 시각은 `Secure Preferences` 의 `extensions.settings` 에 있는 처음 설치 시각과 마지막 업데이트 시각으로 확인합니다. 이 값의 단위와 기준 시점은 Windows 핸드북의 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)에 있습니다.

MetaMask 는 설치·거래·연결 시각을 밀리초 단위 유닉스 시각으로 저장하지만([MetaMask 거래 기록과 연결한 사이트](metamask/activity.md)), 다른 확장 지갑이 어떤 필드에 어떤 기준으로 시각을 적는지는 공개된 자료가 없습니다. 숫자 값이 시각처럼 보이면 테스트용 프로필에서 알려진 시각에 같은 동작을 해 보고 단위(초·밀리초)와 기준을 확인합니다. LevelDB 파일(`.log`·`.ldb`)의 파일 시스템 시각은 LevelDB 가 파일을 새로 쓰거나 합칠 때 바뀌므로, 지갑을 쓴 시각과 바로 같지 않습니다. 기기 시계가 틀려도 블록 시각은 그대로이므로, 로컬 기록과 블록 시각을 비교하는 방법은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)을 따릅니다.

## 함정과 한계

- **이름이 같은 다른 제품.** "Coinbase" 라는 이름은 거래소 앱, 지갑 앱, 지갑 확장, Base App 에 모두 쓰입니다. Coinbase 는 Base App(이전 이름 Coinbase Wallet)을 Coinbase 계정에 연결하면 지갑 주소를 수집합니다[11]. 이 수집이 확장에도 해당하는지는 공개된 자료가 없습니다. 보고서에는 무엇을 분석했는지 확장 ID 나 번들 ID 로 적습니다.
- **스토어별 확장 ID.** 표의 ID 는 Chrome 웹 스토어 것입니다. 다른 스토어에서 받은 같은 지갑은 ID 가 다를 수 있어서, 설치 목록의 이름으로 확인합니다.
- **Phantom 형식의 근거.** 볼트 모양의 근거는 개인이 공개한 README 하나뿐입니다[8]. 판마다 필드가 다를 수 있으므로 실제 데이터의 필드를 그대로 적습니다.
- **여러 볼트.** LevelDB 에는 덮어쓴 옛 값이 남을 수 있어서 볼트 모양의 값이 여럿 나올 수 있습니다. 복구 도구가 마지막 레코드를 "Current" 로, 나머지를 "(Likely) Old" 로 붙이는 것은 레코드 순서에 따른 표시일 뿐입니다[3][4].
- **악성 코드도 같은 폴더를 노림.** Elastic 의 macOS 정보 탈취 악성 코드 탐지 규칙 `Macos_Infostealer_Wallets_8e469ea0`(2024-03-06 작성, 2025-01-30 수정)는 지갑 확장 ID 82개와 Firefox 지갑 확장 설치 파일 이름 11개를 문자열로 담고, 그중 6개 이상이 한 파일이나 메모리에 있으면 탐지합니다[5]. 이 목록에는 MetaMask·Phantom·Coinbase Wallet·Binance Wallet·Ronin Wallet 의 ID 가 모두 들어 있습니다[5]. 확장 폴더를 복사하거나 압축한 흔적이 있으면 사용자가 한 것인지 악성 코드가 한 것인지 따로 판단합니다. 조사 순서는 [악성 코드가 지갑을 노렸나](../../04-scenarios/device-use/wallet-stealer.md)에 있습니다.
- **주소는 기기 밖에도 남음.** 2023년 Chrome 웹 스토어의 인기 지갑 확장 100개를 시험한 연구에서, 89개는 manifest 에 모든 사이트에 콘텐츠 스크립트를 넣을 수 있는 권한이 있었고, 66개는 `history`·`tabs`·`activeTab` 중 하나 이상의 권한을 요청했습니다[7]. 13개는 사용자 지갑 주소를 제3자 서버에 보냈고, Coinbase Wallet 확장은 etherscan.io·bscscan.com·polygonscan.com 같은 블록 탐색기 도메인을 포함한 10곳에 보냈습니다[7]. 이 연구에서 비밀번호를 요청에 실어 보낸 확장은 없었습니다[7]. 지갑 주소가 블록 탐색기 API 같은 외부 서버 로그에 남을 수 있다는 뜻이고, 해당 서비스에 자료를 요청할 때 참고합니다.

## 직접 분석해 보기

### 헥스로 한 번

확장 폴더를 복사한 사본에서 `.log`·`.ldb` 파일을 헥스 편집기로 열고 볼트 모양의 문자열을 찾습니다. 아래는 찾을 문자열을 ASCII 로 바꾼 바이트이며, 명세(ASCII 표)로 만든 예시입니다.

```
"encryptedKey"   22 65 6E 63 72 79 70 74 65 64 4B 65 79 22
encryptedVault   65 6E 63 72 79 70 74 65 64 56 61 75 6C 74
```

`.log` 파일에는 레코드가 대체로 그대로 적혀 있어서 문자열이 이어져 보입니다. `.ldb` 파일의 블록은 압축돼 있을 수 있어서 문자열이 중간에 끊기거나 다른 바이트가 끼어 보일 수 있습니다. 이런 경우는 헥스 검색으로 위치만 찾고, 값은 LevelDB 파서로 읽습니다. 확장 ID 자체(`bfnaelmomeimhlpmgjnjophhpkkoljpa` 등)를 전체 디스크 이미지에서 문자열로 검색하면 지운 프로필이나 악성 코드가 모아 둔 압축 파일 안의 경로도 찾을 수 있습니다.

### 공개 도구로 한 번

`ccl_chrome_indexeddb` 의 `ccl_leveldb` 같은 LevelDB 파서로 확장 폴더의 원시 레코드를 모두 읽고[4], 키 이름과 값을 JSON 이나 표로 내보낸 뒤 `jq` 같은 도구로 필드를 뽑습니다. 원시 레코드에는 지운 키와 덮어쓴 옛 값도 들어 있으므로, 같은 키가 여러 번 나오면 모두 남겨 둡니다. 확장 설치 목록은 `Secure Preferences` 를 JSON 으로 읽어 `extensions.settings` 아래에서 확인합니다.

## 교차 검증

| 함께 볼 것 | 확인하는 것 | 링크 |
|---|---|---|
| `Secure Preferences` 확장 목록 | 설치 여부, 설치·업데이트 시각, 설치 버전 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) |
| 브라우저 방문 기록 | 지갑을 연결한 사이트에 언제 들어갔는지 | [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) |
| 블록 탐색기 | LevelDB 에서 찾은 주소의 거래와 블록 시각 | [블록 탐색기 기록 읽기](../records/block-explorers.md) |
| 같은 지갑의 모바일 앱 | 같은 복구 문구로 되살린 주소가 있는지 | [iOS 지갑 앱](../mobile/ios-wallets.md), [Android 지갑 앱](../mobile/android-wallets.md) |
| 악성 코드 흔적 | 확장 폴더를 모아 보낸 흔적 | [악성 코드가 지갑을 노렸나](../../04-scenarios/device-use/wallet-stealer.md) |
| MetaMask | 같은 프로필의 다른 지갑 확장 | [MetaMask](metamask/index.md) |

기기에서 지갑 흔적을 한꺼번에 찾는 순서는 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)와 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md)에 있습니다.

## 실습

테스트용 브라우저 프로필을 따로 만들고, 그 프로필에 Phantom 이나 Coinbase Wallet 확장을 설치한 뒤 새 지갑을 만들어 테스트넷에서 작은 거래를 한 번 보냅니다. 그다음 프로필 폴더의 사본으로 아래 질문을 풀어 봅니다.

1. `Local Extension Settings` 아래 어느 폴더가 생겼고, 폴더 이름이 표의 확장 ID 와 같은가?
2. `Secure Preferences` 의 확장 목록에 기록된 처음 설치 시각이 실제로 설치한 시각과 맞는가?
3. LevelDB 를 파서로 열면 볼트를 담은 키 이름은 무엇이고, Phantom 이라면 `encryptedKey` 안의 `kdf` 값은 무엇인가?
4. 비밀번호를 바꾸거나 지갑을 지우고 다시 가져온 뒤, 옛 볼트 모양의 값이 몇 개 남는가?
5. 보낸 거래의 주소나 트랜잭션 ID 가 LevelDB 값에 평문으로 남는가? 남는다면 테스트넷 블록 탐색기의 블록 시각과 비교하면 어떤 차이가 있는가?

## 참고 문헌

1. Chrome Web Store, Phantom. https://chromewebstore.google.com/detail/phantom/bfnaelmomeimhlpmgjnjophhpkkoljpa
2. Chrome Web Store, Coinbase Wallet extension. https://chromewebstore.google.com/detail/coinbase-wallet-extension/hnfanknocfeofbddgcijnmhnfnkdnaad
3. btcrecover, `docs/Extract_Scripts.md` (Usage for Metamask). https://github.com/3rdIteration/btcrecover/blob/master/docs/Extract_Scripts.md
4. btcrecover, `extract-scripts/extract-metamask-vaults.py`. https://github.com/3rdIteration/btcrecover/blob/master/extract-scripts/extract-metamask-vaults.py
5. Elastic Security, `yara/rules/Macos_Infostealer_Wallets.yar`. https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Macos_Infostealer_Wallets.yar
6. Phantom, Detecting the Provider. https://docs.phantom.com/solana/detecting-the-provider
7. Christof Ferreira Torres, Fiona Willi, Shweta Shinde, "Is Your Wallet Snitching On You? An Analysis on the Privacy Implications of Web3", arXiv, 2023. doi:10.48550/arXiv.2306.08170
8. cyclone-github, `phantom_pwn` README (Phantom 볼트 위치와 모양, 비공식). https://github.com/cyclone-github/phantom_pwn/blob/main/README.md
9. Solana Documentation, Accounts. https://solana.com/docs/core/accounts
10. iLEAPP, `scripts/artifacts/coinbaseWallet.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/coinbaseWallet.py
11. Coinbase, Privacy Policy. https://www.coinbase.com/legal/privacy
12. MetaMask Extension, `shared/constants/app.ts` (`METAMASK_PROD_CHROME_ID`). https://github.com/MetaMask/metamask-extension/blob/main/shared/constants/app.ts
13. Chrome Web Store, MetaMask. https://chromewebstore.google.com/detail/metamask/nkbihfbeogaeaoehlefnkodbefgpgknn
