# This module contains functions to read the video memory and draw 
# to the screen after a DXYN instruction.

import pygame

# Draw a pixel to the screen
def pixel_draw(canvas, profile, x, y, pixel_bit):
	if pixel_bit == 1:
		x1 = x * profile["zoom"]
		y1 = y * profile["zoom"]

		pygame.draw.rect(canvas, profile["foreground_color"], 
						(x1, y1, profile["zoom"], profile["zoom"]), 0)

# Draw the entire video memory to the screen
def frame_draw(chip8, canvas, profile):
	# Clear the current frame before drawing a new one
	canvas.fill(profile["background_color"])
	
	i = 0
	for y in range(32):
		for x in range(64):
			pixel_draw(canvas, profile, x, y, chip8.video_memory[i])
			i = i + 1
	chip8.video_draw_flag = 0
