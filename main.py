import pygame
# import classes
import sys
import enum
from typinglib_old import *
#from typinglib import *


class Game_States():
    def __init__(self):
        self.solved=True
        self.score=0
        self.combo=0
        dist_moved:int=0
        bg_pos = [0, 0]
        staging_const =19
        score_mul=0
        deplete_start_timer=0
        typed=0

    def init(self):
        super().__init__()


class Process_State(enum.Enum):
    TITLE = enum.auto()
    LAUNCHING_1 = enum.auto()
    LAUNCHING_2 = enum.auto()
    FLYING = enum.auto()
    FALLING = enum.auto()


FPS = 30
WINDOW_SIZE = WIDTH, HEIGHT = 600, 400  # ウインドウサイズ
BACKGROUND_COLOR = (0, 0, 0)  # 背景色(黒)


def text_init():
    return


def main():
    global_k = '0'
    game_state_now=Game_States()
    pygame.init()
    state_now = Process_State.TITLE
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("RockeTyping")
    bg = pygame.image.load("images/background.png")

    word_data = DataReader("words", screen)

    rocket = Rocket(1, 1, (100, 300), 0)
    #ゲージの定義は色、(左上のx座標、y座標、xサイズ、yサイズ)、ゲージの分解能
    gauge_power = GaugeVertical(screen, (255, 255, 0), (550, 50, 40, 300),300)
   # gauge_timer = GaugeHorizontal(screen, (255, 0, 128), (20, 40, 300, 30), 200)
    gauge_timer= GaugeTimer(screen,(255,0,128),(20,40,300,30))
    gauge_vector = GaugeHorizontal(screen, (0, 128, 128), (20, 110, 300, 30), 200)
    text_title=Text(screen,(255,255,0),50)
    text_vector = Text(screen, (255, 200, 150), 30)
    text_orange = Text(screen,(255,128,0),30)
    text_pink = Text(screen,(255,128,128),30)
    text_light_green = Text(screen,(0,255,128),30)
    text_light_blue= Text(screen,(200,200,255),30)
    text_white=Text(screen,(255,255,255),25)
    timer = 0
    time_limit=0

    allvar = []
    allvar.append(rocket)
    allvar.append(gauge_power)

    my_group = pygame.sprite.Group(rocket)

    screen.fill(BACKGROUND_COLOR)  # 背景色を設定
    screen.blit(bg, game_state_now.bg_pos)
    clock = pygame.time.Clock()  # クロックを開始
    bg_stat = 0

    gauge_length = 0
    #state_now = state.LAUNCHING_1
    
    while True:
        screen.fill(BACKGROUND_COLOR)
        screen.blit(bg, [game_state_now.bg_pos[0] - WIDTH, game_state_now.bg_pos[1]])
        screen.blit(bg, [game_state_now.bg_pos[0], game_state_now.bg_pos[1] - HEIGHT])
        screen.blit(bg, [game_state_now.bg_pos[0] - WIDTH, game_state_now.bg_pos[1] - HEIGHT])
        screen.blit(bg, game_state_now.bg_pos)

        val = gauge_power.ret_power()

        if state_now == Process_State.TITLE:
            text_title.display("ROCKETYPING",(WIDTH/2-100,HEIGHT/2-100))
            text_title.display("Enter To Start",(WIDTH/2-100,HEIGHT/2+100))
        if state_now == Process_State.LAUNCHING_1:
            text_light_green.display("Press space to ",(WIDTH/2-220,HEIGHT/2-100))
            text_light_green.display("lock the direction",(WIDTH/2-220,HEIGHT/2-50))
        if state_now == Process_State.LAUNCHING_2:
            text_light_green.display("Press space to",(WIDTH/2-220,HEIGHT/2-100))
            text_light_green.display("set the power",(WIDTH/2-220,HEIGHT/2-50))
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
                combo+=1
                typed+=1
                score_mul=combo/10
                if score_mul >= 4:
                    score_mul=4
                if rocket.movx>80:
                    score_mul *= rocket.movx/80

                score+=question.get_strlen()*(1+score_mul)*staging_const

            elif question.wait_input()== 2:#間違ってたらコンボを0に
                combo/=2.5
                combo=math.floor(combo)
            elif question.wait_input()==0:#1文の入力が終わったら
                game_state_now.solved = True# k
            global_k = None
            score=math.floor(score)
            text_orange.display("Score:"+str(score),(WIDTH/2+30,100))
            text_pink.display("Combo:"+str(combo),(WIDTH/2+30,125))
            text_light_blue.display("Multiplier:"+str(round(score_mul,3)),(WIDTH/2+30,150))

            # print(global_k)
            question.display_process()

            text_vector.display("Flight Time:" + str(math.floor(timer)), (15, 0))
            text_vector.display("Velocity:" + str(math.floor(rocket.movx)), (15, 70))
            dist_moved += rocket.movx
            timer -= 1 / FPS

            rocket.move_center(game_state_now.bg_pos)
            if game_state_now.bg_pos[0] > WIDTH:
                game_state_now.bg_pos[0] = 0
            if game_state_now.bg_pos[1] < 0:
                game_state_now.bg_pos[1] = HEIGHT
            if timer < 0:
                state_now = Process_State.FALLING

        elif state_now == Process_State.FALLING:
            dist_moved=math.floor(dist_moved)
            text_vector.display("GAME FINISHED!",(WIDTH/2-100,HEIGHT/2-120))
            text_vector.display("Score:" + str(score), (WIDTH/2-100,HEIGHT/2+50))
            text_light_blue.display("You traveled:"+str(dist_moved)+"KM",(WIDTH/2-140,HEIGHT/2+75))
            text_white.display("Press [Enter] to restart",(WIDTH/2-140,HEIGHT/2+110))
            text_white.display("Press [ESC] to quit",(WIDTH/2-140,HEIGHT/2+140))
            text_white.display("Your Typing Speed:"+str(round(typed/limit_time,3))+"/s",(WIDTH/2-140,HEIGHT/2+165))
            print(typed)

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
                        score=0
                        score_mul=0
                        combo=0
                        typed=0
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
                        limit_time=calc_limit_time(rocket.movy)
                        timer = calc_limit_time(rocket.movy)
                        gauge_vector.set_gauge_max(rocket.movx*2)
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
