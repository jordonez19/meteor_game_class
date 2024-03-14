import sys
import cfg
import pygame
from modules import *


def show_level_message(screen, font, level):
    level_text = font.render("Nivel " + str(level), True, (255, 255, 255))
    text_rect = level_text.get_rect(
        center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2)
    )
    screen.blit(level_text, text_rect)
    pygame.display.update()
    pygame.time.delay(2000)


def EndGame(screen, font):
    end_text = font.render("Fin del juego", True, (255, 255, 255))
    text_rect = end_text.get_rect(
        center=(cfg.SCREENSIZE[0] // 2, cfg.SCREENSIZE[1] // 2)
    )
    screen.blit(end_text, text_rect)
    pygame.display.update()
    pygame.time.delay(2000)


def GamingInterface(num_player, screen):
    pygame.mixer.music.load(cfg.SOUNDPATHS["Cool Space Music"])
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)
    explosion_sound = pygame.mixer.Sound(cfg.SOUNDPATHS["boom"])
    fire_sound = pygame.mixer.Sound(cfg.SOUNDPATHS["shot"])
    font = pygame.font.Font(cfg.FONTPATH, 40)

    bg_imgs = {
        1: pygame.image.load(cfg.IMAGEPATHS["bg_big"]).convert(),
        2: pygame.image.load(cfg.IMAGEPATHS["seamless_space"]).convert(),
        3: pygame.image.load(cfg.IMAGEPATHS["space3"]).convert(),
        4: pygame.image.load(cfg.IMAGEPATHS["bg_big"]).convert(),
        5: pygame.image.load(cfg.IMAGEPATHS["seamless_space"]).convert(),
        6: pygame.image.load(cfg.IMAGEPATHS["space3"]).convert(),
        7: pygame.image.load(cfg.IMAGEPATHS["bg_big"]).convert(),
        8: pygame.image.load(cfg.IMAGEPATHS["seamless_space"]).convert(),
        9: pygame.image.load(cfg.IMAGEPATHS["space3"]).convert(),
    }

    bg_move_dis = 0
    player_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    asteroid_group = pygame.sprite.Group()

    asteroid_ticks = 90
    level = 1
    asteroids_destroyed = 0
    asteroids_to_destroy = 5
    asteroids_per_level = {
        1: 1,
        2: 2,
        3: 2,
        4: 3,
        5: 3,
        6: 4,
        7: 4,
        8: 5,
        9: 5,
    }  # Cantidad de asteroides por nivel
    asteroid_speeds = {
        1: 2,
        2: 4,
        3: 6,
        4: 8,
        5: 10,
        6: 12,
        7: 13,
        8: 14,
        9: 15,
    }  # Velocidad de los asteroides por nivel

    for i in range(num_player):
        player_group.add(Ship(i + 1, cfg))

    clock = pygame.time.Clock()

    score_1, score_2 = 0, 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pressed_keys = pygame.key.get_pressed()
        for idx, player in enumerate(player_group):
            direction = None
            if idx == 0:
                if pressed_keys[pygame.K_UP]:
                    direction = "up"
                elif pressed_keys[pygame.K_DOWN]:
                    direction = "down"
                elif pressed_keys[pygame.K_LEFT]:
                    direction = "left"
                elif pressed_keys[pygame.K_RIGHT]:
                    direction = "right"
                if direction:
                    player.move(direction)
                if pressed_keys[pygame.K_j]:
                    if player.cooling_time == 0:
                        fire_sound.play()
                        bullet_group.add(player.shot())
                        player.cooling_time = 20

            elif idx == 1:
                if pressed_keys[pygame.K_w]:
                    direction = "up"
                elif pressed_keys[pygame.K_s]:
                    direction = "down"
                elif pressed_keys[pygame.K_a]:
                    direction = "left"
                elif pressed_keys[pygame.K_d]:
                    direction = "right"
                if direction:
                    player.move(direction)
                if pressed_keys[pygame.K_SPACE]:
                    if player.cooling_time == 0:
                        fire_sound.play()
                        bullet_group.add(player.shot())
                        player.cooling_time = 20

            if player.cooling_time > 0:
                player.cooling_time -= 1

        background = bg_imgs[level]

        screen.blit(background, (0, -background.get_rect().height + bg_move_dis))
        screen.blit(background, (0, bg_move_dis))
        bg_move_dis = (bg_move_dis + 2) % background.get_rect().height

        if asteroid_ticks == 0:
            asteroid_ticks = 90
            # Aumentar la cantidad de asteroides según el nivel
            for _ in range(asteroids_per_level[level]):
                # Crear asteroides con velocidad según el nivel
                asteroid_group.add(Asteroid(cfg, speed=asteroid_speeds[level]))
        else:
            asteroid_ticks -= 1

        for player in player_group:
            if pygame.sprite.spritecollide(player, asteroid_group, True, None):
                player.explode_stop = 1
                explosion_sound.play()
            elif player.explode_stop > 0:
                if player.explode_stop > 3:
                    player_group.remove(player)
                    if len(player_group) == 0:
                        return
                else:
                    player.explode(screen)

            else:
                player.draw(screen)

        for bullet in bullet_group:
            bullet.move()
            if pygame.sprite.spritecollide(bullet, asteroid_group, True, None):
                bullet_group.remove(bullet)
                if bullet.player_idx == 1:
                    score_1 += 1
                else:
                    score_2 += 1
                asteroids_destroyed += 1
                if asteroids_destroyed >= asteroids_to_destroy:
                    level += 1
                    asteroids_destroyed = 0
                    if level in asteroids_per_level:
                        show_level_message(screen, font, level)
            else:
                bullet.draw(screen)

        for asteroid in asteroid_group:
            asteroid.move()
            asteroid.rotate()
            asteroid.draw(screen)

        score_1_text = "Player1 Score: %s" % score_1
        score_2_text = "Player2 Score: %s" % score_2
        text_1 = font.render(score_1_text, True, (0, 0, 255))
        text_2 = font.render(score_2_text, True, (255, 0, 0))
        screen.blit(text_1, (10, 10))
        screen.blit(text_2, (10, 50))

        pygame.display.update()
        clock.tick(60)


def main():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode(cfg.SCREENSIZE)
    pygame.display.set_caption("Meteor Game")
    num_player = StartInterface(screen, cfg)
    if num_player == 1:
        while True:
            GamingInterface(num_player=1, screen=screen)
            EndInterface(screen, cfg)
    else:
        while True:
            GamingInterface(num_player=2, screen=screen)
            EndInterface(screen, cfg)


if __name__ == "__main__":
    main()
