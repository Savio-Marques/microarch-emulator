import memory
from array import array

MPC = 0
MIR = 0

MAR = 0
MDR = 0
PC = 0
MBR = 0
X = 0
Y = 0
H = 0

N = 0
Z = 1

BUS_A = 0
BUS_B = 0
BUS_C = 0

firmware = array('L', [0]) * 512

def ucode(nxt, jam, alu_ctrl, shift, write_reg, mem_io, read_reg):
    return (nxt << 23) | (jam << 20) | (shift << 18) | (alu_ctrl << 12) | (write_reg << 6) | (mem_io << 3) | read_reg


firmware[0] = ucode(0, 0b100, 0b110101, 0, 0b001000, 0b001, 1)

firmware[2] = ucode(128, 0, 0b110101, 0, 0b001000, 0b001, 1) 
firmware[128] = ucode(129, 0, 0b010100, 0, 0b100000, 0b010, 2)
firmware[129] = ucode(130, 0, 0b010100, 0, 0b000001, 0, 0)
firmware[130] = ucode(0, 0, 0b111100, 0, 0b000100, 0, 3) 

firmware[6] = ucode(131, 0, 0b110101, 0, 0b001000, 0b001, 1) 
firmware[131] = ucode(132, 0, 0b010100, 0, 0b100000, 0, 2)
firmware[132] = ucode(0, 0, 0b010100, 0, 0b010000, 0b100, 3) 

firmware[9]  = ucode(133, 0, 0b110101, 0, 0b001000, 0b001, 1) 
firmware[133] = ucode(0, 0b100, 0b010100, 0, 0b001000, 0b001, 2) 

firmware[10] = ucode(148, 0b010, 0b010100, 0, 0, 0, 3)
firmware[148] = ucode(0, 0, 0b110101, 0, 0b001000, 0, 1)
firmware[404] = ucode(9, 0, 0, 0, 0, 0, 0)

firmware[11] = ucode(12, 0b001, 0b010100, 0, 0, 0, 3)
firmware[12] = ucode(0, 0, 0b110101, 0, 0b001000, 0, 1) 
firmware[268] = ucode(9, 0, 0, 0, 0, 0, 0) 

firmware[13] = ucode(134, 0, 0b110101, 0, 0b001000, 0b001, 1)
firmware[134] = ucode(135, 0, 0b010100, 0, 0b100000, 0b010, 2)
firmware[135] = ucode(136, 0, 0b010100, 0, 0b000001, 0, 0)
firmware[136] = ucode(0, 0, 0b111111, 0, 0b000100, 0, 3)

firmware[16] = ucode(137, 0, 0b110101, 0, 0b001000, 0b001, 1)
firmware[137] = ucode(138, 0, 0b010100, 0, 0b100000, 0b010, 2)
firmware[138] = ucode(139, 0, 0b010100, 0, 0b000001, 0, 0)
firmware[139] = ucode(0, 0, 0b100000, 0, 0b000100, 0, 3)

firmware[17] = ucode(140, 0, 0b110101, 0, 0b001000, 0b001, 1)
firmware[140] = ucode(141, 0, 0b010100, 0, 0b100000, 0b010, 2)
firmware[141] = ucode(142, 0, 0b010100, 0, 0b000001, 0, 0)
firmware[142] = ucode(0, 0, 0b100001, 0, 0b000100, 0, 3)

firmware[18] = ucode(143, 0, 0b110101, 0, 0b001000, 0b001, 1)
firmware[143] = ucode(144, 0, 0b010100, 0, 0b100000, 0b010, 2)
firmware[144] = ucode(145, 0, 0b010100, 0, 0b000001, 0, 0)
firmware[145] = ucode(0, 0, 0b100010, 0, 0b000100, 0, 3)

firmware[19] = ucode(146, 0, 0b110101, 0, 0b001000, 0b001, 1)
firmware[146] = ucode(147, 0, 0b010100, 0, 0b100000, 0b010, 2)
firmware[147] = ucode(0, 0, 0b010100, 0, 0b000100, 0, 0)

firmware[255] = 0

def hw_mul(a, b, step=32, r=0):
    if not step:
        return r
    if b & 1:
        r = (r + a) & 0xFFFFFFFF
    return hw_mul((a << 1) & 0xFFFFFFFF, b >> 1, step - 1, r)

def bit_divmod(q, m, a=0, step=32):
    if not m:
        return (0, 0)
    if not step:
        return (q, a)
    
    a = ((a << 1) | ((q >> 31) & 1)) & 0xFFFFFFFF
    q = (q << 1) & 0xFFFFFFFF
    diff = (a - m) & 0xFFFFFFFF
    
    if not (diff & 0x80000000): 
        a = diff
        q = q | 1
        
    return bit_divmod(q, m, a, step - 1)

def read_regs(reg_num):
    global MDR, PC, MBR, X, Y, H, BUS_A, BUS_B
    
    BUS_A = H
    
    if not (reg_num ^ 0):
       BUS_B = MDR
    elif not (reg_num ^ 1):
       BUS_B = PC
    elif not (reg_num ^ 2):
       BUS_B = MBR
    elif not (reg_num ^ 3):
       BUS_B = X
    elif not (reg_num ^ 4):
       BUS_B = Y
    else:
       BUS_B = 0

def write_regs(reg_bits):
    global MAR, MDR, PC, X, Y, H, BUS_C
    
    if reg_bits & 0b100000: MAR = BUS_C
    if reg_bits & 0b010000: MDR = BUS_C
    if reg_bits & 0b001000: PC = BUS_C
    if reg_bits & 0b000100: X = BUS_C
    if reg_bits & 0b000010: Y = BUS_C
    if reg_bits & 0b000001: H = BUS_C

def alu(control_bits):
    global N, Z, BUS_A, BUS_B, BUS_C
    
    a = BUS_A
    b = BUS_B
    o = 0
    
    shift_bits = (control_bits & 0b11000000) >> 6
    control_bits = control_bits & 0b00111111
    
    if not (control_bits ^ 0b011000): o = a
    elif not (control_bits ^ 0b010100): o = b
    elif not (control_bits ^ 0b011010): o = ~a
    elif not (control_bits ^ 0b101100): o = ~b
    elif not (control_bits ^ 0b111100): o = (a + b)
    elif not (control_bits ^ 0b111101): o = (a + b + 1)
    elif not (control_bits ^ 0b111001): o = (a + 1)
    elif not (control_bits ^ 0b110101): o = (b + 1)
    elif not (control_bits ^ 0b111111): o = (b - a)
    elif not (control_bits ^ 0b110110): o = (b - 1)
    elif not (control_bits ^ 0b111011): o = -a
    elif not (control_bits ^ 0b001100): o = a & b
    elif not (control_bits ^ 0b011100): o = a | b
    elif not (control_bits ^ 0b010000): o = 0
    elif not (control_bits ^ 0b110001): o = 1
    elif not (control_bits ^ 0b110010): o = -1
    
    # Execução das novas instruções em 1 ciclo simulado
    elif not (control_bits ^ 0b100000): o = hw_mul(a, b)
    elif not (control_bits ^ 0b100001): o, _ = bit_divmod(b, a)
    elif not (control_bits ^ 0b100010): _, o = bit_divmod(b, a)
   
    o = o & 0xFFFFFFFF
    
    if not o:
       N = 0
       Z = 1
    else:
       N = (o >> 31) & 1
       Z = 0
    
    if not (shift_bits ^ 0b01): o = o << 1
    elif not (shift_bits ^ 0b10): o = o >> 1
    elif not (shift_bits ^ 0b11): o = o << 8

    BUS_C = o & 0xFFFFFFFF
    
def next_instruction(nextadd, jam):
    global MPC
    
    if not jam:
        MPC = nextadd
        return
        
    if jam & 0b001: nextadd = nextadd | (Z << 8)
    if jam & 0b010: nextadd = nextadd | (N << 8)
    if jam & 0b100: nextadd = nextadd | MBR
        
    MPC = nextadd

def memory_io(mem_bits):
    global PC, MAR, MDR, MBR
    
    if mem_bits & 0b001: MBR = memory.read_byte(PC)
    if mem_bits & 0b010: MDR = memory.read_word(MAR)
    if mem_bits & 0b100: memory.write_word(MAR, MDR)

def step():
   global MIR, MPC
   
   MIR = firmware[MPC]
   
   if not MIR:
      return False
   
   read_regs( MIR & 0b111 )
   alu((MIR & 0b00000000000011111111000000000000) >> 12)
   write_regs( (MIR & 0b00000000000000000000111111000000) >> 6)
   memory_io( (MIR & 0b00000000000000000000000000111000) >> 3 )
   next_instruction(MIR >> 23, (MIR & 0b00000000011100000000000000000000) >> 20)
   
   return True