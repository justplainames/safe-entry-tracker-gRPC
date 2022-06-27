from concurrent import futures
import logging
from turtle import pos

import grpc
import safeEntry_pb2
import safeEntry_pb2_grpc
import csv
import pandas as pd
import datetime
import time
import threading


to_notify = {}
affected_locations = []


class SafeEntry(safeEntry_pb2_grpc.SafeEntryServicer):

    # Self Check In
    def CheckIn(self, request, context):
        global affected_locations
        checkin_message = safeEntry_pb2.Reply()
        checkin_message.message = f'Name: {request.name}\nNRIC: {request.nric}\nLocation: {request.location}\nCheck In: {request.checkin}'
        flag = 0
        for i in affected_locations:
            if i[0] == request.location:
                flag = 1
                break
        checkin_entry = [request.name, request.nric,
                         request.location, request.checkin, '-', 1, request.id, 0]
        print(checkin_entry)

        # Save data in csv file
        file = open('safeEntry.csv', 'a', newline='')
        csv_writer = csv.writer(file)
        csv_writer.writerow(checkin_entry)
        file.close()

        df = pd.read_csv("safeEntry.csv", header=None)

        if flag == 1:
            return safeEntry_pb2.Reply(message="You have just checked in an area visited by a covid positive case in past 14 days")
        return safeEntry_pb2.Reply(message="Check in successful")

    # Self Check Out
    def CheckOut(self, request, context):
        checkout_message = safeEntry_pb2.Reply()
        checkout_message.message = f'Name: {request.name}\nNRIC: {request.nric}\nLocation: {request.location}\nCheck In: {request.checkin}\nCheck Out: {request.checkout}'

        r = csv.reader(open('safeEntry.csv'))
        data = list(r)
        print(request.checkout)

        # Update checkout time in csv file
        for row in data:
            match_id = row[6]

            if match_id == request.id:
                row[4] = request.checkout

                file = open('safeEntry.csv', 'w', newline='')
                csv_writer = csv.writer(file)
                csv_writer.writerows(data)
                file.close()

        return checkout_message

    # Group Check In
    def GroupCheckIn(self, request_iterator, context):
        groupcheckin_message = safeEntry_pb2.DelayedReply()
        i = 0
        global affected_locations

        flag = 0
        for request in request_iterator:
            for i in affected_locations:
                if i[0] == request.location:
                    flag = 1
                    break
            groupcheckin_message.request.append(request)
            groupcheckin_entry = [request.name, request.nric, request.location,
                                  request.checkin, '-', request.groupnumber, request.id, 0]
            print(groupcheckin_entry)
            if i == 0:
                groupcheckin_message.message = f'Name: {request.name}\nNRIC: {request.nric}\nLocation: {request.location}\nCheck In: {request.checkin}\nGroup Number: {request.groupnumber}'
                i = i + 1

            #  Save data in csv file
            file = open('safeEntry.csv', 'a', newline='')
            csv_writer = csv.writer(file)
            csv_writer.writerow(groupcheckin_entry)
            file.close()
        if flag == 1:
            groupcheckin_message.message += "\nYour group have just checked in an area visited by a covid positive case in past 14 days\n\n"
        return groupcheckin_message

    # Group Check Out
    def GroupCheckOut(self, request, context):

        groupcheckout_message = safeEntry_pb2.Reply()
        groupcheckout_message.message = f'Name: {request.name}\nNRIC: {request.nric}\nLocation: {request.location}\nCheck In: {request.checkin}\nCheck Out: {request.checkout}\nGroup Number: {request.groupnumber}'

        r = csv.reader(open('safeEntry.csv'))
        data = list(r)

        # Update checkout time in csv file
        for row in data:
            match_id = row[6]

            if match_id == request.id:
                row[4] = request.checkout

                file = open('safeEntry.csv', 'w', newline='')
                csv_writer = csv.writer(file)
                csv_writer.writerows(data)
                file.close()

        return groupcheckout_message

    # Self Check In
    def HistoryListing(self, request, context):
        file = open('safeEntry.csv')
        csvreader = csv.reader(file)
        data = list(csvreader)
        file.close()
        historylisting_message = safeEntry_pb2.Reply()

        for row in reversed(data):
            existing_name = row[0]
            existing_nric = row[1]
            if existing_name == request.name and existing_nric == request.nric:
                historylisting_message.message = "[Location: " + row[2] + \
                    " | Check In: " + row[3] + " | Check Out: " + row[4] + "]"
                yield historylisting_message
                time.sleep(0)

    def ListCases(self, request_iterator, context):
        safeEntry = pd.read_csv("safeEntry.csv", header=None)
        safeEntry[3] = pd.to_datetime(safeEntry[3])
        cases = safeEntry.loc[(safeEntry[3] > datetime.datetime.now(
        ) - pd.to_timedelta("14day"))]
        for request in request_iterator:
            if request.message == " ":
                for index, row in cases.iterrows():
                    yield safeEntry_pb2.Reply(message=f'{index, [item for item in row]}')
            else:
                try:
                    case = cases.loc[int(request.message)]
                except:
                    yield safeEntry_pb2.Reply(message="Make Sure index chosen is correct")
                else:
                    case_check_in_details = (case[2], case[3], case[4])

                    list_of_possible_exposure = cases.loc[(
                        cases[2] == case[2])]

                    unique_people = list_of_possible_exposure[1].unique()

                    possible_exposure = {}
                    for unique_person in unique_people:
                        possible_exposure[unique_person] = case_check_in_details
                    global to_notify
                    d = to_notify
                    if case_check_in_details[2] == '-':
                        temp = (
                            case_check_in_details[0], case_check_in_details[1].strftime("%d/%m/%Y %H:%M:%S"), '-')
                    else:
                        temp = (case_check_in_details[0], case_check_in_details[1].strftime(
                            "%d/%m/%Y %H:%M:%S"), case_check_in_details[2])
                    for unique_person in unique_people:

                        if unique_person in d:
                            d[unique_person].append(temp)
                        else:
                            d[unique_person] = [temp]
                    to_notify = d
                    global affected_locations
                    affected_locations.append((case[2], case[3], case[4]))
                    print(case.index)
                    safeEntry.iloc[int(request.message), 7] = 1
                    safeEntry.to_csv(
                        "safeEntry.csv", header=False, index=False)
                    yield safeEntry_pb2.Reply(message="Notification Sent!")

    def GetNotified(self, request, context):
        request = request.message
        if request in to_notify:
            reply = str(to_notify[request])
            del to_notify[request]
            return safeEntry_pb2.Reply(message=reply)
        else:
            return safeEntry_pb2.Reply(message="False")

    def LogInNotification(self, request, context):
        df = pd.read_csv("safeEntry.csv", header=None, parse_dates=[3])
        cases = df.loc[(df[3] > datetime.datetime.now(
        ) - pd.to_timedelta("14day")) & (df[1] == request.message)][2].unique()

        if len(cases) != 0:
            yield safeEntry_pb2.Reply(message='You recently were in area visited by covid positive case. Here are the details:')
            possible_exposure = {}
            for location, checkin, checkout in affected_locations:
                if (location in possible_exposure) and (location in cases):
                    possible_exposure[location].append([checkin, checkout])
                elif (location not in possible_exposure) and (location in cases):
                    possible_exposure[location] = [[checkin, checkout]]
            for j in cases:
                for value in possible_exposure.values():
                    for i in value:
                        yield safeEntry_pb2.Reply(message=f'Location: {j} from {str(i[0])} to {str(i[1])}')
            return safeEntry_pb2.Reply(message="False")
        else:
            return safeEntry_pb2.Reply(message="Log In Success")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    safeEntry_pb2_grpc.add_SafeEntryServicer_to_server(SafeEntry(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    t2 = threading.Thread(target=update_locations)
    t2.start()
    server.wait_for_termination()


def update_locations():
    while True:
        global affected_locations
        new = []
        if not affected_locations:
            pass
        else:
            for i in affected_locations:
                if i[1] > datetime.datetime.now() - pd.to_timedelta("14day"):
                    new.append(i)
        affected_locations = new

        time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig()

    safeEntry = pd.read_csv("safeEntry.csv", header=None)
    safeEntry[3] = pd.to_datetime(safeEntry[3])

    cases = safeEntry.loc[(safeEntry[3] > datetime.datetime.now(
    ) - pd.to_timedelta("14day")) & (safeEntry[7] == 1)]
    new = []
    for i, j in cases.iterrows():
        new.append((j[2], j[3], j[4]))
    affected_locations = new

    serve()
