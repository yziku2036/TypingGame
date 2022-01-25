# -*- coding: utf-8 -*-

import pygame
# import classes
import sys
import enum
from typinglib_old import *
#from typinglib import *


class Game_States_Init():
    def __init__(self):
        self.solved=True
        self.score=0
        self.combo=0
        self.dist_moved=0
        self.bg_pos = [0, 0]
        self.staging_const =19
        self.score_mul=0
        self.deplete_start_timer=0
        self.typed=0
        self.limit_time=0

    def init(self):
        super().__init__()

class Text_Colored_Init():
    def __init__(self,screen):
        self.text_title=Text(screen,(255,255,0),50)
        self.text_vector = Text(screen, (255, 200, 150), 30)
        self.text_orange = Text(screen,(255,128,0),30)
        self.text_pink = Text(screen,(255,128,128),30)
        self.text_light_green = Text(screen,(0,255,128),30)
        self.text_light_blue= Text(screen,(200,200,255),30)
        self.text_white=Text(screen,(255,255,255),25)

class Process_State(enum.Enum):
    TITLE = enum.auto()
    LAUNCHING_1 = enum.auto()
    LAUNCHING_2 = enum.auto()
    FLYING = enum.auto()
    FALLING = enum.auto()


FPS = 30
WINDOW_SIZE = WIDTH, HEIGHT = 600, 400#ウインドウサイズ
BACKGROUND_COLOR = (0, 0, 0)  # 背景色(黒)
def main():
    global_k = '0'
    game_state_now=Game_States_Init()
    pygame.init()
    state_now = Process_State.TITLE
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("RockeTyping")
    bg = pygame.image.load("images/background.png")
    texts=Text_Colored_Init(screen)

    word_data = DataReader("words", screen)

    rocket = Rocket(1, 1, (100, 300), 0)
    #ゲージの定義は色、(左上のx座標、y座標、xサイズ、yサイズ)、ゲージの分解能
    gauge_power = Gauge_Launch_Power(screen, (255, 255, 0), (550, 50, 40, 300), 300)
   # gauge_timer = GaugeHorizontal(screen, (255, 0, 128), (20, 40, 300, 30), 200)
    gauge_timer= GaugeTimer(screen,(255,0,128),(20,40,300,30))
    gauge_vector = Gauge_Horizontal(screen, (0, 128, 128), (20, 110, 300, 30))

    timer = 0

    allvar = []
    allvar.append(rocket)
    allvar.append(gauge_power)

    my_group = pygame.sprite.Group(rocket)

    screen.fill(BACKGROUND_COLOR)  # 背景色を設定
    screen.blit(bg, game_state_now.bg_pos)
    clock = pygame.time.Clock()  # クロックを開始

    while True:
        screen.fill(BACKGROUND_COLOR)
        screen.blit(bg, [game_state_now.bg_pos[0] - WIDTH, game_state_now.bg_pos[1]])
        screen.blit(bg, [game_state_now.bg_pos[0], game_state_now.bg_pos[1] - HEIGHT])
        screen.blit(bg, [game_state_now.bg_pos[0] - WIDTH, game_state_now.bg_pos[1] - HEIGHT])
        screen.blit(bg, game_state_now.bg_pos)

        val = gauge_power.ret_power()

        if state_now == Process_State.TITLE:
            texts.text_title.display("ROCKETYPING",(WIDTH/2-100,HEIGHT/2-100))
            texts.text_title.display("Enter To Start",(WIDTH/2-100,HEIGHT/2+100))
        if state_now == Process_State.LAUNCHING_1:
            texts.text_light_green.display("Press space to ",(WIDTH/2-220,HEIGHT/2-100))
            texts.text_light_green.display("lock the direction",(WIDTH/2-220,HEIGHT/2-50))
        if state_now == Process_State.LAUNCHING_2:
            texts.text_light_green.display("Press space to",(WIDTH/2-220,HEIGHT/2-100))
            texts.text_light_green.display("set the power",(WIDTH/2-220,HEIGHT/2-50))
            gauge_power.update()
            gauge_power.display()
            rocket.calc_launch_angle(val)

        elif state_now == Process_State.FLYING:
            if deplete_start_timer>0:
                print(deplete_start_timer)
                deplete_start_timer-=1
            else:
                rocket.deplete_velocity()
            gauge_power.display_fading()
            gauge_timer.update()
            gauge_timer.display()
            gauge_vector.display()
            gauge_vector.set_power(rocket.movx)
            if game_state_now.solved:#1文打ち終わったら
                word_data.translation()
                question = SeparatedText(word_data.return_question(), screen)
                print("question created")
                rocket.accelerate(question.get_strlen()*5)
                game_state_now.solved = False

            word_data.display_question()  # 引数は問題の場所
            question.load_input(global_k)
            if question.wait_input() == 1:#あってたら
                game_state_now.combo+=1
                game_state_now.typed+=1
                game_state_now.score_mul=game_state_now.combo/10
                if game_state_now.score_mul >= 4:
                    game_state_now.score_mul=4
                if rocket.movx>80:
                    game_state_now.score_mul *= rocket.movx/80

                game_state_now.score+=question.get_strlen()*(1+game_state_now.score_mul)*game_state_now.staging_const
            #間違ってたらコンボを0に
            elif question.wait_input()== 2:
                game_state_now.combo/=2.5
                game_state_now.combo=math.floor(game_state_now.combo)
                #1文の入力が終わったら
            elif question.wait_input()==0:
                game_state_now.solved = True# k
            global_k = None
            score=math.floor(game_state_now.score)
            texts.text_orange.display("Score:"+str(game_state_now.score),(WIDTH/2+30,100))
            texts.text_pink.display("Combo:"+str(game_state_now.combo),(WIDTH/2+30,125))
            texts.text_light_blue.display("Multiplier:"+str(round(game_state_now.score_mul,3)),(WIDTH/2+30,150))

            question.display_process()

            texts.text_vector.display("Flight Time:" + str(math.floor(timer)), (15, 0))
            texts.text_vector.display("Velocity:" + str(math.floor(rocket.movx)), (15, 70))
            game_state_now.dist_moved += rocket.movx
            timer -= 1 / FPS

            rocket.move_center(game_state_now.bg_pos)
            if game_state_now.bg_pos[0] > WIDTH:
                game_state_now.bg_pos[0] = 0
            if game_state_now.bg_pos[1] < 0:
                game_state_now.bg_pos[1] = HEIGHT
            if timer < 0:
                state_now = Process_State.FALLING

        elif state_now == Process_State.FALLING:
            game_state_now.dist_moved=math.floor(game_state_now.dist_moved)
            texts.text_vector.display("GAME FINISHED!",(WIDTH/2-100,HEIGHT/2-120))
            texts.text_vector.display("Score:" + str(game_state_now.score), (WIDTH/2-100,HEIGHT/2+50))
            texts.text_light_blue.display("You traveled:"+str(game_state_now.dist_moved)+"KM",(WIDTH/2-140,HEIGHT/2+75))
            texts.text_white.display("Press [Enter] to restart",(WIDTH/2-140,HEIGHT/2+110))
            texts.text_white.display("Press [ESC] to quit",(WIDTH/2-140,HEIGHT/2+140))
            texts.text_white.display("Your Typing Speed:"+str(round(game_state_now.typed/game_state_now.limit_time,3))+"/s",(WIDTH/2-140,HEIGHT/2+165))
            print(game_state_now.typed)

        for event in pygame.event.get():
            # ESCキーが押されたら終了
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                k = key_pressed(event)
                global_k = k
                if k is pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    #K_RETURNはENTER
                elif k is pygame.K_RETURN:
                    if state_now == Process_State.TITLE:
                        rocket.locked=False
                        gauge_timer.reset()
                        state_now=Process_State.LAUNCHING_1

                    #ゲームリセット時
                    elif state_now == Process_State.FALLING:
                        state_now = Process_State.TITLE
                        rocket.reset()
                        game_state_now.init()
                elif k is pygame.K_SPACE:
                    #ロケットの向きを固定する瞬間
                    if state_now == Process_State.LAUNCHING_1:
                        rocket = Rocket(1, 1, (100, 300), rocket.image_angle)
                        #rocket = Rocket(1, 1, (100, 300), 150)
                        rocket.locked = True
                        my_group = pygame.sprite.Group(rocket)
                        gauge_power.display()
                        state_now = Process_State.LAUNCHING_2
                    elif state_now == Process_State.LAUNCHING_2:
                        #ロケットのパワーを確定した瞬間
                        state_now = Process_State.FLYING
                        game_state_now.limit_time=calc_limit_time(rocket.movy)
                        timer = calc_limit_time(rocket.movy)
                        # gauge_vector.set_gauge_max(rocket.movx*2)
                        gauge_timer.set_limit_time(timer)
                        deplete_start_timer=rocket.movx*FPS/16
                        #gauge_timer.set_gauge_max(timer)
                    # elif state_now == state.FLYING:
                if k is pygame.K_LEFT:
                    rocket.image_angle = 0
                    rocket.calc_launch_angle(val)

                    # 背景色で塗りつぶし

        # 画像を更新して描写
        my_group.update()
        my_group.draw(screen)

        # 表示全体を更新
        pygame.display.update()
        clock.tick(FPS)  # フレームレート分待機


def key_pressed(e):
    return e.key


if __name__ == '__main__':
    main()
