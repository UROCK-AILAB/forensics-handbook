---
title: "프로세스와 열린 파일"
parent: "라이브 대응"
grand_parent: "기법 · 조사 절차·증거 확보"
nav_order: 1990
---

# 프로세스와 열린 파일 (ps·lsof)

켜진 맥에서 `ps` 로 실행 중인 프로세스의 부모 관계·시작 시각·명령줄을 모으고, `lsof` 로 프로세스마다 연 파일과 지웠지만 아직 열려 있는 파일을 모읍니다.

## 언제 쓰나

프로세스 목록은 RFC 3227 휘발성 순서의 2단계(process table)에 들어가서 라이브 대응에서 먼저 모으는 자료입니다. 순서를 정하는 방법은 [휘발성 순서 (Order of Volatility)](order-of-volatility.md)에 있습니다. 의심 프로세스가 아직 돌고 있는지, 누가 띄웠는지, 어떤 파일을 쥐고 있는지 볼 때 쓰고, 소켓 쪽은 [네트워크 연결 (Connections)](connections.md)에서 따로 다룹니다.

## 절차

1. root 권한으로 실행합니다. `lsof` 는 root 가 아니면 자기 프로세스의 파일만 보여 줍니다 [2].
2. 모든 프로세스를 명령줄이 잘리지 않게 모읍니다. `-A` 는 다른 사용자의 프로세스와 제어 터미널이 없는 프로세스까지 보여 주고, `-ww` 는 창 너비와 상관없이 필요한 만큼 출력하며, `-o` 는 칸을 골라 줍니다 [1].

   ```
   ps -Aww -o pid,ppid,uid,user,ruser,lstart,etime,stat,tty,command
   ```

3. 필요하면 환경 변수도 모읍니다. `-E` 를 더하면 환경 변수가 함께 나오지만 프로세스가 실행된 뒤 바뀐 환경은 반영하지 않습니다 [1].
4. 열린 파일 전체를 모읍니다. `-n` 은 네트워크 번호를 호스트 이름으로, `-P` 는 포트 번호를 서비스 이름으로 바꾸지 않아서 [2], 수집하는 동안 이름 조회가 생기지 않도록 이 핸드북은 둘을 함께 줍니다. 멈출 수 있는 커널 함수를 피하는 `-b` 도 있습니다 [2].

   ```
   lsof -nP
   ```

5. 지웠지만(unlink) 아직 열려 있는 파일을 따로 모읍니다. `+L1` 은 링크 수가 1보다 작은 파일을 고르고, `+L` 을 주면 NLINK 칸이 나옵니다 [2].

   ```
   lsof -nP +L1
   ```

6. 의심 프로세스나 폴더를 좁혀 봅니다. `-p` 는 PID로(`^` 를 붙이면 제외), `-u` 는 로그인 이름이나 UID로, `-c` 는 명령 이름으로 고르고(슬래시로 감싸면 정규식), `+D` 는 폴더 아래 전체에서 열린 파일을 찾습니다 [2]. 조건을 여러 개 주면 기본은 OR로 묶이고 `-a` 를 주면 AND로 묶입니다 [2].

   ```
   lsof -nP -a -p <PID> -u <사용자>
   lsof -nP +D <폴더>
   ```

7. 뒤에 스크립트로 읽을 결과는 `-F` 로 필드 출력을 받습니다. 필드 문자는 p(PID), c(명령), f(FD), t(형식), n(이름) 등입니다 [2].
8. 의심 실행 파일은 서명을 확인합니다. `codesign -dr -` 로 코드 요구사항을 얻을 수 있고 [3], 서명과 공증의 뜻은 [서명·공증·무결성 보호 (Code Signing·Notarization·SIP)](../../../01-foundations/protection/codesign-notarization-sip.md)와 [앱 번들 정보 (Info.plist·Code Signature)](../../../02-artifacts/embedded-metadata/app-bundle.md)에서 봅니다.

## 칸 읽기

`ps -o` 에 쓰는 주요 키워드는 아래와 같습니다 [1].

| 키워드 | 뜻 |
|---|---|
| `pid`, `ppid` | 프로세스 ID, 부모 프로세스 ID |
| `uid`, `user` | 유효 UID, 그 사용자 이름 |
| `ruser` | 실제 UID의 사용자 이름 |
| `lstart` | 시작한 정확한 시각. strftime(3)의 `%c` 형식 |
| `start` | 시작 시각. 오래된 프로세스일수록 형식이 달라짐 |
| `etime` | 시작한 뒤 지난 시간 |
| `command`, `args` | 명령과 인자 |
| `comm` | 명령 |
| `tty`, `stat`, `flags` | 제어 터미널, 상태, 플래그(16진) |

상태 칸의 첫 글자는 I(idle), R(runnable), S(sleeping), T(stopped), U(uninterruptible wait), Z(zombie)입니다 [1]. 칸 묶음을 한 번에 주는 옵션도 있어서 `-j`, `-l`, `-v`, `-f` 가 저마다 정해진 칸을 출력하고, `-f` 는 uid, pid, 부모 pid, 최근 CPU 사용, 시작 시각, 제어 tty, 누적 CPU 시간, 명령을 보여 줍니다 [1].

`lsof` 의 기본 출력 칸은 아래와 같습니다 [2].

| 칸 | 뜻 |
|---|---|
| COMMAND | 명령 이름 앞 9글자. `+c` 로 길이를 바꿈 |
| PID, USER | 프로세스 ID, 사용자 |
| FD | cwd·txt·mem·rtd 같은 이름, 또는 숫자와 모드(r/w/u)와 잠금 상태 |
| TYPE | REG·DIR·IPv4·IPv6·unix·PIPE·FIFO·CHR·BLK 등 |
| DEVICE | 장치 번호 |
| SIZE/OFF | 파일 크기 또는 오프셋(바이트) |
| NODE | 로컬 파일의 노드 번호 |
| NAME | 파일 경로나 주소 |

## 함정과 한계

`ps` 는 대부분의 출력 형식에서 명령줄을 자르고, `-f` 와 `-o`·`-O` 를 함께 쓰면 덜 잘립니다 [1]. `-c` 를 주면 명령 칸에 전체 명령줄 대신 실행 파일 이름만 나와서 인자가 빠지니, 증거로 남길 목록에는 쓰지 않습니다 [1]. `lsof` 의 COMMAND 칸도 기본이 9글자라 이름이 긴 프로세스는 `ps` 의 PID와 맞춰 읽습니다 [2].

`lstart` 는 `%c` 형식으로 나오고 [1], 현지 시각인지 UTC인지는 man 페이지에 적혀 있지 않습니다. 출력과 함께 그 맥의 시간대 설정과 수집 시각(UTC)을 적어 두고, 시간대는 [시간대와 시계 설정 (Time Zone·NTP)](../../../02-artifacts/system-account/time-zone.md)에서 확인합니다. `start` 는 오래된 프로세스일수록 형식이 달라져서 [1] 시각 비교에는 `lstart` 를 씁니다.

지워진 파일에는 가능하면 "(deleted)" 표시가 붙지만 [2], 맥에서 실제로 붙는지는 검체에서 확인해야 하므로 지운 파일은 표시 대신 `+L1` 로 찾습니다. 침해된 맥의 `ps`·`lsof` 를 그대로 믿을지는 [라이브 대응 (Live Response)](index.md)의 원칙을 따릅니다.

## 결과를 어떻게 해석하나

두 목록이 수집한 순간의 상태만 담는다는 점은 [휘발성 순서 (Order of Volatility)](order-of-volatility.md)에서 다뤘습니다. 보고서에는 "수집 시각에 PID 몇인 프로세스가 이 명령줄로 실행 중이었고, 이 사용자 권한이었으며, 이 파일을 열고 있었다" 까지만 쓰고, 언제 처음 실행됐는지나 무엇을 했는지는 다른 기록으로 뒷받침합니다. 지난 실행은 [통합 로그의 프로세스 실행 기록 (Process Events)](../../../02-artifacts/execution/unified-log-process.md)과 [KnowledgeC (knowledgeC.db)](../../../02-artifacts/execution/knowledgec/index.md)에서 찾고, 의심 프로세스가 자동 실행으로 올라왔는지는 [실행 에이전트·데몬 (LaunchAgents·LaunchDaemons)](../../../02-artifacts/persistence/launchd/index.md)에서 봅니다.

부모 PID로 이은 관계도 수집 시각의 관계라서, 이 관계만으로 "누가 띄웠다" 고 단정하지 않고 실행 기록과 맞춰 봅니다. 의심 파일을 어떻게 추려 볼지는 [악성 코드 흔적 분석 (Malware Triage)](../../analysis/malware-triage/index.md)에서 이어집니다.

## 참고 문헌

1. ps(1) man page (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/ps.1.html
2. lsof(8) man page, revision 4.91 (Xcode man pages 미러) — https://keith.github.io/xcode-man-pages/lsof.8.html
3. Apple Platform Deployment — Privacy Preferences Policy Control payload settings — https://support.apple.com/guide/deployment/privacy-preferences-policy-control-payload-dep38df53c2a/web
