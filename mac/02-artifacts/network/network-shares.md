---
title: "공유 폴더 연결 기록"
parent: "아티팩트 · 네트워크"
nav_order: 1690
---

# 공유 폴더 연결 기록 (SMB·AFP)

맥에서 파일 서버나 다른 컴퓨터의 공유 폴더에 붙으면 사용자별 최근·즐겨찾는 서버 목록에 서버 주소가 남고, SMB 클라이언트 설정 파일(`nsmb.conf`)과 시스템 네트워크 설정(`preferences.plist`)에는 어느 서버에 어떻게 붙으려 했는지, 이 맥이 공유 서버로서 어떤 이름을 썼는지가 남습니다.

## 무엇을 기록하나 · 왜 생기나

사용자는 보통 Finder 에서 "이동(Go) > 서버에 연결(Connect to Server)"을 고르고 "서버 주소(Server Address)" 칸에 주소를 넣어 공유 폴더에 붙습니다 [2]. 한 번 붙었던 서버는 Apple 메뉴의 "최근 항목(Recent Items)" 안 최근 서버 목록이나, 서버에 연결 창의 서버 주소 칸 오른쪽 팝업 메뉴에서 다시 열 수 있고, 서버에 연결 창에서 주소를 넣고 추가(+) 버튼을 누르면 그 주소가 즐겨찾는 서버 목록에 들어갑니다 [2]. 흔적은 이 두 목록에서 가장 먼저 찾고, 같은 네트워크에 있는 공유 컴퓨터는 Finder 사이드바 "위치(Locations)" 영역의 "네트워크(Network)"에 보입니다 [2].

서버 주소 칸에 넣는 주소는 프로토콜마다 모양이 다르고 [3], 목록에 남은 주소의 앞부분을 보면 어떤 방식으로 붙으려 했는지 알 수 있습니다.

| 프로토콜 | 주소 형식 | 비고 |
|---|---|---|
| SMB/CIFS | `smb://DNS이름/공유이름`, `smb://IP주소/공유이름` [3] | |
| NFS | `nfs://DNS이름/경로` [3] | |
| WebDAV | `http://DNS이름/경로` [3] | |
| FTP | — | Finder 에서는 읽기 전용이고, 서버로 파일을 복사하려면 다른 FTP 앱이 필요할 수 있음 [3] |

macOS 27 판 Mac 사용 설명서에는 AFP 가 나오지 않습니다 [2][3]. 그래도 옛 기록에는 `afp://` 주소가 남아 있을 수 있어서 목록을 읽을 때 함께 찾습니다. 타임 머신 네트워크 백업 대상으로 NAS 를 쓸 때도 SMB·AFP 가 오가는데, 이 부분은 [타임 머신 (Time Machine)](../filesystem/time-machine/index.md)에서 다룹니다.

목록과 따로, SMB 클라이언트는 `nsmb.conf` 라는 설정 파일을 읽어 서버·공유마다 인증 수준이나 서명·암호화 방식을 정합니다 [1]. 반대로 이 맥이 파일 공유 서버 노릇을 하면 시스템 네트워크 설정에 SMB 서버 이름과 작업 그룹이 남습니다 [4].

## 위치와 버전별 차이

| 기록 | 위치 | 알려 주는 것 |
|---|---|---|
| 최근 서버 | `~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.RecentServers.sfl2` | 최근에 붙은 서버 주소 |
| 즐겨찾는 서버 | 같은 폴더의 `com.apple.LSSharedFileList.FavoriteServers.sfl2` | 사용자가 즐겨찾기에 넣은 서버 주소 |
| 최근 호스트 | 같은 폴더의 `com.apple.LSSharedFileList.RecentHosts.sfl2` | 최근 호스트(북마크 없음) |
| 옛 사이드바 목록 (10.12 이하) | `~/Library/Preferences/com.apple.sidebarlists.plist` [5] | 즐겨찾는 서버, 사이드바에 나타난 볼륨 |
| 옛 최근 항목 (10.10 이하) | `com.apple.recentitems.plist` 의 `RecentServers` 키 | 최근 서버 |
| SMB 클라이언트 설정 (전체) | `/etc/nsmb.conf` [1] | 모든 사용자에게 적용하는 SMB 설정 |
| SMB 클라이언트 설정 (사용자) | `~/Library/Preferences/nsmb.conf` [1] | 그 사용자만 쓰는 SMB 설정 |
| 이 맥의 SMB 서버 이름 | `/Library/Preferences/SystemConfiguration/preferences.plist` 의 `SMB` 사전 [4] | `NetBIOSName`, `Workgroup` |
| 이전에 붙었던 볼륨 | `/private/var/db/volinfo.database` [5] | 이전에 연결된 볼륨의 파일 소유권 정보 |
| 사용자 키체인 | `~/Library/Keychains/*.keychain`, `~/Library/Keychains/*/keychain-2.db` [5] | 저장된 암호 항목 |

최근·즐겨찾는 서버 목록은 [최근 항목 (Shared File Lists)](../file-folder-usage/recent-items/index.md)과 같은 폴더, 같은 형식이고, 파일 확장자는 macOS 판에 따라 `.sfl`, `.sfl2`~`.sfl4` 로 바뀝니다. 그래서 경로는 확장자를 와일드카드로 잡아 찾습니다. 옛 버전의 저장 위치는 아래처럼 바뀌어 왔습니다.

| macOS 버전 | 서버 목록이 남는 곳 |
|---|---|
| 10.10 Yosemite 이하 | `com.apple.recentitems.plist` 의 `RecentServers`. 10.10 전에는 항목을 `Alias` 로, 그 뒤로는 `Bookmark` 로 적음 |
| 10.12 이하 | `com.apple.sidebarlists.plist` 의 `favoriteservers`(즐겨찾는 서버)와 `systemitems`(볼륨) |
| 10.15 Catalina 이후 | `com.apple.sharedfilelist/` 아래 `RecentServers`·`FavoriteServers`·`RecentHosts` 목록 파일. 이 목록 파일로 넘어온 정확한 버전은 실제 기기에서 확인 |

`volinfo.database` 는 이전에 연결된 볼륨의 파일 소유권 정보를 담는 파일입니다 [5]. 네트워크 공유도 여기 기록되는지는 실제 기기에서 확인해야 합니다. 서버 암호가 키체인에 저장되는지도 알려져 있지 않아서, 키체인은 교차 검증 대상으로 둡니다.

## 구조

### 최근·즐겨찾는 서버 목록

목록 파일 자체의 형식과 항목 순서는 [최근 항목 (Shared File Lists)](../file-folder-usage/recent-items/index.md)에서 다루고, 여기서는 서버 항목을 알아보는 법만 적습니다. 목록의 항목마다 북마크가 붙어 있고, 북마크의 URL 필드(0x1003)이 `file:///` 로 시작하지 않고 `smb://`, `afp://`, `ftp://` 같은 값이면 그 값이 서버 주소입니다. mac_apt 도 이 방식으로 서버 항목을 골라냅니다. 북마크 안에서 필드를 찾아가는 법은 [파일 참조 데이터 (Alias·Bookmark)](../../01-foundations/value-decoding/alias-bookmark.md)를 따릅니다. `RecentHosts` 목록에는 북마크가 없습니다.

10.12 이하의 `com.apple.sidebarlists.plist` 에서는 `favoriteservers` 아래 `CustomListItems` 배열에 항목마다 `Name` 과 `URL` 이 있고, `systemitems` 아래 `VolumesList` 배열에 `Name`, `EntryType`, `Alias`, `Visibility` 가 있습니다. 이 파일에는 데스크톱에 마운트되어 사이드바 목록에 나타난 볼륨 이름이 담깁니다 [5].

### SMB 클라이언트 설정 (nsmb.conf)

`nsmb.conf` 는 절(section) 단위 텍스트 파일입니다. `[default]` 절은 모든 연결에, `[SERVER]` 절은 그 서버에, `[SERVER:SHARE]` 절은 그 서버의 그 공유에 적용되고, 전체 설정(`/etc/nsmb.conf`)과 사용자 설정이 부딪히면 전체 설정이 이깁니다 [1]. 분석에 자주 쓰는 키는 아래와 같습니다 [1].

| 키 | 뜻 | 기본값 |
|---|---|---|
| `minauth` | 허용할 최소 인증 수준(kerberos, ntlmv2, ntlm, lm, none) | ntlmv2 |
| `signing_required` | 클라이언트 서명 켜기 | no |
| `signing_alg_map` | SMB 3.1.1 서명 알고리즘 비트맵 | 3 |
| `validate_neg_off` | validate negotiate 끄기 | no |
| `port445` | 포트 사용 방식(both, netbios_only, no_netbios) | both |
| `protocol_vers_map` | 켜 둘 SMB 버전 비트맵 | 7 |
| `addr` | 서버의 DNS 이름 또는 IP | — |
| `streams` | 서버가 지원하면 NTFS 스트림 사용 | yes |
| `soft` | 모든 마운트를 soft 로 | no |
| `notify_off` | 알림 끄기 | no |
| `dir_cache_max` / `dir_cache_min` | 디렉터리 캐시 시간 | 60초 / 30초 |
| `mc_on` | SMB 멀티채널 | yes |
| `encrypt_cipher_map` | SMB 3.1.1 암호화 알고리즘 비트맵 | 15 |
| `force_sess_encrypt` | 세션 암호화 강제 | no |

각 키가 어느 macOS 판부터 쓰였는지는 공개 자료가 없습니다.

### 이 맥이 SMB 서버일 때 (preferences.plist)

`/Library/Preferences/SystemConfiguration/preferences.plist` 안의 `SMB` 사전에 `NetBIOSName` 과 `Workgroup` 키가 있고, mac_apt NETWORKING 플러그인은 이 둘을 `Network_Details` 표의 `SMB.NetBIOSName`, `SMB.Workgroup` 열로 냅니다 [4]. 이 파일의 나머지 네트워크 서비스 설정은 [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md)에서 다룹니다. 어떤 폴더를 공유했는지 적는 공유 목록의 저장 위치와 AFP 서버 설정 파일은 실제 기기에서 확인해야 합니다.

## 증거로서 의미

**증명하는 것.** 최근 서버 목록에 주소가 남아 있으면 그 계정에서 그 주소로 서버에 연결한 기록이 있다고 쓸 수 있고, 즐겨찾는 서버 목록의 항목은 누군가 그 계정에서 주소를 즐겨찾기에 넣었다는 기록입니다. 주소 앞부분(`smb://`, `afp://`, `nfs://`, `ftp://`)으로 어떤 프로토콜을 골랐는지 알 수 있고, 주소 안의 DNS 이름이나 IP 로 상대 서버를 좁힐 수 있습니다. 목록이 사용자 홈 아래에 있어서, 어느 계정의 기록인지도 함께 드러납니다.

`nsmb.conf` 의 `[SERVER]` 절 이름이나 `addr` 값은 누군가 그 서버에 붙으려고 설정을 적어 둔 흔적으로 볼 수 있고, 서명·암호화를 끄거나 `minauth` 를 낮춘 설정은 연결 보안을 약하게 만든 흔적으로 볼 여지가 있습니다. 이 해석은 키의 뜻에서 끌어낸 판단이라서, 보고서에는 "이런 설정이 있다" 까지만 쓰고 의도는 다른 기록으로 뒷받침합니다. `preferences.plist` 의 `SMB` 값은 이 맥에 SMB 서버 이름과 작업 그룹이 설정되어 있다는 기록입니다.

**증명하지 못하는 것.** 이 목록들은 연결 시도가 인증까지 성공했는지, 공유 안에서 어떤 파일을 열거나 복사했는지 알려 주지 않습니다. 즐겨찾기 항목은 주소를 등록했다는 뜻일 뿐 그 서버에 실제로 붙었다는 뜻은 아니고, `nsmb.conf` 도 설정일 뿐 연결 기록이 아닙니다. `preferences.plist` 의 SMB 이름만으로는 파일 공유가 켜져 있었는지, 누가 이 맥에 붙었는지 알 수 없습니다. 자료 유출을 다룰 때는 "이 계정의 최근 서버 목록에 이 주소가 있다" 처럼 기록으로 확인되는 만큼만 쓰고, 파일 이동은 [자료를 밖으로 빼돌렸나 (Data Exfiltration)](../../04-scenarios/exfiltration/data-exfiltration/index.md)의 흐름대로 다른 기록으로 따로 보입니다.

## 시각 해석

서버 목록 항목, `nsmb.conf`, `preferences.plist` 의 `SMB` 사전에는 알려진 시각 필드가 없습니다. 그래서 언제 연결했는지는 목록 파일과 설정 파일의 파일 시스템 시각, [파일 시스템 이벤트 (FSEvents)](../filesystem/fsevents/index.md), 통합 로그 같은 다른 기록으로 좁힙니다. 파일 수정 시각은 목록이나 설정이 마지막으로 바뀐 때를 가리킬 수는 있지만 어느 항목이 그때 바뀌었는지는 알려 주지 않고, 가장 최근 항목과 수정 시각을 바로 짝지으면 틀릴 수 있습니다. 파일 시스템 시각의 기준은 [맥의 시각 값 (Mac Absolute Time·Unix·HFS)](../../01-foundations/value-decoding/mac-time-values.md)을 따르고, 여러 기록을 한 시간축에 놓는 법은 [타임라인 작성 (Timeline)](../../03-techniques/analysis/timeline/index.md)을 따릅니다. 공유를 마운트할 때 FSEvents 나 통합 로그에 어떤 모양으로 남는지는 실제 기기에서 확인해야 합니다.

## 함정과 한계

- 최근 서버 목록 파일의 확장자는 macOS 판마다 달라서 `.sfl2` 만 찾으면 다른 판의 파일을 놓칩니다.
- Apple 도움말 [2][3]에 AFP 가 없다고 해서 그 맥에서 AFP 를 쓴 적이 없다고 볼 수는 없고, 옛 목록 파일에는 `afp://` 주소가 남아 있을 수 있습니다.
- 사용자 `nsmb.conf` 만 보고 결론을 내리면, 같은 키를 다르게 적은 전체 설정 `/etc/nsmb.conf` 가 실제로 이긴 경우를 놓칩니다 [1].
- `volinfo.database` 에 네트워크 공유가 남는지, 서버 암호가 키체인에 어떤 항목으로 남는지는 공개 자료가 없으니, 거기에 없다고 해서 연결하지 않았다고 볼 수 없습니다.
- 사용자가 최근 항목을 지우거나 목록 파일을 지우면 현재 목록에서는 사라집니다. 이때는 스냅숏이나 타임 머신 백업에 예전 목록 파일이 남았는지, FSEvents 에 그 파일이 바뀐 기록이 있는지 확인하고, 방법은 [스냅숏과 백업 비교 (Snapshot·Time Machine Diff)](../../03-techniques/analysis/snapshot-diff.md)와 [증거를 없애려 했나 (Anti-Forensics)](../../04-scenarios/activity/anti-forensics/index.md)를 따릅니다.
- 지금 붙어 있는 공유를 라이브에서 볼 때의 수집 순서는 [라이브 대응 (Live Response)](../../03-techniques/process-acquisition/live-response/index.md)을 따릅니다.

## 직접 분석해 보기

원본을 바로 열지 말고 `com.apple.sharedfilelist/` 폴더 전체와 두 `nsmb.conf`, `preferences.plist` 를 작업 폴더에 복사한 뒤 사본으로 봅니다.

### 헥스로 한 번

목록 파일을 구조대로 풀기 전에 원시 바이트에서 서버 주소 문자열부터 찾아 두면 빠릅니다. 아래 바이트는 ASCII 표로 만든 예시이고, 실제 기기에서 나온 값이 아닙니다.

```
"smb://nas.example.com/" 을 ASCII 바이트로 적은 모양 (예시)
73 6d 62 3a 2f 2f 6e 61 73 2e 65 78 61 6d 70 6c 65 2e 63 6f 6d 2f
s  m  b  :  /  /  n  a  s  .  e  x  a  m  p  l  e  .  c  o  m  /

찾을 바이트 열
smb://  → 73 6d 62 3a 2f 2f
afp://  → 61 66 70 3a 2f 2f
nfs://  → 6e 66 73 3a 2f 2f
ftp://  → 66 74 70 3a 2f 2f
```

바이트 열이 나오면 그 둘레를 [파일 참조 데이터 (Alias·Bookmark)](../../01-foundations/value-decoding/alias-bookmark.md)의 순서대로 다시 읽어 URL 필드(0x1003)에 든 값인지 확인합니다. 북마크 안의 URL 문자열 인코딩은 공개 자료가 없으니, 바이트 열을 못 찾았다고 서버 항목이 없다고 단정하지 않고 구조대로 푼 결과와 맞춰 봅니다.

### 공개 도구로 한 번

`nsmb.conf` 는 텍스트 파일이라 아무 편집기로 열어 절 이름과 `addr`, 서명·암호화 관련 키를 봅니다. `preferences.plist` 는 [속성 목록 파일 (Property List)](../../01-foundations/data-formats/plist/index.md)에 나오는 plist 도구로 열어 `SMB` 사전을 보거나, mac_apt NETWORKING 플러그인을 돌려 `Network_Details` 표의 `SMB.NetBIOSName`, `SMB.Workgroup` 열을 봅니다 [4]. 서버 목록 파일은 최근 항목 페이지에 나오는 공개 도구로 풀어서, URL 이 `file:///` 가 아닌 항목만 추립니다.

## 교차 검증

- [최근 항목 (Shared File Lists)](../file-folder-usage/recent-items/index.md) — 서버 목록과 같은 폴더에 있는 최근 문서·앱 목록에서, 공유 안의 파일을 열었는지 봅니다.
- [파인더 설정과 기록 (Finder plist)](../file-folder-usage/finder-plist.md) — Finder 쪽에 남은 경로·볼륨 기록과 맞춰 봅니다.
- [저장된 암호 (Passwords·iCloud Keychain)](../credentials/saved-passwords.md), [키체인 (Keychain)](../../01-foundations/protection/keychain/index.md) — 서버 암호가 저장되어 있는지 확인합니다.
- [네트워크 인터페이스와 설정 (SystemConfiguration)](network-interfaces.md), [와이파이 기록 (Wi-Fi)](wifi.md) — 그 서버가 있을 만한 네트워크에 그때 붙어 있었는지 봅니다.
- [hosts와 DNS 설정 (hosts·DNS)](hosts-dns.md) — 서버 이름이 어디로 풀렸을지 봅니다.
- [통합 로그에서 찾을 것 (Unified Log Events)](../logs/unified-log-events/index.md) — 연결 무렵의 로그를 찾습니다.
- [원격 접속 (Remote Access)](remote-access/index.md) — 파일 공유와 함께 켜 둔 원격 접속 설정이 있는지 봅니다.

## 실습

NIST CFReDS 같은 공개 시험 데이터 가운데 파일 서버나 NAS 에 붙은 맥 이미지를 골라 아래 질문을 풀어 봅니다.

1. 사용자마다 `~/Library/Application Support/com.apple.sharedfilelist/` 아래 서버 목록 파일은 어떤 확장자로 남아 있고, 그 확장자는 그 이미지의 macOS 버전과 맞나요?
2. 최근 서버 목록과 즐겨찾는 서버 목록에서 URL 이 `file:///` 가 아닌 항목을 모두 뽑고 프로토콜별로 나눠 보세요. `afp://` 항목이 있나요?
3. 원시 바이트에서 `73 6d 62 3a 2f 2f` 를 찾은 결과와 구조대로 푼 결과가 같은가요?
4. `/etc/nsmb.conf` 와 사용자 `nsmb.conf` 가 둘 다 있다면, 같은 키를 다르게 적은 곳은 어디이고 실제로는 어느 값이 적용되나요?
5. `preferences.plist` 의 `SMB` 사전에 `NetBIOSName` 과 `Workgroup` 이 있나요? 있다면 [컴퓨터 이름과 하드웨어 정보 (Computer Name·Hardware)](../system-account/computer-name-hardware.md)의 이름과 같은가요?
6. 서버 목록 파일의 수정 시각 무렵에 FSEvents 와 와이파이 기록에는 무엇이 남아 있나요?

## 참고 문헌

1. nsmb.conf(5) man 페이지 (Xcode man pages 모음) — https://keith.github.io/xcode-man-pages/nsmb.conf.5.html
2. Apple 지원, Mac 사용 설명서 "Connect your Mac to shared computers and servers" — https://support.apple.com/guide/mac-help/connect-mac-shared-computers-servers-mchlp1140/mac
3. Apple 지원, Mac 사용 설명서 "Servers and shared computers you can connect to" — https://support.apple.com/guide/mac-help/servers-shared-computers-connect-mac-mchlp3015/mac
4. mac_apt `plugins/networking.py` (NETWORKING 1.0, Yogesh Khatri) — https://raw.githubusercontent.com/ydkhatri/mac_apt/master/plugins/networking.py
5. ForensicArtifacts `artifacts/data/macos.yaml` — https://raw.githubusercontent.com/ForensicArtifacts/artifacts/main/artifacts/data/macos.yaml
