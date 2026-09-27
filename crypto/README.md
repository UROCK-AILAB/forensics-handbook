---
title: Crypto 개요
nav_order: -100
permalink: /
---

# Crypto 개요

암호화폐 지갑과 거래소 앱, 블록체인에 어떤 흔적이 남는지, 그 흔적을 어떻게 찾고 읽고 해석하는지 정리한 한국어 핸드북입니다.

암호화폐 사건은 기기에 남은 지갑 흔적과 누구나 볼 수 있는 블록체인 기록, 거래소가 가진 계정 기록을 이어 붙여야 풀립니다. 그래서 블록·트랜잭션·주소의 기초에서 시작해 데스크톱·브라우저 확장·모바일·하드웨어 지갑의 저장 구조를 다루고, 체인에서 자금을 따라갈 때 알 수 있는 것과 없는 것을 나눠 적었습니다.

## 구성

핸드북은 네 부분으로 나뉩니다.

| 분류 | 다루는 것 |
|---|---|
| **기반 구조** | 블록과 트랜잭션, 비트코인 UTXO, 이더리움 계정과 로그, 토큰, 블록 시각, 지갑 종류, 주소 형식, 복구 문구와 파생 경로, 지갑 파일, 거래소·DEX·브리지·믹서 |
| **아티팩트 사전** | Bitcoin Core·Electrum·Exodus, MetaMask 와 다른 확장 지갑, Android·iOS 지갑 앱, 거래소 앱, 하드웨어 지갑, 거래소 제공 자료, 블록 탐색기 |
| **분석 기법** | 조사 절차, 기기에서 지갑 흔적 찾기, 주소·트랜잭션 ID 찾기, 비트코인·이더리움 거래 따라가기, 주소 묶기와 한계, 거래소 자료 분석, 타임라인, 보고서 |
| **조사 시나리오** | "빼앗긴 자산은 어디로 갔나", "이 기기로 지갑을 썼나", "피싱 사이트에 서명했나" 같은 질문 하나에 여러 기록을 엮어 답하는 흐름 |

큰 주제는 허브 페이지에서 전체를 보여 주고, 하위 페이지에서 자세히 다룹니다.

## 페이지 구성

아티팩트 페이지는 대체로 아래 순서로 씁니다.

1. 무엇을 기록하고, 그 기록이 왜 생기는지
2. 저장 위치 — OS·앱 버전마다 다른 점
3. 구조 — 파일 형식, 데이터 필드
4. 증거로 쓸 때 — 증명할 수 있는 것과 없는 것
5. 시각 읽기 — 기기 시각과 블록 시각
6. 함정과 한계 — 자주 하는 오해, 지웠을 때 남는 흔적
7. 직접 분석하기 — 파일을 직접 열어 한 번, 공개 도구로 한 번
8. 함께 볼 기록 — 다른 기록과 맞춰 보기
9. 실습 질문과 참고 자료

## 읽는 법

- 처음이라면 [블록과 트랜잭션](01-foundations/blockchain/blocks-transactions.md)과 [지갑의 종류](01-foundations/wallets/wallet-types.md)부터 읽기를 권합니다.
- 사건을 앞에 두고 있다면 조사 시나리오에서 질문을 고르면 됩니다. 예: [빼앗긴 자산은 어디로 갔나](04-scenarios/asset-flow/stolen-funds.md), [이 기기로 지갑을 썼나](04-scenarios/device-use/wallet-use.md)
- 특정 지갑만 궁금하다면 아래 목차에서 바로 찾으면 됩니다.

## 표기

- 명세나 공식 문서로 확인한 사실은 그대로 씁니다.
- 지갑 앱은 자주 바뀝니다. 버전에 따라 달라지는 것은 그 자리에 버전을 적습니다.
- 확인되지 않은 것은 쓰지 않습니다. 앱·버전마다 다를 수 있는 것은 분석가가 직접 확인하는 방법을 적습니다.
- 주소·트랜잭션·파일 예시는 명세를 보고 만든 예시입니다. 실제 사람의 주소나 거래가 아닙니다.
- 지갑 암호를 풀거나 복구 문구·개인 키를 빼내는 방법은 다루지 않습니다.
- 특정 회사 제품을 편들지 않고 같은 기준으로 씁니다.
- 용어는 처음 나올 때 "한국어 (English)"로 한 번 적습니다.

# 목차


## 기반 구조

### 블록체인 기초

- [블록과 트랜잭션 (Blocks·Transactions)](01-foundations/blockchain/blocks-transactions.md)
- [비트코인의 UTXO (UTXO Model)](01-foundations/blockchain/utxo.md)
- [이더리움의 계정과 로그 (Accounts·Logs)](01-foundations/blockchain/ethereum-accounts.md)
- [토큰과 NFT (ERC-20·ERC-721)](01-foundations/blockchain/tokens.md)
- [블록 시각과 확정 (Block Time·Confirmations)](01-foundations/blockchain/block-time.md)

### 지갑과 키

- [지갑의 종류 (Custodial·Non-custodial·Hardware)](01-foundations/wallets/wallet-types.md)
- [주소 형식 (Address Formats)](01-foundations/wallets/address-formats.md)
- [복구 문구와 파생 경로 (BIP-39·BIP-32·BIP-44)](01-foundations/wallets/seed-derivation.md)
- [지갑 파일과 암호화 (Wallet Files)](01-foundations/wallets/wallet-files.md)

### 거래 환경

- [거래소와 가상자산사업자 (Exchanges·VASP)](01-foundations/ecosystem/exchanges.md)
- [탈중앙 거래소와 브리지 (DEX·Bridge)](01-foundations/ecosystem/dex-bridge.md)
- [믹서와 추적을 어렵게 하는 방법 (Mixers·Privacy Coins)](01-foundations/ecosystem/mixers.md)

## 아티팩트 사전

### 데스크톱 지갑

- [Bitcoin Core (Bitcoin Core)](02-artifacts/desktop/bitcoin-core.md)
- [Electrum (Electrum)](02-artifacts/desktop/electrum.md)
- [Exodus (Exodus)](02-artifacts/desktop/exodus.md)

### 브라우저 확장 지갑

- [MetaMask (MetaMask)](02-artifacts/browser/metamask/index.md)
  - [저장 위치와 구조 (Storage)](02-artifacts/browser/metamask/storage.md)
  - [볼트와 암호화 (Vault)](02-artifacts/browser/metamask/vault.md)
  - [거래 기록과 연결한 사이트 (Activity·Connected Sites)](02-artifacts/browser/metamask/activity.md)
- [다른 확장 지갑 (Phantom·Coinbase Wallet 등)](02-artifacts/browser/other-extensions.md)

### 모바일 지갑과 거래소 앱

- [Android 지갑 앱 (Android Wallets)](02-artifacts/mobile/android-wallets.md)
- [iOS 지갑 앱 (iOS Wallets)](02-artifacts/mobile/ios-wallets.md)
- [거래소 앱 (Exchange Apps)](02-artifacts/mobile/exchange-apps.md)

### 하드웨어 지갑

- [하드웨어 지갑과 연결 흔적 (Ledger·Trezor)](02-artifacts/hardware/hardware-wallets.md)

### 거래소와 체인 기록

- [거래소가 제공하는 자료 (Exchange Records)](02-artifacts/records/exchange-records.md)
- [블록 탐색기 기록 읽기 (Block Explorers)](02-artifacts/records/block-explorers.md)

## 분석 기법

### 조사 절차·수집

- [조사 절차 (Investigation Process)](03-techniques/acquisition/investigation-process.md)
- [기기에서 지갑 흔적 찾기 (Artifact Search)](03-techniques/acquisition/artifact-search.md)
- [주소와 트랜잭션 ID 찾기 (Address·TXID Carving)](03-techniques/acquisition/address-carving.md)

### 분석

- [비트코인 거래 따라가기 (Bitcoin Tracing)](03-techniques/analysis/bitcoin-tracing.md)
- [이더리움 거래 따라가기 (Ethereum Tracing)](03-techniques/analysis/ethereum-tracing.md)
- [주소 묶기와 그 한계 (Address Clustering)](03-techniques/analysis/clustering.md)
- [거래소 자료 분석 (Exchange Data Analysis)](03-techniques/analysis/exchange-analysis.md)
- [암호화폐 타임라인 (Timeline)](03-techniques/analysis/timeline.md)

### 보고

- [암호화폐 포렌식 보고서 (Forensic Report)](03-techniques/reporting/forensic-report.md)

## 조사 시나리오

### 자산 흐름

- [빼앗긴 자산은 어디로 갔나 (Stolen Funds)](04-scenarios/asset-flow/stolen-funds.md)
- [거래소로 들어갔나 (Exchange Deposit)](04-scenarios/asset-flow/exchange-deposit.md)

### 기기 사용

- [이 기기로 지갑을 썼나 (Wallet Use)](04-scenarios/device-use/wallet-use.md)
- [악성 코드가 지갑을 노렸나 (Wallet Stealer)](04-scenarios/device-use/wallet-stealer.md)

### 사기

- [투자 사기의 흔적 (Investment Scam)](04-scenarios/fraud/investment-scam.md)
- [피싱 사이트에 서명했나 (Wallet Drainer)](04-scenarios/fraud/wallet-drainer.md)
