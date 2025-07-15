from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
import logging

def download_showmebug_video(url):
    # Chrome配置
    chrome_options = Options()
    # 保留浏览器界面，方便调试
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 初始化浏览器
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager(driver_version="138.0.7204.101").install()),
        options=chrome_options
    )
    
    try:
        logging.info(f"打开网页: {url}")
        driver.get(url)
        time.sleep(3)  # 等待页面初步加载

        # 截图看页面实际内容
        driver.save_screenshot("debug.png")
        logging.info("已保存页面截图 debug.png")

        # 等待遮罩层消失
        logging.info("等待加载遮罩层消失")
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "el-loading-mask"))
        )
        logging.info("遮罩层已消失，准备点击播放按钮")

        # 等待并点击可见的播放按钮
        play_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".bar-action[style=''] .smb-icon-play-key"))
        )
        logging.info("点击播放按钮")
        driver.execute_script("arguments[0].click();", play_button)

        # 等待视频元素加载
        logging.info("等待视频元素加载")
        video_element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
        
        # 打印 video 元素结构
        print("video outerHTML:", video_element.get_attribute('outerHTML'))

        # 尝试获取 source 标签
        try:
            source = video_element.find_element(By.TAG_NAME, "source")
            source_url = source.get_attribute('src')
            print(f"Source URL: {source_url}")
        except Exception as e:
            print("未找到 source 标签:", e)

        # 循环等待 src 属性
        blob_url = ""
        for _ in range(30):
            blob_url = video_element.get_attribute('src')
            if blob_url:
                break
            time.sleep(1)
        print(f"Blob URL: {blob_url}")
        
        # 切换到blob处理
        driver.execute_script(f"""
        fetch("{blob_url}")
            .then(response => response.blob())
            .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'interview_video.mp4';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            }})
        """)
        
        # 等待下载
        time.sleep(10)
        
    except Exception as e:
        import traceback
        print(f"发生错误: {e}")
        traceback.print_exc()
    
    finally:
        driver.quit()

# 使用示例
url = "https://www.showmebug.com/paas_nipads/NJAEBAHGBSTWWGYE"
download_showmebug_video(url)
