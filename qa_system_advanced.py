import json
import os
import jieba
import difflib
import re
from collections import Counter
from datetime import datetime


class QASystemAdvanced:
    def __init__(self, data_file="qa_data_advanced.json"):
        self.data_file = data_file
        self.qa_data = self._load_data()
        # 加载停用词
        self.stopwords = self._load_stopwords()
        # 初始化反馈数据
        if "feedback" not in self.qa_data:
            self.qa_data["feedback"] = {}
        # 初始化统计数据
        if "stats" not in self.qa_data:
            self.qa_data["stats"] = {"total_queries": 0, "matched_queries": 0}

    def _load_stopwords(self):
        """加载停用词"""
        default_stopwords = {
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
        return default_stopwords

    def _load_data(self):
        """加载问答数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"questions": [], "categories": {}}
        else:
            return {"questions": [], "categories": {}}

    def _save_data(self):
        """保存问答数据"""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.qa_data, f, ensure_ascii=False, indent=2)

    def add_qa(self, question, answer, category=None, keywords=None):
        """添加问题和答案"""
        # 生成问题ID
        qa_id = len(self.qa_data["questions"]) + 1

        # 如果没有提供关键词，自动提取
        if keywords is None:
            keywords = self._extract_keywords(question)

        # 创建问答对象
        qa_item = {
            "id": qa_id,
            "question": question,
            "answer": answer,
            "keywords": keywords,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": category,
            "similar_questions": [],
        }

        # 添加到问答列表
        self.qa_data["questions"].append(qa_item)

        # 如果指定了分类，将问题添加到分类中
        if category:
            if category not in self.qa_data["categories"]:
                self.qa_data["categories"][category] = []

            self.qa_data["categories"][category].append(qa_id)

        self._save_data()
        return qa_id

    def batch_add_qa(self, qa_list):
        """批量添加问答对

        Args:
            qa_list: 包含多个问答对的列表，每个问答对是一个字典，包含question和answer字段，可选category字段

        Returns:
            添加的问答对ID列表
        """
        added_ids = []
        for qa_item in qa_list:
            question = qa_item.get("question", "")
            answer = qa_item.get("answer", "")
            category = qa_item.get("category", None)

            if question and answer:
                qa_id = self.add_qa(question, answer, category=category)
                added_ids.append(qa_id)

        return added_ids

    def add_similar_question(self, qa_id, similar_question):
        """添加相似问题表述"""
        for i, item in enumerate(self.qa_data["questions"]):
            if item["id"] == qa_id:
                keywords = self._extract_keywords(similar_question)
                self.qa_data["questions"][i]["similar_questions"].append(
                    {"text": similar_question, "keywords": keywords}
                )
                self._save_data()
                return True
        return False

    def delete_qa(self, qa_id):
        """删除问题和答案"""
        for i, item in enumerate(self.qa_data["questions"]):
            if item["id"] == qa_id:
                # 从问题列表中删除
                removed_item = self.qa_data["questions"].pop(i)

                # 从分类中删除
                if removed_item.get("category"):
                    category = removed_item["category"]
                    if category in self.qa_data["categories"]:
                        if qa_id in self.qa_data["categories"][category]:
                            self.qa_data["categories"][category].remove(qa_id)

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
        # 使用正则表达式替换标点符号
        text = re.sub(r"[^\w\s]", "", text)
        words = jieba.cut(text)
        keywords = [
            word for word in words if word not in self.stopwords and len(word) > 1
        ]
        return keywords

    def _calculate_similarity(self, query, question_item):
        """计算问题相似度"""
        # 计算与主问题的相似度
        main_similarity = self._calculate_text_similarity(
            query, question_item["question"]
        )

        # 计算与所有相似问题的相似度
        similar_scores = []
        for similar_q in question_item.get("similar_questions", []):
            sim_score = self._calculate_text_similarity(query, similar_q["text"])
            similar_scores.append(sim_score)

        # 如果有相似问题，取主问题和相似问题中的最高分
        if similar_scores:
            return max([main_similarity] + similar_scores)
        else:
            return main_similarity

    def _calculate_text_similarity(self, query, question_text):
        """计算两个文本的相似度"""
        # 提取查询的关键词
        query_keywords = self._extract_keywords(query)
        question_keywords = self._extract_keywords(question_text)

        # 计算关键词重合度
        if not query_keywords or not question_keywords:
            keyword_similarity = 0
        else:
            # 计算词汇重合度
            common_words = set(query_keywords).intersection(set(question_keywords))
            keyword_similarity = len(common_words) / max(
                len(query_keywords), len(question_keywords)
            )

        # 计算字符串相似度
        string_similarity = difflib.SequenceMatcher(None, query, question_text).ratio()

        # 加权平均
        return 0.7 * keyword_similarity + 0.3 * string_similarity

    def find_best_answer(self, query, threshold=0.3, category=None, record_stats=True):
        """查找最匹配的答案

        Args:
            query: 用户问题
            threshold: 匹配阈值
            category: 限定问题类别
            record_stats: 是否记录统计数据

        Returns:
            如果找到匹配的回答，返回答案字符串和问题ID
            如果没有找到，返回None和None
        """
        if record_stats:
            self.qa_data["stats"]["total_queries"] += 1

        # 如果没有问题，直接返回None
        if not self.qa_data["questions"]:
            self._save_data()
            return None, None

        # 筛选问题
        questions_to_search = self.qa_data["questions"]
        if category:
            # 如果指定了分类，只搜索该分类下的问题
            if category in self.qa_data["categories"]:
                category_qa_ids = self.qa_data["categories"][category]
                questions_to_search = [
                    q for q in self.qa_data["questions"] if q["id"] in category_qa_ids
                ]

        # 计算相似度
        similarities = []
        for q in questions_to_search:
            sim_score = self._calculate_similarity(query, q)
            similarities.append((q, sim_score))

        # 获取最佳匹配
        if not similarities:
            self._save_data()
            return None, None

        best_match = max(similarities, key=lambda x: x[1])

        # 如果相似度超过阈值，返回答案
        if best_match[1] >= threshold:
            if record_stats:
                self.qa_data["stats"]["matched_queries"] += 1

            self._save_data()
            return best_match[0]["answer"], best_match[0]["id"]

        self._save_data()
        return None, None

    def record_feedback(self, qa_id, is_helpful):
        """记录用户反馈"""
        if str(qa_id) not in self.qa_data["feedback"]:
            self.qa_data["feedback"][str(qa_id)] = {"helpful": 0, "not_helpful": 0}

        if is_helpful:
            self.qa_data["feedback"][str(qa_id)]["helpful"] += 1
        else:
            self.qa_data["feedback"][str(qa_id)]["not_helpful"] += 1

        self._save_data()

    def get_qa_by_id(self, qa_id):
        """根据ID获取问答对"""
        for item in self.qa_data["questions"]:
            if item["id"] == qa_id:
                return item
        return None

    def get_all_qa(self, category=None):
        """获取所有问答对，可选按分类筛选"""
        if category:
            if category in self.qa_data["categories"]:
                category_qa_ids = self.qa_data["categories"][category]
                return [
                    q for q in self.qa_data["questions"] if q["id"] in category_qa_ids
                ]
            return []
        else:
            return self.qa_data["questions"]

    def get_all_categories(self):
        """获取所有分类"""
        return list(self.qa_data["categories"].keys())

    def get_stats(self):
        """获取统计数据"""
        return self.qa_data["stats"]


# 测试代码
if __name__ == "__main__":
    qa = QASystemAdvanced()

    # 添加问答对
    qa.add_qa("如何重启系统?", "点击开始菜单，选择重启选项。", category="电脑问题")
    qa.add_qa("群规是什么?", "请大家互相尊重，不要发广告。", category="群管理")

    # 添加相似问题
    qa.add_similar_question(1, "怎么重新启动电脑?")
    qa.add_similar_question(1, "电脑死机了怎么重启?")

    # 测试查询
    test_queries = ["如何重启我的电脑?", "群规有哪些?", "怎么关机?"]

    for query in test_queries:
        answer, qa_id = qa.find_best_answer(query)
        print(f"问题: {query}")
        print(f"回答: {answer if answer else '抱歉，我不知道答案'}")

        if qa_id:
            # 模拟用户反馈
            qa.record_feedback(qa_id, True)

        print()
