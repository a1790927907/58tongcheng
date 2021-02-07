import re

class Parser:
    def __init__(self,text,ocr,ocr_c):
        self.text = text
        self.ocr = ocr
        self.ocr_c = ocr_c

    def parse(self):
        font_face = re.findall(r'@font-face\{.*?base64,(.*?)\)', self.text)[0]

        if self.ocr_c.is_in_cache(font_face):
            all_result = self.ocr_c.get_all_cache_result(font_face)
            for unicode,result in all_result.items():
                if unicode.replace('uni', "&#x") in self.text:
                    self.text = self.text.replace(unicode.replace('uni', "&#x")+';', result)

        else:
            all_result = self.ocr_c.create_cache(self.text)
            for unicode,result in all_result.items():
                if unicode.replace('uni', "&#x") in self.text:
                    self.text = self.text.replace(unicode.replace('uni', "&#x")+';', result)

        return self.text








