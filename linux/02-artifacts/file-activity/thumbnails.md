---
title: "썸네일 캐시"
parent: "아티팩트 · 파일 활동"
nav_order: 660
---

# 썸네일 캐시 (Thumbnails)

파일 관리자나 파일 선택 창이 미리보기를 만들면 사용자 홈 폴더의 썸네일 캐시에 PNG 를 남기고, 그 PNG 안에 원본 파일의 URI 와 수정 시각을 적어 둡니다. 원본을 지운 뒤에도 축소 이미지와 경로가 남을 수 있어서, 어떤 파일이 어느 경로에 있었는지 보여 주는 흔적이 됩니다.

## 무엇을 기록하나 · 왜 생기나

리눅스 데스크톱은 freedesktop 의 썸네일 관리 표준 (Thumbnail Managing Standard) 을 따라 미리보기를 한곳에 모읍니다. 여러 프로그램이 같은 파일의 미리보기를 제각각 만들지 않고 나눠 쓰려는 규약이고, 파일 대화 상자나 파일 관리자가 파일을 알아보기 쉽게 하려고 씁니다[1]. GNOME 은 libgnome-desktop 의 썸네일 공장 (GnomeDesktopThumbnailFactory) 이[2], KDE 는 KIO 의 미리보기 작업이 이 캐시를 읽고 씁니다[5][6][10].

캐시 파일 하나는 원본 파일 하나의 미리보기입니다. 파일 이름은 원본 URI 의 MD5 값이고, PNG 텍스트 청크에는 원본 URI 와 원본의 수정 시각(mtime)이 들어갑니다[1]. 미리보기 만들기에 실패하면 빈 PNG(GNOME 은 1×1 투명 이미지)를 실패 폴더에 남기는데, 여기에도 URI 와 mtime 이 들어갑니다[1][2].

## 위치와 버전별 차이

캐시 폴더는 `$XDG_CACHE_HOME/thumbnails` 이고, 이 변수가 비어 있으면 `$HOME/.cache/thumbnails` 입니다[1]. 이 위치는 표준 0.8.0(2012-05)에서 XDG 기준 폴더를 따르도록 바꾼 결과입니다[1]. 그 전의 옛 위치 `~/.thumbnails` 는 GNOME 정리 코드가 지금도 함께 청소하는 대상이라, 오래 쓴 계정에는 두 곳이 다 있을 수 있습니다[3].

| 하위 폴더 | 크기 | 정한 곳 |
|---|---|---|
| `normal/` | 128×128 이하 | 표준[1], GNOME[2], KDE[6] |
| `large/` | 256×256 이하 | 표준[1], GNOME[2], KDE[6] |
| `x-large/` | 512×512 이하 | GNOME(2020-12-17 추가)[2], KDE[6] |
| `xx-large/` | 1024×1024 이하 | GNOME(2020-12-17 추가)[2], KDE[6] |
| `fail/프로그램-버전/` | 빈 PNG | 표준(예 `fail/nautilus-1.0`)[1], GNOME 은 `fail/gnome-thumbnail-factory/`[2] |

`x-large/`·`xx-large/` 는 표준 0.8.0 에는 없고 구현이 나중에 넣은 폴더입니다[1][2]. 원본 파일 옆의 `.sh_thumbnails/` 폴더는 CD-ROM 처럼 여러 사람이 함께 쓰는 읽기 전용 모음이고, 이 폴더의 PNG 는 URI 에 디렉터리 없이 파일 이름만 적습니다[1].

Ubuntu 24.04 와 RHEL 9 는 경로 규칙이 같습니다. 두 배포판의 차이는 어느 데스크톱을 설치했는지와, 설치된 gsettings-desktop-schemas 판에 따라 정리 기준 크기가 다르다는 점에서 나옵니다(아래 "함정과 한계"). 썸네일은 데스크톱 프로그램이 만들기 때문에, 데스크톱 없이 설치한 서버에는 이 캐시가 없을 가능성이 높습니다.

## 구조

### 파일 이름

파일 이름은 원본의 정규화된 절대 URI(예 `file:///home/jens/photos/me.png`)를 MD5 로 해시한 16진 32자에 `.png` 를 붙인 것이라, 모든 캐시 파일 이름은 36자입니다[1]. 해시 대상은 파일 내용이 아니라 URI 문자열입니다[1]. GNOME 은 받은 URI 문자열을 그대로 해시합니다[2]. KDE 는 파일 미리보기에서 항목 URL 을 퍼센트 인코딩한 문자열(`toEncoded(QUrl::RemovePassword | QUrl::FullyEncoded)`)을 해시하고, 원본이 심볼릭 링크이면 링크가 가리키는 대상 경로의 URI 를 씁니다[10]. KDE 가 폴더 아이콘에 겹쳐 그릴 파일의 썸네일을 만들 때는 `QUrl::fromLocalFile(경로).toEncoded()` 를 해시합니다[5].

### PNG 텍스트 키

PNG 형식 자체는 8비트, 비월(non-interlaced), 알파 채널이 있는 이미지입니다[1]. 원본 정보는 `tEXt` 청크에 키와 값으로 들어갑니다[1][8].

| 키 | 필수 여부 | 뜻 |
|---|---|---|
| `Thumb::URI` | 필수 | 원본의 절대 URI[1] |
| `Thumb::MTime` | 필수 | 원본의 수정 시각, 1970-01-01 부터의 초[1] |
| `Thumb::Size` | 선택 | 원본 크기(바이트)[1] |
| `Thumb::Mimetype` | 선택 | 원본의 MIME 형식[1] |
| `Software` | 선택 | 썸네일을 만든 프로그램[1] |
| `Description` | 선택 | 썸네일 설명[1] |
| `Thumb::Image::Width`·`Thumb::Image::Height` | 형식별 | 원본 이미지의 가로·세로 픽셀[1] |
| `Thumb::Document::Pages` | 형식별 | 원본 문서의 쪽수[1] |
| `Thumb::Movie::Length` | 형식별 | 원본 동영상 길이(초)[1] |

구현마다 채우는 키가 다릅니다. GNOME 은 `Thumb::URI`, `Thumb::MTime`, `Software=GNOME::ThumbnailFactory` 를 넣고, 원본 크기를 알면 `Thumb::Image::Width`·`Thumb::Image::Height` 를 넣으며 `Thumb::Size` 는 넣지 않습니다[2]. KDE 의 파일 미리보기는 `Thumb::URI`, `Thumb::MTime`, `Thumb::Size`, `Thumb::Mimetype` 과 `Software=KDE Thumbnail Generator 플러그인이름 (v판)` 을 넣습니다(판 정보가 없는 플러그인은 괄호 부분이 빠짐)[10]. KDE 가 폴더 아이콘용으로 만든 썸네일에는 `Thumb::URI`, `Thumb::MTime`, `Thumb::Size` 만 들어가고 `Software` 는 없습니다[5].

### 청크 배치

PNG 는 서명 `89 50 4E 47 0D 0A 1A 0A` 뒤에 청크가 이어집니다[8]. 청크는 길이(4바이트, 큰 끝 순서), 형식(4바이트), 데이터, CRC(4바이트, 형식과 데이터를 대상으로 계산) 순서입니다[8]. `tEXt` 청크의 형식 바이트는 `74 45 58 74` 이고, 데이터는 키워드(1~79바이트), `00` 한 바이트, 텍스트 순서입니다[8]. 텍스트는 Latin-1 이고 끝에 NUL 이 없어서 청크 길이로 끝을 압니다[8]. 압축한 텍스트는 `zTXt`(`7A 54 58 74`) 청크에 들어갑니다[8].

### 만들고 고치는 방식

표준은 같은 폴더에 임시 이름으로 쓴 뒤 최종 이름으로 rename 하라고 정합니다[1]. GNOME 은 `최종경로.XXXXXX` 임시 파일을 만들어 PNG 를 쓰고, 권한을 0600 으로 바꾼 뒤 rename 합니다[2]. KDE 는 QSaveFile 로 써서 commit 합니다[5][10]. 폴더 권한은 700, 파일 권한은 600 이고, 원본을 읽을 수 없으면 프로그램은 캐시를 읽지도 쓰지도 않습니다[1].

원본의 mtime 이 `Thumb::MTime` 과 같지 않으면 썸네일을 다시 만듭니다[1]. KDE 는 여기에 더해 `Thumb::Size` 가 있는데 원본 크기와 다르거나 `Thumb::URI` 가 다르면 캐시를 쓰지 않습니다[6]. 다시 만든 썸네일은 같은 이름으로 덮으므로, 크기 폴더마다 URI 하나에 가장 최근 판의 썸네일 하나만 남습니다[1].

## 증거로서 의미

### 증명하는 것

- 이 계정의 썸네일 생성기가 `Thumb::URI` 경로에 있던 파일의 미리보기를 만든 적이 있다는 것.
- 그때 원본의 mtime 이 `Thumb::MTime` 값이었다는 것. KDE 가 만든 썸네일이면 그때의 원본 크기(`Thumb::Size`)까지 알 수 있습니다[5][10].
- 원본의 생김새. 원본을 지웠어도 축소 이미지가 남아 있으면 무엇이었는지 볼 수 있습니다.
- `fail/` 폴더에 항목이 있으면, 그 경로의 파일을 미리보기하려다 실패한 적이 있다는 것[1][2].

### 증명하지 못하는 것

- 사용자가 파일을 열었다는 것. 표준이 드는 쓰임새가 파일 대화 상자와 파일 관리자라서, 폴더를 살펴보기만 해도 썸네일이 생길 수 있습니다[1]. KDE 는 폴더 아이콘에 안에 든 파일 미리보기를 겹쳐 그릴 때 그 파일들의 썸네일도 캐시에 저장할 수 있습니다[5].
- 원본이 지금도 있다는 것, 또는 그 경로의 지금 파일이 썸네일을 만든 그 파일이라는 것. 같은 경로에 다른 파일을 두면 URI 가 같아집니다.
- 썸네일이 없으면 파일을 본 적이 없다는 것. 원본을 읽을 수 없었거나[1], 정리 작업이 지웠거나[3], 실패 기록만 남았을 수 있습니다[1].

## 시각 해석

| 시각 | 뜻 | 기준 |
|---|---|---|
| `Thumb::MTime` | 썸네일을 만들 때 원본 파일의 mtime[1][2][10] | 1970-01-01 UTC 부터의 초라서 UTC |
| 캐시 PNG 파일의 mtime·ctime | 썸네일을 만들거나 다시 만든 때. 임시 파일에 쓰고 rename 하기 때문입니다[1][2] | 파일 시스템 시각 |
| 캐시 PNG 파일의 atime | 썸네일을 마지막으로 읽은 때일 가능성이 있습니다. GNOME 정리 코드는 atime 을 마지막 사용 시각으로 씁니다[3] | 파일 시스템 시각, 마운트의 atime 옵션을 따름 |

`Thumb::MTime` 은 원본을 연 시각이나 썸네일을 만든 시각이 아닙니다. 원본을 열어 보기만 하고 고치지 않았다면 이 값은 바뀌지 않습니다. 반대로 캐시 PNG 의 mtime 은 미리보기를 만든 때라서, 두 값을 나란히 두면 "이 날짜에 수정된 원본을 이 시각에 미리보기로 만들었다" 까지 말할 수 있습니다. 초 단위 값을 날짜로 바꾸는 법은 [Linux 의 시각 값](../../01-foundations/value-decoding/time-values.md) 에서 다룹니다.

GNOME 정리 코드는 noatime 으로 마운트해도 만들 때 atime 과 mtime 이 같게 찍히고, 썸네일을 고쳐 쓰지 않고 새 파일로 바꿔 넣으므로 atime 이 mtime 보다 이르지 않다고 봅니다[3].

## 함정과 한계

- **GNOME 이 오래된 썸네일을 스스로 지웁니다.** gnome-settings-daemon 은 시작하고 2분 뒤에 한 번, 그 뒤로는 하루에 한 번 캐시를 청소합니다[3]. 파일 시각(atime, 없으면 mtime)이 `org.gnome.desktop.thumbnail-cache` 의 `maximum-age`(기본 180일)보다 오래된 파일을 지우고, 합계가 `maximum-size` 를 넘으면 오래된 것부터 지웁니다[3][4]. 두 값 모두 -1 이면 청소하지 않습니다[4]. 이 설정을 바꿨는지는 [GNOME 흔적](../desktop/gnome.md) 의 dconf 에서 봅니다.
- **`maximum-size` 기본값이 판마다 다릅니다.** gsettings-desktop-schemas 46.0 에서는 512(MB)이고, 2026-06-28 에 합친 커밋 이후로는 2048 입니다[4]. 분석 대상에 깔린 판은 [dpkg·apt 기록](../packages/dpkg-apt.md)·[rpm·dnf·yum 기록](../packages/rpm-dnf.md) 에서 확인합니다.
- **청소 대상은 이름이 36자이고 `.png` 로 끝나는 파일뿐입니다[3].** 쓰다 만 `.XXXXXX` 임시 파일이나 GNOME 이 아닌 프로그램의 `fail/` 하위 폴더는 청소 대상에서 빠집니다[2][3].
- **파일 이름으로 원래 경로를 거꾸로 찾지 않습니다.** 경로를 알면 URI 의 MD5 를 계산해 캐시 파일을 찾아갈 수 있지만, 한글·공백 같은 글자를 퍼센트 인코딩하는 방식이 구현마다 조금 다르면 해시가 달라질 가능성이 있습니다[2][5][10]. 캐시 파일이 무엇의 썸네일인지는 PNG 안의 `Thumb::URI` 로 확인합니다.
- **생성기 추정.** `Software=GNOME::ThumbnailFactory` 가 있으면 GNOME 이, `Software` 가 `KDE Thumbnail Generator` 로 시작하면 KDE 가 만든 것입니다[2][10]. `Software` 가 없고 `Thumb::Size` 가 있으면 KDE 가 폴더 아이콘용으로 만들었을 가능성이 있습니다[5].
- **외부 썸네일러를 끈 계정도 있습니다.** GNOME 은 `org.gnome.desktop.thumbnailers` 의 `disable-all`(기본 false)과 `disable`(MIME 형식 목록)로 외부 썸네일러를 끌 수 있고, 목록에 든 형식은 썸네일을 만들지 않습니다[4]. KDE 는 `PreviewSettings` 그룹의 `MaximumSize` 보다 큰 로컬 파일은 미리보기하지 않습니다[7].
- **수집 정의가 옛 위치만 봅니다.** ForensicArtifacts 의 `ThumbnailCacheFolder` 는 `%%users.homedir%%/.thumbnails/**3` 만 적고 `~/.cache/thumbnails` 는 적지 않습니다[9]. UAC 수집 목록에도 이 캐시를 모으는 항목이 없습니다[11]. 홈 폴더마다 두 위치를 직접 모읍니다.

## 직접 분석해 보기

### 헥스로 한 번

아래는 명세로 만든 예시입니다. 원본 `file:///home/user1/Pictures/sample.jpg` 의 썸네일이라면 파일 이름은 이 URI 의 MD5 인 `41211f6495ddec34017e9f484dc3acfb.png` 이고, PNG 안에 다음 두 청크가 들어갑니다.

```
00 00 00 31 74 45 58 74 54 68 75 6D 62 3A 3A 55   ...1tEXtThumb::U
52 49 00 66 69 6C 65 3A 2F 2F 2F 68 6F 6D 65 2F   RI.file:///home/
75 73 65 72 31 2F 50 69 63 74 75 72 65 73 2F 73   user1/Pictures/s
61 6D 70 6C 65 2E 6A 70 67 86 E1 EA DE            ample.jpg....

00 00 00 17 74 45 58 74 54 68 75 6D 62 3A 3A 4D   ....tEXtThumb::M
54 69 6D 65 00 31 37 31 38 30 30 30 30 30 30 EA   Time.1718000000.
31 25 D9                                          1%.
```

첫 청크는 길이 `00 00 00 31`(49바이트), 형식 `tEXt`, 키워드 `Thumb::URI`, 구분 바이트 `00`, URI 49−11=38바이트, CRC `86 E1 EA DE` 순서입니다[8]. 둘째 청크의 값 `1718000000` 은 원본 mtime 이고, UTC 로 2024-06-10 06:13:20 입니다. 두 청크 모두 텍스트가 평문이라, 캐시 폴더 전체를 `Thumb::URI` 문자열로 검색해도 URI 를 뽑을 수 있습니다. 지운 캐시 파일을 파일 시스템 빈 공간에서 찾을 때도 PNG 서명과 이 문자열을 함께 찾으면 됩니다. 지운 파일을 되살리는 조건은 [ext4](../../01-foundations/filesystem/ext4/index.md) 에서 다룹니다.

### 공개 도구로 한 번

plaso·dissect.target 에는 썸네일 캐시 전용 파서가 없어서, 텍스트 청크는 앞의 청크 구조대로 읽는 짧은 스크립트로 뽑습니다. 아래 출력은 만든 예시입니다.

```
$ python3 - ~/.cache/thumbnails/normal/41211f6495ddec34017e9f484dc3acfb.png <<'EOF'
import struct, sys
d = open(sys.argv[1], 'rb').read(); i = 8
while i + 8 <= len(d):
    n, t = struct.unpack('>I4s', d[i:i+8])
    if t == b'tEXt':
        k, v = d[i+8:i+8+n].split(b'\0', 1)
        print(k.decode('latin-1'), '=', v.decode('latin-1'))
    i += 12 + n
EOF
Thumb::URI = file:///home/user1/Pictures/sample.jpg
Thumb::MTime = 1718000000
Software = GNOME::ThumbnailFactory
$ printf '%s' 'file:///home/user1/Pictures/sample.jpg' | md5sum
41211f6495ddec34017e9f484dc3acfb  -
```

`strings` 로 살펴볼 수도 있지만, 키워드와 값 사이의 `00` 에서 줄이 끊기고 앞의 길이 바이트가 글자로 붙어 나올 수 있어 청크 단위로 읽는 편이 헷갈리지 않습니다. 거꾸로 경로를 알고 있을 때 `md5sum` 으로 캐시 파일 이름을 계산해 찾아갈 수 있지만, 앞의 함정처럼 인코딩이 다르면 맞지 않으니 찾은 파일의 `Thumb::URI` 로 다시 확인합니다. 결과를 다른 흔적과 시간순으로 합치는 법은 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 에서 다룹니다.

## 교차 검증

| 함께 볼 기록 | 확인할 것 |
|---|---|
| [최근 연 파일](../execution/recently-used.md) | 썸네일의 URI 를 실제로 열었다는 기록이 있는가 |
| [휴지통](trash.md) | 원본이 휴지통으로 옮겨졌는가, 옮긴 시각과 썸네일 시각의 앞뒤 |
| [마운트 기록](../devices/mounts.md) | URI 가 `/media/` 아래이면 그 시각에 어떤 이동식 매체가 붙어 있었는가 |
| [GNOME 흔적](../desktop/gnome.md)·[KDE 흔적](../desktop/kde.md) | 청소 설정을 바꿨는가, 같은 경로를 파일 관리자에서 보았는가 |
| [편집기 흔적](editor-artifacts.md) | 같은 경로의 파일을 편집기로 열었는가 |

## 실습

NIST CFReDS 같은 공개 시험 데이터 모음에서 Linux 데스크톱 이미지를 골라 풀어 봅니다.

1. 홈 폴더마다 `~/.cache/thumbnails` 와 `~/.thumbnails` 가 둘 다 있는가, 있다면 각각 몇 개의 PNG 가 있는가?
2. `Thumb::URI` 가 가리키는 원본 가운데 지금 디스크에 없는 것은 몇 개이고, 그 축소 이미지는 무엇을 보여 주는가?
3. 한 썸네일의 `Thumb::MTime` 과 캐시 PNG 파일의 mtime 사이는 얼마나 떨어져 있고, 그 차이를 어떻게 설명할 수 있는가?
4. `Software` 키로 보아 GNOME 과 KDE 가 만든 썸네일이 섞여 있는가?
5. `fail/` 폴더에 든 URI 는 어떤 형식의 파일이고, 같은 URI 의 정상 썸네일도 있는가?

## 참고 문헌

1. J. Finke, O. Sessink, Thumbnail Managing Standard 0.8.0 (2012-05). https://github.com/freedesktop-unofficial-mirror/xdg__xdg-specs/blob/master/thumbnail/thumbnail-spec.sgml
2. GNOME gnome-desktop, libgnome-desktop/gnome-desktop-thumbnail.c. https://github.com/GNOME/gnome-desktop/blob/master/libgnome-desktop/gnome-desktop-thumbnail.c , x-large·xx-large 추가 커밋 https://github.com/GNOME/gnome-desktop/commit/aa90b03ce5
3. GNOME gnome-settings-daemon, plugins/housekeeping/gsd-housekeeping-manager.c. https://github.com/GNOME/gnome-settings-daemon/blob/master/plugins/housekeeping/gsd-housekeeping-manager.c
4. GNOME gsettings-desktop-schemas, schemas/org.gnome.desktop.thumbnail-cache.gschema.xml.in·org.gnome.desktop.thumbnailers.gschema.xml.in. https://github.com/GNOME/gsettings-desktop-schemas/tree/master/schemas , 46.0 태그 https://github.com/GNOME/gsettings-desktop-schemas/blob/46.0/schemas/org.gnome.desktop.thumbnail-cache.gschema.xml.in , 기본 크기 변경 커밋 https://github.com/GNOME/gsettings-desktop-schemas/commit/98147ebf2a
5. KDE kio-extras, thumbnail/thumbnail.cpp. https://github.com/KDE/kio-extras/blob/master/thumbnail/thumbnail.cpp
6. KDE kio, src/gui/thumbnailcache_p.cpp. https://github.com/KDE/kio/blob/master/src/gui/thumbnailcache_p.cpp
7. KDE kio, src/gui/previewjob.cpp. https://github.com/KDE/kio/blob/master/src/gui/previewjob.cpp
8. W3C, Portable Network Graphics (PNG) Specification. https://github.com/w3c/png/blob/main/index.html
9. ForensicArtifacts, artifacts/data/linux.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/linux.yaml
10. KDE kio, src/gui/filepreviewjob.cpp. https://github.com/KDE/kio/blob/master/src/gui/filepreviewjob.cpp
11. UAC, artifacts 폴더. https://github.com/tclahr/uac/tree/main/artifacts
