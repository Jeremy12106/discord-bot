from loguru import logger
from service.google_search_api import build_google_search_service, execute_google_search

def google_search(query, num_results=5):
    num_results = min(num_results, 5)
    logger.info(f"[搜尋] Google 關鍵字搜尋：{query}")

    try:
        service = build_google_search_service()
        res = execute_google_search(service, query, num_results)
        results = res.get('items', [])
    except Exception as e:
        logger.error(f"[搜尋] 發生錯誤: {e}")
        results = []

    search_results = "\n\n".join([
        f"搜尋結果 {idx+1}：\n"
        f"標題: {result.get('title', '無標題')}\n"
        f"連結: {result.get('link', '無連結')}\n"
        f"摘要: {result.get('snippet', '無摘要')}\n"
        f"內容: {truncate_text(result.get('pagemap', {}).get('metatags', [{}])[0].get('og:description', '無內容'))}\n"
        for idx, result in enumerate(results[:num_results])
    ])

    if results:
        first_result = results[0]
        logger.debug(f"[搜尋] 第一個搜尋結果:\n"
                     f"標題: {first_result.get('title', '無標題')}\n"
                     f"連結: {first_result.get('link', '無連結')}\n"
                     f"摘要: {first_result.get('snippet', '無摘要')}\n"
                     f"內容: {truncate_text(first_result.get('pagemap', {}).get('metatags', [{}])[0].get('og:description', '無內容'))}")
    else:
        logger.info("[搜尋] 未找到相關搜尋結果")
    
    return search_results

def truncate_text(text, length=256):
    return text[:length] + "..." if len(text) > length else text