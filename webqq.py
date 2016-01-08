#-*- coding:utf-8 -*-

import sys,os,time,random
import urllib2
import urllib
import cookielib
import json
import socket
import MySQLdb
import gevent
from gevent.queue import Queue

class WebQQException(Exception):pass

class WebQQ(object):
    """
    目前每次登陆都要手动填写一些信息:
    ptwebqq
    hash
    psessionid
    vfwebqq
    clientid  -这个值不知道是不是可以任意, 不过目前来说确定下来就不能变
    """
    def __init__(self,handler=None):
        self.handler = None
        self.uin = ""
        self.ptwebqq = ""
        self.hash = ""
        self.psessionid = ""
        self.vfwebqq = ""
        self.clientid = 53999199
        self.appid = 501004106
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        self.friends = {}
        self.groups = {}
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "",
            "Connection": "keep-alive"
        }

    def login(self):
        get_barcode_url = "https://ssl.ptlogin2.qq.com/ptqrshow?" \
                          "appid=%s&e=0&l=M&s=5&d=72&v=4&t=0.2598575626239805" % self.appid
        request = urllib2.Request(get_barcode_url, headers=self.header)
        response = self.opener.open(request)
        with open('barcode.png', 'wb') as f:
            f.write(response.read())
            f.close()

    def login2(self):
        # 为了通过扫描二维码获取登陆信息和 cookie里面的ptwebqq
        retcode = "66"
        headers = self.header
        headers["Referer"] = " http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1"
        while retcode != "0":
            login_url = "https://ssl.ptlogin2.qq.com/ptqrlogin?" \
                        "webqq_type=10&remember_uin=1&login2qq=1&aid={}&" \
                        "u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&" \
                        "ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&" \
                        "action=0-0-67397&mibao_css=m_webqq&t=1&g=1&js_type=0&js_ver=10145&login_sig=&pt_randsalt=0".format(self.appid)
            request2 = urllib2.Request(login_url, headers=self.header)
            response2 = self.opener.open(request2)
            retcode, _, _, _, tip, nickname = eval(response2.read()[6:-3])
            print tip
            time.sleep(1)
        for item in self.cookie:
            if item.name == "ptwebqq":
                self.ptwebqq = item.value
        print self.cookie
        print self.ptwebqq
        print type(self.ptwebqq)
        get_vfwebqq_url ="http://s.web2.qq.com/api/getvfwebqq?" \
                             "ptwebqq={}&" \
                             "clientid={}&" \
                             "psessionid=&t={}".format(self.ptwebqq, self.clientid,int(time.time()*1000))
        print get_vfwebqq_url
        request3 = urllib2.Request(get_vfwebqq_url, headers=headers)
        response3 = self.opener.open(request3)
        print response3.read()

    def login3(self):
        # 通过login2中得到的cookie  来获取psessionid和 vfwebqq
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        login3_url = "http://d1.web2.qq.com/channel/login2"
        post = {
            "ptwebqq": self.ptwebqq,
            "clientid": self.clientid,
            "psessionid": "",
            "status": "online",
        }
        postdata = "r={}".format(self.encode(post))
        request3 = urllib2.Request(login3_url,data=postdata, headers=headers)
        response3 = self.opener.open(request3)
        print postdata
        #return_data = self.send_post(login3_url, postdata, headers)
        print response3.read()
        # print return_data['result']['vfwebqq']
        # if return_data['retcode'] == 0:
        #     self.psessionid = return_data['result']['psessionid']
        #     self.vfwebqq = return_data['result']['vfwebqq']
        # else:
        #     raise WebQQException("get psessionid vfwebqq faild!!!!")
        # print self.psessionid
        # print self.vfwebqq

    def send_post(self, url, post=None, header=None, timeout=60):
        request = urllib2.Request(url, data=post, headers=header)
        response = self.opener.open(request)
        #response = urllib2.urlopen(request)
        return json.loads(response.read())

    def encode(self, code):
        return urllib.quote(json.dumps(code))

    def get_friends_list(self):
        return self.friends

    def get_groups_list(self):
        return self.groups

    def get_user_friends(self):
        headers = self.header
        headers["Referer"] = "http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1"
        url = "http://s.web2.qq.com/api/get_user_friends2"
        post = {
            "vfwebqq": self.vfwebqq,
            "hash": self.hash
        }
        postdata = "r={}".format(self.encode(post))
        friends_list = self.send_post(url,postdata,headers)
        # print friends_list["result"]["info"][1]["uin"]

        if friends_list["retcode"] != 0:
            raise WebQQException("get_friends faild!!!!")

        for i in friends_list["result"]["info"][:]:
             friend_json = self.send_post("http://s.web2.qq.com/api/get_friend_uin2?"\
                               "tuin={}&type=1&"\
                               "vfwebqq={}&"\
                               "t=1451899846020".format(i['uin'],self.vfwebqq),header=headers)
             self.friends[friend_json['result']['account']] = friend_json['result']['uin']
             time.sleep(0.01)
        # print self.friends
        return self

    def get_groups(self):
        headers = self.header
        headers["Referer"] = "http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1"
        url = "http://s.web2.qq.com/api/get_group_name_list_mask2"
        post = {
            "vfwebqq":self.vfwebqq,
            "hash": self.hash
        }
        postdata = "r={}".format(self.encode(post))
        group_list = self.send_post(url,postdata,headers)

        if group_list["retcode"] != 0:
            raise WebQQException("get_groups faild!!!!")

        for i in group_list["result"]["gnamelist"][:]:
            self.groups[i['name']] = i['gid']
        return self

    def send_message(self, uin, message):
        friend_id = self.friends[uin]
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/send_buddy_msg2"
        post = {
            "to": friend_id,
            "content": '[\"%s\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]'%(message),
            "face": 540,
            "clientid": self.clientid,
            "msg_id": 90530032,      # 这个值是可以变的
            "psessionid": self.psessionid
            }
        postdata = "r={}".format(self.encode(post))
        response = self.send_post(url, postdata, headers)
        # print response['errCode']
        return response['errCode']

    def send_group_message(self,gid,message):
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/send_qun_msg2"
        post = {
            "group_uin": gid,
            "content": '[\"%s\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]'% message,
            "face": 540,
            "clientid": self.clientid,
            "msg_id": random.randint(99430009, 99440001),      # 这个值是可以变的
            "psessionid": self.psessionid
            }
        postdata = "r={}".format(self.encode(post))
        response = self.send_post(url, postdata, headers)
        return response['errCode']

# polls是可以接收好友发来的信息的,
    def polls(self):
        pass
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/poll2"
        post = {
            "ptwebqq": self.ptwebqq,
            "clientid": self.clientid,
            "psessionid": self.psessionid,
            "key": ""
            }
        postdata = "r={}".format(self.encode(post))
        request = self.send_post(url, postdata, headers, timeout=65)
        # print request


class SendMessageAPI(object):

    def __init__(self,):
        self.flage = True
        self.send_list = ()
        self.mq = Queue(maxsize=100)
        self.gsl = GetSendList()
        self.webqq = WebQQ()


    def putlist(self):
        while self.flage:
            sendlist = self.gsl.get_send_list()
            if sendlist:
                for i in sendlist:
                    self.mq.put(i)      # 这里可以有try .. execpt
                gevent.sleep(0.1)
            time.sleep(60)

    def send(self):
        while self.flage:
            message = self.mq.get(timeout=1)    # 这里可以有try .. execpt
            id = message[0]
            flage = message[1]
            to = message[2]
            content = message[3].encode('utf-8')
            if flage == "person":
                errCode = self.webqq.send_message(to, content)
                if errCode != 0:
                    self.gsl.change_status(id, 2)
                else:
                    self.gsl.change_status(id, 1)
            time.sleep(1)

    def start(self):
        self.webqq.get_user_friends()
        self.webqq.get_groups()
        gevent.joinall([
            gevent.spawn(self.putlist),
            gevent.spawn(self.send),
        ])

    # def send_to_groups(self, gid_list, content):                        # 这里暂时用for循环  考虑可以用线程
    #     for gid in gid_list:
    #         if self.send_group_message(gid, content) != 0:
    #             print "send to group:%s 's message failed!!!!" % gid  # 这里可以记录成日志 或者改变一下flage
    #
    # def send_to_friends(self, uin_list, content):
    #     for fid in uin_list:
    #         if self.send_message(fid, content) != 0:
    #             print "send to friend:%s 's message failed!!!" % uin_list  # 这里可以记录成日志

    def get_friend_list(self):
        pass

    def get_group_list(self):
        pass


class GetSendList(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='118.26.204.253', user='root', port=3306, db='lzx', passwd='LongHun@Game', charset='utf8')
        self.cursor = self.conn.cursor()

    def get_send_list(self):
        sql = "select iId,sType,sTo,sContents from dzz_qq_assistant where iStatus=0"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def change_status(self, iId, num):
        sql = "update dzz_qq_assistant set iStatus=%s where iId=%s "
        n = self.cursor.execute(sql, (num, iId))
        self.conn.commit()
        return n

if __name__ == '__main__':
    qq = WebQQ()
    # qq.get_groups()
    # qq.get_user_friends()
    # qq.send_message(276949696, 'ok')
    # qq.send_group_message(19223042,"ok")
    # while True:
    #     try:
    #         qq.polls()
    #     except socket.timeout :
    #         print "time out"
    # a = GetSendList()
    # print a.change_status(31492,2)
    # a = SendMessageAPI()
    # a.start()

    qq.login()
    qq.login2()
    qq.login3()


