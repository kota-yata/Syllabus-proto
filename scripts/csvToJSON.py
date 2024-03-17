import csv
import json
import re


def extract_day(value):
    day_match = re.search(r'([月火水木金土日])', value)
    return day_match.group() if day_match else None


def extract_numeric(value):
    numeric_part = re.search(r'\d+', value)
    return int(numeric_part.group()) if numeric_part else None


def convert_csv_to_json(csv_file_path, output_json_path):
    json_data = []

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        row: dict
        for row in reader:
            # Split styles with commas
            styles = [{"style": style.strip()} for style in row['style'].split(',')]

            # Process schedules with error handling
            schedules = []
            days = row['day'].split(',')
            periods = row['period'].split(',')

            for day_period in zip(days, periods):
                day_value = extract_day(day_period[0].strip())
                period_value = extract_numeric(day_period[1].strip()) if day_period[1] else None
                schedules.append({"day": day_value, "period": str(period_value)})

            # Extract numeric part from credit
            credit = extract_numeric(row['credit'])

            # Modify 'term' based on the contents
            if '学期後半' in row['term']:
                term_value = '後半'
            elif '学期前半' in row['term']:
                term_value = '前半'
            else:
                term_value = row['term']

            # Modify 'field' based on the contents
            field_value = row['field'].replace('基盤科目-', '')

            # If the field is '基盤科目-共通科目', update to '基盤-共通科目'
            if field_value == '基盤科目-共通科目':
                field_value = '基盤-共通科目'

            # Create JSON structure
            entry = {
                "sort_id": f"X{row['index']}",
                "subject_name": row['subject_name'],
                "term": term_value,
                "about": row['about'],
                "method": row['method'],
                "place": row['place'],
                "lang": row['lang'],
                "year": int(row['year']),
                "semester": row['semester'],
                "is_giga": row['is_giga'] == 'True',
                "url": row['url'],
                "fields": [
                    {
                        "faculty": row['faculty'],
                        "field": field_value,
                        "credit": credit
                    }
                ],
                "schedules": schedules,
                "staffs": [
                    {
                        "staff_name": row['staff_name']
                    }
                ],
                "styles": styles
            }

            # Append to the list
            json_data.append(entry)

    # Output as JSON
    with open(output_json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(json_data, jsonfile, ensure_ascii=False, indent=2)

    print(f"Conversion completed. JSON data saved to {output_json_path}")


# Replace 'your_csv_file.csv' and 'output.json' with your actual file paths
convert_csv_to_json('syllabus_data.csv', 'output.json')
