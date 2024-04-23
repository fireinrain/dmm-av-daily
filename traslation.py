import time
import aiohttp
import asyncio


async def translate_single(text, source_lang, target_lang, session):
    if source_lang == target_lang:
        return target_lang, text

    url = "https://api.deeplx.org/translate"
    payload = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }

    start_time = time.time()
    async with session.post(url, json=payload) as response:
        print(f"翻译从 {source_lang} 至 {target_lang} 耗时: {time.time() - start_time}")
        if response.status != 200:
            print(f"翻译失败：{response.status}")
            raise Exception(f"翻译失败")

        result = await response.json()
        if result['code'] != 200:
            print(f"翻译失败：{result}")
            raise Exception(f"翻译失败")

        return target_lang, result['data']


async def translate_text(text, source_lang, target_langs) -> {}:
    result = {}
    async with aiohttp.ClientSession() as session:
        tasks = [translate_single(text, source_lang, target_lang, session) for target_lang in target_langs]
        for lang, text in await asyncio.gather(*tasks):
            result[lang] = text
    print(result)
    return result


if __name__ == '__main__':
    asyncio.run(translate_text("下着広告モデルズ カメラが覗いた裏側", 'JP', ['ZH']))
