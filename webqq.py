#-*- coding:utf-8 -*-

import sys,os,time
import urllib2
import urllib
import cookielib
import json

class WebQQException(Exception):pass

class WebQQ(object):
    def __init__(self,handler=None):
        self.handler = None
        self.uin = ""
        self.ptwebqq = ""
        self.hash = "555C09670DD55686"
        self.psessionid = "8368046764001d636f6e6e7365727665725f77656271714031302e3133332e34312e383400001ad00000066b026e040015808a206d0000000a406172314338344a69526d0000002859185d94e66218548d1ecb1a12513c86126b3afb97a3c2955b1070324790733ddb059ab166de6857"
        self.vfwebqq = "64652b3bc9997319ccd6cf2bf295b3956363fad33b36ae100141c320d0d707e591bf181ad90cbf67"
        self.clientid = 53999199
        # self.cookiefile = "C:/Users/FeiYinN/Desktop/cookies.txt"
        # self.cookiejar = cookielib.MozillaCookieJar().load(self.cookiefile,ignore_discard=True,ignore_expires=True)
        self.friends = {}
        self.groups = {}
        self.header = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding":"gzip, deflate",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie":"pgv_pvid=6951714243; ptui_loginuin=421829325; pt2gguin=o0421829325; RK=oPFeGmRyW1; ptcz=f597d32c39fe103f2e09f62992c24012b0f25e1db90b736d98c82e2a947176a4; ts_refer=www.baidu.com/link; ts_uid=9377103228; o_cookie=421829325; pgv_info=ssid=s939526324; ts_last=web2.qq.com/; pt_clientip=b3b10a821c5895d3; pt_serverip=16770aa687cc78a8; ptisp=ctc; uin=o0421829325; skey=@4n5btCwtK; ptwebqq=b41243e031e6d35bb44dacdbf9ae061ec8d82532b4cd37d8d5ec4f22a8810160; p_uin=o0421829325; p_skey=jh3M0As5SonOk3rgQyRdnX35hkfFKIrChrIx9o6F1Qo_; pt4_token=zyUUAhnGGQfDOBRKBO7lRbLZAKPkazYe-9qHQe-HtB8_",
        "Referer":"",
        "Connection":"keep-alive"
        }

    def send_post(self,url,post=None,header=None):
        request = urllib2.Request(url,data=post,headers=header)
        # opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        # response = opener.open(request)
        response = urllib2.urlopen(request)
        return json.loads(response.read())

    def encode(self,code):
        return  urllib.quote(json.dumps(code))


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
        #print friends_list["result"]["info"][1]["uin"]

        if friends_list["retcode"] != 0:
            raise WebQQException("get_friends faild!!!!")

        for i in friends_list["result"]["info"][:]:
             friend_json = self.send_post("http://s.web2.qq.com/api/get_friend_uin2?"\
                               "tuin={}&type=1&"\
                               "vfwebqq=64652b3bc9997319ccd6cf2bf295b3956363fad33b36ae100141c320d0d707e591bf181ad90cbf67&"\
                               "t=1451899846020".format(i['uin']),header=headers)
             self.friends[friend_json['result']['account']] = friend_json['result']['uin']
             time.sleep(0.01)
        #print self.friends
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

    def sendMessage(self,friend_uin,message):
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/send_buddy_msg2"
        post = {
            "to":friend_uin,
            "content":'[\"%s\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]'%(message),
            "face":540,
            "clientid":self.clientid,
            "msg_id":90530032,      #这个值是可以变的
            "psessionid":self.psessionid
            }
        postdata = "r={}".format(self.encode(post))
        request = urllib2.Request(url,data=postdata,headers=headers)
        response = urllib2.urlopen(request)
        return self

    def send_group_message(self,gid,message):
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/send_qun_msg2"
        post = {
            "to":gid,
            "content":'[\"%s\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]'%(message),
            "face":540,
            "clientid":self.clientid,
            "msg_id":90530004,      #这个值是可以变的
            "psessionid":self.psessionid
            }
        postdata = "r={}".format(self.encode(post))
        request = urllib2.Request(url,data=postdata,headers=headers)
        response = urllib2.urlopen(request)
        return self

    def polls(self):
        pass




if __name__ == '__main__':
    qq = WebQQ()
    qq.get_groups()
    print qq.groups
    #qq.sendMessage(160453794,'好')
    qq.send_group_message(1613719089,"o000k")
