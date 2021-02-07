from ocr import Ocr
import re
from font2img import ParseTTFont
from fontTools.ttLib import TTFont
import base64,io
import time,hashlib,os
import json
from S3Client import AWSPersistor

class OcrCache:
    CACHE_ROOT_PATH = './cache'
    CACHE_FILE_NAME = 'words_cache.json'
    FONT_DATA_PATH = './font_data'
    IMG_DATA_PATH = './img_data'
    def __init__(self):
        pass


    # 用于创建缓存，调用一次创建一个缓存，返回缓存的key以及value
    def create_cache(self,text):
        o = Ocr()

        font_face = re.findall(r'@font-face\{.*?base64,(.*?)\)', text)[0]
        onlineFront = TTFont(io.BytesIO(base64.b64decode(font_face)))
        with open(os.path.join(self.CACHE_ROOT_PATH,self.CACHE_FILE_NAME),'r') as f:
            try:
                words_cache = json.loads(f.read())
            except:
                words_cache = {}

        font_md5 = hashlib.md5(font_face.encode()).hexdigest()
        if font_md5 in list(words_cache.keys()):
            return
        else:
            words_cache[font_md5] = {}

        # 随机保存为ttf文件，文件名不能重复，这里的save操作在之后加入缓存的时候，如果命中缓存，则不去save，对应的文件名需要保存在json里
        # 文件名保存是为了之后识别数字之后方便修改
        file_name = '58' + font_md5[:19] + '.ttf'
        onlineFront.save(os.path.join(self.FONT_DATA_PATH,file_name))  # 保存为字体格式的文件

        font = ParseTTFont(os.path.join(self.FONT_DATA_PATH,file_name))
        all_unicode = font.get_glyphnames()[2:]
        for unicode in all_unicode:
            im = font.one_to_image(unicode)
            img_file_name = hashlib.md5(str(time.time()).encode()).hexdigest() + '.png'
            im.save(os.path.join(self.IMG_DATA_PATH,img_file_name))
            result = o.img_to_word_api(os.path.join(self.IMG_DATA_PATH,img_file_name))
            os.remove(img_file_name)
            words_cache[font_md5][unicode] = result
            time.sleep(0.5)

        words_cache[font_md5]['file_name'] = file_name
        with open(os.path.join(self.CACHE_ROOT_PATH, self.CACHE_FILE_NAME), 'w') as f1:
            f1.write(json.dumps(words_cache))
            
        persistor = AWSPersistor('mesoor-ocr')
        persistor.upload(os.path.join(self.CACHE_ROOT_PATH, self.CACHE_FILE_NAME),'58tongcheng/test.json')

        return font_md5,words_cache[font_md5]


    # 之后可以使用这个编辑缓存
    def edit_cache(self):
        o = Ocr()
        with open('./cache/words_cache.json','r') as f:
            data = json.loads(f.read())
        data_copy = data.copy()
        for key,val in data_copy.items():
            file_name = val['file_name']
            font = ParseTTFont(os.path.join(self.FONT_DATA_PATH,file_name))
            for k,v in val:
                # k是unicode,v是对应的识别值
                im = font.one_to_image(k)
                img_file_name = hashlib.md5(str(time.time()).encode()).hexdigest() + '.png'
                im.save(os.path.join(self.IMG_DATA_PATH, img_file_name))
                # 这里可以使用修改之后的ocr
                # result = o.img_to_word_api(os.path.join(self.IMG_DATA_PATH, img_file_name))
                # data[key][k] = result
                os.remove(img_file_name)


    def is_in_cache(self,font_face):
        with open('./cache/words_cache.json','r') as f:
            data = json.loads(f.read())
        j = True if hashlib.md5(font_face.encode()).hexdigest() in list(data.keys()) else False
        return j


    # 暂时未用到
    def get_one_cache_result(self,unicode,font_face):
        with open('./cache/words_cache.json','r') as f:
            data = json.loads(f.read())
        font_md5 = hashlib.md5(font_face.encode()).hexdigest()
        return data[font_md5][unicode]


    def get_all_cache_result(self,font_face):
        with open('./cache/words_cache.json','r') as f:
            data = json.loads(f.read())
        font_md5 = hashlib.md5(font_face.encode()).hexdigest()
        return data[font_md5]


    # 暂时未用到
    def get_file_name(self,font_face):
        with open('./cache/words_cache.json','r') as f:
            data = json.loads(f.read())
        font_md5 = hashlib.md5(font_face.encode()).hexdigest()
        return os.path.join(self.FONT_DATA_PATH,data[font_md5]['file_name'])








