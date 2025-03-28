from Compare import Compare


compare = Compare()
# input_str = "克里斯汀·贝尔出生于1980年8月"
# match_sentence_list = ['克里斯汀·贝尔的出生日期/出生年月是1980-00-10']
# sentence_point_list = [0.8894]
input_str = "陈玉华的代表作品是红娘"
ecs = "5514c3ca61ec5eea2a45c2fa"
match_sentence_list = ['陈玉华的作品/代表作品是《红娘》']
sentence_point_list = [0.777]

subject, key, value = compare.analysis_transformer(match_sentence_list, sentence_point_list)
print(subject, key, value)
func_name, func = compare.find_func(key)
if func_name == "date":
    result = compare.date(func, input_str, value)
    print(f"Score for {input_str} is {result}")
elif func_name == "others":
    best_match, best_score = compare.others(ecs, subject, input_str)
    print(f"{best_match}, {best_score}")
    print(f"Score for {input_str} is {best_score}")
else:
    result = compare.common(func, input_str, value)
    print(f"Score for {input_str} is {result}")
