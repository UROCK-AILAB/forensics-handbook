---
title: "AmCache"
parent: "아티팩트 · 프로그램 실행 흔적"
nav_order: 850
has_children: true
has_toc: false
---

# AmCache (Amcache.hve)

Amcache.hve 는 윈도의 프로그램 호환성 기능이 실행 파일·설치 프로그램·드라이버 정보를 모아 두는 레지스트리 하이브 파일입니다. 파일마다 경로와 SHA-1 이 남습니다. 다만 항목이 있다고 해서 그 파일을 실행했다는 뜻은 아닙니다.

## 왜 중요한가

- 실행 파일의 전체 경로, 크기, 게시자, 버전, SHA-1 이 한곳에 남습니다. 파일이 지워진 뒤에도 이 해시로 위협 정보와 대조할 수 있습니다.
- 설치 프로그램, 드라이버, 연결된 장치 목록도 같은 파일에 들어 있습니다.
- 공격자가 흔적을 지울 때 놓치기 쉬운 아티팩트입니다[1].
- 해석은 까다롭습니다. 호환성 평가 예약 작업은 실행하지 않은 파일도 폴더를 살펴 기록하므로 항목이 있다는 사실만으로는 실행했다고 볼 수 없습니다. 키 마지막 기록 시각 (Last Write Time) 도 예약 작업이 돌 때 키를 다시 쓰기 때문에 실행 시각과 다를 때가 많습니다.
- 형식은 Windows 버전보다 호환성 라이브러리의 판에 따라 달라집니다. 이 라이브러리는 `%WinDir%\System32` 에 있는 `ae` 로 시작하는 DLL(aeinv.dll 등)이고, 업데이트를 한 Windows 7 에도 Amcache.hve 가 생길 수 있으며, 옛 형식 파일과 새 형식 파일이 한 시스템에 같이 남아 있을 수도 있습니다.
- SHA-1 은 파일 앞 31,457,280바이트(30MiB)만으로 계산합니다. 이보다 큰 파일은 파일 전체로 구한 SHA-1 과 맞지 않습니다.

## 한눈에 보기

> 그림 자리: Amcache.hve 의 `Root` 키 아래에서 옛 키(File·Programs·Orphan·Generic)와 새 키(Inventory…)가 라이브러리 판마다 생기고 사라지는 흐름을 가로 막대로 보여 주는 그림

### 파일과 위치

| 파일 | 위치 | 생기는 조건 | 알려 주는 것 |
|---|---|---|---|
| Amcache.hve | `%WinDir%\AppCompat\Programs\Amcache.hve` | Windows 8·Server 2012 에 처음 실린 라이브러리부터 씁니다. Windows 7 은 KB2952664, Windows 8·8.1 은 KB2976978 로 라이브러리를 새로 깔면 생깁니다. | 실행 파일, 설치 프로그램, 드라이버, 바로가기, 장치 목록 |
| 트랜잭션 로그 | 같은 폴더의 `.LOG1`·`.LOG2` | 하이브와 함께 생깁니다. | 주 파일에 아직 들어가지 않은 변경 |
| RecentFileCache.bcf | `%WinDir%\AppCompat\Programs\RecentFileCache.bcf` | Windows 7·Server 2008 R2 에 처음 실린 라이브러리(6.1 판)가 씁니다. | 호환성 보정이 필요했던 실행 파일의 경로(소문자) |

하이브를 수집할 때는 로그 파일도 함께 가져옵니다. 최근 정보는 주 파일이 아니라 로그에만 있을 수 있습니다[1].

### 키와 알려 주는 것

아래 표의 "처음 나온 판" 은 호환성 라이브러리의 판입니다. 괄호 안은 그 판이 처음 실린 Windows 입니다. 표는 Windows 10 1803 판까지를 다룹니다[1].

| 키 (`Root` 아래) | 처음 나온 판 | 알려 주는 것 | 실행 증거가 되나 |
|---|---|---|---|
| InventoryApplicationFile | 10.0.14913 (Win10 1607) | 실행 파일 경로, 크기, SHA-1(`FileId`), 빌드 시각(`LinkDate`), 게시자, 버전 | 일부만 됩니다. 호환성 보정이 필요해 실행된 GUI 실행 파일만 실행을 뜻합니다. |
| InventoryApplication | 10.0.14913 (Win10 1607) | 설치 프로그램 이름, 게시자, 버전, 설치 날짜, 설치 방식. 스토어 앱도 들어갑니다. | 안 됩니다. 조사 시점에 설치되어 있었다는 기록입니다. |
| InventoryDriverBinary | 10.0.14913 (Win10 1607) | 드라이버 파일 경로, SHA-1, 서명 여부, 버전 | 안 됩니다. 로드 여부는 서비스 설정과 이벤트 로그로 따로 확인합니다. |
| InventoryApplicationShortcut | 10.0.16299 (Win10 1709) | 시작 메뉴 폴더에서 찾은 LNK 파일 경로 | 안 됩니다. 바로가기가 있었다는 기록입니다. |
| InventoryDevicePnp | 10.0.14913 (Win10 1607) | 연결된 적 있는 PnP 장치와 그 드라이버 | 안 됩니다. 장치 연결 기록입니다. |
| File·Programs·Orphan·Generic (옛 키) | 6.2.9200 (Win8) | 볼륨별·MFT 참조 번호별 실행 파일, 설치 프로그램, 드라이버 | File 항목 가운데 어느 프로그램에도 속하지 않는 파일(Orphan)은 실행을 뜻합니다. |

옛 키 네 개는 10.0.16299 판에서 비고, 10.0.17134 판(Win10 1803)에서 없어집니다. 그 뒤 판에서도 키 구성은 계속 바뀝니다. 하이브마다 실제 키 목록을 먼저 확인합니다.

### 누가 언제 쓰나

Windows 10 1803 판까지의 흐름입니다[1].

- 호환성 보정이 필요한 실행 파일을 실행하면 서비스가 바로 기록합니다. Windows 7·8 에서는 AeLookupSvc, Windows 10 에서는 DiagTrack 이 이 일을 합니다.
- 설치 프로그램을 실행하면 PcaSvc 가 aeinv.dll 을 불러 설치된 프로그램과 새로 생긴 파일을 기록합니다.
- 예약 작업 Microsoft Compatibility Appraiser(`compattelrunner.exe`)가 정해진 폴더를 살펴 목록을 갱신하는데, 1709 판부터는 사용자 바탕 화면, `Program Files`, `Program Files (x86)` 의 EXE 파일을 실행한 적이 없어도 넣습니다.
- 이 예약 작업은 돌 때마다 InventoryApplication 항목을 모두 다시 씁니다. 그래서 그 키의 마지막 기록 시각은 설치 시각이 아닙니다.

### 시각 값

| 시각 | 뜻 | 기준 |
|---|---|---|
| 키 마지막 기록 시각 | 첫 실행 시각일 수도 있고, 예약 작업이 돈 시각일 수도 있습니다. 어느 쪽인지는 키와 판에 따라 다릅니다. | UTC, FILETIME |
| InventoryApplicationFile 의 `LinkDate` | 실행 파일 PE 헤더에 적힌 빌드 시각입니다. 실행·설치 시각이 아닙니다. | 문자열로 저장합니다. 문자열에 시간대 표시가 없습니다. |
| InventoryApplication 의 `InstallDate` | 설치 날짜 추정값입니다. 폴더 생성 날짜로 짐작한 값이고[4], 날짜 단위까지만 맞습니다[1]. | 문자열로 저장합니다. 문자열에 시간대 표시가 없습니다. |
| 옛 형식 `Root` 의 `Sync` 값 | 예약 작업 ProgramDataUpdater 가 마지막으로 돈 시각입니다. | UTC, FILETIME |

## 읽는 순서

1. [구조와 버전별 차이 (Structure·Versions)](structure-versions.md) — 라이브러리 판마다 `Root` 아래 키가 어떻게 바뀌는지 다룹니다. 옛 형식과 새 형식이 한 파일에 섞여 있을 때 구분해 읽는 법도 봅니다.
2. [실행 파일 항목 (InventoryApplicationFile)](inventoryapplicationfile.md) — 경로, `FileId`, `LinkDate`, 게시자 같은 값을 읽습니다. 키 이름 규칙과 키 시각이 뜻하는 것도 다룹니다.
3. [설치 프로그램 항목 (InventoryApplication)](inventoryapplication.md) — 설치 방식과 설치 날짜를 읽습니다. `InstallDate` 가 왜 추정값인지, 지운 프로그램이 어떻게 빠지는지도 다룹니다.
4. [드라이버 항목 (InventoryDriverBinary)](inventorydriverbinary.md) — 드라이버 파일의 경로, 해시, 서명 정보를 읽고 낯선 드라이버를 가려냅니다.
5. [바로가기 항목 (InventoryApplicationShortcut)](inventoryapplicationshortcut.md) — 시작 메뉴 바로가기 목록으로 설치 흔적을 보강합니다.
6. [장치 항목 (InventoryDevicePnp)](inventorydevicepnp.md) — 연결된 장치 항목을 읽고 USB 흔적과 맞춰 봅니다.
7. [구버전 실행 기록 (RecentFileCache.bcf)](recentfilecache-bcf.md) — Windows 7 기본 라이브러리가 쓰던 파일을 읽습니다. 이 파일이 실행한 파일을 모두 담지는 않는다는 점도 다룹니다.
8. [AmCache 해석 함정 (실행 증거가 아닌 경우·SHA1 계산 범위)](sha1.md) — 실행 증거가 되는 경우와 안 되는 경우를 나눕니다. SHA-1 을 앞 30MiB 로만 계산하는 문제도 정리합니다.

## 함께 볼 페이지

- [심캐시 (ShimCache·AppCompatCache)](../shimcache-appcompatcache.md) — 같은 호환성 기능이 SYSTEM 하이브에 남기는 기록입니다.
- [프로그램 호환성 도우미 (PCA)](../pca.md) — 설치 프로그램을 기록하는 PcaSvc 쪽 실행 기록입니다.
- [프리페치 (Prefetch)](../prefetch/index.md) — 실행 횟수와 실행 시각으로 AmCache 의 빈틈을 채웁니다.
- [BAM·DAM (Background Activity Moderator)](../background-activity-moderator.md) — 사용자별 마지막 실행 시각을 더합니다.
- [설치 프로그램 (Uninstall)](../../system-account/uninstall.md) — InventoryApplication 과 맞춰 볼 레지스트리 목록입니다.
- [서비스·드라이버 (Services·Drivers)](../../persistence/services-drivers.md) — InventoryDriverBinary 의 드라이버가 서비스로 등록됐는지 확인합니다.
- [트랜잭션 로그와 반영 안 된 변경 (.LOG1·.LOG2)](../../../01-foundations/database-log-formats/registry-hive/log1-log2.md) — Amcache.hve 를 로그와 함께 읽는 법입니다.
- [키 마지막 기록 시각 (Last Write Time)](../../../01-foundations/database-log-formats/registry-hive/last-write-time.md) — 키 시각이 바뀌는 조건을 다룹니다.
- [실행 파일 메타데이터 (PE Header·Version Info·Digital Signature)](../../embedded-metadata/pe-header-version-info-digital-signature.md) — `LinkDate`·게시자·버전 값의 출처입니다.
- [해시셋 대조와 유사 해시 (Hash Set·Fuzzy Hash)](../../../03-techniques/analysis/hash-set-fuzzy-hash.md) — `FileId` 를 알려진 파일 목록과 대조합니다.
- [어떤 프로그램을 언제 실행했나 (Program Execution)](../../../04-scenarios/activity/program-execution.md) — 실행 흔적을 묶어 읽는 조사 흐름입니다.

## 참고 문헌

- Blanche Lagny (ANSSI), "Analysis of the AmCache" v2, 2019 — https://cyber.gouv.fr/documents/632/anssi-coriin_2019-analysis_amcache-v2.pdf
- NVISO Labs, "Amcache contains SHA-1 Hash – It Depends!", 2022 — https://blog.nviso.eu/2022/03/07/amcache-contains-sha-1-hash-it-depends/
- Kaspersky Securelist, "AmCache artifact: forensic value and a tool for data extraction" — https://securelist.com/amcache-forensic-artifact/117622/
- Microsoft Learn, "Required diagnostic events and fields for Windows 11, versions 25H2 and 24H2" (Inventory 이벤트 필드 설명) — https://learn.microsoft.com/en-us/windows/privacy/required-diagnostic-events-fields-windows-11-24h2
- Plaso, AmCache 레지스트리 파서 소스 — https://plaso.readthedocs.io/en/stable/_modules/plaso/parsers/winreg_plugins/amcache.html
