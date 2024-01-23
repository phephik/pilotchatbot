import re
import time
import shutil
from pathlib import Path

import selenium
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


WEB_URL = Path(r"https://aim.rlp.cz/vfrmanual/index_en.html")
DRIVER = None
DOWNLOAD_DIRECTORY = None

def download_latest_vfr_manual(url: Path) -> Path:
    print("Downloading most recent version...")
    DRIVER.get(str(url))
    DRIVER.implicitly_wait(2)
    elements = DRIVER.find_elements(By.CLASS_NAME, "download")
    available_versions = [Path(e.get_attribute("href")).name for e in elements]
    available_versions.sort()
    latest_online_version = available_versions[-1]
    print(
        f"Available versions online: {available_versions}, downloading latest: {latest_online_version}"
    )
    [
        e.click()
        for e in elements
        if Path(e.get_attribute("href")).name == latest_online_version
    ]
    time.sleep(5)
    try:
        alert = Alert(DRIVER)
        print(f"Confirmation text: {alert.text}")
        alert.accept()
    except selenium.common.exceptions.NoAlertPresentException as e:
        print(f"{e}")
    downloaded_file = Path(DOWNLOAD_DIRECTORY / latest_online_version)
    while not downloaded_file.is_file():
        time.sleep(1)
    print(f"File downloaded to {downloaded_file.resolve()}")

    shutil.unpack_archive(
        downloaded_file,
        downloaded_file.parent / downloaded_file.stem,
        downloaded_file.suffix[1:],
    )
    print(f"File unpacked. Removing archive.")
    downloaded_file.unlink()
    return downloaded_file.parent / downloaded_file.stem


# checks current version that is downloaded (current offline version)
def check_current_offline_version(dir: Path):
    for x in dir.iterdir():
        if re.match(r"\d{8}_\d+", x.stem) and x.is_dir():
            return x.stem


def check_current_online_version(url: Path):
    global DRIVER
    DRIVER.get(str(url))
    DRIVER.implicitly_wait(3)
    elements = DRIVER.find_elements(By.CLASS_NAME, "download")
    available_versions = [Path(e.get_attribute("href")).stem for e in elements]
    available_versions.sort()
    latest_online_version = available_versions[-1]
    return latest_online_version


def update_cz_vfr_manual(url: Path, local: Path):
    global DOWNLOAD_DIRECTORY
    current_offline_version = check_current_offline_version(local)
    current_online_version = check_current_online_version(url)
    if current_online_version == current_offline_version:
        print(
            f"We have the most recent version downloaded: {current_offline_version} (no action needed)"
        )
        return local / current_offline_version
    # delete the current version if it's old
    print(f"deleting old version: {current_offline_version}")
    # shutil.rmtree(Path(DOWNLOAD_DIRECTORY / current_offline_version))
    return download_latest_vfr_manual(WEB_URL)


def get_latest_cz_vfr_manual(driver_path: Path, url: Path=WEB_URL):
    global DOWNLOAD_DIRECTORY, DRIVER
    DRIVER = driver_path
    DOWNLOAD_DIRECTORY = Path.home() / "Downloads"
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--download.prompt_for_download=false")
    options.add_argument("--download.directory_upgrade=true")
    try:
        DRIVER = webdriver.Chrome(service=service)
        vfr_dir_path = update_cz_vfr_manual(url, DOWNLOAD_DIRECTORY)
        DRIVER.quit()
    except selenium.common.exceptions.NoSuchDriverException:
        print(f"Chrome driver error. Please specify the path to the chrome driver: {DRIVER}")
        raise FileNotFoundError
    return vfr_dir_path