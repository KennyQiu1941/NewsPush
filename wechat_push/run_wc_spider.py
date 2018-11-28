from wechatpush import WeChatPublicPush
import pymongo
import threading
import time

class CgPush(WeChatPublicPush):
    def __init__(self,keyword,to_addrlist):
        super(CgPush,self).__init__(keyword,to_addrlist)
        con = pymongo.MongoClient('192.168.1.60', 27017)
        wechat_puhlic = con.wechat_public
        self.mdb = wechat_puhlic.cgtz


class XzPush(WeChatPublicPush):
    def __init__(self,keyword,to_addrlist):
        super(XzPush,self).__init__(keyword,to_addrlist)
        con = pymongo.MongoClient('192.168.1.60', 27017)
        wechat_puhlic = con.wechat_public
        self.mdb = wechat_puhlic.xzlc


cgppush = WeChatPublicPush(keyword='草根投资', to_addrlist=['***'])
cgstart = cgppush.get_pagenum
cggetpage = cgppush.get_all_page

threading.Thread(target=cgstart).start()
threading.Thread(target=cggetpage).start()


xzpush = XzPush(keyword='小猪理财', to_addrlist=['***'])
xzstart = xzpush.get_pagenum
xzgetpage = xzpush.get_all_page

threading.Thread(target=xzstart).start()
threading.Thread(target=xzgetpage).start()