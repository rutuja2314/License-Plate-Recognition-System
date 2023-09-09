import cv2
import pytesseract
import mysql.connector
framewidth = 640
frameheight = 480
plateCascade = cv2.CascadeClassifier("C:\Program Files\haarcascade_russian_plate_number.xml")
minArea = 500
count = 0

color = (255, 0, 255)
cap = cv2.VideoCapture(0)
cap.set(3, framewidth)
cap.set(4, frameheight)
cap.set(10,150)
while True:
    success, image = cap.read()
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    plates = plateCascade.detectMultiScale(gray_img, 1.1, 4)

    for(x, y, w, h) in plates:
        area = w * h
        if area >minArea:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(image, "Number Plate", (x,y-5), cv2.FONT_HERSHEY_COMPLEX_SMALL,1,color,2)
            imgRoi = image[y:y+h,x:x+w]
            cv2.imshow("ROI", imgRoi)
    cv2.imshow("Result", image)
    if cv2.waitKey(1) & 0xFF == ord('s'):
       # cv2.imwrite("C:\Python\Resources\Scanned\Plate_"+str(count)+".jpg",imgRoi)
        #cv2.rectangle(image,(0,200),(640,300),(0,255,0),cv2.FILLED)
        #cv2.putText(image,"Scan Saved",(150,265),cv2.FONT_HERSHEY_DUPLEX,2,(0,0,255),2)
        cv2.imshow("Result",image)
        cv2.waitKey(1000)
        count += 1
       # cv2.distroyAllWindows()

       # gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # canny edge detection
        canny_edge = cv2.Canny(gray_img, 170, 200)

        # find contours based on edges
        contours, new = cv2.findContours(canny_edge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]

        # initialize plate contour and x,y coordinates
        contour_with_plate = None
        plate = None
        x = None
        y = None
        w = None
        h = None

        # find the contour with corners and create ROI around it
        for contour in contours:
            # find perimeter of contour
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.01 * perimeter, True)
            if len(approx) == 4:  # see whether its rectangle
                contour_with_plate = approx
                x, y, w, h = cv2.boundingRect(contour)
                plate = gray_img[y:y + h, x:x + w]
                break

        # remove noise
        # plate = cv2.bilateralFilter(plate, 11, 17, 17)
        # (thresh, plate) = cv2.threshold(plate, 150, 180, cv2.THRESH_BINARY)

        # Text Recognition
        text = pytesseract.image_to_string(plate)
        lplate = text.strip()
        # draw plate and write text
        image = cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
        image = cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 0), 2)
        # (x-100, y-50), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), cv2.LINE_AA
        print("License Plate Number: ", lplate)
        cv2.imshow("License Plate Detection", image)
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="1234", database="license")
        mycursor = mydb.cursor()
       # query = "select * from info where l_plate='MH12'DE1433"
        query = """select * from info where l_plate = %s"""
        #mycursor.execute(query)
        mycursor.execute(query, (lplate,))
        result = mycursor.fetchall()
        for i in result:
                print("License Plate Number =  ",i[0])
                print("Owner Name           =  ",i[1])
                print("Vehicle Class        =  ",i[2])
                print("Fuel Type            =  ",i[3])
                print("Registration No      =  ",i[4])
                print("Registration Date    =  ",i[5])
                print("Fitness Upto         =  ",i[6])
                print("PUCC No              =  ",i[7])
                print("Insurance Policy No  =  ",i[8])
        cv2.waitKey(0)