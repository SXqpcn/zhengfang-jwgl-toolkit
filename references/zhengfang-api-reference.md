# 正方教务系统 API 通用参考

## 认证流（CAS SSO）

1. 访问门户 `https://i.<university>.edu.cn/web/` → CAS 登录
2. CAS server: `sfrz.<university>.edu.cn/tpass/login`（密码 RSA 加密，`strEnc`）
3. 认证后重定向到门户仪表盘
4. 在门户中点击 **应用中心 → 教学管理 → 教务管理**
5. 门户跳转 `http://jwgl.<university>.edu.cn/jwglxt/`，CAS ticket 自动传递
6. 系统重定向到 `https://jwgl.<university>.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=xs`

HTTP-only `JSESSIONID` cookie 维持 session。浏览器上下文里的 `fetch` 会自动带过去。

## API 端点

基础 URL: `https://jwgl.<university>.edu.cn/jwglxt`

| 功能 | 路径 | gnmkdm | 请求方式 |
|------|------|--------|---------|
| 课表查询 | `/kbcx/xskbcx_cxXsKb.html` | N2151 | POST form-encoded |
| 成绩查询 | `/cjcx/cjcx_cxDgXscj.html` | N305005 | POST form-encoded |
| 成绩明细 | `/cjcx/cjcx_cxCjxq.html` | N305005 | POST form-encoded |
| 考试信息 | `/kwgl/kscx_cxXsksxxIndex.html` | N358105 | POST form-encoded |

## 学期参数

| 语义 | xqm 值 |
|------|--------|
| 第一学期 | `3` |
| 第二学期 | `12` |
| 第三学期(暑假小学期) | `16` |

`xnm` = 学年起始年份。如 2025-2026 学年 → `xnm=2025`

## 课表 API 详解

**请求体:** `xnm=2025&xqm=12`

**响应结构:**
- `xsxx` — 学生信息 (XM, XH, BJMC, ZYMC, XNMC)
- `kbList[]` — 课程列表
- `sjkList[]` — 实践课列表
- `xqjmcMap` — 星期映射

**kbList 字段说明:**

| 字段 | 含义 | 示例 |
|------|------|------|
| kcmc | 课程名称 | 高等数学A2 |
| xm | 教师 | 刘某某 |
| cdmc | 上课地点 | 东教楼C0304 |
| jcs | 节次 | 3-4 |
| xqj | 星期几(数字) | 1=周一 |
| xqjmc | 星期几(中文) | 星期一 |
| zcd | 周次 | 1-5周,7-9周,11-18周 |
| jxbmc | 教学班名称 | 高等数学A2-0010 |
| xf | 学分 | 6.5 |
| kch | 课程代码 | 21212721 |
| jcor | 节次(备用) | 3-4 |
| khfsmc | 考核方式 | 考试 |
| skfsmc | 授课方式 | 面授讲课 |
| kcxz | 课程性质 | 必修 |
| zxs | 总学时 | 104 |

## 考试 API 详解

**请求体:** `xnm=2025&xqm=12&queryModel.showCount=50`

**items[] 字段:**

| 字段 | 含义 | 示例 |
|------|------|------|
| kcmc | 课程名称 | 大学英语2 |
| kssj | 考试时间 | 2026-06-25(19:30-21:30) |
| cdmc | 考试地点 | 北综楼406 |
| zwh | 座位号 | 8 |
| cdxqmc | 校区 | 南望山校区 |
| xymc | 学院 | 计算机学院 |
| xh | 学号 | 2025xxxxxxxx |
| xm | 姓名 | *** |

## 成绩 API 详解

**请求体:** `xnm=2025&xqm=12&queryModel.showCount=100&queryModel.sortOrder=asc`

**items[] 字段:**

| 字段 | 含义 |
|------|------|
| kcmc | 课程名称 |
| cj | 成绩 |
| xf | 学分 |
| jd | 绩点 |
| kcxzmc | 课程性质 |
| jsxm | 教师姓名 |
| xh | 学号 |
| bj | 班级 |
| kcbj | 课程标记(主修/辅修) |

## 周次解析

`zcd` 字段格式示例: `"1-5周,7-9周,11-18周"` 或 `"9-11周(单),12-17周"`

规则:
- `(单)` = 仅奇数周
- `(双)` = 仅偶数周
- 逗号分隔多个区间

## 菜单结构

正方 v9.0 主菜单分组（通过 `button` 元素渲染）:

- **报名申请**: 重修报名, 考级报名, 学分认定
- **信息维护**: 个人信息, 实习资料
- **选课**: 推荐选课, 自主选课, 教材预订
- **信息查询**: 成绩, 课表, 考试, 空闲教室
- **教学评价**: 学生评价, 过程评价

## 课程时间表（通用）

| 节次 | 典型时间 | 备注 |
|------|----------|------|
| 1-2 | 08:00-09:35 | 各校可能有 ±15min 差异 |
| 3-4 | 09:55-11:30 | |
| 5-6 | 14:00-15:35 | |
| 7-8 | 15:55-17:30 | |
| 9-10 | 19:00-20:35 | |
| 9-11 | 19:00-21:30 | |

> 不同学校作息不一样，以你学校的铃声为准改 `TIMESLOT`。
