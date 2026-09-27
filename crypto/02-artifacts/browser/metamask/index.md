---
title: "MetaMask"
parent: "아티팩트 · 브라우저 확장 지갑"
nav_order: 150
has_children: true
has_toc: false
---

# MetaMask

MetaMask 는 브라우저 확장으로 설치하는 이더리움 계열 자기 보관 지갑이고, 지갑 상태 전체를 브라우저의 확장 저장소에 JSON 으로 저장합니다[7]. 복구 문구와 개인 키는 암호화된 볼트 (vault) 문자열 하나에만 들어 있지만, 계정 주소, 보낸 거래, 연결한 사이트, 설치 시각은 볼트 밖에 평문으로 남습니다[9][10][12][13][14]. 이 페이지는 MetaMask 흔적이 어디에 무엇으로 남는지 정리하고, 저장 위치·볼트·거래와 연결 기록을 다루는 하위 페이지로 안내합니다.

## 왜 중요한가

MetaMask 는 Firefox, Google Chrome, Chromium 계열 브라우저를 지원하고[1], Chrome 계열에는 Chrome·Brave·Edge·Opera 가 들어갑니다[4]. 개인 PC 에서 이더리움 주소를 쓴 흔적을 찾을 때 먼저 보는 곳이 브라우저 프로필 안의 MetaMask 저장소입니다.

볼트를 열지 않아도 얻는 것이 많습니다. MetaMask 는 기능별 상태 묶음인 컨트롤러 (controller) 이름을 키로 삼아 상태를 저장합니다[7][8]. 그래서 `AccountsController` 에서 이 지갑의 계정 주소와 계정을 가져온 시각을, `TransactionController` 에서 이 지갑이 만들고 보낸 거래의 해시를, `PermissionController` 에서 지갑을 연결한 사이트의 원점 (origin)을 읽을 수 있습니다[12][13][14]. 이 주소와 해시를 블록체인 기록과 맞춰 보면 "이 기기의 지갑에서 이 거래를 보냈다" 는 문장을 기록으로 뒷받침할 수 있습니다.

남지 않는 것도 알아야 합니다. 사이트가 요청한 서명(`personal_sign`, typed data 서명)은 디스크에 저장하지 않는 상태라서, 피싱 사이트에 서명한 사건은 로컬 기록 없이 체인 위 결과만 남을 수 있습니다[17]. 잠금을 풀 때 쓰는 파생 키(`encryptionKey`)도 디스크에 쓰지 않는 상태입니다[10].

이 폴더는 정보 탈취 악성 코드의 목표이기도 합니다. Elastic 의 macOS 탐지 규칙 `Macos_Infostealer_Wallets_8e469ea0` 은 MetaMask 확장 ID `nkbihfbeogaeaoehlefnkodbefgpgknn` 과 Firefox 설치 파일 이름 `webextension@metamask.io.xpi` 를 다른 지갑 확장 ID 와 함께 담고, 이 중 6개 이상이 맞으면 탐지합니다[18]. 그래서 이 폴더를 복사한 흔적이 있으면 사용자가 한 일인지 악성 코드가 한 일인지 따로 확인해야 합니다.

## 한눈에 보기

MetaMask 는 빌드마다 확장 ID 가 다릅니다[2].

| 빌드 | Chrome 계열 확장 ID | Firefox 확장 ID |
|---|---|---|
| 정식 | `nkbihfbeogaeaoehlefnkodbefgpgknn` | `webextension@metamask.io` |
| 베타 | `pbbkamfgmaedccnfkmjcofcecjhfgldn` | `webextension-beta@metamask.io` |
| Flask | `ljfoeinjpaedjfecbmggjgodbgkmjkjk` | `webextension-flask@metamask.io` |
| MMI 정식 | `ikkihjamdhfiojpdbnfllpjigpneipbc` | — |
| MMI 베타 | `kmbhbcbadohhhgdgihejcicbgcehoaeg` | — |

Firefox 용 빌드는 매니페스트 버전 2 이고, 설치할 수 있는 가장 낮은 Firefox 버전은 128.0 입니다[3]. 아래 표에 흔적별 위치와 버전 차이를 정리했고, 자세한 구조는 표 마지막 열의 페이지에서 다룹니다.

| 알려 주는 것 | 위치 | 버전·브라우저 차이 | 페이지 |
|---|---|---|---|
| 상태 저장소 전체 | Chrome 계열: 프로필의 `Local Extension Settings\nkbihfbeogaeaoehlefnkodbefgpgknn\` (LevelDB)[4] / Firefox: 프로필의 확장 저장소 IndexedDB[6] | 옛 방식은 `data`·`meta` 두 키, 새 방식은 컨트롤러마다 최상위 키와 `manifest` 키[7] / Firefox 66 부터 JSON 파일 대신 IndexedDB[6] | [저장 위치와 구조](storage.md) |
| 처음 설치한 시각과 그때 버전 | `AppMetadataController.firstTimeInfo` 의 `date`·`version`[9] | 한 번 기록하면 바뀌지 않음[9] | [저장 위치와 구조](storage.md) |
| 볼트 사본 | IndexedDB `metamask-backup`[8] | 주 저장소에 볼트가 없을 때 복구에 씀 | [저장 위치와 구조](storage.md) |
| 암호화된 키링 (볼트) | `KeyringController.vault`[10] | 옛 형식은 `data`·`iv`·`salt`, 새 형식은 `keyMetadata` 가 더 붙음[11] | [볼트와 암호화](vault.md) |
| 계정 주소·이름·가져온 시각 | `AccountsController.internalAccounts`[12] | — | [거래 기록과 연결한 사이트](activity.md) |
| 이 지갑이 만들고 보낸 거래 | `TransactionController.transactions`, `submitHistory`[13] | 끝난 거래는 논스 (nonce)·체인·날짜 조합 기준 기본 40개까지, 보낸 기록은 기본 100건까지 남김[13] | [거래 기록과 연결한 사이트](activity.md) |
| 연결한 사이트 | `PermissionController.subjects`, `PermissionLogController.permissionHistory`, `SubjectMetadataController.subjectMetadata`[14][15][16] | — | [거래 기록과 연결한 사이트](activity.md) |

프로필이 여럿이면 프로필 폴더마다 따로 있습니다[4]. Chrome 의 `storage.local` 은 사용자가 캐시와 방문 기록을 지워도 남고, 확장을 지우면 함께 지워집니다[5]. 브라우저 쪽 설치 기록(`Secure Preferences` 의 확장 목록과 설치 시각)은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/) 페이지에서 다룹니다.

모바일 MetaMask 는 저장 구조가 다릅니다. iOS 앱은 앱 데이터 폴더의 `Documents/persistStore/persist-root` JSON 파일에 상태를 저장합니다[20]. 모바일 앱은 [iOS 지갑 앱](../../mobile/ios-wallets.md) 페이지에서 다룹니다.

## 읽는 순서

- [저장 위치와 구조 (Storage)](storage.md) — Chrome 계열·Firefox 에서 확장 저장소를 찾는 방법, 옛 `data` 방식과 새 방식의 키 구조, 디스크에 쓰는 필드와 쓰지 않는 필드, 설치 시각 기록과 사용자가 내보내는 파일을 다룹니다.
- [볼트와 암호화 (Vault)](vault.md) — 볼트가 LevelDB 파일 안에 어떤 모양으로 있는지, 형식 세대를 어떻게 구분하는지, 옛 볼트가 남는 경우와 볼트를 열지 않고 알 수 있는 것을 다룹니다.
- [거래 기록과 연결한 사이트 (Activity·Connected Sites)](activity.md) — 계정·주소록·거래·연결 권한의 필드와 시각 필드의 뜻, 로컬 기록이 잘리거나 남지 않는 경우, 블록 탐색기와 맞춰 보는 방법을 다룹니다.

## 함께 볼 페이지

- [지갑 파일과 암호화](../../../01-foundations/wallets/wallet-files.md) — 여러 지갑의 암호화 파일 형식을 비교합니다.
- [복구 문구와 파생 경로](../../../01-foundations/wallets/seed-derivation.md) — MetaMask 의 복구 문구 키링은 기본 경로 `m/44'/60'/0'/0` 아래에서 계정을 만듭니다[19].
- [주소 형식](../../../01-foundations/wallets/address-formats.md) — 이더리움 주소의 표기를 다룹니다.
- [다른 확장 지갑](../other-extensions.md) — Phantom·Coinbase Wallet 등 다른 확장 지갑의 위치입니다.
- [블록 탐색기 기록 읽기](../../records/block-explorers.md) — 로컬 거래 해시를 체인 기록과 맞춰 봅니다.
- [이 기기로 지갑을 썼나](../../../04-scenarios/device-use/wallet-use.md), [악성 코드가 지갑을 노렸나](../../../04-scenarios/device-use/wallet-stealer.md), [피싱 사이트에 서명했나](../../../04-scenarios/fraud/wallet-drainer.md)
- 저장 형식: [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/database-log-formats/leveldb.html), [LevelDB와 IndexedDB (mac)](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/data-formats/leveldb-indexeddb.html)
- 브라우저 프로필: [크롬 계열 브라우저 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/chrome-edge-whale/), [파이어폭스 (Windows)](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/browsers/firefox/), [크롬·엣지·웨일 (mac)](https://urock-ailab.github.io/forensics-handbook/mac/02-artifacts/browsers/chromium/), [Linux 의 브라우저 프로필](https://urock-ailab.github.io/forensics-handbook/linux/02-artifacts/desktop/browsers.html)

## 참고 문헌

1. MetaMask, metamask-extension `README.md`. https://github.com/MetaMask/metamask-extension/blob/main/README.md
2. MetaMask, metamask-extension `shared/constants/app.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/constants/app.ts
3. MetaMask, metamask-extension `app/manifest/v2/firefox.json`. https://github.com/MetaMask/metamask-extension/blob/main/app/manifest/v2/firefox.json
4. MetaMask Support, How to recover your Secret Recovery Phrase. https://support.metamask.io/configure/wallet/how-to-recover-your-secret-recovery-phrase/
5. Chrome for Developers, chrome.storage API. https://developer.chrome.com/docs/extensions/reference/api/storage
6. Mozilla Add-ons Blog, Extensions in Firefox 66 (2019-02-15). https://blog.mozilla.org/addons/2019/02/15/extensions-in-firefox-66/
7. MetaMask, metamask-extension `shared/lib/stores/extension-store.ts`, `base-store.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/extension-store.ts
8. MetaMask, metamask-extension `shared/lib/stores/persistence-manager.ts`. https://github.com/MetaMask/metamask-extension/blob/main/shared/lib/stores/persistence-manager.ts
9. MetaMask, metamask-extension `app/scripts/controllers/app-metadata.ts`. https://github.com/MetaMask/metamask-extension/blob/main/app/scripts/controllers/app-metadata.ts
10. MetaMask, core `packages/keyring-controller/src/KeyringController.ts`. https://github.com/MetaMask/core/blob/main/packages/keyring-controller/src/KeyringController.ts
11. MetaMask, browser-passworder `src/index.ts`. https://github.com/MetaMask/browser-passworder/blob/main/src/index.ts
12. MetaMask, core `packages/accounts-controller/src/AccountsController.ts`. https://github.com/MetaMask/core/blob/main/packages/accounts-controller/src/AccountsController.ts
13. MetaMask, core `packages/transaction-controller/src/TransactionController.ts`, `utils/feature-flags.ts`. https://github.com/MetaMask/core/blob/main/packages/transaction-controller/src/TransactionController.ts
14. MetaMask, core `packages/permission-controller/src/PermissionController.ts`. https://github.com/MetaMask/core/blob/main/packages/permission-controller/src/PermissionController.ts
15. MetaMask, core `packages/permission-log-controller/src/PermissionLogController.ts`. https://github.com/MetaMask/core/blob/main/packages/permission-log-controller/src/PermissionLogController.ts
16. MetaMask, core `packages/permission-controller/src/SubjectMetadataController.ts`. https://github.com/MetaMask/core/blob/main/packages/permission-controller/src/SubjectMetadataController.ts
17. MetaMask, core `packages/signature-controller/src/SignatureController.ts`. https://github.com/MetaMask/core/blob/main/packages/signature-controller/src/SignatureController.ts
18. Elastic, protections-artifacts `yara/rules/Macos_Infostealer_Wallets.yar`. https://github.com/elastic/protections-artifacts/blob/main/yara/rules/Macos_Infostealer_Wallets.yar
19. MetaMask, accounts `packages/keyring-eth-hd/src/hd-keyring.ts`. https://github.com/MetaMask/accounts/blob/main/packages/keyring-eth-hd/src/hd-keyring.ts
20. iLEAPP, `scripts/artifacts/metamask.py`. https://github.com/abrignoni/iLEAPP/blob/main/scripts/artifacts/metamask.py
