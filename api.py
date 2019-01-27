import sys

from MemberMsg import MemberMsg
from User import User
from Gift import Gift
from Chat import Chat
import requests
import time

s = requests.Session()

DEBUG: bool = False


class XiGuaLiveApi:
    isLive: bool = False
    isValidRoom: bool = False
    _rawRoomInfo = {}
    roomID: int = 0
    roomTitle: str = ""
    roomLiver: User = None
    roomPopularity: int = 0
    roomMember: int = 0
    _cursor = ""

    def __init__(self, room: int):
        self.room = room
        self.updRoomInfo()
        Gift.update(self.roomID)
        self._enterRoom()

    def _updateRoomInfo(self, json):
        if "Msg" in json:
            if "member_count" in json["Msg"]:
                self.roomMember = json["Msg"]["member_count"]
            if "popularity" in json["Msg"]:
                self.roomPopularity = json["Msg"]["popularity"]
        elif "data" in json:
            if "popularity" in json["data"]:
                self.roomPopularity = json["data"]["popularity"]

    def apiChangedError(self, msg: str, *args):
        print(msg)
        print(*args)

    def onPresent(self, gift: Gift):
        print("礼物连击 :", gift)

    def onPresentEnd(self, gift: Gift):
        print("感谢", gift)

    def onAd(self, i):
        # print(i)
        pass

    def onChat(self, chat: Chat):
        print(chat)

    def onEnter(self, msg: MemberMsg):
        print("提示 :", msg)

    def onSubscribe(self, user: User):
        print("消息 :", user, "关注了主播")

    def onJoin(self, user: User):
        print("感谢", user, "加入了粉丝团")

    def onMessage(self, msg: str):
        print("消息 :", msg)

    def onLike(self, user: User):
        print("用户", user, "点了喜欢")

    def onLeave(self, json: any):
        print("消息 :", "主播离开一小会")

    def _enterRoom(self):
        if not self.isValidRoom:
            return
        p = s.post("https://live.ixigua.com/api/room/enter/{roomID}".format(roomID=self.roomID))
        if DEBUG:
            print(p.text)

    def updRoomInfo(self):
        p = s.get("https://live.ixigua.com/api/room?anchorId={room}".format(room=self.room))
        if DEBUG:
            print(p.text)
        d = p.json()
        if "data" not in d or "title" not in d["data"] or "id" not in d["data"]:
            self.apiChangedError("无法获取RoomID，请与我联系")
            return
        self.isValidRoom = True
        self._rawRoomInfo = d["data"]
        self.roomLiver = User(d)
        self.roomTitle = d["data"]["title"]
        self.roomID = d["data"]["id"]
        self._updateRoomInfo(d)
        if "status" in d["data"] and d["data"]["status"] == 2:
            self.isLive = True
        else:
            self.isLive = False

    def getDanmaku(self):
        if not self.isValidRoom:
            return
        p = s.get("https://live.ixigua.com/api/msg/list/{roomID}?AnchorID={room}&Cursor={cursor}".format(
            roomID=self.roomID,
            room=self.room,
            cursor=self._cursor
        ))
        d = p.json()
        if "data" not in d or "Extra" not in d["data"] or "Cursor" not in d["data"]["Extra"]:
            if DEBUG:
                print(d)
            self.apiChangedError("数据结构改变，请与我联系")
            return
        else:
            self._cursor = d["data"]["Extra"]["Cursor"]
            if DEBUG:
                print("Cursor", self._cursor)
        if "LiveMsgs" not in d["data"]:
            self.updRoomInfo()
            return
        for i in d['data']['LiveMsgs']:
            if DEBUG:
                print(i)
            if "Method" not in i:
                continue
            if i['Method'] == "VideoLivePresentMessage":
                self.onPresent(Gift(i))
            elif i['Method'] == "VideoLivePresentEndTipMessage":
                self.onPresentEnd(Gift(i))
            elif i['Method'] == "VideoLiveRoomAdMessage":
                self.onAd(i)
            elif i['Method'] == "VideoLiveChatMessage":
                self.onChat(Chat(i))
            elif i['Method'] == "VideoLiveMemberMessage":
                self._updateRoomInfo(i)
                self.onEnter(MemberMsg(i))
            elif i['Method'] == "VideoLiveSocialMessage":
                self.onSubscribe(User(i))
            elif i['Method'] == "VideoLiveJoinDiscipulusMessage":
                self.onJoin(User(i))
            elif i['Method'] == "VideoLiveControlMessage":
                print("消息：", "主播离开一小会")
            elif i['Method'] == "VideoLiveDiggMessage":
                self.onLike(User(i))
            else:
                pass


if __name__ == "__main__":
    room = 97621754276  # 永恒
    # room = 75366565294
    # room = 83940182312 #Dae
    if len(sys.argv) > 1:
        if sys.argv[-1] == "d":
            DEBUG = True
        try:
            room = int(sys.argv[1])
        except ValueError:
            pass
    print("西瓜直播弹幕助手 by JerryYan")
    api = XiGuaLiveApi(room)
    print("进入", api.roomLiver, "的直播间")
    if not api.isValidRoom:
        input("房间不存在")
        sys.exit()
    print("=" * 30)
    while True:
        if api.isLive:
            try:
                api.getDanmaku()
            except Exception as e:
                print(e)
            time.sleep(1)
        else:
            print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
