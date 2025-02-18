from TopK import TopK
from WordTear import WordTear
from Dbquery import Dbquery
from EntityLink import EntityLink
from Cracking import Cracking
from Calculator import Calculator
from InitialBelief import InitialBelief

a = 0.5
b = 0.5

topK = TopK()
wordtear = WordTear()
dbquery = Dbquery()
entitylink = EntityLink()
cracking = Cracking()
calculator = Calculator()
initialbelief = InitialBelief()

cracking.init()
calculator.init()

f = open("url.txt","r")

urls = []

for line in f.readlines():
    urls.append(line.split("\n")[0])

cnt = 0
for url in urls:
    cnt += 1
    if cnt != 62:
        continue
    # todo:need record
    # 计算初始可信度值
    # initial_beliefvalue = initialbelief.calculate(url)

    context,title = initialbelief.getContext(url)

    queries = cracking.generate_texts_for_sentences(context,title)

    answer = 0.0
    good_cnt = 0.0

    for i in range(0,len(queries)):
        #获取命题对应的实体
        real_sentences = []
        best_scores = []

        query = queries[i]

        print(query)
        names = wordtear.get_names(query)
        print(names)

        real_names = []
        for name in names:
            # 从元命题库中获得所有同名的实体
            propositions = dbquery.select_from_knowledge_people_by_name_like(name)
            proposition_dict = entitylink.propositions_divide(propositions)
            entities = entitylink.get_entities(propositions)
            # print("Entities In List:" + str(entities))

            #对上下文进行拆分
            context_point = wordtear.tear_context(context)

            #进行实体链接
            res = 0.0
            ecs = ""
            for entity_name in entities:
                #对每个可能相同的实体进行拆分
                entity_point = wordtear.tear_entity(proposition_dict[entity_name])
                ans = 0.0
                for word in entity_point:
                    ans += context_point[word]
                if ans >= res:
                    res = ans
                    ecs = entity_name

            # print(ecs)

            linked_propositions = dbquery.select_from_knowledge_people_by_uuid(ecs)
            name = dbquery.select_name_from_knowledge_people_by_uuid(ecs)

            if len(name) != 0:
                real_names.append(name[0]['value'])
                name = name[0]['value']
            else:
                real_names.append(ecs)
                name = str(ecs)

            linked_sentences = topK.sentences_prepare(linked_propositions,name)

            real_sentence,best_score = topK.Sentencesimilarity(query,linked_sentences)

            for s in real_sentence:
                real_sentences.append(s)

            if type(best_score) == int:
                best_scores.append(best_score)
            else:
                for bs in best_score:
                    best_scores.append(bs)

        now_ans = calculator.calculate(input_str=query,match_sentence_list=real_sentences,sentence_point_list=best_scores)
        if now_ans != -1:
            answer += now_ans
            good_cnt += 1

    final_value = 0
    belief_value = 0
    if good_cnt == 0:
        belief_value = 0
        final_value = initial_beliefvalue * a
    else:
        belief_value = answer / good_cnt
        final_value = answer / good_cnt * b + initial_beliefvalue * a
    with open("calculate_result.txt","a") as f:
        f.write("URL:" + url + "\n")
        f.write("initial_value:" + str(initial_beliefvalue) + "\n")
        f.write("context_value:" + str(belief_value) + "\n")
        f.write("good_count:" + str(good_cnt) + "\n")
        f.write("final_value:" + str(final_value) + "\n")




