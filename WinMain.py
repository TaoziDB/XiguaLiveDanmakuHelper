import os
import sys
import time

from Gift import Gift
from MemberMsg import MemberMsg
from User import User

from Chat import Chat
from api import XiGuaLiveApi as Api
import msvcrt
import ctypes


def readInput(caption, default, timeout: int = 5):
    start_time = time.time()
    print('{}({})\r\n>'.format(caption, default), end="")
    input = ''
    while True:
        if msvcrt.kbhit():
            chr = msvcrt.getche()
            if ord(chr) == 13:  # enter_key
                break
            elif ord(chr) == 27:
                break
            elif ord(chr) == 8:
                if input != "":
                    input = input[:-1]
                    msvcrt.putch(b" ")
                    msvcrt.putch(b"\b")
                if len(input) == 0:
                    start_time = time.time()
            elif 32 <= ord(chr) <= 126:  # space_char
                input += chr.decode("utf8")
        if len(input) == 0 and (time.time() - start_time) > timeout:
            break

    if len(input) > 0:
        print()
        return input
    else:
        print("使用默认值")
        return default


STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12
std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
# 字体颜色定义 ,关键在于颜色编码，由2位十六进制组成，分别取0~f，前一位指的是背景色，后一位指的是字体色
# 由于该函数的限制，应该是只有这16种，可以前景色与背景色组合。也可以几种颜色通过或运算组合，组合后还是在这16种颜色中

# Windows CMD命令行 字体颜色定义 text colors
FOREGROUND_BLACK = 0x00  # black.
FOREGROUND_DARKBLUE = 0x01  # dark blue.
FOREGROUND_DARKGREEN = 0x02  # dark green.
FOREGROUND_DARKSKYBLUE = 0x03  # dark skyblue.
FOREGROUND_DARKRED = 0x04  # dark red.
FOREGROUND_DARKPINK = 0x05  # dark pink.
FOREGROUND_DARKYELLOW = 0x06  # dark yellow.
FOREGROUND_DARKWHITE = 0x07  # dark white.
FOREGROUND_DARKGRAY = 0x08  # dark gray.
FOREGROUND_BLUE = 0x09  # blue.
FOREGROUND_GREEN = 0x0a  # green.
FOREGROUND_SKYBLUE = 0x0b  # skyblue.
FOREGROUND_RED = 0x0c  # red.
FOREGROUND_PINK = 0x0d  # pink.
FOREGROUND_YELLOW = 0x0e  # yellow.
FOREGROUND_WHITE = 0x0f  # white.

# Windows CMD命令行 背景颜色定义 background colors
BACKGROUND_BLUE = 0x10  # dark blue.
BACKGROUND_GREEN = 0x20  # dark green.
BACKGROUND_DARKSKYBLUE = 0x30  # dark skyblue.
BACKGROUND_DARKRED = 0x40  # dark red.
BACKGROUND_DARKPINK = 0x50  # dark pink.
BACKGROUND_DARKYELLOW = 0x60  # dark yellow.
BACKGROUND_DARKWHITE = 0x70  # dark white.
BACKGROUND_DARKGRAY = 0x80  # dark gray.
BACKGROUND_BLUE = 0x90  # blue.
BACKGROUND_GREEN = 0xa0  # green.
BACKGROUND_SKYBLUE = 0xb0  # skyblue.
BACKGROUND_RED = 0xc0  # red.
BACKGROUND_PINK = 0xd0  # pink.
BACKGROUND_YELLOW = 0xe0  # yellow.
BACKGROUND_WHITE = 0xf0  # white.


def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool


def resetColor():
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)


class WinMain(Api):
    _tmp = 0

    def getTitle(self):
        self._tmp += 1
        if self._tmp > 10:
            self._tmp = 0
        if self._tmp < 5 :
            return "{} {} --弹幕助手 by JerryYan".format(self.roomLiver, "的直播间")
        else:
            if self.roomPopularity == 0:
                self._tmp = 0
                return self.getTitle()
            else:
                if self.roomMember > 0:
                    return "观看:{} 人气:{} --弹幕助手 by JerryYan".format(self.roomMember, self.roomPopularity)
                else:
                    return "观看:待刷新 人气:{} --弹幕助手 by JerryYan".format(self.roomPopularity)


    def onMessage(self, msg: str):
        set_cmd_text_color(FOREGROUND_DARKGRAY)
        print("消息 : ", msg)
        resetColor()

    def onJoin(self, user: User):
        set_cmd_text_color(BACKGROUND_WHITE | FOREGROUND_BLACK)
        print("感谢", user, "加入了粉丝团")
        resetColor()

    def onSubscribe(self, user: User):
        return

    def onEnter(self, msg:MemberMsg):
        if msg.type != 0:
            set_cmd_text_color(FOREGROUND_DARKGRAY)
            print("提示 : ", msg)
            resetColor()

    def onChat(self, chat: Chat):
        print(chat)

    def onPresent(self, gift: Gift):
        return

    def onPresentEnd(self, gift: Gift):
        set_cmd_text_color(BACKGROUND_WHITE | FOREGROUND_BLACK)
        print("感谢", gift)
        resetColor()

    def onLike(self, user: User):
        return

    def onLeave(self, json: any):
        return


def warning(*args):
    print(*args)


if __name__ == "__main__":
    room = 97621754276  # 永恒
    # room = 75366565294
    # room = 83940182312 #Dae
    resetColor()
    print("西瓜直播弹幕助手 by JerryYan")
    if len(sys.argv) > 1:
        room = int(sys.argv[1])
    else:
        try:
            room = int(readInput("请输入房间号，默认为永恒的直播间", room, 3))
        except ValueError:
            pass
    api = WinMain(room)
    print("进入", api.roomLiver, "的直播间")
    if not api.isValidRoom:
        input("房间不存在")
        sys.exit()
    os.system("title {}".format(api.getTitle()))
    print("=" * 30)
    while True:
        if api.isLive:
            try:
                os.system("title {}".format(api.getTitle()))
                api.getDanmaku()
            except Exception as e:
                warning(e)
            time.sleep(1)
        else:
            print("主播未开播，等待1分钟后重试")
            time.sleep(60)
            api.updRoomInfo()
