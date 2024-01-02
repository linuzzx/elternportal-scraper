## By Linusx -- https://linusx.is-a.dev/

from datetime import datetime
import scraper
from bs4 import BeautifulSoup
import os


# Get HTML from Page

pageurl = 'drucken/liste/schulaufgaben'
page = scraper.get_page(pageurl)

# Find the table

soup = BeautifulSoup(page,'html.parser')
                     
table = soup.find('table',attrs={'class' : 'table2'})

# for getting the data

data = []

HTML_data = table.find_all("tr")[1:]
 
for element in HTML_data:
    sub_data = []
    for sub_element in element:
        try:
            sub_data.append(sub_element.get_text())
        except:
            continue
    data.append(sub_data)

for element in data:
    if element[0].replace(".","").isnumeric() == True:
        element.remove("\xa0")
        if datetime.strptime(element[0], '%d.%m.%Y') > datetime.now():
            print(element[0],element[1],"\n")

try:
    import icalendar
except ImportError as e:
    pass  # module doesn't exist, deal with it.
finally:
    cal = icalendar.Calendar()
    
    for element in data:
        if element[0].replace(".","").isnumeric() == True:
            eventtime = datetime.strptime(element[0], '%d.%m.%Y')
            if eventtime > datetime.now():
                event = icalendar.Event()
                event.add('summary', element[1])
                event.add('dtstart', eventtime.date())
                event.add('dtend', eventtime.date())
                
                cal.add_component(event)
    
    if not os.path.isdir('files'):
        os.mkdir('files')
    
    with open(os.path.join('files','events.ics'),'wb') as f:
        f.write(cal.to_ical())
    

