import pygame
import math
import sys
import time
from pygame.locals import *


background_color = (35, 35, 35)
scr_width, scr_height = 1024, 600

pygame.init()
print "PyGame version " + pygame.version.ver
print "SDL version " + str(pygame.get_sdl_version())

screen = pygame.display.set_mode(
    (scr_width, scr_height), RESIZABLE)
pygame.display.set_caption("PySubs")
screen.fill(background_color)

def_font = pygame.font.SysFont(name = "Calibri", size = 30, 
                               bold = False, italic = False)
dhello_world_surf = def_font.render("Hello World!", True, (255, 255, 255))

time_hp = time.clock()
avg_fps = 60.0
full_redraw = True

# main loop
while 1:
    # parse input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit(0)
        if event.type == pygame.VIDEORESIZE:
            scr_width, scr_height = event.w, event.h
            screen = pygame.display.set_mode(
                (scr_width, scr_height), DOUBLEBUF | RESIZABLE)
            screen.fill(background_color)
            full_redraw = True
        # we are not interested in not keyboard events any further
        if not event.type == KEYDOWN: continue
        if event.key == K_ESCAPE:
            sys.exit(0)

    # Hello world
    tw = dhello_world_surf.get_width()
    th = dhello_world_surf.get_height()
    posx = int((scr_width - tw) / 2.0)
    posy = int((scr_height - th) / 2.0)
    pygame.surface.Surface.blit(screen, dhello_world_surf, (posx, posy))
    line_shift = 20 + round(
        12 * math.sin(2.0 * math.pi * (time.time() % 1.0 - 0.5)))
    line_rect = pygame.draw.line(screen, (255, 255, 255), 
                                (posx, posy - line_shift),
                                (posx + tw, posy - line_shift), 2)
    line_rect.y -= 2
    line_rect.h += 4

    # FPS counter
    frame_time = time.clock() - time_hp
    time_hp += frame_time
    avg_fps = 0.95 * avg_fps + 0.05 / frame_time
    fps_surf = def_font.render("FPS: " + "{0:.1f}".format(avg_fps), 
                               True, (255, 255, 255))
    #fps_surf = def_font.render(str(line_rect), 
    #                           True, (255, 255, 255))
    pygame.surface.Surface.blit(screen, fps_surf, (posx, posy + 30))

    hello_rect = dhello_world_surf.get_rect()
    hello_rect.x, hello_rect.y = posx, posy
    fps_rect = fps_surf.get_rect()
    fps_rect.x, fps_rect.y = posx, posy + 30

    rect_list = [hello_rect, fps_rect, line_rect]

    if full_redraw:
        pygame.display.update()
        full_redraw = False
    else:
        pygame.display.update(rect_list)
    
    # reset some rectangles

    # for hello world
    pygame.surface.Surface.fill(screen, background_color, hello_rect)
    pygame.surface.Surface.fill(screen, background_color, line_rect)

    # for FPS counter
    pygame.surface.Surface.fill(screen, background_color, fps_rect)
