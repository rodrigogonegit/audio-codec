import math
from bit_stream import BitStream, OpenMode
import binascii
import os

class GolombEncoder(object):
    """
        Implements the Golomb encoder
    """
    __input_file = None
    __output_file = None
    __input_file_size = -1

    def __init__(self, input_file_path, output_file_path):
        """

        :param input_file_path:
        :param output_file_path:
        """

        # Open file handlers
        if input_file_path != None:
            self.__input_file = BitStream(input_file_path, OpenMode.READ)

        self.__output_file = BitStream(output_file_path, OpenMode.WRITE)

        if input_file_path != None:
            self.__input_file_size = os.stat(input_file_path).st_size

    def close(self):
        """

        :return:
        """
        # Open file handlers
        if self.__input_file != None:
            self.__input_file.close()

        self.__output_file.close()

    def write_header(self, m_value):
        self.__output_file.write_int(m_value, 4)

    def encode(self, m, report_progress_callback=None):
        """
        :return:
        """
        self.__output_file.set_padding_mode(False)
        # Write header to output file. TODO: write header specification
        # self.__output_file.write_int(m, 4)
        self.write_header(m)

        i = self.__input_file.read_int(1)
        counter = 0.0

        while i != None:

            if report_progress_callback:
                report_progress_callback(counter/self.__input_file_size*100.0)
            # ...
            self.golomb_encode(i, m)
            i = self.__input_file.read_int(1)
            counter = counter + 1

        self.__input_file.close()
        self.__output_file.close()

    def golomb_encode(self, input, m):
        # print('Before:', input)
        if input > 0:
            input = input * 2

        elif input < 0:
            input = (input * -2) - 1

        # print('After:', input)
        b = int(math.ceil(math.log(m, 2)))
        # calculation of quotient
        q = int(math.floor(input / m))
        # calculation of
        r = input - q * m
        # Calculate the fist bits with the use o q parameter, with unitary code
        # example: q = 3 -> first = 1110
        str_repr = ''

        for i in range(q):
            self.__output_file.write_bit(1)
            str_repr += '1'

        self.__output_file.write_bit(0)
        str_repr += '0'
        encode = int(math.pow(2, b) - m)

        # Caso o valor de r seja menor que (2^b)-m vamos usar b-1 bits para representar esses valores
        if (r < encode):
            using_bits = b - 1
            binary_representation_with_fixed_len = ("{0:0" + str(using_bits) + "b}").format(r)

            # print('BIN REPR:', str_repr  + binary_representation_with_fixed_len)
            for c in binary_representation_with_fixed_len:
                self.__output_file.write_bit(int(c))

        # Caso o contrario utiliza-se b bits de r+(2^b)-m para representar os restantes
        else:

            using_bits = b
            x = int(r + math.pow(2, b) - m)

            binary_representation_with_fixed_len = ("{0:0" + str(using_bits) + "b}").format(x)
            # print('BIN REPR:', str_repr + binary_representation_with_fixed_len)

            for c in binary_representation_with_fixed_len:
                self.__output_file.write_bit(int(c))

    def set_padding_mode(self, with_zeros=True):
        self.__output_file.set_padding_mode(with_zeros)

    def decode(self, report_progress_callback=None, returnList=False):
        """
        :return:
        """
        # Open file handlers
        self.__output_file.set_padding_mode(True)
        m = self.__input_file.read_int(4)
        b = math.ceil(math.log(m, 2))  # ceil ( log2 (m) )
        decode = int(math.pow(2, b) - m)

        counter = 0.0

        rtn_list = []

        while True:
            num_of_ones = 0

            if report_progress_callback:
                report_progress_callback(counter/self.__input_file_size*100.0)

            bit = self.__input_file.read_bit()

            while bit == 1:
                num_of_ones = num_of_ones + 1
                bit = self.__input_file.read_bit()

            # If this happened, we have reached the end of the stream without a unary terminating 0
            if bit == -1:
                break

            num_of_bits_to_read = b - 1

            x = self.__input_file.read_n_bits(num_of_bits_to_read)
            int_x = int(x, 2)
            result = -1

            if int_x < decode:
                result = num_of_ones * m + int_x

            else:
                int_x = int_x * 2 + self.__input_file.read_bit()
                result = num_of_ones * m + int_x - decode

            if result % 2 == 0: #Positive
                result = int( result / 2 )

            else:
                result = int( (result + 1) / 2 * -1 )

            # print(result)
            if not returnList:
                self.__output_file.write_int(result, 1)

            else:
                rtn_list.append(result)

            counter += 1

        self.__input_file.close()
        self.__output_file.close()

        if returnList:
            return rtn_list
