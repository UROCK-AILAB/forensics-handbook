---
title: "대화 기록 보관 설정과 삭제"
parent: "기반 · 저장 구조"
nav_order: 40
---

# 대화 기록 보관 설정과 삭제 (Retention·Deletion)

> 확인 날짜: 2026-09. 공식 문서는 2026-09-25 에 열어 읽었고, 문서 마지막 수정일은 Claude 개인정보 문서가 2026-07-01, Gemini 개인정보 문서가 2026-09-24 입니다. ChatGPT 도움말은 이 쪽을 쓰면서 열지 못해서(접근 거부) ChatGPT 의 보관 기간은 싣지 않았습니다. 기기 관찰은 Windows 11(빌드 26200) 한 대에서 설정 파일의 키 이름만 본 결과이고, 값과 앱 버전은 적어 두지 않았습니다. 관찰로 확인한 내용에는 "(확인 범위: Windows 11, 2026-09)" 를 붙였습니다.

## 한 줄 요약

AI 대화 기록은 서버에서는 서비스 회사의 보관 정책과 사용자의 설정에 따라, 기기에서는 도구의 자동 정리 설정과 사용자의 삭제에 따라 따로 사라지고, 목록에서 지운 대화도 용도에 따라 서버에 몇 년씩 남는 경우가 있어서 "지웠다" 와 "없다" 를 나눠 적어야 합니다.

## 이 형식을 쓰는 아티팩트

서버 쪽은 [Claude](../../02-artifacts/chat-services/claude/index.md), [Gemini](../../02-artifacts/chat-services/gemini/index.md), [ChatGPT](../../02-artifacts/chat-services/chatgpt/index.md) 같은 채팅 서비스의 계정 기록이 대상이고, 기기 쪽은 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 처럼 대화를 기기에 남기는 도구와 데스크톱 앱의 데이터 폴더가 대상입니다. 어느 쪽에 원본이 있는지는 [AI 서비스의 데이터는 어디에 있나](where-data-lives.md) 에서 먼저 가립니다.

## 구조

### 서버 쪽 — 서비스별 보관 기간

**Claude 개인용(Free·Pro·Max).** 사용자가 대화를 지우면 대화 목록에서는 바로 사라지고, 서버 저장소에서는 30일 안에 지웁니다 [1]. 이와 별개로 용도에 따라 더 오래 남는 기록이 있고, 법적 요구나 분쟁 해결에 필요하면 아래 기간보다 더 오래 보관할 수 있습니다 [1].

| 기록 | 보관 기간 | 근거 |
|---|---|---|
| 사용자가 지운 대화 | 목록에서 바로 사라지고 서버 저장소에서는 30일 안에 삭제 | [1] |
| 모델 개선 설정을 켠 뒤 만든 대화 | 비식별 형태로 모델 학습 파이프라인에 최대 5년 | [1] |
| 사용 정책 위반으로 자동 표시된 대화 | 입력·출력 최대 2년, 안전 분류 점수 최대 7년 | [1] |
| 피드백으로 보낸 내용 | 5년 | [1] |
| 시크릿 (Incognito) 대화 | 설정과 관계없이 모델 개선에 쓰지 않음. 서버 보관 기간은 확인 못 함 | [1] |

**Claude Code 의 서버 쪽 기록.** 개인 계정(Free·Pro·Max)은 모델 개선을 허용하면 5년, 거부하면 30일 보관하고, 상업 계정(Team·Enterprise·API)은 기본 30일이며 무보관(ZDR)은 자격을 확인한 뒤 조직별로 켭니다 [3]. `/feedback`·`/bug`·`/share` 로 보낸 대화는 5년 보관하고, 세션 품질 설문 뒤 기록 공유에 동의해 올린 기록은 6개월까지 보관합니다 [3].

**Gemini 앱.** 대화는 "Keep Activity" 가 켜져 있을 때 계정의 "Gemini Apps Activity" 에 저장되고, 활동 자동 삭제의 기본값은 18개월이며 3개월·36개월·자동 삭제 안 함으로 바꿀 수 있습니다 [2]. Keep Activity 를 끈 상태의 대화와 임시 대화 (Temporary chat) 도 응답과 서비스 보호를 위해 계정에 72시간 남고, 임시 대화는 Google 모델 학습에 쓰지 않습니다 [2]. 사람 검토자가 본 대화는 언어·기기 종류·위치 정보·피드백과 함께 최대 3년 남고, 사용자가 활동을 지워도 함께 지워지지 않습니다 [2]. 활동은 `myactivity.google.com/product/gemini` 에서 관리합니다 [2].

**ChatGPT.** 보관 기간, 임시 채팅, 삭제 뒤 처리는 도움말을 열지 못해 확인하지 못했습니다.

### 기기 쪽 — 로컬 도구의 자동 정리

Claude Code 는 세션 기록을 `cleanupPeriodDays` 로 정한 기간이 지나면 지우고, 기본값은 30일이며 최소값은 1입니다(0 은 설정 검증에서 거부) [4]. 무엇을 지우고 무엇을 남기는지는 문서가 나눠 적고 있습니다 [4].

| 자동 정리로 지우는 것 | 자동 정리로 지우지 않는 것 |
|---|---|
| 세션 기록 `.jsonl` 과 그 변형, `subagents/`, `tool-results/`, `file-history/` 아래 세션별 폴더, `debug/`, `paste-cache/`, `image-cache/` 등 | `history.jsonl`(입력 이력), `stats-cache.json`(사용량 통계), `backups/`, `jobs/`, `daemon/`, 자동 메모리 |

데스크톱 앱이나 Cowork 에서 시작했거나 마지막으로 이어 간 세션 기록은 기본으로 기한 없이 남고, `desktopSessionCleanupPeriodDays` 로 따로 정합니다(문서 기준 v2.1.248 부터) [4]. 설정 파일을 읽지 못했거나 `--bare` 로 실행하면 정리를 멈추고, 관리 정책이 `cleanupPeriodDays` 를 주면 그 값으로 정리합니다 [4]. 사용자가 직접 지우는 방법으로는 `claude project purge` 가 있고, 그 프로젝트의 기록·자동 메모리·세션별 폴더와 함께 `history.jsonl` 의 해당 줄과 `~/.claude.json` 의 프로젝트 항목까지 지웁니다 [4]. `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 처음부터 기록과 입력 이력을 쓰지 않습니다 [4].

아래는 설정 파일에서 정리 기간 키가 어떻게 보이는지 보이려고 만든 예시이고, 값은 가짜입니다.

```json
{
  "cleanupPeriodDays": 14
}
```

`stats-cache.json` 은 자동 정리 대상이 아니고 [4], 이 PC 의 파일에는 `dailyActivity[].date`·`messageCount`·`sessionCount`·`toolCallCount`, `firstSessionDate`, `hourCounts`, `longestSession`, `modelUsage`, `totalMessages`, `totalSessions` 같은 키가 있었습니다(확인 범위: Windows 11, 2026-09). 세션 기록이 지워진 뒤에도 지워진 세션의 수치가 이 통계에 그대로 남는지는 확인하지 못했습니다. 기록 구조의 자세한 내용은 [Claude Code](../../02-artifacts/dev-agents/claude-code/index.md) 쪽에서 다룹니다.

Claude 데스크톱의 `claude_desktop_config.json` 에는 정수 값을 담는 `preferences.ccAutoArchiveInactiveDays` 키가 있었습니다(확인 범위: Windows 11, 2026-09). 이름으로 보아 쓰지 않은 세션을 며칠 뒤 보관 처리하는 설정으로 보이지만, 이 "보관(archive)" 이 기기의 파일을 지우는 일인지는 확인하지 못했습니다.

### 기기 쪽 삭제의 한계

앱을 지워도 앱의 데이터 폴더가 남는 경우가 있습니다. WebView2 앱은 스토어 앱과 ClickOnce 앱을 빼면 앱을 지워도 사용자 데이터 폴더를 자동으로 지우지 않고, 자세한 규칙은 [Electron·웹뷰 앱의 저장 구조](electron-webview.md) 에 있습니다. 서버에서 대화를 지웠을 때 기기의 IndexedDB·Local Storage·캐시에서도 함께 사라지는지는 이 쪽을 쓰면서 확인하지 못했고, 남은 조각을 찾는 방법은 [대화 내용 되살리기](../../03-techniques/analysis/content-recovery.md) 에서 다룹니다.

## 읽는 법

1. 계정 종류를 먼저 확인합니다. Claude Code 처럼 개인 계정과 조직(Team·Enterprise·API) 계정의 보관 기간이 다른 서비스가 있습니다 [3].
2. 조사 대상 기간에 켜져 있던 설정을 확인합니다. Claude 의 모델 개선 설정, Gemini 의 Keep Activity 와 자동 삭제 기간처럼 보관 기간을 바꾸는 설정은 지금 값이 아니라 그 당시 값이 기준입니다.
3. 대화를 지운 시각과 지금 날짜를 놓고, 위 표의 기간에 비추어 서버에 아직 남아 있을 수 있는 기록을 가립니다. 남아 있을 수 있다면 [서비스 회사에 대한 데이터 요청](../../03-techniques/acquisition/legal-requests.md) 을 서두릅니다.
4. 기기 쪽은 `~/.claude/settings.json` 같은 설정 파일에서 정리 기간 키를 읽고, 남아 있는 가장 오래된 세션 기록 파일의 날짜와 맞춰 봅니다. 정리 기간보다 오래된 기록이 없다면 자동 정리로 사라진 것일 수 있고, `history.jsonl` 과 `stats-cache.json` 에서 그 기간의 흔적을 찾습니다.

## 포렌식에서 중요한 점

**목록에서 사라진 것과 서버에서 사라진 것은 다릅니다.** Claude 는 지운 대화를 목록에서 바로 감추지만 서버 저장소에서는 30일 안에 지우고 [1], Gemini 는 사람 검토를 거친 대화를 활동 삭제와 별개로 최대 3년 남깁니다 [2]. 사용자가 "지웠다" 고 말해도 서버 쪽 기록이 남아 있을 수 있어서, 삭제 시각과 요청 시각을 함께 적습니다.

**기록을 끈 것과 지운 것은 흔적이 다릅니다.** Claude Code 는 `CLAUDE_CODE_SKIP_PROMPT_HISTORY` 를 켜면 처음부터 기록을 쓰지 않고 [4], Gemini 는 Keep Activity 를 끈 대화도 72시간은 계정에 남깁니다 [2]. 기록이 비어 있다면 삭제 흔적을 찾기 전에 기록을 끄는 설정이 있었는지부터 봅니다.

**자동 정리 뒤에도 남는 파일이 있습니다.** Claude Code 의 자동 정리는 입력 이력과 사용량 통계를 지우지 않아서 [4], 세션 기록이 없는 기간의 사용 시기와 규모를 이 두 파일로 가늠할 수 있습니다.

## 함정

**"30일 안에" 는 정확한 삭제 날짜가 아닙니다.** 문서는 상한만 적고 있어서, 지운 지 30일이 안 된 대화가 서버에 남아 있다고 단정하지도, 이미 사라졌다고 단정하지도 않습니다.

**비식별 학습 데이터는 계정 기록이 아닙니다.** Claude 의 모델 개선용 대화는 비식별 형태로 학습 파이프라인에 남는다고 적혀 있고 [1], 이 데이터가 계정 내보내기나 서비스 회사 회신에 들어가는지는 확인하지 못했습니다. 최대 5년이라는 기간을 계정 기록이 5년 남는다는 뜻으로 읽지 않습니다.

**데스크톱에서 시작한 세션은 정리 규칙이 다릅니다.** Claude Code 기록 가운데 데스크톱 앱·Cowork 세션은 `cleanupPeriodDays` 가 아니라 `desktopSessionCleanupPeriodDays` 를 따라서 [4], 같은 폴더 안에서도 기록마다 남은 기간이 다를 수 있습니다.

**문서는 바뀝니다.** 보관 기간은 서비스 회사가 고치는 정책이라서 조사 대상 기간에 적용되던 문서 판을 확인하고, 확인한 날짜를 보고서에 적습니다.

## 도구

설정 파일의 정리 기간 키는 `jq` 같은 공개 도구로 뽑고, 세션 기록 파일의 날짜 목록은 OS 기본 명령으로 뜬 뒤 [AI 사용 타임라인](../../03-techniques/analysis/timeline.md) 에 올립니다. 서버 쪽 보관 정책은 공개 문서를 저장해 둔 사본(날짜가 찍힌 PDF 나 웹 보관본)을 보고서에 붙입니다.

## 참고 문헌

1. Claude Privacy Center — How long do you store my data? — https://privacy.claude.com/en/articles/10023548-how-long-do-you-store-my-data
2. Gemini Apps Help — Gemini Apps Privacy Hub — https://support.google.com/gemini/answer/13594961?hl=en
3. Claude Code Docs — Data usage — https://code.claude.com/docs/en/data-usage
4. Claude Code Docs — .claude 폴더 참조 (claude-directory) — https://code.claude.com/docs/en/claude-directory
