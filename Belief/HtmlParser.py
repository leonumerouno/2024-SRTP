import HtmlDownloader
import UrlManager
import json
from bs4 import BeautifulSoup

class HtmlParser(object):
    def __init__(self):
        self.downloader = HtmlDownloader.HtmlDownloader()
        self.urls = UrlManager.UrlManager

    def get_views(self,url):
        html_cont = self.downloader.download(url)

        soup = BeautifulSoup(html_cont, 'lxml', from_encoding='utf-8')

        try:
            cnt = soup.find_all("div",{'class':'description_yxRex'})[0].text.split("：")[1].split("次")[0]
        except IndexError:
            return

        return int(cnt)

    def get_lemmas(self,url):
        html_cont = self.downloader.download(url)

        soup = BeautifulSoup(html_cont, 'lxml', from_encoding='utf-8')

        titleScript = soup.find_all("script")
        if len(titleScript) == 0:
            return []

        scripttext = ""

        for script in titleScript:
            if len(script) > 0 and script.text[0] == 'w' and script.text[7] == 'P':
                scripttext = script.text[18:]

        python_obj = json.loads(scripttext)
        navigations = python_obj.get('navigation')

        if navigations == None:
            return [], [], []

        result = navigations.get('lemmas')

        lemmaIds = []
        difnames = []
        lemmaTitles = []
        uppernames = []

        for dict in result:
            id = dict.get('lemmaId')
            lemmaIds.append(id)

            lemmaTitle = dict.get('lemmaTitle')
            lemmaTitles.append(lemmaTitle)

            difname = lemmaTitle + '[' + dict.get('lemmaDesc') + ']'
            difnames.append(difname)

            uppernames.append(dict.get('classify'))

        return lemmaIds, difnames, lemmaTitles, uppernames

    def get_editor_urls(self,url):
        html_cont = self.downloader.download_edit_history(url)

        soup = BeautifulSoup(html_cont, 'lxml', from_encoding='utf-8')
        titleScripts = soup.find_all("a",{'class':'uname'})
        tds = soup.find_all("td")
        divs = soup.find_all("div")

        edited_times = 0

        for div in divs:
            if "共被编辑" in div.text:
                str = div.text
                str1 = str.split("辑")[1]
                str2 = str1.split("次")[0]
                edited_times = int(str2)
                break

        editor_urls = []
        editor_name = []
        edit_times = []

        for titleScript in titleScripts:
            href = titleScript['href']
            editor_urls.append(self.urls.create_editor_url(href))
            editor_name.append(titleScript.text)

        for td in tds:
            if "submitTime" in td['class'][0]:
                edit_times.append(td.text)

        return editor_name,editor_urls,edit_times,edited_times

    def get_editor_infos(self,url):
        html_cont = self.downloader.download_user(url)
        soup = BeautifulSoup(html_cont, 'lxml', from_encoding='utf-8')

        totalCounts = soup.find_all("span", {'class': 'total-count'})

        if len(totalCounts) == 0:
            return 0,0,0,0

        passed_versions = ""
        passed_versions_split = totalCounts[0].text.split(',')
        for splits in passed_versions_split:
            passed_versions += splits

        passed_versions = int(passed_versions)

        pass_rate = totalCounts[1].text.split("%")
        pass_rate = int(pass_rate[0]) / 100

        special_versions = ""
        special_versions_split = totalCounts[2].text.split(',')
        for splits in special_versions_split:
            special_versions += splits

        special_versions = int(special_versions)

        helped_people = ""
        helped_people_split = totalCounts[3].text.split(',')
        for splits in helped_people_split:
            helped_people += splits

        helped_people = int(helped_people)

        return passed_versions, pass_rate, special_versions, helped_people