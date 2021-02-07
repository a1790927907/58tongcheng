import requests
import execjs
import base64

class Ocr:
    def __init__(self):
        pass


    # 这里是百度的api
    def img_to_word(self,path):
        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=X2znZr6TBc3zCxdzAFi2c6GA&client_secret=39oPBSRlAFFGYADLrKuzLKR2WVLrMOia'
        response = requests.get(host)
        if response:
            data = response.json()

        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
        # 二进制方式打开图片文件
        f = open(path, 'rb')
        img = base64.b64encode(f.read())

        params = {"image": img}
        access_token = data['access_token']
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            try:
                result = response.json()['words_result'][0]['words']
            except:
                # 之后补充数字ocr
                result = '#未识别#'
            return result
        else:
            return '百度api出错'


    # 这里是Bejson网站的api调用
    def img_to_word_api(self,path):
        session = requests.session()
        url = "https://www.bejson.com/chargeservice/ocr/"
        headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
        }
        res = session.get(url, headers=headers)

        url2 = "https://api.bejson.com/Bejson/Api/ImageHandle/upToken"
        res2 = session.post(url2, headers=headers, cookies=res.cookies)

        url3 = "https://up-z2.qiniup.com/?fileapi" + str(execjs.eval('new Date().getTime()'))
        key = 'upload/' + str(execjs.eval('1e17 * Math.random()')) + ".png"
        files = {
            'file': open(path, 'rb')
        }
        data = {
            '_file': path.split('/')[-1],
            'token': res2.json()['data']['token'],
            'key': key
        }

        session.post(url3, data=data, cookies=res2.cookies, headers=headers, files=files)

        result_url = "https://api.bejson.com/Bejson/Api/DistinguishString/ocrFromPicture"
        d = {
            'path': 'https://qntemp3.bejson.com/' + key
        }
        result_res = session.post(result_url, data=d, headers=headers)
        result_data = result_res.json()
        if result_data['code'] == 200:
            if result_data['data']:
                return result_data['data'][0]
            else:
                return '#未识别#'
        else:
            return 'api网站出错'

















