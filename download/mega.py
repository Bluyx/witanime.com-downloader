# Credits to https://github.com/odwyersoftware/mega.py
import re, requests, json, random, tempfile, shutil, os, time, tqdm, struct, base64, codecs
from Crypto.Util import Counter
from Crypto.Cipher import AES
from pathlib import Path


i = 0
def get_chunks(size):
    p = 0
    s = 0x20000
    while p + s < size:
        yield (p, s)
        p += s
        if s < 0x100000:
            s += 0x20000
    yield (p, size - p)

def aes_cbc_decrypt(data, key):
    aes_cipher = AES.new(key, AES.MODE_CBC, makebyte('\0' * 16))
    return aes_cipher.decrypt(data)

def decrypt_attr(attr, key):
    attr = aes_cbc_decrypt(attr, struct.pack('>%dI' % len(key), *key))
    attr = codecs.latin_1_decode(attr)[0]
    attr = attr.rstrip('\0')
    return json.loads(attr[4:]) if attr[:6] == 'MEGA{"' else False
def makebyte(x):
    return codecs.latin_1_encode(x)[0]
def base64_url_decode(data):
    data += '=='[(2 - len(data) * 3) % 4:]
    for search, replace in (('-', '+'), ('_', '/'), (',', '')):
        data = data.replace(search, replace)
    return base64.b64decode(data)
def str_to_a32(b):
    if isinstance(b, str):
        b = makebyte(b)
    if len(b) % 4:
        # pad to multiple of 4
        b += b'\0' * (4 - len(b) % 4)
    return struct.unpack('>%dI' % (len(b) / 4), b)

def mega(client, url, saveAs):
    if "/file/" in url: # V2 URL structure
        url = url.replace(" ", "")
        file_id = re.findall(r"\W\w\w\w\w\w\w\w\w\W", url)[0][1:-1]
        path = f"{file_id}!{url[re.search(file_id, url).end() + 1:]}".split("!")
    elif "!" in url: # V1 URL structure
        path = re.findall(r"/#!(.*)", url)[0].split("!")
    file_id = path[0]
    file_key = str_to_a32(base64_url_decode(path[1]))
    sequence_num = random.randint(0, 0xFFFFFFFF)
    params = {"id": sequence_num}
    sequence_num += 1
    data = {
        "a": "g",
        "g": 1,
        "p": file_id
    }
    if not isinstance(data, list): data = [data] # ensure input data is a list
    json_resp = client.post("https://g.api.mega.co.nz/cs", params=params, data=json.dumps(data), timeout=160).json()
    try:
        if isinstance(json_resp, list):
            int_resp = json_resp[0] if isinstance(json_resp[0], int) else None
        elif isinstance(json_resp, int):
            int_resp = json_resp
    except IndexError:
        int_resp = None
    if int_resp is not None:
        if int_resp == 0: file_data = int_resp
        if int_resp == -3: raise RuntimeError("Request failed, retrying")
        raise Exception(int_resp)
    file_data = json_resp[0]
    k = (file_key[0] ^ file_key[4], file_key[1] ^ file_key[5], file_key[2] ^ file_key[6], file_key[3] ^ file_key[7])
    iv = file_key[4:6] + (0, 0)
    meta_mac = file_key[6:8]
    if "g" not in file_data:
        raise Exception("File not accessible anymore")
    file_url = file_data["g"]
    file_size = file_data["s"]
    attribs = base64_url_decode(file_data["at"])
    attribs = decrypt_attr(attribs, k)

    input_file = client.get(file_url, stream=True).raw

    with tempfile.NamedTemporaryFile(mode="w+b", prefix="megapy_", delete=False) as temp_output_file:
        k_str = struct.pack('>%dI' % len(k), *k)
        counter = Counter.new(128, initial_value=((iv[0] << 32) + iv[1]) << 64)
        aes = AES.new(k_str, AES.MODE_CTR, counter=counter)
        mac_str = "\0" * 16
        mac_encryptor = AES.new(k_str, AES.MODE_CBC, mac_str.encode("utf8"))
        kk = [iv[0], iv[1], iv[0], iv[1]]
        iv_str = struct.pack('>%dI' % len(kk), *kk)
        print(f"Downloading {saveAs} using Mega")
        progress_bar = tqdm.tqdm(total=file_size, unit="B", unit_scale=True, ncols=100)
        for chunk_start, chunk_size in get_chunks(file_size):
            chunk = input_file.read(chunk_size)
            chunk = aes.decrypt(chunk)
            temp_output_file.write(chunk)
            encryptor = AES.new(k_str, AES.MODE_CBC, iv_str)
            for i in range(0, len(chunk) - 16, 16):
                block = chunk[i:i + 16]
                encryptor.encrypt(block)

            # fix for files under 16 bytes failing
            if file_size > 16:
                i += 16
            else:
                i = 0
            block = chunk[i:i + 16]
            if len(block) % 16: block += b"\0" * (16 - (len(block) % 16))
            mac_str = mac_encryptor.encrypt(encryptor.encrypt(block))
            progress_bar.update(os.stat(temp_output_file.name).st_size - progress_bar.n)
        file_mac = str_to_a32(mac_str)
        # check mac integrity
        if (file_mac[0] ^ file_mac[1],
                file_mac[2] ^ file_mac[3]) != meta_mac:
            raise ValueError("Mismatched mac")
        output_path = Path(saveAs)
        temp_output_file.close()
        time.sleep(1) # to fix "The process cannot access the file because it is being used by another process"
        shutil.move(temp_output_file.name, output_path)
        return True




