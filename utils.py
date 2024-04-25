import os
import random
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

import aiohttp


def generate_date_list(start_date: str = "2002-06-14", end_date: str = "-1") -> [str]:
    if end_date == "-1":
        # Get the current date
        current_date = datetime.now()

        # Format the date
        end_date = current_date.strftime('%Y-%m-%d')

    # parse the start_date
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Initialize an empty list to hold the date strings
    date_list = []

    # Initialize the current date to start date
    current_date = start_date

    # Loop until current date is greater than end date
    while current_date <= end_date:
        # Append current date string to the list
        date_list.append(current_date.strftime('%Y-%m-%d'))

        # Increment the current date by one day
        current_date += timedelta(days=1)

    return date_list


def get_max_page(text: str) -> [str]:
    pattern = r'page=\d+'
    # Use the findall() function to extract all occurrences of the pattern
    matches = re.findall(pattern, text)

    # Print the extracted matches
    # results = set()
    # for match in matches:
    #     # print(match)
    #     results.add(match.replace("page=", ""))
    # results = sorted(list(results))
    # return int(results[-1])
    # print(results)
    results = set()
    for match in matches:
        # print(match)
        results.add(match)
    results = sorted(list(results))
    # print(results)
    return results


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.96 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
]


async def download_file(url: str, destination: str) -> str:
    print(f">>> 下载: {url},保存为: {destination}")
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    try:
        s = None
        async with aiohttp.ClientSession() as session:
            s = session
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                with open(destination, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

                print(f'>>> Download completed: {destination}')
                return destination

    except Exception as e:
        await s.close()
        print(f">>> 下载文件失败: {e}")
        return ""


def get_filename_from_url(url: str) -> str:
    # Parse the URL to get the path part
    parsed_url = urlparse(url)
    # Use os.path.basename to get the filename part from the path
    file_name = os.path.basename(parsed_url.path)
    return file_name


def clean_img_folder(img_folder: str):
    # Define the image file extensions to search for
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']

    # Walk through the directory
    for root, dirs, files in os.walk(img_folder):
        for file in files:
            # Check if the file extension is in our list of image extensions
            if any(file.lower().endswith(ext) for ext in image_extensions):
                file_path = os.path.join(root, file)
                try:
                    # Remove the image file
                    os.remove(file_path)
                    print(f">>> Deleted file: {file_path}")
                except OSError as e:
                    # If error occurs during file deletion, print the message
                    print(f">>> Error: {e.strerror} while deleting file {file_path}")


# cid 转换为dvd id
def convert_cid2code(cid: str) -> str:
    letter = re.sub(r'[0-9]', '', cid)
    number_part = re.sub(r'[a-zA-Z]', '', cid)
    formatted_string = f"{letter}-{int(number_part):03d}"
    return formatted_string


SPECIAL_CHARS = [
    '\\',
    '_',
    '*',
    '[',
    ']',
    '(',
    ')',
    '~',
    '`',
    '>',
    '<',
    '&',
    '#',
    '+',
    '-',
    '=',
    '|',
    '{',
    '}',
    '.',
    '!'
]


def clean_str_for_tg(data_str: str) -> str:
    for char in SPECIAL_CHARS:
        data_str = data_str.replace(char, f'\\{char}')
    return data_str


if __name__ == '__main__':
    # date_list = generate_date_list(end_date='2004-02-01')
    # print(date_list)
    # clean_img_folder("imgs")
    tg = clean_str_for_tg('[abc] (nihao).')
    print(tg)
