import random
from enum import Enum
from typing import Any

import pygame
from pygame.sprite import AbstractGroup

pygame.init()
pygame.font.init()
pygame.mixer.init()

SCREEN_RECT = pygame.Rect(0, 0, 600, 1000)
FPS = 60
# 敌机出现事件常量
ENEMY_APPEAR_EVENT = pygame.USEREVENT
# 音符消失事件常量
ENEMY_DISAPPEAR_EVENT = pygame.USEREVENT + 1
# 英雄动画帧事件常量
HERO_ANIMATION_EVENT = pygame.USEREVENT + 2
# 子弹出现事件常量
BULLET_APPEAR_EVENT = pygame.USEREVENT + 3

# 设置发射音效
MUSIC_ON = True
SFX_ON = True
shoot_sound_1 = pygame.mixer.Sound('./sound/shoot_1.ogg')
shoot_sound_1.set_volume(0.1)
shoot_sound_2 = pygame.mixer.Sound('./sound/shoot_2.ogg')
shoot_sound_2.set_volume(0.1)
shoot_sound_3 = pygame.mixer.Sound('./sound/shoot_3.ogg')
shoot_sound_3.set_volume(0.1)
hit_sound_1 = pygame.mixer.Sound('./sound/hit_1.ogg')
hit_sound_1.set_volume(0.6)
hit_sound_2 = pygame.mixer.Sound('./sound/hit_2.ogg')
hit_sound_2.set_volume(0.6)
hit_sound_3 = pygame.mixer.Sound('./sound/hit_3.ogg')
hit_sound_3.set_volume(0.6)
dead_sound_1 = pygame.mixer.Sound('./sound/dead_1.ogg')
dead_sound_1.set_volume(0.3)
dead_sound_2 = pygame.mixer.Sound('./sound/dead_2.ogg')
dead_sound_2.set_volume(0.3)

WHITE = pygame.Color('White')
BLACK = pygame.Color('Black')


# 颜色枚举类
class MyColor(Enum):
    RED = pygame.Color('Red')
    GREEN = pygame.Color('Green')
    BLUE = pygame.Color('Blue')
    SKY_BLUE = pygame.Color('SkyBlue')
    YELLOW = pygame.Color('Yellow')
    ORANGE = pygame.Color('Orange')
    PURPLE = pygame.Color('Purple')
    PINK = pygame.Color('Pink')
    GRAY = pygame.Color('Gray')
    # 青色
    CYAN = pygame.Color('Cyan')


# 状态枚举类
class GameStatus(Enum):
    NORMAL = 1
    PLAYING = 2
    PAUSE = 3
    RESUME = 4
    STOP = 5


# 敌机类
class Enemy(pygame.sprite.Sprite):

    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface((50, 50))
        self.set_random_color()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_RECT.width - self.rect.width)  # 在屏幕左右两侧随机出现
        self.rect.bottom = random.randint(0, SCREEN_RECT.height // 4)  # 初始化高度，上面1/4屏幕以随机
        self.speed = random.randint(1, 5)

    def set_color(self, color: MyColor):
        self.image.fill(color.value)

    def set_random_color(self):
        self.set_color(random.choice(list(MyColor)))

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.__move()
        self.__check_edge()

    def __move(self):
        self.rect.y += self.speed

    def __check_edge(self):
        if self.rect.bottom > SCREEN_RECT.bottom:
            self.kill()


# 英雄类
class Hero(pygame.sprite.Sprite):

    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface((50, 50))
        self.set_random_color()
        self.current_color = MyColor.SKY_BLUE.value
        self.next_color = MyColor.YELLOW.value
        self.image.fill(self.current_color)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 100
        self.speed_x = 0
        self.speed_y = 0
        # 创建子弹精灵组
        self.bullet_group = pygame.sprite.Group()

    def set_color(self, color: MyColor):
        self.image.fill(color.value)

    def set_random_color(self):
        self.set_color(random.choice(list(MyColor)))

    def fire(self):
        if self.alive():
            sound = random.choice([shoot_sound_1, shoot_sound_2, shoot_sound_3])
            sound.play(maxtime=200, fade_ms=100)
            bullet = Bullet(self.bullet_group)
            bullet.rect.centerx = self.rect.centerx
            bullet.rect.bottom = self.rect.top

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.__move()
        self.__check_edge()

    def __move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def __check_edge(self):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_RECT.width:
            self.rect.right = SCREEN_RECT.width
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > SCREEN_RECT.height:
            self.rect.bottom = SCREEN_RECT.height

    def __del__(self):
        self.bullet_group.empty()


# 子弹类
class Bullet(pygame.sprite.Sprite):

    def __init__(self, *groups: AbstractGroup) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.speed = 10

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


# 背景类
class BackGround(pygame.sprite.Sprite):
    """游戏背景类"""

    def __init__(self, *groups: AbstractGroup, speed: float = 1, is_alt: bool = False) -> None:
        super().__init__(*groups)
        self.image = pygame.image.load('./images/background.png')
        self.rect = self.image.get_rect()
        if is_alt:
            self.rect.y = -self.rect.height
        else:
            self.rect.y = -(self.rect.height - SCREEN_RECT.height)
        self.speed = speed

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        # 移动
        self.__move()
        # 边缘监测
        self.__check_edge()

    def __move(self) -> None:
        self.rect.y += self.speed

    def __check_edge(self) -> None:
        if self.rect.y >= SCREEN_RECT.height:
            self.rect.y = -self.rect.height


class Game:

    def __init__(self):
        print('游戏初始化')
        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        self.clock = pygame.time.Clock()
        self.score = 0  # 分数
        self.score_2 = 0  # 分数
        self.status = GameStatus.NORMAL  # 游戏状态
        self.last_stop_time = None  # 上一次游戏结束的时间，两秒后返回主界面
        self.__set_font()  # 设置字体，和界面文字对象
        self.__init_sound()  # 设置音效
        self.__set_timer_event()  # 设置定时器事件
        self.__create_sprites()  # 创建精灵和精灵组

    def run(self):
        while True:
            self.clock.tick(FPS)
            # 事件处理
            self.__event_handler()
            # 碰撞检测
            self.__check_collide()
            # 更新精灵组
            self.__update_sprites()
            # 渲染
            self.__render()

    def __set_font(self):
        # 设置文字
        self.main_font = pygame.font.SysFont('arial', 40)
        self.center_font = pygame.font.SysFont('arial', 60)
        # 游戏主界面文字
        # self.main_text = self.center_font.render(
        #     'Press Space to start', True, WHITE, MyColor.SKY_BLUE.value)
        # self.main_rect = self.main_text.get_rect()
        # self.main_rect.center = SCREEN_RECT.center
        self.main_text_image = pygame.image.load('./images/main_text.png')
        self.main_text_rect = self.main_text_image.get_rect()
        self.main_text_rect.center = SCREEN_RECT.center
        # 游戏暂停界面文字
        self.game_pause_text = self.center_font.render(
            'Game Paused', True, MyColor.YELLOW.value, MyColor.SKY_BLUE.value)
        self.game_pause_rect = self.game_pause_text.get_rect()
        self.game_pause_rect.center = SCREEN_RECT.center
        # 游戏结束界面文字
        self.game_over_text = self.center_font.render(
            'Game Over', True, MyColor.RED.value, MyColor.PINK.value)
        self.game_over_rect = self.game_over_text.get_rect()
        self.game_over_rect.center = SCREEN_RECT.center
        # 计分文字
        self.score_font = pygame.font.SysFont('arial', 30)

    def __init_sound(self):
        # 设置BGM
        music_path = random.choice([
            './sound/bgm_1.ogg',
            './sound/bgm_2.ogg',
            './sound/bgm_3.ogg',
        ])
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)

    def __set_timer_event(self):
        # 设置定时器事件
        pygame.time.set_timer(ENEMY_APPEAR_EVENT, 250)  # 敌机出现
        pygame.time.set_timer(HERO_ANIMATION_EVENT, 200)  # 英雄动画
        pygame.time.set_timer(BULLET_APPEAR_EVENT, 100)  # 子弹出现

    def show_main_text(self):
        self.screen.blit(self.main_text_image, self.main_text_rect)

    def show_game_pause_text(self):
        self.screen.blit(self.game_pause_text, self.game_pause_rect)

    def show_game_over_text(self):
        self.screen.blit(self.game_over_text, self.game_over_rect)

    def show_score_text(self):
        self.score_text = self.score_font.render(
            f'Score: {self.score}', True, WHITE, MyColor.SKY_BLUE.value)
        self.score_rect = self.score_text.get_rect()
        self.score_rect.right = SCREEN_RECT.right
        self.screen.blit(self.score_text, self.score_rect)
        # 英雄2分数显示
        self.score_text_2 = self.score_font.render(
            f'Score: {self.score_2}', True, WHITE, MyColor.SKY_BLUE.value)
        self.score_rect_2 = self.score_text_2.get_rect()
        self.screen.blit(self.score_text_2, self.score_rect_2)

    def game_start(self):
        print('游戏开始')
        self.status = GameStatus.PLAYING
        # 切换BGM
        fight_music_path = random.choice([
            './sound/fight_1.ogg',
            './sound/fight_2.ogg',
            './sound/fight_3.ogg',
            './sound/fight_4.ogg',
        ])
        pygame.mixer.music.load(fight_music_path)
        pygame.mixer.music.play(-1)
        self.hero = Hero(self.hero_group)
        self.hero.rect.left = SCREEN_RECT.centerx + SCREEN_RECT.centerx // 2
        self.hero_2 = Hero(self.hero_group)
        self.hero_2.rect.x = SCREEN_RECT.centerx // 2

    def game_pause(self):
        print('游戏暂停')
        self.status = GameStatus.PAUSE
        pygame.mixer.music.pause()

    def game_resume(self):
        print('游戏恢复')
        self.status = GameStatus.PLAYING
        pygame.mixer.music.unpause()

    def game_over(self):
        print('游戏结束')
        # 停止BGM
        pygame.mixer.music.fadeout(500)
        # 销毁敌机精灵组
        self.enemy_group.empty()
        self.hero_group.empty()
        # 重置分数
        self.score = 0
        self.score_2 = 0

        self.status = GameStatus.STOP

    def __create_sprites(self):
        # 创建背景精灵组
        self.bg_group = pygame.sprite.Group()
        self.bg_1 = BackGround(self.bg_group)
        self.bg_2 = BackGround(self.bg_group, is_alt=True)
        # 创建敌机精灵组
        self.enemy_group = pygame.sprite.Group()
        # 创建英雄精灵
        self.hero_group = pygame.sprite.Group()

    def __event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.fadeout(200)
                pygame.time.delay(200)
                pygame.quit()
                exit()
            elif event.type == ENEMY_APPEAR_EVENT and self.status == GameStatus.PLAYING:
                # print('敌机出现')
                _ = Enemy(self.enemy_group)
            elif event.type == HERO_ANIMATION_EVENT and self.status == GameStatus.PLAYING:
                # print('英雄动画')
                self.hero.set_random_color()
                self.hero_2.set_random_color()
            elif event.type == BULLET_APPEAR_EVENT and self.status == GameStatus.PLAYING:
                self.hero.fire()
                self.hero_2.fire()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if self.status == GameStatus.NORMAL:
                        self.game_start()
                    elif self.status == GameStatus.PAUSE:
                        self.game_resume()
                    elif self.status == GameStatus.PLAYING:
                        self.game_pause()

        # 判断按键，移动英雄
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_LEFT] and self.status == GameStatus.PLAYING:
            self.hero.speed_x = -8
        elif key_pressed[pygame.K_RIGHT] and self.status == GameStatus.PLAYING:
            self.hero.speed_x = 8
        elif key_pressed[pygame.K_UP] and self.status == GameStatus.PLAYING:
            self.hero.speed_y = -8
        elif key_pressed[pygame.K_DOWN] and self.status == GameStatus.PLAYING:
            self.hero.speed_y = 8
        elif self.status == GameStatus.PLAYING:
            self.hero.speed_x = 0
            self.hero.speed_y = 0
        # 英雄2按键
        if key_pressed[pygame.K_a] and self.status == GameStatus.PLAYING:
            self.hero_2.speed_x = -8
        elif key_pressed[pygame.K_d] and self.status == GameStatus.PLAYING:
            self.hero_2.speed_x = 8
        elif key_pressed[pygame.K_w] and self.status == GameStatus.PLAYING:
            self.hero_2.speed_y = -8
        elif key_pressed[pygame.K_s] and self.status == GameStatus.PLAYING:
            self.hero_2.speed_y = 8
        elif self.status == GameStatus.PLAYING:
            self.hero_2.speed_x = 0
            self.hero_2.speed_y = 0

    def __check_collide(self):
        if not self.status == GameStatus.PLAYING:
            return
        # 子弹摧毁敌机
        result = pygame.sprite.groupcollide(self.hero.bullet_group, self.enemy_group, True, True)
        if result:
            for enemy in result:
                self.score += 1
            hit_sound = random.choice([hit_sound_1, hit_sound_2, hit_sound_3])
            hit_sound.play(maxtime=600, fade_ms=100)
        result_2 = pygame.sprite.groupcollide(self.hero_2.bullet_group, self.enemy_group, True, True)
        if result_2:
            for enemy in result_2:
                self.score_2 += 1
            hit_sound = random.choice([hit_sound_1, hit_sound_2, hit_sound_3])
            hit_sound.play(maxtime=600, fade_ms=100)
        # 敌机撞毁英雄
        result_3 = pygame.sprite.groupcollide(self.enemy_group, self.hero_group, True, True)
        if result_3:
            dead_sound = random.choice([dead_sound_1, dead_sound_2])
            dead_sound.play(fade_ms=500)
        # 如果英雄精灵组为空，则游戏结束
        if not self.hero.alive() and not self.hero_2.alive():
            self.game_over()

    def __update_sprites(self):
        # 更新背景精灵组
        self.bg_group.update()
        self.bg_group.draw(self.screen)

        if self.status == GameStatus.NORMAL:
            self.show_main_text()
        elif self.status == GameStatus.STOP:
            self.show_game_over_text()
            self.show_score_text()
            # 两秒后回到主界面
            if self.last_stop_time is None:
                self.last_stop_time = pygame.time.get_ticks()
            if self.last_stop_time is not None and \
                    pygame.time.get_ticks() - self.last_stop_time >= 1000:
                self.last_stop_time = None
                self.status = GameStatus.NORMAL
                self.__init_sound()
            return
        elif self.status == GameStatus.PLAYING:
            # 更新敌机精灵组
            self.enemy_group.update()
            self.enemy_group.draw(self.screen)
            # 更新英雄精灵组
            self.hero_group.update()
            self.hero_group.draw(self.screen)
            # 更新子弹精灵组
            self.hero.bullet_group.update()
            self.hero.bullet_group.draw(self.screen)
            self.hero_2.bullet_group.update()
            self.hero_2.bullet_group.draw(self.screen)
        elif self.status == GameStatus.PAUSE:
            self.enemy_group.draw(self.screen)
            self.hero_group.draw(self.screen)
            self.hero.bullet_group.draw(self.screen)
            self.show_game_pause_text()

        self.show_score_text()  # 显示分数

    def __render(self):
        pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
