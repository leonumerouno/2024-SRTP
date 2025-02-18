import numpy as np
import pandas as pd
import warnings
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import ParameterGrid
import math
from datetime import datetime, timedelta
from sklearn.model_selection import ParameterSampler
from joblib import Parallel, delayed
from tqdm import tqdm
from urllib import parse
from HtmlDownloader import HtmlDownloader
from bs4 import BeautifulSoup

class InitialBelief(object):
    def __init__(self):
        # 编辑次数权重
        self.W_h = 0.015
        # 编辑时间权重
        self.W_t = 0.01
        # 编辑人信息权重
        self.W_e = 0.975
        # 编辑人通过版本权重
        self.W_vp = 0.1051
        # 编辑人通过率权重
        self.W_pr = 0.7807
        # 编辑人特色词条数权重
        self.W_fa = 0.0259
        # 编辑人已帮助人数权重
        self.W_hp = 0.0883
        self.current_date = datetime.now()
        self.downloader = HtmlDownloader()
        warnings.simplefilter(action='ignore', category=FutureWarning)

    def transform_daytime(self,time_string):
        daytime = datetime.strptime(time_string, "%Y-%m-%d %H:%M")
        return daytime

    def mean_value_normalize(self,list):
        if len(list) == 0:
            return [0 for _ in list]
        min_val = min(list)
        max_val = max(list)
        if max_val == min_val:
            # 防止除数为0的情况
            return [0 for _ in list]
        mv_list = [(val - min_val) / (max_val - min_val) for val in list]
        return mv_list

    def nonlinear_normalisation_arc(self,list):
        # 转换为 numpy 数组
        arr = np.array(list)
        # 使用 np.arctan 函数进行反余切转换，然后乘2/π使最后的结果趋于0-1
        nl_list = np.arctan(arr) * 2 / np.pi
        return nl_list


    def nonlinear_normalisation_lg(self,list):
        # 转换为 numpy 数组
        arr = np.array(list)
        # 避免数列中的0搞事情
        arr = np.where(arr <= 0, 1e-10, arr)
        # 使用 np.log10 函数进行转换
        nl_list = np.log10(arr) * 2 / np.pi
        # 再进行一次差值转化
        nl_list = self.mean_value_normalize(nl_list)
        return nl_list

    def time_decay_score(self,edit_date, current_date):
        time_diff = current_date - edit_date
        time_diff_days = time_diff.days + time_diff.seconds / 86400
        # lambda越大下降越快
        return math.exp(-0.1 * time_diff_days)

    def get_lemmas(self,url):
        lemmas = url.split("/")

        lemmaTitle = lemmas[4]
        lemmaId = lemmas[5]

        return lemmaTitle,lemmaId

    def create_history_url(self,url):
        lemmaTitle,lemmaId = self.get_lemmas(url)
        return "https://baike.baidu.com/p/history?lemmaTitle=" + lemmaTitle + "&lemmaId=" + lemmaId

    def create_editor_url(self,href):
        return "https://baike.baidu.com" + href

    def get_edit_history(self,url):
        edit_history = []

        history_url = self.create_history_url(url)
        html_cont = self.downloader.download_edit_history(history_url)

        soup = BeautifulSoup(html_cont, 'lxml', from_encoding='utf-8')
        titleScripts = soup.find_all("a", {'class': 'uname'})
        tds = soup.find_all("td")

        editor_urls = []
        edit_times = []

        for titleScript in titleScripts:
            href = titleScript['href']
            editor_urls.append(self.create_editor_url(href))


        for td in tds:
            if "submitTime" in td['class'][0]:
                edit_times.append(td.text)

        for i in range(0,len(editor_urls)):
            edit_list = {}
            edit_list['date'] = self.transform_daytime(edit_times[i])
            edit_list['editor'] = editor_urls[i]
            edit_history.append(edit_list)

        return edit_history

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

    def get_editors(self,edits):
        vp_list = []
        pr_list = []
        fa_list = []
        hp_list = []

        editors = []
        for edit in edits:
            if edit['editor'] in editors:
                continue

            passed_versions, pass_rate, special_versions, helped_people = self.get_editor_infos(edit['editor'])

            vp_list.append(passed_versions)
            pr_list.append(pass_rate)
            fa_list.append(special_versions)
            hp_list.append(helped_people)

            editors.append(edit['editor'])

        return vp_list, pr_list, fa_list, hp_list

    def cal_editor(self,edit_history,vp_list, pr_list, fa_list, hp_list):
        vp_list = self.nonlinear_normalisation_lg(vp_list)
        pr_list = self.mean_value_normalize(pr_list)
        fa_list = self.nonlinear_normalisation_arc(fa_list)
        hp_list = self.nonlinear_normalisation_lg(hp_list)

        editor_sum_value = 0.0

        editor_sum = len(vp_list)

        for i in range(0,editor_sum):
            editor_sum_value += vp_list[i] * self.W_vp + pr_list[i] * self.W_pr + fa_list[i] * self.W_fa + hp_list[i] * self.W_hp

        return editor_sum_value,editor_sum

    def calculate(self,url):
        edit_history = self.get_edit_history(url)

        time_score = 0.0
        if(len(edit_history)) != 0:
            time_score = sum(self.time_decay_score(edit['date'], self.current_date) for edit in edit_history) / len(edit_history)
        else:
            time_score = 0

        vp_list, pr_list, fa_list, hp_list = self.get_editors(edit_history)

        editor_sum_value,editor_sum = self.cal_editor(edit_history,vp_list, pr_list, fa_list, hp_list)

        if editor_sum == 0:
            return 0.0

        editor_score = editor_sum_value / editor_sum

        content_stability_score = 1 / (1 + len(edit_history))

        value = content_stability_score * self.W_h + time_score * self.W_t + editor_score * self.W_e

        f = open("initial_value.txt","a")

        f.write(url + " Initial score = " + str(value) + "\n")

        return value

    def getContext(self,url):
        html_cont,title = self.downloader.download(url)
        soup = BeautifulSoup(html_cont, 'lxml', from_encoding='utf-8')

        divs = soup.find_all("div", {'class': 'para_TPQgK summary_myo7c MARK_MODULE'})
        context = ""

        for div in divs:
            context += div.text

        return context,title