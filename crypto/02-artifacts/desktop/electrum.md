---
title: "Electrum"
parent: "아티팩트 · 데스크톱 지갑"
nav_order: 130
---

# Electrum

Electrum 은 전체 블록체인을 내려받지 않고 Electrum 서버에 물어 잔액과 거래를 확인하는 비트코인 데스크톱 지갑입니다[2][15]. 지갑 파일은 기본값이 JSON 텍스트라서, 파일 전체를 암호화하지 않았다면 주소·거래 원문·라벨·청구서와 블록 시각까지 그대로 읽힙니다. 여기서는 데이터 폴더에 남는 설정·서버 목록·로그와 지갑 파일 안의 필드를 증거로 읽는 방법을 다루고, 지갑 파일 형식의 요약은 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 있습니다.

## 무엇을 기록하나 · 왜 생기나

Electrum 은 사용자 계정마다 데이터 폴더 하나를 쓰고, 그 안에 설정 파일 `config`, 최근에 연결한 서버 목록 `recent_servers`, 지갑 파일이 모인 `wallets` 폴더를 둡니다[1][2][6]. 지갑을 열어 둔 동안 내용이 바뀌면 지갑 파일을 다시 저장하므로, 파일 안의 주소 목록과 거래 목록은 마지막으로 저장한 시점의 상태입니다[9][10].

Electrum 은 서버에서 받은 거래가 블록에 들어 있는지 블록 헤더로 확인하고(단순 결제 검증, Simplified Payment Verification, SPV), 확인한 거래마다 블록 높이와 블록 헤더의 시각을 지갑 파일에 적습니다[15]. 그래서 지갑 파일만 있어도 어느 거래가 몇 번 블록에 들어갔는지 알 수 있습니다. 사용자가 붙인 라벨, 받기 요청과 보낼 청구서, 법정화폐 금액 메모도 같은 파일에 들어갑니다[14][16].

## 위치와 버전별 차이

데이터 폴더는 아래 순서로 정합니다[1]. macOS 도 POSIX 계열이라 `~/Library/Application Support` 가 아니라 `~/.electrum` 을 씁니다.

| 조건 | 데이터 폴더 |
|---|---|
| 환경 변수 `ELECTRUMDIR` 이 있음 | 그 경로 |
| Android | 앱 데이터 폴더 |
| Linux·macOS (POSIX) | `~/.electrum` |
| Windows | `%APPDATA%\Electrum`, `APPDATA` 가 없으면 `%LOCALAPPDATA%\Electrum` |
| 포터블 실행 파일 | 실행한 작업 폴더의 `electrum_data`. Windows 포터블 exe 를 더블클릭하면 exe 옆에 생깁니다 |

포터블 실행 파일은 설치 과정 없이 USB 저장 장치 같은 곳에서 바로 실행되고, 데이터도 그 옆에 쌓입니다[2][3]. 사용자 프로필에서 Electrum 폴더가 나오지 않아도 이동식 저장 장치나 내려받기 폴더에서 `electrum_data` 를 찾아봐야 합니다.

메인넷은 데이터 폴더 바로 아래를 쓰고, 다른 체인은 `testnet`, `testnet4`, `regtest`, `simnet`, `signet`, `mutinynet` 하위 폴더에 따로 `config`·`wallets` 를 둡니다[2][4]. 지갑은 기본적으로 `wallets\default_wallet` 에 만들어지지만, 사용자가 이름을 바꿔 여러 개를 만들 수 있고 명령줄 `-w` 옵션으로 아무 경로의 파일이나 열 수 있습니다[2].

| 버전 | 달라지는 점 |
|---|---|
| 2.0 이전 | 지갑 파일 `seed_version` 이 4 입니다[12] |
| 2.0 이상 | `seed_version` 이 11 인 형식을 거쳐, 2.7 이상은 최종 형식 번호를 적어 옛 버전이 파일을 덮어쓰지 못하게 합니다. 현재 코드의 최종 값은 73 입니다[12] |
| 4.4.0 이상 | 새로 만든 지갑 파일에 `db_metadata`(만든 시각, 처음 쓴 Electrum 버전)가 들어갑니다[12] |

Windows 10 에 Electrum 4.4.6 을 설치하면 지갑 파일이 `AppData\Roaming\Electrum\wallets` 에 생기고[18], Ubuntu 20.04 에 기본 설정으로 설치하면 `~/.electrum` 에 생깁니다[19].

## 구조

### 데이터 폴더

| 이름 | 내용 |
|---|---|
| `config` | 사용자 설정 JSON. 공백 4개로 들여쓰고 키를 알파벳순으로 정렬해 저장합니다[2] |
| `recent_servers` | 연결에 성공한 Electrum 서버 목록 JSON. 최근 것이 앞이고 최대 20개입니다[6] |
| `wallets/` | 지갑 파일[2] |
| `certs/` | 서버 인증서 폴더[6] |
| `blockchain_headers`, `forks/` | 내려받은 블록 헤더와 갈라진 체인의 헤더. 데이터 폴더 바로 아래에 둡니다[1][7] |
| `logs/` | 파일 로그. 설정 `log_to_file` 을 켰을 때만 생깁니다(Android 디버그 빌드는 항상)[8] |

`config` 에서 증거로 쓸 만한 키는 아래와 같습니다[2].

| 키 | 기본값 | 뜻 |
|---|---|---|
| `current_wallet` | 없음 | 마지막으로 연 지갑 경로 |
| `recently_open` | 없음 | 최근에 연 지갑 경로 목록 |
| `server`, `auto_connect`, `oneserver` | 없음, true, false | 사용자가 고른 서버, 자동 선택 여부, 한 서버만 쓰는지 |
| `proxy`, `enable_proxy` | 없음, `proxy` 가 있으면 true | 프록시(Tor 등) 설정 |
| `use_exchange_rate`, `currency`, `use_exchange` | false, `EUR`, `CoinGecko` | 환율 표시와 환율 출처 |
| `block_explorer` | `Blockstream.info` | 거래를 브라우저로 열 때 쓰는 탐색기. [블록 탐색기 기록 읽기](../records/block-explorers.md)에서 다룹니다 |
| `backup_dir`, `io_dir` | 없음, 홈 폴더 | 백업 폴더, 파일 입출력 폴더 |
| `log_to_file`, `logs_num_files_keep`, `logs_max_total_size` | false, 30, 200,000,000 | 파일 로그 설정 |
| `wallet_partial_writes` | false | 지갑 파일 부분 쓰기(실험 기능) |

`recently_open` 은 지갑을 열 때마다 그 경로를 맨 앞에 넣고, 그 순간 디스크에 없는 경로를 뺀 뒤 5개만 남깁니다[5]. 이 목록이 파일 메뉴의 최근 지갑 목록이 됩니다[17]. 목록을 고치는 것은 지갑을 열 때뿐이라, Electrum 밖에서 지운 지갑이나 떼어 낸 USB 저장 장치의 지갑 경로는 다음에 다른 지갑을 열 때까지 목록에 남아 있습니다[5]. Electrum 안에서 지갑을 지우거나 이름을 바꾸면 옛 경로도 목록에서 뺍니다[5]. 파일 이름이 점(`.`)으로 시작하는 "숨긴 지갑" 은 `current_wallet` 에도 `recently_open` 에도 적지 않습니다[1][2][5]. 명령줄 `-w` 로 지갑을 열면 `recently_open` 에는 들어가지만 `current_wallet` 은 바뀌지 않습니다[2][5].

로그 파일 이름은 `electrum_log_20260101T000000Z_1234.log` (만든 예시) 처럼 시작 시각(UTC)과 프로세스 ID 로 짓고, 한 줄은 `시각 | 레벨 | 이름 | 메시지` 모양입니다[8]. 한 파일이 커지면 `.log.1` 부터 `.log.4` 까지 돌려 씁니다[8].

### 지갑 파일

지갑 파일은 평문 JSON, 사용자 암호로 파일 전체를 암호화한 것(`BIE1`), 하드웨어 지갑의 키로 파일 전체를 암호화한 것(`BIE2`) 세 가지이고, 판별 방법과 키스토어 암호만 걸었을 때 평문으로 남는 범위는 [지갑 파일과 암호화](../../01-foundations/wallets/wallet-files.md)에 정리했습니다. 평문 JSON 도 공백 4개로 들여쓰고 키를 알파벳순으로 정렬해 저장합니다[10]. 여기서는 증거로 읽을 필드만 봅니다[12][14][16].

| 필드 | 내용 |
|---|---|
| `db_metadata` | `creation_timestamp`(만든 시각, UNIX 초), `first_electrum_version_used`(처음 쓴 버전). 4.4.0 이상에서 만든 파일에만 있습니다 |
| `genesis_blockhash` | 이 지갑이 쓰는 체인의 첫 블록 해시. 메인넷과 테스트넷 지갑을 섞어 열지 못하게 합니다 |
| `wallet_type`, `keystore` | 지갑 종류와 키스토어. 하드웨어 지갑이면 `keystore` 에 `hw_type`·`label`·`soft_device_id` 가 있습니다[13] |
| `addresses` | `receiving`(받는 주소)·`change`(거스름돈 주소) 배열. 배열 순서가 파생 번호입니다. 가져온 키 지갑은 주소 사전입니다 |
| `transactions` | txid 별 트랜잭션 원문 |
| `txi`, `txo` | txid → 내 주소 → 쓴 이전 출력과 금액 / 내 주소가 받은 출력 번호와 금액·코인베이스 여부 |
| `spent_outpoints` | 이전 txid → 출력 번호 → 그 출력을 쓴 txid |
| `addr_history` | 주소 → (txid, 높이) 목록 |
| `verified_tx3` | txid → (블록 높이, 블록 시각, 블록 안 위치, 블록 헤더 해시) |
| `tx_fees` | txid → (수수료, Electrum 이 직접 계산했는지, 입력 수) |
| `labels` | 주소나 txid → 사용자가 붙인 라벨. 줄바꿈은 공백으로 바꿔 저장합니다 |
| `fiat_value` | 통화 → txid → 사용자가 직접 적은 법정화폐 금액 |
| `frozen_addresses`, `frozen_coins`, `reserved_addresses` | 보내기에 쓰지 않도록 묶어 둔 주소·코인, 예약한 주소 |
| `payment_requests`, `invoices` | 받기 요청과 보낼 청구서. 금액(`amount_msat`), 설명(`message`), 만든 시각(`time`), 만료까지 초(`exp`, 0 은 무기한), 출력(`outputs`), 만들 때의 로컬 블록 높이(`height`) |
| `gap_limit`, `gap_limit_for_change` | 미리 만들어 두는 빈 주소 수. 기본값 20, 10 |
| `channels`, `imported_channel_backups` | 라이트닝을 쓴 경우의 채널 정보 |

주소를 만든 파생 경로와 Electrum 자체 시드가 BIP-39 와 다른 점은 [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)에서, 주소 모양은 [주소 형식](../../01-foundations/wallets/address-formats.md)에서 봅니다. `txi`·`txo`·`spent_outpoints` 의 입출력 관계는 [비트코인의 UTXO](../../01-foundations/blockchain/utxo.md) 개념 그대로입니다.

### 저장 방식과 부분 쓰기

Electrum 은 지갑을 저장할 때 `원래경로.tmp.프로세스ID` 파일에 전체 내용을 먼저 쓰고, 그 파일로 원래 파일을 바꿔 넣습니다[9]. 파일을 통째로 새로 쓰므로 옛 내용은 비할당 영역에 남을 수 있습니다.

설정 `wallet_partial_writes` 를 켜면 평문 지갑에 한해 변경분만 파일 끝에 덧붙입니다[2][9]. 파일은 JSON 객체 하나 뒤에 `,` 와 줄바꿈으로 이어진 JSON Patch 연산(`{"op": "add"|"replace"|"remove", "path": …, "value": …}`)이 계속 붙는 모양이 됩니다[10]. 파일 크기가 처음 열었을 때의 두 배를 넘으면 전체를 다시 씁니다[9]. 다시 쓰기 전까지는 사용자가 지운 라벨이나 청구서도 앞선 `add`·`replace` 연산 안에 옛 값이 남아 있습니다.

## 증거로서 의미

### 증명하는 것

- 이 사용자 프로필(또는 포터블 폴더)에서 Electrum 을 실행했다는 사실. 데이터 폴더, `config`, `recent_servers`, 블록 헤더 파일은 실행해야 생깁니다[2][6][7].
- 이 지갑 파일이 관리한 주소, 확장 공개 키(xpub), 파생 경로와 마스터 키 지문[13].
- 지갑이 자기 것으로 기록한 거래의 txid·원문·입출력 금액, 그리고 그 거래가 들어간 블록 높이·블록 시각·블록 해시[12][15].
- 사용자가 직접 입력한 라벨, 법정화폐 금액, 받기 요청·청구서의 설명과 금액[14][16]. 사용자의 의도나 거래 상대를 보여 주는 자료입니다.
- 4.4.0 이상에서 만든 지갑이면 파일을 만든 시각과 그때 쓴 Electrum 버전[12].

보고서에는 "이 기기의 Electrum 지갑 파일에 주소 A 가 받는 주소로 있고, 이 파일의 `verified_tx3` 에 txid B 가 블록 높이 C 로 기록돼 있으며, 블록체인에서 txid B 가 주소 A 로 0.01 BTC 를 보낸 거래로 확인된다(만든 예시)" 처럼 기록으로 확인되는 만큼 씁니다.

### 증명하지 못하는 것

- 주소가 `addresses` 에 있다고 그 주소로 돈을 받은 것은 아닙니다. Electrum 은 아직 쓰지 않은 주소를 받는 주소 20개, 거스름돈 주소 10개까지 미리 만들어 둡니다[14].
- `recently_open` 에 없다고 그 지갑을 안 쓴 것은 아닙니다. 5개만 남고 숨긴 지갑은 적히지 않습니다[2][5].
- `recent_servers` 에 있는 서버가 모두 지갑 주소를 받은 것은 아닙니다. Electrum 은 서버 10개 안팎에 붙지만 주소를 묻는 서버는 그중 하나이고, 나머지는 블록 헤더만 받습니다[2].
- 파일 전체를 암호화한 지갑에서는 형식·크기·파일 시스템 시각 말고는 알 수 없습니다[9].
- `tx_fees` 의 수수료는 서버가 알려 준 값일 수 있고, 그 여부는 두 번째 값(직접 계산 여부)으로 알 수 있습니다[12].
- 지갑 파일은 누가 키보드 앞에 있었는지 보여 주지 않습니다. 계정 로그인·실행 흔적과 함께 봐야 합니다.

## 시각 해석

| 값 | 기준 | 형식 |
|---|---|---|
| `verified_tx3` 의 두 번째 값 | 블록 헤더의 시각. 기기 시계와 관계없습니다[15] | UNIX 초(UTC) |
| `db_metadata.creation_timestamp` | 지갑을 만든 순간의 기기 시계[12] | UNIX 초 |
| 받기 요청의 `time` | 요청을 만든 순간의 기기 시계[14][16] | UNIX 초 |
| 청구서의 `time` | 결제 URI 에 `time` 이 있으면 돈을 받을 사람이 요청을 만들 때 넣은 값, 없으면 청구서를 저장한 순간의 이 기기 시계[14] | UNIX 초 |
| 로그 파일 이름, 로그 줄 | 기기 시계를 UTC 로 바꾼 값[8] | `%Y%m%dT%H%M%SZ`, `%Y%m%dT%H%M%S.%fZ` |

블록 시각은 채굴자가 적는 값이라 실제 시각과 차이가 날 수 있습니다. 이 점은 [블록 시각과 확정](../../01-foundations/blockchain/block-time.md)에서 다룹니다. UNIX 초는 모두 UTC 기준이므로 보고서에 현지 시각으로 옮길 때 기기 시간대를 따로 확인합니다. 지갑 파일과 `config` 의 수정 시각은 마지막 저장 시각일 뿐이고, 저장할 때마다 파일을 바꿔 넣기 때문에 파일 시스템의 생성 시각도 첫 생성 시각이 아닐 수 있습니다[9].

## 함정과 한계

- **macOS 경로.** `~/Library/Application Support` 만 찾으면 놓칩니다. `~/.electrum` 입니다[1].
- **포터블 실행.** 설치 흔적 없이 `electrum_data` 폴더가 실행 파일 옆에 생깁니다[3].
- **체인별 하위 폴더.** 테스트넷 지갑은 `testnet`·`testnet4` 같은 하위 폴더에 따로 있고, 메인넷 주소와 모양도 다릅니다[4].
- **임시 파일과 부분 쓰기.** `.tmp.프로세스ID` 파일이 남아 있거나, 부분 쓰기 파일 끝에 Patch 연산이 붙어 있으면 일반 JSON 도구가 파일을 읽지 못합니다. 이런 파일에는 지운 값이 남아 있을 수 있으므로 복사본으로 따로 봅니다[9][10].
- **로그는 기본으로 꺼져 있습니다.** 켜도 시작할 때마다 오래된 로그를 지워 최신 30개, 합계 2억 바이트까지만 남깁니다[2][8].
- **Electrum 시드와 BIP-39.** 같은 단어라도 파생 결과가 달라서, 복구 문구로 주소를 다시 계산할 때 종류를 먼저 확인해야 합니다. [복구 문구와 파생 경로](../../01-foundations/wallets/seed-derivation.md)를 봅니다.
- **복구 문구가 평문일 수 있습니다.** 암호를 걸지 않고 만든 지갑은 `keystore` 안에 복구 문구가 평문으로 들어 있고[13], Ubuntu 20.04 에 기본 설정으로 만든 지갑에서도 12단어 시드가 JSON 에 그대로 보입니다[19]. 증거 사본을 다룰 때 이 파일을 비밀 자료로 취급합니다.
- **앱을 지운 뒤.** Windows 10 에서 Electrum 4.4.6 을 제거하면 `AppData\Roaming\Electrum` 의 자료는 파일 카빙으로만 되살릴 수 있고, 카빙한 자료에서 지갑 이름과 읽을 수 있는 `recent_servers` 가 나옵니다[18]. 이 조건에서 제거 뒤 메모리에는 지갑 이름만 남고 txid 나 시드는 나오지 않습니다[18].

## 직접 분석해 보기

### 헥스로 한 번

아래 값은 Electrum 코드의 저장 방식으로 만든 예시입니다.

평문 지갑 파일은 `json.dumps(indent=4, sort_keys=True)` 로 저장하므로 첫 7바이트가 `{`, 줄바꿈, 공백 4개, 큰따옴표입니다[10].

```
7B 0A 20 20 20 20 22          {\n    "
```

부분 쓰기를 켠 파일은 본문 JSON 이 끝난 `}` 뒤에 `,` 와 줄바꿈, 그리고 `{"op"` 가 이어집니다[10]. 파일 안에서 이 바이트열을 찾으면 Patch 연산이 몇 개 붙었는지 셀 수 있습니다.

```
7D 2C 0A 7B 22 6F 70 22 3A    },\n{"op":
```

파일 전체를 암호화한 지갑은 base64 텍스트라 첫 6바이트가 `51 6B 6C 46 4D 51`(`QklFMQ`, `BIE2` 이면 `QklFMg`)입니다[9]. base64 를 풀면 아래 모양이 됩니다[11]. 풀어 낸 길이에서 4 + 33 + 32 를 뺀 값이 16의 배수이고 다섯 번째 바이트가 `02` 나 `03` 이면 이 구조가 맞습니다. 이 확인은 암호를 푸는 것이 아니라 파일 형식을 확인하는 것입니다.

| 오프셋 | 길이 | 내용 |
|---|---|---|
| 0 | 4 | `42 49 45 31` (`BIE1`) 또는 `42 49 45 32` (`BIE2`) |
| 4 | 33 | 임시 공개 키(압축 형식, `02` 또는 `03` 으로 시작) |
| 37 | 16 의 배수 | 암호문(AES-128-CBC) |
| 끝 32바이트 | 32 | HMAC-SHA256 |

평문 지갑의 `verified_tx3` 항목은 아래 모양입니다(만든 예시).

```json
"verified_tx3": {
    "5f3c…(만든 txid)…a901": [
        850123,
        1719800000,
        7,
        "0000000000000000000a…(만든 해시)"
    ]
}
```

두 번째 값 `1719800000` 은 UTC 로 2024-07-01 02:13:20 이고, 기기 시각이 아니라 블록 850123 의 헤더 시각입니다[15].

### 공개 도구로 한 번

평문 지갑과 `config`·`recent_servers` 는 JSON 뷰어나 `jq`, 파이썬 `json` 모듈로 읽습니다. 부분 쓰기 파일은 한 개의 JSON 이 아니라서 그대로는 파싱이 실패하는데, Electrum 은 파일 내용 앞뒤에 `[` 와 `]` 를 붙여 배열로 읽고 첫 요소를 본문, 나머지를 Patch 연산으로 씁니다[10]. 같은 방법으로 읽으면 연산을 적용하기 전 값과 적용한 뒤 값을 모두 볼 수 있습니다.

지갑 폴더와 데이터 폴더 전체에서 비트코인 주소·xpub 모양의 문자열을 찾는 방법은 [주소와 트랜잭션 ID 찾기](../../03-techniques/acquisition/address-carving.md)를 봅니다. Linux 에서 Electrum·Exodus 데이터 폴더를 정규식으로 검사하고 실행 중인 프로세스를 확인하는 파이썬 스캐너 코드가 [19] 의 부록에 실려 있습니다. 이 스캐너로 Ubuntu 20.04 에 기본 설정(암호 없음)으로 설치한 Electrum 의 데이터 폴더를 몇 분 간격으로 두 번 검사하면 파일 20개 중 13개, 21개 중 14개에서 주소 패턴이 나옵니다[19].

## 교차 검증

- **블록체인.** `verified_tx3` 의 블록 높이·블록 해시와 `transactions` 의 원문을 [블록 탐색기](../records/block-explorers.md)나 직접 운영하는 노드에서 조회해 같은 블록에 같은 거래가 있는지 봅니다. 지갑 주소를 묶는 방법과 한계는 [주소 묶기와 그 한계](../../03-techniques/analysis/clustering.md)에서 다룹니다.
- **네트워크 기록.** `recent_servers` 와 `config` 의 `server`·`proxy` 를 방화벽·DNS 기록과 비교합니다. `recent_servers` 에는 서버의 IP 나 도메인 이름과 포트가 들어 있습니다[6][18].
- **실행 흔적.** Windows 10 에서는 Windows 타임라인(활동 기록)으로 Electrum 실행 시작·종료 시각을 알 수 있습니다[18]. 이 기록을 읽는 법은 [윈도 타임라인 (ActivitiesCache.db)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/file-folder-usage/activitiescache-db.html), 여러 흔적을 합치는 방법은 [Windows 타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/), Linux 는 [Linux 타임라인 만들기](https://urock-ailab.github.io/forensics-handbook/linux/03-techniques/analysis/timeline.html)를 봅니다.
- **하드웨어 지갑.** `keystore` 의 `hw_type` 이 있으면 [하드웨어 지갑과 연결 흔적](../hardware/hardware-wallets.md)에서 장치 연결 기록을 함께 봅니다.
- **메신저·메일.** `labels`·청구서 `message` 에 적힌 이름이나 메모를 메신저·메일의 송금 요청과 비교합니다.
- **메모리.** 실행 중에 수집했다면 [Windows 메모리 분석](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)으로 지갑 경로와 주소 문자열을 찾습니다.

같은 분류의 [Bitcoin Core](bitcoin-core.md), [Exodus](exodus.md)와 비교하면 지갑마다 평문으로 보이는 범위가 다릅니다. 여러 흔적을 시간순으로 합치는 방법은 [암호화폐 타임라인](../../03-techniques/analysis/timeline.md), 조사 순서는 [이 기기로 지갑을 썼나](../../04-scenarios/device-use/wallet-use.md), 지갑 파일을 노린 악성 코드는 [악성 코드가 지갑을 노렸나](../../04-scenarios/device-use/wallet-stealer.md)를 봅니다. 수집할 폴더 목록은 [기기에서 지갑 흔적 찾기](../../03-techniques/acquisition/artifact-search.md)에 있습니다.

## 실습

가상 머신에 Electrum 을 설치하고 `--testnet4` 옵션으로 실행하면 실제 자산 없이 풀어 볼 수 있습니다[4].

1. 암호 없이 만든 지갑, 키스토어 암호만 건 지갑, 파일 전체를 암호화한 지갑을 하나씩 만들면 각 파일의 첫 바이트와 평문으로 보이는 필드는 어떻게 다른가?
2. `testnet4` 하위 폴더에 생긴 `config` 의 `recently_open` 은 지갑을 여섯 개 열었을 때 어떻게 바뀌는가? 파일 이름을 `.hidden` 처럼 점으로 시작하게 만든 지갑은 목록에 남는가?
3. 테스트넷 수도꼭지(faucet)로 코인을 받은 뒤 `verified_tx3` 의 블록 시각을 블록 탐색기의 블록 시각, 로그 파일의 UTC 시각과 비교하면 어떤가?
4. 받기 요청을 만들고 라벨을 붙였다가 지운 뒤, `wallet_partial_writes` 를 켠 경우와 끈 경우에 지갑 파일에 옛 라벨이 남는가?
5. Windows 포터블 exe 를 USB 저장 장치에서 실행하면 `electrum_data` 는 어디에 생기고, 사용자 프로필에는 무엇이 남는가?

## 참고 문헌

1. Electrum, `electrum/util.py`. https://github.com/spesmilo/electrum/blob/master/electrum/util.py
2. Electrum, `electrum/simple_config.py`. https://github.com/spesmilo/electrum/blob/master/electrum/simple_config.py
3. Electrum, `run_electrum`. https://github.com/spesmilo/electrum/blob/master/run_electrum
4. Electrum, `electrum/constants.py`. https://github.com/spesmilo/electrum/blob/master/electrum/constants.py
5. Electrum, `electrum/daemon.py`. https://github.com/spesmilo/electrum/blob/master/electrum/daemon.py
6. Electrum, `electrum/network.py`. https://github.com/spesmilo/electrum/blob/master/electrum/network.py
7. Electrum, `electrum/blockchain.py`. https://github.com/spesmilo/electrum/blob/master/electrum/blockchain.py
8. Electrum, `electrum/logging.py`. https://github.com/spesmilo/electrum/blob/master/electrum/logging.py
9. Electrum, `electrum/storage.py`. https://github.com/spesmilo/electrum/blob/master/electrum/storage.py
10. Electrum, `electrum/json_db.py`. https://github.com/spesmilo/electrum/blob/master/electrum/json_db.py
11. Electrum, `electrum/crypto.py`. https://github.com/spesmilo/electrum/blob/master/electrum/crypto.py
12. Electrum, `electrum/wallet_db.py`. https://github.com/spesmilo/electrum/blob/master/electrum/wallet_db.py
13. Electrum, `electrum/keystore.py`. https://github.com/spesmilo/electrum/blob/master/electrum/keystore.py
14. Electrum, `electrum/wallet.py`. https://github.com/spesmilo/electrum/blob/master/electrum/wallet.py
15. Electrum, `electrum/verifier.py`. https://github.com/spesmilo/electrum/blob/master/electrum/verifier.py
16. Electrum, `electrum/invoices.py`. https://github.com/spesmilo/electrum/blob/master/electrum/invoices.py
17. Electrum, `electrum/gui/qt/main_window.py`. https://github.com/spesmilo/electrum/blob/master/electrum/gui/qt/main_window.py
18. David Debono, Aleandro Sultana, 「Desktop Crypto Wallets: A Digital Forensic Investigation and Analysis of Remnants and Traces on end-User Machines」, Proceedings of the 10th International Conference on Information Systems Security and Privacy (ICISSP 2024), pp. 350-357, 2024, doi:10.5220/0012313000003648
19. Tomas Kovalcik, 「Digital forensics of cryptocurrency wallets」, 석사 학위 논문, Halmstad University, 2022. https://www.diva-portal.org/smash/record.jsf?pid=diva2:1671204
