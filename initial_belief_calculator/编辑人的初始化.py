import pandas as pd

def normalize(list):
    min_val = min(list)
    max_val = max(list)

    if max_val == min_val:
        # 防止除数为0的情况
        return [0 for _ in list]

    return [(val - min_val) / (max_val - min_val) for val in list]


df_editors = pd.read_csv("editors.csv", header=None)
id_list = df_editors.iloc[:, 0].tolist()
vp_list = df_editors.iloc[:, 3].tolist()
pr_list = df_editors.iloc[:, 4].tolist()
fa_list = df_editors.iloc[:, 5].tolist()
hp_list = df_editors.iloc[:, 6].tolist()
vp_list_nor = normalize(vp_list)
fa_list_nor = normalize(fa_list)
hp_list_nor = normalize(hp_list)


editors_info = {}

for i in range(10):
    editors_info.update({id_list[i]: {'versions_passed': vp_list_nor[i], 'pass_rate': pr_list[i],
                                      'featured_articles': fa_list_nor[i], 'helped_people': hp_list_nor[i]}})

print(editors_info)