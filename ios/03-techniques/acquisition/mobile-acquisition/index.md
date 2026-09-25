---
title: "모바일 증거 확보"
parent: "기법 · 조사 절차·증거 확보"
nav_order: 1160
has_children: true
has_toc: false
---

# 모바일 증거 확보 (Acquisition)

아이폰에서 증거를 얻는 길은 로컬 백업, 파일 시스템 추출, 아이클라우드(iCloud), 진단 묶음(sysdiagnose) 네 가지가 흔하고, 어느 길을 고르고 기기를 어떻게 다루느냐에 따라 손에 들어오는 자료의 범위가 달라집니다.

## 왜 중요한가

NIST 는 모바일 수집 도구를 수동 기록, 논리 추출, 헥스 덤프·JTAG, 칩오프, 마이크로 리드의 다섯 단계로 나누고, 위 단계로 갈수록 기술·침습성·시간·비용이 커진다고 설명합니다[4]. 논리 추출은 디렉터리·파일 같은 논리 객체를 복사하고 그 위 단계는 메모리 칩 같은 물리 저장소를 복사하는데[4], 한 단계를 쓰고 나면 다른 단계를 쓸 수 없게 되는 경우도 있습니다[4]. 그래서 처음 고른 수집 방법에 따라 뒤에 쓸 수 있는 방법이 줄어들 수 있습니다.

아이폰에서는 로컬 백업이 가장 먼저 쓰이는 길입니다. 백업은 기기 파일의 일부만 담지만 수상한 흔적을 찾는 데는 충분한 경우가 많고, MVT 문서는 백업을 먼저 쓰고 전체 파일 시스템은 다른 방법을 다 써 본 뒤에만 고려하라고 권합니다[3]. 백업을 암호화하느냐에 따라서도 담기는 자료가 달라집니다[1].

수집 전 기기를 다루는 단계도 결과를 바꿉니다. 네트워크에 붙어 있는 기기는 원격 잠금·원격 초기화 명령이나 새로 들어오는 전화·문자로 자료가 바뀔 수 있어 통신을 끊어야 하고[4], 아이폰은 잠긴 뒤 1시간이 지나면 잠금을 풀 때까지 새 데이터 연결을 허락하지 않습니다[2]. 모바일 기기는 켜져 있는 동안 계속 자료를 바꾸기 때문에, 같은 기기를 연달아 두 번 수집해도 전체 해시는 달라집니다[4]. 이런 성질을 알고 있어야 수집 기록과 해시 값을 보고서에서 설명할 수 있습니다.

이 묶음은 아이폰(주로 iOS 15 이후)을 다루고, 잠금 해제나 보안 우회 방법은 다루지 않습니다. 파일 시스템 추출은 백업과 비교해 무엇이 더 나오는지를 설명하는 데에만 씁니다.

## 한눈에 보기

| 주제 | 어디서 얻나·어디에 남나 | iOS 버전 | 알려 주는 것 |
|---|---|---|---|
| 로컬 백업 | 수집에 쓴 PC 의 백업 폴더(`Manifest.db`, `Manifest.plist`, `Info.plist`, `Status.plist` 등) | iOS 10 부터 `Manifest.db`, iOS 9 까지 `Manifest.mbdb`[6] | 기기 정보, 설치 앱, 백업에 들어간 파일 목록과 내용. 암호화 백업이면 저장된 비밀번호·Wi‑Fi·방문 기록·건강·통화 기록까지[1] |
| 파일 시스템 추출 | 기기 저장소 | 기종·iOS 버전에 따라 가능 여부가 다름[3] | 백업에 들어가지 않는 자료까지[3] |
| 아이클라우드 | Apple 서버. 기기 쪽에는 `com.apple.MobileBackup.plist` 의 백업·복원 상태 키 | 고급 데이터 보호는 iOS 16.2 이상에서 켤 수 있음[5] | 계정에 동기화·백업한 자료. 종단 간 암호화한 항목은 표준 보호에서 15개, 고급 데이터 보호를 켜면 25개[5] |
| sysdiagnose | 기기에서 만든 `.tar.gz` 한 파일[7] | 이 묶음에서 버전별 차이는 확인하지 못함 | 통합 로그 스냅숏, 크래시 보고서, 프로세스 목록, Wi‑Fi·설치·종료 기록[7] |
| 압수와 보관 | 현장 기록(사진·조작 기록), 차폐 용기 | 이 묶음에서 USB 제한 모드가 처음 들어간 버전은 확인하지 못함 | 수집 전에 기기 자료가 바뀌었을 가능성과 그 이유[2][4] |
| 결과물과 해시 | 백업 폴더, `.tar.gz`, 도구가 만든 결과 파일 | 버전과 무관 | 보관 기간 내내 증거가 그대로인지[4] |

표의 백업 폴더 파일 이름과 `com.apple.MobileBackup.plist` 는 관찰한 암호화하지 않은 로컬 백업에서 확인했습니다(확인 범위: iOS 27.0).

## 읽는 순서

1. [수집 방식 비교 (백업·파일 시스템·클라우드)](methods.md) — 로컬 백업, 파일 시스템 추출, 아이클라우드가 각각 무엇을 담고 무엇을 빠뜨리는지 비교하고, 상황에 맞는 방식을 고르는 기준을 다룹니다.
2. [압수와 보관 (전원·통신 차단·USB 제한 모드)](seizure-handling.md) — 통신을 끊는 세 가지 방법과 각각의 단점, 현장에서 남길 기록, USB 제한 모드가 연결을 막는 조건을 다룹니다.
3. [백업으로 수집 (Backup Acquisition)](backup-acquisition.md) — 백업을 만드는 곳과 저장 위치, 폴더 구조, 백업 안에서 먼저 확인할 파일과 키를 다룹니다.
4. [sysdiagnose로 수집 (sysdiagnose Collection)](sysdiagnose-collection.md) — 기기에서 sysdiagnose 를 만드는 방법, 기기 안 저장 위치, 묶음에 들어가는 로그와 보존 기간을 다룹니다.
5. [결과물 형식과 해시 (Extraction Formats·Hash)](formats-hash.md) — 수집 결과물의 형태와 해시를 계산·대조하는 방법, 두 번 수집하면 해시가 달라지는 이유를 다룹니다.

## 함께 볼 페이지

- [조사 절차 (Investigation Process)](../investigation-process.md) — 수집 앞뒤로 이어지는 조사 전체의 흐름
- [클라우드 데이터 (iCloud·계정 데이터 요청)](../cloud-data.md) — 계정 쪽 자료를 얻는 방법
- [로컬 백업 (Finder·Apple 기기 앱·iTunes Backup)](../../../01-foundations/backups/local-backup/index.md) — 백업 폴더와 `Manifest.db` 의 저장 형식
- [아이클라우드 백업 (iCloud Backup)](../../../01-foundations/backups/icloud-backup.md) — iCloud 백업의 구조
- [sysdiagnose 묶음 (sysdiagnose)](../../../01-foundations/backups/sysdiagnose.md) — sysdiagnose 묶음 안의 파일 구성
- [데이터 보호 (Data Protection)](../../../01-foundations/storage/data-protection/index.md) — 잠금 상태와 파일 보호 등급에 따라 읽을 수 있는 범위가 달라지는 이유
- [도구 검증 (Tool Validation)](../../reporting/tool-validation.md) — 여러 도구의 결과를 비교해 수집 도구를 검증하는 방법

## 참고 문헌

1. About encrypted backups on your iPhone, iPad, or iPod touch — Apple Support — https://support.apple.com/en-us/108353
2. Activating data connections securely — Apple Platform Security — https://support.apple.com/guide/security/activating-data-connections-securely-sec5044aad1b/web
3. iOS Forensic Methodology — Mobile Verification Toolkit(MVT) 문서 — https://docs.mvt.re/en/latest/ios/methodology/
4. NIST SP 800-101 Rev.1, Guidelines on Mobile Device Forensics — https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-101r1.pdf
5. iCloud data security overview — Apple Support — https://support.apple.com/en-us/102651
6. Reverse Engineering the iOS Backup — Rich Infante (2017) — https://www.richinfante.com/2017/3/16/reverse-engineering-the-ios-backup
7. Extracting and Analyzing Apple sysdiagnose Logs — ElcomSoft blog (2025-06) — https://blog.elcomsoft.com/2025/06/extracting-and-analyzing-apple-unified-logs/
