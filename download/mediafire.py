import os, shutil, sys, tempfile, requests, tqdm, os, time, bs4, zipfile
from console import console


def mediafire(client, url, saveAs):
    zipFile = None
    downloadURL = bs4.BeautifulSoup(client.get(url).text, "html.parser").find("a", {"id": "downloadButton"})["href"]
    if downloadURL.endswith(".zip"):
        zipFile = f'{".".join(saveAs.split(".")[:-1])}.zip'
    res = requests.get(downloadURL, stream=True, timeout=10)
    total = int(res.headers.get('Content-Length'))
    with tempfile.NamedTemporaryFile(mode="w+b", prefix="mediafireDL_", delete=False) as temp_output_file:
        console.info(f"Downloading {zipFile or saveAs} using Mediafire")
        progress_bar = tqdm.tqdm(total=total, unit='B', unit_scale=True, ncols=100)
        for chunk in res.iter_content(chunk_size=512 * 1024):  # 512KB
            temp_output_file.write(chunk)
            progress_bar.update(len(chunk))
        progress_bar.close()
        if temp_output_file:
            temp_output_file.close()
            time.sleep(1)
            shutil.move(temp_output_file.name, zipFile or saveAs)
    if zipFile:
        with zipfile.ZipFile(zipFile, "r") as zFile:
            shutil.unpack_archive(zipFile, ".", "zip")
            try:
                os.rename(zFile.namelist()[0], saveAs)
            except FileExistsError:
                os.remove(zFile.namelist()[0])
                console.error(f"{saveAs} already downloaded")
        os.remove(zipFile)
    return True


