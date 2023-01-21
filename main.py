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
        return "\t" + self.subject + self.code + " - " + self.name + " - " + self.instructor + " - " + str(self.credits) + " units" + " - " + self.__grade


class Semester:
    # courses for a semester
    def __init__(self, _courses, _termGPA):
        self.courses = _courses
        self.termGPA = float(_termGPA)

    def __str__(self):
        return "Term GPA: " + str(self.termGPA) + "\n" + "\n".join([str(course) for course in self.courses])


class Student:
    # Class for a student taking multiple courses
    def __init__(self, _name, _id, _major, _minor, _cumgpa):
        self.name = _name
        self.id = _id
        self.major = _major
        self.minor = _minor
        self.cumgpa = float(_cumgpa)
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
        if self.minor != "":
            print("also, a minor: " + self.minor)

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
            while i < len(temp) - 1 and temp[i].find('.') == -1:
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


def getTranscript(filename):
    ts = ""
    for page in PdfReader(filename).pages:
        ts += page.extract_text()
    return ts


def getStudentName(transcript):
    # returns the name of the student
    temp = transcript.split('\n')
    temp = temp[1][temp[1].find("Name:") + 6:]
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
            if (ts[i].find("Unofficial Transcript") != -1):
                temp = ts[i][6:ts[i].find("Unofficial Transcript")]
            else:
                temp = ts[i][6:]
            if "Major" in temp:
                major = temp[:temp.find("Major") - 2]
            if "Minor" in temp:
                minor = temp[:temp.find("Minor") - 5]

    student = Student(getStudentName(transcript), int(getStudentId(transcript)), major, minor, getStudentCumulative(transcript))

    for semester in semesters:
        tempsem = extractSemesterCourses(semester, transcript)
        student.addSemester(semester, Semester(tempsem[0], tempsem[1]))

    return student


def loadTranscripts(path):
    # loads all transcripts in a given directory and returns as a list of students
    transcripts = []
    for file in os.listdir(path):
        if file.endswith(".pdf"):
            transcript = getTranscript(path + file)
            stu = generateStudent(transcript)
            transcripts.append(stu)
    return transcripts


def main():
    allstudents = loadTranscripts("E:\\trspts\\")
    allstudents[5].plotStudentProgress()

main()
