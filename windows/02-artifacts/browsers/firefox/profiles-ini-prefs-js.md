---
title: "프로필 구조"
parent: "파이어폭스"
grand_parent: "아티팩트 · 인터넷·브라우저"
nav_order: 1700
---

# 프로필 구조 (profiles.ini·prefs.js)

파이어폭스는 사용자마다 프로필 (Profile) 이라는 폴더 묶음에 방문 기록·쿠키·비밀번호·설정을 모아 둡니다. 어느 프로필이 어디 있고 어느 것이 기본인지는 `profiles.ini` 파일이 알려 줍니다. 분석은 이 파일로 프로필 폴더를 찾는 데서 시작합니다.

## 무엇을 기록하나 · 왜 생기나

프로필 하나는 한 사용자의 브라우저 데이터를 통째로 담습니다. 방문 기록, 쿠키, 저장 비밀번호, 확장 프로그램, 설정이 모두 한 프로필 안에 있습니다. 프로필 하나는 폴더 한두 개로 이루어지는데, 두 개일 때 한 폴더는 오래 남길 데이터를 담고 다른 폴더는 지워도 되는 캐시를 담습니다.

프로필 서비스 (Profile Service) 는 알려진 프로필의 목록을 `profiles.ini` 에 적어 두고, 설치본마다 어느 프로필이 기본인지도 같은 방식으로 관리합니다. 한 컴퓨터에 파이어폭스를 여러 번 설치하면 설치본 (Installation) 마다 기본 프로필을 따로 둡니다. 설치본은 설치 폴더로 구분하고, Windows 스토어판은 패키지 식별자로 구분합니다. 이 설치 위치 문자열을 CityHash 로 해시한 값이 `profiles.ini` 에서 설치본을 가리키는 식별자입니다. 설치본마다 프로필을 따로 두는 방식에는 예외가 있어서, 리눅스 Snap 은 이전 방식을 씁니다.

## 위치와 버전별 차이

프로필 폴더의 위치는 운영체제를 따릅니다.

### 프로필 본 폴더와 로컬 폴더

파이어폭스는 프로필을 본 폴더 (root) 와 로컬 폴더 (local) 로 나눕니다. 본 폴더에는 오래 남길 데이터가 있습니다. 로컬 폴더에는 캐시처럼 지워도 되는 데이터가 있습니다.

| 운영체제 | 본 폴더 (root) | 로컬 폴더 (local) |
|---|---|---|
| Windows | `%APPDATA%\Mozilla\Firefox\Profiles` | `%LOCALAPPDATA%\Mozilla\Firefox\Profiles` |
| 리눅스 | `~/.mozilla/firefox` | `~/.cache/mozilla/firefox` |
| macOS | `~/Library/Application Support/Firefox/Profiles` | `~/Library/Caches/Firefox/Profiles` |

- 실행 중인 프로그램 안에서는 디렉터리 서비스의 `ProfD` 가 본 폴더를 가리키고, `ProfLD` 가 로컬 폴더를 가리킵니다.
- 옛 Windows 의 실제 경로 예는 아래와 같습니다[2].

| Windows 판 | 본 폴더 안 파일 예 (`places.sqlite`) |
|---|---|
| Vista·7 | `C:\Users\%USERNAME%\AppData\Roaming\Mozilla\Firefox\Profiles\%PROFILE%.default\places.sqlite` |
| XP | `C:\Documents and Settings\%USERNAME%\Application Data\Mozilla\Firefox\Profiles\%PROFILE%.default\places.sqlite` |

- 캐시는 로컬 폴더 쪽에 있습니다. Vista·7 의 캐시 폴더 예는 `C:\Users\%USERNAME%\AppData\Local\Mozilla\Firefox\Profiles\%PROFILE%.default\cache2\` 입니다. 자세한 내용은 [캐시 (cache2)](cache2.md) 에서 다룹니다.
- 폴더 이름의 앞부분은 무작위 문자열입니다. 뒤에 `.default` 처럼 프로필 이름이 붙습니다.

### 실제 데이터로 확인할 것

아래는 실제 파일에서 확인합니다.

- `profiles.ini` 파일 자체의 위치입니다.
- `profiles.ini` 안의 절 이름과 키 이름, 프로필 목록이 적히는 형식입니다.
- 설치본별 전용 프로필이 몇 번 판부터 생겼는지입니다.
- 프로필 잠금 파일의 이름입니다.
- `prefs.js` 의 형식, 파이어폭스가 종료할 때 이 파일을 다시 쓰는지, `user.js` 가 덮어쓰는지입니다.

## 구조

- `profiles.ini` 는 텍스트 파일입니다. 프로필 서비스가 시작할 때 이 파일을 읽어 프로필 목록을 만듭니다.
- 설치본 식별자는 설치 위치 문자열의 CityHash 값입니다. 같은 컴퓨터에 여러 설치본이 있으면 `profiles.ini` 안에서 설치본마다 기본 프로필이 갈립니다.
- `prefs.js` 는 프로필의 설정을 담는 파일로 알려져 있습니다. 파일 형식과 안에 담기는 설정 이름은 실제 데이터로 확인합니다.
- 다른 페이지에서 다룬 설정 이름으로는 세션 복원의 `browser.sessionstore.upgradeBackup.maxUpgradeBackups`, 양식 기록의 `browser.formfill.expire_days`, 확장 프로그램의 `extensions.databaseSchema` 가 있습니다. 이 이름들이 `prefs.js` 에 어떻게 적히는지도 실제 데이터로 확인합니다.

## 증거로서 의미

### 증명하는 것

- `profiles.ini` 에 올라 있는 프로필은 이 컴퓨터의 파이어폭스가 알고 있던 프로필입니다.
- 한 컴퓨터에 프로필이 여러 개 있으면 사용자가 프로필을 나눠 썼을 가능성을 봅니다. 각 프로필의 데이터는 서로 섞이지 않습니다.
- 설치본 식별자가 여러 개면 파이어폭스를 여러 위치에 설치한 적이 있다는 뜻입니다. 지금도 모두 설치돼 있다는 뜻은 아닙니다.

### 증명하지 못하는 것

- 어느 프로필을 언제 마지막으로 썼는지는 `profiles.ini` 만으로 알기 어렵습니다. 마지막 사용 시각은 프로필 안 파일의 시각으로 봅니다. [방문·다운로드·즐겨찾기 (places.sqlite)](places-sqlite.md) 를 참고합니다.
- 프로필이 있다고 그 프로필의 주인이 키보드 앞의 사람이라고 단정할 수 없습니다.
- `profiles.ini` 에서 사라진 프로필이 실제로 지워졌다는 뜻은 아닙니다. 프로필 폴더가 디스크에 그대로 남아 있을 수 있습니다.

보고서에는 "이 컴퓨터에 파이어폭스 프로필이 세 개 있고, 각 본 폴더의 위치는 다음과 같다" 처럼 씁니다.

## 함정과 한계

- **원본 프로필을 브라우저로 열지 않습니다.** 파이어폭스로 프로필을 열면 파일이 바뀝니다. 항상 해시를 기록한 사본으로 분석합니다.
- **쓰는 중인 프로필은 잠깁니다.** 파이어폭스는 쓰는 중인 프로필을 운영체제 파일 잠금으로 잠급니다. 같은 프로필로 두 번째 실행을 하면 "프로필 사용 중" 오류가 납니다. 실행 중인 프로필은 파일이 계속 바뀌고, 복사가 막히는 파일이 있을 수 있습니다. [라이브 응답](../../../03-techniques/process-acquisition/live-response/index.md) 을 참고합니다.
- **`profiles.ini` 하나만 보고 끝내지 않습니다.** 디스크에는 목록에 없는 프로필 폴더가 남아 있을 수 있습니다. `Profiles` 폴더 아래를 직접 살펴봅니다.
- **본 폴더와 로컬 폴더를 함께 봅니다.** 방문 기록은 본 폴더에 있고 캐시는 로컬 폴더에 있습니다. 한쪽만 수집하면 캐시나 기록이 빠집니다.
- **다른 컴퓨터의 프로필일 수 있습니다.** 프로필 폴더는 통째로 복사할 수 있습니다. 폴더 안 파일의 시각과 이 컴퓨터의 다른 흔적을 맞춰 봅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| 방문·다운로드·즐겨찾기 | 프로필을 실제로 언제 썼는지, 무엇을 열었는지 봅니다 | [places.sqlite](places-sqlite.md) |
| $MFT·$UsnJrnl | 프로필 폴더와 그 안 파일의 생성·수정 시각, 지운 프로필의 흔적을 봅니다 | [$MFT](../../filesystem/mft.md), [$UsnJrnl](../../filesystem/usnjrnl.md) |
| 사용자 프로필 목록 | 이 파이어폭스 프로필이 어느 윈도 사용자 계정에 속하는지 봅니다 | [사용자 프로필 목록](../../system-account/profilelist.md) |
| 섀도 복사본 | 지금은 없는 프로필의 옛 상태를 봅니다 | [섀도 복사본 활용](../../../03-techniques/analysis/volume-shadow-copy-analysis.md) |

파이어폭스 프로필 안 파일을 한눈에 보려면 [파이어폭스 (Firefox)](index.md) 허브에서 시작합니다.

## 참고 문헌

1. Mozilla, *Profile Management — Firefox Source Docs* (프로필 서비스, 본·로컬 폴더 위치, 설치본과 CityHash, 프로필 잠금). https://firefox-source-docs.mozilla.org/toolkit/profile/index.html
2. *Mozilla Firefox — Forensics Wiki* (옛 Windows 의 실제 프로필 경로 예). https://forensics.wiki/mozilla_firefox/
