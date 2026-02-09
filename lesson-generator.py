import argparse
from datetime import datetime
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
        f.write(f'date = \'{datetime.now().astimezone()}\'\n')
        f.write(f'etz_url = \'\'\n')
        f.write(f'draft = true\n')
        f.write(f'title = \'{row["Name"]}\'\n')
        f.write(f'youtube_id = \'\'\n')
        f.write(f'alternative_recording_urls = []\n')
        f.write(f'fcc_lesson_url = \'{row["Link"]}\'\n')
        f.write(f'type = \'lessons\'\n')
        f.write(f'lesson_type = [\'{row["Lesson type"]}\']\n')
        f.write(f'instructors = [\'Jess\', \'Carmen\', \'Eda\']\n')
        f.write(f'unit = [\'{row["Unit"]}\']\n')
        f.write('+++\n')


if __name__ == '__main__':
    main()