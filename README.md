# PornPT API 项目

![GitHub last commit](https://img.shields.io/github/last-commit/Lord2333/Porn-PT)


## 1. 项目简介
这个项目是为了给rousi.pro的9KG板块添加一个类似于豆瓣/IMDb影片链接解析功能的后端实现，目前实现了对于**正规出版**的JAV的解析，由于蚊香社的骚操作不在DMM售卖了，所以同时提供了DMM的官方接口和JavDB的网页作为补充数据源，针对PT站的使用场景对接口的返回信息进行了格式化处理，使得输出内容方便辨认。

## 2. 部署方法

### 2.1 环境要求
*   Python 3.x
*   网络环境（需自备代理，DMM接口需要干净的IP，否则会被阻断）

### 2.2 安装依赖
请确保安装了所需的 Python 库。您可以直接运行以下命令：

```bash
pip install -r requirements.txt
```

### 2.3 配置说明
如果需要使用代理，请修改 `function.py` 中的 `__init__` 方法：

```python
# function.py
self.ifproxy = True # 将 False 改为 True 开启代理
self.proxies = {
    "http": "http://127.0.0.1:10086", # 修改为你实际的代理地址
    "https": "http://127.0.0.1:10086"
}
```

### 2.4 启动项目
在项目根目录下运行：

```bash
python app.py
```

项目默认运行在 `http://127.0.0.1:4399`。

## 3. API 调用

本项目集成了 **Swagger UI**，启动项目后访问以下地址可查看可视化文档并进行在线调试：
*   **文档地址**: `http://127.0.0.1:4399/apidocs/`

### 3.1 接口列表

#### 3.1.1. JAVDB 番号查询
*   **接口地址**: `/api/javdbSearch`
*   **请求方式**: `GET`
*   **描述**: 通过番号搜索影片，获取详情页代码（pageCode）。
*   **参数**:
    *   `javCode` (string, 必填): 影片番号，例如 `JUFE-590`。

#### 3.1.2. JAVDB 详情获取
*   **接口地址**: `/api/javdbPage`
*   **请求方式**: `GET`
*   **描述**: 根据详情页代码获取影片详细信息（封面、磁链、演员等）。
*   **参数**:
    *   `pageCode` (string, 必填): JAVDB详情页的唯一标识码，例如 `RkY648`（通常从搜索接口获取）。

#### 3.1.3. DMM 详情获取
*   **接口地址**: `/api/dmm`
*   **请求方式**: `GET`
*   **描述**: 调用 DMM 官方接口获取影片详情。
*   **参数**:
    *   `javCode` (string, 必填): 影片番号。
    *   `ifJAv` (boolean, 必填): 是否为 AV 作品（`true` 为 AV，`false` 为动画/里番）。

## 4. Todolist
- 里番番号解析 
- FC2番号解析
- 数据库缓存
- 接口加盐

## 5. 更新日志
- 2026年2月16日

  上传首个版本，实现了对于正规出版的JAV的检索和信息获取。
