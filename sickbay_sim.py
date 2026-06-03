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
        self.urgent_case_id = 1
        self.student_id = 1
        self.untreated_students = 0
        self.treated_students = 0

        self.summary_file = open('simulation_summary.txt', 'w') #Save Simulation summary

        self.env.process(self.student_generator())
        self.env.run()


    def simulation_summary(self, student):
        text = self.summary_file

        patient_text = f"PATIENT - {student.name}"
        text.write(f'\n{patient_text.center(60, "=")}\n')

        text.write(f'\n{f'Timeline':-^60}')
        text.write(f'\n   Arrival{" "*45}{student.arrival_time}')
        text.write(f'\n   Wait Time:{" "*42}{student.wait_time}')
        text.write(f'\n   Departure:{" "*42}{student.leave_time}')

        # Status
        text.write(f'\n{'Status':-^60}')
        if student.treated:
            text.write(f'\n   Successfully treated')
            text.write(f'\n   Attended at:{" "*40}{student.arrival_time + student.wait_time}')
            text.write(f'\n   Treatment duration:{" "*33}{student.leave_time - (student.arrival_time + student.wait_time)}')
        else:
            text.write(f'\n   Did not receive treatment (timeout)')
            text.write(f'\n   Max wait time exceeded:{" "*29}{student.wait_time}')
            
        text.write(f'\n' + '-' * 60)
        text.write(f'\n\n' + '=' * 60 + '\n')
    
    def read_summary(self):
        file = open('simulation_summary.txt', 'r')
        line = file.readline()
        while line != '':
            print(line)
            line = file.readline()
            
        file.close()
        
        

    def print_status(self, student, status):
        if status == 'arrived':
            print(f'--> {student.name} arrives at the sickbay at time {student.arrival_time}')

        if status == 'attended':
            print(f'+ {student.name} is being attended to by a nurse at time {student.arrival_time + student.wait_time} (waited {student.wait_time})')

        if status == 'left':
            if student.treated:
                print(f'<-- {student.name} leaves the sickbay at time {student.leave_time}')
            else:
                print(f'<-- {student.name} leaves the sickbay at time {student.leave_time} (waited too long | waited {student.wait_time})')
        


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
                self.treated_students += 1
                student.leave_time = self.env.now
                self.print_status(student, 'left')
            else:
                student.wait_time = self.env.now - student.arrival_time
                student.leave_time = self.env.now
                self.untreated_students += 1
                self.print_status(student, 'left')
            
        self.simulation_summary(student)

    def student_generator(self):

        while True:
            urgent_random = random.randint(1, 10)
            if urgent_random == 7:  # 10% chance of an urgent case
                sick_student = student(f'Urgent Case {self.urgent_case_id}', self.urgent_case_id, priority=0)
                self.env.process(self.sickbay(sick_student))  # Process urgent case
                self.urgent_case_id += 1
            else:
                yield self.env.timeout(random.randint(1, 3))  # Time between student arrivals
                sick_student = student(f'Student {self.student_id}', self.student_id, priority=1)
                self.env.process(self.sickbay(sick_student))  # Pass the student object
                self.student_id += 1
                if self.student_id > 25:  # Limit the number of students for the simulation
                    break
    
    def print_summary(self):
        user_input = input('\nDo you want to see the simulation summary? (yes/no): ')
        if user_input.lower() == 'yes':
            self.read_summary()

sickbay = sickbay_simulation(simpy.Environment(), num_nurses=2)
sickbay.print_summary()

print(f'\nTotal students: {sickbay.treated_students + sickbay.untreated_students}')
print(f'Total urgent cases: {sickbay.urgent_case_id - 1}')
print(f'Treated students: {sickbay.treated_students}')
print(f'Untreated students: {sickbay.untreated_students}')