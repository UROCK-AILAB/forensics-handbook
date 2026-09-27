---
title: 처음
layout: minimal
nav_order: -100
permalink: /
---

# 디지털 포렌식 핸드북

디지털 포렌식은 남아 있는 기록으로 지난 일을 다시 맞춰 보는 일입니다. 하지만 기록은 늘 일부만 남고, 남은 기록으로 알 수 있는 것에도 한계가 있습니다. 파일을 연 흔적이 있어도 누가 열었는지는 알 수 없고, 로그인 기록이 있어도 그 사람이 그 자리에 있었다고 단정할 수는 없습니다. 그래서 이 핸드북에는 흔적이 어디에 남는지뿐 아니라, 왜 남는지, 그 기록으로 어디까지 말할 수 있는지를 함께 적었습니다. 보고서를 쓸 때 확인한 것보다 앞서 나가지 않도록, 곁에 두고 찾아보는 책이 되면 좋겠습니다. 포렌식을 공부하는 분과 현업에서 사건을 분석하는 분을 함께 생각하며 썼습니다.

사건 하나가 기기 한 대에서 끝나는 경우는 드뭅니다. PC 에서 시작한 조사가 휴대전화로 이어지고, 메일과 클라우드를 거쳐 요즘은 AI 서비스와 나눈 대화까지 살펴보게 됩니다. 그래서 기기와 서비스를 따로 나누지 않고, 흔적이 이어지는 대로 따라 읽을 수 있게 엮었습니다.

운영체제와 앱은 버전이 바뀔 때마다 기록하는 방식도 조금씩 바뀝니다. 어제까지 있던 파일이 새 버전에서는 없어지기도 합니다. 그래서 페이지마다 기준 버전과 직접 확인하는 방법을 적어 두었습니다. 이 핸드북은 조사의 출발점으로 삼고, 마지막 확인은 꼭 실제 데이터로 해 주세요.

이 핸드북은 많은 분의 작업 덕분에 만들 수 있었습니다. 분석 도구를 공개한 개발자, 실험 결과를 논문으로 남긴 연구자, 기술 문서를 공개한 회사가 없었다면 쓸 수 없었을 것입니다. 참고한 자료는 페이지마다 참고 문헌에 밝혀 두었습니다.

틀린 곳이나 달라진 동작을 발견하면 [GitHub 이슈](https://github.com/UROCK-AILAB/forensics-handbook/issues)로 알려 주십시오. 궁금한 점이나 제안은 [GitHub 토론](https://github.com/UROCK-AILAB/forensics-handbook/discussions)에 남겨 주시면 됩니다. 함께 고쳐 가며 오래 쓸 수 있는 핸드북으로 만들어 가겠습니다.

## 핸드북

<!-- 핸드북 목록 시작 -->

| 핸드북 | 다루는 것 |
|---|---|
| [Windows](https://urock-ailab.github.io/forensics-handbook/windows/) | NTFS·레지스트리·이벤트 로그부터 브라우저·메신저까지 Windows PC 에 남는 흔적 |
| [macOS](https://urock-ailab.github.io/forensics-handbook/mac/) | APFS·통합 로그·plist 와 macOS 앱에 남는 흔적 |
| [Linux](https://urock-ailab.github.io/forensics-handbook/linux/) | 로그인·명령 실행·지속성·로그 중심의 서버와 데스크톱 흔적 |
| [Android](https://urock-ailab.github.io/forensics-handbook/android/) | Android 기기의 앱·통신·위치·사용 기록 |
| [iOS](https://urock-ailab.github.io/forensics-handbook/ios/) | iPhone 의 앱·통신·위치·사용 기록 |
| [Cloud](https://urock-ailab.github.io/forensics-handbook/cloud/) | Microsoft 365·Google Workspace·AWS·Azure·Google Cloud·업무용 SaaS 의 로그 |
| [AI 서비스](https://urock-ailab.github.io/forensics-handbook/ai/) | ChatGPT·Claude·Copilot·Gemini 같은 AI 서비스를 쓰면 기기와 계정에 남는 흔적 |

<!-- 핸드북 목록 끝 -->

## 이용 조건

이 핸드북의 글은 [크리에이티브 커먼즈 저작자표시 4.0 국제 라이선스(CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.ko){:target="_blank" rel="license noopener noreferrer"}를 따릅니다. 출처(주식회사 유락, 디지털 포렌식 핸드북, 해당 페이지 주소)를 밝히면 상업적 목적을 포함해 자유롭게 옮기고 고쳐 쓸 수 있습니다. 사이트를 만드는 코드는 [MIT 라이선스](https://github.com/UROCK-AILAB/forensics-handbook/blob/main/LICENSE-CODE){:target="_blank" rel="noopener noreferrer"}를 따릅니다.

&copy; 2026 [주식회사 유락](https://urock.kr/){:target="_blank" rel="noopener noreferrer"}
