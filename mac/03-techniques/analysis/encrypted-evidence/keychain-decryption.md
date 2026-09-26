---
title: "키체인 풀기"
parent: "암호화된 증거 다루기"
grand_parent: "기법 · 분석"
nav_order: 2200
---

# 키체인 풀기 (Keychain)

증거 이미지에서 키체인 파일을 찾아 어떤 구현인지 가르고, 풀기 전에 읽을 수 있는 것과 풀 수단이 있어야 보이는 것을 나눠 분석하는 순서를 다룹니다.

## 언제 쓰나

저장된 암호나 인증서가 조사에 필요할 때, 파일볼트 복구 키나 암호 걸린 디스크 이미지를 여는 수단을 찾을 때 씁니다. 키체인 파일의 머리·표·속성 구조는 [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md)에, 브라우저와 앱이 저장한 암호를 아티팩트로 읽는 법은 [저장된 암호 (Passwords·iCloud Keychain)](../../../02-artifacts/credentials/saved-passwords.md)에 있고, 이 페이지는 키체인을 여는 순서와 그 결과를 해석하는 법만 다룹니다.

맥의 키체인은 파일 기반 키체인(login·System)과 데이터 보호 키체인(Local Items·iCloud Keychain) 두 구현으로 나뉘고 [KC-3], 여는 방법이 서로 다릅니다.

| 구현 | 파일과 위치 | macOS 버전 | 보호 방식 | 출처 |
|---|---|---|---|---|
| 파일 기반 login | `/Users/<사용자>/Library/Keychains/login.keychain` 또는 `login.keychain-db` | macOS 10.12부터 파일 이름이 `.keychain` 에서 `.keychain-db` 로 바뀜 | 키체인 암호나 메모리에서 얻은 마스터 키로 풀림 | [KC-1][KC-4] |
| 파일 기반 System | `/Library/Keychains/System.keychain` | | 잠금 해제 파일 SystemKey로 풀림 | [KC-4] |
| 데이터 보호(Local Items·iCloud Keychain) | 공개 자료 없음 | macOS 10.9에서 iCloud 키체인과 함께 도입 | 항목을 AES-256-GCM 키 두 개(메타데이터 키, 행별 비밀 키)로 암호화하고 비밀 키는 늘 Secure Enclave를 거침 | [KC-2][KC-3] |

## 절차

1. **키체인 파일을 찾아 사본을 뜹니다.** 위 표의 경로에서 파일을 모으고, 파일 기반 키체인이면 오프셋 0에 `kych` 시그니처가 있는지로 형식을 확인합니다 [KC-1]. 머리의 나머지 칸과 표 종류 값은 [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md)에서 따라 읽습니다.
2. **풀기 전에 메타데이터부터 읽습니다.** 계정·서비스·서버 같은 메타데이터는 풀 수단 없이도 보이고, 암호 값만 풀 수단이 있어야 보입니다 [KC-4]. 어떤 서비스와 서버에 쓸 항목이 저장됐는지를 이 단계에서 먼저 목록으로 만들어 두면, 풀 수단을 얻지 못해도 조사에 쓸 수 있습니다. 날짜 속성 `cdat`·`mdat` 는 `YYYYMMDDhhmmssZ` 모양의 UTC 문자열이라 맥 절대 시각이나 유닉스 시각으로 바꾸지 않습니다 [KC-1]. 다른 시각 값과 비교하는 법은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../../01-foundations/value-decoding/mac-time-values.md)에 있습니다.
3. **풀 수단을 확인합니다.** 파일 기반 키체인을 푸는 수단은 키체인 암호, 메모리에서 얻은 마스터 키, 잠금 해제 파일 SystemKey 세 가지이고, SystemKey는 흔히 `/var/db/SystemKey` 에 있으며 System 키체인에 씁니다 [KC-4]. 메모리에서 마스터 키를 얻는 쪽은 [메모리 분석 (Memory Forensics)](../memory-forensics/index.md)에서 다루고, 키체인 암호는 합법적으로 얻은 것만 씁니다.
4. **공개 도구로 엽니다.** 예로 chainbreaker는 OS X 10.6부터 macOS 13까지를 지원하고, 데이터 보호 키체인은 다루지 않습니다 [KC-4]. 이 범위 밖의 macOS에서 나온 키체인은 결과를 다른 방법으로 한 번 더 확인하고, 도구 검증은 [도구 검증 (Tool Validation)](../../reporting/tool-validation.md)을 따릅니다.
5. **다른 암호화 증거와 이어 봅니다.** 파일볼트 개인 복구 키는 키체인에 저장되므로 [FV-1], 키체인을 풀면 개인 복구 키가 나올 수 있습니다. 어느 키체인의 어떤 항목에 들어 있는지는 공개 자료가 없어 검체에서 확인합니다. 파일볼트 쪽은 [파일볼트 이미지 열기 (FileVault)](filevault-images.md)에, 키체인 파일로 디스크 이미지를 여는 경우는 [암호 걸린 디스크 이미지 (Encrypted DMG)](encrypted-dmg.md)에 있습니다.

## 데이터 보호 키체인

데이터 보호 키체인은 항목의 비밀 키가 늘 Secure Enclave를 거치는 구조이고 [KC-2], 위에 예로 든 공개 도구도 이 구현은 다루지 않습니다 [KC-4]. Secure Enclave가 있는 맥에서 이 키체인을 기기 밖에서 여는 공개된 방법은 없으므로, 이런 항목이 필요한 조사라면 획득 단계에서 [라이브 대응 (Live Response)](../../process-acquisition/live-response/index.md)을 함께 검토합니다. Secure Enclave의 구조는 [파일볼트 (FileVault)](../../../01-foundations/protection/filevault/index.md) 쪽에 정리돼 있습니다.

## 도구

파일 기반 키체인의 메타데이터는 헥스 편집기로도 머리와 표를 따라가며 읽을 수 있고, 따라가는 순서는 [키체인 (Keychain)](../../../01-foundations/protection/keychain/index.md)에 있습니다. 암호 값까지 열 때는 chainbreaker 같은 공개 도구를 예로 쓸 수 있습니다 [KC-4]. 이 도구는 3DES CBC와 PBKDF2(SHA-1, 1000회)로 만든 24바이트 키로 키체인을 읽습니다 [KC-7]. 이 방식은 Apple 공식 명세로 공개된 것이 아니라 도구 코드에 담긴 것입니다.

## 함정과 한계

- 메타데이터가 보인다고 암호 값까지 확인했다고 적지 않습니다. 두 가지를 보고서에서 나눠 씁니다.
- 파일 이름이 `.keychain` 인지 `.keychain-db` 인지는 macOS 10.12를 경계로 달라서 [KC-1], 두 이름을 모두 찾습니다.
- `cdat`·`mdat` 를 다른 아티팩트의 맥 절대 시각과 같은 방식으로 풀면 시각이 틀어집니다. 문자열 끝의 `Z` 대로 UTC로 읽습니다.
- 공개 도구의 지원 범위(OS X 10.6~macOS 13)는 도구가 스스로 적은 것이라서, 그보다 새 macOS의 키체인에서 나온 결과는 그대로 믿지 않고 검증합니다.

## 결과를 어떻게 해석하나

키체인 항목이 말해 주는 범위는 "이 계정·서비스·서버에 쓸 자격 증명이 이 키체인에 저장돼 있었다" 까지입니다. 항목이 있다는 사실만으로는 사용자가 그 서비스에 언제 접속했는지 알 수 없고, 접속 시각은 브라우저·네트워크·통합 로그 기록과 맞춰 봐야 합니다([웹 사용 행위 재구성 (Web Activity)](../../../04-scenarios/activity/web-activity.md), [정보 탈취 악성 코드 (Infostealer)](../../../04-scenarios/incident/infostealer.md)).

보고서에는 "login 키체인에 이 서버용 인터넷 암호 항목이 있고, 항목의 생성 시각(`cdat`)은 UTC 기준 이 시각이다" 처럼 쓰고, 암호 값을 열었다면 어떤 풀 수단과 도구로 열었는지를 함께 적습니다.

## 참고 문헌

- [FV-1] Apple Platform Security, Volume encryption with FileVault in macOS — https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
- [KC-1] libyal dtformats, MacOS keychain database file format — https://raw.githubusercontent.com/libyal/dtformats/main/documentation/MacOS%20keychain%20database%20file%20format.asciidoc
- [KC-2] Apple Platform Security, Keychain data protection — https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
- [KC-3] Apple, TN3137: On Mac keychain APIs and implementations(2022-11-01) — https://developer.apple.com/tutorials/data/documentation/technotes/tn3137-on-mac-keychains.json
- [KC-4] chainbreaker README (n0fate) — https://github.com/n0fate/chainbreaker
- [KC-7] chainbreaker 소스 `chainbreaker/__init__.py` — https://raw.githubusercontent.com/n0fate/chainbreaker/master/chainbreaker/__init__.py
