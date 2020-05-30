# -*- coding: utf-8 -*-
__author__ = "xiaxia"

import json
import random

from airtest.core.api import *
from airtest.core.error import *
from poco.exceptions import *

from tools.ScreenOFF import *
from core.MultiAdb import MultiAdb as Madb
from multiprocessing import Process,Value,Pool
from tools.db import State,ShortVideoState

import traceback

index_print = print

def print(*args, **kwargs):
    index_print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), *args, **kwargs)

'''
整个框架的主程序，根据配置表读取设备，并逐一为其分配搜索进程。
'''
devicesList = Madb().getdevices()
def main():
    #默认去config.ini里读取期望参与测试的设备，若为空，则选择当前连接的所有状态为“device”的设备
    task_search()
    #douyin_task_search()


def douyin_task_search():
    if devicesList:
        try:
            print("启动进程池")
            list=[]
            # 根据设备列表去循环创建进程，对每个进程调用下面的enter_processing方法。
            for i in range(len(devicesList)):
                #start会被传递到进程函数里
                p2=Process(target=douyin_enter_processing, args=(i,))
                list.append(p2)
            for p in list:
                p.start()
            time.sleep(5)
            for p in list:
                p.join()
            # pool.close()
            # pool.join()
            print("进程回收完毕")
            print("测试结束")

        except AirtestError as ae:
            print("Airtest发生错误" + traceback.format_exc())
        except PocoException as pe:
            print("Poco发生错误" + traceback.format_exc())
        except Exception as e:
            print("发生未知错误" +  traceback.format_exc())
    else:
        print("未找到设备，测试结束")

def task_search():
    if devicesList:
        try:
            print("启动进程池")
            list=[]
            # 根据设备列表去循环创建进程，对每个进程调用下面的enter_processing方法。
            for i in range(len(devicesList)):
                #start会被传递到进程函数里
                p2=Process(target=enter_processing, args=(i,))
                list.append(p2)
            for p in list:
                p.start()
            time.sleep(5)
            for p in list:
                p.join()
            # pool.close()
            # pool.join()
            print("进程回收完毕")
            print("测试结束")

        except AirtestError as ae:
            print("Airtest发生错误" + traceback.format_exc())
        except PocoException as pe:
            print("Poco发生错误" + traceback.format_exc())
        except Exception as e:
            print("发生未知错误" +  traceback.format_exc())
    else:
        print("未找到设备，测试结束")
'''
功能进程模块
首先调用airtest库的方法进行设备连接并初始化，然后读取配表，进行应用的点击等操作。
确定启动应用成功以后，调用分配完成搜索。
'''


def enter_processing(i):
    if len(devicesList):
         madb = Madb(devicesList[i])
    else:
        return
    devices = madb.get_mdevice()
    print("进入进程,devicename={}".format(devices))
    isconnect=""
    try:
        #调用airtest的各个方法连接设备
        if("127.0.0.1" in devices):
            connect_device('android:///'+devices+'?cap_method=javacap&touch_method=adb')
        else:
            connect_device("Android:///" + devices)

        time.sleep(madb.get_timeout_of_per_action())
        auto_setup(__file__)
        isconnect="Pass"
        print("设备{}连接成功".format(devices))
        installflag=""
        startflag=""
        if isconnect == "Pass":
            try:
                #尝试启动应用
                madb.StartApp()
                auto_search(i)
                # 查询搜索任务
                startflag = "Success"
            except Exception as e:
                print("运行失败"+traceback.format_exc())
            time.sleep(madb.get_timeout_of_per_action())
            #应用启动成功则开始运行用例
            if (startflag=="Success"):
                print("{}完成测试".format(devices))
            else:
                print("{}未运行测试。".format(devices))
        else:
            print("设备{}连接失败".format(devices))
    except Exception as e:
        print( "连接设备{}失败".format(devices)+ traceback.format_exc())
    #无论结果如何，将flag置为1，通知Performance停止记录。

def auto_search(i,flag=True):
    tasks = get_hotsoon_task()
    if tasks:
        json_result = json.loads(tasks[i].json)
        data = {"status": '1'}
        ShortVideoState.edit_status(tasks[i].id, data)
        dictParameters = json_result["dictParameters"]
        searchWords = dictParameters["searchWord"]
        searchWord_list = searchWords.split(",")
        poco = Madb().get_poco()
        if len(searchWord_list) > 0:
            keyword = searchWord_list[0]
            for searchWord in searchWord_list:
                 index = searchWord_list.index(searchWord)
                 aut_search_recur(keyword,searchWord,index,poco,flag)
        auto_search(i,False)


#递归搜索
def aut_search_recur(keyword,searchWord,index,poco,flag=True):
    f=False
    if index==0 and flag and f:
        stop_app('com.ss.android.ugc.live')
        start_app('com.ss.android.ugc.live', activity=None)
        time.sleep(10)
        #poco("com.ss.android.ugc.live:id/cgr").click()
        #poco(desc="搜索").wait_for_appearance(timeout=10)
        back = poco(desc="返回")

        i_know = poco(text="我知道了")
        later = poco(text="以后再说")
        if later:
            later.click()
        if back:
            back.click()
        time.sleep(5)
        if i_know:
            i_know.click()
            time.sleep(5)
        search = poco(desc="搜索")
        if search:
            search.click()
    else:
        searchWord = keyword
    time.sleep(10)
    #touch(Template(r"tpl1590407481240.png"))
    text_flag = True
    while text_flag:
        try:
            poco(type='android.widget.EditText').click()
            # poco(type='android.widget.EditText').set_text(searchWord)wuqiong
            poco(type='android.widget.EditText').set_text("")
            text_flag = False
        except:
            text_flag = True
    text(searchWord, search=True)
    poco(text="搜索").click()
    poco(text="视频").click()
    x, y = device().get_current_resolution()
    start_pt = (x * 0.5, y * 0.8)
    end_pt = (x * 0.5, y * 0.2)
    flag = True
    count = 0
    swip_count = 0
    while (flag and count<3 and swip_count <100):
        time.sleep(3)
        try:
            end_text = poco(text="没有更多了")
            if(end_text and end_text.get_text().startswith('没有更多了')):
                flag=False
            init_failed = poco(text="加载失败,点击重试")
            if (init_failed and init_failed.get_text().startswith('加载失败')):
                count = count+1
                init_failed.click()
                continue
            swipe(start_pt, end_pt)
            time.sleep(random.random())
            swip_count =swip_count+1
        except Exception as e:
            print("发生未知错误" + traceback.format_exc())
            time.sleep(8)

            pass
    return



def get_hotsoon_task():
    condition = {"status": '0', "platform": "hotSoon"}

    tasks = ShortVideoState.get_crawl_lists(**condition)
    return tasks




def douyin_enter_processing(i):
    if len(devicesList):
         madb = Madb(devicesList[i])
    else:
        return
    devices = madb.get_mdevice()
    print("进入进程,devicename={}".format(devices))
    isconnect=""
    try:
        #调用airtest的各个方法连接设备
        if("127.0.0.1" in devices or '-' in devices):
            connect_device('android:///'+devices+'?cap_method=javacap&touch_method=adb')
        else:
            connect_device("Android:///" + devices)

        time.sleep(madb.get_timeout_of_per_action())
        auto_setup(__file__)
        isconnect="Pass"
        print("设备{}连接成功".format(devices))
        installflag=""
        startflag=""
        if isconnect == "Pass":
            try:
                #尝试启动应用
                madb.StartApp()
                douyin_auto_search(i)
                # 查询搜索任务
                startflag = "Success"
            except Exception as e:
                print("运行失败"+traceback.format_exc())
            time.sleep(madb.get_timeout_of_per_action())
            #应用启动成功则开始运行用例
            if (startflag=="Success"):
                print("{}完成测试".format(devices))
            else:
                print("{}未运行测试。".format(devices))
        else:
            print("设备{}连接失败".format(devices))
    except Exception as e:
        print( "连接设备{}失败".format(devices)+ traceback.format_exc())
    #无论结果如何，将flag置为1，通知Performance停止记录。

def douyin_auto_search(i,flag=True):
    tasks = get_douyin_task()
    if tasks:
        json_result = json.loads(tasks[i].json)
        data = {"status": '1'}
        #State.edit_status(tasks[i].id, data)
        ShortVideoState.edit_status(tasks[i].id, data)
        dictParameters = json_result["dictParameters"]
        searchWords = dictParameters["searchWord"]
        searchWord_list = searchWords.split(",")
        poco = Madb().get_poco()
        if len(searchWord_list) > 0:
            keyword = searchWord_list[0]
            for searchWord in searchWord_list:
                 index = searchWord_list.index(searchWord)
                 douyin_aut_search_recur(keyword,searchWord,index,poco,flag)
        douyin_auto_search(i,False)


#递归搜索
def douyin_aut_search_recur(keyword,searchWord,index,poco,flag=True):
    try:
        if index==0 and flag:
            stop_app('com.ss.android.ugc.aweme')
            start_app('com.ss.android.ugc.aweme', activity=None)
            time.sleep(10)
            #poco("com.ss.android.ugc.live:id/cgr").click()
            #poco(desc="搜索").wait_for_appearance(timeout=10)
            later = poco(text="以后再说")
            if later:
                later.click()
                time.sleep(5)
            back = poco(desc="返回")
            if back:
                back.click()
            time.sleep(10)
            i_know = poco(text="我知道了")
            if i_know:
                i_know.click()
                time.sleep(5)
            time.sleep(10)
            search = poco(desc="搜索")
            search.click()
        else:
            searchWord = keyword
        time.sleep(10)
        text_flag = True
        while text_flag:
            try:
                poco(type='android.widget.EditText').click()
                #poco(type='android.widget.EditText').set_text(searchWord)
                poco(type='android.widget.EditText').set_text("")
                text_flag=False
            except:
                text_flag=True
        text(searchWord,search=True)
        time.sleep(3)
        poco(text="视频").click()
        time.sleep(5)
        x, y = device().get_current_resolution()
        start_pt = (x * 0.5, y * 0.8)
        end_pt = (x * 0.5, y * 0.2)
        flag = True
        count = 0
        swip_count = 0
        while (flag and count<3 and swip_count<30):
            time.sleep(2)
            end_text = poco(text="暂时没有更多了")
            if(end_text and end_text.get_text().startswith('暂时没有更多了')):
                flag=False
            init_failed = poco(text="加载失败,点击重试")
            if (init_failed and init_failed.get_text().startswith('加载失败')):
                count = count+1
                init_failed.click()
                continue
            swipe(start_pt, end_pt)
            swip_count=swip_count+1
            time.sleep(random.random())
    except Exception as e:

        print("发生未知错误" + traceback.format_exc())
        time.sleep(5)

    return



def get_douyin_task():
    condition = {"status": '0', "platform": "douyinVideo"}
    #tasks = State.get_crawl_lists(**condition)
    tasks = ShortVideoState.get_crawl_lists(**condition)
    return tasks




