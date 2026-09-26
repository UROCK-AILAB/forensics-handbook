---
title: "완전삭제 도구를 썼나"
parent: "증거를 없애려 했나"
grand_parent: "시나리오 · 행위 재구성"
nav_order: 3900
---

# 완전삭제 도구를 썼나 (Wiping Tools)

> 상위 허브: [증거를 없애려 했나 (Anti-Forensics)](index.md)

완전삭제 도구는 파일 내용을 덮어쓰고 이름을 바꾼 뒤 지웁니다. 덮어쓴 내용은 되살리기 어렵습니다. 하지만 도구를 실행한 기록과 이름을 바꾼 기록은 따로 남습니다. 이 페이지는 공개 도구 SDelete 와 Windows 기본 명령 `cipher /w` 를 예로 흔적을 찾는 순서를 다룹니다. 다른 완전삭제 프로그램은 제품마다 흔적이 달라 여기서 다루지 않습니다.

"(현장 관찰)" 을 붙인 내용은 조사 현장에서 본 것이므로, 다른 기기에서는 다시 확인합니다.

## 조사 질문

- 이 PC 에서 완전삭제 도구를 실행했습니까? 누가 언제 실행했습니까?
- 파일이나 폴더를 골라 지웠습니까, 빈 공간 전체를 지웠습니까?
- 지운 파일의 이름이나 내용이 어디에 남아 있습니까?

## 먼저 확인할 것

| 확인할 것 | 이유 |
|---|---|
| Windows 버전 | SDelete 는 Windows 10 이상, Windows Server 2012 이상, Nano Server 2016 이상에서 돕니다[1]. JPCERT/CC 분석[2]에 나온 흔적은 분석 대상의 OS 버전에서 다시 확인합니다. |
| 사용자 | SDelete 사용권 동의 값은 사용자 하이브(`HKEY_USERS\<사용자 SID>`) 아래에 남습니다[2]. 어느 사용자 하이브에 있는지로 실행 계정을 좁힙니다. |
| 수집 범위 | $MFT, $UsnJrnl:$J, 사용자 하이브, 프리패치, 보안 로그, Sysmon 로그를 확보합니다. |
| USN 저널을 뽑은 방법 | $UsnJrnl:$J 는 앞부분이 비어 있는 희소 (sparse) 스트림입니다(현장 관찰). 구멍을 0 으로 채워 뽑으면 논리 크기(수 GB)가 되고, 건너뛰면 실제 데이터만 남습니다(현장 관찰). 두 방법은 크기와 해시가 다르므로 어떻게 뽑았는지 기록합니다. |

## 도구가 하는 일

### SDelete

SDelete 는 Sysinternals 의 명령줄 도구입니다[1]. 사용법은 세 가지 형식입니다[1].

```
sdelete [-p passes] [-r] [-s] [-q] [-f] <파일·폴더>
sdelete [-p passes] [-q] [-z|-c] <드라이브 문자>
sdelete [-p passes] [-q] [-z|-c] <물리 디스크 번호>
```

| 옵션 | 뜻 |
|---|---|
| -p | 덮어쓰기 횟수 (기본 1) |
| -s | 하위 폴더까지 |
| -r | 읽기 전용 속성 해제 |
| -q | 조용히 |
| -f | 글자만 있는 인자를 파일로 봄 |
| -c | 빈 공간 정리 |
| -z | 빈 공간을 0 으로 채움 (가상 디스크 최적화용) |
| -nobanner | 배너를 보이지 않음 |

(표는 [1])

SDelete 는 DoD 5220.22-M 정리·삭제 기준을 구현하며[1], 물리 디스크를 정리하려면 그 디스크에 볼륨이 없어야 합니다[1].

**파일 이름 지우기.** SDelete 는 지울 파일의 이름을 26번 바꿉니다[1]. 매번 이름의 모든 글자를 다음 알파벳으로 바꿉니다[1]. "foo.txt" 의 첫 번째 새 이름은 "AAA.AAA" 입니다[1].

**압축·암호화·희소 파일.** NTFS 는 이런 파일을 16클러스터 단위로 다룹니다[1]. 덮어쓰면 새 자리에 쓰고 옛 클러스터를 풀어 줍니다[1]. 그래서 그냥 덮어써서는 지워지지 않습니다[1]. SDelete 는 조각 모음 API 로 그 파일의 클러스터를 찾은 뒤, 디스크를 직접 열고 덮어씁니다[1].

**빈 공간 정리.**

만들 수 있는 가장 큰 파일을 캐시 없는 I/O 로 만들고[1], 남은 자리는 캐시를 쓰는 가장 큰 파일로 채운 뒤 두 파일을 덮어씁니다[1]. NTFS 에서는 이어서 MFT 의 빈 레코드를 작은 파일로 채우는데, 새 파일을 더 만들 수 없을 때까지 되풀이합니다[1]. MFT 레코드는 보통 1KB 입니다[1]. 빈 레코드를 채우므로, 빈 레코드에 남아 있던 지운 파일 정보도 덮어써질 수 있습니다.

빈 공간을 정리할 때는 파일 이름을 지우지 않습니다[1]. 폴더 구조의 빈 공간에는 지운 파일 이름이 남아 있을 수 있고[1], 그 공간은 다른 파일에 할당되지 않아 덮어쓸 방법이 없습니다[1]. 이 이름은 [폴더 인덱스와 슬랙](../../../02-artifacts/filesystem/i30.md) 에서 찾습니다.

**EFS.** EFS 로 파일을 암호화하면 새 암호화 파일이 만들어지고, 원래 평문 데이터는 디스크에 남습니다[1].

### cipher /w

- 형식은 `cipher /w:<directory>` 입니다[3].
- 볼륨 전체의 쓰지 않는 공간에서 데이터를 지웁니다[3]. 지금 있는 파일은 건드리지 않고 빈 공간만 대상으로 하며[3], /w 를 쓰면 다른 인자는 모두 무시합니다[3].
- 폴더는 그 볼륨 안이면 어디든 되고[3], 폴더가 마운트 지점이거나 다른 볼륨의 폴더를 가리키면 그 볼륨의 데이터를 지웁니다[3].
- 몇 번, 어떤 값으로 덮어쓰는지와 작업 중에 만드는 임시 폴더는 공개 문서에 나와 있지 않으므로 실제 기기에서 확인해야 합니다.

## 볼 아티팩트와 순서

아래는 JPCERT/CC 가 SDelete 를 실행해 보고 정리한 흔적입니다[2].

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 사용자 하이브 `Software\Sysinternals\SDelete\EulaAccepted` | 이 사용자가 SDelete 사용권에 동의함 (DWORD, 값 1) | [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) |
| 2 | 프리패치 | 실행 기록, 마지막 실행 시각 | [프리패치](../../../02-artifacts/execution/prefetch/index.md) |
| 3 | UserAssist | 실행 시각과 실행 횟수 | [UserAssist](../../../02-artifacts/execution/userassist.md) |
| 4 | 보안 4688·4689, Sysmon 1 | 프로세스 생성과 종료 | [프로세스 생성](../../../02-artifacts/event-logs/4688.md) · [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) |
| 5 | Sysmon 11·12·13 | 프리패치 파일 생성, 레지스트리 기록 | [Sysmon 로그](../../../02-artifacts/event-logs/sysmon/index.md) |
| 6 | USN 변경 저널 | 이름 바꾸기와 삭제 | [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) |
| 7 | MFT | 지운 파일 레코드의 상태 | [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) |
| 8 | 보안 4656·4663·4660·4658 | 삭제 권한 요청과 개체 삭제 | [파일 접근 감사](../../../02-artifacts/event-logs/4656-4663-4660.md) |
| 9 | 폴더 인덱스 슬랙 | 지운 파일의 이름 | [폴더 인덱스와 슬랙](../../../02-artifacts/filesystem/i30.md) |

**USN 변경 저널.** 대상 파일에는 이름이 다른 글자로 바뀐 기록이 남았습니다[2]. 대상 파일에는 CLOSE+FILE_DELETE 가 남았습니다[2]. 프리패치 파일에는 FILE_CREATE 와 DATA_EXTEND+FILE_CREATE 가 남았습니다[2].

**MFT.** 지운 파일은 삭제 상태로, 프리패치 항목은 할당 상태로 남았습니다[2].

**보안 로그.** DELETE 권한을 요청한 4656 이 여러 건 남았습니다[2]. 4663·4660(개체 삭제)·4658 도 남았습니다[2]. 이 기록은 개체 접근 감사가 켜져 있어야 남습니다[2]. 이 이벤트가 남는 조건은 [파일 접근 감사](../../../02-artifacts/event-logs/4656-4663-4660.md) 에서 봅니다.

## 분석 흐름

1. 사용자 하이브마다 `Software\Sysinternals\SDelete\EulaAccepted` 값을 찾습니다. 값이 있으면 그 사용자가 SDelete 사용권에 동의한 기록입니다.
2. 프리패치·UserAssist·4688·Sysmon 1 에서 실행 시각을 모읍니다. 명령줄이 남아 있으면 대상이 파일인지 드라이브인지, 어떤 옵션을 썼는지 읽습니다.
3. 실행 시각 앞뒤의 USN 변경 저널을 뽑습니다. 같은 파일이 이름을 여러 번 바꾼 뒤 지워진 흐름을 찾습니다. SDelete 는 이름을 26번 바꿉니다[1].
4. 이름이 바뀌기 전의 레코드에서 원래 파일 이름과 부모 폴더를 찾습니다. 레코드 필드를 읽는 법은 [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) 에 있습니다.
5. MFT 에서 그 파일 레코드가 삭제 상태인지 확인합니다. 레코드가 $ATTRIBUTE_LIST 로 확장 레코드를 쓰면 긴 이름($FILE_NAME)이 확장 레코드에만 있을 수 있습니다(현장 관찰). 기본 레코드만 보면 8.3 짧은 이름만 보입니다(현장 관찰). 확장 레코드까지 따라가서 이름을 읽습니다.
6. [폴더 인덱스와 슬랙](../../../02-artifacts/filesystem/i30.md) 에서 원래 이름을 찾습니다. 빈 공간 정리는 폴더 구조에 남은 이름을 지우지 않습니다[1].
7. 빈 공간 정리(SDelete -c·-z, `cipher /w`) 흔적이 있으면, 그보다 앞서 파일을 지운 기록을 [지운 파일의 흔적 찾기](../deleted-file-traces.md) 로 찾습니다. 빈 공간을 덮어쓴 뒤에는 내용보다 이름·시각·크기를 중심으로 정리합니다.
8. 파일 접근 감사가 켜져 있었으면 4656·4663·4660 으로 지운 개체와 계정을 봅니다.
9. 모든 시각을 UTC 하나로 맞춰 [타임라인](../../../03-techniques/analysis/timeline/index.md) 으로 정리합니다.

## 흔한 오판

1. **사용권 동의 값을 실행 시각으로 씁니다.** EulaAccepted 는 동의했다는 값(1)입니다[2]. 실행 시각은 프리패치·UserAssist·4688 에서 읽습니다.
2. **도구를 실행했으니 특정 파일을 지웠다고 씁니다.** 실행 기록은 도구를 띄웠다는 것만 보여 줍니다. 무엇을 지웠는지는 USN 변경 저널과 MFT 로 따로 확인합니다.
3. **빈 공간 정리를 파일 삭제로 봅니다.** `cipher /w` 는 지금 있는 파일을 건드리지 않고 빈 공간만 지웁니다[3]. SDelete 의 -c·-z 도 빈 공간이 대상입니다[1].
4. **`cipher /w` 의 폴더 경로를 지운 범위로 씁니다.** /w 는 그 폴더가 속한 볼륨 전체의 빈 공간을 지웁니다[3].
5. **새 이름 모양 하나로 SDelete 라고 단정합니다.** 이름을 여러 번 바꾼 흐름과 실행 흔적을 함께 봅니다.
6. **기본 MFT 레코드에 짧은 이름만 있으면 긴 이름이 없다고 봅니다.** 긴 이름이 확장 레코드에만 있을 수 있습니다(현장 관찰).
7. **USN 저널 사본의 해시가 다르다고 사본을 의심합니다.** 희소 구멍을 채웠는지에 따라 크기와 해시가 달라집니다(현장 관찰).

## 보고서 문장 예

- 쓰지 않을 문장: "피조사자는 완전삭제 프로그램으로 자료를 모두 없앴습니다."
- 쓸 문장: "사용자 ○○ 의 하이브에 SDelete 사용권 동의 값(EulaAccepted, 1)이 있습니다. 프리패치에는 SDelete 실행 기록이 있고, 마지막 실행 시각은 ○○(UTC) 입니다. USN 변경 저널에는 같은 시간대에 파일 ○○ 의 이름이 여러 번 바뀐 뒤 삭제된 기록이 있습니다. 이 기록은 이 파일을 이름을 바꾸며 지웠음을 보여 줍니다. 파일의 내용과 지운 사람의 의도는 이 기록만으로 알 수 없습니다."

## 함께 볼 페이지

- [USN 변경 저널](../../../02-artifacts/filesystem/usnjrnl.md) · [마스터 파일 테이블](../../../02-artifacts/filesystem/mft.md) · [폴더 인덱스와 슬랙](../../../02-artifacts/filesystem/i30.md) — 이름 바꾸기와 삭제의 흔적입니다.
- [프리패치](../../../02-artifacts/execution/prefetch/index.md) · [UserAssist](../../../02-artifacts/execution/userassist.md) — 도구를 실행한 흔적입니다.
- [어떤 프로그램을 언제 실행했나](../program-execution.md) — 실행 흔적을 모으는 순서입니다.
- [지운 파일의 흔적 찾기](../deleted-file-traces.md) · [삭제 데이터 복구](../../../03-techniques/analysis/data-recovery/index.md) — 덮어쓰기 전 일반 삭제를 봅니다.
- [PC 를 초기화하거나 윈도를 다시 깔았나 (Reset·Reinstall)](reset-reinstall.md) — 초기화의 드라이브 데이터 지우기 옵션입니다.
- [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md) — MFT 레코드와 속성의 구조입니다.

## 참고 문헌

1. Microsoft Learn (Sysinternals), "SDelete" — https://learn.microsoft.com/en-us/sysinternals/downloads/sdelete
2. JPCERT/CC, Tool Analysis Result Sheet, "sdelete" — https://jpcertcc.github.io/ToolAnalysisResultSheet/details/sdelete.htm
3. Microsoft Learn, "cipher" (Windows commands) — https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cipher
