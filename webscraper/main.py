import argparse
from pathlib import Path

from webscraper import WEB_URL, get_latest_cz_vfr_manual
from html_parser import get_data_from_htmls

def main():
    parser = argparse.ArgumentParser(
        prog='VFR Manual Parser CZ',
        description='A script that updates and extracts available information from the Czech VFR manual based on local AIP'
    )
    parser.add_argument('-d', '--driver-path', default=Path.home() / "Downloads/chromedriver.exe", required=False)
    parser.add_argument('-u','--url', default=WEB_URL, required=False)
    parser.add_argument('-t','--type', default='json', required=False)
    parser.add_argument('-o','--output-file', default=Path.home() / "Downloads", required=False)
    parser.add_argument('-f', '--format', choices=['json', 'hdf5'], default='json', required=False)

    args = parser.parse_args()

    vfr_man_path = get_latest_cz_vfr_manual(driver_path=args.driver_path, url=args.url)
    get_data_from_htmls(path=vfr_man_path, out_dir=args.output_file, format=args.format)


if __name__ == "__main__":
    main()