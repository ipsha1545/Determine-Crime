from collections import Counter
import logging, requests

logging.basicConfig(level=logging.DEBUG)
from spyne import Application, srpc, ServiceBase, \
    Integer, Unicode
from spyne import Iterable
from spyne.protocol.http import HttpRpc
import json
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
import requests, regex, re
from datetime import datetime, time
from address import AddressParser, Address
import timestring


class Determinecrime(ServiceBase):
    @srpc(float, float, float, _returns=Iterable(Unicode))
    def checkcrime(lat, lon, radius):
        output = {"total_crime": 0,"the_most_dangerous_streets":[],
                   "crime_type_count": {},

                   'event_time_count': {
                       "12:01am-3am": 0, "3:01am-6am": 0, "6:01am-9am": 0, "9:01am-12noon": 0, "12:01pm-3pm": 0,
                       "3:01pm-6pm": 0,
                       "6:01pm-9pm": 0, "9:01pm-12midnight": 0}
                   }


        URL = "https://api.spotcrime.com/crimes.json"
        data = {'lat': lat, 'lon': lon, 'radius': radius, 'key': '.'}
        a = requests.get(URL, params=data)
        # yield a.json()
        data1 = a.json()


        for n in data1["crimes"]:
            output["total_crime"]+= 1
        #yield output

        for n in data1["crimes"]:
         if n["type"] in output['crime_type_count']:
            output['crime_type_count'][n['type']] += 1
         else:
            output['crime_type_count'][n['type']] = 1
        #yield output

        for n in data1["crimes"]:
            q1 = n["date"]
            p = q1.split(' ')
            time1 = p[1]
            ampm = p[2]
            part = time1.split(':')
            hour = part[0]
            min = part[1]
            # print min
            # print hour
            # print ampm

            if ((hour == "12" and min != "00" and ampm == "AM") or ((hour == "01" or hour == "02") and ampm == "AM") or (
                                hour == "03" and min == "00" and ampm == "AM")):
                output['event_time_count']["12:01am-3am"] += 1

            elif ((hour == "03" and min != "00" and ampm == "AM") or ((hour == "04" or hour == "05") and ampm == "AM") or (
                                hour == "06" and min == "00" and ampm == "AM")):
                output['event_time_count']["3:01am-6am"] += 1

            elif ((hour == "06" and min != "00" and ampm == "AM") or ((hour == "07" or hour == "08") and ampm == "AM") or (
                                hour == "09" and min == "00" and ampm == "AM")):
                output['event_time_count']["6:01am-9am"] += 1

            elif ((hour == "09" and min != "00" and ampm == "AM") or ((hour == "11" or hour == "10") and ampm == "AM") or (
                                hour == "12" and min == "00" and ampm == "PM")):
                output['event_time_count']["9:01am-12noon"] += 1


            elif ((hour == "12" and min != "00" and ampm == "PM") or ((hour == "02" or hour == "01") and ampm == "PM") or (
                                hour == "03" and min == "00" and ampm == "PM")):
                output['event_time_count']["12:01pm-3pm"] += 1

            elif ((hour == "03" and min != "00" and ampm == "PM") or ((hour == "05" or hour == "04") and ampm == "PM") or (
                                hour == "06" and min == "00" and ampm == "PM")):
                output['event_time_count']["3:01pm-6pm"] += 1

            elif ((hour == "06" and min != "00" and ampm == "PM") or ((hour == "07" or hour == "08") and ampm == "PM") or (
                                hour == "09" and min == "00" and ampm == "PM")):
                output['event_time_count']["6:01pm-9pm"] += 1
            else:
                output['event_time_count']["9:01pm-12midnight"] += 1

        #yield output

        addresslist = []
        for i in range(50):
            totaldict = data1["crimes"][i]
            addressdict = totaldict['address']
            addresslist.append(addressdict)
        #print addresslist

        # print all addesses
        newstreetlist = []
        for i in addresslist:
            ap = AddressParser()
            address = ap.parse_address(i)
            a = "{} {}".format(address.street, address.street_suffix)
            newstreetlist.append(a)
        #print newstreetlist


        # find all with & in between
        substreet = []
        for s in newstreetlist:
            joint = re.findall("[\w.\s] {1,20}&[\w.\s] {1,20}", s)
            substreet.append(joint)
        print substreet

        totaladdresslist = []
        for i in substreet:
            previous = re.compile(r"&(.*)")
            matches = re.findall(previous, ''.join(i))
            totaladdresslist.append(matches)
            later = re.compile(r"(.*)&")
            matches2 = re.findall(later, ''.join(i))
            totaladdresslist.append(matches2)
        #print totaladdresslist



        list2 = [x for x in newstreetlist if x != []]  # remove []

        # list 2 has all the individual addresses so chanage elements into string
        list3 = []
        for i in list2:
            addinstr = ''.join(i)
        list3.append(addinstr)
        # print list3 #it has the streets of intersection in string in list
        mergelists = list3 + newstreetlist
        # print mergelists,len(mergelists)


        for i in mergelists:
            if regex.findall("[\w.\s*]{1,20}&[\w.\s*]{1,20}", i):
               mergelists.remove(i)
        for i in mergelists:
            if regex.findall("[\w.\s*]{1,20}&[\w.\s*]{1,20}", i):
               mergelists.remove(i)
        print mergelists,len(mergelists)


        #convert into dict with corresponding value as total numbers

        addresscounter = {}

        for n in data1["crimes"]:
            if not n["address"] in addresscounter:
             addresscounter[str(n["address"])] = 1
        else:
             addresscounter[str(n["address"])] += 1
        #print addresscounter

        streetcounter = {}
        for o in mergelists:
            streetcounter[o] = streetcounter.get(o, 0) + 1
        #print streetcounter

        cou = dict()
        timelist = []
        for j in timelist:
            cou[j] = cou.get(j,0) + 1

        mostthree = []
        dangerous = Counter(streetcounter)
        dangerous.most_common()
        for k, v in dangerous.most_common(3):
         output["the_most_dangerous_streets"].append(k)
        yield output







        # str_time = datetime.datetime.strptime(data1["crimes"][1]["date"],"%m/%j/%y %H:%M").time()
        # datetime.time(0,12)
        # yield str_time


application = Application([Determinecrime],
                              tns='spyne.abc',
                              in_protocol=HttpRpc(validator='soft'),
                              out_protocol=JsonDocument()
                         )

if __name__ == '__main__':
        # You can use any Wsgi server. Here, we chose
        # Python's built-in wsgi server but you're not
        # supposed to use it in production.
    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 7000, wsgi_app)
    server.serve_forever()
