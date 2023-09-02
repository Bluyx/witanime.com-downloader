import requests, os
from tqdm import tqdm
from urllib.parse import urlparse, urlunparse
from console import console

def tusfiles(client, url, saveAs):
    fileID = url.split(".com/")[1].split("/")[0]
    headers = {
        "authority": "tusfiles.com",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9,ar;q=0.8",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": "lang=english",
        "origin": "https://tusfiles.com",
        "referer": f"https://tusfiles.com/{fileID}",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
    data = {
        "op": "download2",
        "id": fileID,
        "rand": "",
        "referer": "",
        "method_free": "",
        "method_premium": "1"
    }
    response = client.post(f"https://tusfiles.com/{fileID}", headers=headers, data=data, allow_redirects=False, timeout_seconds=10, insecure_skip_verify=True)
    parsed_url = urlparse(response.headers["Location"])
    netloc = parsed_url.netloc.split(":")[0]
    modified_path = parsed_url.path.replace(" ", "%20")
    url = urlunparse((parsed_url.scheme, netloc, modified_path, parsed_url.params, parsed_url.query, parsed_url.fragment))
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("Content-Length", 0))
    with open(saveAs, "wb") as file:
        console.info(f"Downloading {saveAs} using Tusfiles")
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, ncols=100)
        for data in response.iter_content(chunk_size=512*1024):
            file.write(data)
            progress_bar.update(len(data))
    return True





