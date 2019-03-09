#!/usr/bin/python
# encoding: utf-8

import datetime
import sys
from workflow import Workflow3, web, ICON_CLOCK, ICON_ERROR, ICON_INFO


# Get departure time
# https://stackoverflow.com/questions/18039625/converting-asp-net-json-date-into-python-datetime
def parse_date(datestring):
    timepart = datestring.split("(")[1].split(")")[0]
    milliseconds = int(timepart[:-5])
    hours = int(timepart[-5:]) / 100
    time = milliseconds / 1000
    dt = datetime.datetime.utcfromtimestamp(time + hours * 3600)
    return dt


def get_stop_departures(wf, stop_id, response):
    buses = []
    # Show current time
    stop_name = ""
    stops = wf.cached_data("tcat_all_stops", get_stop_list, max_age=60 * 60 * 24)
    for stop in stops:
        if stop["StopId"] == int(stop_id):
            stop_name = stop["Name"]
            break
    dt_now = datetime.datetime.now()
    wf.add_item(title=u"%s, Now %s" % (stop_name, dt_now.strftime("%H:%M")), subtitle=u"%s" % dt_now.strftime("%B %-d, %Y, %A"), icon=ICON_INFO)
    # Show departure time
    stop_departure = response.json()[0]
    route_directions = stop_departure["RouteDirections"]
    for route_direction in route_directions:
        route_id = route_direction["RouteId"]
        direction = route_direction["Direction"]
        is_done = route_direction["IsDone"]
        if not is_done:
            departures = route_direction["Departures"]
            for departure in departures:
                if departure["SDT"]:
                    internet_service_desc = departure["Trip"]["InternetServiceDesc"]
                    edt = parse_date(departure["EDT"])
                    sdt = parse_date(departure["SDT"])
                    buses.append({
                        "RouteId": route_id,
                        "Direction": direction,
                        "InternetServiceDesc": internet_service_desc,
                        "SDT": sdt,
                        "EDT": edt,
                        })
    # Sort results by EDT
    buses = sorted(buses, key=lambda k: k["EDT"])
    for bus in buses:
        # Calculate estimated arrival time
        time_delta = bus["EDT"] - dt_now
        time_delta_minutes, time_delta_seconds = divmod(time_delta.days * 24 * 60 * 60 + time_delta.seconds, 60)
        time_delta_hours, time_delta_minutes = divmod(time_delta_minutes, 60)
        if time_delta.days >= 0:
            text_minutes = "minutes" if time_delta_minutes > 1 else "minute"
            text_hours = "hours" if time_delta_hours > 1 else "hour"
            # Construct display item
            title_prefix = u"Route %d, SDT %s, EDT %s, " % (bus["RouteId"], bus["SDT"].strftime("%H:%M"), bus["EDT"].strftime("%H:%M"))
            arg_prefix = u"The next route %d bus will arrive in " % bus["RouteId"]
            title_suffix = u""
            if time_delta_hours > 0:
                title_suffix = u"%d %s %d %s" % (time_delta_hours, text_hours, time_delta_minutes, text_minutes)
            else:
                title_suffix = u"%d %s" % (time_delta_minutes, text_minutes)
            if bus["InternetServiceDesc"]:
                subtitle = u"%s, %s" % (bus["InternetServiceDesc"], bus["Direction"])
            else:
                subtitle = u"%s" % bus["Direction"]
            # Add to the list of results for Alfred
            wf.add_item(
                title=title_prefix + title_suffix,
                subtitle=subtitle,
                valid=True,
                arg=arg_prefix + title_suffix,
                icon=ICON_CLOCK
                )


# Get all stops
def get_stop_list():
    response = web.get("https://realtimetcatbus.availtec.com/InfoPoint/rest/Stops/GetAllStops")
    response.raise_for_status()
    return response.json()


def get_all_stops(wf, query):
    outputs = [[], []]  # Priority lists
    stops = wf.cached_data("tcat_all_stops", get_stop_list, max_age=60 * 60 * 24)
    # Add matching stops to priority lists
    for stop in stops:
        if stop["Name"].lower().startswith(query.lower()):
            outputs[0].append(stop)
        elif query.lower() in stop["Name"].lower():
            outputs[1].append(stop)
    # Add to the lists of results for Alfred
    if len(outputs[0]) + len(outputs[1]) == 0:
        wf.add_item(title=u"Error", subtitle=u"Stop \"%s\" does not exist, or there is no service today" % query, icon=ICON_ERROR)
    else:
        wf.add_item(title=u"Instruction", subtitle=u"Select a stop and press Tab key to see the schedule" , icon=ICON_INFO)
        for i in range(len(outputs)):
            for stop in outputs[i]:
                subtitle_suffix = u"" if not stop["IsTimePoint"] else u" \U0001F557" 
                wf.add_item(
                    title=u"[%d] %s" % (stop["StopId"], stop["Name"]),
                    subtitle=u"%s" % stop["Description"] + subtitle_suffix,
                    arg=stop["StopId"],
                    icon="/Applications/Maps.app",
                    icontype="fileicon",
                    autocomplete=stop["StopId"]
                    )


def main(wf):
    query = " ".join(wf.args)
    valid_stop_id = False
    # First check whether the query string is a valid stop ID
    if query.isdigit() and int(query) >= 100 and int(query) < 7000:
        response = web.get("https://realtimetcatbus.availtec.com/InfoPoint/rest/StopDepartures/Get/%d" % int(query))
        response.raise_for_status()
        # Parse the JSON
        if len(response.json()) != 0:
            valid_stop_id = True
    if valid_stop_id:  # Show departure time for the stop
        get_stop_departures(wf, query, response)
    else:  # Search for stops
        get_all_stops(wf, query)
    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3(update_settings={
        "github_slug": "maobowen/tcat-alfred-workflow",
        "frequency": 7
        })
    if wf.update_available:
        wf.add_item(
            title=u"New version available",
            subtitle=u"Action this item to install the update",
            autocomplete="workflow:update",
            icon=ICON_INFO
            )
    sys.exit(wf.run(main))
