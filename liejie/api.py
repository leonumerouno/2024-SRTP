import dashscope
from dashscope import Generation
import json
from Instances_2 import instances
from functools import lru_cache
from dashscope.api_entities.dashscope_response import Role
dashscope.api_key = "sk-97319ce302d344c291afd5a4fda52b8d"


PROMPT_LIEJIE="""
Input: 1945年8月6日，美国在日本广岛投掷了第一颗原子弹，这一事件导致了大规模人员伤亡，并促使了第二次世界大战的结束，同时也引发了关于核武器伦理道德的全球性讨论。
Output: 1945年8月6日，美国向日本广岛投掷了首枚原子弹||广岛原子弹事件造成了大量人员伤亡||广岛原子弹事件直接促成了第二次世界大战的终结||广岛原子弹事件引起了全球范围对核武器伦理问题的深入讨论。

Input: 玛丽通过不懈的努力和坚定的决心，在科研项目中取得了突破性的进展，这一成就不仅为她赢得了业界的广泛赞誉，还促使她在40岁时晋升为研究所所长。
Output: 玛丽在科研项目中付出不懈努力||玛丽展现出坚定的决心||玛丽取得了突破性的科研进展||突破性的科研进展为玛丽赢得了业界的高度认可||玛丽在40岁时因这些成就晋升为研究所所长。

Input: 苏轼，字子瞻，又字和仲，号铁冠道人、东坡居士，世称苏东坡、苏仙、坡仙。 与父苏洵、弟苏辙三人并称“三苏”。 
Output: 苏轼字子瞻||苏轼字和仲||苏轼号铁冠道人||苏轼号东坡居士||世人称苏轼为苏东坡||世人称苏轼为苏仙||世人称苏轼为坡仙||苏轼的父亲是苏洵||苏轼的弟弟是苏辙||苏轼、苏洵和苏辙三人一同被并称为“三苏”。

Input: 贝多芬以其卓越的音乐才华和不屈不挠的精神，在古典音乐领域留下了深远的影响，他创作了《月光奏鸣曲》、《命运交响曲》等众多经典作品，并在失聪后仍坚持创作，成为音乐史上的一座丰碑。
Output: 贝多芬在音乐领域拥有卓越的才华||贝多芬以不屈不挠的精神著称||贝多芬的作品对古典音乐产生深远影响||贝多芬创作了《月光奏鸣曲》||贝多芬创作了《命运交响曲》||贝多芬在失聪后仍然坚持作曲||贝多芬是音乐史上的一座丰碑。

Input: 在1971年阿波罗14号任务中，美国宇航员艾伦·谢泼德成功登月，成为第三位在月球表面留下人类足迹的人，进一步扩展了人类对外太空探索的边界。
Output: 1971年，阿波罗14号任务实施||美国宇航员艾伦·谢泼德参与此次任务||艾伦·谢泼德成功登月||艾伦·谢泼德是历史上第三位在月球表面行走的宇航员||谢泼德的登月行动继续拓宽了人类对外太空探索的疆界。

Input : 爱因斯坦在理论物理学领域提出了广义相对论，这一革命性的理论改变了人们对时空观念的认识，因此在1921年荣获诺贝尔物理学奖。
Output: 爱因斯坦在理论物理学领域提出了具有革命性的广义相对论||广义相对论的提出深刻地改变了人类对时空的理解与认知||爱因斯坦在1921年被授予诺贝尔物理学奖。

Input: 薛琴, 女 ，汉族 ，1970年12月出生， 籍贯四川隆昌人 ，大学学历 ，1989年7月参加工作。
Output: 薛琴是女性||薛琴是汉族||薛琴出生于1970年12月||薛琴的籍贯是四川隆昌||薛琴拥有大学学历||薛琴自1989年7月开始参加工作。

Input: 李白（唐朝著名诗人，号青莲居士），祖籍陇西成纪（今甘肃省天水市秦安县），出生于西域碎叶城（今吉尔吉斯斯坦托克马克附近）。
Output:李白是唐朝的著名诗人||李白的别号为青莲居士||李白的祖籍位于陇西成纪||陇西成纪即今甘肃省天水市秦安县||李白出生于西域碎叶城||西域碎叶城即今吉尔吉斯斯坦托克马克附近。

Input: 阿尔伯特·爱因斯坦因其在理论物理领域的突出贡献，特别是他提出的相对论，被认为是在现代物理学发展中最具影响力的人物之一。
Output: 阿尔伯特·爱因斯坦在理论物理领域有着显著贡献||阿尔伯特·爱因斯坦提出了著名的相对论||相对论在现代物理学发展中占据了极为重要的地位||阿尔伯特·爱因斯坦被认为是现代物理学发展中最具影响力的人物之一。

Input:《三体》是刘慈欣创作的长篇科幻小说系列。
Output: 《三体》是由刘慈欣所创作||《三体》是一部长篇科幻小说系列。
"""

def qwen_generate_question(question_prompt):
    try:
        messages = []
        messages.append({'role': 'user', 'content': question_prompt})

        whole_message = ''
        responses = Generation.call(
            Generation.Models.qwen_max,
            messages=messages,
            result_format='message',
            stream=True,
            incremental_output=True
        )
        for response in responses:
            whole_message += response.output.choices[0]['message']['content']
            print(response.output.choices[0]['message']['content'], end='')

        generated_answer = whole_message
        messages.append({'role': 'assistant', 'content': generated_answer})
        return generated_answer
    except Exception as e:
        print(f"出现异常: {e}")
        return None

cache_dict = {}

@lru_cache(maxsize=500)
def cached_qwen_generate_question(question_prompt):
    """利用lru_cache装饰器实现对qwen_generate_question的缓存"""
    if question_prompt not in cache_dict:
        # 如果不在缓存中，才真正调用API
        generated_answer = qwen_generate_question(question_prompt)
        if generated_answer:
            cache_dict[question_prompt] = generated_answer
    else:
        print(f"命中缓存: {question_prompt}")
    return cache_dict.get(question_prompt, None)


def generate_intermediate_questions_and_save(prompt, instances, output_path='result042.json'):
    results = []
    for instance in instances:
        input_question = instance["Input"]
        print(f"Input: {input_question}")
        question_prompt = prompt + input_question + "\nOutput:"
        generated_answer = cached_qwen_generate_question(question_prompt)
        if generated_answer:
            results.append({"Input": input_question, "Output": generated_answer})

    # 将所有结果保存到JSON文件
    with open(output_path, 'w', encoding='utf-8') as fp:
        json.dump(results, fp, ensure_ascii=False, indent=4)
    print(f"所有结果已保存至 {output_path}")


if __name__ == "__main__":
    for instance in instances:
        input_question=instance["Input"]

    generate_intermediate_questions_and_save(PROMPT_LIEJIE, instances)




