import sys, json, tls_client, os, random, string
from bs4 import BeautifulSoup as soup
from download import *


# webhook = SyncWebhook.from_url("https://discord.com/api/webhooks/1123671857086877766/gdI7c5bRNj5aMx7R34b-kGhr956gCMUPapYiRFjFJtJL-nXsIvTR3ocbQyHbfbPhZD5K")
with open("config.json", 'r') as c:
    config = json.load(c)


download_priorities = config["download_priorities"]

client = tls_client.Session(client_identifier="chrome_114", random_tls_extension_order=True, ja3_string="".join(random.choice(string.digits + string.ascii_lowercase) for x in range(1000)))
headers = {
    'authority': 'witanime.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
    'cache-control': 'max-age=0',
    'referer': 'https://witanime.com/?search_param=animes&s=bleach',
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


# https://witanime.com/anime/naruto/
animeURL = input("Anime URL: ")
if "https://witanime.com/anime" not in animeURL: sys.exit("Invalid Anime URL. Use 'https://witanime.com/animeName' format.")
try:
    fromEpisode = int(input("Start downloading from episode: "))
    toEpisode = int(input("stop downloading at episode: "))
except ValueError: sys.exit("Only numbers")
if fromEpisode > toEpisode:
    sys.exit(f"{fromEpisode} is greater than {toEpisode}")
animePage = soup(client.get(animeURL, headers=headers).text, 'html.parser')
# episodesCount = animePage.find("div", {"class": "anime-info"}, string="عدد الحلقات")
episodesCount = animePage.find(lambda tag: tag.name == 'span' and "عدد الحلقات" in tag.text).find_next_sibling(string=True).strip()
if "غير معروف" in episodesCount:
    maxEpisodes = 9999999999
else:
    maxEpisodes = int(episodesCount)

if toEpisode > maxEpisodes:
    sys.exit(f"the anime have {maxEpisodes} and you want stop downloading at {toEpisode}")

animeName = animeURL.split("/anime/")[1].split("/")[0]
if not os.path.isdir("animes"): os.makedirs("animes")
if not os.path.isdir(f"animes/{animeName}"): os.makedirs(f"animes/{animeName}")


for episode in range(toEpisode):
    episode = episode + fromEpisode # Todo
    if episode == toEpisode + 1:
        break
    episodePage = soup(client.get(f"https://witanime.com/episode/{animeName}-الحلقة-{episode}/", headers=headers).text, features="lxml")
    saveAs = f"animes/{animeName}/{config['outputFormat'].replace('{anime_name}', animeName).replace('{episode}', str(episode))}"
    downloadFunctions = {
        # "mega": (mega, None),
        "google_drive": (google_drive, None, None),
        "tusfiles": (tusfiles, None, None),
        "mega": (mega, None, None),
        "mediafire": (mediafire, None, None),
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
    for downloadMethod in downloadLinks.find_all("li"):
        try:
            downloadLink = downloadMethod.find("a").get("href")
            downloadText = downloadMethod.find("a").text.lower()
            if downloadText.replace(" ", "_") in downloadFunctions:
                availableDownloads.append(downloadText.replace(" ", "_"))
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
    if len(availableDownloads) == 0:
        print("Not supported")
    else:
        for priorityDownload in sorted(availableDownloads, key=lambda item: download_priorities.index(item) if item.replace(" ", "_") in download_priorities else len(download_priorities)):
            downloadFunction, downloadLink, saveAs = downloadFunctions[priorityDownload]
            if downloadFunction(client, downloadLink, saveAs):
                break
