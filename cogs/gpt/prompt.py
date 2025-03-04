
def get_prompt(system_prompt:str, text:str, personality:str=None, search_results:str=None):

    prompt = f"{system_prompt}"

    if personality is not None:
        prompt += f"""
                    \n根據以下人物設定來回答使用者輸入。
                    \n{personality}\n
                    """
        
    if search_results is not None:
        prompt += f"""
                    \n根據以下參考資料提供回答。請務必使用參考資料中的資訊，避免使用未提供的其他知識：
                    \n參考資料：
                    \n{search_results}\n
                    """
    prompt += f"""
                \n使用者輸入：{text}
                """
    return prompt