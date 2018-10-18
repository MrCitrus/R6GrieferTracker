import pytesseract,Database,numpy, cv2
from PIL import ImageGrab, Image
from PySide2.QtCore import Signal, QObject
import re


class siege_image_process(QObject):
    im_new_image = Signal(str)
    im_player_path_dict = Signal(dict)
    def __init__(self):
        super().__init__()
        self.screenshot = None
        self.kill_cam_img   = None
        self.score_board_headline_img = None
        self.top_scoreboard_img = None
        self.bottom_scoreboard_img = None
        self.score_board_headline_text = None
        self.score_board_top_text = None
        self.score_board_bottom_text = None
        self.kill_cam_text = None
        self.database_conn = Database.RainbowDB()
        self.database_conn.db_new_image.connect(self.im_new_image.emit)
        self.database_conn.db_player_path_dict.connect(self.im_player_path_dict.emit)
        self.addvalue = 0.051 #height of scoreboard name boxes

    def process_score_board(self):

        self.tempplayerlist = list()
        for tb in range(2):
            for x in range(5):
                if tb == 0:
                    self.test_screenshot = self.screenshot.crop((int(self.screenshot.width * .24479),int(self.screenshot.height*(.2777+(self.addvalue*x))), int(self.screenshot.width*.3645),int(self.screenshot.height*(.2777+(self.addvalue*x)))+51))
                elif tb ==1:
                    self.test_screenshot =  self.screenshot.crop((int( self.screenshot.width * .2449),int( self.screenshot.height*(.5583+(self.addvalue*x))), int( self.screenshot.width*.36458),int( self.screenshot.height*(.5583+(self.addvalue*x)))+51))


                self.test_screenshot = self.test_screenshot.resize((int(self.test_screenshot.width*1.5), int(self.test_screenshot.height*1.5)))


                self.playername = (pytesseract.image_to_string(self.test_screenshot, lang = 'eng')).replace(" ","")
                self.tempplayerlist.append(self.playername)


        self.database_conn.player_search(self.tempplayerlist)
        print(self.tempplayerlist)

    def process_kill_cam(self):

        self.griefer = (self.kill_cam_text.replace("KILLED YOU", "")).replace(" ","")
        self.griefer = re.sub(r'[^a-zA-Z0-9_\-.]', "", self.griefer)

        print("The griefer is: ", self.griefer)
        self.database_conn.add_player(self.griefer, self.screenshot)

    def check_kcam_sboard(self):

        self.screenshot = ImageGrab.grab()
        self.score_board_headline_img = self.screenshot.crop((int(self.screenshot.width * .19), int(self.screenshot.height * .8555), int(self.screenshot.width * .355), int(self.screenshot.height * .888)))
        self.score_board_headline_img = self.score_board_headline_img.resize((int(self.score_board_headline_img.width * 1.5), int(self.score_board_headline_img.height * 1.5)))
        self.score_board_headline_img = cv2.cvtColor(numpy.array(self.score_board_headline_img), cv2.COLOR_RGB2BGR)
        self.lower = numpy.array([152,152,152])
        self.upper = numpy.array([255,255,255])
        self.score_board_headline_img = cv2.inRange(self.score_board_headline_img, self.lower, self.upper)
        self.score_board_headline_img = cv2.bitwise_not(self.score_board_headline_img)
        self.score_board_headline_img = Image.fromarray(self.score_board_headline_img)
        self.score_board_headline_text = pytesseract.image_to_string(self.score_board_headline_img)
        self.kill_cam_img = self.screenshot.crop((int(self.screenshot.width*.32), int(self.screenshot.height*.19), int(self.screenshot.width*.65),int(self.screenshot.height*.30)))
        self.kill_cam_img = self.kill_cam_img.resize((int(self.kill_cam_img.width*1.5), int(self.kill_cam_img.height*1.5)))
        self.kill_cam_img =cv2.cvtColor(numpy.array(self.kill_cam_img), cv2.COLOR_RGB2BGR)
        self.lower = numpy.array([235,238,236])
        self.upper = numpy.array([255,255,255])
        self.kill_cam_img = cv2.inRange(self.kill_cam_img,self.lower,self.upper)
        self.kill_cam_img = cv2.bitwise_not(self.kill_cam_img)
        self.kill_cam_img = Image.fromarray(self.kill_cam_img)

        self.kill_cam_text = pytesseract.image_to_string(self.kill_cam_img)


        if 'to interact with the scoreboard.' in self.score_board_headline_text.lower():
            print("processing scoreboard")
            self.process_score_board()
        elif "killed you" in self.kill_cam_text.lower():
            self.kill_cam_img.save("invertedblackandwhite.jpg")
            self.process_kill_cam()
        else:
            print("Not scoreboard or killcam")
