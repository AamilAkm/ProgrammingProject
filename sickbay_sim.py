import simpy
import random

#Scenario – A school with limited number of nurses. 

#Variables – number of nurses | wait time in sickbay | students in queue | urgent cases | nurses occupied with an urgent case

MAX_WAIT_TIME = 20  # Maximum time a student is willing to wait

def sickbay(env, name, nurses):
    arrival_time = env.now
    print(f'{name} arrives at the sickbay at {env.now}')
    with nurses.request() as request:
        results = yield request | env.timeout(MAX_WAIT_TIME)
        
        # Check if the student timed out waiting
        if request  in results:
            wait_time = env.now - arrival_time
            print(f'{name} is being attended to by a nurse at {env.now} (waited {wait_time})')
            yield env.timeout(random.randint(5, 15))  # Time taken to attend to the student
            print(f'{name} leaves the sickbay at {env.now}')
        else:
            print(f'{name} leaves the sickbay at {env.now} (waited too long)')

def student_generator(env, nurses):
    student_id = 1
    while True:
        yield env.timeout(random.randint(1, 3))  # Time between student arrivals
        env.process(sickbay(env, f'Student {student_id}', nurses))  # Regular students have lower priority
        student_id += 1
        if student_id > 25:  # Limit the number of students for the simulation
            break
        
def urgent_case_generator(env, nurses):
    case_id = 1
    while True:
        yield env.timeout(random.randint(10, 20))  # Time between urgent cases
        print(f'An urgent case arrives at {env.now}')
        with nurses.request() as request:  # Urgent cases have higher priority
            yield request
            print(f'An urgent case is being attended to by a nurse at {env.now}')
            yield env.timeout(random.randint(10, 20))  # Time taken to attend to the urgent case
            print(f'An urgent case leaves the sickbay at {env.now}')
            case_id += 1
            if case_id > 5:  # Limit the number of urgent cases for the simulation
                break


# Set up the simulation environment
env = simpy.Environment()
nurses = simpy.Resource(env, capacity=2)  # Number of nurses available
env.process(student_generator(env, nurses))
env.process(urgent_case_generator(env, nurses))  # Urgent cases have the highest priority
env.run()  # Run the simulation for a certain time period
    
