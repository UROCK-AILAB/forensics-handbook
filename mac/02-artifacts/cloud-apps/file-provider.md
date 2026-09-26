---
title: "파일 공급자"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1510
---

# 파일 공급자 (File Provider)

파일 공급자 (File Provider)는 클라우드 저장소 앱이 원격 파일을 맥의 폴더처럼 보여 주도록 Apple이 제공하는 프레임워크이고, 이 방식을 쓰는 앱의 동기화 폴더에서는 파일 이름이 보여도 내용이 로컬에 없을 수 있어서 수집과 해석에서 따로 챙겨야 합니다.

## 무엇을 기록하나 · 왜 생기나

클라우드 저장소 앱이 파일 공급자 확장(extension)을 만들어 두면, 다른 앱은 그 확장을 거쳐 원격 저장소와 동기화되는 파일과 폴더에 접근합니다 [1].

파일 공급자 자체가 하나의 기록 파일은 아니지만, 이 방식이 쓰이면 동기화 폴더의 자리와 파일이 로컬에 놓이는 방식이 바뀌어서 여러 클라우드 앱 아티팩트를 읽는 바탕이 됩니다. 제3자 앱이 이 방식으로 옮긴 예로, 드롭박스의 File Provider판은 폴더를 `~/Library/CloudStorage/` 로 옮겼습니다 [2]. 그 밖의 드롭박스 변화는 [드롭박스 (Dropbox)](dropbox.md)에서 다룹니다.

## 위치와 버전별 차이

| 구분 | 제공 OS | 로컬 사본을 관리하는 쪽 |
|---|---|---|
| File Provider 프레임워크 | macOS 10.15+, iOS·iPadOS 11.0+, Mac Catalyst 11.0+, visionOS 1.0+ [1] | 확장 종류에 따라 다름 |
| `NSFileProviderReplicatedExtension` (복제형) | macOS 11+, iOS 16+ [1] | 시스템 [1] |
| `NSFileProviderExtension` (복제형이 아닌 것) | iOS 11+ [1] | 확장 [1] |

복제형 확장에서는 시스템이 로컬 사본을 관리하고 확장은 로컬과 원격 사이의 동기화만 맡습니다 [1]. 복제형이 아닌 확장은 로컬 사본과 원격 파일의 자리표시자 (placeholder)를 확장이 직접 만들고 관리합니다 [1]. 표에 적힌 제공 OS로 보면 맥에서는 macOS 11부터 복제형을 쓸 수 있고, 복제형이 아닌 확장은 제공 OS에 macOS가 적혀 있지 않아서, 앱마다 어느 확장을 쓰는지는 앱 자료로 따로 확인합니다.

동기화 폴더는 `~/Library/CloudStorage/` 아래에 놓이는 예가 있지만 [2], 그 아래 폴더 이름 규칙은 앱마다 다를 수 있어 검체에서 확인합니다. 파일 공급자를 관리하는 시스템 데몬의 상태 DB 위치와 통합 로그 서브시스템은 공개된 분석 자료가 없습니다.

ForensicArtifacts 정의(macos.yaml)에는 File Provider나 CloudStorage 항목이 없어서 [3], 이 정의만 쓰는 도구로 자동 수집하면 `~/Library/CloudStorage/` 가 빠질 수 있습니다.

## 구조

### APFS의 동기화 뿌리 표시

APFS inode 플래그 가운데 `INODE_IS_SYNC_ROOT`(0x200000)는 fileproviderd 동기화 계층의 뿌리를 표시합니다. 플래그가 놓인 inode 필드와 그 오프셋은 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)에서 다루고, 이 비트가 켜진 디렉터리를 찾으면 어느 폴더가 파일 공급자 동기화의 시작점인지 파일 시스템 수준에서 가려낼 수 있습니다.

### 접근 권한

파일 공급자와 관련된 TCC 서비스 이름으로 `kTCCServiceFileProviderDomain` 과 `kTCCServiceFileProviderPresence` 가 있고, 앞의 것은 iCloud Drive 접근 권한으로 풀이되고, 뒤의 것은 macOS 10.15에서 추가됐습니다. 권한 DB를 읽는 법과 각 서비스의 해석은 [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md)에서 다룹니다.

## 증거로서 의미

**증명하는 것.** `~/Library/CloudStorage/` 아래에 폴더가 있으면 그 사용자 계정에서 파일 공급자 방식을 쓰는 클라우드 앱이 동기화 폴더를 만들었다는 기록이 있다는 뜻입니다 [2]. 동기화 뿌리 플래그가 켜진 디렉터리는 파일 공급자 동기화 계층의 시작점으로 표시된 폴더라는 파일 시스템 기록입니다.

**증명하지 못하는 것.** 동기화 폴더에 파일 이름이 보여도 그 파일 내용이 로컬 디스크에 있다고 단정하지 않습니다. 복제형이 아닌 확장은 원격 파일의 자리표시자를 만들고 [1], 복제형에서는 로컬 사본을 시스템이 관리해서 [1] 어느 파일의 내용이 내려와 있는지를 앱 설정만으로 알 수 없으므로, 이름과 내용이 함께 있는지는 파일마다 확인합니다. 폴더가 있다는 사실만으로 사용자가 그 안의 파일을 열었거나 올렸다고도 단정하지 않습니다.

보고서에는 "`~/Library/CloudStorage/` 아래 이 이름의 폴더가 있고, 그 안에 이 이름의 파일 항목이 있다" 처럼 쓰고, 내용을 확보했는지는 파일마다 따로 적습니다.

## 시각 해석

파일 공급자에 고유한 시각 값은 알려진 것이 없습니다. 동기화 폴더 안 파일의 파일 시스템 시각은 로컬 사본이 만들어지고 바뀐 때를 보여 줄 수 있지만, 그 사본을 시스템이 관리하는 구조라서 [1] 내려받기나 동기화가 시각에 어떤 영향을 주는지는 검체에서 확인한 범위만 씁니다. 시각을 읽는 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따르고, 폴더 안 변경의 흐름은 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)와 맞춰 봅니다.

## 함정과 한계

- **내용이 없는 파일.** 이름만 있고 내용이 내려오지 않은 파일은 이미징할 때 내용 없이 들어올 수 있습니다. 이런 파일의 크기·확장 속성·플래그가 어떻게 보이는지는 공개 자료가 없어서, 해시를 계산하기 전에 파일마다 내용이 있는지 먼저 봅니다.
- **옛 위치와 새 위치.** 같은 앱이라도 파일 공급자 방식으로 바뀌기 전과 뒤에 폴더 자리가 다를 수 있습니다 [2]. 옛 위치에 남은 파일과 새 위치의 파일을 따로 봅니다.
- **자동 수집에서 빠짐.** ForensicArtifacts 정의에 이 경로가 없습니다 [3].
- **데몬 기록.** 파일 공급자 데몬의 상태 DB와 로그는 공개된 분석 자료가 없습니다. 도구가 이런 기록을 보여 주면 그 경로와 뜻의 근거를 먼저 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

명세로 만든 예시로, 어떤 디렉터리 inode의 내부 플래그 값을 읽었더니 아래와 같다고 해 봅니다.

```
플래그 값          : 0x0000000000208000
INODE_IS_SYNC_ROOT : 0x0000000000200000
AND 결과           : 0x0000000000200000  → 0이 아님, 비트가 켜짐
```

두 값을 비트 AND 해서 0이 아니면 이 디렉터리가 동기화 뿌리로 표시된 것입니다. 예시의 다른 비트는 설명용으로 넣은 값이고, 플래그 필드를 inode 안에서 찾아가는 법은 [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md)에서 다룹니다.

### 공개 도구로 한 번

마운트한 사본에서 사용자마다 동기화 폴더를 나열하고, 파일의 크기와 확장 속성을 함께 뽑아 둡니다.

```
ls -la "/Volumes/evidence/Users/사용자/Library/CloudStorage/"
ls -laR "/Volumes/evidence/Users/사용자/Library/CloudStorage/" > cloudstorage_list.txt
xattr -l "/Volumes/evidence/Users/사용자/Library/CloudStorage/폴더/파일"
```

나열한 목록은 수집 당시의 모습으로 보존하고, 파일마다 내용이 있는지는 해시 계산이나 파일 열기로 확인한 결과만 적습니다. 확장 속성의 이름과 값이 무엇을 뜻하는지는 공개된 자료가 없어서, 뽑은 값은 그대로 기록만 해 둡니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [드롭박스 (Dropbox)](dropbox.md) | 파일 공급자로 옮긴 제3자 앱의 실제 변화 |
| [아이클라우드 드라이브 (iCloud Drive·CloudDocs)](icloud-drive.md) | Apple 자체 동기화 서비스의 항목 목록 |
| [원드라이브 (OneDrive)](onedrive.md), [구글 드라이브 (Google Drive)](google-drive.md) | 같은 폴더 아래 놓일 수 있는 다른 클라우드 앱 |
| [APFS 구조 (APFS)](../../01-foundations/disk-volume/apfs/index.md) | 동기화 뿌리 플래그가 켜진 디렉터리 |
| [개인 정보 보호 권한 (TCC)](../credentials/tcc/index.md) | 파일 공급자 관련 권한을 받은 앱 |
| [맥 증거 확보 (Acquisition)](../../03-techniques/process-acquisition/evidence-acquisition/index.md) | 내용이 없는 파일이 섞인 폴더를 수집할 때의 주의 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 사용자 홈마다 `~/Library/CloudStorage/` 가 있는지, 있으면 그 아래 어떤 폴더가 있는지 적어 보세요.
2. 검체의 macOS 버전을 확인하고, 위 표로 보아 복제형 확장을 쓸 수 있는 버전인지 따져 보세요.
3. 동기화 폴더 안 파일 가운데 크기는 있는데 내용을 읽을 수 없는 파일이 있는지 찾아보세요.
4. APFS 도구로 동기화 뿌리 플래그가 켜진 디렉터리를 찾고, 그 경로가 1번에서 찾은 폴더와 맞는지 확인해 보세요.

## 참고 문헌

1. Apple Developer, File Provider 프레임워크 문서 — https://developer.apple.com/tutorials/data/documentation/fileprovider.json
2. Dropbox Help Center, "Expected changes with Dropbox for macOS on File Provider" — https://help.dropbox.com/installs/macos-support-for-expected-changes
3. ForensicArtifacts, artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
