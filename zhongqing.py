from webbrowser import get
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time
import os

class Utils:
    def __init__(self, driver=None) :
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
        tmp = 1
        while tmp <= num:
            self.swipeUp(start_y=0.55, end_y=0.5, t=0)
            self.swipeDown(start_y=0.5, end_y=0.55, t=0)
            tmp = tmp + 1
    #####获取广告的图片######
    def get_images(self):
        self.driver.page_source
        #获取图片链接
        images = self.driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Image")
        if len(images) == 0:
            #使用content-desc来获取
            images = self.driver.find_elements(by=AppiumBy.XPATH, value = "//*[contains(@content-desc, 'sogou')]")
        return images
    #####普通看看赚处理######
    def common_kan(self, time_wait):
        one_num = 0
        while one_num < 6:
            print(f"=====等待{time_wait}s=====")
            self.up_down_roll(time_wait)
            print("=====获取图片=====")
            images = self.get_images()
            if len(images) == 0:
                print("=====没有图片=====")
                return False 
            if one_num>= len(images):
                images[len(images)-1].click()
            else:
                images[one_num].click()
            one_num = one_num + 1
            print("=====点击图片跳转=====")
            #开始上下滑动
            self.up_down_roll(8)
            #返回
            print("=====页面返回=====")
            driver.back()
        return True

    #需要等待的标题
    def get_wait_title(self):
        return ['今日看点']
    #有次首页的标题，需要
    def get_secondary_title(self):
        return ['非凡资讯']
    #搜索标题的处理
    def get_search_title(self):
        return ['搜索']
    #进来先点关闭按键的标题
    def get_close_title(self):
        return []
    #跳过的标题
    def get_jump_title(self):
        return ['手机乐视_乐视视频,...', '网页无法打开']

    #需要先点击
    def get_click_title(self):
        return ['巨资讯','一点生活趣事']

#加载APP
def load_driver():
    # 会话配置
    desired_caps = {
            "platformName":"Android",
            "platformVersion":"10.0.0",
            "deviceName":"192.168.0.154:5555",
            "appPackage":"cn.youth.news",
            "appActivity":"cn.youth.news.ui.splash.SplashActivity",
            "noReset": True
    }
    return webdriver.Remote("http://127.0.0.1:4723/wd/hub",desired_caps)
#赚赚看
def browse_look(driver):
    #TODO 解决首页和搜索页在一起的情况
    print("=====开始浏览看看赚=====")
    utils = Utils(driver)
    #点击任务列表
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/vi").click()
    time.sleep(5)
    #点击看看赚
    print("=====点击看看赚=====")
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/ac8").click()
    time.sleep(5)
    #循环下面任务
    task_num = 0
    t = 0
    while True:
        tasks = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.TextView")
        while (tasks[task_num].text.find("进行中") == -1) and (tasks[task_num].text.find("去完成") == -1) :
            task_num = task_num + 1
        print(f"=====找到第{t+1}个任务=====")
        tasks[task_num].click()
        #等待网页刷出来
        time.sleep(5)
        #打印标题
        title = driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/an6").text
        print(title)
        time_wait = 2
        if title in utils.get_wait_title():
            print("=====进入等待标题处理=====")
            time_wait = 10
        if title in utils.get_jump_title():
            driver.back()
            task_num = task_num + 1
            continue
        #普通处理
        is_success = utils.common_kan(time_wait)
        #当前任务没有成功，跳过
        if not is_success:
            task_num = task_num + 1
        while not utils.check_page('浏览赚'):
            print("=====页面返回=====")
            driver.back()
        time.sleep(3)
        t = t + 1

#浏览文章 
def browse_articles(driver):
    print("=====开始读取文章=====")
    utils = Utils(driver)
    #点击首页
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/vg").click()
    time.sleep(2)
    num_article = 1
    flash_flag = True
    while(num_article<=20):
        #获取当前页面的文章
        articles = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/agh")
        while len(articles) == 0:
            print("没有找到文章")
            utils.swipeUp(t=100)
            time.sleep(2)
            articles = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/agh")
        print(f"一共找到{len(articles)}篇文章")
        for art in articles:
            print(f"====开始读第{num_article}篇")
            #按顺序点击文章
            try:
                art.click()
            except Exception as e:
                print("点击文章报错了！上划继续！")
                break
            time.sleep(5)
            for _ in range(5):
                utils.swipeUp(t=1000)
                tmp = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.view.View")
                for quan_num in range(len(tmp)):
                    if(tmp[quan_num].text.find("查看全文") != -1):
                        tmp[quan_num].click()
                        break
                time.sleep(5) 
            #返回
            driver.back()
            num_article = num_article + 1
        if flash_flag:
            #下划
            utils.swipeUp(start_y=0.9, end_y=0.1,t=1000)
            flash_flag = False
        else:
            #点击首页
            driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/vg").click()
            flash_flag = True
        time.sleep(2)     

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



if __name__ == "__main__":
    for i in range(4):
        try:
            #关闭相应app
            os.system("adb shell am force-stop io.appium.settings")
            os.system("adb shell am force-stop io.appium.uiautomator2.server")
            driver = load_driver()
            time.sleep(10)
            browse_articles(driver)
            browse_look(driver)
        except Exception as e:
            print(e)
        finally:
            #关闭相应app
            os.system("adb shell am force-stop io.appium.settings")
            os.system("adb shell am force-stop io.appium.uiautomator2.server")
            