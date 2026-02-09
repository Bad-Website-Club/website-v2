import argparse
import pandas

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to the CSV file', type=str)
    parser.add_argument('bootcamp', help='The bootcamp name', type=str)
    args = parser.parse_args()
    csv = pandas.read_csv(args.file)
    first = csv.iloc[0].to_dict()
    generate_lesson_from_row(first, args.bootcamp)

def generate_lesson_from_row(row, bootcamp):
    filename = f'./content/bootcamps/{bootcamp}/lessons/{row["Lesson number"]}.md'
    with open(filename, 'w+', encoding='utf-8') as f:
        f.write('+++\n')
        f.write('+++\n')


if __name__ == '__main__':
    main()