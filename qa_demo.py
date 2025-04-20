from qa_system import QASystem
import json


def main():
    qa_system = QASystem()

    print("欢迎使用问答系统!")
    print("1. 输入问题获取回答")
    print("2. 添加新的问答对")
    print("3. 删除问答对")
    print("4. 查看所有问答对")
    print("5. 批量添加问答对")
    print("6. 批量删除问答对")
    print("0. 退出程序")

    while True:
        choice = input(
            "\n请选择功能 (0-6): \n"
            "1. 输入问题获取回答\n"
            "2. 添加新的问答对\n"
            "3. 删除问答对\n"
            "4. 查看所有问答对\n"
            "5. 批量添加问答对\n"
            "6. 批量删除问答对\n"
            "0. 退出程序\n"
        )

        if choice == "0":
            print("感谢使用，再见!")
            break

        elif choice == "1":
            query = input("请输入您的问题: ")
            answer = qa_system.find_best_answer(query)
            if answer:
                print(f"回答: {answer}")
            else:
                print("抱歉，没有找到匹配的答案。")

        elif choice == "2":
            question = input("请输入问题: ")
            answer = input("请输入答案: ")
            qa_id = qa_system.add_qa(question, answer)
            print(f"已添加问答对，ID: {qa_id}")

        elif choice == "3":
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

        elif choice == "4":
            qa_list = qa_system.get_all_qa()
            if not qa_list:
                print("当前没有问答对。")
                continue

            print("所有问答对:")
            for qa in qa_list:
                print(f"ID: {qa['id']}")
                print(f"问题: {qa['question']}")
                print(f"答案: {qa['answer']}")
                print(f"关键词: {', '.join(qa['keywords'])}")
                print("-" * 30)

        elif choice == "5":
            print("批量添加问答对")
            print("请选择输入方式：")
            print("1. 一次性输入所有问答对")
            print("2. 从JSON文件导入")

            input_choice = input("请选择 (1-2): ")

            if input_choice == "1":
                print("请一次性输入所有问答对，格式为：")
                print("问题1####答案1")
                print("问题2####答案2")
                print("...")
                print("使用'####'作为问题和答案的分隔符")
                print("输入空行完成添加")

                qa_list = []
                print("请输入所有问答对(输入空行结束):")
                while True:
                    line = input()
                    if not line:
                        break

                    parts = line.split("####")
                    if len(parts) == 2:
                        question, answer = parts
                        qa_list.append(
                            {"question": question.strip(), "answer": answer.strip()}
                        )
                    else:
                        print(f"格式错误: {line}，已跳过")

                if qa_list:
                    added_ids = qa_system.batch_add_qa(qa_list)
                    print(f"成功批量添加 {len(added_ids)} 个问答对")
                else:
                    print("未添加任何问答对")

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

        elif choice == "6":
            qa_list = qa_system.get_all_qa()
            if not qa_list:
                print("当前没有问答对。")
                continue

            print("当前所有问答对:")
            for qa in qa_list:
                print(f"ID: {qa['id']}, 问题: {qa['question']}")

            print("\n批量删除问答对")
            print("请一次性输入所有要删除的ID，以逗号分隔")
            print("例如: 1,3,5,7")
            id_input = input("要删除的ID: ")

            try:
                id_list = [
                    int(id_str.strip())
                    for id_str in id_input.split(",")
                    if id_str.strip()
                ]

                if id_list:
                    deleted_ids = qa_system.batch_delete_qa(id_list)
                    print(f"成功批量删除 {len(deleted_ids)} 个问答对")
                    if len(deleted_ids) < len(id_list):
                        not_found = set(id_list) - set(deleted_ids)
                        print(f"未找到的ID: {', '.join(map(str, not_found))}")
                else:
                    print("未输入有效的ID")

            except ValueError:
                print("ID格式不正确，请输入数字ID，并用逗号分隔")

        else:
            print("无效的选项，请重新选择")


if __name__ == "__main__":
    main()
