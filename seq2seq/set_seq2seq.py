from transformers import BartForConditionalGeneration, BertTokenizer
import torch

# 加载模型和分词器
model_path = "D:\pythonProject\seq2seq\my_finetuned_bart_model_2_for20"
tokenizer = BertTokenizer.from_pretrained(model_path)
model = BartForConditionalGeneration.from_pretrained(model_path).to("cuda" if torch.cuda.is_available() else "cpu")


def generate_text(input_text):
    """
    使用训练好的模型生成预测文本，确保移除输入文本中的'Input'标识。

    参数:
    input_text (str): 用户提供的输入文本，可能带有'Input'前缀。

    返回:
    str: 模型生成的预测文本。
    """
    # 确保去除可能的'Input'前缀
    clean_input_text = input_text.replace("Input", "").strip()  # 这里去除了'Input'

    inputs = tokenizer(clean_input_text, return_tensors="pt", padding=True, truncation=True, max_length=512).to(
        model.device)
    with torch.no_grad():
        generated_ids = model.generate(inputs["input_ids"], attention_mask=inputs["attention_mask"], max_new_tokens=500)
    pred_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return  "Output: " + pred_text.strip()

# 示例用法
def generate_texts_for_sentences(sentences):
    """
    对给定的句子列表中的每个句子，使用训练好的模型生成预测文本。

    参数:
    sentences (list[str]): 用户提供的句子列表。

    返回:
    list[str]: 包含模型针对每个输入句子生成的预测文本的列表。
    """
    outputs = []
    for sentence in sentences:
        output = generate_text(sentence)
        outputs.append(output)
    return outputs


# 示例用法
if __name__ == "__main__":
    sentences = [
        "Input: 陈国良, 陈国良（1944.1-）1967年毕业于南京铁道医学院医疗系。",
        "Input: 陈国良, 抗日战争期间，历任豫鄂边警卫团长、鄂中分区后勤处政委等职。",
        "Input: 宋学义, 1939年参加抗日游击队，编入晋察冀一分区一团七连六班当战士，1941年加入中国共产党。",
        "Input: 蔡和, 蔡和是游戏《三国智》官渡-惊蛰版本中的卡牌。",
        "Input: 郑冲, 郑冲为人清恬寡欲，博究儒术，是《晋律》的编修者之一。",
        "Input: Labyrinth, 《Labyrinth》是由韩国女子演唱组合GFriend录唱的一首歌曲，于2020年2月3日发行。",
        "Input: Labyrinth, 《Labyrinth》是由歌手Alesana演唱的歌曲，收录于2011年10月17日发行的专辑中。",
        "Input: 蔡中, 蔡中，原名蔡兰阶，又名蔡钟。",
        "Input: 夏侯恩, 不想撞着赵云，被他一枪刺死。",
        "Input: 夏侯德, 在汉中镇守天荡山，接纳战败的张郃、夏侯尚等人。",
        "Input: 傅巽, 三国时期曹魏大臣，是西汉义阳侯傅介子的后代。",
        "Input: 姜芃, 姜芃，是灾难电影《狂鳄海啸》中的角色，由荣飞饰演。",
        "Input: 于海东, 于海东，蒙古族，现为大连三仪动物药品有限公司设备网络保障部电工。",
        "Input: 巴布尔, 巴布尔于1494年继费尔干纳王位。",
        "Input: 王文才, 原新疆军区副政委。",
        "Input: 李维新, 德国慕尼黑大学医学院访问学者、美国华盛顿大学Harborview医学中心联合培训导师。",
        "Input: 李维新, 李维新，男：（清），云南呈贡人。",
        "Input: 王森, 2016年6月，参演都市剧《外科风云》，饰演扬子轩 ；9月，参演电影《击战》，饰演雷皓 。",
        "Input: 王森, 擅唱评剧白派曲目，河北梆子、京剧等片段，曾获卡拉OK大赛优秀表演奖。",
        "Input: 陈鹏年, 翌年，升任江宁知府，严惩两江总督阿山宠信的不法僧人。",
        "Input: ASOS, 1995年，推出组合首张日语专辑《Best Of SOS》，从而正式进军日本歌坛 。",
        "Input: 林旭, 林旭于清光绪十九年（1893年），中举人，后入赀官内阁中书。",
        "Input: 郭元兴, 郭元兴（1920—1989）现代佛教学者。",
        "Input: 邓实, 1877年生于上海。",
        "Input: 米芾, 北宋书法家、画家、书画理论家。",
        "Input: 褚遂良, 隋末时期，追随西秦霸王薛举，担任通事舍人。",
        "Input: 郑俊浩, 1996年，获得电视播出奖新人奖。",
        "Input: 郑俊浩, 2004年，郑俊浩主演喜剧片《大佬传奇》。",
        "Input: 任静, 2017年12月，获得中国综艺峰会匠心盛典年度匠心制作人。",
        "Input: 马旭, 马旭，男，湖南澧州人，师参谋长。",
        "Input: 杨柳, 建筑技术科学省级重点学科学术带头人，国家创新群体学术骨干。",
        "Input: 杨柳, 国家卫生健康委医疗应急工作专家组眼科组成员。",
        "Input: 甄诚, 后被史进生擒，宋江将他碎剐于市，血祭英魂。",
        "Input: 李洋, 现任中国航天科工集团有限公司纪检监察组组长、党组成员。",
        "Input: 张莉, 为了追寻自己成为优秀导演和制片人的梦想， 张莉放弃了电视剧制作中心的工作。",
        "Input: 张莉, 2010年张莉在国内发展房地产业，每年都会回国几趟，照顾她在北京的资产。",
        "Input: 昂山素季, 2012年全国民主联盟重新注册后担任主席。",
        "Input: 刘表, 东汉末年宗室、名士、军阀 ，汉末群雄之一，西汉鲁恭王刘余之后 。",
        "Input: 女神, 女神是一个汉语词语，拼音是nǚ shén，意思指对女性的神明或至尊的称谓。",
        "Input: 女神, 《女神》是一款横版仙侠题材回合制RPG手游。",
        "Input: 刘勰, 南朝梁时期大臣，文学理论家、文学批评家，刘宋越骑校尉刘尚之子。",
        "Input: 西施, 该片讲述了春秋时期，吴国擒获越王。",
        "Input: 白灵, 白灵，美籍华裔女演员，电影制片人、编剧。",
        "Input: 白灵, 白灵（Ghost ）是琼恩·雪诺的白色冰原狼 ，外观像狐狸。",
        "Input: 陈琳, 陈琳初为古射阳（即盐渎）地方官， 汉灵帝末年（189年），任大将军何进主簿。",
        "Input: 诸葛青云, 台北行政专科学校（即中兴大学法商学院前身）毕业，曾任“总统府第一局”科员。",
        "Input: 王驾, 《史记·高祖本纪》：“楚因四面击之。",
        "Input: 崔珏, 判官位于酆都天子殿中，负责审判来到冥府的幽魂。",
        "Input: 张乐平, 毕生从事漫画创作，画笔生涯达60多个春秋。",
        "Input: 春野樱, 春野樱是《火影忍者》手游中登场的一名C级忍者角色。"
    ]

    outputs = generate_texts_for_sentences(sentences)
    for i, (input_text, output) in enumerate(zip(sentences, outputs)):
        print(f"\n输入文本 {i + 1}: {input_text}")
        print(f"模型生成的输出 {i + 1}: {output}")