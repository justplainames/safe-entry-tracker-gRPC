from __future__ import print_function

import threading
import logging


import grpc
import safeEntry_pb2
import safeEntry_pb2_grpc
from datetime import datetime
import csv
import time
import ast


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = safeEntry_pb2_grpc.SafeEntryStub(channel)

        name_input = input("Please enter name: ")
        nric_input = input("Please enter NRIC: ")

        if name_input == "admin" and nric_input == "admin":
            while True:
                print("/ListCases. Check In")
                print("/LogOut. Check Out")
                rpc_call = input("Please enter function: ")

                if rpc_call == "/ListCases":
                    responses = stub.ListCases(get_client_stream_requests())
                    print("Case List Past 14 days:")
                    for response in responses:
                        print(response.message)

        else:
            t2 = threading.Thread(target=get_notifications,
                                  args=[stub, nric_input])
            t2.start()
            check = stub.LogInNotification(
                safeEntry_pb2.Reply(message=nric_input))
            for status in check:
                print(status.message)

            print("1. West Mall")
            print("2. Bukit Panjang Plaza")
            print("3. JCube")
            select_location = input("Please select location:")
            if select_location == "1":
                selected_location = "West Mall"
            elif select_location == "2":
                selected_location = "Bukit Panjang Plaza"
            elif select_location == "3":
                selected_location = "JCube"
            while True:
                print("1. Check In")
                print("2. Check Out")
                print("3. Group Check In")
                print("4. Group Check Out")
                rpc_call = input("Please enter number: ")

                # Check In
                if rpc_call == "1":
                    timestamp = datetime.now()
                    checkin_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")
                    tracking_id = nric_input + " " + checkin_time
                    request = safeEntry_pb2.Request(
                        name=name_input, nric=nric_input, location=selected_location, checkin=checkin_time, id=tracking_id)
                    response = stub.CheckIn(request)
                    checkin_message = "Details:\n" + str(response.message)
                    print(checkin_message)

                # Check Out
                elif rpc_call == "2":
                    file = open('safeEntry.csv')
                    csvreader = csv.reader(file)
                    data = list(csvreader)
                    file.close()
                    check_id = ""
                    for row in reversed(data):
                        existing_name = row[0]
                        existing_nric = row[1]
                        existing_checkout = row[4]
                        group_number = row[5]

                        if existing_name == name_input and existing_nric == nric_input and existing_checkout == "-" and group_number == "1" and check_id == "":

                            check_id = row[6]
                            timestamp = datetime.now()
                            checkout_time = timestamp.strftime(
                                "%d/%m/%Y %H:%M:%S")
                            request = safeEntry_pb2.Request(
                                name=name_input, nric=nric_input, location='West Mall', checkin=row[3], checkout=checkout_time, id=check_id)
                            response = stub.CheckOut(request)
                            checkout_message = "Details:\n" + \
                                str(response.message)
                            print(checkout_message)

                # Group Check In
                elif rpc_call == "3":
                    response = stub.GroupCheckIn(
                        groupcheckin_requests(name_input, nric_input))
                    groupcheckin_message = "Details:\n" + str(response.message)
                    print(groupcheckin_message)

                # Group Check Out
                elif rpc_call == "4":
                    file = open('safeEntry.csv')
                    csvreader = csv.reader(file)
                    data = list(csvreader)
                    file.close()
                    group_check_id = ""
                    for row in reversed(data):
                        existing_name = row[0]
                        existing_nric = row[1]
                        existing_checkout = row[4]
                        group_number = row[5]

                        if existing_name == name_input and existing_nric == nric_input and existing_checkout == "-" and group_number != "0" and group_check_id == "":

                            group_check_id = row[6]
                            timestamp = datetime.now()
                            checkout_time = timestamp.strftime(
                                "%d/%m/%Y %H:%M:%S")
                            request = safeEntry_pb2.Request(name=name_input, nric=nric_input, location='West Mall',
                                                            checkin=row[3], checkout=checkout_time, groupnumber=int(group_number), id=group_check_id)
                            response = stub.GroupCheckOut(request)
                            checkout_message = "Details:\n" + \
                                str(response.message)
                            print(checkout_message)


def groupcheckin_requests(name_input, nric_input):
    list_name = [name_input]
    list_nric = [nric_input]

    group_number = 1

    timestamp = datetime.now()
    checkin_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")
    group_tracking_id = nric_input + " " + checkin_time
    print(group_tracking_id)

    while True:
        print("1. Check In")
        print("2. Add another user")
        group_select = input("Please enter number: ")

        if group_select == "2":
            name_input_group = input("Please enter name: ")
            nric_input_group = input("Please enter NRIC: ")
            group_number = group_number + 1
            list_name.append(name_input_group)
            list_nric.append(nric_input_group)

        if group_select == "1":
            break

    for row in range(len(list_name)):
        if row != 0:
            group_number = 0
        request = safeEntry_pb2.Request(name=list_name[row], nric=list_nric[row], location='West Mall',
                                        checkin=checkin_time, groupnumber=group_number, id=group_tracking_id)
        yield request
        time.sleep(1)


def get_client_stream_requests():
    for i in range(2):
        if i == 0:
            yield safeEntry_pb2.Reply(message=" ")
        else:
            nric = input(
                "Enter index to Declare Location has been Compromised: ")

            request = safeEntry_pb2.Reply(message=nric)
            yield request
        time.sleep(1)


def get_notifications(stub, nric):
    while True:
        responses = stub.GetNotified(safeEntry_pb2.Reply(message=nric))
        if responses.message == "False":
            pass
        else:
            response = ast.literal_eval(responses.message)
            print(
                "You recently were in area visited by covid positive case. Here are the details:")
            if response == type(list) or type(tuple):
                for i in response:
                    print(f'Location: {i[0]} from {i[1]} to {i[2]}')
            else:
                print(
                    f'Location: {response[0]} from {response[1]} to {response[2]}')
        time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig()
    run()
