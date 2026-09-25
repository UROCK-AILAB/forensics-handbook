---
title: "Recall"
parent: "아티팩트 · Windows의 AI 기능"
nav_order: 460
---

# Recall (Recall)

Recall 은 Copilot+ PC 에서 화면 스냅숏을 주기적으로 저장하고 기기 안에서 분석해 자연어로 다시 찾게 해 주는 Windows 기능이고, 스냅숏과 색인을 사용자 폴더 아래 암호화된 저장소에 남깁니다.

> 확인 날짜: 2026-09. 기능·보호 방식·정책은 Microsoft 공식 문서(Manage Recall 은 ms.date 2025-12-10, WindowsAI Policy CSP 는 ms.date 2026-09-10)로 확인했습니다. 저장 경로와 DB 표 이름은 Microsoft 문서에 없고, 제3자 연구 도구의 설명서(Windows 11 25H2 Build 26300.8155 ARM64, AIXHost.exe 2126.7602.0.0 에서 시험, 2026-04 판)에서 가져왔습니다. 이 핸드북을 쓰면서 Recall 폴더를 직접 관찰하지는 않았습니다. Microsoft 문서는 2026-09 에도 Recall 을 미리 보기(preview)로 적고 있고, Recall 앱의 버전 번호는 확인하지 못했습니다.

## 무엇을 기록하나 · 왜 생기나

Recall 을 켠 사용자의 화면 내용이 직전 스냅숏과 달라지면 Windows 가 스냅숏을 한 장 저장하고, 로컬 OCR 로 글자를 읽어 이미지와 텍스트를 모두 검색할 수 있게 한 뒤 타임라인으로 정리합니다. 오디오는 녹음하지 않고 연속 동영상도 남기지 않으며, DRM 콘텐츠와 게임 모드 중의 게임 화면(지원 플랫폼)도 저장하지 않습니다. 검색에 최적화된 언어는 영어, 중국어(간체), 프랑스어, 독일어, 일본어, 스페인어입니다.

스냅숏 저장과 분석에는 인터넷이나 클라우드를 쓰지 않고 스냅숏을 Microsoft 로 보내지도 않아서, Recall 의 원본은 그 기기에만 있고 서버 사본을 요청할 곳이 없습니다. 예외는 타임라인과 검색 결과에 보여 줄 파비콘 같은 웹 메타데이터를 스냅숏 URL 의 최상위 도메인에서 가끔 받아 오는 일, 설정에 따라 보내는 일부 진단 데이터, 사용자가 피드백을 보낼 때 함께 가는 첨부 스크린샷입니다. 서버·기기·동기화로 나눈 일반 설명은 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

### 켜지는 조건

Recall 은 Secured-core 기준을 채운 Copilot+ PC 에서만 돌고, 최소 기준은 40 TOPS NPU, 메모리 16GB, 논리 프로세서 8개, 저장소 256GB 입니다. 켜려면 빈 공간이 50GB 이상 있어야 하고, 25GB 밑으로 떨어지면 저장을 스스로 멈춥니다. 장치 암호화나 BitLocker 가 켜져 있어야 하고, Windows Hello 강화 로그인 보안(Enhanced Sign-in Security, ESS)에 얼굴이나 지문을 하나 이상 등록해야 합니다.

관리하지 않는 개인 기기에는 Recall 이 설치돼 있지만 기본으로 꺼져 있어서 사용자가 직접 켜야 스냅숏을 저장하고, 회사가 관리하는 기기에서는 기본으로 꺼져 있거나 제거돼 있으며 관리자가 사용자 대신 스냅숏 저장을 켤 수 없습니다. 켤지 말지는 계정마다 따로 정하고, 같은 PC 의 다른 사용자와 스냅숏을 나누지 않습니다. 선택적 기능 이름은 `Recall` 이라서 "Windows 기능 켜기/끄기"나 PowerShell 의 `Enable-WindowsOptionalFeature`/`Disable-WindowsOptionalFeature` 로 통째로 넣거나 뺄 수 있고, `ms-recall` 프로토콜로 부르면 Recall 이 열리면서 스냅숏을 한 장 찍습니다.

### 저장하지 않는 화면

민감 정보 필터(Sensitive information filtering)가 기본으로 켜져 있어서, 비밀번호나 신분증 번호, 카드 번호 같은 정보를 감지하면 그 스냅숏은 저장하지 않습니다. 이 감지에는 NPU 와 Microsoft Classification Engine(MCE)을 씁니다. 지원 브라우저의 비공개 창도 저장하지 않는데, Edge, Firefox, Opera, Chrome 은 사이트 필터와 비공개 필터를 모두 지원하고 그 밖의 Chromium 124 이상 브라우저는 비공개 필터만 지원합니다. `edge://`, `chrome://` 같은 브라우저 내부 주소는 기본으로 거르지만, 거른 사이트라도 다른 페이지에 들어간 콘텐츠나 브라우저 기록, 뒤쪽 탭은 스냅숏에 나올 수 있습니다.

원격 데스크톱 클라이언트인 mstsc.exe, VMConnect.exe, Azure Virtual Desktop(MSI), RAIL 의 세션은 기본으로 빠지지만, 같은 문서는 클라이언트가 화면 캡처 보호를 구현하지 않으면 저장될 수 있다고도 적었습니다. `SetWindowDisplayAffinity` 에 `WDA_EXCLUDEFROMCAPTURE` 를 건 창은 담기지 않습니다. DLP 제품과 연동하면 제공자가 지정한 창만 지우고 나머지는 남기는데, 문서가 적은 지원 DLP 는 Microsoft Purview 하나입니다.

## 위치와 버전별 차이

아래 경로와 파일 이름은 제3자 연구 도구 설명서에 나온 것이고, Microsoft 는 경로를 공개하지 않았습니다. Windows 빌드마다 같은지도 밝힌 적이 없어서 검체에서 폴더가 이 모양인지 먼저 봅니다.

```
%LocalAppData%\CoreAIPlatform.00\UKP\{GUID}\
    ukg.db                      주 DB (SQLite)
    SemanticTextStore.sidb      텍스트 의미 검색 색인
    SemanticImageStore.sidb     이미지 의미 검색 색인
    ImageStore\                 스냅숏 PNG 원본과 썸네일
```

`{GUID}` 는 사용자마다 다릅니다. 같은 설명서는 판을 둘로 나눕니다.

| 판 | 시기 | 보호 |
|---|---|---|
| 초기 미리 보기 | 2024-06 | 암호화 전 형태 |
| 다시 설계한 판 | 2025-04 이후 | ukg.db 를 SQLite SEE 의 AES-256-GCM 으로 암호화, VBS 엔클레이브, Windows Hello 인증 |

Microsoft 문서가 설명하는 다시 설계한 판의 보호 방식은 다음과 같습니다. 스냅숏과 벡터 DB 관련 정보는 늘 암호화하고, 키는 TPM 이 보호하면서 사용자의 Windows Hello ESS 신원에 묶이며, VBS 엔클레이브 안의 작업만 키를 씁니다. Recall 을 열 때와 스냅숏에 접근할 때마다 Windows Hello 로 본인을 확인하고 그 순간에만 복호하며(just in time decryption), 다른 사용자는 물론 관리자와 Microsoft 도 스냅숏을 볼 수 없다고 문서에 적혀 있습니다. Windows 앱 데이터 보호에 흔히 쓰는 DPAPI 는 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/protection/data-protection-api/index.html)에 설명이 있지만, Recall 문서가 적은 키 보호는 TPM·Windows Hello ESS·VBS 엔클레이브이고 DPAPI 와의 관계는 문서에 없습니다.

### 설정과 정책

사용자 설정은 설정 → 개인 정보 및 보안 → Recall & snapshots 에 있지만, 이 토글과 필터 목록, 보존 기간을 어느 파일이나 레지스트리에 저장하는지는 확인하지 못했습니다. 조직이 거는 정책은 `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` 키에 들어가고(ADMX 는 `WindowsCopilot.admx`, 그룹 정책 경로는 Windows Components → Windows AI), 장치와 사용자 둘 다 되는 항목은 HKLM 과 HKCU 양쪽에 올 수 있습니다.

| 정책 이름 | 범위 | 값 |
|---|---|---|
| `AllowRecallEnablement` | 장치 | 0 사용 불가, 1 사용 가능(CSP 기본값 1) |
| `DisableAIDataAnalysis` | 장치·사용자 | 0 저장 허용(기본), 1 저장 끔 |
| `SetMaximumStorageSpaceForRecallSnapshots` | 장치·사용자, Ent/Edu | MB 단위 0(OS 가 정함, 기본)·10240·25600·51200·76800·102400·153600 |
| `SetMaximumStorageDurationForRecallSnapshots` | 장치·사용자, Ent/Edu | 일 단위 0·30·60·90(기본)·180 |
| `SetDenyAppListForRecall` | 장치·사용자, Ent/Edu | AUMID 나 실행 파일 이름을 세미콜론으로 이은 목록, 재부팅 후 적용 |
| `SetDenyUriListForRecall` | 장치·사용자, Ent/Edu | URI 를 세미콜론으로 이은 목록(하위 도메인·경로까지 거름), 재부팅 후 적용 |
| `AllowRecallExport` | 장치, Ent/Edu, EEA | 0 금지(기본), 1 허용(Insider 빌드 표기) |
| `SetDataLossPreventionProvider` | 장치, Ent/Edu | DLP 제공자의 레지스트리 위치와 DLL 을 적은 문자열(그룹 정책 이름 `SetDataLossPreventionProviderKey`) |
| `DisableRecallDataProviders` | 사용자, Ent/Edu, Insider | 앱 작업 제공자가 주는 추가 정보(예: 회의 참석자)를 보일지, Recall 을 다시 시작해야 적용 |

표의 이름은 CSP 정책 이름이고, CSP 문서가 `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` 아래 레지스트리 값 이름을 적어 둔 것은 이 가운데 `SetDataLossPreventionProvider` 와 `DisableRecallDataProviders` 를 뺀 일곱 개입니다. 이 두 정책이 레지스트리 어디에 남는지는 확인하지 못했습니다. `AllowRecallEnablement`, `DisableAIDataAnalysis`, 저장·필터 정책은 Windows 11 24H2 KB5055627(10.0.26100.3915) 이상에서, `SetDataLossPreventionProvider` 는 KB5065789(10.0.26100.6725) 이상에서 적용됩니다. 정책으로 Recall 을 끄거나(`AllowRecallEnablement`=0) 스냅숏 저장을 끄면(`DisableAIDataAnalysis`=1) 이미 있던 스냅숏을 지우고, `AllowRecallEnablement`=0 은 재시작 뒤 Recall 구성 요소도 기기에서 지웁니다. DLP 정책을 지우면 DLP 제공자를 더 부르지 않을 뿐 이미 저장된 스냅숏은 그대로 둡니다.

### 보존과 삭제

용량 한도는 10, 25, 50, 75, 100, 150GB 가운데 고르고, 정하지 않으면 디스크 256GB 에서 25GB, 512GB 에서 75GB, 1TB 이상에서 150GB 로 잡으며, 한도에 닿으면 가장 오래된 스냅숏부터 지웁니다. 보존 기간은 30, 60, 90, 180일 가운데 고르는데, 정하지 않았을 때의 동작을 두 문서가 다르게 적었습니다. Policy CSP 문서는 사용자가 따로 정하지 않았으면 90일이라고 적었고, Manage Recall 문서는 용량 한도에 닿을 때까지 지우지 않는다고 적었습니다. 용량과 기간을 둘 다 정하면 먼저 닿는 쪽에서 지웁니다.

사용자는 설정에서 스냅숏을 모두 지울 수 있고, 검색 결과나 스냅숏 화면에서 특정 앱이나 웹사이트의 스냅숏만 모두 지울 수도 있습니다. 알림 영역 아이콘이 저장 중, 일시 정지, 필터링 상태를 보여 주고, 그 아이콘으로 저장을 잠시 멈출 수 있습니다. 보관 설정과 삭제의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

### 내보내기(EEA 한정)

유럽경제지역(EEA) 기기에서만 사용자가 스냅숏을 내보낼 수 있고, 관리 기기는 기본으로 막혀 있습니다. 지난 스냅숏을 한 번 내보내거나(최근 7일, 30일, 전부) 지금부터 계속 내보내게 할 수 있으며, 계속 내보내기를 켜 두면 30일마다 켜져 있다고 알려 줍니다. 내보내기 전에 Windows Hello 로 본인을 확인하고, 내보내는 내용은 스냅숏과 저장 시각, 그때 열려 있던 앱 정보 같은 스냅숏 세부 정보이고, 내보낸 스냅숏은 암호화돼 있어서 다른 앱이 쓰려면 Recall 을 설정할 때 보여 준 "Recall export code" 가 있어야 합니다. 내보낸 파일의 위치와 형식은 확인하지 못했습니다.

## 구조

ukg.db 의 표 이름은 연구 도구 설명서에 나온 대로 적고, 칸 이름은 확인하지 못했습니다.

| 묶음 | 표 | 설명서가 적은 내용 |
|---|---|---|
| 캡처 | `WindowCapture` | 스크린샷, 시각, 창 제목, 창 위치·크기, 머문 시간 |
| 캡처 관계 | `WindowCaptureAppRelation`, `WindowCaptureWebRelation`, `WindowCaptureFileRelation`, `WindowCaptureTopicRelation` | 캡처와 앱·웹·파일·주제를 잇는 표 |
| 텍스트 색인 | `WindowCaptureTextIndex` | FTS5 가상 표 |
| 대상 | `App` | 앱 이름, 경로, 아이콘 URI |
| | `Web` | 도메인, URL, 파비콘 URI |
| | `File` | 경로, 확장자, NTFS 객체 ID·볼륨 ID |
| | `Topic` | 주제 |
| | `ScreenRegion` | OCR 텍스트와 픽셀 단위 영역 |
| 사용 집계 | `AppDwellTime`, `WebDomainDwellTime` | 앱별·도메인별 머문 시간, 일 단위 사용 시간 |
| 검색 | `SearchHistory`, `SearchFeedback` | 검색 이력과 피드백 |
| 관리 | `IdTable`, `_MigrationMetadata` | ID 와 이전 정보 |

의미 검색 파일(.sidb)에는 `si_items`, `si_embedding_metadata`, `si_diskann_graph`, `si_diskann_references`, `si_diskann_config`, `si_diskann_info` 표가 있다고 합니다. SQLite 파일 구조 자체는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html)에서 다룹니다.

표 설명만 보면 `App`, `Web`, `File` 표가 스냅숏 이미지와 따로 앱 경로, URL, 파일 경로를 적어 두고, `AppDwellTime` 과 `WebDomainDwellTime` 이 날마다 머문 시간을 모아 둡니다. 스냅숏이 지워진 뒤 이 표들의 행도 함께 지워지는지는 확인하지 못했습니다.

## 증거로서 의미

**증명하는 것.** 사용자 폴더 아래 `CoreAIPlatform.00\UKP` 폴더와 `ImageStore` 안의 파일은 암호화와 상관없이 존재, 크기, 파일 시스템 시각이 MFT 와 USN 저널에 남습니다. 어느 사용자 폴더에 스냅숏 파일이 언제 생기고 늘었는지를 "사용자가 켜야 저장하고 계정마다 따로 켠다" 는 문서 설명과 함께 보면, 그 계정에서 스냅숏 저장이 켜져 있던 기간을 가늠하는 단서가 될 수 있습니다. 이 해석은 문서들을 엮어 끌어낸 것이고 직접 검증하지 않았습니다. 정책 키에 `DisableAIDataAnalysis`=1 이나 `AllowRecallEnablement`=0 이 있으면 조직이 저장을 막았다는 사실과 그 뒤 기존 스냅숏이 지워졌을 가능성을 알려 줍니다. 보고서에는 "이 사용자 폴더에 Recall 저장소로 알려진 폴더가 있고, 이 기간에 이 폴더의 파일이 생기고 바뀐 기록이 있다" 처럼 씁니다.

**증명하지 못하는 것.** 다시 설계한 판에서는 디스크 이미지만으로 ukg.db 와 스냅숏 이미지의 내용을 읽는 공식 경로가 없어서, 폴더가 있어도 무엇이 화면에 떠 있었는지는 알 수 없습니다. 스냅숏이 없다고 그 화면을 보지 않았다는 뜻도 아닙니다. 민감 정보 필터, 비공개 창, DRM, 원격 데스크톱, 앱·URI 차단 목록, 캡처 제외 창이 저장을 막고, 용량과 기간 한도, 사용자의 삭제, 정책 변경이 이미 저장된 스냅숏을 지웁니다. 스냅숏이 있어도 사용자가 그 화면을 읽었다거나 그 내용을 다른 곳에 옮겼다는 뜻은 아닙니다.

## 시각 해석

연구 도구 설명서는 캡처 시각이 100나노초 단위라고만 적었습니다. 이 단위는 Windows FILETIME(1601-01-01 부터 센 값, 보통 UTC)과 같지만, ukg.db 의 값이 FILETIME 인지, UTC 인지 현지 시각인지는 확인하지 못했습니다. 설명서가 적은 `WindowCapture` 의 시각이 스냅숏을 찍은 순간인지 저장을 마친 순간인지도 알 수 없습니다.

디스크 이미지에서 바로 쓸 수 있는 시각은 파일 시스템 쪽입니다. `ImageStore` 파일의 생성 시각은 스냅숏이 저장된 무렵을, 파일이 사라진 USN 기록은 한도나 사용자 삭제, 정책으로 지워진 무렵을 가리킬 수 있지만, 어떤 까닭으로 지웠는지는 USN 기록만으로 가를 수 없습니다. 정책 키의 마지막 쓰기 시각은 정책 값이 바뀐 무렵을 알려 줍니다.

## 함정과 한계

경로와 표 이름은 Microsoft 가 밝힌 것이 아니라 한 연구 도구가 한 빌드에서 본 것이라서 빌드가 바뀌면 달라질 수 있고, 보고서에는 검체의 Windows 빌드를 함께 적습니다. 초기 미리 보기 판과 다시 설계한 판은 보호 방식이 달라서, 2024-06 무렵 자료가 설명하는 평문 DB 분석이 지금 검체에 그대로 통한다고 여기지 않습니다.

보존 기간 기본값은 두 공식 문서가 다르게 적었기 때문에, 스냅숏이 90일보다 오래된 것까지 있는지 없는지를 두고 결론을 내리기 전에 검체의 정책 값과 설정을 먼저 봅니다. 사용자 설정이 어디에 저장되는지 몰라서 정책 키가 비어 있다고 Recall 이 꺼져 있었다고 판단할 수도 없습니다. 스냅숏 생성과 삭제가 이벤트 로그에 남는지, 남는다면 어떤 채널인지도 확인하지 못했습니다. 설명서가 시험한 환경에 나오는 AIXHost.exe 가 어떤 역할을 하는지도 문서로 확인하지 못했습니다.

Recall 이 켜진 기기에서는 화면에 떠 있던 다른 AI 서비스의 대화도 스냅숏에 담길 수 있어서 대화 원본이 서버에만 있는 서비스라도 화면 기록이 남을 수 있지만, 위에서 적은 대로 디스크 이미지에서 그 내용을 읽는 공식 경로는 없습니다.

## 직접 분석해 보기

**헥스로 한 번.** 먼저 ukg.db 사본의 처음 16바이트를 봅니다. SQLite 명세상 평문 SQLite 파일은 아래 문자열로 시작합니다.

```
명세로 만든 예시(SQLite 파일 머리)
00000000  53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00  SQLite format 3.
```

이 문자열이 보이면 평문 SQLite 형태이고, 보이지 않으면 암호화된 판일 가능성을 생각합니다. 암호화한 판의 파일 머리가 어떤 모양인지는 확인하지 못했습니다.

값이 FILETIME 이라고 가정하고 읽는 연습은 FILETIME 명세로 합니다. 아래 8바이트는 2026-09-03 05:40:12 UTC 를 FILETIME 으로 바꿔 만든 예시이고, 검체에서 뜬 값이 아닙니다. 리틀 엔디언으로 읽으면 0x01DD3B66B035C600, 10진수로 134328876120000000 이고, 1천만으로 나누면 1601-01-01 부터 지난 초 수가 됩니다.

```
명세로 만든 예시(FILETIME)
00 C6 35 B0 66 3B DD 01
```

**공개 도구로 한 번.** 파일 시스템 흔적은 MFTECmd 같은 공개 도구로 `$MFT` 와 `$UsnJrnl:$J` 를 풀어 `CoreAIPlatform.00` 경로가 들어간 줄만 걸러 봅니다. 정책은 SOFTWARE 하이브와 사용자의 NTUSER.DAT 를 Registry Explorer 같은 레지스트리 도구로 열어 `SOFTWARE\Policies\Microsoft\Windows\WindowsAI` 의 값과 키의 마지막 쓰기 시각을 적습니다. 평문 SQLite 형태의 ukg.db 가 나온 경우에는 사본을 `sqlite3` 로 열어 표 목록부터 설명서의 표 이름과 맞춰 봅니다.

```sh
# 사본에서만 실행한다. 파일 이름은 만든 예시다
sqlite3 -readonly case-copy-ukg.db ".tables"
sqlite3 -readonly case-copy-ukg.db ".schema WindowCapture"
```

## 교차 검증

Recall 폴더의 파일 시각은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md)에 올려 브라우저 방문 기록, AI 앱 기록과 겹쳐 보고, Windows 타임라인 일반 방법은 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html)에 있습니다. 스냅숏 위에서 도는 [클릭 투 두](click-to-do.md)의 흔적은 그 페이지에서 다룹니다. 화면 기록이 대화 내용을 되살리는 단서가 되는 경우는 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md)에, 기기에서 이 폴더를 빠뜨리지 않고 모으는 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md)에 있습니다. 조직의 DLP 설정과 함께 보려면 [보안 제품이 남기는 AI 사용 기록](../network-enterprise/dlp-casb.md)을 봅니다.

## 실습

공개 검체에 Recall 저장소가 들어 있는지는 확인하지 못했습니다. 조건을 채운 시험용 Copilot+ PC 가 있다면 다음 질문으로 풀어 봅니다.

1. Recall 을 켜기 전과 켠 뒤의 `%LocalAppData%` 파일 목록을 비교해 어떤 폴더가 새로 생기는지, 설명서의 경로와 같은지 확인합니다.
2. 비공개 창과 일반 창에서 같은 페이지를 연 뒤 `ImageStore` 파일 수가 어떻게 달라지는지 봅니다.
3. 특정 앱의 스냅숏을 "모두 삭제" 한 뒤 USN 저널에 어떤 기록이 남는지 봅니다.
4. 정책으로 `DisableAIDataAnalysis` 를 1로 바꾼 뒤 폴더에서 무엇이 사라지고 무엇이 남는지, 정책 키의 마지막 쓰기 시각과 파일 삭제 시각이 어떻게 맞물리는지 봅니다.

## 참고 문헌

1. Update on Recall security and privacy architecture (Windows Experience Blog, 2024-09-27) — https://blogs.windows.com/windowsexperience/2024/09/27/update-on-recall-security-and-privacy-architecture/
2. Manage Recall for Windows clients (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/client-management/manage-recall
3. WindowsAI Policy CSP (Microsoft Learn) — https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-windowsai
4. TotalRecall README (xaitax, GitHub, 2026-04 확인판) — https://github.com/xaitax/TotalRecall
5. Privacy and control over your Recall experience (Microsoft Support) — https://support.microsoft.com/en-us/windows/privacy-and-control-over-your-recall-experience-d404f672-7647-41e5-886c-a3c59680af15
