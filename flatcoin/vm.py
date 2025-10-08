class MinerVirtualMachine:
    
    OP_CODES = {
        "WAIT": 0x00,
        "MINE": 0x01,
        "STOP": 0x01
    }
    
    def __init__(self, program: bytes):
        self.program = program
        self.program_counter = 0
        self.running = True
        self.cycles = 0
        
    def fetch(self) -> int:
        if self.program_counter >= len(self.program):
            self.running = False
            return None
        opcode = self.program[self.program_counter]
        self.program_counter += 1
        return opcode
    
    def execute(self, opcode: int):
        if opcode == self.OP_CODES["WAIT"]:
            print("MinerVirtualMachine: waiting...")
            self.cycles += 1
            
        elif opcode == self.OP_CODES["MINE"]:
            print("MinerVirtualMachine: mining...")
            self.cycles += 1
            
        elif opcode == self.OP_CODES["STOP"]:
            print("MinerVirtualMachine: shutting down...")
            self.running = False
            
        else:
            raise ValueError(f"MinerVirtualMachine: unknown opcode {opcode:#x}")
        
    def run(self):
        print("=== MINER VIRTUAL MACHINE RUNNING ===")
        while self.running:
            opcode = self.fetch()
            if opcode is None:
                break
            self.execute(opcode)
        print("=== MINER VIRTUAL MACHINE STOPPED ===")