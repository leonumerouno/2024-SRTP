import requests
import torch
import re
from Levenshtein import ratio
from transformers import BartForConditionalGeneration, BertTokenizer

#分词系统
url = "http://localhost/SegAPI/rest/seg"

header={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}

#加载模型路径
model_path = r"D:\pythonProject\bart_model\train_model_20_7729_2598_large"  #模型所在的路径
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BartForConditionalGeneration.from_pretrained(model_path).to("cuda" if torch.cuda.is_available() else "cpu")


#计算两个人名的相似度
def calculate(name1, name2):
    similarity = ratio(name1, name2)
    return similarity

#进行词性标注
def seg(text):
    Param = {
        'secret': 'qt80oh3psexeifkh5don6jxidicygz4ibbq5um3z',
        'segstr': text
    }
    resp = requests.get(url, params=Param, headers=header)
    return resp.text

#剔除[]
"""
分词存在如“是/vshi [金庸/nr 武侠小说/n]/nz”这样的句子
"""
def tichu(word):
    if "[" in word:
        return word[1:]
    if "]"in word:
        return word.split("/",1)[0]
    else:
        return word

#识别input中的人名
def recognize_person_names(text):
    person_names=[]#用于储存人名
    result=seg(text)
    for sentence in re.split(r'\s+', result):  #对一个或多个空格进行分割
        if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
            try:
                name, tag = sentence.rsplit('/', 1)
                name=tichu(name)
                if tag == 'nr'or tag=='nrf'or tag=='nrj':     #保证人名中没有
                    #分别对应中国人名、译名和日本人名
                    if name not in person_names:
                        person_names.append(name)
            except ValueError:  # 如果句子不能被正确分割，则跳过
                pass
    print(f"识别的人名{person_names}")
    return person_names


#识别中文名及日本人名
def replace_names_nr(text,person_names):
    result = seg(text)
    print(result)
    modified_result = []

    for sentence in re.split(r'\s+', result):
        if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
            try:
                name, tag = sentence.rsplit('/', 1)
                name = tichu(name)
                if tag == 'nr'or tag=='nrj':
                    max_similarity = (len(name) - 1) / len(name)
                    print(f"{name}应大于的数值：{max_similarity}")
                    best_match = name
                    for value in person_names:
                        similarity = calculate(name, value)
                        print(f"{name}对于{value}的相似度{similarity}")
                        if similarity >= max_similarity:
                            max_similarity = similarity
                            best_match = value
                    name = best_match
                modified_result.append(name)
            except ValueError:  # 如果句子不能被正确分割，则跳过
                pass
    return ''.join(modified_result)

# #识别译名
def replace_name_nrf(text,person_names):
    result = seg(text)
    print(result)
    names=[]#用于储存按点分割后的
    modified_result = []
    n=10   #设置一个字数的基础值

    for sentence in re.split(r'\s+', result):
        if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
            try:
                name, tag = sentence.rsplit('/', 1)
                name = tichu(name)
                if tag == 'nrf':
                    l=len(name)
                    if "·" in name:    #先将分隔开的内容存放在names中
                        for item in name.split("·"):
                            print(item)
                            names.append(item)
                    else:
                        names.append(name)
                    for item in names:
                        if len(item)<n:
                            n=len(item)

                    max_similarity=(n-1)/l
                    print(f"{name}应大于的数值为{max_similarity}")
                    best_match=name
                    for value in person_names:
                        similarity = calculate(name, value)
                        print(f"{name}对于{value}的相似度{similarity}")
                        if similarity >= max_similarity:
                            max_similarity = similarity
                            best_match = value
                    name = best_match
                modified_result.append(name)
            except ValueError:  # 如果句子不能被正确分割，则跳过
                pass
    return ''.join(modified_result)

#处理英语
# def replace_x(output_text,input_text):
#     result = seg(input_text)
#     # print(result)
#     x=[]
#     modified_result = []
#
#     for sentence in re.split(r'\s+', result):
#         if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
#             try:
#                 name, tag = sentence.rsplit('/', 1)
#                 name = tichu(name)
#                 if tag=="x":
#                     x.append(name)
#             except ValueError:  # 如果句子不能被正确分割，则跳过
#                 pass
#
#     print(f"英文有{x}")
#     result=seg(output_text)
#     for sentence in re.split(r'\s+', result):
#         if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
#             try:
#                 name, tag = sentence.rsplit('/', 1)
#                 name = tichu(name)
#                 if tag == 'x':
#                     max_similarity = 0.5
#                     print(f"{name}应大于的数值：{max_similarity}")
#                     best_match = name
#                     for value in x:
#                         similarity = calculate(name, value)
#                         print(f"{name}对于{value}的相似度{similarity}")
#                         if similarity >= max_similarity:
#                             max_similarity = similarity
#                             best_match = value
#                     name = best_match
#                 modified_result.append(name)
#             except ValueError:  # 如果句子不能被正确分割，则跳过
#                 pass
#     return ''.join(modified_result)
#
#先判断的是否在“、”，“/cc”之前
def Order(text,str1,str2):  #str1为“、”或cc str2为的
    index1=text.find(str1)
    index2=text.find(str2)
    if index1<index2 and index2!=-1 and index1!=-1:  #当“的”存在且连词等在前面时
        return True
    else:
        return False


def binlie(text):  #使用前要先判断有没有cc
    result=seg(text)
    all=[]  #句子都有的内容
    obj=[]
    part=[]  #用于同一宾语的合成
    aft=[] #用于保存的之后的内容
    output=[]
    ifverb=False
    ifude1=False
    counter=1#用于分隔宾语

    if Order(text, "、", "的") or Order(text, "/cc", "的"): #当为谁谁谁拥有什么什么学历时
        for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
            if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                try:
                    name, tag = sentence.rsplit('/', 1)
                    name = tichu(name)
                    if tag=="v"or tag=="vshi"or tag=="vi"or tag=="vyou":
                        """
                        动词、是、有、不及物动词
                        还可以继续补充
                        """
                        all.append(name)
                        ifverb = True
                    elif not ifverb:
                        all.append(name)
                    elif ifverb and not ifude1:   #遇到动词等之后,的之前的内容向obj添加宾语
                        if tag=="ude1":
                            ifude1=True
                            aft.append(name)
                        elif name=="、" or tag =="cc" and name!="与":
                            obj.append(counter)
                        else:
                            obj.append(name)
                    else:
                        aft.append(name)

                except ValueError:  # 如果句子不能被正确分割，则跳过
                    pass
        obj.append(counter)
        for value in obj:
            if not isinstance(value, int):   #当value不为整数时
                part.append(value)
            else:
                output.append(''.join(all+part+aft))
                part=[]

        return output

    #当为 什么什么是什么什么的情况
    else:
        for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
            if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                try:
                    name, tag = sentence.rsplit('/', 1)
                    name = tichu(name)
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

                except ValueError:  # 如果句子不能被正确分割，则跳过
                    pass
        obj.append(counter)
        for value in obj:
            if not isinstance(value, int):   #当value不为整数时
                part.append(value)
            else:
                output.append(''.join(all+part))
                part=[]

        return output
    # else:
    #     for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
    #         if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
    #             try:
    #                 name, tag = sentence.rsplit('/', 1)
    #                 name = tichu(name)
    #                 if tag == "v" or tag == "vshi" or tag == "vi" or tag == "vyou":
    #                     """
    #                     动词、是、有、不及物动词
    #                     还可以继续补充
    #                     """
    #                     all.append(name)
    #                     ifverb = True
    #                 elif not ifverb:
    #                     all.append(name)
    #                 elif ifverb and not ifude1:  # 动词到“的”之间
    #                     if tag == "ude1":
    #                         ifude1 = True
    #                         aft.append(name)
    #                     else:
    #                         aft.append(name)
    #                 else:
    #                     if name == "、" or tag == "cc" and name != "与":
    #                         obj.append(counter)
    #                     else:
    #                         obj.append(name)
    #
    #             except ValueError:  # 如果句子不能被正确分割，则跳过
    #                 pass
    #     obj.append(counter)
    #     for value in obj:
    #         if not isinstance(value, int):  # 当value不为整数时
    #             part.append(value)
    #         else:
    #             output.append(''.join(all + aft + part))
    #             part = []
    #
    #     return output


#处理只有一个人名的其，人称代词
def daici(text,person_names):#用前判断人名是不是只有一个
    result=seg(text)
    key=person_names[0]
    output=[]
    for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
        if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
            try:
                name, tag = sentence.rsplit('/', 1)
                name = tichu(name)
                if (tag=="rr" or name=="其") and name!="大家":
                    #人称代词和指示代词
                    name=key
                output.append(name)
            except ValueError:  # 如果句子不能被正确分割，则跳过
                pass
    return ''.join(output)



#加载模型,生成output
def model_load(input_text,ifsecond):
    # 确保去除可能的'Input'前缀

    print(f"输入{input_text}")
    clean_input_text = input_text.replace("Input", "").strip()  # 去除了'Input'
    person_names=recognize_person_names(clean_input_text) #先识别出人名便于人名替换
    # print(person_names)

    inputs = tokenizer(clean_input_text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(
        model.device)
    with torch.no_grad():
        generated_ids = model.generate(inputs["input_ids"], attention_mask=inputs["attention_mask"], max_new_tokens=512)
    pred_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    pred_text=''.join(pred_text.split())
    print(f"模型生成的输出{pred_text}")
    if not ifsecond or len(person_names)!=0:   #当第一次裂解或者第二次裂解从input中识别出人名
        result=seg(pred_text)
        #替换人名
        if any('/nr' in item or '/nrj' in item for item in re.split(r'\s+', result)):
            pred_text=replace_names_nr(pred_text,person_names)
        if any('/nrf' in item for item in re.split(r'\s+', result)):
            pred_text=replace_name_nrf(pred_text,person_names)
            # pred_text=replace_x(pred_text,clean_input_text)
        #当人名只有一个时处理代词
        if len(person_names)==1:
            pred_text=daici(pred_text,person_names)

        return "".join(pred_text.split())
    else:   #当第二次裂解识别的人名数为0时
        output=[]
        result=seg(pred_text)
        for sentence in re.split(r'\s+', result):  # 对一个或多个空格进行分割
            if '/' in sentence:  # 确保句子包含"/"，避免空字符串导致错误
                try:
                    name, tag = sentence.rsplit('/', 1)
                    name = tichu(name)
                    if tag == "nr" or tag == "nrf" or tag=="nrj":
                        name = "None"
                    output.append(name)
                except ValueError:  # 如果句子不能被正确分割，则跳过
                    pass
        return ''.join(output)



def generate_texts_for_sentences(input_text):
    """
   先对output进行分割，再次裂解，处理并列宾语
    """
    #ifsecond=False   #判断是不是二次裂解
    outputs = []
    output = model_load(input_text,False)
    if "||"in output:
        for item in output.split("||"):
            result=seg(item)
            print(result)
            if "," in item or "，" in item:     #先进行再次裂解
                print(f"再次裂解{item}")
                #ifsecond=True   #进行二次裂解
                items = []
                items.append(''.join(model_load(item,True).split()))
                print(items)
                for value in items:
                    result=seg(value)
                    if ("/cc" in result or "、"in result) and "与"not in result:  #判断再次裂解后的句子是否有并列结构
                        outputs.extend(binlie(value))

                    else:
                        outputs.append(value)
            elif "/cc" in result or "、"in result:  #不再次裂解则判断是否有并列宾语
                outputs.extend(binlie(item))
            else:
                outputs.append(item)
    else:
        result = seg(output)
        print(result)
        items=[]
        if ("/cc" in result or "、"in result) :
            items = items.append(''.join(model_load(output).split()))
            for value in items:
                result = seg(value)
                if "/cc" in result or "、"in result:
                    outputs.extend(binlie(value))
                else:
                    outputs.append(value)
        elif "/cc" in result or "、"in result:
            outputs.extend(binlie(output))
        else:
            outputs.append(output)


    print(f"替换后的输出{outputs}")
    return outputs



if __name__=="__main__":
    """
    输入Input
            """
    sentences=[
        "Input: 赵普, 赵普，1971年4月24日出生于安徽省黄山市 ，祖籍安徽省肥西县三河镇，中国内地男主持人、文化学者，毕业于中国传媒大学、北京电影学院、北京师范大学。",
        "Input: 陈道明, 陈道明，1955年4月26日出生于中国天津市，祖籍中国浙江省绍兴市，毕业于中央戏剧学院，中国内地男演员、监制、歌手、国家一级演员、中国电影家协会主席 、中国环境文化促进会理事、第十届、十一届、十二届全国政协委员、中国文学艺术界联合会第八次全国代表、广电总局颁发优秀电影表演艺术家、2006年中宣部“四个一批”人才、中国电视艺术家协会委员。",
        "Input: 林耀华, 林耀华（1910年3月27日—2000年11月27日），福建古田人，民族学家、人类学家、历史学家、社会学家和民族教育家。",
        "Input: 丁颖, 丁颖（1888年11月25日－1964年10月14日），男，字君颖，号竹铭，广东高州人，中国科学院院士，农业科学家、教育家，中国现代稻作科学主要奠基人，农业高等教育先驱。",
        "Input: 李雪涛, 李雪涛，女，傈僳族，1978年8月生，云南泸水人，1999年11月参加工作，2001年4月加入中国共产党，云南省委党校行政管理专业毕业，研究生。",
        "Input: 胡斐, 胡斐，是金庸武侠小说《飞狐外传》中的主人公《雪山飞狐》重要人物，出身于武林世家，是明末农民起义军领袖闯王李自成手下四大护卫之一，胡姓护卫的后代，英姿飒爽，才貌兼备，明心慧眼，一生品格优良，行事作派光明磊落即是最好的印证，尽管他没有做出什么惊天动地的大事业。",
        "Input: 魏巍, 魏巍，男，汉族，1981年6月出生，河北沧州人，北京林业大学城市规划与设计专业毕业，研究生学历，2008年8月参加工作，2008年12月加入中国共产党，高级工程师。",
        "Input: 查尔斯·罗伯特·达尔文, 1882年4月19日，达尔文在达温宅逝世，享年73岁，葬于威斯敏斯特大教堂。",
        "Input: 威尔特·张伯伦，威尔特·张伯伦（Wilt Chamberlain，1936年8月21日—1999年10月12日），出生于美国宾夕法尼亚州费城，前美国职业篮球运动员，司职中锋",
        "Input: 罗纳德·李维斯特，罗纳德·李维斯特（Ronald L. Rivest），1947年出生于美国纽约斯克内克塔迪，2002年图灵奖得主之一，美国国家科学院院士，美国国家工程院院士，美国艺术与科学院院士，ACM fellow，IEEE fellow，麻省理工学院教授",
        "Input: 路易·德·菲奈斯，路易·德·菲奈斯（Louis De Funès，1914年7月31日-1983年1月27日），出生于西班牙，法国著名电影演员，导演，剧作家 ",
        "Input: 杰里·韦斯特，杰里·韦斯特（Jerry AlanWest，1938年5月28日-2024年6月12日），生于美国西弗吉尼亚州奇兰镇（Cheylan），前美国职业篮球运动员，司职控球后卫，也可担任得分后卫，80年代湖人王朝和21世纪初三连冠湖人的奠基者，NBA标志原型",
    ]
    i=1
    for sentence in sentences:
        generate_texts_for_sentences(sentence)
        print(i)
        i+=1
        print(" ")


    """输出结果：
    输入Input: 赵普, 赵普，1971年4月24日出生于安徽省黄山市 ，祖籍安徽省肥西县三河镇，中国内地男主持人、文化学者，毕业于中国传媒大学、北京电影学院、北京师范大学。
识别的人名['赵普']
模型生成的输出赵普出生于1971年4月24日||赵普的出生地是安徽省黄山市||刘普的祖籍同样位于中国肥西县三河镇||陈普是中国内地的男主持人、文化学者||李普拥有中国传媒大学、北京电影学院和北京师范大学的学历。
赵普/nr 出生于/v 1971年4月24日/t |/w |/w 赵普/nr 的/ude1 出生地/n 是/vshi 安徽省/ns 黄山市/ns |/w |/w 刘普/nr 的/ude1 祖籍/n 同样/d 位于/v 中国/ns 肥西县/ns 三河镇/ns |/w |/w 陈普/nr 是/vshi [中国/ns 内地/s]/nz 的/ude1 男/b 主持人/nnt 、/w 文化学者/nnd |/w |/w 李普/nr 拥有/v [中国/ns 传媒/n 大学/nis]/nt 、/w [北京/ns 电影/n 学院/nis]/ntu 和/cc [北京/ns 师范大学/nis]/ntu 的/ude1 学历/n 。/w 
赵普应大于的数值：0.5
赵普对于赵普的相似度1.0
赵普应大于的数值：0.5
赵普对于赵普的相似度1.0
刘普应大于的数值：0.5
刘普对于赵普的相似度0.5
陈普应大于的数值：0.5
陈普对于赵普的相似度0.5
李普应大于的数值：0.5
李普对于赵普的相似度0.5
赵普/nr 出生于/v 1971年4月24日/t 
赵普/nr 的/ude1 出生地/n 是/vshi 安徽省/ns 黄山市/ns 
赵普/nr 的/ude1 祖籍/n 同样/d 位于/v 中国/ns 肥西县/ns 三河镇/ns 
赵普/nr 是/vshi [中国/ns 内地/s]/nz 的/ude1 男/b 主持人/nnt 、/w 文化学者/nnd 
赵普/nr 拥有/v [中国/ns 传媒/n 大学/nis]/nt 、/w [北京/ns 电影/n 学院/nis]/ntu 和/cc [北京/ns 师范大学/nis]/ntu 的/ude1 学历/n 。/w 
替换后的输出['赵普出生于1971年4月24日', '赵普的出生地是安徽省黄山市', '赵普的祖籍同样位于中国肥西县三河镇', '赵普是中国内地的男主持人', '赵普是文化学者', '赵普拥有中国传媒大学的学历。', '赵普拥有北京电影学院的学历。', '赵普拥有北京师范大学的学历。']
    """

