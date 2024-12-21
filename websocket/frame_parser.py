class FrameParser:
    def __init__(self):
        self.reset()

    def reset(self):
        self.buffer = b""
        self.state = "HEADER"
        self.is_frame_complete = False
        self.fin = 1
        self.rsv = []
        self.opcode = 0
        self.mask_flag = False
        self.masking_key = b""
        self.paylod_len = 0
        self.payload = b""

    def parse(self, buffer):
        self.buffer += buffer
        if self.state == "HEADER":
            self.parse_header()
        elif self.state == "LEN":
            self.parse_len()
        elif self.state == "MASK":
            self.parse_mask()
        elif self.state == "PAYLOAD":
            self.parse_payload()
        elif self.state == "COMPLETE":
            self.is_message_complete = True

    def parse_header(self):
        if len(self.buffer) < 2:
            return

        header = int.from_bytes(self.buffer, "big", signed=False)
        byte1 = (header & 0xFF00) >> 8
        self.fin = byte1 & 0b1000_0000 == 0x80
        self.rsv.append(byte1 & 0b0100_0000 == 0x40)
        self.rsv.append(byte1 & 0b0010_0000 == 0x20)
        self.rsv.append(byte1 & 0b0001_0000 == 0x10)
        self.opcode = byte1 & 0x0F

        byte2 = header & 0xFF
        self.mask_flag = (byte2 >> 7 & 1) == 1
        self.payload_len = byte2 & 0b01111111
        self.buffer = b""
        if self.payload_len < 126:
            self.state = "MASK"
        else:
            self.state = "LEN"

    def parse_len(self):
        if self.payload_len == 126:
            if len(self.buffer) < 2:
                return
            else:
                self.payload_len = int.from_bytes(self.buffer, "big", signed=False)
                self.state = "MASK"
                self.buffer = b""
        elif self.payload_len == 127:
            if len(self.buffer) < 6:
                return
            else:
                self.payload_len = int.from_bytes(self.buffer, "big", signed=False)
                self.state = "MASK"
                self.buffer = b""

    def parse_payload(self):
        if len(self.buffer) < self.payload_len:
            return
        self.payload = self.unmask()
        self.state = "COMPLETE"
        self.is_frame_complete = True

    def unmask(self):
        return bytes(b ^ self.mask[j % 4] for j, b in enumerate(self.buffer))

    def parse_mask(self):
        if len(self.buffer) < 4:
            return
        self.mask = self.buffer
        self.buffer = b""
        self.state = "PAYLOAD"

    def get_message(self):
        retval = {}
        match self.opcode:
            case 0x1:
                retval["type"] = "text"
                retval["content"] = self.payload.decode()
            case 0x2:
                retval["type"] = "bytes"
                retval["content"] = self.payload
        return retval
