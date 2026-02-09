import argparse
import pandas

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to the CSV file', type=str)
    args = parser.parse_args()
    csv = pandas.read_csv(args.file)
    first = csv.iloc[0].to_dict()
    print(first)



if __name__ == '__main__':
    main()