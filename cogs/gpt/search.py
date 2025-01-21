from googlesearch import search
from loguru import logger

def google_search(query, num_results=5, region='tw', safe=None):
    logger.info(f"[搜尋] Google 關鍵字搜尋：{query}")
    try:
        search_results_list = list(search(query, num_results=num_results, region=region, safe=safe, advanced=True))
    except ValueError as e:
        logger.error(f"[搜尋] 發生錯誤: {e}")
        search_results_list = []
    search_results = "\n\n".join([
        f"搜尋結果 {idx+1}：\n"
        f"{result.title if result.title else '無標題'}\n"
        f"{result.description if result.description else '無摘要'}"
        for idx, result in enumerate(search_results_list[:num_results])
    ])
    if search_results_list:
        logger.debug(f'[搜尋] 搜尋結果:\n'
                    f'標題: {search_results_list[0].title}\n'
                    f'摘要: {search_results_list[0].description}')
    else:
        logger.info('[搜尋] 未找到相關搜尋結果')
    return search_results