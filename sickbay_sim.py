import simpy
import random

#Scenario – A school with limited number of nurses. 

#Variables – number of nurses | wait time in sickbay | students in queue | urgent cases | nurses occupied with an urgent case

def sickbay(env, name, nurses):
    print(f'{name} arrives at the sickbay at {env.now}')
    with nurses.request() as request:
        yield request
        print(f'{name} is being attended to by a nurse at {env.now}')
        yield env.timeout(random.randint(5, 15))  # Time taken to attend to the student
        print(f'{name} leaves the sickbay at {env.now}')

def student_generator(env, nurses):
    student_id = 1
    while True:
        yield env.timeout(random.randint(1, 3))  # Time between student arrivals
        env.process(sickbay(env, f'Student {student_id}', nurses))
        student_id += 1


# Set up the simulation environment
env = simpy.Environment()
nurses = simpy.Resource(env, capacity=2)  # Number of nurses available
env.process(student_generator(env, nurses))
env.run()  # Run the simulation for a certain time period
