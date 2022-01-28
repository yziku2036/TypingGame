# -*- coding: utf-8 -*-

import sys
from rocketyping_lib import *


def main():
    global_k = '0'
    game_state_now = Game_States_Init()
    pygame.init()
    state_now = Process_State.TITLE
    screen = pygame.display.set_mode(Game_System.WINDOW_SIZE)
    pygame.display.set_caption("RockeTyping")
    bg = pygame.image.load("images/background.png")
    texts = Text_Colored_Init(screen)

    word_data = DataReader("words", screen)

    rocket = Rocket(1, 1, (100, 300), 0)
    # ゲージの定義は色、(左上のx座標、y座標、xサイズ、yサイズ)、ゲージの値の最大値(見た目に影響はなく、ret_powerの戻り値にのみ影響)
    gauge_power = Gauge_Launch_Power(screen, (255, 255, 0), (550, 50, 40, 300), 200)
    gauge_timer = Gauge_Timer(screen, (255, 0, 128), (20, 40, 300, 30), 20)
    gauge_vector = Gauge_Horizontal(screen, (0, 128, 128), (20, 110, 300, 30), 100)

    time_remaining = 0

    my_group = pygame.sprite.Group(rocket)

    screen.fill(Game_System.BACKGROUND_COLOR)  # 背景色を設定
    screen.blit(bg, game_state_now.bg_pos)
    clock = pygame.time.Clock()  # クロックを開始

    while True:
        screen.fill(Game_System.BACKGROUND_COLOR)
        screen.blit(bg, [game_state_now.bg_pos[0] - Game_System.WIDTH, game_state_now.bg_pos[1]])
        screen.blit(bg, [game_state_now.bg_pos[0], game_state_now.bg_pos[1] - Game_System.HEIGHT])
        screen.blit(bg, [game_state_now.bg_pos[0] - Game_System.WIDTH, game_state_now.bg_pos[1] - Game_System.HEIGHT])
        screen.blit(bg, game_state_now.bg_pos)
        # 最大100
        rocket_power = gauge_power.ret_power()

        if state_now == Process_State.TITLE:
            texts.text_title.display("ROCKETYPING", (Game_System.WIDTH / 2 - 100, Game_System.HEIGHT / 2 - 100))
            texts.text_title.display("Enter To Start", (Game_System.WIDTH / 2 - 100, Game_System.HEIGHT / 2 + 100))
        if state_now == Process_State.LAUNCHING_1:
            texts.text_light_green.display("Press space to ",
                                           (Game_System.WIDTH / 2 - 220, Game_System.HEIGHT / 2 - 100))
            texts.text_light_green.display("lock the direction",
                                           (Game_System.WIDTH / 2 - 220, Game_System.HEIGHT / 2 - 50))
        if state_now == Process_State.LAUNCHING_2:
            texts.text_light_green.display("Press space to",
                                           (Game_System.WIDTH / 2 - 220, Game_System.HEIGHT / 2 - 100))
            texts.text_light_green.display("set the power", (Game_System.WIDTH / 2 - 220, Game_System.HEIGHT / 2 - 50))
            gauge_power.update()
            gauge_power.display()
            rocket.calc_launch_angle(rocket_power)

        elif state_now == Process_State.FLYING:
            if game_state_now.deplete_start_timer > 0:
                game_state_now.deplete_start_timer -= 1
            else:
                rocket.deplete_velocity()
            gauge_power.display_fading()
            gauge_timer.update()
            gauge_timer.display()
            gauge_vector.set_power(rocket.speed_x)
            gauge_vector.update()
            gauge_vector.display()

            if game_state_now.solved:  # 1文打ち終わったら
                word_data.translation()
                question = SeparatedText(word_data.return_question(), screen)
                rocket.accelerate(question.get_strlen() * 5)
                game_state_now.solved = False

            word_data.display_question()  # 引数は問題の場所
            question.load_input(global_k)
            if question.judge_input() == 1:  # あってたら
                game_state_now.combo += 1
                game_state_now.typed += 1
                game_state_now.score_mul = game_state_now.combo / 10
                if game_state_now.score_mul >= 4:
                    game_state_now.score_mul = 4
                if rocket.speed_x > 80:
                    game_state_now.score_mul *= rocket.speed_x / 80

                game_state_now.score += question.get_strlen() * (
                        1 + game_state_now.score_mul) * game_state_now.staging_const
            # 間違ってたらコンボを0に
            elif question.judge_input() == 2:
                game_state_now.combo /= 2.5
                game_state_now.combo = math.floor(game_state_now.combo)
                # 1文の入力が終わったら
            elif question.judge_input() == 0:
                game_state_now.solved = True  # k
            global_k = None
            game_state_now.score = math.floor(game_state_now.score)
            texts.text_orange.display("Score:" + str(game_state_now.score), (Game_System.WIDTH / 2 + 30, 100))
            texts.text_pink.display("Combo:" + str(game_state_now.combo), (Game_System.WIDTH / 2 + 30, 125))
            texts.text_light_blue.display("Multiplier:" + str(round(game_state_now.score_mul, 3)),
                                          (Game_System.WIDTH / 2 + 30, 150))

            question.display()

            texts.text_vector.display("Flight Time:" + str(math.floor(time_remaining)), (15, 0))
            texts.text_vector.display("Velocity:" + str(math.floor(rocket.speed_x)), (15, 70))
            game_state_now.dist_moved += rocket.speed_x
            time_remaining -= 1 / Game_System.FPS

            rocket.move_background(game_state_now.bg_pos)

            if time_remaining < 0:
                state_now = Process_State.FALLING

        elif state_now == Process_State.FALLING:
            game_state_now.dist_moved = math.floor(game_state_now.dist_moved)
            texts.text_vector.display("GAME FINISHED!", (Game_System.WIDTH / 2 - 100, Game_System.HEIGHT / 2 - 120))
            texts.text_vector.display("Score:" + str(game_state_now.score),
                                      (Game_System.WIDTH / 2 - 100, Game_System.HEIGHT / 2 + 50))
            texts.text_light_blue.display("You traveled:" + str(game_state_now.dist_moved) + "KM",
                                          (Game_System.WIDTH / 2 - 140, Game_System.HEIGHT / 2 + 75))
            texts.text_white.display("Press [Enter] to restart",
                                     (Game_System.WIDTH / 2 - 140, Game_System.HEIGHT / 2 + 110))
            texts.text_white.display("Press [ESC] to quit", (Game_System.WIDTH / 2 - 140, Game_System.HEIGHT / 2 + 140))
            texts.text_white.display(
                "Your Typing Speed:" + str(round(game_state_now.typed / game_state_now.limit_time, 3)) + "/s",
                (Game_System.WIDTH / 2 - 140, Game_System.HEIGHT / 2 + 165))

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
                    # K_RETURNはENTER
                elif k is pygame.K_RETURN:
                    if state_now == Process_State.TITLE:
                        # タイトルから移行する場面
                        rocket.locked = False
                        gauge_timer.reset()
                        state_now = Process_State.LAUNCHING_1
                    # ゲームリセット時
                    elif state_now == Process_State.FALLING:
                        state_now = Process_State.TITLE
                        rocket.reset()
                        gauge_timer.reset()
                        game_state_now.init()
                elif k is pygame.K_SPACE:
                    # ロケットの向きを固定する瞬間
                    if state_now == Process_State.LAUNCHING_1:
                        rocket = Rocket(1, 1, (100, 300), rocket.image_angle)
                        rocket.locked = True
                        my_group = pygame.sprite.Group(rocket)
                        gauge_power.display()
                        state_now = Process_State.LAUNCHING_2
                    elif state_now == Process_State.LAUNCHING_2:
                        # ロケットのパワーを確定した瞬間
                        # ゲームの状態を「飛行状態」に
                        state_now = Process_State.FLYING
                        # 時間制限を計算し確定させ、ゲーム本体にわたす
                        game_state_now.limit_time = calc_limit_time(rocket.speed_y)
                        # 残り時間(可変)の変数を作成
                        time_remaining = calc_limit_time(rocket.speed_y)
                        # タイマーゲージに時間を渡す
                        gauge_timer.set_max_value(game_state_now.limit_time)
                        # ロケットの速度減少が始まる時間を計算
                        game_state_now.deplete_start_timer = rocket.speed_x * Game_System.FPS / 16
                if k is pygame.K_LEFT:
                    rocket.image_angle = 0
                    rocket.calc_launch_angle(rocket_power)

                    # 背景色で塗りつぶし

        # 画像を更新して描写
        my_group.update()
        my_group.draw(screen)

        # 表示全体を更新
        pygame.display.update()
        clock.tick(Game_System.FPS)  # フレームレート分待機


def key_pressed(e):
    return e.key


if __name__ == '__main__':
    main()
