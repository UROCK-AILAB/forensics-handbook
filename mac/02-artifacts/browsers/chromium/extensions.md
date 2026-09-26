---
title: "확장 (Extensions)"
parent: "크롬·엣지·웨일"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1260
---

# 확장 (Extensions)

Chromium 계열 브라우저의 확장은 프로필 폴더의 `Extensions` 아래에 확장 ID별 폴더로 설치되고, 어떤 경로로 설치됐는지는 환경설정에 정수 하나로 남아서, 스토어를 거치지 않은 확장이나 관리 정책·외부 설정 파일로 들어온 확장을 가려낼 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

확장 (Extension)을 설치하면 확장 파일이 프로필 폴더의 `Extensions` 폴더 아래 확장 ID 이름의 폴더에 풀리고, 설치 상태와 설정은 같은 프로필의 `Preferences`·`Secure Preferences` 에 남습니다 [1]. 확장이 어떤 경로로 들어왔는지를 나타내는 설치 위치 (location) 값은 환경설정에 정수로 저장되고, 이 번호는 버전이 바뀌어도 달라지지 않습니다 [3]. 그래서 오래된 프로필과 새 프로필을 같은 표로 읽을 수 있습니다.

확장은 사용자가 스토어에서 직접 설치하는 것 말고도, 맥의 외부 확장 설정 파일이나 관리 정책으로 들어올 수 있습니다 [4]. 사고 대응에서는 확장이 어느 경로로 들어왔는지부터 이 값으로 확인합니다.

## 위치와 버전별 차이

```
<프로필>/Extensions/<확장 ID>/<버전>/...
```

Chrome·Chromium·Edge·Brave·Opera 모두 같은 구조이고, 수집할 때는 `Extensions` 아래를 10단계 깊이까지 모읍니다 [1][2]. `<버전>` 폴더 아래의 파일 구성은 검체에서 확인합니다. 프로필 폴더를 찾는 법은 [맥에서의 위치와 프로필 (Profiles)](profiles.md)에서 다룹니다.

크롬은 사용자 한 명에게만 적용되는 외부 확장 설정 폴더와 맥 전체에 적용되는 폴더를 따로 읽습니다 [4].

```
~<사용자>/Library/Application Support/Google/Chrome/External Extensions/
/Library/Application Support/Google/Chrome/External Extensions/
```

Edge와 웨일 (Whale)의 외부 확장 설정 폴더는 공개 자료가 없어 검체에서 확인합니다. 관리 정책(ExtensionInstallForcelist 등)으로 설치되는 확장도 있고 [4], 맥에서 정책을 담는 plist 를 포함한 관리 설정 전반은 [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md)에서 관리 설정 전반을 봅니다.

옛 버전 프로필에는 확장 활동 기록 파일 `Extension Activity` 와 확장 전용 쿠키 파일 `Extension Cookies` 가 있습니다 [1]. 최신 버전에도 있는지는 검체에서 확인합니다.

## 구조

### 설치 위치 값

| 값 | 이름 | 뜻 [3] |
|---|---|---|
| 0 | kInvalidLocation | 잘못된 값 |
| 1 | kInternal | 내부 `Extensions` 폴더의 crx, 사용자가 직접 설치한 확장 포함 |
| 2 | kExternalPref | 외부 폴더의 crx, prefs 경유 |
| 3 | kExternalRegistry | 외부 폴더, 윈도우 레지스트리 경유 |
| 4 | kUnpacked | 확장 설정 페이지에서 압축 풀린 확장을 불러옴 |
| 5 | kComponent | 브라우저 자체 구성 요소 |
| 6 | kExternalPrefDownload | 외부 폴더(prefs 경유), 업데이트 URL에서 설치 |
| 7 | kExternalPolicyDownload | 관리 정책 경유, 업데이트 URL에서 설치 |
| 8 | kCommandLine | `--load-extension` 명령줄 인자로 불러옴 |
| 9 | kExternalPolicy | 관리 정책 경유, 로컬 캐시에서 설치 |
| 10 | kExternalComponent | 구성 요소지만 업데이트 URL에서 설치 |

이 값이 `Preferences` 와 `Secure Preferences` 가운데 어느 파일의 어느 키에 들어 있는지는 검체에서 확인합니다. 확장 ID로 JSON을 검색해 그 확장의 항목을 찾은 뒤 설치 위치 값이 담긴 키를 봅니다.

### 외부 확장 설정 파일

외부 확장 설정 폴더에는 `<확장 ID>.json` 이름의 파일이 놓이고, 맥에서 쓰는 키는 웹 스토어 업데이트 URL을 적는 `external_update_url` 과 `supported_locales` 입니다 [4]. `external_crx`·`external_version` 키는 리눅스 전용입니다 [4]. 명세로 만든 예시는 아래와 같습니다.

```json
{
  "external_update_url": "<웹 스토어 업데이트 URL>"
}
```

맥 전체에 적용되는 폴더는 경로의 모든 폴더가 root 소유이고 그룹이 admin 또는 wheel이며, 다른 사용자가 쓸 수 없고 심볼릭 링크가 없어야 크롬이 읽습니다 [4]. 윈도우와 맥에서는 이렇게 들어온 확장을 사용자가 확인 대화상자에서 켜야 동작합니다 [4].

## 증거로서 의미

**증명하는 것.** 이 프로필의 `Extensions` 아래에 이 확장 ID의 폴더가 있다는 점, 환경설정에 적힌 설치 위치 값으로 그 확장이 스토어·외부 설정 파일·관리 정책·압축 풀린 폴더·명령줄 가운데 어느 경로로 들어왔는지입니다 [3]. 외부 확장 설정 폴더에 `.json` 파일이 있으면 그 확장 ID를 외부 설치로 넣으려 한 설정이 있었다는 뜻입니다 [4].

**증명하지 못하는 것.** 폴더와 설정만으로는 확장이 언제 설치됐는지, 사용자가 실제로 켜서 썼는지는 알 수 없습니다. 설치 시각을 담는 환경설정 키는 검체에서 따로 찾아야 합니다. 외부 설정 파일이 있어도 사용자가 확인 대화상자에서 켜지 않았다면 동작하지 않아서 [4], 설정 파일만 보고 확장이 동작했다고 적지 않습니다. 설치 위치 값 1(kInternal)에는 사용자가 직접 설치한 확장이 포함되지만 [3], 값만으로 설치한 사람이 누구인지는 알 수 없습니다.

보고서에는 "이 프로필의 환경설정에 이 확장 ID가 설치 위치 값 4(압축 풀린 확장)로 기록되어 있고, `Extensions` 폴더에 같은 ID의 폴더가 있다" 처럼 씁니다.

## 탐지 포인트

설치 위치 값 4(kUnpacked)와 8(kCommandLine)은 스토어를 거치지 않은 확장이라서 [3] 사고 대응 때 먼저 봅니다. 값 8은 브라우저를 `--load-extension` 인자로 실행했다는 뜻이라서, 브라우저를 그 인자로 띄우는 실행 에이전트나 로그인 항목이 있는지 함께 찾습니다. 값 7과 9는 관리 정책으로 들어온 확장이라서 조직이 배포한 것인지 구성 프로파일로 확인하고, 값 2와 6은 외부 확장 설정 폴더에 짝이 되는 `.json` 파일이 있는지 확인합니다 [3][4].

확장이 받은 파일은 방문·다운로드 기록의 `downloads` 표에 확장 정보가 붙어 남을 수 있어서, [방문·다운로드 기록 (History)](history-downloads.md)에서 `by_ext_id` 칸을 함께 봅니다.

## 함정과 한계

- **프로필마다 따로.** 확장은 프로필 단위로 설치되어서, 한 프로필만 보면 다른 프로필의 확장을 놓칩니다.
- **폴더와 설정이 어긋남.** `Extensions` 폴더의 ID 목록과 환경설정의 ID 목록을 맞춰 보고, 한쪽에만 있는 ID는 왜 그런지 확인하기 전까지 한쪽 근거만으로 설치 여부를 적지 않습니다.
- **압축 풀린 확장의 위치.** 값 4 확장은 확장 설정 페이지에서 폴더를 골라 불러온 것이라서 [3], 파일이 `Extensions` 폴더 밖에 있을 수 있습니다.
- **다루지 않은 경로.** Edge·웨일의 외부 확장 설정 폴더와 관리 정책 plist 경로는 이 페이지에서 다루지 않으므로 검체에서 찾습니다.

## 직접 분석해 보기

### 파일로 한 번

검체의 모든 프로필에서 확장 ID 폴더와 외부 확장 설정 파일을 찾습니다.

```sh
find "/Volumes/<검체>/Users" -maxdepth 12 -type d -path "*/Extensions/*" 2>/dev/null
ls -le "/Volumes/<검체>/Library/Application Support/Google/Chrome/External Extensions/"
```

외부 확장 설정 폴더가 있으면 폴더마다 소유자·그룹·권한을 확인해, 앞에서 말한 조건(root 소유, 그룹 admin 또는 wheel, 다른 사용자 쓰기 불가)에 맞는지 봅니다 [4]. `.json` 파일은 텍스트로 열어 `external_update_url` 값을 적습니다.

### 환경설정으로 한 번

`Preferences` 와 `Secure Preferences` 사본을 `python3 -m json.tool` 로 들여쓰기를 맞춰 연 뒤, 위에서 찾은 확장 ID로 검색합니다. 그 확장의 항목에서 설치 위치 정수를 찾아 위 표로 풀고, `Extensions` 폴더 목록과 ID를 하나씩 맞춰 봅니다. 공개 수집 도구가 ForensicArtifacts 정의로 `Extensions` 아래를 모았다면 [2], 도구 결과의 ID 목록과 환경설정의 ID 목록이 같은지 확인합니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [방문·다운로드 기록 (History)](history-downloads.md) | 확장이 시작한 다운로드와 확장 설치 전후의 방문을 봅니다 |
| [구성 프로파일 (Configuration Profiles·MDM)](../../persistence/configuration-profiles.md) | 값 7·9 확장이 관리 정책으로 배포된 것인지 확인합니다 |
| [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](../../persistence/launchd/index.md) | 값 8 확장을 불러오는 명령줄로 브라우저를 띄우는 항목이 있는지 찾습니다 |
| [파일 시스템 이벤트 (FSEvents)](../../filesystem/fsevents/index.md) | 확장 폴더와 외부 확장 설정 파일이 만들어진 흔적을 찾습니다 |
| [악성 코드 지속성 찾기 (Persistence)](../../../04-scenarios/incident/persistence.md) | 확장을 지속성 수단의 하나로 놓고 다른 위치와 함께 봅니다 |

## 실습

공개 검체(NIST CFReDS 등)의 macOS 이미지로 풀어 봅니다.

1. 프로필마다 `Extensions` 아래의 확장 ID 폴더를 모두 적어 보세요.
2. 환경설정에서 확장마다 설치 위치 값을 찾아 위 표의 이름으로 바꿔 보세요.
3. 설치 위치 값이 4 또는 8인 확장이 있는지, 있다면 파일이 어디에 있는지 찾아보세요.
4. 사용자별·맥 전체 외부 확장 설정 폴더가 있는지, 있다면 폴더 권한이 조건에 맞는지 확인해 보세요.

## 참고 문헌

1. Forensics Wiki, "Google Chrome" — https://forensics.wiki/google_chrome/
2. ForensicArtifacts, webbrowser.yaml — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/webbrowser.yaml
3. Chromium 소스, extensions/common/mojom/manifest.mojom — https://chromium.googlesource.com/chromium/src/+/HEAD/extensions/common/mojom/manifest.mojom
4. Chrome for Developers, "Alternative extension installation methods" — https://developer.chrome.com/docs/extensions/how-to/distribute/install-extensions
