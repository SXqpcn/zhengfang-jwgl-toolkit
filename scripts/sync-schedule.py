#!/usr/bin/env python3
"""
课表 → Google Calendar 同步（RRULE 重复规则）。

一次运行 = 清旧建新，避免重复事件。

用法:
    1. 修改下方 CONFIG 区域的配置
    2. 确保 GOOGLE_TOKEN_PATH 指向有效的 OAuth token JSON
    3. 运行: python sync-schedule.py

前置条件:
    pip install google-api-python-client google-auth-oauthlib
    需要代理访问 Google API（国内网络）: export HTTPS_PROXY=http://127.0.0.1:7890
"""
import json, os
from datetime import date, timedelta

# ============================================================
# 🔧 配置区 —— 修改为你自己的数据
# ============================================================

# 学期第1周周一日期
SEMESTER_START = date(2026, 3, 2)  # TODO: 改为你的学期起始日

# Google OAuth token 路径
GOOGLE_TOKEN_PATH = r"C:\Users\xxx\AppData\Local\hermes\google_token.json"  # TODO: 改为你的路径

# 代理设置（国内网络访问 Google API 需要）
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

# 上课时间表（可自定义，匹配你学校的铃声）
TIMESLOT = {
    "1-2":  ("08:00", "09:35"),
    "3-4":  ("09:55", "11:30"),
    "5-6":  ("14:00", "15:35"),
    "7-8":  ("15:55", "17:30"),
    "9-10": ("19:00", "20:35"),
    "9-11": ("19:00", "21:30"),
}

# 星期 → RRULE 映射
WEEKDAY_MAP = {1: 'MO', 2: 'TU', 3: 'WE', 4: 'TH', 5: 'FR', 6: 'SA', 7: 'SU'}

# 颜色映射（Google Calendar colorId 1-11）
COLOR_MAP = {
    '高等数学': '5',
    '大学物理': '9',
    '大学英语': '1',
    # TODO: 添加你需要的颜色映射
}

# ============================================================
# 课表数据
# 格式: {"kcmc": "课程名", "xm": "教师", "cdmc": "教室",
#         "jcs": "节次", "xqj": 星期(1-7),
#         "weeks": [[起始周, 结束周], ...]}
# ============================================================
COURSES = [
    # TODO: 从正方 API 获取后填入这里
    # 示例:
    # {"kcmc": "高等数学A2", "xm": "刘老师", "cdmc": "东教楼C0304",
    #  "jcs": "3-4", "xqj": 1, "weeks": [[1, 5], [7, 9], [11, 18]]},
]

# ============================================================
# 以下为执行逻辑，通常不需要修改
# ============================================================

COURSE_NAMES = list(set(c['kcmc'] for c in COURSES)) if COURSES else []


def build_rrule(week_start, week_end, weekday, parity=None):
    end_date = SEMESTER_START + timedelta(weeks=week_end - 1) + timedelta(days=6)
    until_str = end_date.strftime('%Y%m%dT235959Z')
    if parity == 'odd':
        count = (week_end - week_start) // 2 + 1
        return f"FREQ=WEEKLY;INTERVAL=2;BYDAY={weekday};COUNT={count}"
    return f"FREQ=WEEKLY;BYDAY={weekday};UNTIL={until_str}"


def get_service():
    with open(GOOGLE_TOKEN_PATH) as f:
        creds_info = json.load(f)
    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_info(creds_info)
    from googleapiclient.discovery import build
    return build('calendar', 'v3', credentials=creds)


def clean(service):
    """删除所有课表相关事件（包括重复规则）"""
    if not COURSE_NAMES:
        return 0
    all_ids = set()
    page_token = None
    while True:
        events = service.events().list(
            calendarId='primary',
            timeMin=(SEMESTER_START - timedelta(days=14)).strftime('%Y-%m-%dT00:00:00+08:00'),
            timeMax=(SEMESTER_START + timedelta(weeks=22)).strftime('%Y-%m-%dT00:00:00+08:00'),
            pageToken=page_token,
            fields='items(id,summary)',
            singleEvents=False
        ).execute()
        for e in events.get('items', []):
            if e.get('summary', '') in COURSE_NAMES:
                all_ids.add(e['id'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    print(f'  删除 {len(all_ids)} 个旧事件/规则...')
    for i in range(0, len(all_ids), 10):
        batch = service.new_batch_http_request()
        for eid in list(all_ids)[i:i + 10]:
            batch.add(service.events().delete(calendarId='primary', eventId=eid))
        batch.execute()
    return len(all_ids)


def create(service):
    """创建所有课程重复事件规则"""
    created = 0
    errors = 0
    for c in COURSES:
        slot = c['jcs']
        if slot not in TIMESLOT:
            continue
        st, et = TIMESLOT[slot]
        weekday = WEEKDAY_MAP.get(c['xqj'])
        if not weekday:
            continue
        color = '1'
        for kw, cl in COLOR_MAP.items():
            if kw in c['kcmc']:
                color = cl
                break
        for seg in c['weeks']:
            ws, we = seg[0], seg[1]
            parity = seg[2] if len(seg) > 2 else None
            first = SEMESTER_START + timedelta(weeks=ws - 1) + timedelta(days=c['xqj'] - 1)
            rrule = build_rrule(ws, we, weekday, parity)
            event = {
                'summary': c['kcmc'],
                'location': c['cdmc'],
                'description': f"老师: {c['xm']}",
                'start': {'dateTime': f"{first}T{st}:00+08:00", 'timeZone': 'Asia/Shanghai'},
                'end': {'dateTime': f"{first}T{et}:00+08:00", 'timeZone': 'Asia/Shanghai'},
                'recurrence': [f"RRULE:{rrule}"],
                'colorId': color,
                'reminders': {'useDefault': False, 'overrides': [{'method': 'popup', 'minutes': 15}]},
            }
            try:
                service.events().insert(calendarId='primary', body=event).execute()
                created += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  ✖ {c['kcmc']} 第{ws}-{we}周: {e}")
    return created, errors


def verify(service):
    """验证最终状态 —— 检查下周是否有重复"""
    from datetime import datetime as dt
    now = dt.now()
    monday = (now + timedelta(days=7 - now.weekday())).date()
    sunday = monday + timedelta(days=6)
    events = service.events().list(
        calendarId='primary',
        timeMin=f'{monday}T00:00:00+08:00',
        timeMax=f'{sunday}T23:59:59+08:00',
        singleEvents=True,
        fields='items(summary,start,location)'
    ).execute()
    from collections import Counter
    pairs = [(e['summary'], e['start'].get('dateTime', '')[:16])
             for e in events.get('items', [])
             if e.get('summary', '') in COURSE_NAMES]
    dups = {k: v for k, v in Counter(pairs).items() if v > 1}
    if dups:
        print(f'  ❌ 发现 {len(dups)} 个重复事件!')
        for (name, dt_str), count in dups.items():
            print(f'     {name} @ {dt_str} × {count}')
    else:
        print(f'  ✅ 下周共 {len(pairs)} 个课表事件，无重复')


if __name__ == '__main__':
    if not COURSES:
        print('⚠️  请先在脚本顶部的 COURSES 列表中填入课表数据')
        print('   数据可从正方 API 获取，参考 GUIDE.md')
        exit(1)
    if not os.path.exists(GOOGLE_TOKEN_PATH):
        print(f'⚠️  Google OAuth token 未找到: {GOOGLE_TOKEN_PATH}')
        print('   请先完成 Google Calendar API 认证')
        exit(1)

    print('📅 课表同步（先清后建）')
    service = get_service()
    print('🧹 清理阶段...')
    cleaned = clean(service)
    print(f'   已清理 {cleaned} 个')
    print('📝 创建阶段...')
    created, errors = create(service)
    print(f'   已创建 {created} 条重复规则（{errors} 失败）')
    print('✅ 验证阶段...')
    verify(service)
    print('✨ 完成')
