---
title: "구글 드라이브"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1550
---

# 구글 드라이브 (Google Drive)

맥의 구글 드라이브 데스크톱 앱 (Drive for desktop)은 macOS 12.1부터 파일 공급자 방식으로 파일을 `~/Library/CloudStorage` 에 두고 관리 설정은 `com.google.drivefs.settings` 도메인에 남겨서, 이 맥이 어떤 방식으로 동기화했는지와 조직이 어떤 설정을 걸었는지를 읽을 수 있습니다.

이 페이지는 설정 위치, 관리 키, 동기화 방식을 다룹니다 [1][2]. 계정별 폴더와 동기화 DB, 로그는 공개된 분석 자료가 없어 검체에서 확인해야 하고, macOS가 클라우드 저장소 앱에 내주는 동기화 틀은 [파일 공급자 (File Provider)](file-provider.md)에서 다룹니다.

## 무엇을 기록하나 · 왜 생기나

관리자는 `com.google.drivefs.settings` 도메인에 키를 넣어 마운트 경로, 콘텐츠 캐시 위치와 크기, 로그인 때 자동 실행 여부를 정하고, 이 설정은 호스트 전체, 사용자 한 명, 관리 강제(override) 세 자리에 놓일 수 있습니다 [1]. 그래서 조사에서는 세 자리를 모두 열어 어느 범위에 어떤 값이 들어 있었는지 나눠서 적습니다.

동기화 방식은 macOS 버전에 따라 갈립니다. macOS 12.1 이상에서는 파일 공급자 방식을 쓰고, 그보다 앞선 버전에서는 마운트 포인트를 쓰는 예전 방식 (legacy streaming)을 씁니다 [1][2]. 방식에 따라 파일이 놓이는 자리와 관리 키가 먹히는지, 앱이 꺼졌을 때 파일을 열 수 있는지가 달라서, 설정 값을 읽기 전에 먼저 이 맥이 어느 방식이었는지를 가립니다.

## 위치와 버전별 차이

### 설정 위치

| 범위 | 경로 |
|---|---|
| 호스트 전체 | `/Library/Preferences/com.google.drivefs.settings` |
| 사용자 한 명 | `~/Library/Preferences/com.google.drivefs.settings` |
| 관리 강제 (override) | `/Library/Managed Preferences/com.google.drivefs.settings.plist` |

앞의 두 자리는 디스크의 파일 이름 끝에 `.plist` 가 붙을 수도 있어서 [1], 검체에서는 두 이름을 모두 찾아봅니다.

### 동기화 방식과 macOS 버전

| macOS | 방식 | 파일 자리 | 관리 키 |
|---|---|---|---|
| 12.1 미만 | 예전 방식(마운트 포인트) | `DefaultMountPoint` 로 정한 마운트 경로이고, 콘텐츠 캐시 기본 위치는 `~/Library/Application Support/Google/DriveFS` 입니다 [1][2] | `DefaultMountPoint`, `ContentCachePath`, `ContentCacheMaxKbytes` 가 적용됩니다 [1] |
| 12.1 이상 | 파일 공급자 | 기본으로 `~/Library/CloudStorage` 에 있고 사용자가 위치를 바꿀 수 없으며, 캐시 위치는 macOS가 정합니다 [1][2] | 앞의 세 키가 적용되지 않습니다 [1] |

두 방식은 Finder 사이드바에서도 자리가 달라서, 파일 공급자 방식은 "Locations" 아래에, 예전 방식은 "Favorites" 아래에 보입니다 [2]. 라이브 대응 때 찍은 화면이나 사용자 진술로 방식을 가릴 때 이 차이를 씁니다.

### 공개 자료가 없는 것

| 항목 | 상태 |
|---|---|
| macOS 12.1 이상에서 사용자가 예전 방식을 고를 수 있는지 | 공개 자료 없음, 검체에서 확인 |
| 예전 방식의 마운트 경로 기본값(`/Volumes/GoogleDrive` 등) | 공개 자료 없음, 검체에서 확인 |
| `~/Library/CloudStorage/` 아래 폴더 이름 규칙(`GoogleDrive-<계정 이메일>` 등) | 공개 자료 없음, 검체에서 확인 |
| `~/Library/Application Support/Google/DriveFS/` 아래 계정별 폴더와 DB(`metadata_sqlite_db`, `mirror_sqlite.db` 등), `Logs/` 폴더 | 공개 자료 없음, 검체에서 확인 |
| macOS 12.1 이상에서 위 DriveFS 폴더에 무엇이 남는지 | 공개 자료 없음, 검체에서 확인 |
| DB 안의 표·칸 이름과 시각 기준 | 공개 자료 없음, 검체에서 확인 |

## 구조

설정은 속성 목록 파일이라서 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)을 따릅니다. 아래는 관리 키 가운데 조사에서 뜻이 있는 것만 고른 표입니다 [1].

| 키 | 값 | 뜻 |
|---|---|---|
| `DefaultMountPoint` | 경로(`~` 와 환경 변수 허용) | 드라이브를 마운트할 경로입니다. macOS 12.1 이상에는 적용되지 않습니다. |
| `ContentCachePath` | 경로(APFS·HFS+·NTFS) | 콘텐츠 캐시 위치입니다. macOS 12.1 이상에는 적용되지 않습니다. |
| `ContentCacheMaxKbytes` | 크기 | 콘텐츠 캐시 크기 상한입니다. macOS 12.1 이상에는 적용되지 않습니다. |
| `AutoStartOnLogin` | boolean | 로그인 때 앱을 자동으로 실행할지 정합니다. macOS 12.1 이상에서 적용되는지는 공개 자료가 없습니다. |

관리 강제 자리의 설정이 plist로 직접 들어갔는지 구성 프로파일로 배포됐는지는 [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md)에서 설치된 프로파일과 맞춰 가립니다.

## 증거로서 의미

**증명하는 것.** 설정 도메인에 키가 있으면 그 설정이 이 맥의 해당 범위에 걸려 있었다는 기록이 있다는 뜻이고, `DefaultMountPoint` 나 `ContentCachePath` 에 든 경로는 예전 방식에서 파일과 캐시를 어디에 두도록 설정했는지 알려 줍니다 [1]. 파일 공급자 방식에서는 앱이 꺼져 있어도 내려받은 파일과 로컬에서 만든 파일을 열 수 있어서 [2], 이 방식의 드라이브 폴더에 내용이 있는 파일이 있으면 그 파일의 로컬 사본이 이 맥에 있었다고 볼 근거가 됩니다. 예전 방식에서는 앱이 꺼져 있으면 파일을 열 수 없습니다 [2].

파일 공급자 방식에서 구글 드라이브 폴더 안팎으로 파일을 끌어 놓으면 복사가 아니라 이동이라서 [2], 어떤 파일이 드라이브 폴더에 있고 원래 자리에서는 사라졌다면 지운 것이 아니라 옮긴 것일 수 있습니다. 유출을 따질 때 "옮겼다" 와 "복사했다" 를 가르는 근거로 씁니다.

**증명하지 못하는 것.** 설정 값만으로 파일이 실제로 올라갔는지, 어느 구글 계정으로 로그인했는지, 언제 동기화했는지는 알 수 없습니다. macOS 12.1 이상에서는 `DefaultMountPoint`, `ContentCachePath`, `ContentCacheMaxKbytes` 가 적용되지 않아서 [1], 값이 들어 있어도 그 경로가 실제로 쓰였다고 말하지 못합니다. 계정과 파일 목록을 담는 DB는 공개된 분석 자료가 없어서, 도구가 그런 파일에 뜻을 붙여 보여 주면 근거를 확인한 뒤에 씁니다.

보고서에는 "이 맥은 macOS 12.1 이상이었고, 사용자 홈의 `Library/CloudStorage` 아래에 구글 드라이브 폴더로 보이는 폴더와 그 안의 파일 항목이 있다" 처럼 기록이 보여 주는 만큼만 씁니다.

## 시각 해석

관리 키에는 시각 값이 없습니다. 설정이 언제 들어갔는지는 설정 파일의 수정 시각, [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md), 구성 프로파일 설치 기록으로 좁히고, 파일 수정 시각은 마지막으로 바뀐 때만 알려 준다는 점을 함께 적습니다. DriveFS DB 안의 시각 기준은 공개 자료가 없고, 맥 시각 값을 읽는 일반 규칙은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다.

## 함정과 한계

- **버전에 따라 무시되는 키.** macOS 12.1 이상에서는 마운트 경로와 캐시 관련 세 키가 적용되지 않습니다 [1]. 예전 macOS에서 옮겨 온 설정이 남아 있을 수 있어서, 값과 실제 파일 자리를 따로 확인합니다.
- **macOS가 정하는 캐시 위치.** 파일 공급자 방식에서는 캐시 위치를 macOS가 정해서 [1], `~/Library/Application Support/Google/DriveFS` 만 보고 캐시가 없다고 판단하지 않습니다.
- **이동과 복사.** 파일 공급자 방식에서 드라이브 폴더 안팎으로 끌어 놓으면 이동입니다 [2]. 원래 자리에서 사라진 파일을 곧바로 삭제로 적지 않습니다.
- **폴더 접근 승인.** 데스크탑, 문서, 다운로드, 이동식 볼륨, 사진 보관함에 접근하려면 시스템 설정의 개인 정보 보호 및 보안에서 승인이 필요할 수 있습니다 [2]. 승인 기록은 [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md)에서 확인합니다.
- **동기화 흔적.** 계정별 폴더, DB, 로그의 위치와 구조는 공개된 분석 자료가 없어 검체에서 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

설정 파일을 헥스 편집기로 열어 바이너리 plist인지 XML인지 첫 바이트로 가리고, 바이너리라면 오프셋 표를 따라 `DefaultMountPoint` 같은 키 문자열이 든 객체를 찾아갑니다. 머리말과 오프셋 표를 읽는 법은 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에서 다루고, 이 파일에 고유한 바이트 구조는 공개된 자료가 없어서 헥스 예시를 싣지 않습니다.

### 공개 도구로 한 번

사본을 만든 뒤 macOS의 `plutil` 로 세 자리의 설정을 차례로 엽니다.

```
plutil -p "Library/Preferences/com.google.drivefs.settings"
plutil -p "Library/Preferences/com.google.drivefs.settings.plist"
plutil -p "Library/Managed Preferences/com.google.drivefs.settings.plist"
```

키가 나오면 어느 범위에서 나왔는지 함께 적고, 이 맥의 macOS 버전과 맞춰 그 키가 적용되는 버전인지 확인합니다. 동기화 폴더 목록을 뽑는 방법은 [파일 공급자 (File Provider)](file-provider.md)의 절차를 따릅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [OS 버전과 설치 기록 (SystemVersion·InstallHistory)](../system-account/os-version-install-history.md) | macOS 12.1 앞뒤 어느 쪽이었는지, 언제 올렸는지 |
| [파일 공급자 (File Provider)](file-provider.md) | `~/Library/CloudStorage` 아래 폴더와 파일 상태 |
| [구성 프로파일 (Configuration Profiles·MDM)](../persistence/configuration-profiles.md) | 관리 강제 설정이 프로파일로 들어왔는지 |
| [로그인 항목 (Login Items)](../persistence/login-items.md) | `AutoStartOnLogin` 과 실제 로그인 항목 등록 |
| [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md) | 데스크탑·문서·다운로드 등에 접근을 승인했는지 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 드라이브 폴더로 파일이 옮겨진 흔적 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 구글 드라이브 프로세스가 보낸 양 |
| [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) | 클라우드 동기화를 유출 경로로 따지는 흐름 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 검체의 macOS 버전을 확인하고, 구글 드라이브가 파일 공급자 방식과 예전 방식 가운데 어느 쪽이었을지 적어 보세요.
2. 설정 세 자리에서 `com.google.drivefs.settings` 를 찾고, 어느 범위에 어떤 키가 있는지 표로 정리해 보세요.
3. `DefaultMountPoint` 나 `ContentCachePath` 가 있으면 그 경로가 검체에 실제로 있는지, 그 키가 이 macOS 버전에서 적용되는지 확인해 보세요.
4. 사용자 홈의 `Library/CloudStorage` 아래에서 구글 드라이브 폴더로 보이는 것을 찾고, 그렇게 판단한 근거를 적어 보세요.

## 참고 문헌

1. Google Workspace Admin Help, "Advanced Drive for desktop configuration" — https://knowledge.workspace.google.com/admin/drive/advanced-drive-for-desktop-configuration
2. Google Drive Help, Drive for desktop on macOS (File Provider) — https://support.google.com/drive/answer/12178485
