from sentence_transformers import SentenceTransformer,util
import torch
import pymysql
import pickle
import Dbquery
from word_similarity import WordSimilarity2010


class TopK(object):

    def __init__(self):
        self.dbquery = Dbquery.Dbquery()
        self.model = self.embedder = SentenceTransformer("distiluse-base-multilingual-cased-v2")
        self.ws_tool = WordSimilarity2010()

    def construct_sentence(self,proposition,name):
        key = proposition['key']
        value = proposition['value']
        return name + "的" + key + "是" + value

    def construct_value(self,proposition):
        key = proposition['key']
        value = proposition['value']
        return  "的" + key + "是" + value

    def sentences_prepare(self,propositions,name):
        res = []
        for proposition in propositions:
            res.append(self.construct_sentence(proposition,name))
        return res

    def values_prepare(self,propositions):
        res = []
        for proposition in propositions:
            res.append(self.construct_value(proposition))
        return res

    def Predata_sentence(self):
        result = self.dbquery.select_from_knowledge_people()

        sentences = []
        for dict in result:
            sentence = dict['name'] + "的" + dict['key'] + "是" + dict['value']
            sentences.append(sentence)

        sentences_embeddings = self.model.encode(sentences)

        # Store sentences & embeddings on disc
        with open("sentences_embeddings.pkl", "wb") as fOut:
            pickle.dump({"sentences": sentences, "embeddings": sentences_embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

    def Predata_value(self):
        result = self.dbquery.select_from_knowledge_people()

        values = []
        for dict in result:
            value = "的" + dict['key'] + "是" + dict['value']
            values.append(value)

        values_embeddings = self.model.encode(values)

        # Store sentences & embeddings on disc
        with open("values_embeddings.pkl", "wb") as fOut:
            pickle.dump({"values": values, "embeddings": values_embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

    def Sentencesimilarity(self,query,embeddings):
        if len(embeddings) == 0:
            return [""],[0]
        corpus_embeddings = self.embedder.encode(embeddings,convert_to_tensor=True)
        query_embedding = self.embedder.encode(query,convert_to_tensor=True)
        similarity_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        scores, indices = torch.topk(similarity_scores, k=5)

        real_entity_sentences = []
        best_scores = []

        for score, idx in zip(scores, indices):
            real_entity_sentences.append(embeddings[idx])
            best_scores.append(score)

        return real_entity_sentences,best_scores

    def WordSimilarity(self,word1,word2):
        return self.ws_tool.similarity(word1, word2)


# topk = TopK()
# ecs = '5514c3ca61ec5eea2a45c2fa' # 陈玉华
# # ecs = '5514c3ca61ec5eea2a45c306' # 方蕾
# real_names = []
# linked_propositions = topk.dbquery.select_from_knowledge_people_by_uuid(ecs)  # 查询数据库
# print(linked_propositions)
# name = topk.dbquery.select_name_from_knowledge_people_by_uuid(ecs)  # 查询名称
# if len(name) != 0:
#     real_names.append(name[0]['value'])
#     name = name[0]['value']
# else:
#     real_names.append(ecs)
#     name = str(ecs)
#
# print(name)
# linked_sentences = topk.sentences_prepare(linked_propositions, name)  # 生成完整句子
#
# query = "陈玉华的作品/代表作品是《红娘》"
#
# # 获取最相似的句子
# real_sentence, best_scores = topk.Sentencesimilarity(query, linked_sentences)
#
# # 输出相似度最高的句子
# for sentence, score in zip(real_sentence, best_scores):
#     print(f"相关句子: {sentence} | 相似度: {score:.4f}")
#
# linked_values = topk.values_prepare(linked_propositions)
# value_query = "的作品/代表作品是《红娘》"
# real_value, best_scores = topk.Sentencesimilarity(value_query, linked_values)
#
# for value, score in zip(real_value, best_scores):
#     print(f"相关键值: {value} | 相似度: {score:.4f}")

