import json,re,time,requests
from pathlib import Path
import datetime
targets=["https://ciaw.es/","https://www.ciaw.es/","https://ciaw.netlify.app/"]
results=[]
for url in targets:
 try:
  res=requests.get(url,timeout=35,headers={"User-Agent":"Mozilla/5.0 CIAW-Migration-Diagnostics","Cache-Control":"no-cache","Pragma":"no-cache"},params={"ciaw_verify":str(int(time.time()))},allow_redirects=True)
  html=res.text
  result={"requested_url":url,"final_url":res.url,"status":res.status_code,"bytes":len(res.content),"title":re.search(r"<title[^>]*>(.*?)</title>",html,re.S|re.I).group(1) if re.search(r"<title[^>]*>(.*?)</title>",html,re.S|re.I) else None,"contains_new_neuro":'Different Minds. <span class="gradient-text">Better Humanities.' in html,"contains_neuro_id":'id="neurodiversity"' in html,"contains_catalonia":"Based in Catalonia" in html,"contains_original_playing_artwork":"playing-antiquity-banner.webp" in html,"has_game_studies":"id=\"game-studies\"" in html,"is_old_hero":"Reimagining Ancient Studies" in html,"last_modified":res.headers.get("Last-Modified"),"etag":res.headers.get("ETag"),"age":res.headers.get("Age"),"server":res.headers.get("Server"),"x_nf_request_id":res.headers.get("X-Nf-Request-Id")}
  results.append(result)
 except Exception as ex:
  results.append({"requested_url":url,"error":str(ex)})
out=Path(".ciaw-deploy-check.json")
out.write_text(json.dumps({"checked_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"results":results},indent=2),encoding="utf-8")
print(json.dumps(results,indent=2))
