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

    #Initializing the simulation
    def __init__(self, env, num_nurses):
        self.env = env
        self.nurses = simpy.PriorityResource(env, capacity=num_nurses)
        self.urgent_case_id = 1
        self.student_id = 1
        self.untreated_students = 0
        self.treated_students = 0

        open('simulation_summary.txt', 'w').close() #Removing previous data 

        self.env.process(self.student_generator())
        self.env.run()


    #Sickbay process
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
            
        self.student_list_summary(student)


    #Generating students
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


    #Printing simulation timeline
    def print_status(self, student, status):

        #color codes for printing
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE   = "\033[34m"
        RESET = "\033[0m"
        
        if status == 'arrived':
            if student.priority == 0:
                print(f'{RED}[>]  {student.name} arrives at the sickbay at time {student.arrival_time}{RESET}')
            else:
                print(f'[>]  {student.name} arrives at the sickbay at time {student.arrival_time}')

        if status == 'attended':
            print(f'{GREEN}[+]  {student.name} is being attended to by a nurse at time {student.arrival_time + student.wait_time} (waited {student.wait_time}{RESET})')

        if status == 'left':
            if student.treated:
                print(f'{BLUE}[<]  {student.name} leaves the sickbay at time {student.leave_time}{RESET}')
            else:
                print(f'{YELLOW}[X]  {student.name} leaves the sickbay at time {student.leave_time} (waited too long | waited {student.wait_time}{RESET})')



    #writing student list summary to text file
    def student_list_summary(self, student):
        text = open('simulation_summary.txt', 'a') 

        text.write(f'\n{f'PATIENT - {student.name}':=^50}')

        #Timeline
        text.write(f'\n{f'Timeline':-^50}')
        text.write(f'\n{'Arrival:':<25}{student.arrival_time:>25}')
        text.write(f'\n{'Wait Time:':<25}{student.wait_time:>25}')
        text.write(f'\n{'Departure:':<25}{student.leave_time:>25}')

        # Status
        text.write(f'\n{'Status':-^50}')
        if student.treated:
            text.write(f'\nSuccessfully treated')
            text.write(f'\n{'Attended at:':<25}{student.arrival_time + student.wait_time:>25}')
            text.write(f'\n{'Treatment duration:':<25}{student.leave_time - (student.arrival_time + student.wait_time):>25}')
        else:
            text.write(f'\nDid not receive treatment (timeout)')
            text.write(f'\n{'Max wait time exceeded:':<25}{student.wait_time:>25}')
            
        text.write(f'\n' + '=' * 50 + '\n')

        text.close()
    

    #Reading the student list summary
    def read_summary(self):
        line = 'a'
        file = open('simulation_summary.txt', 'r')
        while line != '':
            line = file.readline()
            print(line)
        file.close()
        

    #Asking user if they want to see the student list summary
    def print_student_list_summary(self):
        print("\n" + '=' * 60)
        user_input = input('\nDo you want to see the student list summary? (yes/no): ')
        if user_input.lower() == 'yes':
            print(f'\n{f'Student List Summary':=^60}')
            self.read_summary()

    #Printing the simulation summary
    def print_simulation_summary(self):
        print('\n' + '=' * 50)
        print(f'{"SIMULATION SUMMARY":^50}')
        print('=' * 50)

        print(f'{"Total students:":<25}{sickbay.treated_students + sickbay.untreated_students:>25}')
        print(f'{"Total urgent cases:":<25}{sickbay.urgent_case_id - 1:>25}')
        print(f'{"Treated students:":<25}{sickbay.treated_students:>25}')
        print(f'{"Untreated students:":<25}{sickbay.untreated_students:>25}')
        print('=' * 50)



sickbay = sickbay_simulation(simpy.Environment(), num_nurses=2)
sickbay.print_student_list_summary()
sickbay.print_simulation_summary()