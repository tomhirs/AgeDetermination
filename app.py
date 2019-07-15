import sqlite3
import math
import cv2
import tkinter as tk
from tkinter import filedialog
from person import Person

WIDTH = 720
HEIGHT = 480
personList = []
person = Person("", 0, 0, 0, 0)
conn = sqlite3.connect('./Database/database.db')
c = conn.cursor()

def get_points(im):
    # Set up data to send to mouse handler
    data = {}
    data['im'] = im.copy()
    data['points'] = []

    # Set the callback function for any mouse event
    cv2.imshow("Image", im)
    cv2.setMouseCallback("Image", mouse_handler, data)
    cv2.waitKey(0)

    return data['points']

def mouse_handler(event, x, y, flags, data):
    # For dot placement on image
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(data['im'], (x, y), 3, (0, 0, 255), 5, 16);
        cv2.imshow("Image", data['im']);
        if len(data['points']) < 8: # This can be changed for more or less points
            data['points'].append([x, y])

def insertIntoDatabase():
    # Insert persons data into database
    try:
        person.age = ageEntry.get()
        person.gender = genderSelection.get(genderSelection.curselection())
        if(person.age == ""):
            outputLabel['text'] += "\nError! Please enter correct age!"
        else:
            query = "INSERT INTO persons(gender, age, head_height, leg_height, shoulders_hips) "
            query += "VALUES ('{}', {}, {}, {}, {})".format(person.gender, person.age, person.headHeight, person.ratioLegs, person.ratioSH)
            print(query)
            with conn:
                c.execute("INSERT INTO persons(gender, age, head_height, leg_height, shoulders_hips) VALUES (:gender, :age, :headHeight, :ratioLegs, :ratioSH)",
                           {'gender': person.gender, 'age': person.age, 'headHeight': person.headHeight, 'ratioLegs': person.ratioLegs, 'ratioSH': person.ratioSH})
    except:
        outputLabel['text'] += "\nError! Please select gender!"
    

def getApproximation(personList, person):
    # Calculate age approximation based on
    # Database entries
    headHeight = 100
    ratioLegs = 100
    ratioSH = 100
    perDict = {}
    age = 0
    for per in personList:
        if abs(per.headHeight - person.headHeight) < headHeight:
            headHeight = abs(per.headHeight - person.headHeight)
            perDict["Head"] = per
        if abs(per.ratioLegs - person.ratioLegs) < ratioLegs:
            ratioLegs = abs(per.ratioLegs - person.ratioLegs)
            perDict["Legs"] = per
        if abs(per.ratioSH - person.ratioSH) < ratioSH:
            ratioSH = abs(per.ratioSH - person.ratioSH)
            perDict["SH"] = per
    for per in perDict:
        age += perDict[per].age
    age = int(age / 3)
    return age

def calculateAge():
    # Get entrys from database based on gender
    # Check which are closest to messured
    # Return that persons age, or an estimationtry:
    person.gender = genderSelection.get(genderSelection.curselection())
    personList.clear()
    query = "SELECT * FROM persons WHERE gender={}".format(person.gender)
    print(query)
    c.execute("SELECT * FROM persons WHERE gender=:gender", {'gender':person.gender})
    for row in c.fetchall():
        tempPerson = Person(row[1], row[2], row[3], row[4], row[5])
        personList.append(tempPerson)
    print(personList)
    person.age = getApproximation(personList, person)
    outputLabel['text'] += "\nAge: " + str(person.age)

def getImage():
    # After button Browse is pressed
    # Loads the image and calculates
    # The ratios
    outputLabel['text'] = "Use mouse to first select top of head, than bottom of chin"
    outputLabel['text'] += "\nAfter that, select top of the leg and bottom of the leg"
    outputLabel['text'] += "\nLast select shoulder width and hips width"
    outputLabel['text'] += "\nAnd select the gender of the person below"
    
    imgPath = filedialog.askopenfilename()
    entry.delete(0, 'end')
    entry.insert(0, imgPath)
    if len(entry.get()) != 0:
        # Load image
        img = cv2.imread(imgPath)

        # Resize window
        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Image', 300,500)

        pts = get_points(img)
        if len(pts) != 0:
            cv2.line(img, (pts[0][0], pts[0][1]), (pts[1][0], pts[1][1]), (0,0,255), 2)
            cv2.line(img, (pts[0][0], pts[0][1]), (pts[3][0], pts[3][1]), (0,0,255), 2)
            cv2.line(img, (pts[2][0], pts[2][1]), (pts[3][0], pts[3][1]), (0,0,255), 2)
            cv2.line(img, (pts[4][0], pts[4][1]), (pts[5][0], pts[5][1]), (0,0,255), 2)
            cv2.line(img, (pts[6][0], pts[6][1]), (pts[7][0], pts[7][1]), (0,0,255), 2)

            head = math.sqrt(math.pow((pts[0][0] - pts[1][0]),2)+math.pow((pts[1][1] - pts[0][1]),2))
            height = math.sqrt(math.pow((pts[0][0] - pts[3][0]),2)+math.pow((pts[0][1] - pts[3][1]),2))
            legs = math.sqrt(math.pow((pts[2][0] - pts[3][0]),2)+math.pow((pts[2][1] - pts[3][1]),2))
            shoulders = math.sqrt(math.pow((pts[4][0] - pts[5][0]),2)+math.pow((pts[4][1] - pts[5][1]),2))
            hips = math.sqrt(math.pow((pts[6][0] - pts[7][0]),2)+math.pow((pts[6][1] - pts[7][1]),2))
            ratioLegs = legs / height * 100
            ratioSH = shoulders / hips
            headHeight = height / head
            name = imgPath.split("/")
            person.age = 0
            person.headHeight = headHeight
            person.ratioLegs = ratioLegs
            person.ratioSH = ratioSH
            
            outputLabel['text'] = name[len(name)-1]
            outputLabel['text'] += "\nHead lenght: " + str(head)
            outputLabel['text'] += "\nBody lenght: " + str(height)
            outputLabel['text'] += "\nHead lengths in body length: " + str(headHeight)
            outputLabel['text'] += "\nLeg to body ratio: " + str(ratioLegs) + "%"
            outputLabel['text'] += "\nShoulder to hips ratio: " + str(ratioSH)
            
        # Resize window
        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Image', 300,500)
        cv2.imshow('Image', img)

if __name__ == "__main__":
    # Main part of the program
    # Creation of GUI
    root = tk.Tk()

    canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
    canvas.pack()

    bgImage = tk.PhotoImage(file='./images/background.png')
    bgLabel = tk.Label(root, image=bgImage)
    bgLabel.place(relwidth=1, relheight=1)

    frameInput = tk.Frame(root, bg='#f97235', bd=5)
    frameInput.place(relx=0.125, rely=0.1, relwidth=0.75, relheight=0.075)

    entry = tk.Entry(frameInput)
    entry.place(relwidth=0.8, relheight=1)

    buttonBrowse = tk.Button(frameInput, text="Browse", command=getImage)
    buttonBrowse.place(relx=0.85, relwidth=0.15, relheight=1)

    frameOutput = tk.Frame(root, bg='#f97235', bd=5)
    frameOutput.place(relx=0.125, rely=0.25, relwidth=0.75, relheight=0.55)

    outputLabel = tk.Label(frameOutput, anchor='nw', justify='left')
    outputLabel.place(relwidth=1, relheight=1)

    frameAgeInput = tk.Frame(root, bg='#f97235', bd=5)
    frameAgeInput.place(relx=0.125, rely=0.85, relwidth=0.75, relheight=0.095)

    ageLabel = tk.Label(frameAgeInput, text="Insert correct age:", anchor='w', justify='left')
    ageLabel.place(relwidth=0.2, relheight=1)
            
    ageEntry = tk.Entry(frameAgeInput)
    ageEntry.place(relx=0.25, relwidth=0.15, relheight=1)

    genderSelection = tk.Listbox(frameAgeInput)
    genderSelection.place(relx=0.45, relwidth=0.15, relheight=1)
    genderSelection.insert(1, "Male")
    genderSelection.insert(2, "Female")

    buttonCalculate = tk.Button(frameAgeInput, text="Calculate", command=calculateAge)
    buttonCalculate.place(relx=0.65, relwidth=0.15, relheight=1)

    buttonInsert = tk.Button(frameAgeInput, text="Insert", command=insertIntoDatabase)
    buttonInsert.place(relx=0.85, relwidth=0.15, relheight=1)
    
    root.mainloop()

    conn.close()
