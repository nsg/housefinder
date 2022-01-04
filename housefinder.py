from bs4 import BeautifulSoup
import requests
import json
import argparse
import re

def load_state():
    try:
        f = open("state.json", "r")
        return json.load(f)
    except:
        return {}

def save_state(data):
    f = open("state.json", "w")
    f.write(json.dumps(data))
    f.write("\n")
    f.close()

def last_segment(string, split):
    segments = string.split(split)
    return segments[len(segments)-1]

def get_booli_items(object_area, object_type="Villa") -> str:
    url = f"https://www.booli.se/{object_area}?objectType={object_type}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.text
    else:
        raise Exception("Failed to query Booli", resp.status_code)

def get_hemnet_items(url) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        return resp.text
    else:
        raise Exception("Failed to query Hemnet", resp.status_code, resp.text)

def get_hemnet_salu_items(location_id, object_type="villa") -> str:
    url = f"https://www.hemnet.se/bostader?location_ids[]={location_id}&item_types[]={object_type}"
    return get_hemnet_items(url)

def get_hemnet_kommande_items(location_id, object_type="villa") -> str:
    url = f"https://www.hemnet.se/kommande/bostader?location_ids[]={location_id}&item_types[]={object_type}"
    return get_hemnet_items(url)

def process_booli_items(name, object_area) -> None:
    print(f"{name}")
    html = get_booli_items(object_area)
    soup = BeautifulSoup(html, 'html.parser')
    for o in soup.find_all(class_="_2CbdZ"):
        street_name = o.find("h3").text
        href = o.get("href")
        object_id = last_segment(href, "/")
        if object_id not in state.get("booli", []):
            print(f"  {street_name}")
            print(f"    https://www.booli.se{href}")
            print(f"    ID: {object_id}")
            for p in o.find_all("p"):
                print(f"    {p.text}")
            print()

def process_hemnet_items(name, location_id):
    print(f"{name}")
    html_salu = get_hemnet_salu_items(location_id)
    html_kommande = get_hemnet_kommande_items(location_id)
    for html in (html_salu, html_kommande):
        soup = BeautifulSoup(html, 'html.parser')
        for o in soup.find_all(class_="listing-card"):
            street_name = o.find("h2").text.strip()
            href = o.get("href")
            object_id = last_segment(href, "-")
            if object_id not in state.get("hemnet", []):
                print(f"  {street_name}")
                print(f"    {href}")
                print(f"    ID: {object_id}")
                attr = o.find(class_="listing-card__attributes-container")
                for p in attr.find_all(class_="listing-card__attribute--primary"):
                    p2 = p.text.strip()
                    p2 = re.sub(r"[^+\w\s]", '', p2)
                    p2 = re.sub(r"( |\n)+", '', p2)
                    print(f"    {p2}")
                for p in attr.find_all(class_="listing-card__attribute--secondary"):
                    p2 = p.text.strip()
                    p2 = re.sub(r"[^+\w\s]", '', p2)
                    print(f"    {p2}")

parser = argparse.ArgumentParser(description='Find a house')
parser.add_argument('--list-booli', action='store_true', help='List Booli objects')
parser.add_argument('--list-hemnet', action='store_true', help='List Hemnet objects')
parser.add_argument('--hide-booli', help='Hide a Booli object from --list-booli')
parser.add_argument('--hide-hemnet', help='Hide a Hemnet object from --list-hemnet')
args = parser.parse_args()

state = load_state()

if args.list_booli:
    print("BOOLI")
    process_booli_items("Bromma", "bromma/115355")
if args.list_hemnet:
    print("HEMNET")
    process_hemnet_items("Norra Ängby", 473403)
    process_hemnet_items("Eneby", 473348)
    process_hemnet_items("Bällsta", 473345)
    process_hemnet_items("Bromma Kyrka", 473343)
    process_hemnet_items("Ulvsunda", 473431)
    #process_hemnet_items("Bromma", 898740)
elif args.hide_booli:
    print(f"Hiding object: {args.hide_booli}")
    if "booli" not in state:
        state["booli"] = []
    state["booli"].append(args.hide_booli)
    save_state(state)
elif args.hide_hemnet:
    print(f"Hiding object: {args.hide_hemnet}")
    if "hemnet" not in state:
        state["hemnet"] = []
    state["hemnet"].append(args.hide_hemnet)
    save_state(state)
