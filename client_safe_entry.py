import grpc
from google.protobuf.timestamp_pb2 import Timestamp
import safe_entry_pb2
import safe_entry_pb2_grpc
import time


def get_notification():
    while True:
        name = input("Please enter your NRIC or nothing to break: ")

        if name == "":
            break


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = safe_entry_pb2_grpc.SafeEntryStub(channel)
        login = input("enter NRIC: ")
        if login == "admin":
            while True:
                print("1. Declare Exposure")  # Unary
                print("2. logout")
                choice = input("Enter option: ")
                if choice == "2":
                    break
                locations = stub.ListLocations(safe_entry_pb2.Empty())
                print("Available locations:")
                for location in locations:
                    print(location.name)
        else:
            check = stub.AffectedNotification(
                safe_entry_pb2.NRIC(nric=login))
            print("Completed client side check")
            for status in check:
                print("client side receiving")
                print(status.message)
            while True:
                print("1. CheckIn/CheckOut")  # Unary
                print("2. Group Check In")
                print("3. List past history")
                rpc_call = input("Choose an option: ")
                if rpc_call == "1":
                    print("Checking IN/OUT")
                    check_response = stub.CheckValidation(
                        safe_entry_pb2.NRIC(nric=login))
                    if check_response.status == True:
                        response = stub.CheckOut(
                            safe_entry_pb2.NRIC(nric=login))
                        print("Checked Out!")
                    else:
                        name = input("Enter Name: ")
                        location = input("Enter Location: ")
                        response = stub.CheckIn(safe_entry_pb2.PersonDetails(
                            name=name, nric=login, location=location))
                        print("Checked In!")


if __name__ == '__main__':
    run()
