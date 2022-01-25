import pygame
import sys
# import main
import math
import random

WINDOW_SIZE = WIDTH, HEIGHT = 600, 400  # ウインドウサイズ
BACKGROUND_COLOR = (0, 0, 0)  # 背景色(黒)
FPS = 30  # フレームレート


def draw_rect_alpha(surface, color, rect, frame=0):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), frame)
    surface.blit(shape_surf, rect)

def calc_limit_time(time):
    time/=5
    time*=2
    if time>120:
        time=120
    elif time>90:
        tmp=(time-90)/3
        time=90+tmp
    elif time>60:
        tmp=(time-60)/2
        time=60+tmp
    elif time<20:
        time=20
    return time

class GameObj:
    def __init__(self):
        self.state = state.TITLE

    def state(self, state):
        self.state = state

    # def update(self):


class Text:
    def __init__(self, screen, color, size):
        self.screen = screen
        self.color = color
        self.font = pygame.font.Font("fonts/" + "Senobi-Gothic-Regular.ttf", size)
        # self.font=pygame.font.Font(None,size)

    def display(self, text, pos):
        text = self.font.render(text, True, self.color)
        self.screen.blit(text, pos)

    # def display_r(self,text,pos):
    #   text=self.font.render(text,True,self.color,align="right")
    # self.screen.blit(text,pos)


class Gauge(GameObj):
    def __init__(self, screen, color, pos):
        self.color = color
        self.pos = pos
        self.frame_pos = pos
        self.pos_old=pos
        self.screen = screen
        self.gauge = 0.0
        self.movx = 0
        self.movy = 0
        self.alpha = 255

        # self.barpos=self.pos[1]+self.pos[3]

    def display(self):
        pygame.draw.rect(self.screen, self.color, self.pos)
        pygame.draw.rect(self.screen, (0, 255, 255), self.frame_pos, 5)

    def display_fading(self):
        draw_rect_alpha(self.screen, (self.color[0], self.color[1], self.color[2], self.alpha), self.pos)
        draw_rect_alpha(self.screen, (0, 255, 255, self.alpha), self.frame_pos, 5)
        if self.alpha >= 10:
            self.alpha -= 10

    def ret_power(self):
        return self.gauge

    def reset(self):
        self.pos=self.pos_old
        self.frame_pos=self.pos_old

class Gauge_Launch_Power(Gauge):
    def __init__(self,screen, color, pos,gauge_max):
        super().__init__(screen,color,pos)
        self.gauge_max=gauge_max
    def update(self):
        self.gauge += 10
        barpos = self.pos[1] + self.pos[3]
        self.pos = (self.pos[0], barpos - self.gauge, self.pos[2], self.gauge)
        if self.gauge >= self.gauge_max:
            self.gauge = 0


class Gauge_Horizontal(Gauge):

    def __init__(self,screen, color, pos):
        super().__init__(screen,color,pos)
        self.time=0

    def set_max_time(self,time):
        self.time=time#時間をとって

    def update(self):

        if not self.time*FPS == 0:
            deplete_value = self.gauge_max/(self.time*FPS)
        else:
            deplete_value=0

        self.pos = (self.pos[0], self.pos[1],self.pos[2]-deplete_value, self.pos[3])
        #if self.gauge >= self.gauge_max:
        #    self.gauge = 0

        # スプライトアニメーションさせるクラス
    def set_power(self,val):
        self.pos = (self.pos[0], self.pos[1],val, self.pos[3])

class GaugeTimer(Gauge):

    def __init__(self,screen, color, pos):
        super().__init__(screen,color,pos)


    def set_limit_time(self,limit):
        self.limit=limit

        #deplete_ratioが1になったらゲージが空になる
        #deplete_ratioは0~1
        self.deplete_ratio=1/(self.limit*FPS)
        self.gauge_length=self.pos[2]-self.pos[0]
    def update(self):
        self.pos = (self.pos[0], self.pos[1],self.pos[2]-self.deplete_ratio*self.gauge_length, self.pos[3])
        #if self.gauge >= self.gauge_max:
        #    self.gauge = 0

        # スプライトアニメーションさせるクラス
    def set_power(self,val):
        self.pos = (self.pos[0], self.pos[1],val*self.limit, self.pos[3])



class Rocket(pygame.sprite.Sprite, GameObj):
    # コンストラクタ
    def __init__(self, width_rate, height_rate, pos, angle):
        super(Rocket, self).__init__()

        # 画像をリストで読み込み
        self.images = list()
        for num in range(0, 5):
            self.images.append(pygame.image.load("images/rocket_" + str(num) + ".png"))

        self.index = 0
        self.image = self.images[self.index]
        # 画像の描写範囲　中心を割り出して回転させるのに用いる
        self.rect = self.image.get_rect()

        self.width_rate = width_rate
        self.height_rate = height_rate
        self.pos = pos

        self.image_angle = 0
        self.clockwise = False
        self.locked = True
        self.image_angle =angle
        self.movx:float=0.0

    def reset(self):
        self.index=0
        self.rect = self.image.get_rect()

        self.pos = (100,300)

        self.image_angle = 0
        self.clockwise = False
        self.locked = True
        self.image_angle = 300
        self.movx:float=0.0

    # 1フレーム事に実行される関数
    def update(self):
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]
        self.index += 1
        self.change_image_scale()  # 画像サイズを変更
        self.rotate_center_image()  # 画像を回転

    def deplete_velocity(self):
        deplete_value:float=0
        if self.movx>200:
            deplete_value=self.movx/150
        elif self.movx>150:
            deplete_value=self.movx/240
        elif self.movx>100:
            deplete_value=self.movx/300
        else:
            deplete_value =0.15

        self.movx-=deplete_value

        if self.movx <0:
            self.movx=0

    def accelerate(self,val):
        self.movx+=val


    # 画像のサイズを変更する関数
    def change_image_scale(self):
        x_size = self.image.get_width() * self.width_rate
        y_size = self.image.get_height() * self.height_rate
        self.image = pygame.transform.scale(self.image, (int(x_size), int(y_size)))

    # 画像の中心で回転させる関数
    def rotate_center_image(self):
        # 画像の傾きを設定
        if not self.locked:
            if self.clockwise:
                self.image_angle -= 10  # 真横で-90°　真上で0°
            else:
                self.image_angle += 10

            if self.image_angle >= 0:
                self.clockwise = True
                self.image_angle = 0
            elif self.image_angle <= -90:
                self.clockwise = False
                self.image_angle = -90
        # 画像を回転
        rot_image = pygame.transform.rotate(self.image, self.image_angle)
        rot_rect = rot_image.get_rect()
        rot_rect.center = self.pos  # 中心位置を設定(移動)

        # 結果を格納
        self.image = rot_image
        self.rect = rot_rect

    def calc_launch_angle(self, power=1):
        angle = self.image_angle + 90
        angle = angle * (math.pi / 180)
        sin = math.sin(angle)
        cos = math.cos(angle)
        self.movx = cos * power
        self.movy = sin * power
        #self.dispx= self.movx
    def move_center(self, bg_pos):
        # 画面中央のとき
        moved_x = self.pos[0]
        moved_y = self.pos[1]
        if self.pos[0] < WIDTH / 2:
            if self.movx != 0:
                moved_x += self.movx / 15
        else:
            bg_pos[0] += self.movx / 15

        if self.pos[1] > HEIGHT / 2:
            if self.movy != 0:
                moved_y -= self.movy / 15
        else:
            bg_pos[1] -= self.movy / 15
        self.pos = (moved_x, moved_y)


class DataReader():
    def __init__(self, name, screen):
        self.name = name
        self.screen = screen
        self.index = 0
        self.target = "this sentence must not be displayed"

        file_name = "words/" + self.name + ".txt"
        f = open(file_name, 'r', encoding='shift-jis')
        data_raw = f.read().split('\n')
        data_split = []
        f.close()
        self.length = len(data_raw)
        for i in data_raw:
            data_split.append(i.split(" "))

        self.data = data_split
        """
        The question text is consisted following form:
            Japanese English(Strings I want players to type)
        And self.data is:
            [0]:Japanese English
            [1]:Japanese English
            [2]:~
        Then self.data is MultiDimentional List
        """

    def return_question(self):

        return self.target

    def translation(self):
        alphabet = ""
        skip = False
        self.index = random.randint(0, self.length - 1)

        # self.index=0

        tmp = self.data[self.index]
        target = tmp[1]  # English
        loop = 0
        print(target)
        lower = "ゃゅょっ"
        print(target)
        lim = len(target)
        for i in range(lim):
            if skip:
                skip = False
                continue

            char = target[i]
            print(str(i) + "回目")
            # 文字列の範囲をはみ出ないようにする
            if lim - 1 > i and target[i + 1] in lower:  # 小文字があった場合
                tmp = target[i] + target[i + 1]
                if tmp == "きゃ":
                    alphabet += "kya"
                if tmp == "きゅ":
                    alphabet += "kyu"
                if tmp == "きょ":
                    alphabet += "kyo"
                if tmp == "しゃ":
                    alphabet += "sya"
                if tmp == "しゅ":
                    alphabet += "syu"
                if tmp == "しょ":
                    alphabet += "syo"
                if tmp == "ちゃ":
                    alphabet += "tya"
                if tmp == "ちゅ":
                    alphabet += "tyu"
                if tmp == "ちょ":
                    alphabet += "tyo"
                if tmp == "にゃ":
                    alphabet += "nya"
                if tmp == "にゅ":
                    alphabet += "nyu"
                if tmp == "にょ":
                    alphabet += "nyo"
                if tmp == "ひゃ":
                    alphabet += "hya"
                if tmp == "ひゅ":
                    alphabet += "hyu"
                if tmp == "ひょ":
                    alphabet += "hyo"
                if tmp == "みゃ":
                    alphabet += "mya"
                if tmp == "みゅ":
                    alphabet += "myu"
                if tmp == "みょ":
                    alphabet += "myo"
                if tmp == "りゃ":
                    alphabet += "rya"
                if tmp == "りゅ":
                    alphabet += "ryu"
                if tmp == "りょ":
                    alphabet += "ryo"
                skip = True
            else:

                if char == 'あ':
                    alphabet += "a"
                elif char == 'い':
                    alphabet += "i"
                elif char == 'う':
                    alphabet += "u"
                elif char == 'え':
                    alphabet += "e"
                elif char == 'お':
                    alphabet += "o"
                elif char == 'か':
                    alphabet += "ka"
                elif char == 'き':
                    alphabet += "ki"
                elif char == 'く':
                    alphabet += "ku"
                elif char == 'け':
                    alphabet += "ke"
                elif char == 'こ':
                    alphabet += "ko"
                elif char == 'さ':
                    alphabet += "sa"
                elif char == 'し':
                    alphabet += "si"
                elif char == 'す':
                    alphabet += "su"
                elif char == 'せ':
                    alphabet += "se"
                elif char == 'そ':
                    alphabet += "so"
                elif char == 'た':
                    alphabet += "ta"
                elif char == 'ち':
                    alphabet += "ti"
                elif char == 'つ':
                    alphabet += "tu"
                elif char == 'て':
                    alphabet += "te"
                elif char == 'と':
                    alphabet += "to"
                elif char == 'な':
                    alphabet += "na"
                elif char == 'に':
                    alphabet += "ni"
                elif char == 'ぬ':
                    alphabet += "nu"
                elif char == 'ね':
                    alphabet += "ne"
                elif char == 'の':
                    alphabet += "no"
                elif char == 'は':
                    alphabet += "ha"
                elif char == 'ひ':
                    alphabet += "hi"
                elif char == 'ふ':
                    alphabet += "hu"
                elif char == 'へ':
                    alphabet += "he"
                elif char == 'ほ':
                    alphabet += "ho"

                elif char == 'ま':
                    alphabet += "ma"
                elif char == 'み':
                    alphabet += "mi"
                elif char == 'む':
                    alphabet += "mu"
                elif char == 'め':
                    alphabet += "me"
                elif char == 'も':
                    alphabet += "mo"

                elif char == 'や':
                    alphabet += "ya"
                elif char == 'ゆ':
                    alphabet += "yu"
                elif char == 'よ':
                    alphabet += "yo"

                elif char == 'わ':
                    alphabet += "wa"
                elif char == 'を':
                    alphabet += "wo"
                elif char == 'ん':
                    alphabet += "nn"

                elif char == 'ら':
                    alphabet += "ra"
                elif char == 'り':
                    alphabet += "ri"
                elif char == 'る':
                    alphabet += "ru"
                elif char == 'れ':
                    alphabet += "re"
                elif char == 'ろ':
                    alphabet += "ro"

                elif char =='が':
                    alphabet +="ga"
                elif char =='ぎ':
                    alphabet +="gi"
                elif char =='ぐ':
                    alphabet +="gu"
                elif char =='げ':
                    alphabet +="ge"
                elif char =='ご':
                    alphabet +="go"


                elif char == 'ざ':
                    alphabet += "za"
                elif char == 'じ':
                    alphabet +="zi"
                elif char == 'ず':
                    alphabet += "zu"
                elif char == 'ぜ':
                    alphabet += "ze"
                elif char == 'ぞ':
                    alphabet += "zo"


                elif char == 'だ':
                    alphabet += "da"
                elif char == 'ぢ':
                    alphabet += "di"
                elif char == 'づ':
                    alphabet += "du"
                elif char == "で":
                    alphabet += "de"
                elif char == 'ど':
                    alphabet += "do"

                elif char == 'ば':
                    alphabet += "ba"
                elif char == 'び':
                    alphabet += "bi"
                elif char == 'ぶ':
                    alphabet += "bu"
                elif char == "べ":
                    alphabet += "be"
                elif char == 'ぼ':
                    alphabet += "bo"

                elif char == 'ぱ':
                    alphabet += "pa"
                elif char == 'ぴ':
                    alphabet += "pi"
                elif char == 'ぷ':
                    alphabet += "pu"
                elif char == 'ぺ':
                    alphabet += "pe"
                elif char == 'ぽ':
                    alphabet += "po"

                elif char == 'ー':
                    alphabet +="-"

                else:
                    alphabet += "what"
            loop += 1
        print(alphabet)
        self.target = alphabet

    def display_question(self):
        # index=random.randint(0,self.length-1)
        row = self.data[self.index]
        text = Text(self.screen, (255, 0, 0), 30)
        # text_en=Text(self.screen,(255,0,0),30)

        # row[0]:Japansese
        # 日本語出力
        # text.display_r(row[0],(WIDTH/2,HEIGHT/2))
        text.display(row[0], (WIDTH / 2+100, HEIGHT / 2+50))
        # text_en.display(row[1],(WIDTH/2,HEIGHT/2+50))


# def update(self):


class SeparatedText():
    def __init__(self, string, screen):
        self.screen = screen
        self.graytext = Text(self.screen, (100, 100, 100), 30)
        self.whitetext = Text(self.screen, (255, 255, 255), 30)
        self.index = 0
        self.string = string

    def display_process(self):
        strlen = len(self.string) - 1
        for i in range(len(self.string)):
            if strlen - i < self.index:
                self.whitetext.display(self.string[strlen - i], (WIDTH / 2 + 250 - i * 15, HEIGHT / 2 + 80))
            else:
                self.graytext.display(self.string[strlen - i], (WIDTH / 2 + 250 - i * 15, HEIGHT / 2 + 80))
    def get_strlen(self):
        return len(self.string)

    def load_input(self, inputchar):
        if not inputchar == None:
            inputchar = pygame.key.name(inputchar)
        else:
            inputchar = None

        self.inputchar = inputchar

    def wait_input(self):
        if len(self.string) == self.index:
            return 0     #あってたら1　間違ってたら2 一文を打ち終わったら0
        target = self.string[self.index]
        if target == self.inputchar:
            self.index += 1
            #print("あってる")
            return 1
        elif self.inputchar is not None:
            #print("まちがってる")
            return 2
    def display_progress(self):
        text = Text(self.screen, (0, 255, 0), 30)
        text.display(self.string, (WIDTH / 2, HEIGHT / 2 + 100))

