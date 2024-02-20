import caldav
import icalendar
import requests
import re

# config
from secret import davlogin
from urls import urls


def getdav():
    with caldav.DAVClient(**davlogin) as client:
        my_principal = client.principal()
        try:
            cal = my_principal.calendar("ics")
        except caldav.lib.error.NotFoundError:
            cal = my_principal.make_calendar(name="ics")
        return cal


def getics(url):
    r = requests.get(url)
    r.raise_for_status()
    # print(r.text)
    cal = icalendar.Calendar.from_ical(r.text)
    # for event in cal.walk("VEVENT"):
    #    uid = event["UID"]
    return cal


def getuid(ev):
    dat = ev._get_data()
    cal = icalendar.Calendar.from_ical(dat)
    for event in cal.walk("VEVENT"):
        uids = event["UID"]
        out = []
        for k in re.finditer(r"\([^()]*\)", uids):
            out.append(k.group(0)[4:-3])

        return out


dav = getdav()
uids = []
for x in dav.events():
    uids += getuid(x)
for u in urls:
    for event in getics(u).walk("VEVENT"):
        uid = event["UID"]
        if uid in uids:
            continue
        print(uid, "is new")
        print(event.pop("DTSTAMP", None))
        dav.add_event(**event)
