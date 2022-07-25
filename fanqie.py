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
            "platformVersion":"9.0.0",
            "deviceName":"127.0.0.1:62001",
            "appPackage":"com.dragon.read",
            "appActivity":"com.dragon.read.pages.splash.SplashActivity",
            "noReset": True
    }
    return webdriver.Remote("http://127.0.0.1:4723/wd/hub",desired_caps)



if __name__ == "__main__":
    driver = load_driver() 
    print("=====开启应用结束=====")
    time.sleep(5)
    
