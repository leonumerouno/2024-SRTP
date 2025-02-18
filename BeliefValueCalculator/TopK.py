from sentence_transformers import SentenceTransformer,util
import torch
import pymysql
import pickle
import Dbquery
from word_similarity import WordSimilarity2010

class TopK(object):

    def __init__(self):
        self.dbquery = Dbquery.Dbquery()
        self.model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
        self.embedder = SentenceTransformer("distiluse-base-multilingual-cased-v2")
        self.ws_tool = WordSimilarity2010()

    def construct(self,proposition,name):
        key = proposition['key']
        value = proposition['value']
        return name + "的" + key + "是" + value

    def sentences_prepare(self,propositions,name):
        res = []
        for proposition in propositions:
            res.append(self.construct(proposition,name))
        return res

    def Predata(self):
        result = self.dbquery.select_from_knowledge_people()

        sentences = []
        for dict in result:
            sentence = dict['name'] + "的" + dict['key'] + "是" + dict['value']
            sentences.append(sentence)

        embeddings = self.model.encode(sentences)

        # Store sentences & embeddings on disc
        with open("embeddings.pkl", "wb") as fOut:
            pickle.dump({"sentences": sentences, "embeddings": embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

    def Sentencesimilarity(self,query,embeddings):
        if len(embeddings) == 0:
            return [""],[0]
        corpus_embeddings = self.embedder.encode(embeddings,convert_to_tensor=True)
        query_embedding = self.embedder.encode(query,convert_to_tensor=True)
        similarity_scores = util.cos_sim(query_embedding, corpus_embeddings)[0]
        scores, indices = torch.topk(similarity_scores, k=2)

        real_entity_sentences = []
        best_scores = []

        for score, idx in zip(scores, indices):
            real_entity_sentences.append(embeddings[idx])
            best_scores.append(score)

        return real_entity_sentences,best_scores


    def WordSimilarity(self,word1,word2):
        return self.ws_tool.similarity(word1, word2)



