import simpy
import random

#Scenario – A school with limited number of nurses. 

#Variables – number of nurses | wait time in sickbay | students in queue | urgent cases | nurses occupied with an urgent case

class student:
    MAX_WAIT_TIME = 30

    def __init__(self, name, student_id, priority):
        self.name = name
        self.student_id = student_id
        self.priority = priority
        self.arrival_time = None
        self.wait_time = None
        self.treated = False

class sickbay_simulation:
    def __init__(self, env, num_nurses):
        self.env = env
        self.nurses = simpy.PriorityResource(env, capacity=num_nurses)
        self.env.process(self.student_generator())
        self.env.run()

    def sickbay(self, student):
        """Process a student through the sickbay."""
        student.arrival_time = self.env.now
        print(f'{student.name} arrives at the sickbay at {student.arrival_time}')
        with self.nurses.request(priority=student.priority) as request:
            results = yield request | self.env.timeout(student.MAX_WAIT_TIME)

            # Check if the student timed out waiting
            if request in results:
                student.wait_time = self.env.now - student.arrival_time
                print(f'{student.name} is being attended to by a nurse at {self.env.now} (waited {student.wait_time})')
                treatment_time = random.randint(5, 15)
                yield self.env.timeout(treatment_time)  # Time taken to attend to the student
                student.treated = True
                print(f'{student.name} leaves the sickbay at {self.env.now}')
            else:
                student.wait_time = self.env.now - student.arrival_time
                print(f'{student.name} leaves the sickbay at {self.env.now} (waited too long | waited {student.wait_time})')

    def student_generator(self):
        urgent_case_id = 1
        student_id = 1

        while True:
            urgent_random = random.randint(1, 10)
            if urgent_random == 7:  # 10% chance of an urgent case
                sick_student = student(f'Urgent Case {urgent_case_id}', urgent_case_id, priority=0)
                self.env.process(self.sickbay(sick_student))  # Process urgent case
                urgent_case_id += 1
            else:
                yield self.env.timeout(random.randint(1, 3))  # Time between student arrivals
                sick_student = student(f'Student {student_id}', student_id, priority=1)
                self.env.process(self.sickbay(sick_student))  # Pass the student object
                student_id += 1
                if student_id > 25:  # Limit the number of students for the simulation
                    break


sickbay = sickbay_simulation(simpy.Environment(), num_nurses=2)

