from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json,os

# 启动 Chrome 浏览器
options = Options()
# options.add_argument("--headless")
options.add_argument("--disable-extensions")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-data-dir=/tmp/selenium_profile")
options.add_argument("--start-maximized")

print("启动浏览器...")
driver = webdriver.Chrome(options=options)
print("浏览器已启动")

print("打开网页...")
driver.get("http://192.168.31.101:3000/test")
print("网页已打开")

print("等待页面元素加载...")
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[id^='test-']")))
print("页面元素已加载")


result_file = "result.json"
if os.path.exists(result_file):
    with open(result_file, "r", encoding="utf-8") as f:
        try:
            old_results = json.load(f)
        except Exception:
            old_results = []
else:
    old_results = []

results = old_results

# 获取所有题目区块
test_blocks = driver.find_elements(By.CSS_SELECTOR, "div[id^='test-']")

failed_questions = []

start_from = "Question #37"
start_flag = False

run_questions = ["Question #6", "Question #9", "Question #14"]

for block in test_blocks:
    question_title = "(未知题号)"
    try:
        # 获取题号（h3）
        question_title = block.find_element(By.TAG_NAME, "h3").text.strip()

        # if question_title not in run_questions:
        #     continue

        # 只从指定题号开始
        if not start_flag:
            if question_title == start_from:
                start_flag = True
            else:
                continue  # 跳过前面的题目
        # 下面是原有处理逻辑
        print(f"\n========== 开始处理：{question_title} ==========")

        # 获取所有按钮，找到“Run Test”按钮
        print("查找 Run Test 按钮...")
        buttons = block.find_elements(By.TAG_NAME, "button")
        run_button = None
        for btn in buttons:
            if btn.text.strip() == "Run Test":
                run_button = btn
                break
        if run_button is None:
            print(f"⚠️ {question_title} 未找到 Run Test 按钮")
            failed_questions.append(question_title)
            continue
        print("Run Test 按钮已找到。")

        # 如果按钮被禁用，解除禁用
        if not run_button.is_enabled():
            print("Run Test 按钮被禁用，尝试解除禁用...")
            driver.execute_script("arguments[0].removeAttribute('disabled')", run_button)
            print("已解除禁用。")

        # 点击按钮
        print("点击 Run Test 按钮...")
        run_button.click()

        # 等待 block 内有文本为“Running...”的按钮出现
        print("等待按钮变为 Running... 状态...")
        WebDriverWait(block, 15).until(
            lambda d: block.find_elements(By.XPATH, ".//button[normalize-space(text())='Running...']")
        )
        print("按钮已变为 Running...。")

        # 等待按钮重新变回“Run Test”并且可点击
        print("等待按钮变回 Run Test 并且结果出现...")
        def wait_for_run_test_button(driver):
            try:
                btn = block.find_element(By.XPATH, ".//button[normalize-space(text())='Run Test' and not(@disabled)]")
                return btn.is_enabled()
            except Exception:
                return False

        WebDriverWait(block, 600).until(wait_for_run_test_button)
        print("按钮已变回 Run Test，且结果已出现。")

        # 获取结果
        result_span = block.find_element(By.XPATH, ".//p[contains(., 'Result')]/span")
        result_text = result_span.text.strip()
        print(f"{question_title}: {result_text}")
        # 获取详细解释内容（如果有）
        try:
            detail = block.find_element(By.XPATH, ".//div[contains(@style, 'white-space: pre-wrap')]").text
        except Exception:
            detail = ""

        # 获取特殊 <p> 内容
        try:
            bold_p = block.find_element(By.XPATH, ".//p[@style='margin: 0px 0px 10px; font-weight: bold;']").get_attribute("outerHTML")
        except Exception:
            bold_p = ""

        try:
            answer_p = block.find_element(By.XPATH, ".//p[@style='margin: 0px; background-color: rgb(249, 249, 249); padding: 5px;']").get_attribute("outerHTML")
        except Exception:
            answer_p = ""

        results.append({
            "question": question_title,
            "result": result_text,
            "detail": detail,
            "bold_p": bold_p,
            "answer_p": answer_p
        })

        # 立即写入 result.json
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        if "Correct" not in result_text:
            failed_questions.append(question_title)
        print(f"========== {question_title} 处理结束 ==========")
        time.sleep(1)  # 方便观察

    except Exception as e:
        import traceback
        print(f"⚠️ {question_title} 执行出错：{repr(e)}")
        print(traceback.format_exc())
        failed_questions.append(question_title)
        results.append({
            "question": question_title,
            "result": "Error",
            "detail": str(e)
        })
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"========== {question_title} 处理异常 ==========")
        continue

print("\n❌ 以下题目未通过:")
for q in failed_questions:
    print(q)

with open("result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# driver.quit()