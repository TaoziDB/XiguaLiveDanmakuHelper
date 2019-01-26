import sys
import time
from datetime import datetime
import m3u8
import queue
import threading
from config import config
from api import XiGuaLiveApi
from bilibili import *

q = queue.Queue()
base_uri = ""
isUpload = False
uq = queue.Queue()
d = datetime.strftime(datetime.now(),"%Y_%m_%d")

class downloader(XiGuaLiveApi):
    files = []
    playlist: str = None

    def updRoomInfo(self):
        super(downloader, self).updRoomInfo()
        self.updPlayList()

    def updPlayList(self):
        if "playInfo" not in self._rawRoomInfo or "Main" not in self._rawRoomInfo["playInfo"]:
            if self.playlist is None:
                self.apiChangedError("无法获取直播链接")
                self.playlist = False
        else:
            self.playlist = self._rawRoomInfo["playInfo"]["Main"]["1"]["Url"]["HlsUrl"]

    def onLike(self, user):
        pass
    def onAd(self, i):
        pass
    def onChat(self, chat):
        pass
    def onEnter(self, msg):
        pass
    def onJoin(self, user):
        pass
    def onLeave(self, json):
        self.updRoomInfo()
    def onMessage(self, msg):
        pass
    def onPresent(self, gift):
        pass
    def onPresentEnd(self, gift):
        pass
    def onSubscribe(self, user):
        pass
    def preDownload(self):
        global base_uri
        if self.playlist:
            try:
                p = m3u8.load(self.playlist)
            except:
                self.updRoomInfo()
                return
            base_uri = p.base_uri
            for i in p.files:
                if i not in self.files:
                    self.files.append(i)
                    print("{} : Add Sequence {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"),
                                                         len(self.files)))
                    q.put(i)
        self.genNewName()
    def genNewName(self):
        if len(self.files) > 800:
            q.put(True)
            self.files.clear()


def download(path=datetime.strftime(datetime.now(),"%Y%m%d_%H%M.ts")):
    global isUpload
    print("{} : Download Daemon Starting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
    n = False
    isUpload = False
    i = q.get()
    while True:
        if isinstance(i, bool):
            print("{} : Download Daemon Receive Command {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
            break
        print("{} : Download {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
        try:
            _p = requests.get("{}{}".format(base_uri,i))
        except:
            continue
        f = open(path, "ab")
        f.write(_p.content)
        f.close()
        n=True
        i = q.get()
    if n:
        uq.put(path)
    print("{} : Download Daemon Quiting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
    isUpload = True



def upload(date = datetime.strftime(datetime.now(), "%Y_%m_%d")):
    print("{} : Upload Daemon Starting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))
    i = uq.get()
    while True:
        if isinstance(i, bool):
            if i is True:
                print("自动投稿中，请稍后")
                b.finishUpload(config["t_t"].format(date),17, config["tag"],config["des"],
                               source= "https://live.ixigua.com/userlive/97621754276", no_reprint= 0)
            print("{} : Upload Daemon Receive Command {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
            break
        print("{} : Upload {}".format(datetime.strftime(datetime.now(), "%y%m%d %H%M"), i))
        try:
            b.preUpload(VideoPart(i, i))
        except:
            continue
        i = uq.get()
    print("{} : Upload Daemon Quiting".format(datetime.strftime(datetime.now(), "%y%m%d %H%M")))


b = Bilibili()
b.login(config["b_u"], config["b_p"])

if __name__ == "__main__":
    room = 97621754276  # 永恒
    # room = 75366565294
    # room = 83940182312 #Dae
    # room = 5947850784 #⑦
    # room = 58649240617 #戏
    if len(sys.argv) > 1:
        try:
            room = int(sys.argv[1])
        except ValueError:
            pass
    print("西瓜直播录播助手 by JerryYan")
    api = downloader(room)
    print("进入", api.roomLiver, "的直播间")
    if not api.isValidRoom:
        input("房间不存在")
        sys.exit()
    print("=" * 30)
    _preT = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.ts")
    t = threading.Thread(target=download, args=(_preT,))
    ut = threading.Thread(target=upload, args=(d,))
    while True:
        if api.isLive:
            if d is None:
                d = datetime.strftime(datetime.now(), "%Y_%m_%d")
            if not t.is_alive():
                _preT = datetime.strftime(datetime.now(), "%Y%m%d_%H%M.ts")
                t = threading.Thread(target=download, args=(_preT,))
                t.setDaemon(True)
                t.start()
            if not ut.is_alive():
                ut = threading.Thread(target=upload, args=(d,))
                ut.setDaemon(True)
                ut.start()
            try:
                api.preDownload()
            except:
                pass
            time.sleep(3)
        else:
            q.put(False)
            if isUpload:
                uq.put(True)
                isUpload = False
            else:
                pass
                # print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            d=None
            api.updRoomInfo()
