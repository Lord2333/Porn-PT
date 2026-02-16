from flask import Flask,request
from function import PornPT
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)
ppt = PornPT()

@app.route('/api/javdbSearch', methods=["GET"])
def javdbSearch():
    """
        JAVDB 查询番号
        ---
        tags:
            - JAVDB
        parameters:
            -   name: javCode
                in: query
                type: string
                required: true
                description: jav番号，如JUFE-590
        responses:
            200:
                description: 请求成功
            400:
                description: 番号格式错误
        """
    javCode = request.args.get('javCode', type=str)
    if javCode:
        return {"code": 200, "javResult": ppt.get_JAVDB_search(javCode)}
    else:
        return {"code": 400, "msg": "没番号你找个寄吧！"}

@app.route('/api/javdbPage', methods=["GET"])
def javdbPage():
    """
        JAVDB 详情数据获取
        ---
        tags:
            - JAVDB
        parameters:
            -   name: pageCode
                in: query
                type: string
                required: true
                description: javdb详情页面代码，如RkY648
        responses:
            200:
                description: 请求成功
            400:
                description: 页面代码错误
    """
    pageCode = request.args.get('pageCode', type=str)
    if pageCode:
        return {"code": 200, "searchResult": ppt.get_JAVDB_detailPage(pageCode)}
    else:
        return {"code": 400, "msg": "填错了！重来！"}

@app.route('/api/dmm', methods=["GET"])
def dmm():
    """
        DMM 详情数据获取
        ---
        tags:
            - DMM
        parameters:
            -   name: javCode
                in: query
                type: string
                required: true
                description: jav番号，如JUFE-590
            -   name: ifJAv
                in: query
                type: boolean
                required: true
                description: 是否为jav，后续将支持里番搜索
        responses:
            200:
                description: 请求成功
            400:
                description: 页面代码错误
    """
    javCode = request.args.get('javCode', type=str)
    ifJAv = request.args.get('ifJAv', type=bool)
    return ppt.get_DMM_detailInfo(javCode, ifJAv)

if __name__ == "__main__":
    app.run(debug=True, port=4399)
