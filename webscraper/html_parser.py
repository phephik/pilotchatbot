import re
from pathlib import Path
from io import StringIO

import bs4
from bs4 import BeautifulSoup
import html2text
import pandas as pd

text_maker = html2text.HTML2Text()
text_maker.ignore_links = True
text_maker.ignore_images = True
text_maker.ignore_emphasis = True

AD_DATA = {
    "aerodrome-statut": "statut",
    "aerodrome-provoz": "operation",
    "aerodrome-poloha": "location",
    "aerodrome-sluzby": "services",
    "aerodrome-frekvence": "frequency",
    "aerodrome-postupy": "procedures",
    "aerodrome-drahy": "runways",
    "aerodrome-kontakty": "contacts",
    "vfrc-chart": "vfr_chart",
    "adc-chart": "ad_chart",
    "aerodrome-text": "text",
}

AD_SERVICES = {
    "Olej": "oil",
    "Záchranná služba": "rescue_service",
    "Hangárování": "hangars",
    "Restaurace": "restaurants",
    "Palivo": "fuel",
    "Provozní doba": "operating_hours",
    "Ubytování": "accomodation",
    "Servis": "repair",
    "Doprava": "transport",
}


def process_tag_text(tag: bs4.Tag) -> str:
    return text_maker.handle(tag.get_text(separator=" ")).replace("\n", " ")


def process_data(data_type: str, raw_html_tag):
    match data_type:
        case "aerodrome-statut" | "aerodrome-provoz" | "aerodrome-poloha" | "aerodrome-postupy" | "aerodrome-kontakty":
            return process_tag_text(raw_html_tag)
        case "aerodrome-sluzby":
            divs = raw_html_tag.find_all("div")
            to_ret = {AD_SERVICES[key]: "NIL" for key in AD_SERVICES.keys()}
            for key, val in AD_SERVICES.items():
                for div in divs:
                    if div.find("img", {"alt": key}):
                        to_ret[val] = process_tag_text(div)
            return to_ret
        case "aerodrome-frekvence" | "aerodrome-text":
            the_str = process_tag_text(raw_html_tag)
            if ret := re.sub(r"([0-9|,]+(\.[0-9|,]+)?)", r" \1 ", the_str).strip():
                return ret
            return "NIL"
        case "aerodrome-drahy":
            try:
                return pd.read_html(StringIO(str(raw_html_tag)))[0]
            except ValueError:
                return "NIL"
        case "vfrc-chart" | "adc-chart":
            return raw_html_tag.find("img")["src"]
        case _:
            raise ValueError


def get_ad_codes(dir_path: Path) -> tuple[list, list]:
    pattern = re.compile(r"(lk[a-z]{2,})_text_en\.html")
    ad_codes = set()
    ad_paths = []
    for file in dir_path.glob('**/*'):
        if result := re.match(pattern, file.name):
            ad_codes.add(result[1])
            ad_paths.append(file)
    return (sorted(list(ad_codes)), sorted(ad_paths))


def get_ad_data(file_path: Path, ad_code) -> pd.Series:
    ret = pd.Series(index=["ad_code"] + list(AD_DATA.values()), dtype=str)
    ret["ad_code"] = ad_code
    with open(file_path, encoding="UTF-8") as f:
        file_content = BeautifulSoup(f.read(), "lxml")
    for key, val in AD_DATA.items():
        content = file_content.find(
            "table" if key == "aerodrome-drahy" else "div", {"id": key}
        )
        ret[val] = process_data(key, content)
    return ret


def get_data_from_htmls(path:Path, out_dir: Path=Path.home() / "Downloads", format:str = 'json'):
    ad_codes, ad_filepaths = get_ad_codes(path)
    ads_data = []
    for ad_code, filepath in zip(ad_codes, ad_filepaths):
        ads_data.append(get_ad_data(filepath, ad_code))
    match format:
        case 'json':
            pd.DataFrame(ads_data).to_json(out_dir / 'vfr_cz_data.json',index=False)
        case 'hdf5':
            pd.DataFrame(ads_data).to_hdf(out_dir / 'vfr_cz_data.h5')
