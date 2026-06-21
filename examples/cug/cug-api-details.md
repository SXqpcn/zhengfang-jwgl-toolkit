# CUG 正方教务系统 API 详情

> 通用的 API 参考见 [`../../references/zhengfang-api-reference.md`](../../references/zhengfang-api-reference.md)，本文档补充 CUG 特定的端点和参数细节。

## 端点汇总

基础 URL: `https://jwgl.cug.edu.cn/jwglxt`

| 功能 | 完整 URL | gnmkdm |
|------|----------|--------|
| 课表 | `/kbcx/xskbcx_cxXsKb.html` | N2151 |
| 成绩 | `/cjcx/cjcx_cxDgXscj.html` | N305005 |
| 考试 | `/kwgl/kscx_cxXsksxxIndex.html` | N358105 |

## 请求参数

```
POST body (form-encoded):
xnm=2025&xqm=12&queryModel.showCount=100
```

## 响应字段补充

### 课表 kbList 的 CUG 特有字段

| 字段 | 含义 | 示例 |
|------|------|------|
| cdbh | 教室编号 | JS5816 |
| cdlbmc | 教室类型 | 多功能教室 |
| xqz | 开始周 | 1 |
| zzz | 结束周 | 18 |
| kclb | 课程类别 | 学科基础课 |

### 提交成绩查询需要的额外字段

POST body 中可能需要附加 `queryModel.sortOrder=asc`

## 认证流

```
浏览器 → https://i.cug.edu.cn/web/?CASLOGIN=CASLOGIN
       → CAS: sfrz.cug.edu.cn/tpass/login
       → 门户仪表盘 (hash routing: #/home)
       → 直接导航 http://jwgl.cug.edu.cn/jwglxt/
       → 302 → https://jwgl.cug.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=xs
```

不需要直接调用 CAS。在已登录门户的浏览器标签页中，直接导航到教务系统 URL，CAS ticket 自动完成认证。

## Session 维持

`JSESSIONID` 是 HTTP-only cookie，JavaScript 无法读取，但浏览器上下文中的 `fetch` 会自动携带。session 生命周期约 30 分钟。

## 网络环境

CUG 校内访问需要代理才能连接 Google API。建议使用 Clash Verge 等本地代理工具。
