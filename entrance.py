# 导入Flask类
from flask import Flask
from flask import request
from ocr_cache import OcrCache
from ocr import Ocr
from parser import Parser
# 实例化，可视为固定格式
app = Flask(__name__)

# route()方法用于设定路由；类似spring路由配置
@app.route('/receive',method=['POST'])
def receive():
    data = request.form['data']
    ocr_c = OcrCache()
    ocr_obj = Ocr()
    parser_58 = Parser(data,ocr_obj,ocr_c)
    text = parser_58.parse()
    return text

if __name__ == '__main__':
    # app.run(host, port, debug, options)
    # 默认值：host="127.0.0.1", port=5000, debug=False
    app.run(host="0.0.0.0", port=5000)










