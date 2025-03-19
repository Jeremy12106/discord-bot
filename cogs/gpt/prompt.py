
def get_prompt(system_prompt:str, user_nick:str, text:str, personality:str=None, search_results:str=None, memory:str=None) -> str:

    prompt = f"""
                [系統設定]
                \n{system_prompt}\n
                """

    if personality is not None:
        prompt += f"""
                    \n[個性設定]
                    \n{personality}\n
                    """
        
    if memory is not None:
        prompt += f"""
                    \n[歷史對話] （最舊的在上，最新的在下）
                    \n{memory}\n
                    """
    
    if search_results is not None:
        prompt += f"""
                    \n[搜尋結果]
                    \n{search_results}\n
                    """

    prompt += f"""
                \n[使用者輸入]
                \n{user_nick}：{text}
                """
    return prompt