# 泥地专属

> `zhengfang-jwgl-toolkit` 的地大配置，拿来改个参数就能跑。

## 基本信息

| 项 | 值 |
|---|-----|
| 门户地址 | `https://i.cug.edu.cn/web/` |
| 教务系统 | `https://jwgl.cug.edu.cn/jwglxt/` |
| CAS 服务器 | `sfrz.cug.edu.cn/tpass/login` |
| 系统版本 | 正方 V9.0 |
| 当前学期 | 2025-2026 第二学期（xnm=2025, xqm=12） |

## 怎么跑

### 1. 先看看 API

登录 `i.cug.edu.cn` 门户，OpenCLI 绑上标签页：

```bash
opencli browser cug bind
opencli browser cug open "http://jwgl.cug.edu.cn/jwglxt/"
```

然后调用 API 获取课表/成绩/考试数据：
```bash
# 课表
opencli browser cug eval '
fetch("https://jwgl.cug.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151", {
  method: "POST",
  headers: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
  body: "xnm=2025&xqm=12"
}).then(r => r.json()).then(d => JSON.stringify(d))
'
```

### 2. 同步课表

从课表 API 的 `kbList` 提取数据，按 `sample-config.py` 的格式填入 `COURSES`。

然后改 `../../scripts/sync-schedule.py` 里的这几个地方：
- `COURSES` — 你的课表
- `GOOGLE_TOKEN_PATH` — 你 Google OAuth token 的路径
- `SEMESTER_START` — `date(2026, 3, 2)`（下学期自己算一下）

```bash
export HTTPS_PROXY=http://127.0.0.1:7890
python scripts/sync-schedule.py
```

### 3. 考试提醒

考试 API 的 `items` 提取出来，填入 `../../scripts/exam-reminder.py` 的 `EXAMS` 列表。

## CUG 上课时间表

| 节次 | 时间 |
|------|------|
| 1-2 | 08:00-09:35 |
| 3-4 | 09:55-11:30 |
| 5-6 | 14:00-15:35 |
| 7-8 | 15:55-17:30 |
| 9-10 | 19:00-20:35 |
| 9-11 | 19:00-21:30 |

## 常见问题

**API 返回 HTML 而不是 JSON？**
session 过期了，半小时的事儿。重新导航一次 `http://jwgl.cug.edu.cn/jwglxt/`。

**门户里点教务管理 App 没反应？**
URL 直连 `http://jwgl.cug.edu.cn/jwglxt/`，别点那个 App 卡片。

**Google Calendar API 连不上？**
校园网直连 Google 会超时，需要代理：
```bash
export HTTPS_PROXY=http://127.0.0.1:7890
```

**学期起始日怎么算？**
课表 API 里找 `zcd` 含 "1周" 的课程，那周的周一就是。或者翻校历。
地大 2025-2026 第二学期：`date(2026, 3, 2)`
