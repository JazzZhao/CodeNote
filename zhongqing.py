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
    def up_down_roll(self):
        tmp = 1
        while tmp < 6:
            self.swipeUp(start_y=0.55, end_y=0.5, t=0)
            self.swipeDown(start_y=0.5, end_y=0.55, t=0)
            tmp = tmp + 1
    #能够进行的标题
    def get_title_do(self):
        return ['今日看点','今日热讯',"今日热搜",'八卦资讯']
    
    #跳出进来的标题
    def get_turn_out_title():
        return []
    #进来先点关闭按键的标题
    def get_close_title():
        return []

    #需要先点击
    def get_click_title():
        return ['巨资讯','一点生活趣事']

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
    utils = Utils(driver)
    #点击首页
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/vg").click()
    time.sleep(2)
    num_article = 1
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
        #上划
        utils.swipeUp(start_y=0.9, end_y=0.1,t=1000)
        time.sleep(2)

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
    driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/ac_").click()
    time.sleep(5)
    #循环下面任务
    task_num = 0
    #没有图片的个数
    non_img = 0
    for t in range(20):
        tasks = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.TextView")
        while (tasks[task_num].text.find("进行中") == -1) and (tasks[task_num].text.find("去完成") == -1) :
            task_num = task_num + 1
        print(f"=====找到第{t+1}个任务=====")
        tasks[task_num].click()
        #需要增加网速不好没刷出来页面的等待
        time.sleep(1)
        #打印标题
        print(driver.find_element(by=AppiumBy.ID, value="cn.youth.news:id/an6").text)
        if utils.check_page():
            print("=====搜索页等待自动刷新进入目标首页=====")
            time.sleep(15)
        else:
            print("=====正常首页，不用等待")
            time.sleep(1)
        one_num = 0
        #不是搜索页面，就进行点击，并且只划动7次
        while one_num < 6:
            if utils.check_page() or utils.check_page("百度一下") or utils.check_page("搜狗搜索"):
                print("=====进入了搜索页面，滑动，返回")
                utils.up_down_roll()
                task_num = task_num + 1
                break
            else:
                #获取图片链接
                images = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Image")
                if len(images) == 0:
                    #使用content-desc来获取
                    images = driver.find_elements(by=AppiumBy.XPATH, value = "//*[contains(@content-desc, 'sogou')]")
                if len(images)>0:
                    if one_num>= len(images):
                        images[len(images)-1].click()
                    else:
                        images[len(images)-1-one_num].click()
                    print("=====点击图片跳转=====")
                    time.sleep(2)
                    #这里需要特殊处理含有弹窗的情况(风细柳斜)
                    if utils.check_page(feature="close"):
                        #重新获取图片点击
                        images = driver.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Image")
                        images[len(images)-1].click()
                        time.sleep(1)
                    #开始上下滑动
                    utils.up_down_roll()
                    one_num = one_num + 1
                    #返回
                    if utils.check_page() or utils.check_page("百度一下") or utils.check_page("搜狗搜索"):
                        print("=====页面返回=====")
                        driver.back()
                    else:
                        print("=====不是搜索页面不用返回=====")
                    time.sleep(1)
                    if utils.check_page() or utils.check_page("百度一下") or utils.check_page("搜狗搜索"):
                        print("=====搜索页等待自动刷新进入目标首页=====")
                        time.sleep(15)
                    else:
                        print("=====正常首页，不用等待")
                        time.sleep(1)
                else:
                    non_img = non_img + 1
                    print(f"====={non_img}个页面不含图片=====")
                    task_num = task_num + 1
                    break
        while not utils.check_page('浏览赚'):
            print("=====页面返回=====")
            driver.back()


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
    for i in range(3):
        try:
            driver = load_driver()
            time.sleep(5)
            # browse_articles(driver)
            browse_look(driver)
        except Exception as e:
            print(e)
        finally:
            driver.quit()
    
    
    
