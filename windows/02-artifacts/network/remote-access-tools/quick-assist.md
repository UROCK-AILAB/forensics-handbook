---
title: "빠른 지원"
parent: "원격 제어 프로그램"
grand_parent: "아티팩트 · 네트워크"
nav_order: 2415
---

# 빠른 지원 (Quick Assist)

빠른 지원 (Quick Assist) 은 Windows 10·11 의 시작 메뉴에서 바로 여는 원격 지원 앱이고, 두 PC 어디에도 세션 로그를 만들지 않습니다. 세션 흔적은 앱이 쓰는 WebView2 프로필 폴더의 `History` 와 파일 시각, SRUM 의 네트워크 사용량, 보안 이벤트 5058, 원격 데스크톱 비트맵 캐시에 나뉘어 남습니다. 이 기록들을 합치면 세션이 언제 열리고 닫혔는지, 이 PC 가 화면을 내준 쪽인지 본 쪽인지 판단할 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

빠른 지원 세션에는 두 역할이 있습니다. 도우미 (helper) 는 보안 코드를 만들어 상대에게 알려 주고 상대 화면을 보거나 조작하는 사람이고, 공유자 (sharer) 는 그 코드를 넣고 자기 화면을 내주는 사람입니다. 공유자가 화면 공유를 허용하면 세션이 열리고, 도우미가 제어를 요청해 공유자가 허용하면 도우미가 조작까지 할 수 있습니다[2]. [허브](index.md)의 말로 옮기면 공유자 PC 가 받는 쪽, 도우미 PC 가 거는 쪽입니다.

도우미는 Microsoft 계정이나 Microsoft Entra ID 로 로그인해야 하지만 공유자는 로그인하지 않습니다. 두 PC 는 `https://remoteassistance.support.services.microsoft.com` 의 원격 지원 서비스에 443 포트로 접속하고, 화면과 입력은 RDP 중계 서비스를 거쳐 오갑니다[2].

빠른 지원은 세션 로그를 두 PC 어디에도 만들지 않습니다[2]. Microsoft 는 세션 시작·끝 시각, 오류, 쓴 기능 같은 적은 양의 세션 데이터를 서비스 쪽에 남기고, 공유자·도우미에 관한 데이터는 3일보다 오래 두지 않습니다[2]. 그래서 PC 에서는 앱이 부수적으로 남기는 기록을 찾아야 합니다.

- **WebView2 프로필 폴더**: 새 빠른 지원 앱은 Edge WebView2 로 만든 앱이라서[2] 사용자 프로필 안에 Chromium 과 같은 모양의 폴더가 생깁니다. 이 안의 `History` 에 세션 화면 주소가 방문 기록처럼 남습니다[1].
- **SRUM 네트워크 사용량**: `QuickAssist.exe` 가 주고받은 바이트 수가 남습니다[1].
- **보안 이벤트 5058**: 세션이 열릴 때 공유자 PC 에만 남습니다[1].
- **원격 데스크톱 비트맵 캐시**: 도우미 PC 에 생깁니다[1][3].

조사에서 이 흔적이 필요한 배경도 있습니다. 2024년에는 IT 지원팀을 사칭한 전화·Teams 연락으로 사용자가 빠른 지원 세션을 열게 한 뒤 랜섬웨어까지 이어진 침해가 보고됐습니다[5]. 따로 설치한 원격 제어 도구가 없다고 원격 조작이 없었다고 볼 수 없습니다.

## 위치와 버전별 차이

이 페이지의 WebView2 프로필 흔적은 Microsoft Store 에서 받는 새 빠른 지원 앱에 해당합니다. Windows 11 에는 WebView2 런타임이 들어 있고, Windows 10 에서는 앱이 처음 실행될 때 WebView2 가 없으면 설치합니다[2]. 앱 버전에 따라 파일 이름과 동작이 달라질 수 있으므로, 분석 대상의 앱 버전을 먼저 확인합니다.

| 흔적 | 위치 | 남는 PC |
|---|---|---|
| 앱 패키지 | 패키지 이름 `MicrosoftCorporationII.QuickAssist`[2], 실행 파일 `QuickAssist.exe`[6] | 두 PC |
| WebView2 프로필 | `%LOCALAPPDATA%\Temp\QuickAssist\EBWebView\Default\`[1] | 두 PC |
| 방문 기록 | 위 폴더의 `History`[1] | 두 PC. `roleselection#` 주소는 공유자 PC 에서만 늘어납니다 |
| 파일 시각 | 위 폴더의 `Secure Preferences`, `Network Action Predictor`, `Network\DIPS`[1] | 두 PC |
| 세션 스토리지 | 위 폴더의 `Session Storage\`[1] | 두 PC |
| SRUM | `%SystemRoot%\System32\sru\SRUDB.dat` 네트워크 사용량 표 | 두 PC. 보낸 양과 받은 양의 비율이 다릅니다 |
| 보안 이벤트 5058 | Security 로그[1] | 공유자 PC |
| 비트맵 캐시 | `%LOCALAPPDATA%\Microsoft\Terminal Server Client\Cache`[1] | 도우미 PC |

WebView2 프로필이 `%LOCALAPPDATA%\Temp` 아래에 있다는 점을 기억해 둡니다. 임시 파일을 정리하는 동작으로 이 폴더가 통째로 사라질 수 있습니다. `EBWebView` 폴더가 무엇이고 다른 앱에서는 어디에 생기는지는 [Electron·WebView2 앱 데이터 위치](../../../01-foundations/app-mail-data/chromium-electron-webview2/teams-discord-slack.md)에서 다룹니다.

## 구조

### History 의 세션 주소

`History` 는 암호화되지 않은 SQLite 파일입니다[1]. 표 구성과 시각 열은 브라우저의 방문 기록과 같으므로 [방문·다운로드 기록](../../browsers/chrome-edge-whale/history.md)에서 읽는 법을 봅니다. 빠른 지원에서 볼 주소는 세 개입니다[1].

| 주소 | 뜻 | 마지막 방문 시각 |
|---|---|---|
| `https://remoteassistance.support.services.microsoft.com/screenshare` | 세션에 참가한 화면. 방문 횟수가 세션 수를 따라 늘어납니다 | 가장 최근에 세션에 참가한 시각 |
| `https://remoteassistance.support.services.microsoft.com/status/ended` | 세션이 끝난 화면 | 가장 최근 세션이 끝난 시각 |
| `https://remoteassistance.support.services.microsoft.com/roleselection#` | 상대에게 제어를 넘긴 화면. 공유자 PC 에서 제어를 넘겼을 때만 방문 횟수가 늘어납니다 | 가장 최근에 상대에게 제어를 넘긴 시각 |

`urls` 표에는 주소마다 마지막 방문 시각만 있으므로, 세션마다의 시각은 `visits` 표에서 방문 한 번씩 읽습니다.

### 프로필 폴더의 파일 시각

프로필 폴더의 파일 몇 개는 내용보다 파일 시스템 시각이 쓸모 있습니다[1].

| 파일 | 볼 시각 | 뜻 |
|---|---|---|
| `Secure Preferences` | 만든 시각 | 이 PC 가 처음 세션에 참가한 때. 앱을 실행하기만 해서는 생기지 않습니다 |
| `Network Action Predictor` | 수정 시각 | 가장 최근 세션이 열린 때 |
| `Network\DIPS` | 수정 시각 | 가장 최근 세션이 끝난 때. 세션 시작, 제어 넘김, 제어 회수, 세션 종료 때마다 바뀝니다 |

`Secure Preferences` 와 `DIPS` 가 Chromium 프로필에서 무엇을 담는 파일인지는 [프로필 폴더와 계열 브라우저 구분](../../../01-foundations/app-mail-data/chromium-electron-webview2/user-data-profile-local-state.md)에 목록이 있습니다. 이 페이지에서는 빠른 지원 세션과 맞물려 바뀌는 시각만 봅니다.

### 세션 스토리지

`Session Storage\` 폴더의 파일에 세션을 연 날짜·시각이 사람이 읽는 문자열로 목록처럼 남고, 세션을 열 때 찾은 원격 지원 도메인도 함께 남습니다[1]. 이 폴더는 LevelDB 형식이라 파일 이름에 번호가 붙습니다. 어떤 파일에 문자열이 있는지는 폴더 안 파일을 모두 문자열 검색해서 확인합니다. LevelDB 를 읽는 법은 [LevelDB](../../../01-foundations/database-log-formats/leveldb.md)와 [웹 저장소](../../browsers/chrome-edge-whale/local-storage-indexeddb.md)에서 다룹니다.

### 역할을 판단하는 기록

| 기록 | 공유자 PC (화면을 내준 쪽) | 도우미 PC (화면을 본 쪽) |
|---|---|---|
| SRUM 의 `QuickAssist.exe` 행 | 보낸 양이 받은 양보다 많습니다[1] | 받은 양이 보낸 양보다 많습니다[1] |
| 보안 이벤트 5058, `KeyName` 이 `Desktop Sharing` | 연결이 열릴 때 남습니다[1] | 남지 않습니다[1] |
| `History` 의 `roleselection#` | 제어를 넘기면 방문 횟수가 늘어납니다[1] | 늘어나지 않습니다[1] |
| 원격 데스크톱 비트맵 캐시 | 생기지 않습니다[1] | 생깁니다. 공유자 화면 조각이 들어 있습니다[1][3] |

네 가지 가운데 SRUM 이 역할을 판단하는 데 가장 기대기 좋은 기록입니다[1]. 표 구조와 읽는 법은 [네트워크 사용량](../../execution/system-resource-usage-monitor/network-data-usage.md)에서 다룹니다.

5058 은 키 저장소 공급자 (Key Storage Provider, KSP) 로 키 파일을 읽거나 쓰거나 지울 때 남는 이벤트이고, 감사 정책의 "기타 시스템 이벤트 감사 (Audit Other System Events)" 하위 범주에 속합니다[4]. 빠른 지원에서는 연결이 성공할 때마다 시작 무렵에 남습니다[1]. 이 하위 범주를 켜 두지 않은 PC 에는 남지 않습니다. 필드는 `SubjectUserSid`, `SubjectUserName`, `SubjectDomainName`, `SubjectLogonId`, `ProviderName`, `AlgorithmName`, `KeyName`, `KeyType`, `KeyFilePath`, `Operation`, `ReturnCode` 입니다[4]. 감사 정책을 확인하는 법은 [감사 정책과 로그 설정](../../event-logs/audit-policy-log-settings.md)에 있습니다.

### DNS 이름

빠른 지원은 `*.support.services.microsoft.com` 을 주 접속 도메인으로 씁니다[2]. 화면 공유 세션이 열리면 RDP 중계 서버의 지역별 이름을 조회하는데, 이 이름은 자료마다 다르게 적혀 있습니다. HackUponTheGale 은 `rdprelayv3*.support.services.microsoft.com` 형식을 적었고[1], HUNT-IR 은 `relayv2.support.services.microsoft.com` 과 `rdprelayv2northeuropeprod-2.support.services.microsoft.com` 을 적었습니다[3]. 버전 번호와 지역 이름이 바뀔 수 있으므로 `rdprelay` 와 `support.services.microsoft.com` 을 함께 찾습니다.

## 증거로서 의미

**증명하는 것**

- `History` 에 `screenshare` 주소가 있으면 이 사용자 프로필에서 빠른 지원 세션에 참가한 적이 있습니다. 방문 횟수는 참가한 세션 수를 따릅니다.
- `roleselection#` 주소의 방문 기록은 이 PC 에서 상대에게 제어를 넘긴 기록입니다. 상대가 화면을 보기만 한 것이 아니라 조작할 수 있었다는 뜻입니다.
- SRUM 의 보낸 양과 받은 양 비율로 이 PC 가 공유자였는지 도우미였는지 판단할 수 있습니다.
- `KeyName` 이 `Desktop Sharing` 인 5058 은 그 시각에 이 PC 가 화면을 내주는 연결이 열린 기록입니다.
- 도우미 PC 의 비트맵 캐시에는 상대 화면 조각이 남아서, 도우미가 무엇을 보았는지 일부를 확인할 수 있습니다.

**증명하지 못하는 것**

- 상대가 누구인지는 공유자 PC 기록으로 알기 어렵습니다. 공유자에게는 도우미 이름의 줄인 형태(이름과 성의 첫 글자)만 보이고[2], 도우미의 IP 주소와 Microsoft 계정 메일 주소는 보이지 않습니다[3]. Microsoft 는 세션 데이터를 3일보다 오래 두지 않습니다[2].
- 세션 중에 누른 키, 실행한 명령, 옮긴 파일은 이 기록들에 없습니다. [프로세스 생성](../../event-logs/4688.md) 기록과 파일 시스템 흔적으로 따로 찾습니다.
- `History` 의 `urls` 표 마지막 방문 시각과 `Network Action Predictor`·`DIPS` 수정 시각은 가장 최근 세션만 보여 줍니다. 앞선 세션은 `visits` 표, 세션 스토리지, SRUM 에서 찾습니다.
- `roleselection#` 기록이 없다고 조작이 없었다고 단정하지 않습니다. 프로필 폴더가 지워졌을 수 있습니다.
- 5058 이 없다고 공유가 없었다고 단정하지 않습니다. 감사 정책이 꺼져 있으면 남지 않습니다.
- 이 기록만으로 키보드 앞에 누가 있었는지는 알 수 없습니다.

보고서에는 기록으로 확인되는 만큼만 씁니다. 예를 들면 "사용자 kim 의 `%LOCALAPPDATA%\Temp\QuickAssist\EBWebView\Default\History` 에 `…/roleselection#` 주소의 방문 기록이 1회 있고, 마지막 방문 시각은 2025-03-14 01:12:40 UTC 이다. 같은 시간대 SRUM 의 `QuickAssist.exe` 행은 보낸 양이 받은 양보다 많다. 이 기록으로 이 PC 가 화면을 내준 쪽이며 상대에게 제어를 넘겼다고 볼 수 있으나, 상대가 누구인지와 세션 중에 한 일은 알 수 없다." 처럼 씁니다(만든 예시).

## 시각 해석

| 기록 | 형식 | 기준 | 무엇을 기준으로 기록되나 |
|---|---|---|---|
| `History` 방문 시각 | 1601-01-01 0시부터 센 마이크로초 | UTC | 앱이 그 주소를 연 때 |
| 프로필 파일의 만든·수정 시각 | NTFS 파일 시각 | UTC | 파일을 만들거나 고친 때 |
| 세션 스토리지 문자열 | 사람이 읽는 날짜·시각 | 실제 데이터로 확인 | 세션을 연 때 |
| SRUM `TimeStamp` | OLE 자동화 날짜 | UTC | DB 에 쓴 때. 통신한 때가 아닙니다 |
| 5058 | 이벤트 레코드 시각 | UTC | 연결이 열릴 때 키 파일을 다룬 때 |
| 비트맵 캐시 파일 수정 시각 | NTFS 파일 시각 | UTC | 마지막 세션이 끝난 때[1] |

- `History` 의 시각 변환은 [방문·다운로드 기록](../../browsers/chrome-edge-whale/history.md)에서, 파일 시각은 [마스터 파일 테이블](../../filesystem/mft.md)에서 봅니다.
- 세션 스토리지 문자열의 시간대는 같은 세션의 `History` `screenshare` 방문 시각과 비교해 확인합니다.
- SRUM 한 행은 한 시간 안팎 구간의 합계입니다. 짧은 세션은 구간 안 어디쯤이었는지 SRUM 만으로 알 수 없으므로, `History` 와 5058 로 세션 시각을 먼저 잡고 그 시각을 덮는 SRUM 행을 찾습니다.
- `screenshare` 방문과 `Network Action Predictor` 수정 시각은 세션 시작 무렵에, `status/ended` 방문과 `DIPS` 수정 시각은 세션 끝 무렵에 모입니다. 공유자 PC 라면 5058 도 시작 무렵에 붙습니다. 두 묶음이 서로 맞으면 한 세션의 시작과 끝으로 봅니다. 몇 초 차이까지 같은 사건으로 볼지는 실습 3번처럼 실제 데이터로 재 봅니다.

## 함정과 한계

- **따로 설치한 도구만 찾으면 놓칩니다.** 빠른 지원은 시작 메뉴에서 바로 여는 앱이라[2], 새로 설치된 원격 제어 도구를 찾는 방법으로는 드러나지 않을 수 있습니다. `QuickAssist.exe` 실행 흔적과 이 페이지의 프로필 폴더를 함께 봅니다.
- **프로필 폴더가 `Temp` 아래에 있습니다.** 임시 파일 정리로 지워질 수 있으니 수집을 서두르고, 지워졌다면 [마스터 파일 테이블](../../filesystem/mft.md)과 섀도 복사본에서 옛 기록을 찾습니다.
- **`urls` 표는 마지막 시각만 적습니다.** 세션이 여러 번이면 `visits` 표를 봐야 세션마다의 시각이 나옵니다.
- **SRUM 비율은 한 구간 합계입니다.** 같은 구간에 여러 세션이 겹치거나 역할이 바뀌면 비율만으로 판단하기 어렵습니다. 화면 전송량이 `QuickAssist.exe` 행에 모두 잡히는지, 다른 프로세스 행으로 나뉘는지는 실제 데이터로 확인합니다.
- **WebView2 의 다른 DB 는 암호화될 수 있습니다.** DPAPI 로 풀 수 있지만, 세션 역할을 판단하는 데 더 보탤 내용은 적습니다[1]. 암호화 방식은 [쿠키·비밀번호 암호화](../../../01-foundations/app-mail-data/chromium-electron-webview2/dpapi-app-bound-encryption.md)에서 다룹니다.
- **중계 서버 이름은 자료마다 다릅니다.** DNS 기록은 한 가지 이름으로 찾지 않습니다.

## 직접 분석해 보기

### 헥스로 한 번

`History` 는 SQLite 파일이라, 페이지와 레코드를 헥스로 따라가는 법은 [SQLite 데이터베이스](../../../01-foundations/database-log-formats/sqlite/index.md)와 [방문·다운로드 기록](../../browsers/chrome-edge-whale/history.md)에서 다룹니다. 이 페이지에서는 따로 헥스 예시를 싣지 않습니다. 세션 스토리지는 헥스 편집기에서 `remoteassistance` 문자열을 찾으면 그 근처에 날짜·시각 문자열이 보입니다.

### 공개 도구로 한 번

`History` 는 사본을 만든 뒤 `sqlite3` 로 엽니다. 아래는 세션 주소의 방문을 한 번씩 UTC 로 뽑습니다.

```sql
SELECT u.url, u.visit_count,
       datetime(v.visit_time / 1000000 - 11644473600, 'unixepoch') AS visit_utc
FROM visits v JOIN urls u ON u.id = v.url
WHERE u.url LIKE 'https://remoteassistance.support.services.microsoft.com/%'
ORDER BY v.visit_time;
```

프로필 파일의 시각은 마운트한 이미지에서 PowerShell 로 봅니다.

```powershell
$p = 'E:\mount\Users\*\AppData\Local\Temp\QuickAssist\EBWebView\Default'   # 마운트한 경로로 바꿉니다
Get-Item "$p\Secure Preferences", "$p\Network Action Predictor", "$p\Network\DIPS" |
  Select-Object FullName, CreationTimeUtc, LastWriteTimeUtc
```

5058 은 메시지 문구가 OS 언어에 따라 바뀌므로 XML 의 `KeyName` 필드로 거릅니다.

```powershell
Get-WinEvent -FilterHashtable @{ Path = 'E:\case\Security.evtx'; Id = 5058 } |
  Where-Object { ([xml]$_.ToXml()).Event.EventData.Data |
    Where-Object { $_.Name -eq 'KeyName' -and $_.'#text' -eq 'Desktop Sharing' } } |
  Select-Object @{ n = 'UTC'; e = { $_.TimeCreated.ToUniversalTime() } }, RecordId
```

SRUM 은 SrumECmd 같은 도구로 네트워크 사용량 표를 CSV 로 내보낸 뒤 `QuickAssist.exe` 행만 골라 시간대별 보낸 양과 받은 양을 비교합니다[1]. 비트맵 캐시는 [원격 데스크톱 비트맵 캐시](../rdp-bitmap-cache.md)의 방법으로 타일을 꺼냅니다.

## 교차 검증

| 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|
| SRUM 네트워크 사용량 | `QuickAssist.exe` 의 시간대별 보낸 양·받은 양. 역할 판단 | [네트워크 사용량](../../execution/system-resource-usage-monitor/network-data-usage.md) |
| 원격 데스크톱 비트맵 캐시 | 도우미 PC 에서 본 공유자 화면 조각 | [원격 데스크톱 비트맵 캐시](../rdp-bitmap-cache.md) |
| 프로세스 생성 · Sysmon 1 | `QuickAssist.exe` 실행 시각과 세션 직후 실행된 프로그램. Sigma 규칙 "QuickAssist Execution" 이 이 이미지 이름을 찾습니다[6] | [프로세스 생성](../../event-logs/4688.md), [Sysmon 로그](../../event-logs/sysmon/index.md) |
| Sysmon 22 (DNS 조회) | `QuickAssist.exe` 가 `remoteassistance.support.services.microsoft.com` 을 조회한 시각. Sigma 규칙 "DNS Query Request By QuickAssist.EXE" 가 이것을 찾습니다[6] | [Sysmon 이벤트 3·22](../../event-logs/sysmon/3-22.md) |
| 실행 흔적 | 프리페치·BAM·AmCache 의 `QuickAssist.exe` | [프리페치](../../execution/prefetch/index.md), [BAM·DAM](../../execution/background-activity-moderator.md), [AmCache](../../execution/amcache-hve/index.md) |
| 앱 패키지 등록 | `MicrosoftCorporationII.QuickAssist` 가 이 사용자에게 등록된 시각 | [앱 패키지 등록 기록](../../system-account/appx-staterepository.md) |
| Teams 외부 대화 | 세션 직전에 온 외부 연락 | [마이크로소프트 팀즈](../../messengers/teams.md) |

세션 뒤에 다른 원격 제어 도구를 설치했는지는 [허브](index.md)의 공통 흔적으로 찾고, 조사 순서는 [원격 제어 프로그램으로 누가 조작했나](../../../04-scenarios/incident/remote-access-tool-abuse.md)를 따릅니다.

## 실습

빠른 지원 흔적이 있는 공개 이미지나, 직접 만든 Windows 11 가상 머신 두 대로 아래 질문을 풀어 봅니다.

1. 두 PC 의 `%LOCALAPPDATA%\Temp\QuickAssist\EBWebView\Default\History` 에서 `screenshare` 방문 횟수는 몇 번입니까? 실제로 연 세션 수와 같습니까?
2. 도우미가 제어를 요청하고 공유자가 허용한 뒤, 두 PC 가운데 어느 쪽에서 `roleselection#` 방문 횟수가 늘어납니까?
3. `Network Action Predictor` 와 `Network\DIPS` 의 수정 시각을 `screenshare`·`status/ended` 방문 시각과 비교합니다. 몇 초 차이 납니까?
4. 공유자 PC 에서 기타 시스템 이벤트 감사를 켜고 세션을 엽니다. `KeyName` 이 `Desktop Sharing` 인 5058 이 남습니까? 도우미 PC 에도 남습니까?
5. 한 시간 넘게 기다린 뒤 두 PC 의 SRUDB.dat 에서 `QuickAssist.exe` 행의 보낸 양과 받은 양을 비교합니다.

## 참고 문헌

1. Brandon Smith (HackUponTheGale), "Investigating Microsoft Quick Assist" (2023-10-31). https://hackuponthegale.github.io/blog/dfir/QuickAssist1
2. Microsoft Learn, "Use Quick Assist to help users" (ms.date 2025-08-18). https://learn.microsoft.com/en-us/windows/client-management/client-tools/quick-assist
3. John A (HUNT-IR), "Forensics Blog: Quick Assist RAT?". https://www.hunt-ir.com/huntirs-blog/quick-assist-rat
4. Microsoft Learn, "5058(S, F) Key file operation" (ms.date 2021-09-08). https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5058
5. Microsoft Threat Intelligence, "Threat actors misusing Quick Assist in social engineering attacks leading to ransomware" (2024-05-15). https://www.microsoft.com/en-us/security/blog/2024/05/15/threat-actors-misusing-quick-assist-in-social-engineering-attacks-leading-to-ransomware/
6. SigmaHQ 규칙 저장소 (커밋 07ec293, 2026-09-25). rules/windows/process_creation/proc_creation_win_quickassist_execution.yml, rules/windows/dns_query/dns_query_win_quickassist.yml. https://github.com/SigmaHQ/sigma
