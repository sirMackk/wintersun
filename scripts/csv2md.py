import fileinput
import sys
import csv


def process_line(csv_line):
    # replace <!!!> with newline - done
    # format date
    headers = ['no', 'mys1', 'title', 'desc', 'slug', 'contents', 'created', 'updated', 'tra1', 'tra2']
    reader = csv.reader(csv_line, quoting=csv.QUOTE_ALL, quotechar='|')
    row = [r[0] for r in reader if r and r != ['', '']]

    entry = dict(zip(headers, row))
    with open('posts/' + entry['slug'] + '.md', 'wb') as f:
        f.write("""Title: {title}
Date: {date}
Template: Post
Tags:

{contents}""".format(
    title=entry['title'],
    date=entry['created'],
    contents=entry['contents'].replace('<!!!>', "\n")))


def main():
    try:
        for input in fileinput.input():
            process_line(input)

    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
