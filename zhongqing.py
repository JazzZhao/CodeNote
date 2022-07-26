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
    num_article = 1
    while(num_article<70):
        #获取当前页面的文章
        articles = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/agh")
        for i in range(len(articles)):
            print(f"====开始读第{num_article}篇")
            #按顺序点击文章
            articles[i].click()
            time.sleep(5)
            utils = Utils(driver)
            for i in range(5):
                utils.swipeUp(t=1000)
                tmp = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.view.View")
                for i in range(len(tmp)):
                    if(tmp[i].text.find("查看全文") != -1):
                        tmp[i].click()
                        break
                time.sleep(5) 
            #返回
            driver.back()
            num_article = num_article + 1
        #上划
        utils.swipeUp(start_y=0.9, end_y=0.1,t=1000)
#浏览视频
def browse_video(driver):
    print("=====开始浏览视频=====")
    num_video = 1
    while(num_video<11):
        #获取当前页面的视频
        videos = driver.find_elements(by=AppiumBy.ID, value="cn.youth.news:id/agh")
        for i in range(len(videos)):
            print(f"====开始浏览第{num_video}个")
            #按顺序点击视频
            videos[i].click()
            time.sleep(5)
            time.sleep(20)
            #返回
            driver.back()
            num_article = num_article + 1
        #上划
        utils = Utils(driver)
        utils.swipeUp(start_y=0.9, end_y=0.1,t=1000)

#赚赚看
def browse_look(driver):
    print("=====开始浏览看看赚=====")
    utils = Utils(driver)
    #点击任务列表
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/vi").click()
    time.sleep(5)
    #点击看看赚
    print("=====点击看看赚=====")
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/ac_").click()
    time.sleep(5)
    #循环下面任务
    for i in range(50):
        tasks = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.TextView")
        print("=====开始找任务=====")
        if(tasks[i].text.find("进行中") != -1 or  tasks[i].text.find("去完成") != -1):
            tasks[i].click()
            time.sleep(10)
            before_page = driver.page_source
            time.sleep(15)
            afer_page = driver.page_source
            #判断是否自动刷新
            if before_page == afer_page:
                #点击链接
                for i in range(8):
                    images = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Image")
                    images[i].click()
                    time.sleep(15)
                    utils.swipeUp(t=100)
                    time.sleep(2)
                    #返回
                    driver.back()
                    time.sleep(5)
                
            else:
                utils.swipeUp(t=100)
                utils.swipeDown(t=100)





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
    driver = load_driver()
    # is_compl_task(driver)
    type = input("======输入类型======\n all ===> 全部类型\n 1 ===> 文章\n 2 ===> 视频\n 3 ===> 看看赚\n")
    time.sleep(5)
    try:
        if type == 'all':
            browse_articles(driver)
            browse_video(driver)
            browse_look(driver)
        elif type == '1':
            browse_articles(driver)
        elif type == '2':
            browse_video(driver)
        elif type == '3':
            browse_look(driver)
    except Exception as e:
        print(e)
    finally:
        driver.quit()

    
    
