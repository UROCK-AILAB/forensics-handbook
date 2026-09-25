---
title: "대화 내용 되살리기"
parent: "기법 · 분석"
nav_order: 870
---

# 대화 내용 되살리기 (캐시·스냅숏·알림)

화면이나 목록에서 사라진 AI 대화를 기기에 남은 사본(도구 기록의 이전 판, 앱 로그, SQLite WAL, 앱 캐시, 스냅숏)과 서버에 남은 사본에서 다시 찾는 방법이며, 원본이 어디에 있는지부터 가려야 헛수고를 줄일 수 있습니다.

> 확인 날짜: 2026-09-25. Claude Code 의 폴더와 키 이름은 Windows 11 PC 한 대에서 관찰한 이름까지만 싣고 값은 싣지 않습니다(확인 범위: Windows 11, 2026-09). 로컬 LLM 앱은 LangurTrace 논문[1](Windows 11 Pro 24H2), 모바일 컴패니언 앱은 Ex Machina 논문[2](Android 12 에뮬레이터), Grok Android 는 ALEAPP 분석기[3]의 시험 결과를 근거로 씁니다. 잠금 해제나 암호화 우회, 남은 토큰으로 서버에 접근하는 방법은 다루지 않습니다.

## 언제 쓰나

사용자가 대화를 지웠거나, 자동 삭제로 기록이 사라졌거나, 앱 화면에 보이는 것보다 더 많은 내용을 확인해야 할 때 씁니다. 대화 원본이 서버에 있는 서비스와 기기에 있는 도구는 찾을 곳이 전혀 달라서, 아래 표로 먼저 갈래를 정합니다.

| 대상 | 대화 원본 | 기기에서 찾을 곳 |
|---|---|---|
| 웹·모바일 채팅 서비스(ChatGPT, Claude, Gemini, Copilot) | 서버 계정 | 앱·브라우저 캐시. 대화 내용이 캐시에 남는지는 공개된 분석 자료가 없어 검체로 확인해야 합니다 |
| ChatGPT macOS 앱 | 서버 계정 | 2024-07 보도 기준 옛 판은 `~/Library/Application Support/com.openai.chat` 에 대화를 평문으로 두었고, 그 뒤 판은 저장한 대화를 암호화함[4] |
| Claude Code(로컬 세션) | 기기, 평문 JSONL | 기록 파일과 그 이전 판, 입력 기록, 편집 전 파일 사본, 붙여넣기 캐시(아래 2단계) |
| Gemini CLI | 기기 `~/.gemini/tmp/` 아래 `chats/` | 세션 JSONL. 되감은 턴도 파일에 남음(아래 2단계) |
| Codex CLI | 기기 `~/.codex/` | 입력 기록 `history.jsonl`, 세션 기록 `sessions/` 아래 `rollout-*.jsonl`, 보관한 세션 `archived_sessions/`[5][6] |
| Cursor | 기기 `…/Cursor/User/globalStorage/state.vscdb` | SQLite 표 `cursorDiskKV` 의 `composerData:`·`bubbleId:` 키[6] |
| 로컬 LLM 앱(Ollama, Chatbox, LM Studio, Msty, Jan, GPT4All) | 기기 | 앱 로그, 설정 백업, 첨부 폴더(아래 3단계) |
| 모바일 컴패니언 앱(Replika, Persona.AI 등) | 앱마다 기기 또는 서버 | 앱 DB 의 WAL, Crashlytics 로그(아래 5·6단계) |
| Windows Recall | 기기에만 있음(2025-04 이후 판은 암호화) | 폴더·파일의 존재, 크기, 파일 시스템 시각 |

## 절차

### 1. 무엇이 어떻게 지워졌는지 먼저 확인합니다

지운 방식에 따라 남는 것이 다릅니다. Claude Code 는 세션 기록과 그 하위 폴더를 기본 30일(`cleanupPeriodDays`) 뒤에 지우지만 `history.jsonl`·`stats-cache.json`·`backups/`·자동 메모는 날짜 기준으로 지우지 않고, `claude project purge` 는 그 프로젝트의 기록과 `history.jsonl` 의 해당 줄까지 지웁니다. 환경 변수 `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켰다면 처음부터 기록을 쓰지 않았으니 되살릴 것도 없습니다. Gemini CLI 는 기본 30일 보관에 `--delete-session` 으로 세션을 지울 수 있고, Codex CLI 는 `[history] persistence = "none"` 이면 입력 기록을 남기지 않습니다. 설정 파일에서 이런 값을 먼저 읽어 두면 "지웠다" 와 "처음부터 안 남았다" 를 가를 수 있습니다. 보관 규칙 전체는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 있습니다.

앱 화면의 "삭제" 도 앱마다 하는 일이 다릅니다. Ex Machina 논문[2]에서 Linky.AI 는 대화를 지우면 새 대화 ID 만 만들고 원래 기록은 DB 에 그대로 두었고, Replika 는 계정을 지우면 주 DB 를 지웠습니다. 그래서 사용자가 어느 메뉴로 무엇을 지웠는지(메시지 하나, 대화 전체, 계정)를 먼저 적어 두고 그에 맞는 곳을 찾습니다.

### 2. 개발 도구 기록 안에 남은 사본을 찾습니다

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

세션 기록이 정리된 뒤에도 `history.jsonl` 은 남으므로, 이 파일의 `sessionId` 가운데 기록 파일이 없는 줄이 지워진 세션의 프롬프트입니다. claude-forensics 도구[7]는 이런 줄을 "orphan" 으로 모아 `orphan-prompts.jsonl` 로 내고, 보관 기간보다 오래된 대화에서는 이것이 유일하게 남은 기록인 경우가 많다고 적습니다. 다만 같은 도구 README(2026-06 기준)는 Windows 판 Claude Code 가 `history.jsonl`·`paste-cache/`·`file-history/` 를 쓰지 않는 것으로 보인다고 적었고, 이 핸드북이 관찰한 Windows 11 PC(2026-09)에는 `history.jsonl` 이 있었습니다. 판과 설정에 따라 다를 수 있으니 검체에 이 파일들이 있는지부터 봅니다.

관찰한 PC 에서는 `history.jsonl` 의 `pastedContents.#` 아래에 붙여넣기 본문(`content`)이 있는 줄과 해시(`contentHash`)만 있는 줄이 섞여 있었습니다(확인 범위: Windows 11, 2026-09). 해시와 `paste-cache/` 파일의 연결은 공개 문서에 없으니, 두 곳을 모두 수집하고 연결은 검체의 실제 파일로 확인합니다. 대화를 요약(`/compact`)해도 원래 메시지는 기록 파일에 그대로 남는다고 문서가 적고 있어, 화면에서 요약만 보였다는 진술과 파일 내용이 다를 수 있습니다. 기록 구조는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 페이지에 있습니다.

Gemini CLI 는 세션 파일에 줄을 덧붙이기만 합니다. 공개 소스(`chatRecordingService.ts`)[8]를 보면 대화를 되감을 때 앞선 메시지 줄을 지우지 않고 `{"$rewindTo": "<메시지 id>"}` 줄을 하나 덧붙이며, 불러올 때 그 id 부터 뒤의 메시지를 빼고 보여 줍니다. 그래서 화면에서 사라진 턴도 파일을 직접 읽으면 나옵니다. 세션 파일의 칸은 [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md)에 있습니다.

### 3. 로컬 LLM 앱은 앱이 남긴 로그와 백업을 봅니다

로컬 LLM 앱은 화면에서 지운 대화가 본 저장소에서는 사라져도 로그, 설정 백업, 첨부 폴더에 남는 경우가 있습니다. LangurTrace 논문[1]은 Windows 11 Pro 24H2(빌드 26100.3775)에서 Ollama 0.6.5, Chatbox 1.11.8, LM Studio 0.3.14, Msty 1.8.5, Jan 0.5.16, GPT4All 3.10.0 을 시험했고(표 1), 앱 화면에서 지운 뒤 LangurTrace 로 되살린 비율을 표 8 로 냈습니다.

| 앱 | 모델 다운로드 | 대화 | 올린 파일 | 생성 파일 |
|---|---|---|---|---|
| Ollama | 100%(5/5) | – | – | – |
| Chatbox | – | 58%(29/50) | 100%(50/50) | 100%(50/50) |
| LM Studio | 100%(5/5) | 0%(0/50) | 0%(0/50) | – |
| Msty | 100%(5/5) | 0%(0/50) | 100%(50/50) | – |
| Jan | 100%(5/5) | 100%(50/50) | – | – |
| GPT4All | 0%(0/5) | 0%(0/50) | – | – |

(출처: LangurTrace 논문 표 8. 괄호는 지운 개수 가운데 되살린 개수, "–" 는 그 기능이 없거나 시험하지 않은 항목)

되살린 내용이 나온 곳은 앱마다 다릅니다(논문 §4.4~§5.3, 부록 A). Ollama 는 모델을 지워도 `%LocalAppData%/Ollama/server.log` 의 다운로드 기록에 시각, 모델 이름, manifest 정보가 남습니다. Chatbox 는 `%AppData%/xyz.chatboxapp.app/config.json` 의 백업 사본을 만들고 지우는데 백업 간격이 일정하지 않아 대화는 일부만 되살아났고, 올린 파일과 만든 파일은 `chatbox-blobs/` 에 그대로 남았습니다. LM Studio 는 `%UserProfile%/.lmstudio/.internal/download-jobs-info.json` 에 모델 이름·다운로드 URL·SHA-256 이 남지만 지운 대화와 올린 파일은 흔적이 없었습니다. Msty 는 `%AppData%/Msty/logs/app.log` 에 모델 설정 기록이, `%AppData%/Msty/attachments/` 에 메시지를 지운 뒤에도 올린 파일이 남았습니다. Jan 은 엔진 로그 `cortex.log` 에 대화 요청 본문과 모델 받기 기록이 남아 지운 대화가 모두 나왔습니다. GPT4All 은 지운 뒤 되살린 것이 없었습니다. 파일 안의 칸과 시각 형식은 [Ollama](../../02-artifacts/local-ai/ollama.md), [Chatbox](../../02-artifacts/local-ai/chatbox.md), [LM Studio](../../02-artifacts/local-ai/lm-studio.md), [Msty](../../02-artifacts/local-ai/msty.md), [Jan](../../02-artifacts/local-ai/jan.md), [GPT4All](../../02-artifacts/local-ai/gpt4all.md) 페이지에 있습니다.

이 표는 디스크에 남은 파일에서 도구로 되살린 결과만 잽니다. 논문은 볼륨 섀도 복사본(VSC)과 실행 중 메모리를 시험하지 않았고, SQLite·LevelDB 저장소는 slack 영역이나 freelist·WAL 카빙으로 더 건질 수 있다고 적었습니다(§6.2). 그래서 표의 0% 는 "그 방법으로는 나오지 않았다" 로 읽고, 아래 5단계의 방법을 더 써 봅니다. 2026-05 에 올라온 LangurTrace 후속 구현 문서[9]는 Jan 과 Msty 가 그 뒤 저장 형식을 바꿨다고 적었으니, 검체의 앱 판이 표 1 과 다르면 경로부터 다시 확인합니다.

### 4. 앱 캐시를 살핍니다

데스크톱 채팅 앱은 대부분 Electron 이나 WebView2 위에서 돌아 브라우저와 같은 저장소를 씁니다. 관찰한 Claude 데스크톱(Windows 스토어 앱)의 패키지 폴더 아래 `LocalCache\Roaming\Claude` 에는 `Cache`, `Code Cache`, `IndexedDB`, `Local Storage\leveldb`, `File System`, `Network` 폴더가 있었습니다(확인 범위: Windows 11, 2026-09). 폴더가 있다는 사실과 그 안에 대화 내용이 있다는 사실은 다르므로, 캐시는 "대화가 있을 수도 있는 곳" 으로 두고 LevelDB·IndexedDB·Chromium 캐시를 읽는 일반 방법으로 살핍니다. 읽는 법은 [LevelDB 저장소](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/leveldb.html)와 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html)에 있습니다.

앱이 실행 중이면 파일이 잠겨 열리지 않을 수 있습니다. 관찰 때도 기본 `Network\Cookies` DB 가 OperationalError 로 열리지 않았으니, 복사본을 만들어 엽니다. 앱을 지운 뒤에도 캐시가 남는지는 앱 형식마다 다릅니다. WebView2 사용자 데이터 폴더는 Win32·.NET·WinUI 앱을 지워도 자동으로 지워지지 않고, 스토어 앱을 지우면 Windows 가 지웁니다. Electron 기반 스토어 앱의 `LocalCache` 가 앱 삭제 때 함께 지워지는지는 공개 문서에 없어 검체로 확인해야 합니다. 저장 구조의 공통 원리는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)에 있습니다.

### 5. 지운 파일과 지운 레코드를 찾습니다

JSONL 기록 파일이 통째로 지워졌다면 파일 시스템 쪽 복구 방법을 쓰고, 찾은 조각은 `sessionId`·`uuid`·`parentUuid` 같은 키로 어느 세션의 몇 번째 줄인지 이어 붙입니다.

SQLite 를 쓰는 저장소는 레코드를 지워도 빈 페이지나 WAL 파일에 이전 내용이 남을 수 있어서, 원본 DB 와 `-wal`·`-shm`·`-journal` 파일을 함께 수집합니다. Ex Machina 논문[2]에서 Persona.AI 와 Fantasy.AI 는 대화를 지우면 주 DB `ai_personal_db` 에서 행이 빠졌지만 내용이 `ai_personal_db-wal` 에 남았고, 앱 데이터를 모두 지운 뒤에도 WAL 파일에서 지운 대화를 되살릴 수 있었습니다(§4.7). SQLite 문서[10]는 체크포인트가 WAL 파일을 보통 자르지 않고 앞에서부터 덮어쓴다고 적어서, 덮어쓰이기 전의 옛 프레임이 파일에 남을 수 있습니다.

같은 문서는 마지막 연결이 닫힐 때 SQLite 가 마지막 체크포인트를 하고 WAL 과 공유 메모리 파일을 지운다고 적습니다. 그래서 수집한 DB 를 `sqlite3` 로 바로 열었다 닫으면 WAL 안의 옛 내용이 주 DB 에 합쳐지고 WAL 사본이 사라질 수 있습니다. 손대지 않은 `-wal` 사본을 따로 두고, 프레임을 직접 읽는 방법은 OS 별 SQLite 페이지([Windows](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html), [macOS](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/data-formats/sqlite/index.html), [Android](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html), [iOS](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/data-formats/sqlite/index.html))를 따릅니다.

캐시 DB 에만 남은 기록도 지운 파일의 흔적이 됩니다. ALEAPP 의 Grok 분석기[3](Grok Android 1.0.71, 2025-11-11 판에서 시험, 2026-08-01 갱신)는 `ai.x.grok/cache/*/video-cache/*/` 의 `.exo` 캐시 파일과 `ai.x.grok/databases/exoplayer_internal.db` 를 함께 읽습니다. DB 의 `ExoPlayerCacheFileMetadata*` 표에는 캐시 파일 `name`·`length`·`last_touch_timestamp`(ms) 가, `ExoPlayerCacheIndex*` 표에는 캐시 `id` 와 원래 URL(`key`)이 있습니다. 캐시 파일 이름은 `7.0.1760000000000.v3.exo`(만든 예시)처럼 생겼고, 첫 칸이 캐시 ID, 셋째 칸이 ms 단위 Unix 시각이며 분석기는 이를 UTC 로 바꿉니다. 분석기는 URL 이 `https://assets.grok.com/users/` 로 시작하면 사용자가 만든 영상(User Generated)으로, 나머지는 공개 영상(Public)으로 나누고, DB 에는 있는데 파일이 없는 항목을 `Cache Video` 칸에 "Not Present" 로 적습니다. 이 항목은 파일은 사라졌지만 그 URL 의 영상이 한때 캐시에 있었다는 기록입니다. 서비스별 나머지 흔적은 [그 밖의 서비스](../../02-artifacts/chat-services/other-services.md)에 있습니다.

### 6. 모바일 앱의 충돌 로그를 봅니다

앱이 쓰는 충돌 보고 SDK 의 로그에 대화가 남는 경우가 있습니다. Ex Machina 논문[2]에서 Replika 는 계정을 지우자 주 DB(`databases/REPLIKA_DB`)가 기기에서 지워졌지만, Firebase Crashlytics 로그 파일의 `userlog` 하위 폴더에서 대화 전체를 되살릴 수 있었습니다(§4.7). 논문은 이 폴더의 전체 경로를 적지 않았으니, 수집한 앱 데이터 폴더 전체에서 `userlog` 폴더를 찾습니다. 논문의 시험 환경은 루팅한 Android 12(API 31) 에뮬레이터였고, `/data/data` 전체를 tar 로 묶어 논리 이미지를 떴습니다(§3.3). 앱 판은 논문에 없어서 검체의 앱 판을 따로 적어 둡니다. 앱별 DB 와 패키지 이름은 [AI 컴패니언 앱](../../02-artifacts/chat-services/companion-apps.md)에 있습니다.

모바일에서 앱 데이터를 얻는 범위는 기기 암호화와 데이터 보호 등급에 달려 있고, 원리는 [Android 저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/encryption/index.html), [Android 앱 데이터 폴더 구조](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/storage/app-data-layout.html), [iOS 데이터 보호](https://urock-ailab.github.io/forensics-handbook-ios/01-foundations/storage/data-protection/index.html)에 있습니다. macOS 앱의 암호 키가 키체인에 있다면 원리는 [키체인](https://urock-ailab.github.io/forensics-handbook-mac/01-foundations/protection/keychain/index.html) 페이지를 봅니다.

### 7. 스냅숏을 봅니다

**Windows Recall.** Recall 스냅숏은 기기 안에만 있고 Microsoft 로 보내지 않아 서버 사본이 없습니다. 2025-04 이후 다시 설계한 판은 스냅숏을 암호화해서 디스크 이미지만으로 내용을 읽는 공식 경로가 없습니다. 암호화된 상태에서 쓸 수 있는 것은 폴더와 파일의 존재, 크기, 파일 시스템 시각이고, 유럽경제지역(EEA) 기기라면 사용자가 Windows Hello 인증을 거쳐 스냅숏을 내보내는 경로를 사용자 협조로 씁니다. 다만 관리 기기는 정책으로 내보내기가 기본으로 막혀 있습니다. 정책으로 Recall 이나 스냅숏 저장을 끄면 기존 스냅숏이 지워지니, 스냅숏이 없을 때는 정책 값도 확인합니다. 저장 위치, 보호 방식, 정책 이름은 [Recall](../../02-artifacts/windows-ai/recall.md)에 있습니다.

**Click to Do.** 화면 내용을 보관하지 않지만, 내용을 다른 앱으로 넘길 때 `C:\Users\{username}\AppData\Local\Temp` 에 임시 파일을 만든다고 문서가 적고 있습니다. 파일 이름 규칙은 공개 문서에 없어서, 흔적은 작업을 받은 앱 쪽을 먼저 찾아봅니다([클릭 투 두](../../02-artifacts/windows-ai/click-to-do.md)).

**파일 되돌리기 스냅숏.** Claude Code 는 사용자가 턴을 시작할 때마다 체크포인트를 만들고 편집 전 파일 사본을 `file-history/<세션>/` 에 둡니다. 오래된 체크포인트를 버려도 파일마다 첫 사본은 남긴다고 문서가 적어서, 에이전트가 바꾸기 전의 파일 내용을 되살리는 데 씁니다. 다만 Claude 의 편집 도구로 바꾼 파일만 추적하고, Bash 명령(rm, mv, cp 등)으로 바꾼 파일, 사람이 직접 바꾼 파일, 다른 세션의 편집, 대부분의 하위 에이전트 편집은 잡지 않습니다.

**브라우저 에이전트의 화면 기록.** Claude Code 를 Chrome 과 연결해 쓰면 브라우저 동작을 GIF 파일로 녹화할 수 있고, `save_to_disk` 옵션으로 스크린샷을 파일로 남길 수 있습니다(v2.1.211 부터 파일로 저장). 이 파일에는 로그인된 화면의 계정 정보까지 담기니 수집물을 다룰 때 조심합니다. 에이전트 쪽 흔적은 [브라우저를 조작하는 AI](../../02-artifacts/agentic-services/browser-agents.md)에 있습니다.

### 8. 알림은 시험 기기로 먼저 확인합니다

AI 앱이 OS 알림에 대화 내용을 미리 보기로 싣는지, 그 알림이 OS 알림 저장소에 남는지는 공개된 분석 자료가 없어 검체나 시험 기기로 확인해야 합니다. 같은 OS·같은 앱 판을 시험 기기에 깔고, 알림 미리 보기 설정을 기록한 뒤 알림을 받아 어디에 무엇이 남는지 먼저 봅니다. Claude Code 는 훅 이벤트에 `Notification` 이 있고 관찰한 PC 의 사용자 설정에도 이 이벤트 키가 있었으니(확인 범위: Windows 11, 2026-09), 알림 훅이 부르는 스크립트가 따로 기록을 남기는지도 봅니다. 훅이 받는 값과 스크립트 동작은 설정마다 달라서 스크립트를 직접 읽어 확인합니다.

### 9. 서버 사본을 요청합니다

원본이 서버에 있는 서비스는 기기를 뒤지기보다 서버 사본을 받는 편이 빠릅니다. Claude 개인 계정에서 지운 대화는 목록에서 바로 사라지고 30일 안에 서버 저장소에서 지워지며, Gemini 앱은 활동 기록을 끈 상태의 대화와 임시 대화도 72시간 계정에 남습니다. 계정 주인이 협조하면 [계정 데이터 내보내기로 수집](../acquisition/export-collection.md)으로, 그렇지 않으면 [서비스 회사에 대한 데이터 요청](../acquisition/legal-requests.md)으로 가고, 보관 기간이 짧으니 요청을 서두릅니다. Claude Code Remote Control 세션은 연결된 동안 대화가 서버에도 저장되어, 기기 기록이 지워졌을 때 서버 쪽 사본을 찾아볼 근거가 됩니다.

대화를 서버에만 두는 컴패니언 앱은 계정을 지우면 서버에서도 사라질 수 있습니다. Ex Machina 논문[2]에서 Kindroid 는 계정 삭제 뒤 서버의 대화에 더는 닿지 않았고, Character.AI 는 지운 메시지가 서버 응답에서 빠졌습니다. 논문은 Character.AI 서버의 백업이나 로그에서까지 지워졌는지는 알 수 없다고 적었으니, 이런 앱은 서비스 회사에 보존과 제출을 요청하는 쪽으로 갑니다. 기기에 남은 인증 토큰은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)에 적힌 대로 위치만 기록하고 보고서에서 가립니다.

조직 계정은 조직 서버에 사본이 있을 수 있습니다. Microsoft Purview 보존 정책을 쓰는 조직에서는 Copilot·AI 앱의 프롬프트와 응답이 사용자 메일함의 숨은 폴더에 복사되어 eDiscovery 로 찾을 수 있고, 사용자가 지운 뒤에도 `SubstrateHolds` 폴더에서 영구 삭제되기 전까지 찾을 수 있습니다([Microsoft Purview로 본 Copilot 기록](../../02-artifacts/network-enterprise/purview-copilot.md)). Claude Enterprise 감사 로그에는 대화 내용이 없고 식별자만 들어가서, 내용은 Primary Owner 의 데이터 내보내기로 받습니다([Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md)).

## 도구

JSONL 기록과 조각은 `jq` 로 키를 골라 읽고, 깨진 줄은 문자열 검색 도구로 `sessionId` 나 `uuid` 값을 찾아 이어 붙입니다. SQLite 는 손대지 않은 원본 사본을 따로 두고 작업 사본을 `sqlite3` 로 열며, WAL 은 5단계처럼 따로 읽습니다. LevelDB·IndexedDB 는 위에 링크한 다른 판 페이지의 공개 도구를 씁니다.

AI 앱 전용 공개 도구는 아래와 같습니다. 모두 시험한 판이 정해져 있어 지금 판에서는 경로가 다를 수 있습니다.

| 도구 | 대상 | 시험한 판 |
|---|---|---|
| LangurTrace[11] | Ollama, Chatbox, LM Studio, Msty, Jan, GPT4All. KAPE 타깃으로 모으고 KAPE 모듈(`LangurTrace.exe`, Python 소스 공개)로 풀어 대화는 세션별 HTML, 설정은 CSV·XLSX 로 냄 | 논문 표 1 의 판(2025-02~04 배포), Windows 11 Pro 24H2 |
| ALEAPP `Grok.py`[3] | Grok Android 의 영상 캐시와 계정 설정 | Grok 1.0.71(2025-11-11) |
| claude-forensics[7] | Claude Code·Claude 데스크톱 폴더, 지워진 세션의 프롬프트(`orphan-prompts.jsonl`) | v0.1.1(2026-06-16 커밋) |

도구 하나의 결과만 믿지 말고, 찾은 문자열이 원래 파일의 어느 위치에 있었는지 헥스 편집기로 한 번 확인해 두면 보고서에서 출처를 밝히기 쉽습니다.

## 함정과 한계

되살린 조각에는 앞뒤 맥락이 없는 경우가 많습니다. 조각만으로는 어느 세션, 어느 시각의 내용인지 알 수 없으니 `sessionId`·`uuid`·`timestamp` 같은 키가 함께 남아 있는지 확인하고, 남아 있지 않으면 "출처 세션 불명의 조각" 으로 적습니다.

캐시 시각은 사용자가 본 시각이 아닙니다. ALEAPP Grok 분석기는 앱이 LRU 가 아닌 캐시 정리 방식을 쓰면 `last_touch_timestamp` 가 전혀 갱신되지 않고, LRU 여도 사용자가 본 때가 아니라 캐시를 읽은 때 갱신된다고 적었습니다[3]. "Not Present" 항목도 캐시 정리로 파일이 지워졌을 수 있어서, 그것만으로 사용자가 지웠다고 쓰지 않습니다.

대화 기록에는 비밀 값이 섞여 있을 수 있습니다. Claude Code 문서는 도구가 `.env` 파일을 읽거나 명령이 자격 증명을 출력하면 그 값이 대화 기록에 그대로 쓰인다고 적고, 기록은 저장할 때 암호화하지 않아 OS 파일 권한이 유일한 보호입니다. 같은 폴더의 `.credentials.json` 에는 `accessToken`·`refreshToken` 키가 있었고(확인 범위: Windows 11, 2026-09), Jan 의 `cortex.log` 에는 등록한 API 키가 평문으로 남습니다[1]. 수집한 사본은 원본과 같은 수준으로 보관하고 보고서에서는 값을 가립니다([API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)).

앱 판이 결과를 가릅니다. ChatGPT macOS 앱은 2024-07 보도 뒤 저장 방식을 바꿨고 고친 판 번호는 보도에 없으며, Claude Code 도 첨부 이미지 저장 위치를 v2.1.274 뒤로 바꿨습니다. 수집한 앱의 판을 먼저 적고, 판이 다르면 이 페이지의 위치를 그대로 믿지 않습니다.

이 페이지의 방법은 모두 디스크에 남은 것을 다룹니다. 앱이 실행 중인 기기라면 전원을 끄기 전에 메모리를 먼저 확보할지 정해야 하고, 방법은 [메모리에서 AI 흔적 찾기](memory-analysis.md)에 있습니다. 한쪽(기기 또는 서버)에 없다는 사실만으로 다른 쪽에도 없다고 쓰지 않습니다. Recall 처럼 암호화된 저장소를 푸는 일은 이 핸드북의 범위가 아닙니다.

## 결과를 어떻게 해석하나

되살린 내용으로는 "이 파일(또는 이 위치)에 이 글이 있었다" 까지만 말할 수 있습니다. 그 글이 서비스로 보내졌는지는 저장 위치의 성격에 따라 다릅니다. Claude Code 는 모든 프롬프트와 모델 출력을 서버로 보낸다고 문서가 적고 있어 대화 기록의 사용자 메시지는 송신과 이어 볼 근거가 되지만, 붙여넣기 캐시나 앱 캐시의 조각은 입력 중이던 글일 수도 있어 송신을 증명하지 못합니다. 로컬 LLM 앱의 로그에 남은 대화는 기기 안의 모델과 주고받은 기록일 수 있어, 외부 서비스로 보냈다는 뜻이 아닙니다. 편집 전 파일 사본은 에이전트가 파일을 바꾸기 전 내용을 보여 주지만, 누가 그 편집을 시켰는지는 대화 기록과 입력 기록으로 따로 가려야 합니다.

WAL 이나 충돌 로그에서 되살린 대화는 "사용자가 지운 뒤에도 남아 있었다" 까지는 말하지만, 언제 지웠는지는 따로 말해 주지 않습니다. 지운 시각이 필요하면 파일 시스템 시각과 앱 로그를 함께 놓고, 되살린 시각을 다른 흔적과 한 줄로 놓는 방법은 [AI 사용 타임라인](timeline.md)에 있습니다.

보고서 문장은 다음처럼 씁니다(만든 예시).

- 좋은 예: "`C:\Users\kim.sample\.claude\projects\` 아래 세션 파일의 이전 판(`.superseded` 이름이 붙은 파일)에서 `sessionId` 가 같은 사용자 메시지 3줄을 찾았고, 그 가운데 한 줄에 '2분기 단가표' 라는 글이 있습니다."
- 좋은 예: "앱 DB 에서는 해당 대화 행이 없었으나, 같은 폴더의 `-wal` 파일에서 같은 대화 ID 를 가진 메시지 12건을 찾았습니다."
- 피할 예: "용의자가 지운 대화를 복구한 결과, 단가표를 AI 에 유출한 사실이 확인되었다."

## 참고 문헌

1. Jeong, S., Lee, S., Park, J. "LangurTrace: Forensic analysis of local LLM applications." Forensic Science International: Digital Investigation 54 (2025) 301987. https://doi.org/10.1016/j.fsidi.2025.301987
2. Comeaux, K.J., Spinosa, T.T., Ghosn, A., Baggili, I. "Ex Machina: A forensic evaluation of AI companion applications and their evidentiary value." Forensic Science International: Digital Investigation 56 (2026) 302050 (DFRWS EU 2026). https://doi.org/10.1016/j.fsidi.2026.302050
3. abrignoni/ALEAPP — `scripts/artifacts/Grok.py`(Damien Attoe, 2025-11-14 작성, 2026-08-01 갱신). https://github.com/abrignoni/ALEAPP
4. 9to5Mac, "ChatGPT for Mac stored conversations in plain text" (2024-07-03). https://9to5mac.com/2024/07/03/chatgpt-macos-conversations-plain-text/
5. OpenAI Codex — Advanced configuration. https://learn.chatgpt.com/docs/config-file/config-advanced
6. kenn-io/agentsview — `internal/parser/discovery.go`, `internal/parser/cursor_ide.go`(2026-09-25 push 기준). https://github.com/kenn-io/agentsview
7. forensicdave/claude-forensics — `README.md`(v0.1.1, 2026-06-16 커밋). https://github.com/forensicdave/claude-forensics
8. google-gemini/gemini-cli — `packages/core/src/services/chatRecordingService.ts`(커밋 acae712). https://github.com/google-gemini/gemini-cli
9. k0w4lzk1/LangurTrace-Implementation — `GAPS.md`(2026-05-08 커밋). https://github.com/k0w4lzk1/LangurTrace-Implementation
10. SQLite — Write-Ahead Logging. https://sqlite.org/wal.html
11. jeongramon/LangurTrace. https://github.com/jeongramon/LangurTrace
12. Claude Code Docs — Explore the .claude directory. https://code.claude.com/docs/en/claude-directory
13. Claude Code Docs — Checkpointing. https://code.claude.com/docs/en/checkpointing
14. Claude Code Docs — Data usage. https://code.claude.com/docs/en/data-usage
15. Claude Code Docs — Hooks reference. https://code.claude.com/docs/en/hooks
16. Claude Code Docs — Use Claude Code with Chrome. https://code.claude.com/docs/en/chrome
17. google-gemini/gemini-cli — docs/cli/session-management.md. https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/session-management.md
18. Microsoft Learn — Manage user data folders (WebView2). https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/user-data-folder
19. Microsoft Learn — Manage Recall for Windows clients. https://learn.microsoft.com/en-us/windows/client-management/manage-recall
20. Microsoft Support — Privacy and control over your Recall experience. https://support.microsoft.com/en-us/windows/privacy-and-control-over-your-recall-experience-d404f672-7647-41e5-886c-a3c59680af15
21. Microsoft Learn — Manage Click to Do for Windows clients. https://learn.microsoft.com/en-us/windows/client-management/manage-click-to-do
22. Claude Privacy Center — How long do you store my data? https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
23. Gemini Apps Help — Gemini Apps Privacy Hub. https://support.google.com/gemini/answer/13594961?hl=en
24. Microsoft Learn — Learn about retention for Copilot and AI apps. https://learn.microsoft.com/en-us/purview/retention-policies-copilot
25. Claude Help Center — How to access audit logs. https://support.claude.com/en/articles/9970975-how-to-access-audit-logs
