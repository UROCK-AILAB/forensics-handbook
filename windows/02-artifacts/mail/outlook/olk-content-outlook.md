---
title: "첨부 임시 폴더"
parent: "아웃룩"
grand_parent: "아티팩트 · 메일"
nav_order: 1910
---

# 첨부 임시 폴더 (OLK·Content.Outlook)

> 상위 허브: [아웃룩 (Outlook)](index.md)

## 한 줄 요약

클래식 Outlook 에서 첨부를 열면 임시 폴더에 사본이 생긴다는 설명이 흔합니다. 이 폴더를 흔히 OLK 폴더, Content.Outlook 폴더라고 부릅니다. 이번에 연 공식 자료 가운데 이 폴더를 다룬 문서는 없었습니다. 그래서 이 페이지는 확인한 사실과 흔한 설명을 나눠 적고, 검체와 가상 머신에서 직접 확인하는 법을 중심으로 씁니다.

## 이 페이지 내용의 확인 상태

| 내용 | 상태 |
|---|---|
| 첨부를 열면 임시 폴더에 사본이 생긴다 | 흔한 설명. 확인하지 못했습니다 |
| Windows·Outlook 판에 따른 폴더 위치 | 흔한 설명. 확인하지 못했습니다 |
| 사본이 지워지지 않고 남는 경우 | 흔한 설명. 확인하지 못했습니다 |
| 폴더 위치를 바꾸는 설정 | 확인하지 못했습니다. 이름이 비슷한 Microsoft 문서는 "다른 이름으로 저장" 기본 폴더를 다룹니다 |
| 클래식 Outlook 이 없는 PC 의 상태 | Windows 11 25H2 PC 한 대에서 관찰했습니다 |
| 새 Outlook 의 `Olk` 폴더 | Windows 11 25H2 PC 한 대에서 관찰했습니다 |

"흔한 설명" 은 보고서에 그대로 쓰지 않습니다. 조사하는 검체와 같은 판의 Outlook 으로 재현한 뒤 씁니다(아래 실습).

## 무엇을 기록하나 · 왜 생기나

분석가 사이에 널리 퍼진 설명은 다음과 같습니다. 모두 이번에 공식 자료로 확인하지 못했습니다.

사용자가 첨부를 Outlook 안에서 바로 열면 Outlook 이 임시 폴더에 첨부 사본을 만들고, Outlook 이 비정상 종료되거나 첨부를 연 채로 두면 사본이 지워지지 않고 남습니다. 같은 이름의 파일이 쌓이면 이름 뒤에 `(2)` 같은 번호가 붙고, 99개를 넘으면 "파일을 만들 수 없습니다" 오류가 납니다.

이 설명이 맞다면 폴더 안의 파일은 첨부를 연 흔적이고, 첨부를 저장하지 않고 열기만 해도 흔적이 남기 때문에 분석가가 자주 찾습니다. 다만 동작을 확인하지 못했으므로, 이 페이지는 폴더를 찾고 내용을 맞춰 보는 방법에 무게를 둡니다.

## 위치와 버전별 차이

### 흔히 알려진 위치 (확인하지 못함)

| Outlook · Windows | 흔히 알려진 위치 |
|---|---|
| Outlook 2003 이전 (Windows XP) | Temporary Internet Files 아래 `OLK` 로 시작하는 폴더 |
| Outlook 2007 이후, Windows Vista·7 | `%LOCALAPPDATA%\Microsoft\Windows\Temporary Internet Files\Content.Outlook\<무작위 8글자>\` |
| Outlook 2007 이후, Windows 8 이후 | `%LOCALAPPDATA%\Microsoft\Windows\INetCache\Content.Outlook\<무작위 8글자>\` |

폴더 위치는 Outlook 의 레지스트리 설정이 정한다는 설명도 흔하지만, 키와 값 이름은 이번에 확인하지 못해 이 페이지에 적지 않습니다.

- Microsoft 문서 "Change the folder where emails and attachments are saved in Outlook" (옛 KB 823131) 은 이름이 비슷하지만 임시 폴더를 다루지 않습니다. 이 문서는 "다른 이름으로 저장" 의 기본 폴더(기본값 `Documents`)를 바꾸는 값 `HKCU\Software\Microsoft\Office\16.0\Outlook\Options` 의 `DefaultPath` 를 설명하며, 이 값을 첨부 임시 폴더 위치로 읽지 않습니다.
- 위치가 바뀔 수 있으므로 기본 위치만 보지 않습니다. 디스크 전체에서 폴더 이름으로 찾습니다(아래 "직접 분석해 보기").

### 클래식 Outlook 이 없는 PC 에서 본 것

아래는 새 Outlook 만 깔린 PC 에서 본 것입니다. (확인 범위: Windows 11 25H2 PC 한 대, 클래식 Outlook 없음)

`%LOCALAPPDATA%\Microsoft\Windows\INetCache` 아래에는 `Content.IE5`·`Content.MSO`·`Content.Word`·`IE`·`Low`·`Virtualized`·`WebTempDir` 만 있었고 `Content.Outlook` 은 없었습니다. `HKCU\Software\Microsoft\Office\16.0\Outlook` 아래에는 `Options` 키만 있었습니다.

클래식 Outlook 을 쓰지 않은 PC 에서는 이 폴더가 없을 수 있고, 폴더가 없다는 사실만으로 첨부를 열지 않았다고 볼 수 없습니다. 먼저 클래식 Outlook 을 썼는지부터 확인합니다([설치 프로그램](../../system-account/uninstall.md)).

### 이름이 헷갈리는 폴더: 새 Outlook 의 `Olk`

새 Outlook 은 `%LOCALAPPDATA%\Microsoft\Olk` 폴더를 씁니다. 같은 PC 에서 이 폴더 안에는 `EBWebView`·`Feedback`·`logs` 폴더와 `UserSettings.json`·`updated.txt`·`xpdApi.log` 파일이 있었습니다. (확인 범위: Windows 11 25H2 PC 한 대, 새 Outlook 1.2026.707.300)

이 폴더는 클래식 Outlook 의 OLK 임시 폴더와 다르므로 이름만 보고 첨부 임시 폴더로 보고하지 않습니다. 새 Outlook 의 흔적은 [새 Outlook](../new-outlook.md)에서 다룹니다.

## 증거로서 의미

| 증명하는 것 | 증명하지 못하는 것 |
|---|---|
| 폴더 안에 파일이 있으면, 그 이름과 내용의 파일이 그 경로에 있었습니다 | 사용자가 Outlook 에서 그 첨부를 열었다는 것. 사본이 생기는 동작을 이 글에서 확인하지 못했습니다. 같은 판으로 재현해 확인한 뒤에만 이렇게 씁니다 |
| 파일 해시가 PST·OST 안 첨부의 해시와 같으면 내용이 같습니다 | 그 첨부가 어느 메시지에 붙어 있었는지. 해시가 같은 첨부가 여러 메시지에 있을 수 있습니다 |
| 파일 시스템 시각은 파일이 그 폴더에 생기고 바뀐 때를 알려 줍니다 | 폴더가 비었거나 없을 때, 첨부를 열지 않았다는 것 |

### 보고서 문장

아래 파일 이름과 시각은 설명을 위해 만든 예입니다.

- 쓸 수 있는 문장: "`...\INetCache\Content.Outlook\` 아래 하위 폴더에 `견적서.xlsx` 가 있습니다. 파일 만든 시각은 2025-04-02 01:15:07 UTC 입니다. 이 파일의 SHA-256 은 사용자 OST 안 메시지 첨부 `견적서.xlsx` 의 값과 같습니다."
- 쓰면 안 되는 문장: "사용자는 4월 2일 Outlook 에서 견적서 첨부를 열어 보았습니다."

앞 문장에 "첨부를 열었다" 는 해석을 더하려면, 같은 판의 Outlook 에서 첨부를 열었을 때 이 폴더에 사본이 생기는지 재현한 결과를 함께 적습니다.

## 시각 해석

폴더 안 파일의 NTFS 시각은 파일이 그 폴더에 생기고 바뀐 시각입니다. 읽는 법은 [마스터 파일 테이블](../../filesystem/mft.md)을 봅니다. 흔한 설명이 맞다면 파일 만든 시각은 첨부를 연 무렵이지만, 이 해석은 재현으로 확인한 뒤에 씁니다.

첨부가 붙은 메시지의 보낸 시각·받은 시각은 PST·OST 안의 속성 값이므로 폴더 안 파일의 시각과 따로 봅니다. 사본이 지워졌어도 [USN 변경 저널](../../filesystem/usnjrnl.md)에 파일이 생기고 지워진 기록이 남았는지 봅니다.

## 함정과 한계

1. **흔한 설명을 확인 없이 보고서에 씁니다.** 이 페이지의 위치·동작 설명은 공식 자료로 확인하지 못했습니다. 같은 판의 Outlook 으로 재현한 뒤 씁니다.
2. **새 Outlook 의 `Olk` 폴더를 첨부 임시 폴더로 봅니다.** 두 폴더는 다른 것입니다. 경로를 끝까지 읽습니다.
3. **기본 위치만 봅니다.** 위치를 바꾸는 설정이 있다는 설명이 흔합니다. 디스크 전체에서 `Content.Outlook` 과 `OLK` 로 시작하는 폴더를 찾습니다.
4. **번호 붙은 파일을 서로 다른 첨부로 셉니다.** 같은 이름이 쌓이면 번호가 붙는다는 설명이 흔합니다. `견적서 (2).xlsx` 와 `견적서.xlsx` 는 해시를 비교해 같은 내용인지 먼저 봅니다.
5. **폴더가 비었다고 첨부를 열지 않았다고 단정합니다.** 사본은 지워질 수 있습니다. [USN 변경 저널](../../filesystem/usnjrnl.md)과 [섀도 복사본](../../../03-techniques/analysis/volume-shadow-copy-analysis.md)에서 예전 모습을 찾습니다.
6. **폴더 안 파일을 메일 첨부라고 단정합니다.** 다른 프로그램이 같은 폴더에 파일을 둘 수 있는지는 확인하지 못했습니다. PST·OST 안 첨부와 해시를 맞춘 파일만 첨부 사본으로 적습니다.

## 직접 분석해 보기

### 원시 바이트로 한 번

NTFS 는 파일 이름을 UTF-16LE 로 적기 때문에 MFT 에서 폴더 이름을 바이트로 찾을 수 있습니다. 아래 바이트는 글자를 UTF-16LE 로 바꿔 계산한 값입니다.

| 찾을 글자 | 바이트 |
|---|---|
| `Content.Outlook` | `43 00 6F 00 6E 00 74 00 65 00 6E 00 74 00 2E 00 4F 00 75 00 74 00 6C 00 6F 00 6F 00 6B 00` |
| `OLK` | `4F 00 4C 00 4B 00` |

1. `$MFT` 를 뽑아 `Content.Outlook` 바이트를 찾습니다. 찾은 자리가 파일 이름 속성 안인지 확인합니다. 파일 이름 속성의 구조는 [NTFS 구조](../../../01-foundations/disk-volume/ntfs/index.md)를 봅니다.
2. 찾은 레코드의 번호를 적습니다. 부모가 이 레코드를 가리키는 다른 레코드를 찾으면 폴더 안 파일 목록이 나옵니다.
3. `OLK` 는 세 글자라 다른 이름에도 많이 나옵니다. 폴더 레코드만 남기고, 이름이 `OLK` 로 시작하는지 확인합니다.
4. 폴더 안 파일마다 해시를 구합니다.
5. PST·OST 에서 첨부를 풀어내고 해시를 구합니다. 두 목록에서 같은 해시를 찾습니다([데이터 파일 구조](pst-ost.md)).

### 공개 도구로 한 번

- `$MFT` 를 읽는 공개 도구로 전체 파일 목록을 뽑습니다. 경로에 `Content.Outlook` 이나 `\OLK` 가 든 줄만 거릅니다.
- 지워진 레코드도 목록에 넣는지 확인합니다. 지워진 사본의 이름이 남아 있을 수 있습니다.
- PST·OST 파서로 첨부를 풀어낸 결과와 해시를 맞춥니다. 해시 대조 방법은 [해시셋 대조와 유사 해시](../../../03-techniques/analysis/hash-set-fuzzy-hash.md)를 봅니다.

> 그림 자리: 메시지 첨부(PST·OST 안) → 임시 폴더의 사본 → 사본을 연 바로가기·점프리스트 기록으로 이어지는 흐름. 각 단계에서 맞춰 볼 값(해시·경로·시각)을 적은 그림

## 교차 검증

| 함께 볼 아티팩트 | 무엇을 맞춰 보나 |
|---|---|
| [데이터 파일 구조 (PST·OST)](pst-ost.md) | 폴더 안 파일과 같은 해시의 첨부가 있는지 |
| [개별 메시지 파일 (MSG)](msg.md) | 임시 폴더에 `.msg` 가 있으면 그 안의 수신자·첨부 |
| [마스터 파일 테이블](../../filesystem/mft.md) · [USN 변경 저널](../../filesystem/usnjrnl.md) | 사본이 생기고 지워진 시각 |
| [바로가기 파일](../../file-folder-usage/lnk.md) · [점프리스트](../../file-folder-usage/jump-lists.md) | 임시 폴더 경로의 파일을 연 기록 |
| [최근 문서](../../file-folder-usage/recentdocs.md) · [오피스 사용 흔적](../../file-folder-usage/microsoft-office/index.md) | 첨부 이름의 문서를 연 기록 |
| [다운로드 출처 표시](../../filesystem/zone-identifier.md) | 사본에 출처 표시 스트림이 붙어 있는지 |
| [인터넷 익스플로러·옛 엣지](../../browsers/ie-edgehtml/index.md) | 같은 인터넷 캐시 폴더 아래 다른 폴더 |

첨부로 들어온 파일을 추적하는 순서는 [이 파일은 어디서 왔나](../../../04-scenarios/activity/file-origin.md)에서 다룹니다.

## 실습

**직접 만든 가상 머신에 클래식 Outlook 을 깔고** 해 봅니다. 이 페이지의 흔한 설명을 확인하는 실습입니다.

1. 문서 첨부가 붙은 메일을 받고, 첨부를 저장하지 않고 Outlook 안에서 엽니다. 디스크 전체에서 그 파일 이름을 찾아보십시오. 사본이 어느 폴더에 생겼습니까?
2. 그 폴더 경로가 레지스트리의 Outlook 설정 키 아래 어느 값에 들어 있는지 찾아보십시오. `Options` 의 `DefaultPath` 와는 다른 값입니까?
3. 같은 첨부를 여러 번 엽니다. 파일 이름이 어떻게 바뀝니까?
4. 첨부를 연 채로 Outlook 을 정상 종료한 경우와 작업 관리자로 강제 종료한 경우를 비교해 보십시오. 사본이 남습니까?
5. 첨부를 열지 않고 "다른 이름으로 저장" 만 했을 때도 임시 폴더에 사본이 생깁니까?

**공개 검체(NIST CFReDS 등)** 가운데 클래식 Outlook 을 쓴 이미지에서도 해 봅니다.

1. `Content.Outlook` 이나 `OLK` 로 시작하는 폴더가 있습니까? 어느 경로에 있습니까?
2. 폴더 안 파일 가운데 PST·OST 안 첨부와 해시가 같은 것은 몇 개입니까?
3. USN 변경 저널에 이 폴더에서 생겼다가 지워진 파일이 있습니까?

## 참고 문헌

- Microsoft Learn, 클래식 Outlook for Windows 문제 해결 목차 — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/classic-windows-toc/toc.json
- Microsoft Learn, "Change the folder where emails and attachments are saved in Outlook" (옛 KB 823131, 2025-05-07 갱신) — https://learn.microsoft.com/en-us/microsoft-365-apps/outlook/data-files/change-the-default-save-folder
