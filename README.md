# QQ 群问答系统

这是一个基于 JSON 存储的本地问答系统，可以用于自动回复 QQ 群中的常见问题。

## 特点

- 纯算法实现，无需模型训练
- 基于 JSON 本地存储问答对
- 支持添加、删除问答对
- 支持批量添加、批量删除问答对
- 基于关键词和字符串相似度的问题匹配算法
- 脱离 QQ 的独立版本，便于测试

## 安装依赖

```bash
pip install jieba
```

## 文件说明

- `qa_system.py`: 核心问答系统实现
- `qa_demo.py`: 命令行演示程序
- `qa_system_advanced.py`: 高级版本的问答系统实现，支持分类和用户反馈
- `qa_advanced_demo.py`: 高级版本的命令行演示程序

## 使用方法

1. 运行演示程序:

```bash
python qa_demo.py  # 基础版本
python qa_advanced_demo.py  # 高级版本
```

2. 功能说明:

   - 输入问题获取回答
   - 添加新的问答对
   - 删除问答对
   - 查看所有问答对
   - 批量添加问答对（手动输入或从 JSON 文件导入）
   - 批量删除问答对

3. 高级版本额外功能:
   - 问题分类管理
   - 添加相似问题表述
   - 用户反馈收集
   - 系统使用统计

## 批量操作说明

### 批量添加问答对

系统支持两种方式批量添加问答对：

1. 手动输入多个问答对
2. 从 JSON 文件导入

JSON 文件格式示例：

```json
[
  {
    "question": "如何重启系统?",
    "answer": "点击开始菜单，选择重启选项。",
    "category": "电脑问题"
  },
  {
    "question": "群规是什么?",
    "answer": "请大家互相尊重，不要发广告。"
  }
]
```

### 批量删除问答对

输入多个 ID，用逗号分隔，例如：`1,3,5`，系统将批量删除这些 ID 的问答对。

## 核心算法说明

系统使用两种方法计算问题相似度:

1. 关键词重合度: 使用 jieba 分词提取关键词，计算用户问题与存储问题的关键词重合度
2. 字符串相似度: 使用 difflib 计算整体字符串相似度

两种相似度按权重合并，默认为关键词重合度占 70%，字符串相似度占 30%。

## JSON 数据格式

```json
{
  "questions": [
    {
      "id": 1,
      "question": "如何使用这个问答系统?",
      "answer": "你可以问我任何问题，我会尽力回答!",
      "keywords": ["使用", "问答系统"]
    }
  ]
}
```

## 与 QQ 群集成

本系统提供了核心的问答匹配算法，可以轻松与 QQ 群机器人 API 集成。只需调用`find_best_answer`方法即可查找最匹配的答案。
