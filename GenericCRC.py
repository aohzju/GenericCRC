class GenericCRC():
    """An arbitrary-length (>=8) CRC calculator
       Usage:
            Consruct a crc object and then call its Calculate() method. To see
        the check value of the CRC, call Check() method
    """

    def __init__(self, name, crcLen, poly, initCRC=0, refin=False, refout=False, xorout=0):
        """ Construct a CRC64 calculator. The polynomial is assumed to be the normal form polynomial
            - name: The name of the CRC. Informative, not used for calculating the CRC digest
            - crcLen: The number of CRC bits, must be >= 8
            - poly: The CRC polynomial in normal representation.
            - initCRC: the initial CRC value to use
            - refin: Input reflected
            - refout: Output reflected
            - xorout: The value to be XOR-ed with the final CRC.
        """

        self.name = name
        self.crcLen = crcLen
        self.refin = refin
        self.refout = refout
        self.xorout = xorout
        if self.refin:
            self.initCRC = GenericCRC.reverseInt(initCRC, crcLen)
            self.poly = GenericCRC.reverseInt(poly, crcLen)
            self.genCRCTbl_refin()
        else:
            self.initCRC = initCRC
            self.poly = poly
            self.genCRCTbl_nrefin()

    @classmethod
    def reverseInt(cls, v, nBits):
        """Reverse an int with nBits"""
        sbin = bin(v)
        sbin = sbin[2:] #discard the leading "0b"
        n = len(sbin)
        if n > nBits:
            print("Value out of range of", nBits, "bits")
            return None
        s = '0'*(nBits-len(sbin)) + sbin
        
        return int(s[::-1], 2)

    
    def genCRCTbl_nrefin(self):
        """Generate CRC look-up table for the case that the input bytes
           are not reflected
        """
        tbl = [None]*256

        for byte in range(0, 256):
            crc = byte << (self.crcLen - 8)
            for i in range(0, 8):
                c = (crc << 1) & ((1 << self.crcLen) - 1)
                if (crc >> (self.crcLen-1)) != 0:
                    crc = c ^ self.poly
                else:
                    crc = c

            tbl[byte] = crc

        self.crcTbl = tbl

    def genCRCTbl_refin(self):
        """Generate CRC look-up table for the case that the input bytes
           are reflected
        """

        tbl = [None]*256

        for byte in range(0, 256):
            crc = byte
            for i in range(0, 8):
                c = crc >> 1
                if (crc & 0x1) != 0:
                    crc = c ^ self.poly
                else:
                    crc = c

            tbl[byte] = crc

        self.crcTbl = tbl

    def calculate_nrefin(self, message):
        """Compute CRC digest for a message, input not reflected
         - message: a byte array message
         - Return: CRC digest
        """
        if (type(message) != bytes) and (type(message) != bytearray):
            print("Error: expecting bytes or bytearray input")
            return None

        crc = self.initCRC #0xFFFFFFFF #initial crc
        for byte in message:
            pos = (crc >> (self.crcLen - 8)) ^ byte
            crc = (crc << 8) & ((1 << self.crcLen) - 1)
            crc = crc ^ self.crcTbl[pos]

        return crc

    def calculate_refin(self, message):
        """Compute CRC digest for a message, input reflected
         - message: a byte array message
         - Return: CRC digest
        """
        if (type(message) != bytes) and (type(message) != bytearray):
            print("Error: expecting bytes or bytearray input")
            return None

        crc = self.initCRC #0xFFFFFFFF #initial crc
        for byte in message:
            pos = (crc ^ byte) & 0xFF
            crc = crc >> 8
            crc = crc ^ self.crcTbl[pos]

        return crc

    #The public API for calculating CRC64:
    def Calculate(self, message):
        """Calculate CRC digest"""
        if self.refin:
            crc = self.calculate_refin(message)
        else:
            crc = self.calculate_nrefin(message)
        
        if self.refout ^ self.refin:
            crc = GenericCRC.reverseInt(crc, self.crcLen) #reflect output
        return crc ^ self.xorout    #final XOR

    def Check(self):
        """Calculate CRC for the message '123456789'"""
        msg = "123456789".encode("utf-8")
        return self.Calculate(msg)
        
#===========================================================================================================================================
#Run some tests below:

if __name__ == "__main__":
    """ See CRC catalogue and parameters at https://reveng.sourceforge.io/crc-catalogue/all.htm"""

    crc64_ecma = GenericCRC("CRC-64/ECMA-182", crcLen=64,  poly=0x42f0e1eba9ea3693) #Construct a CRC64 object
    crc = crc64_ecma.Check()                 
    expected = 0x6c40df5f0b497347
    print(f'CRC64/ECMA-182 check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc64_iso = GenericCRC("CRC-64/GO-ISO", crcLen=64, poly=0x000000000000001B, initCRC=0xFFFFFFFFFFFFFFFF, refin=True, refout=True, xorout=0xFFFFFFFFFFFFFFFF)
    crc = crc64_iso.Check()
    expected = 0xb90956c775a41001
    print(f'CRC64/GO-ISO check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc40_gsm = GenericCRC("CRC40/GSM", crcLen=40, poly=0x0004820009, initCRC=0, refin=False, refout=False, xorout=0xFFFFFFFFFF)
    crc = crc40_gsm.Check()
    expected = 0xd4164fc646
    print(f'CRC40/GSM check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc32c = GenericCRC("CRC32C", crcLen=32, poly=0x1EDC6F41, initCRC=0xFFFFFFFF, refin=True, refout=True, xorout=0xFFFFFFFF)
    crc = crc32c.Check()
    expected = 0xe3069283
    print(f'CRC32C check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc32_cksum = GenericCRC("CRC32/CKSUM", crcLen=32, poly=0x04c11db7, initCRC=0, refin=False, refout=False, xorout=0xFFFFFFFF)
    crc = crc32_cksum.Check()
    expected = 0x765e7680
    print(f'CRC32/CKSUM check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc31_philips = GenericCRC("CRC31/PHILIPS", crcLen=31, poly=0x04c11db7, initCRC=0x7fffffff, refin=False, refout=False, xorout=0x7fffffff)
    crc = crc31_philips.Check()
    expected = 0x0ce9e46c
    print(f'CRC31/PHILIPS check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc30_cdma = GenericCRC("CRC31/CDMA", crcLen=30, poly=0x2030b9c7, initCRC=0x3fffffff, refin=False, refout=False, xorout=0x3fffffff)
    crc = crc30_cdma.Check()
    expected = 0x04c34abf
    print(f'CRC30/CDMA check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc24_lteb = GenericCRC("CRC24/LTE_B", crcLen=24, poly=0x800063)
    crc = crc24_lteb.Check()
    expected = 0x23ef52
    print(f'CRC24/LTE_B check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    
    crc24_openpgp = GenericCRC("CRC24/OPENPGP", crcLen=24, poly=0x864cfb, initCRC=0xb704ce)
    crc = crc24_openpgp.Check()
    expected = 0x21cf02 
    print(f'CRC24/OPENPGP check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')


    crc16_t10dif = GenericCRC("CRC16/T10DIF", crcLen=16, poly=0x8bb7)
    crc = crc16_t10dif.Check()
    expected = 0xd0db
    print(f'CRC16/T10DIF check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc16_tms37157 = GenericCRC("CRC-16/TMS37157", crcLen=16, poly=0x1021, initCRC=0x89ec, refin=True, refout=True)
    crc = crc16_tms37157.Check()
    expected = 0x26b1
    print(f'CRC16/TMS37157 check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc8_wcdma = GenericCRC("CRC8/WCDMA", crcLen=8, poly=0x9b, initCRC=0x00, refin=True, refout=True)
    crc = crc8_wcdma.Check()
    expected = 0x25
    print(f'CRC8/WCDMA check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')

    crc8_smbus = GenericCRC("CRC8/SMBUS", crcLen=8, poly=0x07)
    crc = crc8_smbus.Check()
    expected = 0xf4
    print(f'CRC8/SMBUS check is {crc:#x}. Expected: {expected:#x}. Error={crc-expected}')


