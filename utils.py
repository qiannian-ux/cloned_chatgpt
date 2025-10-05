from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI


def get_chat_response(prompt, memory, openai_api_key):
    try:

        model = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key,
                           openai_api_base="https://api.aigc369.com/v1")
        chain = ConversationChain(llm=model, memory=memory)
        response = chain.invoke({"input": prompt})
    except Exception as e:
        response = {"response": "抱歉，你的密钥有误或已欠费，我不能回答你的问题"}
        return response["response"]
    return response["response"]



