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
        self.leave_time = None
        self.treated = False

class sickbay_simulation:
    def __init__(self, env, num_nurses):
        self.env = env
        self.nurses = simpy.PriorityResource(env, capacity=num_nurses)
        self.simulation_summary = ''
        self.env.process(self.student_generator())
        self.env.run()

    def print_outcome(self, student):

        self.simulation_summary += f'\n  PATIENT : {student.name}'

        # Timeline
        self.simulation_summary += f'\n  Timeline:'
        self.simulation_summary += f'\n   Arrival:        {student.arrival_time:7.1f}'
        self.simulation_summary += f'\n   Wait Time:      {student.wait_time:7.1f}'
        self.simulation_summary += f'\n   Departure:      {student.leave_time:7.1f}'

        # Status
        self.simulation_summary += f'\n' + '-' * 40
        self.simulation_summary += f'\n  Status:'
        if student.treated:
            self.simulation_summary += f'\n  Successfully treated'
            self.simulation_summary += f'\n   Attended at:        {student.arrival_time + student.wait_time:7.1f}'
            self.simulation_summary += f'\n   Treatment duration: {student.leave_time - (student.arrival_time + student.wait_time):7.1f}'
        else:
            self.simulation_summary += f'\n   Did not receive treatment (timeout)'
            self.simulation_summary += f'\n   Max wait time exceeded: {student.wait_time}'
        
        self.simulation_summary += f'\n' + '=' * 60 + '\n'


    def print_status(self, student, status):
        if status == 'arrived':
            print ('-' * 80)
            print(f'{student.name} arrives at the sickbay at time {student.arrival_time}')
            print ('-' * 80)

        if status == 'attended':
            print(f'{student.name} is being attended to by a nurse at time {student.arrival_time + student.wait_time} (waited {student.wait_time})')

        if status == 'left':
            if student.treated:
                print(f'{student.name} leaves the sickbay at time {student.leave_time}')
            else:
                print(f'{student.name} leaves the sickbay at time {student.leave_time} (waited too long | waited {student.wait_time})')
        


    def sickbay(self, student):
        """Process a student through the sickbay."""
        student.arrival_time = self.env.now
        self.print_status(student, 'arrived')
        with self.nurses.request(priority=student.priority) as request:
            results = yield request | self.env.timeout(student.MAX_WAIT_TIME)

            # Check if the student timed out waiting
            if request in results:
                student.wait_time = self.env.now - student.arrival_time
                self.print_status(student, 'attended')
                treatment_time = random.randint(5, 15)
                yield self.env.timeout(treatment_time)  # Time taken to attend to the student
                student.treated = True
                student.leave_time = self.env.now
                self.print_status(student, 'left')
            else:
                student.wait_time = self.env.now - student.arrival_time
                student.leave_time = self.env.now
                self.print_status(student, 'left')
            
        self.print_outcome(student)

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
print(sickbay.simulation_summary)

