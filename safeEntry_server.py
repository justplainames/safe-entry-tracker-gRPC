from concurrent import futures
import logging

import grpc
import safeEntry_pb2
import safeEntry_pb2_grpc
import csv
import pandas as pd
import datetime
import time
import threading


to_notify = {"237444T": [("a", 'b', 'c'), ('d', 'e', 'f')]}
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
                    safeEntry.iloc[case.index, 7] = 1
                    safeEntry.to_csv(
                        "safeEntry.csv", header=False, index=False)
                    yield safeEntry_pb2.Reply(message="Notification Sent!")

    def GetNotified(self, request, context):
        request = request.message
        print(request)
        if request in to_notify:
            reply = str(to_notify[request])
            del to_notify[request]
            return safeEntry_pb2.Reply(message=reply)
        else:
            return safeEntry_pb2.Reply(message="False")

    def LogInNotification(self, request, context):
        safeEntry = pd.read_csv("safeEntry.csv", header=None)
        safeEntry[3] = pd.to_datetime(safeEntry[3])

        cases = safeEntry.loc[(safeEntry[3] > datetime.datetime.now(
        ) - pd.to_timedelta("14day")) & (safeEntry[7] == 1)]

        if cases.empty:
            print("There is no active cases in the past 14 days")
            return safeEntry_pb2.Reply(message="Log In Success")
        check = cases.loc[cases[1] == request.message]
        if check.empty:
            print("User was not in any affected areas in the past 14 Days")
            return safeEntry_pb2.Reply(message="Log In Success")
        print("User was in an affected area in the past 14 Days")
        check[3] = pd.to_datetime(check[3])
        for i, j in check.iterrows():
            yield safeEntry_pb2.Reply(message=f'Location: {j[2]} from {str(j[3])} to {j[4]}')
        return safeEntry_pb2.Reply(message="False")


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
        print(affected_locations)
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
