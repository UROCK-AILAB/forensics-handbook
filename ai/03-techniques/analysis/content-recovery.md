---
title: "대화 내용 되살리기"
parent: "기법 · 분석"
nav_order: 790
---

# 대화 내용 되살리기 (캐시·스냅숏·알림)

화면이나 목록에서 사라진 AI 대화를 기기에 남은 사본(도구 기록의 이전 판, 편집 전 파일 사본, 앱 캐시, 화면 스냅숏)과 서버에 남은 사본에서 다시 찾는 방법이며, 원본이 어디에 있는지부터 가려야 헛수고를 줄일 수 있습니다.

> 확인 날짜: 2026-09. 기기 쪽 폴더와 키 이름은 Windows 11 PC 한 대의 AI 도구 폴더를 읽기 전용으로 열어 확인했고, 대화 내용과 설정 값은 읽지 않았습니다(확인 범위: Windows 11, 2026-09). 그래서 앱 캐시 안에 대화 내용이 실제로 남는지, 그 PC 에 깔린 앱 버전이 무엇인지는 확인하지 못했습니다. macOS·Android·iOS 는 문서와 보도 근거만 씁니다. 잠금 해제나 암호화 우회 방법은 다루지 않습니다.

## 언제 쓰나

사용자가 대화를 지웠거나, 자동 삭제로 기록이 사라졌거나, 앱 화면에 보이는 것보다 더 많은 내용을 확인해야 할 때 씁니다. 대화 내용이 필요하다는 점은 같아도 원본이 서버에 있는 서비스와 기기에 있는 도구는 찾을 곳이 전혀 달라서, 아래 표로 먼저 갈래를 정합니다.

| 대상 | 대화 원본 | 기기에서 기대할 수 있는 것 |
|---|---|---|
| 웹·모바일 채팅 서비스(ChatGPT, Claude, Gemini, Copilot) | 서버 계정 | 앱·브라우저 캐시. 대화 내용이 캐시에 남는지는 이 핸드북에서 확인하지 못함 |
| ChatGPT macOS 앱 | 서버 계정 | 2024-07 보도 기준 옛 판은 `~/Library/Application Support/com.openai.chat` 에 대화를 평문으로 두었고, 그 뒤 판은 저장한 대화를 암호화함 |
| Claude Code(로컬 세션) | 기기, 평문 JSONL | 기록 파일과 그 이전 판, 편집 전 파일 사본, 붙여넣기 캐시 |
| Gemini CLI | 기기 `~/.gemini/tmp/<project_hash>/chats/` | 세션 파일(형식은 확인하지 못함) |
| Codex CLI | 기기 `~/.codex/history.jsonl`(입력 기록) | 입력 기록. 세션 전체 기록 위치는 확인하지 못함 |
| Cursor | 기기 `state.vscdb`(작업 공간마다 하나, 제3자 도구가 2025년 중반까지 기준으로 적은 내용) | SQLite 표 `ItemTable`·`cursorDiskKV` |
| Windows Recall | 기기에만 있음(2025-04 이후 판은 암호화) | 폴더·파일의 존재, 크기, 파일 시스템 시각 |

## 절차

### 1. 무엇이 어떻게 지워졌는지 먼저 확인합니다

지운 방식에 따라 남는 것이 다릅니다. Claude Code 는 세션 기록과 그 하위 폴더를 기본 30일(`cleanupPeriodDays`) 뒤에 지우지만 `history.jsonl`·`stats-cache.json`·`backups/`·자동 메모는 날짜 기준으로 지우지 않고, `claude project purge` 는 그 프로젝트의 기록과 `history.jsonl` 의 해당 줄까지 지웁니다. 환경 변수 `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켰다면 처음부터 기록을 쓰지 않았으니 되살릴 것도 없습니다. Gemini CLI 는 기본 30일 보관에 `--delete-session` 으로 세션을 지울 수 있고, Codex CLI 는 `[history] persistence = "none"` 이면 입력 기록을 남기지 않습니다. 설정 파일에서 이런 값을 먼저 읽어 두면 "지웠다" 와 "처음부터 안 남았다" 를 가를 수 있습니다. 보관 규칙 전체는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

### 2. 도구 기록 안에 남은 사본을 찾습니다

기기에 원본을 두는 개발 도구는 한 대화를 여러 곳에 나눠 적어서, 본 기록이 지워져도 조각이 남는 경우가 있습니다. Claude Code 문서는 도구를 거친 파일 내용, 명령 출력, 붙여 넣은 글이 모두 디스크의 대화 기록에 쓰인다고 적고, 나눠 적는 곳은 아래와 같습니다.

| 위치(`~/.claude` 아래) | 담긴 것 | 남는 기간 |
|---|---|---|
| `projects/<프로젝트>/<세션>.jsonl` | 대화 전문(메시지, 도구 호출, 도구 결과) | `cleanupPeriodDays`(기본 30일) |
| `<세션>.jsonl.superseded-<시각>`, `<세션>.orphaned-<시각>-<접미사>.jsonl` | 덮어쓰기 전 이전 판, 떼어 둔 기록 | 세션 기록과 같이 정리 |
| `projects/<프로젝트>/<세션>/subagents/`, `.../tool-results/` | 하위 에이전트 대화, 따로 떼어 둔 큰 도구 출력 | 부모 기록과 함께 삭제 |
| `history.jsonl` | 입력한 프롬프트, 시각, 프로젝트 경로 | 지울 때까지 |
| `paste-cache/` | 긴 붙여넣기 내용 | `cleanupPeriodDays` |
| `image-cache/<세션>/` | v2.1.274 까지 저장한 첨부 이미지(그 뒤 판은 임시 폴더 아래 세션별 `images/`) | `cleanupPeriodDays` |
| `file-history/<세션>/` | Claude 가 고친 파일의 편집 전 사본(최근 체크포인트 100개) | `cleanupPeriodDays` |
| `feedback/drafts/`, `feedback-bundles/` | 피드백 초안, 서드파티 공급자를 쓸 때 보내지 않고 남긴 기록 압축본 | 초안은 최대 10개·30일 |
| `debug/<세션 ID>.txt` | `--debug`·`/debug` 로 켰을 때만 남는 디버그 로그 | `cleanupPeriodDays` |

이 PC 에서는 `history.jsonl` 의 `pastedContents.#` 아래에 붙여넣기 본문(`content`)이 있는 줄과 해시(`contentHash`)만 있는 줄이 섞여 있었습니다(확인 범위: Windows 11, 2026-09). 해시만 있는 줄이 `paste-cache/` 의 어느 파일과 이어지는지는 확인하지 못해서, 두 곳을 모두 수집하고 연결은 실제 파일로 검증합니다. 대화를 요약(`/compact`)해도 원래 메시지는 기록 파일에 그대로 남는다고 문서가 적고 있어, 화면에서 요약만 보였다는 진술과 파일 내용이 다를 수 있습니다. 세션 기록의 `attachment` 키는 사용자가 올린 첨부 파일이 아니라 훅 결과 같은 부가 정보를 담는 이름으로 보이니 첨부와 헷갈리지 않습니다. 기록 구조는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 페이지에 있습니다.

### 3. 앱 캐시를 살핍니다

데스크톱 채팅 앱은 대부분 Electron 이나 WebView2 위에서 돌아 브라우저와 같은 저장소를 씁니다. 관찰한 Claude 데스크톱(Windows 스토어 앱)의 패키지 폴더 아래 `LocalCache\Roaming\Claude` 에는 `Cache`, `Code Cache`, `IndexedDB`, `Local Storage\leveldb`, `File System`, `Network` 폴더가 있었습니다(확인 범위: Windows 11, 2026-09). 폴더가 있다는 사실과 그 안에 대화 내용이 있다는 사실은 다르고, 이 핸드북은 내용을 읽지 않아 뒤쪽을 확인하지 못했습니다. 그래서 캐시는 "대화가 있을 수도 있는 곳" 으로 두고 LevelDB·IndexedDB·Chromium 캐시를 읽는 일반 방법으로 살핍니다. 읽는 법은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)에 있습니다.

앱이 실행 중이면 파일이 잠겨 열리지 않을 수 있습니다. 관찰 때도 기본 `Network\Cookies` DB 가 OperationalError 로 열리지 않았으니, 복사본을 만들어 엽니다. 앱을 지운 뒤에도 캐시가 남는지는 앱 형식마다 다릅니다. WebView2 사용자 데이터 폴더는 Win32·.NET·WinUI 앱을 지워도 자동으로 지워지지 않고, 스토어 앱을 지우면 Windows 가 지웁니다. Electron 기반 스토어 앱의 `LocalCache` 가 앱 삭제 때 함께 지워지는지는 확인하지 못했습니다. 저장 구조의 공통 원리는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)에 있습니다.

### 4. 지운 파일과 지운 레코드를 찾습니다

JSONL 기록 파일이 통째로 지워졌다면 파일 시스템 쪽 복구 방법을 쓰고, 찾은 조각은 `sessionId`·`uuid`·`parentUuid` 같은 키로 어느 세션의 몇 번째 줄인지 이어 붙입니다. SQLite 를 쓰는 저장소(Cursor 의 `state.vscdb`, 쿠키 DB 등)는 레코드를 지워도 빈 페이지나 WAL 파일에 이전 내용이 남을 수 있어서, 원본 DB 와 `-wal`·`-journal` 파일을 함께 수집합니다. 읽는 법은 OS 별 SQLite 페이지([Windows](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html), [macOS](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/sqlite/index.html), [Android](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html), [iOS](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/sqlite/index.html))를 따릅니다.

### 5. 스냅숏을 봅니다

**Windows Recall.** Recall 스냅숏은 기기 안에만 있고 Microsoft 로 보내지 않아 서버 사본이 없습니다. 2025-04 이후 다시 설계한 판은 스냅숏을 암호화해서 디스크 이미지만으로 내용을 읽는 공식 경로가 없습니다. 암호화된 상태에서 쓸 수 있는 것은 폴더와 파일의 존재, 크기, 파일 시스템 시각이고, 유럽경제지역(EEA) 기기라면 사용자가 Windows Hello 인증을 거쳐 스냅숏을 내보내는 경로를 사용자 협조로 씁니다. 다만 관리 기기는 정책으로 내보내기가 기본으로 막혀 있습니다. 정책으로 Recall 이나 스냅숏 저장을 끄면 기존 스냅숏이 지워지니, 스냅숏이 없을 때는 정책 값도 확인합니다. 저장 위치, 보호 방식, 정책 이름은 [Recall](../../02-artifacts/windows-ai/recall.md)에 있습니다.

**Click to Do.** 화면 내용을 보관하지 않지만, 내용을 다른 앱으로 넘길 때 `C:\Users\{username}\AppData\Local\Temp` 에 임시 파일을 만든다고 문서가 적고 있습니다. 파일 이름 규칙은 확인하지 못했고, 흔적은 작업을 받은 앱 쪽을 먼저 찾아봅니다([클릭 투 두](../../02-artifacts/windows-ai/click-to-do.md)).

**파일 되돌리기 스냅숏.** Claude Code 는 사용자가 턴을 시작할 때마다 체크포인트를 만들고 편집 전 파일 사본을 `file-history/<세션>/` 에 둡니다. 오래된 체크포인트를 버려도 파일마다 첫 사본은 남긴다고 문서가 적어서, 에이전트가 바꾸기 전의 파일 내용을 되살리는 데 씁니다. 다만 Claude 의 편집 도구로 바꾼 파일만 추적하고, Bash 명령(rm, mv, cp 등)으로 바꾼 파일, 사람이 직접 바꾼 파일, 다른 세션의 편집, 대부분의 하위 에이전트 편집은 잡지 않습니다.

**브라우저 에이전트의 화면 기록.** Claude Code 를 Chrome 과 연결해 쓰면 브라우저 동작을 GIF 파일로 녹화할 수 있고, `save_to_disk` 옵션으로 스크린샷을 파일로 남길 수 있습니다(v2.1.211 부터 파일로 저장). 이 파일에는 로그인된 화면의 계정 정보까지 담기니 수집물을 다룰 때 조심합니다. 에이전트 쪽 흔적은 [브라우저를 조작하는 AI](../../02-artifacts/agentic-services/browser-agents.md)에 있습니다.

### 6. 알림은 시험 기기로 먼저 확인합니다

AI 앱이 OS 알림에 대화 내용을 미리 보기로 싣는지, 그 알림이 OS 알림 저장소에 남는지는 이 핸드북 조사에서 확인하지 못했습니다. 알림에 기대려면 같은 OS·같은 앱 버전을 시험 기기에 깔고, 알림 미리 보기 설정을 기록한 뒤 알림을 받아 어디에 무엇이 남는지 먼저 확인합니다. Claude Code 는 훅 이벤트에 `Notification` 이 있고 이 PC 의 사용자 설정에도 이 이벤트 키가 있었으니(확인 범위: Windows 11, 2026-09), 알림 훅이 부르는 스크립트가 따로 기록을 남기는지도 봅니다. 훅이 받는 값과 스크립트 동작은 설정마다 달라서 스크립트를 직접 읽어 확인합니다.

### 7. 서버 사본을 요청합니다

원본이 서버에 있는 서비스는 기기를 뒤지기보다 서버 사본을 받는 편이 빠릅니다. Claude 개인 계정에서 지운 대화는 목록에서 바로 사라지고 30일 안에 서버 저장소에서 지워지며, Gemini 앱은 활동 기록을 끈 상태의 대화와 임시 대화도 72시간 계정에 남습니다. 계정 주인이 협조하면 [계정 데이터 내보내기로 수집](../acquisition/export-collection.md)으로, 그렇지 않으면 [서비스 회사에 대한 데이터 요청](../acquisition/legal-requests.md)으로 가고, 보관 기간이 짧으니 요청을 서두릅니다. Claude Code Remote Control 세션은 연결된 동안 대화가 서버에도 저장되어, 기기 기록이 지워졌을 때 서버 쪽 사본을 찾아볼 근거가 됩니다.

조직 계정은 조직 서버에 사본이 있을 수 있습니다. Microsoft Purview 보존 정책을 쓰는 조직에서는 Copilot·AI 앱의 프롬프트와 응답이 사용자 메일함의 숨은 폴더에 복사되어 eDiscovery 로 찾을 수 있고, 사용자가 지운 뒤에도 `SubstrateHolds` 폴더에서 영구 삭제되기 전까지 찾을 수 있습니다([Microsoft Purview로 본 Copilot 기록](../../02-artifacts/network-enterprise/purview-copilot.md)). Claude Enterprise 감사 로그에는 대화 내용이 없고 식별자만 들어가서, 내용은 Primary Owner 의 데이터 내보내기로 받습니다([Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md)).

## OS 별 정리

| OS | 확인한 것 | 확인하지 못한 것 |
|---|---|---|
| Windows | Claude Code `%USERPROFILE%\.claude` 기록 구조, Claude 데스크톱 스토어 앱의 Electron 폴더(관찰), Recall·Click to Do 문서 | 채팅 앱 캐시 안 대화 내용, ChatGPT·Copilot 앱의 로컬 저장 위치 |
| macOS | Claude Code `~/.claude`(문서), ChatGPT 앱의 옛 평문 저장과 뒤이은 암호화(보도) | 지금 ChatGPT 앱의 저장 형식, Claude 데스크톱의 캐시 폴더 |
| Android | 없음 | 채팅 앱의 `/data/data` 아래 DB·캐시 |
| iOS | 없음 | 채팅 앱 컨테이너 안 파일, 백업 포함 여부 |

모바일에서 앱 데이터를 얻는 범위는 기기 암호화와 데이터 보호 등급에 달려 있고, 원리는 [Android 저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html), [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html), [iOS 데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)에 있습니다. macOS 앱의 암호 키가 키체인에 있다면 원리는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) 페이지를 봅니다.

## 도구

JSONL 기록과 조각은 `jq` 로 키를 골라 읽고, 깨진 줄은 문자열 검색 도구로 `sessionId` 나 `uuid` 값을 찾아 이어 붙입니다. SQLite 는 복사본을 `sqlite3` 로 열고 WAL 파일도 함께 봅니다. LevelDB·IndexedDB 는 위에 링크한 다른 판 페이지의 공개 도구를 씁니다. 도구 하나의 결과만 믿지 말고, 찾은 문자열이 원래 파일의 어느 위치에 있었는지 헥스 편집기로 한 번 확인해 두면 보고서에서 출처를 밝히기 쉽습니다.

## 함정과 한계

되살린 조각에는 앞뒤 맥락이 없는 경우가 많습니다. 조각만으로는 어느 세션, 어느 시각의 내용인지 알 수 없으니 `sessionId`·`uuid`·`timestamp` 같은 키가 함께 남아 있는지 확인하고, 남아 있지 않으면 "출처 세션 불명의 조각" 으로 적습니다.

대화 기록에는 비밀 값이 섞여 있을 수 있습니다. Claude Code 문서는 도구가 `.env` 파일을 읽거나 명령이 자격 증명을 출력하면 그 값이 대화 기록에 그대로 쓰인다고 적고, 기록은 저장할 때 암호화하지 않아 OS 파일 권한이 유일한 보호입니다. 같은 폴더의 `.credentials.json` 에는 `accessToken`·`refreshToken` 키가 있었으니(확인 범위: Windows 11, 2026-09), 수집한 사본을 원본과 같은 수준으로 보관합니다([API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)).

앱 버전이 결과를 가릅니다. ChatGPT macOS 앱은 2024-07 보도 뒤 저장 방식을 바꿨고 고친 버전 번호는 보도에 없으며, Claude Code 도 첨부 이미지 저장 위치를 v2.1.274 뒤로 바꿨습니다. 수집한 앱의 버전을 먼저 적고, 버전이 다르면 이 페이지의 위치를 그대로 믿지 않습니다.

서버에서 지운 대화가 기기 캐시에 남는지, 기기에서 지운 대화가 서버에 남는지는 서비스마다 다르고 이 핸드북에서 확인하지 못했습니다. 한쪽에서 찾지 못했다고 다른 쪽에도 없다고 쓰지 않습니다. Recall 처럼 암호화된 저장소를 푸는 일은 이 핸드북의 범위가 아닙니다.

## 결과를 어떻게 해석하나

되살린 내용으로는 "이 파일(또는 이 위치)에 이 글이 있었다" 까지만 말할 수 있습니다. 그 글이 서비스로 보내졌는지는 저장 위치의 성격에 따라 다릅니다. Claude Code 는 모든 프롬프트와 모델 출력을 서버로 보낸다고 문서가 적고 있어 대화 기록의 사용자 메시지는 송신과 이어 볼 근거가 되지만, 붙여넣기 캐시나 앱 캐시의 조각은 입력 중이던 글일 수도 있어 송신을 증명하지 못합니다. 편집 전 파일 사본은 에이전트가 파일을 바꾸기 전 내용을 보여 주지만, 누가 그 편집을 시켰는지는 대화 기록과 입력 기록으로 따로 가려야 합니다. 되살린 시각을 다른 흔적과 한 줄로 놓는 방법은 [AI 사용 타임라인](timeline.md)에 있습니다.

보고서 문장은 다음처럼 씁니다(만든 예시).

- 좋은 예: "`C:\Users\kim.sample\.claude\projects\` 아래 세션 파일의 이전 판(`.superseded` 이름이 붙은 파일)에서 `sessionId` 가 같은 사용자 메시지 3줄을 찾았고, 그 가운데 한 줄에 '2분기 단가표' 라는 글이 있습니다."
- 피할 예: "용의자가 지운 대화를 복구한 결과, 단가표를 AI 에 유출한 사실이 확인되었다."

## 참고 문헌

- Claude Code Docs — Explore the .claude directory. https://code.claude.com/docs/en/claude-directory
- Claude Code Docs — Checkpointing. https://code.claude.com/docs/en/checkpointing
- Claude Code Docs — Data usage. https://code.claude.com/docs/en/data-usage
- Claude Code Docs — Hooks reference. https://code.claude.com/docs/en/hooks
- Claude Code Docs — Use Claude Code with Chrome. https://code.claude.com/docs/en/chrome
- google-gemini/gemini-cli — docs/cli/session-management.md. https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/session-management.md
- OpenAI Codex — Advanced configuration. https://learn.chatgpt.com/docs/config-file/config-advanced
- somogyijanos/cursor-chat-export (GitHub, 2025-06-17 보관 처리). https://github.com/somogyijanos/cursor-chat-export
- 9to5Mac, "ChatGPT for Mac stored conversations in plain text" (2024-07-03). https://9to5mac.com/2024/07/03/chatgpt-macos-conversations-plain-text/
- Microsoft Learn — Manage user data folders (WebView2). https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/user-data-folder
- Microsoft Learn — Manage Recall for Windows clients. https://learn.microsoft.com/en-us/windows/client-management/manage-recall
- Microsoft Support — Privacy and control over your Recall experience. https://support.microsoft.com/en-us/windows/privacy-and-control-over-your-recall-experience-d404f672-7647-41e5-886c-a3c59680af15
- Microsoft Learn — Manage Click to Do for Windows clients. https://learn.microsoft.com/en-us/windows/client-management/manage-click-to-do
- Claude Privacy Center — How long do you store my data? https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
- Gemini Apps Help — Gemini Apps Privacy Hub. https://support.google.com/gemini/answer/13594961?hl=en
- Microsoft Learn — Learn about retention for Copilot and AI apps. https://learn.microsoft.com/en-us/purview/retention-policies-copilot
- Claude Help Center — How to access audit logs. https://support.claude.com/en/articles/9970975-how-to-access-audit-logs
