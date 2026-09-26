---
title: "AI 관련 포렌식 보고서"
parent: "기법 · 보고"
nav_order: 910
---

# AI 관련 포렌식 보고서 (Forensic Report)

AI 서비스에서 찾은 흔적을 보고서로 옮길 때 무엇을 적어야 하는지, 그리고 발견 사실을 기록으로 확인되는 만큼만 쓰는 방법을 다룹니다.

AI 앱은 자주 바뀌어서 이 페이지에 나온 키 이름과 폴더 구조도 앱 버전에 따라 달라질 수 있습니다.

## 언제 쓰나

분석을 마치고 결과를 사건 보고서·감사 보고서·징계 자료·법정 제출 자료로 정리할 때 씁니다. 일반 PC 포렌식 보고서와 뼈대는 같지만, AI 서비스를 다룰 때는 보고서에 따로 밝혀야 할 점이 몇 가지 더 생깁니다.

대화 원본이 기기가 아니라 서비스 서버에만 있는 경우가 많고, 기기에 남은 기록도 앱이 정한 기간이 지나면 저절로 지워질 수 있습니다. 한 대화 안에서도 사람이 친 프롬프트, 사람이 올린 첨부, 모델이 만든 생성물, 에이전트가 스스로 실행한 도구 호출이 섞여 있어서 문장마다 주어를 구분해 써야 합니다. "이 글을 AI가 썼다" 같은 판정은 도구로 확정하기 어려워서 판정의 근거와 한계를 함께 적어야 합니다.

조사 전체의 흐름은 [조사 절차](../acquisition/investigation-process.md)에 있고, 이 페이지는 그 마지막 단계인 보고만 다룹니다.

## 절차

1. **조사 질문과 범위를 적습니다.** 무엇을 밝히려 했는지 질문 한두 개로 적고, 조사한 기기·OS 계정·서비스 계정·기간을 표로 정리합니다. 서비스 회사에 자료를 요청했는지, 계정 데이터 내보내기를 받았는지, 조직 관리자 로그를 받았는지도 여기에 적어 두면 읽는 사람이 증거의 출처를 처음부터 알 수 있습니다. 요청 경로는 [서비스 회사에 대한 데이터 요청](../acquisition/legal-requests.md)과 [계정 데이터 내보내기로 수집](../acquisition/export-collection.md)을 봅니다.

2. **수집 기록과 보관 연속성을 적습니다.** RFC 3227 에 맞춰 누가·언제·어디서 증거를 발견하고 수집했는지, 누가·언제·어디서 다루고 검사했는지, 누가 어느 기간 어떻게 보관했는지, 넘겨줄 때 언제·어떻게 넘겼는지를 기록합니다. 수집한 파일과 내보내기 묶음마다 해시를 계산해 목록에 적고, 계산한 도구와 시각도 함께 남깁니다.

3. **자료를 출처별로 나눠 적습니다.** 같은 대화라도 어디서 얻었느냐에 따라 담긴 내용과 믿을 수 있는 범위가 다릅니다. 보고서에서는 출처를 섞지 말고 아래처럼 나눠 적습니다.

   | 자료 출처 | 담긴 것 | 보고서에 함께 적을 것 |
   |---|---|---|
   | 기기(사용자 프로필 폴더·앱 폴더) | 앱이 남긴 기록 파일, 설정, 캐시 | 경로, 앱 버전, 자동 삭제 설정 여부 |
   | 계정 데이터 내보내기 | 서비스가 계정에 보관한 대화와 사용자 데이터 | 요청 시각, 받은 방법, 받은 파일 해시 |
   | 서비스 회사 제공 자료 | 회사가 법적 요청에 따라 준 자료 | 요청 근거와 날짜, 회사가 밝힌 범위 |
   | 조직 관리자 로그 | 로그인·대화 생성·파일 업로드 같은 행위 기록 | 로그 종류, 내보낸 기간, 내용 포함 여부 |

   관리자 로그에는 대화 본문이 없을 수 있어서 이 구분이 중요합니다. 예를 들어 Claude Enterprise 감사 로그에는 대화·프로젝트의 제목과 내용 없이 고유 ID만 남고, 대화 본문은 별도의 데이터 내보내기로 받습니다. Claude 계정 데이터 내보내기는 메일로 내려받기 링크를 보내고, 링크는 24시간 뒤 만료되며, 내려받으려면 계정에 로그인해 있어야 합니다. 그래서 보고서에는 누가 어떤 권한으로 로그인해 받았는지까지 적어 둡니다. 다른 서비스의 관리자 로그와 내보내기 형식은 [Claude 기업용 감사 로그](../../02-artifacts/network-enterprise/claude-enterprise.md), [ChatGPT 기업용 감사 기록](../../02-artifacts/network-enterprise/chatgpt-enterprise.md), [Microsoft Purview로 본 Copilot 기록](../../02-artifacts/network-enterprise/purview-copilot.md), [계정 데이터 내보내기 형식](../../01-foundations/storage-model/data-export-formats.md)에서 같은 기준으로 확인합니다.

4. **OS·앱 버전·확인 날짜를 적습니다.** AI 앱의 기록 형식은 공개 규격이 없는 경우가 많고 버전마다 키가 바뀔 수 있어서, 해석의 근거가 된 앱 버전을 적어야 나중에 다른 사람이 같은 결론을 확인할 수 있습니다. 앱이 기록 안에 버전을 남기기도 합니다. Claude Code 세션 기록의 대화 줄에는 `version` 키가 있고, 피드백 초안 파일에는 `cli_version` 키가, Claude 데스크톱 앱의 `config.json` 에는 `updaterLastSeenVersion` 키가 있습니다. OS 마다 앱 데이터를 보호하는 방식도 다르니, 보호된 자료를 열었다면 어느 보호 방식이었고 어떤 권한으로 열었는지 적습니다. 보호 방식의 원리는 아래 페이지에 있습니다.

   | OS | 보호 방식 설명 |
   |---|---|
   | Windows | [DPAPI 구조](https://urock-ailab.github.io/forensics-handbook/windows/01-foundations/protection/data-protection-api/index.html), [자격 증명 관리자와 볼트](https://urock-ailab.github.io/forensics-handbook/windows/02-artifacts/credentials/credential-manager-windows-vault.html) |
   | macOS | [키체인](https://urock-ailab.github.io/forensics-handbook/mac/01-foundations/protection/keychain/index.html) |
   | Android | [저장 공간 암호화](https://urock-ailab.github.io/forensics-handbook/android/01-foundations/storage/encryption/index.html) |
   | iOS | [데이터 보호](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/data-protection/index.html), [키체인](https://urock-ailab.github.io/forensics-handbook/ios/01-foundations/storage/keychain.html) |

5. **시각 표기를 하나로 맞춥니다.** 같은 앱 안에서도 파일마다 시각을 적는 방식이 다를 수 있습니다. Claude Code의 입력 이력 `history.jsonl` 은 `timestamp` 를 정수로 적고, 세션 기록 `projects` 아래 `.jsonl` 은 `timestamp` 를 문자열로 적습니다. 보고서 본문에는 한 가지 시간대로 바꾼 값을 쓰고, 부록에는 원래 값과 어느 파일·어느 키에서 읽었는지, 어떤 규칙으로 바꿨는지를 적습니다. 바꾸는 규칙을 알 수 없는 값은 원래 값만 적고, 바꾸지 않았다고 밝힙니다. 여러 기록을 시간순으로 합치는 방법은 [AI 사용 타임라인](../analysis/timeline.md)에 있습니다.

6. **발견 사실을 기록으로 확인되는 만큼만 씁니다.** 기록으로는 "이 계정 프로필 아래 이 앱이 이 시각에 이런 줄을 남겼다" 까지 알 수 있고, 누가 자판을 눌렀는지나 왜 그랬는지는 알 수 없습니다. 문장마다 주어를 사람·계정·앱·에이전트 가운데 무엇으로 삼을지 정하고, 기록이 가리키는 쪽으로 씁니다. 프롬프트·첨부·생성물을 섞어 쓰지 않도록 [프롬프트·첨부·생성물 구분하기](../../01-foundations/concepts/prompt-attachment-output.md)를 따릅니다. 아래 표의 예시는 만든 예시이고 값은 가짜입니다.

   | 기록보다 앞서 나간 문장 | 기록으로 확인되는 만큼의 문장 |
   |---|---|
   | 직원 A가 AI에 기밀 문서를 넣었다. | 사용자 프로필 `demo_user` 의 Claude Code 입력 이력에 2026-09-10 프로젝트 경로 `C:\work\demo-app` 로 입력한 줄이 있고, 붙여넣은 내용이 들어 있다. |
   | AI가 파일을 지웠다. | 같은 세션 기록에 셸 명령을 실행한 도구 호출과 그 결과 줄이 있다. 명령을 사람이 승인했는지는 이 기록만으로 알 수 없다. |
   | 이 보고서는 AI가 썼다. | 이 문서 파일에는 AI 생성 출처 정보나 워터마크가 없다. 출처 정보가 없다는 사실로는 누가 썼는지 판단할 수 없다. |

   키 이름만 보고 뜻을 짐작해 쓰지 않습니다. 예를 들어 Claude Code 세션 기록에는 `attachment` 라는 키가 있지만 훅 실행 결과(훅 이름·종료 코드·출력) 같은 값이 들어 있어서, 사용자가 올린 첨부 파일로 적으면 안 됩니다. 공식 문서에 뜻이 나오지 않는 키는 "키 이름만 확인" 이라고 밝힙니다.

7. **기록이 없을 때는 없는 이유의 가능성을 적습니다.** 기록이 없다는 사실만으로 "사용하지 않았다" 고 쓰지 않습니다. 앱이 정한 기간이 지나 기록이 지워졌거나, 기록을 쓰지 않는 설정이 켜져 있었거나, 대화 원본이 처음부터 서버에만 있었을 수 있습니다. Claude Code는 세션 기록을 기본 30일 보관하고 `cleanupPeriodDays` 로 기간을 바꾸지만 입력 이력 `history.jsonl` 은 이 자동 삭제 대상이 아니며, `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 대화 기록과 입력 이력을 쓰지 않습니다. 웹에서 돌린 Claude Code 클라우드 세션은 Anthropic 가상 머신에서 돌아가서 사용자 PC에 세션 기록이 없을 수 있고, 이때 대화 원본은 서버 쪽에 있습니다. 그 경우 PC에 남는 흔적은 실제 기기로 확인해야 합니다. 브라우저로 쓰는 대화 서비스도 대화 원본이 서비스 서버에 있고 기기에는 브라우저 저장소 흔적만 남을 수 있습니다. 서버 쪽도 영원히 남지 않아서, 예를 들어 Gemini 앱은 임시 채팅과 활동 기록 유지(Keep Activity)를 끈 상태의 채팅을 계정에 72시간 보관합니다. 서비스별 보관 기간은 [대화 기록 보관 설정과 삭제](../../01-foundations/storage-model/retention-deletion.md)와 [AI 서비스의 데이터는 어디에 있나](../../01-foundations/storage-model/where-data-lives.md)에 모아 두었습니다.

8. **확인 범위와 빈자리를 따로 적습니다.** 공식 문서로 확인한 사실, 조사한 기기에서 관찰한 사실, 분석가가 추론한 해석을 섞지 않고 표시를 달리합니다. 관찰한 사실에는 OS·앱 버전·확인 날짜를 붙이고, 추론에는 추론이라고 적습니다. 암호화 등으로 열 수 없었던 자료와 요청했는데 오지 않은 자료도 목록으로 남겨 두면, 읽는 사람이 보고서의 빈자리를 알 수 있습니다.

9. **부록에 붙일 원문을 가립니다.** AI 도구 기록에는 인증 정보와 비밀값이 섞이기 쉽습니다. Windows에서 Claude Code의 `.credentials.json` 은 로그인 자격 증명을 따로 암호화하지 않고 담으며(macOS는 기본으로 키체인에 저장합니다), 대화 중 `.env` 를 읽었거나 비밀값을 출력했으면 그 내용이 세션 기록에 그대로 남습니다. `.credentials.json` 에는 `claudeAiOauth` 아래에 `accessToken`·`refreshToken` 키가 있습니다. 보고서와 부록에는 토큰·키의 값을 옮기지 않고 "있었다" 와 키 이름만 적으며, 원본은 증거물 보관 절차에 따라 따로 다룹니다. 토큰이 남는 곳은 [API 키와 토큰이 남는 곳](../../01-foundations/storage-model/api-keys-tokens.md)을 봅니다.

보고서 뼈대는 아래처럼 잡을 수 있습니다. 만든 예시이고, 사건 번호·기기 이름·사용자 이름·경로는 모두 가짜 값입니다.

```
사건 번호: DEMO-2026-0001
1. 조사 질문
   - 사용자 프로필 demo_user 에서 2026-09-01 ~ 2026-09-15 사이 AI 도구로 사내 문서를 다룬 기록이 있는가
2. 조사 대상과 범위
   - 기기: LAPTOP-DEMO01 (Windows 11), OS 계정 demo_user
   - 서비스 계정: 조직 계정 1개 (관리자 로그 요청, 내보내기 요청)
3. 수집과 보관 연속성
   - 수집물 목록, 해시 (SHA-256), 계산 도구와 시각, 인계 기록
4. 확인 범위
   - 앱 이름과 버전, 확인 날짜, 시간대 변환 규칙
5. 발견 사실 (출처별)
   - 5.1 기기 기록  5.2 계정 내보내기  5.3 관리자 로그
6. 해석과 한계
   - 증명하는 것 / 증명하지 못하는 것 / 빠진 자료
부록: 원래 값 표 (파일 · 키 · 원래 값 · 바꾼 값), 가린 항목 목록
```

## 도구

해시 계산에는 OS에 들어 있는 명령이나 공개 도구를 쓰고, JSON Lines 기록은 `jq` 같은 공개 도구로, SQLite 데이터베이스는 SQLite 명령줄 도구로 열 수 있습니다. 어느 도구를 쓰든 보고서에는 도구 이름과 버전, 실행한 명령이나 질의를 부록에 남겨서 다른 분석가가 같은 결과를 다시 얻을 수 있게 합니다. 여러 기록을 시간순으로 합치는 도구와 방법은 [AI 사용 타임라인](../analysis/timeline.md)과 Windows 판 [타임라인 작성](https://urock-ailab.github.io/forensics-handbook/windows/03-techniques/analysis/timeline/index.html)을 봅니다.

## 함정과 한계

**폴더가 있다고 사용했다고 쓰지 않습니다.** Cursor 사용자 폴더 `%USERPROFILE%\.cursor` 에 `hooks.json` 하나만 있거나, Codex CLI·Gemini CLI 폴더에 대화 기록 파일 없이 설정만 있을 수 있습니다. 폴더는 설치나 설정의 흔적일 뿐이라서, 보고서에는 "설정 파일이 있다" 까지만 쓰고 사용 여부는 다른 기록과 맞춰 판단합니다.

**앱 폴더에 AI와 무관한 파일이 섞일 수 있습니다.** Claude 데스크톱 스토어 앱의 폴더 안 `LocalCache/Local/` 아래에서 Android SDK·NuGet·npm·pip 캐시처럼 다른 도구의 파일이 함께 있을 수 있습니다. 경로가 AI 앱 폴더 안이라는 이유만으로 그 파일을 AI 앱이 만들었다고 쓰지 않습니다.

**평문 기록은 누구나 고칠 수 있습니다.** Claude Code 는 대화 기록과 입력 이력을 암호화하지 않고 저장하며, OS 파일 권한만이 보호 수단입니다. 그래서 기록 내용만 근거로 삼지 말고 파일 시스템 시각이나 서버 쪽 기록과 맞춰 본 결과를 함께 적습니다.

**요약된 화면과 기록 파일은 다를 수 있습니다.** Claude Code에서 대화를 요약해도 원래 메시지는 기록 파일에 그대로 남습니다. 앱 화면을 캡처한 자료와 기록 파일을 함께 냈다면 어느 쪽을 근거로 삼았는지 적습니다.

**편집 흔적이 모든 변경을 담지는 않습니다.** Claude Code의 파일 되돌리기 사본은 Claude의 파일 편집 도구로 바꾼 파일만 추적하고, 셸 명령으로 지우거나 옮긴 파일과 사용자가 직접 바꾼 파일은 추적하지 않습니다. 사본이 없다는 사실로 "파일을 바꾸지 않았다" 고 쓰지 않습니다. 에이전트가 실행한 일을 따라가는 방법은 [AI 에이전트가 무엇을 실행했나](../../04-scenarios/agents/agent-actions.md)에 있습니다.

**서비스마다 공개된 문서의 양이 다릅니다.** 공식 문서가 많은 서비스와 적은 서비스를 함께 다루면 보고서에서 한쪽만 자세하게 쓰기 쉽습니다. 공식 문서가 없는 서비스는 관찰로만 확인했다고 적고, 모든 서비스에 같은 질문을 같은 기준으로 던졌다는 점을 밝힙니다.

## 결과를 어떻게 해석하나

**증명하는 것**은 기록이 있는 범위입니다. 기기 기록은 그 OS 계정 프로필에서 그 앱이 그 시각에 줄을 남겼다는 사실을 보여 주고, 서버 기록과 관리자 로그는 그 서비스 계정에서 그 행위가 있었다는 사실을 보여 줍니다. 관리자 로그가 행위와 ID만 담고 있다면 본문은 내보내기 자료로 따로 확인했는지까지 적어야 증명 범위가 분명해집니다.

**증명하지 못하는 것**도 함께 적습니다. 사용자 프로필 폴더 아래 흔적은 "그 Windows 계정" 까지만 좁혀 주고, 그 계정을 실제로 누가 썼는지는 로그온 기록 같은 다른 흔적과 맞춰 봐야 합니다([그 대화를 한 사람이 누구인가](../../04-scenarios/attribution/user-attribution.md)). 모델이 만든 답을 사용자가 실제로 읽거나 썼는지, 붙여넣은 내용이 기밀이었는지는 기록 밖의 판단이라서 근거를 따로 댑니다.

AI 생성 여부는 가장 조심해서 씁니다. C2PA 출처 정보(Content Credentials)는 출처 정보가 형식에 맞고 조작되지 않았는지만 알려 주고, 그 내용이 참인지는 판단하지 않습니다. 출처 정보를 넣는 일도 선택 사항이라서, 출처 정보가 없다는 사실이 사람이 만들었다는 뜻이 되지 않습니다. 판별 도구의 한계는 [AI가 만든 글·이미지 판별의 한계](../analysis/detection-limits.md)와 [AI 생성물의 출처 정보](../../01-foundations/concepts/c2pa-provenance.md)를 보고, 판정 문장 예는 [이 글·이미지는 AI가 만들었나](../../04-scenarios/attribution/ai-generated.md)를 따릅니다.

## 참고 문헌

- RFC 3227 — Guidelines for Evidence Collection and Archiving — https://www.rfc-editor.org/rfc/rfc3227
- Claude Code Docs — Data usage — https://code.claude.com/docs/en/data-usage
- Claude Code Docs — Explore the .claude directory — https://code.claude.com/docs/en/claude-directory
- Claude Code Docs — Checkpointing — https://code.claude.com/docs/en/checkpointing
- Claude Help Center — How can I export my Claude data? — https://support.claude.com/en/articles/9450526-how-can-i-export-my-claude-data
- Claude Help Center — Access audit logs — https://support.claude.com/en/articles/9970975-how-to-access-audit-logs
- Google — Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961?hl=en
- C2PA — Explainer 2.2 — https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html
