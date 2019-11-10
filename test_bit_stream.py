import inspect

from bit_stream import BitStream, OpenMode
import hashlib


def test_write_bit():
    """
        Tests BitStream.write_bit(). BitStream.Flush() is also tested as we are writing less than 8 bits
    :return:
    """
    output_file_path = 'write_bit_test'
    file = BitStream(output_file_path, OpenMode.WRITE)
    file.write_bit(1)
    file.close()

    file_read = open(output_file_path, 'rb')

    if hashlib.md5(file_read.read()).hexdigest() == '8d39dd7eef115ea6975446ef4082951f':
        print('write_bit: Passed!')
    else:
        print('write_bit: FAILED!')

    file_read.close()


def test_write_14_bits():
    """
        It aims to test the padding when the buffer is not full and there already is one byte written.
    :return:
    """
    output_file_path = 'write_14_bit_test'
    file = BitStream(output_file_path, OpenMode.WRITE)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(0)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(0)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(1)
    file.write_bit(1)
    # 14 calls to write_bit
    file.close()

    file_read = open(output_file_path, 'rb')

    if hashlib.md5(file_read.read()).hexdigest() == 'df349ae692f79d86f3aeed3a42547576':
        print('write_14_bit: Passed!')
    else:
        print('write_14_bit: FAILED!')


def test_write_n_bits():
    bits = [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1]

    output_file_path = 'write_n_bits'
    file = BitStream(output_file_path, OpenMode.WRITE)
    file.write_n_bits(bits)
    file.close()

    file_read = open(output_file_path, 'rb')

    if hashlib.md5(file_read.read()).hexdigest() == '284f75f95c70ca126a2ab1b7ee63d7b4':
        print('write_bit: Passed!')
    else:
        print('write_bit: FAILED!')

    file_read.close()

def test_read_one_bit():
    output_file_path = 'write_n_bits'

    file = BitStream(output_file_path, OpenMode.READ)
    file.close()
    bit = file.read_bit()
    bit_sequence = []

    while bit != -1:
        bit = file.read_bit()
        bit_sequence.append(bit)


test_write_bit()
test_write_14_bits()
test_write_n_bits()
test_read_one_bit()
