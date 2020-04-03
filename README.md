基于Python/Airtest/的自动化多设备测试




    
********************************************************************************************************    

首先，先确认你电脑里的adb环境
本框架使用airtest的adb作为默认adb，目前该adb采用40版本，电脑里其他应用如果使用adb且非该版本，会产生冲突。
可以复制\Lib\site-packages\airtest\core\android\static\adb 目录下的所有文件，替换掉本地的其他adb版本。

其次，python的安装目录不要有空格，类似 C:\Program Files\python 这样的目录因为中间有空格，在执行adb命令时会报错。如果不愿意重装python，可以手动修改框架代码里的各个ADB变量，为其指定合理的路径。

********************************************************************************************************


第一次运行前需要手动修改config.ini，里面的包名和包路径是必填项，也支持在运行过程中通过set方式修改。


    madb.set_packagename("")#填待测apk的包名
    madb.set_packagepath("")#填待测apk在硬盘上的绝对路径
    madb.set_TestCasePath("")#填本地测试用例目录的绝对路径
    
程序入口

    from start import *
    
    if __name__ == "__main__":
        start()
        
2./config.ini。整个项目的配置文件。
    
    [config]
    packName填写待测试包名，str；
    activityname 填写测试包的入口类名，留空的话，Madb也会在需要时自动计算，可能会多花一点时间。
    deviceslist填写测试设备名，以逗号分隔，（PS：如不想使用配置，留空即可，则读取当前所有已连接的设备）元组；
    apkpath填写待测试应用的安装地址，须使用绝对路径，str；
    testcase填写期望测试的用例id，须是一个int元组，RunTestCase函数会比对testcase元组与TestCase目录下的TC_*.py文件，在元组内的用例才会被测试；
    needclickinstall和needclickstartapp 填写True或False，设置是否需要安装点击或运行点击，不为True则不执行；
    timeout_of_per_action填写全局sleep时间，int；
    timeout_of_startapp填写安装app等待时间，int（已废弃）；
    iteration填写权限脚本循环次数，int。
    
    skip_pushapk2devices填写“是否跳过pushapk2devices函数”的标志，1为True 0为False，以下同。
    auto_delete_package填写“是否在安装包过程中自动删除设备里的旧包”的标志。
    auto_install_package填写“是否需要重新安装新包”的标志。
    skip_check_of_install填写“是否要跳过安装过程中的自动输入权限检查部分”的标志。
    skip_check_of_startapp填写“是否要跳过安装过程中的自动输入权限检查部分”的标志。
    skip_performance填写“是否要跳过性能监控部分”的标志。
    storage_by_excel填写“是否使用excel存储性能数据”的标志，填1为使用excel，填0为使用json。
    

3./start.py。可以使用pycharm运行，也可以被其他方法调用运行。

4./core/index index是整个框架的索引，负责根据devices分发进程，让每个设备各自去运行enterprocess()函数。该函数里进行设备的初始化，在确保初始化成功、安装包成功的情况下，启动待测试apk并调用RunTestCase函数，进行测试用例的分发。
当needPerformance为True时，还会同步运行enter_performance()函数，对设备进行性能监控并同步记录在excel文件里。

5./core/MultiADB Madb类，集成了各个与device有关的方法。


7.MultiAdb.py里的StartApp函数 。StartApp负责启动apk，然后会进行应用开启权限的点击，此处代码也需要用户自行完成。

12.新增了Performance.py，用以处理adbdump抓取的性能数据，同时在tools目录下新增了Excel.py。用来处理表格。限于adb的效率，大概4、5秒能抓一次，抓取时会同步截图。
划重点：性能测试不支持模拟器，所有的手机模拟器都是x86架构，而99%的安卓手机都是arm架构，adb在不同的架构下抓取dump的返回值不同，所以我写的adb抓性能的代码在模拟器上运行会出错。这不是bug，也不会修。
13.完成性能测试后，会在/Report目录下重新生成xxx_PLUS.html的报告，是在BeautifulReport基础上拼接了性能部分的页面显示。


