import pygame
import math
import random
from main import Game_System
from abc import ABCMeta, abstractmethod


WINDOW_SIZE = Game_System.WIDTH, HEIGHT = 600, 400  # ウインドウサイズ
BACKGROUND_COLOR = (0, 0, 0)  # 背景色(黒)
Game_System.FPS = 30  # フレームレート


def draw_rect_alpha(surface, color, rect, frame=0):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), frame)
    surface.blit(shape_surf, rect)


def calc_limit_time(time):
    # 制限時間を計算
    time /= 5
    time *= 2
    if time > 120:
        time = 120
    elif time > 90:
        tmp = (time - 90) / 3
        time = 90 + tmp
    elif time > 60:
        tmp = (time - 60) / 2
        time = 60 + tmp
    elif time < 20:
        time = 20
    return time


class Text:
    def __init__(self, screen, color, size):
        self.screen = screen
        self.color = color
        self.font = pygame.font.Font("fonts/" + "Senobi-Gothic-Regular.ttf", size)

    def display(self, text, pos):
        text = self.font.render(text, True, self.color)
        self.screen.blit(text, pos)


@abstractmethod
class Gauge(metaclass=ABCMeta):
    def __init__(self, screen, color, pos, max_value=100):
        self.color = color
        #       posは(左上のx、左上のy、横の長さ、縦の長さ)のタプル
        self.pos = pos
        self.frame_pos = pos
        self.pos_old = pos
        self.screen = screen
        self.gauge_value = 0.0
        self.gauge_percentage = 0.0
        self.alpha = 255
        self.gauge_length = pos[3]
        self.max_value = max_value

    def display(self):
        pygame.draw.rect(self.screen, self.color, self.pos)
        pygame.draw.rect(self.screen, (0, 255, 255), self.frame_pos, 5)

    def display_fading(self):
        draw_rect_alpha(self.screen, (self.color[0], self.color[1], self.color[2], self.alpha), self.pos)
        draw_rect_alpha(self.screen, (0, 255, 255, self.alpha), self.frame_pos, 5)
        if self.alpha >= 10:
            self.alpha -= 10
        elif self.alpha > 0:
            self.alpha = 0

    def ret_power(self):
        return (self.gauge_percentage * self.max_value) / 100

    def reset(self):
        self.pos = self.pos_old
        self.frame_pos = self.pos_old

    def set_max_value(self, max_value):
        self.max_value = max_value

    def change_gauge(self):
        pass


class Gauge_Vertical(Gauge):
    def __init__(self, screen, color, pos, max_value):
        super().__init__(screen, color, pos, max_value)

    def update(self):
        # pos[1]は左上の点 pos[3]は縦の長さ
        # bottom_posはゲージの一番下の座標
        bottom_pos = self.frame_pos[1] + self.frame_pos[3]
        vary_value = (self.frame_pos[3] * self.gauge_percentage) / 100
        self.pos = (self.pos[0], bottom_pos - vary_value, self.pos[2], vary_value)


class Gauge_Horizontal(Gauge):
    def __init__(self, screen, color, pos, max_value):
        super().__init__(screen, color, pos, max_value)

    def update(self):
        # pos[0]は左上の点のx座標 pos[2]はゲージの横の長さ
        vary_value = (self.frame_pos[2] * self.gauge_percentage) / 100
        self.pos = (self.pos[0], self.pos[1], vary_value, self.pos[3])

    def set_power(self, val):
        self.gauge_percentage = val


class Gauge_Launch_Power(Gauge_Vertical):
    def __init__(self, screen, color, pos, max_value):
        super().__init__(screen, color, pos, max_value)

    def update(self):
        self.change_gauge()
        if self.gauge_percentage >= 100:
            self.gauge_percentage = 0
        super().update()

    def change_gauge(self):
        self.gauge_percentage += 3


class Gauge_Timer(Gauge_Horizontal):
    def __init__(self, screen, color, pos, max_value):
        super().__init__(screen, color, pos, max_value)
        self.gauge_percentage = 100

    def change_gauge(self):
        self.gauge_percentage -= (1 / Game_System.FPS) * (100 / self.max_value)

    def update(self):
        self.change_gauge()
        super().update()

    def reset(self):
        self.gauge_percentage = 100


class Rocket(pygame.sprite.Sprite):
    # コンストラクタ
    def __init__(self, width_rate, height_rate, pos, angle):
        super(Rocket, self).__init__()
        # 画像をリストで読み込み
        self.images = list()
        for num in range(0, 5):
            self.images.append(pygame.image.load("images/rocket_" + str(num) + ".png"))

        # 現在このクラスが指す画像を一応初期化
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.pos = pos
        self.image_angle = 0
        self.clockwise = False
        self.locked = True
        self.image_angle = angle
        self.speed_x: float = 0.0
        self.speed_y: float = 0.0
        # インスタンス変数から縮尺を変更
        #for num in range(0, 5):
         #   print(num)
            #self.images[num] = self.change_image_scale(self.images[num],width_rate,height_rate)

    def reset(self):
        self.index = 0
        self.rect = self.image.get_rect()
        self.pos = (100, 300)
        self.image_angle = 0
        self.clockwise = False
        self.locked = True
        self.speed_x: float = 0.0

    # 1フレーム事に実行される関数
    def update(self):
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]
        self.index += 1
        self.display()
        if not self.locked:
            self.rotate_image()

    def display(self):
        rot_image = pygame.transform.rotate(self.image, self.image_angle)
        rot_rect = rot_image.get_rect()
        rot_rect.center = self.pos  # 中心位置を設定(移動)
        # 結果を格納
        self.image = rot_image
        self.rect = rot_rect

    def deplete_velocity(self):
        if self.speed_x > 100:
            deplete_value = self.speed_x / 150
        elif self.speed_x > 75:
            deplete_value = self.speed_x / 200
        elif self.speed_x > 50:
            deplete_value = self.speed_x / 250
        elif self.speed_x > 25:
            deplete_value = self.speed_x / 300
        else:
            deplete_value = 0.08

        self.speed_x -= deplete_value

        if self.speed_x < 0:
            self.speed_x = 0

    def accelerate(self, val):
        self.speed_x += val

        # 画像のサイズを変更する関数
    def change_image_scale(self, image,width_rate,height_rate):
        x_size = image.get_width() * width_rate
        y_size = image.get_height() * height_rate
        changed_image = pygame.transform.scale(self.image, (int(x_size), int(y_size)))
        return changed_image

    def rotate_mode_change(self):
        now_mode = self.locked
        print(now_mode)
        self.locked = not now_mode
        print(self.locked)

    # 画像の中心で回転させる関数
    def rotate_image(self):
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

    def calc_launch_angle(self, power=1):
        # mainではpowerは最大100
        angle = self.image_angle + 90
        angle = angle * (math.pi / 180)
        sin = math.sin(angle)
        cos = math.cos(angle)
        self.speed_x = cos * power
        self.speed_y = sin * power

    #背景を動かすのに用いる
    def move_background(self, bg_pos):
        # 画面中央のとき
        moved_x = self.pos[0]
        moved_y = self.pos[1]
        if self.pos[0] < Game_System.WIDTH / 2:
            if self.speed_x != 0:
                moved_x += self.speed_x / 15
        else:
            bg_pos[0] += self.speed_x / 15

        if self.pos[1] > HEIGHT / 2:
            if self.speed_y != 0:
                moved_y -= self.speed_y / 15
        else:
            bg_pos[1] -= self.speed_y / 15
        self.pos = (moved_x, moved_y)

        if bg_pos[0] > Game_System.WIDTH:
            bg_pos[0] = 0
        if bg_pos[1] < 0:
            bg_pos[1] = HEIGHT

class DataReader:
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
        lower = "ゃゅょっ"
        lim = len(target)
        for i in range(lim):
            if skip:
                skip = False
                continue
            char = target[i]
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

                elif char == 'が':
                    alphabet += "ga"
                elif char == 'ぎ':
                    alphabet += "gi"
                elif char == 'ぐ':
                    alphabet += "gu"
                elif char == 'げ':
                    alphabet += "ge"
                elif char == 'ご':
                    alphabet += "go"


                elif char == 'ざ':
                    alphabet += "za"
                elif char == 'じ':
                    alphabet += "zi"
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
                    alphabet += "-"

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
        # text.display_r(row[0],(Game_System.WIDTH/2,HEIGHT/2))
        text.display(row[0], (Game_System.WIDTH / 2 + 100, HEIGHT / 2 + 50))
        # text_en.display(row[1],(Game_System.WIDTH/2,HEIGHT/2+50))


class SeparatedText:
    def __init__(self, string, screen):
        self.screen = screen
        self.graytext = Text(self.screen, (100, 100, 100), 30)
        self.whitetext = Text(self.screen, (255, 255, 255), 30)
        self.index = 0
        self.string = string
        self.inputchar = None

    def display_process(self):
        strlen = len(self.string) - 1
        for i in range(len(self.string)):
            if strlen - i < self.index:
                self.whitetext.display(self.string[strlen - i], (Game_System.WIDTH / 2 + 250 - i * 15, HEIGHT / 2 + 80))
            else:
                self.graytext.display(self.string[strlen - i], (Game_System.WIDTH / 2 + 250 - i * 15, HEIGHT / 2 + 80))

    def get_strlen(self):
        return len(self.string)

    def load_input(self, inputchar):
        if inputchar is not None:
            inputchar = pygame.key.name(inputchar)
        else:
            inputchar = None

        self.inputchar = inputchar

    def wait_input(self):
        if len(self.string) == self.index:
            return 0  # あってたら1　間違ってたら2 一文を打ち終わったら0
        target = self.string[self.index]
        if target == self.inputchar:
            self.index += 1
            # print("あってる")
            return 1
        elif self.inputchar is not None:
            # print("まちがってる")
            return 2

    def display_progress(self):
        text = Text(self.screen, (0, 255, 0), 30)
        text.display(self.string, (Game_System.WIDTH / 2, HEIGHT / 2 + 100))
