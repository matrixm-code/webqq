#-*- coding:utf-8 -*-

import sys,os,time,random
import urllib2
import urllib
import cookielib
import json
import socket

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
        self.ptwebqq = "f1c4470627ca82dc77bb75c77f25cb402991100d52b1c6c21cf390405050eb9c"
        self.hash = "015C096705D55686"
        self.psessionid = "8368046764001d636f6e6e7365727665725f77656271714031302e3133332e34312e383400001ad00000066b026e040015808a206d0000000a406172314338344a69526d0000002859185d94e66218548d1ecb1a12513c86126b3afb97a3c2955b1070324790733ddb059ab166de6857"
        self.vfwebqq = "e480fdb18e2383b9cef8529954f403b36b76bc56071bc1e70bd6275f6bbca11d3833d8592d715e7f"
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
        "Cookie":"pgv_pvid=6951714243; ptui_loginuin=421829325; pt2gguin=o0421829325; RK=oPFeGmRyW1; ptcz=f597d32c39fe103f2e09f62992c24012b0f25e1db90b736d98c82e2a947176a4; ts_refer=www.baidu.com/link; ts_uid=9377103228; o_cookie=421829325; pgv_info=ssid=s3294480201; ts_last=web2.qq.com/; pt_clientip=9c210a82158ac86a; pt_serverip=521c0aa687ccad10; ptisp=ctc; uin=o0421829325; skey=@Kzi4pHXtP; ptwebqq=f1c4470627ca82dc77bb75c77f25cb402991100d52b1c6c21cf390405050eb9c; p_uin=o0421829325; p_skey=zsp*1lmyXKuUb4htVyyrUPagDnWF2zLm6HUyGpC9a-Y_; pt4_token=rL01YBlOb73osKmca2Ngg6OcJosLAAabv46zSJ0N0J0_:",
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
        #print friends_list["result"]["info"][1]["uin"]

        if friends_list["retcode"] != 0:
            raise WebQQException("get_friends faild!!!!")

        for i in friends_list["result"]["info"][:]:
             friend_json = self.send_post("http://s.web2.qq.com/api/get_friend_uin2?"\
                               "tuin={}&type=1&"\
                               "vfwebqq={}&"\
                               "t=1451899846020".format(i['uin'],self.vfwebqq),header=headers)
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

    def sendMessage(self,uin,message):
        friend_id = self.friends[uin]
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/send_buddy_msg2"
        post = {
            "to":friend_id,
            "content":'[\"%s\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]'%(message),
            "face":540,
            "clientid":self.clientid,
            "msg_id":90530032,      #这个值是可以变的
            "psessionid":self.psessionid
            }
        postdata = "r={}".format(self.encode(post))
        response = self.send_post(url,postdata,headers)
        #print response
        return response["errCode"]

    def send_group_message(self,gid,message):
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/send_qun_msg2"
        post = {
            "group_uin":gid,
            "content":'[\"%s\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]'%(message),
            "face":540,
            "clientid":self.clientid,
            "msg_id":random.randint(99430009,99440001),      #这个值是可以变的
            "psessionid":self.psessionid
            }
        postdata = "r={}".format(self.encode(post))
        response = self.send_post(url,postdata,headers)
        return response["errCode"]

#polls是可以接收好友发来的信息的,
    def polls(self):
        pass
        headers = self.header
        headers["Referer"] = "http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2"
        url = "http://d1.web2.qq.com/channel/poll2"
        post = {
            "ptwebqq":self.ptwebqq,
            "clientid":self.clientid,
            "psessionid":self.psessionid,
            "key":""
            }
        postdata = "r={}".format(self.encode(post))
        request = self.send_post(url,postdata,headers,timeout=5)
        #print request

class send_message_api(WebQQ):
    def __init__(self,typeflage,send_list,content):
        self.typeflage = typeflage
        self.send_list = send_list
        self.content = content

    def SendToGroup(self,gid_list,content):
        for gid in gid_list:
            if self.send_group_message(gid,content) != 0:
                print "send to group:%s 's message failed!!!!" % (gid)  #这里可以记录成日志 或者改变一下flage

    def SendToFriends(self,uin_list,content):
        for fid in uin_list:
            if self.sendMessage(fid,content) !=0:
                print "send to friend:%s 's message failed!!!" % (uin)  #这里可以记录成日志

    def GetfriendList(self):
        pass
    def GetgroupList(self):
        pass



if __name__ == '__main__':
    qq = WebQQ()
    qq.get_groups()
    qq.get_user_friends()
    try:
        qq.polls()
    except socket.timeout:
        print "time out"
    #print qq.groups
    # print qq.friends[276949696]
    qq.sendMessage(qq.friends[276949696],'ok')
    qq.send_group_message(19223042,"okjhg")
    while True:
        try:
            qq.polls()
        except socket.timeout :
            print "time out"