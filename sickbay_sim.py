import simpy
import random

#Scenario – A school with limited number of nurses. 

#Variables – number of nurses | wait time in sickbay | students in queue | urgent cases | nurses occupied with an urgent case

MAX_WAIT_TIME = 30  # Maximum time a student is willing to wait

def sickbay(env, name, nurses, priority):
    arrival_time = env.now
    print(f'{name} arrives at the sickbay at {env.now}')
    with nurses.request(priority=priority) as request:
        results = yield request | env.timeout(MAX_WAIT_TIME)
        
        # Check if the student timed out waiting
        if request in results:
            wait_time = env.now - arrival_time
            print(f'{name} is being attended to by a nurse at {env.now} (waited {wait_time})')
            yield env.timeout(random.randint(5, 15))  # Time taken to attend to the student
            print(f'{name} leaves the sickbay at {env.now}')
        else:
            wait_time = env.now - arrival_time
            print(f'{name} leaves the sickbay at {env.now} (waited too long | waited {wait_time})')

def student_generator(env, nurses):
    urgent_case_id = 1
    student_id = 1

    while True:
        urgent_random = random.randint(1, 10)
        if urgent_random == 7:  # 10% chance of an urgent case
            env.process(urgent_case_generator(env, urgent_case_id, nurses, priority=0))  # Urgent cases have higher priority
            urgent_case_id += 1
        else:
            yield env.timeout(random.randint(1, 3))  # Time between student arrivals
            env.process(sickbay(env, f'Student {student_id}', nurses, priority=1))  # Regular students have lower priority
            student_id += 1
            if student_id > 25:  # Limit the number of students for the simulation
                break
        
def urgent_case_generator(env, urgent_case_id, nurses, priority):
    print(f'An urgent case {urgent_case_id} arrives at {env.now}')
    with nurses.request(priority=priority) as request:
        yield request
        print(f'An urgent case {urgent_case_id} is being attended to by a nurse at {env.now}')
        yield env.timeout(random.randint(10, 20))  # Time taken to attend to the urgent case
        print(f'An urgent case {urgent_case_id} leaves the sickbay at {env.now}')



# Set up the simulation environment
env = simpy.Environment()
nurses = simpy.PriorityResource(env, capacity=2)  # Number of nurses available
env.process(student_generator(env, nurses))
env.run()  # Run the simulation for a certain time period
    
