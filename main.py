import streamlit as st
from langchain.memory import ConversationBufferMemory
import traceback  # 用于捕获异常

from utils import get_chat_response

# 页面配置（增强用户体验）
st.set_page_config(page_title="克隆ChatGPT", page_icon="💬")

st.title("💬 克隆ChatGPT")

# 侧边栏：API密钥持久化（存入session_state，避免重复输入）
with st.sidebar:
    # 从session_state读取已保存的密钥（默认空）
    saved_api_key = st.session_state.get("openai_api_key", "")
    # 输入框默认显示已保存的密钥
    openai_api_key = st.text_input(
        "请输入OpenAI API Key：",
        value=saved_api_key,
        type="password"
    )
    # 实时更新session_state中的密钥
    if openai_api_key != saved_api_key:
        st.session_state["openai_api_key"] = openai_api_key
    st.markdown("[获取OpenAI API key](https://platform.openai.com/account/api-keys)")

# 初始化session_state（确保记忆和消息同步）
if "memory" not in st.session_state:
    # 初始化记忆（return_messages=True：返回消息对象而非字符串）
    st.session_state["memory"] = ConversationBufferMemory(return_messages=True)
    # 初始化消息列表（包含AI欢迎语）
    st.session_state["messages"] = [{"role": "ai", "content": "你好，我是你的AI助手，有什么可以帮你的吗？"}]
    # 关键：将初始欢迎语同步到记忆（否则记忆中没有这条消息）
    st.session_state["memory"].save_context(
        inputs={"human": ""},  # 初始无用户输入
        outputs={"ai": "你好，我是你的AI助手，有什么可以帮你的吗？"}
    )

# 优化渲染：用固定容器显示历史消息，减少DOM冲突
chat_container = st.container()  # 固定容器，避免每次重绘整个区域
with chat_container:
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# 处理用户输入
prompt = st.chat_input("请输入你的问题...")
if prompt:
    # 检查API密钥是否存在
    if not openai_api_key:
        st.info("请在侧边栏输入你的OpenAI API Key")
        st.stop()

    # 添加用户消息到列表，并在固定容器中显示（避免重绘全部消息）
    st.session_state["messages"].append({"role": "human", "content": prompt})
    with chat_container:
        with st.chat_message("human"):
            st.write(prompt)

    # 调用AI接口（带异常处理，避免崩溃）
    try:
        with st.spinner("AI正在思考中，请稍等..."):
            # 调用工具函数获取回复（需确保get_chat_response使用memory中的历史）
            response = get_chat_response(
                prompt=prompt,
                memory=st.session_state["memory"],
                openai_api_key=openai_api_key
            )

        # 关键：将当前对话（用户输入+AI回复）存入记忆，确保上下文连贯
        st.session_state["memory"].save_context(
            inputs={"human": prompt},
            outputs={"ai": response}
        )

        # 添加AI回复到消息列表，并在固定容器中显示
        ai_msg = {"role": "ai", "content": response}
        st.session_state["messages"].append(ai_msg)
        with chat_container:
            with st.chat_message("ai"):
                st.write(response)

    except Exception as e:
        # 捕获异常并显示友好提示
        st.error(f"出错了：{str(e)}")
        # 调试用：显示详细错误日志（可注释掉）
        st.text(traceback.format_exc())

