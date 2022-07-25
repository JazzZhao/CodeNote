from webbrowser import get
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import time

class Utils:
    def __init__(self, driver=None) :
        self.driver = driver
    def getSize(self):                               #获取当前的width和height的x、y的值
        x = self.driver.get_window_size()['width']   #width为x坐标
        y = self.driver.get_window_size()['height']  #height为y坐标
        return (x, y)

    def swipeUp(self,t):  #当前向上滑动swipeup
        l = self.getSize()
        x1 = int(l[0] * 0.5)  
        y1 = int(l[1] * 0.75)   
        y2 = int(l[1] * 0.25)   
        self.driver.swipe(x1, y1, x1, y2, t)  #设置时间为500

    def swipLeft(self, t):      #当前向左进行滑动swipleft
        l=self.getSize()
        x1=int(l[0]*0.75)
        y1=int(l[1]*0.5)
        x2=int(l[0]*0.05)
        self.driver.swipe(x1,y1,x2,y1, t)

    def swipeDown(self, t):    #向下滑动swipedown
        l = self.getSize()
        x1 = int(l[0] * 0.5)
        y1 = int(l[1] * 0.25)
        y2 = int(l[1] * 0.75)
        self.driver.swipe(x1, y1, x1, y2, t)

    def swipRight(self, t): #向右滑行swipright
        l=self.getSize()
        x1=int(l[0]*0.05)
        y1=int(l[1]*0.5)
        x2=int(l[0]*0.75)
        self.driver.swipe(x1,y1,x2,y1, t)

#加载APP
def load_driver():
    # 会话配置
    desired_caps = {
            "platformName":"Android",
            "platformVersion":"10.0.0",
            "deviceName":"7XBNW18901004436",
            "appPackage":"cn.youth.news",
            "appActivity":"cn.youth.news.ui.splash.SplashActivity",
            "noReset": True
    }
    return webdriver.Remote("http://127.0.0.1:4723/wd/hub",desired_caps)


#浏览文章 
def browse_articles(driver):
    print("=====开始读取文章=====")
    while(True):
        #获取当前页面的文章
        articles = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/aj_")
        for i in range(len(articles)):
            #按顺序点击文章
            articles[i].click()
            utils = Utils(driver)
            for i in range(8):
                if i%2==0 :
                    utils.swipeUp(500)
                else:
                    utils.swipeDown(1000)
                time.sleep(5) #TODO
            #返回
            driver.back()
        #上划
        utils = Utils(driver)
        utils.swipeUp(1000)
        driver.quit()
#判断是否完成文章任务
def is_compl_task(driver):
    tasks_dic = {}
    #点击任务列表
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/x7").click()
    get_tasks(driver, tasks_dic)
    utils = Utils(driver)
    utils.swipeUp(500)
    #展开
    while driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/aeo"):
        driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/aeo").click
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
    driver = load_driver() 
    time.sleep(10)

    is_compl_articles(driver)
    # browse_articles(driver)
    
    
