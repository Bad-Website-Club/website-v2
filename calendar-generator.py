import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path
import tomllib


DEFAULT_BASE_URL = "https://badwebsite.club"
DEFAULT_TIMEZONE = "Europe/Vienna"
DEFAULT_DURATION_MINUTES = 60


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bootcamp", help="The bootcamp name", type=str)
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL for lesson links",
        type=str,
    )
    parser.add_argument(
        "--duration-minutes",
        default=DEFAULT_DURATION_MINUTES,
        help="Lesson duration in minutes",
        type=int,
    )
    args = parser.parse_args()

    lesson_dir = Path(f"content/bootcamps/{args.bootcamp}/lessons")
    if not lesson_dir.exists():
        raise FileNotFoundError(f"Lesson directory not found: {lesson_dir}")

    output_dir = Path(f"static/calendars/{args.bootcamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    events = []
    for lesson_file in sorted(lesson_dir.glob("*.md")):
        if not is_dated_lesson_file(lesson_file):
            continue
        event = build_event(lesson_file, args.bootcamp, args.base_url, args.duration_minutes)
        if event is None:
            continue
        write_ics_file(output_dir / f"{lesson_file.stem}.ics", event)
        events.append(event)

    print(f"Wrote {len(events)} lesson calendar files to {output_dir}")


def build_event(lesson_file, bootcamp, base_url, duration_minutes):
    frontmatter = load_frontmatter(lesson_file)
    lesson_date = frontmatter.get("date")
    lesson_title = frontmatter.get("title")
    if not lesson_date or not lesson_title:
        return None

    start_at = datetime.fromisoformat(lesson_date)
    end_at = start_at + timedelta(minutes=duration_minutes)
    lesson_url = f"{base_url.rstrip('/')}/bootcamps/{bootcamp}/lessons/{lesson_file.stem}/"
    return {
        "title": lesson_title,
        "url": lesson_url,
        "start_at": start_at,
        "end_at": end_at,
        "uid": f"{bootcamp}-{lesson_file.stem}@badwebsite.club",
    }


def is_dated_lesson_file(lesson_file):
    try:
        datetime.strptime(lesson_file.stem, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def load_frontmatter(lesson_file):
    text = lesson_file.read_text(encoding="utf-8")
    parts = text.split("+++", 2)
    if len(parts) < 3:
        return {}
    return tomllib.loads(parts[1].strip())


def write_ics_file(output_path, event):
    now_utc = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Bad Website Club//Lesson Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        fold_ical_line(f"UID:{event['uid']}"),
        fold_ical_line(f"DTSTAMP:{now_utc}"),
        fold_ical_line(
            f"DTSTART:{event['start_at'].astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}"
        ),
        fold_ical_line(
            f"DTEND:{event['end_at'].astimezone(UTC).strftime('%Y%m%dT%H%M%SZ')}"
        ),
        fold_ical_line(f"SUMMARY:{escape_ical_text(event['title'])}"),
        fold_ical_line(f"DESCRIPTION:{escape_ical_text(event['url'])}"),
        fold_ical_line(f"LOCATION:{escape_ical_text(event['url'])}"),
        fold_ical_line(f"URL:{event['url']}"),
        "END:VEVENT",
        "END:VCALENDAR",
    ]

    output_path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")


def escape_ical_text(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


def fold_ical_line(line, max_length=75):
    if len(line) <= max_length:
        return line

    chunks = []
    remaining = line
    while len(remaining) > max_length:
        chunks.append(remaining[:max_length])
        remaining = " " + remaining[max_length:]
    chunks.append(remaining)
    return "\r\n".join(chunks)


if __name__ == "__main__":
    main()
