# 확장 프로그램 (Extensions)

## 한 줄 요약

크롬 계열 브라우저는 확장 프로그램 (Extension) 의 파일을 프로필 폴더의 `Extensions` 폴더에 풀어 둡니다. 확장마다의 설정은 `Secure Preferences` 파일의 `extensions.settings` 에 JSON 으로 남으며, 여기에는 설치 경로의 종류, 처음 설치한 시각, 마지막 업데이트 시각, 꺼진 이유, manifest 전체가 들어 있습니다.

> 이 페이지에서 "(관찰)" 을 붙인 내용은 Windows 11(빌드 26200) PC 한 대의 Chrome 153·Edge 151 에서 본 것입니다. 다른 판이나 다른 PC 에서는 다를 수 있습니다. 값의 뜻은 2026년 9월 크로미엄 (Chromium) 소스와 Chrome for Developers 문서를 따릅니다.

## 무엇을 기록하나 · 왜 생기나

확장 프로그램은 브라우저에 기능을 더하는 작은 프로그램이며, `manifest.json` 과 스크립트(js)·페이지(html)·이미지 파일로 이뤄집니다 (관찰). `manifest.json` 에는 확장의 이름·버전·권한이 적힙니다. 브라우저는 확장 파일을 `Extensions\<확장 ID>\<버전>_0\` 에 두고, 확장마다 설치 경로의 종류, 설치·업데이트 시각, 권한, 꺼진 이유를 설정 파일에 적습니다 (관찰).

확장은 브라우저 안에서 도는 프로그램이라서 어느 확장을 언제, 어떤 경로로 넣었는지가 조사에서 중요합니다. 악성 확장을 찾을 때도, 사용자가 쓴 도구를 확인할 때도 이 기록을 봅니다.

확장은 웹 스토어 말고 다른 경로로도 들어옵니다. 레지스트리로 밖에서 설치하거나, 개발자 모드로 압축 풀린 폴더를 불러오거나, 관리자 정책으로 넣을 수 있으며, 설정의 `location` 값이 이 경로를 알려 줍니다.

## 위치와 버전별 차이

확장 기록은 Windows 버전보다 브라우저 판에 따라 달라집니다. 브라우저별 `User Data` 위치와 Windows 버전별 폴더 위치는 [크롬 계열 브라우저](index.md) 에 있습니다.

### 폴더와 파일 (프로필 폴더 기준, 관찰)

| 위치 | 담긴 것 | 형식 |
|---|---|---|
| `Extensions\<확장 ID>\<버전>_0\` | 확장 파일 (`manifest.json`, js, html, 이미지 등) | 폴더 |
| `Extensions\<확장 ID>\<버전>_0\_metadata\` | `computed_hashes.json`, `verified_contents.json`. 웹 스토어에서 받은 확장 폴더에 있었습니다 | JSON |
| `Extensions\Temp` | 폴더 | |
| `Secure Preferences` | `extensions.settings` (확장별 설정 목록) | JSON |
| `Preferences` | `extensions` 아래 `pinned_extensions`, `commands`, `theme`, `install_signature`, `last_chrome_version` | JSON |
| `Local Extension Settings\<확장 ID>\` | CURRENT·LOCK·LOG·MANIFEST-·*.log·*.ldb | LevelDB |
| `Sync Extension Settings`, `Managed Extension Settings` | 폴더 | |
| `Extension State`, `Extension Rules`, `DNR Extension Rules`, `Extension Scripts` | 폴더 | |
| `Extension Cookies` | 파일 | SQLite |
| `ExtensionActivityEdge`, `ExtensionActivityComp` | Edge 에만 있었습니다 | `ExtensionActivityEdge` 는 SQLite |

- `Secure Preferences` 에는 확장 설정마다 검증값 (MAC) 이 붙어 있었습니다. `protection.macs.extensions.settings` 같은 키입니다.
- `ExtensionActivityEdge` 에는 `string_ids`, `url_ids`, `activitylog_edge_compressed`, `activitylog_edge_submissions`, `activitylog_edge_excluded_ids` 표가 있었습니다.
- `activitylog_edge_compressed` 의 열은 `extension_id_x`, `time`, `action_type`, `api_name_x`, `args_x`, `page_url_x`, `page_title_x`, `arg_url_x`, `other_x` 입니다.
- 관찰한 PC 에서는 이 표가 모두 0행이었습니다. 언제 기록하는지는 확인하지 못했습니다.
- LevelDB 를 읽는 법은 [LevelDB 저장소](../../../01-foundations/database-log-formats/leveldb.md) 에서, SQLite 를 읽는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md) 에서 다룹니다.

### 판에 따른 차이

| 항목 | 내용 |
|---|---|
| 설정 목록 위치 | 관찰한 Chrome 153·Edge 151 모두 `Secure Preferences` 의 `extensions.settings` 에 있었습니다. `Preferences` 의 `extensions` 에는 `settings` 가 없었습니다. 옛 판에서 `Preferences` 에 목록이 있던 시기가 있는지는 확인하지 못했습니다. 그래서 두 파일을 모두 봅니다. |
| `install_time`·`state` | 관찰한 두 판에는 이 키가 없었습니다. 이 키를 읽는 옛 도구는 요즘 판에서 빈 값을 냅니다. 키가 바뀐 판 번호는 확인하지 못했습니다. |
| Edge 전용 | `ExtensionActivityEdge`·`ExtensionActivityComp` 는 Edge 에만 있었습니다. |
| Whale | 확장 폴더와 설정 구조가 같은지, Whale 스토어에서 받은 확장을 어떻게 표시하는지는 확인하지 못했습니다. |

### 밖에서 설치하는 경로 (외부 설치)

Chrome for Developers 문서는 웹 스토어 밖에서 확장을 설치하는 방법으로 레지스트리와 설정(JSON) 파일을 적습니다.

| 방법 | 내용 |
|---|---|
| 레지스트리 (32비트 Windows) | `HKEY_LOCAL_MACHINE\Software\Google\Chrome\Extensions` |
| 레지스트리 (64비트 Windows) | `HKEY_LOCAL_MACHINE\Software\Wow6432Node\Google\Chrome\Extensions` |
| 레지스트리 값 | 위 키 아래에 확장 ID 이름의 키를 만들고 `update_url` 값을 둡니다 |
| 설정 파일 | 이름은 `{확장ID}.json` 입니다. 문서에 적힌 위치는 macOS·Linux 뿐입니다. 키는 `external_update_url`, `external_crx`(Linux 만), `external_version`, `supported_locales` 입니다 |

- Windows·macOS 에서는 밖에서 설치한 확장을 사용자가 확인 창에서 켜야 합니다.
- Chrome 33 부터 Windows 에서는 로컬 CRX 파일 경로로 밖에서 설치하지 못합니다. Windows·Mac 에서는 웹 스토어 update URL 만 쓸 수 있습니다.
- 레지스트리 키나 JSON 파일을 지우면 그 확장도 없어집니다.
- 사용자가 브라우저 화면에서 그 확장을 지우면, 브라우저는 다시 자동으로 설치하지 않습니다.
- 이 문서에는 관리자 정책으로 강제 설치하는 방법이 없습니다. 정책 레지스트리 경로와 Edge 의 외부 설치 경로는 이 페이지에서 확인하지 못했습니다.
- 관찰한 PC 에는 HKLM 쪽 Chrome·Edge 의 `...\Extensions` 키가 없었습니다. `HKCU\SOFTWARE\Google\Chrome\Extensions` 와 `HKCU\SOFTWARE\Microsoft\Edge\Extensions` 는 있었지만 하위 키가 비어 있었습니다.
- 레지스트리 파일을 읽는 법은 [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) 에서 다룹니다.

## 구조

> 그림 자리: `Secure Preferences` 의 `extensions.settings` 항목 하나(확장 ID → location·from_webstore·first_install_time·last_update_time·path·manifest·disable_reasons)와, `path` 가 가리키는 `Extensions\<ID>\<버전>_0\` 폴더를 화살표로 잇는 그림

### 확장 ID

- 확장 폴더의 이름이 확장 ID 입니다. 32글자이고 a 부터 p 까지의 글자만 씁니다.
- 관찰한 확장의 ID 는 아래 규칙으로 만든 값과 같았습니다. Chrome·Edge 의 확장 18개가 모두 맞았습니다 (관찰).
  1. `manifest.json` 의 `key` 값을 읽습니다. 이 값은 공개키를 base64 로 적은 것입니다.
  2. 공개키를 SHA-256 으로 해시합니다.
  3. 해시의 앞 16바이트를 16진수 32글자로 적습니다.
  4. 16진수 글자 0 을 a 로, 1 을 b 로 … f 를 p 로 바꿉니다.
- 이 규칙을 적은 공식 문서는 이번에 열어 보지 못했습니다.
- 규칙이 공개키만 쓰므로, 같은 확장은 Chrome 과 Edge 에서 ID 가 같았습니다 (관찰).

### extensions.settings 항목

확장 ID 마다 객체가 하나씩 있습니다. 아래는 관찰한 두 판에서 거의 모든 항목에 있던 키 가운데 분석에 쓰는 것입니다.

| 키 | 뜻 | 분석에서 보는 점 |
|---|---|---|
| `location` | 설치 경로의 종류 (정수) | 아래 "location 값" 표 |
| `from_webstore` | 웹 스토어에서 받았는지 | 관찰한 Chrome 에서 `location` 1 인 확장은 모두 true 였습니다 |
| `first_install_time` | 처음 설치한 시각 | 숫자가 든 문자열입니다. "시각 해석" 절 |
| `last_update_time` | 마지막으로 업데이트한 시각 | 업데이트한 적이 없으면 `first_install_time` 과 같았습니다 |
| `path` | 확장 파일 위치 | `Extensions` 안의 확장은 `<ID>\<버전>_0` 상대 경로입니다. 브라우저에 딸린 확장(`location` 5)은 `C:\Program Files\...\Application\<판>\...` 같은 절대 경로였습니다 |
| `manifest` | `manifest.json` 내용 전체 | 확장 폴더를 지운 뒤에도 이름·버전·권한을 여기서 볼 수 있습니다 |
| `active_permissions` | 권한 | `manifest` 의 권한과 함께 봅니다. 일부 항목에는 `granted_permissions`·`withholding_permissions` 도 있었습니다 |
| `disable_reasons` | 꺼진 이유 (정수 목록) | 아래 "disable_reasons 값" 표. 빈 목록 `[]` 은 켜져 있다는 뜻입니다 |

- 거의 모든 항목에 있던 나머지 키는 `was_installed_by_default`, `was_installed_by_oem`, `creation_flags`, `account_extension_type`, `commands`, `content_settings`, `preferences` 입니다.
- 일부 항목에만 있던 키는 `cws-info`, `allowlist`, `active_bit`, `service_worker_registration_info`, `uninstall_url`, `incognito`, `last_loaded_browser_version`, `lastpingday` 등입니다.
- 폴더를 지운 뒤에도 이 항목이 남는지는 확인하지 못했습니다.

### location 값

소스 `manifest.mojom` 의 `ManifestLocation` 입니다. 설정 파일에는 정수로 저장합니다. 소스 주석에 따르면 값의 순서를 바꾸거나 지우지 않고 끝에만 덧붙입니다. 그래서 옛 판 파일에서도 같은 숫자는 같은 뜻입니다.

| 값 | 소스 이름 | 뜻 |
|---|---|---|
| 0 | `kInvalidLocation` | 잘못된 값 |
| 1 | `kInternal` | 내부 `Extensions` 폴더의 crx |
| 2 | `kExternalPref` | 외부 폴더의 crx (설정 파일 경유) |
| 3 | `kExternalRegistry` | 외부 폴더의 crx (레지스트리 경유) |
| 4 | `kUnpacked` | 압축 풀린 확장을 불러옴 (개발자 모드의 "압축해제된 확장 프로그램 로드") |
| 5 | `kComponent` | 브라우저 자체의 구성 요소 |
| 6 | `kExternalPrefDownload` | 업데이트 URL 로 설치한 crx |
| 7 | `kExternalPolicyDownload` | 관리자 정책으로 받은 crx |
| 8 | `kCommandLine` | 실행 인자 `--load-extension` 으로 불러옴 |
| 9 | `kExternalPolicy` | 관리자 정책으로 받아 로컬에 둔 crx |
| 10 | `kExternalComponent` | `kComponent` 와 비슷하지만 URL 로 설치 |

관찰한 PC 의 Chrome 과 Edge 에서는 1·5·6·10 이 나왔습니다.

### disable_reasons 값

소스 `disable_reason.h` 의 `DisableReason` 입니다. 값은 비트 하나씩입니다.

| 값 | 이름 |
|---|---|
| 0 | `DISABLE_NONE` |
| 1 | `USER_ACTION` |
| 2 | `PERMISSIONS_INCREASE` |
| 4 | `RELOAD` |
| 8 | `UNSUPPORTED_REQUIREMENT` |
| 16 | `SIDELOAD_WIPEOUT` |
| 32 | `DEPRECATED_UNKNOWN_FROM_SYNC` |
| 256 | `NOT_VERIFIED` |
| 512 | `GREYLIST` |
| 1024 | `CORRUPTED` |
| 2048 | `REMOTE_INSTALL` |
| 8192 (1<<13) | `EXTERNAL_EXTENSION` |
| 16384 | `UPDATE_REQUIRED_BY_POLICY` |
| 32768 | `CUSTODIAN_APPROVAL_REQUIRED` |
| 65536 | `BLOCKED_BY_POLICY` |
| 1<<19 | `REINSTALL` |
| 1<<20 | `NOT_ALLOWLISTED` |
| 1<<21 | `DEPRECATED_NOT_ASH_KEEPLISTED` |
| 1<<22 | `PUBLISHED_IN_STORE_REQUIRED_BY_POLICY` |
| 1<<23 | `UNSUPPORTED_MANIFEST_VERSION` |
| 1<<24 | `UNSUPPORTED_DEVELOPER_EXTENSION` |
| 1<<25 | `UNKNOWN` |
| 1<<26 | `BLOCKED_BY_CLOUD_POLICY_CHECK` |
| 1<<27 | `BY_ANOTHER_EXTENSION` |

- 0(`DISABLE_NONE`)은 켜져 있다는 뜻입니다. 1(`USER_ACTION`)은 사용자가 끈 것입니다.
- 나머지 값은 이 페이지에서 이름만 확인했습니다. 이름이 뜻을 짐작하게 해 주지만, 정확한 조건은 소스를 확인합니다.
- 비트를 모두 합치면 int 에 담기지 않습니다. 그래서 설정 파일과는 정수 목록으로 바꿔 주고받습니다.
- 관찰한 PC 에서 `disable_reasons` 는 JSON 배열이었습니다. 나온 값은 `[]`, `[1]`, `[2]`, `[8192]`, `[134217728]`(=1<<27) 입니다.

## 증거로서 의미

### 증명하는 것

- `manifest` 가 든 항목이 있으면, 설정 파일을 마지막으로 쓸 때 이 프로필의 확장 목록에 그 확장이 있었습니다.
- `location` 으로 확장이 들어온 경로를 가릴 수 있습니다. 웹 스토어 설치, 레지스트리나 설정 파일을 쓴 외부 설치, 개발자 모드 불러오기, 실행 인자, 관리자 정책, 브라우저 구성 요소가 각각 다른 값입니다.
- `first_install_time` 으로 이 프로필에 처음 설치한 시각을 알 수 있습니다.
- `last_update_time` 과 `path` 의 버전 폴더로 업데이트했는지 알 수 있습니다.
- `disable_reasons` 로 확장이 꺼져 있었는지와 그 이유를 알 수 있습니다. 예를 들어 `[1]` 은 사용자가 끈 것입니다. `[134217728]` 은 이름(`BY_ANOTHER_EXTENSION`)으로 보아 다른 확장이 끈 것입니다.
- `manifest` 로 확장이 요청한 권한의 범위를 알 수 있습니다.
- 외부 설치 레지스트리 키에 확장 ID 가 있으면, 그 확장을 밖에서 설치하도록 설정한 흔적입니다.

### 증명하지 못하는 것

- 설치 버튼을 누른 사람이 누구인지는 남지 않습니다.
- 확장이 실제로 무엇을 했는지는 이 기록으로 알 수 없습니다. Edge 의 활동 DB 는 관찰한 PC 에서 비어 있었습니다.
- `manifest` 에 권한이 있다고 그 권한을 실제로 썼다는 뜻은 아닙니다.
- 이 기록만으로 확장이 악성인지 알 수 없습니다. 확장 폴더의 코드를 따로 검사합니다.
- 목록에 없다고 설치한 적이 없는 것은 아닙니다. 지운 확장이 설정 목록에서 어떻게 되는지는 확인하지 못했습니다.
- 같은 확장은 Chrome 과 Edge 에서 ID 가 같습니다. ID 만으로 어느 브라우저의 기록인지 알 수 없으므로 파일 위치로 가립니다.

보고서에는 "이 확장을 설치했다" 대신 이렇게 씁니다. "이 프로필의 `Secure Preferences` 에 ID X 확장이 `location` 4(압축 풀린 확장 불러오기)로 있고, `first_install_time` 은 Y(UTC) 이다."

## 시각 해석

- `first_install_time`·`last_update_time` 은 숫자가 든 문자열(JSON string)입니다. 1601-01-01 00:00 UTC 부터 센 마이크로초로 읽으면 UTC 로 그럴듯한 값이 나왔습니다 (관찰). 현지 시각이 아닙니다.
- 바꾸는 법은 [시각 값 형식](../../../01-foundations/value-decoding/filetime-unix-webkit-dos-ole.md) 에서 다룹니다.
- 업데이트한 적이 없는 확장은 두 값이 같았습니다 (관찰).
- 업데이트한 확장은 `last_update_time` 이 더 뒤였습니다. 이때 `path` 의 버전 폴더(`<버전>_0`)와 `manifest` 의 `version` 이 새 버전이었습니다 (관찰).
- `lastpingday` 처럼 다른 시각으로 보이는 키도 있습니다. 이 페이지에서는 뜻을 확인하지 않았으므로 해석하지 않습니다.
- 옛 도구가 `install_time` 만 읽으면 설치 시각이 비어 보입니다. 이때는 `first_install_time` 을 직접 봅니다.
- 확장 폴더를 만든 시각은 [마스터 파일 테이블](../../filesystem/mft.md) 에서 따로 확인하고 `first_install_time` 과 맞춰 봅니다.

## 함정과 한계

- **`Preferences` 만 보면 목록이 비어 보입니다.** 관찰한 두 판에서 확장 목록은 `Secure Preferences` 에 있었습니다.
- **ID 만 있는 항목이 있습니다.** `manifest`·`location`·설치 시각이 없는 항목이 Edge 에 22개, Chrome 에 1개 있었습니다 (관찰). 이런 항목은 설치된 확장으로 세지 않습니다.
- **ID 만 있는 항목의 `[8192]` 를 단정하지 않습니다.** Edge 의 그 22개 가운데 21개는 `disable_reasons` 가 `[8192]` 하나뿐이었습니다 (관찰). 8192 는 `EXTERNAL_EXTENSION` 이고, 문서에는 밖에서 설치한 확장을 사용자가 켜야 한다고 적혀 있습니다. 두 사실을 이으면 "밖에서 설치해 사용자 확인을 기다리는 상태" 로 읽을 수 있지만, 이 연결은 확인하지 못한 추론입니다.
- **브라우저에 딸린 확장을 따로 셉니다.** `location` 5 는 브라우저 구성 요소입니다. `path` 가 `Program Files` 아래를 가리킵니다. 사용자가 넣은 확장과 섞어 세지 않습니다.
- **Edge 의 `from_webstore` 가 false 라고 바로 의심하지 않습니다.** Edge 에는 `location` 1 인데 `from_webstore` 가 false 인 확장이 있었습니다 (관찰). Edge 애드온 스토어에서 받은 것으로 보이지만 확인하지 못했습니다.
- **웹 스토어가 아닌 경로를 먼저 봅니다.** `location` 2·3·4·8 은 웹 스토어가 아닌 경로입니다. Chrome 에서 `location` 1 인데 `from_webstore` 가 false 인 확장도 따로 확인합니다. 관찰한 Chrome 에서는 `location` 1 이 모두 `from_webstore` true 였습니다.
- **`disable_reasons` 는 값을 더하지 않고 목록으로 읽습니다.** 목록의 원소 하나가 이유 하나입니다.
- **검증값으로 조작 여부를 가리지 못합니다.** `Secure Preferences` 의 검증값(MAC)을 어떻게 계산하는지 확인하지 못했습니다. 그래서 이 페이지는 검증값으로 설정 조작을 가리는 법을 다루지 않습니다.
- **외부 설치 키는 지우면 사라집니다.** 키를 지우면 확장도 없어지므로, 조사 시점에 키가 없어도 외부 설치가 없었다고 단정하지 않습니다. [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) 으로 옛 레지스트리를 봅니다.
- **원본 프로필로 브라우저를 띄우지 않습니다.** 해시를 기록한 사본의 JSON 파일을 읽습니다.
- **Whale 은 따로 확인합니다.** 이 페이지의 구조는 Chrome·Edge 에서 확인한 것입니다.

## 직접 분석해 보기

### 값으로 한 번

아래 값은 모두 이 페이지의 규칙으로 만든 예시입니다. 실제 확장이나 검체에서 나온 값이 아닙니다.

**확장 ID 만들기.** 공개키의 SHA-256 앞 16바이트가 아래와 같다고 합니다.

```
0F 1E 2D 3C 4B 5A 69 78 87 96 A5 B4 C3 D2 E1 F0
```

16진수 글자를 하나씩 바꿉니다.

| 16진수 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | c | d | e | f |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 글자 | a | b | c | d | e | f | g | h | i | j | k | l | m | n | o | p |

```
0f 1e 2d 3c 4b 5a 69 78 87 96 a5 b4 c3 d2 e1 f0
ap bo cn dm el fk gj hi ih jg kf le md nc ob pa
→ 확장 ID: apbocndmelfkgjhiihjgkflemdncobpa
```

실제 확장 폴더에서 이 규칙을 확인할 때는 아래 스크립트를 씁니다. 결과가 폴더 이름과 같으면 `manifest.json` 의 `key` 와 폴더가 짝이 맞습니다.

```python
import base64, hashlib, json, sys

key = json.load(open(sys.argv[1], encoding='utf-8-sig')).get('key')
if not key:
    sys.exit('manifest 에 key 가 없습니다')
h = hashlib.sha256(base64.b64decode(key)).hexdigest()[:32]
print(''.join(chr(ord('a') + int(c, 16)) for c in h))
```

**설치 시각.** `extensions.settings` 에 아래 값이 있다고 합니다.

```
"first_install_time": "13348540800000000"
13348540800000000 마이크로초 (1601-01-01 00:00 UTC 부터) → 2024-01-01 00:00:00 UTC
```

### 공개 도구로 한 번

Python 의 json 모듈만으로 확장 목록을 표로 뽑을 수 있습니다. 사본 `Secure Preferences` 를 인자로 줍니다. 옛 판 프로필이라면 `Preferences` 도 같은 방법으로 읽어 봅니다.

```python
import json, sys, datetime as dt

EPOCH = dt.datetime(1601, 1, 1, tzinfo=dt.timezone.utc)

def when(v):
    return (EPOCH + dt.timedelta(microseconds=int(v))).isoformat() if v else '-'

prefs = json.load(open(sys.argv[1], encoding='utf-8-sig'))
for ext_id, s in prefs.get('extensions', {}).get('settings', {}).items():
    m = s.get('manifest') or {}
    print(ext_id, m.get('name', '-'), m.get('version', '-'), s.get('location', '-'),
          s.get('from_webstore', '-'), when(s.get('first_install_time')),
          when(s.get('last_update_time')), s.get('disable_reasons', '-'),
          s.get('path', '-'), sep='\t')
```

- `python -X utf8 ext_list.py "Secure Preferences" > ext.tsv` 처럼 실행해 표 파일로 받습니다.
- 이름·버전이 `-` 인 줄은 `manifest` 가 없는 항목입니다. 설치된 확장 수에서 뺍니다.
- `location` 이 5 인 줄을 빼고, 2·3·4·8 인 줄과 `from_webstore` 가 false 인 줄을 먼저 봅니다.
- 같은 확장 ID 로 `Extensions\<확장 ID>\` 폴더가 있는지, `path` 의 버전 폴더가 실제로 있는지 맞춰 봅니다.
- 브라우저 기록을 정리하는 공개 도구 가운데 확장 목록을 보여 주는 것도 있습니다. 도구가 `install_time` 을 읽는지, `Secure Preferences` 를 읽는지 이 표와 한 번 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문·다운로드 기록 | 설치 시각 무렵 확장 스토어나 배포 페이지를 연 기록 | [방문·다운로드 기록](history.md) |
| 세션·탭 복원 | `Session_` ID 13(SetExtensionAppID)에 적힌 확장 앱 ID | [세션·탭 복원](sessions.md) |
| 쿠키 | 확장이 보낸 요청이 만든 쿠키 | [쿠키](cookies.md) |
| LevelDB | `Local Extension Settings\<확장 ID>\` 에 남은 값 | [LevelDB 저장소](../../../01-foundations/database-log-formats/leveldb.md) |
| $MFT·$UsnJrnl | `Extensions\<확장 ID>\` 폴더를 만들고 지운 시각 | [마스터 파일 테이블](../../filesystem/mft.md), [USN 변경 저널](../../filesystem/usnjrnl.md) |
| 레지스트리 | 외부 설치 키와 그 키의 마지막 기록 시각 | [레지스트리 하이브 구조](../../../01-foundations/database-log-formats/registry-hive/index.md) |
| 설치 프로그램 | 같은 시간대에 설치한 프로그램. 외부 설치 키를 넣은 프로그램을 찾습니다 | [설치 프로그램](../../system-account/uninstall.md) |
| 확장 폴더의 코드 | 스크립트를 규칙으로 검사해 의심 코드를 찾습니다 | [의심 실행 파일 선별](../../../03-techniques/analysis/code-signing-yara.md) |

조사 흐름은 아래 시나리오에서 다룹니다.

- [악성코드는 어디서 들어왔나](../../../04-scenarios/incident/initial-access.md) — 악성 확장이 들어온 경로를 찾습니다.
- [악성코드 지속성(자동실행) 찾기](../../../04-scenarios/incident/persistence.md) — 외부 설치나 정책으로 계속 다시 들어오는 확장을 찾습니다.
- [웹 사용 행위 재구성](../../../04-scenarios/activity/web-activity.md) — 확장을 포함해 웹 사용 전체를 묶습니다.

같은 구조를 쓰는 다른 앱은 [크롬 계열 앱 공통 구조](../../../01-foundations/app-mail-data/chromium-electron-webview2/index.md) 에서 다룹니다.

## 실습

크롬이나 엣지를 쓴 공개 검체(NIST CFReDS 등)에서 사용자 프로필 폴더를 꺼내 아래 질문을 풀어 봅니다.

1. 확장 목록이 `Secure Preferences` 와 `Preferences` 가운데 어디에 있습니까?
2. `manifest` 가 든 항목은 몇 개이고, ID 만 있는 항목은 몇 개입니까?
3. `location` 값별로 확장 수를 세어 봅니다. 5 를 빼면 어떤 값이 남습니까?
4. `Extensions` 폴더의 ID 목록과 `extensions.settings` 의 ID 목록이 같습니까? 한쪽에만 있는 ID 는 무엇입니까?
5. 확장 하나를 골라 `manifest.json` 의 `key` 로 ID 를 계산해 봅니다. 폴더 이름과 같습니까?
6. `first_install_time` 과 확장 폴더의 $MFT 생성 시각은 얼마나 차이 납니까?
7. `disable_reasons` 가 빈 목록이 아닌 확장은 어떤 이유로 꺼져 있습니까?
8. 검체의 레지스트리에 외부 설치 키가 있습니까? 있다면 그 확장 ID 가 설정 목록에도 있습니까?

## 참고 문헌

1. Chromium 소스, *extensions/common/mojom/manifest.mojom* (`ManifestLocation` 값). https://chromium.googlesource.com/chromium/src/+/HEAD/extensions/common/mojom/manifest.mojom
2. Chromium 소스, *extensions/browser/disable_reason.h* (`DisableReason` 값과 저장 방식). https://chromium.googlesource.com/chromium/src/+/HEAD/extensions/browser/disable_reason.h
3. Chrome for Developers, "Alternative extension distribution options" (레지스트리·설정 파일로 밖에서 설치하는 방법). https://developer.chrome.com/docs/extensions/how-to/distribute/install-extensions
