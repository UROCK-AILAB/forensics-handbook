---
title: "드롭박스"
parent: "아티팩트 · 클라우드·애플 앱"
nav_order: 1530
---

# 드롭박스 (Dropbox)

드롭박스 (Dropbox) 맥 앱은 사용자 홈의 `~/.dropbox/info.json` 에 연결된 계정 종류와 동기화 폴더 위치를 적어 두고, File Provider판부터는 동기화 폴더를 `~/Library/CloudStorage/` 아래로 옮겨서, 이 두 곳을 먼저 보면 어느 계정이 어느 폴더와 동기화됐는지 가려낼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

`info.json` 은 다른 프로그램이 드롭박스 폴더를 찾을 수 있도록 드롭박스가 남겨 두는 파일이고, 다른 프로그램은 이 파일을 읽어 폴더 위치를 알아냅니다 [2]. 파일 안에는 개인 계정과 업무 계정이 따로 적히고, 계정마다 동기화 폴더 경로, 사용자와 컴퓨터 쌍을 나타내는 숫자, 업무 계정 여부, 요금제가 들어 있습니다 [2].

동기화 폴더 쪽은 앱이 Apple의 파일 공급자 방식으로 옮겨 가면서 자리와 모양이 바뀌었습니다. File Provider판은 폴더를 `~/Library/CloudStorage/` 로 옮겼고, 디스크 여유가 적으면 파일을 자동으로 "온라인 전용"으로 바꿉니다 [1]. 파일 공급자 방식이 로컬 사본을 다루는 원리는 [파일 공급자 (File Provider)](file-provider.md)에서 다루고, 이 페이지는 드롭박스에 고유한 변화와 `info.json` 을 다룹니다.

## 위치와 버전별 차이

| 구분 | 동기화 폴더 위치 | 조건 |
|---|---|---|
| File Provider판 | `~/Library/CloudStorage/` 아래 [1] | macOS 12.5 이상 필요, 최신 macOS 권장 [1] |
| File Provider판이 아닌 설치 | `info.json` 의 `path` 값으로 확인. 예: `/Users/<username>/Dropbox (Personal)` 형태 [2] | macOS 12.5 미만에서는 File Provider판을 쓸 수 없음 [1] |

`info.json` 은 두 판 모두 `~/.dropbox/info.json` 에 있습니다 [2]. 다만 알려진 `path` 예시는 옛 위치 형태라서, File Provider판에서 이 값이 `~/Library/CloudStorage/` 아래 경로로 바뀌는지는 실제 데이터에서 값을 직접 읽어 확인합니다. File Provider판으로 바뀐 날짜와 자동 전환 여부를 다룬 공개 자료는 없습니다.

File Provider판에서는 드롭박스 폴더가 Finder 사이드바의 "즐겨찾기 (Favorites)"가 아니라 "위치 (Locations)"에 보이고, Finder 도구 막대에 드롭박스가 더는 나타나지 않으며, 동기화 아이콘이 macOS 표준 모양으로 바뀌었습니다 [1]. 호환 외장 드라이브로 드롭박스 폴더를 옮기는 기능도 일부 사용자에게 배포 중이라서 [1], 동기화 폴더가 내장 디스크 밖에 있을 수 있습니다.

클라이언트 내부 데이터베이스와 로그 파일, 설치·자동 실행 흔적의 구체 경로는 공개 분석 자료에 나와 있지 않아 실제 데이터로 확인해야 합니다. ForensicArtifacts 정의(macos.yaml)에도 드롭박스 항목이 없어서 [3], 이 정의만 쓰는 도구로 자동 수집하면 `~/.dropbox/` 와 동기화 폴더가 빠질 수 있습니다.

## 구조

`info.json` 은 JSON 텍스트 파일이고, 최상위 키가 계정 종류를 나타냅니다 [2].

| 위치 | 키 | 뜻 |
|---|---|---|
| 최상위 | `personal` | 개인 계정 항목 [2] |
| 최상위 | `business` | 업무 계정 항목 [2] |
| 계정 항목 안 | `path` | 드롭박스 폴더 위치 [2] |
| 계정 항목 안 | `host` | 사용자와 컴퓨터 쌍을 나타내는 숫자 [2] |
| 계정 항목 안 | `is_team` | 업무 계정인지 여부(불리언) [2] |
| 계정 항목 안 | `subscription_type` | 요금제 [2] |

연결된 계정이 여럿이면 계정 종류마다 따로 나오고, 하나뿐이면 한 항목만 있습니다 [2]. 예시는 아래와 같습니다 [2].

```json
{"personal": {"path": "/Users/<username>/Dropbox (Personal)", "host": 123456789, "is_team": false, "subscription_type": "Basic"}, "business": {...}}
```

`host` 의 숫자는 예시 값입니다. 이 숫자를 드롭박스 계정 번호나 기기 일련번호로 바꿔 읽는 방법은 공개된 자료가 없습니다.

## 증거로서 의미

**증명하는 것.** `info.json` 에 `personal` 이나 `business` 항목이 있으면 그 사용자 홈에서 드롭박스 앱이 그 종류의 계정과 연결된 적이 있다는 기록이고, `path` 는 그 계정의 동기화 폴더가 어디에 있었는지, `is_team` 과 `subscription_type` 은 업무 계정인지와 요금제가 무엇이었는지를 알려 줍니다 [2]. 개인 계정과 업무 계정이 함께 적혀 있으면 한 맥에서 두 계정이 모두 연결됐던 기록이라서, 업무 자료가 개인 계정 폴더로 옮겨졌는지 따질 때 두 폴더를 나눠 보는 출발점이 됩니다. `~/Library/CloudStorage/` 아래에 드롭박스 폴더가 있으면 File Provider판이 동기화 폴더를 만든 기록입니다 [1].

**증명하지 못하는 것.** `info.json` 에는 알려진 시각 키가 없어서, 계정을 언제 연결했는지는 이 파일만으로 말할 수 없습니다. 동기화 폴더에 파일 이름이 보여도 그 내용이 로컬 디스크에 있다고 단정하지 않는데, 디스크 여유가 적으면 파일이 자동으로 온라인 전용이 되고 "오프라인에서 사용 가능"으로 표시한 파일만 디스크 공간을 차지하기 때문입니다 [1]. 폴더 안에 파일이 있다는 사실만으로 사용자가 그 파일을 올렸거나 다른 사람과 공유했다고도 단정하지 않습니다.

보고서에는 "이 사용자 홈의 `info.json` 에 업무 계정 항목이 있고, 그 `path` 값은 이 경로다" 처럼 파일이 적은 만큼만 쓰고, 동기화 폴더 안 파일은 내용을 확보했는지를 파일마다 따로 적습니다.

## 시각 해석

`info.json` 안에는 알려진 시각 값이 없습니다. 파일 자체의 파일 시스템 시각은 앱이 이 파일을 쓴 때를 보여 줄 수 있지만, 앱이 언제 이 파일을 다시 쓰는지는 공개 자료에 나와 있지 않아서 실제 데이터에서 확인된 범위만 씁니다. 동기화 폴더 안 파일의 시각도 같은 조건이라서, 폴더 안 변경 흐름은 [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md)와 맞춰 보고, 시각 값을 읽는 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따릅니다.

## 함정과 한계

- **내용이 없는 파일.** 온라인 전용 파일은 이름만 보이고 내용이 로컬에 없을 수 있습니다 [1]. 해시를 계산하거나 내용 검색을 하기 전에 파일마다 내용이 있는지 먼저 확인합니다.
- **패키지가 파일로 보임.** 새 macOS 패키지(.pages, .numbers, .key)는 File Provider판에서 폴더가 아니라 보통 파일로 보입니다 [1]. 폴더 목록을 옛 판 데이터와 비교할 때 항목 개수와 모양이 다를 수 있습니다.
- **지원하지 않는 항목.** Photos 보관함, Final Cut Pro 보관함, Adobe InDesign 잠금 파일은 File Provider판이 지원하지 않는 항목이라서 [1], 드롭박스 폴더 안에 있어도 동기화됐다고 보지 않고 따로 확인합니다.
- **경로 길이.** 경로 길이 제한은 8,096자입니다 [1]. 이 길이를 넘는 경로의 파일이 어떻게 처리되는지는 공개 자료에 나와 있지 않아 실제 데이터로 확인합니다.
- **폴더가 외장 드라이브에.** 외장 드라이브로 폴더를 옮기는 기능이 있어서 [1], `info.json` 의 `path` 가 외장 볼륨을 가리키면 그 드라이브도 수집 대상에 넣습니다.
- **옛 위치와 새 위치.** File Provider판으로 바뀌기 전과 뒤에 폴더 자리가 다르므로 [1], 옛 위치에 남은 파일과 `~/Library/CloudStorage/` 아래 파일을 따로 봅니다.
- **내부 기록.** 클라이언트 내부 데이터베이스와 로그를 다룬 공개 분석 자료는 없습니다. 도구가 이런 기록을 보여 주면 그 경로와 필드의 뜻에 대한 근거를 먼저 확인합니다.

## 직접 분석해 보기

### 헥스로 한 번

`info.json` 은 텍스트라서 헥스로 열면 첫 바이트부터 JSON 문자가 그대로 보입니다. 아래는 위 `info.json` 예시 [2]의 앞부분을 UTF-8로 적은 것이고, 특정 기기에서 나온 값이 아닙니다.

```
오프셋  바이트                                              문자
0000    7B 22 70 65 72 73 6F 6E 61 6C 22 3A 20 7B 22 70     {"personal": {"p
0010    61 74 68 22 3A 20 22 2F 55 73 65 72 73 2F           ath": "/Users/
```

첫 바이트 `7B` 가 `{` 이고 바로 뒤에 계정 종류 키가 나오므로, 헥스 편집기에서 `personal` 이나 `business` 문자열을 검색하면 계정 항목의 시작을 찾을 수 있습니다. 지운 `info.json` 을 비할당 영역에서 찾을 때도 이 두 키와 `subscription_type` 문자열을 검색어로 쓸 수 있고, 검색 방법은 [콘텐츠 검색 (Content Search)](../../03-techniques/analysis/content-search.md)에서 다룹니다.

### 공개 도구로 한 번

마운트한 사본에서 사용자 홈마다 `info.json` 을 보기 좋게 풀어 보고, 동기화 폴더 목록을 함께 뽑아 둡니다.

```
python3 -m json.tool "/Volumes/evidence/Users/사용자/.dropbox/info.json"
ls -la "/Volumes/evidence/Users/사용자/Library/CloudStorage/"
ls -laR "/Volumes/evidence/Users/사용자/Library/CloudStorage/" > dropbox_list.txt
```

`jq` 같은 다른 JSON 도구를 써도 결과는 같습니다. `path` 값이 가리키는 폴더가 실제로 있는지, 두 번째 명령의 목록에 나오는 폴더와 맞는지 확인하고, 목록은 수집 당시의 모습으로 보존합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [파일 공급자 (File Provider)](file-provider.md) | 동기화 폴더의 로컬 사본과 내용이 없는 파일 |
| [설치한 앱과 영수증 (Applications·Receipts)](../system-account/installed-apps-receipts.md) | 드롭박스 앱이 설치돼 있었는지 |
| [로그인 항목 (Login Items)](../persistence/login-items.md) | 드롭박스가 로그인 때 자동으로 실행되도록 등록됐는지 |
| [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md) | 동기화 폴더 안 파일이 생기고 지워진 흐름 |
| [앱별 네트워크 사용량 (netusage)](../network/netusage.md) | 드롭박스 프로세스가 보낸 양 |
| [USB 저장 장치 (USB Storage)](../external-devices/usb/index.md) | `path` 가 외장 볼륨을 가리킬 때 그 장치의 연결 기록 |
| [원드라이브 (OneDrive)](onedrive.md), [구글 드라이브 (Google Drive)](google-drive.md) | 같은 맥에서 쓰인 다른 클라우드 저장소 |
| [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md) | 클라우드 동기화를 유출 경로로 따지는 흐름 |

## 실습

공개 시험 데이터(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 사용자 홈마다 `~/.dropbox/info.json` 이 있는지 찾고, 있으면 `personal` 과 `business` 가운데 어느 항목이 있는지 적어 보세요.
2. 각 계정 항목의 `path`, `is_team`, `subscription_type` 값을 뽑고, `path` 가 가리키는 폴더가 이미지에 실제로 있는지 확인해 보세요.
3. 이미지의 macOS 버전을 확인하고, 위 표를 보고 File Provider판을 쓸 수 있는 버전인지, `~/Library/CloudStorage/` 아래에 드롭박스 폴더가 있는지 맞춰 보세요.
4. 동기화 폴더 안 파일 가운데 크기는 있는데 내용을 읽을 수 없는 파일이 있는지 찾아보세요.

## 참고 문헌

1. Dropbox Help Center, "Expected changes with Dropbox for macOS on File Provider" — https://help.dropbox.com/installs/macos-support-for-expected-changes
2. Dropbox Help Center, "Programmatically locate Dropbox folder" (info.json) — https://help.dropbox.com/installs/locate-dropbox-folder
3. ForensicArtifacts, artifacts/data/macos.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
