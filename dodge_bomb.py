import os
import random
import sys

import pygame as pg


WIDTH, HEIGHT = 1100, 650
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BOMB_START_RADIUS = 10
BOMB_MAX_RADIUS = 60
BOMB_START_SPEED = 5
BOMB_MAX_SPEED = 15
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:

    yoko = 0 <= obj_rct.left and obj_rct.right <= WIDTH
    tate = 0 <= obj_rct.top and obj_rct.bottom <= HEIGHT
    return yoko, tate


def calc_bomb_params(tmr: int) -> tuple[int, int]:
    level = tmr // 500
    radius = min(BOMB_START_RADIUS + level * 2, BOMB_MAX_RADIUS)
    speed = min(BOMB_START_SPEED + level, BOMB_MAX_SPEED)
    return radius, speed


def create_bomb_img(radius: int) -> pg.Surface:
    bb_img = pg.Surface((radius * 2, radius * 2))
    bb_img.set_colorkey(BLACK)
    pg.draw.circle(bb_img, RED, (radius, radius), radius)
    return bb_img


def create_bomb() -> tuple[pg.Surface, pg.Rect]:
    bb_img = create_bomb_img(BOMB_START_RADIUS)
    bb_rct = bb_img.get_rect()
    bb_rct.center = (
        random.randint(BOMB_MAX_RADIUS, WIDTH - BOMB_MAX_RADIUS),
        random.randint(BOMB_MAX_RADIUS, HEIGHT - BOMB_MAX_RADIUS),
    )
    return bb_img, bb_rct


def show_game_over(
    screen: pg.Surface,
    bg_img: pg.Surface,
    kk_img: pg.Surface,
    kk_rct: pg.Rect,
) -> None:
    cover = pg.Surface((WIDTH, HEIGHT))
    cover.fill(BLACK)
    cover.set_alpha(150)
    screen.blit(cover, (0, 0))

    font = pg.font.Font(None, 72)
    txt_img = font.render("Game Over", True, WHITE)
    txt_rct = txt_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    left_kk_rct = kk_img.get_rect()
    right_kk_rct = kk_img.get_rect()
    left_kk_rct.centery = txt_rct.centery
    right_kk_rct.centery = txt_rct.centery
    left_kk_rct.right = txt_rct.left - 35
    right_kk_rct.left = txt_rct.right + 35

    screen.blit(kk_img, left_kk_rct)
    screen.blit(txt_img, txt_rct)
    screen.blit(kk_img, right_kk_rct)

    pg.display.update()
    pg.time.wait(5000)


def main() -> None:

    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    game_over_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img, bb_rct = create_bomb()
    vx, vy = BOMB_START_SPEED, BOMB_START_SPEED
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, [0, 0])

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]

        old_kk_rct = kk_rct.copy()
        kk_rct.move_ip(sum_mv)
        if not all(check_bound(kk_rct)):
            kk_rct = old_kk_rct

        radius, speed = calc_bomb_params(tmr)
        bb_img = create_bomb_img(radius)
        bb_rct = bb_img.get_rect(center=bb_rct.center)
        vx = speed if vx > 0 else -speed
        vy = speed if vy > 0 else -speed
        bb_rct.move_ip(vx, vy)

        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
            bb_rct.move_ip(vx, 0)
        if not tate:
            vy *= -1
            bb_rct.move_ip(0, vy)

        if kk_rct.colliderect(bb_rct):
            show_game_over(screen, bg_img, game_over_img, kk_rct)
            return

        screen.blit(kk_img, kk_rct)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()