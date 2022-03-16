import datetime
import os, time, threading, sys, traceback
import tkinter as tk
from tkinter import ttk
import PIL
import PIL
from PIL import ImageTk, Image, ImageDraw, ImageFont
from tkinter import filedialog
import pandas as pd
from jira import JIRA
import pyAesCrypt, io
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class IDB_Printer_Line(tk.Frame):
    def __init__(self, parent, image = None, dirs=['Input',],extension='.tif'):
        tk.Frame.__init__(self)
        self.IP_dic = {#'IDB-PT-04': '192.168.1.78',
                       #'IDB-PT-05': '192.168.1.33',
                       'IDB-PT-07': '192.168.1.241',
                       #'IDB-PT-08': '192.168.1.122',
                       'IDB-PT-09': '192.168.1.163',
                       'IDB-PT-11': '192.168.1.178',
                       'IDB-PT-12': '192.168.1.186',
                       'IDB-PT-13': '192.168.1.185',
                        'IDB-PT-14': '192.168.1.45',
                        'IDB-PT-15': '192.168.1.138',
                        'IDB-PT-16': '192.168.1.93',
                       'IDB-PT-17': '192.168.1.128'
        }
        #Initialize attributes
        # s = ttk.Style()
        # s.theme_use('xpnative')
        while True:
            try:
                #Source: https://github.com/marcobellaccini/pyAesCrypt
                #password = input("Password: ")   #Getpass edit configurations->Emulate terminal in output console
                #password = getpass.getpass()
                password = tk.simpledialog.askstring("Password", "Enter password:", show='*')
                password="LFO Rox!"
                fDec = io.BytesIO()
                bufferSize = 64 * 1024
                fCiph = open('auth.txt.aes', 'rb').read()
                fCiph = io.BytesIO(fCiph)
                ctlen = len(fCiph.getvalue())
                fCiph.seek(0)
                pyAesCrypt.decryptStream(fCiph, fDec, password, bufferSize, ctlen)
                auth = fDec.getvalue().decode().split(', ')
                break
            except ValueError:
                print(" Wrong password (or file is corrupted).")
                print("Try Again")
        self.jira = JIRA({'server': auth[0]},
                    basic_auth=(auth[1],auth[2]))
        self.allfields = self.jira.fields()
        self.nameMap = {field['name']: field['id'] for field in self.allfields}
        self.parent = parent
        parent.title('LightForce IDB Printer Line')
        self.frame0=tk.Frame(master=parent)
        self.frame0.grid(column=0,row=1)
        self.frame1=tk.Frame(master=parent)
        self.frame1.grid(column=0,row=3)
        self.frame2=tk.Frame(master=parent)
        self.frame2.grid(column=0,row=4)
        self.frame3=tk.Frame(master=parent)
        self.frame3.grid(column=0,row=5)
        self.frame4=tk.Frame(master=parent)
        self.frame4.grid(column=0,row=6)
        self.font_clock = ImageFont.truetype("arial.ttf",30)
        self.font = ImageFont.truetype("arial.ttf", 17)
        self.font_box = ImageFont.truetype("arial.ttf", 10)
        self.original = Image.open("Images/Print_line_flip.jpg")
        self.bx, self.by = self.original.size
        self.background = self.original.copy()
        self.image = ImageDraw.Draw(self.background)

        self.interface  = ImageTk.PhotoImage(self.background, (self.by, self.bx))
        self.canv = tk.Canvas(self.frame0, width=self.bx, height=self.by, bg='white')
        self.canv.grid(column=4, row=3)
         #self.canv.create_image(0, 0, image=self.background)
        self.canv.create_image(1, 1, image=self.interface, anchor="nw")
        self.label_place = {'IDB-PT-11': [750, 83],
                            'IDB-PT-09': [923, 83],
                            'IDB-PT-05': [1100, 83],
                            'IDB-PT-07': [750, 185],
                            'IDB-PT-08': [923, 185],
                            'IDB-PT-12': [1100, 185],
                            'IDB-PT-13': [750, 435],
                            'IDB-PT-15': [928, 435],
                            'IDB-PT-16': [1107, 435],
                            'IDB-PT-14': [754, 538],
                           # 'IDB-PT-04':[928, 538],
                            'IDB-PT-17':[1100, 538]
                            }
        self.dot_place = {'IDB-PT-05': [1104, 36],
                          'IDB-PT-07': [756, 299],
                          'IDB-PT-08': [926, 299],
                          'IDB-PT-09': [926, 36],
                          'IDB-PT-11': [750, 36],
                          'IDB-PT-12': [1104, 299],
                          'IDB-PT-13': [756, 391],
                          #'IDB-PT-04': [926, 669],
                          'IDB-PT-14': [761, 669],
                          'IDB-PT-15': [926, 391],
                          'IDB-PT-16': [1104, 391],
                          'IDB-PT-17': [1117, 669]
                          }
        self.box_place = {'Box1': [539, 31],
                          'Box2': [504, 234],
                          'Box3': [208, 319],
                          'Box4': [261, 26],
                          'Box5': [66, 26],
                          }
        self.info_box_place = (15, 504)
        self.clock_place = (15, 442)
        dx,dy = 35,35
        self.rgb = (5, 1, 51)
        self.greendot = Image.open("Images/green_dot.png").resize((dx,dy), Image.ANTIALIAS)
        self.reddot = Image.open("Images/red_dot.png").resize((dx,dy), Image.ANTIALIAS)
        self.redfrown = Image.open("Images/red_frown.png").resize((dx,dy), Image.ANTIALIAS)
        #self.reddot = ImageTk.PhotoImage(self.reddot)
        # self.greendot = ImageTk.PhotoImage(self.greendot)
        # self.redfrown =ImageTk.PhotoImage(self.redfrown)
        self.hourglass = Image.open("Images/hourglass.png").resize((dx,dy), Image.ANTIALIAS)
        # self.hourglass = ImageTk.PhotoImage(self.hourglass)
        self.Unplugged = Image.open("Images/Unplugged.png").resize((dx,dy), Image.ANTIALIAS)
        self.Wrench = Image.open("Images/Wrench.png").resize((dx,dy), Image.ANTIALIAS)
        # self.Wrench = ImageTk.PhotoImage(self.Wrench)
        self.Warning = Image.open("Images/Warning.png").resize((dx,dy), Image.ANTIALIAS)
        # self.Warning = ImageTk.PhotoImage(self.Warning)
        self.job_dic,self.status_dic, self.job_dic_short, self.label_dic = {},{},{},{}
        self.start_dic,self.print_dic,self.dot_dic, self.data_dic = {},{}, {},{}
        self.print_count_dic, self.time_offset,self.size_dic, self.uptime_dic = {},{},{},{}
        self.runtime_dic = {}
        self.database_file = datetime.datetime.now().strftime("%Y%m%d")
        today = datetime.datetime.now()
        self.shift_start = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=4,minute=30, second=0)
        self.work_day = datetime.datetime.now() - self.shift_start
        self.end_of_day = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=23,minute=59, second=59)
        self.file_date = self.end_of_day.strftime("%m-%d-%Y")
        self.data_file = f'IDB_Line_data_{self.file_date}.csv'
        for f in self.label_place:
            self.status_dic[f] = 'Offline'
            self.job_dic[f] = ''
            self.job_dic_short[f]=''
            self.start_dic[f] = ''
            self.print_dic[f] =''
            self.data_dic[f] = {'Time':[], 'Filename':[], "Status":[], 'Runtime':[], 'Print Count':[]}
            self.print_count_dic[f] = 0
            self.time_offset[f]=['','']
            self.size_dic[f]=[0,0]
            self.uptime_dic[f] = datetime.timedelta(seconds=0)

        # self.gauth = GoogleAuth()
        # self.drive = GoogleDrive(self.gauth)
        #
        # self.gfile = self.drive.CreateFile({'parents': [{'id': '1vaPbo_ddkGsslCc9z5X4UrprK5ZHago4'}]})
        worker = threading.Thread(name='read_printer', target=lambda: self.read_printers())
        worker.daemon = True
        worker.start()
        # worker = threading.Thread(name='read_printer', target=lambda: self.initial_read())
        # worker.daemon = True
        # worker.start()
    def read_printers(self):
        self.dlpcs_lines_old_dic, self.ecs_lines_old_dic = {}, {}
        self.dlpcs_lines_new_dic, self.ecs_lines_new_dic = {}, {}
        N = 8000
        for f in self.label_place:
            self.dlpcs_lines_old_dic[f], self.ecs_lines_old_dic[f]= ['',],[]
        while True:
            if self.end_of_day<datetime.datetime.now():
                try:
                    csv = pd.DataFrame.from_dict(self.data_dic)
                    csv.to_csv(self.data_file)

                except PermissionError as e:
                    csv = pd.DataFrame.from_dict(self.data_dic)
                    csv.to_csv(self.data_file)
                # self.gfile.SetContentFile(self.data_file)
                # self.gfile.Upload()
                self.end_of_day = datetime.datetime(year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day, hour=23,minute=59, second=59)
                self.file_date = self.end_of_day.strftime("%m-%d-%Y")
                self.data_file = f'IDB_Line_data_{self.file_date}.csv'
                for f in self.label_place:
                    self.data_dic[f] = {'Time': [], 'Filename': [], "Status": [], 'Runtime': [], 'Print Count': []}
                    self.print_count_dic[f] = 0


            # print(self.parent.winfo_width(), self.parent.winfo_height(),self.bx,self.by)
            for printer in self.IP_dic:
                self.background.paste(self.Warning, self.dot_place[printer])
                stop=False
                list_of_lines = []
                #print(f'updating {printer}, {self.IP_dic[printer]}')   #Troubleshooting problem printers
                logfile = f'\\\\{self.IP_dic[printer]}/log/dlpcs_core.log'
                try:
                    self.size_dic[printer][0] = os.stat(logfile).st_size


                    if self.size_dic[printer][0]!=self.size_dic[printer][1]:
                        with open(logfile, 'rb') as f:
                            f.seek(0, os.SEEK_END)
                            buffer = bytearray()
                            pointer_location = f.tell()
                            while pointer_location >= 0:
                                f.seek(pointer_location)
                                pointer_location = pointer_location - 1
                                new_byte = f.read(1)
                                if new_byte == b'\n':
                                    try:
                                        list_of_lines.append(buffer.decode()[::-1])
                                    except UnicodeDecodeError:
                                        'bad byte'
                                    if self.time_offset[printer][0]=='':
                                        for c in range(len(list_of_lines)):
                                            try:
                                                t_recent = datetime.datetime.strptime(list_of_lines[c][7:30],"%Y-%m-%d_%H:%M:%S.%f")# Log date format: 2022-02-03_19:29:11.321
                                                #self.time_offset[printer][0] =t_recent-datetime.datetime.now()
                                                self.time_offset[printer][0] = datetime.datetime.now() - t_recent

                                                break
                                            except ValueError:
                                                #print(list_of_lines[c][7:30])
                                                continue
                                    line = list_of_lines[-1]
                                    #print(buffer.decode()[::-1])
                                    if '/Job/' in line and "Start process build job" in line:
                                        self.job_dic[printer] = line.split('/Job/')[-1].split('/')[0]
                                        self.job_dic[printer] = self.job_dic[printer].split('"')[0]
                                        self.job_dic_short[printer] = self.job_dic[printer]
                                        if len(self.job_dic[printer])>18:
                                            self.job_dic_short[printer]=self.job_dic[printer][:18]
                                    if "JOB FINISHED" in line:
                                        print('Job finished', self.status_dic[printer])

                                        if self.status_dic[printer] == "Active":
                                            print("JOB RESTARTED")
                                            self.uptime_dic[printer]=self.uptime_dic[printer] + self.runtime_dic[printer]
                                            print(self.uptime_dic[printer])
                                            self.print_count_dic[printer]+=1
                                        self.status_dic[printer] = 'Inactive'
                                        for c in range(len(list_of_lines)):
                                            try:
                                                self.start_dic[printer] = datetime.datetime.strptime(list_of_lines[-c][7:30], "%Y-%m-%d_%H:%M:%S.%f")
                                                break
                                            except ValueError:
                                                continue
                                        #self.start_dic[printer] = datetime.datetime.strptime(list_of_lines[-4][7:30], "%Y-%m-%d_%H:%M:%S.%f") #Log date format: 2022-02-03_19:29:11.321datetime.datetime.now()
                                        self.job_dic[printer] = ''
                                        # update_data
                                        self.data_dic[printer]['Time'].append(str(self.start_dic[printer]))
                                        self.data_dic[printer]['Filename'].append(self.job_dic[printer])
                                        self.data_dic[printer]['Status'].append('Job Finished')
                                        # self.dot_dic[printer].configure(image=self.reddot)
                                        self.background.paste(self.reddot, self.dot_place[printer])
                                        break
                                    if "START JOB" in line:
                                        if self.time_offset[printer][1]=='':
                                            for c in range(len(list_of_lines)):
                                                try:
                                                    t_recent = datetime.datetime.strptime(list_of_lines[c][7:30],"%Y-%m-%d_%H:%M:%S.%f")  # Log date format: 2022-02-03_19:29:11.321
                                                    self.time_offset[printer][0],self.time_offset[printer][1] = datetime.datetime.now()- t_recent, t_recent - datetime.datetime.now()
                                                    print(printer, 'offset', self.time_offset[printer][0])
                                                    break
                                                except ValueError:
                                                    continue
                                        for c in range(len(list_of_lines)):
                                            try:
                                                self.start_dic[printer] = datetime.datetime.strptime(list_of_lines[-c][7:30], "%Y-%m-%d_%H:%M:%S.%f")
                                                break
                                            except ValueError:
                                                continue
                                        # update_data
                                        self.status_dic[printer] = "Active"
                                        self.data_dic[printer]['Time'].append(str(self.start_dic[printer]))
                                        self.data_dic[printer]['Filename'].append(self.job_dic[printer])
                                        self.data_dic[printer]['Status'].append('Start Job')
                                        self.data_dic[printer]['Runtime'] = str(self.uptime_dic[printer])
                                        self.data_dic[printer]['Print Count'] = self.print_count_dic[printer]
                                        # self.dot_dic[printer].configure(image=self.greendot)
                                        self.background.paste(self.greendot, self.dot_place[printer])
                                        maintenance_prints = ['OQ', 'cubes','block']
                                        res = [f for f in maintenance_prints if (f in self.job_dic[printer].lower())]
                                        if bool(res):
                                            status = "Maintenance"
                                            # self.dot_dic[printer].configure(image=self.Wrench)
                                            self.background.paste(self.Wrench, self.dot_place[printer])
                                        break
                                    if len(list_of_lines) == N or stop==True:
                                        break
                                    buffer = bytearray()
                                else:
                                    # If last read character is not eol then add it in buffer
                                    buffer.extend(new_byte)
                            if len(buffer) > 0:
                                list_of_lines.append(buffer.decode()[::-1])
                            self.dlpcs_lines_new_dic[printer] = list(reversed(list_of_lines))
                        for c in range(len(self.dlpcs_lines_new_dic[printer])):
                            try:

                                printer_time = self.dlpcs_lines_new_dic[printer][-c][7:30] #Log date format: 2022-02-03_19:29:11.321
                                printer_time = datetime.datetime.strptime(printer_time, "%Y-%m-%d_%H:%M:%S.%f")
                                break
                            except ValueError:
                                continue
                        self.size_dic[printer][1]=self.size_dic[printer][0]
                except FileNotFoundError:
                    self.status_dic[printer] = 'Log file not found'
                    self.status_dic[printer] = 'Offline'
                    continue
                
                printer_time_now = datetime.datetime.now()
                try:
                    #runtime = printer_time - self.start_dic[printer]
                    runtime2 = datetime.datetime.now()-(self.start_dic[printer]+self.time_offset[printer][0])  #How the printer time offset is calculated needs
                    if runtime2 < datetime.timedelta(minutes=5) and self.status_dic[printer] == 'Inactive':
                        # self.dot_dic[printer].configure(image=self.hourglass)
                        self.background.paste(self.hourglass, self.dot_place[printer])
                    if runtime2 > datetime.timedelta(minutes=5) and self.status_dic[printer] == 'Inactive':
                        # self.dot_dic[printer].configure(image=self.Warning)
                        self.background.paste(self.Warning, self.dot_place[printer])
                    self.runtime_dic[printer] = runtime2
                    runtime2 = ':'.join(str(runtime2).split('):')[:3]).split('.')[0]
                    uptime =':'.join(str(self.uptime_dic[printer]).split('):')[:3]).split('.')[0]

                except TypeError:
                    runtime2 = 'No Data'
                    uptime='No Data'
                    self.status_dic[printer] = 'Offline'
                #self.strvar_dic[printer].set(f'{printer}\nStatus: {self.status_dic[printer]}\n{self.job_dic[printer]}\nTime In Status: {runtime2}\n')
                self.image.text((self.label_place[printer][0], self.label_place[printer][1]), f'{printer}\nStatus: {self.status_dic[printer]} #{self.print_count_dic[printer]}\n{self.job_dic_short[printer]}\nStatus Time:{runtime2}\nUptime: {str(uptime)}',
                                fill=self.rgb, font=self.font)
                # self.ecs_lines_old_dic[printer] =self.ecs_lines_new_dic[printer]
                file_time, self.time_now = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S"), datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

                #self.write_database(printer)
            self.read_jira(printer)
            if self.parent.winfo_width() !=self.bx and self.winfo_height() != self.by:
                # print('size changed!!!',self.parent.winfo_width()==int(self.parent.winfo_width()))
                self.bx,self.by = self.parent.winfo_width(),self.parent.winfo_height()
                self.canv.config(width=self.bx, height=self.by)
            for printer in self.print_dic:
                if self.status_dic[printer] == "Active":
                    self.background.paste(self.greendot, self.dot_place[printer])
                if self.status_dic[printer] == "Inactive":
                    self.background.paste(self.reddot, self.dot_place[printer])
            self.image.text(self.clock_place, f'Time:    {datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}',
                            fill=(230, 16, 16), font=self.font_clock)
            self.canv.delete("all")
            del self.image
            # self.canv = tk.Canvas(self.frame0, width=self.bx, height=self.by, bg='white')
            # self.canv.grid(column=4, row=3)
            self.background = self.background.resize((self.bx,self.by), Image.ANTIALIAS)
            self.interface = ImageTk.PhotoImage(self.background, (self.by, self.bx))
            del self.background
            self.canv.create_image(1, 1, image=self.interface, anchor="nw")
            
            self.background = self.original.copy()
            
            self.image = ImageDraw.Draw(self.background)
            # self.canv.itemconfig(self.image_on_canvas, image= ImageTk(self.background))

            print('done loop')

            try:
                csv = pd.DataFrame.from_dict(self.data_dic)
                csv.to_csv(f'IDB_Line_data_{self.file_date}.csv')
            except PermissionError as e:
                print('file write: Permision Error')
            time.sleep(50)

    def initial_read(self):
        csv = pd.DataFrame.from_dict(self.data_dic)
        csv.to_csv(self.data_file)
        # self.gfile.SetContentFile(self.data_file)
        # self.gfile.Upload()
        for printer in self.label_place:
            t_finish, t_start,recent_time='','',''

            end_time=''
            N = 100000
            f_line=True
            logfile = f'\\\\{self.IP_dic[printer]}/log/dlpcs_core.log'
            try:
                with open(logfile, 'rb') as f:
                    f.seek(0, os.SEEK_END)
                    buffer = bytearray()
                    pointer_location = f.tell()
                    list_of_lines = []

                    while pointer_location >= 0:
                        f.seek(pointer_location)
                        pointer_location = pointer_location - 1
                        new_byte = f.read(1)
                        if new_byte == b'\n':
                            try:
                                list_of_lines.append(buffer.decode()[::-1])
                            except UnicodeDecodeError as e:
                                print('bad buffer????')
                            line = list_of_lines[-1]
                            buffer = bytearray()
                            if f_line:
                                try:
                                    recent_time = datetime.datetime.strptime(line[7:30],"%Y-%m-%d_%H:%M:%S.%f")

                                    f_line=False
                                    end_time = recent_time-self.work_day
                                except ValueError:
                                    pass
                            if '/Job/' in line and "Start process build job" in line:
                                self.job_dic[printer] = line.split('/Job/')[-1].split('/')[0]
                                self.job_dic[printer] = self.job_dic[printer].split('"')[0]
                            if "JOB FINISHED" in line:

                                for c in range(len(list_of_lines)):
                                    try:
                                        if f_line:
                                            recent_time = datetime.datetime.strptime(list_of_lines[c][7:30], "%Y-%m-%d_%H:%M:%S.%f")

                                            f_line = False

                                        t_finish = datetime.datetime.strptime(list_of_lines[-4][7:30],
                                                                              "%Y-%m-%d_%H:%M:%S.%f")
                                        t_start = datetime.datetime.strptime(list_of_lines[c][7:30],
                                                                             "%Y-%m-%d_%H:%M:%S.%f")
                                        break
                                    except ValueError:
                                        continue
                                # update_data
                                self.data_dic[printer]['Time'].append(str(t_finish))
                                self.data_dic[printer]['Filename'].append(self.job_dic[printer])
                                self.data_dic[printer]['Status'].append('Job Finished')
                            if end_time=='' or t_start=='':
                                continue
                            if "START JOB" in line:

                                for c in range(len(list_of_lines)):
                                    try:
                                        t_start = datetime.datetime.strptime(list_of_lines[-c][7:30], "%Y-%m-%d_%H:%M:%S.%f")
                                        break
                                    except ValueError:
                                        continue

                                print(f"{printer},Job: {self.job_dic[printer]}, started at:{t_start}, print count: {self.print_count_dic[printer]}")
                                if t_start > end_time:
                                    runtime = t_finish - t_start
                                    self.print_count_dic[printer] += 1
                                    #update_data
                                    self.uptime_dic[printer] = self.uptime_dic[printer] + runtime
                                    self.data_dic[printer]['Time'].append(str(t_start))
                                    self.data_dic[printer]['Filename'].append(self.job_dic[printer])
                                    self.data_dic[printer]['Status'].append('Start Job')
                                    self.data_dic[printer]['Runtime'] = str(self.uptime_dic[printer])
                                    self.data_dic[printer]['Print Count'] = self.print_count_dic[printer]
                                # try:
                                #     runtime = t_finish-t_start
                                #     self.uptime_dic[printer] = self.uptime_dic[printer] + runtime
                                # except TypeError:
                                #     'Printer is active'




                            if len(list_of_lines) >= N or t_start<end_time:
                                print('finish initial read',printer,'Uptime: ', self.uptime_dic[printer])
                                print('read until time: ',t_start,'from: ',recent_time, 'should be before: ', end_time)
                                print(f'{len(list_of_lines)} Lines')
                                del list_of_lines
                                break

                            buffer = bytearray()
                        else:
                            # If last read character is not eol then add it in buffer
                            buffer.extend(new_byte)
                    if len(buffer) > 0:
                        list_of_lines.append(buffer.decode()[::-1])
            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                print(printer,exc_type,  exc_tb.tb_lineno)
        print('finish initial loop')
        csv=pd.DataFrame.from_dict(self.data_dic)
        csv.to_csv(self.data_file)
        # self.gfile.SetContentFile(self.data_file)
        # self.gfile.Upload()
        self.read_printers()

    def read_jira(self,printer):
        for status,box in zip(["Ready for Cleaning","IDB cleaning", "IDB Rinse","IDB Drying","IDB curing"],self.box_place):
            results = self.jira.search_issues(f'''project = MFG AND (labels is EMPTY OR labels not in (duplicate_tx, test, test_treatment)) AND issuetype = MakeIDB AND "status" = "{status}"''')
            c,case_list,case_string =0,[],'\n'
            n = 3
            if box in ['Box1','Box4','Box5']:
                n = 4
            if box == 'Box2':
                n = 4
            if box == 'Box3':
                n = 5

            for case in results:
                c+=1
                case_list.append(str(getattr(case.fields, self.nameMap['PatientAlias'])))
                if c >= n:
                    case_string+=  ', '.join(case_list)
                    case_string+='\n'
                    case_list = []
                    c=0
            if len(case_list)>0:
                case_string += ', '.join(case_list)
            self.image.text((self.box_place[box][0], self.box_place[box][1]),
                            f'{status}: {case_string}',
                            fill=self.rgb, font = self.font_box)
            #self.strvar_dic[box].set(f'{status}: {case_string}')


if __name__ == '__main__':
    for f in ['Output',"Images","Database"]:
        if not os.path.isdir(f):
            os.makedirs(f)
    root = tk.Tk()
    root.iconbitmap('Images/Lightforce_refraction.ico')
    root.protocol('WM_DELETE_WINDOW', exit)
    x,y =  Image.open("Images/IDB_Floor_Layout.jpg").size
    root.geometry(f"{x}x{y}")
    #root.withdraw()
    #parent = tk.Toplevel(master=root)
    app = IDB_Printer_Line(root)
    root.mainloop()
#
# if __name__ =='__main__':
#     while True:
#         log_job_view()
#         cont = input('\n again? \n')
#         if cont == 'no':
#             break
