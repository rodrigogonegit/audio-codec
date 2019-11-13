import struct

from golomb import GolombEncoder


class PredictiveCoding(object):
    __residual = []
    __encoded = ''
    __list_of_integers = []
    __input_file_path = None
    __output_file_path = None

    def __init__(self, input_file_path, output_file_path):
        """
        :param input_file_path:
        :param output_file_path:
        """
        self.__input_file_path = input_file_path
        self.__output_file_path = output_file_path

        self.__read_ints()

    def __read_ints(self):
        f = open(self.__input_file_path, 'rb')
        byte = f.read(1)

        while byte != b'':
            self.__list_of_integers.append(struct.unpack('b', byte)[0])
            byte = f.read(1)

        f.close()
        # print('UInts read from {}:'.format(self.__input_file_path), self.__list_of_integers)

    def encode(self, m_golomb_factor, report_progress_callback=None):
        """
        :param data:
        :param predictor:
        :return:
        """
        o = GolombEncoder(None, self.__output_file_path)
        o.set_padding_mode(False)

        o.write_header(m_golomb_factor)
        o.golomb_encode(self.__list_of_integers[0], m_golomb_factor)

        for i in range(1, len(self.__list_of_integers)):

            if report_progress_callback is not None:
                report_progress_callback(i / len(self.__list_of_integers) * 100.0)

            o.golomb_encode(self.__list_of_integers[i] - self.__list_of_integers[i - 1], m_golomb_factor)
            # if i < 20:
            #     print(self.__list_of_integers[i] - self.__list_of_integers[i - 1], ', ', end ='')

        o.close()

    def decode(self, report_progress_callback=None):
        """

        :return:
        """
        o = GolombEncoder(self.__input_file_path, self.__output_file_path)
        int_list = o.decode(returnList=True)
        o.close()

        with open(self.__output_file_path, 'wb') as output:
            step = 0
            counter = 0 # refactor
            for i in int_list:

                if report_progress_callback is not None:
                    report_progress_callback(counter/len(int_list)*100.0)

                step = step + i
                counter += 1
                # print('step', step)
                output.write(struct.pack('b', step))
