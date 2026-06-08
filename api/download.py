from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import urllib.request

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
            # هنا الخدعة: كنصيفطو الطلب لـ API قوي ومحمي ضد البلوك ديال يوتيوب وسط السيرفر ديالنا
            api_endpoint = "https://api.cobalt.tools/api/json"
            req_data = json.dumps({
                "url": video_url,
                "vQuality": "720",
                "isAudioOnly": False
            }).encode('utf-8')

            req = urllib.request.Request(
                api_endpoint, 
                data=req_data, 
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                }
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.parse(response.read().decode('utf-8'))
                
                if res_data and 'url' in res_data:
                    # كنرجعو الرابط المباشر للواجهة ديالنا
                    self.wfile.write(json.dumps({"url": res_data['url']}).encode())
                else:
                    self.wfile.write(json.dumps({"error": "تعذر استخراج الرابط، جرب لاحقاً"}).encode())

        except Exception as e:
            # خطة احتياطية قوية ومجربة لتفادي كاع أنواع الحماية
            try:
                backup_url = f"https://co.wuk.sh/api/json"
                req_data_backup = json.dumps({"url": video_url}).encode('utf-8')
                req_backup = urllib.request.Request(
                    backup_url, 
                    data=req_data_backup, 
                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'}
                )
                with urllib.request.urlopen(req_backup, timeout=10) as response_backup:
                    res_backup = json.loads(response_backup.read().decode('utf-8'))
                    if res_backup and 'url' in res_backup:
                        self.wfile.write(json.dumps({"url": res_backup['url']}).encode())
                        return
            except:
                pass
                
            self.wfile.write(json.dumps({"error": "السيرفر واجه حماية مؤقتة، يرجى إعادة المحاولة برابط آخر"}).encode())
        return
