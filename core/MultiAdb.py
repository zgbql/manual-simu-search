# -*- coding: utf-8 -*-
__author__ = "xiaxia"

import os,inspect
import sys
import threading
import queue
from tools import Config
from airtest.core.api import *
from airtest.core.error import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from airtest.core.android.adb import ADB
import  subprocess
from airtest.utils.apkparser import APK

_print = print
def print(*args, **kwargs):
    _print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), *args, **kwargs)

adb = ADB().adb_path
#同文件内用queue进行线程通信


'''
MultiAdb类封装了所有与设备有关的方法。
大部分方法都单独写了注释。

'''

class MultiAdb:

    def __init__(self,mdevice=""):
        #获取当前文件的上层路径
        self._parentPath=os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())) + os.path.sep + ".")
        #获取当前项目的根路径
        self._rootPath=os.path.abspath(os.path.dirname(self._parentPath) + os.path.sep + ".")
        self._configPath=self._rootPath+"\config.ini"
        self._devicesList = Config.getValue(self._configPath, "deviceslist", )
        self._packageName = Config.getValue(self._configPath, "packname")[0]
        self._activityName = Config.getValue(self._configPath, "activityname")[0]
        self._skip_pushapk2devices=Config.getValue(self._configPath, "skip_pushapk2devices")[0]
        self._auto_delete_package=Config.getValue(self._configPath,"auto_delete_package")[0]
        self._auto_install_package=Config.getValue(self._configPath,"auto_install_package")[0]
        self._skip_check_of_install = Config.getValue(self._configPath, "skip_check_of_install")[0]
        self._skip_check_of_startapp = Config.getValue(self._configPath, "skip_check_of_startapp")[0]
        self._skip_performance=Config.getValue(self._configPath,"skip_performance")[0]
        self._storage_by_excel=Config.getValue(self._configPath,"storage_by_excel")[0]
        self._screenoff=Config.getValue(self._configPath,"screenoff")[0]
        self._startTime=time.time()
        self._timeout_of_per_action=int(Config.getValue(self._configPath, "timeout_of_per_action")[0])
        self._timeout_of_startapp=int(Config.getValue(self._configPath, "timeout_of_startapp")[0])
        self._mdevice=mdevice
        self._poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
        # 处理模拟器端口用的冒号
        if ":" in self._mdevice:
            self._nickName = self._mdevice.split(":")[1]
        else:
            self._nickName=self._mdevice
        self._iteration=int(Config.getValue(self._configPath, "iteration")[0])
        self._allTestcase=Config.getValue(self._configPath, "testcase")
        try:
            self._testcaseForSelfDevice =Config.getTestCase(self._configPath, self._nickName)
            if self._testcaseForSelfDevice[0]=="":
                self._testcaseForSelfDevice = self._allTestcase
        except Exception:
            self._testcaseForSelfDevice=self._allTestcase
        self._testCasePath=Config.getValue(self._configPath, "testcasepath")
        if self._testCasePath[0]=="":
            self._testCasePath=os.path.join(self._rootPath, "TestCase")


    #获取设备列表
    def get_devicesList(self):
        return self._devicesList
    def get_poco(self):
        return self._poco
    #获取apk的本地路径
    def get_apkpath(self):
        return self._packagePath
    #获取包名
    def get_packagename(self):
        return self._packageName
    #获取Activity类名
    def get_activityname(self):
        return self._activityName

    #获取是否跳过安装apk步骤的flag
    def get_skip_pushapk2devices(self):
        return self._skip_pushapk2devices

    #获取是否需要在安装应用时点击二次确认框的flag
    def get_skip_check_of_install(self):
        return self._skip_check_of_install


    #获取是否需要在打开应用时点击二次确认框的flag
    def get_skip_check_of_startapp(self):
        return self._skip_check_of_startapp

    #获取当前设备id
    def get_mdevice(self):
        return self._mdevice

    #获取当前设备id的昵称，主要是为了防范模拟器和远程设备带来的冒号问题。windows的文件命名规范里不允许有冒号。
    def get_nickname(self):
        return self._nickName

    #获取启动app的延时时间
    def get_timeout_of_startapp(self):
        return self._timeout_of_startapp

    #获取每步操作的延时时间
    def get_timeout_of_per_action(self):
        return self._timeout_of_per_action

    #获取运行循环点击处理脚本的循环次数
    def get_iteration(self):
        return self._iteration

    #获取所有的用例名称列表
    def get_alltestcase(self):
        return self._allTestcase

    #获取针对特定设备的用例列表
    def get_testcaseforselfdevice(self):
        return self._testcaseForSelfDevice

    #获取测试用例路径，不填是默认根目录TestCase
    def get_TestCasePath(self):
        return self._testCasePath

    #获取项目的根目录绝对路径
    def get_rootPath(self):
        return self._rootPath




    #获取是否需要在测试结束以后灭屏
    def get_screenoff(self):
        return self._screenoff

    def get_isSurfaceView(self):
        return  self._isSurfaceView

    #修改当前设备的方法
    def set_mdevice(self,device):
        self._mdevice=device

    #写回包名、包路径、测试用例路径等等到配置文件

    def set_packagename(self,packagename):
        configPath=self._configPath
        Config.setValue(configPath,"packname",packagename)

    def set_packagepath(self, packagepath):
        configPath = self._configPath
        Config.setValue(configPath, "apkpath", packagepath)

    def set_TestCasePath(self,TestCasepath):
        configPath=self._configPath
        Config.setValue(configPath,"testcasepath",TestCasepath)

    # 本方法用于读取实时的设备连接
    def getdevices(self):
        deviceslist=[]
        for devices in os.popen(adb + " devices"):
            if "\t" in devices:
                if devices.find("emulator")<0:
                    if devices.split("\t")[1] == "device\n":
                        deviceslist.append(devices.split("\t")[0])
                        print("设备{}被添加到deviceslist中".format(devices))
        return deviceslist

    #启动APP的方法，核心是airtest的start_app函数，后面的一大堆if else 是用来根据设备进行点击操作的。需要用户自行完成。
    def StartApp(self):
        devices=self.get_mdevice()
        skip_check_of_startapp=self.get_skip_check_of_startapp()
        skip_check_of_startapp = True if skip_check_of_startapp == "1" else False
        print("{}进入StartAPP函数".format(devices))
        start_app(self.get_packagename())
        if not skip_check_of_startapp:
            print("设备{}，skip_check_of_startapp为{}，开始初始化pocoui，处理应用权限".format(devices,skip_check_of_startapp))
            # 获取andorid的poco代理对象，准备进行开启应用权限（例如申请文件存储、定位等权限）点击操作
            pocoAndroid = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)
            n=self.get_iteration()

            #以下代码写得极丑陋，以后有空再重构，期望是参数化。
            if devices == "127.0.0.1:62001":
                # 这里是针对不同机型进行不同控件的选取，需要用户根据自己的实际机型实际控件进行修改
                count = 0
                while not pocoAndroid("android.view.View").exists():
                    print("{}开启应用的权限点击，循环第{}次".format(devices,count))
                    if count >= n:
                        break
                    if pocoAndroid("com.android.packageinstaller:id/permission_allow_button").exists():
                        pocoAndroid("com.android.packageinstaller:id/permission_allow_button").click()
                    else:
                        time.sleep(self.get_timeout_of_per_action())
                        count += 1
            elif devices == "127.0.0.1:62025":
                count = 0
                while not pocoAndroid("android.view.View").exists():
                    print("{}开启应用的权限点击，循环第{}次".format(devices,count))
                    if count >= 3:
                        break
                    if pocoAndroid("android:id/button1").exists():
                        pocoAndroid("android:id/button1").click()
                    else:
                        time.sleep(3)
                        count += 1
        else:
            print("设备{}，skip_check_of_startapp{}，不做开启权限点击操作".format(devices,skip_check_of_startapp))
        return None


    #判断给定设备的安卓版本号
    def get_androidversion(self):
        command=adb+" -s {} shell getprop ro.build.version.release".format(self.get_mdevice())
        version=os.popen(command).read()[0]
        return int(version)


    def check_device(self):
        ABIcommand = adb + " -s {} shell getprop ro.product.cpu.abi".format(self.get_mdevice())
        ABI = os.popen(ABIcommand).read().strip()
        versioncommand=adb+" -s {} shell getprop ro.build.version.release  ".format(self.get_mdevice())
        version=os.popen(versioncommand).read().strip()
        devicenamecommand = adb + " -s {} shell getprop ro.product.model".format(self.get_mdevice())
        devicename=os.popen(devicenamecommand).read().strip()
        batterycommand=adb+  " -s {} shell dumpsys battery".format(self.get_mdevice())
        battery=os.popen(batterycommand)
        for line in battery:
            if "level:" in line:
                battery=line.split(":")[1].strip()
                break
        wmsizecommand = adb + " -s {} shell wm size".format(self.get_mdevice())
        size = os.popen(wmsizecommand).read().strip()
        size = size.split(":")[1].strip()
        DPIcommand= adb+ " -s {}  shell wm density".format(self.get_mdevice())
        dpi = os.popen(DPIcommand).read().strip()
        if "Override density" in dpi:
            dpi= dpi.split(":")[2].strip()
        else:
            dpi = dpi.split(":")[1].strip()
        android_id_command= adb + " -s {} shell  settings get secure android_id ".format(self.get_mdevice())
        android_id=os.popen(android_id_command).read().strip()
        mac_address_command = adb + " -s {}  shell cat /sys/class/net/wlan0/address".format(self.get_mdevice())
        mac_address=os.popen(mac_address_command).read().strip()
        if "Permission denied" in mac_address:
            mac_address="Permission denied"
        typecommand= adb + " -s {}  shell getprop ro.product.model".format(self.get_mdevice())
        typename=os.popen(typecommand).read().strip()
        brandcommand= adb + " -s {}  shell getprop ro.product.brand".format(self.get_mdevice())
        brand=os.popen(brandcommand).read().strip()
        namecommand=adb + " -s {} shell getprop ro.product.name".format(self.get_mdevice())
        name=os.popen(namecommand).read().strip()
        core_command = adb + " -s {} shell cat /sys/devices/system/cpu/present".format(self.get_mdevice())
        core_num=os.popen(core_command).read().strip()[2]
        core_num=int(core_num)+1
        device=self.get_mdevice()
        package=self.get_packagename()
        activity=self.get_activityname()
        androidversion=self.get_androidversion()
        isSurfaceView=False
        isGfxInfo=False
        SurfaceView_command=""
        if androidversion<7:
            SurfaceView_command=adb+ " -s {} shell dumpsys SurfaceFlinger --latency 'SurfaceView'".format(device)
        elif androidversion==7:
            SurfaceView_command=adb+ " -s {} shell \"dumpsys SurfaceFlinger --latency 'SurfaceView - {}/{}'\"".format(device,package,activity)
        elif androidversion>7:
            SurfaceView_command = adb + " -s {} shell \"dumpsys SurfaceFlinger --latency 'SurfaceView - {}/{}#0'\"".format(device, package, activity)
        print(SurfaceView_command)
        results=os.popen(SurfaceView_command)
        for line in results:
            print("surface",line)
            if line =="16666666":
                continue
            elif len(line)>10:
                isSurfaceView=True
                break

        GfxInfo_command=adb + " -s {} shell dumpsys gfxinfo {}".format(device,package)
        results = os.popen(GfxInfo_command)
        for line in results:
            #print("gfx",line)
            if "Draw" and "Prepare" and "Process" and "Execute" in line:
                isGfxInfo=True
                break
        deviceinfo={"ABI":ABI,"VERSION":version,"DEVICENAME":devicename,"BATTERY":battery,"VMSIZE":size,"DPI":dpi,"ANDROID_ID":android_id,"MAC_ADDRESS":mac_address,"TYPE":typename,"BRAND":brand,"NAME":name,"CORE_NUM":core_num,"isSurfaceView":isSurfaceView,"isGfxInfo":isGfxInfo}
        return  deviceinfo













