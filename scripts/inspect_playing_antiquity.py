#!/usr/bin/env python3
"""Inventory the existing Playing Antiquity artwork; do not alter the live site."""
import json, re
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
URL="https://ai-antiquity.org/index.php/ai/gamestudies"
s=requests.Session()
s.headers.update({"User-Agent":"Mozilla/5.0 (compatible; CIAW-asset-retrieval/1.0)"})
r=s.get(URL,timeout=40)
r.raise_for_status()
soup=BeautifulSoup(r.text,"html.parser")
result={"page":r.url,"http_status":r.status_code,"title":soup.title.get_text(" ",strip=True) if soup.title else "","images":[],"backgrounds":[],"meta":[],"stylesheets":[]}
for tag in soup.find_all(["img","source"]):
    src=tag.get("src") or tag.get("data-src") or tag.get("srcset")
    if src:
        ctx=tag.parent.get_text(" ",strip=True)[:200] if tag.parent else ""
        result["images"].append({"url":urljoin(r.url,src.split(",")[0].split()[0]),"alt":tag.get("alt",""),"title":tag.get("title",""),"parent":ctx,"width":tag.get("width"),"height":tag.get("height")})
for tag in soup.find_all("meta"):
    if tag.get("property") in ("og:image","twitter:image") or tag.get("name") in ("twitter:image",):
        result["meta"].append({"name":tag.get("property") or tag.get("name"),"url":urljoin(r.url,tag.get("content",""))})
for tag in soup.find_all(style=True):
    for img in re.findall(r"url\(['\"]?([^)'\"\s]+)",tag["style"]):
        result["backgrounds"].append({"url":urljoin(r.url,img),"element":tag.name,"text":tag.get_text(" ",strip=True)[:100]})
for tag in soup.find_all("style"):
    for img in re.findall(r"url\(['\"]?([^)'\"\s]+)",tag.get_text()):
        result["backgrounds"].append({"url":urljoin(r.url,img),"element":"style","text":""})
for tag in soup.find_all("link",rel=True):
    if "stylesheet" in tag.get("rel",[]):
        result["stylesheets"].append(urljoin(r.url,tag.get("href","")))
out=Path("assets/playing-antiquity-inventory.json")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"http":r.status_code,"images":result["images"],"backgrounds":result["backgrounds"],"meta":result["meta"],"css_files":result["stylesheets"]},ensure_ascii=False)[:12000])
