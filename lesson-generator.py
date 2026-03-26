import argparse
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
import pandas

BASE_SITE_URL = "https://badwebsite.club"
CALENDAR_TIMEZONE = "UTC"
CALENDAR_START_HOUR = 15
CALENDAR_DURATION_MINUTES = 60


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to the CSV file', type=str)
    parser.add_argument('bootcamp', help='The bootcamp name', type=str)
    args = parser.parse_args()
    csv = pandas.read_csv(args.file)
    columns = get_column_lookup(csv.columns)
    date_covered_column = require_column(
        columns,
        ["Date covered", "Date Covered", "Date"],
        'Expected a date column such as "Date covered" or "Date" in CSV',
    )

    grouped_rows = []
    for date_value, group in csv.groupby(date_covered_column, sort=True):
        grouped_rows.append(
            {
                "date_value": date_value,
                "group": group,
                "base_title": infer_lesson_name(group, columns),
            }
        )

    lesson_titles = build_group_titles(grouped_rows)
    for grouped_row, lesson_title in zip(grouped_rows, lesson_titles):
        generate_lesson_from_group(
            grouped_row["date_value"],
            grouped_row["group"],
            args.bootcamp,
            columns,
            lesson_title,
        )


def generate_lesson_from_group(date_value, group, bootcamp, columns, lesson_name):
    date_dt = datetime.strptime(str(date_value), "%Y-%m-%d")
    date_slug = date_dt.strftime("%Y-%m-%d")
    filename = f'./content/bootcamps/{bootcamp}/lessons/{date_slug}.md'
    lesson_url = f"{BASE_SITE_URL}/bootcamps/{bootcamp}/lessons/{date_slug}/"
    calendar_ics_url = f"/calendars/{bootcamp}-lessons.ics"
    calendar_google_url = build_google_calendar_url(
        lesson_name,
        lesson_url,
        date_dt,
    )
    lesson_types = unique_ordered(
        normalize_lesson_type(value)
        for value in group[require_column(columns, ["Lesson type"])].tolist()
    )
    units = unique_ordered(
        normalize_text(value) for value in group[require_column(columns, ["Unit"])].tolist()
    )
    links = unique_ordered(
        normalize_text(value) for value in group[require_column(columns, ["Link"])].tolist()
    )
    with open(filename, 'w+', encoding='utf-8') as f:
        f.write('+++\n')
        lesson_start = date_dt.replace(
            hour=CALENDAR_START_HOUR,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=timezone.utc,
        )
        f.write(f'date = \'{lesson_start.isoformat(timespec="seconds")}\'\n')
        f.write(f'etz_url = \'\'\n')
        f.write(f'draft = true\n')
        f.write(f'title = \'{lesson_name}\'\n')
        f.write(f'youtube_id = \'\'\n')
        f.write(f'alternative_recording_urls = []\n')
        f.write(f'fcc_lesson_url = \'{links[0] if links else ""}\'\n')
        f.write(f'fcc_lesson_urls = {format_array(links)}\n')
        f.write(f'calendar_ics_url = \'{calendar_ics_url}\'\n')
        f.write(f'calendar_google_url = \'{calendar_google_url}\'\n')
        f.write(f'type = \'lessons\'\n')
        f.write(f'lesson_type = {format_array(lesson_types)}\n')
        f.write(f'instructors = [\'Jess\', \'Carmen\', \'Eda\']\n')
        f.write(f'unit = {format_array(units)}\n')
        f.write('+++\n')
        f.write('\n')
        f.write('## FreeCodeCamp Lessons\n\n')
        for row in sort_group_rows(group):
            lesson_number = get_lesson_number(row, columns)
            lesson_title = get_row_value(row, columns, "Name")
            lesson_url = get_row_value(row, columns, "Link")
            lesson_type = get_row_value(row, columns, "Lesson type")
            label = f'{lesson_number}. {lesson_title}' if lesson_number else lesson_title
            if lesson_type:
                label = f'{label} ({lesson_type})'
            if lesson_url:
                f.write(f'- [{escape_markdown(label)}]({lesson_url})\n')
            else:
                f.write(f'- {escape_markdown(label)}\n')


def infer_lesson_name(group, columns):
    topics = unique_ordered(
        normalize_text(value) for value in group[require_column(columns, ["Topic"])].tolist()
    )
    units = unique_ordered(
        normalize_text(value) for value in group[require_column(columns, ["Unit"])].tolist()
    )
    name_prefix = infer_common_name_prefix(group[require_column(columns, ["Name"])].tolist())
    if name_prefix:
        return name_prefix
    if len(topics) == 1 and len(units) == 1:
        return f"{topics[0]} - {units[0]}"
    if len(topics) == 1:
        return f"{topics[0]} - Mixed Units"
    if 1 < len(topics) <= 3:
        return " / ".join(topics)
    return f"Mixed Topics ({len(topics)})"


def build_group_titles(grouped_rows):
    title_counts = {}
    for grouped_row in grouped_rows:
        base_title = grouped_row["base_title"]
        title_counts[base_title] = title_counts.get(base_title, 0) + 1

    title_indexes = {}
    lesson_titles = []
    for grouped_row in grouped_rows:
        base_title = grouped_row["base_title"]
        if title_counts[base_title] == 1:
            lesson_titles.append(base_title)
            continue

        title_indexes[base_title] = title_indexes.get(base_title, 0) + 1
        lesson_titles.append(f'{base_title} Part {title_indexes[base_title]}')

    return lesson_titles


def build_google_calendar_url(title, lesson_url, date_dt):
    start_at = date_dt.replace(
        hour=CALENDAR_START_HOUR,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=timezone.utc,
    )
    end_at = start_at + timedelta(minutes=CALENDAR_DURATION_MINUTES)
    params = {
        "action": "TEMPLATE",
        "text": title,
        "dates": f"{format_google_datetime(start_at)}/{format_google_datetime(end_at)}",
        "details": lesson_url,
        "location": lesson_url,
        "ctz": CALENDAR_TIMEZONE,
    }
    return f"https://calendar.google.com/calendar/render?{urlencode(params)}"


def format_google_datetime(value):
    return value.strftime("%Y%m%dT%H%M%S")


def infer_common_name_prefix(names):
    normalized_names = [normalize_text(name) for name in names if normalize_text(name)]
    if not normalized_names:
        return ""

    prefixes = []
    for name in normalized_names:
        if ":" in name:
            prefixes.append(name.split(":", 1)[0].strip())
        else:
            prefixes.append(name)

    unique_prefixes = unique_ordered(prefixes)
    if len(unique_prefixes) == 1:
        return unique_prefixes[0]

    return ""


def get_column_lookup(columns):
    return {normalize_column_name(column): column for column in columns}


def normalize_column_name(name):
    return normalize_text(name).casefold()


def require_column(columns, candidates, error_message=None):
    for candidate in candidates:
        match = columns.get(normalize_column_name(candidate))
        if match:
            return match
    if "Lesson number" in candidates:
        fallback = infer_lesson_number_column(columns)
        if fallback:
            return fallback
    if error_message:
        raise ValueError(error_message)
    raise ValueError(f"Missing required column. Tried: {', '.join(candidates)}")


def get_row_value(row, columns, candidate):
    column_name = require_column(columns, [candidate])
    return normalize_text(row.get(column_name))


def get_lesson_number(row, columns):
    raw_value = get_row_value(row, columns, "Lesson number")
    if not raw_value:
        return ""
    try:
        number = float(raw_value)
    except ValueError:
        return raw_value
    if number.is_integer():
        return str(int(number))
    return raw_value


def infer_lesson_number_column(columns):
    for column in columns.values():
        normalized = normalize_column_name(column)
        if normalized in {"topic", "unit", "name", "link", "lesson type", "week", "day", "date"}:
            continue
        if normalized.isdigit():
            return column
    return None


def normalize_lesson_type(value):
    text = normalize_text(value)
    if not text:
        return ""
    return text.lower().replace(" ", "-")


def normalize_text(value):
    if value is None or pandas.isna(value):
        return ""
    text = str(value).strip()
    return text


def unique_ordered(values):
    seen = set()
    ordered = []
    for value in values:
        if not value:
            continue
        if value not in seen:
            ordered.append(value)
            seen.add(value)
    return ordered


def format_array(values):
    escaped = [value.replace("'", "\\'") for value in values]
    quoted = [f"'{value}'" for value in escaped]
    return f"[{', '.join(quoted)}]"


def sort_group_rows(group):
    rows = group.to_dict("records")
    return sorted(rows, key=lesson_sort_key)


def lesson_sort_key(row):
    raw_number = normalize_text(row.get("Lesson number"))
    if not raw_number:
        raw_number = normalize_text(row.get("1"))
    try:
        return (0, int(float(raw_number)))
    except ValueError:
        return (1, raw_number)


def escape_markdown(text):
    return text.replace("[", "\\[").replace("]", "\\]")


if __name__ == '__main__':
    main()
