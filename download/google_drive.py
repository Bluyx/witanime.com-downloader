import gdown, sys, io
from console import console



def google_drive(client, url, saveAs):
    stdout_backup, stderr_backup = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    console.info(f"Downloading {saveAs} using Google Drive")
    gdown.download(url, saveAs, quiet=False)
    output = sys.stdout.getvalue()
    sys.stdout, sys.stderr = stdout_backup, stderr_backup
    if "Access denied" in output: return False
