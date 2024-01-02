# By Linusx -- https://linusx.is-a.dev/


subject_dict = {
    'E': 'Englisch', 'F': 'Frz', 'C': 'Chemie', 'Inf': 'Info', 'D': 'Deutsch', 'Ph': 'Physik', 'M': 'Mathe', 'B': 'Bio', 'G': 'Gesch.', 'Ku': 'Kunst', 'Mu': 'Musik'
}


def get_timetable():
    import scraper
    from bs4 import BeautifulSoup

    # Get HTML from Page

    pageurl = 'service/stundenplan'
    # Returns the html page on which the timetable is
    page = scraper.get_page(pageurl)

    # Find the table

    soup = BeautifulSoup(page, 'html.parser')

    table = soup.find(
        'table', attrs={'class': 'table table-condensed table-bordered'})

    # Convert to 2d list

    tablelist = []

    for tr in table.findAll('tr'):
        td = tr.findAll('td')
        tdtext = []
        for x in td:
            tdtext.append(x.text)
        tablelist.append(tdtext)

    return tablelist


def extract_numbers_from_string(string):
    import re

    # Find all numbers in the string
    numbers = re.findall(r'\d+', string)
    # Convert the numbers to integers
    numbers = [int(x) for x in numbers]
    return numbers


def format_table_data(table):
    # Format Data
    table[0][0] = 'Zeit'

    # Timestamps
    for row in table[1:]:
        # Remove Numbering, Spaces, Unnessesary Spaces and 0s
        row[0] = row[0][row[0].index(
            '.')+1:].replace('.', ':').replace(' ', '').replace('08', '8').replace('09', '9')

    # Subjects
    for row in table[1:]:
        for i, cell in enumerate(row[1:]):
            if cell == ' ':
                row[i + 1] = ''
            elif 'Sm' in cell:
                row[i + 1] = 'Sport'
            elif 'Eth' in cell:
                row[i + 1] = 'Ethik' + ' ' + \
                    "%03d"%extract_numbers_from_string(cell)[0]
            elif 'Ku' in cell:
                row[i + 1] = 'Kunst' + ' ' + \
                    "%03d"%extract_numbers_from_string(cell)[0]
            elif 'Druckgrafik' in cell:
                row[i + 1] = 'Kurs' + ' ' + \
                    "%03d"%extract_numbers_from_string(cell)[1]
            elif 'Geo' in cell:
                row[i + 1] = 'Geo' + ' ' + \
                    "%03d"%extract_numbers_from_string(cell)[-1]
            else:
                # Try to get the long name of the subject and format to 'SubjectName RoomNumber'
                if cell[:-4] in subject_dict.keys():
                    row[i + 1] = subject_dict[cell[:-4]] + ' ' + cell[-4:-1]
                else:
                    row[i + 1] = cell[:-4] + ' ' + cell[-4:-1]

    table[8][3] = 'MSK 066'
    
    # Remove unneeded rows

    for row in table[1:]:
        if all(x == '' for x in row[1:]) and not '12:50-13:30' in row[0]:
            table.remove(row)
            
    # Add space to every cell for spacing
    
    for row in range(len(table)):
        for cell in range(len(table[row])):
            if table[row][cell] != '':
                table[row][cell] = ' ' + table[row][cell]

    return table


def gen_csv(table):
    import csv
    import os
    
    if not os.path.isdir('files'):
        os.mkdir('files')

    # Create CSV
    with open(os.path.join('files','timetable.csv'), 'w', newline='') as f:
        # Create a CSV writer
        writer = csv.writer(f, delimiter=';')

        # Write the data to the CSV file
        for row in table:
            writer.writerow(row)


if __name__ == '__main__':
    
    
    gen_csv(format_table_data(get_timetable()))
