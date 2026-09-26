---
title: "언어 패키지 관리자"
parent: "아티팩트 · 패키지와 소프트웨어"
nav_order: 620
---

# 언어 패키지 관리자 (pip·npm 등)

pip 나 npm 으로 설치한 패키지는 dpkg·rpm 데이터베이스에 들어가지 않고, 설치 폴더 안의 메타데이터 파일과 사용자 홈의 캐시·설정·로그에 흔적을 남깁니다.

## 무엇을 기록하나 · 왜 생기나

배포판 패키지 관리자는 설치 기록을 한곳에 모읍니다([dpkg·apt 기록](dpkg-apt.md), [rpm·dnf·yum 기록](rpm-dnf.md)). 프로그래밍 언어마다 따로 있는 패키지 관리자 (language package manager) 는 사정이 다릅니다. 설치 목록을 모아 두는 데이터베이스가 없고, 패키지를 풀어 놓은 폴더 옆에 메타데이터를 함께 적어 둡니다. 설치 위치도 시스템 전체, 사용자 홈, 가상 환경 (virtual environment), 프로젝트 폴더로 흩어집니다.

Python 은 설치한 프로젝트마다 `이름-버전.dist-info` 폴더를 만들고, 그 안에 어떤 도구로 설치했는지, 어떤 파일을 깔았는지, 어디서 받았는지를 적습니다[1][2]. 이 형식은 PyPA 명세이고, 배포판 패키지 관리자 같은 Python 밖의 도구도 따를 수 있도록 대부분의 항목을 선택으로 두었습니다[1]. 그래서 배포판 패키지로 들어온 Python 모듈에도 같은 폴더가 있을 수 있습니다.

npm 은 프로젝트마다 `node_modules` 폴더에 패키지를 풀고, 무엇을 어디서 받았는지를 잠금 파일 (lockfile) 에 적습니다[7][11]. 실행할 때마다 캐시 폴더 안에 디버그 로그도 남기는데, 로그 파일 이름에 실행 시각이 들어갑니다[8][9].

두 도구 모두 설치 과정에서 패키지가 들고 온 코드를 실행할 수 있습니다. npm 은 `preinstall`, `install`, `postinstall` 스크립트를 설치 때 실행하고[13], Python 은 `site-packages` 에 놓인 `.pth` 파일의 `import` 줄을 인터프리터가 시작될 때마다 실행합니다[6]. 그래서 이 흔적은 "무슨 도구가 깔렸나" 와 함께 "설치 때나 실행 때 무엇이 돌았을 수 있나" 를 따질 때도 씁니다.

## 위치와 버전별 차이

### Python·pip

| 흔적 | 위치 | 비고 |
|---|---|---|
| 설치된 프로젝트 | `site-packages` (또는 `dist-packages`) 안의 `이름-버전.dist-info` | 모듈 폴더와 나란히 있음[1] |
| 사용자 설치 | `~/.local/lib/pythonX.Y/site-packages` | 사용자 설치 방식(user scheme)의 기본 위치. 기준 폴더(USER_BASE)는 `~/.local`[6] |
| 가상 환경 | 환경 폴더 안의 `lib/pythonX.Y/site-packages`, 뿌리에 `pyvenv.cfg` | `pyvenv.cfg` 는 환경의 `sys.prefix` 에 있음[6] |
| 외부 관리 표시 | 표준 라이브러리 폴더의 `EXTERNALLY-MANAGED` | 있으면 pip 가 시스템 환경 설치를 거부함[3] |
| pip 캐시 | `~/.cache/pip` (`XDG_CACHE_HOME` 을 따름) | HTTP 응답 캐시와 직접 빌드한 wheel 캐시[4] |
| pip 설정 | `/etc/xdg/pip/pip.conf`, `/etc/pip.conf`, `~/.config/pip/pip.conf`, `~/.pip/pip.conf`, `$VIRTUAL_ENV/pip.conf` | 전역·사용자·환경 세 단계[4] |
| 대화형 입력 기록 | `~/.python_history` | UAC 가 수집함[15] |

배포판은 배포판이 설치한 Python 패키지와 관리자가 따로 설치한 패키지를 다른 폴더에 둡니다[3].

| 항목 | Debian·Ubuntu 계열 | Fedora 계열 |
|---|---|---|
| 배포판 패키지 | `/usr/lib/python3/dist-packages` | `/usr/lib/python3.x/site-packages` |
| 관리자가 따로 설치한 패키지 | `/usr/local/lib/python3/dist-packages` | `/usr/local/lib/python3.x/site-packages` |

RHEL 은 Fedora 에서 갈라져 나온 배포판이라 같은 나눔을 따를 가능성이 있습니다. Debian 은 직접 빌드해 `/usr/local` 에 깐 CPython 이 쓰는 `site-packages` 와 섞이지 않게 이름을 `dist-packages` 로 바꿔 한 번 더 나눕니다[3]. Debian 이라면 이 파일은 `/usr/lib/python3.9/EXTERNALLY-MANAGED` 같은 자리에 놓이고[3], Ubuntu 24.04 와 RHEL 9 가 이 파일을 싣는지는 실제 시스템의 `/usr/lib/python3.*/EXTERNALLY-MANAGED` 로 확인합니다. 실제 폴더 이름은 파이썬 판과 빌드에 따라 달라지므로, 이미지 전체에서 `*.dist-info` 폴더와 `pyvenv.cfg` 파일을 찾는 편이 빠뜨리는 곳이 적습니다.

pip 캐시는 23.3 부터 HTTP 응답을 `http-v2` 폴더에 두고, 그 전에는 `http` 폴더에 두었습니다[4]. 캐시 안쪽 구조는 구현 세부라서 pip 판마다 바뀔 수 있습니다[4].

### npm

| 흔적 | 위치 | 비고 |
|---|---|---|
| 로컬 설치 | 프로젝트 뿌리의 `node_modules` | 실행 파일 링크는 `node_modules/.bin`[7] |
| 전역 설치(`-g`) | `{prefix}/lib/node_modules`, 실행 파일은 `{prefix}/bin` | prefix 는 node 가 설치된 곳, 대개 `/usr/local`[7] |
| 캐시 | `~/.npm` | 안에 `_cacache`, `_npx`, `_tuf`[7][10] |
| 디버그 로그 | `~/.npm/_logs` | 설정 `logs-dir` 로 옮길 수 있음[8][10] |
| 잠금 파일 | 프로젝트의 `package-lock.json`, `node_modules/.package-lock.json` | 뒤쪽은 npm 7 부터 생기는 숨은 잠금 파일[11] |
| 설정 | 프로젝트 `.npmrc`, `~/.npmrc`, `$PREFIX/etc/npmrc`, npm 내장 `npmrc` | 인증 값이 들어갈 수 있음[12] |

prefix 는 node 실행 파일(`{prefix}/bin/node`)보다 한 단계 위 폴더입니다[7]. 그래서 node 를 배포판 패키지로 깔아 `/usr/bin/node` 에 있으면 전역 패키지는 `/usr/lib/node_modules` 에 들어가고, `/usr/local` 에 따로 깔았으면 `/usr/local/lib/node_modules` 에 들어갑니다. 두 곳을 다 봅니다.

Rust 의 cargo 같은 다른 언어 도구도 비슷한 흔적을 남기지만, 이 페이지는 pip 와 npm 을 중심으로 씁니다. UAC 는 라이브 응답에서 `cargo install --list` 도 실행합니다[14].

## 구조

### dist-info 폴더

폴더 이름은 `이름-버전.dist-info` 이고, 이름과 버전은 정규화한 뒤 `-` 를 `_` 로 바꾸므로 폴더 이름에는 `-` 가 딱 하나 남습니다[1]. 예전 도구는 정규화를 하지 않았으므로 대소문자나 점이 섞인 이름도 나올 수 있습니다[1]. 폴더 안의 파일은 아래와 같습니다.

| 파일 | 내용 | 필수 |
|---|---|---|
| `METADATA` | 이름·버전 등 프로젝트 메타데이터 | 예[1] |
| `RECORD` | 설치한 파일 목록(CSV) | 아니요[1] |
| `INSTALLER` | 설치한 도구 이름 한 줄 | 아니요[1] |
| `REQUESTED` | 빈 파일. 사용자가 직접 요청한 설치 표시 | 도구별 확장[1][5] |
| `direct_url.json` | URL·VCS·로컬 경로로 설치했을 때의 출처 | 조건부[2] |
| `entry_points.txt` | 콘솔 명령 등 진입점 | 아니요[1] |
| `licenses/`, `sboms/` | 라이선스 파일, SBOM | 조건부[1] |

**RECORD.** 한 줄에 파일 하나를 적고, 필드는 경로, 해시, 크기 셋입니다[1]. 해시는 `알고리즘=값` 모양이고, 값은 파일 내용 다이제스트를 URL 안전 base64 로 바꾼 뒤 끝의 `=` 를 뗀 문자열입니다[1]. `.pyc` 파일과 RECORD 자신은 해시와 크기를 비워 두는 경우가 많습니다[1]. 경로는 `dist-info` 가 들어 있는 폴더 기준 상대 경로이거나 절대 경로라서, `../../../bin/명령` 처럼 `site-packages` 밖에 깐 실행 파일도 목록에 나옵니다[1].

**INSTALLER.** 설치한 도구의 명령 이름을 한 줄로 적습니다[1]. pip 는 `pip` 와 줄바꿈을 씁니다[5]. 배포판 관리 도구가 설치한 패키지는 다른 도구가 건드리지 못하게 RECORD 를 지우거나 이름을 바꾸고, INSTALLER 에 관리할 도구 이름을 적는 것이 권장 방식입니다[1]. INSTALLER 값은 참고용으로만 쓰도록 정해진 값입니다[1].

**REQUESTED.** 지금은 표준이 아니라 도구별 확장 파일이지만[1], pip 는 설치를 요청받은 패키지에만 빈 `REQUESTED` 파일을 만듭니다[5]. 여기서 요청받은 패키지는 명령줄 인자나 요구 사항 파일에 적은 것이고, 의존성·추가 기능(extras)·제약 조건으로 딸려 온 것은 빠집니다[5].

**direct_url.json.** 이름과 버전으로 설치하면 만들지 않고, URL·VCS 주소·로컬 경로로 설치했을 때만 만듭니다[2]. `pip install 이름` 이나 `--find-links` 로 설치한 경우도 만들지 않습니다[2]. 키 `url` 에 출처가 들어가고, 출처 종류에 따라 아래 셋 중 하나가 붙습니다[2].

| 키 | 출처 | 안쪽 키 |
|---|---|---|
| `vcs_info` | git 등 VCS 저장소 | `vcs`, `requested_revision`(요청한 브랜치·태그·커밋 등), `commit_id`(설치한 커밋) |
| `archive_info` | 소스 압축 파일이나 wheel | `hashes`(알고리즘별 16진수 다이제스트), 옛 키 `hash` |
| `dir_info` | 로컬 폴더(`file://`) | `editable`(편집 가능 설치 여부) |

`url` 의 인증 정보는 지우고 저장해야 하지만, `${환경변수}` 모양의 사용자·비밀번호 자리나 `git@` 같은 이름은 남을 수 있습니다[2]. `archive_info` 의 해시는 RECORD 와 달리 16진수라는 점도 다릅니다[1][2].

만든 예시입니다.

```json
{"url": "https://git.example.org/team/tool.git", "vcs_info": {"vcs": "git", "requested_revision": "v1.0", "commit_id": "0123456789abcdef0123456789abcdef01234567"}}
```

### .pth 파일

`site-packages` 같은 사이트 폴더의 `이름.pth` 파일은 한 줄마다 `sys.path` 에 더할 경로를 적습니다[6]. `import` 와 공백·탭으로 시작하는 줄은 경로가 아니라 코드로 보고 실행합니다[6]. 이 줄은 해당 모듈을 쓰든 안 쓰든 Python 이 시작될 때마다 실행되고, `-S` 옵션을 줄 때만 건너뜁니다[6]. Python 3.15 는 `import` 줄을 폐지 예정으로 돌렸고, 같은 이름의 `.start` 파일이 있으면 `.pth` 의 `import` 줄을 무시합니다[6]. 사용자 사이트 폴더(`~/.local/lib/pythonX.Y/site-packages`)도 사이트 폴더라서 여기 놓인 `.pth` 파일도 읽힙니다[6]. 같은 방식으로 시작 때 불러오는 모듈로 `sitecustomize` 와 `usercustomize` 가 있습니다[6].

### npm 디버그 로그

로그 폴더는 기본으로 캐시 안의 `_logs` 입니다[8][9]. 파일 이름은 `실행ID-debug-번호.log` 이고, 실행 ID 는 npm 이 시작할 때의 시각을 `toISOString()` 으로 만든 뒤 `.` 과 `:` 를 `_` 로 바꾼 값입니다[9]. 한 파일에 로그 항목 5만 개가 차면 다음 번호 파일을 열고, 한 번 실행에 최대 5개까지 만듭니다[9]. npm 8.2.0 전에는 이름 끝에 번호가 없었습니다[9].

만든 예시입니다.

```
~/.npm/_logs/2026-01-02T03_04_05_678Z-debug-0.log
```

로그 파일 수가 `logs-max`(기본 10)를 넘으면 오래된 파일부터 지우고, `logs-max` 가 0 이면 로그 파일을 만들지 않습니다[8][10]. 이 수는 실행 횟수가 아니라 파일 개수입니다[9].

한 줄은 `순번 수준 제목 내용` 모양이고, 줄 안에 시각 필드는 없습니다[9]. 시작 부분에 `verbose title` 과 `verbose argv` 줄이 남아 어떤 명령과 인자로 실행했는지 보여 줍니다[9]. 기본 인증 URL 의 비밀번호와 npm 토큰은 가리려고 하지만, 모든 비밀 값이 가려진다고 기대할 수는 없습니다[8]. 만든 예시입니다.

```
15 verbose title npm install example-pkg
16 verbose argv "install" "example-pkg"
```

앞의 순번은 그 실행에서 몇 번째 로그 항목인지를 뜻하므로 값은 실행마다 다릅니다[9].

### package-lock.json

`packages` 객체는 패키지 위치(`node_modules/이름`)를 키로 삼고, 값에 아래 필드를 적습니다[11].

| 필드 | 뜻 |
|---|---|
| `version` | 그 위치에 있는 패키지 `package.json` 의 판 |
| `resolved` | 실제로 받은 곳. 레지스트리면 tarball URL, git 이면 커밋 sha 가 붙은 git URL, 링크면 링크 대상 |
| `integrity` | 받은 파일의 `sha512` 또는 `sha1` SRI 문자열 |
| `hasInstallScript` | `preinstall`·`install`·`postinstall` 스크립트가 있는 패키지 표시 |
| `dev`, `optional`, `devOptional` | 개발용·선택 의존성 표시 |

`lockfileVersion` 은 npm 5·6 이 1, npm 7·8 이 2, npm 9 이상이 3 입니다[11]. 숨은 잠금 파일 `node_modules/.package-lock.json` 은 항상 3 이고, 이 파일의 수정 시각이 참조하는 패키지 폴더들과 같거나 그보다 늦고, 목록과 실제 폴더 구성이 맞을 때만 npm 이 믿고 씁니다[11].

### .npmrc 의 인증 값

`_auth`, `_authToken`, `username`, `_password`, `certfile`, `keyfile` 은 `//registry.example.org/:_authToken=...` 처럼 레지스트리 주소를 앞에 붙여 적어야 합니다[12]. 이 값이 있으면 어느 레지스트리에 인증해 받았는지 알 수 있습니다. 보고서에는 값 대신 "인증 값이 있다" 는 사실만 적습니다.

## 증거로서 의미

**증명하는 것.** 어떤 Python 환경에 어떤 프로젝트가 어떤 판으로 들어 있는지는 `dist-info` 폴더가 보여 줍니다[1]. INSTALLER 로 pip 설치와 배포판 패키지를 가를 수 있고, REQUESTED 로 사용자가 직접 요청한 설치와 의존성으로 딸려 온 설치를 가를 수 있습니다[1][5]. `direct_url.json` 은 이름으로 받지 않고 특정 URL·저장소·로컬 폴더에서 설치했다는 것과 그 출처를 보여 줍니다[2]. RECORD 해시를 지금 파일과 대조하면 설치 뒤 파일이 바뀌었는지 알 수 있습니다[1]. npm 쪽에서는 `package-lock.json` 의 `resolved` 가 실제로 받은 곳을, `hasInstallScript` 가 설치 때 스크립트가 돌 수 있었던 패키지를 보여 줍니다[11]. 남아 있는 디버그 로그는 그 npm 실행의 시작 시각(UTC)과 명령 인자를 보여 줍니다[9].

**증명하지 못하는 것.** `dist-info` 에는 설치 시각을 적는 필드가 없어서 설치 시각은 파일 시스템 시각으로만 추정합니다[1]. 누가 설치했는지도 적지 않으므로 파일 소유자와 셸 명령 기록으로 간접 추정합니다. `direct_url.json` 이 없다고 해서 공식 색인에서 받았다는 뜻은 아닙니다. `pip.conf` 의 `index-url` 로 다른 색인을 가리키거나 `--find-links` 로 받은 설치도 이 파일을 만들지 않습니다[2][4]. `.pth` 파일에 `import` 줄이 있다는 사실만으로 악성이라고 할 수 없고, 정상 패키지도 이 방식을 써 왔습니다[6]. npm 디버그 로그가 없다고 npm 을 실행하지 않았다고 할 수도 없습니다. `logs-max` 설정이나 순환 삭제로 없을 수 있기 때문입니다[8][10].

## 시각 해석

npm 디버그 로그 이름의 시각은 `toISOString()` 으로 만든 UTC 이고, 끝의 `Z` 가 그 표시입니다[9]. 밀리초까지 들어 있고, 파일 안의 줄에는 시각이 없습니다[9]. 실행이 길면 파일 이름 시각은 시작 시각만 뜻하고, 끝난 시각은 파일의 수정 시각으로 추정합니다.

`dist-info` 폴더와 그 안 파일, `node_modules/이름` 폴더의 생성·수정 시각은 설치나 갱신 때 생깁니다. 이 값은 파일 시스템 시각이라 UTC 로 저장되고, 해석은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)과 [ext4](../../01-foundations/filesystem/ext4/index.md)에서 다룹니다. 폴더 이름에 판이 들어 있어서 판을 올리면 새 이름의 폴더가 생기므로, 폴더 생성 시각은 처음 설치한 시각이 아니라 지금 판을 설치한 시각일 가능성이 있습니다.

숨은 잠금 파일은 참조하는 패키지 폴더들과 수정 시각이 같거나 그보다 늦어야 npm 이 믿습니다[11]. 그래서 `node_modules` 안의 패키지 폴더가 `.package-lock.json` 보다 늦게 바뀌었다면 npm 설치 뒤 다른 방법으로 트리를 건드렸을 가능성이 있습니다. 다만 폴더 안 파일 내용만 바꾸면 폴더 수정 시각은 그대로일 수 있습니다[11].

## 함정과 한계

- `dist-info` 폴더가 있다고 pip 로 설치한 것이 아닙니다. apt·dnf 로 설치한 Python 패키지에도 이 폴더가 있을 수 있으므로 INSTALLER 값과 RECORD 유무를 봅니다[1].
- 폴더 이름의 이름·버전은 정규화된 형태라 `METADATA` 의 표기와 다를 수 있습니다[1].
- `pip list` 같은 라이브 명령은 그 명령을 실행한 인터프리터 하나의 환경만 봅니다. 가상 환경마다 `pyvenv.cfg` 가 환경 폴더 뿌리에 있으므로 이미지 전체에서 이 파일을 찾습니다[6].
- RECORD 는 명세상 선택 파일이고, 해시와 크기를 비운 줄도 허용됩니다[1]. 해시가 빈 파일은 RECORD 로 변조를 확인할 수 없습니다. 파일을 바꾸면서 RECORD 까지 고쳐 쓰면 대조해도 드러나지 않으므로, 공개 색인의 같은 판 wheel 과 대조합니다.
- `EXTERNALLY-MANAGED` 가 있는 시스템에서도 `--break-system-packages` 를 주면 pip 가 시스템 환경에 설치합니다[3]. 이 파일이 있는 시스템의 시스템 사이트 폴더에 INSTALLER 가 `pip` 인 패키지가 있으면 이 옵션을 썼거나 표시 파일을 치웠을 가능성이 있습니다.
- npm 7 부터 설치 스크립트 출력은 기본으로 화면에 나오지 않습니다(`foreground-scripts`)[8][10]. 사용자가 화면으로는 스크립트 실행을 알아채지 못했을 수 있으므로, 잠금 파일의 `hasInstallScript` 와 패키지의 `package.json` 을 함께 봅니다[11].
- pip 캐시는 내부 구조가 판마다 바뀔 수 있습니다[4]. `pip cache purge` 는 wheel 캐시와 HTTP 캐시를 모두 비웁니다[4].

## 직접 분석해 보기

### 헥스로 한 번

INSTALLER 파일은 pip 가 `pip\n` 을 쓰므로 4바이트입니다[5]. 아래는 명세와 pip 코드로 만든 예시입니다.

```
00000000: 7069 700a                                pip.
```

RECORD 는 이 파일을 `sha256=zuuue4knoyJ-UwPPXg8fezS7VCrXJQrAP7zeNuwvFQg,4` 로 적고, 명세 예시의 RECORD 에도 같은 값이 나옵니다[1]. `sha256sum` 의 16진수 출력을 RECORD 형식으로 바꾸면 대조할 수 있습니다.

```
sha256sum example_pkg-1.0.dist-info/INSTALLER | cut -d' ' -f1 | xxd -r -p | base64 | tr '+/' '-_' | tr -d '='
```

같은 방법으로 RECORD 의 모든 줄을 돌며 해시를 다시 계산하면 설치 뒤 바뀐 파일과 RECORD 에 없는 파일을 찾을 수 있습니다. RECORD 에 없는 `.py` 파일이나 `.pth` 파일이 `site-packages` 에 있으면 따로 봅니다.

### 공개 도구로 한 번

라이브 시스템에서는 UAC 가 `pip list`, `pip list -v`, `npm list --depth=0`, `npm list -g --depth=0`, `cargo install --list` 를 실행해 결과를 남깁니다[14]. 수집 절차는 [라이브 응답 수집](../../03-techniques/acquisition/live-response.md)에서 다룹니다.

디스크 이미지에서는 파일을 꺼내 직접 읽습니다. 모두 텍스트·CSV·JSON 이라 따로 해석기가 필요 없습니다.

1. `*.dist-info` 폴더를 모두 찾아 폴더 경로, INSTALLER 값, REQUESTED 유무, `direct_url.json` 내용을 한 표로 만듭니다.
2. 사이트 폴더마다 `*.pth` 파일에서 `import` 로 시작하는 줄을 뽑고, 같은 폴더의 `sitecustomize.py`, `usercustomize.py` 를 확인합니다.
3. `package-lock.json` 과 `.package-lock.json` 에서 `resolved` 주소가 설정된 레지스트리와 다른 항목, `hasInstallScript` 가 참인 항목을 뽑습니다.
4. 사용자마다 `~/.npm/_logs` 의 파일 이름을 UTC 시각으로 풀어 타임라인에 넣고, `verbose argv` 줄을 붙입니다.

## 교차 검증

| 함께 볼 아티팩트 | 알려 주는 것 |
|---|---|
| [셸 명령 기록](../execution/shell-history/index.md) | `pip install`, `npm install -g` 명령과 인자. `--break-system-packages` 나 URL 설치 흔적 |
| [dpkg·apt 기록](dpkg-apt.md), [rpm·dnf·yum 기록](rpm-dnf.md) | 같은 Python 모듈이 배포판 패키지로도 들어왔는지, node·pip 자체를 언제 설치했는지 |
| [sudo·su 사용 기록](../logins/sudo-su.md) | 시스템 폴더에 설치하려고 root 권한을 쓴 시각 |
| [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md) | `dist-info`·`node_modules` 파일 소유자를 계정으로 잇기 |
| [패키지 파일 변조 확인](package-verify.md) | 배포판 패키지가 깐 Python 파일이 바뀌었는지 |
| [알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md) | 설치된 패키지 파일을 알려진 해시와 대조 |
| [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) | `.pth`·`sitecustomize` 를 다른 지속성 흔적과 함께 보기 |

타임라인에 넣는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)에서 다룹니다.

## 실습

공개 Linux 디스크 이미지(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. 이미지 전체에 `*.dist-info` 폴더가 몇 개 있고, INSTALLER 값별로 몇 개인가? `pip` 인 것은 어느 사이트 폴더에 있는가?
2. REQUESTED 가 있는 pip 설치 가운데 `direct_url.json` 도 있는 것은 무엇이고, `url` 은 어디를 가리키는가?
3. 사이트 폴더에 `import` 줄이 있는 `.pth` 파일이 있는가? 그 파일은 어느 `dist-info` 의 RECORD 에 올라 있는가?
4. `~/.npm/_logs` 의 가장 이른 로그와 가장 늦은 로그의 UTC 시각은 언제이고, 셸 명령 기록의 `npm` 명령과 맞는가?
5. `node_modules` 안에 `.package-lock.json` 보다 수정 시각이 늦은 패키지 폴더가 있는가?

## 참고 문헌

1. PyPA, Recording installed projects — https://github.com/pypa/packaging.python.org/blob/main/source/specifications/recording-installed-packages.rst
2. PyPA, Recording the Direct URL Origin of installed distributions·Direct URL Data Structure — https://github.com/pypa/packaging.python.org/blob/main/source/specifications/direct-url.rst , https://github.com/pypa/packaging.python.org/blob/main/source/specifications/direct-url-data-structure.rst
3. PyPA, Externally Managed Environments — https://github.com/pypa/packaging.python.org/blob/main/source/specifications/externally-managed-environments.rst
4. pip, docs/html/topics/caching.md·configuration.md — https://github.com/pypa/pip/blob/main/docs/html/topics/caching.md , https://github.com/pypa/pip/blob/main/docs/html/topics/configuration.md
5. pip, src/pip/_internal/operations/install/wheel.py·src/pip/_internal/req/req_install.py — https://github.com/pypa/pip/blob/main/src/pip/_internal/operations/install/wheel.py , https://github.com/pypa/pip/blob/main/src/pip/_internal/req/req_install.py
6. CPython, Doc/library/site.rst — https://github.com/python/cpython/blob/main/Doc/library/site.rst
7. npm, folders(5) — https://github.com/npm/cli/blob/latest/docs/lib/content/configuring-npm/folders.md
8. npm, logging(7) — https://github.com/npm/cli/blob/latest/docs/lib/content/using-npm/logging.md
9. npm, lib/npm.js·lib/utils/log-file.js·lib/utils/format.js — https://github.com/npm/cli/blob/latest/lib/npm.js , https://github.com/npm/cli/blob/latest/lib/utils/log-file.js , https://github.com/npm/cli/blob/latest/lib/utils/format.js
10. npm, workspaces/config/lib/definitions/definitions.js — https://github.com/npm/cli/blob/latest/workspaces/config/lib/definitions/definitions.js
11. npm, package-lock.json(5) — https://github.com/npm/cli/blob/latest/docs/lib/content/configuring-npm/package-lock-json.md
12. npm, npmrc(5) — https://github.com/npm/cli/blob/latest/docs/lib/content/configuring-npm/npmrc.md
13. npm, scripts(7) — https://github.com/npm/cli/blob/latest/docs/lib/content/using-npm/scripts.md
14. UAC, artifacts/live_response/packages (pip.yaml·npm.yaml·cargo.yaml) — https://github.com/tclahr/uac/tree/main/artifacts/live_response/packages
15. UAC, artifacts/files/applications/python.yaml — https://github.com/tclahr/uac/blob/main/artifacts/files/applications/python.yaml
