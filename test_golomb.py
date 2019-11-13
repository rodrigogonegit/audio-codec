import argparse
from golomb import GolombEncoder

parser = argparse.ArgumentParser()
parser.add_argument('operation', choices=['enc', 'dec'], help='"enc" for encoding "dec" for decoding')
parser.add_argument('--m_param', type=int, help='the m value parameter to be used')
parser.add_argument('input_file', help='the input file to be processed')
parser.add_argument('output_file', help='the resulting file')
args = parser.parse_args()


def main():
    g = GolombEncoder(args.input_file, args.output_file)

    def callback_progress(percentage):
        print('\rPercentage:{:.2f}'.format(percentage), end='')

    if args.operation.lower() == 'enc':

        if not args.m_param:
            print('[ERROR] You need to specify the m parameter for the encoding operation')
            return

        g.encode(args.m_param, report_progress_callback=callback_progress)

    else:
        g.decode()

    g.close()


main()
