from concurrent import futures
import logging

import grpc
import safeEntry_pb2
import safeEntry_pb2_grpc
import csv
import pandas as pd
import datetime
from collections import defaultdict


to_notify = {"Test": "IT finally fucking WORKSSS"}


class SafeEntry(safeEntry_pb2_grpc.SafeEntryServicer):

    # Self Check In
    def CheckIn(self, request, context):
        checkin_message = safeEntry_pb2.Reply()
        checkin_message.message = f'Name: {request.name}\nNRIC: {request.nric}\nLocation: {request.location}\nCheck In: {request.checkin}'
        checkin_entry = [request.name, request.nric,
                         request.location, request.checkin, '-', 1, request.id, 0]
        print(checkin_entry)

        # Save data in csv file
        file = open('safeEntry.csv', 'a', newline='')
        csv_writer = csv.writer(file)
        csv_writer.writerow(checkin_entry)
        file.close()
        return checkin_message

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
        for request in request_iterator:
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

    # List cases in the past 14 days
    def DeclareAffected(self, request, context):

        return super().DeclareAffected(request, context)

    def ListCases(self, request_iterator, context):

        infected_details = []
        original = pd.read_csv("safeEntry.csv", header=None)
        safeEntry = original
        safeEntry[3] = pd.to_datetime(safeEntry[3])
        cases = safeEntry.loc[(safeEntry[3] > datetime.datetime.now(
        ) - pd.to_timedelta("14day"))]
        for request in request_iterator:
            if request.message == " ":
                for index, row in cases.iterrows():
                    yield safeEntry_pb2.Reply(message=f'{index, [item for item in row]}')
            else:
                print("Infected Locations")
                case = cases.iloc[int(request.message)]
                case_check_in_details = (case[2], case[3], case[4])

                list_of_possible_exposure = cases.loc[(
                    cases[2] == case[2]) & (cases[3] >= case[3])]
                indexes = list_of_possible_exposure.index.tolist()
                print(list_of_possible_exposure)
                unique_people = list_of_possible_exposure[1].unique()
                possible_exposure = {}
                for unique_person in unique_people:
                    possible_exposure[unique_person] = case_check_in_details
                global to_notify
                d = to_notify
                for unique_person in unique_people:
                    if unique_person in d:
                        d[unique_person].append(case_check_in_details)
                    else:
                        d[unique_person] = [case_check_in_details]
                to_notify = d
                original.iloc[indexes, 7] = 1
                original.to_csv("safeEntry.csv", header=False, index=False)
                return safeEntry_pb2.Reply(message="Notification Sent!")

    def GetNotified(self, request, context):
        request = request.message
        if request in to_notify:
            print("to_notify")
            return safeEntry_pb2.Reply(message=to_notify[request])
        else:
            return safeEntry_pb2.Reply(message="False")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    safeEntry_pb2_grpc.add_SafeEntryServicer_to_server(SafeEntry(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
