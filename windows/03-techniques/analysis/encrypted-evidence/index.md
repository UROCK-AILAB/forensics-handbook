# 암호화 증거 다루기 (Encrypted Evidence)

## 한 줄 요약

암호화 증거 다루기는 증거 안의 암호화된 볼륨과 파일을 찾고, 여는 방법을 정하고, 풀어서 분석하는 일을 묶은 주제입니다.
암호화는 층이 다릅니다. 볼륨 전체를 암호화하기도 하고, 파일 하나만 암호화하기도 합니다.
문서와 압축 파일의 암호는 그 파일 형식 안에 표시됩니다.
여는 열쇠는 켜진 시스템에서만 쉽게 얻을 때가 많습니다.
그래서 전원을 끄기 전에 암호화 여부부터 확인하는 편이 낫습니다.

## 왜 중요한가

- 암호화된 자료는 비밀 없이는 내용을 읽을 수 없습니다. 열쇠를 구하는 일이 분석의 갈림길이 됩니다.
- 열쇠 가운데 일부는 전원을 끄면 얻기 어려워집니다. BitLocker 키 패키지는 잠금이 풀린 볼륨에서만 새로 만들 수 있습니다. EFS 인증서와 키는 켜진 시스템에서 백업할 수 있습니다.
- 그래서 켜진 PC 앞에서는 끄기 전에 암호화 여부를 확인하고, 잠금이 풀린 상태에서 할 일을 먼저 합니다(위 두 사실에서 끌어낸 판단).
- 켜진 시스템에서 데이터를 모으는 순서는 [라이브 응답](/03-techniques/process-acquisition/live-response/index.md) 을 봅니다.

## 한눈에 보기

암호화는 무엇을 감싸느냐에 따라 층이 다릅니다.

- 볼륨 단위 암호화는 볼륨 전체를 감쌉니다. BitLocker 가 그 예입니다.
- 파일 단위 암호화는 NTFS 파일을 하나씩 감쌉니다. EFS (Encrypting File System) 가 그 예입니다.
- 문서와 압축 파일의 암호는 그 파일 형식 안에 표시됩니다.
- DRM 보안 문서는 사용자 비밀번호로 여는 문서와 따로 가립니다. 한글(HWP)은 두 경우를 서로 다른 비트로 표시합니다.

| 하위 페이지 | 다루는 대상 | 알아보는 단서 | 여는 열쇠를 찾는 곳 |
|---|---|---|---|
| 암호화 컨테이너 찾기 | 볼륨과 파일 전반 | 서명, 플래그, 무작위처럼 보이는 성질 | 아래 하위 페이지로 갈립니다 |
| BitLocker | 볼륨 | 볼륨 앞머리의 서명 | 복구 비밀번호, 복구 키, 키 패키지 |
| EFS | NTFS 파일 | MFT 의 암호화 플래그 | 사용자 개인 키 |
| 암호 걸린 문서·압축 파일 | 파일 | 형식 안의 암호 표시 | 비밀번호 |
| DRM 문서 판별 | 파일 | 형식 안의 DRM 표시 | 이 묶음에서 다루지 않음 (DRM 프로그램마다 다름) |
| 비밀번호 복구 | 위의 모든 대상 | — | 대입으로 찾습니다 |

- BitLocker 와 EFS 는 Windows 기능입니다. Windows 버전에 따라 다른 점은 각 하위 페이지에 있습니다.
- 문서·ZIP·한글(HWP) 형식의 암호 표시는 Windows 버전과 상관없습니다.

## 읽는 순서

1. [암호화 컨테이너 찾기 (Encrypted Container Detection)](/03-techniques/analysis/encrypted-evidence/encrypted-container-detection.md) — 증거에서 암호화된 볼륨과 파일을 먼저 골라냅니다. 어느 하위 페이지로 갈지 여기서 갈립니다.
2. [BitLocker 볼륨 구조와 풀기 (BitLocker)](/03-techniques/analysis/encrypted-evidence/bitlocker.md) — 볼륨 앞머리와 메타데이터를 읽고, 걸린 키 보호기를 확인하고, 복구 비밀번호를 찾습니다.
3. [EFS 암호화 파일 (Encrypting File System)](/03-techniques/analysis/encrypted-evidence/encrypting-file-system.md) — MFT 의 암호화 표시로 파일을 찾고, 켜진 시스템에서 키를 백업합니다.
4. [암호 걸린 문서·압축 파일 (Password-Protected Files)](/03-techniques/analysis/encrypted-evidence/password-protected-files.md) — 오피스, ZIP, 한글 문서의 암호 표시와 방식을 읽습니다.
5. [DRM 문서 판별 (Enterprise DRM)](/03-techniques/analysis/encrypted-evidence/enterprise-drm.md) — 단순 암호 문서, DRM 보안 문서, 형식 미상 파일을 나눕니다.
6. [비밀번호 복구 (Password Recovery)](/03-techniques/analysis/encrypted-evidence/password-recovery.md) — 비밀을 어디서도 구하지 못했을 때 대입으로 찾습니다.

## 함께 볼 페이지

- [라이브 응답](/03-techniques/process-acquisition/live-response/index.md) — 켜진 시스템에서 잠금이 풀린 볼륨과 키를 먼저 다룹니다.
- [NTFS 구조](/01-foundations/disk-volume/ntfs/index.md) · [마스터 파일 테이블](/02-artifacts/filesystem/mft.md) — EFS 파일의 암호화 표시가 MFT 어디에 있는지 봅니다.
- [OLE 복합 파일](/01-foundations/shell-document-formats/compound-file-binary.md) — 암호 걸린 오피스 문서와 한글 문서의 스트림을 봅니다.
- [파일 내용 검색](/03-techniques/analysis/content-search/index.md) — 확장자와 실제 형식이 어긋난 파일을 서명으로 가립니다.
- [파티션 구조](/01-foundations/disk-volume/mbr-gpt.md) — 파일 시스템으로 읽히지 않는 파티션을 셉니다.
- [DPAPI 구조](/01-foundations/protection/data-protection-api/index.md) — EFS 개인 키와 DPAPI 마스터키를 보호하는 구조를 봅니다.
- [레지스트리 속 비밀번호 정보](/02-artifacts/credentials/sam-security/index.md) · [자격 증명 관리자와 볼트](/02-artifacts/credentials/credential-manager-windows-vault.md) · [크롬 계열 브라우저](/02-artifacts/browsers/chrome-edge-whale/index.md) — 후보 비밀번호와 해시를 찾습니다.
- [압축 프로그램 사용 기록](/02-artifacts/file-folder-usage/7-zip-winrar-bandizip.md) — 어떤 압축 프로그램을 썼는지 찾습니다.
- [액티브 디렉터리 DB](/02-artifacts/credentials/ntds-dit.md) — 도메인에 가입한 PC 의 BitLocker 복구 정보를 오프라인으로 찾습니다.

## 참고 문헌

- Joachim Metz, *BitLocker Drive Encryption (BDE) format* (libbde 문서) — https://raw.githubusercontent.com/libyal/libbde/main/documentation/BitLocker%20Drive%20Encryption%20(BDE)%20format.asciidoc
- Microsoft Learn, *BitLocker recovery overview* (2025-07-29) — https://learn.microsoft.com/en-us/windows/security/operating-system-security/data-protection/bitlocker/recovery-overview
- Microsoft Learn, *File Encryption* (Win32 apps, 2025-07-08) — https://learn.microsoft.com/en-us/windows/win32/fileio/file-encryption
- Microsoft Learn, *cipher* (Windows Commands) — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cipher
