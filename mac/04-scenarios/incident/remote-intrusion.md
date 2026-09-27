---
title: "원격 접속 침입 확인"
parent: "시나리오 · 침해 사고"
nav_order: 2560
---

# 원격 접속 침입 확인 (Remote Intrusion)

누군가 SSH 나 화면 공유로 밖에서 이 맥에 들어왔는지, 다시 들어올 수 있게 무엇을 남겼는지, 이 맥을 발판으로 다른 맥에 접속했는지 묻는 조사를 다룹니다. 원격 로그인·화면 공유·원격 관리가 켜져 있었는지 먼저 확인하고, `~/.ssh/authorized_keys`, `/etc/ssh/sshd_config`, 로그인 때 실행되는 스크립트와 환경 변수 파일을 차례로 봅니다. 그다음 통합 로그에서 로그인 기록을, 화면 공유 클라이언트 plist 와 known_hosts 에서 나간 접속을 찾고, 파일 시스템 이벤트의 변경 시각과 함께 타임라인에 올립니다.

## 조사 질문

누군가 SSH 나 화면 공유 (Screen Sharing) 로 밖에서 이 맥에 들어왔는지, 들어왔다면 다음에 다시 들어올 수 있게 무엇을 남겼는지 묻습니다. 반대 방향도 함께 묻는데, 침입한 쪽이 이 맥을 발판으로 삼아 다른 맥에 접속했는지도 흔적으로 남기 때문입니다. 이 페이지는 SSH 서버 쪽 설정 파일과 화면 공유 클라이언트 기록을 중심으로 조사 순서를 다루고, 원격 접속 서비스 전체의 아티팩트는 [원격 접속](../../02-artifacts/network/remote-access/index.md) 페이지로 넘깁니다.

## 먼저 확인할 것

OS 버전부터 적어 둡니다. 이 페이지의 SSH 파일 위치와 동작은 macOS 12 판 sshd(8) 매뉴얼 기준이고 [1], 다른 버전은 실제 기기에서 확인합니다. 원격 로그인과 원격 관리가 켜져 있었는지 확인하는 방법은 [원격 접속](../../02-artifacts/network/remote-access/index.md) 페이지에 있습니다.

사용자와 수집 범위도 정합니다. SSH 공개키 목록과 로그인 스크립트는 사용자 홈의 `~/.ssh/` 아래에 따로 있고, 서버 설정과 호스트 키는 `/etc/ssh/` 아래에 있어서 [1], 모든 사용자 홈과 `/etc/` 를 함께 수집합니다. 화면 공유 클라이언트 기록은 사용자 컨테이너 안에 있습니다 [2]. 라이브 대응이 가능하면 `sshd -T` 로 설정 파일을 검사해 기본값까지 반영한 유효 설정을 출력해 저장해 둡니다 [1]. 시각은 [시간대와 시계 설정](../../02-artifacts/system-account/time-zone.md) 에서 정한 기준으로 맞춥니다.

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 원격 로그인·화면 공유·원격 관리 켜짐 여부 | 밖에서 들어올 길이 열려 있었는지 | [원격 접속](../../02-artifacts/network/remote-access/index.md) |
| 2 | `~/.ssh/authorized_keys` | 비밀번호 없이 로그인할 수 있게 등록한 공개키 | [SSH 키와 접속 목록](../../02-artifacts/credentials/ssh-keys.md) |
| 3 | `/etc/ssh/sshd_config` | SSH 서버 설정 | 이 페이지 아래 표 |
| 4 | `~/.ssh/rc`, `/etc/ssh/sshrc`, `~/.ssh/environment` | 로그인 때 실행되는 스크립트와 환경 변수 | 이 페이지 아래 표 |
| 5 | 통합 로그의 인증 기록 | 로그인 성공·실패 시각과 출발지 | [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md) |
| 6 | 화면 공유 클라이언트 plist, known_hosts | 이 맥에서 다른 컴퓨터로 나간 접속 | 이 페이지 아래 표, [SSH 키와 접속 목록](../../02-artifacts/credentials/ssh-keys.md) |
| 7 | 파일 시스템 이벤트 | 위 파일들이 생기거나 바뀐 시각 | [파일 시스템 이벤트](../../02-artifacts/filesystem/fsevents/index.md) |

### SSH 서버 쪽 파일

| 경로 | 담긴 것 |
|---|---|
| `~/.ssh/authorized_keys` | 공개키 인증 목록. 줄마다 `restrict`, `no-pty`, `no-port-forwarding` 같은 제한 옵션이 붙을 수 있습니다 [1] |
| `/etc/ssh/sshd_config` | sshd 설정 [1] |
| `~/.ssh/rc` | 사용자가 로그인할 때 실행되는 스크립트. 설정의 `PermitUserRC` 가 켜져 있을 때 실행됩니다 [1] |
| `/etc/ssh/sshrc` | 로그인 때 실행되는 시스템 쪽 스크립트. 사용자의 `~/.ssh/rc` 가 없을 때 실행됩니다 [1] |
| `~/.ssh/environment` | 사용자 환경 변수 파일. 설정의 `PermitUserEnvironment` 가 켜져 있을 때만 읽고, 기본값은 꺼져 있습니다 [1] |
| `/etc/nologin` | 이 파일이 있으면 root 외 사용자의 로그인을 막습니다 [1] |
| `/etc/ssh/ssh_host_ecdsa_key`, `ssh_host_ed25519_key`, `ssh_host_rsa_key` 등과 짝이 되는 `.pub` | 호스트 키. 개인키는 root 만 읽습니다 [1] |

`~/.ssh/rc` 와 `/etc/ssh/sshrc` 는 로그인할 때마다 실행되는 자리라서, 침입 흔적이면서 동시에 지속성 자리로도 볼 수 있습니다. 지속성 전체 목록은 [악성 코드 지속성 찾기](persistence.md) 에 있습니다.

### 화면 공유 클라이언트 기록

이 맥에서 다른 맥으로 화면 공유를 연 기록은 아래 plist 에 남습니다 [2].

```
~/Library/Containers/com.apple.ScreenSharing/Data/Library/Preferences/com.apple.ScreenSharing.plist
```

이 파일의 `connectionsStore` 아래에는 아래 키가 있습니다 [2].

| 키 | 담긴 것 |
|---|---|
| `connectionGroups` | 연결 묶음. `groupName`, `members` |
| `connectionDetails` | 호스트 UUID 마다 `networkAddress`, `address`, `username`, `displayName` |
| `sessionMetadatas` | 호스트 UUID 마다 `lastConnectedDate` |

`lastConnectedDate` 는 plist 날짜형입니다 [2]. plist 날짜형을 읽는 기준은 [맥의 시각 값](../../01-foundations/value-decoding/mac-time-values.md) 을 따릅니다.

## 분석 흐름

1. 원격 로그인·화면 공유·원격 관리가 켜져 있었는지 확인합니다. 모두 꺼져 있었으면 언제 켜고 껐는지부터 찾습니다.
2. 사용자마다 `~/.ssh/authorized_keys` 를 열어 키 목록을 조직이 관리하는 키와 대조합니다. 모르는 키가 있으면 그 줄의 옵션과 파일이 바뀐 시각을 적습니다.
3. `/etc/ssh/sshd_config` 에서 인증 방식과 허용 범위가 바뀌었는지 봅니다. 라이브면 `sshd -T` 출력과 파일 내용을 나란히 둡니다.
4. `~/.ssh/rc`, `/etc/ssh/sshrc`, `~/.ssh/environment` 가 있는지 확인하고, 있으면 내용과 생긴 시각을 기록합니다. 스크립트가 부르는 실행 파일은 [악성 코드 흔적 분석](../../03-techniques/analysis/malware-triage/index.md) 절차로 살핍니다.
5. 통합 로그에서 원격 로그인 성공·실패 기록을 찾아 출발지 주소와 시각을 정리합니다. 찾는 방법은 [통합 로그에서 찾을 것](../../02-artifacts/logs/unified-log-events/index.md) 에 있습니다.
6. 나간 접속을 확인합니다. 화면 공유 클라이언트 plist 의 `connectionDetails` 와 `lastConnectedDate` 를 이어 어느 주소에 어떤 사용자 이름으로 언제 접속했는지 정리하고, SSH 로 나간 접속은 [SSH 키와 접속 목록](../../02-artifacts/credentials/ssh-keys.md) 에서 봅니다.
7. 키 등록, 설정 변경, 로그인 기록, 나간 접속을 [타임라인](../../03-techniques/analysis/timeline/index.md) 에 올리고, 그 시간대의 명령 기록은 [터미널 명령 기록](../../02-artifacts/execution/shell-history.md) 에서 찾습니다.

## 흔한 오판

- **`authorized_keys` 에 모르는 키가 있으니 그 키로 들어왔다고 쓰는 경우.** 이 파일은 로그인할 수 있게 등록한 목록이고, 실제 로그인은 인증 기록으로 따로 확인합니다.
- **`sshd_config` 파일만 보고 적용된 설정을 단정하는 경우.** 파일에 적지 않은 항목은 기본값이 쓰이고, 기본값까지 반영한 유효 설정은 `sshd -T` 가 출력합니다 [1]. 이 명령은 그 시점의 설정 파일을 다시 읽으므로, 이미 돌고 있던 sshd 가 읽은 설정과는 다를 수 있습니다. 이미지로만 조사할 때는 파일 내용이 곧 적용 설정이라고 쓰지 않고, 파일에 적힌 설정이라고 씁니다.
- **화면 공유 plist 를 들어온 접속 기록으로 읽는 경우.** 이 plist 는 이 맥이 클라이언트로 다른 컴퓨터에 접속한 기록입니다 [2]. 이 맥으로 들어온 화면 공유는 서버 쪽 기록에서 찾습니다.
- **호스트 키가 만들어진 시각을 원격 로그인을 처음 켠 때로 쓰는 경우.** 그렇게 해석하는 경우가 있지만, 이 시각만으로 원격 로그인을 켠 때를 단정하지 않고 분석 대상 맥의 다른 기록과 맞춰 봅니다.
- **`/etc/nologin` 이 있으니 아무도 로그인하지 못했다고 보는 경우.** 이 파일은 root 외 로그인만 막습니다 [1]. 파일이 언제 생겼는지와 root 로그인 기록을 함께 봅니다.

## 보고서 문장 예

> 사용자 ○○의 `~/.ssh/authorized_keys` 에 조직의 키 목록에 없는 공개키 한 줄(주석 "○○")이 있고, 파일 시스템 이벤트에서 이 파일이 바뀐 기록은 ○○○○-○○-○○ ○○:○○:○○(UTC)입니다. 이 기록은 그 시각 이후 해당 키로 이 계정에 SSH 공개키 로그인이 가능하도록 등록되어 있었다는 사실을 보여 주지만, 그 키로 실제 로그인했는지는 인증 기록을 확인한 뒤에 따로 적습니다.

## 함께 볼 페이지

- [원격 접속 (Remote Access)](../../02-artifacts/network/remote-access/index.md) — 원격 로그인·화면 공유·원격 관리 서비스의 흔적 전체
- [SSH 키와 접속 목록 (SSH Keys·known_hosts)](../../02-artifacts/credentials/ssh-keys.md) — 키 파일과 나간 SSH 접속
- [통합 로그에서 찾을 것 (Unified Log Events)](../../02-artifacts/logs/unified-log-events/index.md) — 인증 기록
- [그 시각에 맥을 쓴 사람이 누구인가 (User Attribution)](../activity/user-attribution.md) — 원격 사용자와 앞에 앉은 사용자 가르기
- [권한 상승과 TCC 우회 흔적 (Privilege·TCC Bypass)](privilege-tcc-bypass.md) — 들어온 뒤 권한을 넓혔는지

## 참고 문헌

1. sshd(8) man page (Xcode man page 모음, macOS 12 판) — https://keith.github.io/xcode-man-pages/sshd.8.html
2. mac_apt, plugins/screensharing.py — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/screensharing.py
