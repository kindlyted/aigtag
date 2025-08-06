from openai import OpenAI
import os
import base64

def invoke_qwen(prompt_path, user_input, MODEL_NAME='deepseek-v3'):
    client = OpenAI(
        api_key=os.getenv('API_KEY_QWEN'),
        base_url=os.getenv('URL_QWEN'), 
    )
    print("大模型工作中，请稍等片刻")
    with open(prompt_path, 'r', encoding='utf-8') as file:
        system_prompt = file.read()
    print("系统提示词长度:", len(system_prompt))

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,   
            messages=[
                {"role": "system", "content": system_prompt}, 
                {"role": "user", "content": user_input}
            ],
            stream=False,
            temperature=0.6
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        print("提示", e)
        answer = "敏感词censored by QWEN"

    return answer

def invoke_qwen_with_picture(image_path, prompt_path, user_input="图中是什么物体?", MODEL_NAME='qwen-vl-max-latest'):
    client = OpenAI(
        api_key=os.getenv('API_KEY_QWEN'),
        base_url=os.getenv('URL_QWEN'), 
    )
    print("大模型工作中，请稍等片刻")
    with open(prompt_path, 'r', encoding='utf-8') as file:
        system_prompt = file.read()
    print("系统提示词长度:", len(system_prompt))
    
    with open(image_path, "rb") as image_file:
        picture = base64.b64encode(image_file.read()).decode("utf-8")
    
    # 获取文件扩展名并转换为小写
    file_ext = os.path.splitext(image_path)[1].lower()
    
    # 定义扩展名到MIME类型的映射
    EXT_TO_MIME = {
        '.bmp': 'bmp',
        '.jpe': 'jpeg',
        '.jpeg': 'jpeg',
        '.jpg': 'jpeg',
        '.png': 'png',
        '.tif': 'tiff',
        '.tiff': 'tiff',
        '.webp': 'webp',
        '.heic': 'heic'
    }
    
    # 获取对应的MIME类型，默认为jpeg
    picture_type = EXT_TO_MIME.get(file_ext, 'jpeg')

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,   
            messages=[
                {"role": "system", "content": [{"type":"text","text": system_prompt}]},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/{picture_type};base64,{picture}"}}, 
                    # {"type": "text", "text": user_input},
                ]},
            ],
            response_format={'type': 'json_object'},
            stream=False,
            temperature=0.6
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        print("提示", e)
        answer = "敏感词censored by QWEN"

    return answer

