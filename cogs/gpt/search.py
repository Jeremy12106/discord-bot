import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from loguru import logger

# 讀取 API 金鑰與 CSE ID
load_dotenv(override=True)
MY_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
MY_CSE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

def google_search(query, num_results=5):
    num_results = min(num_results, 5)  # 限制最大 10 筆
    logger.info(f"[搜尋] Google 關鍵字搜尋：{query}")

    try:
        service = build("customsearch", "v1", developerKey=MY_API_KEY)
        res = service.cse().list(q=query, cx=MY_CSE_ID, num=num_results).execute()
        results = res.get('items', [])
    except Exception as e:
        logger.error(f"[搜尋] 發生錯誤: {e}")
        results = []

    search_results = "\n\n".join([
        f"搜尋結果 {idx+1}：\n"
        f"標題: {result.get('title', '無標題')}\n"
        f"摘要: {result.get('snippet', '無摘要')}\n"
        f"內容: {truncate_text(result.get('pagemap', {}).get('metatags', [{}])[0].get('og:description', '無內容'))}\n"
        for idx, result in enumerate(results[:num_results])
    ])

    if results:
        first_result = results[0]
        logger.debug(f"[搜尋] 第一個搜尋結果:\n"
                     f"標題: {first_result.get('title', '無標題')}\n"
                     f"摘要: {first_result.get('snippet', '無摘要')}\n"
                     f"內容: {truncate_text(first_result.get('pagemap', {}).get('metatags', [{}])[0].get('og:description', '無內容'))}")
    else:
        logger.info("[搜尋] 未找到相關搜尋結果")
    
    return search_results

def truncate_text(text, length=256):
    """ 截短過長文字，避免內容過長 """
    return text[:length] + "..." if len(text) > length else text

# 測試搜尋
if __name__ == "__main__":
    query = "台中氣爆"
    results = google_search(query)
    print(results)
