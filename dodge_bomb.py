import os
import random
import sys
import math
import time

import pygame as pg


WIDTH, HEIGHT = 1100, 650
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BOMB_START_RADIUS = 10
BOMB_STAGES = 10
BOMB_MAX_RADIUS = BOMB_START_RADIUS * BOMB_STAGES
BOMB_START_SPEED = 5
BOMB_NORM = math.hypot(BOMB_START_SPEED, BOMB_START_SPEED)
HOMING_DISTANCE = 300
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
}
KK_IMG_PATH = "fig/3.png"
GAMEOVER_KK_IMG_PATH = "fig/8.png"
MOVEMENT_TO_ANGLE = {
    (0, 0): 0,
    (+5, 0): 180,
    (-5, 0): 0,
    (0, -5): -90,
    (0, +5): 90,
    (+5, -5): -135,
    (+5, +5): 135,
    (-5, -5): -45,
    (-5, +5): 45,
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """obj_rctが画面内に収まっているかを横方向・縦方向で判定する。"""

    yoko = 0 <= obj_rct.left and obj_rct.right <= WIDTH
    tate = 0 <= obj_rct.top and obj_rct.bottom <= HEIGHT
    return yoko, tate


def create_bomb_img(radius: int) -> pg.Surface:
    """指定した半径の爆弾画像を作成する。"""

    bb_img = pg.Surface((radius * 2, radius * 2))
    bb_img.set_colorkey(BLACK)
    pg.draw.circle(bb_img, RED, (radius, radius), radius)
    return bb_img


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """大きさを変えた爆弾画像リストと加速度リストを作成する。"""

    bb_imgs = []
    for r in range(1, BOMB_STAGES + 1):
        bb_imgs.append(create_bomb_img(BOMB_START_RADIUS * r))
    bb_accs = [a for a in range(1, BOMB_STAGES + 1)]
    return bb_imgs, bb_accs


def create_bomb() -> tuple[pg.Surface, pg.Rect]:
    """初期位置をランダムに決めて爆弾画像とRectを作成する。"""

    bb_img = create_bomb_img(BOMB_START_RADIUS)
    bb_rct = bb_img.get_rect()
    bb_rct.center = (
        random.randint(BOMB_MAX_RADIUS, WIDTH - BOMB_MAX_RADIUS),
        random.randint(BOMB_MAX_RADIUS, HEIGHT - BOMB_MAX_RADIUS),
    )
    return bb_img, bb_rct


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """移動方向ごとのこうかとん画像を回転して作成する。"""

    kk_imgs = {}
    kk_img = pg.image.load(KK_IMG_PATH)
    for movement, angle in MOVEMENT_TO_ANGLE.items():
        kk_imgs[movement] = pg.transform.rotozoom(kk_img, angle, 0.9)
    return kk_imgs


def calc_orientation(
    org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]
) -> tuple[float, float]:
    """爆弾の向きを計算し、一定距離より遠いときはこうかとんへ向かわせる。"""

    diff_x = dst.centerx - org.centerx
    diff_y = dst.centery - org.centery
    norm = math.hypot(diff_x, diff_y)
    if norm < HOMING_DISTANCE or norm == 0:
        return current_xy

    return diff_x / norm * BOMB_NORM, diff_y / norm * BOMB_NORM


def bounce_bound(obj_rct: pg.Rect, vx: float, vy: float) -> tuple[float, float]:
    """画面端で爆弾を跳ね返し、画面外に出た位置を補正する。"""

    yoko, tate = check_bound(obj_rct)
    if not yoko:
        vx *= -1
        if obj_rct.left < 0:
            obj_rct.left = 0
        elif obj_rct.right > WIDTH:
            obj_rct.right = WIDTH
    if not tate:
        vy *= -1
        if obj_rct.top < 0:
            obj_rct.top = 0
        elif obj_rct.bottom > HEIGHT:
            obj_rct.bottom = HEIGHT
    return vx, vy


def gameover(screen: pg.Surface) -> None:
    """半透明の幕とGame Over文字を表示して終了画面にする。"""

    cover = pg.Surface((WIDTH, HEIGHT))
    cover.fill(BLACK)
    cover.set_alpha(150)
    screen.blit(cover, (0, 0))

    font = pg.font.Font(None, 72)
    txt_img = font.render("Game Over", True, WHITE)
    txt_rct = txt_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    kk_img = pg.transform.rotozoom(pg.image.load(GAMEOVER_KK_IMG_PATH), 0, 0.9)
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
    time.sleep(5)


def main() -> None:
    """ゲームの初期化、イベント処理、描画を行うメイン関数"""

    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_imgs, bb_accs = init_bb_imgs()
    bb_img, bb_rct = create_bomb()
    vx, vy = BOMB_START_SPEED, BOMB_START_SPEED
    clock = pg.time.Clock()
    tmr = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        screen.blit(bg_img, [0, 0])

        # 押されているキーから、こうかとんの移動量を作る。
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]

        old_kk_img = kk_img
        old_kk_rct = kk_rct.copy()
        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct = kk_img.get_rect(center=kk_rct.center)
        kk_rct.move_ip(sum_mv)
        if not all(check_bound(kk_rct)):
            kk_img = old_kk_img
            kk_rct = old_kk_rct

        # 爆弾は時間経過で大きく速くなり、距離があるときはこうかとんを追尾する。
        bb_level = min(tmr // 500, BOMB_STAGES - 1)
        bb_img = bb_imgs[bb_level]
        bb_rct = bb_img.get_rect(center=bb_rct.center)
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        avx = vx * bb_accs[bb_level]
        avy = vy * bb_accs[bb_level]
        bb_rct.move_ip(avx, avy)
        vx, vy = bounce_bound(bb_rct, vx, vy)

        if kk_rct.colliderect(bb_rct):
            gameover(screen)
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
