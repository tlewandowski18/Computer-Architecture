"""CPU functionality."""

import sys

OP1 = 0b00000001
OP2 = 0b10000010
OP3 = 0b01000111
OP4 = 0b10100010
OP5 = 0b10100000
OP6 = 0b01000101
OP7 = 0b01000110
OP8 = 0b01010000
OP9 = 0b00010001
OP10 = 0b10100111
OP11 = 0b01010100
OP12 = 0b01010110
OP13 = 0b01010101

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xf4
        self.pc = 0
        self.equal_flag = 0b00000000
        self.running = True
        self.branchtable = {}
        self.branchtable[OP1] = self.halt
        self.branchtable[OP2] = self.ldi_handler
        self.branchtable[OP3] = self.prn
        self.branchtable[OP4] = self.mult
        self.branchtable[OP5] = self.mult_2_print
        self.branchtable[OP6] = self.push
        self.branchtable[OP7] = self.pop
        self.branchtable[OP8] = self.call
        self.branchtable[OP9] = self.ret
        self.branchtable[OP10] = self.cmp
        self.branchtable[OP11] = self.jmp
        self.branchtable[OP12] = self.jne
        self.branchtable[OP13] = self.jeq

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self, prog_name):
        """Load a program into memory."""
        address = 0
        try:
            with open(f'ls8/examples/{prog_name}') as f:
                for line in f:
                    split_line = line.split(' ')
                    code_value = split_line[0].strip()
                    if code_value == '' or code_value == '#':
                        continue
                    num = int(code_value, 2)
                    self.ram[address] = num
                    address += 1
        except FileNotFoundError:
            print(f'{prog_name} file not found')
            sys.exit(2)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            added_value = self.reg[reg_b]
            self.reg[reg_a] += added_value
        #elif op == "SUB": etc
        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "COMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.equal_flag = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.equal_flag = 0b00000010
            else:
                self.equal_flag = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    def halt(self):
        self.running = False

    def ldi_handler(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b

    def prn(self):
        operand_a = self.ram_read(self.pc + 1)
        value = self.reg[operand_a]
        print(value)
    
    def mult(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu("MULT", reg_a, reg_b)
      
    def mult_2_print(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu("ADD", reg_a, reg_b)

    def push(self):
        #decrement the stack pointer
        self.reg[7] -= 1
        #pull reg index from memory
        reg_num = self.ram[self.pc + 1]
        #pull value from reg
        value = self.reg[reg_num]
        #Store at top of stack
        top_of_stack_addr = self.reg[7]
        self.ram[top_of_stack_addr] = value
        # self.pc += 2
    
    def pop(self):
        #find stop of stack and copy value
        top_of_stack_addr = self.reg[7]
        value = self.ram[top_of_stack_addr]
        #find reg spot and store the value at that place in reg
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = value
        #increment stack pointer
        self.reg[7] += 1
        # self.pc += 2
    
    def call(self):
        #save return address to Stack
        ret_addr = self.pc + 2
        self.reg[7] -= 1
        self.ram[self.reg[7]] = ret_addr
        # Call the subroutine
        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def ret(self):
        top_stack = self.reg[7]
        ret_address = self.ram[top_stack]
        self.reg[7] += 1
        self.pc = ret_address

    def cmp(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu("COMP", reg_a, reg_b)

    def jmp(self):
        reg_num = self.ram[self.pc + 1]
        jmp_address = self.reg[reg_num]
        self.pc = jmp_address
    
    def jne(self): 
        if self.equal_flag & 0b00000001 == 0:
            reg_num = self.ram[self.pc + 1]
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def jeq(self): 
        if self.equal_flag & 0b00000001 == 1:
            reg_num = self.ram[self.pc + 1]
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def run(self):
        while self.running:
            ir = self.ram[self.pc]
            self.branchtable[ir]()
            if ir & 0b00010000 == 0:
                num_operands = ir >> 6
                increment = num_operands + 1
                self.pc += increment
    

           


            
