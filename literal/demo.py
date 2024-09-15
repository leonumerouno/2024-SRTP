from Literal import Literal
import re


def match_entity(sentence):
    pattern = re.compile(r'(.*)的(.*)是(.*)')
    match = pattern.match(sentence)
    if match:
        subject = match.group(1).strip()
        key = match.group(2).strip()
        value = match.group(3).strip()
        return subject, key, value
    else:
        return None

key_to_function = {
    '出生日期/出生年月': 'date',
    '逝世日期': 'date',
    '血型': 'blood',
    '年龄/年': 'age',
    '身高/高': 'height',
    '身高': 'height',
    '体重/重': 'weight',
    '性别': 'gender',
    '星座': 'constellation',
    '外文名/英语名': 'special_name'
}

# input_str = "马特尔·韦伯斯特全名Martell Webster"
# match_sentence_list = [
#     '马特尔·韦伯斯特的外文名/英语名是Martell Webster',
#     '泰勒·洛特纳#*#泰莱·罗纳（港译）#*#泰勒·洛特（台译）的外文名/英语名是Taylor Lautner#*#Taylor Daniel Lautner（全名）'
# ]
# sentence_point_list = [
#     0.8971,
#     0.3827
# ]
input_str = "克里斯汀·贝尔出生于1980年8月"
match_sentence_list = ['克里斯汀·贝尔的出生日期/出生年月是1980-00-10']
sentence_point_list = [0.8894]
# input_str = "西蒙娜·韦伊是一位女性"
# match_sentence_list = ['西蒙娜·韦伊的外文名/英语名是Simone Weil', '金莉的出生地是山东青岛', '西蒙娜·韦伊的性别是女']
# sentence_point_list = [0.6863, 0.3557, 1] # 编的
# input_str = "张乔的星座属于天秤座"
# match_sentence_list = ['张乔的星座是天秤座']
# sentence_point_list = [1] # 编的
# input_str = "李娜拥有五英尺三英寸"
# match_sentence_list = ['李娜的身高/高是152.4']
# sentence_point_list = [1] # 编的
# input_str = "李娜的体重为五十八磅"
# match_sentence_list = ['李娜的体重/重是26.31']
# sentence_point_list = [1] # 编的
print(f"裂解后的最小分句: {input_str}")
print(match_sentence_list)
print(sentence_point_list)

literal = Literal()
max_point = max(sentence_point_list)
if max_point < 0.7:
    print("无法识别")
else:
    # 第一步：将sentence_transformer的句子解析出来
    max_index = sentence_point_list.index(max_point)
    match_sentence = match_sentence_list[max_index]
    subject, key, value = match_entity(match_sentence)
    print(f"识别到的key是: {key}; 识别到的value是: {value}")

    # 第二步：通过解析出来的句子的key来查找使用的函数
    func_name = key_to_function.get(key)
    func = getattr(literal, func_name, None)

    if func_name == "date":
        # 第三步中"date"的特殊处理
        result = True
        date_value = func(input_str)
        print(f"日期的值为: {date_value}")
        year_bool = True
        month_bool = True
        day_bool = True
        year_, month_, day_ = date_value.split('-')
        year, month, day = value.split('-')

        if year_ == "0000":
            year_bool = False
        elif month_ == "00":
            month_bool = False
        elif day_ == "00":
            day_bool = False

        if year_bool and month_bool and day_bool:
            if date_value != value:
                result = False
        elif year_bool and month_bool:
            if (year != year_ and year != "0000") or (month != month_ and month != "00"):
                result = False
        elif month_bool and day_bool:
            if (month != month_ and month != "00") or (day != day_ and day != "00"):
                result = False
        elif year_bool and day_bool:
            if (year != year_ and year != "0000") or (day != day_ and day != "00"):
                result = False
        elif year_bool:
            if year != year_ and year != "0000":
                result = False
        elif month_bool:
            if month != month_ and month != "00":
                result = False
        elif day_bool:
            if day != day_ and day != "00":
                result = False

        if result:
            print("True")
        else:
            print("False")

    else:
        # 第三步：调用函数，从裂解后的最小分句提取出value
        entity_value = func(input_str)
        print(f"实体的值为: {entity_value}")

        if entity_value == value:
            print("TRUE")
        else:
            print("FALSE")





