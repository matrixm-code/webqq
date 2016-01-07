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
        self.ptwebqq = "586b50666f0b9c8f1a6ec812e7caa1e7fa012a890b1879a785700b6377c0eb51"
        self.hash = "505C0B6706D55486"
        self.psessionid = "8368046764001d636f6e6e7365727665725f77656271714031302e3133332e34312e383400001ad00000066b026e040015808a206d0000000a406172314338344a69526d0000002859185d94e66218548d1ecb1a12513c86126b3afb97a3c2955b1070324790733ddb059ab166de6857"
        self.vfwebqq = "0aba6c04f97f36b391aff85812d59c2bfaf053ddfad9c102b99caec3b6d57adfc70ab03b0d5ccede"
        self.clientid = 53999199
        # self.cookiefile = "C:/Users/FeiYinN/Desktop/cookies.txt"
        # self.cookiejar = cookielib.MozillaCookieJar().load(self.cookiefile,ignore_discard=True,ignore_expires=True)
        self.friends = {}
        self.groups = {}
        self.header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        #"Accept-Encoding":"gzip, deflate", 加上这个就会导致在有时返回的结果是乱码问题
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie":"pgv_pvid=6951714243; ptui_loginuin=421829325; pt2gguin=o0421829325; RK=oPFeGmRyW1; ptcz=f597d32c39fe103f2e09f62992c24012b0f25e1db90b736d98c82e2a947176a4; ts_refer=www.baidu.com/link; ts_uid=9377103228; o_cookie=421829325; pgv_info=ssid=s1856092840; ts_last=web2.qq.com/; pt_clientip=bb2a0a821c3b1fef; pt_serverip=b0bd0a8259676e2c; ptisp=ctc; uin=o0421829325; skey=@Oszrw3mRo; ptwebqq=586b50666f0b9c8f1a6ec812e7caa1e7fa012a890b1879a785700b6377c0eb51; p_uin=o0421829325; p_skey=Zw0FUhimNO5wZ6EwjfXwbigbRndWoP3YxbBtZjW6AqU_; pt4_token=oNLaBsa1uxH9Gv5zuqRmchQrF4sS40BzibNUpADx420_",
        "Referer":"",
        "Connection":"keep-alive"
        }

    def send_post(self,url,post=None,header=None,timeout=60):
        request = urllib2.Request(url,data=post,headers=header)
        # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        # response = opener.open(request)
        response = urllib2.urlopen(request,timeout=timeout)
        return json.loads(response.read())

    def encode(self,code):
        return  urllib.quote(json.dumps(code))

    def get_friends_list(self):
        return self.friends

    def get_groups_list(self):
        return self.groups

    def get_user_friends(self):
        headers = self.header
        headers["Referer"] = "http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1"
        url = "http://s.web2.qq.com/api/get_user_friends2"
        post = {
            "vfwebqq":self.vfwebqq,
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
    # qq = WebQQ()
    # qq.get_groups()
    # qq.get_user_friends()
    # qq.send_message(276949696, 'ok')
    # qq.send_group_message(19223042,"ok")
    # while True:
    #     try:
    #         qq.polls()
    #     except socket.timeout :
    #         print "time out"

    a = SendMessageAPI()
    a.start()

    # a = GetSendList()
    # print a.change_status(31492,2)
