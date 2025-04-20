import json
import os
import jieba
import difflib


class QASystem:
    def __init__(self, data_file="qa_data.json"):
        self.data_file = data_file
        self.qa_data = self._load_data()

    def _load_data(self):
        """加载问答数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"questions": []}
        else:
            return {"questions": []}

    def _save_data(self):
        """保存问答数据"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.qa_data, f, ensure_ascii=False, indent=2)

    def add_qa(self, question, answer, keywords=None):
        """添加问题和答案"""
        if keywords is None:
            # 自动提取关键词
            keywords = self._extract_keywords(question)

        qa_item = {
            "id": len(self.qa_data["questions"]) + 1,
            "question": question,
            "answer": answer,
            "keywords": keywords,
        }

        self.qa_data["questions"].append(qa_item)
        self._save_data()
        return qa_item["id"]

    def batch_add_qa(self, qa_list):
        """批量添加问答对

        Args:
            qa_list: 包含多个问答对的列表，每个问答对是一个字典，包含question和answer字段

        Returns:
            添加的问答对ID列表
        """
        added_ids = []
        for qa_item in qa_list:
            question = qa_item.get("question", "")
            answer = qa_item.get("answer", "")

            if question and answer:
                qa_id = self.add_qa(question, answer)
                added_ids.append(qa_id)

        return added_ids

    def delete_qa(self, qa_id):
        """删除问题和答案"""
        for i, item in enumerate(self.qa_data["questions"]):
            if item["id"] == qa_id:
                self.qa_data["questions"].pop(i)
                self._save_data()
                return True
        return False

    def batch_delete_qa(self, id_list):
        """批量删除问答对

        Args:
            id_list: 要删除的问答对ID列表

        Returns:
            成功删除的ID列表
        """
        deleted_ids = []
        for qa_id in id_list:
            if self.delete_qa(qa_id):
                deleted_ids.append(qa_id)

        return deleted_ids

    def _extract_keywords(self, text):
        """提取关键词"""
        words = jieba.cut(text)
        # 过滤常见停用词
        stopwords = {
            "的",
            "了",
            "是",
            "在",
            "我",
            "有",
            "和",
            "就",
            "不",
            "人",
            "都",
            "一",
            "一个",
            "上",
            "也",
            "很",
            "到",
            "说",
            "要",
            "去",
            "你",
            "会",
            "着",
            "没有",
            "看",
            "好",
            "自己",
            "这",
        }
        keywords = [word for word in words if word not in stopwords and len(word) > 1]
        return keywords

    def _calculate_similarity(self, query, question):
        """计算两个问题的相似度"""
        # 方法1: 分词后的关键词重合度
        query_words = set(self._extract_keywords(query))
        question_words = set(question.get("keywords", []))

        if not query_words or not question_words:
            return 0

        # 计算词汇重合度
        common_words = query_words.intersection(question_words)
        keyword_similarity = len(common_words) / max(
            len(query_words), len(question_words)
        )

        # 方法2: 字符串相似度
        string_similarity = difflib.SequenceMatcher(
            None, query, question["question"]
        ).ratio()

        # 综合两种相似度，可以调整权重
        return 0.7 * keyword_similarity + 0.3 * string_similarity

    def find_best_answer(self, query, threshold=0.3):
        """查找最匹配的答案"""
        if not self.qa_data["questions"]:
            return None

        similarities = [
            (q, self._calculate_similarity(query, q)) for q in self.qa_data["questions"]
        ]
        print(f"相似度: {similarities}")
        best_match = max(similarities, key=lambda x: x[1])
        print(f"最佳匹配: {best_match}")

        if best_match[1] >= threshold:
            return best_match[0]["answer"]
        return None

    def get_all_qa(self):
        """获取所有问答对"""
        return self.qa_data["questions"]


# 演示示例
if __name__ == "__main__":
    qa_system = QASystem()

    # 添加问答对示例
    qa_system.add_qa("如何使用这个问答系统?", "你可以问我任何问题，我会尽力回答!")
    qa_system.add_qa("群规是什么?", "请大家互相尊重，不要发广告。")
    qa_system.add_qa("今天天气怎么样?", "我不知道，因为我只是一个本地问答系统。")

    # 测试查询
    test_queries = ["怎么用这个系统", "群规定是什么", "明天会下雨吗"]

    for query in test_queries:
        answer = qa_system.find_best_answer(query)
        print(f"问题: {query}")
        print(f"回答: {answer if answer else '抱歉，我不知道答案'}")
        print()
