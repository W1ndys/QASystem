import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
from collections import defaultdict
import jieba
from db_manager import QADatabaseManager
import scipy.sparse
from typing import Optional


class AdvancedQAMatcher:
    def __init__(self):
        self.qa_pairs = []
        self.vectorizer = TfidfVectorizer(tokenizer=self._tokenize)
        self.tfidf_matrix: Optional[scipy.sparse.csr_matrix] = None
        self.keyword_index = defaultdict(list)
        self.db = QADatabaseManager()
        self._load_from_db()

    def _load_from_db(self):
        # 从数据库加载所有QA对
        self.qa_pairs = [(q, a) for _, q, a in self.db.get_all_qa_pairs()]

    def _tokenize(self, text):
        text = text.lower()
        tokens = list(jieba.cut(text))
        return [t for t in tokens if t.strip()]

    def add_qa_pair(self, question, answer):
        self.qa_pairs.append((question, answer))
        self.db.add_qa_pair(question, answer)

    def build_index(self):
        # 构建TF-IDF索引
        questions = [q for q, a in self.qa_pairs]
        self.tfidf_matrix = self.vectorizer.fit_transform(questions).tocsr()  # type: ignore

        # 构建关键词倒排索引
        self.keyword_index.clear()
        for idx, (q, a) in enumerate(self.qa_pairs):
            keywords = set(self._tokenize(q))
            for word in keywords:
                self.keyword_index[word].append(idx)

    def _get_candidate_indices(self, query):
        # 使用关键词索引初步筛选候选问题
        query_keywords = set(self._tokenize(query))
        candidate_indices = set()

        for word in query_keywords:
            if word in self.keyword_index:
                candidate_indices.update(self.keyword_index[word])

        return (
            list(candidate_indices) if candidate_indices else range(len(self.qa_pairs))
        )

    def find_best_match(self, query, threshold=0.47):
        if not self.qa_pairs or self.tfidf_matrix is None:
            return None, None, 0.0

        # 步骤1: 初步筛选候选问题
        candidate_indices = self._get_candidate_indices(query)

        # 步骤2: 计算TF-IDF余弦相似度
        query_vec = self.vectorizer.transform([query])
        indices = list(candidate_indices)
        assert isinstance(self.tfidf_matrix, scipy.sparse.csr_matrix)
        tfidf_candidates = scipy.sparse.vstack(
            [self.tfidf_matrix[i] for i in indices]
        ).tocsr()
        similarities = cosine_similarity(query_vec, tfidf_candidates)  # type: ignore
        best_candidate_idx = np.argmax(similarities)
        best_score = similarities[0, best_candidate_idx]
        best_qa_idx = indices[best_candidate_idx]

        # 步骤3: 使用编辑距离进行二次验证
        seq_score = difflib.SequenceMatcher(
            None, query, self.qa_pairs[best_qa_idx][0]
        ).ratio()
        # 优化加权方式：TF-IDF与编辑距离0.3:0.7
        combined_score = 0.3 * best_score + 0.7 * seq_score

        if combined_score >= threshold:
            orig_question, orig_answer = self.qa_pairs[best_qa_idx]
            return orig_question, orig_answer, combined_score
        return None, None, combined_score


if __name__ == "__main__":
    matcher = AdvancedQAMatcher()
    matcher.build_index()

    while True:
        query = input("请输入问题: ")
        orig_question, answer, score = matcher.find_best_match(query)
        print(f"问题: {query}")
        if answer:
            print(f"数据库原句: {orig_question}")
            print(f"匹配答案: {answer} (相似度: {score:.2f})\n")
        else:
            print(f"未找到合适答案 (相似度: {score:.2f})\n")
