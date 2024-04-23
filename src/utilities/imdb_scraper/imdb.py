import asyncio
import json
import re

from PyMovieDb import IMDB
from fastapi import HTTPException

from src.models.db.movie import Movie
imdb = IMDB()
async def async_get_by_id(imdb_url: str):
    loop = asyncio.get_running_loop()
    # 在线程池中运行同步函数，避免阻塞事件循环
    try:
        json_result = await loop.run_in_executor(None, imdb.get, imdb_url)
        result = json.loads(json_result)
        result['duration'] = parse_iso_duration(result.get('duration')) if result.get('duration') else None
    except Exception as e:
        print(e)
        raise HTTPException(status_code=404, detail="Movie not found")
    return result


def parse_iso_duration(duration):
    # Regex to find hours (H) and minutes (M) in ISO 8601 duration strings
    pattern = re.compile(r'PT(\d+H)?(\d+M)?')
    matches = pattern.match(duration)
    hours = minutes = 0
    if matches:
        hours_part = matches.group(1)
        minutes_part = matches.group(2)

        if hours_part:
            hours = int(hours_part[:-1])  # Remove the 'H' and convert to int
        if minutes_part:
            minutes = int(minutes_part[:-1])  # Remove the 'M' and convert to int

    total_minutes = hours * 60 + minutes
    return total_minutes
async def main():
    movie = await async_get_by_id('https://www.imdb.com/title/tt16426418/?ref_=hm_inth_tt_i_5')
    print(movie.title)

if __name__ == '__main__':
    asyncio.run(main())
