---
title: "systemd 서비스와 타이머"
parent: "아티팩트 · 지속성"
nav_order: 510
---

# systemd 서비스와 타이머 (systemd Units·Timers)

systemd 는 유닛 파일 (unit file) 과 그 유닛을 켜 두는 심볼릭 링크로 부팅 때마다, 또는 정해진 시각마다 프로그램을 실행하므로, 유닛 파일·드롭인·링크·타이머 시각 파일을 모아 보면 무엇이 언제부터 자동으로 돌게 설정됐는지 알 수 있습니다.

## 무엇을 기록하나 · 왜 생기나

유닛 파일은 ini 형식의 평문 파일이고, 서비스 (service) 유닛에는 실행할 명령(`ExecStart=`), 실행 계정(`User=`·`Group=`), 재시작 정책(`Restart=`)이 들어 있습니다[1][3][4]. `User=` 를 적지 않은 시스템 서비스는 root 로 돕니다[4]. 서비스 종류(`Type=`)는 `simple`, `exec`, `forking`, `oneshot`, `dbus`, `notify`, `notify-reload`, `idle` 가운데 하나입니다[3].

유닛을 켜는 (enable) 일은 파일을 하나 더 만드는 일입니다. `systemctl enable` 은 유닛의 `[Install]` 절에 적힌 `WantedBy=`·`RequiredBy=`·`UpheldBy=` 를 읽어 대상 유닛의 `.wants/`·`.requires/`·`.upholds/` 디렉터리에 심볼릭 링크를 만들고, systemd 는 평소에 `[Install]` 절을 전혀 보지 않고 이 링크만 따라 움직입니다[1]. 링크는 `systemctl` 을 쓰지 않고 손으로 만들어도 되고, 그 뒤 `daemon-reload` 를 하면 반영됩니다[5]. 그래서 유닛 파일의 `[Install]` 절보다 실제 링크가 있는지가 부팅 때 켜지는지를 정합니다.

타이머 (timer) 유닛은 cron 과 같은 일을 합니다. `이름.timer` 는 따로 적지 않으면 같은 이름의 `.service` 를 켜고, `Unit=` 으로 다른 유닛을 가리킬 수 있습니다[2]. `Persistent=true` 인 타이머는 마지막으로 발동한 시각을 디스크의 시각 파일(stamp 파일)에 남기므로, 이 파일의 수정 시각으로 마지막 발동 시각을 알 수 있습니다[2][7]. cron 쪽 흔적은 [cron·anacron·at](cron-at.md) 에서 다룹니다.

## 위치와 버전별 차이

systemd 는 아래 순서로 유닛을 찾고, 앞쪽 디렉터리의 파일이 뒤쪽의 같은 이름 파일을 덮습니다[1]. 환경 변수 `$SYSTEMD_UNIT_PATH` 가 있으면 이 목록을 바꿉니다[1].

| 순서 | 시스템 유닛 경로 | 뜻 | 전원을 끈 이미지에 남나 |
|---|---|---|---|
| 1 | `/etc/systemd/system.control` | dbus API 로 만든 설정 | 남음 |
| 2 | `/run/systemd/system.control` | dbus API 로 만든 설정 | 남지 않음 |
| 3 | `/run/systemd/transient` | 일시 유닛 (transient unit) | 남지 않음 |
| 4 | `/run/systemd/generator.early` | 생성기가 만든 유닛(우선순위 높음) | 남지 않음 |
| 5 | `/etc/systemd/system` | 관리자가 만든 유닛 | 남음 |
| 6 | `/etc/systemd/system.attached` | — | 남음 |
| 7 | `/run/systemd/system` | 런타임 유닛 | 남지 않음 |
| 8 | `/run/systemd/system.attached` | — | 남지 않음 |
| 9 | `/run/systemd/generator` | 생성기가 만든 유닛(보통) | 남지 않음 |
| 10 | `/usr/local/lib/systemd/system` | 관리자가 설치한 유닛 | 남음 |
| 11 | `/usr/lib/systemd/system` | 배포판 패키지가 설치한 유닛 | 남음 |
| 12 | `/run/systemd/generator.late` | 생성기가 만든 유닛(우선순위 낮음) | 남지 않음 |

`/run` 아래 내용은 재부팅하면 사라지므로[5] 이 아래 유닛은 라이브 수집으로만 얻습니다. 실제 검색 경로는 라이브 시스템에서 `systemd-analyze unit-paths` 로 확인합니다[1].

사용자 유닛은 사용자마다 도는 사용자 관리자 (user manager) 가 읽습니다. 사용자가 직접 쓸 수 있는 곳은 `~/.config/systemd/user`(`$XDG_CONFIG_HOME` 이 있으면 그 아래), `~/.config/systemd/user.control`, `~/.local/share/systemd/user`(`$XDG_DATA_HOME` 이 있으면 그 아래)이고, 모든 사용자에게 적용되는 곳으로 `/etc/systemd/user`, `/etc/xdg/systemd/user`, `/usr/local/lib/systemd/user`, `/usr/lib/systemd/user`, `/usr/local/share/systemd/user`, `/usr/share/systemd/user` 가 있습니다[1]. 런타임 경로는 `$XDG_RUNTIME_DIR/systemd/` 아래의 `user.control`, `transient`, `generator.early`, `user`, `generator`, `generator.late` 와 `/run/systemd/user` 입니다[1].

유닛 파일 말고도 함께 볼 곳이 있습니다.

| 흔적 | 경로 | 근거 |
|---|---|---|
| 켜기 링크 | 유닛 디렉터리 아래 `대상.wants/`, `대상.requires/`, `대상.upholds/` | [1] |
| 드롭인 (drop-in) | `이름.service.d/*.conf`, 대시 앞부분 이름의 `foo-.service.d/`, 종류 전체의 `service.d/` | [1] |
| 생성기 실행 파일 | `/etc/systemd/system-generators/`, `/usr/local/lib/systemd/system-generators/`, `/run/systemd/system-generators/`, 배포판 기본 생성기 디렉터리(사용자용은 `user-generators`) | [6] |
| 타이머 시각 파일 | 시스템 `/var/lib/systemd/timers/stamp-타이머이름`, 사용자 `~/.local/share/systemd/timers/stamp-타이머이름`(`$XDG_DATA_HOME` 이 있으면 `$XDG_DATA_HOME/systemd/timers/`) | [7] |
| 사용자 상주 설정 (linger) | `/var/lib/systemd/linger/사용자이름` | [10] |

생성기 (generator) 는 부팅 초기와 설정을 다시 읽을 때마다 유닛을 읽기 전에 실행되는 프로그램이고, 결과 유닛을 `/run/systemd/generator*` 에 씁니다[6]. 생성기가 만든 유닛은 `/run` 에 있어 이미지에 남지 않지만, 생성기 실행 파일은 `/etc` 나 `/usr` 에 남으므로 이 디렉터리의 실행 파일을 목록으로 뽑아 패키지 파일과 대조합니다. 호환용 생성기가 SysV 스크립트와 rc.local 을 유닛으로 바꾸는 일은 [init 스크립트와 rc.local](sysv-init.md) 에서, `.desktop` 자동 실행을 유닛으로 바꾸는 일은 [데스크톱 자동 실행](xdg-autostart.md) 에서 다룹니다.

기준 판의 systemd 는 Ubuntu 24.04 가 255, RHEL 9 가 252 입니다[13][14]. 타이머 시각 파일의 경로와 동작은 v252 코드와 현재 코드가 같습니다[7]. `/lib/systemd/system` 과 `/usr/lib/systemd/system` 이 같은 디렉터리인지(usr 병합)는 실제 시스템에서 `/lib` 이 링크인지 보고 정합니다. UAC 는 두 경로를 모두 모읍니다[16].

## 구조

아래는 만든 예시 서비스 하나와 그 흔적입니다. 이름과 경로는 지어낸 값입니다.

```ini
# /etc/systemd/system/update-helper.service  (만든 예시)
[Unit]
Description=Update Helper

[Service]
Type=simple
ExecStart=/opt/uh/uh-agent --quiet
Restart=always

[Install]
WantedBy=multi-user.target
```

```text
# 켜기 링크 (만든 예시)
/etc/systemd/system/multi-user.target.wants/update-helper.service -> /etc/systemd/system/update-helper.service

# 드롭인 (만든 예시): 본 파일은 그대로 두고 실행 명령만 바꾼다
/etc/systemd/system/update-helper.service.d/override.conf
[Service]
ExecStart=
ExecStart=/opt/uh/uh-agent2
```

드롭인은 본 유닛 파일을 읽은 뒤 이름 순서로 합쳐지고, `/etc` 의 드롭인이 `/run`, `/usr/lib` 의 드롭인보다 앞서며, 드롭인은 어느 위치의 유닛 파일보다 우선합니다[1]. 종류 전체 드롭인(`service.d/`)은 이름별 드롭인보다 우선순위가 낮지만 시스템의 모든 서비스에 적용됩니다[1]. 그래서 본 유닛 파일만 읽으면 실제로 도는 명령을 놓칠 수 있습니다.

그 밖에 해석에 영향을 주는 규칙은 다음과 같습니다.

- 크기가 0 인 유닛 파일이나 `/dev/null` 로 가는 링크는 마스크 (masked) 상태이고 손으로도 시작할 수 없습니다[1].
- 이름이 `.` 으로 시작하거나 `.ignore` 로 끝나는 파일은 무시됩니다[1].
- `.wants/`·`.requires/` 링크의 대상 파일은 없어도 됩니다[1].
- 검색 경로 밖을 가리키는 심볼릭 링크는 링크된 유닛 (linked unit) 이 되어 그 파일을 유닛으로 읽습니다. 다만 `/home`·`/var` 아래 파일은 그 디렉터리가 루트 파일 시스템에 있을 때만 쓸 수 있습니다[1].
- `systemctl enable --runtime` 은 링크를 `/etc` 대신 `/run` 에 만들어 재부팅하면 사라집니다[5].

타이머에는 단조 시계 기준 키 `OnActiveSec=`, `OnBootSec=`, `OnStartupSec=`, `OnUnitActiveSec=`, `OnUnitInactiveSec=` 와 달력 시각 키 `OnCalendar=` 가 있고, 그 밖에 `Persistent=`, `WakeSystem=`, `RandomizedDelaySec=`, `AccuracySec=`, `RemainAfterElapse=`, `Unit=` 등을 씁니다[2]. `OnStartupSec=` 는 사용자 관리자에서 주로 쓰고, 사용자 관리자는 대개 첫 로그인 때 시작합니다[2].

linger 가 켜진 사용자는 부팅 때 사용자 관리자가 뜨고 로그아웃한 뒤에도 남아 있습니다[9]. `loginctl enable-linger` 는 `/var/lib/systemd/linger/사용자이름` 파일을 만들고, `disable-linger` 는 이 파일을 지웁니다[8][10]. 이 파일은 내용이 없고, 파일이 있는지 없는지로 linger 여부를 정합니다. 로그인 기록이 없는 시간대에 사용자 유닛이 돈 흔적이 있으면 이 파일부터 봅니다.

systemd 는 유닛을 시작할 때 저널에 메시지를 남깁니다. 저널 필드 `UNIT=`·`USER_UNIT=` 은 시스템·사용자 관리자가 어떤 유닛에 대해 남긴 기록에 붙고, `_SYSTEMD_UNIT=`·`_SYSTEMD_USER_UNIT=` 은 메시지를 낸 프로세스가 속한 유닛입니다[11]. `INVOCATION_ID=` 는 유닛이 한 번 실행될 때마다 새로 뽑는 128비트 무작위 ID 로 systemd 쪽 메시지에 붙고, 유닛의 프로세스가 낸 메시지에는 그 실행의 ID 가 `_SYSTEMD_INVOCATION_ID=` 로 붙습니다[11]. 시작 작업 메시지는 메시지 ID 로 가려냅니다[12].

| MESSAGE_ID | 뜻 |
|---|---|
| `7d4958e842da4a758f6c1cdc7b36dcc5` | 시작 작업이 실행되기 시작함 |
| `39f53479d3a045ac8e11786248231fbf` | 시작 작업이 성공함 |
| `be02cf6855d2428ba40df7e9d022f03d` | 시작 작업이 실패함 |
| `d34d037fff1847e6ae669a370e694725` | 다시 읽기 (reload) 작업이 시작됨 |

상태 메시지에는 유닛의 `Description=` 문자열이 들어가서 `Starting 설명...`, `Started 설명.`, `Failed to start 설명.` 모양이 됩니다[1]. 저널 파일 자체는 [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) 에서 다룹니다.

## 증거로서 의미

**증명하는 것**

- 유닛 파일이 있으면 그 실행 명령·계정·재시작 정책이 정의돼 있었다는 것.
- `.wants/`·`.requires/` 링크가 있으면 그 유닛이 부팅 때 켜지도록 설정돼 있었다는 것.
- 드롭인이 있으면 본 유닛 파일과 다른 설정으로 실행되도록 바뀌어 있었다는 것.
- 저널에 시작 작업 메시지가 있으면 그 시각에 그 유닛이 시작됐거나 시작에 실패했다는 것.
- stamp 파일이 있으면 그 이름의 `Persistent=true` 타이머가 적어도 한 번 시작됐다는 것, 그리고 그 수정 시각이 마지막 발동 시각이라는 것(아래 "시각 해석" 참고).
- linger 파일이 있으면 그 사용자의 유닛이 로그인 없이도 돌 수 있었다는 것.

**증명하지 못하는 것**

- 누가 유닛을 만들었는지. 시스템 유닛 파일의 소유자는 대개 root 라서 만든 사람을 가리키지 않습니다. 만든 사람은 [sudo·su 사용 기록](../logins/sudo-su.md), [셸 명령 기록](../execution/shell-history/index.md), [감사 로그의 실행 기록](../execution/auditd-execve.md) 에서 찾습니다.
- `ExecStart=` 가 가리키는 파일이 그때 어떤 내용이었는지. 실행 파일은 나중에 바뀔 수 있으므로 해시와 파일 시각을 따로 봅니다.
- 유닛이 실제로 돌았는지. 켜 두었다는 것과 실행됐다는 것은 다르고, 실행 여부는 저널이나 프로세스 흔적으로 확인합니다.
- `/run` 아래 일시 유닛·런타임 유닛·생성기 결과가 있었는지. 재부팅하면 사라지므로 전원을 끈 이미지에 없다고 해서 없었다고 말할 수 없습니다.

## 시각 해석

유닛 파일과 드롭인의 수정 시각은 그 파일을 쓰거나 고친 때입니다. 패키지가 깐 파일은 패키지를 풀 때 정한 값일 수 있으므로 [dpkg·apt 기록](../packages/dpkg-apt.md) 이나 [rpm·dnf·yum 기록](../packages/rpm-dnf.md) 의 설치 시각과 대조합니다. `.wants/` 링크는 켤 때 만들어지므로 링크 자체의 시각이 켠 시각에 가깝습니다. 링크 자체의 시각은 링크를 따라가지 않고 읽어야 합니다(`stat` 은 기본으로 링크 자체를, `stat -L` 은 대상을 봅니다).

stamp 파일의 수정 시각은 이렇게 바뀝니다.

1. 타이머가 서비스를 켤 때 systemd 는 stamp 파일의 접근 시각과 수정 시각을 그 발동 시각(실제 시계 기준)으로 맞춥니다[7][8].
2. 타이머가 시작할 때 stamp 파일이 없으면 현재 시각으로 새로 만듭니다[7]. 그래서 한 번도 발동하지 않은 타이머의 stamp 파일 시각은 타이머가 처음 시작된 시각입니다.
3. 타이머가 시작할 때 stamp 파일의 수정 시각이 현재보다 미래면 그 값을 쓰지 않고 `Not using persistent file timestamp %s as it is in the future.` 경고를 남깁니다[7]. 저널에 이 경고가 있으면 시스템 시각이 뒤로 갔거나 stamp 파일 시각을 누가 바꿨을 가능성이 있습니다.

`Persistent=` 는 `OnCalendar=` 를 쓴 타이머에서만 효과가 있고[2], stamp 파일은 `Persistent=true` 인 타이머만 만듭니다[7]. 파일 시스템 시각은 UTC 기준 epoch 값으로 저장되고, 표시하는 도구가 시간대를 적용합니다. 저널 시각은 UTC 마이크로초입니다. 시각 값 일반은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 을 봅니다.

linger 파일은 `enable-linger` 를 할 때마다 시각이 새로 찍히므로[8][10] 수정 시각은 마지막으로 linger 를 켠 때입니다.

## 함정과 한계

- **드롭인을 빼먹기 쉽습니다.** 이름별 드롭인, 대시 앞부분 드롭인(`foo-.service.d/`), 종류 전체 드롭인(`service.d/`)을 모두 봐야 실제 설정이 나옵니다[1].
- **도구마다 보는 범위가 좁습니다.** dissect.target 의 `services` 는 `/etc/systemd/system`, `/lib/systemd/system`, `/usr/lib/systemd/system` 바로 아래 파일만 읽고 이름이 `.wants`·`.requires`·`.d` 로 끝나는 항목은 건너뜁니다[17]. 사용자 유닛, `/usr/local/lib`, 드롭인, 생성기는 이 결과에 나오지 않습니다. Velociraptor `Linux.Sys.Services` 는 라이브 시스템에서 `systemctl list-units --type=service` 출력을 읽는 방식입니다[18].
- **수집 정의와 문서 이름이 다른 곳이 있습니다.** ForensicArtifacts 의 `LinuxSystemdServices`·`LinuxSystemdTimers` 에는 `/etc/systemd/systemd.attached/`, `/run/systemd/systemd.attached/` 가 들어 있는데 systemd 문서의 이름은 `system.attached` 입니다[15][1]. 이 두 정의는 디렉터리 바로 아래 `*.service`·`*.timer` 만 가리키므로 드롭인 `.conf`, `/usr/local/lib/systemd/system`, 생성기 실행 파일은 따로 모읍니다[15].
- **UAC 는 `/run/systemd/generator*` 를 따로 모으지 않습니다.** `/run/systemd/system`, `/run/systemd/transient`, `/run/user/*/systemd/transient`, `/run/systemd/sessions` 는 모읍니다[16].
- **`/run` 은 이미지에 없습니다.** 일시 유닛(`systemd-run` 등으로 만든 것)과 `--runtime` 으로 켠 링크는 라이브 수집으로만 얻습니다[1][5].
- **켜기와 시작은 다릅니다.** 켜지 않은 유닛도 손으로 시작할 수 있고, 켠 유닛도 시작하지 않았을 수 있습니다[5].
- **stamp 파일은 지우기 쉽습니다.** `systemctl clean --what=state` 로 지울 수 있고[2], 지우면 다음 타이머 시작 때 현재 시각으로 다시 생깁니다[7].
- 지속성 흔적 전반을 살펴보는 순서는 [무엇이 계속 살아남게 했나](../../04-scenarios/intrusion/persistence-hunt.md) 에서 다룹니다.

## 직접 분석해 보기

### 헥스로 한 번

유닛 파일은 평문이라 헥스로 볼 거리가 적고, 볼 것은 링크와 stamp 파일의 아이노드입니다. stamp 파일은 내용 없이 만들어지고(`O_CREAT` 로 연 뒤 시각만 바꿈) 크기가 0 입니다[8]. 그러니 stamp 파일에서 읽을 값은 아이노드의 시각뿐입니다. 아래는 만든 예시입니다.

```text
$ stat -c '%s %y %n' /mnt/evidence/var/lib/systemd/timers/stamp-*
0 2026-03-02 00:00:04.118302000 +0000 /mnt/evidence/var/lib/systemd/timers/stamp-uh-sync.timer
0 2026-03-01 06:12:55.402100000 +0000 /mnt/evidence/var/lib/systemd/timers/stamp-logrotate.timer

$ stat -c '%y %N' /mnt/evidence/etc/systemd/system/multi-user.target.wants/update-helper.service
2026-02-27 13:40:11.905512000 +0000 '/mnt/evidence/etc/systemd/system/multi-user.target.wants/update-helper.service' -> '/etc/systemd/system/update-helper.service'
```

마운트하지 않고 이미지에서 읽을 때는 Sleuth Kit 의 `fls` 로 아이노드 번호를 찾고 `istat` 으로 그 아이노드의 시각을 봅니다. ext4 아이노드 안에서 시각과 짧은 심볼릭 링크 대상이 어디에 들어가는지는 [ext4](../../01-foundations/filesystem/ext4/index.md) 에서 다룹니다.

### 공개 도구로 한 번

- 수집: UAC 는 `/etc/systemd`, `/lib/systemd/system`, `/usr/lib/systemd`, `/usr/local/lib/systemd/system`, `/usr/local/lib/systemd/user`, `/usr/local/share/systemd/user`, `/usr/share/systemd/user`, 사용자 홈의 `.config/systemd`·`.local/share/systemd` 를 파일로 모으고, 라이브 시스템에서 `systemctl list-units`, `systemctl list-timers --all`, `systemctl status *.timer`, `systemctl list-unit-files` 를 실행해 둡니다[16].
- 파싱: dissect.target 의 `services` 는 유닛의 `[절]` 과 키를 `절_키` 이름의 필드로 펼치고, 기록의 시각으로 유닛 파일의 수정 시각을 씁니다(링크를 따라가며, 대상이 없는 링크는 링크 자체의 시각)[17].
- 라이브: `systemctl list-timers` 는 NEXT, LEFT, LAST, PASSED, UNIT, ACTIVATES 열을 보여 줍니다[5]. LAST 가 마지막 발동 시각입니다.
- 저널: 아래처럼 유닛 이름과 메시지 ID 로 거릅니다(만든 예시).

```text
journalctl -D /mnt/evidence/var/log/journal/MACHINE_ID --utc UNIT=update-helper.service
journalctl -D /mnt/evidence/var/log/journal/MACHINE_ID --utc MESSAGE_ID=be02cf6855d2428ba40df7e9d022f03d
```

## 교차 검증

| 함께 볼 것 | 맞춰 볼 것 |
|---|---|
| [systemd 저널](../../01-foundations/logging/systemd-journal/index.md) | 유닛 시작·실패 메시지 시각, `INVOCATION_ID=`·`_SYSTEMD_INVOCATION_ID=` 로 한 번의 실행에 딸린 기록 묶기 |
| [dpkg·apt 기록](../packages/dpkg-apt.md), [rpm·dnf·yum 기록](../packages/rpm-dnf.md) | 유닛 파일이 패키지 파일 목록에 있는지. 없으면 사람이 만들었을 가능성이 있습니다 |
| [패키지 파일 변조 확인](../packages/package-verify.md) | `/usr/lib/systemd/system` 의 패키지 유닛과 생성기 실행 파일이 바뀌었는지 |
| [cron·anacron·at](cron-at.md) | 같은 명령이 cron 에도 걸려 있는지 |
| [인증 로그](../logins/auth-log.md), [로그인 기록](../logins/wtmp-btmp-lastlog.md) | 사용자 유닛이 돈 시각에 로그인이 있었는지, 없었다면 linger 파일 |
| [실행 중인 프로세스](../execution/proc.md) | 라이브 수집에서 그 유닛의 프로세스가 실제로 돌고 있었는지 |
| [부팅과 종료 기록](../system-info/boot-shutdown.md) | 부팅 때 켜지는 유닛이 부팅 시각 직후에 시작됐는지 |

타임라인에 넣는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 를 봅니다.

## 실습

공개 디스크 이미지(NIST CFReDS 의 Linux 침해 이미지 등)나 직접 만든 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. `/etc/systemd/system` 과 사용자 홈의 `.config/systemd/user` 에 있는 유닛 가운데 어느 패키지의 파일 목록에도 없는 것은 무엇입니까?
2. `*.wants/` 디렉터리의 링크 가운데 대상 파일이 `/usr/lib/systemd/system` 밖에 있는 것은 무엇이고, 링크 자체의 수정 시각은 언제입니까?
3. 모든 `*.service.d/` 와 `service.d/` 드롭인을 모아 `ExecStart=` 를 바꾸는 것이 있습니까?
4. `/var/lib/systemd/timers/` 의 stamp 파일 이름을 타이머 유닛 목록과 맞춰 보면, 지금은 유닛 파일이 없는 타이머의 stamp 파일이 남아 있습니까?
5. `/var/lib/systemd/linger/` 에 파일이 있는 사용자는 누구이고, 그 사용자의 유닛이 로그인 기록이 없는 시간대에 저널에 나옵니까?

## 참고 문헌

1. systemd, systemd.unit(5) — https://github.com/systemd/systemd/blob/main/man/systemd.unit.xml
2. systemd, systemd.timer(5) — https://github.com/systemd/systemd/blob/main/man/systemd.timer.xml
3. systemd, systemd.service(5) — https://github.com/systemd/systemd/blob/main/man/systemd.service.xml
4. systemd, systemd.exec(5) — https://github.com/systemd/systemd/blob/main/man/systemd.exec.xml
5. systemd, systemctl(1) — https://github.com/systemd/systemd/blob/main/man/systemctl.xml
6. systemd, systemd.generator(7) — https://github.com/systemd/systemd/blob/main/man/systemd.generator.xml
7. systemd, src/core/timer.c (main, v252) — https://github.com/systemd/systemd/blob/main/src/core/timer.c , https://github.com/systemd/systemd/blob/v252/src/core/timer.c
8. systemd, src/basic/fs-util.c (`touch_file`·`touch_fd`) — https://github.com/systemd/systemd/blob/main/src/basic/fs-util.c
9. systemd, loginctl(1) — https://github.com/systemd/systemd/blob/main/man/loginctl.xml
10. systemd, src/login/logind-dbus.c — https://github.com/systemd/systemd/blob/main/src/login/logind-dbus.c
11. systemd, systemd.journal-fields(7) — https://github.com/systemd/systemd/blob/main/man/systemd.journal-fields.xml
12. systemd, catalog/systemd.catalog.in — https://github.com/systemd/systemd/blob/main/catalog/systemd.catalog.in
13. Ubuntu, systemd 패키지 debian/changelog (noble-updates) — https://git.launchpad.net/ubuntu/+source/systemd/tree/debian?h=ubuntu/noble-updates
14. CentOS Stream 9, systemd.spec — https://gitlab.com/redhat/centos-stream/rpms/systemd/-/tree/c9s
15. ForensicArtifacts, artifacts/data/linux.yaml — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
16. UAC, artifacts/files/system/systemd.yaml·artifacts/live_response/system/systemctl.yaml — https://github.com/tclahr/uac/blob/main/artifacts/files/system/systemd.yaml , https://github.com/tclahr/uac/blob/main/artifacts/live_response/system/systemctl.yaml
17. dissect.target, plugins/os/unix/linux/services.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/services.py
18. Velociraptor, Linux.Sys.Services — https://github.com/Velocidex/velociraptor/blob/master/artifacts/definitions/Linux/Sys/Services.yaml
