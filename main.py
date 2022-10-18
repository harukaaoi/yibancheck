import time
from urllib import parse
import requests
from requests import cookies



class person:
    def __init__(self, loginToken, deviceData, UA, name, bark):
        self.loginToken = loginToken
        self.name = name
        self.bark = bark
        self.deviceData = deviceData
        self.UA = UA  
        self.log = ''  # 保存日志
        self.session = requests.Session()
        # 打卡
        self.post()

    def post(self):
        AppVersion = '5.0.13'
        for i in range(3):  # 尝试3次打卡
            time.sleep(3)
            date = time.strftime("%Y-%m-%d", time.localtime())

            # 第一次重定向
            # 从 http://f.yiban.cn/iapp378946 到 http://f.yiban.cn/iapp/index?act=iapp378946
            header1 = {
                'Host': 'f.yiban.cn',
                'Authorization': 'Bearer ' + self.loginToken,
                'AppVersion': AppVersion,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'loginToken': self.loginToken,
                'User-Agent': self.UA,
                'Connection': 'keep-alive'
            }
            url_1 = 'https://f.yiban.cn/iapp378946'
            try:
                a = self.session.get(url=url_1, headers=header1, allow_redirects=False)
                if "Location" not in a.headers:
                    self.log = self.log + '易班服务器异常\n'
                    yb_result = {'code': 404, 'msg': '易班服务器异常'}
                    return yb_result
            except Exception:
                self.log = self.log + '第一次重定向出错\n'
                continue

            # 第二次重定向
            # 从 http://f.yiban.cn/iapp/index?act=iapp378946 到 ygj判断授权界面
            url_2 = a.headers['Location']
            header2 = {
                'Host': 'f.yiban.cn',
                'AppVersion': AppVersion,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'loginToken': self.loginToken,
                'User-Agent': self.UA,
                'Connection': 'keep-alive'
            }
            try:
                b = self.session.get(url=url_2, headers=header2, allow_redirects=False)
                if "Location" not in b.headers:
                    self.log = self.log + 'loginToken错误\n'
                    yb_result = {'code': 555, 'msg': 'loginToken错误，请修改'}
                    return yb_result
            except Exception:
                self.log = self.log + '第二次重定向出错\n'
                continue

            # 跳转到易广金 得到cookie

            url_3 = b.headers['Location']  # ygj.gduf.edu.cn/index.aspx?verify_request-.......

            header3 = {
                'Host': 'ygj.gduf.edu.cn',
                'AppVersion': AppVersion,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'loginToken': self.loginToken,
                'User-Agent': self.UA,
                'Connection': 'keep-alive'
            }
            try:
                c = self.session.get(url=url_3, headers=header3, allow_redirects=False)
            except Exception:
                self.log = self.log + '第三次重定向出错\n'
                continue
            
            # 新增第四次重定向

            header4 = {
                'Host': 'ygj.gduf.edu.cn',
                'AppVersion': AppVersion,
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'loginToken': self.loginToken,
                'User-Agent': self.UA,
                'Connection': 'keep-alive',
            }
            url_4 = c.headers['Location']
            d = self.session.get(url=url_4, headers=header4, allow_redirects=False)    

            # 拿到StudentID
            ygjhome = "https://ygj.gduf.edu.cn"+d.text.split("href=")[1].split("<")[0].replace("'","")
            studentID = ygjhome.split('=')[1]
            # 进入易广金首页
            self.session.get(url=ygjhome, headers=header4)

            # GetNotice
            header_api = {
                'Host': 'ygj.gduf.edu.cn',
                'Accept': '*/*',
                'Cookie': d.headers['Set-Cookie'],
                "X-Requested-With": "XMLHttpRequest",
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://ygj.gduf.edu.cn",
                'User-Agent': self.UA,
                'Connection': 'keep-alive'
            }
            self.session.post(url='https://ygj.gduf.edu.cn/Handler/device.ashx?flag=getNotice',
                                headers=header_api, data={'studentID': studentID}).json()
                                       


            # 检查绑定设备
            url_bind = "https://ygj.gduf.edu.cn/Handler/device.ashx?flag=checkBindDevice"
            
            devicedata = {
                "deviceData": self.deviceData,
                "autoBind": "false"
            }

            self.session.post(url=url_bind, headers=header_api,data=devicedata)

            # 进入健康打卡页面
            header_html = {
                'Host': 'ygj.gduf.edu.cn',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'User-Agent': self.UA,
                'Connection': 'keep-alive',
                'Cookie': d.headers['Set-Cookie']
            }
            url_health = 'https://ygj.gduf.edu.cn/ygj/health/student-index.aspx'
            self.session.get(url=url_health, headers=header_html)

            # GetStudentInfo
            header_api['Referer'] = url_health
            self.session.post(url='https://ygj.gduf.edu.cn/Handler/health.ashx?flag=getStudentInfo', headers=header_api, verify = False,
                              data={"studentID": studentID})

            # 进入今日打卡界面
            url_today = "https://ygj.gduf.edu.cn/ygj/health/student-add.aspx"
            header_html['Referer'] = url_health
            self.session.get(url=url_today, headers=header_html )

            # 检查打卡记录
            url_check = 'https://ygj.gduf.edu.cn/Handler/health.ashx?flag=getHealth'
            check_header = {
                'Host': 'ygj.gduf.edu.cn',
                'Accept': '*/*',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://ygj.gduf.edu.cn',
                'User-Agent': self.UA,
                'Connection': 'keep-alive',
                "Referer": url_today,
                'Cookie': d.headers['Set-Cookie']
            }
            check_data = {
                'studentID': studentID,
                'date': date
            }

            
            self.session.post(url=url_check, headers=check_header, data=check_data).json()

            # 判断今日是否已打卡
            if True:
                headers = {
                "Host": "ygj.gduf.edu.cn",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Accept-Language": "zh-CN,zh-Hans;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://ygj.gduf.edu.cn",
                "User-Agent": self.UA,
                "Connection": "keep-alive",
                'Cookie': d.headers['Set-Cookie']
                }
                data = {
                "studentID": studentID
                }
                res = self.session.post(url="https://ygj.gduf.edu.cn/Handler/health.ashx?flag=getHistoryList",data=data,
                            headers=headers).json()
                # 查询成功
                if res['code'] == 0:
                    self.addressinfo = res['data'][0]
                    self.log = self.log + "获取打卡地址成功\n打卡地址为:" + self.addressinfo['address'] + '\n'

                else:
                    self.log = self.log + "获取打卡地址失败"
                    return 1
                # 打卡
                url_save = "https://ygj.gduf.edu.cn/Handler/health.ashx?flag=save"
                save_headers = {
                    'Host': 'ygj.gduf.edu.cn',
                    'Accept': '*/*',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Origin': 'https://ygj.gduf.edu.cn',
                    'User-Agent': self.UA,
                    'Connection': 'keep-alive',
                    "Referer": "https://ygj.gduf.edu.cn/ygj/health/student-add.aspx",
                    'Cookie': d.headers['Set-Cookie']
                }
                data_yb_save = {
                    "studentID": studentID,
                    "date": date,
                    "health": "体温37.3℃以下（正常）",
                    "address": self.addressinfo['address'],
                    "isTouch": "否",
                    "isPatient": "不是",
                    'latitude':self.addressinfo['latitude'],
                    'longitude':self.addressinfo['longitude'],
                    "autoAddress": '1'}
                
                yb_result = self.session.post(url=url_save, headers=save_headers, data=data_yb_save).json()
                if yb_result["code"] == 0 :
                    api = "https://api.day.app/%s/%s易班打卡结果%s?" % (self.bark, self.name,yb_result)
                    requests.get(url=api)
                else:
                    api = "https://api.day.app/%s/%s易班打卡失败%s?" % (self.bark, self.name, yb_result)
                    requests.get(url=api)
                    return 1
                return 0
                
            
        return {'code': 404, 'msg': "打卡失败了"}

information=[ 
        [
            '4ws5u6wja4w6juartha45uj6e87oek867', # 32位的loginToken
            '{"uuid":"123F123123D-6CE2-4035-BD75-D081231231","appVersion":"5.0.13","deviceModel":"iPhone+X","systemVersion":"16.0.2"}', # deviceData
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 yiban_iOS/5.0.13", # User-Agent
            "某某某", #打卡人的匿称或姓名
            "bavwoevfweouvbawev"], #bark token
        [
            'wj56jws56jke678kws45j4w6jw5rjhaq',
            '{"uuid":"123F123123D-6CE2-4035-BD75-D081231231","appVersion":"5.0.13","deviceModel":"iPhone+X","systemVersion":"15.5"}',
            "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 yiban_iOS/5.0.13",
            "某某某",
            "cqanweoirgvfbn3vcfw"] #多人打卡示例
        
]
for i in range(len(information)):
	person(*information[i])