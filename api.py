import urllib3
import json
from PIL import Image
import io
import base64

http = urllib3.PoolManager()


def pil_to_b64(img):
    img_byte = io.BytesIO()
    img.save(img_byte, format="png")
    return base64.b64encode(img_byte.getvalue()).decode()

def b64_to_pil(img_b64):
    raw_image = base64.b64decode(img_b64.encode('utf8'))
    return Image.open(io.BytesIO(raw_image))


def getText(url, img):
    img_b64 = pil_to_b64(img)
    body ='{ "img": "' + img_b64 + '"}'
    method = 'POST'
    r = http.request(method, url, body=body, headers={'Content-Type': 'application/json'})
    data = json.loads(r.data.decode('utf-8')) #, ensure_ascii=False))
    data = data['data']
    return data

def getParsedImage(url, img, data):
    img_b64 = pil_to_b64(img)
    data = json.dumps(data, ensure_ascii=False)
    body ='{ "img": "' + img_b64 + '", "data": ' +data+'}'
    body=body.encode('utf-8')
    method = 'GET'
    r = http.request(method, url, body=body, headers={'Content-Type': 'application/json'})
    data = json.loads(r.data.decode('utf-8'))
    img_b64 = data['data']
    img_pil = b64_to_pil(img_b64)
    return img_pil


if __name__ == "__main__":
    url = "http://localhost:8090/api/tr-run/"
    img_path =  "imgs/id_card.jpeg"
    img = Image.open(img_path)
    data = getText(url, img)
    img_pil = getParsedImage(url, img, data)
    img_pil.save('/tmp/img.png')
