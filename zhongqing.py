from datetime import datetime
from datetime import timedelta
from operator import truediv
from pathlib import Path
from sys import flags
from webbrowser import get
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time
import os
import threading

class Utils:
    def __init__(self, driver=None):
        self.driver = driver
        #搜索页的关键词
        self.search = ['百度一下','搜狗搜索','javascript:;']

    def getSize(self):                               #获取当前的width和height的x、y的值
        x = self.driver.get_window_size()['width']   #width为x坐标
        y = self.driver.get_window_size()['height']  #height为y坐标
        return (x, y)

    def swipeUp(self,start_x=0.5, start_y=0.75, end_y=0.25, t=1000):  #当前向上滑动swipeup
        l = self.getSize()
        x1 = int(l[0] * start_x)  
        y1 = int(l[1] * start_y)   
        y2 = int(l[1] * end_y)   
        self.driver.swipe(x1, y1, x1, y2, t)  #设置时间为500

    def swipLeft(self, t):      #当前向左进行滑动swipleft
        l=self.getSize()
        x1=int(l[0]*0.75)
        y1=int(l[1]*0.5)
        x2=int(l[0]*0.05)
        self.driver.swipe(x1,y1,x2,y1, t)

    def swipeDown(self,start_x=0.5, start_y=0.25, end_y=0.75, t=1000):    #向下滑动swipedown
        l = self.getSize()
        x1 = int(l[0] * start_x)
        y1 = int(l[1] * start_y)
        y2 = int(l[1] * end_y)
        self.driver.swipe(x1, y1, x1, y2, t)

    def swipRight(self, t): #向右滑行swipright
        l=self.getSize()
        x1=int(l[0]*0.05)
        y1=int(l[1]*0.5)
        x2=int(l[0]*0.75)
        self.driver.swipe(x1,y1,x2,y1, t)

    #比较页面有没有变化
    def is_similar(self):
        before_page = self.driver.page_source
        time.sleep(10)
        after_page = self.driver.page_source
        return before_page == after_page

    #检查页面特征
    def check_page(self, feature = "javascript:;"):
        return (feature in self.driver.page_source)

    #在搜索页面来回划动防止自动刷新
    def up_down_roll(self, num):
        # tmp = 1
        for i in range(num):
            self.swipeUp(start_y=0.55, end_y=0.5, t=0)
            self.swipeDown(start_y=0.5, end_y=0.55, t=0)
        # time.sleep(2)
        # self.swipeUp(start_y=0.55, end_y=0.5, t=0)
        # self.swipeDown(start_y=0.5, end_y=0.55, t=0)
        # time.sleep(num-3)
        # self.swipeUp(start_y=0.55, end_y=0.5, t=0)
        # self.swipeDown(start_y=0.5, end_y=0.55, t=0)
    #####获取广告的图片######
    def get_images(self):
        #获取图片链接
        images = self.driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Image")
        if len(images) == 0:
            #使用content-desc来获取
            images = self.driver.find_elements(by=AppiumBy.XPATH, value = "//*[contains(@content-desc, 'sogou')]")
        return images

    #####普通看看赚处理######
    def common_kan(self, time_wait, no_image_flag, no_back_flag):
        one_num = 0
        while one_num < 2:
            print(f"=====等待{time_wait}s=====")
            # self.swipeUp(start_y=0.55, end_y=0.5, t=0)
            # self.swipeDown(start_y=0.5, end_y=0.55, t=0)
            # time.sleep(time_wait)
            self.up_down_roll(time_wait)
            if no_image_flag:
                print("=====无图片处理成功=====")
                if not self.common_kan_no_image():
                    return False
            elif not no_back_flag:
                print("=====获取图片=====")
                images = self.get_images()
                if len(images) == 0:
                    print("=====没有图片=====")
                    print("=====开始划动=====")
                    #开始上下滑动
                    self.up_down_roll(8)
                    return False 
                if one_num>= len(images):
                    images[len(images)-1].click()
                else:
                    images[one_num].click()
            one_num = one_num + 1
            print("=====开始划动=====")
            #开始上下滑动
            self.up_down_roll(8)
            #返回
            if (not self.check_page('看看赚')):
                print("=====页面返回=====")
                self.driver.back()
        return True

    #####无图片的看看赚点击处理######
    def common_kan_no_image(self):
        print("=====进入无图片处理=====")
        print("=====刷新=====")
        try:
            self.driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/t0").click()
            # time.sleep(0.5)
            # self.driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/akp").click()
            time.sleep(2)
        except Exception as e:
            print("=====无法获取刷新=====")
            if not self.check_page('看看赚'):
                self.driver.back()
            return False
        l=self.getSize()
        x1=int(l[0]*0.5)
        y1=int(l[1]*0.5)
        #点击中间
        self.driver.tap([(x1, y1)])
        return True

    #需要等待的标题
    def get_wait_title(self):
        return ['今日看点','八卦资讯','今日热讯',"看点","神马广告"]
    #有次首页的标题，需要
    def get_secondary_title(self):
        return ['非凡资讯']
    #搜索标题的处理
    def get_search_title(self):
        return ['搜索']
    #进来先点关闭按键的标题
    def get_close_title(self):
        return []
    #无法定位图片，需要点击的标题
    def get_click_title(self):
        return ['今日资讯']
    #跳过的标题
    def get_jump_title(self):
        return ['手机乐视_乐视视频,...', '网页无法打开','一点生活趣事','标点资讯','今日热讯','今日看点','灵异岛新闻','10754-标点资讯','今日导播',"每日播报","每日新闻"]

    #需要先点击
    def get_click_title(self):
        return ['巨资','尚瑞咨询',"尚瑞健康咨询"]

#加载APP
def load_driver(device_ip):
    # 会话配置
    desired_caps = {
            "platformName":"Android",
            "platformVersion":"7.1.2",
            "deviceName":device_ip,
            "appPackage":"cn.youth.news",
            "udid":device_ip,
            "appActivity":"cn.youth.news.ui.splash.SplashActivity",
            "noReset": True
    }
    return webdriver.Remote("http://127.0.0.1:4723/wd/hub",desired_caps)
#赚赚看
def browse_look(driver, device_ip):
    print("=====开始浏览看看赚=====")
    utils = Utils(driver)
    #点击任务列表
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/ui").click()
    time.sleep(5)
    #点击看看赚
    print("=====点击看看赚=====")
    driver.find_element(by=AppiumBy.XPATH, value = "//*[contains(@text, '看看赚')]").click()
    time.sleep(30)
    print("=====页面返回=====")
    driver.back()
    if (utils.check_page(feature = "关闭")):
        print("=====点击关闭=====")
        driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/afv").click()
    time.sleep(20)
    print("=====点击看看赚=====")
    driver.find_element(by=AppiumBy.XPATH, value = "//*[contains(@text, '看看赚')]").click()
    time.sleep(50)
    #循环下面任务
    task_num = 0
    while (utils.check_page(feature = "进行中") or utils.check_page(feature = "去完成")):
        tasks = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.TextView")
        try:
            while (tasks[task_num].text.find("进行中") == -1) and (tasks[task_num].text.find("去完成") == -1) :
                task_num = task_num + 1
            device_ip[2] = device_ip[2] + 1
            print(f"=====找到第{device_ip[2]}个任务=====")
            tasks[task_num].click()
        except Exception as e :
            if "list index out of range" in str(e) and device_ip[2] != 1:
                task_num = 0
                while (tasks[task_num].text.find("进行中") == -1) and (tasks[task_num].text.find("去完成") == -1) :
                    task_num = task_num + 1
                device_ip[2] = 1
                print(f"=====找到第{device_ip[2]}个任务=====")
                tasks[task_num].click()
            else:
                raise e 
        #等待网页刷出来
        utils.up_down_roll(5) 
        #打印标题
        title = driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/alt").text
        print(title)
        time_wait = 4
        if title in utils.get_wait_title():
            print("=====进入等待标题处理=====")
            time_wait = 8
        jump_flag = False
        for tmp in utils.get_jump_title():
            if tmp in title:
                jump_flag = True
        if jump_flag:
            print("=====进入跳过标题处理=====")
            #开始上下滑动
            utils.up_down_roll(8)
            fan_num = 0
            while not utils.check_page('看看赚') and fan_num < 30:
                print("=====页面返回=====")
                driver.back()
                time.sleep(3)
                fan_num = fan_num + 1
            task_num = task_num + 1
            continue
        no_image_flag = False 
        if title in utils.get_click_title():
            print("=====进入无图片标题处理=====")
            no_image_flag = True
        no_back_flag = False
        if (not time_wait ==8) and utils.check_page():
            print("=====进入滑动搜索页面处理=====")
            no_back_flag = True
        #普通处理
        is_success = utils.common_kan(time_wait, no_image_flag,no_back_flag)
        #当前任务没有成功，跳过
        task_num = task_num + 1
        fan_num = 0
        while not utils.check_page('看看赚') and fan_num < 30:
            print("=====页面返回=====")
            driver.back()
            time.sleep(3)
            fan_num = fan_num + 1
        tasks = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.TextView")
    #写入文件已读
    today = datetime.today()
    file = open(today.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt','w')
    if (not utils.check_page(feature = "进行中")) and (not utils.check_page(feature = "去完成")) and utils.check_page(feature = "已完成"):
        file.write("False")
    else:
        file.write("True")
    file.close()

#浏览文章 
def browse_articles(device_ip, driver):
    print("=====开始读取文章=====")
    utils = Utils(driver)
    #点击首页
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/ug").click()
    time.sleep(2)
    today = datetime.today()
    num_article = 1
    if Path(today.strftime('%Y%m%d')+device_ip+'.txt').exists():
        file = open(today.strftime('%Y%m%d')+device_ip+'.txt','r')
        num_article = (int)(file.readline())
        file.close()
    while(num_article<=80):
        #获取当前页面的文章
        articles = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/afb")
        while len(articles) == 0:
            print("没有找到文章")
            utils.swipeUp(t=100)
            time.sleep(2)
            articles = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/afb")
        print(f"一共找到{len(articles)}篇文章")
        for art in articles:
            print(f"====开始读第{num_article}篇")
            time.sleep(3)
            #按顺序点击文章
            try:
                art.click()
            except Exception as e:
                print("点击文章报错了！上划继续！")
                #点击首页
                driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/ug").click()
                break
            time.sleep(5)
            for _ in range(5):
                tmp = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.view.View")
                for quan_num in range(len(tmp)):
                    if(tmp[quan_num].text.find("查看全文") != -1):
                        tmp[quan_num].click()
                        break
                utils.swipeUp(t=1000)
                time.sleep(5) 
            #返回
            driver.back()
            num_article = num_article + 1
            #写入文件已读
            file = open(today.strftime('%Y%m%d')+device_ip+'.txt','w')
            file.write((str)(num_article))
            file.close()
        if not num_article % 5 == 0 :
            #下划
            utils.swipeUp(start_y=0.9, end_y=0.1,t=1000)
        else:
            #点击首页
            driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/ug").click()
        time.sleep(2)     

#浏览视频
def browse_videos(device_ip, driver):
    print("=====开始读取视频=====")
    utils = Utils(driver)
    #点击视频
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/uj").click()
    time.sleep(20)
    today = datetime.today()
    num_video = 1
    if Path(today.strftime('%Y%m%d')+device_ip+'_video.txt').exists():
        file = open(today.strftime('%Y%m%d')+device_ip+'_video.txt','r')
        num_video = (int)(file.readline())
        file.close()
    while(num_video<=30):
        print(f"====开始看第{num_video}个")
        time.sleep(30)
        num_video = num_video + 1
        #写入文件已读
        file = open(today.strftime('%Y%m%d')+device_ip+'_video.txt','w')
        file.write((str)(num_video))
        file.close()
        utils.swipeUp(t=1000)

#判断是否完成文章任务
def is_compl_task(driver):
    tasks_dic = {}
    #点击任务列表
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/vi").click()
    get_tasks(driver, tasks_dic)
    utils = Utils(driver)
    utils.swipeUp(500)
    #展开
    while driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/aeo"):
        driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/aeo").click()
    #获取部分任务
    tasks = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/agn")
    for i in range(len(tasks)):
        print(tasks[i])
    print("=====判断文章=====")
#获取部分任务
def get_tasks(driver, tasks_dic):
    tasks = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/agn")
    for i in range(len(tasks)):
        text = tasks[i].get_attribute("text")
        if text.find("阅读60篇") != -1:
            tasks_dic['article'] = 0
        if text.find("") != -1:
            tasks_dic['video'] = 0

def task_thread(device_ip):
    print(f'=====开始{device_ip[0]}=====')
    today = datetime.today()
    yestoday = today - timedelta(days=1)
    num_article = 1
    num_video = 1
    kankan_flag = "True"
    if Path(yestoday.strftime('%Y%m%d')+device_ip[0]+'.txt').exists():
        os.remove(yestoday.strftime('%Y%m%d')+device_ip[0]+'.txt')
    # if Path(yestoday.strftime('%Y%m%d')+device_ip[0]+'_video.txt').exists():
    #     os.remove(yestoday.strftime('%Y%m%d')+device_ip[0]+'_video.txt')
    if Path(yestoday.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt').exists():
        os.remove(yestoday.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt')
    if Path(today.strftime('%Y%m%d')+device_ip[0]+'.txt').exists():
        file = open(today.strftime('%Y%m%d')+device_ip[0]+'.txt','r')
        num_article = (int)(file.readline())
        file.close()
    # if Path(today.strftime('%Y%m%d')+device_ip[0]+'_video.txt').exists():
    #     file = open(today.strftime('%Y%m%d')+device_ip[0]+'_video.txt','r')
    #     num_video = (int)(file.readline())
    #     file.close()
    if Path(today.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt').exists():
        file = open(today.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt','r')
        kankan_flag = file.readline()
        file.close()
    if num_article <= 80 or kankan_flag == "True":
        os.popen(f'"D:/Program Files/Nox/bin/Nox.exe" -clone:'+device_ip[0])
        time.sleep(60)
    while num_article<=80 or kankan_flag == "True":
        try:
            #关闭相应app
            # os.system(f"adb -s {device_ip[1]} shell am force-stop io.appium.settings")
            # os.system(f"adb -s {device_ip[1]} shell am force-stop io.appium.uiautomator2.server")
            # os.system(f"adb -s {device_ip[1]} shell am force-stop cn.youth.news")
            driver = load_driver(device_ip[1])
            time.sleep(30)
            browse_articles(device_ip[0], driver)
            # browse_videos(device_ip[0], driver)
            device_ip[2] = 0
            browse_look(driver,device_ip)
        except Exception as e:
            print(e)
            if "Cannot find any free port in range" in str(e) or "not found" in str(e):
                os.popen(f'"D:/Program Files/Nox/bin/Nox.exe" -clone:'+device_ip[0]+' -quit')
                time.sleep(10)
                os.popen(f'"D:/Program Files/Nox/bin/Nox.exe" -clone:'+device_ip[0])
                time.sleep(30)
            if "list index out of range" in str(e) and device_ip[2] == 1:
                today = datetime.today()
                file = open(today.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt','w')
                file.write("False")
                file.close()
        finally:
            time.sleep(10)
            #关闭相应app
            os.system(f"adb -s {device_ip[1]} shell am force-stop io.appium.settings")
            os.system(f"adb -s {device_ip[1]} shell am force-stop io.appium.uiautomator2.server")
            os.system(f"adb -s {device_ip[1]} shell am force-stop cn.youth.news")
            if Path(today.strftime('%Y%m%d')+device_ip[0]+'.txt').exists():
                file = open(today.strftime('%Y%m%d')+device_ip[0]+'.txt','r')
                num_article = (int)(file.readline())
                file.close()
            # if Path(today.strftime('%Y%m%d')+device_ip[0]+'_video.txt').exists():
            #     file = open(today.strftime('%Y%m%d')+device_ip[0]+'_video.txt','r')
            #     num_video = (int)(file.readline())
            #     file.close()
            if Path(today.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt').exists():
                file = open(today.strftime('%Y%m%d')+device_ip[0]+'看看赚.txt','r')
                kankan_flag = file.readline()
                file.close()
    os.popen(f'"D:/Program Files/Nox/bin/Nox.exe" -clone:'+device_ip[0]+' -quit')

if __name__ == "__main__":
    device_ip = ["Nox_0","127.0.0.1:62001",0]
    device_ip_f = ["Nox_1","127.0.0.1:62025",0]
    device_ip_m = ["Nox_2","127.0.0.1:62026",0]
    # thread3=threading.Thread(target=task_thread,args=(device_ip_f,))
    # thread3.start()
    # thread2=threading.Thread(target=task_thread,args=(device_ip,))
    # thread2.start()
    # thread1=threading.Thread(target=task_thread,args=(device_ip_m,))
    # thread1.start()
    task_thread(device_ip_m)
    task_thread(device_ip_f)
    task_thread(device_ip)