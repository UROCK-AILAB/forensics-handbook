---
title: "휴지통"
parent: "아티팩트 · 파일 활동"
nav_order: 650
---

# 휴지통 (Trash)

데스크톱에서 파일을 "휴지통으로 버리면" 파일은 사라지지 않고 휴지통 폴더의 `files/` 로 옮겨지며, `info/` 에 원래 경로와 버린 시각을 적은 `.trashinfo` 파일이 하나 생깁니다.

## 무엇을 기록하나 · 왜 생기나

Linux 데스크톱의 휴지통은 FreeDesktop 휴지통 명세 (Trash specification) 를 따릅니다. 명세는 파일을 휴지통 폴더로 옮기는 "버리기 (trashing)" 와 파일 시스템에서 파일을 떼어 내는(unlink) "지우기 (erasing)" 를 나눠 정의합니다[1]. 명세는 저장 방식만 정하고, 실제로 버리고 비우는 일은 GNOME 계열이 쓰는 GLib·gvfs 와 KDE 의 KIO 같은 구현이 합니다[1][2][3][4]. 여러 구현이 같은 휴지통을 함께 쓸 수 있도록 형식을 맞춘 것이라, GNOME 에서 버린 파일을 KDE 에서 보거나 되살릴 수 있습니다[1].

버리기는 파일 관리자의 "휴지통으로 이동", `gio trash` 명령처럼 휴지통 구현을 거치는 동작입니다[2]. 셸의 `rm` 은 명세의 지우기에 해당하므로 휴지통에 아무것도 남기지 않습니다[1]. 그래서 데스크톱 없이 쓰는 서버에서는 휴지통 폴더가 아예 없을 가능성이 있습니다.

## 위치와 버전별 차이

휴지통 폴더는 사용자마다, 그리고 장치(파티션)마다 따로 있습니다.

| 휴지통 | 위치 | 쓰는 경우 |
|---|---|---|
| 홈 휴지통 (home trash) | `$XDG_DATA_HOME/Trash`, 보통 `~/.local/share/Trash` | 홈 폴더와 같은 장치의 파일을 버릴 때[1] |
| 장치 최상위 휴지통 (1) | `$topdir/.Trash/$uid` | 관리자가 만든 `$topdir/.Trash` 가 있고, sticky bit 가 켜져 있고, 심볼릭 링크가 아닐 때[1] |
| 장치 최상위 휴지통 (2) | `$topdir/.Trash-$uid` | (1) 을 쓸 수 없을 때[1] |

`$topdir` 는 그 파일 시스템이 마운트된 디렉터리이고, `$uid` 는 버린 사용자의 숫자 ID 입니다[1]. USB 매체를 `/media/user1/EXAMPLE` 에 붙여 쓰다가 파일을 버렸다면 매체 안의 `/media/user1/EXAMPLE/.Trash-1000` 이 휴지통이 됩니다(만든 예시). 이름은 대소문자를 구분합니다[1].

휴지통 위치와 형식은 배포판이 아니라 데스크톱 구현이 정합니다. Ubuntu 24.04 와 RHEL 9 모두 같은 규칙을 따르고, 구현별 차이는 아래와 같습니다.

| 항목 | GLib·gvfs (GNOME Files, `gio trash`) | KDE KIO (Dolphin 등) |
|---|---|---|
| 홈 휴지통 만들기 | `g_get_user_data_dir()/Trash` 를 권한 0700 으로 만듦[2] | 같은 위치[4] |
| 장치 최상위 휴지통 | `$topdir/.Trash/$uid` → 안 되면 `$topdir/.Trash-$uid`[2] | `$topdir/.Trash/$uid` → `$topdir/.Trash-$uid`[4] |
| 옮기는 방법 | `g_rename` 만 씀. 다른 파일 시스템이면 복사하지 않고 "across filesystem boundaries" 오류[2] | — |
| 휴지통을 쓰지 않는 마운트 | 시스템 내부 마운트. 마운트 옵션이나 fstab 의 `x-gvfs-trash`·`x-gvfs-notrash` 로 바꿈[2] | — |
| 자동 비우기 설정 | GSettings `org.gnome.desktop.privacy` 의 `remove-old-trash-files`(기본 false), `old-files-age`(기본 30일)[5] | `ktrashrc` 의 휴지통 경로별 그룹: `UseTimeLimit`(기본 false), `Days`(기본 7), `UseSizeLimit`(기본 true), `Percent`(기본 10.0), `LimitReachedAction`(기본 0)[4] |
| 상태 파일 | — | `trashrc` 의 `[Status]` 그룹 `Empty=`[4] |

GNOME 의 자동 비우기는 gnome-settings-daemon 이 켜져 있을 때 3600초마다 검사하고, 버린 시각(`trash::deletion-date`)이 `old-files-age` 일보다 오래된 항목을 지웁니다[6]. KDE 는 `UseTimeLimit` 이 켜져 있으면 버린 시각이 `Days` 일보다 오래된 항목을 지웁니다[4]. KDE 의 크기 제한은 휴지통이 장치의 `Percent`% 를 넘을 때 동작하고, `LimitReachedAction` 이 0 이면 경고만, 1 이면 오래된 항목부터, 2 이면 큰 항목부터 지웁니다[4]. 이 설정들의 위치는 [GNOME 흔적](../desktop/gnome.md), [KDE 흔적](../desktop/kde.md)을 봅니다.

## 구조

휴지통 폴더 하나에는 하위 폴더 두 개와 캐시 파일 하나가 있습니다[1].

| 이름 | 내용 |
|---|---|
| `files/` | 버린 파일·폴더를 그대로 옮겨 둔 곳. 폴더는 안의 내용과 함께 통째로 옮김 |
| `info/` | `files/` 의 항목마다 `항목이름.trashinfo` 파일 하나. 하위 폴더 없음 |
| `directorysizes` | 명세 1.0 에서 추가. 버린 폴더의 크기 캐시 |

`info/` 의 파일 이름은 `files/` 의 항목 이름에 `.trashinfo` 를 붙인 것과 정확히 같아야 합니다[1]. `files/foo.bar` 의 정보 파일은 `info/foo.bar.trashinfo` 입니다[1]. 폴더를 버리면 폴더 자체의 정보 파일 하나만 생기고, 폴더 안 파일마다 정보 파일이 생기지는 않습니다[1].

### .trashinfo

데스크톱 항목 파일과 비슷한 텍스트 형식입니다. 첫 줄은 `[Trash Info]` 이고, 키 두 개가 뒤따릅니다[1].

| 키 | 값 |
|---|---|
| `Path` | 원래 위치. `/` 로 시작하면 절대 경로이고, 아니면 휴지통이 있는 디렉터리 기준 상대 경로. 파일 시스템의 바이트를 URL 식(RFC 2396)으로 % 인코딩 |
| `DeletionDate` | 버린 시각. `YYYY-MM-DDThh:mm:ss` 형식이고 사용자(또는 파일 시스템)의 현지 시각 |

상대 경로에는 `..` 가 들어갈 수 없습니다[1]. 명세는 절대 경로를 홈 휴지통에서만 쓰도록 권하고, 구현도 그렇게 합니다. GLib 과 KIO 는 홈 휴지통에는 절대 경로를, 장치 최상위 휴지통에는 `$topdir` 기준 상대 경로를 적습니다[2][4]. 인코딩할 때 두 구현 모두 `/` 는 그대로 두고 나머지를 % 인코딩합니다(GLib `g_uri_escape_string(…, "/", FALSE)`, KIO `QUrl::toPercentEncoding(…, "/")`)[2][4].

GLib 이 쓰는 내용은 `"[Trash Info]\nPath=%s\nDeletionDate=%s\n"` 이고, 파일 권한은 0600 입니다[2]. 시각은 `g_date_time_new_now_local()` 을 `%Y-%m-%dT%H:%M:%S` 로 적고, 현재 시각을 얻지 못하면 `9999-12-31T23:59:59` 를 적습니다[2]. KIO 는 `QDateTime::currentDateTime().toString(Qt::ISODate)` 로 적습니다[4].

읽는 쪽은 첫 줄과 두 키 말고 다른 줄을 무시해야 하고, 같은 키가 여러 번 나오면 첫 번째를 씁니다[1].

### files/ 의 이름

`files/` 안의 이름은 구현이 정하고, 같은 디렉터리 안에서 겹치지만 않으면 됩니다[1]. 같은 이름의 파일을 여러 번 버려도 앞의 것을 덮어쓰면 안 됩니다[1]. GLib 은 이름이 겹치면 첫 점 앞에 번호를 넣어 `이름.2.확장자`, `이름.3.확장자` 로 만들고, 점이 없으면 `이름.2` 로 만듭니다[2]. 이름이 길어 `.trashinfo` 를 붙일 수 없으면 앞부분을 잘라 뒷부분(확장자)을 남깁니다[2]. 명세는 `files/` 의 이름으로 원래 이름을 알아내면 안 되고 반드시 정보 파일을 보라고 정합니다[1].

### directorysizes

한 줄에 버린 폴더 하나를 적습니다[1].

```
[size] [mtime] [percent-encoded-directory-name]
```

`size` 는 `du -B1` 처럼 계산한 블록 바이트 수입니다[1]. `mtime` 은 폴더의 수정 시각이 아니라 그 폴더의 `.trashinfo` 파일 수정 시각이고, epoch 초로 적습니다[1]. 파일은 크기를 stat 으로 알 수 있어서 이 캐시에 넣지 않습니다[1]. 고칠 때는 임시 파일에 쓰고 rename 으로 바꿉니다[1]. KIO 는 `TrashSizeCache` 로 이 파일을 다룹니다[4].

### 버리고 비우는 순서

버릴 때는 `info/` 의 정보 파일을 O_EXCL 로 먼저 만든 다음 파일을 옮깁니다[1]. GLib 은 정보 파일 내용을 다 쓴 뒤에 `g_rename` 으로 옮깁니다[2]. 옮긴 파일의 권한, 접근 시각, 수정 시각, 확장 속성은 버리기 전과 같게 두도록 명세가 권합니다[1].

gvfs 에서 휴지통 항목을 영구히 지우면, 먼저 그 항목을 휴지통의 `expunged/` 아래 무작위 숫자 이름(`g_random_int()` 에서 시작)으로 옮기고 정보 파일을 지웁니다[3]. 그다음 `trash-expunge` 스레드가 `expunged/` 아래를 재귀로 지웁니다[3]. 되살리기(restore)도 같은 옮기기 함수를 거치므로, 원래 위치로 되돌린 항목도 정보 파일이 지워집니다[3].

## 증거로서 의미

**증명하는 것**

- `.trashinfo` 는 이 휴지통 폴더의 주인 계정(홈 휴지통이면 그 홈의 주인, 장치 최상위 휴지통이면 폴더 이름의 `$uid`)으로 동작한 프로그램이, `Path` 에 있던 파일을 `DeletionDate` 의 현지 시각에 휴지통으로 옮겼다는 기록입니다.
- `files/` 에 항목이 남아 있으면 버린 파일의 내용을 그대로 읽을 수 있습니다. 폴더를 버렸다면 폴더 구조와 안의 파일 이름도 바뀌지 않고 남습니다[1].
- 장치 최상위 휴지통이 있으면 그 사용자 번호가 그 매체에서 파일을 버린 적이 있다는 뜻입니다.

**증명하지 못하는 것**

- 누가 버렸는지는 모릅니다. 같은 계정으로 돌던 어떤 프로그램이든 휴지통으로 옮길 수 있습니다.
- 휴지통을 거치지 않은 삭제는 남지 않습니다. `rm` 같은 지우기는 휴지통에 기록을 만들지 않습니다[1].
- 휴지통을 비우거나 항목을 영구 삭제하거나 되살리면 정보 파일도 함께 지워집니다[3][4]. 정보 파일이 없다고 해서 버린 적이 없다는 뜻이 아닙니다.
- 폴더를 버렸을 때 정보 파일은 폴더 하나에만 있으므로, 폴더 안 파일 각각의 원래 경로는 폴더의 `Path` 에 상대 경로를 이어 붙여 짐작합니다.

보고서에는 "user1 계정의 휴지통에 2026-01-02 03:04:05(현지 시각)에 /home/user1/한.txt 를 휴지통으로 옮긴 기록이 있다"처럼 기록이 말하는 만큼만 씁니다(만든 예시).

## 시각 해석

`DeletionDate` 는 버린 순간의 현지 시각이고, 시간대 표기가 없으며 초 단위입니다[1][2][4]. GLib 은 버린 프로세스가 본 현지 시각을 적습니다[2]. UTC 로 바꾸려면 검체의 시간대 설정과, 필요하면 그 사용자 세션의 `TZ` 를 먼저 확인합니다. 시간대를 찾는 곳은 [호스트 이름·시간대·로캘](../system-info/hostname-timezone.md)을 봅니다.

`.trashinfo` 파일 자체의 수정 시각은 버린 순간에 새로 만든 파일이라 `DeletionDate` 와 거의 같습니다[1][2]. 명세도 정보 파일의 수정 시각을 "실제로 버린 시각" 으로 보고 `directorysizes` 의 `mtime` 에 씁니다[1]. 파일 시스템 시각은 UTC 기준 epoch 값이므로(자세한 내용은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md)), `DeletionDate` 와 정보 파일 수정 시각을 비교하면 버릴 때의 시간대 차이를 가늠할 수 있습니다.

`files/` 안 항목의 수정 시각과 접근 시각은 원래 파일의 값을 유지하도록 명세가 권합니다[1]. 그래서 이 값은 버린 시각이 아니라 버리기 전의 파일 시각입니다.

## 함정과 한계

- **`files/` 이름으로 원래 이름 짐작하기.** GLib 은 겹치는 이름에 번호를 붙이고 긴 이름은 앞을 잘라 냅니다[2]. 원래 이름과 위치는 `.trashinfo` 의 `Path` 로만 봅니다[1].
- **상대 경로.** 장치 최상위 휴지통의 `Path` 는 `$topdir` 기준 상대 경로라서, 어느 매체의 어느 마운트 지점이었는지는 휴지통 폴더가 놓인 위치로 알아내야 합니다[1][2]. 매체를 따로 이미징했다면 호스트의 [마운트 기록](../devices/mounts.md)과 맞춰 봅니다.
- **% 인코딩.** `Path` 는 % 인코딩된 바이트라서 한글 파일 이름은 디코딩해야 읽힙니다[1][2][4]. 디코딩한 바이트가 UTF-8 이 아닐 수도 있습니다.
- **날짜 모양.** 명세 본문은 `YYYY-MM-DDThh:mm:ss` 형식을 정하지만, 명세의 예시는 `DeletionDate=20040831T22:32:08` 로 구분자가 없습니다[1]. GLib 과 KIO 는 구분자가 있는 모양으로 적으므로[2][4], 도구가 두 모양을 다 읽는지 확인합니다.
- **수집 범위.** ForensicArtifacts 의 `FreeDesktopTrashInfoFiles`·`FreeDesktopTrashFiles` 는 홈 휴지통의 `info/*.trashinfo` 와 `files/*` 만 정의합니다[7]. UAC 도 홈 휴지통(`%user_home%/.local/share/Trash`)만 모으고, 로그인할 수 없는 계정은 뺍니다(`exclude_nologin_users: true`)[8]. 다른 파티션과 이동식 매체의 `$topdir/.Trash-$uid`, `$topdir/.Trash/$uid` 는 따로 찾아야 합니다.
- **자동 비우기.** GNOME 의 `remove-old-trash-files` 나 KDE 의 `UseTimeLimit`·`LimitReachedAction` 이 켜져 있으면 오래된 항목이 없는 것이 정상입니다[4][5][6]. 설정 값을 먼저 보고 해석합니다.
- **`expunged/` 에 남은 것.** 영구 삭제 중 지우기에 실패한 항목이 `expunged/` 에 남을 수 있습니다[9]. 이 항목에는 정보 파일이 없어 원래 경로를 알 수 없습니다[3][9].
- **흔적 지우기.** 같은 계정이면 정보 파일을 직접 고치거나 지울 수 있습니다. `DeletionDate` 와 정보 파일의 파일 시스템 시각이 크게 어긋나면 고친 흔적일 가능성이 있습니다. 비운 뒤의 파일을 되살리는 일은 [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md)와 [ext4](../../01-foundations/filesystem/ext4/index.md)를 봅니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세와 GLib 코드의 형식대로 만든 `.trashinfo` 예시입니다. 경로와 시각은 지어낸 값입니다.

```
000000 5b 54 72 61 73 68 20 49 6e 66 6f 5d 0a 50 61 74  >[Trash Info].Pat<
000010 68 3d 2f 68 6f 6d 65 2f 75 73 65 72 31 2f 25 45  >h=/home/user1/%E<
000020 44 25 39 35 25 39 43 2e 74 78 74 0a 44 65 6c 65  >D%95%9C.txt.Dele<
000030 74 69 6f 6e 44 61 74 65 3d 32 30 32 36 2d 30 31  >tionDate=2026-01<
000040 2d 30 32 54 30 33 3a 30 34 3a 30 35 0a           >-02T03:04:05.<
```

1. 첫 12바이트가 `[Trash Info]` 이고 줄바꿈(`0a`)이 따릅니다.
2. `Path=` 뒤의 값은 `/` 로 시작하므로 절대 경로이고, 홈 휴지통의 항목입니다.
3. `%ED%95%9C` 를 바이트로 풀면 `ed 95 9c` 이고, UTF-8 로 읽으면 "한" 입니다. 원래 경로는 `/home/user1/한.txt` 입니다.
4. `DeletionDate=2026-01-02T03:04:05` 는 시간대가 없는 현지 시각입니다.
5. 같은 휴지통의 `files/` 에서 이 정보 파일 이름에서 `.trashinfo` 를 뗀 이름을 찾으면 버린 파일의 내용이 나옵니다.

`directorysizes` 는 `16384 1767290645 %ED%95%9C%20%ED%8F%B4%EB%8D%94` 처럼 한 줄이 됩니다(만든 예시). 가운데 값은 그 폴더 정보 파일의 수정 시각(epoch 초)입니다.

### 공개 도구로 한 번

- **dissect.target**: `trash` 플러그인(별칭 `recyclebin`)은 사용자 홈의 `.local/share/Trash` 와, 마운트 지점·`/mnt`·`/media` 아래에서 `.Trash-*` 로 찾은 폴더를 읽습니다[9]. 레코드 필드는 `ts`(DeletionDate), `path`(원래 경로), `filesize`, `deleted_path`(`files/` 안 실제 위치), `source`(.trashinfo 경로)입니다[9]. `files/` 항목은 정보 파일 이름에서 `.trashinfo` 를 뗀 이름으로 찾고, 버린 폴더면 안의 파일마다 레코드를 내지만 `path` 에는 폴더의 `Path` 를 그대로 둡니다[9]. 짝이 되는 `files/` 항목이 없으면 `filesize` 0 인 레코드를 내고 경고를 남깁니다[9].
- **라이브 시스템**: `gio trash --list` 는 현재 사용자의 휴지통 항목을 `trash:///` URI 와 원래 경로를 탭으로 나눠 한 줄씩 찍습니다[2]. 수집 전 상태를 바꾸지 않도록 `--empty`, `--restore` 는 쓰지 않습니다.
- **직접 읽기**: 정보 파일은 텍스트라 `cat` 으로 읽고, `Path` 는 % 디코딩합니다. 정보 파일의 수정 시각은 `stat` 으로 봅니다.

dissect.target 을 쓸 때는 코드상 아래를 알고 씁니다.

- `.Trash-*` 만 찾으므로 `$topdir/.Trash/$uid` 방식 휴지통은 빠질 수 있습니다[9].
- `DeletionDate` 문자열을 그대로 `ts` 에 넣으므로[9], 출력이 UTC 로 표시되면 실제로는 현지 시각인 값일 수 있습니다.
- 상대 경로 `Path` 에 `$topdir` 를 붙이는 처리가 없어서[9], 매체 휴지통의 `path` 는 상대 경로로 나옵니다.
- `expunged` 아래를 `rglob("*/*")` 로 훑어 경로가 없는 레코드를 내고, `ts` 에 항목의 수정 시각을 넣으며 코드 주석은 이를 "지우기에 실패한 시각" 이라고 적습니다[9]. gvfs 는 항목을 옮기기(rename)로 `expunged/` 에 넣으므로[3], 이 값은 원래 파일의 수정 시각일 가능성이 있습니다. 또 `expunged/` 바로 아래에 파일 하나로 남은 항목은 이 패턴에 걸리지 않을 가능성이 있어 폴더를 직접 봅니다.

## 교차 검증

| 함께 볼 아티팩트 | 맞춰 볼 것 |
|---|---|
| [최근 연 파일](../execution/recently-used.md) | 버리기 전에 그 파일을 연 기록 |
| [썸네일 캐시](thumbnails.md) | 원본을 버리거나 비운 뒤에도 남은 썸네일 |
| [셸 명령 기록](../execution/shell-history/index.md) | `gio trash`, `rm` 명령과 경로 |
| [감사 로그의 파일 감시](auditd-watches.md) | 감시 규칙이 있으면 `rename`·`renameat2` 기록 |
| [마운트 기록](../devices/mounts.md) | 매체의 `.Trash-uid` 폴더가 어느 마운트 지점이었는지 |
| [UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md) | `.Trash-$uid` 의 숫자가 어느 계정인지 |

여러 기록의 시각을 한 줄로 늘어놓는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md)를 봅니다.

## 실습

공개 Linux 데스크톱 검체(NIST CFReDS 등)나 직접 만든 가상 머신 이미지로 아래 질문을 풀어 봅니다.

1. 사용자마다 `~/.local/share/Trash/info/` 에 정보 파일이 몇 개 있고, `files/` 의 항목과 짝이 모두 맞는가?
2. `DeletionDate` 와 정보 파일의 수정 시각(UTC)은 몇 시간 차이가 나는가? 그 차이는 검체의 시간대 설정과 맞는가?
3. `/`, `/home` 말고 다른 파티션이나 이동식 매체 이미지에 `.Trash-1000` 같은 폴더가 있는가? 있다면 `Path` 의 상대 경로를 어느 마운트 지점에 붙여야 하는가?
4. GNOME 의 `remove-old-trash-files` 나 KDE `ktrashrc` 의 자동 삭제가 켜져 있는가? 켜져 있다면 가장 오래된 `DeletionDate` 는 설정과 맞는가?
5. `expunged/` 폴더가 있는가? 있다면 안의 항목은 어떤 파일로 보이는가?

## 참고 문헌

1. FreeDesktop.org, Trash specification 1.0 — https://specifications.freedesktop.org/trash-spec/latest/ (사본: https://github.com/freedesktop-unofficial-mirror/xdg__xdg-specs/blob/master/trash/trashspec.html)
2. GLib, gio/glocalfile.c·gio/gio-tool-trash.c — https://github.com/GNOME/glib/blob/main/gio/glocalfile.c , https://github.com/GNOME/glib/blob/main/gio/gio-tool-trash.c
3. gvfs, daemon/trashlib/trashitem.c·trashexpunge.c — https://github.com/GNOME/gvfs/blob/master/daemon/trashlib/trashitem.c , https://github.com/GNOME/gvfs/blob/master/daemon/trashlib/trashexpunge.c
4. KDE KIO, src/kioworkers/trash/trashimpl.cpp·trashsizecache.cpp·DESIGN — https://github.com/KDE/kio/blob/master/src/kioworkers/trash/trashimpl.cpp , https://github.com/KDE/kio/blob/master/src/kioworkers/trash/trashsizecache.cpp , https://github.com/KDE/kio/blob/master/src/kioworkers/trash/DESIGN
5. gsettings-desktop-schemas, schemas/org.gnome.desktop.privacy.gschema.xml.in — https://github.com/GNOME/gsettings-desktop-schemas/tree/master/schemas
6. gnome-settings-daemon, plugins/housekeeping/gsd-disk-space.c·gsd-housekeeping-manager.c — https://github.com/GNOME/gnome-settings-daemon/blob/master/plugins/housekeeping/gsd-disk-space.c , https://github.com/GNOME/gnome-settings-daemon/blob/master/plugins/housekeeping/gsd-housekeeping-manager.c
7. ForensicArtifacts, artifacts/data/linux.yaml — https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
8. UAC, artifacts/files/system/trash.yaml·trash_info.yaml — https://github.com/tclahr/uac/tree/main/artifacts/files/system
9. dissect.target, dissect/target/plugins/os/unix/trash.py — https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/trash.py
