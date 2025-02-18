import re
from Literal import Literal

class Calculator(object):
    def init(self):
        self.key_to_function = {
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
        self.literal = Literal()

    def match_entity(self,sentence):
        pattern = re.compile(r'(.*)的(.*)是(.*)')
        match = pattern.match(sentence)
        if match:
            subject = match.group(1).strip()
            key = match.group(2).strip()
            value = match.group(3).strip()
            return subject, key, value
        else:
            return None

    def calculate(self,input_str,match_sentence_list,sentence_point_list):
        #todo:1,0,uncalculated、
        max_point = 1
        if len(sentence_point_list) == 0:
            return -1
        else:
            max_point = max(sentence_point_list)
        if max_point < 0.7:
            print(max_point)
            return -1
        else:
            # 第一步：将sentence_transformer的句子解析出来
            max_index = sentence_point_list.index(max_point)
            print(max_index,match_sentence_list,sentence_point_list)
            match_sentence = match_sentence_list[max_index]
            subject, key, value = self.match_entity(match_sentence)
            print(f"识别到的key是: {key}; 识别到的value是: {value}")

            # 第二步：通过解析出来的句子的key来查找使用的函数
            print(key)
            func_name = self.key_to_function.get(key)
            if func_name != None:
                func = getattr(self.literal, func_name, None)
            else:
                return -1

            if func_name == "date":
                # 第三步中"date"的特殊处理
                result = True
                date_value = func(input_str)
                # print(f"日期的值为: {date_value}")
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
                    # print("True")
                    print("a")
                    return 1.0
                else:
                    print("b")
                    return 0.0
                    # print("False")

            else:
                # 第三步：调用函数，从裂解后的最小分句提取出value
                entity_value = func(input_str)
                # print(f"实体的值为: {entity_value}")

                if entity_value == value:
                    # print("TRUE")
                    return 1.0
                else:
                    return 0.0
                    # print("FALSE")