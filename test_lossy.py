import argparse
import hashlib
import os

from golomb import GolombEncoder
from lossy import Lossy

parser = argparse.ArgumentParser()
parser.add_argument('operation', choices=['enc', 'dec'], help='"enc" for encoding "dec" for decoding')
parser.add_argument('--m_param', type=int, help='the m value parameter to be used')
parser.add_argument('--q_param', type=int, help='the q value parameter to be used')
parser.add_argument('input_file', help='the input file to be processed')
parser.add_argument('output_file', help='the resulting file')
args = parser.parse_args()

def main():
    def callback_progress(percentage):
        print('\rPercentage:{:.2f}%'.format(percentage), end='')

    in_file_size = os.stat(args.input_file).st_size
    print('Input file:\t\t', args.input_file)
    print('Input file size:\t', in_file_size)
    print('Encoded output file:\t', args.output_file + '_encoded')
    print('Decoded output file:\t', args.output_file + '_decoded')

    print('Encoding...')    
    p = Lossy(args.input_file, args.output_file + "_encoded")
    p.encode(args.m_param,args.q_param, report_progress_callback=callback_progress)
    print('')

    print('Decodind...')
    d = Lossy(args.output_file + "_encoded", args.output_file + '_decoded')
    d.setwav(args.input_file)
    d.decode(args.q_param,report_progress_callback=callback_progress)
    print('')
    enc_file_size = os.stat(args.output_file + '_encoded').st_size

    print('Encoded file is {} bytes, {:.2f}% of the input file.'.format(in_file_size, enc_file_size / in_file_size*100.0))

    input_file_hash = None
    decoded_file_hash = None

    with open(args.input_file, 'rb') as f:
        input_file_hash = hashlib.md5(f.read()).hexdigest()

    with open(args.input_file, 'rb') as f:
        decoded_file_hash = hashlib.md5(f.read()).hexdigest()

    print('Input file hash and decode file hashes match?', input_file_hash == decoded_file_hash)
main() 

#python test_predictive.py enc wav-samples/sample04.wav out --m_param 200000000