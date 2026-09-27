---
title: "볼트와 암호화"
parent: "MetaMask"
grand_parent: "아티팩트 · 브라우저 확장 지갑"
nav_order: 170
---

# 볼트와 암호화 (Vault)

MetaMask 확장은 복구 문구와 가져온 개인 키를 키링 배열로 묶어 암호화한 뒤, 그 결과를 `KeyringController.vault` 에 문자열 하나로 저장합니다[1][2]. 볼트는 base64 필드 `data`·`iv`·`salt` 와 새 형식에만 있는 `keyMetadata` 로 이루어진 JSON 이라서, 열지 않아도 형식의 세대와 PBKDF2 반복 횟수, 볼트가 몇 개 남아 있는지는 알 수 있습니다[1][6]. 이 페이지는 볼트 안에 무엇이 들어 있는지, 저장소에서 어떤 모양으로 보이는지, 볼트가 언제 다시 쓰이는지, 볼트 밖에서 평문으로 확인할 수 있는 것을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

MetaMask 는 계정 묶음 하나를 키링 (keyring)이라고 부릅니다. 복구 문구로 만든 계정, 가져온 개인 키, 하드웨어 지갑 연동은 서로 다른 종류의 키링입니다[3]. 볼트 (vault)는 이 키링들을 직렬화한 배열을 사용자가 정한 비밀번호로 암호화한 문자열입니다[2]. 볼트는 지갑을 처음 만들 때 생기고 저장소에 남아 있어서, 브라우저를 닫았다 열어도 비밀번호만 넣으면 계정이 다시 나타납니다[2].

직렬화한 키링 하나는 `type`·`data`·`metadata` 필드로 이루어진 객체이고, `metadata` 에는 키링 ID `id` 와 이름 `name` 이 들어갑니다[2]. `type` 에 들어가는 문자열은 다음과 같습니다.

| `type` | 뜻 |
|---|---|
| `HD Key Tree` | 복구 문구로 만든 키링[3] |
| `Simple Key Pair` | 가져온 개인 키[3] |
| `Snap Keyring` | 스냅 (Snap, MetaMask 에 기능을 더하는 모듈)이 관리하는 계정[3] |
| 하드웨어 지갑 종류 | Ledger·Trezor 같은 하드웨어 지갑 연동[3] |

복구 문구 키링의 `data` 에는 복구 문구(`mnemonic`, 숫자 배열), 계정 수 `numberOfAccounts`, 파생 경로 `hdPath` 가 들어가고, 파생 경로 기본값은 `m/44'/60'/0'/0` 입니다[4]. 현재 코드는 볼트를 다시 쓸 때 복구 문구 키링이 하나도 없으면 오류를 내므로, 정상적으로 쓰인 볼트에는 복구 문구 키링이 적어도 하나 있습니다[2]. 이 내용은 모두 암호문 안에 있어서 비밀번호 없이는 보이지 않습니다. 파생 경로의 뜻은 [복구 문구와 파생 경로](../../../01-foundations/wallets/seed-derivation.md) 페이지에서 다룹니다.

## 위치와 버전별 차이

볼트는 확장 저장소의 `KeyringController` 상태 안에 있습니다. 저장 방식이 옛 방식이면 `data` 키의 JSON 안에, 새 방식이면 최상위 `KeyringController` 키 안에 있습니다. MetaMask 가 따로 여는 IndexedDB `metamask-backup` 에도 `KeyringController` 사본이 있어서 볼트가 두 곳 이상에 있을 수 있습니다[8]. 브라우저별 폴더 경로와 두 저장 방식의 구분은 [저장 위치와 구조](storage.md) 페이지에서 다룹니다.

볼트 형식은 시기에 따라 세 가지로 나뉩니다.

| 형식 | 모양 | 판별 |
|---|---|---|
| 아주 옛 평문 형식 | `{"wallet-seed":"…"}` 처럼 복구 문구가 평문으로 들어 있습니다[6]. | `wallet-seed` 필드가 있으면 이 형식입니다[6]. |
| 옛 암호화 형식 | `data`·`iv`·`salt` 만 있습니다[1]. | `keyMetadata` 가 없으면 라이브러리는 PBKDF2 10,000회로 봅니다[1]. |
| 새 암호화 형식 | `data`·`iv`·`keyMetadata`·`salt` 가 있습니다[1]. | `keyMetadata.params.iterations` 에 반복 횟수가 적혀 있습니다[1]. |

새 형식의 반복 횟수는 출처마다 기본값이 다릅니다. 암호화 라이브러리 `@metamask/browser-passworder` 의 기본값은 900,000회이고[1], MetaMask 지갑 초기화 코드(`@metamask/wallet`)는 따로 지정하지 않으면 600,000회로 만듭니다[5]. 버전마다 달라질 수 있으므로 기본값을 외우지 말고 볼트의 `keyMetadata` 를 직접 읽습니다.

모바일 MetaMask 의 볼트는 필드 이름이 다릅니다. iOS 백업의 `persist-root` 에서 보이는 볼트는 `cipher`·`iv`·`salt`·`lib` 필드로 이루어지고, `iv` 는 32자 헥스 문자열입니다[7]. 확장 볼트와 같은 방법으로 읽으면 안 되며, 모바일 쪽은 [iOS 지갑 앱](../../mobile/ios-wallets.md) 페이지에서 다룹니다.

## 구조

### 암호화 결과 필드

암호화는 PBKDF2 로 비밀번호에서 256비트 키를 만들고 AES-GCM 으로 암호화합니다[1]. 결과 JSON 의 필드는 다음과 같습니다.

| 필드 | 내용 | 모양 |
|---|---|---|
| `data` | 키링 배열 JSON 을 암호화한 값[1] | base64. 길이는 키링 양에 따라 다릅니다. |
| `iv` | 암호화할 때마다 새로 만드는 무작위 16바이트[1] | base64 24자, `==` 로 끝납니다(명세로 계산한 값). |
| `keyMetadata` | 키 유도 방식[1] | `{"algorithm":"PBKDF2","params":{"iterations":N}}`. 옛 형식에는 없습니다. |
| `salt` | 키를 만들 때 쓰는 무작위 32바이트[1] | base64 44자, `=` 로 끝납니다(명세로 계산한 값). |

암호화 함수가 `data`·`iv` 를 먼저 만들고 `keyMetadata` 를 붙인 뒤, 마지막에 `salt` 를 넣습니다[1][2]. 그래서 저장된 문자열은 `{"data":` 로 시작하고 `salt` 값으로 끝나며, 파일 안의 이스케이프된 모양에서는 `salt` 값 뒤의 `=\"}` 가 볼트의 끝입니다[1][7].

### 저장소 안의 모양

`KeyringController` 는 암호화 결과 객체를 `JSON.stringify` 로 한 번 문자열로 만든 다음 `vault` 에 넣습니다[2]. 이 상태 전체가 다시 JSON 으로 저장되므로, 파일에서는 볼트 안쪽의 따옴표가 역슬래시로 이스케이프된 모양으로 보입니다[6].

```text
"KeyringController":{"vault":"{\"data\":\"AfRfT9PYdrMJrUzR9QqUfrUGVj28ohIlPDmTPJDuI1NcPvoMwwq6pn7WASw31Drk\",\"iv\":\"BNmtDmRaXaQw2YXmbklWaw==\",\"keyMetadata\":{\"algorithm\":\"PBKDF2\",\"params\":{\"iterations\":600000}},\"salt\":\"uaA28XyeGLMBJ1P0TVPJITirg5kuhRQRxKNgzEjlJd4=\"}"}
```

위 값은 만든 예시이고, 실제 `data` 는 이보다 훨씬 깁니다. LevelDB 파일 안에서 볼트는 다음 모양으로 나옵니다[6].

| 모양 | 나오는 곳(예) |
|---|---|
| `"KeyringController":{"vault":"{…}"` | Linux Chromium `.log` |
| 위 모양에 `\"keyMetadata\":` 가 들어간 것 | macOS `.log`, 새 암호화 형식 |
| `KeyringController` 안에 `keyringsMetadata` 필드가 더 있는 것 | macOS `.log` |
| `Keyring` 뒤에 숫자가 오고, 압축 흔적 사이에 `data`·`iv`·`salt` 가 흩어진 것 | Windows `.ldb` |
| 최상위 `KeyringController` 키 값 안의 `"vault":"…"` | 새 저장 방식 `.log`, Windows |

`.ldb` 는 블록이 압축되어 있어 필드 이름과 값 사이에 다른 바이트가 끼거나 문자열이 끊길 수 있습니다[6]. 파일 번호와 LevelDB 레코드 구조는 [저장 위치와 구조](storage.md) 페이지에서 다룹니다.

### 볼트가 다시 쓰이는 때

볼트 문자열은 한 번 만들고 끝나지 않고 키링이 바뀔 때마다 새로 씁니다. 코드로 보면 경우마다 `iv`·`salt`·`keyMetadata` 가 바뀌는 방식이 다릅니다.

| 일어난 일 | `iv` | `salt` | `keyMetadata` |
|---|---|---|---|
| 계정 추가, 개인 키 가져오기처럼 키링 내용이 바뀜 | 새 값[1][2] | 그대로[2] | 그대로 |
| 비밀번호 변경 | 새 값 | 새 값[2] | 현재 설정 |
| 지갑 새로 만들기, 복구 문구로 다시 가져오기 | 새 값 | 새 값[2] | 현재 설정 |
| 비밀번호로 잠금 해제할 때 `keyMetadata` 가 현재 설정과 다르거나, 키링을 읽는 중에 내용이 바뀜 | 새 값 | 새 값[2] | 현재 설정으로 바뀜[1][2] |

마지막 경우에는 잠금을 풀면서 볼트를 현재 설정으로 다시 암호화합니다[1][2]. 옛 형식 볼트는 `keyMetadata` 가 없어서 이 조건에 걸립니다[1]. 그래서 한 저장소에서 옛 형식 볼트와 새 형식 볼트가 함께 나오면, 옛 형식 시절부터 쓰던 지갑을 업데이트 뒤에 누군가 비밀번호로 연 적이 있을 가능성이 있습니다.

### 볼트 밖에서 평문으로 보이는 것

볼트를 열지 않고도 다음을 알 수 있습니다.

- 계정 주소·이름·가져온 시각과 계정마다의 키링 종류: `AccountsController.internalAccounts` 의 계정 `metadata.keyring.type` 에 볼트 안 키링과 같은 `type` 문자열이 들어갑니다[9]. 이것으로 계정이 복구 문구에서 나왔는지, 가져온 개인 키인지, 하드웨어 지갑인지 구분합니다. 필드 구조는 [거래 기록과 연결한 사이트](activity.md) 페이지에서 다룹니다.
- 형식 세대와 반복 횟수: `keyMetadata` 는 평문입니다[1].
- 볼트 개수: 한 폴더에서 `salt` 가 다른 볼트가 여럿 나오면 비밀번호 변경, 지갑 새로 만들기, 잠금 해제 때 다시 암호화 가운데 하나가 있었습니다[2].

## 증거로서 의미

**증명하는 것.** 이 브라우저 프로필에 MetaMask 지갑 볼트가 만들어진 적이 있습니다. 볼트가 있으면 복구 문구 키링이 적어도 하나 있었습니다[2]. `keyMetadata` 로 볼트를 쓴 형식 세대를, 볼트 밖 계정 목록으로 이 지갑에 속했던 주소와 키링 종류를 확인할 수 있습니다[9]. `salt` 가 다른 볼트가 여럿이면 이 프로필에서 비밀번호를 바꾸거나, 지갑을 새로 만들거나, 잠금을 풀면서 볼트를 다시 암호화한 일이 있었습니다[2].

**증명하지 못하는 것.** 볼트 암호문만으로는 어떤 주소가 들어 있는지 알 수 없습니다. 볼트가 있다는 것은 누군가 지갑을 만들었다는 뜻일 뿐, 누가 비밀번호를 알고 있었는지, 누가 마지막으로 잠금을 풀었는지는 알 수 없습니다. 볼트를 옮겨 다른 기기에서 쓸 수 있으므로 볼트가 이 기기에만 있었다는 것도 알 수 없습니다.

보고서에는 "이 프로필의 MetaMask 저장소에 암호화된 볼트가 2개 있고, 두 볼트의 `salt` 가 다르며, 저장소의 계정 목록에 `HD Key Tree` 계정 0x… 이 있다" 처럼 기록으로 확인되는 만큼만 씁니다.

## 시각 해석

볼트 안에는 시각 필드가 없습니다[1]. 볼트가 언제 쓰였는지는 볼트 밖에서 봅니다.

| 시각 근거 | 뜻 |
|---|---|
| LevelDB 레코드 순번 (sequence number) | 같은 키의 값이 여럿일 때 어느 값이 나중에 쓰였는지 알 수 있습니다([LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)). 절대 시각은 아닙니다. |
| `.log`·`.ldb` 파일의 파일 시스템 시각 | 파일이 마지막으로 바뀐 때입니다. 볼트가 아닌 다른 상태가 바뀌어도 갱신됩니다. |
| 계정의 `metadata.importTime` | 계정을 추가한 때, 유닉스 기준 밀리초, 기기 시계[9]. [거래 기록과 연결한 사이트](activity.md) 페이지에서 다룹니다. |
| `firstTimeInfo.date` | MetaMask 를 처음 설치한 때. [저장 위치와 구조](storage.md) 페이지에서 다룹니다. |

계정을 추가하면 키링 내용이 바뀌어 볼트를 다시 쓰므로, 계정의 `importTime` 무렵에 `iv` 가 새로 만들어진 볼트가 저장되었을 가능성이 있습니다[2][9].

## 함정과 한계

**`data`·`iv`·`salt` 는 흔한 이름입니다.** 다른 확장이나 웹 앱의 암호문도 같은 필드 이름을 쓸 수 있습니다. `KeyringController`·`vault`(`.ldb` 에서는 `Keyring` 과 숫자)가 앞에 오는 문맥에서만 MetaMask 볼트로 판단합니다[6].

**볼트가 여러 개 나옵니다.** 주 저장소, `metamask-backup`, LevelDB 에 남은 옛 레코드가 모두 볼트를 담을 수 있습니다[8][10]. 볼트 복구 도구는 여러 개를 찾으면 "Found multiple vaults!" 를 출력하고 첫 번째 것만 씁니다[6]. btcrecover 추출 스크립트는 마지막에 읽은 레코드에 "Current Vault Data", 나머지에 "(Likely) Old Vault Data" 를 붙이는데, 읽은 순서로 붙인 표시라 실제 최신 여부와 다를 수 있습니다[10]. 최신 여부는 레코드 순번으로 확인합니다.

**복구 문구 여러 개에 대한 설명이 엇갈립니다.** MetaMask 도움말은 한 페이지 안에서 "여러 복구 문구를 넣었다면 한 볼트 파일에 모두 있을 수 있다" 고 하면서, "프로필마다 복구 문구 하나만 저장하고 새로 가져오면 기존 복구 문구 데이터를 지운다" 고도 적습니다[7]. 코드는 키링마다 `metadata.id`·`name` 을 두어 한 볼트에 여러 키링을 담을 수 있게 되어 있고[2], 복구 문구로 다시 가져오면 기존 키링을 지우고 새 `salt` 로 볼트를 만듭니다[2]. 볼트 안 복구 문구 키링 수는 볼트 밖 계정 목록에서 `HD Key Tree` 계정의 `options.entropySource`(키링 ID)가 몇 종류인지로 추정합니다[9].

**옛 볼트가 남습니다.** 다른 복구 문구를 가져온 뒤에도 옛 볼트가 시스템이나 그때의 백업에 남아 있을 수 있습니다[7]. 볼트가 하나뿐이라고 과거에 다른 지갑이 없었다는 뜻은 아니므로 볼륨 섀도 복사본과 백업도 확인합니다.

**아주 옛 형식은 평문입니다.** `wallet-seed` 필드가 있는 볼트는 복구 문구가 암호화되지 않은 상태입니다[6]. 이런 값이 나오면 증거 사본의 접근 권한을 더 엄격하게 관리합니다.

**잠금 해제 중의 키는 디스크에 없습니다.** 볼트에서 유도한 `encryptionKey`·`encryptionSalt` 는 디스크에 쓰지 않는 상태입니다(`persist: false`)[2]. Manifest V3 빌드가 잠금 해제 상태를 이어 가려고 쓰는 값도 메모리 전용 저장소에만 있습니다([저장 위치와 구조](storage.md)). 이 값들은 실행 중인 시스템의 메모리에서만 나올 수 있습니다.

## 직접 분석해 보기

원본은 건드리지 않고 확장 폴더를 복사한 사본에서 작업합니다. 볼트 복구 도구·btcrecover 는 볼트 모양과 위치의 근거로만 참고하고, 이 페이지는 볼트를 여는 절차를 다루지 않습니다.

**헥스로 한 번.** 볼트 안쪽 JSON 은 이스케이프된 따옴표로 시작하므로, 바이트열 `7B 5C 22 64 61 74 61 5C 22 3A 5C 22`(`{\"data\":\"`, 명세로 만든 예시)를 찾으면 볼트 시작 위치가 나옵니다. 이어서 `iv`·`keyMetadata`·`salt` 필드를 확인합니다.

```sh
cd nkbihfbeogaeaoehlefnkodbefgpgknn_copy
grep -a -o -b '{\\"data\\":\\"' *.log *.ldb
grep -a -o '\\"iterations\\":[0-9]*' *.log *.ldb | sort | uniq -c
grep -a -o '\\"salt\\":\\"[A-Za-z0-9+/]*=*' *.log *.ldb | sort -u
```

첫 줄로 볼트 후보의 파일과 바이트 위치를, 둘째 줄로 반복 횟수별 볼트 수를, 셋째 줄로 서로 다른 `salt` 목록을 확인합니다. `iv` 값을 base64 로 풀어 16바이트, `salt` 를 풀어 32바이트가 나오는지 보면 볼트 필드인지 다른 데이터인지 확인할 수 있습니다[1].

```sh
echo 'BNmtDmRaXaQw2YXmbklWaw==' | base64 -d | wc -c    # 16 (만든 예시)
```

`.ldb` 는 압축 블록 때문에 이 방법으로 안 보일 수 있으므로 다음 방법으로 한 번 더 봅니다.

**공개 도구로 한 번.** `ccl_chrome_indexeddb` 의 LevelDB 파서로 확장 폴더의 원시 레코드를 모두 읽고[10], 키에 `vault` 가 들어가거나 값에 `KeyringController` 가 있는 레코드를 골라 레코드 순번과 함께 저장합니다. 값의 `vault` 문자열을 한 번 더 JSON 으로 풀면 `jq '.keyMetadata, (.salt|length), (.iv|length)'` 로 형식과 필드 길이를 확인할 수 있습니다. 레코드를 읽는 방법은 [저장 위치와 구조](storage.md) 페이지에서 다룹니다.

## 교차 검증

- 계정 목록: 볼트 밖 `AccountsController` 의 키링 종류·가져온 시각과 볼트 개수를 비교합니다([거래 기록과 연결한 사이트](activity.md)).
- 백업 사본: 주 저장소와 `metamask-backup` 의 볼트 `salt`·`iv` 가 같은지 확인합니다[8]. 다르면 둘 중 하나가 더 옛 상태입니다.
- 다른 지갑 파일: 데스크톱 지갑의 암호화 방식과 비교할 때는 [지갑 파일과 암호화](../../../01-foundations/wallets/wallet-files.md) 페이지를 봅니다.
- 탈취 흔적: 확장 폴더를 압축하거나 외부로 보낸 흔적이 있으면 [악성 코드가 지갑을 노렸나](../../../04-scenarios/device-use/wallet-stealer.md)를 봅니다.

## 실습

테스트넷 전용 새 브라우저 프로필에 MetaMask 를 설치하고, 단계마다 확장 폴더를 복사해 다음을 확인합니다.

1. 지갑을 만든 직후 볼트의 `keyMetadata.params.iterations` 값을 읽습니다.
2. 계정을 하나 추가한 뒤 `iv` 는 바뀌고 `salt` 는 그대로인지 비교합니다.
3. 비밀번호를 바꾼 뒤 `salt` 가 바뀌는지 봅니다.
4. 다른 테스트용 복구 문구를 가져온 뒤 LevelDB 레코드에서 볼트가 몇 개 나오는지 세고, 레코드 순번으로 최신 볼트를 고릅니다.
5. `metamask-backup` 의 볼트와 주 저장소의 볼트를 비교합니다.

## 참고 문헌

1. MetaMask, browser-passworder `src/index.ts`. https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts
2. MetaMask, core `packages/keyring-controller/src/KeyringController.ts`. https://github.com/MetaMask/core/blob/main/packages/keyring-controller/src/KeyringController.ts
3. MetaMask, metamask-extension `shared/constants/keyring.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/constants/keyring.ts
4. MetaMask, accounts `packages/keyring-eth-hd/src/hd-keyring.ts`. https://github.com/MetaMask/accounts/blob/main/packages/keyring-eth-hd/src/hd-keyring.ts
5. MetaMask, core `packages/wallet/src/initialization/instances/keyring-controller/keyring-controller.ts`. https://github.com/MetaMask/core/blob/main/packages/wallet/src/initialization/instances/keyring-controller/keyring-controller.ts
6. MetaMask, vault-decryptor `app/lib.js`. https://github.com/MetaMask/vault-decryptor/blob/master/app/lib.js
7. MetaMask Support, "How to recover your Secret Recovery Phrase". https://support.metamask.io/configure/wallet/how-to-recover-your-secret-recovery-phrase/
8. MetaMask, metamask-extension `shared/lib/stores/persistence-manager.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/persistence-manager.ts
9. MetaMask, core `packages/accounts-controller/src/AccountsController.ts`. https://github.com/MetaMask/core/blob/main/packages/accounts-controller/src/AccountsController.ts
10. 3rdIteration, btcrecover `extract-scripts/extract-metamask-vaults.py`, `docs/Extract_Scripts.md`. https://github.com/3rdIteration/btcrecover/blob/master/extract-scripts/extract-metamask-vaults.py , https://github.com/3rdIteration/btcrecover/blob/master/docs/Extract_Scripts.md
