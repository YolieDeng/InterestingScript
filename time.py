from datetime import datetime

def detailed_date_difference(input_date_str):
    """
    计算输入日期到今天的天数差，并显示：
    1. 完整天数
    2. 完整年 + 剩余天数 (X 年 Y 天)
    """
    # 将输入的字符串转为日期对象
    try:
        input_date = datetime.strptime(input_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("日期格式错误，请使用 YYYY-MM-DD 格式")
        return

    today = datetime.today().date()

    # 判断日期先后
    if today >= input_date:
        start_date, end_date = input_date, today
    else:
        start_date, end_date = today, input_date

    # 计算完整天数
    delta_days = (end_date - start_date).days

    # 计算完整年份差
    years_diff = end_date.year - start_date.year
    if (end_date.month, end_date.day) < (start_date.month, start_date.day):
        years_diff -= 1

    # 计算剩余天数
    anniversary = datetime(start_date.year + years_diff, start_date.month, start_date.day).date()
    remaining_days = (end_date - anniversary).days

    print(f"{input_date} 到 {today} 相差：")
    print(f"- {delta_days} 天")
    print(f"- {years_diff} 年 {remaining_days} 天")

if __name__ == "__main__":
    date_str = input("请输入日期 (YYYY-MM-DD): ")
    detailed_date_difference(date_str)
