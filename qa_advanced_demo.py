from qa_system_advanced import QASystemAdvanced
import json


def main():
    qa_system = QASystemAdvanced()

    print("欢迎使用高级问答系统!")
    print("1. 输入问题获取回答")
    print("2. 添加新的问答对")
    print("3. 添加相似问题表述")
    print("4. 删除问答对")
    print("5. 查看所有问答对")
    print("6. 查看问答系统统计数据")
    print("7. 按分类查看问答对")
    print("8. 批量添加问答对")
    print("9. 批量删除问答对")
    print("0. 退出程序")

    while True:
        choice = input("\n请选择功能 (0-9): ")

        if choice == "0":
            print("感谢使用，再见!")
            break

        elif choice == "1":
            query = input("请输入您的问题: ")

            # 检查是否要指定分类
            use_category = input("是否限定问题分类? (y/n): ").lower() == "y"
            category = None

            if use_category:
                categories = qa_system.get_all_categories()
                if not categories:
                    print("当前没有分类。")
                else:
                    print("可用分类:")
                    for i, cat in enumerate(categories, 1):
                        print(f"{i}. {cat}")

                    cat_choice = input("请选择分类编号 (直接回车跳过): ")
                    if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                        category = categories[int(cat_choice) - 1]

            answer, qa_id = qa_system.find_best_answer(query, category=category)

            if answer:
                print(f"回答: {answer}")

                # 记录用户反馈
                feedback = input("这个回答对您有帮助吗? (y/n): ").lower()
                is_helpful = feedback == "y"
                qa_system.record_feedback(qa_id, is_helpful)
            else:
                print("抱歉，没有找到匹配的答案。")

        elif choice == "2":
            question = input("请输入问题: ")
            answer = input("请输入答案: ")

            # 检查是否要添加分类
            add_category = input("是否添加分类? (y/n): ").lower() == "y"
            category = None

            if add_category:
                categories = qa_system.get_all_categories()
                if categories:
                    print("现有分类:")
                    for i, cat in enumerate(categories, 1):
                        print(f"{i}. {cat}")

                    cat_choice = input("请选择分类编号，或输入新分类名称: ")
                    if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                        category = categories[int(cat_choice) - 1]
                    else:
                        category = cat_choice
                else:
                    category = input("请输入分类名称: ")

            qa_id = qa_system.add_qa(question, answer, category=category)
            print(f"已添加问答对，ID: {qa_id}")

        elif choice == "3":
            qa_list = qa_system.get_all_qa()
            if not qa_list:
                print("当前没有问答对。")
                continue

            print("当前所有问答对:")
            for qa in qa_list:
                print(f"ID: {qa['id']}, 问题: {qa['question']}")

            qa_id = input("请输入要添加相似问题的问答对ID: ")
            try:
                qa_id = int(qa_id)
                qa_item = qa_system.get_qa_by_id(qa_id)

                if qa_item:
                    similar_question = input("请输入相似问题表述: ")
                    if qa_system.add_similar_question(qa_id, similar_question):
                        print(f"已为ID {qa_id} 添加相似问题")
                    else:
                        print("添加失败")
                else:
                    print(f"未找到ID为 {qa_id} 的问答对")
            except ValueError:
                print("ID必须是数字")

        elif choice == "4":
            qa_list = qa_system.get_all_qa()
            if not qa_list:
                print("当前没有问答对。")
                continue

            print("当前所有问答对:")
            for qa in qa_list:
                print(f"ID: {qa['id']}, 问题: {qa['question']}")

            qa_id = input("请输入要删除的问答对ID: ")
            try:
                qa_id = int(qa_id)
                if qa_system.delete_qa(qa_id):
                    print(f"已删除ID为 {qa_id} 的问答对")
                else:
                    print(f"未找到ID为 {qa_id} 的问答对")
            except ValueError:
                print("ID必须是数字")

        elif choice == "5":
            qa_list = qa_system.get_all_qa()
            if not qa_list:
                print("当前没有问答对。")
                continue

            print("所有问答对:")
            for qa in qa_list:
                print(f"ID: {qa['id']}")
                print(f"问题: {qa['question']}")
                print(f"答案: {qa['answer']}")
                print(f"分类: {qa['category'] if qa.get('category') else '无分类'}")
                print(f"关键词: {', '.join(qa['keywords'])}")

                if qa.get("similar_questions"):
                    print("相似问题:")
                    for i, sq in enumerate(qa["similar_questions"], 1):
                        print(f"  {i}. {sq['text']}")

                # 显示反馈数据
                qa_id_str = str(qa["id"])
                if qa_id_str in qa_system.qa_data["feedback"]:
                    feedback = qa_system.qa_data["feedback"][qa_id_str]
                    print(
                        f"用户反馈: 有帮助: {feedback['helpful']}, 无帮助: {feedback['not_helpful']}"
                    )

                print("-" * 30)

        elif choice == "6":
            stats = qa_system.get_stats()
            print("问答系统统计数据:")
            print(f"总查询次数: {stats['total_queries']}")
            print(f"成功匹配次数: {stats['matched_queries']}")

            if stats["total_queries"] > 0:
                match_rate = (stats["matched_queries"] / stats["total_queries"]) * 100
                print(f"匹配成功率: {match_rate:.2f}%")

            # 显示反馈统计
            feedback = qa_system.qa_data.get("feedback", {})
            if feedback:
                total_helpful = sum(item["helpful"] for item in feedback.values())
                total_not_helpful = sum(
                    item["not_helpful"] for item in feedback.values()
                )
                total_feedback = total_helpful + total_not_helpful

                print(f"总反馈次数: {total_feedback}")
                if total_feedback > 0:
                    helpful_rate = (total_helpful / total_feedback) * 100
                    print(f"有帮助反馈率: {helpful_rate:.2f}%")

        elif choice == "7":
            categories = qa_system.get_all_categories()
            if not categories:
                print("当前没有分类。")
                continue

            print("可用分类:")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")

            cat_choice = input("请选择分类编号: ")
            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories):
                category = categories[int(cat_choice) - 1]
                qa_list = qa_system.get_all_qa(category=category)

                if not qa_list:
                    print(f"分类 '{category}' 下没有问答对。")
                    continue

                print(f"分类 '{category}' 下的问答对:")
                for qa in qa_list:
                    print(f"ID: {qa['id']}")
                    print(f"问题: {qa['question']}")
                    print(f"答案: {qa['answer']}")
                    print("-" * 30)
            else:
                print("无效的分类编号")

        elif choice == "8":
            print("批量添加问答对")
            print("请选择输入方式：")
            print("1. 手动输入多个问答对")
            print("2. 从JSON文件导入")

            input_choice = input("请选择 (1-2): ")

            if input_choice == "1":
                qa_list = []
                while True:
                    question = input("请输入问题 (输入空行结束): ")
                    if not question:
                        break

                    answer = input("请输入答案: ")

                    # 检查是否要添加分类
                    add_category = input("是否添加分类? (y/n): ").lower() == "y"
                    category = None

                    if add_category:
                        categories = qa_system.get_all_categories()
                        if categories:
                            print("现有分类:")
                            for i, cat in enumerate(categories, 1):
                                print(f"{i}. {cat}")

                            cat_choice = input("请选择分类编号，或输入新分类名称: ")
                            if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(
                                categories
                            ):
                                category = categories[int(cat_choice) - 1]
                            else:
                                category = cat_choice
                        else:
                            category = input("请输入分类名称: ")

                    qa_item = {"question": question, "answer": answer}
                    if category:
                        qa_item["category"] = category

                    qa_list.append(qa_item)
                    print(f"已添加问答对，当前共 {len(qa_list)} 个")

                if qa_list:
                    added_ids = qa_system.batch_add_qa(qa_list)
                    print(f"成功添加 {len(added_ids)} 个问答对")

            elif input_choice == "2":
                file_path = input("请输入JSON文件路径: ")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        qa_list = json.load(f)

                    if isinstance(qa_list, list):
                        added_ids = qa_system.batch_add_qa(qa_list)
                        print(f"成功添加 {len(added_ids)} 个问答对")
                    else:
                        print("JSON文件格式不正确，应为问答对数组")
                except Exception as e:
                    print(f"导入失败: {str(e)}")

            else:
                print("无效的选择")

        elif choice == "9":
            qa_list = qa_system.get_all_qa()
            if not qa_list:
                print("当前没有问答对。")
                continue

            print("当前所有问答对:")
            for qa in qa_list:
                print(f"ID: {qa['id']}, 问题: {qa['question']}")

            print("\n批量删除问答对")
            print("请输入要删除的问答对ID，多个ID之间用逗号分隔")
            id_input = input("要删除的ID: ")

            try:
                id_list = [
                    int(id_str.strip())
                    for id_str in id_input.split(",")
                    if id_str.strip()
                ]

                if id_list:
                    deleted_ids = qa_system.batch_delete_qa(id_list)
                    print(f"成功删除 {len(deleted_ids)} 个问答对")
                    if len(deleted_ids) < len(id_list):
                        not_found = set(id_list) - set(deleted_ids)
                        print(f"未找到ID: {', '.join(map(str, not_found))}")
                else:
                    print("未输入有效的ID")

            except ValueError:
                print("ID格式不正确，请输入数字ID，并用逗号分隔")

        else:
            print("无效的选项，请重新选择")


if __name__ == "__main__":
    main()
