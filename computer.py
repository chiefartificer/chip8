# This module contains the CPU & memory. It also includes functions
# to support the DXYN instruction and load ROM files.

import pygame
import sys
import random
import time

# Stateful class representing the CHIP-8 computer
class CHIP8:
    # Initialize CPU & memory
    def __init__(self):

        # Memory and stack
        self.system_memory = [0] * 4096
        self.video_memory = [0] * (64 * 32)
        self.stack = [] 

        # 8-bits registers
        self.register_V = [0] * 16
        self.delay_timer = 0
        self.sound_timer = 0
        
        # 16-bits registers
        self.register_I = 0 
        self.register_PC = 0x0200

        # Draw flag pseudo register. set to 1 when a screen redraw is needed
        self.video_draw_flag = 0

        # Keyboard pseudo register. indexes 0-15 are use to store the 
        # correspospoding hex keys state. Set to 1 if the key is pressed and 0 
        # otherwise 
        self.keys_pressed = [0] * 16

        # shift_VY is a compatibility flag that can be toggled off to 
        # shift VX instead of VY. Check instructions 8XY6 and 8XYE. Many games
        # like "BLINKY" requires it off
        self.shift_VY = 0

        # cycle_start_time and cycle_end_time are used to measure the time 
        # between CPU cycles
        self.cycle_start_time = 0
        self.cycle_end_time = 0
        
        # Initialize sound
        pygame.mixer.music.load("pong.wav") 

        # Load default fontset into system memory. Each character takes 5 bytes
        self.fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0, #0
                        0x20, 0x60, 0x20, 0x20, 0x70, #1
                        0xF0, 0x10, 0xF0, 0x80, 0xF0, #2
                        0xF0, 0x10, 0xF0, 0x10, 0xF0, #3
                        0x90, 0x90, 0xF0, 0x10, 0x10, #4
                        0xF0, 0x80, 0xF0, 0x10, 0xF0, #5
                        0xF0, 0x80, 0xF0, 0x90, 0xF0, #6
                        0xF0, 0x10, 0x20, 0x40, 0x40, #7
                        0xF0, 0x90, 0xF0, 0x90, 0xF0, #8
                        0xF0, 0x90, 0xF0, 0x10, 0xF0, #9
                        0xF0, 0x90, 0xF0, 0x90, 0x90, #A
                        0xE0, 0x90, 0xE0, 0x90, 0xE0, #B
                        0xF0, 0x80, 0x80, 0x80, 0xF0, #C
                        0xE0, 0x90, 0x90, 0x90, 0xE0, #D
                        0xF0, 0x80, 0xF0, 0x80, 0xF0, #E
                        0xF0, 0x80, 0xF0, 0x80, 0x80] #F
        for i in range(80):
            self.system_memory[i] = self.fontset[i]

    # Writes a bit to the video memory
    def video_memory_write(self, x, y, system_memory_bit):
        if x < 64 and y < 32:
            # row major calculation for video memory offset
            video_offset = x + (y * 64)
            # Set the sprite collision detection flag
            if (self.video_memory[video_offset] & int(system_memory_bit)) == 1:
                self.register_V[0xF] = 1 
            # video memory writes are XORed in CHIP8
            self.video_memory[video_offset] ^= int(system_memory_bit)

    # Writes a sprite to the video memory
    def dxyn(self, x, y, n):
        # Reset collision detection flag
        self.register_V[0xF] = 0

        for i in range(n):
            system_memory_byte = int(self.system_memory[self.register_I+i])
            for j in range(8):
                self.video_memory_write(x+j, y+i, (system_memory_byte >> 7-j) & 0x01)
        self.video_draw_flag = 1
            
    # Open a game ROM file and load it on RAM location 0x200
    def file_open(self, file_name):
        try:
            with open("roms/" + file_name, "rb") as f:
                file_bytes = f.read()
                for i in range(len(file_bytes)):
                    self.system_memory[0x200+i] = int(file_bytes[i])
        except:
            print("WRONG FILE NAME, USE SYNTAX: python main.py <FILE>, <profile>")
            print("EXAMPLE: python main.py INVADERS, normal")
            
            pygame.quit()
            sys.exit()

    # CPU fetch–decode–execute cycle
    def cpu_cycle(self):

        # Fetch
        instruction = self.system_memory[self.register_PC] << 8 ^ self.system_memory[self.register_PC+1]
        xx = (instruction & 0x0F00) >> 8
        yy = (instruction & 0x00F0) >> 4

        # OOEO Clear the screen
        if instruction == 0x00E0:
            self.video_memory = [0] * (64 * 32)
            self.video_draw_flag = 1

        # 00EE Return from a subroutine
        elif instruction == 0x00EE:
            self.register_PC = self.stack.pop()

        # 1NNN Jump to address NNN
        elif instruction & 0xF000 == 0x1000:
            # The -2 is to account for the +2 add the end of the cycle
            self.register_PC = (instruction & 0x0FFF) - 2

        # 2NNN Execute subroutine starting at address NNN
        elif instruction & 0xF000 == 0x2000:
            self.stack.append(self.register_PC)
            self.register_PC = (instruction & 0x0FFF) -2
        
        # 3XNN Skip the following instruction if the value of register 
        # equals NN
        elif instruction & 0xF000 == 0x3000:
            if self.register_V[xx] == (instruction & 0x00FF):
                self.register_PC += 2
        
        # 4XNN Skip the following instruction if the value of register VX 
        # is not equal to NN
        elif instruction & 0xF000 == 0x4000:
            if self.register_V[xx] != (instruction & 0x00FF):
                self.register_PC += 2
        
        # 5XY0 Skip the following instruction if the value of register VX 
        # is equal to the value of register VY
        elif instruction & 0xF000 == 0x5000:
            if self.register_V[xx] == self.register_V[yy]:
                self.register_PC += 2
        
        # 6XNN Store number NN in register VX
        elif instruction & 0xF000 == 0x6000:
            self.register_V[xx] = (instruction & 0x00FF)
        
        # 7XNN Add the value NN to register VX
        elif instruction & 0xF000 == 0x7000:
            self.register_V[xx] += (instruction & 0x00FF)
            
            # Truncate VX to 8 bits to ensure compatibility
            self.register_V[xx] &= 0xFF
        
        # Decode and Execute all opcodes starting with 0x8
        elif instruction & 0xF000 == 0x8000:
            
            # 8XY0 Store the value of register VY in register VX
            if instruction & 0xF00F == 0x8000:
                self.register_V[xx] = self.register_V[yy]
            
            # 8XY1 Set VX to VX OR VY
            elif instruction & 0xF00F == 0x8001:
                self.register_V[xx] |= self.register_V[yy]
            
            # 8XY2 Set VX to VX AND VY
            elif instruction & 0xF00F == 0x8002:
                self.register_V[xx] &= self.register_V[yy]
            
            # 8XY3 Set VX to VX XOR VY
            elif instruction & 0xF00F == 0x8003:
                self.register_V[xx] ^= self.register_V[yy]
            
            # 8XY4 Add the value of register VY to register VX
            # Set VF to 01 if a carry occurs
            # Set VF to 00 if a carry does not occur
            elif instruction & 0xF00F == 0x8004:
                self.register_V[xx] += self.register_V[yy]

                # Truncate VX to 8 bits to ensure compatibility
                self.register_V[xx] &= 0xFF

                if self.register_V[xx] > 0xFF:
                    self.register_V[0x0F] = 0x01
                else:
                    self.register_V[0x0F] = 0x00
                
            # 8XY5 Subtract the value of register VY from register VX
            # Set VF to 00 if a borrow occurs (xx < VY)
            # Set VF to 01 if a borrow does not occur (xx > VY)
            elif instruction & 0xF00F == 0x8005:
                if self.register_V[xx] < self.register_V[yy]:
                    self.register_V[0x0F] = 0x00
                elif self.register_V[xx] > self.register_V[yy]:
                    self.register_V[0x0F] = 0x01
                self.register_V[xx] -= self.register_V[yy]

                # Truncate VX to 8 bits to ensure compatibility
                self.register_V[xx] &= 0xFF
                
            # 8XY6 Store the value of register VY shifted right one bit in register
            # VX Set register VF to the least significant bit prior to the shift
            elif instruction & 0xF00F == 0x8006:
                if self.shift_VY == 1:
                    self.register_V[0x0F] = self.register_V[yy] & 0x01
                    self.register_V[xx] = self.register_V[yy] >> 1
                else:
                    self.register_V[0x0F] = self.register_V[xx] & 0x01
                    self.register_V[xx] = self.register_V[xx] >> 1
                   
            # 8XY7 Set register VX to the value of VY minus VX. Set VF to 00 if 
            # a borrow occurs. Set VF to 01 if a borrow does not occur
            elif instruction & 0xF00F == 0x8007:
                if self.register_V[yy] < self.register_V[xx]:
                    self.register_V[0x0F] = 0x00
                elif self.register_V[yy] > self.register_V[xx]:
                    self.register_V[0x0F] = 0x01
                self.register_V[xx] = self.register_V[yy] - self.register_V[xx]

                # Truncate VX to 8 bits to ensure compatibility
                self.register_V[xx] &= 0xFF
                
            # 8XYE	Store the value of register VY shifted left one bit in register
            # VX, Set register VF to the most significant bit prior to the shift
            elif instruction & 0xF00F == 0x800E:
                if self.shift_VY == 1:
                    self.register_V[0x0F] = self.register_V[yy] & 0x80
                    self.register_V[xx] = self.register_V[yy] << 1
                else:
                    self.register_V[0x0F] = self.register_V[xx] & 0x80
                    self.register_V[xx] = self.register_V[xx] << 1

                # Truncate VX to 8 bits to ensure compatibility
                self.register_V[xx] &= 0xFF

        # 9XY0 Skip the following instruction if the value of register VX is 
        # not equal to the value of register VY 
        elif instruction & 0xF000 == 0x9000:
            if self.register_V[xx] != self.register_V[yy]:
                self.register_PC += 2
        
        # ANNN Store memory address NNN in register I
        elif instruction & 0xF000 == 0xA000:
            self.register_I = (instruction & 0x0FFF)
        
        # BNNN Jump to address NNN + V0
        elif instruction & 0xF000 == 0xB000:
            self.register_PC = ((instruction & 0x0FFF) + self.register_V[0]) - 2   
        
        # CXNN Set VX to a random number with a mask of NN
        elif instruction & 0xF000 == 0xC000:
            nn = instruction & 0x00FF
            self.register_V[xx] = random.randrange(0, 255) & nn
        
        # DXYN Draw a sprite at position VX, VY with N bytes of sprite data 
        # starting at the address stored in I, Set VF to 01 if any set pixels
        # are changed to unset, and 00 otherwise
        elif instruction & 0xF000 == 0xD000:
                n = (instruction & 0x000F)
                self.dxyn(self.register_V[xx], self.register_V[yy], n)
        
        # EX9E Skip the following instruction if the key corresponding to the
        # hex value currently stored in register VX is pressed
        elif instruction & 0xF0FF == 0xE09E:
            if self.keys_pressed[self.register_V[xx]] == 1:
                self.register_PC += 2
        
        # EXA1 Skip the following instruction if the key corresponding to the 
        # hex value currently stored in register VX is not pressed
        elif instruction & 0xF0FF == 0xE0A1:
            if self.keys_pressed[self.register_V[xx]] == 0:
                self.register_PC += 2

        # Decode and Execute all opcodes starting with 0xF
        elif instruction & 0xF000 == 0xF000:
            
            # FX07 Store the current value of the delay timer in register VX
            if instruction & 0xF0FF == 0xF007:
                self.register_V[xx] = self.delay_timer
            
            # FX0A Wait for a keypress and store the result in register VX
            elif instruction & 0xF0FF == 0xF00A:
                self.register_PC -= 2
                for i in range(16):
                    if self.keys_pressed[i] == 1:
                        self.register_V[xx] = i
                        self.register_PC += 2
                        break     
            
            # FX15 Set the delay timer to the value of register VX
            elif instruction & 0xF0FF == 0xF015:
                self.delay_timer = self.register_V[xx]
            
            # FX18 Set the sound timer to the value of register VX
            elif instruction & 0xF0FF == 0xF018:
                self.sound_timer = self.register_V[xx]
            
            # FX1E Add the value stored in register VX to register I
            elif instruction & 0xF0FF == 0xF01E:
                self.register_I += self.register_V[xx]
            
            # FX29 Set I to the memory address of the sprite data corresponding to
            # the hexadecimal digit stored in register VX
            elif instruction & 0xF0FF == 0xF029:
                self.register_I = self.register_V[xx] * 5
            
            # FX33 Store the binary-coded decimal equivalent of the value stored in
            # register VX at addresses I, I+1, and I+2
            elif instruction & 0xF0FF == 0xF033:
                self.system_memory[self.register_I] = self.register_V[xx] // 100
                self.system_memory[self.register_I+1] = (self.register_V[xx] % 100) // 10
                self.system_memory[self.register_I+2] = (self.register_V[xx] % 100) % 10 
            
            # FX55 Store the values of registers V0 to VX inclusive in memory 
            # starting at address I. I is set to I + X + 1 after operation
            elif instruction & 0xF0FF == 0xF055:
                for i in range(xx+1):
                    self.system_memory[self.register_I+i] = self.register_V[i]
                self.register_I += (xx + 1)
            
            # FX65 Fill registers V0 to VX inclusive with the values stored in 
            # memory starting at address I. I is set to I + X + 1 after operation
            elif instruction & 0xF0FF == 0xF065:
                for i in range(xx+1):
                    self.register_V[i] = self.system_memory[self.register_I+i]

                    # Truncate VX to 8 bits to ensure compatibility
                    self.register_V[i] &= 0xFF

                self.register_I += (xx + 1)

        # Count down the delay and sound timer registers every CPU cycle if at 
        # least 1/60 seconds has elapsed since the last cycle. If the sound 
        # timer isn't zero it generates a sound
        self.cycle_end_time = time.time()   

        if self.cycle_end_time - self.cycle_start_time >= 1/60:
            if self.delay_timer > 0:
                self.delay_timer -= 1
        
            if self.sound_timer > 0:
                self.sound_timer -= 1
                pygame.mixer.music.play()
        
            self.cycle_start_time = self.cycle_end_time

        # Increment the PC register for the next cycle
        self.register_PC += 2    
