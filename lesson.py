#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author : wcomaqsw
# E-mail: wcomaqsw@qq.com

import requests
import time
import logging

# 配置log文件
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='lesson.log',
                filemode='w')
#################################################################################################
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#################################################################################################


agent = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
headers = {
    "User-Agent": agent
}
data = {
    "zjh": "",
    "mm": ""
}

param = {
    "kcId": "306003010_01",
    "preActionType": "5",
    "actionType" : "9"
}

courses = []
course = {
    "kch" : "",
    "cxkxh" : "",
    "done" : False
}

tparam = {
    "kch": "306003010",
    "cxkxh": "01",
    "kcm" : "",
    "skjs": "",
    "kkxsjc": "",
    "skxq": "",
    "skjc": "",
    "pageNumber": "-2",
    "preActionType": "2",
    "actionType": "5"
}

jwc_ip = "202.115.47.141"
time_delay = 1
sleeptime = 5

# 会话
s = requests.Session()

# login 负责更新Session的cookies和登录
# first_flag 用来标记是否是第一次登录
def login(first_flag = False):
    global s
    s.headers.update(headers)
    while True:
        try:
            s.get("http://" + jwc_ip + "/loginAction.do", timeout = time_delay)
            # 再访问一次加入cookies
            r = s.get("http://" + jwc_ip + "/loginAction.do", timeout = time_delay)
            # 登录
            r = s.post("http://" + jwc_ip + "/loginAction.do", data = data, timeout = time_delay)

            # 测试一下请求头是否正确
            #print(r.request.headers)
            #r = s.post("http://" + jwc_ip + "/xkAction.do?actionType=6")
            #print(r.request.headers)

            # 检查密码是否正确
            r = s.get("http://" + jwc_ip + "/xkAction.do?actionType=6", timeout = time_delay)
            with open("原始课表.html", "w") as f:
                f.write(r.text)

            if "错误信息" not in r.text:
                break
            else:
                print("账号或密码不正确，请重新输入账号和密码...")
                return 0 # 账号和密码不正确
        except requests.exceptions.Timeout:
            logging.info("网络有问题，正在重连...")
        except requests.exceptions.ConnectionError as e:
            logging.info(e)
            logging.info("有可能是教务处宕机了，也有可能没联网...\n请检查网络后，重启程序")
            time.sleep(1008611)
    if first_flag:
        logging.info("登陆成功，开始工作...")
    return 1

# 选课子程序
# urp教务系统需要按照步骤一步一步完成
def xk(param):
    global s
    global headers
    while True:
        try:
            # 查找课程
            r = s.get("http://" + jwc_ip + "/xkAction.do?actionType=-1", timeout = time_delay)
            r = s.get("http://" + jwc_ip + "/xkAction.do?actionType=5&pageNumber=-1&cx=ori", timeout = time_delay)
            r = s.post("http://" + jwc_ip + "/xkAction.do", data = tparam, timeout = time_delay)
            # 选课
            r = s.post("http://" + jwc_ip + "/xkAction.do", data = param, timeout = time_delay)

            # 看信息
            with open("test.html", "w") as f:
                f.write(r.text)

            # 处理一些情况

            # 中途被顶掉登录了
            if "请您登录后再使用" in r.text:
                logging.info("重复登录，程序重新登陆...")
                login()

            # 课余量不足
            # 并不需要显示这个信息 因为很多时候都是这个状态
            # 使用debug
            elif "没有课余量" in r.text:
                logging.debug("课程" + ' ' + param["kcId"] + ' ' + "没有课余量...")
                break

            # 非选课时间
            elif "非选课阶段" in r.text:
                logging.info("现阶段不允许选课\n具体时间请参看学校教务处公告...")
                break

            # 已选择
            elif "你已经选择了课程" in r.text:
                logging.info("你已经选择了课程" + ' ' + param["kcId"])
                return 1
                break

            # 检查是否选课成功
            elif "选课成功" in r.text:
                logging.info("课程" + ' ' + param["kcId"] + ' ' + "选择成功")
                # 存储新课表
                r = s.get("http://" + jwc_ip + "/xkAction.do?actionType=6", timeout = time_delay)
                with open("选课后课表.html", "w") as f:
                    f.write(r.text)
                # 成功，返回1
                return 1
                break

        except requests.exceptions.Timeout:
            logging.info("网络有问题，正在重连...")
            login()
        except requests.exceptions.ConnectionError as e:
            logging.info(e)
            logging.info("有可能是教务处宕机了，也有可能没联网...\n请检查网络后，重启程序")
            time.sleep(1008611)

    # 若不成功, 返回0
    return 0

def input_courses():
    """
    请输入想要选择课程的课程号和课序号
    *每个课程按照课程号 课序号的顺序输在一行，以空格隔开
    e.g.,123465789 01
    ***课序号为两位 不足补零
    最后以0 0为结束输入课程
    """
    global courses
    print(input_courses.__doc__)
    st = input()
    course["kch"] = st.split(' ', 1)[0]
    course["cxkxh"] = st.split(' ', 1)[1]
    while(not((course["kch"] == "0") & (course["cxkxh"] == "0"))):
        courses.append(dict(course))
        #print(course)
        st = input()
        course["kch"] = st.split(' ', 1)[0]
        course["cxkxh"] = st.split(' ', 1)[1]

def update(course):
    global param
    param["kcId"] = course["kch"] + '_' + course["cxkxh"]
    tparam["kch"] = course["kch"]
    tparam["cxkxh"] = course["cxkxh"]
    return param

if __name__ == "__main__":
    # 登录
    while True:
        data["zjh"] = input("请输入学号：")
        data["mm"] = input("请输入密码：")
        if login(True) == 1:
            break

    input_courses()
    #print(courses)

    flag = True #False 代表不需要继续刷 True 代表需要继续刷
    firsttime = True # 第一次的话，就选快点，后面有个间隔就好
    while flag:
        flag = False # 先假设不需要刷了
        for clas in courses:
            if clas["done"]:
                continue
            if xk(update(clas)) == 0:
                flag = True
            else:
                clas["done"] = True
            if not firsttime:
                time.sleep(sleeptime)
        flagtime = False

    logging.info("已完成所有工作...\n好好学习，天天向上！！！")
