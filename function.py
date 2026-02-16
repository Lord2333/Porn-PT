from bs4 import BeautifulSoup as bs
import re
import requests
import json

class PornPT():
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.ifproxy = False # 开启代理
        self.proxies = {"http": "http://127.0.0.1:10086","https": "http://127.0.0.1:10086"} if self.ifproxy == True else {}
        self.javdb_cookie = {}
        self.dmm_cookie = {}
        self.fc2_cookie = {}


    # JAVDB 检索
    def get_JAVDB_search(self, javCode:str):
        """
        通过番号搜索，并返回结果

        :param javCode: 番号
        :return: 搜索结果
        """
        javDetail = []

        if bool(re.match("^[A-Za-z0-9 _-]*$",javCode.replace(" ",""))): # 检查是否是番号
            search_url = f"https://javdb.com/search?q={javCode}"
        else:
            return "This API can only deal with JAVcode!"

        html = requests.get(search_url, headers=self.headers, proxies=self.proxies).text
        soup = bs(html, 'html.parser')
        javList = soup.find("div", {"class": "movie-list h cols-4 vcols-8"})
        try:
            javCards = javList.find_all("div", {"class": "item"})
        except AttributeError:
            return "The JAVcode does not exist!"
        else:
            for card in javCards:
                card_info = {}
                card = card.find("a")
                card_info["card_url"] = card.get("href").replace("/v/", "")
                card_info["title"] = card.find("div", {"class": "video-title"}).text
                card_info["id"] = re.findall("[a-zA-Z0-9_-]+", card_info["title"])[0]  # 从标题中提取番号
                card_info["ReleasedDate"] = card.find("div", {"class": "meta"}).text.replace("\n","").replace(" ","")
                javDetail.append(card_info)
            return javDetail

    # JAVDB 请求页面
    def get_JAVDB_detailPage(self, pageCode:str):
        """
        直接访问JAVDB详情页面

        :param pageCode: javdb详情页面代码，为了避免用户使用乱七八糟的代理页面，前端匹配到链接后自动提取并传递到后端
        :return: 符合PT格式的详情内容
        """
        video_detail = {}
        url = f"https://javdb.com/v/{pageCode}" # 构造页面链接
        html = requests.get(url,headers = self.headers,proxies = self.proxies).text
        soup = bs(html, 'html.parser')
        page_detail = soup.find("div", {"class": "video-detail"})
        if page_detail:
            video_detail["cover"] = f"https://c0.jdbstatic.com/covers/j0/{pageCode}.jpg"

            video_detail["thumbnails"] = [] # 尝试获取截图
            thumbnails_list = page_detail.find("article", {"class": "message video-panel"})
            thumbnails_links = thumbnails_list.find_all("a")
            i = 0
            for link in thumbnails_links:
                i += 1
                if i <= 2: # 跳过视频预览及封面
                    continue
                video_detail["thumbnails"].append(link.get("href"))

            video_detail["title"] = page_detail.find("strong", {"class": "current-title"}).text
            meta_blocks = page_detail.find("div", {"class": "video-meta-panel"}).find_all("div", {"class": "panel-block"})
            video_detail["ID"] = meta_blocks[0].find("span",{"class":"value"}).text
            video_detail["ReleasedDate"] = meta_blocks[1].find("span",{"class":"value"}).text
            video_detail["Duration"] = meta_blocks[2].find("span",{"class":"value"}).text.replace("分鍾","分")
            video_detail["Maker"] = meta_blocks[3].find("span",{"class":"value"}).text
            if "評分" not in meta_blocks[4].text: # 有系列标签
                video_detail["Series"] = meta_blocks[4].find("span",{"class":"value"}).text
                video_detail["Score"] = meta_blocks[5].find("span",{"class":"value"}).text.replace("\xa0","")
                video_detail["Tags"] = meta_blocks[6].find("span",{"class":"value"}).text.replace("\xa0","").split(",")
                video_detail["Actors"] = meta_blocks[7].find("span",{"class":"value"}).text.replace("\xa0","").replace("\n","").replace(" ","")[:-1].split("♂")
            else:
                video_detail["Series"] = "无"
                video_detail["Score"] = meta_blocks[4].find("span", {"class": "value"}).text.replace("\xa0", "")
                video_detail["Tags"] = meta_blocks[5].find("span", {"class": "value"}).text.replace("\xa0", "").split(",")
                video_detail["Actors"] = meta_blocks[6].find("span", {"class": "value"}).text.replace("\xa0","").replace("\n","").replace(" ", "")[:-1].split("♂")
            return video_detail
        else:
            return "The JAVDB page does not exist!"

    # DMM 检索
    def get_DMM_detailInfo(self, javCode:str, isJAV:bool = True):
        """
        直接调用dmm官方接口，返回格式化后的影片信息（暂时只支持Jav）

        :param javCode: 品番，格式不重要会自动处理
        :param isJAV: 默认为AV，False为里番
        :return:
        """
        video_detail = {}
        headers = self.headers
        headers["content-type"] = "application/json"
        dataForm = {
            "operationName": "ContentPageData",
            "query": "query ContentPageData($id: ID!, $isLoggedIn: Boolean!, $isAmateur: Boolean!, $isAnime: Boolean!, $isAv: Boolean!, $isCinema: Boolean!, $isSP: Boolean!, $shouldFetchRelatedTags: Boolean = false) {\n  ppvContent(id: $id) {\n    ...ContentData\n    __typename\n  }\n  reviewSummary(contentId: $id) {\n    ...ReviewSummary\n    __typename\n  }\n  ...basketCountFragment @include(if: $isSP)\n}\nfragment ContentData on PPVContent {\n  id\n  floor\n  title\n  isExclusiveDelivery\n  releaseStatus\n  description\n  notices\n  isNoIndex\n  isAllowForeign\n  announcements {\n    body\n    __typename\n  }\n  featureArticles {\n    link {\n      url\n      text\n      __typename\n    }\n    __typename\n  }\n  packageImage {\n    largeUrl\n    mediumUrl\n    __typename\n  }\n  sampleImages {\n    number\n    imageUrl\n    largeImageUrl\n    __typename\n  }\n  products {\n    ...ProductData\n    __typename\n  }\n  mostPopularContentImage {\n    ... on ContentSampleImage {\n      __typename\n      largeImageUrl\n      imageUrl\n    }\n    ... on PackageImage {\n      __typename\n      largeUrl\n      mediumUrl\n    }\n    __typename\n  }\n  pricing {\n    lowestEffectivePriceInclusiveTax\n    lowestRegularPriceInclusiveTax\n    sale {\n      name\n      id\n      endAt\n      __typename\n    }\n    pointRewardCampaign {\n      name\n      id\n      endAt\n      promotionId\n      rate\n      __typename\n    }\n    __typename\n  }\n  weeklyRanking: ranking(term: Weekly)\n  monthlyRanking: ranking(term: Monthly)\n  wishlistCount\n  sample2DMovie {\n    highestMovieUrl\n    hlsMovieUrl\n    __typename\n  }\n  sampleVRMovie {\n    highestMovieUrl\n    __typename\n  }\n  ...AmateurAdditionalContentData @include(if: $isAmateur)\n  ...AnimeAdditionalContentData @include(if: $isAnime)\n  ...AvAdditionalContentData @include(if: $isAv)\n  ...CinemaAdditionalContentData @include(if: $isCinema)\n  __typename\n}\nfragment ProductData on PPVProduct {\n  id\n  priority\n  deliveryUnit {\n    id\n    priority\n    streamMaxQualityGroup\n    downloadMaxQualityGroup\n    __typename\n  }\n  pricing {\n    regularPriceInclusiveTax\n    effectivePriceInclusiveTax\n    __typename\n  }\n  expireDays\n  utilizationStatus @include(if: $isLoggedIn)\n  licenseType\n  shopName\n  couponDiscount {\n    coupon {\n      name\n      expirationPolicy {\n        ... on CouponExpirationAt {\n          expirationAt\n          __typename\n        }\n        ... on CouponExpirationDay {\n          expirationDays\n          __typename\n        }\n        __typename\n      }\n      expirationAt\n      minPayment\n      destinationUrl\n      __typename\n    }\n    discountedPriceInclusiveTax\n    __typename\n  }\n  __typename\n}\nfragment AmateurAdditionalContentData on PPVContent {\n  deliveryStartDate\n  duration\n  amateurActress {\n    id\n    name\n    imageUrl\n    age\n    waist\n    bust\n    bustCup\n    height\n    hip\n    relatedContents {\n      id\n      title\n      __typename\n    }\n    __typename\n  }\n  maker {\n    id\n    name\n    __typename\n  }\n  label {\n    id\n    name\n    __typename\n  }\n  genres {\n    id\n    name\n    __typename\n  }\n  makerContentId\n  playableInfo {\n    ...PlayableInfo\n    __typename\n  }\n  __typename\n}\nfragment PlayableInfo on PlayableInfo {\n  playableDevices {\n    deviceDeliveryUnits {\n      id\n      deviceDeliveryQualities {\n        isDownloadable\n        isStreamable\n        __typename\n      }\n      __typename\n    }\n    device\n    name\n    priority\n    isSupported\n    __typename\n  }\n  deviceGroups {\n    id\n    devices {\n      deviceDeliveryUnits {\n        id\n        deviceDeliveryQualities {\n          isStreamable\n          isDownloadable\n          __typename\n        }\n        __typename\n      }\n      isSupported\n      __typename\n    }\n    __typename\n  }\n  vrViewingType\n  __typename\n}\nfragment AnimeAdditionalContentData on PPVContent {\n  deliveryStartDate\n  duration\n  series {\n    id\n    name\n    __typename\n  }\n  maker {\n    id\n    name\n    __typename\n  }\n  label {\n    id\n    name\n    __typename\n  }\n  genres {\n    id\n    name\n    __typename\n  }\n  makerContentId\n  playableInfo {\n    ...PlayableInfo\n    __typename\n  }\n  __typename\n}\nfragment AvAdditionalContentData on PPVContent {\n  deliveryStartDate\n  makerReleasedAt\n  duration\n  actresses {\n    id\n    name\n    nameRuby\n    imageUrl\n    isBookmarked @include(if: $isLoggedIn)\n    __typename\n  }\n  histrions {\n    id\n    name\n    __typename\n  }\n  directors {\n    id\n    name\n    __typename\n  }\n  series {\n    id\n    name\n    __typename\n  }\n  maker {\n    id\n    name\n    __typename\n  }\n  label {\n    id\n    name\n    __typename\n  }\n  genres {\n    id\n    name\n    __typename\n  }\n  contentType\n  relatedWords @skip(if: $shouldFetchRelatedTags)\n  relatedTags(limit: 16) @include(if: $shouldFetchRelatedTags) {\n    ... on ContentTagGroup {\n      tags {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    ... on ContentTag {\n      id\n      name\n      __typename\n    }\n    __typename\n  }\n  makerContentId\n  playableInfo {\n    ...PlayableInfo\n    __typename\n  }\n  __typename\n}\nfragment CinemaAdditionalContentData on PPVContent {\n  deliveryStartDate\n  duration\n  actresses {\n    id\n    name\n    nameRuby\n    imageUrl\n    __typename\n  }\n  histrions {\n    id\n    name\n    __typename\n  }\n  directors {\n    id\n    name\n    __typename\n  }\n  authors {\n    id\n    name\n    __typename\n  }\n  series {\n    id\n    name\n    __typename\n  }\n  maker {\n    id\n    name\n    __typename\n  }\n  label {\n    id\n    name\n    __typename\n  }\n  genres {\n    id\n    name\n    __typename\n  }\n  makerContentId\n  playableInfo {\n    ...PlayableInfo\n    __typename\n  }\n  __typename\n}\nfragment ReviewSummary on ReviewSummary {\n  average\n  total\n  withCommentTotal\n  distributions {\n    total\n    withCommentTotal\n    rating\n    __typename\n  }\n  __typename\n}\nfragment basketCountFragment on Query {\n  legacyBasket @skip(if: $isLoggedIn) {\n    total\n    __typename\n  }\n  basketCount: user @include(if: $isLoggedIn) {\n    ... on Member {\n      ppvBasketItemCount\n      __typename\n    }\n    __typename\n  }\n  __typename\n}",
            "variables": {
                "id": "javCode",
                "isAmateur": False,
                "isAnime": False,
                "isAv": True,
                "isCinema": False,
                "isLoggedIn": False,
                "isSP": False,
                "shouldFetchRelatedTags": True
            }
        }
        dmmAPI = "https://api.video.dmm.co.jp/graphql"

        if bool(re.match("^[A-Za-z0-9_-]*$",javCode.replace(" ",""))): # 检查是否是番号
            javCode = javCode.lower()
            if "-" in javCode: # 尝试修改番号为贩售番号
                javCode = javCode.replace("-","00")
            elif "_" in javCode:
                javCode = javCode.replace("_","00")
            else:
                javCode_num = re.findall(r"\d+",javCode)[0]
                javCode_cha = re.findall(r"[a-zA-Z]+",javCode)[0]
                javCode = f"{javCode_cha}00{javCode_num}"
        else:
            return "This API can only deal with JAVcode"
        dataForm["variables"]["id"] = javCode
        if not isJAV:
            dataForm["variables"]["isAnime"] = True
            dataForm["variables"]["isAv"] = False

        res = requests.post(dmmAPI, json=dataForm, headers=headers, proxies=self.proxies).text
        res_json = json.loads(res)["data"]
        if res_json["ppvContent"]:
            ppvContent = res_json["ppvContent"]
            video_detail["cover"] = ppvContent["packageImage"]["largeUrl"]
            video_detail["thumbnails"] = []
            for thumbnail in ppvContent["sampleImages"]:
                video_detail["thumbnails"].append(thumbnail["largeImageUrl"])
            video_detail["ID"] = ppvContent["id"]
            video_detail["ReleasedDate"] = ppvContent["deliveryStartDate"]
            video_detail["Duration"] = f"{ppvContent["duration"]//60} 分"
            video_detail["Maker"] = ppvContent["maker"]["name"]
            if ppvContent["series"] is not None:
                video_detail["Series"] = ppvContent["series"]["name"]
            else:
                video_detail["Series"] = ""
            video_detail["Score"] = "" # DMM貌似没有评分
            video_detail["Tags"] = []
            for tag in ppvContent["genres"]:
                video_detail["Tags"].append(tag["name"])
            video_detail["Actors"] = []
            if ppvContent["actresses"]:
                for actor in ppvContent["actresses"]:
                    video_detail["Actors"].append(actor["name"])
            return video_detail
        else:
            return "The JAVcode does not exist!"

if __name__ == "__main__":
    ppt = PornPT()
    print(ppt.get_DMM_detailInfo("mukc110"))


    # key = input("请输入番号：")
    # print(f"正在检索番号 {key}")
    # menu = ppt.get_JAVDB_search(key)
    # i = 0
    # if type(menu) is not str:
    #     for item in menu:
    #         i += 1
    #         print(f"{i}. {item["title"]}")
    #         selection = input("请选择(序号)：")
    #         javDB_code = menu[int(selection) - 1]["card_url"]
    #         print(f"正在番号 {menu[int(selection) - 1]["id"]} 影片详情")
    #         print(ppt.get_JAVDB_detailPage(javDB_code))
    # else:
    #     print(menu)


