from tkinter import *
from PIL import Image, ImageTk
from tkinter import filedialog
import Speed_Detection as sd
import cv2
import imageio

class Window(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.master = master
        self.catchOpposite = BooleanVar()
        self.catchOpposite.set(False)        
        self.overSpeed = BooleanVar()
        self.overSpeed.set(False)        
        self.pos = []
        self.line = []
        self.rect = []
        self.master.title("GUI")
        self.pack(fill=BOTH, expand=1)

        self.counter = 0

        menu = Menu(self.master)
        self.master.config(menu=menu)
        
        def toggleTrackOppsite(event=None):
        
            if self.catchOpposite.get() == False:
                    self.catchOpposite.set(True)

            elif self.catchOpposite.get() == True:
                    self.catchOpposite.set(False)
        
        def toggleTrackOverspeed(event=None):
            if self.overSpeed.get() == False:
                    self.overSpeed.set(True)

            elif self.overSpeed.get() == True:
                    self.overSpeed.set(False)

        file = Menu(menu)
        file.add_command(label="Open", command=self.open_file)
        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)
        
        analyze = Menu(menu)
        analyze.add_command(label="Region of Interest", command=self.regionOfInterest)
        analyze.add_checkbutton(label="Check vehicles in opposite direction also", onvalue=1, offvalue=0, command = toggleTrackOppsite)
        analyze.add_checkbutton(label="Check over speeding vehicles only", onvalue=1, offvalue=0, command = toggleTrackOverspeed)
        menu.add_cascade(label="Analyze", menu=analyze)

        self.filename = "Images/home.jpg"
        self.imgSize = Image.open(self.filename)
        self.tkimage =  ImageTk.PhotoImage(self.imgSize)
        self.w, self.h = (1366, 768)
        
        self.canvas = Canvas(master = root, width = self.w, height = self.h)
        self.canvas.create_image(20, 20, image=self.tkimage, anchor='nw')
        self.canvas.pack()

    def open_file(self):
        self.filename = filedialog.askopenfilename()
        self.cap = cv2.VideoCapture(self.filename)

        reader = imageio.get_reader(self.filename)
        fps = reader.get_meta_data()['fps'] 

        ret, image = self.cap.read()
        cv2.imwrite('Images/preview.jpg', image)

        self.show_image('Images/preview.jpg')

    def show_image(self, frame):
        self.imgSize = Image.open(frame)
        self.tkimage =  ImageTk.PhotoImage(self.imgSize)
        self.w, self.h = (1366, 768)

        self.canvas.destroy()

        self.canvas = Canvas(master = root, width = self.w, height = self.h)
        self.canvas.create_image(0, 0, image=self.tkimage, anchor='nw')
        self.canvas.pack()

    def regionOfInterest(self):
        root.config(cursor="plus") 
        # self.canvas.bind("<Button-1>", self.imgClick) 
        
        # Select ROI
        img = cv2.imread('Images/preview.jpg')
        r = cv2.selectROI("select the area", img)
        cv2.destroyAllWindows()
        cv2.waitKey(0)
        sd.trackMultipleObjects1(self.cap, r, self.catchOpposite, self.overSpeed)


    def client_exit(self):
        exit()

    def imgClick(self, event):

        if self.counter < 4:
            x = int(self.canvas.canvasx(event.x))
            y = int(self.canvas.canvasy(event.y))
            self.line.append((x, y))
            self.pos.append(self.canvas.create_line(x - 5, y, x + 5, y, fill="red", tags="crosshair"))
            self.pos.append(self.canvas.create_line(x, y - 5, x, y + 5, fill="red", tags="crosshair"))
            self.counter += 1

        # elif self.counter < 4:
        #     x = int(self.canvas.canvasx(event.x))
        #     y = int(self.canvas.canvasy(event.y))
        #     self.rect.append((x, y))
        #     self.pos.append(self.canvas.create_line(x - 5, y, x + 5, y, fill="red", tags="crosshair"))
        #     self.pos.append(self.canvas.create_line(x, y - 5, x, y + 5, fill="red", tags="crosshair"))
        #     self.counter += 1

        if self.counter == 4:
            #unbinding action with mouse-click
            self.canvas.unbind("<Button-1>")
            root.config(cursor="arrow")
            self.counter = 0

            #show created virtual line
            print(self.line)
            print(self.rect)
            img = cv2.imread('Images/preview.jpg')
            cv2.line(img, self.line[0], self.line[1], (0, 255, 0), 3)
            cv2.line(img, self.line[2], self.line[3], (0, 255, 0), 3)
            cv2.imwrite('Images/copy.jpg', img)
            self.show_image('Images/copy.jpg')

            #image processing
            self.points = self.line[0], self.line[1], self.line[2], self.line[3]
            sd.trackMultipleObjects(self.cap, self.points, self.catchOpposite, self.overSpeed)
            print("Executed Successfully!!!")

            #clearing things
            self.line.clear()
            self.rect.clear()
            for i in self.pos:
                self.canvas.delete(i)



root = Tk()
app = Window(root)
root.geometry("%dx%d"%(535, 380))
root.title("Traffic Violation")

root.mainloop()