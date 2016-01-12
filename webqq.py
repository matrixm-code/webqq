# -*- coding:utf-8 -*-

import sys, os, time, random
import urllib2
import urllib
import cookielib
import json
import MySQLdb
import gevent
from gevent.queue import Queue, Empty
from config import dbhost, dbpasswd, dbport, dbuser, db, t_qq_assistant, t_qq_assistant_group

class WebQQException(Exception):
    pass


class WebQQ(object):
    """
    clientid  -这个值不知道是不是可以任意, 不过目前来说确定下来就不能变
    """
    def __init__(self, handler=None):
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
            retcode, _, other_url, _, tip, nickname = eval(response2.read()[6:-3])
            print tip
            time.sleep(1)
        for item in self.cookie:
            if item.name == "ptwebqq":
                self.ptwebqq = item.value
        # 从这里开始有些乱, 因为下面要访问两个网页 目的只是为了获取cookie  不然后面的页面访问会出错.
        get_vfwebqq_url ="http://s.web2.qq.com/api/getvfwebqq?" \
                             "ptwebqq={}&" \
                             "clientid={}&" \
                             "psessionid=&t={}".format(self.ptwebqq, self.clientid, int(time.time()*1000))
        request3 = urllib2.Request(other_url, headers=headers)
        response3 = self.opener.open(request3)
        response3 = self.send_post(get_vfwebqq_url, header=headers)
        self.vfwebqq = response3['result']['vfwebqq']       # 这里获得了vfwebqq

    def login3(self):
        # 通过login2中得到的cookie  来获取psessionid
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
        return_data = self.send_post(login3_url, postdata, headers)
        if return_data['retcode'] == 0:
            self.psessionid = return_data['result']['psessionid']
            # self.vfwebqq = str(return_data['result']['vfwebqq'])
            self.uin = return_data['result']['uin']
            self.hash = self._gethash(self.uin, self.ptwebqq)
        else:
            raise WebQQException("get psessionid vfwebqq faild!!!!")
        # 实验  加的一个访问连接   结果表明,加了这个在poll的时候就会返回正确的值,不然导致返回retode:103
        buddy_url = "http://d1.web2.qq.com/channel/get_online_buddies2?" \
                    "vfwebqq={}&" \
                    "clientid={}&" \
                    "psessionid={}&" \
                    "t=1452481618011".format(self.vfwebqq,self.clientid,self.psessionid)
        response = self.send_post(buddy_url,header=headers)

    def _gethash(self, x, k):
        N = [0, 0, 0, 0]
        V = [0, 0, 0, 0]
        U = [0, 0, 0, 0, 0, 0, 0, 0]
        x = int(x)
        v =''
        n = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        for T in range(len(k)):
            N[T % 4] ^= ord(k[T])

        V[0] = int(x >> 24 & 255 ^ 69)
        V[1] = int(x >> 16 & 255 ^ 67)
        V[2] = int(x >> 8 & 255 ^ 79)
        V[3] = int(x & 255 ^ 75)

        for T in range(8):
            if T % 2 == 0:
                U[T] = N[T >> 1]
            else:
                U[T] = V[T >> 1]

        for T in range(len(U)):
            v += n[U[T] >> 4 & 15]
            v += n[U[T] & 15]
        return v

    def send_post(self, url, post=None, header=None, timeout=60):
        request = urllib2.Request(url, data=post, headers=header)
        response = self.opener.open(request)
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
        friends_list = self.send_post(url, postdata, headers)
        if friends_list["retcode"] != 0:
            raise WebQQException("get_friends faild!!!!")

        for i in friends_list["result"]["info"][:]:
             friend_json = self.send_post("http://s.web2.qq.com/api/get_friend_uin2?"\
                               "tuin={}&type=1&"\
                               "vfwebqq={}&"\
                               "t=1451899846020".format(i['uin'], self.vfwebqq), header=headers)
             self.friends[friend_json['result']['account']] = friend_json['result']['uin']
             time.sleep(0.01)
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
        group_list = self.send_post(url, postdata, headers)

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
            "content": '[\"%s\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]'% message,
            "face": 540,
            "clientid": self.clientid,
            "msg_id": 90530032,      # 这个值是可以变的
            "psessionid": self.psessionid
            }
        postdata = "r={}".format(self.encode(post))
        response = self.send_post(url, postdata, headers)
        return response

    def send_group_message(self, gid, message):
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
        return response

# polls是可以接收好友发来的信息的,
    def polls(self):
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
        return request


class SendMessageAPI(object):

    def __init__(self,):
        self.flage = True
        self.send_list = ()
        self.mq = Queue(maxsize=100)
        self.gsl = GetSqlOpreation()
        self.webqq = WebQQ()
        self.qqfriends = {}
        self.qqgroups = {}

    def putlist(self):
        while self.flage:
            sendlist = self.gsl.get_send_list()
            print(sendlist)
            if sendlist:
                for i in sendlist:
                    self.mq.put(i)      # 这里可以有try .. execpt
            gevent.sleep(10)
            #time.sleep(10)

    def send(self):
        while self.flage:
            try:
                message = self.mq.get(timeout=1)    # 这里可以有try .. execpt
                id = message[0]
                flage = message[1]
                to = message[2]
                content = message[3].encode('utf-8')
                if flage == "person" and to in self.qqfriends:
                    errCode = self.webqq.send_message(to, content)
                    if errCode["errCode"] != 0:
                        self.gsl.change_status(id, 2)
                    else:
                        self.gsl.change_status(id, 1)
                elif flage == "group":
                    errCode = self.webqq.send_group_message(to, content)
                    if errCode["errCode"] != 0:
                        self.gsl.change_status(id, 2)
                    else:
                        self.gsl.change_status(id, 1)
                else:
                    self.gsl.change_status(id, 4)
                time.sleep(0.5)
            except Empty:
                gevent.sleep(0.1)
            except KeyError, e:
                self.gsl.change_status(id, 4)

    def pollmessage(self):
        while self.flage:
            print self.webqq.polls()
            gevent.sleep(0.1)

    def group_list_tosql(self):
        errnum = 0
        while self.flage:
            try:
                self.webqq.get_groups()
                self.qqgroups = self.webqq.get_groups_list()
                print "I got group list"
                for gname, gid in self.qqgroups.items():
                    self.gsl.update_group_id(gname, gid)
                gevent.sleep(1800)
            except WebQQException:
                if errnum < 3:
                    errnum += 1
                    continue
                else:
                    errnum = 0
                    raise WebQQException("get_group Faill !!!!")

    def start(self):
        self.webqq.login()
        self.webqq.login2()
        self.webqq.login3()
        self.webqq.get_user_friends()
        #self.webqq.get_groups()
        self.qqfriends = self.webqq.get_friends_list()
        #self.qqgroups = self.webqq.get_groups_list()
        gevent.joinall([
            gevent.spawn(self.group_list_tosql),
            gevent.spawn(self.putlist),
            gevent.spawn(self.send),
            gevent.spawn(self.pollmessage),
        ])


class GetSqlOpreation(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host=dbhost, user=dbuser, port=dbport, db=db, passwd=dbpasswd, charset='utf8')
        self.cursor = self.conn.cursor()

    def get_send_list(self):
        sql = "select iId,sType,sTo,sContents from {} where iStatus=0".format(t_qq_assistant)
        self.cursor.execute(sql)
        self.conn.commit()           # 不加这个会出问题
        return self.cursor.fetchall()

    def change_status(self, iId, num):
        sql = "update {} set iStatus=%s where iId=%s ".format(t_qq_assistant)
        n = self.cursor.execute(sql, (num, iId))
        self.conn.commit()
        return n

    def update_group_id(self, gname, gid):
        sql = "select * from {} where gname=%s".format(t_qq_assistant_group)
        sql2 = "insert into {} (gname,gid) values(%s,%s)".format(t_qq_assistant_group)
        n = self.cursor.execute(sql, gname)
        if not n:
            self.cursor.execute(sql2, (gname, gid))
        self.conn.commit()
        return n

if __name__ == '__main__':
    # qq = WebQQ()
    # qq.login()
    # qq.login2()
    # qq.login3()
    # qq.get_groups()
    # qq.get_user_friends()
    # qq.polls()
    # qq.send_message(276949696, 'ok')
    # qq.send_group_message(19223042,"ok")
    # while True:
    #     try:
    #         qq.polls()
    #         time.sleep(0.5)
    #     except socket.timeout:
    #         print "time out"
    # a = GetSqlOpreation()
    # a.update_group_id('我是谁', 12334456)
    a = SendMessageAPI()
    a.start()



