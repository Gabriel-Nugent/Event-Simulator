import random
import math
import queue
import sys, getopt

# function generates a random number in an exponential distribution given the rate of occurance
# *uses the Inverse transform sampling method*
def randExp(rate):
    random_exp = math.log(1-random.uniform(0,1))/(-rate)
    return random_exp

def generateProcess(process_number,rate_of_arrival,avg_service_time):
    arrival_time = randExp(rate_of_arrival)
    service_time = randExp(1/avg_service_time)
    process = {
        "process_ID": process_number,
        "arrival_time": arrival_time,
        "service_time": service_time
    }
    return process

def scheduleEvent(event_type,event_time,process,event_queue):
    event = {
        "event_type": event_type,
        "event_time": event_time,
        "process": process
    }
    event_queue.put((event["event_time"],event))

def handleArrival(event,event_queue,ready_queue,cpu_state,clock):
    process = event["process"]
    if cpu_state == 1:
        cpu_state = 0
        scheduleEvent("DEP",clock + process["service_time"],process,event_queue)
    else:
        ready_queue.put(process)
    return cpu_state

def handleDeparture(event_queue,ready_queue,cpu_state,clock):
    if ready_queue.qsize() == 0:
        cpu_state = 1
    else:
        process = ready_queue.get()
        scheduleEvent("DEP",clock + process["service_time"],process,event_queue)
    return cpu_state

def runSimulation(rate_of_arrival,avg_service_time):
    ready_queue = queue.Queue()
    event_queue = queue.PriorityQueue()
    clock = 0
    cpu_state = 1
    process_count = 1
    completed_processes = 0
    process = generateProcess(process_count,rate_of_arrival,avg_service_time)
    scheduleEvent("ARR",process["arrival_time"],process,event_queue)
    while completed_processes < 10:
        event = event_queue.get()[1]
        print(event)
        event_type = event["event_type"]
        clock = event["event_time"]
        if event_type == "ARR":
            cpu_state = handleArrival(event,event_queue,ready_queue,cpu_state,clock)
            if process_count < 10:
                process_count += 1
                new_process = generateProcess(process_count,rate_of_arrival,avg_service_time)
                scheduleEvent("ARR",clock + new_process["arrival_time"],new_process,event_queue)
        elif event_type == "DEP":
            cpu_state = handleDeparture(event_queue,ready_queue,cpu_state,clock)
            completed_processes += 1
        print("Process count: ", process_count);
        print("Completed processes: ", completed_processes);

def main():
    runSimulation(sys.argv[1],sys.argv[2])

if __name__ == "__main__":
    main(sys.argv)