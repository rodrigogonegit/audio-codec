import struct

from golomb import GolombEncoder
import wave


class Lossy(object):   
    __residual = []
    __encoded = ''
    __list_of_integers = []
    __input_file_path = None
    __output_file_path = None
    __nchannels=2
    __sampwidth=2
    __framerate=44100
    __nframes  =588588
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
            print("Type: ",type(data))
            while data != b'':
                self.__list_of_integers.append((int.from_bytes(data,byteorder="little",signed=True)))
                #print(int.from_bytes(data,byteorder="big",signed=True))
                data = file.readframes(1)

    def __read_ints(self):
        f = open(self.__input_file_path, 'rb')
        byte = f.read(1)

        while byte != b'':
            self.__list_of_integers.append(struct.unpack('b', byte)[0])
            byte = f.read(1)

        f.close()
        # print('UInts read from {}:'.format(self.__input_file_path), self.__list_of_integers)

    def encode(self, m_golomb_factor,q_predict_factor, report_progress_callback=None):
        """
        :param data:
        :param predictor:
        :return:
        """
        o = GolombEncoder(None, self.__output_file_path)
        o.set_padding_mode(False)

        o.write_header(m_golomb_factor)
        
        #ToDo: ainda não aceita isto
        #o.write_header(q_predict_factor)

        

        tmp = []
        result_to_code = int(self.__list_of_integers[0]/q_predict_factor)
        tmp.append(result_to_code*q_predict_factor)
        o.golomb_encode(result_to_code, m_golomb_factor)
        
        for i in range(1, len(self.__list_of_integers)):
            #print(i)
            if report_progress_callback is not None:
                report_progress_callback(i / len(self.__list_of_integers) * 100.0)
            
            result_to_code = int((self.__list_of_integers[i] - tmp[i - 1])/q_predict_factor)
            tmp.append(tmp[i-1]+(result_to_code*q_predict_factor))
            o.golomb_encode(result_to_code, m_golomb_factor)
            
            
            # if i < 20:
            #     print(self.__list_of_integers[i] - self.__list_of_integers[i - 1], ', ', end ='')

        o.close()


    def decode(self, q_predict_factor, report_progress_callback=None):
        """

        :return:
        """
        o = GolombEncoder(self.__input_file_path, self.__output_file_path)
        int_list = o.decode(returnList=True)
        o.close()
        #todo: not wel done 
        output = wave.open(self.__output_file_path, 'wb')
        print(self.__nchannels)
        output.setparams((self.__nchannels, self.__sampwidth, self.__framerate, self.__nframes, self.__comptype, self.__compname))
        
        step = 0
        counter = 0 # refactor
        int_list = [x*q_predict_factor for x in int_list]
        for i in int_list:
            if report_progress_callback is not None:
                report_progress_callback(counter/len(int_list)*100.0)

            step = step + i
            counter += 1
            output.writeframes(step.to_bytes(4,byteorder="little",signed="True"))
            # output.write(bytes(step))




