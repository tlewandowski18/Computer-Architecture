"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xf4
        self.pc = 0
       
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

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            ir = self.ram[self.pc]
            # #LDI Instruction Handler
            if ir == 0b10000010:
                #Register num
                operand_a = self.ram_read(self.pc + 1)
                #Constant Value
                operand_b = self.ram_read(self.pc + 2)
                self.reg[operand_a] = operand_b
                #increase pc by 3 (opcode and two operands)
                self.pc += 3
            # #PRN Instruction Handler
            elif ir == 0b01000111:
                operand_a = self.ram_read(self.pc + 1)
                value = self.reg[operand_a]
                print(value)
                self.pc += 2
            #MULT Instruction Handler
            elif ir == 0b10100010:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu("MULT", reg_a, reg_b)
                self.pc += 3
            #MULT2Print Instruction Handler
            elif ir == 0b10100000:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu("ADD", reg_a, reg_b)
                self.pc += 3
            #PUSH Instruction Handler
            elif ir == 0b01000101:
                #decrement the stack pointer
                self.reg[7] -= 1
                #pull reg index from memory
                reg_num = self.ram[self.pc + 1]
                #pull value from reg
                value = self.reg[reg_num]
                #Store at top of stack
                top_of_stack_addr = self.reg[7]
                self.ram[top_of_stack_addr] = value
                self.pc += 2
            #POP INSTRUCTION Handler
            elif ir == 0b01000110:
                #find stop of stack and copy value
                top_of_stack_addr = self.reg[7]
                value = self.ram[top_of_stack_addr]
                #find reg spot and store the value at that place in reg
                reg_num = self.ram[self.pc + 1]
                self.reg[reg_num] = value
                #increment stack pointer
                self.reg[7] += 1
                self.pc += 2
            #CALL Instruction Handler
            elif ir == 0b01010000:
                #save return address to Stack
                ret_addr = self.pc + 2
                self.reg[7] -= 1
                self.ram[self.reg[7]] = ret_addr

                # Call the subroutine
                reg_num = self.ram[self.pc + 1]
                self.pc = self.reg[reg_num]
            #RET Instruction Handler
            elif ir == 0b00010001:
                top_stack = self.reg[7]
                ret_address = self.ram[top_stack]
                self.reg[7] += 1
                self.pc = ret_addr
            #HLT Instruction Handler
            elif ir == 1:
                running = False

           


            
