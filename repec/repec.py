#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
import configparser
import glob
import json
import requests
import sys
import traceback
import urllib.parse


CONFIG = configparser.ConfigParser()
CONFIG.read("repec.cfg")


def extract_view (elem, count):
    view = {}

    try:
        view["dimensions_id"] = elem["dimensions_id"]
        view["doi"] = elem["doi"]
        view["title"] = elem["title"]
        view["related_dataset_name"] = elem["related_dataset_name"]

        view["authors"] = []

        if "authors" in elem:
            for a in elem["authors"]:
                view["authors"].append({
                        "first_name": a["first_name"],
                        "last_name": a["last_name"],
                        })
    
        if "journal" in elem:
            view["journal"] = elem["journal"]
        else:
            view["journal"] = None

        return view

    except:
        print(traceback.format_exc())
        print(count, elem)
        sys.exit(1)


def get_repec_handle (title):
    enc_title = urllib.parse.quote_plus(title.replace("(", "").replace(")", "").replace(":", ""))

    cgi_url = "https://ideas.repec.org/cgi-bin/htsearch?q={}".format(enc_title)
    response = requests.get(cgi_url).text
    #print(BeautifulSoup(response, "html.parser").prettify())

    soup = BeautifulSoup(response, "html.parser")
    ol = soup.find("ol", {"class": "list-group"})
    results = ol.findChildren()

    if len(results) > 0:
        li = results[0]
        handle = li.find("i").get_text()
        return handle
    else:
        return None


def get_repec_meta (token, handle):
    try:
        api_url = "https://api.repec.org/call.cgi?code={}&getref={}".format(token, handle)
        response = requests.get(api_url).text

        meta = json.loads(response)
        return meta

    except:
        print(traceback.format_exc())
        print("ERROR: {}".format(handle))
        return None


if __name__ == "__main__":
    mode = sys.argv[1]

    if mode == "1":
        pubs = []

        ## load the Dimensions API results
        for filename in glob.glob("string_searches/*.json"):
            with open(filename) as f:
                count = 0

                for elem in json.load(f):
                    #print(elem)
                    view = extract_view(elem, count)
                    view["repec_handle"] = get_repec_handle(view["title"])

                    pubs.append(view)
                    count += 1

        ## persist the results to a file
        with open("pub_handles.json", "w") as f:
            json.dump(pubs, f, indent=2, sort_keys=True)


    else:
        repec_token = CONFIG["DEFAULT"]["repec_token"]
        pubs = []

        ## call RePEc API to get author metadata        
        with open("pub_handles.json", "r") as f:
            for view in json.load(f):
                if view["repec_handle"]:
                    #print(view)
                    results = get_repec_meta(repec_token, view["repec_handle"])

                    if results and len(results) > 0:
                        meta = results[0]

                        if view["title"].lower() == meta["bibliographic"]["name"].lower():
                            view["repec_authors"] = meta["author"].split(" & ")
                            view["repec_biblio"] = meta["bibliographic"]
                            pubs.append(view)

        ## persist the results to a file
        with open("pub_authors.json", "w") as f:
            json.dump(pubs, f, indent=2, sort_keys=True)
