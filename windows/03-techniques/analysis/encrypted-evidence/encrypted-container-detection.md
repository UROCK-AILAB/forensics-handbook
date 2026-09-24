# 암호화 컨테이너 찾기 (Encrypted Container Detection)

> 위치: [암호화 증거 다루기 (Encrypted Evidence)](/03-techniques/analysis/encrypted-evidence/index.md) > 암호화 컨테이너 찾기

## 한 줄 요약

암호화 컨테이너 찾기는 증거 안에서 암호화된 볼륨과 파일을 골라내는 일입니다.
BitLocker 볼륨은 볼륨 앞머리의 서명으로 찾습니다.
VeraCrypt 볼륨에는 서명이 없습니다.
그래서 VeraCrypt 는 "알려진 서명이 없고 전체가 무작위처럼 보인다" 는 성질로 후보를 좁힐 수밖에 없습니다.
파일 하나에 걸린 암호는 형식마다 표시가 다릅니다. 그 표시는 하위 페이지마다 따로 적었습니다.

## 언제 쓰나

- 증거 이미지를 처음 열었는데 파일 시스템으로 읽히지 않는 파티션이 있을 때
- 파일 시스템은 읽히지만 내용을 알아볼 수 없는 큰 파일이 있을 때
- 켜진 PC 앞에서 전원을 끌지 정해야 할 때
- 보고서에 암호화된 자료가 있었는지를 적어야 할 때

## 무엇을 찾나

| 대상 | 단위 | 찾는 단서 | 자세한 내용 |
|---|---|---|---|
| BitLocker 볼륨 | 볼륨 | 볼륨 헤더 오프셋 3 의 `-FVE-FS-` | 이 페이지, [BitLocker 볼륨 구조와 풀기](/03-techniques/analysis/encrypted-evidence/bitlocker.md) |
| BitLocker To Go | 이동식 드라이브의 볼륨 | 겉은 FAT32. FVE 메타데이터 위치 칸 | 이 페이지, [BitLocker 볼륨 구조와 풀기](/03-techniques/analysis/encrypted-evidence/bitlocker.md) |
| VeraCrypt 볼륨 | 파티션 또는 파일 | 서명 없음. 전체가 무작위처럼 보임 | 이 페이지 |
| EFS 암호화 파일 | NTFS 파일 | MFT 의 암호화 플래그 | [EFS 암호화 파일](/03-techniques/analysis/encrypted-evidence/encrypting-file-system.md) |
| 암호 걸린 문서·압축 파일 | 파일 | 형식 안의 암호 표시 | [암호 걸린 문서·압축 파일](/03-techniques/analysis/encrypted-evidence/password-protected-files.md) |
| DRM 보안 문서 | 파일 | 형식 안의 DRM 표시 | [DRM 문서 판별](/03-techniques/analysis/encrypted-evidence/enterprise-drm.md) |

### BitLocker 볼륨의 앞머리

| 오프셋 | 크기 | Vista | Windows 7 이상 | BitLocker To Go (FAT32 로 포맷한 이동식 드라이브) |
|---|---|---|---|---|
| 0 | 3 | `EB 52 90` | `EB 58 90` | `EB 58 90` |
| 3 | 8 | `-FVE-FS-` | `-FVE-FS-` | `MSWIN4.1` |

- 오프셋 0 의 3바이트는 시작 점프 코드입니다. Vista 와 Windows 7 이상이 서로 다릅니다. To Go 는 Windows 7 이상과 같은 `EB 58 90` 입니다.
- 오프셋 3 의 서명 `-FVE-FS-` 는 Vista 와 Windows 7 이상에서 같습니다.
- BitLocker To Go 는 오프셋 3 에 `MSWIN4.1` 이 있습니다. 겉으로는 FAT32 볼륨처럼 보입니다.
- 그래서 BitLocker To Go 는 이 두 칸만으로 가리지 못합니다. 볼륨 헤더의 FVE 메타데이터 위치 칸을 따로 읽어야 합니다.
- 서명 뒤의 구조(메타데이터 위치 칸, 메타데이터 블록)는 [BitLocker 볼륨 구조와 풀기](/03-techniques/analysis/encrypted-evidence/bitlocker.md) 에 있습니다.

### VeraCrypt 볼륨의 배치

VeraCrypt 볼륨은 파티션 전체일 수도 있고 파일 하나일 수도 있습니다.
아래 위치는 볼륨 시작에서 잰 값입니다. S 는 볼륨 크기입니다.

| 위치 (바이트) | 내용 | 복호하기 전 모습 |
|---|---|---|
| 0 ~ 63 | 솔트 (Salt) 64바이트 | 평문. 알아볼 문자열이 없음 |
| 64 부터 | 헤더의 나머지. 오프셋 64 에 ASCII `VERA` | 암호문 |
| 65536 ~ 131072 | 숨은 볼륨 (Hidden Volume) 헤더 영역 | 무작위처럼 보임 |
| S−131072 ~ S−65536 | 백업 헤더 (Backup Header) | 무작위처럼 보임 |

- VeraCrypt 볼륨에는 서명도 ID 문자열도 없습니다.
- 암호화하지 않은 부분은 오프셋 0 의 솔트 64바이트뿐입니다.
- `VERA` 는 오프셋 64 에 있지만 암호화되어 있습니다. 복호해야만 보입니다.
- 복호하기 전에는 볼륨 전체가 무작위 데이터로만 보입니다.

## 절차

1. **켜진 시스템인지 먼저 봅니다.**
   - 전원이 켜져 있고 암호화 볼륨이 열려 있으면, 끄기 전에 할 일을 정합니다.
   - 잠금이 풀린 상태에서만 할 수 있는 일이 있습니다. [BitLocker 볼륨 구조와 풀기](/03-techniques/analysis/encrypted-evidence/bitlocker.md) 와 [EFS 암호화 파일](/03-techniques/analysis/encrypted-evidence/encrypting-file-system.md) 에 적었습니다.
   - 켜진 시스템을 다루는 순서는 [라이브 응답](/03-techniques/process-acquisition/live-response/index.md) 을 봅니다.
2. **파티션을 모두 셉니다.**
   - 파티션 표를 읽어 파티션마다 시작 위치와 크기를 적습니다. 읽는 법은 [파티션 구조](/01-foundations/disk-volume/mbr-gpt.md) 에 있습니다.
   - 파일 시스템으로 읽히지 않는 파티션을 따로 표시합니다.
3. **볼륨마다 앞머리 11바이트를 봅니다.**
   - 오프셋 3 의 8바이트가 `-FVE-FS-` 면 BitLocker 볼륨입니다.
   - 오프셋 0 의 점프 코드로 Vista 인지 Windows 7 이상인지 가립니다.
4. **FAT32 로 보이는 이동식 드라이브를 다시 봅니다.**
   - 오프셋 3 이 `MSWIN4.1` 이면 BitLocker To Go 일 수 있습니다.
   - 볼륨 헤더의 FVE 메타데이터 위치 칸을 읽고, 그 자리에 FVE 메타데이터 블록이 있는지 확인합니다.
   - 칸의 오프셋과 블록의 서명은 [BitLocker 볼륨 구조와 풀기](/03-techniques/analysis/encrypted-evidence/bitlocker.md) 에 있습니다. FAT32 부트 섹터 자체는 [FAT·exFAT 구조](/01-foundations/disk-volume/fat-exfat.md) 를 봅니다.
5. **서명도 파일 시스템도 없는 영역을 VeraCrypt 후보로 적습니다.**
   - 읽히지 않는 파티션과, 파일 시스템 안의 알아볼 수 없는 큰 파일이 대상입니다.
   - VeraCrypt 명세가 말하는 모습은 "서명이 없고 무작위 데이터로만 보인다" 는 것입니다. 후보를 고르는 단서도 이것뿐입니다(명세에서 끌어낸 판단).
   - 이 글은 "무작위처럼 보인다" 를 가를 기준값을 제시하지 않습니다. 기준값을 쓴다면 그 값과 근거를 보고서에 함께 적습니다.
6. **알려진 형식을 먼저 걸러 냅니다.**
   - 후보 가운데 알려진 파일 서명이 있는 파일은 그 형식부터 확인합니다.
   - VeraCrypt 볼륨의 첫 64바이트는 알아볼 문자열이 없는 솔트이기 때문입니다.
   - 서명으로 형식을 가리는 방법은 [파일 내용 검색](/03-techniques/analysis/content-search/index.md) 에 있습니다.
7. **파일 하나에 걸린 암호를 모읍니다.**
   - NTFS 볼륨이면 MFT 에서 암호화 플래그가 켜진 파일을 모읍니다. 플래그 값과 자리는 [EFS 암호화 파일](/03-techniques/analysis/encrypted-evidence/encrypting-file-system.md) 에 있습니다.
   - 문서·압축 파일은 [암호 걸린 문서·압축 파일](/03-techniques/analysis/encrypted-evidence/password-protected-files.md), DRM 문서는 [DRM 문서 판별](/03-techniques/analysis/encrypted-evidence/enterprise-drm.md) 의 표시로 가립니다.
   - 확장자와 실제 형식이 어긋나는 파일도 이 단계에서 걸립니다. 암호 걸린 오피스 문서가 그런 예입니다.
8. **암호화 프로그램을 쓴 흔적을 찾습니다.**
   - 서명이 없는 컨테이너는 파일만 보고 확정하기 어렵습니다.
   - 암호화 프로그램을 설치하거나 실행한 흔적이 있으면 후보를 좁힐 수 있습니다. [설치 프로그램](/02-artifacts/system-account/uninstall.md) 과 [어떤 프로그램을 언제 실행했나](/04-scenarios/activity/program-execution.md) 를 봅니다.
   - 드라이브 문자가 붙었던 기록을 볼 때는 [USB 저장장치 흔적](/02-artifacts/external-devices/usb-storage-artifacts/index.md) 을 함께 봅니다.
9. **찾은 것을 적습니다.**
   - 위치(파티션 번호와 시작 오프셋, 또는 파일 경로)를 적습니다.
   - 판단 근거(서명, 플래그, 성질만 보고 한 추정)를 적습니다.
   - 확정한 것과 추정한 것을 나눠 적습니다.

### 헥스로 한 번 따라가기

아래 바이트는 **명세로 만든 예시**입니다. 실제 검체에서 나온 값이 아닙니다. `??` 는 이 예시에서 정하지 않은 바이트입니다.

```
BitLocker 볼륨 (Windows 7 이상), 볼륨 첫 섹터 앞부분 (명세로 만든 예시)
00000000  EB 58 90 2D 46 56 45 2D  46 53 2D ?? ?? ?? ?? ??   .X.-FVE-FS-.....
```

- `EB 58 90` 은 Windows 7 이상의 점프 코드입니다. Vista 라면 `EB 52 90` 입니다.
- `2D 46 56 45 2D 46 53 2D` 는 ASCII `-FVE-FS-` 입니다.

```
BitLocker To Go 볼륨, 볼륨 첫 섹터 앞부분 (명세로 만든 예시)
00000000  EB 58 90 4D 53 57 49 4E  34 2E 31 ?? ?? ?? ?? ??   .X.MSWIN4.1.....
```

- `4D 53 57 49 4E 34 2E 31` 은 ASCII `MSWIN4.1` 입니다.
- 여기까지만 보면 FAT32 볼륨과 구분되지 않습니다. 다음은 FVE 메타데이터 위치 칸을 읽을 차례입니다.

```
VeraCrypt 볼륨 앞부분 (명세로 만든 예시)
00000000  ?? ?? ?? ?? ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??   솔트 (평문, 0x00~0x3F)
   ...
00000040  ?? ?? ?? ?? ?? ?? ?? ??  ?? ?? ?? ?? ?? ?? ?? ??   암호문 (복호하면 여기서 "VERA")
```

- 0x40 은 64 입니다. 복호하기 전에는 솔트와 암호문 모두 무작위 바이트처럼 보입니다.
- 숨은 볼륨 헤더 영역은 0x10000(65536) 에서 0x20000(131072) 까지입니다.

## 도구

아래 공개 도구는 예로만 듭니다. 한 도구의 결과에만 기대지 않습니다.

| 도구 | 쓰임 |
|---|---|
| 헥스 편집기 | 볼륨 앞머리의 점프 코드와 서명을 직접 봅니다 |
| The Sleuth Kit (`mmls`) | 파티션 표를 읽어 파티션마다 시작 위치를 적습니다 |
| libbde (`bdeinfo`) | BitLocker 볼륨인지 확인하고 메타데이터를 읽습니다 |
| 파일 형식 식별 도구 (`file` 명령 등) | 후보 파일 가운데 알려진 형식을 걸러 냅니다 |
| 짧은 스크립트 (Python 등) | 볼륨마다 오프셋 3 의 8바이트를 읽어 한꺼번에 대조합니다 |

## 함정과 한계

- **FAT32 로 보이면 FAT32 라고 봅니다.** BitLocker To Go 는 오프셋 3 이 `MSWIN4.1` 이라 겉은 FAT32 입니다. FVE 메타데이터 위치 칸까지 확인합니다.
- **`VERA` 를 문자열 검색으로 찾습니다.** `VERA` 는 암호화되어 있어 검색에 걸리지 않습니다.
- **서명이 없으니 VeraCrypt 라고 씁니다.** "서명이 없고 무작위처럼 보인다" 는 후보의 조건일 뿐입니다. 이 성질만으로 볼륨 종류를 확정하지 않습니다.
- **이름·확장자로 거릅니다.** VeraCrypt 볼륨에는 서명이 없습니다. 그래서 파일 이름과 확장자로는 가릴 수 없습니다.
- **이미지를 뜬 뒤에야 확인합니다.** 전원을 끄면 잠금이 풀린 상태에서만 할 수 있던 일을 되돌릴 수 없습니다. 켜진 PC 라면 1단계부터 합니다.
- **볼륨 하나만 확인하고 멈춥니다.** 볼륨 단위 암호와 파일 단위 암호는 따로 걸릴 수 있습니다. 볼륨을 푼 뒤에도 7단계를 합니다.

## 결과를 어떻게 해석하나

- **서명이 맞은 BitLocker 볼륨**: "이 볼륨은 BitLocker 형식이다" 까지는 확정입니다. 누가 언제 BitLocker 를 켰는지는 서명이 말하지 않습니다.
- **VeraCrypt 후보**: 복호에 성공하기 전에는 "VeraCrypt 볼륨이다" 라고 쓰지 않습니다. 복호한 헤더에서 `VERA` 가 보이면 확정합니다.
- **프로그램 흔적**: 암호화 프로그램을 실행한 기록은 "이 PC 에서 그 프로그램을 실행했다" 를 뒷받침합니다. 특정 후보 파일을 그 프로그램으로 만들었다는 증명은 아닙니다.
- **복호에 필요한 것**: 비밀번호를 대입해야 하면 [비밀번호 복구](/03-techniques/analysis/encrypted-evidence/password-recovery.md) 로 넘어갑니다.

보고서 문장 예:

- "파티션 3 의 볼륨 헤더 오프셋 3 에 `-FVE-FS-` 가 있고 오프셋 0 이 `EB 58 90` 이다. 이 볼륨을 Windows 7 이상 형식의 BitLocker 볼륨으로 판단했다."
- "파일 X 는 알려진 형식 서명이 없고 내용 전체가 무작위 바이트처럼 보인다. 암호화 컨테이너일 수 있으나 복호하지 못해 확인하지 못했다."

## 참고 문헌

- Joachim Metz, *BitLocker Drive Encryption (BDE) format* (libbde 문서) — https://raw.githubusercontent.com/libyal/libbde/main/documentation/BitLocker%20Drive%20Encryption%20(BDE)%20format.asciidoc
- VeraCrypt, *VeraCrypt Volume Format Specification* — https://veracrypt.io//en/VeraCrypt%20Volume%20Format%20Specification.html
