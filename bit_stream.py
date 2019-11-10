import logging
import sys
from enum import Enum
import binascii

class OpenMode(Enum):
    WRITE = 0
    READ = 1

class BitStream(object):
    """
        Bit-level write and read operations to a file
    """

    __file_object = None
    __byte_buffer = 0
    __idx = 0
    __logger = None
    __open_mode = None

    # Entire file buffer. Only used in OpenMode.READ mode
    __file_buffer = None
    __current_byte_position = 0

    def __init__(self, file_path: str, open_mode: OpenMode):
        """
            Constructor of BitStream. Note: logging level should be set using the appropriate cmd flag (Python3 logging
        --log=INFO/DEBUG/etc)
        :param file_path: string representing the file path to be opened
        :param open_mode: specify weather to read or write to the file
        """

        self.__logger = logging.getLogger(__name__)
        self.__open_mode = open_mode
        rwb = None

        if open_mode == OpenMode.WRITE:
            rwb = 'wb'

        elif open_mode == OpenMode.READ:
            rwb = 'rb'

        else:
            self.__logger.critical('Unexpected Open Mode specified!')

        self.__file_object = open(file_path, rwb)

        if open_mode == OpenMode.READ:
            self.__init_read_buffer()
        self.__logger.debug('BitStream initialized with file {} and mode {}'.format(file_path, open_mode))

    def __init_read_buffer(self):
        """
            Called if OpenMode == READ. It will read the entire content of the file to memory.
        :return:
        """
        self.__file_buffer = self.__file_object.read()
        # print(bin(int.from_bytes(self.__file_buffer, sys.byteorder)))
        # print(binascii.hexlify(self.__file_buffer))
        self.__file_object.close()
        self.__read_byte()

    def flush(self):
        """
            Writes remaining bits to file. Right-padding if necessary.
        :return:
        """
        if self.__open_mode != OpenMode.WRITE:
            self.__logger.critical('OpenMode is not WRITE. Flush not performed.')

        if self.__idx != 0:
            self.__logger.debug('Flushing {} bits of data to file'.format(self.__idx))
            self.__write_byte()

        else:
            self.__logger.debug('Byte buffer was empty. Flushing operation not performed')

    def __write_byte(self):
        """
            Writes byte buffer to file
        :return:
        """
        if self.__open_mode != OpenMode.WRITE:
            self.__logger.critical('OpenMode is not WRITE. __write_byte not performed.')
            return

        if self.__idx == 8:
            self.__file_object.write(self.__byte_buffer.to_bytes(1, byteorder='big'))
            self.__byte_buffer = 0

        # This should only run if self.flush() calls self.__write_byte()
        elif self.__idx < 8:
            bitwise_length = 8 - self.__idx
            self.__byte_buffer = self.__byte_buffer << bitwise_length
            self.__file_object.write(self.__byte_buffer.to_bytes(1, byteorder='big'))

        else:
            self.__logger.debug('__write_byte was called in an unexpected state. Current byte buffer size: {}'.format(self.__idx))

        self.__idx = 0

    def write_bit(self, bit: int):
        """
            Writes one bit to file. Note: the actual content is only written when the buffer has been filled or flush was called.
        :param bit:
        :return:
        """
        if self.__open_mode != OpenMode.WRITE:
            self.__logger.critical('OpenMode is not WRITE. Write_bit not performed.')
            return

        self.__idx = self.__idx + 1

        if bit == 0:
            self.__byte_buffer = self.__byte_buffer << 1

        elif bit == 1:
            self.__byte_buffer = self.__byte_buffer << 1
            self.__byte_buffer = self.__byte_buffer | 1

        else:
            self.__logger.error('Unexpected bit value: {}. Ignoring.'.format(bit))

        if self.__idx == 8:
            self.__write_byte()

    def write_n_bits(self, bits: [int]):
        """
            Writes n bits to the file
        :param bits: list of integers representing the bit sequence
        :return:
        """

        if self.__open_mode != OpenMode.WRITE:
            self.__logger.critical('OpenMode is not WRITE. write_n_bits not performed.')
            return

        for b in bits:
            self.write_bit(b)

    def __read_byte(self):
        """"
            Reads the next byte from buffer
        """

        if self.__current_byte_position >= len(self.__file_buffer):
            self.__logger.info('Reached end of file. Cannot read.')
            self.__byte_buffer = None
            return False

        self.__byte_buffer = self.__file_buffer[self.__current_byte_position]
        # print(binascii.hexlify(self.__file_buffer[self.__current_byte_position]))
        self.__current_byte_position = self.__current_byte_position + 1
        self.__logger.debug('Read one byte from file buffer')
        return True

    def read_bit(self) -> int:
        """
            Reads one bit from file
        :return:
        """
        if self.__open_mode != OpenMode.READ:
            self.__logger.critical('OpenMode is not READ. read_bit not performed.')
            return -1

        if self.__idx == 8:
            # Read next byte from file and update buffer
            # Reset pointer to first bit
            self.__idx = 0
            if not self.__read_byte():
                return -1

        mask = 2**(7 - self.__idx)
        bit = self.__byte_buffer & mask

        self.__idx = self.__idx + 1
        return 1 if bit != 0 else 0

    def read_n_bits(self, num_of_bits: int) -> [int]:
        """
            Reads n bits from the sequence
        :param num_of_bits:
        :return: bit sequence represented as a list of integers (composed of 0's and 1s, obviously)
        """
        lst = []

        for i in range(0, num_of_bits):
            lst.append(self.read_bit())

        return lst

    def close(self):
        """
            Closes file handler and flushes buffer if necessary
        :return:
        """
        if self.__open_mode == OpenMode.WRITE:
            self.flush()

        self.__file_object.close()
