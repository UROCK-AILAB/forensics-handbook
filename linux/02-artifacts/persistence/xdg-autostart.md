---
title: "데스크톱 자동 실행"
parent: "아티팩트 · 지속성"
nav_order: 580
---

# 데스크톱 자동 실행 (XDG Autostart)

사용자가 그래픽 데스크톱에 로그인할 때 저절로 실행할 프로그램을 `.desktop` 파일로 적어 두는 자리이고, 사용자 한 명 또는 시스템 전체에 지속성을 심는 데 쓰일 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

데스크톱 자동 실행 명세(Desktop Application Autostart Specification)는 자동 실행 디렉터리에 놓인 `.desktop` 파일의 프로그램을, 사용자가 로그인한 뒤 데스크톱 환경이 시작될 때 실행하도록 정합니다[1]. 메신저·업데이트 알림·입력기처럼 로그인과 함께 떠야 하는 프로그램이 패키지 설치로 이 파일을 깔고, 사용자가 설정 화면에서 "시작 프로그램" 을 추가해도 같은 자리에 파일이 생깁니다.

파일 하나가 알려 주는 것은 "무엇을(`Exec`), 어떤 조건에서(`Hidden`·`OnlyShowIn`·`NotShowIn`·`TryExec`) 실행하도록 설정했는가" 입니다. 실행했다는 기록은 이 파일에 남지 않고, systemd 가 자동 실행을 맡는 시스템에서는 사용자 저널에 따로 남습니다(아래 "systemd 가 맡는 경우" 참고).

같은 명세에는 이동식 매체를 마운트할 때 매체 루트의 `.autorun`, `autorun`, `autorun.sh` 가운데 처음 찾은 파일 하나를 실행하는 규칙도 있습니다[1]. 이 경우 데스크톱 환경은 실행 전에 반드시 사용자에게 확인을 받아야 하고, 정책에 따라 이 파일을 아예 무시해도 됩니다[1].

## 위치와 버전별 차이

자동 실행 디렉터리는 `$XDG_CONFIG_DIRS/autostart` 이고, 사용자 설정 디렉터리(`$XDG_CONFIG_HOME`)도 여기에 들어갑니다[1][2]. `$XDG_CONFIG_HOME` 이 비어 있으면 `$HOME/.config` 를, `$XDG_CONFIG_DIRS` 가 비어 있으면 `/etc/xdg` 를 씁니다[2]. 그래서 환경 변수를 따로 두지 않은 시스템의 기본 위치는 아래 두 곳입니다[1].

| 범위 | 기본 경로 | 누가 만드나 |
|---|---|---|
| 사용자 한 명 | `~/.config/autostart/*.desktop` | 그 사용자(설정 화면, 직접 만든 파일) |
| 시스템 전체 | `/etc/xdg/autostart/*.desktop` | 패키지, 관리자 |

같은 파일 이름이 두 디렉터리에 다 있으면 더 중요한 디렉터리의 파일만 쓰고, 사용자 디렉터리가 시스템 디렉터리보다 중요합니다[1]. `$XDG_CONFIG_DIRS` 에 디렉터리를 여러 개 적으면 적은 순서가 중요도 순서입니다[2]. 로그인 세션이 이 변수를 다르게 잡았다면 그 디렉터리들의 `autostart` 도 함께 읽으므로, 라이브 시스템에서는 데스크톱 세션 프로세스의 환경 변수를 확인합니다([실행 중인 프로세스](../execution/proc.md)).

UAC 는 표준 두 곳 말고도 `/usr/share/autostart`, `~/.local/share/autostart`, 그리고 KDE 가 쓰는 비표준 디렉터리 `~/.config/autostart-scripts` 를 함께 모읍니다[4]. ForensicArtifacts 의 `XDGAutostartEntries` 는 `/etc/xdg/autostart/*.desktop` 과 `~/.config/autostart/*.desktop` 두 곳만 정의합니다[5]. UAC 의 `desktop.yaml` 은 사용자 홈 아래 깊이 6까지의 `*.desktop` 파일을 모두 모으므로, 자동 실행 디렉터리 밖에 놓인 `.desktop` 파일도 함께 볼 수 있습니다[4].

배포판별로 볼 것은 systemd 가 자동 실행을 맡을 수 있는 판인지입니다. `systemd-xdg-autostart-generator` 는 systemd 246 에 들어갔고[9], Ubuntu 24.04 의 systemd 는 255[12], RHEL 9 의 systemd 는 252 입니다[13]. 실제로 쓰는지는 실제 시스템에서 `/usr/lib/systemd/user-generators/systemd-xdg-autostart-generator` 가 있는지[6], 데스크톱 환경이 `xdg-desktop-autostart.target` 을 시작하는지로 확인합니다.

## 구조

`.desktop` 파일은 데스크톱 항목 명세(Desktop Entry Specification)를 따르는 텍스트 파일입니다[1]. `[Desktop Entry]` 그룹 머리가 있어야 하고, 그 앞에는 주석만 올 수 있으며, 그룹 머리 다음 줄부터 다음 그룹 머리까지의 `키=값` 이 그 그룹에 속합니다[3].

아래는 만든 예시입니다.

```ini
[Desktop Entry]
Type=Application
Name=Update Helper
Exec=/home/alice/.local/bin/update-helper --quiet
TryExec=/home/alice/.local/bin/update-helper
OnlyShowIn=GNOME;
```

자동 실행을 볼 때 읽어야 할 키는 아래와 같습니다.

| 키 | 자동 실행에서의 뜻 |
|---|---|
| `Exec` | 실행할 프로그램과 인수[3] |
| `Type` | 항목 종류이고, `Application`·`Link`·`Directory` 세 가지가 있습니다[3]. systemd 는 `Application` 이 아니면 유닛을 만들지 않습니다[7] |
| `Hidden` | `true` 면 이 파일을 무시합니다. 가장 중요한 디렉터리의 파일이 `Hidden=true` 면 다른 디렉터리의 같은 이름 파일도 모두 무시합니다[1] |
| `OnlyShowIn` / `NotShowIn` | 자동 실행할(또는 하지 않을) 데스크톱 환경 목록이고, 한 파일에 둘 중 하나만 올 수 있습니다[1] |
| `TryExec` | 값이 비어 있지 않은데 설치된 실행 파일과 맞지 않으면 자동 실행하지 않습니다. 경로 없이 이름만 적으면 `$PATH` 에서 찾습니다[1] |
| `Path` | 작업 디렉터리. systemd 는 이 값을 `WorkingDirectory=-` 뒤에 옮깁니다[7] |
| `X-제품-키` | 제품별 확장 키(예: `X-GNOME-Autostart-Phase`, `X-KDE-autostart-condition`)[3][6] |
| `AutostartCondition` | 접두어 없이 쓰는 GNOME 확장 키로, 명세가 역사적 예외로 남겨 둔 이름입니다[3] |

`Hidden` 은 원래 "지웠다(Deleted)" 는 뜻이라, 그 사용자에게는 파일이 없는 것과 같습니다[3]. 사용자가 시스템 항목을 끄려면 같은 이름의 파일을 자기 자동 실행 디렉터리에 두고 `Hidden=true` 를 적습니다[1].

### systemd 가 맡는 경우

`systemd-xdg-autostart-generator` 는 자동 실행 `.desktop` 파일마다 사용자 `.service` 유닛을 만들고, 데스크톱 환경은 `xdg-desktop-autostart.target` 으로 이 유닛들을 시작합니다[6]. 유닛 이름은 파일 이름에서 `.desktop` 을 떼고 유닛 이름 규칙으로 바꾼 뒤 앞뒤를 붙인 `app-이름@autostart.service` 이고, `foo.desktop` 이면 `app-foo@autostart.service` 가 됩니다[7].

만든 유닛에는 원래 `.desktop` 파일 경로가 `SourcePath=` 로, `Name` 이 `Description=` 으로 들어갑니다. `Exec` 는 첫 단어를 절대 경로로 바꾸고 `%f`·`%U` 같은 필드 코드를 뺀 뒤 `ExecStart=:` 뒤에 들어가며, `Slice=app.slice` 와 `PartOf=graphical-session.target` 도 함께 들어갑니다[7]. `OnlyShowIn`·`NotShowIn`·`AutostartCondition`·`X-KDE-autostart-condition` 은 `ExecCondition=` 줄로 바뀌어, 실행할 때 조건을 다시 봅니다[6].

아래 경우에는 유닛을 아예 만들지 않습니다[6][7].

- `Hidden=` 이나 `X-systemd-skip=` 이 참일 때
- `TryExec=` 의 실행 파일이 없거나 실행할 수 없을 때
- `Type` 이 `Application` 이 아니거나 `Exec` 줄이 없을 때, `Exec` 의 실행 파일이 없을 때

`X-GNOME-Autostart-Phase=` 는 출처끼리 설명이 다릅니다. man 페이지는 값이 있으면 유닛을 만들지 않는다고 적었고[6], 소스는 `NotShowIn` 에 `GNOME` 을 더해 유닛을 만들고 `OnlyShowIn` 이 GNOME 하나뿐일 때만 건너뜁니다[7].

만든 유닛 파일은 `$XDG_RUNTIME_DIR/systemd/` 아래 생성기 디렉터리에 놓입니다[8]. 이 디렉터리는 실행 중에만 있는 런타임 디렉터리라서[8] 디스크 이미지에는 남지 않을 가능성이 높고, 사후 분석에서는 `.desktop` 원본과 저널 기록으로 거슬러 올라가 확인합니다.

## 증거로서 의미

**증명하는 것**

- 그 파일이 있던 시점에, 그 사용자(사용자 디렉터리) 또는 모든 사용자(시스템 디렉터리)가 그래픽 데스크톱에 로그인하면 `Exec` 의 명령을 실행하도록 설정되어 있었다는 것
- 사용자 디렉터리의 같은 이름 파일이 시스템 항목을 덮어쓰거나(`Hidden=true`) 바꿔 놓았다는 것
- systemd 가 맡는 시스템에서 사용자 저널에 `app-…@autostart.service` 기록이 있다면, 그 시각에 해당 유닛이 사용자 관리자 아래에서 다뤄졌다는 것

**증명하지 못하는 것**

- 실제로 실행되었는지. 그래픽 로그인이 없는 계정(SSH 로만 쓰는 서버 계정 등)에서는 돌지 않고, `Hidden`·`OnlyShowIn`·`NotShowIn`·`TryExec` 조건에 걸려 건너뛰었을 수도 있습니다[1]
- 누가 파일을 만들었는지. 파일 소유자와 권한은 만든 사람의 단서일 뿐이고, 패키지가 깐 파일인지는 패키지 기록과 대조해야 합니다
- 매체의 `autorun` 파일이 실행되었는지. 명세상 사용자 확인이 필요하고 정책으로 무시할 수도 있어서[1], 파일이 있다는 사실만으로는 실행을 말할 수 없습니다

## 시각 해석

`.desktop` 파일 자체에는 시각 필드가 없습니다. 시각은 파일 시스템의 타임스탬프에서 얻습니다. 내용을 고쳐 쓰면 mtime 과 ctime 이 바뀌고, 소유자·권한·링크 수 같은 아이노드 정보만 바꿔도 ctime 이 바뀝니다[14]. 저장 형식과 해상도는 [ext4](../../01-foundations/filesystem/ext4/index.md) 를 봅니다. 이 값들은 UTC 기준 epoch 에서 센 값이라 시간대가 없고[14], 도구가 현지 시각으로 바꿔 보여 줄 수 있으므로 표시 시간대를 확인합니다([Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)).

실행 시각은 사용자 저널에서 찾습니다. 사용자 관리자가 유닛에 관해 남기는 기록에는 `USER_UNIT=` 필드가 붙고, 프로그램 자신이 남긴 기록에는 `_SYSTEMD_USER_UNIT=` 필드가 붙습니다[10]. 저널 시각의 형식과 사용자 저널 파일 위치는 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 을 봅니다.

## 함정과 한계

- 같은 이름의 사용자 파일이 시스템 파일을 덮어씁니다[1]. 시스템 디렉터리의 파일만 보고 "정상 패키지 항목" 이라고 판단하면, 사용자 디렉터리에서 같은 이름으로 `Exec` 를 바꾼 파일을 놓칩니다. 파일 이름별로 두 디렉터리를 나란히 비교합니다.
- 반대로 사용자 디렉터리의 `Hidden=true` 파일은 시스템 항목을 끈 흔적이고, 그 자체로 실행 설정이 아닙니다[1].
- `Exec` 가 가리키는 파일이 지워졌으면 systemd 는 유닛을 만들지 않습니다[7]. 따라서 저널에 기록이 없다고 해서 설정이 없었다고 볼 수 없고, 실행 파일이 언제 사라졌는지를 따로 봅니다.
- `/usr/share/autostart`, `~/.local/share/autostart`, `~/.config/autostart-scripts` 는 명세의 기본 자동 실행 디렉터리가 아니고, ForensicArtifacts 정의에도 없습니다[4][5]. 이 정의만으로 수집하면 이 세 곳의 파일이 빠지고, 그 가운데 `~/.config/autostart-scripts` 는 KDE 가 쓰는 디렉터리입니다[4].
- 파일 이름이 기존 프로그램과 비슷하거나 `Name` 이 그럴듯해도, 판단은 `Exec` 의 실제 경로로 합니다. 홈 디렉터리 아래 숨김 폴더나 `/tmp`·`/dev/shm` 을 가리키면 따로 살핍니다([임시 폴더와 메모리 파일 시스템](../file-activity/tmp-shm.md)).
- mtime 은 `utime` 호출(`touch` 명령 등)로 바꿀 수 있으므로[14], mtime 하나로 설치 시점을 단정하지 않고 저널·패키지 기록과 맞춰 봅니다.

## 직접 분석해 보기

**헥스로 한 번.** `.desktop` 파일은 텍스트라서 헥스로 볼 것은 첫 줄과 줄 끝입니다. 아래는 앞의 예시 파일 첫 줄을 명세대로 만든 헥스 예시입니다.

```text
00000000: 5b44 6573 6b74 6f70 2045 6e74 7279 5d0a  [Desktop Entry].
```

첫 바이트가 `5b`(`[`)가 아니면 앞에 BOM 이나 주석이 있는지 보고, 줄 끝이 `0a` 인지 `0d0a` 인지도 봅니다. 명세상 `[Desktop Entry]` 앞에는 주석만 올 수 있습니다[3].

**공개 도구로 한 번.** UAC 로 수집했다면 `xdg_autostart.yaml` 과 `desktop.yaml` 이 모은 파일이 수집 결과에 들어 있습니다[4]. 이미지를 마운트한 뒤에는 아래처럼 두 디렉터리를 이름별로 모아 봅니다(`/mnt/img` 는 만든 예시 마운트 위치입니다).

```sh
ls -la --time-style=full-iso /mnt/img/etc/xdg/autostart/ /mnt/img/home/*/.config/autostart/
grep -H -E '^(Type|Exec|TryExec|Hidden|OnlyShowIn|NotShowIn|X-systemd-skip)=' \
  /mnt/img/etc/xdg/autostart/*.desktop /mnt/img/home/*/.config/autostart/*.desktop
```

저널을 복사해 왔다면 `journalctl` 의 `--directory=` 로 그 디렉터리를 읽고, `필드=값` 조건으로 앞에서 본 두 필드를 겁니다. 서로 다른 필드의 조건 사이에 `+` 를 두면 둘 중 하나에 맞는 기록이 나옵니다[11].

```sh
journalctl --directory=/mnt/img/var/log/journal \
  USER_UNIT=app-updater@autostart.service + _SYSTEMD_USER_UNIT=app-updater@autostart.service
```

위 유닛 이름은 `updater.desktop` 에서 만든 예시입니다. 파일 이름의 일부 문자는 유닛 이름 규칙에 따라 다른 표기로 바뀔 수 있으므로[7], 저널에서 실제 이름을 확인합니다.

## 교차 검증

| 함께 볼 것 | 알 수 있는 것 |
|---|---|
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | `app-…@autostart.service` 로 실행 시각, 프로그램이 남긴 출력 |
| [로그인 기록 (wtmp·btmp·lastlog)](../logins/wtmp-btmp-lastlog.md) | 그 계정이 그래픽 세션으로 로그인한 시각 |
| [dpkg·apt 기록](../packages/dpkg-apt.md), [rpm·dnf·yum 기록](../packages/rpm-dnf.md) | 시스템 디렉터리의 파일을 패키지가 깐 것인지 |
| [패키지 파일 변조 확인](../packages/package-verify.md) | 패키지가 깐 `.desktop` 파일의 내용이 바뀌었는지 |
| [systemd 서비스와 타이머](systemd-units.md) | 사용자 유닛으로 직접 심은 지속성 |
| [셸 시작 파일](shell-startup.md) | 터미널·SSH 로그인 때 실행되는 지속성 |
| [셸 명령 기록](../execution/shell-history/index.md) | `.desktop` 파일을 만들거나 고친 명령 |

여러 지속성 자리를 한꺼번에 살펴보는 순서는 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 에 있고, 파일 시각과 저널을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 를 봅니다.

## 실습

NIST CFReDS 등에 공개된 Linux 데스크톱 디스크 이미지로 아래 질문을 풀어 봅니다.

1. 사용자마다 `~/.config/autostart/` 에 어떤 파일이 있고, 각 파일의 `Exec` 는 어디를 가리키나?
2. `/etc/xdg/autostart/` 와 같은 이름을 쓰는 사용자 파일이 있나? 있다면 `Hidden=true` 로 끈 것인가, `Exec` 를 바꾼 것인가?
3. 시스템 디렉터리의 파일 가운데 어느 패키지에도 속하지 않는 파일이 있나?
4. 수상한 파일의 mtime 과, 같은 계정의 그래픽 로그인 시각, 사용자 저널의 `app-…@autostart.service` 기록이 서로 맞는가?

## 참고 문헌

1. freedesktop.org, Desktop Application Autostart Specification (Version 0.5), https://gitlab.freedesktop.org/xdg/xdg-specs/-/blob/master/autostart/autostart-spec.xml
2. freedesktop.org, XDG Base Directory Specification, https://gitlab.freedesktop.org/xdg/xdg-specs/-/blob/master/basedir/basedir-spec.xml
3. freedesktop.org, Desktop Entry Specification, https://gitlab.freedesktop.org/xdg/xdg-specs/-/blob/master/desktop-entry/desktop-entry-spec.xml
4. UAC, `artifacts/files/system/xdg_autostart.yaml`, `artifacts/files/system/desktop.yaml`, https://github.com/tclahr/uac/tree/main/artifacts/files/system
5. ForensicArtifacts, `linux.yaml` (`XDGAutostartEntries`), https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
6. systemd, systemd-xdg-autostart-generator(8), https://github.com/systemd/systemd/blob/main/man/systemd-xdg-autostart-generator.xml
7. systemd, `src/xdg-autostart-generator/xdg-autostart-service.c`, https://github.com/systemd/systemd/blob/main/src/xdg-autostart-generator/xdg-autostart-service.c
8. systemd, systemd.generator(7), https://github.com/systemd/systemd/blob/main/man/systemd.generator.xml
9. systemd, NEWS ("CHANGES WITH 246"), https://github.com/systemd/systemd/blob/main/NEWS
10. systemd, systemd.journal-fields(7), https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
11. systemd, journalctl(1), https://github.com/systemd/systemd/blob/main/man/journalctl.xml
12. Ubuntu, systemd 패키지 `debian/changelog` (noble, 255.4-1ubuntu8), https://git.launchpad.net/ubuntu/+source/systemd/tree/debian?h=ubuntu/noble-updates
13. CentOS Stream 9, `systemd.spec` (`Version: 252`), https://gitlab.com/redhat/centos-stream/rpms/systemd/-/tree/c9s
14. Linux man-pages, inode(7), https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
