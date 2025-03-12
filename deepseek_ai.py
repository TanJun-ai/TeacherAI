from openai import OpenAI
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os


# 设置 Matplotlib 支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为 SimHei
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 设置 OpenAI API 密钥
# openai.api_key = "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"  # 替换为你的 OpenAI API Key
client = OpenAI(api_key="sk-539ed55e6dd84c50a66c01967ba68b62", base_url="https://api.deepseek.com")

# '''=======================1、智能答疑功能模块=========================='''
# 智能答疑功能
def ask_question(question):

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for computer engineering students."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

# '''=======================2、代码分析功能模块=========================='''
# 代码分析功能
def analyze_code_with_openai(code, language="python"):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个代码分析助手，可以检测代码中的错误、警告和风格问题，并给出代码质量评分（0-100分）。"},
                {"role": "user", "content": f"请分析以下 {language} 代码，列出所有问题，并给出代码质量评分：\n\n{code}"}
            ]
        )
        analysis_result = response.choices[0].message.content
        return {"analysis": analysis_result}
    except Exception as e:
        return {"error": f"请求 OpenAI API 时出错: {str(e)}"}

# 解析分析结果
def parse_analysis_result(analysis_result):
    issues = {
        "错误": 0,
        "警告": 0,
        "风格问题": 0
    }
    details = []
    score = 100  # 默认评分

    # 解析 OpenAI 返回的分析结果
    for line in analysis_result.split("\n"):
        if "错误" in line:
            issues["错误"] += 1
            details.append({"type": "错误", "message": line})
            score -= 5  # 每个错误扣 5 分
        elif "警告" in line:
            issues["警告"] += 1
            details.append({"type": "警告", "message": line})
            score -= 2  # 每个警告扣 2 分
        elif "风格问题" in line:
            issues["风格问题"] += 1
            details.append({"type": "风格问题", "message": line})
            score -= 1  # 每个风格问题扣 1 分
        elif "评分" in line:
            # 提取评分
            try:
                score = int(line.split(":")[1].strip())
            except (IndexError, ValueError):
                pass

    # 确保评分在 0-100 之间
    score = max(0, min(100, score))
    return issues, details, score

# 可视化分析结果
def visualize_analysis(issues, details, score):
    # 显示代码质量评分
    st.write("### 代码质量评分")
    st.metric("评分", f"{score}/100")

    # 显示问题分布
    st.write("### 问题分布")
    fig, ax = plt.subplots()
    ax.bar(issues.keys(), issues.values(), color=['red', 'orange', 'yellow'])
    ax.set_ylabel("数量")
    ax.set_title("代码问题分布")
    st.pyplot(fig)

    # 显示详细问题列表
    st.write("### 详细问题")
    for detail in details:
        st.write(f"- **类型**: {detail['type']}, **消息**: {detail['message']}")

# '''======================3、添加学习记录功能模块=========================='''
# 初始化数据库（使用 CSV 文件模拟）
def init_db():
    if 'db' not in st.session_state:
        if os.path.exists("student_progress.csv"):
            st.session_state.db = pd.read_csv("student_progress.csv")
        else:
            # 示例数据
            st.session_state.db = pd.DataFrame({
                "学生姓名": ["张三", "李四", "王五", "赵六"],
                "任务名称": ["任务1", "任务1", "任务1", "任务1"],
                "分数": [80, 90, 70, 85],
                "完成时间": ["2023-10-01", "2024-10-02", "2025-2-03", "2025-10-04"]
            })
            # 添加更多任务数据
            additional_data = {
                "学生姓名": ["张三", "李四", "王五", "赵六", "陈七"],
                "任务名称": ["任务2", "任务2", "任务2", "任务2", "任务2"],
                "分数": [85, 95, 75, 90, 65],
                "完成时间": ["2023-10-06", "2024-10-07", "2025-2-08", "2025-10-09", "2025-10-10"]
            }
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame(additional_data)], ignore_index=True)
            save_db()

# 保存数据库到文件
def save_db():
    st.session_state.db.to_csv("./student_progress.csv", index=False)

# 添加学习记录
def add_progress(student_name, task_name, score):
    new_entry = {
        "学生姓名": student_name,
        "任务名称": task_name,
        "分数": score,
        "完成时间": pd.Timestamp.now().strftime("%Y-%m-%d")  # 只保留日期部分
    }
    st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_entry])], ignore_index=True)
    save_db()
    st.success(f"已添加 {student_name} 的任务 {task_name} 的分数: {score}")

# '''=======================4、统计学习进度功能模块=========================='''
# 计算学习进度
def calculate_progress():
    if st.session_state.db.empty:
        return None

    # 获取所有任务名称
    tasks = st.session_state.db["任务名称"].unique()
    total_tasks = len(tasks)

    # 计算每个学生的完成进度
    progress_data = []
    for student in st.session_state.db["学生姓名"].unique():
        completed_tasks = st.session_state.db[st.session_state.db["学生姓名"] == student]["任务名称"].nunique()
        progress = completed_tasks / total_tasks
        progress_data.append({"学生姓名": student, "完成进度": progress})

    return pd.DataFrame(progress_data), total_tasks

# 可视化学习进度统计结果
def visualize_progress_stats(progress_df, total_tasks):
    if progress_df is None:
        st.warning("暂无学习进度数据。")
        return

    # 统计不同进度区间的人数
    progress_stats = {
        "0%": len(progress_df[progress_df["完成进度"] == 0]),
        "25%": len(progress_df[(progress_df["完成进度"] > 0) & (progress_df["完成进度"] <= 0.25)]),
        "50%": len(progress_df[(progress_df["完成进度"] > 0.25) & (progress_df["完成进度"] <= 0.5)]),
        "75%": len(progress_df[(progress_df["完成进度"] > 0.5) & (progress_df["完成进度"] <= 0.75)]),
        "100%": len(progress_df[(progress_df["完成进度"] > 0.75)])
    }

    # 显示统计结果
    st.write("### 学习进度统计")
    st.write(f"总任务数: {total_tasks}")
    st.write("#### 不同进度区间的人数")
    st.bar_chart(progress_stats)

    # 显示学生详细进度（所有信息在一张表格中）
    st.write("#### 学生详细进度")
    st.dataframe(st.session_state.db)

# '''======================5、批改报告功能模块=========================='''
# 调用 DeepSeek API 批改报告
def grade_report(report_text):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # 替换为 DeepSeek 的模型名称
            messages=[
                {"role": "system", "content": "你是一个批改实验报告助手，可以从实验报告的三个部分给出分数（0-100分）,"
                                              "三个部分包括：1、实验内容与要求（代码），2、实验结果（数据集展示和聚类结果），3、实验总结"},
                {"role": "user", "content": f"请分析以下实验报告，并给出评分和改进建议：\n\n{report_text}"}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return {"error": f"请求 DeepSeek API 时出错: {str(e)}"}

# Streamlit 应用界面
def main():
    st.title("计算机工程综合能力实训 AI 助手")
    st.sidebar.title("导航")
    choice = st.sidebar.radio("选择功能", ["智能答疑", "代码分析", "添加学习记录", "学习进度统计", "批改报告"])

    if choice == "智能答疑":
        st.header("智能答疑")
        question = st.text_input("请输入你的问题：")
        if st.button("提交"):
            if question:
                answer = ask_question(question)
                st.write("### 回答：")
                st.write(answer)
            else:
                st.warning("请输入问题。")

    elif choice == "代码分析":
        st.header("代码分析")
        language = st.selectbox("选择编程语言", ["python", "java", "cpp"])
        code = st.text_area("请输入你的代码：", height=200)
        if st.button("分析代码"):
            if code:
                analysis_result = analyze_code_with_openai(code, language)
                if "error" in analysis_result:
                    st.error(analysis_result["error"])
                else:
                    st.write("### 代码分析结果")
                    issues, details, score = parse_analysis_result(analysis_result["analysis"])
                    visualize_analysis(issues, details, score)
            else:
                st.warning("请输入代码。")

    elif choice == "添加学习记录":
        st.header("添加学习记录")
        student_name = st.text_input("学生姓名：")
        task_name = st.text_input("任务名称：", max_chars=100)
        score = st.number_input("分数：", min_value=0, max_value=100, value=80)
        if st.button("添加记录"):
            print(student_name)
            print(task_name)
            if student_name and task_name:
                add_progress(student_name, task_name, score)
            else:
                st.warning("请输入学生姓名和任务名称")


    elif choice == "学习进度统计":
        st.header("学习进度统计")
        progress_df, total_tasks = calculate_progress()
        visualize_progress_stats(progress_df, total_tasks)


    elif choice == "批改报告":
        st.header("批改报告")
        uploaded_file = st.file_uploader("上传实验报告文件（支持 .txt 或 .docx）", type=["txt", "docx"])
        if uploaded_file is not None:
            # 读取文件内容
            if uploaded_file.type == "text/plain":
                report_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                import docx
                doc = docx.Document(uploaded_file)
                report_text = "\n".join([para.text for para in doc.paragraphs])
            else:
                st.error("不支持的文件格式！")
                return

            st.write("### 实验报告内容")
            st.write(report_text)

            # 调用 DeepSeek API 批改报告
            if st.button("批改报告"):
                result = grade_report(report_text)

                if "error" in result:
                    st.error(result["error"])
                    if "details" in result:
                        st.write("错误详情：", result["details"])
                else:
                    st.write("### 批改结果")
                    st.write(result)

# 运行应用
if __name__ == "__main__":
    init_db()
    main()
