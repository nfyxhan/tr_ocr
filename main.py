# -*- coding: utf-8 -*-
import tr
import sys, cv2, time, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
_BASEDIR = os.path.dirname(os.path.abspath(__file__))

import tornado.web
import tornado.httpserver
import tornado.ioloop
import json
import base64
from io import BytesIO


import logging
from logging.handlers import RotatingFileHandler
import datetime
logger = logging.getLogger("tr" + '.' + __name__)
logger.setLevel(logging.INFO)
# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] | %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

logfile_name = datetime.date.today().__format__('%Y-%m-%d.log')
logfile_path = os.path.join(_BASEDIR, f'logs/')
if not os.path.exists(logfile_path):
    os.mkdir(logfile_path)
handler_logfile = RotatingFileHandler(logfile_path + logfile_name, maxBytes=1 * 1024 * 1024, backupCount=3, encoding="utf-8")
handler_logfile.setLevel(logging.INFO)
handler_logfile.setFormatter(formatter)
logger.addHandler(handler_logfile)

#console_output = logging.StreamHandler()
#console_output.setLevel(logging.INFO)
#console_output.setFormatter(formatter)
#logger.addHandler(console_output)



os.chdir(_BASEDIR)
settings = dict(
)


def rotate(x1,y1, x2, y2, a):
    x = (x1 - x2)*math.cos(math.pi / 180.0 * a) - (y1 - y2)*math.sin(math.pi / 180.0 * a) + x2; 
    y = (x1 - x2)*math.sin(math.pi / 180.0 * a) + (y1 - y2)*math.cos(math.pi / 180.0 * a) + y2; 
    return x, y

def pre_run(img_pil):
    try:
        if hasattr(img_pil, '_getexif'):
            # from PIL import ExifTags
            # for orientation in ExifTags.TAGS.keys():
            #     if ExifTags.TAGS[orientation] == 'Orientation':
            #         break
            orientation = 274
            exif = dict(img_pil._getexif().items())
            if exif[orientation] == 3:
                img_pil = img_pil.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img_pil = img_pil.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img_pil = img_pil.rotate(90, expand=True)
    except:
        pass

    MAX_SIZE = 1600
    if img_pil.height > MAX_SIZE or img_pil.width > MAX_SIZE:
        scale = max(img_pil.height / MAX_SIZE, img_pil.width / MAX_SIZE)
        new_width = int(img_pil.width / scale + 0.5)
        new_height = int(img_pil.height / scale + 0.5)
        img_pil = img_pil.resize((new_width, new_height), Image.ANTIALIAS)
    gray_pil = img_pil.convert("L")
    color_pil = img_pil.convert("L")
    return gray_pil, color_pil

#def run(gray_pil):
#    t = time.time()
#    width, height = gray_pil.size
#    print("size", gray_pil.size)
##    text = tr.recognize(gray_pil) #, flag=tr.FLAG_ROTATED_RECT)
##    print("text", text)
#    results = tr.detect(gray_pil, flag=tr.FLAG_ROTATED_RECT)
#    print("detect",results)
#    for i, rect in enumerate(results):
#        # todo rect[4] 
#        w, h = rect[2], rect[3]
#        x1, y1 = width/2, height/2
#        x2, y2 = rect[0]-w/2, rect[1]-h/2
#        a = rect[4]
#        x, y = rotate(x1, y1, x2, y2, a)
#        box = (x, y, x+w, y+h) 
#        sub_pil = gray_pil.rotate(a, expand=True).crop(box)
#        #sub_pil.save("imgs/run/"+str(i)+".png")
#        text = tr.recognize(sub_pil) #, flag=tr.FLAG_ROTATED_RECT)
#        print(i, text)
#    print("time", (time.time() - t))
#    return 

def run(gray_pil):
    t = time.time()
    results = tr.run(gray_pil, flag=tr.FLAG_ROTATED_RECT)
    logger.debug("result", results)
    result = []
    for i, rect in enumerate(results):
        if len(rect[1]) == 0:
            continue
        if rect[2] < 0.5:
            continue
        result.append(rect)
    return result

def compare(img_pil, results):
    color_pil = img_pil.copy()
    img_draw = ImageDraw.Draw(color_pil)
    colors = ['red', 'green', 'blue', "purple"]
    for i, rect in enumerate(results):
        cx, cy, w, h, a = tuple(rect[0])
#        print(i, "\t", rect[1], rect[2], rect[0])
        box = cv2.boxPoints(((cx, cy), (w, h), a))
        box = np.int0(np.round(box))
        for p1, p2 in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            img_draw.line(xy=(box[p1][0], box[p1][1], box[p2][0], box[p2][1]), fill=colors[i % len(colors)], width=2)
    return color_pil

class tr_run(tornado.web.RequestHandler):
    def get(self):
        self.set_status(404)
        self.write("404 : Please use POST")

    @tornado.gen.coroutine
    def post(self):
        t = time.time()
        img_up = self.request.files.get('file', None)
        r = json.loads(self.request.body)
        img_b64 = r.get('img', None)
        img_pil = None
        if img_up is not None and len(img_up) > 0:
            img_up = img_up[0]
            up_image_type = img_up.content_type
            up_image_name = img_up.filename
            img_pil = Image.open(BytesIO(img_up.body))
        elif img_b64 is not None:
            raw_image = base64.b64decode(img_b64.encode('utf8'))
            img_pil = Image.open(BytesIO(raw_image))
#        else:
#            img_path = "imgs/ch2.png"
#            img_path = "imgs/ch.png"
        #    img_path = "imgs/id_card.jpeg"
#            img_pil = Image.open(img_path)
        if img_pil is None:
            logger.error(json.dumps({'code': 400, 'msg': u'没有传入参数'}, ensure_ascii=False))
            self.finish(json.dumps("img is none", cls=NpEncoder))
            return 
        logger.info(img_pil.size)
        gray_pil, color_pil = pre_run(img_pil)
    #    run(gray_pil)
        results = run(gray_pil)
        result =  {
               'code': 200, 
               'data': results,
               "cost": time.time()-t,
        }
        logger.info(json.dumps(result, cls=NpEncoder, ensure_ascii=False))
        self.finish(json.dumps(result, cls=NpEncoder, ensure_ascii=False))

#        img_draw = compare(color_pil, results)
#        img_draw.save("imgs/result.png")

        return

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

def make_app(port):
    app = tornado.web.Application([
        (r"/api/tr-run/", tr_run),

    ], **settings)

    server = tornado.httpserver.HTTPServer(app)
    # server.listen(port)
    server.bind(port)
    server.start(1)
    print(f'Server is running: http://0.0.0.0:{port}')

    # tornado.ioloop.IOLoop.instance().start()
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    result = tr.recognize("imgs/line.png"))
    print(result[1])
    make_app(8090)
