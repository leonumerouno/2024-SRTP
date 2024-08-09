import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from docx import Document
import re

def remove_citations(text):
    citation_patterns = [
        r'\[\d+\]',  # 匹配形如 [1], [2], ...
        r'\(\d+\)',  # 匹配形如 (1), (2), ...
    ]
    for pattern in citation_patterns:
        text = re.sub(pattern, '', text)
    return text

def clean_title(title):
    """清理标题，去除 '_百度百科' 及词条末尾的括号及其内容"""
    title = title.replace('_百度百科', '').strip()
    title = re.sub(r'[（\[].*?[）\]]$', '', title)
    return title

def process_first_sentence(text, title):
    """获取第一句并格式化为指定输出格式"""
    cleaned_text = remove_citations(text)
    sentences = re.split(r'(?<=[。！？])', cleaned_text)
    first_sentence = sentences[0].strip() if sentences else ''
    return f'Input: {title}, {first_sentence}' if first_sentence else ''

websites = [
'https://baike.baidu.com/item/%E5%BC%A0%E6%99%BA%E5%8D%8E/9631',
'https://baike.baidu.com/item/%E6%9D%A8%E6%99%93%E9%B2%81/3084256',
'https://baike.baidu.com/item/%E9%99%88%E6%B1%9F%E5%B9%B3/3092304',
'https://baike.baidu.com/item/%E4%B8%81%E5%9B%BD%E8%89%AF/3092458',
'https://baike.baidu.com/item/%E8%B0%B7%E6%B3%A2/3092914',
'https://baike.baidu.com/item/%E6%9D%9C%E6%9C%9D%E8%BE%89/3092768',
'https://baike.baidu.com/item/%E6%9B%BE%E5%85%89%E6%98%8E/4208661',
'https://baike.baidu.com/item/%E6%9B%BE%E5%85%8B%E6%9E%97/3316975',
'https://baike.baidu.com/item/%E8%B0%A2%E6%98%8E/20277181',
'https://baike.baidu.com/item/%E8%B0%A2%E5%BF%A0%E8%89%AF/3317739',
'https://baike.baidu.com/item/%E9%9D%B3%E8%99%8E/3317852',
'https://baike.baidu.com/item/%E8%B0%A2%E7%AB%8B%E5%85%A8/3317622',
'https://baike.baidu.com/item/%E4%BD%95%E9%B9%A4/16489357',
'https://baike.baidu.com/item/%E5%88%98%E7%8E%AE/14773207',
'https://baike.baidu.com/item/%E6%9D%8E%E5%A8%85/16012526',
'https://baike.baidu.com/item/%E6%B8%85%E6%B0%B4%E5%AE%97%E6%B2%BB/3331157',
'https://baike.baidu.com/item/%E6%96%8B%E8%97%A4%E5%88%A9%E4%B8%89/3331253',
'https://baike.baidu.com/item/%E6%B0%B4%E7%AE%AD%E9%BE%9F/3331348',
'https://baike.baidu.com/item/%E6%86%8E%E6%81%B6/15413475',
'https://baike.baidu.com/item/%E5%88%98%E5%8F%8B%E5%85%89/3332116',
'https://baike.baidu.com/item/%E5%88%98%E5%AD%90%E4%BA%91/17567398',
'https://baike.baidu.com/item/%E4%BC%8D%E5%AD%9A/3332304',
'https://baike.baidu.com/item/%E4%BA%8E%E6%B5%B7%E5%B9%BF/3502499',
'https://baike.baidu.com/item/%E9%A9%AC%E6%94%80%E9%BE%99/3552076',
'https://baike.baidu.com/item/%E9%A9%AC%E5%90%AF%E5%85%83/3552226',
'https://baike.baidu.com/item/%E9%A9%AC%E7%9B%BC/3552096',
'https://baike.baidu.com/item/%E9%A9%AC%E6%B3%89/23770968',
'https://baike.baidu.com/item/%E9%87%91%E6%95%8F%E4%BF%8A/3552483',
'https://baike.baidu.com/item/%E9%A9%AC%E6%97%A5%E7%A3%BE/6479554',
'https://baike.baidu.com/item/%E9%A9%AC%E5%BC%BA/2625428',
'https://baike.baidu.com/item/%E6%9D%A8%E5%B0%9A%E5%84%92/3552732',
'https://baike.baidu.com/item/%E5%BC%A0%E6%B0%B4%E5%8F%91/3553211',
'https://baike.baidu.com/item/%E5%BC%A0%E4%BA%91%E9%BE%99/6154071',
'https://baike.baidu.com/item/%E5%90%B4%E4%BA%91%E6%A0%B9/3553996',
'https://baike.baidu.com/item/%E5%88%98%E4%BA%91%E5%B3%B0/19652962',
'https://baike.baidu.com/item/%E5%88%9D%E4%B8%83/13680630',
'https://baike.baidu.com/item/%E6%9B%BC%E5%8A%A0%E5%B0%BC/3554338',
'https://baike.baidu.com/item/%E6%9E%97%E5%A8%9C/13783266',
'https://baike.baidu.com/item/%E5%88%98%E5%AD%A6%E7%91%9E/3554156',
'https://baike.baidu.com/item/%E6%9C%B1%E6%88%90/2485426',
'https://baike.baidu.com/item/%E9%9D%A2%E5%A1%91%E8%89%BA%E6%9C%AF/3555234',
'https://baike.baidu.com/item/%E7%A7%A6%E5%8D%8E/3555955',
'https://baike.baidu.com/item/%E8%92%8B%E8%93%89/3556059',
'https://baike.baidu.com/item/%E8%82%96%E4%BC%A6/3556444',
'https://baike.baidu.com/item/%E5%BC%A0%E5%AD%98%E6%B5%A9/3556518',
'https://baike.baidu.com/item/%E6%A2%81%E6%A0%8B%E6%9D%90/3557286',
'https://baike.baidu.com/item/%E5%88%98%E5%BB%BA%E5%BA%B7/45112',
'https://baike.baidu.com/item/%E5%90%B4%E4%B8%AD%E4%BC%A6/3557968',
'https://baike.baidu.com/item/%E7%8E%8B%E4%B8%96%E7%9C%9F/3557869',
'https://baike.baidu.com/item/%E7%8E%8B%E5%BE%B7%E5%AE%9D/65073',
'https://baike.baidu.com/item/%E5%BC%A0%E8%87%B4%E4%B8%80/3558228',
'https://baike.baidu.com/item/%E7%86%8A%E6%AF%85/12684',
'https://baike.baidu.com/item/%E6%9D%A8%E7%AE%80/23812464',
'https://baike.baidu.com/item/%E6%9C%B1%E7%A5%96%E7%A5%A5/12150',
'https://baike.baidu.com/item/%E9%83%AD%E6%96%87%E9%AD%81/3559097',
'https://baike.baidu.com/item/%E6%AF%9B%E5%AD%A9/3559524',
'https://baike.baidu.com/item/%E9%AA%81%E9%AA%91%E6%A0%A1/3559407',
'https://baike.baidu.com/item/%E8%83%A1%E8%8D%A3%E8%B4%B5/3119963',
'https://baike.baidu.com/item/%E6%9C%B4%E9%95%87%E5%AE%87/62030429',
'https://baike.baidu.com/item/%E7%8E%8B%E4%BB%81%E6%96%8B/62142',
'https://baike.baidu.com/item/%E5%87%8C%E5%85%83/3601323',
'https://baike.baidu.com/item/%E6%9D%A8%E6%B1%89%E6%9E%97/3601500',
'https://baike.baidu.com/item/%E6%9D%8E%E7%A6%8F%E6%9E%97/5300505',
'https://baike.baidu.com/item/%E6%9D%A8%E5%AE%B6%E4%BF%9D/3601630',
'https://baike.baidu.com/item/%E8%83%A1%E4%BA%91%E7%94%9F/3601163',
'https://baike.baidu.com/item/%E5%90%91%E6%A2%85/4096768',
'https://baike.baidu.com/item/%E5%8F%B6%E7%90%B3%E7%90%85/3601909',
'https://baike.baidu.com/item/%E5%A1%94%E5%93%88%E5%B0%94%E5%8D%A1/3601797',
'https://baike.baidu.com/item/%E5%85%8B%E6%B4%9B/6146001',
'https://baike.baidu.com/item/%E5%BC%A0%E5%9C%86/12875503',
'https://baike.baidu.com/item/%E7%94%B0%E6%96%B9/13784990',
'https://baike.baidu.com/item/%E6%96%B9%E5%AD%90%E5%93%A5/59799337',
'https://baike.baidu.com/item/%E6%9D%A8%E4%BF%8A%E6%81%92/3602559',
'https://baike.baidu.com/item/%E9%9F%A9%E9%9C%87/42580',
'https://baike.baidu.com/item/%E7%8E%8B%E4%B8%BA/7930365',
'https://baike.baidu.com/item/%E5%90%95%E7%8F%AD/3602722',
'https://baike.baidu.com/item/%E9%A9%AC%E7%A5%AF/58991008',
'https://baike.baidu.com/item/%E9%87%91%E8%8E%89%E8%8E%89/8254587',
'https://baike.baidu.com/item/%E9%A9%AC%E7%BF%8A%E5%AE%B8/3603358',
'https://baike.baidu.com/item/%E8%82%96%E5%B9%B3/3858487',
'https://baike.baidu.com/item/%E5%B2%B3%E7%BA%A2/3279562',
'https://baike.baidu.com/item/%E5%90%B4%E6%B6%9B/15823190',
'https://baike.baidu.com/item/%E4%B8%8A%E5%AE%98%E7%92%A8/3603814',
'https://baike.baidu.com/item/%E5%90%B4%E6%B0%B8%E5%85%89/6749597',
'https://baike.baidu.com/item/%E5%8F%B2%E5%8F%AF/32840',
'https://baike.baidu.com/item/%E4%B8%87%E5%AE%BE/56958144',
'https://baike.baidu.com/item/%E9%B2%8D%E6%96%B9/62148936',
'https://baike.baidu.com/item/%E4%BD%95%E8%BF%9B/13389940',
'https://baike.baidu.com/item/%E6%9D%8E%E6%B3%BD/8083261',
'https://baike.baidu.com/item/%E5%93%88%E8%BF%AA/16824709',
'https://baike.baidu.com/item/%E5%BC%A0%E6%A1%82%E8%90%8D/3406276',
'https://baike.baidu.com/item/%E7%BF%A0%E8%8A%B1/806192',
'https://baike.baidu.com/item/%E6%9D%8E%E8%A7%A3/22326504',
'https://baike.baidu.com/item/%E5%8D%97%E9%99%88%E5%8C%97%E6%9D%8E/3631434',
'https://baike.baidu.com/item/%E5%A5%94%E6%9C%88/14590614',
'https://baike.baidu.com/item/%E5%85%8B%E9%87%8C%E6%96%AF%E8%92%82%E5%AE%89%E4%B8%80%E4%B8%96/4588131',
'https://baike.baidu.com/item/%E6%A2%81%E5%BB%BA%E7%AB%A0/12825',
'https://baike.baidu.com/item/%E9%A9%AC%E8%B7%83/10445608',
'https://baike.baidu.com/item/%E5%BC%A0%E5%8D%AB/19501314',
'https://baike.baidu.com/item/%E7%8E%8B%E4%B8%B0/1945345',
'https://baike.baidu.com/item/%E4%B9%8C%E5%B0%94/10672007',
'https://baike.baidu.com/item/%E8%B4%BA%E5%BE%B7%E8%8B%B1/6923648',
'https://baike.baidu.com/item/%E5%8A%A0%E9%87%8C%E6%A3%AE/6926219',
'https://baike.baidu.com/item/%E5%AD%99%E5%A4%A7%E5%85%B4/6930274',
'https://baike.baidu.com/item/%E6%AD%A6%E5%BB%BA%E5%8D%8E/20314668',
'https://baike.baidu.com/item/%E8%BF%9E%E4%BD%93%E5%85%84%E5%BC%9F/6933203',
'https://baike.baidu.com/item/%E6%98%A5%E9%A6%99/63249',
'https://baike.baidu.com/item/%E6%9C%AC%E5%A4%9A%E6%AD%A3%E4%BF%A1/8657920',
'https://baike.baidu.com/item/%E6%9E%97%E7%BF%A0/8657902',
'https://baike.baidu.com/item/%E6%9C%89%E9%A9%AC%E6%99%B4%E4%BF%A1/8657868',
'https://baike.baidu.com/item/%E7%9C%9F%E7%94%B0%E4%BF%A1%E4%B9%8B/8658166',
'https://baike.baidu.com/item/%E7%BB%86%E5%B7%9D%E5%BF%A0%E5%85%B4/8658367',
'https://baike.baidu.com/item/%E7%8E%9B%E9%97%A8/79919',
'https://baike.baidu.com/item/%E6%AD%A6%E5%AE%89%E5%9B%BD/12830',
'https://baike.baidu.com/item/%E6%9E%97%E5%90%AF/10533547',
'https://baike.baidu.com/item/%E7%99%BD%E4%BA%91%E5%B3%B0/7225840',
'https://baike.baidu.com/item/%E6%AE%B5%E5%A9%95/10539281',
'https://baike.baidu.com/item/%E6%9D%A8%E5%85%B4%E4%B9%89/5219347',
'https://baike.baidu.com/item/%E5%BC%A0%E6%83%A0%E5%AE%81/10540081',
'https://baike.baidu.com/item/%E7%8E%8B%E4%B9%89/453000',
'https://baike.baidu.com/item/%E6%9F%B3%E8%90%8D/10540025',
'https://baike.baidu.com/item/%E7%8E%8B%E4%B8%B9%E5%8D%8E/21171',
'https://baike.baidu.com/item/%E7%8E%8B%E6%95%8F%E6%B8%85/7687898',
'https://baike.baidu.com/item/%E6%9D%A8%E5%8F%91%E6%98%8E/20960',
'https://baike.baidu.com/item/%E5%BC%A0%E9%B9%8F%E7%BF%94/3500659',
'https://baike.baidu.com/item/%E8%94%A1%E8%8F%81/2671899',
'https://baike.baidu.com/item/%E9%BB%84%E5%86%A0%E8%8B%B1/24116253',
'https://baike.baidu.com/item/%E6%B8%A9%E6%99%AF%E6%96%87/15868769',
'https://baike.baidu.com/item/%E5%88%98%E5%A4%A9%E9%94%A1/9161117',
'https://baike.baidu.com/item/%E6%9D%8E%E6%98%A5%E8%99%B9/10540992',
'https://baike.baidu.com/item/%E9%99%88%E6%99%93%E9%98%B3/142025',
'https://baike.baidu.com/item/%E5%BE%90%E7%92%86/10542557',
'https://baike.baidu.com/item/%E6%9D%A8%E8%84%A9/8088',
'https://baike.baidu.com/item/%E5%91%A8%E8%8D%A3/7402343',
'https://baike.baidu.com/item/%E9%99%88%E5%BF%A0/4145304',
'https://baike.baidu.com/item/%E9%82%93%E5%BD%AA/6776692',
'https://baike.baidu.com/item/%E7%8E%8B%E9%BE%9A/10542750',
'https://baike.baidu.com/item/%E5%91%A8%E4%B8%BE/10543290',
'https://baike.baidu.com/item/%E9%92%9F%E7%9A%93/10543406',
'https://baike.baidu.com/item/%E7%8E%8B%E6%BD%AE/24418224',
'https://baike.baidu.com/item/%E7%8E%8B%E6%B0%B8%E5%B9%B4/2068071',
'https://baike.baidu.com/item/%E5%88%98%E7%A5%90/7423',
'https://baike.baidu.com/item/%E6%9D%9C%E4%B9%94/9248322',
'https://baike.baidu.com/item/%E5%88%98%E6%B7%91/548363',
'https://baike.baidu.com/item/%E5%9B%BE%E4%BC%AF%E7%89%B9/10547411',
'https://baike.baidu.com/item/%E6%B0%B8%E5%AE%89%E5%85%AC%E4%B8%BB/9724096',
'https://baike.baidu.com/item/%E9%BB%84%E6%97%B6%E4%B8%AD/10547578',
'https://baike.baidu.com/item/%E8%A3%B4%E7%A5%9E%E7%AC%A6/10547448',
'https://baike.baidu.com/item/%E7%BD%97%E5%9F%B9%E6%96%B0/10548584',
'https://baike.baidu.com/item/%E5%BC%A0%E5%85%86%E4%B8%9C/18238232'

    # 在这里添加你的百度百科网址
]

doc = Document()

options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
        'permissions.default.stylesheet': 2,
        'javascript': 2
    }
}
options.add_experimental_option('prefs', prefs)

browser = webdriver.Chrome(options=options)
browser.implicitly_wait(10)

for website in websites:
    try:
        browser.get(website)
        raw_title = browser.title
        title = clean_title(raw_title)
        wait = WebDriverWait(browser, 10)

        # 使用正确的xpath抓取摘要部分
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "lemmaSummary_Swr9S J-summary")]')))
        first_sentence = process_first_sentence(element.text, title)

        # 将第一句话写入Word文档
        if first_sentence:
            doc.add_paragraph(first_sentence)
    except Exception as e:
        print(f"访问网站 {website} 出现异常：{e}")

browser.quit()

doc.save('output_processed2.docx')
print("处理后的结果已保存至Word文档。")