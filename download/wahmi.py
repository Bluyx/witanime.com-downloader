import requests, bs4
from tqdm import tqdm
from console import console


def wahmi(client, url, saveAs):
    headers = {
        'sec-ch-ua':'"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile':'?0',
        'sec-ch-ua-platform':'"Windows"',
        'upgrade-insecure-requests':'1',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-fetch-site':'cross-site',
        'sec-fetch-mode':'navigate',
        'sec-fetch-user':'?1',
        'sec-fetch-dest':'document',
        'referer':'https://witanime.one/',
        'accept-encoding':'gzip, deflate, br, zstd',
        'accept-language':'en-US,en;q=0.9',
    }

    res = client.get(url, headers=headers)
    headers = {
        'authority': 'surfe.pro',
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'content-length': '0',
        # 'cookie': '_ga=GA1.1.155189566.1710434532; cf_clearance=33cOGxH1zcnolEReuDp_6cJePo9qY.p4m3eEjpNZju8-1710542247-1.0.1.1-UQiR1zmG830H6rAeFo6Ou6THey9I2n_nyBpamn7Kv5DjX81SeD8zxu4jn_CJc9Z3z98GeSIYIrQGSMB3epEbEg; XSRF-TOKEN=eyJpdiI6IjVyYWlSVWZyVWRUSFNyVDRidFBkaVE9PSIsInZhbHVlIjoiUGNXbG11SXhkZUxtK1pzMTBHaTNod3BGZWxTcGVsTmdkcGhqZzUxeGQwQmRCY2pTTE1IOG41ZlNqZWMvMGZtMnc2NGFSMFRCS0NsWnlMR0MzL05adjVoMC90VWZHdE5Ed2ZYTjZFSDJkajBuR1RMRFpCSFc4UHFkb1JZTCtKZWMiLCJtYWMiOiI1NmU5NWMxMWFmN2VmY2RlNzk1YzA2MTM1MTdjZjViMWNhODBkZGU0NjdmZTNkOWMyNzdmMDE4MDhiMTA3YWJiIiwidGFnIjoiIn0%3D; filebob_user_session=eyJpdiI6IkRydjVhZFNyYVRRblk0NmkwYi83YlE9PSIsInZhbHVlIjoiVXVwYWNydVpaYmc1ZEJiKzcxempadjZieXNLUHFGYy9xODBnS0hXRVlLelJOQlpiT2JreS9JNGFKWUZ4Vi83VjVibytBWTFEbk1lS1VuUFdQdkRFVTNSbFhiRVhacHdaOEs3aFFyMXNWdG1oa0pPWGVldVZMRkk1Nk9oOGZRVkgiLCJtYWMiOiIyNTI3YmVjMDlmNTRlZjg1NDJiODhhOGM2MzFiNjJhY2Q1YjFjNjNiNjdjYjkyYTFkM2MxYjAwODkwNWUzYzc3IiwidGFnIjoiIn0%3D; _ga_HBD3FGX1DP=GS1.1.1710542247.2.1.1710542302.0.0.0',
        'origin': 'https://wahmi.org',
        'referer': 'https://witanime.one/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-csrf-token': bs4.BeautifulSoup(res.text, 'html.parser').find('meta', {'name': 'csrf-token'})['content'],
        'x-requested-with': 'XMLHttpRequest',
    }

    downloadURL = client.post(url.replace('/file', '/download/create'), headers=headers).json()["download_link"]
    response = requests.get(downloadURL, stream=True)
    total_size = int(response.headers.get("Content-Length", 0))
    with open(saveAs, "wb") as file:
        console.info(f"Downloading {saveAs} using Tusfiles")
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True, ncols=100)
        for data in response.iter_content(chunk_size=512*1024):
            file.write(data)
            progress_bar.update(len(data))
    return True