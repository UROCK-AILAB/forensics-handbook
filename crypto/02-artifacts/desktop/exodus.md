---
title: "Exodus"
parent: "아티팩트 · 데스크톱 지갑"
nav_order: 140
---

# Exodus

Exodus 데스크톱 지갑은 사용자 프로필 아래 `Exodus` 데이터 폴더에 지갑 자료를 두고, 복구 문구를 바꿔 지갑을 덮어쓰면 옛 지갑 폴더를 `Backups\Wallet` 아래에 90일 동안 보관합니다. 지갑 파일은 본문이 암호화된 보안 컨테이너 (secure container, SECO)라 주소나 거래가 평문으로 거의 보이지 않습니다. 대신 파일 머리의 앱 이름·버전, 데이터 폴더가 남아 있다는 사실, 사용자가 바탕화면에 내보낸 CSV·확장 공개 키(xpub)·Safe Report 파일로 지갑 사용과 주소·거래를 확인할 수 있습니다. 앱을 제거해도 데이터 폴더가 남는 일이 많아서 제거 뒤에도 사용 흔적을 찾을 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

Exodus 는 계정 가입 없이 쓰는 비수탁형 지갑입니다. 처음 열 때 만든 12단어 비밀 키(secret key, 다른 페이지의 복구 문구와 같은 것)와 거기서 파생한 개인 키가 사용자 기기에 암호화돼 저장되고, 회사는 사용자의 키나 자산을 보관하지 않습니다[16][18]. 그래서 지갑 자료는 기기 안의 데이터 폴더에 쌓이고, 잔액과 거래 내역은 앱이 각 블록체인에서 읽어 와 보여 줍니다[16]. 암호를 설정하면 암호 없이는 앱을 열거나 비밀 키에 접근할 수 없고, 개인 메모 같은 로컬 자료는 비밀 키에서 만든 키로 암호화합니다[16].

기기에 남는 흔적은 세 종류입니다. 데이터 폴더의 지갑 파일, 지갑을 덮어쓸 때 생기는 보관본, 사용자가 메뉴에서 실행한 내보내기 파일입니다. 한 사용자 계정에는 Exodus 지갑이 하나만 있고, 같은 PC 라도 사용자 계정마다 지갑이 따로 있습니다[2][4]. 비수탁형 지갑이 무엇을 기기에 두는지는 [지갑의 종류](../../01-foundations/wallets/wallet-types.md)에서 다룹니다.

## 위치와 버전별 차이

데스크톱 데이터 폴더의 기본 위치는 아래와 같습니다[1][2]. 지갑 자료는 이 폴더 안의 `exodus.wallet` 폴더에 있습니다[1].

| OS | 데이터 폴더 |
|---|---|
| Windows | `C:\Users\사용자\AppData\Roaming\Exodus` |
| macOS | `/Users/사용자/Library/Application Support/Exodus` |
| Linux | `/home/사용자/.config/Exodus` |

폴더는 숨김 폴더 아래에 있어서 탐색기에서 숨김 항목을 켜야 보입니다[1]. 앱의 개발자 메뉴(Windows·Linux 는 Ctrl+Shift+D, macOS 는 메뉴 막대의 Exodus)에서 Data Folder > Open Data Folder 로 이 폴더를 열 수 있고, Export Zipped Data Folder 를 누르면 데이터 폴더의 zip 사본이 바탕화면에 생깁니다[1]. 그래서 바탕화면의 zip 파일도 데이터 폴더 사본일 수 있으니 함께 수집합니다.

다른 12단어 비밀 키로 복원하거나 다른 Exodus 지갑과 동기화하면 새 지갑이 옛 지갑을 덮어씁니다[1]. 이때 Exodus 는 옛 지갑 자료를 옛 비밀 키까지 포함해 보관합니다[1]. 데스크톱에서는 데이터 폴더의 `Backups\Wallet` 아래에 시각이 붙은 폴더가 하나 이상 생기고, 폴더마다 옛 `exodus.wallet` 폴더가 들어 있습니다[1]. 데스크톱 보관본은 덮어쓴 뒤 90일 동안만 유지됩니다[1]. 폴더 이름의 시각 형식은 공개 문서에 없으므로 실제 데이터에서 폴더 이름과 폴더의 파일 시스템 시각을 함께 봅니다. 모바일 앱은 보관 기간을 영구·1개월·3개월·6개월 가운데 고르는 방식이고[1], 모바일 지갑은 [Android 지갑 앱](../mobile/android-wallets.md)·[iOS 지갑 앱](../mobile/ios-wallets.md)에서 다룹니다.

사용자가 내보내기 메뉴를 쓰면 바탕화면에 `exodus-exports` 폴더가 생기고 그 안에 파일이 쌓입니다. 거래 내역 CSV[13], 주소 목록 CSV[9], xpub·zpub 이 든 `.txt` 파일[10], `exodus-report-SAFE-(날짜+시각).json` 이름의 Safe Report[14]가 여기에 저장됩니다. 주소 목록과 xpub 내보내기는 데스크톱에서만 할 수 있어서, 모바일 사용자가 이 파일을 만들려면 데스크톱과 동기화해야 합니다[9][10].

## 구조

### 데이터 폴더

공개 문서에는 데이터 폴더 안 파일 목록이 없습니다. Windows 10 에서 Exodus 23 버전대를 시험한 연구에서는 `exodus.wallet` 폴더에 `info.seco`, `seed.seco`, `storage.seco`, `twofactor-secret.seco`, `twofactor.seco` 다섯 파일이 있었고, 내용은 모두 암호화돼 있었습니다[3]. 같은 연구에서 데이터 폴더에는 389바이트의 `Local State` 파일(운영체제가 암호화한 키가 든 파일), 로컬 저장소 폴더의 `LOCK`·`LOG`·`CURRENT` 와 `.db` 파일, `Code Cache`·`Dawn Cache`·`Cache` 폴더도 있었습니다[3]. 이 이름들은 크롬 계열 앱 폴더에서 쓰는 이름과 같으므로, 구조와 읽는 법은 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/)와 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 페이지를 봅니다.

Linux(Ubuntu)에서 암호 없이 기본 설정으로 시험한 연구에서는 Exodus 데이터 폴더의 파일 143개 가운데 5개, 두 번째 실행 때 161개 가운데 8개에서만 비트코인 관련 문자열 패턴(주로 주소)이 나왔고, 설정은 사람이 읽을 수 없는 이진 형식이었습니다[4]. 같은 조건의 Electrum 폴더는 파일의 절반 정도에서 이런 패턴이 나왔습니다[4]. 그래서 Exodus 폴더는 문자열 검색만으로 주소를 얻기 어렵습니다.

### 보안 컨테이너 (SECO)

Exodus 는 파일에 암호화 컨테이너를 쓰는 secure-container·seco-file 라이브러리를 공개했고, 이 형식의 파일은 매직 `SECO` 로 시작합니다[5][6]. 파일은 머리(header) 224바이트, 체크섬 32바이트, 암호화 설정(메타데이터) 256바이트, 본문 길이 4바이트(UInt32 빅엔디언), 암호화된 본문 순서로 이어집니다[5]. 머리에는 `versionTag`(`seco-v0-scrypt-aes`)·`appName`·`appVersion` 문자열이 평문으로 들어 있어서, 암호 없이도 어떤 앱의 어떤 버전이 파일을 썼는지 읽을 수 있습니다[5]. 오프셋별 구조와 헥스 예시는 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있으므로 여기서는 되풀이하지 않습니다.

체크섬은 메타데이터, 본문 길이, 본문을 이어 붙인 값의 SHA-256 입니다[5]. 파일에서 보면 오프셋 0x100 부터 본문 끝까지를 해시한 값이 오프셋 0xE0~0xFF 의 32바이트와 같아야 합니다. 라이브러리는 이 값이 다르면 "seco checksum does not match" 오류를 내고 파일을 읽지 않으므로[5][6], 체크섬 비교로 파일이 손상됐거나 일부만 쓰였는지를 암호 없이 판별할 수 있습니다.

Exodus 가 앱의 어느 파일에 이 라이브러리를 쓰는지는 공개 문서에 없습니다. seco-keyval 의 사용 예에 `appName: 'exodus'` 가 나오지만 이 값은 예시 코드에 나온 것입니다[7]. 그래서 `.seco` 확장자만 보고 판단하지 말고, 파일 앞 4바이트가 `SECO` 인지와 `appName` 값을 직접 확인합니다.

### 파생 경로와 주소

Exodus 는 12단어 비밀 키에서 주소와 개인 키를 파생하는 계층 결정적 지갑 (HD wallet)이고, 파생 경로는 주로 BIP-44 를, 코인 번호는 SLIP-0044 를 따릅니다[8][16]. 기본 포트폴리오의 기본 주소 경로는 아래와 같습니다[8].

| 자산 | 주소 모양 | 경로 |
|---|---|---|
| 비트코인 Legacy | `1…` | `m/44'/0'/0'/0/0` |
| 비트코인 SegWit | `bc1q…` | `m/84'/0'/0'/0/0` |
| 비트코인 Taproot | `bc1p…` | `m/86'/0'/0'/0/0` |
| 이더리움과 같은 경로를 쓰는 체인(Arbitrum One·Base·BNB Smart Chain·Optimism·Polygon 등) | `0x…` | `m/44'/60'/0'/0/0` |
| 라이트코인 | — | `m/44'/2'/0'/0/0` |
| Solana | — | `m/44'/501'/0'/0/0` (비표준) |

경로의 account 자리는 포트폴리오 번호라서 기본 포트폴리오가 0 이고 포트폴리오를 추가할 때마다 1씩 늘어납니다[8]. change 는 기본 0 이고 일부 UTXO 자산의 거스름돈 주소면 1, index 는 기본 0 이고 여러 주소를 쓰는 자산에서 새 주소를 만들 때마다 늘어납니다[8]. 여러 주소 기능은 켜야 동작하고, 켜면 받을 때마다 새 주소를 만듭니다[9]. 이 기능을 켜지 않은 지갑은 자산마다 같은 주소를 계속 썼을 가능성이 큽니다. Solana 처럼 비표준 경로를 쓰는 자산은 같은 비밀 키를 다른 지갑에 넣으면 그 자산이 보이지 않을 수 있습니다[8]. 파생 경로 자체는 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에서 다룹니다.

### 내보내기 파일

거래 내역 CSV 는 데스크톱 History 화면의 Export All Transactions·Export Sent·Export Received·Export Swapped, 또는 자산 화면의 Export Transactions 로 만들고, 포트폴리오와 자산을 골라 내보낼 수 있습니다[13]. 거래 내보내기 모듈은 개인 메모(`personalNotesAtom`)와 주문(`ordersAtom`)을 입력으로 받고 CSV 생성은 각 앱이 맡으므로[15], CSV 에 메모나 주문 정보가 함께 들어갈 가능성이 있습니다. 열 이름은 공개 문서에 없으므로 실제 파일의 첫 줄로 확인합니다.

xpub·zpub 파일은 자산 화면의 Export XPub 으로 만들고, 비트코인은 `.txt` 파일에 xpub 과 zpub 이 함께 들어갑니다[10]. Exodus 문서는 xpub 을 Legacy(`1…`) 주소용, zpub 을 SegWit(`bc1q…`)과 Taproot(`bc1p…`) 주소용이라고 설명합니다[10]. 확장 키 접두사를 정리한 SLIP-0132 에서 `zpub` 은 P2WPKH(`m/84'/0'`)용이고 Taproot 용 접두사는 따로 없으며[11], BIP-86 시험 벡터는 Taproot 계정 키(`m/86'/0'/0'`)를 `xpub` 접두사로 표시합니다[12]. 그래서 Exodus 가 내보낸 zpub 을 다른 도구에 넣으면 `bc1q` 주소만 나오고 `bc1p` 주소는 빠질 수 있습니다. Taproot 주소가 필요하면 Safe Report 나 주소 목록 CSV 의 주소를 씁니다.

Safe Report JSON 에는 모든 공개 주소와 xpub·zpub, 전체 거래 내역, 설정 파일(Exodus 버전 이력, 운영체제, 다운로드·복원 날짜 같은 지갑 이벤트), 스왑 주문 이력, 법정화폐 매수·매도 주문 이력, 지갑 오류가 들어갑니다[14]. 12단어 비밀 키, 개인 키, 암호는 들어가지 않고, 법정화폐 주문 이력에도 카드·은행 정보는 없습니다[14]. Exodus 는 다 쓴 Safe Report 파일을 지우고 휴지통도 비우라고 안내하므로[14], 삭제된 파일과 휴지통도 찾아봅니다.

## 증거로서 의미

### 증명하는 것

사용자 프로필에 Exodus 데이터 폴더와 `exodus.wallet` 폴더가 있으면 그 계정에서 Exodus 지갑을 만들거나 복원했다는 것이 확인됩니다. SECO 파일 머리의 `appName`·`appVersion` 으로 그 파일을 쓴 앱과 버전을 알 수 있습니다[5]. `Backups\Wallet` 아래 시각 폴더가 있으면 다른 비밀 키로 복원하거나 다른 지갑과 동기화해서 지갑을 덮어쓴 적이 있다는 뜻이고, 보관 기간이 90일이라 그 일이 수집 시점에서 90일 안쪽에 있었을 가능성이 큽니다[1]. 보관 폴더가 여러 개면 서로 다른 지갑을 여러 번 바꿔 썼을 수 있습니다.

`exodus-exports` 의 파일은 사용자가 내보내기 메뉴를 실행했다는 것과 그 시점에 지갑에 있던 주소·xpub·거래 내역을 보여 줍니다[9][10][13]. Safe Report 는 여기에 Exodus 버전 이력과 다운로드·복원 날짜, 스왑·법정화폐 주문 이력까지 더해 줍니다[14]. 이 주소와 xpub 을 블록 탐색기에서 조회하면 거래와 잔액을 확인할 수 있습니다.

### 증명하지 못하는 것

SECO 본문은 암호화돼 있어서 파일만으로는 어떤 자산을 얼마나 가졌는지, 누구와 거래했는지 알 수 없습니다. 내보내기 파일이 없으면 주소를 얻기 어렵고, 데이터 폴더를 문자열로 검색해도 주소가 나오는 파일은 적습니다[4]. 데이터 폴더가 있다는 것만으로 그 사람이 직접 지갑을 조작했다거나 거래를 보냈다는 것까지는 확인되지 않습니다.

Exodus 화면과 CSV 에 거래가 없다고 거래가 없었던 것은 아닙니다. 일부 네트워크는 "light support" 라서 보낸 거래만 보여 주고, 그 내역은 기기에만 저장돼 기기 사이에 동기화되지 않으며 지갑을 지우거나 복원하면 사라집니다[13]. 다른 네트워크는 최근 거래만 보여 주는데, 예를 들어 Base 는 약 1년 반, BNB Smart Chain 은 약 2년 치만 보여 줍니다[13]. Exodus 가 더 이상 지원하지 않는 자산도 내보낸 거래 내역에서 빠집니다[13]. 이런 자산은 주소로 블록 탐색기를 조회해 확인합니다.

보고서에는 "이 사용자 프로필에 Exodus 데이터 폴더가 있고, 바탕화면 `exodus-exports` 의 주소 목록에 이 주소가 있으며, 이 주소에서 이 시각에 이 금액을 보낸 트랜잭션이 블록체인에 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

거래 내역 CSV 의 시각은 UTC 입니다. 내보내는 순간 기기의 현지 시각을 UTC 로 바꿔 적으므로[13], 기기의 시간대 설정이 틀렸다면 UTC 값도 어긋날 수 있습니다. CSV 시각은 블록의 시각과 비교해 확인합니다. 블록 시각의 의미는 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다룹니다.

Safe Report 파일 이름에는 만든 날짜와 시각이 들어가지만 형식과 시간대는 공개 문서에 없습니다[14]. `Backups\Wallet` 의 폴더 이름에도 시각이 붙지만 형식이 공개돼 있지 않습니다[1]. 두 경우 모두 실제 파일 이름을 파일 시스템의 생성 시각과 비교해 시간대를 판단합니다. 보관 폴더가 만들어진 시각은 지갑을 덮어쓴 시점에 가깝고, `exodus-exports` 안 파일의 생성 시각은 사용자가 내보내기를 실행한 시점에 가깝습니다. `.seco` 파일의 수정 시각은 앱이 그 파일을 마지막으로 쓴 시점이지만, 무엇을 할 때 어떤 파일을 다시 쓰는지는 공개 문서에 없습니다.

Safe Report 의 버전 이력과 다운로드·복원 날짜[14]는 앱이 기록한 사건 시각이라 파일 시스템 시각과 따로 비교할 수 있습니다. 여러 출처의 시각을 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 함정과 한계

**앱 제거와 데이터 폴더.** Exodus 의 두 지원 문서는 앱 제거 뒤의 결과를 다르게 설명합니다. 지갑 삭제 문서는 데스크톱 지갑 자료가 별도 폴더에 있어 앱을 제거해도 보통 지워지지 않고, 지우려면 데이터 폴더를 직접 삭제해야 한다고 설명합니다[2]. 덮어쓴 지갑 복구 문서는 Exodus 를 제거하면 보관된 지갑 자료가 영구 삭제된다고 설명합니다[1]. Windows 10 에서 Exodus 23 버전대를 제거한 시험에서는 설치 프로그램 목록과 Windows 검색에서는 사라졌지만 `AppData\Roaming\Exodus` 숨김 폴더가 이전과 같은 내용으로 남았습니다[3]. 제거했다고 사용 흔적이 없다고 판단하지 말고 데이터 폴더와 `Backups` 폴더를 직접 확인합니다.

**사용자가 직접 지운 폴더.** Exodus 는 새 지갑을 만들거나 Exodus 를 그만 쓸 때 데이터 폴더를 통째로 지우거나 휴지통으로 옮기라고 안내합니다[2]. 폴더가 없으면 휴지통, 삭제된 파일, 바탕화면의 데이터 폴더 zip 사본을 찾습니다.

**보관본의 기한.** 데스크톱 보관본은 덮어쓴 뒤 90일만 남습니다[1]. 보관 폴더가 없다고 지갑을 바꾼 적이 없다고 볼 수는 없습니다.

**파일 목록은 연구 결과.** `exodus.wallet` 안의 다섯 파일 이름은 한 연구의 Windows 시험 결과입니다[3]. 버전에 따라 파일 구성이 다를 수 있으므로 실제 폴더의 파일을 모두 목록으로 만들고, 각 파일의 앞 4바이트와 `appVersion` 을 확인합니다.

**zpub 과 Taproot.** 위 내보내기 파일 절에서 설명한 것처럼 Exodus 문서의 zpub 설명과 SLIP-0132 의 정의가 다릅니다[10][11]. zpub 하나로 주소를 모두 얻었다고 보지 말고, Taproot 주소가 따로 있는지 Safe Report 나 주소 목록으로 확인합니다.

**화면에 없는 거래.** light support 네트워크와 최근 거래만 보여 주는 네트워크는 앱 기록이 불완전합니다[13]. 거래 내역은 블록체인에서 다시 확인합니다.

**본문 복호.** 이 페이지는 SECO 본문을 푸는 방법을 다루지 않습니다. 암호가 걸린 지갑은 머리·체크섬·파일 시스템 시각과 내보내기 파일, 다른 기록으로 판단합니다.

## 직접 분석해 보기

### 헥스로 한 번

`.seco` 파일의 사본을 헥스 편집기로 열어 아래 순서로 봅니다. 오프셋은 secure-container 코드의 길이 상수로 계산한 값입니다[5].

1. 오프셋 0x00 의 4바이트가 `53 45 43 4F`(`SECO`)인지 확인합니다.
2. 오프셋 0x0C 의 1바이트가 `versionTag` 길이이고, 보통 `12`(10진수 18) 다음에 `seco-v0-scrypt-aes` 가 옵니다.
3. 그 뒤의 1바이트 길이와 문자열이 `appName`, 다시 1바이트 길이와 문자열이 `appVersion` 입니다.
4. 오프셋 0x200 의 4바이트(UInt32 빅엔디언)가 본문 길이입니다. 파일 크기가 516 + 본문 길이와 같은지 봅니다.
5. 오프셋 0x100 부터 본문 끝까지의 SHA-256 을 계산해 오프셋 0xE0~0xFF 의 32바이트와 비교합니다.

아래는 위 순서를 그대로 옮긴 파이썬 코드입니다. 파일을 읽기만 하고 본문은 풀지 않습니다.

```python
import hashlib, struct, sys

d = open(sys.argv[1], "rb").read()
assert d[:4] == b"SECO", "SECO 파일이 아님"
p = 12
for name in ("versionTag", "appName", "appVersion"):
    n = d[p]; print(name, d[p+1:p+1+n].decode("utf-8", "replace")); p += 1 + n
blob_len = struct.unpack(">I", d[512:516])[0]
end = 516 + blob_len
print("본문 길이", blob_len, "파일 크기", len(d), "남는 바이트", len(d) - end)
print("체크섬 일치", hashlib.sha256(d[256:end]).digest() == d[224:256])
```

체크섬이 맞지 않거나 파일 크기가 계산과 다르면 손상됐거나 쓰기 도중에 멈춘 파일일 수 있습니다. 헤더 부분의 헥스 모양은 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)의 예시를 봅니다.

### 공개 도구로 한 번

내보내기 CSV 는 표 계산 프로그램으로, Safe Report 는 JSON 뷰어로 엽니다. 데이터 폴더의 로컬 저장소와 캐시는 크롬 계열 앱 폴더를 읽는 도구로 봅니다([크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/)). 데이터 폴더 전체에서 주소·xpub 문자열을 찾는 방법은 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)에서, 기기 전체에서 SECO 파일을 찾는 방법은 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)에서 다룹니다.

## 교차 검증

- **블록 탐색기.** 내보낸 주소·xpub, Safe Report 의 주소로 거래와 잔액을 조회합니다([블록 탐색기 기록 읽기](../records/block-explorers.md)). 여러 주소를 쓴 지갑의 주소 묶음은 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)를 봅니다.
- **브라우저 기록.** Windows 10 에서 Exodus 로 Ramp 를 통해 SOL 을 산 시험에서는 브라우저 기록에 `buy.ramp.network` 가 남고, 캐시된 이미지에서 결제한 유로 금액·코인 종류·환율이 나왔습니다[3]. 같은 시험에서 메모리에는 카드 정보 일부와 이메일·주소·이름·금액·시각이 있었습니다[3]. [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)와 [메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/) 페이지를 함께 봅니다.
- **네트워크 기록.** Exodus 앱은 대부분의 기능에 `*.a.exodus.io`·`*.exodus.io` 도메인을 씁니다[17]. DNS 기록·방화벽 로그에 이 도메인이 있으면 앱을 실행한 시점을 추정할 수 있고, 위 시험에서도 DNS 기록으로 설치와 사용이 확인됐습니다[3].
- **설치 흔적과 Safe Report.** Safe Report 의 버전 이력과 다운로드·복원 날짜를 설치 프로그램 기록·파일 시스템 시각과 비교합니다[14].
- **하드웨어 지갑.** Exodus 는 Trezor 하드웨어 지갑의 자산도 관리할 수 있으므로[18], 연결 흔적은 [하드웨어 지갑과 연결 흔적](../hardware/hardware-wallets.md)에서 봅니다.
- **회사 자료.** Exodus 는 계정이 없어서 사용자가 연락하지 않았다면 이름·이메일·주소·신분증 번호를 갖고 있지 않습니다[18]. 지원팀에 문의한 사용자라면 이메일 주소와 대화 내용이 남아 있고, 앱 사용·성능 통계도 수집하는데 사용자가 설정에서 끌 수 있습니다[16]. 수사기관 요청은 Kodex 로 받고 정부 도메인 이메일에서 보낸 요청에만 답하며, 요청서에 관련 거래를 담은 CSV 나 엑셀 파일을 넣으라고 안내합니다[18]. 거래소 자료와의 차이는 [거래소가 제공하는 자료](../records/exchange-records.md)를 봅니다.
- **악성 코드.** 지갑 파일을 노린 악성 코드 흔적은 [악성 코드가 지갑을 노렸나](../../04-scenarios/device-use/wallet-stealer.md)에서 다룹니다.

같은 분류의 [Bitcoin Core](bitcoin-core.md), [Electrum](electrum.md) 페이지와 비교하면 지갑 파일에서 평문으로 보이는 범위가 지갑마다 크게 다르다는 것을 알 수 있습니다. 조사 순서는 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md)를 봅니다.

## 실습

가상 머신에 Exodus 데스크톱을 설치하고 아래 질문을 풀어 봅니다. 자산을 넣지 않아도 대부분 확인할 수 있습니다.

1. 새 지갑을 만든 직후 데이터 폴더와 `exodus.wallet` 폴더에는 어떤 파일이 있고, 각 파일의 앞 4바이트와 `appName`·`appVersion` 은 무엇인가?
2. 암호를 설정하기 전과 뒤에 `.seco` 파일의 크기·수정 시각·체크섬 결과는 어떻게 달라지는가?
3. 다른 12단어 비밀 키로 복원하면 `Backups\Wallet` 아래 폴더 이름은 어떤 형식이고, 그 시각은 파일 시스템 시각·기기 시간대와 어떤 관계인가?
4. 주소 목록·xpub·Safe Report 를 내보내면 `exodus-exports` 에 어떤 이름의 파일이 생기는가? 비트코인 `.txt` 파일의 zpub 으로 다른 도구에서 만든 주소가 Safe Report 의 `bc1q`·`bc1p` 주소와 일치하는가?
5. 앱을 제거한 뒤 데이터 폴더와 `Backups` 폴더는 남는가? 결과를 [1]과 [2]의 설명과 비교합니다.
6. 기기 시간대를 바꾼 뒤 거래 내역 CSV 를 내보내면 시각 값이 달라지는가?

## 참고 문헌

1. Exodus Support, How do I rescue an overwritten wallet? https://support.exodus.com/article/204-how-to-rescue-an-overwritten-wallet
2. Exodus Support, How do I delete my wallet and create a new one? https://support.exodus.com/article/224-new-secret-phrase
3. David Debono, Aleandro Sultana, "Desktop Crypto Wallets: A Digital Forensic Investigation and Analysis of Remnants and Traces on end-User Machines", Proceedings of the 10th International Conference on Information Systems Security and Privacy (ICISSP 2024), pp. 350-357, 2024. doi:10.5220/0012313000003648
4. Tomas Kovalcik, "Digital forensics of cryptocurrency wallets", 석사 학위 논문, Halmstad University, 2022. https://www.diva-portal.org/smash/record.jsf?pid=diva2:1671204
5. Exodus, secure-container (README.md, src/header.js, src/file.js, src/metadata.js, src/index.js). https://github.com/ExodusMovement/secure-container/blob/master/README.md , https://github.com/ExodusMovement/secure-container/blob/master/src/header.js , https://github.com/ExodusMovement/secure-container/blob/master/src/file.js , https://github.com/ExodusMovement/secure-container/blob/master/src/metadata.js , https://github.com/ExodusMovement/secure-container/blob/master/src/index.js
6. Exodus, seco-file (README.md, src/index.js). https://github.com/ExodusMovement/seco-file/blob/master/README.md , https://github.com/ExodusMovement/seco-file/blob/master/src/index.js , https://docs.exodus.com/open-source/hydra/libraries/seco-file
7. Exodus, seco-keyval. https://docs.exodus.com/open-source/hydra/libraries/seco-keyval
8. Exodus Support, Derivation paths in Exodus. https://support.exodus.com/article/1795-derivation-paths-in-exodus
9. Exodus Support, How can I export a list of my wallet addresses? https://support.exodus.com/article/702-how-can-i-export-a-list-of-my-wallet-addresses
10. Exodus Support, How do I export my xpub or zpub? https://exodus.com/support/article/112-how-to-export-your-xpub-or-zpub-key
11. SLIP-0132, Registered HD version bytes for BIP-0032. https://github.com/satoshilabs/slips/blob/master/slip-0132.md
12. BIP-86, Key Derivation for Single Key P2TR Outputs. https://github.com/bitcoin/bips/blob/master/bip-0086.mediawiki
13. Exodus Support, How do I export my transaction history? https://www.exodus.com/support/en/articles/8598673-how-do-i-export-my-transaction-history
14. Exodus Support, Safe Report. https://support.exodus.com/article/191-safe-report
15. Exodus, @exodus/export-transactions. https://docs.exodus.com/open-source/hydra/features/export-transactions
16. Exodus Support, What information does Exodus have access to? https://support.exodus.com/article/138-what-information-does-exodus-have-access-to
17. Exodus Support, Which domains does Exodus use? https://www.exodus.com/support/en/articles/8598740-which-domains-does-exodus-use
18. Exodus, Legal Inquiries. https://www.exodus.com/legal-inquiries
