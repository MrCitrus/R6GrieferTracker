import sqlite3, uuid, os, APIconnection
from PySide2.QtCore import Signal, QObject, QDateTime
class RainbowDB(QObject):
    db_new_image = Signal(str)
    db_player_path_dict = Signal(dict)
    def __init__(self, database = 'grieferdatabase.db'):
        super().__init__()
        self.database = database
        self.API_obj = APIconnection.API_connection()
        if (APIconnection.API_connection.ubi_email != None) and (APIconnection.API_connection.ubi_password != None):
            self.API_obj.authenticate()
        self.connection = sqlite3.connect(self.database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS griefers (username text, date text, killcam_path text, uuid text)")
    def _close(self):
        self.connection.commit()
    def add_player(self,name,killcam_screenshot):
        self.killcam_path  = os.getcwd() + "\\" + uuid.uuid4().hex + ".jpg"
        killcam_screenshot.save(self.killcam_path)
        self.killcam_path  = os.getcwd() + "\\" + uuid.uuid4().hex + ".png"
        killcam_screenshot.save(self.killcam_path)
        self.dateobj = QDateTime.currentDateTime()
        self.uuid = self.API_obj.get_uuid_from_username(name)
        print("this is the uid being inserted into the databse: " , self.uuid)
        self.cursor.execute("INSERT INTO griefers (username, date,killcam_path, uuid) VALUES (?,?,?,?)", (name,self.dateobj.toString("dd.MM.yyyy"),self.killcam_path, self.uuid))
        self.db_new_image.emit(self.killcam_path)
        self.connection.commit()
    def player_kill_counts(self):
        self.cursor.execute("SELECT killcam_path,username FROM griefers")
        self.player_kc_dict = {}
        for tup in (self.cursor.fetchall()):
            if tup[1] in self.player_kc_dict:
                self.player_kc_dict[tup[1]] += 1
            else:
                 self.player_kc_dict[tup[1]] = 1
        return self.player_kc_dict
    def player_kill_count_date(self):
        self.cursor.execute("SELECT username,killcam_path, date FROM griefers")
        self.player_kc_dict = {}
        for tup in (self.cursor.fetchall()):
            if tup[0] in self.player_kc_dict and QDateTime.fromString(tup[2]) < QDateTime.fromString(self.player_kc_dict[tup[0]][1]):
                self.player_kc_dict[tup[0]] = (self.player_kc_dict[tup[0]][0]+1,tup[2])
            elif tup[0] in self.player_kc_dict and QDateTime.fromString(tup[2]) >= QDateTime.fromString(self.player_kc_dict[tup[0]][1]):
                self.player_kc_dict[tup[0]][0] += 1
            else:
                self.player_kc_dict[tup[0]] = [1, tup[2]]
        return self.player_kc_dict
    def get_all_player_paths(self):
        self.cursor.execute("SELECT killcam_path FROM griefers")
        return self.cursor.fetchall()
    def player_search(self,player_list):
        self.playerdict = {}
        self.player_uuid_list = self.API_obj.get_list_uuids_from_usernames(player_list)
        for name_uuid_tup in self.player_uuid_list:
            self.cursor.execute("SELECT killcam_path FROM griefers where uuid =\'" + name_uuid_tup[1] + "\'")
            if len(self.cursor.fetchall()):

                self.playerdict[name_uuid_tup[0]] = []
                self.cursor.execute("SELECT killcam_path FROM griefers where uuid  =\'" + name_uuid_tup[1] + "\'")
                for path_tuple in self.cursor.fetchall():

                    print("extending list in this following dictionary:", self.playerdict)
                    print("extending with: ",path_tuple )
                    self.playerdict[name_uuid_tup[0]].extend(path_tuple)
                    print("After extension: ",self.playerdict)

        if len(self.playerdict):
            self.db_player_path_dict.emit(self.playerdict)
