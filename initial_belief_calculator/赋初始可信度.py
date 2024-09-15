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


# 编辑次数权重
W_h = 0.01
# 编辑时间权重
W_t = 0.01
# 编辑人信息权重
W_e = 0.98
# 编辑人通过版本权重
W_vp = 0.14
# 编辑人通过率权重
W_pr = 0.09
# 编辑人特色词条数权重
W_fa = 0.01
# 编辑人已帮助人数权重
W_hp = 0.76


warnings.simplefilter(action='ignore', category=FutureWarning)

def transform_daytime(time_string):
    daytime = datetime.strptime(time_string, "%Y-%m-%d %H:%M")
    return daytime

def edit_division(path):
    # 传出的形式为{'edit_list_1': [{'data': ,'editor': }, {'data': ,'editor': },....], 'edit_list_2': ......}
    df_editors = pd.read_csv(path, header=None)
    whole_edit_list = {}
    i = 0
    edit_str = "fucku"
    for index, row in df_editors.iterrows():
        if row.iloc[2] != edit_str:
            i += 1
            whole_edit_list[int(i)] = []
            whole_edit_list[int(i)].append({'date': transform_daytime(row[3]), 'editor': row[1]})
            edit_str = row.iloc[2]
        elif row.iloc[2] == edit_str:
            whole_edit_list[int(i)].append({'date': transform_daytime(row[3]), 'editor': row[1]})
            edit_str = row.iloc[2]
    return whole_edit_list

def mean_value_normalize(list):
    min_val = min(list)
    max_val = max(list)
    if max_val == min_val:
        # 防止除数为0的情况
        return [0 for _ in list]
    mv_list = [(val - min_val) / (max_val - min_val) for val in list]
    return mv_list

def nonlinear_normalisation_arc(list):
    # 转换为 numpy 数组
    arr = np.array(list)
    # 使用 np.arctan 函数进行反余切转换，然后乘2/π使最后的结果趋于0-1
    nl_list = np.arctan(arr) * 2 / np.pi
    return nl_list


def nonlinear_normalisation_lg(list):
    # 转换为 numpy 数组
    arr = np.array(list)
    # 避免数列中的0搞事情
    arr = np.where(arr <= 0, 1e-10, arr)
    # 使用 np.log10 函数进行转换
    nl_list = np.log10(arr) * 2 / np.pi
    # 再进行一次差值转化
    nl_list = mean_value_normalize(nl_list)
    return nl_list


def editor(path):
    df_editors = pd.read_csv(path, header=None)
    editors_list = {}
    editor_score = {}
    # 通过版本数
    vp_list = df_editors.iloc[:, 3].tolist()
    vp_list = nonlinear_normalisation_lg(vp_list)
    df_editors.iloc[:, 3] = vp_list
    # 通过率
    pr_list = df_editors.iloc[:, 4].tolist()
    pr_list = mean_value_normalize(pr_list)
    df_editors.iloc[:, 4] = pr_list
    # 特色词条数
    fa_list = df_editors.iloc[:, 5].tolist()
    fa_list = nonlinear_normalisation_arc(fa_list)
    df_editors.iloc[:, 5] = fa_list
    # 已帮助人数
    hp_list = df_editors.iloc[:, 6].tolist()
    hp_list = nonlinear_normalisation_lg(hp_list)
    df_editors.iloc[:, 6] = hp_list
    for index, row in df_editors.iterrows():
        editors_list[row[1]] = {'vp': row[3], 'pr': row[4], 'fa': row[5], 'hp': row[6]}
        #editors_list的形式为{'editor_name': {'vp': ,'pr': ,'fa': ,'hp': }, 'editor_name': {'vp': ,'pr': ,'fa': ,'hp': }......}
        editor_score[row[1]] = ((editors_list[row[1]]['vp'] * W_vp) + (editors_list[row[1]]['pr'] * W_pr) +
                                (editors_list[row[1]]['fa'] * W_fa) + (editors_list[row[1]]['hp'] * W_hp))
    return editors_list, editor_score

def time_decay_score(edit_date, current_date):
    time_diff = current_date - edit_date
    time_diff_days = time_diff.days + time_diff.seconds / 86400
    # lambda越大下降越快
    return math.exp(-0.1 * time_diff_days)



def calculate_initial_trustworthiness(create_history_path):
    entry_score = {}
    entry = pd.read_csv(create_history_path, header=None)
    if len(edit_division('data/edit.csv')) == len(entry):
        i = 0
        length = len(edit_division('data/edit.csv'))
        while i < length:
            i += 1
            # persent = "{:.2f}%".format((i / length) * 100)
            # print(f"目前进度{persent}")
            time_score = sum(time_decay_score(edit['date'], current_date)
                             for edit in edit_division('data/edit.csv')[i]) / len(edit_division('data/edit.csv')[i])
            editor_sum_value = 0
            editor_num = 0
            for edit in edit_division('data/edit.csv')[i]:
                if edit['editor'] in editor('data/editors.csv')[1]:
                    editor_sum_value += editor('data/editors.csv')[1][edit['editor']]
                    editor_num += 1
            editor_score = editor_sum_value / editor_num
            content_stability_score = 1 / (1 + len(edit_division('data/edit.csv')[i]))

            entry_score[entry.iloc[i - 1, 1]] = (content_stability_score * W_h + time_score * W_t + editor_score * W_e)
    return entry_score


# 当前日期
# current_date = datetime.now()
# 固定的时间
current_date = datetime(2024, 5, 28)

# 计算初始可信度
whole_entry_score = calculate_initial_trustworthiness('data/create_history.csv')
whole_entry_name = list(whole_entry_score.keys())
info_entry = pd.read_csv('data/information.csv', header=None)
info_entry[4] = None
for index, row in info_entry.iterrows():
    if row[0] in whole_entry_name:
        entry_score = whole_entry_score[row[0]]
        info_entry.at[index, 4] = entry_score

info_entry.to_csv('data/information_after_calculation.csv', index=False, header=False)


for entry_name in whole_entry_name:
    entry_score = whole_entry_score[entry_name]
    print(f"The initial trustworthiness of '{entry_name}' is {entry_score}")