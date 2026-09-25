---
title: "대화 기록 보관 설정과 삭제"
parent: "기반 · 저장 구조"
nav_order: 40
---

# 대화 기록 보관 설정과 삭제 (Retention·Deletion)

> 확인 날짜: 2026-09-25. 공식 문서의 마지막 수정일은 Claude 개인정보 문서 2026-07-01, Gemini 개인정보 문서 2026-09-24, Microsoft Purview 보존 문서 2026-06-25(작성 2025-09-23), eDiscovery 문서 2026-06-29, 감사 보관 문서 2026-06-24 입니다. 기기 쪽 삭제 실험은 논문 두 편의 결과이고, 시험한 OS 와 앱 판은 본문 표에 적었습니다. 기기 관찰은 Windows 11(빌드 26200)에서 설정 파일의 키 이름만 본 결과이고, 그런 문장에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였습니다.

## 한 줄 요약

AI 대화 기록은 서버에서는 서비스 회사의 보관 정책과 사용자 설정에 따라, 기기에서는 앱의 저장 방식과 자동 정리 설정에 따라 따로 사라집니다. 목록에서 지운 대화가 서버의 보류 폴더나 기기의 WAL·로그 파일에 남는 경우가 있어서 "지웠다" 와 "없다" 를 나눠 적어야 합니다.

## 이 형식을 쓰는 아티팩트

서버 쪽은 [Claude](../../02-artifacts/chat-services/claude/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md), [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md) 같은 채팅 서비스의 계정 기록과 [Microsoft 365 Copilot](../../02-artifacts/office-integrations/m365-copilot.md) 의 조직 보존 사본이 대상입니다. 기기 쪽은 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 처럼 대화를 파일로 남기는 도구, [AI 컴패니언 앱](../../02-artifacts/chat-services/companion-apps.md), [Ollama](../../02-artifacts/local-ai/ollama.md)·[LM Studio](../../02-artifacts/local-ai/lm-studio.md) 같은 로컬 AI 앱이 대상입니다. 어느 쪽에 원본이 있는지는 [AI 서비스의 데이터는 어디에 있나](where-data-lives.md) 에서 먼저 가립니다.

## 구조

### 서버 쪽 — 서비스별 보관 기간

**Claude 개인용(Free·Pro·Max).** 사용자가 대화를 지우면 대화 목록에서는 바로 사라지고, 서버 저장소에서는 30일 안에 지웁니다 [1]. 용도에 따라 더 오래 남는 기록이 따로 있고, 법적 요구나 분쟁 해결에 필요하면 아래 기간보다 더 오래 보관할 수 있습니다 [1].

| 기록 | 보관 기간 | 근거 |
|---|---|---|
| 사용자가 지운 대화 | 목록에서 바로 사라지고 서버 저장소에서는 30일 안에 삭제 | [1] |
| 모델 개선 설정을 켠 뒤 만든 대화 | 비식별 형태로 모델 학습 파이프라인에 최대 5년 | [1] |
| 사용 정책 위반으로 자동 표시된 대화 | 입력·출력 최대 2년, 안전 분류 점수 최대 7년 | [1] |
| 피드백으로 보낸 내용 | 5년 | [1] |
| 시크릿 (Incognito) 대화 | 설정과 관계없이 모델 개선에 쓰지 않음 | [1] |

**Claude Code 의 서버 쪽 기록.** 개인 계정(Free·Pro·Max)은 모델 개선을 허용하면 5년, 거부하면 30일 보관하고, 상업 계정(Team·Enterprise·API)은 기본 30일입니다 [3]. 무보관(ZDR)은 자격을 확인한 뒤 조직별로 켭니다 [3]. `/feedback`·`/bug`·`/share` 로 보낸 대화는 5년 보관하고, 세션 품질 설문 뒤 기록 공유에 동의해 올린 기록은 6개월까지 보관합니다 [3].

**Gemini 앱.** 대화는 "Keep Activity" 가 켜져 있을 때 계정의 "Gemini Apps Activity" 에 저장됩니다 [2]. 활동 자동 삭제의 기본값은 18개월이고, 3개월·36개월·자동 삭제 안 함으로 바꿀 수 있습니다 [2]. Keep Activity 를 끈 상태의 대화와 임시 대화 (Temporary chat) 도 응답과 서비스 보호를 위해 계정에 72시간 남고, 임시 대화는 Google 모델 학습에 쓰지 않습니다 [2]. 사람 검토자가 본 대화는 언어·기기 종류·위치 정보·피드백과 함께 최대 3년 남고, 사용자가 활동을 지워도 함께 지워지지 않습니다 [2]. 활동은 `myactivity.google.com/product/gemini` 에서 관리합니다 [2].

**ChatGPT.** 보관 기간과 임시 채팅의 처리는 OpenAI 도움말과 개인정보 문서에서 조사 대상 기간에 적용되던 판으로 확인합니다.

**Microsoft 365 Copilot 과 조직 보존 정책.** 조직이 보존 정책을 걸면 Copilot 과 AI 앱의 프롬프트·응답 사본이 앱을 쓴 사용자의 Exchange Online 메일함 안 숨은 폴더에 저장됩니다 [5]. 새로 만드는 보존 정책은 Microsoft 365 Copilot, Copilot Studio 같은 Microsoft 앱뿐 아니라 ChatGPT, Google Gemini, 소비자용 Microsoft Copilot, DeepSeek 같은 "다른 AI 앱" 도 위치로 고를 수 있습니다 [5]. Microsoft 365 Copilot 과 Copilot Studio 는 프롬프트·응답이 늘 들어가고, 그 밖의 Copilot 과 생성형 AI 앱은 수집 정책에서 내용 수집을 켜 두었을 때만 들어갑니다 [5]. 사용자가 Microsoft 365 Copilot Chat 에서 대화를 지우거나 그 사용자의 전체 기록 삭제 요청이 들어오면 항목이 같은 메일함의 또 다른 숨은 폴더 `SubstrateHolds` 로 옮겨집니다 [5]. 창이나 앱을 닫는 것만으로는 메시지가 지워지지 않고 화면에서 숨겨질 뿐입니다 [5].

`SubstrateHolds` 로 간 항목은 최소 1일 머물고, 보존 기간이 끝난 뒤 Exchange 타이머 작업이 다음에 돌 때 영구 삭제됩니다 [5]. 이 타이머 작업은 보통 1~7일 간격으로 돕니다 [5]. 영구 삭제 전까지는 eDiscovery 로 검색되고, 같은 위치의 다른 보존 정책, Litigation Hold, delay hold, eDiscovery hold 가 걸려 있으면 영구 삭제가 멈춥니다 [5]. 문서의 예시로는 "1일 뒤 삭제" 정책도 영구 삭제까지 16일 걸릴 수 있습니다 [5]. 퇴사해 계정이 지워진 사용자의 메시지는 비활성 사서함 (inactive mailbox) 에 남아 eDiscovery 로 찾을 수 있습니다 [5]. Copilot 메모리는 item class `IPM.Contact` 로 저장되고, Purview 나 eDiscovery 에서 대화를 지워도 연결된 메모리는 지워지지 않습니다 [6]. 정책 종류별 삭제 흐름 표와 감사 기록의 칸은 [Microsoft Purview로 본 Copilot 기록](../../02-artifacts/network-enterprise/purview-copilot.md) 에 있습니다.

감사 기록은 보존 사본과 보관 체계가 따로입니다. 감사 (Standard) 의 기본 보관은 180일이고, 2023-10-17 이전에 생긴 레코드는 90일입니다 [7]. Audit (Premium) 의 기본 1년 정책은 `Workload` 가 AzureActiveDirectory·Exchange·OneDrive·SharePoint 인 레코드에만 걸려서, 그 밖의 레코드는 사용자 지정 정책이 없으면 180일 보관입니다 [7]. 180일을 넘겨 1년까지 두려면 레코드를 만든 사용자에게 E5 계열 라이선스가 있어야 하고, 10년까지 두려면 10년 보관 추가 라이선스도 있어야 합니다 [7].

### 기기 쪽 — 로컬 도구의 자동 정리

Claude Code 는 세션 기록을 `cleanupPeriodDays` 로 정한 기간이 지나면 지우고, 기본값은 30일이며 최소값은 1입니다(0 은 설정 검증에서 거부) [4]. 무엇을 지우고 무엇을 남기는지는 문서가 나눠 적고 있습니다 [4].

| 자동 정리로 지우는 것 | 자동 정리로 지우지 않는 것 |
|---|---|
| 세션 기록 `.jsonl` 과 그 변형, `subagents/`, `tool-results/`, `file-history/` 아래 세션별 폴더, `debug/`, `paste-cache/`, `image-cache/` 등 | `history.jsonl`(입력 이력), `stats-cache.json`(사용량 통계), `backups/`, `jobs/`, `daemon/`, 자동 메모리 |

데스크톱 앱이나 Cowork 에서 시작했거나 마지막으로 이어 간 세션 기록은 기본으로 기한 없이 남고, `desktopSessionCleanupPeriodDays` 로 따로 정합니다(문서 기준 v2.1.248 부터) [4]. 설정 파일을 읽을 수 없거나 `--bare` 로 실행하면 정리를 멈추고, 관리 정책이 `cleanupPeriodDays` 를 주면 그 값으로 정리합니다 [4]. 사용자가 직접 지우는 명령은 `claude project purge` 이고, 그 프로젝트의 기록·자동 메모리·세션별 폴더와 함께 `history.jsonl` 의 해당 줄과 `~/.claude.json` 의 프로젝트 항목까지 지웁니다 [4]. `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 처음부터 기록과 입력 이력을 쓰지 않습니다 [4].

아래는 설정 파일에서 정리 기간 키가 어떻게 보이는지 보이려고 만든 예시이고, 값은 가짜입니다.

```json
{
  "cleanupPeriodDays": 14
}
```

`stats-cache.json` 은 자동 정리 대상이 아니고 [4], 관찰한 파일에는 `dailyActivity[].date`·`messageCount`·`sessionCount`·`toolCallCount`, `firstSessionDate`, `hourCounts`, `longestSession`, `modelUsage`, `totalMessages`, `totalSessions` 같은 키가 있었습니다(확인 범위: Windows 11, 2026-09). 세션 기록이 정리된 뒤에도 그 세션의 수치가 통계에 남는지는 정리 전후의 파일을 견주어 검체에서 확인합니다. 기록 구조는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 쪽에서 다룹니다.

Claude 데스크톱의 `claude_desktop_config.json` 에는 정수 값을 담는 `preferences.ccAutoArchiveInactiveDays` 키가 있었습니다(확인 범위: Windows 11, 2026-09). 이 설정이 기기의 파일을 지우는지는 값과 데이터 폴더의 세션 파일을 대조해 검체에서 확인합니다.

### 기기 쪽 — 앱 화면에서 지운 뒤 남는 것

앱 화면에서 대화를 지워도 파일이 함께 사라지는지는 앱의 저장 방식에 따라 다릅니다. 아래 두 논문은 앱 안의 삭제 기능을 쓴 뒤 기기에 무엇이 남는지 시험했습니다.

**AI 컴패니언 앱.** Comeaux 외는 루팅한 Android 12(API 31) 에뮬레이터에서 `/data/data` 를 논리 수집해 여섯 앱을 시험했습니다 [8]. 논문에 앱 판 번호가 없어서 지금 판에서는 결과가 다를 수 있습니다. 앱마다 쓸 수 있는 삭제 기능이 달라서, Character.AI 만 메시지 한 건씩 지울 수 있었고, Linky.AI·Persona.AI·Fantasy.AI 는 대화 전체 지우기, Replika·Kindroid 는 계정 삭제만 가능했습니다 [8].

| 앱 | 쓴 삭제 기능 | 삭제 뒤 결과 |
|---|---|---|
| Replika | 계정 삭제 | 주 SQLite DB 는 기기에서 지워졌지만, Firebase Crashlytics 로그의 `userlog` 하위 폴더에서 대화 전체가 복구됨 |
| Persona.AI·Fantasy.AI | 대화 삭제 | 주 DB 에서는 지워졌지만 `ai_personal_db-wal` 에 남았고, 앱 데이터를 모두 지운 뒤에도 WAL 에서 복구됨 |
| Linky.AI | 대화 지우기 | 새 대화 ID 만 만들고 원래 대화 기록은 DB 에 그대로 남음. 앱에 계정 삭제 기능이 없음 |
| Kindroid | 계정 삭제 | 기기에 남은 인증 정보로도 서버 대화를 얻을 수 없었음 |
| Character.AI | 메시지 삭제, 계정 삭제 | 지운 메시지가 서버 API 응답에서 빠짐. 계정을 지우면 기기의 인증 토큰과 로그인 정보도 지워짐. 서버 백업·로그에서 지워졌는지는 논문의 시험 범위 밖 |

논문은 대화를 기기에 저장하는 네 앱이 모두 대화 지우기와 계정 삭제 뒤에도 기기에 자료를 남겼고, 서버에 저장하는 두 앱은 지우거나 접근할 수 없게 만들었다고 정리합니다 [8]. 앱별 경로는 [AI 컴패니언 앱](../../02-artifacts/chat-services/companion-apps.md) 에 있습니다.

**로컬 LLM 앱.** Jeong 외는 Windows 11 Pro 24H2(빌드 26100.3775)에서 앱 화면으로 지운 항목을 LangurTrace 로 얼마나 되살리는지 쟀습니다 [9]. 시험한 판은 Ollama 0.6.5, Chatbox 1.11.8, LM Studio 0.3.14, Msty 1.8.5, Jan 0.5.16, GPT4All 3.10.0 이고 [9], 이후 판은 저장 방식이 바뀌었을 수 있습니다.

| 앱 | 모델 다운로드 | 대화 | 올린 파일 | 생성 파일 |
|---|---|---|---|---|
| Ollama | 100%(5/5) | – | – | – |
| Chatbox | – | 58%(29/50) | 100%(50/50) | 100%(50/50) |
| LM Studio | 100%(5/5) | 0%(0/50) | 0%(0/50) | – |
| Msty | 100%(5/5) | 0%(0/50) | 100%(50/50) | – |
| Jan | 100%(5/5) | 100%(50/50) | – | – |
| GPT4All | 0%(0/5) | 0%(0/50) | – | – |

표는 논문 표 8 을 옮긴 것이고, 괄호는 지운 개수 가운데 되살린 개수입니다. "–" 는 그 앱에 해당 기능이 없거나 시험하지 않은 항목입니다. 모델을 지워도 Ollama 의 서버 로그, LM Studio·Msty·Jan 의 모델 설치 기록에 무엇을 받았는지 남았습니다 [9]. Chatbox 는 백업을 정해진 주기 없이 해서 지운 대화의 일부만 되살렸고, Jan 은 상세 로그 (verbose log) 에 지운 대화가 남았습니다 [9]. 이 비율은 디스크에서 되살린 것만 잰 값이고, 볼륨 섀도 복사본, 메모리, SQLite freelist·WAL 카빙은 시험하지 않았습니다 [9]. 그래서 0% 인 항목도 다른 방법으로는 일부 남아 있을 수 있습니다. 앱별 경로는 각 앱 쪽([Ollama](../../02-artifacts/local-ai/ollama.md), [Chatbox](../../02-artifacts/local-ai/chatbox.md), [LM Studio](../../02-artifacts/local-ai/lm-studio.md), [Msty](../../02-artifacts/local-ai/msty.md), [Jan](../../02-artifacts/local-ai/jan.md), [GPT4All](../../02-artifacts/local-ai/gpt4all.md))에 있습니다.

**앱을 지운 뒤.** WebView2 앱은 스토어 앱과 ClickOnce 앱을 빼면 앱을 지워도 사용자 데이터 폴더를 자동으로 지우지 않고, 자세한 규칙은 [Electron·웹뷰 앱의 저장 구조](electron-webview.md) 에 있습니다. 서버에서 대화를 지운 뒤 기기의 IndexedDB·Local Storage·캐시에 남은 조각을 찾는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md) 에서 다룹니다.

## 읽는 법

1. 계정 종류를 먼저 확인합니다. Claude Code 처럼 개인 계정과 조직(Team·Enterprise·API) 계정의 보관 기간이 다른 서비스가 있고 [3], Microsoft 365 Copilot 은 조직의 보존 정책과 보류 여부가 기간을 정합니다 [5].
2. 조사 대상 기간에 켜져 있던 설정을 확인합니다. Claude 의 모델 개선 설정, Gemini 의 Keep Activity 와 자동 삭제 기간처럼 보관 기간을 바꾸는 설정은 지금 값이 아니라 그 당시 값이 기준입니다.
3. 대화를 지운 시각과 지금 날짜를 놓고, 위 표의 기간에 비추어 서버에 아직 남아 있을 수 있는 기록을 가립니다. 남아 있을 수 있다면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 을 서두르고, 조직 쪽이면 보류(hold)부터 걸도록 요청합니다.
4. 기기 쪽은 `~/.claude/settings.json` 같은 설정 파일에서 정리 기간 키를 읽고, 남아 있는 가장 오래된 세션 기록 파일의 날짜와 맞춰 봅니다. 정리 기간보다 오래된 기록이 없다면 자동 정리로 사라진 것일 수 있고, `history.jsonl` 과 `stats-cache.json` 에서 그 기간의 흔적을 찾습니다.
5. 앱 화면에서 지운 대화라면 주 DB 옆의 `-wal` 파일, 충돌 로그 폴더, 상세 로그, 첨부 폴더를 먼저 수집합니다. 위 두 논문에서 복구된 자리가 이런 곳이었습니다 [8][9].

## 포렌식에서 중요한 점

**목록에서 사라진 것과 서버에서 사라진 것은 다릅니다.** Claude 는 지운 대화를 목록에서 바로 감추지만 서버 저장소에서는 30일 안에 지우고 [1], Gemini 는 사람 검토를 거친 대화를 활동 삭제와 별개로 최대 3년 남깁니다 [2]. Microsoft 문서는 AI 앱에 보이는지 여부가 보존·영구 삭제 상태를 정확히 나타내지 않는다고 적고 있습니다 [5]. 사용자가 "지웠다" 고 말해도 서버 쪽 기록이 남아 있을 수 있어서, 삭제 시각과 요청 시각을 함께 적습니다.

**기록을 끈 것과 지운 것은 흔적이 다릅니다.** Claude Code 는 `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 처음부터 기록을 쓰지 않고 [4], Gemini 는 Keep Activity 를 끈 대화도 72시간은 계정에 남깁니다 [2]. 기록이 비어 있다면 삭제 흔적을 찾기 전에 기록을 끄는 설정이 있었는지부터 봅니다.

**앱의 "지우기" 가 파일을 지우지 않는 경우가 있습니다.** Linky.AI 는 대화를 지워도 새 대화 ID 만 만들었고, Persona.AI·Fantasy.AI 는 지운 대화가 WAL 에 남았으며, Replika 는 계정을 지운 뒤에도 충돌 로그에 대화가 남았습니다 [8]. 반대로 LM Studio 는 지운 대화와 업로드가 디스크 수준에서 되살아나지 않았습니다 [9]. 같은 "삭제" 라도 앱마다 결과가 달라서, 앱과 판을 밝히고 판단합니다. WAL 의 구조는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-android/01-foundations/data-formats/sqlite/index.html) 에서 다룹니다.

**자동 정리 뒤에도 남는 파일이 있습니다.** Claude Code 의 자동 정리는 입력 이력과 사용량 통계를 지우지 않아서 [4], 세션 기록이 없는 기간의 사용 시기와 규모를 이 두 파일로 가늠할 수 있습니다.

**모델 파일이 없어도 받은 기록은 남습니다.** 로컬 LLM 앱 다섯 개 가운데 네 개는 모델을 지워도 다운로드 기록으로 무엇을 받았는지 모두 되살렸습니다 [9]. 모델 파일 자체는 [로컬 모델 파일](../../02-artifacts/local-ai/model-files.md) 에서 다룹니다.

## 함정

**"30일 안에" 는 정확한 삭제 날짜가 아닙니다.** 문서는 상한만 적고 있어서, 지운 지 30일이 안 된 대화가 서버에 남아 있다고 단정하지도, 이미 사라졌다고 단정하지도 않습니다. Microsoft 365 Copilot 도 타이머 작업 주기 때문에 영구 삭제 날짜가 며칠씩 흔들립니다 [5].

**비식별 학습 데이터는 계정 기록이 아닙니다.** Claude 의 모델 개선용 대화는 비식별 형태로 학습 파이프라인에 남는다고 적혀 있어서 [1], 최대 5년이라는 기간을 계정 기록이 5년 남는다는 뜻으로 읽지 않습니다.

**대화를 지워도 메모리는 남을 수 있습니다.** Microsoft 365 Copilot 의 메모리는 대화와 따로 `IPM.Contact` 로 저장되고, Purview 나 eDiscovery 에서 대화를 지워도 함께 지워지지 않습니다 [6]. 대화가 없다는 사실만으로 그 대화에서 나온 정보가 계정에 남아 있지 않다고 보지 않습니다.

**데스크톱에서 시작한 세션은 정리 규칙이 다릅니다.** Claude Code 기록 가운데 데스크톱 앱·Cowork 세션은 `cleanupPeriodDays` 가 아니라 `desktopSessionCleanupPeriodDays` 를 따라서 [4], 같은 폴더 안에서도 기록마다 남은 기간이 다를 수 있습니다.

**논문의 복구율은 그 판, 그 방법의 값입니다.** 표 8 의 0% 는 디스크 수준 파싱 결과이고 [9], 컴패니언 앱 결과는 Android 에뮬레이터 한 환경의 결과입니다 [8]. 다른 판·다른 OS 에서는 검체로 다시 확인합니다.

**문서는 바뀝니다.** 보관 기간은 서비스 회사가 고치는 정책이라서 조사 대상 기간에 적용되던 문서 판을 확인하고, 확인한 날짜를 보고서에 적습니다.

## 도구

설정 파일의 정리 기간 키는 `jq` 같은 공개 도구로 뽑고, 세션 기록 파일의 날짜 목록은 OS 기본 명령으로 뜬 뒤 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 에 올립니다. 로컬 LLM 앱은 LangurTrace(github.com/jeongramon/LangurTrace)가 KAPE 타깃과 파서로 지운 모델·대화 기록을 모읍니다 [9]. WAL 에 남은 레코드는 [SQLite 데이터베이스](https://urock-ailab.github.io/forensics-handbook-windows/01-foundations/database-log-formats/sqlite/index.html) 의 방법으로 읽습니다. Microsoft 365 Copilot 의 보존 사본과 `SubstrateHolds` 항목은 Purview eDiscovery 로 검색합니다 [5][6]. 서버 쪽 보관 정책은 공개 문서를 저장해 둔 사본(날짜가 찍힌 PDF 나 웹 보관본)을 보고서에 붙입니다.

## 참고 문헌

1. Claude Privacy Center — How long do you store my data? — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
2. Gemini Apps Help — Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961?hl=en
3. Claude Code Docs — Data usage — https://code.claude.com/docs/en/data-usage
4. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
5. Microsoft Learn — Learn about retention for Copilot & AI apps (ms.date 2025-09-23, 갱신 2026-06-25) — https://learn.microsoft.com/en-us/purview/retention-policies-copilot
6. Microsoft Learn — Search for and delete AI application data in eDiscovery (ms.date 2026-06-19, 갱신 2026-06-29) — https://learn.microsoft.com/en-us/purview/edisc-search-copilot-data
7. Microsoft Learn — Manage audit log retention policies (ms.date 2026-06-19, 갱신 2026-06-24) — https://learn.microsoft.com/en-us/purview/audit-log-retention-policies
8. K. J. Comeaux, T. T. Spinosa, A. Ghosn, I. Baggili, "Ex Machina: A forensic evaluation of AI companion applications and their evidentiary value", Forensic Science International: Digital Investigation, 56 (2026), 302050. https://doi.org/10.1016/j.fsidi.2026.302050
9. S. Jeong, S. Lee, J. Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. https://doi.org/10.1016/j.fsidi.2025.301987
