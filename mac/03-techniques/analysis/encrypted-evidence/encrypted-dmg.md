---
title: "암호 걸린 디스크 이미지"
parent: "암호화된 증거 다루기"
grand_parent: "기법 · 분석"
nav_order: 2190
---

# 암호 걸린 디스크 이미지 (Encrypted DMG)

증거 안에서 암호 걸린 디스크 이미지 파일을 확장자와 상관없이 골라내고, 어떤 판의 암호화 머리인지 확인한 뒤 사본을 읽기 전용으로 붙이는 방법을 다룹니다.

## 언제 쓰나

사용자 폴더나 외장 저장장치에서 `.dmg`, `.sparseimage`, `.sparsebundle` 파일이 나왔거나, 확장자를 바꾼 큰 파일이 이미지인지 의심될 때 씁니다. 맥에서는 디스크 유틸리티(GUI)와 `hdiutil`(명령줄) 두 도구로 암호 걸린 이미지를 만듭니다 [1][7]. 암호화하지 않은 이미지 형식(UDIF, 스파스 이미지, 스파스 번들)의 구조는 [디스크 이미지 형식 (DMG·Sparsebundle)](../../../01-foundations/disk-volume/dmg-sparsebundle.md)에 있고, 이 페이지는 암호화된 경우만 다룹니다.

## 만들 때 고르는 것

이미지를 만들 때 고른 값이 나중에 이미지를 여는 방법을 정해서, 먼저 어떤 선택지가 있는지 알아 둡니다. `hdiutil` 의 `-encryption` 은 AES-128과 AES-256을 받고, OS X 10.7 이후 기본값은 CBC 모드·512바이트 블록·128비트 키의 AES입니다 [1]. 디스크 유틸리티에서는 암호화 방식을 팝업 메뉴에서 고릅니다 [7].

암호 말고도 이미지를 여는 수단을 붙일 수 있습니다. `-certificate` 는 DER 인증서로 보조 접근을 걸고, `-pubkey` 는 공개 키 해시 목록으로 이미지를 보호하며, `-recover` 는 복호 비밀이 든 키체인 파일을 지정합니다 [1]. 그래서 암호를 모르는 이미지라도 같은 사용자의 인증서나 키체인 파일이 증거에 있으면 여는 수단이 될 수 있고, 키체인 쪽은 [키체인 풀기 (Keychain)](keychain-decryption.md)에서 이어서 다룹니다. 암호 입력은 `-stdinpass`(표준 입력에서 널로 끝나는 암호)와 `-agentpass`(대화형으로 묻기)로 받습니다 [1].

이미지 형식은 아래와 같고, 암호화 여부와 별개로 고릅니다 [1][7].

| 형식 | 뜻 | 비고 |
|---|---|---|
| UDRW | 읽기·쓰기 | |
| UDSP | 스파스 이미지(SPARSE) | 한 파일로 커짐 |
| UDSB | 스파스 번들(SPARSEBUNDLE) | 디렉터리 기반, 밴드 파일 기본 크기 8MB(`-imagekey sparse-band-size` 로 바꿈) |
| UDRO | 읽기 전용 | |
| UDZO | 읽기 전용, zlib 압축 | |
| ULFO | 읽기 전용, lzfse 압축 | |
| ULMO | 읽기 전용, lzma 압축 | |
| ASIF | Apple 스파스 이미지 | 현대적 스파스 읽기·쓰기 이미지 |

디스크 유틸리티에서는 이 밖에 RAW, DVD/CD 마스터, 하이브리드(HFS+/ISO/UDF) 형식도 고를 수 있습니다(macOS 10.15 Catalina 이후 기준) [7].

## 암호화 머리 구조

아래 구조는 Apple 공식 명세가 아니라 공개 도구 코드에 따른 것입니다 [6]. 암호화 머리에는 두 판이 있고, 판마다 머리가 놓인 위치가 다릅니다.

| 판 | 시그니처 | 위치 | 머리 크기 |
|---|---|---|---|
| v2 | `encrcdsa` | 파일 시작(오프셋 0) | 264바이트, 빅엔디언 구조 |
| v1 | `cdsaencr` | 파일 끝 8바이트 | 1276바이트, 파일 끝에서 그 크기만큼 앞으로 가서 읽음 |

v2 머리는 `sig`(8바이트), `version`, `enc_iv_size`, 뜻이 밝혀지지 않은 4바이트 필드 다섯, `uuid`(16바이트), `blocksize`(4바이트), `datasize`(8바이트), `dataoffset`(8바이트), 채움 24바이트 순서로 시작합니다. 그 뒤로 키 유도 필드(`kdf_algorithm`, `kdf_prng_algorithm`, `kdf_iteration_count`, `kdf_salt_len`, `kdf_salt`)과 키 블롭을 감싼 방식 필드(`blob_enc_iv_size`, `blob_enc_iv`, `blob_enc_key_bits`, `blob_enc_algorithm`, `blob_enc_padding`, `blob_enc_mode`)이 오고, 끝에 `encrypted_keyblob_size` 와 `encrypted_keyblob`(64바이트)이 있습니다. v1 머리에는 `kdf_iteration_count`, `kdf_salt_len`, `kdf_salt`, `len_wrapped_aes_key`, `wrapped_aes_key`(296바이트), `len_hmac_sha1_key`, `wrapped_hmac_sha1_key`(300바이트) 필드가 있습니다.

v2에서 인증서처럼 암호 말고 다른 수단을 함께 건 이미지는 키 블롭이 하나라고 가정하지 않고, `hdiutil isencrypted` 출력과 함께 봅니다.

아래 헥스는 위 구조로 만든 예시이고 실제 이미지에서 뽑은 값이 아닙니다. v2 이미지의 첫 8바이트이고, 뒤쪽은 생략했습니다.

```
00000000  65 6E 63 72 63 64 73 61  .. .. .. .. .. .. .. ..  |encrcdsa........|
```

암호화하지 않은 이미지와 가르는 기준도 함께 알아 둡니다. UDIF 이미지는 512바이트 리소스 구조에 `koly` 시그니처가 있고, 스파스 이미지는 오프셋 0에 `sprs` 가 오며 머리가 4096바이트입니다. 스파스 번들은 파일이 아니라 디렉터리이고, 안에 `Info.plist`, `Info.bckup`, `token` 파일과 `bands` 하위 디렉터리가 있습니다 [4].

## 절차

1. **시그니처로 후보를 고릅니다.** 확장자와 상관없이 파일 첫 8바이트가 `encrcdsa` 이거나 끝 8바이트가 `cdsaencr` 인 파일을 암호 걸린 이미지 후보로 모읍니다. 스파스 번들은 디렉터리 구조(`Info.plist`, `token`, `bands`)로 먼저 찾습니다. 콘텐츠 검색 전반은 [콘텐츠 검색 (Content Search)](../content-search.md)에 있습니다.
2. **맥에서 사본으로 정보를 확인합니다.** `hdiutil isencrypted` 는 암호화 여부와 세부를, `hdiutil imageinfo` 는 이미지 메타데이터를 보여 줍니다 [1]. 이 단계는 원본이 아닌 사본으로 합니다.
3. **여는 수단을 모읍니다.** 암호, 인증서, 공개 키, 복호 비밀이 든 키체인 파일 가운데 합법적으로 얻을 수 있는 것을 확인합니다.
4. **읽기 전용으로 붙입니다.** `hdiutil attach` 에 `-readonly`(읽기 전용 장치)와 `-nomount`(마운트하지 않음)를 함께 주면 장치만 만들고 파일 시스템은 올리지 않아서, 그 장치를 다른 읽기 전용 도구로 읽을 수 있습니다 [1]. `-noverify` 는 체크섬 검증을 건너뛰는 옵션이라 증거 이미지에는 쓰지 않는 편이 낫습니다.
5. **붙인 뒤 안쪽 파일 시스템을 봅니다.** 안에 APFS 볼륨이 있으면 [APFS 구조 (APFS)](../../../01-foundations/disk-volume/apfs/index.md), HFS+ 볼륨이면 [HFS+ 구조 (HFS+)](../../../01-foundations/disk-volume/hfs-plus.md)를 따라 읽습니다. 쓴 명령과 여는 수단의 종류를 기록에 남깁니다.

## 도구

맥에서는 `hdiutil` 이 이미지 판별과 연결을 모두 맡습니다 [1]. 이미지 안이 APFS이고 압축 형식이 zlib이나 ADC라면 apfs-fuse도 DMG를 입력으로 받고, 암호화된 DMG면 암호를 묻습니다 [9](도구 설명은 [파일볼트 이미지 열기 (FileVault)](filevault-images.md) 참고). 맥이 아닌 분석 환경이라면 헥스 편집기로 시그니처만 먼저 확인해 두고, 연결은 맥 분석기에서 합니다.

## 함정과 한계

- 확장자는 믿지 않습니다. 확장자가 `.dmg` 인데 암호화하지 않은 이미지도 있고, 확장자를 바꾼 암호 걸린 이미지도 있어서 시그니처를 기준으로 구분합니다.
- v1 머리는 파일 끝에 있어서 파일 앞부분만 보는 시그니처 검색으로는 놓칩니다. 끝 8바이트도 함께 봅니다.
- 스파스 번들은 디렉터리라서 파일 단위 시그니처 검색에 걸리지 않고, 밴드 파일이 일부만 남으면 이미지가 온전히 붙지 않을 수 있습니다.
- 여기 적은 머리 구조는 공개 도구 코드에서 읽은 것이라서 Apple이 바꾸면 달라질 수 있습니다. 새 macOS에서 만든 이미지는 `hdiutil isencrypted` 결과와 함께 봅니다.
- 이미지 암호를 키체인에 기억시키는 동작이나 이미지를 붙였다 뗀 기록이 어디에 남는지는 시험 기기에서 재현해 확인합니다. 붙인 흔적은 [통합 로그에서 찾을 것 (Unified Log Events)](../../../02-artifacts/logs/unified-log-events/index.md)과 [최근 항목 (Shared File Lists)](../../../02-artifacts/file-folder-usage/recent-items/index.md) 쪽에서 따로 찾아봅니다.

## 결과를 어떻게 해석하나

`encrcdsa` 나 `cdsaencr` 시그니처가 보이면 그 파일이 암호 걸린 디스크 이미지라는 것까지는 말할 수 있지만, 누가 언제 만들었는지나 안에 무엇이 들었는지는 시그니처로 알 수 없습니다. 파일 시스템의 생성·수정 시각, 다운로드 출처 속성, 붙인 기록 같은 다른 흔적과 묶어야 사용 행위를 이야기할 수 있고, 그 방법은 [이 파일은 어디서 왔나 (File Origin)](../../../04-scenarios/activity/file-origin.md)와 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../../04-scenarios/exfiltration/data-exfiltration/index.md)에 있습니다.

열지 못한 이미지도 보고서에 남깁니다. "사용자 폴더에서 v2 암호화 머리(`encrcdsa`)가 있는 디스크 이미지 파일 1개를 확인했고, 여는 수단이 없어 내용은 확인하지 못했다" 처럼 기록이 보여 주는 만큼만 적습니다.

## 참고 문헌

- [1] hdiutil(1) man 페이지(2020-12-09 판) — https://keith.github.io/xcode-man-pages/hdiutil.1.html
- [4] libyal libmodi, Mac OS disk image types(0.0.11, 2021-08) — https://raw.githubusercontent.com/libyal/libmodi/main/documentation/Mac%20OS%20disk%20image%20types.asciidoc
- [6] openwall john 저장소, DMG 암호화 머리 구조 정의가 든 소스 파일(구조 정의만 참고) — https://raw.githubusercontent.com/openwall/john/bleeding-jumbo/run/dmg2john.py
- [7] Apple, Disk Utility User Guide — Create a disk image using Disk Utility on Mac — https://support.apple.com/guide/disk-utility/create-a-disk-image-dskutl11888/mac
- [9] apfs-fuse README (sgan81) — https://github.com/sgan81/apfs-fuse
