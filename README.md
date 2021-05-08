# GenericCRC
A generic CRC implementation in Python, which supports arbitrary CRC size.

---

Class GenericCRC is a generic CRC implementation supporting arbitrary CRC sizes (>=8). 

## Usage
Use Generic CRC in 2 steps:
1. Construct a GenericCRC object. The construction of GenericCRC:<br><br>
    ```
    GenericCRC(name, crcLen, poly, initCRC=0, refin=False, refout=False, xorout=0)
    ```
    - **name**: The name of the CRC. Informative, not used by CRC calculation.
    - **crcLen**: Size of the CRC. For example, 32 for CRC32
    - **poly**: The ***normal representation*** of the generation polynomial of the CRC
    - **initCRC**: The value used to initialize the CRC value / register
    - **refin**: If this value is True, each input byte is reflected before being used in the calculation. Reflected means that the bits of the input byte are used in reverse order.
    - **refout**:  If this value is True, the final CRC value is reflected before being returned. The reflection is done over the whole CRC value.
    - **xorout**: This value is xored to the final CRC value before being returned.
    For example, to calculate CRC32C:<br>
    ```
    crc32c = GenericCRC("CRC32C", crcLen=32, poly=0x1EDC6F41, initCRC=0xFFFFFFFF, refin=True, refout=True, xorout=0xFFFFFFFF)<br>
    ```
2. Call the object's Calculate() method on the message whose CRC is to be calculated. For example, to calculate CRC32C for messeage "Hello, World!":<br>
    ```
    msg = "Hello, World".encode('utf-8') <br>
    crc = crc32c.Calculate(msg)
    ```
  Note, the method Calculate expects an input of bytes or bytearray type.<br>
  You can also call the **Check()** method to see the check value of the constructed CRC object. The check value is the CRC value of input string "123456789" encoded in utf-8.
  
## Sanity Check
GenericCRC.py has sanity checks. Directly run "python GenericCRC.py" to see the test results. All test vectors are from https://reveng.sourceforge.io/crc-catalogue/all.htm
