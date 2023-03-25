import random
import math
import queue
import sys

# function generates a random number in an exponential distribution given the rate of occurance
# *uses the Inverse transform sampling method*
def randExp(rate):
    random_exp = math.log(1-random.uniform(0,1))/(-rate)
    return random_exp

def generateProcess(process_number,rate_of_arrival,avg_service_time,clock):
    arrival_time = randExp(rate_of_arrival) + clock
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

    if event_type == "DEP":
        event["arrival_time"] = process["arrival_time"]

    event_queue.put((event["event_time"],event))

def handleArrival(event,event_queue,ready_queue,cpu_is_idle,clock):
    process = event["process"]
    if cpu_is_idle == 1:
        cpu_is_idle = 0
        scheduleEvent("DEP",clock + process["service_time"],process,event_queue)
    else:
        ready_queue.put(process)
    return cpu_is_idle

def handleDeparture(event_queue,ready_queue,cpu_is_idle,clock):
    if ready_queue.qsize() == 0:
        cpu_is_idle = 1
    else:
        process = ready_queue.get()
        scheduleEvent("DEP",clock + process["service_time"],process,event_queue)
    return cpu_is_idle

def calcAvgTurnaround(turnaround_times):
    total_turnaround_time = 0
    for time in turnaround_times:
        total_turnaround_time += time
    return round(total_turnaround_time / len(turnaround_times),4)

def calcAvgThroughput(throughput_at_checks):
    total_throughputs = 0
    for throughput in throughput_at_checks:
        total_throughputs += throughput
    return  round(total_throughputs / len(throughput_at_checks), 2)

def calcCpuUtil(idle_times,clock):
    total_idle_time = 0
    for time in idle_times:
        total_idle_time += time
    cpu_util = (clock - total_idle_time) / clock
    return round(cpu_util, 2)

def calcAvgReadyProcesses(processes_in_queue):
    total_ready_processes = 0
    for processes_at_check in processes_in_queue:
        total_ready_processes += processes_at_check
    return round(total_ready_processes / len(processes_in_queue), 2)

def runSimulation(rate_of_arrival,avg_service_time):

    print("\nRUNNING SIMULATION WITH ARGUMENTS:")
    print("RATE OF ARRIVAL = ", rate_of_arrival, "processes per second")
    print("AVERAGE SERVICE TIME = ", avg_service_time, "s\n...")

    ready_queue = queue.Queue()
    event_queue = queue.PriorityQueue()

    turnaround_times = []
    time_of_last_tp_check = 0
    throughput_at_checks = []
    idle_start_time = 0
    times_cpu_is_idle = []
    processes_in_queue_at_check = []

    clock = 0
    cpu_is_idle = 1
    process_count = 1
    completed_processes = 0

    process = generateProcess(process_count,rate_of_arrival,avg_service_time,clock)
    scheduleEvent("ARR",process["arrival_time"],process,event_queue)

    while completed_processes < 10000:
        event = event_queue.get()[1]
        event_type = event["event_type"]
        clock = event["event_time"]
        if event_type == "ARR":

            temp_cpu_is_idle = handleArrival(event,event_queue,ready_queue,cpu_is_idle,clock)
            if temp_cpu_is_idle == 0 and cpu_is_idle == 1:
                times_cpu_is_idle.append(clock - idle_start_time)
            cpu_is_idle = temp_cpu_is_idle

            process_count += 1
            new_process = generateProcess(process_count,rate_of_arrival,avg_service_time,clock)
            scheduleEvent("ARR",new_process["arrival_time"],new_process,event_queue)

        elif event_type == "DEP":

            temp_cpu_is_idle = handleDeparture(event_queue,ready_queue,cpu_is_idle,clock)
            if temp_cpu_is_idle == 1 and cpu_is_idle == 0:
                idle_start_time = clock
            cpu_is_idle = temp_cpu_is_idle

            turnaround_time = clock - event["arrival_time"]
            turnaround_times.append(turnaround_time)

            completed_processes += 1

            if completed_processes % 10 == 0:
                throughput_at_checks.append(10 / (clock - time_of_last_tp_check))
                time_of_last_tp_check = clock

        processes_in_queue_at_check.append(ready_queue.qsize())
    
    print("The average turnaround time of processes: ", calcAvgTurnaround(turnaround_times), "s")
    print("The total throughput (number of processes per second): ", calcAvgThroughput(throughput_at_checks))
    print("The CPU Utilization: ",calcCpuUtil(times_cpu_is_idle,clock))
    print("The average number of processes in the ready queue: ",calcAvgReadyProcesses(processes_in_queue_at_check),"\n")

def main(args):
    runSimulation(int(args[1]),float(args[2]))

if __name__ == "__main__":
   main(sys.argv)#
