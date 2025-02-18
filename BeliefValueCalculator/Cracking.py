from transformers import BartForConditionalGeneration, BertTokenizer
import torch
import re
from Levenshtein import ratio
from WordTear import WordTear

class Cracking(object):
    def init(self):
        self.model_path = "../train_model_20_7729_2598_large"  # 模型所在的路径
        self.tokenizer = BertTokenizer.from_pretrained(self.model_path)
        self.model = BartForConditionalGeneration.from_pretrained(self.model_path).to(
            "cuda" if torch.cuda.is_available() else "cpu")
        self.wordtear = WordTear()

    def remove_citations(self,text):
        citation_patterns = [
            r'\[\d+\]',  # 匹配形如 [1], [2], ...
            r'\(\d+\)',  # 匹配形如 (1), (2), ...
        ]
        for pattern in citation_patterns:
            text = re.sub(pattern, '', text)
        return text

    def clean_title(self,title):
        """清理标题，去除 '_百度百科' 及词条末尾的括号及其内容"""
        title = title.replace('_百度百科', '').strip()
        title = re.sub(r'[（\[].*?[）\]]$', '', title)
        return title

    def process_sentences(self,text, title):
        """获取第一句并格式化为指定输出格式"""
        #去除注释
        cleaned_text = self.remove_citations(text)
        #分句
        sentences = re.split(r'(?<=[。！？])', cleaned_text)
        real_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            real_sentences.append(f'Input: {title}, {sentence}' if sentence else '')
        return real_sentences

    def calculate(self,name1, name2):
        similarity = ratio(name1, name2)
        return similarity

    def tichu(self,word):
        if "[" in word:
            return word[1:]
        if "]" in word:
            return word.split("/", 1)[0]
        else:
            return word

    def recognize_person_names(self,text):
        person_names = []  # 用于储存人名
        result = self.wordtear.tear(text)
        for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
            if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                try:
                    name, tag = sentence.rsplit('/', 1)
                    name = self.tichu(name)
                    if tag == 'nr' or tag == 'nrf' or tag == 'nrj':  # 保证人名中没有
                        # 分别对应中国人名、译名和日本人名
                        if name not in person_names:
                            person_names.append(name)
                except ValueError:  # 如果句子不能被正确分割，则跳过
                    print("句子不能被正确分割")
                    pass
        return person_names

    def replace_names_nr(self,text, person_names):
        result = self.wordtear.tear(text)
        modified_result = []

        for sentence in re.split(r'\s+', result):
            if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                try:
                    name, tag = sentence.rsplit('/', 1)
                    name = self.tichu(name)
                    if tag == 'nr' or tag == 'nrj':
                        max_similarity = (len(name) - 1) / len(name)
                        best_match = name
                        for value in person_names:
                            similarity = self.calculate(name, value)
                            if similarity >= max_similarity:
                                max_similarity = similarity
                                best_match = value
                        name = best_match
                    modified_result.append(name)
                except ValueError:
                    # 如果句子不能被正确分割，则跳过
                    print("句子无法被正确分割")
                    pass
        return ''.join(modified_result)

    def replace_name_nrf(self,text, person_names):
        result = self.wordtear.tear(text)
        names = []  # 用于储存按点分割后的
        modified_result = []
        n = 10  # 设置一个字数的基础值

        for sentence in re.split(r'\s+', result):
            if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                try:
                    name, tag = sentence.rsplit('/', 1)
                    name = self.tichu(name)
                    if tag == 'nrf':
                        l = len(name)
                        if "·" in name:  # 先将分隔开的内容存放在names中
                            for item in name.split("·"):
                                names.append(item)
                        else:
                            names.append(name)
                        for item in names:
                            if len(item) < n:
                                n = len(item)

                        max_similarity = (n - 1) / l
                        best_match = name
                        for value in person_names:
                            similarity = self.calculate(name, value)
                            if similarity >= max_similarity:
                                max_similarity = similarity
                                best_match = value
                        name = best_match
                    modified_result.append(name)

                except ValueError:
                    # 如果句子不能被正确分割，则跳过
                    print("句子无法被正确分割")
                    pass
        return ''.join(modified_result)

    def daici(self,text, person_names):  # 用前判断人名是不是只有一个
        result = self.wordtear.tear(text)
        key = person_names[0]
        output = []
        for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
            if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                try:
                    name, tag = sentence.rsplit('/', 1)
                    name = self.tichu(name)
                    if (tag == "rr" or name == "其") and name != "大家":
                        # 人称代词和指示代词
                        name = key
                    output.append(name)
                except ValueError:  # 如果句子不能被正确分割，则跳过
                    pass
        return ''.join(output)

    def Order(self,text, str1, str2):  # str1为“、”或cc str2为的
        index1 = text.find(str1)
        index2 = text.find(str2)
        if index1 < index2 and index2 != -1 and index1 != -1:  # 当“的”存在且连词等在前面时
            return True
        else:
            return False

    def binlie(self,text):  # 使用前要先判断有没有cc
        result = self.wordtear.tear(text)
        all = []  # 句子都有的内容
        obj = []
        part = []  # 用于同一宾语的合成
        aft = []  # 用于保存的之后的内容
        output = []
        ifverb = False
        ifude1 = False
        counter = 1  # 用于分隔宾语

        if self.Order(text, "、", "的") or self.Order(text, "/cc", "的"):  # 当为谁谁谁拥有什么什么学历时
            for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
                if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                    try:
                        name, tag = sentence.rsplit('/', 1)
                        name = self.tichu(name)
                        if tag == "v" or tag == "vshi" or tag == "vi" or tag == "vyou":
                            """
                            动词、是、有、不及物动词
                            还可以继续补充
                            """
                            all.append(name)
                            ifverb = True
                        elif not ifverb:
                            all.append(name)
                        elif ifverb and not ifude1:  # 遇到动词等之后,的之前的内容向obj添加宾语
                            if tag == "ude1":
                                ifude1 = True
                                aft.append(name)
                            elif name == "、" or tag == "cc" and name != "与":
                                obj.append(counter)
                            else:
                                obj.append(name)
                        else:
                            aft.append(name)

                    except ValueError:
                        # 如果句子不能被正确分割，则跳过
                        print("句子无法被正确分割")
                        pass
            obj.append(counter)
            for value in obj:
                if not isinstance(value, int):  # 当value不为整数时
                    part.append(value)
                else:
                    output.append(''.join(all + part + aft))
                    part = []

            return output

        # 当为 什么什么是什么什么的情况
        else:
            for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
                if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                    try:
                        name, tag = sentence.rsplit('/', 1)
                        name = self.tichu(name)
                        if tag == "v" or tag == "vshi" or tag == "vi" or tag == "vyou":
                            """
                            动词、是、有、不及物动词
                            还可以继续补充
                            """
                            all.append(name)
                            ifverb = True
                        elif not ifverb:
                            all.append(name)
                        elif ifverb:  # 遇到动词等之后向obj添加宾语
                            if name == "、" or tag == "cc":
                                obj.append(counter)
                            else:
                                obj.append(name)

                    except ValueError:
                        # 如果句子不能被正确分割，则跳过
                        print("句子无法被正确分割")
                        pass
            obj.append(counter)
            for value in obj:
                if not isinstance(value, int):  # 当value不为整数时
                    part.append(value)
                else:
                    output.append(''.join(all + part))
                    part = []

            return output

    def model_load(self,input_text, ifsecond):
        # 确保去除可能的'Input'前缀
        clean_input_text = input_text.replace("Input", "").strip()  # 去除了'Input'
        person_names = self.recognize_person_names(clean_input_text)  # 先识别出人名便于人名替换

        inputs = self.tokenizer(clean_input_text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(
            self.model.device)
        with torch.no_grad():
            generated_ids = self.model.generate(inputs["input_ids"], attention_mask=inputs["attention_mask"],
                                           max_new_tokens=512)
        pred_text = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
        pred_text = ''.join(pred_text.split())

        if not ifsecond or len(person_names) != 0:  # 当第一次裂解或者第二次裂解从input中识别出人名
            result = self.wordtear.tear(pred_text)
            # 替换人名
            if any('/nr' in item or '/nrj' in item for item in re.split(r'\s+', result)):
                pred_text = self.replace_names_nr(pred_text, person_names)
            if any('/nrf' in item for item in re.split(r'\s+', result)):
                pred_text = self.replace_name_nrf(pred_text, person_names)
            # 当人名只有一个时处理代词
            if len(person_names) == 1:
                pred_text = self.daici(pred_text, person_names)

            return "".join(pred_text.split())

        else:  # 当第二次裂解识别的人名数为0时
            output = []
            result = self.wordtear.tear(pred_text)
            for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
                if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                    try:
                        name, tag = sentence.rsplit('/', 1)
                        name = self.tichu(name)
                        if tag == "nr" or tag == "nrf" or tag == "nrj":
                            name = "None"
                        output.append(name)
                    except ValueError:
                        # 如果句子不能被正确分割，则跳过
                        print("句子无法被正确分割")
                        pass
            return ''.join(output)

    def generate_texts_for_sentences(self,input_text,title):
        #首先对文本段进行处理
        title = self.clean_title(title)
        sentences = self.process_sentences(input_text,title)

        #先对output进行分割，再次裂解，处理并列宾语
        outputs = []
        for sentence in sentences:
            if sentence == '':
                continue
            output = self.model_load(sentence, False)
            if "||" in output:
                for item in output.split("||"):
                    result = self.wordtear.tear(item)
                    if "," in item or "，" in item:  # 先进行再次裂解
                        items = []
                        items.append(''.join(self.model_load(item, True).split()))
                        for value in items:
                            result = self.wordtear.tear(value)
                            if ("/cc" in result or "、" in result) and "与" not in result:  # 判断再次裂解后的句子是否有并列结构
                                outputs.extend(self.binlie(value))
                            else:
                                outputs.append(value)
                    elif "/cc" in result or "、" in result:  # 不再次裂解则判断是否有并列宾语
                        outputs.extend(self.binlie(item))
                    else:
                        outputs.append(item)
            else:
                result = self.wordtear.tear(output)
                items = []
                if ("/cc" in result or "、" in result):
                    items.append(''.join(output.split()))
                    for value in items:
                        result = self.wordtear.tear(value)
                        if "/cc" in result or "、" in result:
                            outputs.extend(self.binlie(value))
                        else:
                            outputs.append(value)
                elif "/cc" in result or "、" in result:
                    outputs.extend(self.binlie(output))
                else:
                    outputs.append(output)
        print(outputs)
        return outputs

