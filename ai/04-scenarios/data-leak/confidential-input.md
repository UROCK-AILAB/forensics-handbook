---
title: "기밀 자료를 AI에 넣었나"
parent: "시나리오 · 정보 유출"
nav_order: 920
---

# 기밀 자료를 AI에 넣었나 (Confidential Data Input)

회사 자료가 AI 서비스에 들어갔는지, 들어갔다면 언제 어느 계정과 기기로 무엇이 들어갔는지를 묻는 조사를 다룹니다. 기한이 짧은 기록을 먼저 보존한 뒤 회사 보안 제품 기록에서 사건 후보를 찾고, AI 서비스 관리자 로그로 계정과 기기를 맞춥니다. 입력 본문은 계정 데이터 내보내기와 기기에 남은 개발 도구·로컬 AI 기록에서 확인하고, 세 곳의 시각과 계정을 한 타임라인에 놓고 대조합니다.

## 조사 질문

회사 자료(설계 문서, 고객 명단, 소스 코드 등)가 AI 서비스에 들어갔는지, 들어갔다면 언제 어느 계정과 기기로 무엇이 들어갔는지를 묻는 조사입니다. 답은 회사 보안 제품의 기록, AI 서비스의 관리자 로그, 기기에 남은 입력 기록 세 곳에서 찾고, 세 곳이 서로 맞는지 대조해서 결론을 냅니다. 허용되지 않은 AI 를 썼는지 자체를 따지는 조사는 [회사가 허용하지 않은 AI를 썼나](shadow-ai.md) 에서 다루고, 이 페이지는 "무엇이 들어갔나" 에 집중합니다.

## 먼저 확인할 것

- **서비스 종류.** 웹 채팅처럼 대화 원본이 서버에만 있는 서비스는 기기에 대화 본문이 없을 수 있어서, 기기에서는 방문·붙여넣기 흔적만 보고 본문은 서버 쪽 관리자 로그나 데이터 내보내기로 확인합니다. 개발 도구와 로컬 AI 는 기기에 기록을 남기는 경우가 많습니다. 서비스마다 어디에 무엇이 남는지는 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md) 와 각 서비스 페이지를 봅니다.
- **기한.** Claude Code 는 세션 기록을 기본 30일 동안 기기에 두고 지우며 [4], Claude Enterprise 감사 로그는 과거 180일까지만 내보낼 수 있습니다 [3]. 기한이 짧은 기록부터 먼저 보존합니다.
- **사용자와 계정.** 어느 Windows 사용자 프로필인지, AI 서비스에는 개인 계정으로 들어갔는지 회사 조직 계정으로 들어갔는지를 나눠 적습니다. 회사 관리자 로그는 회사 조직 계정만 보여 주므로, 개인 계정으로 쓴 흔적은 기기와 네트워크 기록에서 찾습니다.
- **시간대.** 기기 기록의 시각 필드마다 UTC 인지 현지 시각인지, 단위가 초인지 밀리초인지 확인하고 나서 다른 기록과 맞춥니다. 기기 기록의 시각 형식은 각 서비스 페이지를 보고, 실제 데이터에서 시각을 아는 기록 하나와 맞춰 본 뒤에 씁니다.
- **권한과 전제 조건.** 관리자 로그를 내보낼 권한이 누구에게 있는지, 회사 기기가 Microsoft Purview 에 등록(온보딩)돼 있는지를 먼저 알아 둡니다. 전제 조건이 빠지면 기록이 처음부터 생기지 않습니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 회사 보안 제품 기록(DLP·데이터 보안 관리 도구) | 민감 정보가 AI 사이트로 붙여넣기·업로드됐는지, 일부는 프롬프트 글까지 | [보안 제품이 남기는 AI 사용 기록](../../02-artifacts/network-enterprise/dlp-casb.md), [Microsoft Purview로 본 Copilot 기록](../../02-artifacts/network-enterprise/purview-copilot.md) |
| 2 | AI 서비스 관리자 로그 | 계정, 시각, IP, 기기, 파일 업로드 사건 | [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md), [ChatGPT 기업용 감사 기록](../../02-artifacts/network-enterprise/chatgpt-enterprise.md), [Google Workspace의 Gemini](../../02-artifacts/office-integrations/workspace-gemini.md), [Microsoft 365 Copilot](../../02-artifacts/office-integrations/m365-copilot.md) |
| 3 | 계정 데이터 내보내기 | 대화 본문과 첨부 | [계정 데이터 내보내기로 수집](../../03-techniques/acquisition/export-collection.md), [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md) |
| 4 | 개발 도구의 대화·입력 기록 | 입력한 글, 붙여넣은 내용, 도구가 읽은 파일 내용, 작업 폴더 | [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md), [Cursor](../../02-artifacts/dev-agents/cursor.md), [Codex CLI](../../02-artifacts/dev-agents/codex-cli.md), [Gemini CLI](../../02-artifacts/dev-agents/gemini-cli.md) |
| 5 | 데스크톱 앱·브라우저 저장소 | 방문 기록, 캐시에 남은 대화 조각 | [Electron·웹뷰 앱의 저장 구조](../../01-foundations/storage-model/electron-webview.md), [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md) |
| 6 | 로컬 AI | 서버 로그가 없어 기기 흔적만 남는 경우, 올린 파일 원본 | [Ollama](../../02-artifacts/local-ai/ollama.md), [LM Studio](../../02-artifacts/local-ai/lm-studio.md), [Msty](../../02-artifacts/local-ai/msty.md), [GPT4All](../../02-artifacts/local-ai/gpt4all.md) |

회사 보안 제품과 관리자 로그를 먼저 보는 이유는 사건 후보의 시각과 계정을 좁혀 주기 때문이고, 기기 기록은 그 시각 주변에서 본문을 확인하는 데 씁니다. 입력으로 볼 것과 첨부·생성물로 볼 것의 구분은 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md) 를 따릅니다.

## OS 별로 다른 점

**Windows.** 개발 도구는 사용자 폴더 아래 점(.)으로 시작하는 폴더에 기록을 두고, Claude 데스크톱 같은 스토어 앱은 패키지 폴더 아래 Electron(Chromium) 저장소 모양으로 데이터를 둡니다. 저장소 원리와 DPAPI 로 보호되는 값은 다른 판의 [크롬 계열 앱 공통 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/app-mail-data/chromium-electron-webview2/index.html) 와 [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html) 를 봅니다.

**macOS.** Endpoint DLP 는 Windows 10/11 과 함께 macOS 최신 3개 주 버전을 지원하지만, 브라우저 붙여넣기 평가는 macOS 에서 미리 보기(Preview) 단계입니다 [2]. 로컬 AI 인 Ollama 는 모델을 `~/.ollama/models` 에 둡니다 [5]. macOS 의 AI 앱 저장 위치는 각 서비스 페이지를 보고, 보호된 값은 다른 판의 [키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html) 페이지를 봅니다.

**Linux.** Ollama 모델 위치는 `/usr/share/ollama/.ollama/models` 입니다 [5].

**Android·iOS.** 모바일 앱의 저장 위치는 각 서비스 페이지를 봅니다. 앱 데이터를 보호하는 방식은 다른 판의 [Android 저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/encryption/index.html) 와 [iOS 데이터 보호](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/data-protection/index.html) 를 보고, 본문은 서버 쪽 내보내기로 확인하는 쪽을 먼저 검토합니다.

## 분석 흐름

1. **기한이 짧은 기록부터 보존합니다.** Claude Code 세션 기록은 `~/.claude/projects/` 아래에 평문으로 있고 기본 30일이 지나면 지워지며, 이 기한은 `cleanupPeriodDays` 로 바꿀 수 있습니다 [4]. 다만 Claude 데스크톱이나 Cowork 에서 시작했거나 마지막으로 이어 간 세션 기록은 기본으로 이 기한에서 빠집니다 [4]. 관리자 로그를 내보내는 이메일 링크는 24시간만 유효하므로 받는 즉시 해시를 떠서 보관합니다 [3]. 수집 순서는 [기기에서 AI 흔적 모으기](../../03-techniques/acquisition/endpoint-triage.md) 를 따릅니다.

2. **회사 보안 제품에서 사건 후보를 찾습니다.** Microsoft Purview 의 AI 용 데이터 보안 관리(DSPM for AI) 활동 탐색기(Activity explorer)에는 아래 이벤트가 남습니다 [1].

   | 이벤트 | 뜻 |
   |---|---|
   | `AI interaction` | 사용자가 생성형 AI 사이트와 주고받음. 프롬프트·응답이 들어가지만 Edge 의 관리되지 않는 AI 앱은 텍스트 프롬프트만 들어가고, Copilot 이 아닌 AI 앱은 콘텐츠 캡처를 고른 수집 정책이 있어야 프롬프트·응답이 남음 |
   | `DLP rule match` | 생성형 AI 사이트와 주고받는 중에 DLP 규칙과 일치 |
   | `Sensitive info types` | 생성형 AI 사이트와 주고받는 중에 민감 정보 유형 발견 |

   기본 DLP 정책 `DSPM for AI: Detect sensitive info added to AI sites` 는 Edge·Chrome·Firefox 에서 AI 사이트에 붙여넣거나 올린 민감 내용을 감사 모드로만 탐지합니다 [1]. 수집 정책 `DSPM for AI - Capture interactions for enterprise AI apps` 는 ChatGPT Enterprise 와 Entra·Microsoft Foundry 로 연결한 AI 앱의 프롬프트·응답을 eDiscovery 등에서 다룰 수 있게 캡처합니다 [1]. 제3자 AI 사이트에 민감 정보를 넣은 사건을 보려면 기기가 Purview 에 등록돼 있어야 합니다 [1]. DSPM for AI 는 "classic" 판에서 새 판으로 바뀌는 중이므로, 사건 당시 어느 판을 썼는지도 함께 확인합니다 [1].

   Endpoint DLP 쪽에서는 `Paste to supported browsers`(제한된 서비스 도메인에 붙여넣는 내용 자체를 평가하고 원본 파일 분류와는 상관없음), `Upload to a restricted cloud service domain or access from an unallowed browser`, `Copy to clipboard`(보호된 파일에서 복사) 활동을 봅니다 [2]. 기기가 온보딩되면 DLP 정책을 걸기 전에도 감사된 활동이 활동 탐색기로 들어오고 [2], 상세 속성에는 사용자, 기기 이름, 파일 이름·경로, 민감 정보 유형, sha1·sha256, 작업한 앱 등이 있습니다 [2]. 보안 제품 기록 읽는 법은 [보안 제품이 남기는 AI 사용 기록](../../02-artifacts/network-enterprise/dlp-casb.md) 에서 다룹니다.

3. **서비스 관리자 로그로 계정과 기기를 맞춥니다.** Claude 는 Enterprise 조직에만 감사 로그가 있고, Organization Owner 나 Primary Owner 가 조직 설정의 데이터·개인정보 메뉴에서 내보냅니다 [3]. 이 사건에서 먼저 볼 이벤트는 `file_uploaded` 와 `conversation_created` 이고, `created_at`, `actor_info`, `ip_address`, `device_id`, `user_agent`, `client_platform` 필드로 언제 누가 어느 기기에서 올렸는지 맞춥니다 [3]. 감사 로그에는 대화·프로젝트의 제목과 내용이 없고 고유 ID 만 있어서, 무엇을 올렸는지는 Primary Owner 가 따로 받는 데이터 내보내기로 확인합니다 [3]. 내보낸 `conversations.json` 의 `chat_messages[].attachments[]` 에는 `file_name`, `file_size`, `file_type` 과 함께 첨부에서 뽑은 글인 `extracted_content` 가 있고, `files[]` 에는 `file_name` 만 있습니다 [7][8]. 첨부의 글 내용은 `extracted_content` 에서 보고, `files[]` 에 이름만 있는 파일은 내용을 다른 곳에서 찾습니다. 프로젝트에 올린 문서는 `projects.json` 의 `docs[].filename` 과 `docs[].content` 에 들어갑니다 [7]. 필드 이름은 판마다 바뀔 수 있어 실제 데이터에서 먼저 확인합니다. 전체 이벤트 목록은 [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md) 에 있고, ChatGPT Enterprise 와 Google Workspace 의 Gemini 도 각 페이지의 관리자 기록을 같은 방식으로 봅니다. 회사가 직접 볼 수 없는 기록은 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 으로 받습니다.

4. **기기에서 입력 본문을 확인합니다.** 개발 도구는 입력과 도구 결과를 기기에 남깁니다. Claude Code 에서 이 사건에 바로 쓰는 키는 다음과 같습니다. 파일 구조 전체는 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 페이지에서 설명합니다.

   | 보는 것 | 파일 | 키 |
   |---|---|---|
   | 사용자가 입력한 글과 모델 응답 | `projects\이름\파일.jsonl` | `message.role`, `message.content`(글 또는 목록), `message.content[].text` |
   | 도구에 넘긴 입력, 도구가 돌려준 결과 | 같은 파일 | `message.content[].input`, `toolUseResult.stdout`, `attachment.content` |
   | 어느 폴더·브랜치에서 한 작업인지 | 같은 파일 | `cwd`, `gitBranch`, `timestamp`, `sessionId`, `version`, `entrypoint` |
   | 어느 계정에 묶인 세션인지 | 같은 파일 | `ownerAccountUuid`, `ownerOrganizationUuid` |
   | 입력 이력과 붙여넣은 내용 | `history.jsonl` | `display`, `project`, `sessionId`, `timestamp`, `pastedContents.번호.id / type / content / contentHash` |
   | 붙여넣기 캐시 | `paste-cache\파일.txt` | (글 파일) |

   `ownerAccountUuid` 와 `ownerOrganizationUuid` 는 개인 계정과 회사 조직 계정을 가르는 단서가 될 수 있고, 값이 어느 계정을 가리키는지는 관리자 로그의 계정·조직 ID 와 대조해서 정합니다. `history.jsonl` 의 붙여넣기 항목은 `content` 에 본문이 든 것과 `contentHash` 만 있는 것이 섞여 있을 수 있습니다(Windows 11 기준). `contentHash` 가 `paste-cache` 의 어느 파일과 이어지는지는 실제 데이터에서 해시 값과 파일 이름·내용을 대조해 확인합니다. 아래는 키 모양만 보여 주는 만든 예시이고 값은 모두 가짜입니다. `type` 값은 비워 두었고, `timestamp` 단위는 실제 데이터에서 확인합니다.

   ```json
   {"display":"첨부한 견적서 요약해 줘","pastedContents":{"1":{"id":1,"type":"...","contentHash":"0000aaaa1111bbbb"}},"project":"C:\\work\\sample-project","sessionId":"00000000-1111-2222-3333-444444444444","timestamp":1700000000000}
   ```

   세션 기록에 도구 결과로 파일 내용이 들어 있으면 사용자가 직접 붙여넣지 않았어도 그 내용이 대화에 들어간 것입니다. Claude Code 는 모든 프롬프트와 모델 출력을 TLS 1.2 이상으로 서버에 보내지만 [4], 도구 결과 하나하나가 서버로 간 범위는 이 사실만으로 단정하지 않습니다. 에이전트가 스스로 읽은 파일을 따로 추려야 할 때는 [AI 에이전트가 무엇을 실행했나](../agents/agent-actions.md) 의 흐름을 함께 씁니다.

5. **서버로 간 뒤 어디에 얼마나 남는지 확인합니다.** Claude Code 의 서버 보관 기간은 소비자 요금제(Free·Pro·Max)에서 모델 개선을 허용하면 5년, 거부하면 30일이고, 상업 요금제(Team·Enterprise·API)는 기본 30일이며 조건을 갖춘 Enterprise 는 제로 데이터 보관(ZDR)을 씁니다 [4]. `/feedback`·`/bug`·`/share` 로 보낸 기록에는 코드를 포함한 대화 기록이 들어가 5년 동안 보관되고, 세션 설문 뒤 대화 기록을 보여 줄지 묻는 질문에 "Yes" 를 고르면 대화 기록, 하위 에이전트 기록, 디스크의 세션 로그가 올라가 최대 6개월 보관됩니다 [4]. Bedrock·Google Cloud Agent Platform 같은 제3자 공급자를 쓰거나 Anthropic 자격 증명이 없는 환경에서는 `/feedback` 보고가 `~/.claude/feedback-bundles/` 에 로컬 파일로 남고 보내지 않습니다 [4]. Claude 가 대신 쓴 피드백 초안은 사용자가 보내기로 고르기 전까지 기기에만 있고 [4], 기기의 `feedback\drafts\파일.json` 에는 `details`, `transcript_ref.session_file`, `cwd`, `status`, `created_at` 키가 있습니다. 초안 파일만 있다면 보냈다는 근거가 되지 못합니다. 보관·삭제 설정의 일반 원리는 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md) 를 봅니다.

6. **로컬 AI 인지 판별합니다.** Ollama 는 로컬에서 돌릴 때 프롬프트와 데이터를 보지 않으므로 [5], 서버 쪽 기록은 기대하지 않고 기기 쪽을 조사합니다. Ollama 의 파일 위치는 [Ollama](../../02-artifacts/local-ai/ollama.md) 페이지를 봅니다. 로컬 AI 앱에 올린 파일은 아래 위치에 남습니다(Windows 11 Pro 24H2 기준, 앱 판은 표에 적음) [6].

   | 앱(시험한 판) | 올린 파일이 남는 곳 | 저장 방식과 삭제 뒤 복구 |
   |---|---|---|
   | LM Studio 0.3.14 | `%UserProfile%\.lmstudio\user-files\파일이름` 과 같은 폴더의 `파일이름.metadata.json` | 원본 형식 그대로 저장합니다. 메타데이터에는 형식, 크기, 원래 이름, SHA-256 값이 있습니다. 앱에서 지운 업로드 50건은 한 건도 되살아나지 않았습니다. |
   | Msty 1.8.5 | `%AppData%\Msty\attachments\` | 원본 형식 그대로 저장합니다. 업로드 메시지를 지워도 파일은 남아서, 지운 업로드 50건이 모두 되살아났습니다. |
   | GPT4All 3.10.0 | `%LocalAppData%\nomic.ai\GPT4ALL\gpt4all-ID.chat` | 올린 파일 내용이 대화 파일 안에 통째로 들어갑니다. 앱에서 지운 대화는 되살아나지 않았습니다. |

   LM Studio 메타데이터의 SHA-256 값은 회사 문서의 해시와 바로 맞춰 볼 수 있습니다. 표의 "되살아나지 않음" 은 앱 화면에서 지운 뒤 디스크에 남은 파일만 본 LangurTrace 시험 결과이고, 볼륨 섀도 복사본과 메모리는 시험 범위에 없었으므로 [6], 그 둘은 따로 확인합니다. 새 판은 저장 위치가 다를 수 있어 실제 기기의 앱 판을 먼저 봅니다. 로컬 AI 에 넣은 자료는 기기 밖으로 나가지 않았을 수 있으므로 "유출" 과 "입력" 을 나눠 적습니다.

7. **타임라인으로 묶어 교차 검증합니다.** 보안 제품의 붙여넣기 시각, 관리자 로그의 업로드 시각, 기기 기록의 `timestamp` 를 한 줄에 놓고 계정과 기기가 같은지 봅니다. 방법은 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 을 따릅니다.

## 흔한 오판

**"Purview `AI interaction` 에 프롬프트가 없으니 넣은 것이 없다."** 이 이벤트는 프롬프트·응답 글을 늘 보여 주지 않고, 연속 항목에 나뉘어 남기도 하며, Exchange Online 사서함이 없는 사용자나 콘텐츠 캡처를 고르지 않은 수집 정책에서는 글이 보이지 않습니다 [1].

**"Endpoint DLP 에 기록이 없으니 넣은 것이 없다."** Endpoint DLP 는 로컬에 저장된 적 없는 데이터를 검사하지 못하고, 오프라인 기기에서 집행된 이벤트는 기기가 다시 연결돼야 활동 탐색기에 보입니다 [2]. 온보딩되지 않은 기기에는 처음부터 기록이 없습니다.

**"감사 로그에 `file_uploaded` 가 있으니 기밀 파일을 올렸다."** 감사 로그에는 파일 내용도 제목도 없고 ID 만 있습니다 [3]. 어떤 파일이었는지는 데이터 내보내기나 기기 기록으로 따로 확인해야 합니다.

**"기기에 대화 본문이 없으니 AI 를 쓰지 않았다."** 웹 채팅처럼 대화 원본이 서버에만 있는 서비스는 기기에 본문을 남기지 않을 수 있습니다. 본문 확인은 서버 쪽으로 넘기고, 기기에서는 방문·붙여넣기 흔적만 봅니다.

**"30일보다 오래된 세션 기록이 없으니 사용자가 지웠다."** Claude Code 는 기본 설정만으로도 30일이 지난 세션 기록을 지웁니다 [4]. 지운 행위를 주장하려면 `cleanupPeriodDays` 를 바꿨는지, 기한 안의 기록이 비었는지를 먼저 봅니다.

**"붙여넣기 항목에 본문이 없으니 붙여넣은 것이 없다."** `history.jsonl` 에는 해시만 남은 붙여넣기 항목이 있을 수 있습니다. 해시만 있어도 붙여넣은 사실 자체는 남습니다.

## 보고서 문장 예

보고서에는 기록으로 확인되는 만큼만 씁니다. 아래 예시의 날짜·계정·파일 이름은 만든 값입니다.

| 피할 문장 | 쓸 문장 |
|---|---|
| 사용자가 고객 명단을 AI 에 유출했다. | 2026-03-14 10:20(UTC) 무렵 user-a 계정으로 로그인한 기기에서 AI 사이트로 붙여넣은 내용이 DLP 규칙 "고객 정보" 와 일치했다는 활동 기록이 있다. 붙여넣은 글 자체는 이 기록에 남지 않았다. |
| 사용자가 설계 문서를 Claude 에 올렸다. | 같은 날 10:22(UTC) 조직 감사 로그에 user-a 계정의 `file_uploaded` 이벤트가 있고, IP·기기 ID 는 조사 대상 기기와 일치한다. 업로드한 파일의 이름과 내용은 감사 로그에 없어 데이터 내보내기로 확인했다. |
| 개발 도구가 소스 코드를 외부로 보냈다. | 조사 대상 기기의 개발 도구 세션 기록에 작업 폴더 C:\work\sample-project 의 파일 내용이 도구 결과로 들어 있다. 이 도구는 프롬프트와 모델 출력을 서버로 보낸다고 공식 문서에 적혀 있다. |

보고서 전체 틀은 [AI 관련 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 를 봅니다.

## 함께 볼 페이지

- [회사가 허용하지 않은 AI를 썼나](shadow-ai.md) — 어떤 AI 를 언제부터 썼는지 찾는 조사
- [그 대화를 한 사람이 누구인가](../attribution/user-attribution.md) — 계정과 실제 사용자를 잇는 방법
- [AI 에이전트가 무엇을 실행했나](../agents/agent-actions.md) — 에이전트가 스스로 읽고 보낸 파일
- [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md) — 증거 파일 속 토큰을 비밀로 다루는 이유
- [조사 절차](../../03-techniques/acquisition/investigation-process.md)

## 참고 문헌

1. Considerations for deploying Microsoft Purview Data Security Posture Management (DSPM) for AI | Microsoft Learn — https://learn.microsoft.com/en-us/purview/dspm-for-ai-considerations
2. Learn about Endpoint data loss prevention | Microsoft Learn — https://learn.microsoft.com/en-us/purview/endpoint-dlp-learn-about
3. Access audit logs | Claude Help Center — https://support.claude.com/en/articles/9970975-how-to-access-audit-logs
4. Data usage | Claude Code Docs — https://code.claude.com/docs/en/data-usage
5. FAQ | Ollama — https://docs.ollama.com/faq
6. Sungjo Jeong, Sangjin Lee, Jungheum Park, "LangurTrace: Forensic analysis of local LLM applications", Forensic Science International: Digital Investigation, 54 (2025), 301987. DOI: 10.1016/j.fsidi.2025.301987 (§4.6.1·§4.6.2·§4.6.4, 표 8, 부록 A·B)
7. lordjabez/claude-export-viewer — https://github.com/lordjabez/claude-export-viewer , `src/claude_export_viewer/models.py`
8. kenn-io/agentsview — https://github.com/kenn-io/agentsview , `internal/parser/claude_ai.go`
