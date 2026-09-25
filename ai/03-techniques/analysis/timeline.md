---
title: "AI 사용 타임라인"
parent: "기법 · 분석"
nav_order: 780
---

# AI 사용 타임라인 (Timeline)

AI 도구가 기기와 서버, 네트워크에 남긴 시각을 모아 UTC 기준 한 줄로 늘어놓고, 시각마다 무슨 일이 있을 때 바뀌는 값인지를 옆에 적어 두는 분석 방법입니다.

> 확인 날짜: 2026-09. 기기 쪽 파일 이름과 키 이름은 Windows 11 PC 한 대의 AI 도구 폴더를 읽기 전용으로 열어 확인했고, 값은 가려 두어서 보지 않았습니다(확인 범위: Windows 11, 2026-09). 그래서 그 PC 에 깔린 앱 버전과 시각 값의 실제 형식은 확인하지 못했습니다. Claude Code 의 버전 번호는 공식 문서에 적힌 "이 버전부터/까지" 문장을 옮긴 것입니다. macOS·Android·iOS 는 기기에서 본 것 없이 문서 근거만 씁니다.

## 언제 쓰나

"그 사람이 언제 AI 를 썼고, 그 앞뒤로 무슨 일이 있었나" 를 물을 때 씁니다. 기밀 파일을 연 시각과 AI 에 내용을 붙여 넣은 시각이 가까운지 보거나, 에이전트가 명령을 실행한 시각과 디스크의 파일이 바뀐 시각을 맞춰 보는 일이 대표적입니다. OS 전체 타임라인을 만드는 일반 방법은 OS 별 판의 타임라인 페이지([Windows](https://urock-ailab.github.io/forensics-handbook-windows/03-techniques/analysis/timeline/index.html), [macOS](https://urock-ailab.github.io/forensics-handbook-mac/03-techniques/analysis/timeline/index.html), [Android](https://urock-ailab.github.io/forensics-handbook-android/03-techniques/analysis/timeline/index.html), [iOS](https://urock-ailab.github.io/forensics-handbook-ios/03-techniques/analysis/timeline/index.html))에 있고, 이 페이지는 그 위에 AI 흔적을 얹는 부분만 다룹니다.

## 절차

### 1. 시간대와 기준을 먼저 적습니다

기기의 시간대 설정과 수집 시각을 먼저 적고, 타임라인의 기준은 UTC 로 정합니다. 기록마다 UTC 로 적는 것과 현지 시각으로 적는 것이 섞여 있고 형식을 확인하지 못한 값도 있어서, 바꾼 값 옆에 원래 값과 원래 표기를 그대로 남겨 둡니다. Sysmon 이벤트 로그는 시각을 UTC 로 적고, Chromium 쿠키 DB 는 `creation_utc`·`last_access_utc` 처럼 칸 이름에 `_utc` 가 붙어 있습니다. 쿠키 시각 값을 사람이 읽는 시각으로 바꾸는 법은 [크롬 계열 브라우저](https://urock-ailab.github.io/forensics-handbook-windows/02-artifacts/browsers/chrome-edge-whale/index.html) 페이지를 따릅니다.

### 2. 대화 원본이 어디에 있는지 가릅니다

타임라인에 넣을 수 있는 시각은 대화 원본이 어디에 있느냐에 따라 달라집니다. 원본이 서버에만 있으면 기기에는 접속 흔적만 남고, 대화 시각은 계정 내보내기나 사업자 요청으로 얻어야 합니다. 원리는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 있습니다.

| 갈래 | 예 | 대화 시각을 얻는 곳 |
|---|---|---|
| 원본이 서버에만 있음 | 웹·모바일 채팅 서비스(ChatGPT, Claude, Gemini, Copilot), 웹에서 돌린 Claude Code 클라우드 세션 | [계정 데이터 내보내기로 수집](../acquisition/export-collection.md), [서비스 회사에 대한 데이터 요청](../acquisition/legal-requests.md). 기기에는 브라우저·앱 접속 흔적만 |
| 원본이 기기에 있음 | Claude Code 로컬 세션, Gemini CLI 세션, Codex CLI 입력 기록 | 기기의 기록 파일 |
| 양쪽에 있음 | Claude Code Remote Control 세션(실행은 기기, 연결된 동안 서버에도 저장) | 기기 기록과 서버 사본을 서로 맞춰 봄 |
| 조직 서버에 있음 | Claude Enterprise 감사 로그(내보내기 범위는 최근 180일), Microsoft Purview 감사 | 조직 관리자에게 요청. PC 이미지에는 없음 |

### 3. 출처마다 시각 칸을 뽑습니다

**Claude Code.** 데이터 폴더는 Windows 에서 `%USERPROFILE%\.claude`, macOS·Linux 에서 `~/.claude` 이고, 환경 변수 `CLAUDE_CONFIG_DIR` 를 두면 다른 곳으로 옮겨 가서 기본 위치에 없으면 이 변수부터 확인합니다. 파일별 시각 칸은 아래와 같습니다.

| 파일 | 시각 칸 | 뜻과 근거 |
|---|---|---|
| `history.jsonl` | `timestamp`(정수) | 입력한 프롬프트마다 시각과 프로젝트 경로를 한 줄씩 남기고, 날짜 기준 자동 삭제 대상이 아닙니다(문서). 정수의 단위는 확인하지 못했습니다 |
| `projects/<프로젝트>/<세션>.jsonl` | 줄마다 `timestamp`(문자열) | 메시지, 도구 호출, 도구 결과를 줄로 쌓는 대화 전문입니다(문서). 문자열에 시간대 표기가 붙는지는 확인하지 못했습니다 |
| 같은 파일의 스냅숏 줄 | `snapshot.timestamp` | 파일 되돌리기 체크포인트 줄로 보이고, 문서는 사용자가 프롬프트를 보내 턴을 시작할 때마다 체크포인트를 만든다고 적습니다 |
| `jobs/<이름>/state.json`, `jobs/<이름>/timeline.jsonl` | `createdAt`·`updatedAt`, `at` | 백그라운드 작업의 상태 변화로 보이지만 뜻은 문서로 확인하지 못했습니다 |
| `feedback/drafts/<파일>.json` | `created_at` | 피드백 초안을 만든 시각으로 보입니다 |
| `stats-cache.json` | `firstSessionDate`, `dailyActivity[].date`, `hourCounts`, `longestSession.timestamp` | 날짜별 메시지·세션·도구 호출 수를 모은 집계이고 내용은 없습니다. 날짜를 어느 시간대 기준으로 자르는지는 확인하지 못했습니다 |

위 표의 키 이름은 모두 관찰로 확인했습니다(확인 범위: Windows 11, 2026-09). 세션 기록은 이전 판을 `<세션>.jsonl.superseded-<시각>`, 떼어 둔 기록을 `<세션>.orphaned-<시각>-<접미사>.jsonl` 로 남기기도 해서, 파일 이름 안의 시각도 함께 적어 둡니다.

**Claude 데스크톱(Windows 스토어 앱).** 패키지 폴더 아래 `LocalCache\Roaming\Claude` 에 Electron 모양 폴더와 앱 설정 JSON 이 있고, 그 가운데 시각으로 보이는 칸은 `config.json` 의 `first_launch_at`·`version_first_launch.at`, `plan-usage-history.json` 의 `samples[].t` 입니다. 같은 패키지의 `LocalCache\Local\claude-cli-nodejs\Cache\` 아래 `mcp-logs-<서버 이름>` 폴더의 JSONL 에는 줄마다 `timestamp` 가 있고, `Partitions\<이름>\Network\Cookies` 의 `cookies` 표에는 `creation_utc`·`last_access_utc`·`last_update_utc`·`expires_utc` 칸이 있습니다(확인 범위: Windows 11, 2026-09). 칸 이름으로 뜻을 짐작할 수는 있지만 공식 설명은 확인하지 못해서 근거 등급을 "관찰" 로 둡니다. 폴더 구조의 공통 원리는 [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md)에 있습니다.

**다른 개발 도구.** Gemini CLI 는 세션을 `~/.gemini/tmp/<project_hash>/chats/` 에 대화하는 동안 자동으로 저장하지만, 세션 파일의 형식과 시각 칸 이름은 확인하지 못했습니다. Codex CLI 는 `~/.codex/history.jsonl` 에 입력 기록을 남기는데 줄의 키 이름은 확인하지 못했고, 조직이 OpenTelemetry 수집을 켜 두었다면 `codex.user_prompt`·`codex.tool_result` 같은 이벤트가 수집 서버에 따로 있습니다. Cursor 는 작업 공간마다 `state.vscdb` SQLite 파일에 대화를 둔다고 제3자 도구(2025년 중반까지 기준)가 적고 있지만 시각 칸은 확인하지 못했습니다. 이런 도구는 기록 파일 자체의 파일 시스템 시각을 먼저 타임라인에 올리고, 안의 시각 칸은 실제 파일로 확인한 뒤 더합니다. 도구별 경로는 [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Cursor](../../02-artifacts/dev-agents/cursor.md) 페이지에 있습니다.

**서버에서 받은 자료.** ChatGPT 계정 내보내기 ZIP 의 `conversations.json` 에는 메시지마다 `create_time`·`update_time` 이 있다고 오픈소스 변환 도구 convoviz 의 메시지 모델이 적고 있지만, 공식 스키마가 아니고 값의 형식도 확인하지 못했습니다. convoviz 는 2026년 7월 무렵부터 일부 메시지에서 `status`·`weight` 가 빠졌다고 적어서, 내보내기 형식이 알림 없이 바뀔 수 있다는 점도 기억해 둡니다. Claude Enterprise 감사 로그는 기록마다 `created_at`, `event`, `ip_address`, `device_id`, `client_platform` 같은 칸이 있고 대화 내용은 넣지 않습니다.

**네트워크.** Sysmon 이벤트 ID 22 는 프로세스가 DNS 질의를 할 때마다, 이벤트 ID 3 은 TCP/UDP 연결을 기록하고, 둘 다 프로세스와 연결되며 시각은 UTC 입니다. 이벤트 3 은 기본으로 꺼져 있어 설정 파일이 있어야 남습니다. Zeek 를 쓰는 조직이라면 `ssl.log` 의 `server_name` 칸에서 클라이언트가 요청한 도메인을 봅니다. 도메인 해석은 [AI 서비스 도메인과 네트워크 기록](../../02-artifacts/network-enterprise/network-traces.md)에 있습니다.

**Windows 의 AI 기능.** Recall 은 스냅숏 시각을 100나노초 단위(FILETIME)로 적는다고 제3자 연구 도구 문서가 설명하지만, 2025-04 이후 다시 설계한 판은 스냅숏과 DB 를 암호화해서 디스크 이미지만으로는 폴더와 파일의 존재, 크기, 파일 시스템 시각 정도만 타임라인에 올릴 수 있습니다. 자세한 내용은 [Recall](../../02-artifacts/windows-ai/recall.md)에 있습니다.

### 4. 한 표로 합치고 근거 등급을 붙입니다

출처마다 뽑은 시각을 UTC 로 바꿔 한 표에 합치고, 줄마다 원래 값, 출처(파일과 키), 사건, 근거 등급을 적습니다. 근거 등급은 "문서"(공식 문서로 뜻을 확인), "관찰"(키 이름만 확인), "추정"(이름이나 앞뒤 사건으로 짐작) 세 가지로 나누면 보고서를 쓸 때 문장의 세기를 정하기 쉽습니다. 아래는 모양을 보여 주려고 새로 만든 예시이고, 사용자 이름·경로·세션 ID·시각은 모두 지어낸 값입니다.

```text
UTC 시각              출처(파일 · 키)                                       사건                          근거
2026-09-10 02:10:31   C:\Users\kim.sample\Documents\plan_v2.docx (OS 타임라인)  파일 열람 흔적            OS 흔적
2026-09-10 02:15:00   .claude\history.jsonl · timestamp                     프롬프트 입력(project=C:\work\sample-report)  문서
2026-09-10 02:15:04   .claude\projects\...\3f2a9c1e-....jsonl · timestamp   도구 호출 Edit(README.md)     관찰
2026-09-10 02:15:05   C:\work\sample-report\README.md (OS 타임라인)         파일 내용 바뀜                OS 흔적
2026-09-10 02:16:40   Partitions\...\Network\Cookies · last_access_utc      쿠키 접근                     관찰
```

### 5. 빈 구간을 설명합니다

타임라인에 비는 구간이 있으면 "그때 쓰지 않았다" 로 읽기 전에 기록이 지워지거나 처음부터 쓰이지 않은 까닭이 있는지 확인합니다. Claude Code 는 세션 기록을 기본 30일(`cleanupPeriodDays`) 뒤에 지우지만 `history.jsonl` 과 `stats-cache.json` 은 남겨서, 대화 전문 없이 입력 시각과 날짜별 사용량만 남은 구간이 생깁니다. 데스크톱 앱·Cowork 에서 시작하거나 마지막으로 이어 간 세션은 나이와 상관없이 남고(`desktopSessionCleanupPeriodDays` 를 두면 그 기간), 환경 변수 `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 기록과 입력 이력을 아예 쓰지 않습니다. `claude project purge` 는 그 프로젝트의 기록과 `history.jsonl` 의 해당 줄까지 지웁니다. Gemini CLI 는 `sessionRetention` 으로 기본 30일 보관하고 `--delete-session` 으로 세션을 지울 수 있으며, Codex CLI 는 `[history] persistence = "none"` 이면 입력 기록을 남기지 않습니다. 서버 쪽은 Claude 개인 계정에서 지운 대화가 목록에서 바로 사라지고 30일 안에 서버 저장소에서 지워지며, Gemini 앱 활동은 기본 18개월 뒤 자동 삭제되고 활동 기록을 끈 상태의 대화는 72시간만 남습니다. 보관 규칙은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)에 모아 두었습니다.

### 6. 다른 흔적과 교차 검증합니다

도구 기록의 시각은 앱이 적은 값이라서, 파일 시스템과 운영체제 흔적으로 한 번 더 받쳐 둡니다. Claude Code 세션 기록의 도구 호출 줄에 편집 대상 파일 경로가 있으면 그 파일의 변경 시각과 맞춰 보고, `file-history/<세션>/` 에 남은 편집 전 사본의 생성 시각도 함께 봅니다. 줄마다 있는 `cwd`·`gitBranch` 는 작업 폴더와 브랜치를 알려 주어 저장소의 커밋 시각과 이어 볼 수 있습니다. 웹 서비스를 쓴 구간은 브라우저 방문 기록과 서버 내보내기의 대화 시각을 나란히 둡니다. 모으는 순서는 [기기에서 AI 흔적 모으기](../acquisition/endpoint-triage.md)를 따릅니다.

## 도구

JSONL 기록은 `jq` 로 필요한 키만 뽑아 표로 만들면 됩니다. 아래 명령은 `history.jsonl` 에서 관찰로 확인한 키 이름만 쓴 예시이고, `display` 칸에는 입력한 프롬프트가 그대로 들어 있어 결과 파일도 증거와 같은 수준으로 다룹니다.

```bash
jq -r '[.timestamp, .sessionId, .project] | @tsv' history.jsonl > history_times.tsv
```

쿠키 DB 같은 SQLite 파일은 앱이 쓰는 중이면 열리지 않아서(관찰 때 기본 `Network\Cookies` 가 OperationalError 로 열리지 않았습니다) 복사본을 `sqlite3` 로 엽니다. 읽는 법은 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 페이지에 있습니다. ChatGPT 내보내기는 오픈소스 도구 convoviz 로 Markdown 과 사용 그래프로 바꿔 볼 수 있지만, 시각 해석은 원본 JSON 으로 다시 확인합니다. 여러 출처를 합친 뒤에는 스프레드시트나 OS 판에서 소개한 타임라인 도구에 넣어 정렬합니다.

## 함정과 한계

시각 값의 형식을 확인하지 못한 칸이 많습니다. `history.jsonl` 의 정수가 밀리초인지, 세션 기록의 문자열이 UTC 인지는 이 핸드북에서 확인하지 못해서, 실제 파일에서 알고 있는 사건(수집 직전에 한 번 입력해 본 시각 등) 하나로 변환이 맞는지 먼저 시험합니다.

세션 기록의 줄 시각이 모두 사람이 입력한 시각은 아닙니다. 같은 파일에는 모델 응답, 도구 결과, 훅 실행 결과(`attachment.hookEvent` 등), 파일 되돌리기 스냅숏 줄이 섞여 있고, 하위 에이전트 기록은 `subagents/` 아래 다른 파일에 `agentId`·`isSidechain` 키와 함께 따로 쌓입니다(확인 범위: Windows 11, 2026-09). 사람의 입력 시각은 `history.jsonl` 과 맞춰 가립니다.

앱 폴더에 AI 와 무관한 흔적이 섞일 수 있습니다. 관찰한 Claude 데스크톱 스토어 앱 패키지의 `LocalCache\Local` 아래에는 Android SDK, NuGet, npm, pip 캐시도 있었고(확인 범위: Windows 11, 2026-09), 이 파일들의 시각을 AI 사용 시각으로 읽으면 안 됩니다. 쿠키 시각도 쿠키가 만들어지거나 쓰인 시각이지 대화 시각은 아닙니다.

기기에 원본이 없는 세션이 있습니다. Claude Code 클라우드 세션은 서비스 쪽 가상 머신에서 돌아 사용자 PC 에 대화 파일이 생기지 않고, 이런 구간은 서버 자료 없이는 채울 수 없다고 보고서에 적습니다.

버전마다 기록 모양이 바뀝니다. Claude Code 는 v2.1.274 까지 첨부 이미지를 `image-cache/<세션>/` 에 두다가 그 뒤로 임시 폴더로 옮겼고, 세션 기록의 키도 공개 규격이 없어 바뀔 수 있으니 줄마다 있는 `version` 값을 표에 함께 적습니다. 네트워크 쪽도 Sysmon 이벤트 3 은 기본으로 꺼져 있고, TLS 에 ECH 를 쓰면 `ssl.log` 의 `server_name` 이 비어 도메인이 보이지 않습니다.

## 결과를 어떻게 해석하나

타임라인으로는 "이 시각에 이 파일에 이런 기록이 있다" 까지만 말할 수 있습니다. `history.jsonl` 의 한 줄은 그 Windows 계정에서 돈 Claude Code 가 프롬프트 입력을 기록했다는 뜻이고, 누가 키보드 앞에 있었는지는 로그온 기록 같은 다른 흔적과 맞춰야 합니다. 그 판단은 [그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)에서 다룹니다. 두 사건이 몇 초 차이로 붙어 있어도 앞의 사건이 뒤의 사건을 일으켰다고 쓰지 않고, 같은 세션 ID·같은 파일 경로처럼 기록이 직접 잇는 고리가 있을 때만 이어서 씁니다.

보고서에는 다음처럼 근거와 세기를 맞춘 문장을 씁니다(만든 예시).

- 좋은 예: "2026-09-10 02:15:00(UTC)에 `history.jsonl` 에 프로젝트 경로 `C:\work\sample-report` 로 프롬프트 입력이 한 줄 기록되어 있고, 같은 세션 ID 의 대화 기록에는 4초 뒤 README.md 편집 도구 호출이 있습니다. 같은 파일의 변경 시각은 그 1초 뒤입니다."
- 피할 예: "용의자가 02:15 에 AI 로 보고서를 고쳤다."

보고서 전체의 틀은 [AI 관련 포렌식 보고서](../reporting/forensic-report.md)를 따릅니다.

## 참고 문헌

- Claude Code Docs — Explore the .claude directory. https://code.claude.com/docs/en/claude-directory
- Claude Code Docs — Checkpointing. https://code.claude.com/docs/en/checkpointing
- Claude Code Docs — Data usage. https://code.claude.com/docs/en/data-usage
- google-gemini/gemini-cli — docs/cli/session-management.md. https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/session-management.md
- OpenAI Codex — Advanced configuration. https://learn.chatgpt.com/docs/config-file/config-advanced
- somogyijanos/cursor-chat-export (GitHub, 2025-06-17 보관 처리). https://github.com/somogyijanos/cursor-chat-export
- mohamed-chs/convoviz README. https://github.com/mohamed-chs/convoviz
- convoviz 메시지 모델(message.py). https://raw.githubusercontent.com/mohamed-chs/convoviz/main/convoviz/models/message.py
- Claude Help Center — How to access audit logs. https://support.claude.com/en/articles/9970975-how-to-access-audit-logs
- Claude Privacy Center — How long do you store my data? https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
- Gemini Apps Help — Gemini Apps Privacy Hub. https://support.google.com/gemini/answer/13594961?hl=en
- Microsoft Learn — Sysmon. https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon
- Zeek documentation — ssl.log. https://docs.zeek.org/en/master/logs/ssl.html
- xaitax/TotalRecall README. https://github.com/xaitax/TotalRecall
