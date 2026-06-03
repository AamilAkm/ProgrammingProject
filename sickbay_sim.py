import simpy
import random

#Scenario – A school with limited number of nurses. 

#Variables – number of nurses | wait time in sickbay | students in queue | urgent cases | nurses occupied with an urgent case

class sickbay_simulation:
    def __init__(self, env, num_nurses):
        self.env = env
        self.nurses = simpy.PriorityResource(env, capacity=num_nurses)
        self.MAX_WAIT_TIME = 30  # Maximum time a student is willing to wait
        self.env.process(self.student_generator())
        self.env.run()

    def sickbay(self, name, priority):
        arrival_time = self.env.now
        print(f'{name} arrives at the sickbay at {self.env.now}')
        with self.nurses.request(priority=priority) as request:
            results = yield request | self.env.timeout(self.MAX_WAIT_TIME)

            # Check if the student timed out waiting
            if request in results:
                wait_time = self.env.now - arrival_time
                print(f'{name} is being attended to by a nurse at {self.env.now} (waited {wait_time})')
                yield self.env.timeout(random.randint(5, 15))  # Time taken to attend to the student
                print(f'{name} leaves the sickbay at {self.env.now}')
            else:
                wait_time = self.env.now - arrival_time
                print(f'{name} leaves the sickbay at {self.env.now} (waited too long | waited {wait_time})')

    def student_generator(self):
        urgent_case_id = 1
        student_id = 1

        while True:
            urgent_random = random.randint(1, 10)
            if urgent_random == 7:  # 10% chance of an urgent case
                self.env.process(self.urgent_case_generator(urgent_case_id, priority=0))  # Urgent cases have higher priority
                urgent_case_id += 1
            else:
                yield self.env.timeout(random.randint(1, 3))  # Time between student arrivals
                self.env.process(self.sickbay(f'Student {student_id}', priority=1))  # Regular students have lower priority
                student_id += 1
                if student_id > 25:  # Limit the number of students for the simulation
                    break

    def urgent_case_generator(self, urgent_case_id, priority):
        print(f'An urgent case {urgent_case_id} arrives at {self.env.now}')
        with self.nurses.request(priority=priority) as request:
            yield request
            print(f'An urgent case {urgent_case_id} is being attended to by a nurse at {self.env.now}')
            yield self.env.timeout(random.randint(10, 20))  # Time taken to attend to the urgent case
            print(f'An urgent case {urgent_case_id} leaves the sickbay at {self.env.now}')

sickbay = sickbay_simulation(simpy.Environment(), num_nurses=2)

