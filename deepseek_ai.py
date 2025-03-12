import requests
import streamlit as st

# DeepSeek API 配置
# DEEPSEEK_API_URL = "https://api.deepseek.com"  # 替换为实际的 API URL
DEEPSEEK_API_URL = "https://api.deepseek.com/v1"  # 替换为实际的 API URL
DEEPSEEK_API_KEY = "sk-539ed55e6dd84c50a66c01967ba68b62"

# 智能答疑功能
def ask_question(question):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",  # 替换为 DeepSeek 提供的模型名称
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for computer engineering students."},
            {"role": "user", "content": question}
        ]
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Streamlit 应用界面
def main():
    st.title("计算机工程综合能力实训AI助手")
    st.sidebar.title("导航")
    choice = st.sidebar.radio("选择功能", ["智能答疑"])

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

# 运行应用
if __name__ == "__main__":
    main()