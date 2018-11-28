from wechatpush import WeChatPublicPush
import pymongo
import threading


class CgPush(WeChatPublicPush):
    def __init__(self, keyword, to_addrlist):
        super(CgPush, self).__init__(keyword, to_addrlist)
        con = pymongo.MongoClient('192.168.1.60', 27017)
        wechat_puhlic = con.wechat_public
        self.mdb = wechat_puhlic.cgtz


class XzPush(WeChatPublicPush):
    def __init__(self, keyword, to_addrlist):
        super(XzPush, self).__init__(keyword, to_addrlist)
        con = pymongo.MongoClient('192.168.1.60', 27017)
        wechat_puhlic = con.wechat_public
        self.mdb = wechat_puhlic.xzlc


cgppush = WeChatPublicPush(keyword='草根投资', to_addrlist=['13402160763@qq.com'])
cgdetail = cgppush.get_detail

threading.Thread(target=cgdetail).start()


xzpush = XzPush(keyword='小猪理财', to_addrlist=['13402160763@qq.com'])
xzdetail = xzpush.get_detail

threading.Thread(target=xzdetail).start()