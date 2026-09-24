---
title: "정보 탈취 악성 코드"
parent: "시나리오 · 침해 사고"
nav_order: 2570
---

# 정보 탈취 악성 코드 (Infostealer)

## 조사 질문

정보 탈취 악성 코드 (Infostealer) 가 이 맥에서 실행되었는지, 실행되었다면 어떤 자격 증명과 데이터를 모았고 언제 밖으로 보냈을 수 있는지 묻습니다. AMOS(Atomic Stealer) 처럼 오래 머물지 않고 한 번에 모아 보내는 악성 코드가 있어서 [1], 지속성 흔적보다 실행 순간의 기록과 유입·전송 기록이 조사의 중심이 됩니다. 이 페이지의 행동 흔적은 AMOS 분석 글 하나로만 확인했고 [1], Poseidon·Banshee·Cuckoo 같은 다른 계열의 행동은 확인하지 못했습니다. 다른 계열을 조사할 때는 이 페이지의 흐름만 빌려 쓰고, 명령줄이나 문구 같은 세부 단서는 그 계열의 분석 자료로 다시 확인합니다.

## 먼저 확인할 것

OS 버전, 시간대, 사용자 목록을 먼저 정리하고, 특히 수집 시점이 감염 뒤 재부팅보다 앞인지 뒤인지를 적어 둡니다. AMOS 는 지속성을 만들지 않고 한 번 훔치고 끝내서 [1], 필자 해석으로는 재부팅 뒤에는 실행 중인 흔적이 없고 격리 데이터베이스, 다운로드 기록, 통합 로그, 네트워크 기록이 주 단서가 됩니다. 라이브 상태라면 [라이브 대응](../../03-techniques/process-acquisition/live-response/index.md) 절차로 휘발성 정보부터 확보하고, 메모리를 떠 둘 수 있으면 [메모리 분석](../../03-techniques/analysis/memory-forensics/index.md) 도 준비합니다.

수집 범위에는 악성 코드가 노린 데이터 위치를 넣습니다. 사례에서 노린 곳은 키체인 `login.keychain-db`, Chrome 의 `~/Library/Application Support/Google/Chrome/Default/`, Firefox 프로필, 그리고 Atomic·Binance·Electrum·Exodus·Coinomi 암호화폐 지갑입니다 [1]. 이 위치들은 피해 범위를 정할 때 목록이 되고, 각 위치의 구조는 [키체인](../../01-foundations/protection/keychain/index.md), [크롬·엣지·웨일](../../02-artifacts/browsers/chromium/index.md), [파이어폭스](../../02-artifacts/browsers/firefox.md) 페이지에 있습니다.

## 볼 아티팩트와 순서

AMOS 사례에서 관찰된 행동을 단계별로 놓고, 단계마다 어느 흔적을 보면 되는지 정리하면 아래와 같습니다. 행동 설명은 모두 출처 [1] 의 관찰이고, "찾아볼 흔적" 열은 필자가 행동마다 아티팩트를 짝지어 채웠습니다.

| 단계 | 사례에서 관찰된 행동 | 찾아볼 흔적 | 링크 |
|---|---|---|---|
| 유입 | 정상 앱(Tor Browser, Photoshop CC, Notion, Microsoft Office, 게임 설치 파일 등)으로 위장한 DMG | 격리 데이터베이스, 다운로드 기록, DMG 마운트 | [악성 코드는 어디서 들어왔나](initial-access.md) |
| 파일 | Go 로 만든 유니버설 바이너리(Intel+arm64), 서명 없음. 한 변형은 Appify 기본 번들 ID "Appify by Machine Box.My Go Application" 을 그대로 씀 | 앱 번들의 Info.plist 와 코드 서명 | [앱 번들 정보](../../02-artifacts/embedded-metadata/app-bundle.md) |
| 환경 확인 | `system_profiler SPHardwareDataType` 실행 | 프로세스 실행 기록 | [통합 로그의 프로세스 실행 기록](../../02-artifacts/execution/unified-log-process.md) |
| 가짜 암호 창 | `osascript` 가 AppleScript 대화 상자를 띄움 | 프로세스 실행 기록과 명령줄 | [통합 로그의 프로세스 실행 기록](../../02-artifacts/execution/unified-log-process.md) |
| 암호 확인 | `/usr/bin/dscl -authonly` 로 받은 암호가 맞는지 확인 | 프로세스 실행 기록과 명령줄 | [감사 로그](../../02-artifacts/logs/openbsm-audit.md) |
| 키체인 조회 | `/usr/bin/security find-generic-password -ga 'Chrome'` | 프로세스 실행 기록과 명령줄 | [키체인](../../01-foundations/protection/keychain/index.md) |
| 모으기 | 보내기 전에 임시 zip 을 만듦 | 파일 시스템 이벤트 | [파일 시스템 이벤트](../../02-artifacts/filesystem/fsevents/index.md) |
| 보내기 | HTTP POST 로 경로 `/sendlog` 에 보냄 | 앱별 네트워크 사용량, 조직의 프록시·방화벽 기록 | [앱별 네트워크 사용량](../../02-artifacts/network/netusage.md) |

### 가짜 암호 창의 단서

AMOS 의 대화 상자 문구에는 "MacOS wants to access System Preferences" 와 "You entered invalid password" 가 들어가고, 사용자가 취소해도 창이 다시 뜹니다 [1]. 대화 상자 아이콘으로는 아래 파일을 지정합니다 [1].

```
System:Library:CoreServices:CoreTypes.bundle:Contents:Resources:ToolbarAdvanced.icns
```

경로가 슬래시 대신 콜론으로 이어져 있어서, 명령줄 기록에서 찾을 때는 이 모양 그대로 검색합니다. 받은 암호를 확인하는 명령은 아래 모양으로 남습니다 [1].

```
/usr/bin/dscl -authonly <사용자> <암호>
```

프로세스 실행 기록에 `dscl -authonly` 가 사용자 이름과 함께 남아 있으면 강한 단서로 봅니다(필자 해석). 명령줄에 암호 문자열까지 남을 수 있어서, 이 기록을 보고서에 옮길 때는 암호 부분을 가립니다.

### 탐지 신호

출처가 탐지 신호로 꼽는 동작은 `osascript` 대화 상자 생성, `/usr/bin/security` 호출, `system_profiler` 실행입니다 [1]. 셋 다 정상 앱과 관리 스크립트도 쓰는 명령이라, 하나만으로 판정하지 않고 같은 부모 프로세스에서 짧은 시간 안에 이어서 일어났는지로 묶어 봅니다(필자 해석).

## 분석 흐름

1. 유입 파일과 시각을 찾습니다. 절차는 [악성 코드는 어디서 들어왔나](initial-access.md) 를 따릅니다.
2. 앱 번들을 확보해 번들 ID, 서명 여부, 아키텍처를 확인합니다. 파일을 살피는 절차는 [악성 코드 흔적 분석](../../03-techniques/analysis/malware-triage/index.md) 에 있습니다.
3. 유입 시각 이후의 프로세스 실행 기록에서 `system_profiler`, `osascript`, `dscl -authonly`, `security find-generic-password` 를 찾고, 같은 부모 프로세스와 시간대로 묶습니다.
4. 노린 데이터 위치마다 그 시간대에 읽힌 흔적이 있는지 봅니다. 키체인, 브라우저 프로필, 지갑 폴더가 대상입니다.
5. 임시 zip 이 생기고 지워진 흔적을 파일 시스템 이벤트에서 찾습니다.
6. 전송을 확인합니다. 맥 안에서는 [앱별 네트워크 사용량](../../02-artifacts/network/netusage.md) 으로 그 앱의 송신량을 보고, 목적지 주소와 `/sendlog` 경로는 조직의 프록시·방화벽 기록에서 찾습니다.
7. 단계별 시각을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 가져갔을 수 있는 자격 증명과 지갑을 피해 범위 목록으로 정리합니다.

## 흔한 오판

- **지속성이 없으니 감염이 없었다고 보는 경우.** AMOS 는 지속성을 만들지 않습니다 [1]. [악성 코드 지속성 찾기](persistence.md) 에서 아무것도 나오지 않아도 실행 기록과 유입 기록을 따로 봅니다.
- **`dscl -authonly` 기록이 있으니 암호가 밖으로 나갔다고 쓰는 경우.** 이 기록은 받은 암호를 확인한 동작을 보여 줍니다 [1]. 전송 여부는 네트워크 기록으로 따로 확인합니다.
- **`security` 호출 기록을 키체인 전체 유출로 쓰는 경우.** 사례에서 관찰된 호출은 Chrome 저장 암호 키를 조회하는 명령입니다 [1]. 다른 항목까지 가져갔는지는 기록이 말하는 만큼만 씁니다.
- **번들 ID 가 다르니 AMOS 가 아니라고 보는 경우.** Appify 기본 번들 ID 는 한 변형에서 관찰된 값입니다 [1]. 번들 ID 하나로 계열을 넣거나 빼지 않습니다.
- **AMOS 의 행동을 다른 계열에 그대로 대입하는 경우.** 이 페이지는 AMOS 분석 글 하나로 확인한 내용이라, 다른 계열의 문구·명령줄·전송 경로는 그 계열 자료로 다시 확인합니다.

## 보고서 문장 예

> ○○○○-○○-○○ ○○:○○(UTC) 무렵 프로세스 실행 기록에 `osascript`, `/usr/bin/dscl -authonly ○○ [가림]`, `/usr/bin/security find-generic-password -ga 'Chrome'` 이 차례로 남아 있고, 셋 다 같은 부모 프로세스 "○○"에서 시작되었습니다. 이 기록은 그 프로세스가 사용자 암호를 확인하고 Chrome 관련 키체인 항목을 조회하는 명령을 실행한 기록이 있다는 사실을 보여 주지만, 조회한 값이 밖으로 전송되었는지는 네트워크 기록을 확인한 뒤에 따로 적습니다.

## 함께 볼 페이지

- [악성 코드는 어디서 들어왔나 (Initial Access)](initial-access.md) — 위장 DMG 와 첫 실행 흔적
- [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](privilege-tcc-bypass.md) — 받은 암호로 권한을 넓혔는지
- [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md) — 노린 자격 증명 저장소
- [저장된 암호 (Passwords·iCloud Keychain)](../../02-artifacts/credentials/saved-passwords.md) — 피해 범위에 넣을 저장 암호
- [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../exfiltration/data-exfiltration/index.md) — 전송 흔적을 보는 일반 원칙

## 참고 문헌

1. SentinelOne, "Atomic Stealer: Threat Actor Spawns Second Variant of macOS Malware Sold on Telegram" — https://www.sentinelone.com/blog/atomic-stealer-threat-actor-spawns-second-variant-of-macos-malware-sold-on-telegram/
