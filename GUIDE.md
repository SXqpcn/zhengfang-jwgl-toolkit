# 我是怎么折腾正方教务系统的

地大教务系统，正方 v9.0，外面套了个 SPA 统一门户。查课表得先登门户 → 应用中心 → 教务管理 → 展开菜单 → 点课表查询……每次七八步，查个考试座位号也一样。

于是开始琢磨怎么绕过去。下面是我踩出来的路。

## 发现一：不需要处理登录

最大的误区是一上来就想逆向 CAS。其实根本不用。

正方用 CAS SSO。你在 Chrome 里正常登录一次门户，就有了个有效的 `JSESSIONID`。然后你**直接访问教务系统 URL**（`jwgl.cug.edu.cn/jwglxt/`），CAS 会自动从门户 session 上挂 ticket 传过去，教务系统就认了。

结论：浏览器不关、session 不过期，脚本里不用写密码。这是整个方案成立的前提。

## 发现二：后端 API 直接调

正方前端是 SPA，点左边菜单，右边 AJAX 加载内容。DOM 解析只能看到空壳。

但它请求的后端 API 非常规矩——

```
POST https://jwgl.xxx.edu.cn/jwglxt/{模块}/{动作}.html?gnmkdm={功能码}
Content-Type: application/x-www-form-urlencoded

xnm=2025&xqm=12
```

浏览器 session 有效时 `fetch` 自动带 cookie。我用 OpenCLI 绑定登录过的标签页，`eval` 一跑 fetch，JSON 就回来了。

我常用的三个：

- 课表 — `/kbcx/xskbcx_cxXsKb.html` (gnmkdm=N2151)
- 成绩 — `/cjcx/cjcx_cxDgXscj.html` (gnmkdm=N305005)
- 考试 — `/kwgl/kscx_cxXsksxxIndex.html` (gnmkdm=N358105)

> 字段太长了，放 `references/zhengfang-api-reference.md`。

## 学期参数这个坑

正方用 `xnm` + `xqm` 表示学期。`xnm` 是学年起始年份（比如 2025-2026 就是 2025），但 `xqm` 的映射很迷：

| 学期 | xqm | 
|------|-----|
| 第一学期 | 3 |
| 第二学期 | 12 |
| 暑假小学期 | 16 |

为什么第一学期是 3？我也不知道。一个个试出来的。

## 课表 → Google Calendar

最实用的一块。

**坑 1：事件太多。** 一学期 200+ 次课，全建单独事件日历直接爆炸。

→ 解法：RRULE 重复规则。把周次拆成连续区间，每个区间一条规则。比如 `[1-5周, 7-9周, 11-18周]` → 3 条 RRULE。整个学期 34 条搞定。

**坑 2：xqj 偏移。** API 返回 `xqj=1` 表示周一。算日期偏移用 `xqj-1`（周一=0）。我一开始直接用了 `xqj`，所有课往后错一天，周二变周三，排了一整周才发现人都傻了。

**坑 3：清理旧事件。** Google Calendar 删完不是立刻生效的，最终一致性。我的流程：`singleEvents=True` 扫出所有实例 → 拿 `recurringEventId`（master ID）→ 删 master → 等 3-5 秒 → 再扫确认没了 → 建新的。有时候得扫两三遍。

**坑 4：学期起始日。** 按校历推 2 月 23 号第一周，跑完最后一周课全丢了。查半天发现第一周周一应该是 3 月 2 号。差一周把全部周次往后推了。

**坑 5：Google API 要代理。** 校园网直连必超时。

脚本在 `scripts/sync-schedule.py`，`examples/cug/sample-config.py` 是地大配置。

## 考试倒计时

逻辑很简单：硬编码考试列表 → 跟今天比较 → 输出。为什么硬编码不每次调 API？考试安排一学期就变一次，没必要天天查。而且 API session 偶尔会过期。

脚本在 `scripts/exam-reminder.py`，改配置区的 `EXAMS` 列表就行。

## 踩坑清单

1. SPA 的 DOM 是空的 — 别想 parse 页面，直接 fetch API
2. session 半小时过期 — 重新导航一次教务系统 URL 就行，不用重新登录门户
3. Content-Type 得是 `application/x-www-form-urlencoded` — 不是 JSON，正方不吃
4. 门户里点 App 卡片经常不生效 — SPA 事件委托太复杂，URL 直连最稳
5. 学期起始日别拍脑袋 — 从课表 API 找最早那门课反推
6. 清 Google Calendar 用 `singleEvents=True` 查 — `False` 有时候返回 0 但实例还在

## 接别的学校

改三个东西就行：
- 门户地址和教务系统 URL
- `xnm`/`xqm`
- 课程时间表（如果你们学校作息不一样）

API 端点应该不变的，都是正方 v9.0。不确定就 F12 抓个包看看。
