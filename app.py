import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp

movie_title_query = input("Type a Title: ")
page = requests.get(f'https://torrentz2.nz/search?q={movie_title_query}')
soup = BeautifulSoup(page.content, 'html.parser')

container = soup.find('div', class_='results')
movie_elements = container.find_all('dl')

movies = []
magnets = []
for movie_element in movie_elements:
    title_node = movie_element.find('dt')
    title = title_node.find('a').text
    stats = movie_element.find('dd')
    size = stats.contents[2].text
    seeds = stats.contents[3].text
    leecher = stats.contents[4].text
    date = stats.contents[1].text

    magnet_node = stats.contents[0]
    magnet = magnet_node.find("a").get("href")

    movie = {
        'title': title,
        'size': size,
        'seeds': seeds,
        'leecher': leecher,
        'date': date,
        'magnets': magnets.append(magnet)
    }

    movies.append(movie)

api_key = "YOUR REAL-DEBRID API"
headers = {"Authorization": f"Bearer {api_key}"}

magnet_links = magnets
torrent_ids = []


async def add_magnet(link):
    payload = {"magnet": link}
    url = f"https://api.real-debrid.com/rest/1.0/torrents/addMagnet?"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, data=payload) as response:
            data = await response.json()
            torrent_id = data.get("id")
            torrent_ids.append(torrent_id)


async def select_files(magnet_id):
    payload = {"files": "all"}
    url = f"https://api.real-debrid.com/rest/1.0/torrents/selectFiles/{magnet_id}"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, data=payload) as response:
            pass


async def get_links(magnet_id):
    url = f"https://api.real-debrid.com/rest/1.0/torrents/info/{magnet_id}"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            data = await response.json()
            link = data["links"]
            return link


async def unrestrict(link):
    payload = {"link": link}
    url = "https://api.real-debrid.com/rest/1.0/unrestrict/link?"
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, data=payload) as response:
            data = await response.json()
            stream_link = data.get("download")
            if stream_link is not None:
                print(stream_link)


async def main():
    magnet_links = magnets
    tasks = []
    for link in magnet_links:
        tasks.append(asyncio.create_task(add_magnet(link)))
    await asyncio.gather(*tasks)

    tasks = []
    for magnet_id in torrent_ids:
        tasks.append(asyncio.create_task(select_files(magnet_id)))
    await asyncio.gather(*tasks)

    tasks = []
    for magnet_id in torrent_ids:
        tasks.append(asyncio.create_task(get_links(magnet_id)))
    links = await asyncio.gather(*tasks)

    tasks = []
    for link in links:
        tasks.append(asyncio.create_task(unrestrict(link)))
    await asyncio.gather(*tasks)


asyncio.run(main())
