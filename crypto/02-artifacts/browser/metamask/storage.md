---
title: "저장 위치와 구조"
parent: "MetaMask"
grand_parent: "아티팩트 · 브라우저 확장 지갑"
nav_order: 160
---

# 저장 위치와 구조 (Storage)

MetaMask 확장은 지갑 상태 전체를 브라우저의 확장 저장소 (`storage.local`)에 JSON 으로 저장하는데, Chrome 계열 브라우저에서는 프로필 안의 LevelDB 폴더이고 Firefox 66 부터는 IndexedDB 입니다[1][2][5]. 저장 방식은 `data` 키 하나에 상태를 모두 담는 옛 방식과 컨트롤러마다 키를 따로 두는 새 방식이 있고, 어느 쪽인지는 `meta`·`manifest` 키로 판별합니다[9][10]. 이 페이지는 저장소를 찾는 방법, 두 저장 방식의 키 구조, 디스크에 남는 필드와 남지 않는 필드, 설치 시각 기록과 사용자가 내보내는 파일을 다룹니다.

## 무엇을 기록하나 · 왜 생기나

MetaMask 는 기능별로 상태를 나눠 관리하고, 이 단위를 컨트롤러 (controller)라고 부릅니다. `KeyringController`, `AccountsController`, `TransactionController` 같은 컨트롤러 이름이 저장소 안의 키 이름이 됩니다[9][13]. 확장이 실행되는 동안 상태가 바뀔 때마다 이 JSON 을 다시 써서, 브라우저를 닫았다 열어도 지갑이 그대로 남습니다.

모든 상태가 디스크에 가는 것은 아닙니다. 각 컨트롤러는 필드마다 `persist` 표시를 두고, 확장은 `persist: true` 인 필드만 골라 저장합니다[12]. 그래서 저장소를 보면 이 지갑이 오래 간직하는 정보(볼트, 계정 목록, 거래 기록, 연결 권한, 설치 정보)는 있지만, 잠금 해제 상태나 처리 중인 서명 요청처럼 잠깐 쓰는 정보는 없습니다.

## 위치와 버전별 차이

### Chrome 계열 브라우저

Chrome 정식 빌드의 저장소는 확장 ID 를 이름으로 한 LevelDB 폴더입니다[1][2].

| OS | 경로 |
|---|---|
| Windows 10·11 | `C:\Users\USER_NAME\AppData\Local\Google\Chrome\User Data\Default\Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn` |
| macOS | `~/Library/Application Support/Google/Chrome/Default/Local Extension Settings/nkbihfbeogaeaoehlefnkodbefgpgknn` |

Brave 같은 다른 Chromium 계열 브라우저는 앞쪽 경로만 다르고 마지막 폴더 이름은 같습니다[2]. 프로필이 여럿이면 `User Data` 아래 프로필 폴더마다 따로 있으므로 `Default` 만 보면 안 됩니다[1]. 베타·Flask 같은 다른 빌드는 확장 ID 가 달라서 폴더 이름도 다릅니다[20]. 빌드별 ID 는 [MetaMask](index.md) 페이지 표에 있고, 브라우저 프로필 위치는 [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/), [크롬·엣지·웨일 (mac)](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/chromium/), [Linux 의 브라우저 프로필](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/desktop/browsers.html) 페이지에서 다룹니다.

폴더 안에는 LevelDB 의 `.log` 와 `.ldb` 파일이 있고, 상태 JSON 은 두 종류 파일 모두에 들어 있을 수 있습니다. MetaMask 의 볼트 복구 도구는 Linux 의 `000003.log`, macOS 의 `000006.log`·`0000056.log`, Windows 의 `000005.ldb`·`000004.log` 에서 볼트를 찾도록 짜여 있습니다[19]. 파일 번호와 레코드 구조는 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html) 페이지에서 다룹니다.

Chrome 의 `storage.local` 은 사용자가 캐시와 방문 기록을 지워도 남고, 확장을 지우면 함께 지워집니다[3]. 확장을 설치한 기록과 브라우저가 적은 설치 시각은 `Secure Preferences` 에 따로 있으며 [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) 페이지에서 다룹니다.

### Firefox

Firefox 는 버전에 따라 저장 형식이 다릅니다.

| Firefox 버전 | `storage.local` 저장 형식 | 위치 |
|---|---|---|
| 65 이하 | JSON 파일 | 프로필의 `browser-extension-data/webextension@metamask.io/storage.js`[7] |
| 66 이상 | IndexedDB | DB 이름 `webExtensions-storage-local`, 객체 저장소 `storage-local-data`[6] |

Firefox 66 으로 올리면 JSON 파일의 내용을 IndexedDB 로 옮기고, 옛 파일은 지우지 않고 같은 폴더에서 `storage.js.migrated` 같은 이름으로 바꿔 둡니다[5][6]. 그래서 66 이전부터 쓴 프로필에는 옮기기 전의 상태가 이 파일에 남아 있을 가능성이 있습니다. 옮긴 확장은 환경설정 값 `extensions.webextensions.ExtensionStorageIDB.migrated.webextension@metamask.io` 로 표시합니다[6].

Firefox 에서는 확장 ID 로 폴더를 바로 찾을 수 없습니다. 확장 주소 `moz-extension://` 에는 확장 ID 대신 기기마다 새로 만든 UUID 가 들어가고, 확장 ID 와 UUID 의 대응은 환경설정 값 `extensions.webextensions.uuids` 에 JSON 문자열로 있습니다[8]. 확장 저장소 IndexedDB 는 이 확장 주소와 확장 저장 전용 userContextId `4294967295`(코드상 `-1 >>> 0`)로 엽니다[6]. 그래서 먼저 `extensions.webextensions.uuids` 에서 `webextension@metamask.io` 의 UUID 를 찾고, 프로필의 저장소 폴더에서 그 UUID 가 들어간 폴더를 찾습니다. 프로필 구조는 [파이어폭스 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/) 페이지에서 다룹니다.

Firefox 도 확장을 지우면 저장소를 지웁니다. 다만 `extensions.webextensions.keepStorageOnUninstall` 과 `extensions.webextensions.keepUuidOnUninstall` 이 `true` 이면 저장소와 UUID 가 남습니다[4][8]. 이 두 값은 개발자 시험용이고 확장이 스스로 바꿀 수 없습니다[4].

Firefox 는 값을 구조화 복제 (structured clone) 형식으로 저장합니다[6]. 데이터 인코딩이 Chrome 계열과 달라서, 파일을 텍스트로 열어 볼트를 찾는 방법은 Firefox 에서 잘 통하지 않습니다[1].

### MetaMask 가 따로 여는 IndexedDB

MetaMask 는 `storage.local` 과 별도로 IndexedDB 두 개를 씁니다. 두 DB 모두 버전 1 이고 객체 저장소 이름은 `store` 입니다[10][11].

| DB 이름 | 담는 것 | 특징 |
|---|---|---|
| `metamask-backup` | `KeyringController`·`AppMetadataController`·`MetaMetricsController`·`AnalyticsController` 의 상태와 `meta`[10] | 볼트가 있을 때만, 내용이 바뀔 때만 씁니다. 쓰기가 디스크에 닿을 때까지 기다리는 `durability: 'strict'` 로 씁니다[10][11]. |
| `metamask-storage-service` | 컨트롤러가 따로 맡긴 큰 데이터. 키 형식 `storageService:{namespace}:{key}`(예: `storageService:TokenListController:tokensChainsCache`)[11] | IndexedDB 를 못 쓰면(Firefox 개인 정보 보호 모드 등) 같은 키로 `storage.local` 에 씁니다[11]. |

`metamask-backup` 은 볼트가 망가졌을 때 쓰는 복구용 사본입니다. 시작할 때 주 저장소를 읽지 못하거나 주 저장소에 볼트가 없는데 이 백업에 값이 있으면 복구 절차로 넘어갑니다[10]. 그래서 볼트는 주 저장소와 이 백업 두 곳에 있을 수 있습니다. 볼트 모양은 [볼트와 암호화](vault.md) 페이지에서 다룹니다.

Chrome 계열 브라우저는 확장이 연 IndexedDB 를 웹 사이트와 같은 규칙으로 프로필의 `IndexedDB` 폴더 아래 출처 이름이 들어간 LevelDB 폴더에 두고, 확장의 출처 이름은 `chrome-extension_<확장 ID>_0` 입니다. 공개 포렌식 도구 AABF 도 에이전트 확장의 IndexedDB 를 `IndexedDB/chrome-extension_<확장 ID>_0.indexeddb.leveldb` 에서 찾습니다[21]. 폴더 이름 규칙은 [웹 저장소 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/local-storage-indexeddb.html) 페이지에서 다룹니다. MetaMask 정식 빌드라면 `IndexedDB\chrome-extension_nkbihfbeogaeaoehlefnkodbefgpgknn_0.indexeddb.leveldb` 폴더를 찾고, 안에 `metamask-backup` 문자열이 있는지 확인합니다.

## 구조

### `meta` 키와 두 저장 방식

`meta` 에는 상태를 마지막으로 옮긴 마이그레이션 번호 `version`, 저장 방식 `storageKind`(`data` 또는 `split`), 새 방식으로 옮기는 동안 잠깐 쓰는 `platformSplitStateGradualRolloutAttempted` 가 들어 있습니다[9]. `storageKind` 가 없으면 옛 방식으로 봅니다[10][12].

| 방식 | 최상위 키 | 판별 |
|---|---|---|
| 옛 방식 (`data`) | `data`(컨트롤러 상태 전체), `meta`[9] | `manifest` 키가 없고 `meta.storageKind` 가 없거나 `data` |
| 새 방식 (`split`) | 컨트롤러 이름마다 키 하나, 키 목록을 담은 `manifest`, `meta`[9][10] | `manifest` 키가 있고 `meta.storageKind` 가 `split` |

확장은 시작할 때 `manifest` 키부터 읽고, 그 값이 배열이면 배열에 적힌 키를 모두 읽습니다. `manifest` 가 없으면 `data` 와 `meta` 두 키만 읽습니다[9].

옛 방식의 모양은 MetaMask 개발 문서의 그림에서 볼 수 있습니다. Chrome 개발자 도구에서 `data` 를 펼치면 `AlertController`·`KeyringController`·`NetworkController` 같은 컨트롤러 이름이 `data` 아래에 나오고, `KeyringController` 안에 볼트 문자열 `vault` 가 있습니다[13]. 이 그림에서는 `firstTimeInfo: {date: 1650488603972, version: '10.12.4'}` 가 컨트롤러 안이 아니라 `data` 바로 아래에 있는데, 마이그레이션 190 이전의 옛 상태가 이런 모양입니다[12][13]. 두 값은 공식 문서 그림에 나온 값입니다.

새 방식으로 옮길 때는 컨트롤러마다 키를 새로 쓰고 `data` 키를 지웁니다[10]. 코드의 기본값은 `split` 이지만 실제로 옮길지는 원격 기능 플래그 `platformSplitStateGradualRollout` 의 `enabled`·`maxAccounts`·`maxNetworks` 값과 이 지갑의 계정 수·네트워크 수로 정합니다[10][12]. 같은 MetaMask 버전이라도 기기마다 저장 방식이 다를 수 있으므로, 버전으로 짐작하지 말고 `meta.storageKind` 와 `manifest` 키로 확인합니다.

새 방식의 `meta` 와 `manifest` 는 다음과 같은 모양입니다(만든 예시).

```json
"meta":     {"version": 200, "storageKind": "split"}
"manifest": ["meta", "KeyringController", "AppMetadataController", "AccountsController", "TransactionController"]
```

### 디스크에 남는 필드와 남지 않는 필드

| 구분 | 필드 예 | 자세한 페이지 |
|---|---|---|
| 남음 (`persist: true`) | `KeyringController.vault`[15], `AppMetadataController` 전체[14], 계정·거래·연결 권한 | [볼트와 암호화](vault.md), [거래 기록과 연결한 사이트](activity.md) |
| 남지 않음 (`persist: false`) | `KeyringController.isUnlocked`·`keyrings`·`encryptionKey`·`encryptionSalt`[15], 서명 요청, 권한 요청 활동 로그 | [거래 기록과 연결한 사이트](activity.md) |

`storage.session` 에 `loginToken`·`loginSalt` 가 있으면 MetaMask 는 이 값으로 잠금을 풀고, 그 전에 `loginSalt` 가 볼트의 `salt` 와 맞는지 비교합니다[16]. `storage.session` 은 메모리에만 있고 디스크에 쓰지 않으며, 브라우저를 다시 시작하거나 확장을 끄거나 업데이트하면 지워집니다[3]. 그래서 이 값은 디스크 이미지에는 없고 실행 중인 시스템의 메모리에만 있을 수 있습니다([메모리 분석 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/memory-forensics/)).

### 설치 정보 `AppMetadataController`

`AppMetadataController` 에는 지금 버전 `currentAppVersion`, 바로 앞 버전 `previousAppVersion`, 마이그레이션 번호 `currentMigrationVersion`·`previousMigrationVersion`, 처음 설치 정보 `firstTimeInfo`, 설치할 때 metamask.io 쿠키에서 가져온 Google Analytics 식별자 `installAttribution` 이 있고 모두 디스크에 남습니다[14]. `firstTimeInfo` 는 처음 설치할 때 한 번 기록하고 바꾸지 않으며, `version` 에 처음 설치한 MetaMask 버전을, `date` 에 그때의 `Date.now()` 값을 넣습니다[14]. 마이그레이션 190 이전의 옛 상태에서는 `firstTimeInfo` 가 컨트롤러 밖 최상위 키에 있습니다[12].

`currentAppVersion` 은 저장된 값과 다른 버전으로 시작할 때 바뀌고, 그때 옛 값이 `previousAppVersion` 으로 옮겨 갑니다[14]. 그래서 두 값으로 마지막으로 버전이 바뀐 한 단계만 알 수 있고 업데이트 전체 이력은 알 수 없습니다.

### 사용자가 내보내는 파일

MetaMask 는 사용자가 직접 내려받는 JSON 파일을 두 가지 만듭니다. 다운로드 폴더나 메일 첨부에서 이 파일이 나오면 지갑 사용을 뒷받침하는 흔적이 됩니다.

| 파일 | 만드는 곳 | 내용 |
|---|---|---|
| 상태 로그 (state logs) | 설정 > 개인 정보 > 상태 로그 다운로드[17] | 상태를 JSON 으로 내보냅니다. `vault`·`encryptionKey`·`encryptionSalt` 는 `includeInStateLogs: false` 라 빠집니다[15]. |
| 사용자 데이터 백업 `MetaMaskUserData.….json` | 사용자 데이터 백업 기능[18] | `preferences`, `internalAccounts`, `addressBook`, `network.networkConfigurationsByChainId`[18] |

사용자 데이터 백업 파일 이름은 코드 주석에 `YYYY_MM_DD_HH_mm_SS` 형식이라고 적혀 있지만, 코드는 일(DD)과 초(SS) 자리에 모두 요일 번호(`getDay()`, 일요일 0 ~ 토요일 6)를 넣습니다[18]. 예를 들어 `MetaMaskUserData.2026_03_02_14_05_02.json` 은 2026년 3월의 어느 화요일 14시 5분에 만든 파일이라는 뜻입니다(만든 예시). 이름의 시·분은 기기의 현지 시각입니다[18].

## 증거로서 의미

**증명하는 것.** 확장 ID 폴더(Firefox 는 `extensions.webextensions.uuids` 의 MetaMask 항목과 그 UUID 저장소)가 있으면 이 브라우저 프로필에 MetaMask 가 설치된 적이 있습니다. `firstTimeInfo` 에서 MetaMask 가 적은 처음 설치 시각과 그때의 버전을, `currentAppVersion`·`previousAppVersion` 에서 마지막으로 실행된 버전을 알 수 있습니다[14]. `metamask-backup` 에 값이 있으면 이 프로필에서 볼트를 만든 적이 있습니다[10].

**증명하지 못하는 것.** 폴더가 있다고 지갑을 만들었다는 뜻은 아니고, `KeyringController.vault` 가 있는지 따로 확인해야 합니다[10]. 저장소만으로는 누가 브라우저를 썼는지 알 수 없습니다. 확장을 지우면 저장소도 지워지므로[3][4], 저장소가 없다고 MetaMask 를 쓴 적이 없다는 뜻도 아닙니다. 이때는 볼륨 섀도 복사본, 백업, `Secure Preferences` 의 설치 기록, 사용자가 내보낸 파일을 확인합니다.

## 시각 해석

| 값 | 뜻 | 형식·기준 |
|---|---|---|
| `firstTimeInfo.date` | MetaMask 를 처음 설치한 때[14] | 유닉스 기준 밀리초. 기기 시계로 기록합니다. |
| 사용자 데이터 백업 파일 이름 | 파일을 만든 때[18] | 년·월·시·분만 쓸 수 있습니다. 기기 현지 시각이고 일·초 자리는 요일입니다. |
| `Secure Preferences` 의 설치 시각 | 브라우저가 적은 확장 설치 시각 | [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) 페이지 |

`firstTimeInfo.date` 는 시간대가 없는 UTC 기준 경과 시간이라 보고서에는 UTC 로 바꿔 적고 현지 시각을 함께 씁니다. 예를 들어 `1767225600000` 은 2026-01-01 00:00:00 UTC 입니다(만든 예시). 브라우저가 적은 설치 시각과 MetaMask 가 적은 `firstTimeInfo.date` 는 서로 다른 프로그램이 따로 기록하므로 정확히 같지 않을 수 있습니다. 두 값이 크게 다르면 확장을 다시 설치했거나, 프로필을 다른 곳에서 복사했거나, 기기 시계를 바꿨을 가능성을 확인합니다.

## 함정과 한계

**볼트 파일 번호는 출처마다 설명이 다릅니다.** MetaMask 도움말의 한 단락은 번호가 작은 `.ldb` 파일이 볼트이고 번호가 크면 볼트가 아니라고 하고, 다른 단락은 번호와 상관없이 `.ldb` 파일을 보라고 합니다[1]. MetaMask 의 볼트 복구 도구는 `.log` 파일에서도 볼트를 찾습니다[19]. 파일 번호로 고르지 말고 폴더의 `.log`·`.ldb` 를 모두 확인합니다.

**옛 값이 남을 수 있습니다.** 새 방식으로 옮기면 `data` 키를 지우지만[10], LevelDB 는 지운 키를 표시만 해 두고 실제 파일 정리는 나중에 하므로 옛 `data` 값이 파일에 남아 있을 가능성이 있습니다. btcrecover 의 MetaMask 추출 스크립트도 확장 폴더의 LevelDB 레코드를 모두 읽어 덮어쓴 옛 볼트까지 꺼내는데, 마지막에 읽은 것을 "Current", 나머지를 "(Likely) Old" 로 붙일 뿐입니다[2]. 같은 키의 값이 여럿 나오면 어느 것이 최신인지는 LevelDB 레코드의 순번(sequence number)으로 확인합니다([LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html)).

**빌드·프로필·브라우저마다 따로 있습니다.** 정식 ID 로만 찾으면 베타·Flask 빌드를 놓치고[20], `Default` 프로필만 보면 다른 프로필을 놓칩니다[1]. 다른 스토어에서 받은 빌드는 ID 가 다를 수 있으므로 `Secure Preferences` 의 설치 목록에서 확장 이름으로 확인합니다.

**Firefox 는 경로를 외울 수 없습니다.** UUID 가 기기마다 다르므로 매번 `extensions.webextensions.uuids` 로 찾습니다[8].

**저장 용량 한도는 문서마다 다르게 적혀 있습니다.** Chrome 문서는 `storage.local` 한도를 10MB(Chrome 113 이하는 5MB)로[3], MDN 은 Chrome 5MB 로 적습니다[4]. 분석할 때는 한도보다 실제 파일 크기를 봅니다.

## 직접 분석해 보기

원본 프로필은 건드리지 않고 폴더를 복사한 뒤 사본에서 작업합니다. 실행 중인 브라우저가 LevelDB 파일을 잠그거나 새로 쓸 수 있으므로 브라우저가 꺼진 상태의 이미지에서 복사하는 편이 안전합니다.

**문자열로 한 번.** Chrome 계열 사본 폴더에서 키 이름을 검색하면 저장 방식과 설치 정보를 먼저 알 수 있습니다.

```sh
cd nkbihfbeogaeaoehlefnkodbefgpgknn_copy
grep -a -o '"storageKind":"[a-z]*"' *.log *.ldb
grep -a -o '"firstTimeInfo":{[^}]*}' *.log *.ldb
grep -a -c 'KeyringController' *.log *.ldb
```

`.ldb` 파일은 압축된 블록이 섞여 있어 문자열이 중간에 끊기거나 보이지 않을 수 있습니다. 볼트 복구 도구도 Windows `.ldb` 에서는 필드 이름과 값 사이에 다른 바이트가 몇 개 끼어도 찾도록 느슨한 패턴을 씁니다[19]. 문자열 검색은 찾아볼 파일을 좁히는 데만 쓰고 값은 아래 도구로 확인합니다.

**공개 도구로 한 번.** 확장 저장소 전용 공개 포렌식 분석기는 없으므로 LevelDB 파서로 원시 레코드를 읽습니다. btcrecover 의 MetaMask 추출 스크립트는 `ccl_chrome_indexeddb` 의 `ccl_leveldb.RawLevelDb` 로 확장 폴더를 열어 LevelDB 레코드를 하나씩 읽습니다[2]. 같은 방법을 쓰면 볼트뿐 아니라 모든 키를 읽을 수 있습니다. 키가 `meta`·`manifest`·`data` 또는 컨트롤러 이름인 레코드를 골라 값을 JSON 으로 저장한 뒤 `jq` 로 필드를 뽑습니다.

## 교차 검증

- 브라우저 설치 기록: `Secure Preferences` 의 설치 시각과 `firstTimeInfo.date` 를 비교합니다([크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/)).
- 볼트: 주 저장소와 `metamask-backup` 의 볼트가 같은지 확인합니다([볼트와 암호화](vault.md)).
- 계정·거래: 같은 저장소의 `AccountsController`·`TransactionController` 를 읽습니다([거래 기록과 연결한 사이트](activity.md)).
- 내보낸 파일: 다운로드 폴더의 상태 로그·`MetaMaskUserData` 파일의 계정 목록을 저장소의 계정 목록과 비교합니다.
- 탈취 흔적: 이 폴더를 압축하거나 복사한 흔적이 있으면 [악성 코드가 지갑을 노렸나](../../../04-scenarios/device-use/wallet-stealer.md)를 봅니다.

## 실습

테스트넷 전용 새 브라우저 프로필에 MetaMask 를 설치하고 다음을 확인합니다.

1. 지갑을 만들기 전과 만든 뒤에 확장 폴더를 복사해, 볼트 키가 언제 처음 나타나는지 비교합니다.
2. `meta.storageKind` 와 `manifest` 키가 있는지 보고 이 설치본의 저장 방식을 판별합니다.
3. `firstTimeInfo.date` 를 UTC 로 바꾸고 `Secure Preferences` 의 설치 시각과 비교합니다.
4. 사용자 데이터 백업 파일을 내려받아 파일 이름의 일·초 자리가 요일과 같은지 확인합니다.
5. Firefox 에 설치한 뒤 `extensions.webextensions.uuids` 에서 UUID 를 찾고, 프로필 저장소 폴더에서 그 UUID 가 들어간 폴더를 찾습니다.

## 참고 문헌

1. MetaMask Support, How to recover your Secret Recovery Phrase. https://support.metamask.io/configure/wallet/how-to-recover-your-secret-recovery-phrase/
2. 3rdIteration, btcrecover `docs/Extract_Scripts.md`, `extract-scripts/extract-metamask-vaults.py`. https://github.com/3rdIteration/btcrecover/blob/master/docs/Extract_Scripts.md , https://github.com/3rdIteration/btcrecover/blob/master/extract-scripts/extract-metamask-vaults.py
3. Chrome for Developers, chrome.storage API. https://developer.chrome.com/docs/extensions/reference/api/storage
4. MDN Web Docs, storage.local. https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/API/storage/local
5. Mozilla Add-ons Blog, Extensions in Firefox 66 (2019-02-15). https://blog.mozilla.org/addons/2019/02/15/extensions-in-firefox-66/
6. Mozilla, firefox `toolkit/components/extensions/ExtensionStorageIDB.sys.mjs`. https://github.com/mozilla-firefox/firefox/blob/main/toolkit/components/extensions/ExtensionStorageIDB.sys.mjs
7. Mozilla, firefox `toolkit/components/extensions/ExtensionStorage.sys.mjs`. https://github.com/mozilla-firefox/firefox/blob/main/toolkit/components/extensions/ExtensionStorage.sys.mjs
8. Mozilla, firefox `toolkit/components/extensions/Extension.sys.mjs`. https://github.com/mozilla-firefox/firefox/blob/main/toolkit/components/extensions/Extension.sys.mjs
9. MetaMask, metamask-extension `shared/lib/stores/extension-store.ts`, `base-store.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/extension-store.ts
10. MetaMask, metamask-extension `shared/lib/stores/persistence-manager.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/persistence-manager.ts
11. MetaMask, metamask-extension `shared/lib/stores/indexeddb-store.ts`, `indexeddb-storage-adapter.ts`, `indexeddb-storage-constants.ts`, `browser-storage-adapter.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/indexeddb-store.ts
12. MetaMask, metamask-extension `app/scripts/lib/startup/load-state-from-persistence.ts`, `wire-state-persistence.ts`, `app/scripts/lib/use-split-state-storage.ts`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/lib/startup/load-state-from-persistence.ts
13. MetaMask, metamask-extension `docs/assets/chrome-storage-local.png`. https://github.com/MetaMask/metamask-extension/blob/main/docs/assets/chrome-storage-local.png
14. MetaMask, metamask-extension `app/scripts/controllers/app-metadata.ts`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/controllers/app-metadata.ts
15. MetaMask, core `packages/keyring-controller/src/KeyringController.ts`. https://github.com/MetaMask/core/blob/main/packages/keyring-controller/src/KeyringController.ts
16. MetaMask, metamask-extension `app/scripts/metamask-controller.js`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/metamask-controller.js
17. MetaMask, metamask-extension `docs/state_dump.md`. https://github.com/MetaMask/metamask-extension/blob/main/docs/state_dump.md
18. MetaMask, metamask-extension `app/scripts/lib/backup.js`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/lib/backup.js
19. MetaMask, vault-decryptor `app/lib.js`. https://github.com/MetaMask/vault-decryptor/blob/master/app/lib.js
20. MetaMask, metamask-extension `shared/constants/app.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/constants/app.ts
21. seturi, AABF (AI Agent Browser Forensics) `aabf/signatures.py`. https://github.com/seturi/AI-Agent-Browser-Forensics/blob/main/aabf/signatures.py
