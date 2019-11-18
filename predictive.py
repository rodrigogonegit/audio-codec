import struct

from golomb import GolombEncoder
import wave


class PredictiveCoding(object):
    __residual = []
    __encoded = ''
    __list_of_integers_channel1 = []
    __list_of_integers_channel2 = []
    __input_file_path = None
    __output_file_path = None
    __nchannels=2
    __sampwidth=2
    __framerate=44100
    __nframes  =911988
    __comptype ='NONE'
    __compname ='not compressed'

    def __init__(self, input_file_path, output_file_path):
        """
        :param input_file_path:
        :param output_file_path:
        """
        self.__input_file_path = input_file_path
        self.__output_file_path = output_file_path
        if(self.__input_file_path.endswith('.wav')):
            self.__readWaveFile()
        else:
            self.__read_ints()

    def __readWaveFile(self):
        with wave.open(self.__input_file_path, 'rb') as file:
            # Read input file params
            self.__nchannels, self.__sampwidth, self.__framerate, self.__nframes, self.__comptype, self.__compname =  file.getparams()

            bit_depth = self.__sampwidth/self.__nchannels*8

            if bit_depth % 8 != 0:
                print('Bit depth is not a multiple of 8. Ma come?!')
                return

            bit_depth = int(bit_depth)
            print("Input file:\t", self.__input_file_path)
            print("Bit-depth:\t", bit_depth)
            print("No Channels:\t", self.__nchannels)
            print("Sample Width:\t", self.__sampwidth)
            print("Framerate:\t", self.__framerate)
            print("No frames:\t", self.__nframes)
            print("Comp Type:\t", self.__comptype)
            print("Comp Name:\t", self.__compname)
            # self.__list_of_integers.append(bit_depth)
            # self.__list_of_integers.append(nchannels)
            # self.__list_of_integers.append(nchannels)
            # self.__list_of_integers.append(sampwidth)
            # self.__list_of_integers.append(framerate)
            # self.__list_of_integers.append(nframes)
            # self.__list_of_integers.append(comptype)
            # self.__list_of_integers.append(compname)
            # Open target file with same params (conversion of channel or similar would be here)
            data = file.readframes(1)
            #print("Type: ",type(data))
            while data != b'':
                self.__list_of_integers_channel1.append((int.from_bytes(data[0:self.__nchannels],byteorder="little",signed=True)))
                self.__list_of_integers_channel2.append((int.from_bytes(data[self.__nchannels:],byteorder="little",signed=True)))
                # print("channnel 1: ",(int.from_bytes(data[0:self.__nchannels],byteorder="little",signed=True)) )
                # print("channel 2: ", (int.from_bytes(data[self.__nchannels:],byteorder="little",signed=True)))

                #print(int.from_bytes(data,byteorder="big",signed=True))
                data = file.readframes(1)

    def __read_ints(self):
        f = open(self.__input_file_path, 'rb')
        byte = f.read(1)

        while byte != b'':
            self.__list_of_integers_channel1.append(struct.unpack('b', byte)[0])
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
        o.golomb_encode(self.__list_of_integers_channel1[0], m_golomb_factor)
        o.golomb_encode(self.__list_of_integers_channel2[0], m_golomb_factor)
        for i in range(1, len(self.__list_of_integers_channel1)):
            #print(i)
            if report_progress_callback is not None:
                report_progress_callback(i / len(self.__list_of_integers_channel1) * 100.0)
            
            o.golomb_encode(self.__list_of_integers_channel1[i] - self.__list_of_integers_channel1[i - 1], m_golomb_factor)
            o.golomb_encode(self.__list_of_integers_channel2[i] - self.__list_of_integers_channel2[i - 1], m_golomb_factor)
            # if i < 20:
            #     print(self.__list_of_integers[i] - self.__list_of_integers[i - 1], ', ', end ='')

        o.close()
    def setwav(self,input):
        with wave.open(input, 'rb') as file:
            # Read input file params
            self.__nchannels, self.__sampwidth, self.__framerate, self.__nframes, self.__comptype, self.__compname =  file.getparams()

            bit_depth = self.__sampwidth/self.__nchannels*8

        
    def decode(self, report_progress_callback=None):
        """

        :return:
        """
        o = GolombEncoder(self.__input_file_path, self.__output_file_path)
        int_list = o.decode(returnList=True)
        o.close()
        #todo: not wel done 
        output = wave.open(self.__output_file_path, 'wb')
        
        output.setparams((self.__nchannels, self.__sampwidth, self.__framerate, self.__nframes, self.__comptype, self.__compname))

        int_list_channel1 = int_list[::2]
        int_list_channel2 = int_list[1::2]
        
        step_channel1 = 0
        step_channel2 = 0
        counter = 0 # refactor
        for i in range(0,len(int_list_channel1)):
            if report_progress_callback is not None:
                report_progress_callback(counter/len(int_list)*100.0)
            

            step_channel1 = step_channel1 + int_list_channel1[i]
            step_channel2 = step_channel2 + int_list_channel2[i]
            bytes_channel1 = step_channel1.to_bytes(2,byteorder="little",signed="True")
            bytes_channel2 = step_channel2.to_bytes(2,byteorder="little",signed="True")
            bytes_to_write = bytes_channel1 + bytes_channel2
            counter += 1
            #print('step', step)
            output.writeframes(bytes_to_write)
            # output.write(bytes(step))
