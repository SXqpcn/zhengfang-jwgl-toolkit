#!/usr/bin/env python3
"""
考试倒计时提醒 —— 每天检查最近的考试并推送提醒。

用法:
    python exam-reminder.py [--json]

配置文件:
    见下方 EXAMS 列表，按你的考试安排修改。

输出格式:
    Markdown，适合飞书/Telegram/Discord 推送。
    --json 模式输出原始 JSON 数组。
"""

import sys
from datetime import datetime, date

# ============================================================
# 🔧 配置区 —— 修改为你自己的考试安排
# ============================================================
EXAMS = [
    # 格式: {"name": "课程名", "date": "YYYY-MM-DD", "time": "HH:MM-HH:MM", "location": "教学楼教室", "seat": "座位号"}
    # 示例:
    # {"name": "高等数学A2", "date": "2026-07-09", "time": "09:00-11:00", "location": "北综楼307", "seat": "54"},
]
# ============================================================

SEVERITY = [
    (0,  lambda d, e: f"🚨 **今天考试！** {e['name']} {e['time']} @ {e['location']} 座位{e['seat']}"),
    (1,  lambda d, e: f"⚠️ **明天考试！** {e['name']} {e['time']} @ {e['location']} 座位{e['seat']}"),
    (3,  lambda d, e: f"📌 **{d}天后考试** {e['name']} {e['time']} @ {e['location']} 座位{e['seat']}"),
    (7,  lambda d, e: f"📚 **{d}天后考试** {e['name']} {e['time']}"),
    (14, lambda d, e: f"📖 **{d}天后** {e['name']} {e['date']}"),
]

def main():
    if not EXAMS:
        print("⚠️  请先在脚本顶部的 EXAMS 列表中填入考试安排")
        sys.exit(1)

    if '--json' in sys.argv:
        print(str(EXAMS).replace("'", '"'))
        sys.exit(0)

    today = date.today()
    upcoming = []

    for e in EXAMS:
        exam_date = datetime.strptime(e["date"], "%Y-%m-%d").date()
        days_left = (exam_date - today).days

        if days_left < 0:
            continue

        for threshold, formatter in SEVERITY:
            if days_left <= threshold:
                upcoming.append((days_left, formatter(days_left, e)))
                break

    if not upcoming:
        print("🎉 所有考试已完成！")
        sys.exit(0)

    upcoming.sort(key=lambda x: x[0])
    output_lines = ["📋 **考试倒计时**\n"]
    for _, msg in upcoming[:5]:
        output_lines.append(msg)

    print("\n".join(output_lines))


if __name__ == "__main__":
    main()
