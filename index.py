# terabox_api.py
from flask import Flask, request, jsonify
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)

ALLOWED_DOMAINS = [
    "teraboxlink.com", "4funbox.in", "1024tera.com", "mirrobox.com", "nephobox.com",
    "terabox.app", "terabox.com", "teraboxlink.com"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

@app.route("/v1/terabox", methods=["GET"])
def terabox():
    url = request.args.get("url")
    if not url:
        return jsonify({"success": False, "invalid url": True}), 400

    # Validate domain
    hostname = urlparse(url).hostname
    if hostname not in ALLOWED_DOMAINS:
        return jsonify({"success": False, "invalid url": True}), 400

    try:
        # Fetch page
        r = requests.get(url, headers=HEADERS, timeout=10)
        html = r.text
        soup = BeautifulSoup(html, "html.parser")

        # Try <video> tags
        video_tag = soup.find("video")
        if video_tag and video_tag.get("src"):
            return jsonify({"success": True, "download_link": video_tag["src"], "thamel": video_tag.get("poster","")})

        # Try meta og:video
        meta = soup.find("meta", property="og:video")
        thumb = soup.find("meta", property="og:image")
        if meta:
            return jsonify({"success": True, "download_link": meta.get("content"), "thamel": thumb.get("content") if thumb else ""})

        # Try JS embedded JSON / downloadUrl
        scripts = soup.find_all("script")
        for s in scripts:
            if s.string:
                m = re.search(r'["\'](?:downloadUrl|file|source|url)["\']\s*:\s*["\'](https?://[^"\']+\.(?:mp4|m3u8|webm|mkv))["\']', s.string)
                if m:
                    return jsonify({"success": True, "download_link": m.group(1), "thamel": thumb.get("content") if thumb else ""})

        # Fallback
        return jsonify({"success": False, "error": "data_not_found"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)