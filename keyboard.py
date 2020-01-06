# This module contains functions to use the PC keyboard as a
# CHIP-8 hex keyboard

import pygame

# Get the hex value of the key pressed
def key_pressed(chip8, event):

    # This dictionary is organized to resemble the 1977 COSMAC VIP's keyboard
    keys = { 
        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF 
        }

    if event.key in keys:
        key = keys[event.key]
        if event.type == pygame.KEYDOWN:
            chip8.keys_pressed[key] = 1
        elif event.type == pygame.KEYUP:
            chip8.keys_pressed[key] = 0
