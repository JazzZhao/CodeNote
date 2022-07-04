import string
import requests
from lxml import etree
import re
import json
import pandas as pd
import base64
import urllib
import time
import os



def write_json(video_name_list):
    with open("video_name_list.json","w", encoding='utf-8') as f:
        json.dump(video_name_list,f)
        print("加载入文件完成...")

def read_json():
    if os.path.exists('video_name_list.json'):
        with open("video_name_list.json",'r', encoding='utf-8') as load_f:
            load_dict = json.load(load_f)
            return load_dict

def del_file():
    os.remove('video_name_list.json')

def json_decode(json_str):#传入json字符串，递归解析成列表或者字典
    import json
    ret=None
    '''
    1.判断传入字符串是否是合法json string
    2.是 json，返回解析结果；递归迭代元素
    3.非 json，原样返回字符串
    '''
    try:
        ret=json.loads(json_str)
        if(isinstance(ret,dict)):
            for x in ret:
                ret[x]=json_decode(ret[x])
        elif(isinstance(ret,list)):
            for x in range(len(ret)):
                ret[x]=json_decode(ret[x])
        return ret
    except:
        return json_str

#神马的解码
def url_decode(url_encode):
    video_url = ""
    i = 0
    while(i < len(url_encode)):
        tmp = url_encode[i]
        if tmp == '+':
            video_url += ' '
            i += 1
        else :
            if tmp == '%':
                sub_tmp = url_encode[i + 1:i + 3]
                if int(('0x' + sub_tmp), 16) > 127:
                    video_url += urllib.parse.unquote('%' + sub_tmp + url_encode[i + 3: i + 9])
                    i += 8
                else:
                    video_url += chr(int(('0x' + sub_tmp), 16))
                    i += 2
            else:
                video_url += tmp
                i += 1
    return video_url

#神马获取地址
def get_sm_url(video_name_list):
    for video_name in video_name_list:
        downed_num = len(video_name['playlist'])
        sm_url = video_name.get('url')
        sm_root_url = sm_url.split("/k")[0]
        try:
            response_sm_search = requests.get(sm_url).text
        except:
            print('请求神马网站报报错')
            return 0
        html_sm_search = etree.HTML(response_sm_search)
        title_list = html_sm_search.xpath("//ul[@class='stui-content__playlist clearfix']")
        if len(title_list)>1:
            tmp = title_list[0]
            src_list = tmp.xpath(".//a/@href")
            text_list = tmp.xpath(".//a/text()")
            while downed_num < len(src_list):
                src = src_list[downed_num]
                #请求网站的剧集地址
                print(f"开始请求神马剧集网址{src}")
                try:
                    normal_url_response = requests.get(sm_root_url+src).text
                except:
                    print("请求神马剧集网址报错了")
                    return 0
                html_normal_url = etree.HTML(normal_url_response)
                script_list = html_normal_url.xpath("//script/text()")
                script = list(filter(lambda x: ("player_aaaa" in x ),script_list))[0]
                script = script.split("=")[1]
                tmp_url = json.loads(script).get('url')
                #请求解析网站
                response_token = requests.get('https://player.6080kan.cc/player/play.php?url='+tmp_url).text
                token_tree = etree.HTML(response_token)
                script_list = token_tree.xpath("//script/text()")
                jiami_url = re.findall("url\": \"(.*)\",\\n            \"vkey", script_list[0])[0]
                vkey = re.findall("vkey\": \"(.*)\",\\n            \"nexturl", script_list[0])[0]
                token = re.findall("token\": \"(.*)\"\\n        }", script_list[0])[0]
                print(token)
                #搜索url
                data = {
                    "url": jiami_url,
                    "vkey":vkey,
                    "token":token,
                    "sign":"D4GE4tm2Q3NXbeeK",
                }
                response_search = requests.post('https://player.6080kan.cc/player/hd0L3TjH4m8zSK1N.php', data=data).text
                jiami_url = json.loads(response_search).get('url')
                sub_jiami_url = jiami_url[8: len(jiami_url)]
                base64_result = base64.b64decode(bytes(sub_jiami_url, encoding='utf-8')).decode()
                url_encode = base64_result[8:len(base64_result)-8]
                url_result = url_decode(url_encode)
                player = {"src":url_result, "title":text_list[src_list.index(src)]}
                video_name['playlist'].append(player)
                print(f"剧名：{video_name.get('title')},剧集名字：{text_list[src_list.index(src)]}")
                downed_num += 1
                time.sleep(6)
    return video_name_list

def post_list(url):
    try:
        return requests.post(url).text
    except:
        print("请求miaomu剧集网址报错了")
        time.sleep(60)
        return 0

# miaomu网站解析
def get_miaomu_video_name(video_name_list):
    jiexi_url = 'https://p1397.mmlllasjd.com/?url='
    url = 'https://www.1miaomu.com'
    jiexi_header = {
        "authority":"p1397.mmlllasjd.com",
        "referer":"https://www.1miaomu.com/"
    }
    #获取剧集信息
    for video_name in video_name_list:
        if isinstance(video_name, str):
            video_name = json.loads(video_name)
        downed_num = len(video_name['playlist'])
        video_url = video_name.get("url")
        print(f"请求miaomu网址{video_url}")
        try:
            response_video = requests.post(video_url).text
        except:
            print("请求miaomu网址报错了")
            time.sleep(60)
            return 0
        html_video = etree.HTML(response_video)
        title_tmp = html_video.xpath("//ul[@class='stui-content__playlist clearfix']")
        if len(title_tmp)>0:
            tmp = title_tmp[0]
            src_list = tmp.xpath(".//a/@href")
            text_list = tmp.xpath(".//a/text()")
            while downed_num < len(src_list):
                src = src_list[downed_num]
                #请求网站的剧集地址
                print(f"请求miaomu剧集网址{src}")
                normal_url_response = 0
                while normal_url_response == 0:
                    normal_url_response = post_list(url+src)
                html_normal_url = etree.HTML(normal_url_response)
                script_list = html_normal_url.xpath("//script/text()")
                script = list(filter(lambda x: ("player_aaaa" in x ),script_list))[0]
                script = script.split("=")[1]
                normal_url = json.loads(script).get('url')
                #请求解析网站
                print(f"请求解析网址{normal_url}")
                try:
                    jiexi_response = requests.get(jiexi_url+normal_url,headers=jiexi_header,timeout=10).text
                except:
                    print("请求解析网址出错！")
                    time.sleep(60)
                    return 0
                html_jiexi = etree.HTML(jiexi_response)
                script_jiexi_list = html_jiexi.xpath("//script/text()")
                jiexi_string = list(filter(lambda x: ("vip" in x ),script_jiexi_list))[0]
                vip_url = re.findall(".*vip = \'(.*)\'.*", jiexi_string)[0]
                if vip_url != 'null':
                    player = {"src":vip_url, "title":text_list[src_list.index(src)]}
                    video_name['playlist'].append(player)
                    print(f"剧名：{video_name.get('title')},剧集名字：{text_list[src_list.index(src)]}")
                    print(vip_url)
                    downed_num += 1
                    time.sleep(120)  
    return video_name_list

def main():
    input = "梦华录"
    video_name_list = read_json()
    #获取认证码
    appid = 'wxd397424bab866bd4'
    appsecret = 'e21e94dabdcd16c4a9a4432b2c92d22e'
    result = requests.get("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid="+appid+"&secret="+appsecret)
    access_token = json.loads(result.text).get('access_token')
    if video_name_list == None:
        #查询数据
        data_get = json.dumps({"env":"resource-3g78bp0u80d3979b","query": "db.collection('video_name').where({title: '"+input+"'}).limit(1).get()"})
        reponse_get = requests.post("https://api.weixin.qq.com/tcb/databasequery?access_token="+access_token, data=data_get)
        video_name_list = json.loads(reponse_get.text).get('data')
    # if video_name_list == None :
    #     input = "梦华录"
    #     root_url = "https://www.cupfox.app"
    #     search_url = root_url+"/search?key="
    #     response_search = requests.get(search_url+input).text
    #     html_search = etree.HTML(response_search)
    #     video_name_list = []
    #     sm_url_list = list(filter(lambda x: ("smdyy" in x ),html_search.xpath("//a/@href")))
    #     for sm_url in sm_url_list:
    #         video_name = {"title":html_search.xpath("//title/text()")[0],"url":(sm_url), "playlist":[], "src":''}
    #         video_name_list.append(video_name)
    #根URL
    while len(video_name_list) == 0 :
        url = 'https://www.1miaomu.com'
        #搜索url
        search_url = url+'/f.html'
        params = {
            "wd": input
        }
        try:
            response_search = requests.post(search_url, params=params).text
        except:
            print("搜索出错！")
            time.sleep(60)
            continue
        #解析搜索html
        html_search = etree.HTML(response_search)
        title_search = html_search.xpath("//ul[@class='stui-vodlist clearfix']")
        if len(title_search)>0:
            for tmp in  title_search[0].xpath(".//a[@class='stui-vodlist__thumb lazyload']"):
                video_name = {"title":tmp.xpath("@title")[0],"url":(url +tmp.xpath("@href")[0]), "coverImgUrl":url+tmp.xpath("@data-original")[0], "playlist":[], "src":""}
                video_name_list.append(video_name)
    flag = 0
    while flag == 0:
        flag = get_miaomu_video_name(video_name_list)
        write_json(video_name_list)
    #删除数据库数据
    data = json.dumps({"env":"resource-3g78bp0u80d3979b","query": "db.collection('video_name').where({title: '"+input+"'}).remove()"})
    response_del = requests.post("https://api.weixin.qq.com/tcb/databasedelete?access_token="+access_token, data=data)
    #插入数据
    data_add = json.dumps({"env":"resource-3g78bp0u80d3979b","query": 'db.collection("video_name").add({"data": '+json.dumps(video_name_list)+'})'})
    reponse_add = requests.post("https://api.weixin.qq.com/tcb/databaseadd?access_token="+access_token, data=data_add)
    del_file()



if __name__ == "__main__":
    main()