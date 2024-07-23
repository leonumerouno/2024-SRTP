#预处理文本

import json
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def remove_citations(text):
    citation_patterns = [
        r'\[\d+\]',  # 匹配形如 [1], [2], ...
        r'\(\d+\)',  # 匹配形如 (1), (2), ...
        r'\[\d+—\d+\]'  # 新增匹配形如 [1—2], [3—5], ...
    ]
    for pattern in citation_patterns:
        text = re.sub(pattern, '', text)
    return text

def clean_title(title):
    """清理标题，去除 '_百度百科' 及词条末尾的括号及其内容"""
    # 去除 '_百度百科'
    title = title.replace('_百度百科', '').strip()
    # 查找并移除末尾的括号及其内容（包括圆括号和方括号）
    title = re.sub(r'[（\[].*?[）\]]$', '', title)
    return title

def process_and_format_text(text, title):
    """处理文本并格式化为JSON格式"""
    cleaned_text = remove_citations(text)
    sentences = re.split(r'(?<=[。！？])', cleaned_text)
    formatted_output = [{"Input": f"{title}, {s.strip()}"} for s in sentences if s.strip()]
    return formatted_output

websites=[
'https://baike.baidu.com/item/%E9%99%88%E7%82%9C/15933275'
]
options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
        'permissions.default.stylesheet': 2,
        'javascript': 2
    }
}
options.add_experimental_option('prefs', prefs)
options.add_argument("disable_infobars")
#options.add_experimental_option("excludeSwitches",['enable-automation'])

browser = webdriver.Chrome(options=options)
browser.implicitly_wait(10)

all_data = []

for website in websites:
    try:
        browser.get(website)
        # 提取并清理页面标题作为词条名
        raw_title = browser.title
        title = clean_title(raw_title)
        wait = WebDriverWait(browser, 10)
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="J-lemma-main-wrapper"]/div[2]/div/div[1]/div/div[4]')))
        processed_data = process_and_format_text(element.text, title)
        all_data.extend(processed_data)

    except Exception as e:
        print(f"访问网站 {website} 出现异常：{e}")

browser.quit()

# 保存数据到JSON文件
with open('outputtest.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=4)

print("处理后的结果已保存至JSON文件。")