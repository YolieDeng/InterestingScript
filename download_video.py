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
import base64

def download_blob_url(blob_url, filename='video.mp4'):
    """
    专门下载Blob URL视频的函数
    
    Args:
        blob_url (str): Blob类型的视频URL
        filename (str, optional): 保存的文件名. 默认 'video.mp4'.
    """
    try:
        # 创建downloads目录
        os.makedirs('downloads', exist_ok=True)
        
        # Chrome配置
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # 初始化浏览器
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # 打开空白页
        driver.get(blob_url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 获取当前页面源码并尝试下载
        download_script = """
        return new Promise((resolve) => {
            const video = document.querySelector('video');
            if (video && video.src) {
                fetch(video.src)
                .then(response => response.blob())
                .then(blob => {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        resolve(reader.result);
                    };
                    reader.readAsDataURL(blob);
                });
            } else {
                resolve(null);
            }
        });
        """
        
        # 执行下载脚本
        base64_data = driver.execute_script(download_script)
        
        # 关闭浏览器
        driver.quit()
        
        # 解码Base64数据
        if base64_data:
            # 移除Base64前缀
            base64_data = base64_data.split(',')[1]
            video_data = base64.b64decode(base64_data)
            
            # 完整路径
            full_path = os.path.join('downloads', filename)
            
            # 写入文件
            with open(full_path, 'wb') as f:
                f.write(video_data)
            
            print(f"🎉 视频下载成功: {full_path}")
            return full_path
        else:
            print("❌ 未找到可下载的视频")
            return None
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def download_showmebug_video(url):
    # Chrome配置
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # 初始化浏览器
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        logging.info(f"打开网页: {url}")
        driver.get(url)
        time.sleep(3)  # 等待页面初步加载

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
        play_button.click()

        # 等待视频元素加载
        logging.info("等待视频元素加载")
        video_element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
        
        # 循环等待 src 属性
        blob_url = ""
        for _ in range(30):
            blob_url = video_element.get_attribute('src')
            if blob_url and blob_url.startswith('blob:'):
                break
            time.sleep(1)
        
        print(f"Blob URL: {blob_url}")
        driver.quit()  # 关闭原浏览器
        
        # 下载视频
        if blob_url:
            download_blob_url(blob_url)
        
    except Exception as e:
        import traceback
        print(f"发生错误: {e}")
        traceback.print_exc()
        driver.quit()

# 使用示例
url = "https://www.showmebug.com/paas_nipads/NJAEBAHGBSTWWGYE"
download_showmebug_video(url)
