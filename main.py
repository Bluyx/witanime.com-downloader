import sys, json, tls_client, os, random, string, base64
from bs4 import BeautifulSoup as soup
from download import *
from console import console
from urllib.parse import urlparse
import re
# Todo: notify when download is completed
# webhook = SyncWebhook.from_url("https://discord.com/api/webhooks/xxxxxxx/xxxxxxxxxxx")

with open("config.json", 'r') as c:
    config = json.load(c)


download_priorities = config["download_priorities"]

client = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True, ja3_string="".join(random.choice(string.digits + string.ascii_lowercase) for x in range(1000)))

animeURL = input("Anime URL: ")
witURL = urlparse(animeURL)
witURL = f"{witURL.scheme}://{witURL.netloc}"
if f"/anime/" not in animeURL: sys.exit(f"Invalid Anime URL. Use '{witURL}/anime/one-piece' format.")
headers = {
    'authority': 'witanime.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
    'cache-control': 'max-age=0',
    'referer': f'{witURL}/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
}


try:
    fromEpisode = int(input("Start downloading from episode: "))
    toEpisode = int(input("stop downloading at episode: "))
except ValueError: sys.exit(console.error("Only numbers"))
if fromEpisode > toEpisode:
    sys.exit(console.error(f"{fromEpisode} is greater than {toEpisode}"))
animePage = soup(client.get(animeURL, headers=headers, allow_redirects=True).text, 'html.parser')
episodesCount = animePage.find(lambda tag: tag.name == 'span' and "عدد الحلقات" in tag.text).find_next_sibling(string=True).strip()
if "غير معروف" in episodesCount:
    maxEpisodes = 99999999999999999999
else:
    maxEpisodes = int(episodesCount)

if toEpisode > maxEpisodes:
    sys.exit(console.error(f"the anime have {maxEpisodes} episodes and you want stop downloading at episode {toEpisode}"))

animeName = animeURL.split("/anime/")[1].split("/")[0]
if not os.path.isdir("animes"): os.makedirs("animes")
if not os.path.isdir(f"animes/{animeName}"): os.makedirs(f"animes/{animeName}")


for episode in range(toEpisode):
    episode = episode + fromEpisode # Todo
    if episode == toEpisode + 1:
        break
    epPage = client.get(f"{witURL}/episode/{animeName}-الحلقة-{episode}/", headers=headers, allow_redirects=True).text
    episodePage = soup(epPage, features="lxml")
    saveAs = f"animes/{animeName}/{config['outputFormat'].replace('{anime_name}', animeName).replace('{episode}', str(episode))}"
    downloadFunctions = {
        "wahmi": (wahmi, None, None),
        "google_drive": (google_drive, None, None),
        "tusfiles": (tusfiles, None, None),
        "mega": (mega, None, None),
        "mediafire": (mediafire, None, None)
    }
    availableDownloads = []
    FHD = episodePage.find("li", string="الجودة الخارقة FHD")
    HD = episodePage.find("li", string="الجودة العالية HD")
    SD = episodePage.find("li", string="الجودة المتوسطة SD")
    if FHD:
        downloadLinks = FHD.find_parent("ul")
    elif HD:
        downloadLinks = HD.find_parent("ul")
    elif SD:
        downloadLinks = SD.find_parent("ul")
    else:
        print("No UL")
    downloadLinks = downloadLinks.find_all("li")[1:]
    search = re.search(r'var _d = (\[.*?\]);', epPage)
    n = json.loads(re.search(r'var _n = (\[.*?\]);', epPage).group(1))
    if search:
        downloadUrls = json.loads(search.group(1))
        #input(downloadUrlsDict)
        #input(n)
    else:
        sys.exit("No dict found")
    for downloadMethod in downloadLinks:
        #print(downloadLinks)
        try:
            downloadIndex = int(downloadMethod.find("a").get("data-index"))
            #downloadLink = downloadMethod.find("a").get("href")
            #downloadKey = downloadMethod.find("a").get("data-key")
            #if downloadLink is None and downloadKey is None:
            #    downloadLink = base64.b64decode(downloadMethod.find("a").get("data-url")).decode()
            #if downloadKey:
            #    downloadLink = base64.b64decode(downloadUrlsDict[downloadKey]).decode()
            #input(downloadUrls)
       
            downloadLink = base64.b64decode(downloadUrls[downloadIndex]).decode()
            print(downloadLink)
            #print(downloadIndex)
            #n = n[downloadIndex]
            #input(n[downloadIndex]["d"])
            #print(base64.b64decode(n[downloadIndex]["k"]).encode())
            #downloadLink = downloadLink.slice(0, -n["d"][int(base64.b64decode(n[downloadIndex]["k"]).decode())])
            #print(downloadLink)
            downloadText = downloadMethod.find("a").text.lower().strip()
            print(downloadText)
            if downloadText.replace(" ", "_") in downloadFunctions:
                availableDownloads.append(downloadText.replace(" ", "_"))
            if downloadText == "wahmi":
                downloadFunctions["wahmi"] = (wahmi, downloadLink, saveAs)
            if downloadText == "google drive":
                downloadFunctions["google_drive"] = (google_drive, downloadLink, saveAs)
            elif downloadText == "tusfiles":
                downloadFunctions["tusfiles"] = (tusfiles, downloadLink, saveAs)
            elif downloadText == "mega":
                downloadFunctions["mega"] = (mega, downloadLink, saveAs)
            elif downloadText == "mediafire":
                downloadFunctions["mediafire"] = (mediafire, downloadLink, saveAs)
            else: pass
        except AttributeError as err:
            pass
        except Error as err:
            print(str(err))
    if len(availableDownloads) == 0:
        print("Not supported")
    else:
        for priorityDownload in sorted(availableDownloads, key=lambda item: download_priorities.index(item) if item.replace(" ", "_") in download_priorities else len(download_priorities)):
            downloadFunction, downloadLink, saveAs = downloadFunctions[priorityDownload]
            if downloadFunction(client, downloadLink, saveAs):
                console.success(f"{saveAs} Downloaded!\n")
                break

console.success("Downloaded!")
