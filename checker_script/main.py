import datetime, locale, logging, json, sys
from asyncio import sleep, run
from os import getcwd

import requests

logging.basicConfig(filename="roominfo.log", level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler())

strnow = lambda: datetime.datetime.now().isoformat()


def get_availability(allocation_data):
    # Mo-Fr 08:00-20:00
    availability_trimmed = [[1] * 12 * 4 for _ in range(5)]
    for allocation_block in allocation_data:
        start = datetime.datetime.fromisoformat(allocation_block["date_from"])
        end = datetime.datetime.fromisoformat(allocation_block["date_to"])
        if start.weekday() >= 5:
            continue
        start_index = start.hour * 4 + start.minute // 15 - (8 * 4)
        end_index = end.hour * 4 + end.minute // 15 - (8 * 4)
        for i in range(start_index, end_index):
            if i < 0 or i >= 12 * 4:
                continue
            availability_trimmed[start.weekday()][i] = 0
    return availability_trimmed


def roominfo_request(path, extra_params={}):
    params = "&".join([f"path={path}"] + [f"{k}={v}" for k, v in extra_params.items()])
    logging.info(strnow() + f"\tRequesting https://ethz.ch/bin/ethz/roominfo?{params}")
    return requests.get(
        f"https://ethz.ch/bin/ethz/roominfo?{params}",
        headers={"User-Agent": "Mozilla/5.0"},
    ).json()


async def update_json():
    logging.info(strnow() + "\tUpdating json")

    rooms = [
        r
        for r in roominfo_request("/rooms")
        if r["orgunit"][0]["orgunit"] == "09188"  # "Unterrichtsräume Rektorat"
        and r["typecode"] in ["3430", "3420"]  # Lecture halls, seminar/course rooms
    ]

    today = datetime.datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    monday_thisweek = today - datetime.timedelta(days=today.weekday())

    next_mondays = [
        (monday_thisweek + datetime.timedelta(weeks=i)).isoformat() for i in range(3)
    ]

    jsonData = {
        "datetime_thisweek": next_mondays[0],
        "datetime_nextweek": next_mondays[1],
        "datetime_now": strnow(),
        "buildings": {},
    }

    for room in rooms:
        try:
            await sleep(0.2)
            r_building, r_floor, r_room = room["building"], room["floor"], room["room"]
            room_groups = roominfo_request(
                "/roomgroup", {"building": r_building, "floor": r_floor, "room": r_room}
            )
            room_name = f"{r_building} {r_floor} {r_room}"
            if 114 not in room_groups["roomGroups"]:
                logging.info(strnow() + "\tSkipping room " + room_name)
                continue

            room_availabilites = []
            for week in range(2):
                start = next_mondays[week].split("T")[0]
                end = next_mondays[week + 1].split("T")[0]
                allocation_data = roominfo_request(
                    f"/rooms/{room_name}/allocations", {"from": start, "to": end}
                )
                room_availabilites.append(get_availability(allocation_data))

            if r_building not in jsonData["buildings"]:
                jsonData["buildings"][r_building] = []

            jsonData["buildings"].get(r_building).append(
                {
                    "name": f"{r_floor} {r_room}",
                    "availability_thisweek": room_availabilites[0],
                    "availability_nextweek": room_availabilites[1],
                }
            )
            logging.info(strnow() + "\tAdded room " + room_name)
        except Exception as e:
            logging.info(
                strnow()
                + f"\tError occurred with room {room_name} on line {sys.exc_info()[-1].tb_lineno}:\n__ "
                + str(e)
            )
            logging.info("__ Therefore, skipping room " + room_name)

    with open("docs/data/data.json", "w") as file:
        json.dump(jsonData, file, ensure_ascii=False)
        logging.info(strnow() + f"\tSaved to path: {getcwd()}/docs/data/data.json")
    logging.info(strnow() + f"\tSuccessfully updated json for {len(rooms)} rooms")


locale.setlocale(locale.LC_ALL, "de_CH")
run(update_json())
