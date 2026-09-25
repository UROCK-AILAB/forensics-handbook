---
title: "웹 서버가 뚫렸나"
parent: "시나리오 · 침해"
nav_order: 1040
---

# 웹 서버가 뚫렸나 (Web Server Compromise)

웹 요청이 서버에서 명령 실행이나 파일 업로드로 이어졌는지 가리는 조사입니다. 접근 로그에는 요청 본문이 남지 않으므로, 문서 루트의 파일 변화와 웹 서버 계정의 실행 흔적을 로그와 맞춰 봐야 답이 나옵니다.

## 조사 질문

이 조사가 답하려는 질문은 세 가지입니다. 웹 요청으로 서버에 파일이 올라가거나 명령이 실행됐는가, 웹 서버 계정으로 무엇이 실행됐는가, 그 일이 언제부터였는가입니다.

웹 서버 계정에서 root 로 올라갔는지는 [권한을 올렸나](privilege-escalation.md) 에서, 공격자가 남겨 둔 자동 실행 장치는 [무엇이 계속 살아남게 했나](persistence-hunt.md) 에서 이어서 다룹니다. 이 쪽은 로그와 파일의 형식을 다시 설명하지 않고, 무엇을 어떤 순서로 보고 어디서 흔히 잘못 읽는지를 다룹니다.

## 먼저 확인할 것

**시스템 기본 정보.** 배포판과 판([배포판과 버전](../../02-artifacts/system-info/os-release.md)), 시간대([호스트 이름·시간대·로캘](../../02-artifacts/system-info/hostname-timezone.md))를 먼저 정합니다. 웹 서버 오류 로그는 시간대 정보 없이 현지 시각만 적으므로, 시간대를 모르면 접근 로그와 오류 로그를 맞출 수 없습니다([웹 서버 로그](../../02-artifacts/servers/web-server-logs.md) 의 시각 해석).

**웹 서버 계정과 문서 루트.** 기준 배포판의 기본 설정은 다음과 같습니다.

| 항목 | Ubuntu 24.04 LTS | RHEL 9 |
|---|---|---|
| Apache 실행 계정 | `/etc/apache2/envvars` 의 `APACHE_RUN_USER=www-data`, `APACHE_RUN_GROUP=www-data`[1] | `httpd.conf` 의 `User apache`, `Group apache`[3] |
| Apache 문서 루트 | `000-default.conf` 의 `DocumentRoot /var/www/html`[1] | `DocumentRoot "/var/www/html"`, CGI 는 `ScriptAlias /cgi-bin/ "/var/www/cgi-bin/"`[3] |
| Nginx 실행 계정 | `nginx.conf` 의 `user www-data;`[2] | `nginx.conf` 의 `user nginx;`[4] |
| Nginx 문서 루트 | `sites-available/default` 의 `root /var/www/html;`[2] | `nginx.conf` 의 `root /usr/share/nginx/html;`[4] |

기본값은 출발점일 뿐이므로, 검체에서는 가상 호스트 설정(`sites-enabled`, `conf.d`)까지 읽어 실제 문서 루트와 로그 경로를 모두 적어 둡니다. 로그 파일 이름과 위치, RHEL httpd 의 `journald:` 대상처럼 로그가 파일이 아닌 곳으로 가는 설정은 [웹 서버 로그](../../02-artifacts/servers/web-server-logs.md) 에서 다룹니다. 웹 서버 계정의 UID 숫자는 배포판 기본값을 외워 쓰지 말고 검체의 `/etc/passwd` 로 확인합니다([UID·GID 와 사용자 이름 잇기](../../01-foundations/value-decoding/uid-gid.md)).

**기록이 켜져 있었는지.** 다음 기록은 켜 두어야만 생기므로, 없다는 사실을 "일이 없었다" 로 읽기 전에 설정부터 봅니다.

- 감사 데몬과 `execve` 규칙([감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md))
- 프로세스 회계 설치 여부([프로세스 회계](../../02-artifacts/execution/process-accounting.md))
- RHEL 의 SELinux 강제 모드 여부(검체의 설정과 감사 로그로 확인)
- 웹 서버 `LogLevel` 과 접근 로그 형식(`LogFormat`, `log_format`)

**수집 범위.** 로그와 설정 말고도 문서 루트 전체, `/tmp`·`/dev/shm`, 웹 애플리케이션 설정 파일(예: ForensicArtifacts 의 `WordpressConfigFile` 은 `/var/www/**/wp-config.php`, `/var/www/wp-config.php` 등을 잡습니다[13])을 함께 가져옵니다. 서버가 켜져 있다면 프로세스 목록과 부모 관계는 끄기 전에 떠 둡니다([라이브 응답 수집](../../03-techniques/acquisition/live-response.md)).

## 볼 아티팩트와 순서

| 순서 | 아티팩트 | 알려 주는 것 | 링크 |
|---|---|---|---|
| 1 | 웹 서버 설정(가상 호스트·로그 경로·문서 루트) | 어느 로그와 어느 폴더를 볼지 | [웹 서버 로그](../../02-artifacts/servers/web-server-logs.md) |
| 2 | 접근 로그 | 요청 주소·시각·상태 코드·User-Agent, 드문 경로에 반복된 POST | [웹 서버 로그](../../02-artifacts/servers/web-server-logs.md) |
| 3 | 오류 로그 | 스크립트 오류, CGI 가 stderr 로 쓴 내용 | [웹 서버 로그](../../02-artifacts/servers/web-server-logs.md) |
| 4 | 문서 루트의 파일 목록과 시각(디렉터리 mtime 포함) | 새로 생긴 스크립트 파일과 그 무렵 | [ext4](../../01-foundations/filesystem/ext4/index.md), [타임라인 만들기](../../03-techniques/analysis/timeline.md) |
| 5 | 패키지 검증 | 패키지가 깐 파일 가운데 내용이 바뀐 것 | [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md) |
| 6 | 감사 실행 기록·프로세스 회계·`/proc` | 웹 서버 계정으로 실행된 프로그램 | [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md), [프로세스 회계](../../02-artifacts/execution/process-accounting.md), [실행 중인 프로세스](../../02-artifacts/execution/proc.md) |
| 7 | `/tmp`·`/dev/shm` | 내려받은 도구와 임시 파일 | [임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md) |
| 8 | 지속성 장치(cron·systemd·authorized_keys) | 웹 서버 계정이나 root 로 심어 둔 것 | [무엇이 계속 살아남게 했나](persistence-hunt.md) |
| 9 | 데이터베이스 서버 로그 | 웹 애플리케이션의 DB 로 이어진 행위 | [데이터베이스 서버 로그](../../02-artifacts/servers/database-logs.md) |

### 로그가 보여 주는 범위

Apache 의 `%r` 는 요청 첫 줄이고[5], 기본 combined 형식에는 요청 본문 칸이 없습니다. 그래서 POST 로 보낸 명령이나 업로드한 파일 내용은 접근 로그에 남지 않고, 로그에서 얻는 것은 "어느 주소가 어느 경로로 POST 를 보냈고 서버가 무엇으로 답했는가" 까지입니다.

오류 로그는 이 빈자리를 조금 메웁니다. CGI 스크립트가 stderr 로 쓴 내용은 오류 로그에 그대로 복사되고, PHP 스크립트 같은 처리기도 오류 로그에 메시지를 보낼 수 있습니다[6]. 올라온 스크립트나 취약한 스크립트가 낸 오류 문구가 여기 남을 수 있으므로, 접근 로그에서 고른 시각 앞뒤의 오류 로그 줄을 함께 읽습니다. httpd 2.4 에서는 404 응답의 "File does not exist" 메시지가 info 수준으로 내려가 기본 `LogLevel warn` 에서는 오류 로그에 남지 않습니다[6]. 접근 로그와 오류 로그 형식 양쪽에 `%L` 을 넣어 둔 서버라면 로그 항목 ID 로 두 줄을 이을 수 있지만[6], 두 배포판의 기본 접근 로그 형식에는 `%L` 이 없습니다.

### 웹 서버 계정의 실행 흔적

감사 로그의 `auid` 는 로그인 때 정해지는 값이고, 정해지지 않은 프로세스는 `4294967295` 로 적힙니다(규칙에서는 `unset`, `-1` 과 같은 뜻)[7]. 서비스 관리자가 띄운 웹 서버와 그 자식 프로세스는 로그인 세션을 거치지 않으므로 `auid=4294967295` 로 적힐 가능성이 있고, 관리자가 셸에서 직접 띄웠다면 그 관리자의 로그인 UID 가 따라갑니다. 검체에서 웹 서버 프로세스 자체의 레코드를 먼저 찾아 기준값을 정한 뒤, 같은 `auid` 에 `uid` 가 웹 서버 계정이고 부모가 웹 서버나 PHP 처리 프로세스인 셸·다운로드 명령 실행을 찾습니다. 레코드의 필드와 부모 추적은 [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md) 과 [감사 로그 형식](../../01-foundations/logging/auditd-format.md) 에서 다룹니다.

RHEL 에서 SELinux 가 막은 접근은 감사 로그에 `AVC`(종류 번호 1400) 레코드로 남습니다[8]. 웹 서버 프로세스가 막히면 `comm="httpd"` 인 거부 레코드가 생깁니다[9]. 다음은 그 모양을 따른 만든 예시입니다.

```
type=AVC msg=audit(1773291909.551:4210): avc:  denied  { write } for  pid=3120 comm="httpd" path="/var/www/html/uploads" dev=sda2 ino=1048613
```

거부 레코드는 "시도했다가 막혔다" 는 기록이라 실행이 일어났다는 증거가 아니지만, 웹 서버 계정이 평소와 다른 파일이나 동작에 손댄 시각을 알려 줍니다. Ubuntu 쪽 AppArmor 거부에는 종류 번호 `AUDIT_APPARMOR_DENIED`(1503)가 정의돼 있습니다[8]. 웹 서버에 AppArmor 프로필이 걸려 있는지는 검체에서 확인합니다.

### 문서 루트의 파일 시각

디렉터리 안에 파일이 생기거나 지워지면 그 디렉터리의 mtime 이 바뀝니다[10]. 그래서 새 파일의 mtime 을 누가 되돌려 놓았더라도, 그 파일이 든 폴더의 mtime 과 파일의 ctime 은 따로 봐야 합니다. mtime 은 `utime` 으로 바꿀 수 있고, ctime 은 파일에 쓰거나 소유자·권한 같은 아이노드 정보를 바꿀 때 바뀝니다[10]. 생성 시각(btime)은 `statx` 로만 보이고 파일 시스템이 지원할 때만 있습니다[10]. 각 파일 시스템에서 시각을 읽는 법은 [ext4](../../01-foundations/filesystem/ext4/index.md) 를, 시각 조작 흔적은 [흔적을 지웠나](../insider/anti-forensics.md) 를 봅니다.

## 분석 흐름

1. **설정에서 범위를 정합니다.** 가상 호스트마다 문서 루트, 접근·오류 로그 경로, 로그 형식을 표로 적습니다. 회전본까지 포함해 로그가 덮는 기간을 정하고, 기간 밖의 일은 로그로 답할 수 없다고 적어 둡니다.
2. **파일 쪽에서 출발합니다.** 문서 루트의 스크립트 파일을 mtime·ctime·(있으면) btime 과 소유자로 정렬하고, 웹 서버 계정이 소유한 파일이나 설치 때와 시각이 동떨어진 파일을 고릅니다. 패키지가 깐 파일이라면 `rpm -V`(`--verify`)나 `dpkg -V`(`--verify`)로 설치 뒤에 바뀌었는지 봅니다[11][12]. 고른 파일은 [알려진 파일 대조와 YARA](../../03-techniques/analysis/hash-yara.md) 로 알려진 웹셸인지 대조합니다.
3. **고른 파일 이름으로 접근 로그를 찾습니다.** 그 파일을 처음 요청한 주소와 시각을 찾고, 그 직전에 같은 주소가 보낸 업로드 후보 요청(드문 경로로 간 POST)을 봅니다.
4. **같은 주소의 요청을 시간순으로 모두 놓습니다.** 스캔으로 보이는 요청, 업로드 후보, 올라온 파일에 대한 반복 요청이 어떤 순서로 이어지는지 보고, 오류 로그의 같은 시각 줄을 UTC 로 바꿔 붙입니다.
5. **웹 서버 계정의 실행을 찾습니다.** 감사 실행 기록, 프로세스 회계의 명령 이름, 서버가 켜져 있으면 `/proc` 의 부모 관계로 웹 서버 계정이 띄운 셸·다운로드 도구를 찾습니다. 같은 무렵 `/tmp`·`/dev/shm` 에 생긴 파일도 봅니다.
6. **다음 단계로 넘깁니다.** 웹 서버 계정에서 root 로 올라간 흔적은 [권한을 올렸나](privilege-escalation.md), 남겨 둔 자동 실행 장치는 [무엇이 계속 살아남게 했나](persistence-hunt.md), 같은 주소에서 SSH 로도 들어왔는지는 [SSH 로 들어왔나](ssh-intrusion.md) 로 이어 갑니다. 모든 결과는 [타임라인 만들기](../../03-techniques/analysis/timeline.md) 로 한 줄에 놓습니다.

파일에서 출발하면 로그가 회전으로 지워졌거나 다른 곳에 있어도 조사를 시작할 수 있습니다. DFRWS 발표에 실린 HDFS 클러스터 침해 사례에서는 `/etc` 에서 낯선 cluster 서비스를 찾고, 그 php 파일(cluster.php)이 최근에 생긴 것임을 아이노드 정보(istat)로 확인한 뒤 내용(icat)을 꺼내 보니 systemd 서비스로 돌던 PHP 웹셸이었습니다(오류 출력을 끄고, 17001 포트를 열고, `shell_exec()` 를 쓰는 코드)[15]. 이 사례의 침입 경로는 웹이 아니라 약한 비밀번호를 무차별 대입으로 뚫은 것이었고, 웹셸 서비스는 root 를 얻은 뒤에 설치됐습니다[15]. 한 사례이지만, 문서 루트 밖에도 스크립트 파일이 있을 수 있고 웹셸이 서비스로 등록돼 있을 수 있다는 점을 보여 줍니다.

## 흔한 오판

- **"상태 200 이니 공격이 성공했다."** 접근 로그에는 요청 첫 줄·상태 코드·보낸 크기 같은 값만 있고 응답 내용이나 결과는 없습니다. 오류를 알리는 페이지도 200 으로 답할 수 있으므로, 성공 여부는 파일 변화나 뒤이은 실행 기록으로 확인합니다.
- **"로그에 POST 가 없으니 업로드도 없었다."** 가상 호스트마다 로그 파일이 다를 수 있고, Ubuntu 의 `other_vhosts_access.log`, RHEL httpd 의 `journald:` 대상, Nginx 의 `if=` 조건이나 `buffer=` 설정 때문에 줄이 다른 곳에 있거나 빠질 수 있습니다([웹 서버 로그](../../02-artifacts/servers/web-server-logs.md)). 회전으로 지워진 기간도 있습니다.
- **"오류 로그에 404 가 없으니 스캔이 없었다."** httpd 2.4 의 기본 `LogLevel warn` 에서는 404 의 "File does not exist" 가 남지 않습니다[6]. 스캔은 접근 로그의 상태 코드로 봅니다.
- **접근 로그와 오류 로그의 시각을 그대로 비교합니다.** 접근 로그는 시간대 차이를 함께 적고 오류 로그는 현지 시각만 적습니다. Apache 접근 로그의 `%t` 는 요청을 받은 때이고[5], Nginx 의 `$time_local` 은 로그를 쓸 때 캐시해 둔 시각을 옮겨 적습니다[16]. 둘을 맞출 때는 시간대와 이 기준점 차이를 먼저 맞춥니다([웹 서버 로그](../../02-artifacts/servers/web-server-logs.md)).
- **웹셸 파일의 mtime 을 올라온 시각으로 씁니다.** mtime 은 되돌릴 수 있습니다[10]. 폴더의 mtime, 파일의 ctime, 접근 로그에 처음 나온 요청을 함께 보고, 셋이 어긋나면 그 차이를 보고서에 적습니다.
- **`auid=4294967295` 인 실행을 모두 무시합니다.** 웹 서버처럼 로그인 세션 밖에서 도는 서비스가 낳은 실행은 오히려 이 값으로 남을 가능성이 있습니다. 걸러 낼 때는 `auid` 만 보지 말고 `uid` 와 부모 프로세스를 함께 봅니다.
- **원격 주소를 공격자 한 사람으로 봅니다.** 프록시·로드 밸런서 뒤라면 로그의 주소는 중간 장비의 주소이고, `X-Forwarded-For` 와 User-Agent 는 클라이언트가 보낸 값이라 꾸밀 수 있습니다([웹 서버 로그](../../02-artifacts/servers/web-server-logs.md)).

## 보고서 문장 예

기록이 말하는 만큼만 씁니다. 다음은 만든 예시이고, 주소·시각·파일 이름은 모두 지어낸 값입니다.

- "2026-03-12 05:04:58 UTC 에 203.0.113.10 에서 `/uploads/` 경로로 보낸 POST 요청에 서버가 200 으로 답한 기록이 접근 로그에 있다. 요청 본문은 기록되지 않았다."
- "`/var/www/html/uploads/x.php` 는 웹 서버 계정 소유이고, 이 파일이 든 폴더의 mtime 은 2026-03-12 05:04:58 UTC 로 위 요청 시각과 같다. 파일 자체의 mtime 은 2025-11-02 로 폴더 시각보다 이르다."
- "같은 날 05:06:12 UTC 부터 `x.php` 에 대한 GET 요청이 14회 기록돼 있고, 같은 구간에 웹 서버 계정(uid 는 /etc/passwd 기준 www-data)으로 `/usr/bin/curl` 을 실행한 감사 레코드가 있다."

"공격자가 웹셸을 올려 명령을 실행했다" 처럼 기록을 넘어서는 문장은 쓰지 않고, 위와 같은 사실을 나열한 뒤 "이 기록들은 업로드된 스크립트를 통해 명령이 실행됐을 가능성과 들어맞는다" 처럼 판단을 따로 적습니다. 보고서 틀은 [Linux 포렌식 보고서](../../03-techniques/reporting/forensic-report.md) 를 봅니다.

## 함께 볼 페이지

- [웹 서버 로그 (Apache·Nginx)](../../02-artifacts/servers/web-server-logs.md) — 로그 위치·형식·시각 해석·공개 도구
- [데이터베이스 서버 로그](../../02-artifacts/servers/database-logs.md) — 웹 애플리케이션 뒤의 DB 접속·쿼리
- [감사 로그의 실행 기록](../../02-artifacts/execution/auditd-execve.md), [프로세스 회계](../../02-artifacts/execution/process-accounting.md), [실행 중인 프로세스](../../02-artifacts/execution/proc.md) — 웹 서버 계정의 실행
- [임시 폴더와 메모리 파일 시스템](../../02-artifacts/file-activity/tmp-shm.md) — 내려받은 도구가 놓이는 곳
- [패키지 파일 변조 확인](../../02-artifacts/packages/package-verify.md) — 바뀐 시스템 파일 가르기
- [로그 분석](../../03-techniques/analysis/log-analysis.md), [타임라인 만들기](../../03-techniques/analysis/timeline.md), [지운 파일 되살리기](../../03-techniques/analysis/file-recovery.md)
- [SSH 로 들어왔나](ssh-intrusion.md), [권한을 올렸나](privilege-escalation.md), [채굴기가 돌았나](cryptominer.md), [무엇이 계속 살아남게 했나](persistence-hunt.md)
- [흔적을 지웠나](../insider/anti-forensics.md) — 로그를 고치거나 지운 흔적

공개 도구로는 dissect.target 의 `webserver.logs`, `apache.access`, `nginx.access`, `apache.hosts`, `nginx.hosts`, plaso 의 `apache_access` 가 로그와 가상 호스트를 읽고(자세한 내용은 [웹 서버 로그](../../02-artifacts/servers/web-server-logs.md)), UAC 는 사용자 홈 아래 `.php_history` 파일을 함께 모읍니다[14].

## 참고 문헌

1. Ubuntu apache2 패키지(noble), debian/config-dir/envvars, debian/config-dir/sites-available/000-default.conf. https://git.launchpad.net/ubuntu/+source/apache2/tree/debian?h=ubuntu/noble
2. Ubuntu nginx 패키지(noble), debian/conf/nginx.conf, debian/conf/sites-available/default. https://git.launchpad.net/ubuntu/+source/nginx/tree/debian?h=ubuntu/noble
3. CentOS Stream 9 httpd 패키지, httpd.conf. https://gitlab.com/redhat/centos-stream/rpms/httpd/-/tree/c9s
4. CentOS Stream 9 nginx 패키지, nginx.conf. https://gitlab.com/redhat/centos-stream/rpms/nginx/-/tree/c9s
5. Apache HTTP Server 2.4, docs/manual/mod/mod_log_config.xml. https://github.com/apache/httpd/blob/2.4.x/docs/manual/mod/mod_log_config.xml
6. Apache HTTP Server 2.4, docs/manual/logs.xml. https://github.com/apache/httpd/blob/2.4.x/docs/manual/logs.xml
7. linux-audit audit-userspace, docs/audit.rules.7. https://github.com/linux-audit/audit-userspace/blob/master/docs/audit.rules.7
8. linux-audit audit-documentation, specs/messages/message-dictionary.csv. https://github.com/linux-audit/audit-documentation/tree/main/specs
9. plaso, plaso/parsers/text_plugins/selinux.py. https://github.com/log2timeline/plaso/blob/main/plaso/parsers/text_plugins/selinux.py
10. Linux man-pages, man7/inode.7. https://github.com/mkerrisk/man-pages/blob/master/man7/inode.7
11. RPM, docs/man/rpm.8.scd. https://github.com/rpm-software-management/rpm/blob/master/docs/man/rpm.8.scd
12. dpkg, man/dpkg.pod. https://github.com/guillemj/dpkg/blob/main/man/dpkg.pod
13. ForensicArtifacts, artifacts/data/webservers.yaml. https://github.com/ForensicArtifacts/artifacts/blob/main/artifacts/data/webservers.yaml
14. UAC, artifacts/files/applications/php.yaml. https://github.com/tclahr/uac/blob/main/artifacts/files/applications/php.yaml
15. Ali Hadi, Mariam Khader, Thomas Claflin, "Learning Linux Forensic Analysis and Why it Matters", DFRWS 발표 자료. https://dfrws.org/presentation/learning-linux-forensic-analysis-and-why-it-matters/
16. nginx, src/http/modules/ngx_http_log_module.c(`ngx_http_log_time`). https://github.com/nginx/nginx/blob/master/src/http/modules/ngx_http_log_module.c
