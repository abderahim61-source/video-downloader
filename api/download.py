from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import yt_dlp

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        video_url = params.get('url', [None])[0]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if not video_url:
            self.wfile.write(json.dumps({"error": "Missing URL parameter"}).encode())
            return

        try:
            # إعدادات yt-dlp لجلب أفضل جودة mp4 مباشرة
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                # نأخذ رابط التحميل المباشر الحقيقي من السيرفر
                direct_url = info.get('url')
                
                if direct_url:
                    self.wfile.write(json.dumps({"url": direct_url}).encode())
                else:
                    self.wfile.write(json.dumps({"error": "Could not extract direct link"}).encode())
        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        return
