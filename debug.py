# This module contains functions used for debugging the CPU & video

# Generate a hexdump of the chip8's RAM
def system_memory_dump(chip8):
    for i in range(0, len(chip8.system_memory), 16):
        print(format(i, '04X'),":", end=" ")
        for j in range(8):
            print(format(chip8.system_memory[i+j], '02X'), end=" ")
        print(" ", end="")
        for k in range(8,16):
            print(format(chip8.system_memory[i+k], '02X'), end=" ")
        print("")
    print(len(chip8.system_memory), "bytes")
    print("\n")

# Generate a bitmap dump of the chip8's video memory
def video_memory_dump(chip8):
    for i in range(32):
        for j in range(64):
            print(chip8.video_memory[i*64+j],end="")
        print("")
    print("\n")

# Generate a hexdump of the chip8's registers
def system_registers_dump(chip8):
    print("   I:", format(chip8.register_I, '04X'))
    print("  PC:", format(chip8.register_PC, '04X'))
    print("DRAW:", format(int(chip8.video_draw_flag), "02X"))

    print(" KEY:", end=" ")
    for i in range(8):
        print(format(chip8.keys_pressed[i],'02X'),end=" ")
    print(" ", end="")
    for j in range(8,16):
        print(format(chip8.keys_pressed[j],'02X'),end=" ")
    print("\n", end="")    
    
    print("  Vn:", end=" ")
    for i in range(8):
        print(format(chip8.register_V[i],'02X'),end=" ")
    print(" ", end="")
    for j in range(8,16):
        print(format(chip8.register_V[j],'02X'),end=" ")
    print("\n")

# Generate a hexdump of the chip8's stack
def system_stack_dump(chip8):
    print("STACK:", end=" ")
    for i in reversed(chip8.stack):
        print(format(i,'04X'),end=" ")
    print("\n")

# Execute all debugging functions
def dump(chip8):
    video_memory_dump(chip8)
    system_memory_dump(chip8)
    system_registers_dump(chip8)
    system_stack_dump(chip8)
