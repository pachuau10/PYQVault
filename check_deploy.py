import requests, re
r = requests.get('https://pyqvault-five.vercel.app/')
print('Status:', r.status_code)
m = re.search(r'href="([^"]*css[^"]*)"', r.text)
if m: print('CSS:', m.group(1))
m = re.search(r'<script[^>]*src="([^"]+js)"[^>]*>', r.text)
if m: print('JS:', m.group(1))
# Check if CSS loads
css_resp = requests.get('https://pyqvault-five.vercel.app/static/css/style.css')
print('CSS status:', css_resp.status_code, len(css_resp.content))
# Check JS
js_resp = requests.get('https://pyqvault-five.vercel.app/static/js/main.js')
print('JS status:', js_resp.status_code, len(js_resp.content))
