---
title: "최근 연 파일"
parent: "아티팩트 · 실행 흔적"
nav_order: 490
---

# 최근 연 파일 (recently-used.xbel)

GTK 앱과 KDE 앱은 사용자가 열거나 저장한 파일의 URI 를 사용자 홈의 `recently-used.xbel` 한 파일에 적고, 항목마다 처음 등록한 시각과 마지막으로 바뀐 시각, 등록한 앱과 횟수를 함께 남깁니다.

## 무엇을 기록하나 · 왜 생기나

GTK 앱과 KDE 앱이 보여 주는 최근 파일 목록은 이 파일을 읽어 만듭니다[4][7]. GTK 의 최근 파일 관리자 (GtkRecentManager) 는 GLib 의 북마크 파일 (GBookmarkFile) 형식으로 목록을 저장하고[4][1], KDE 의 KIO 라이브러리에 있는 최근 문서 기능 (KRecentDocument) 도 같은 파일에 같은 형식으로 씁니다[7]. 그래서 GNOME 데스크톱이든 KDE Plasma 든 한 계정의 최근 파일 기록이 한 파일에 섞여 쌓입니다.

앱이 파일 하나를 등록하면 목록에 그 URI 의 항목이 생기고, 항목 안에는 MIME 형식, 등록한 앱의 이름과 실행 명령, 그 앱이 등록한 횟수가 들어갑니다[1][7]. 같은 파일을 다시 등록하면 새 항목을 만들지 않고 기존 항목의 횟수와 시각을 고칩니다[1][7]. 셸에서 명령으로 연 파일이나 이 기능을 쓰지 않는 앱이 연 파일은 이 목록에 들어가지 않으므로, 셸 쪽 흔적은 [셸 명령 기록](shell-history/index.md) 에서 봅니다.

## 위치와 버전별 차이

기본 위치는 `$XDG_DATA_HOME/recently-used.xbel` 이고, `XDG_DATA_HOME` 이 비어 있으면 `~/.local/share/recently-used.xbel` 입니다[4][7][8]. GTK 2.24, GTK 3.24, 현재 GTK 모두 파일 이름이 같고[4], KDE 는 Qt 의 사용자 데이터 위치 (GenericDataLocation) 아래 같은 이름을 씁니다[7]. 경로는 배포판이 아니라 이 규칙이 정하므로 Ubuntu 24.04 와 RHEL 9 에서 같습니다. GTK 나 KDE 앱을 쓰지 않은 계정에는 이 파일이 생기지 않습니다.

| 경로 | 쓰는 쪽 | 비고 |
|---|---|---|
| `~/.local/share/recently-used.xbel` | GTK 2.10 이후, 현재 KDE KIO | 현재 기본 위치[4][7] |
| `~/.local/share/recently-used.xbel.lock` | KDE KIO | KDE 가 쓸 때 잡는 잠금 파일, GTK 는 쓰지 않음[7] |
| `~/.recently-used.xbel` | 옛 GTK | GTK 2.24 가 발견하면 새 위치로 옮기거나 합침[4] |
| `~/.config/libreoffice`, `~/.var/app/org.libreoffice.LibreOffice`, `~/snap/libreoffice` 아래 `recently-used.xbel` | LibreOffice(일반·Flatpak·Snap) | UAC 가 따로 모으는 위치[11] |

GTK 2.24 는 옛 파일 `~/.recently-used.xbel` 이 있고 새 파일이 없으면 옛 파일의 이름을 새 위치로 바꾸고, 둘 다 있으면 내용을 합친 뒤 옛 파일을 지웁니다[4]. 오래 쓴 시스템이나 옛 이미지에서는 두 위치를 다 봅니다.

수집 도구마다 보는 범위가 다릅니다. ForensicArtifacts 의 `GTKRecentlyUsedDatabase` 와 dissect 의 `recently_used` 플러그인은 `~/.local/share/recently-used.xbel` 하나만 봅니다[10][9]. UAC 의 `linux_mru` 는 로그인할 수 있는 사용자 홈 전체에서 `recently-used.xbel` 이라는 이름의 파일을 모두 모으므로 샌드박스 앱의 사본까지 걸립니다[11].

GTK 는 저장할 때마다 파일 권한을 0600 으로 맞춥니다[4]. 다른 권한이 붙어 있다면 GTK 가 아닌 무엇이 파일을 마지막으로 썼을 가능성이 있습니다.

## 구조

XBEL 1.0 형식의 UTF-8 XML 이고, 루트 요소 `xbel` 에 두 이름공간 `bookmark`(`http://www.freedesktop.org/standards/desktop-bookmarks`) 와 `mime`(`http://www.freedesktop.org/standards/shared-mime-info`) 을 선언합니다[1][7]. 파일 하나에 `bookmark` 요소가 파일마다 하나씩 들어갑니다.

| 위치 | 이름 | 뜻 |
|---|---|---|
| `bookmark` 속성 | `href` | 파일의 URI. 로컬 파일은 `file:///…` 이고 경로 문자는 퍼센트 인코딩[1][7] |
| `bookmark` 속성 | `added` | 항목이 처음 생긴 시각[1] |
| `bookmark` 속성 | `modified` | 항목이 마지막으로 바뀐 시각[1] |
| `bookmark` 속성 | `visited` | "마지막으로 연 시각" 자리. 실제로 언제 바뀌는지는 아래 시각 해석 참고[1][7] |
| `bookmark` 아래 | `title`, `desc` | 앱이 표시 이름·설명을 넘겼을 때만[1][4] |
| `info/metadata` | `owner="http://freedesktop.org"` | 데스크톱 북마크 규약의 메타데이터 묶음[1] |
| `metadata` 아래 | `mime:mime-type` 의 `type` | MIME 형식[1] |
| `metadata` 아래 | `bookmark:groups/bookmark:group` | 분류 이름. 앱이 분류를 넘기지 않으면 KDE 는 MIME 형식에 따라 `Graphics`·`Video`·`Audio` 를 넣음[1][7] |
| `metadata` 아래 | `bookmark:applications/bookmark:application` | 등록한 앱마다 한 줄. 속성 `name`·`exec`·`modified`·`count`[1] |
| `metadata` 아래 | `bookmark:icon` 의 `href`·`type` | 아이콘(있을 때만)[1] |
| `metadata` 아래 | `bookmark:private` | 등록한 앱에서만 보여 주라는 표시[1][4] |

`bookmark:application` 의 `modified` 는 그 앱이 마지막으로 등록한 시각이고, `count` 는 그 앱이 이 파일을 등록한 횟수입니다[1][7]. 옛 파일에는 같은 뜻의 속성이 `timestamp` 라는 이름으로 남아 있을 수 있습니다[1]. GLib 는 등록한 앱이 하나도 없는 항목과 `count` 가 0 인 앱은 파일에 쓰지 않습니다[1].

`exec` 는 쓰는 쪽에 따라 모양이 다릅니다. GLib 는 실행 명령을 셸 따옴표로 감싸 저장하고[1], XML 로 쓸 때 작은따옴표를 `&apos;` 로 바꾸므로[3] 파일에는 `&apos;gedit %u&apos;` 같은 모양으로 보입니다. KDE 는 앱의 데스크톱 파일에 적힌 실행 명령을 따옴표 없이 쓰고, `%U`·`%F` 는 소문자로 바꾸며, 인자 자리가 없으면 로컬 파일은 `%f`, 그 밖은 `%u` 를 붙입니다[7]. 데스크톱 파일을 찾지 못하면 실행 명령 대신 앱 이름을 쓰고, `name` 에는 데스크톱 파일 이름을 씁니다[7].

만든 예시(코드로 만든 예시이며 사용자 이름·경로·시각은 지어낸 값)는 아래와 같습니다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info"
>
  <bookmark href="file:///home/user1/Documents/report%202024.odt" added="2024-04-05T01:02:03.123456Z" modified="2024-04-06T02:03:04.654321Z" visited="2024-04-05T01:02:03.123456Z">
    <info>
      <metadata owner="http://freedesktop.org">
        <mime:mime-type type="application/vnd.oasis.opendocument.text"/>
        <bookmark:applications>
          <bookmark:application name="LibreOffice" exec="&apos;soffice %u&apos;" modified="2024-04-06T02:03:04.654321Z" count="2"/>
        </bookmark:applications>
      </metadata>
    </info>
  </bookmark>
</xbel>
```

이 예시는 GLib 가 쓰는 모양을 따른 것입니다. 루트 요소를 여러 줄에 나눠 쓰고 닫는 `>` 를 따로 한 줄에 두는 것은 GLib 의 출력 방식이고[1], KDE 는 Qt 의 XML 작성기로 들여쓰기 2칸의 다른 모양을 씁니다[7].

## 증거로서 의미

**증명하는 것**

- 이 계정으로 실행한 GTK 또는 KDE 앱이 이 URI 를 최근 파일로 등록했다는 것. 등록한 앱의 이름과 실행 명령도 함께 남습니다.
- 앱마다 이 파일을 몇 번 등록했는지(`count`)와 그 앱이 마지막으로 등록한 시각.
- 항목이 목록에 처음 들어간 시각(`added`)과 마지막으로 바뀐 시각(`modified`). 모두 UTC 입니다.
- URI 가 `/media` 나 `/run/media` 아래를 가리키면, 그 경로에 붙은 매체의 파일을 앱으로 다룬 적이 있다는 것.

**증명하지 못하는 것**

- 파일의 내용, 그리고 그 파일이 지금도 있는지. 이 목록은 URI 만 적습니다.
- 사용자가 파일을 "열었다" 는 것 자체. 등록은 앱이 정한 때에 하므로 열기인지 저장인지는 앱에 따라 다릅니다.
- `visited` 를 마지막으로 연 시각으로 보는 것. GTK 가 쓴 항목은 다시 등록해도 이 값이 바뀌지 않습니다[1][4].
- 목록에 없다는 것이 쓰지 않았다는 뜻이라는 것. 등록하지 않는 앱, 설정으로 끈 기록, 보존 기간이 지나 잘린 항목, KDE 에서 숨김·임시 경로 파일은 빠집니다(아래 함정 참고).

보고서에는 "2024-04-06 02:03:04 UTC 에 LibreOffice 가 `report 2024.odt` 를 두 번째로 최근 파일에 등록한 기록이 있다" 처럼 기록이 말하는 만큼만 씁니다.

## 시각 해석

모든 시각은 UTC 이고 문자열 끝에 `Z` 가 붙습니다. GLib 와 KDE 둘 다 현재 UTC 시각을 가져와 씁니다[1][2][7]. 문자열을 epoch 값과 맞춰 보는 방법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

| 값 | GTK(GLib) 에서 바뀌는 때 | KDE 에서 바뀌는 때 |
|---|---|---|
| `added` | 새 항목을 만들 때 한 번[1] | 새 항목을 만들 때 한 번[7] |
| `modified`(항목) | 새 항목일 때, 그리고 어느 앱이든 다시 등록하거나 앱을 지울 때[1] | 새 항목일 때, 그리고 다시 등록할 때[7] |
| `visited` | 새 항목일 때만. GtkRecentManager 로 다시 등록해도 그대로[1][4] | 새 항목일 때, 그리고 다시 등록할 때[7] |
| `modified`(앱) | 그 앱이 등록할 때마다[1] | 그 앱이 등록할 때마다[7] |
| `count`(앱) | 등록할 때마다 1 씩 늘어남[1] | 같은 앱이 다시 등록하면 1 씩 늘어남[7] |

그래서 GTK 가 만든 항목은 `visited` 가 `added` 와 같은 경우가 많고, 마지막 사용 시각은 항목 `modified` 나 앱 `modified` 로 읽습니다. KDE 가 다시 등록한 항목은 `visited` 도 그때 바뀝니다.

시각 문자열 모양으로 쓴 쪽을 가늠할 수 있습니다. GLib 는 `%C%y-%m-%dT%H:%M:%S`(연도 네 자리) 뒤에 마이크로초가 0 이 아니면 `.` 과 6자리를 붙이고 UTC 면 `Z` 를 붙입니다[2]. KDE 는 밀리초까지 만든 뒤 `Z` 를 떼고 `000Z` 를 붙이므로 소수부가 늘 `.123000Z` 처럼 끝 세 자리가 0 입니다[7]. GLib 는 파일을 읽을 때 시각을 해석해 두었다가 다시 쓰므로 이 모양은 GTK 가 파일을 다시 써도 유지됩니다[1][2]. 다만 밀리초가 0 인 KDE 시각(`.000000Z`)은 GLib 가 다시 쓰면 소수부가 빠집니다[2]. 끝 세 자리가 0 인 시각이 여러 개 모여 있으면 KDE 가 쓴 항목일 가능성이 있습니다.

`time_t` 를 받는 옛 GLib 함수로 넣은 시각은 초 단위라 소수부 없이 `2024-04-05T01:02:03Z` 모양으로 저장됩니다[1][2]. GTK 2.24 가 옛 파일을 합칠 때 이 함수를 씁니다[4].

파일 자체의 mtime 은 목록을 마지막으로 저장한 때입니다. GLib 는 저장할 때마다 파일을 통째로 다시 쓰므로[1] 파일 mtime 은 보통 가장 늦은 항목 `modified` 와 가깝고, 둘이 크게 어긋나면 누군가 파일을 따로 고쳤는지 봅니다. 여러 기록을 시간순으로 합치는 방법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 함정과 한계

- **보존 기간 기본값이 둘입니다.** GTK 자체 설정 `gtk-recent-files-max-age` 의 기본은 30일이고, 저장할 때 항목 `modified` 가 이 일수보다 오래된 항목을 지웁니다[4][5]. 0 이면 목록을 비우고 -1 이면 지우지 않습니다[4][5]. GNOME 스키마 `org.gnome.desktop.privacy` 의 `recent-files-max-age` 기본값은 -1(무기한)이고[6], GNOME 세션에서는 설정 데몬(X11)이나 GTK4 의 Wayland 백엔드가 이 값을 GTK 에 넘깁니다[6][5]. 그래서 GNOME 에서는 오래된 항목이 남아 있기 쉽고, GNOME 밖에서 GTK 앱만 쓴 계정은 30일 넘은 항목이 사라졌을 수 있습니다. 검체의 실제 값은 [GNOME 흔적](../desktop/gnome.md) 의 dconf 사용자 DB 에서 확인합니다.
- **기록을 끈 계정.** GNOME 의 `remember-recent-files` 가 false 이면(`gtk-recent-files-enabled` 가 FALSE) GTK 는 새 항목을 넣지 않고, 다음 저장 때 목록을 비웁니다[4][5][6]. 파일이 있는데 항목이 하나도 없다면 이 설정이나 목록 비우기를 먼저 의심합니다. GTK 의 목록 비우기 함수도 항목 없는 파일을 새로 씁니다[4].
- **개수 상한.** GTK 는 저장할 때 1000 개를 넘는 만큼 항목을 지웁니다[4]. KDE 는 등록한 뒤 항목 수가 `MaxEntries`(기본 300)를 넘으면 항목 `modified` 가 오래된 것부터 지우는데, 넘친 수가 10 개를 넘을 때는 이 정리를 하지 않습니다[7].
- **KDE 가 지우는 것.** KDE 설정 `UseRecent` 가 false 이거나 `MaxEntries` 가 0 이면 KDE 앱이 다음에 등록하려 할 때 파일 자체를 지우므로 GTK 앱의 기록까지 함께 사라집니다[7]. `IgnoreHidden`(기본 true)이면 경로에 `/.` 가 든 숨김 파일은 적지 않고, KDE 가 파일을 다시 쓸 때 GTK 가 넣어 둔 숨김 경로 항목도 빼 버립니다[7]. 임시 폴더 아래 파일도 적지 않습니다[7]. 설정 키 자리는 [KDE 흔적](../desktop/kde.md) 에서 다룹니다.
- **지운 항목은 파일 안에 남지 않습니다.** GLib 와 KDE 모두 파일을 처음부터 끝까지 새로 쓰므로[1][7] 목록에서 빠진 항목은 현재 파일에 흔적이 없습니다. 옛 내용은 파일 시스템의 빈 공간에 남아 있을 가능성만 있습니다.
- **손으로 고치기 쉽습니다.** 평문 XML 이라 편집기로 항목이나 시각을 바꿀 수 있습니다. 이때는 파일 mtime·ctime 이 바뀌고, 들여쓰기나 시각 소수부 모양이 GLib·KDE 어느 쪽과도 맞지 않는 흔적이 남을 수 있습니다. 흔적 지우기 판단 흐름은 [흔적을 지웠나](../../04-scenarios/insider/anti-forensics.md) 에서 다룹니다.
- **샌드박스 앱의 사본.** Flatpak·Snap 으로 설치한 앱은 자기 폴더 아래에 따로 `recently-used.xbel` 을 둘 수 있습니다[11]. 기본 위치 하나만 모으는 도구로는 이 사본이 빠집니다.
- **도구가 시각을 버리는 경우.** dissect 는 시각을 `%Y-%m-%dT%H:%M:%S.%fZ` 한 가지 형식으로만 해석하고, 맞지 않으면 경고를 남기고 빈 값(None)으로 둡니다[9]. 소수부가 없는 GLib 시각이 그런 경우입니다[2]. 또 dissect 는 항목의 대표 시각(`ts`)으로 `visited` 를 쓰므로[9] GTK 항목은 타임라인에 처음 등록한 때로만 찍힙니다.
- **plaso 기본 목록에 파서가 없습니다.** plaso 의 `linux` 프리셋 파서 목록에는 xbel 파서가 없습니다[12]. 이 파일은 따로 파싱해 타임라인에 넣습니다.

## 직접 분석해 보기

**헥스로 한 번.** 파일 첫 16바이트는 XML 선언의 앞부분입니다. 아래는 GLib 출력 코드[1]로 만든 예시입니다.

```text
00000000: 3c3f 786d 6c20 7665 7273 696f 6e3d 2231  <?xml version="1
```

XML 선언 뒤에 `<xbel version="1.0"` 이 오면 이 형식입니다. 파일 크기가 작고 `<bookmark` 가 하나도 없다면 목록을 비운 상태입니다.

**텍스트로 한 번.** 평문이라 편집기나 `xmllint` 로 읽으면 됩니다. 수집한 사본에서 URI 와 시각만 뽑으려면 이름공간이 없는 `bookmark` 요소의 속성을 봅니다.

```text
xmllint --format recently-used.xbel | less
xmllint --xpath '//bookmark/@href | //bookmark/@modified' recently-used.xbel
```

`href` 의 퍼센트 인코딩(`%20` 은 공백)은 풀어서 경로로 읽습니다. 앱별 `count` 와 `modified` 는 `bookmark:applications` 아래에 있습니다.

**공개 도구로 한 번.** dissect 는 사용자 홈마다 `.local/share/recently-used.xbel` 을 찾아 항목, 아이콘, 앱을 각각 레코드로 냅니다[9]. 항목 레코드에는 `href`·`added`·`modified`·`visited`·`mimetype`·`groups`·`private` 이, 앱 레코드에는 `name`·`exec`·`count` 와 앱 `modified` 가 들어갑니다[9].

```text
target-query -f recently_used /mnt/evidence/image.E01
```

`ts` 칸은 `visited` 이므로 GTK 항목의 마지막 사용 시각은 `modified` 칸과 앱 레코드의 시각으로 다시 봅니다. 샌드박스 앱 사본과 옛 `~/.recently-used.xbel` 은 이 플러그인이 보지 않으므로 파일을 따로 찾아 같은 방법으로 읽습니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [셸 명령 기록](shell-history/index.md)·[감사 로그의 실행 기록](auditd-execve.md) | `exec` 에 적힌 앱을 그 시각에 실행한 기록이 있는가 |
| [GNOME 흔적](../desktop/gnome.md)·[KDE 흔적](../desktop/kde.md) | 기록을 끄거나 보존 기간을 바꾼 설정이 있는가, 같은 파일이 다른 데스크톱 기록에도 있는가 |
| [썸네일 캐시](../file-activity/thumbnails.md) | 같은 URI 의 썸네일이 있는가, 원본이 사라졌어도 모습이 남았는가 |
| [휴지통](../file-activity/trash.md) | 목록의 파일을 뒤에 버렸는가 |
| [마운트 기록](../devices/mounts.md)·[USB 장치 연결 기록](../devices/usb.md) | `/media`·`/run/media` 아래 URI 의 시각에 어떤 매체가 붙어 있었는가 |
| [Linux 의 브라우저 프로필](../desktop/browsers.md) | 다운로드한 파일을 뒤에 열었는가 |
| 파일 시스템 시각 | URI 가 가리키는 파일의 mtime·atime 이 항목 시각과 어떻게 놓이는가 |

## 실습

NIST CFReDS 같은 공개 검체 모음에서 Linux 데스크톱 이미지를 골라 풀어 봅니다.

1. 사용자 홈마다 `~/.local/share/recently-used.xbel` 이 있는가? `~/.recently-used.xbel` 이나 `~/.var/app`·`~/snap` 아래 사본도 있는가?
2. 항목은 몇 개이고, 가장 이른 `added` 와 가장 늦은 `modified` 는 언제인가? 30일보다 오래된 항목이 남아 있다면 보존 기간 설정은 무엇이었다고 볼 수 있는가?
3. `visited` 가 `added` 와 다른 항목이 있는가? 그 항목의 시각 소수부는 GLib 모양인가, KDE 모양인가?
4. `count` 가 가장 큰 파일은 무엇이고, 어느 앱이 등록했는가?
5. `/media` 나 `/run/media` 아래를 가리키는 URI 가 있다면, 그 시각에 연결된 이동식 매체를 다른 기록으로 찾을 수 있는가?
6. 파일 mtime 과 가장 늦은 항목 `modified` 는 얼마나 떨어져 있는가?

## 참고 문헌

1. GNOME glib, glib/gbookmarkfile.c. https://github.com/GNOME/glib/blob/main/glib/gbookmarkfile.c
2. GNOME glib, glib/gdatetime.c (`g_date_time_format_iso8601`). https://github.com/GNOME/glib/blob/main/glib/gdatetime.c
3. GNOME glib, glib/gmarkup.c (`g_markup_escape_text`). https://github.com/GNOME/glib/blob/main/glib/gmarkup.c
4. GNOME gtk, gtk/gtkrecentmanager.c (gtk-2-24, gtk-3-24, main 브랜치). https://github.com/GNOME/gtk/blob/gtk-2-24/gtk/gtkrecentmanager.c , https://github.com/GNOME/gtk/blob/gtk-3-24/gtk/gtkrecentmanager.c , https://github.com/GNOME/gtk/blob/main/gtk/gtkrecentmanager.c
5. GNOME gtk, gtk/gtksettings.c (gtk-3-24), gdk/wayland/gdksettings-wayland.c (main). https://github.com/GNOME/gtk/blob/gtk-3-24/gtk/gtksettings.c , https://github.com/GNOME/gtk/blob/main/gdk/wayland/gdksettings-wayland.c
6. GNOME gsettings-desktop-schemas, schemas/org.gnome.desktop.privacy.gschema.xml.in; GNOME gnome-settings-daemon, plugins/xsettings/gsd-xsettings-manager.c. https://github.com/GNOME/gsettings-desktop-schemas/blob/master/schemas/org.gnome.desktop.privacy.gschema.xml.in , https://github.com/GNOME/gnome-settings-daemon/blob/master/plugins/xsettings/gsd-xsettings-manager.c
7. KDE kio, src/core/krecentdocument.cpp. https://github.com/KDE/kio/blob/master/src/core/krecentdocument.cpp
8. freedesktop.org, XDG Base Directory Specification (basedir/basedir-spec.xml). https://gitlab.freedesktop.org/xdg/xdg-specs/-/tree/master/basedir
9. Fox-IT dissect.target, dissect/target/plugins/os/unix/linux/recentlyused.py. https://github.com/fox-it/dissect.target/blob/main/dissect/target/plugins/os/unix/linux/recentlyused.py
10. ForensicArtifacts, artifacts/data/linux.yaml (`GTKRecentlyUsedDatabase`). https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
11. UAC, artifacts/files/system/linux_mru.yaml, artifacts/files/applications/libreoffice_mru.yaml. https://github.com/tclahr/uac/tree/main/artifacts/files
12. log2timeline plaso, plaso/data/presets.yaml. https://github.com/log2timeline/plaso/blob/main/plaso/data/presets.yaml
