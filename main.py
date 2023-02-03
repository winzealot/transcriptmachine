from PyPDF2 import PdfReader
import os
import seaborn as sns
import matplotlib.pyplot as plt


class Course:
    # Class representing info for a course

    def __init__(self, name, subject, creds, code, instructor, _grade, _date):
        self.name = name
        self.subject = subject
        self.credits = float(creds)
        self.code = code
        self.instructor = instructor
        self.date = _date
        self.__grade = _grade

    def __str__(self):
        return "\t" + self.subject + self.code + " - " + self.name + " - " + self.instructor + " - " + str(
            self.credits) + " units" + " - " + self.__grade


class Semester:
    # courses for a semester
    def __init__(self, _courses, _termGPA):
        self.courses = _courses
        self.termGPA = float(_termGPA)

    def __str__(self):
        return "Term GPA: " + str(self.termGPA) + "\n" + "\n".join([str(course) for course in self.courses])


class Student:
    # Class for a student taking multiple courses
    def __init__(self, _name=None, _id=None, _major=None, _minor=None, _cumgpa=None):
        self.name = _name
        self.id = _id
        self.major = _major
        self.minor = _minor
        self.cumgpa = float(_cumgpa) if _cumgpa is not None else 0.0
        self.history = dict()

    def addSemester(self, name, semesterx):
        self.history[name] = semesterx

    def prStu(self):
        print(self.name + " is pursuing a major in " + self.major + " with a cumulative GPA of " + str(self.cumgpa))
        if self.minor != "":
            print("also, a minor: " + self.minor)
        for key in self.history.keys():
            print(key, self.history[key])

    def quickPrint(self):
        # Prints a quick summary of the student
        print(self.name + " is pursuing a major in " + self.major + " with a cumulative GPA of " + str(self.cumgpa))
        # if self.minor != "":
        #     print("also, a minor: " + self.minor)

    def getSemClasses(self, semester):
        # Returns a list of all classes taken in a given semester
        if semester not in self.history.keys():
            return
        return self.history[semester].courses

    def getClasses(self):
        # Returns a list of all classes taken by the student
        classes = []
        for key in self.history.keys():
            for course in self.history[key].courses:
                classes.append(course)
        return classes

    def getSemesterGPAs(self):
        # Returns a list of all semester GPAs with the semester names
        gpas = []
        names = []
        for key in self.history.keys():
            if self.history[key].termGPA != 0.0:
                gpas.append(self.history[key].termGPA)
                names.append(key)
        return gpas, names

    def plotStudentProgress(self):
        # Plots a graph of the student's progress over time
        gpas, names = self.getSemesterGPAs()
        if len(gpas) <= 1:
            print("Not enough data to plot")
            return
        plt.figure(figsize=(10, 5))
        sns.lineplot(x=names, y=gpas)
        plt.suptitle(self.name + "'s GPA Progression", fontsize=18)
        plt.title("Major: " + self.major, fontsize=12)

        plt.xlabel("Semester")
        plt.ylabel("GPA")
        plt.show()

    # def __str__(self):
    #     return self.name + "is taking " + str(len(self.history)) + " courses: " + "\n".join(
    #         [str(crs) + "\n" for crs in self.history])


def extractSemesterCourses(semester, transcript):
    # extracts course info from any given semester and returns a list of course objects
    undergrad = transcript.find("Beginning of Undergraduate  Record")
    currSemIndex = transcript.find(semester, undergrad)
    currSem = transcript[currSemIndex:transcript.find("Term GPA", currSemIndex) - 38]
    currSem = currSem[currSem.find("Points") + 7:]

    termGPA = transcript[transcript.find("Term GPA", currSemIndex) + 9: transcript.find("Term GPA", currSemIndex) + 14]

    tempCode = ""
    tempName = ""
    tempCredits = ""
    tempInstructor = ""
    tempSubject = ""
    tempGrade = ""
    courses = []

    for line in currSem.split("\n"):
        if line[0:3].isalpha():
            # if it has a subject in the beginning
            temp = line.split(" ")
            if (len(temp[0])) > 4:
                continue
            tempSubject = temp[0]
            tempCode = temp[1]
            i = 2
            while i < len(temp) - 1:
                if temp[i].find('.') != -1 and "".join(temp[i].split(".")).isnumeric():
                    break
                tempName += temp[i] + " "
                i += 1
            tempCredits = temp[i]
            tempGrade = temp[i + 2] if temp[i + 2] != "Progress" else "IP"
        if line.find("Instructor:") != -1:
            # if it has an instructor's details
            temp = line[line.find("Instructor:") + 15:len(line)].split(' ')
            for item in temp:
                if item != '':
                    tempInstructor += item + " "
            crse = Course(tempName, tempSubject, tempCredits, tempCode, tempInstructor, tempGrade, semester)
            courses.append(crse)
            tempCode = ""
            tempName = ""
            tempCredits = ""
            tempInstructor = ""
            tempSubject = ""

    return courses, termGPA


def mainMenu():
    # Main menu for the program
    print("\u001b[32mTranscript management time!\033[0m")
    members = loadTranscripts("E:\\trspts\\")
    temp = True
    while temp:
        print("Please select an option:")
        print("1. Get info for a student")
        print("2. Get info for all students")
        print("3. Group tools")
        print("4. Exit")
        print("\n" * 3)
        choice = input("Enter your choice: ")
        if choice == "1":
            singleStudent(members)
        elif choice == "2":
            wholeOrg(members)
        elif choice == "3":
            groupMenu(members)
        elif choice == "4":
            print("\033[31;1;4mExiting... \033[0m")
            return
        else:
            print("Invalid choice")

def groupMenu(mb):
    # Menu for the group options
    print("\u001b[32mGroup tools!\033[0m")
    print("Please select an option:")
    print("1. Group students by major/minor")
    print("2. Group students by classes")
    print("3. Go back")
    print("\n" * 3)
    choice = input("Enter your choice: ")
    while int(choice) < 1 or int(choice) > 4:
        choice = input("Wrong entry, try again: ")
    if choice == "1":
        majors = groupStudentsMM(mb)
        plotPieChartMMclass(majors)
        # if len(minors) > 0:
        #     plotPieChartMMclass(minors)
    elif choice == "2":
        cls = groupStudentsClass(mb, "SP 2023")
        plotPieChartSubjects(cls)

    elif choice == "3":
        return


def getTranscript(filename):
    ts = ""
    for page in PdfReader(filename).pages:
        ts += page.extract_text()
    return ts


def getStudentName(transcript):
    # returns the name of the student
    #print(transcript)
    temp = transcript.split('\n')
    try:
        temp = temp[1][temp[1].find("Name:") + 6:]
    except:
        print("Error in getStudentName", temp)
        exit()
    temp = [item for item in temp.split(' ') if item != '']
    name = ""
    for item in temp:
        name += item + " "
    return name[:-1]


def getStudentId(transcript):
    # returns the student ID
    temp = transcript.split('\n')
    temp = temp[2][temp[1].find("Student ID:") + 12:]
    temp = [item for item in temp.split(' ') if item != '']
    return temp[0]


def getStudentCumulative(transcript):
    # returns the cumulative GPA of the student
    temp = transcript.split('\n')
    for line in temp:
        if "Cum GPA: " in line:
            return line[8:14]


def generateStudent(transcript):
    # makes a student object
    semesters = []
    tempIndex = transcript.find("Beginning of Undergraduate  Record") + 35
    major = ""
    minor = ""
    ts = transcript[tempIndex + 2:]
    ts = ts.split("\n")
    for i in range(len(ts)):
        if (ts[i].find('FA 20') != -1) or (ts[i].find('SP 20') != -1) or (ts[i].find('SU 20') != -1) or (
                ts[i].find('WI 20') != -1):
            semesters.append(ts[i])
        if ts[i].find("Plan:") != -1:
            if ts[i].find("Unofficial Transcript") != -1:
                temp = ts[i][6:ts[i].find("Unofficial Transcript")]
            else:
                temp = ts[i][6:]
            if "Major" in temp:
                major = temp[:temp.find("Major") - 2]
            if "Minor" in temp:
                minor = temp[:temp.find("Minor") - 5]

    student = Student(getStudentName(transcript), int(getStudentId(transcript)), major, minor,
                      getStudentCumulative(transcript))

    for semester in semesters:
        tempsem = extractSemesterCourses(semester, transcript)
        student.addSemester(semester, Semester(tempsem[0], tempsem[1]))

    return student


def groupStudentsMM(studentList):
    # groups students by major and minor
    majors = {}
    #minors = {}
    for student in studentList:
        if student.major not in majors.keys():
            majors[student.major] = []
        #elif student.minor not in minors.keys():
            #minors[student.minor] = []
        majors[student.major].append(student)
        #if student.minor != "":
            #minors[student.minor].append(student)

    for major in majors:
        if len(majors[major]) > 1:
            print("\nGroup found for " + major)
            for student in majors[major]:
                print("\t-\t", student.name)
    # for minor in minors:
    #     if len(minors[minor]) >= 1:
    #         print("Group found for " + minor)
    #         for student in minors[minor]:
    #             print(student.name)
    #
    print('\n')
    return majors#, minors


def groupStudentsClass(studentList, semester):
    # groups students by classes they're taking, by semester specifically
    classes = {}
    for student in studentList:
        if semester not in student.history.keys():
            continue
        for course in student.history[semester].courses:
            if (course.subject + course.code) not in classes.keys():
                classes[course.subject + course.code] = []
            classes[course.subject + course.code].append(student)
    for cls in classes:
        if len(classes[cls]) > 1:
            print("\nGroup found for " + cls)
            for student in classes[cls]:
                print("\t-\t", student.name)
    print('\n')
    return classes


def plotPieChartMMclass(dataset):
    # plots a pie chart of majors/minors
    frequencies = {}
    for key in dataset.keys():
        frequencies[key] = len(dataset[key])
    plt.rcParams['font.size'] = 8.0
    plt.rcParams['figure.figsize'] = 12, 8
    plt.pie(frequencies.values(), labels=frequencies.keys(), autopct='%1.1f%%')
    plt.show()


def plotPieChartSubjects(dataset):
    # plots a pie chart of subjects currently being taken
    frequencies = {}
    for key in dataset.keys():
        frequencies[key[:-4]] = len(dataset[key])
    plt.pie(frequencies.values(), labels=frequencies.keys(), autopct='%1.1f%%')
    plt.show()


def loadTranscripts(path):
    # loads all transcripts in a given directory and returns as a list of students
    transcripts = []
    for file in os.listdir(path):
        if file.endswith(".pdf"):
            #print(file)
            transcript = getTranscript(path + file)
            stu = generateStudent(transcript)
            transcripts.append(stu)
    print("Loaded " + str(len(transcripts)) + " transcripts.")
    return transcripts


def getStudentByName(name, studentList):
    returnables = []
    for student in studentList:
        if name in student.name:
            returnables.append(student)

    if len(returnables) > 1:
        print("More than one student found. Select a choice: ")
        for i in range(len(returnables)):
            print(str(i + 1) + ": " + returnables[i].name)
        choice = int(input())
        return returnables[choice - 1]
    elif len(returnables) == 1:
        return returnables[0]
    else:
        print("No student found. Try again.")
        return None


def createClassDist(studentList, semester):
    # plots a histogram of the distribution of class subjects taken by students
    classes = {}
    if semester == "all":
        for student in studentList:
            for course in student.getClasses():
                if course.subject in classes:
                    classes[course.subject] += 1
                else:
                    classes[course.subject] = 1
    else:
        for student in studentList:
            if student.getSemClasses(semester) is None:
                continue
            for course in student.getSemClasses(semester):
                if (course.subject + course.code) in classes:
                    classes[course.subject + course.code] += 1
                else:
                    classes[course.subject + course.code] = 1

    # plot the dictionary
    plt.title("Class Distribution For " + semester)
    plt.bar(classes.keys(), classes.values(), color='g')
    plt.show()


def singleStudent(members):
    # mini menu that either prints out all students or allows user to search student by name
    print("\n"*100)
    print("\u001b[32mSingle Student Menu\u001b[0m")
    print("1: Print all students")
    print("2: Search for student by name")
    print("3: Return to main menu")
    print("\n"*3)
    choice = int(input("Enter your choice:"))
    if choice == 1:
        print('\n')
        print("All students: ")
        for student in members:
            print("\t-\t", student.name)
        print('\n')
        singleStudent(members)
        return
    elif choice == 2:
        name = input("Enter name, or enter L to return: ")
        if name == "L":
            return
        stu = getStudentByName(name, members)
        if stu is not None:
            stu.prStu()
            stu.plotStudentProgress()
        else:
            print("No student found. Try again.")
            return
    elif choice == 3:
        return
    else:
        print("Invalid choice. Try again.")
        singleStudent(members)
        return




def wholeOrg(members):
    #menu for whole organization commands
    print("\n"*5)
    print("\u001b[32mWhole Organization Menu\u001b[0m")
    print("1: Plot pie chart of majors/minors")
    print("2: Plot pie chart of subjects taken")
    print("3: Plot histogram of class distribution")
    print("4: Print all students with GPA")
    print("5: Return to main menu")
    print("\n"*3)
    choice = int(input("Enter your choice:"))
    if choice == 1:
        majors = groupStudentsMM(members)
        plotPieChartMMclass(majors)
        wholeOrg(members)
        return
    elif choice == 2:
        classes = groupStudentsClass(members, "all")
        plotPieChartSubjects(classes)
        wholeOrg(members)
        return
    elif choice == 3:
        createClassDist(members, "all")
        wholeOrg(members)
        return
    elif choice == 4:
        print("\n")
        for student in members:
            student.quickPrint()
        print("\n")
        wholeOrg(members)
        return
    elif choice == 5:
        return
    else:
        print("Invalid choice. Try again.")
        wholeOrg(members)
        return






mainMenu()
