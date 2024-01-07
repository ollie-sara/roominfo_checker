import datetime, locale, werkzeug, Room, json
werkzeug.cached_property = werkzeug.utils.cached_property
from robobrowser import RoboBrowser
from asyncio import sleep, run
import logging
import sys

logging.basicConfig(filename='roominfo.log', level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

strnow = lambda : datetime.datetime.now().isoformat()

def get_name_from_url(url):
    url = url.split('?')[1]
    tuples = url.split('&')[-3:]
    name = ''
    for tup in tuples:
        name += f'{tup.split("=")[1]} '
    name = name.strip().split(" ")
    return name[0], " ".join(name[1:])


def get_availability(browser):
    rows = browser.find_all('table')[1].select('tr')[1:]
    checkDay = [0] * 5
    availability = [[0] * 60 for i in range(5)]
    availability_trimmed = [[0] * 48 for i in range(5)]
    currentRow = 0
    for row in rows:
        if currentRow%4 == 0:
            columns = row.select('td')[2:]
        else:
            columns = row.select('td')[1:]
        it = 0
        for i in range(5):
            if checkDay[i] != 0:
                checkDay[i] -= 1
            else:
                # Explicitly skip all bookings marked "study rooms"
                if True:
                    allow_blocked = 'rbeitsplätze' in str(columns[it].find('font'))
                    for o in range(int(columns[it]['rowspan'])):
                        availability[i][currentRow + o] = 1 if allow_blocked or columns[it]['bgcolor'] == '#99cc99' else 0
                    checkDay[i] = int(columns[it]['rowspan']) - 1
                it += 1
                availability_trimmed[i] = availability[i][4:52]
        currentRow += 1
    return availability_trimmed

async def update_json():
    logging.info(strnow() + "\tUpdating json")
    browser = RoboBrowser(parser='html.parser',
                          user_agent='Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0')
    browser.open('http://www.rauminfo.ethz.ch/IndexPre.do')

    room_links = [x['href'] for x in browser.select('.tabcell-distance a') if 'RauminfoPre.do' in str(x['href'])]
    today = datetime.datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    monday_thisweek = today - datetime.timedelta(days=today.weekday())
    monday_nextweek = monday_thisweek + datetime.timedelta(weeks=1)

    jsonData = {"datetime_thisweek": monday_thisweek.isoformat(),
                "datetime_nextweek": monday_nextweek.isoformat(),
                "datetime_now": strnow(),
                "buildings": {}}

    for room in room_links:
        try:
            await sleep(0.5)
            browser.open('http://www.rauminfo.ethz.ch/' + room)
            name = get_name_from_url(room)
            form = browser.get_forms()[1]
            checkable = form['rektoratInListe'].value == 'true' and form['raumInRaumgruppe'].value == 'true'
            if not checkable:
                logging.info(strnow() + "\tSkipping room " + " ".join(name))
                continue

            daystr = monday_thisweek.strftime('%d')
            if daystr[0] == '0':
                form['tag'].value = daystr[1]
            else:
                form['tag'].value = daystr
            form['monat'].value = monday_thisweek.strftime('%b')
            form['jahr'].value = monday_thisweek.strftime('%Y')
            browser.submit_form(form)
            availability_thisweek = get_availability(browser)
            browser.back()
            daystr = monday_nextweek.strftime('%d')
            if daystr[0] == '0':
                form['tag'].value = daystr[1]
            else:
                form['tag'].value = daystr
            form['monat'].value = monday_nextweek.strftime('%b')
            form['jahr'].value = monday_nextweek.strftime('%Y')
            browser.submit_form(form)
            availability_nextweek = get_availability(browser)
            roomObj = Room.Room(name[1], availability_thisweek, availability_nextweek)
            if name[0] not in jsonData.get("buildings"):
                jsonData.get("buildings").update({name[0]: []})
            jsonData.get("buildings").get(name[0]).append(roomObj.__dict__)
            logging.info(strnow() + "\tAdded room " + " ".join(name))
        except Exception as e:
            logging.info(strnow() + f'\tError occurred with room {" ".join(name)} on line {sys.exc_info()[-1].tb_lineno}:\n__ ' + str(e))
            logging.info("__ Therefore, skipping room " + " ".join(name))

    with open('docs/_site/data/data.json', 'w') as file:
        json.dump(jsonData, file, ensure_ascii=False)
    logging.info(strnow() + "\tSuccessfully updated json")


run(update_json())