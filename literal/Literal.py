import requests
import re
from WordTear import WordTear

class Literal(object):
    def __init__(self):
        self.word_tear = WordTear()

    def _chinese_to_arabic(self, chinese_num_str):
        chinese_num_map = {
            '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9
        }

        chinese_unit_map = {
            '十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000
        }

        result = 0
        temp_number = 0

        for char in chinese_num_str:
            if char in chinese_num_map:
                temp_number = chinese_num_map[char]
            elif char in chinese_unit_map:
                unit = chinese_unit_map[char]
                if temp_number == 0 and unit >= 10:
                    temp_number = 1
                result += temp_number * unit
                temp_number = 0
            else:
                return chinese_num_str

        result += temp_number
        return result

    def _convert_chinese_num_in_string(self, text):
        chinese_num_pattern = re.compile(r'[零一二三四五六七八九十百千万亿]+')

        def replace_func(match):
            chinese_num = match.group()
            arabic_num = self._chinese_to_arabic(chinese_num)
            return str(arabic_num)

        return chinese_num_pattern.sub(replace_func, text)


    def age(self, seg):
        age = self.word_tear.get_value('mq', seg)
        age_num = self._convert_chinese_num_in_string(age)
        match_age = re.match(r'(\d+)\s*岁', age_num)
        return int(match_age.group(1))

    def blood(self, seg):
        blood_types = {"A", "AB", "B", "O"}
        if self.word_tear.get_value('ng', seg) == "型":
            value_or_list = self.word_tear.get_value('x', seg)
            if type(value_or_list) == list:
                blood = [item for item in value_or_list if item in blood_types]
                if len(blood) == 1:
                    return blood[0]
                else:
                    return ""
            else:
                return value_or_list

    def constellation(self, seg):
        zodiac_signs = [
            '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座',
            '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座'
        ]

        pattern = re.compile(r'(' + '|'.join(zodiac_signs) + r')')
        match = pattern.search(seg)
        if match:
            return match.group(1)
        else:
            return ""

    def date(self, seg):
        date = self.word_tear.get_value('t', seg)
        # 使用正则表达式匹配年、月、日
        match = re.match(r'(?:(\d{4})年)?(?:(\d{1,2})月)?(?:(\d{1,2})日)?', date)

        if not match:
            return ""

        year = match.group(1) if match.group(1) else '0000'
        month = match.group(2).zfill(2) if match.group(2) else '00'
        day = match.group(3).zfill(2) if match.group(3) else '00'

        return f"{year}-{month}-{day}"

    def height(self, seg):
        def convert_to_cm(height):
            unit_conversion = {
                '尺': 33.3333,
                '寸': 3.3333,
                '米': 100,
                'm': 100,
                '分米': 10,
                'dm': 10,
                '厘米': 1,
                'cm': 1,
                '英尺': 30.48,
                '英寸': 2.54
            }

            # 匹配标准单位格式
            match_normal = re.match(r'(\d+\.?\d*)([a-zA-Z\u4e00-\u9fa5]+)', height)
            if match_normal:
                number = float(match_normal.group(1))
                unit = match_normal.group(2)
                if unit in unit_conversion:
                    return round(number * unit_conversion[unit], 2)

            # 匹配“英尺 英寸”格式
            inch_1_match = re.match(r'(\d+\.?\d*)英尺(\d+\.?\d*)英寸', height)
            if inch_1_match:
                feet = float(inch_1_match.group(1))
                inch = float(inch_1_match.group(2))
                return round(feet * 30.48 + inch * 2.54, 2)

            # 匹配“尺 寸”格式
            inch_2_match = re.match(r'(\d+\.?\d*)尺(\d+\.?\d*)寸', height)
            if inch_2_match:
                feet = float(inch_2_match.group(1))
                inch = float(inch_2_match.group(2))
                return round(feet * 33.3333 + inch * 3.3333, 2)

            return ''

        value_or_list = self.word_tear.get_value('mq', seg)
        height = ''
        if isinstance(value_or_list, list):
            for value in value_or_list:
                height += value
        else:
            height = value_or_list

        height_cm = convert_to_cm(self._convert_chinese_num_in_string(height))

        return str(height_cm)

    def gender(self, seg):
        if '男' in seg:
            return '男'
        elif '女' in seg:
            return '女'
        else:
            return ''

    def special_name(self, seg):
        value_or_list = self.word_tear.get_value('x', seg)
        if type(value_or_list) == list:
            eng_name = ' '.join(value_or_list)
        else:
            eng_name = value_or_list

        return eng_name

    def weight(self, seg):
        def convert_to_kg(input_str):
            unit_conversion = {
                '公斤': 1,
                '千克': 1,
                'kg': 1,
                '斤': 0.5,
                '克': 0.001,
                'g': 0.001,
                '磅': 0.453592,
                '英镑': 0.453592,
                'lbs': 0.453592
            }
            match = re.match(r'([0-9.]+)([a-zA-Z\u4e00-\u9fa5]+)', input_str)
            number = float(match.group(1))
            unit = match.group(2)
            if unit in unit_conversion:
                number_in_kg = round(number * unit_conversion[unit], 2)
            return number_in_kg

        weight = self.word_tear.get_value('mq', seg)

        weight_kg = convert_to_kg(self._convert_chinese_num_in_string(weight))

        return str(weight_kg)











