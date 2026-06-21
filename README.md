# 正方教务系统自动化工具集

[![Stars](https://img.shields.io/github/stars/SXqpcn/zhengfang-jwgl-toolkit?style=flat)](https://github.com/SXqpcn/zhengfang-jwgl-toolkit/stargazers)
[![License](https://img.shields.io/github/license/SXqpcn/zhengfang-jwgl-toolkit?style=flat)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/SXqpcn/zhengfang-jwgl-toolkit?style=flat)](https://github.com/SXqpcn/zhengfang-jwgl-toolkit/commits/master)

> 每天早上打开手机就能看到今天在哪上课，考试前自动提醒，再也不用点开信息门户。
>
> 折腾了一小时，把正方教务系统接进了自己的自动化工作流。整理出来给舍友校友们抄作业。

## 怎么回事

泥地用的是正方 v9.0，外面套了个 SPA 统一门户。其实就一句话：**你浏览器里登录过门户之后，直接调教务系统的后端 API 就行，session cookie 会自动带过去。不用处理密码，不用逆向 CAS。**

基于这个，做了几件事：

- 不用每次打开门户点七八下才能看到课表
- 课表自动同步到谷歌日历，换教室跟着变
- 一键同步考试信息，不用总是翻门户的页面
- API 文档整理（课表/成绩/考试三个接口的字段全标好了）

## 怎么搞

依赖一个工具：[OpenCLI](https://github.com/jackwener/OpenCLI)（感谢 [@jackwener](https://github.com/jackwener)），它能在命令行里控制你已登录的 Chrome 标签页。正是靠它绕过登录这关。

### 1. 装 OpenCLI

```bash
npm install -g opencli
```

装好之后确认 Chrome 已经在跑，然后：

```bash
opencli doctor    # 检查环境是否就绪
```

### 2. 登录门户，绑定浏览器

用 Chrome 正常登入你们学校的统一门户（别关标签页）。然后：

```bash
opencli browser jwc bind   # 绑定当前活跃的 Chrome 标签页
```

> 如果你的教务系统地址不是 `jwgl.xxx.edu.cn`，把上面的 `jwc` 换成任意你喜欢的名字就行。

### 3. 调 API 拿数据

```bash
# 先导航到教务系统（CAS ticket 自动传递，不用重新登录）
opencli browser jwc open "http://jwgl.cug.edu.cn/jwglxt/"

# 等 5 秒让页面加载完
# 然后直接 fetch 后端 API：
opencli browser jwc eval '
fetch("https://jwgl.cug.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N2151", {
  method: "POST",
  headers: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
  body: "xnm=2025&xqm=12"
}).then(r => r.json()).then(d => JSON.stringify(d, null, 2))
'
```

返回的就是你的课表 JSON。成绩和考试同理，换个 endpoint 就行（见 [API 参考](references/zhengfang-api-reference.md)）。

### 4. 跑脚本

拿到课表数据后，填进 `scripts/sync-schedule.py` 的配置区：

```bash
# 课表同步到 Google Calendar（需要开代理）
export HTTPS_PROXY=http://127.0.0.1:7890
python scripts/sync-schedule.py

# 考试倒计时
python scripts/exam-reminder.py
```

CUG 直接看 `examples/cug/`，地址参数我都踩好了，改个配置就能跑。

## 目录

内容很简单：

- **scripts/sync-schedule.py** — 课表接入 Google Calendar，34 条 RRULE 搞定一学期
- **scripts/exam-reminder.py** — 考试倒计时，改 `EXAMS` 列表就能用
- **references/** — API 字段速查表，懒得翻代码的时候看
- **examples/cug/** — 泥地专属配置，校友直接抄
- **[GUIDE.md](GUIDE.md)** — 详细的踩坑记录和认证逻辑分析

## 哪些学校能用

中国地质大学(武汉) 2025-2026 第二学期跑通了。理论上任何正方 v9.0 的高校都行——只要教务系统 URL 是 `jwgl.xxx.edu.cn/jwglxt/` 这个路径的。

不确定的话开 F12 抓个请求看一眼，结构一样就能用。欢迎提 Issue 或 PR 补上你们学校的细节。

## 致谢

- [OpenCLI](https://github.com/jackwener/OpenCLI) — 让命令行能控制浏览器，是整个方案的关键一环

## 注意

- 脚本里不放密码，靠浏览器已有登录 session
- Google API 要走代理
- MIT，随便改随便用
