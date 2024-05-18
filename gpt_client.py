import os
import json
from openai import OpenAI

def initialize_gpt_client(api_key, base_url="https://api.deepseek.com"):
    return OpenAI(api_key=api_key, base_url=base_url)

def process_text(client, conversation_history, input_text, MAX_HISTORY_LENGTH=5):
    conversation_history.append({"role": "user", "content": input_text})
    if len(conversation_history) > MAX_HISTORY_LENGTH:
        conversation_history = conversation_history[-MAX_HISTORY_LENGTH:]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=conversation_history,
        stream=True  # 使用流式对话
    )
    
    ai_response_text = ""
    print("\rAI回复:", end="")
    for resp in response:
        content = resp.choices[0].delta.content
        ai_response_text += content
        print(content, end="")
    print()

    conversation_history.append({"role": "assistant", "content": ai_response_text})
    return ai_response_text

def main():
    # 获取当前脚本文件所在的绝对路径
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(dir_path, 'config.json')
    
    # 从配置文件加载配置
    with open(config_path, 'r') as file:
        config = json.load(file)
    
    # 初始化 GPT 客户端
    gpt_client = initialize_gpt_client(
        api_key=config['openai_api_key'],
        base_url=config['openai_base_url']
    )
    MAX_HISTORY_LENGTH = config.get('max_history_length', 5)
    conversation_history = []

    print("Enter 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        ai_response = process_text(gpt_client, conversation_history, user_input, MAX_HISTORY_LENGTH)

if __name__ == '__main__':
    main()
