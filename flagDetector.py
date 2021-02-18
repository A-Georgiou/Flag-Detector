from tkinter import *
import pyautogui
import cv2
import os
from skimage.metrics import structural_similarity as compare_ssim
import numpy as np

"""
Flag Detector - Click and Drag
"""
class Application():
    def __init__(self, master):
        self.master = master
        self.rect = None
        self.x = self.y = 0
        self.start_x = None
        self.start_y = None
        self.curX = None
        self.curY = None
        self.first_click = None
        
        root.attributes("-transparent", "blue")
        root.geometry('500x200')  # set new geometry
        root.title('Flag Detector')
        
        self.menu_frame = Frame(master, bg="blue")
        self.menu_frame.pack(fill=BOTH, expand=YES)

        self.buttonBar = Frame(self.menu_frame,bg="white")
        self.buttonBar.pack(fill=BOTH,expand=YES)

        self.snipButton = Button(self.buttonBar, width=10, command=self.createScreenCanvas, background="purple", text="Scan Flag", font=("Courier", 16))
        self.snipButton.pack(expand=YES)
        
        self.master_screen = Toplevel(root)
        self.master_screen.withdraw()
        self.master_screen.attributes("-transparent", "blue")
        
        self.picture_frame = Frame(self.master_screen, background = "blue")
        self.picture_frame.pack(fill=BOTH, expand=YES)
        
        self.FRAME = Label(self.menu_frame, text="", bg="white", fg="black", font=("Courier", 16))
        self.FRAME.pack(fill=BOTH, expand=YES)
        
        self.flags = self.generateFlags()
        
    #Imports and converts all images into array 
    def generateFlags(self):
        flags = []
        full_path = os.path.abspath("Flags")
        directory = os.fsencode(full_path)
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            filepath = "Flags/" + filename
            image2 = cv2.imread(filepath)
            flags.append([image2, filename])
        print('flags generated')
        return flags


    """
    Function calculateDifference
    Creates RGB Histogram and creates probability prediction score from the comparison between the screenshot and the flags
    Uses structural similarity index to detect the difference between each flag and the screenshot
    Multiplied by 1/d (due to Bhattacharyya comparison) to give an overall score for each flag
    """
    def calculateDifference(self, image):            
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resize_height = 150
        scale_percent = (resize_height / image_gray.shape[1])*100
        resize_width = int(image_gray.shape[0] * scale_percent / 100) 
        image_gray = cv2.resize(image_gray, (resize_height, resize_width))
        minFlag = ""
        minFlagVal = 0
        
        for file, filename in self.flags:
            image2 = file
            image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            #image2_gray = image2
            (H,W) = image_gray.shape
            image2_gray = cv2.resize(image2_gray, (W,H))
            (score, diff) = compare_ssim(image_gray, image2_gray, full=True)
            
            histr_screen = cv2.calcHist([image_gray],[0],None,[256],[0,256])
            histr_screen = cv2.normalize(histr_screen, histr_screen).flatten()
            
            histr_flag = cv2.calcHist([image2],[0],None,[256],[0,256])
            histr_flag = cv2.normalize(histr_flag, histr_flag).flatten()  
                
            d = cv2.compareHist(histr_screen, histr_flag, cv2.HISTCMP_BHATTACHARYYA)
            overall_score = score * (1/d)
            
            if overall_score > minFlagVal:
                minFlagVal = overall_score
                minFlag = filename
                self.FRAME['text'] = minFlag.replace(".png", "")
        
        
    def takeBoundedScreenShot(self, x1, y1, x2, y2):
        im = pyautogui.screenshot(region=(x1, y1, x2, y2))
        self.master_screen.attributes('-alpha', 0)
        open_cv_image = np.array(im) 
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        self.calculateDifference(open_cv_image)
        
    #Draw canvas on selection
    def createScreenCanvas(self):
        self.master_screen.deiconify()
        root.withdraw()

        self.screenCanvas = Canvas(self.picture_frame, cursor="cross", bg="grey")
        self.screenCanvas.pack(fill=BOTH, expand=YES)

        self.screenCanvas.bind("<ButtonPress-1>", self.on_button_press)
        self.screenCanvas.bind("<Motion>", self.on_motion)
        self.screenCanvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.master_screen.attributes('-fullscreen', True)
        self.master_screen.attributes('-alpha', 0.15)
        self.master_screen.lift()
        self.master_screen.attributes("-topmost", True)
    
    def on_button_press(self, event):
        self.first_click = True
        self.start_x = self.screenCanvas.canvasx(event.x)
        self.start_y = self.screenCanvas.canvasy(event.y)
        self.rect = self.screenCanvas.create_rectangle(self.x, self.y, 1, 1, outline='red', width=3, fill="blue")
    
    def on_button_release(self, event):
        if self.start_x <= self.curX and self.start_y <= self.curY:
            self.takeBoundedScreenShot(self.start_x, self.start_y, self.curX - self.start_x, self.curY - self.start_y)
        elif self.start_x >= self.curX and self.start_y <= self.curY:
            self.takeBoundedScreenShot(self.curX, self.start_y, self.start_x - self.curX, self.curY - self.start_y)
        elif self.start_x <= self.curX and self.start_y >= self.curY:
            self.takeBoundedScreenShot(self.start_x, self.curY, self.curX - self.start_x, self.start_y - self.curY)
        elif self.start_x >= self.curX and self.start_y >= self.curY:
            self.takeBoundedScreenShot(self.curX, self.curY, self.start_x - self.curX, self.start_y - self.curY)

        self.screenCanvas.destroy()
        self.master_screen.withdraw()
        root.deiconify()
        return event

    #When dragging mouse across screen
    def on_motion(self, event):
        if self.first_click != None:
            self.curX, self.curY = (event.x, event.y)
            self.screenCanvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

if __name__ == '__main__':
    root = Tk()
    app = Application(root)
    root.mainloop()
    