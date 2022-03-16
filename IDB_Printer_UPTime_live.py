import os,datetime,sys, traceback

flist = os.listdir()
data_dic={}
runtime_dic={}
csv_dic={}
IP_dic = {#'IDB-PT-04': '192.168.1.78',
                       #'IDB-PT-05': '192.168.1.33',
                       'IDB-PT-07': '192.168.1.241',
                       'IDB-PT-08': '192.168.1.122',
                       'IDB-PT-09': '192.168.1.163',
                       'IDB-PT-11': '192.168.1.178',
                       'IDB-PT-12': '192.168.1.186',
                       'IDB-PT-13': '192.168.1.185',
                        'IDB-PT-14': '192.168.1.45',
                        'IDB-PT-15': '192.168.1.138',
                        'IDB-PT-16': '192.168.1.93',
                       'IDB-PT-17': '192.168.1.128'
        }
today = datetime.datetime.now()
shift_start = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=4,minute=30, second=0)
work_day = datetime.datetime.now() - shift_start
N=1000000
for printer in IP_dic:
    # break
    data_dic[printer] = {'Print Number': [], "Start Time":[], 'Filename': [], "Runtime": [], 'Material': [], 'Completion': []}
    logfile = f'\\\\{IP_dic[printer]}/log/dlpcs_core.log'
    print(printer, logfile)
    f_line=True
    t_finish, t_start, recent_time,end_time = '', '', '',''
    material_used = []
    material = 0
    completion = "Successful"
    job=None
    f_mat = [False, False]
    print_count,uptime=0,datetime.timedelta(seconds=0)
    counter=0
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
                #print(new_byte)
                if new_byte == b'\n':
                    counter+=1
                    try:
                        line = buffer.decode()[::-1]
                        list_of_lines.append(line)
                    except UnicodeDecodeError:
                        'bad byte'
                    #print(buffer.decode()[::-1])
                    buffer = bytearray()    #Needed to reset line so it doesn't grow endlessly
                    if f_line:
                        try:
                            recent_time = datetime.datetime.strptime(line[7:30], "%Y-%m-%d_%H:%M:%S.%f")

                            f_line = False
                            end_time = recent_time - work_day
                            print('check2')
                        except ValueError:
                            pass
# [0;37m2022-03-14_19:59:40.517[0;33m[Dispatcher:I][0;0m[0;37m[32168][0m    [1;30m[0;37mMaterial volume (real) decreased:  1  ( 4 ml total for this print)[0m
# [0;37m2022-03-14_19:59:40.517[0;33m[Dispatcher:I][0;0m[0;37m[32168][0m    [1;30m[0;37mMaterial per layer =  0.0949292[0m
#[0;37m2022-03-15_15:00:07.580[0;33m[Dispatcher:I][0;0m[0;37m[2126][0m    [1;30m[0;37mMaterial per layer =  0.205761 , active pixels =  6462[0m
                    try:
                        if f_mat[0]:
                            if "Material volume" in line:
                                material += int(line.split(" ml total")[-2].split('(')[-1])
                                #print(line)
                                f_mat[0] = False
                            if "per layer" in line and f_mat[1]:
                                if "active pixels" in line:
                                    material+=float(line.split('per layer = ')[-1].split(',')[0])
                                else:
                                    material += float(line.split('[0m')[-2].split('=')[-1])
                                #print(line)
                                f_mat[1] = False
                    except:
                        print(traceback.format_exc())
                    #print(len(buffer.decode()[::-1]),len(line))
                    if "abort job" in line:
                        completion = "Aborted"
                    if '/Job/' in line and "Start process build job" in line:
                        job = line.split('/Job/')[-1].split('/')[0]
                        job = job.split('"')[0]
                        print(line)
                    if "JOB FINISHED" in line:
                        f_mat=[True,True]
                        for c in range(len(list_of_lines)):
                            try:
                                if f_line:
                                    print('check1')
                                    recent_time = datetime.datetime.strptime(list_of_lines[c][7:30],
                                                                             "%Y-%m-%d_%H:%M:%S.%f")
                                    end_time = recent_time - work_day
                                    f_line = False
                                    print(end_time)
                                t_finish = datetime.datetime.strptime(list_of_lines[-4][7:30],
                                                                      "%Y-%m-%d_%H:%M:%S.%f")
                                t_start = datetime.datetime.strptime(list_of_lines[c][7:30],
                                                                     "%Y-%m-%d_%H:%M:%S.%f")

                                break
                            except ValueError:
                                continue
                        # update_data
                        # data_dic[printer]['Time'].append(str(t_finish))
                        # data_dic[printer]['Filename'].append(job)
                        # data_dic[printer]['Status'].append('Job Finished')

                    if end_time == '' or t_start == '':
                        continue
                    #print(line)
                    if "START JOB" in line:
                        for c in range(len(list_of_lines)):
                            try:
                                t_start = datetime.datetime.strptime(list_of_lines[-c][7:30], "%Y-%m-%d_%H:%M:%S.%f")
                                break
                            except ValueError:
                                continue
                        list_of_lines=[]

                        if t_start > end_time:
                            runtime = t_finish - t_start
                            print_count += 1
                            # update_data
                            uptime= uptime + runtime
                            data_dic[printer]['Start Time'].append(str(t_start))
                            data_dic[printer]['Filename'].append(job)
                            data_dic[printer]['Runtime'].append(runtime)
                            data_dic[printer]['Print Number'].append(str(print_count))
                            data_dic[printer]['Completion'].append(completion)
                            data_dic[printer]['Material'].append(material)
                            print(
                                f"{printer},Job: {job}, started at:{t_start}, runtime: {runtime} print count: {print_count}")
                            print('material used ml', material)
                            material=0
                            completion = "Successful"

                        # try:
                        #     runtime = t_finish-t_start
                        #     uptime_dic[printer] = uptime_dic[printer] + runtime
                        # except TypeError:
                        #     'Printer is active'

                    if counter >= N or t_start < end_time:
                        print('finish initial read', printer, 'Uptime: ', uptime)
                        print('read until time: ', t_start, 'from: ', recent_time, 'should be before: ', end_time)
                        print(f'{counter} Lines')
                        del list_of_lines
                        break

                    buffer = bytearray()
                else:
                    # If last read character is not eol then add it in buffer
                    buffer.extend(new_byte)
            if len(buffer) > 0:
                list_of_lines.append(buffer.decode()[::-1])
    except:
        print(traceback.format_exc())

print(data_dic)
# data_dic={'IDB-PT-07': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'], 'Start Time': ['2022-03-16 00:22:33.007000', '2022-03-15 23:34:48.930000', '2022-03-15 23:01:16.404000', '2022-03-15 22:19:49.715000', '2022-03-15 21:48:26.985000', '2022-03-15 21:08:28.599000', '2022-03-15 20:30:43.127000', '2022-03-15 19:55:53.680000', '2022-03-15 19:19:11.606000', '2022-03-15 17:05:41.639000', '2022-03-15 16:27:32.147000', '2022-03-15 15:35:37.196000', '2022-03-15 14:56:22.083000', '2022-03-15 14:18:45.063000', '2022-03-15 13:30:15.883000', '2022-03-15 12:53:21.715000', '2022-03-15 12:16:53.159000', '2022-03-15 11:43:44.966000', '2022-03-15 11:06:37.548000', '2022-03-15 10:30:01.567000'], 'Filename': ['N5IUV-auto', 'DAFKK', 'RDWOC', '7V798', 'A5DIM-auto-2', 'F96DT-auto', '6F3A2-NBBR2', 'S7VI3-auto', 'PK6CW-auto', 'PGZU6-O9E29', 'LZPMB-ZJSKR', 'A86FG-4LOIT', 'WX73M-auto', '4C4NV-FBXNA', 'L97FI-auto', '3TRRX-auto', '7FJGY-auto', '37HYT-auto', 'F2MSW-auto', 'IKCFZ-auto'], 'Runtime': ['0:30:03.108000', '0:33:38.956000', '0:28:56.216000', '0:32:58.176000', '0:30:30.431000', '0:37:28.298000', '0:29:09.262000', '0:30:43.465000', '0:28:01.768000', '0:31:23.758000', '0:31:37.502000', '0:37:41.691000', '0:30:43.616000', '0:31:24.340000', '0:31:24.062000', '0:33:38.997000', '0:29:22.714000', '0:30:03.714000', '0:30:57.335000', '0:29:09.068000'], 'Material': ['29.31333', '36.549656', '28.431155', '27.401029', '25.531589', '24.281567', '24.45551', '21.464943', '24.0222883', '22.427902', '25.0311084', '26.145537', '26.0752347', '26.378585', '23.0274421', '27.615547', '23.938285', '27.781117', '24.472428', '24.234184'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-08': {'Print Number': [], 'Start Time': [], 'Filename': [], 'Runtime': [], 'Material': [], 'Completion': []}, 'IDB-PT-09': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'], 'Start Time': ['2022-03-16 00:19:28.799000', '2022-03-15 23:32:41.755000', '2022-03-15 22:57:36.781000', '2022-03-15 22:15:41.799000', '2022-03-15 20:26:55.170000', '2022-03-15 19:52:23.269000', '2022-03-15 19:18:41.686000', '2022-03-15 18:18:41.822000', '2022-03-15 17:42:00.823000', '2022-03-15 17:08:00.439000', '2022-03-15 16:30:12.166000', '2022-03-15 15:45:16.663000', '2022-03-15 15:03:12.399000', '2022-03-15 14:28:39.311000', '2022-03-15 13:50:09.791000', '2022-03-15 13:06:17.791000', '2022-03-15 12:24:21.828000', '2022-03-15 11:48:35.162000', '2022-03-15 11:12:07.743000', '2022-03-15 10:24:38.122000'], 'Filename': ['RRVBY-auto', 'PCSKZ', 'LYFA2-auto', '6OUZ3-auto', 'MJTHN-auto', '54GYT-auto', 'CL5XK-auto', 'MEATL-auto', '7I4T6-auto', 'YFJUN-auto', '2RIUM-auto', '3J59W-auto', 'F96DT-auto', 'XNUIW-auto', 'DMJPN-auto', '343VO-auto', 'P4ZYZ-auto', '7V798-auto', 'LBZ5P-auto', 'SFQI2-auto'], 'Runtime': ['0:35:01.296000', '0:31:14.515000', '0:29:37.533000', '0:30:04.473000', '0:30:57.597000', '0:30:02.553000', '0:29:48.407000', '0:31:09.691000', '0:29:23.756000', '0:30:18.130000', '0:35:16.105000', '0:28:02.142000', '0:37:41.902000', '0:28:40.520000', '0:35:12.268000', '0:30:55.498000', '0:35:14.711000', '0:33:14.143000', '0:30:41.542000', '0:29:24.439000'], 'Material': ['27.186804', '32.186675', '25.037242', '27.635193', '25.26789', '22.013216', '21.77716', '23.163254', '27.182796', '27.50371', '30.346561', '24.167304', '24.682899', '20.900896', '23.348318', '21.603566999999998', '27.868062', '28.00674102', '20.933713', '29.682118'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-11': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22'], 'Start Time': ['2022-03-16 00:17:31.332000', '2022-03-15 23:31:06.806000', '2022-03-15 22:56:44.898000', '2022-03-15 22:15:31.754000', '2022-03-15 21:41:36.886000', '2022-03-15 21:01:09.342000', '2022-03-15 20:24:51.766000', '2022-03-15 19:50:48.830000', '2022-03-15 19:18:30.326000', '2022-03-15 18:23:36.378000', '2022-03-15 17:43:59.304000', '2022-03-15 17:10:34.330000', '2022-03-15 16:31:56.882000', '2022-03-15 15:48:21.949000', '2022-03-15 15:09:15.019000', '2022-03-15 14:31:43.318000', '2022-03-15 13:52:40.886000', '2022-03-15 13:02:27.858000', '2022-03-15 12:19:57.334000', '2022-03-15 11:48:14.358000', '2022-03-15 11:11:51.842000', '2022-03-15 10:27:37.422000'], 'Filename': ['6F3A2-8XQ5L', '5N7Y8-TXTME', '3XYCV', 'URDPH-Z9BMY', 'DYTFB-auto', 'KAULA-auto', '52JN3-auto', 'YFJUN-auto', 'KTN7Z-auto', '8JJBN-auto', 'DWZJN-auto', 'H9TOB-auto', '7Y38L-auto', 'QSLGX-auto', 'HYL4A-auto', 'KL2Z6-auto', 'K782U-auto', 'YFJUN-auto', 'SCI6G-auto', 'BIKY9-auto', 'SXOP9-auto', 'KRJM6-auto'], 'Runtime': ['0:42:10.305000', '0:29:08.570000', '0:31:40.994000', '0:31:37.359000', '0:29:08.737000', '0:29:48.539000', '0:33:11.337000', '0:30:17.804000', '0:29:48.321000', '0:31:36.799000', '0:33:11.075000', '0:29:36.046000', '0:30:15.549000', '0:35:22.997000', '0:35:42.157000', '0:31:41.414000', '0:30:03.309000', '0:30:18.023000', '0:37:30.305000', '0:28:43.081000', '0:29:08.523000', '0:28:14.499000'], 'Material': ['23.605304', '24.939899', '31.266439', '24.205329', '24.222193', '24.529205', '24.0214418', '28.0236638', '22.528129', '25.65727', '23.419938', '25.479207', '23.861174', '17.376871', '29.641717', '33.449466', '25.529226', '28.0236638', '30.841346', '27.228206', '24.53049', '22.199451'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-12': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16'], 'Start Time': ['2022-03-16 00:21:05.841000', '2022-03-15 23:36:00.859000', '2022-03-15 22:59:27.366000', '2022-03-15 22:18:33.769000', '2022-03-15 21:43:38.516000', '2022-03-15 21:06:02.396000', '2022-03-15 20:28:47.984000', '2022-03-15 19:54:20.908000', '2022-03-15 19:19:39.824000', '2022-03-15 17:29:47.912000', '2022-03-15 15:44:16.060000', '2022-03-15 14:16:36.855000', '2022-03-15 13:26:02.915000', '2022-03-15 12:42:55.749000', '2022-03-15 12:08:21.816000', '2022-03-15 11:33:15.406000'], 'Filename': ['76YQX-auto', 'QSLGX-auto', 'XW3LD-auto', '8YXJN-auto', '8NCZL-auto', 'HJRQ9-auto', '6BNMH-auto', '556XZ-auto', 'GSK2A-auto', 'BWC4O-auto', 'TZUQJ-auto', 'RHQIC-auto', 'O8RFS-auto', 'GWCUF-auto', 'AV6OW-auto', '7YVOR-auto'], 'Runtime': ['0:33:01.154000', '0:35:23.667000', '0:35:05.433000', '0:28:55.235000', '0:29:23.224000', '0:28:28.607000', '0:30:04.047000', '0:30:30.329000', '0:30:30.414000', '0:35:01.342000', '0:33:52.759000', '0:29:22.396000', '0:31:38.622000', '0:31:27.301000', '0:31:24.209000', '0:30:32.394000'], 'Material': ['28.11596', '17.488204', '31.398905', '22.395664', '24.0877907', '22.496153', '25.812901', '24.0110582', '23.206002', '27.0490809', '24.20721', '23.729797', '26.234365', '30.638901', '24.92072', '27.661043'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-13': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], 'Start Time': ['2022-03-15 16:12:27.396000', '2022-03-15 15:31:16.432000', '2022-03-15 14:49:57.340000', '2022-03-15 14:12:27.092000', '2022-03-15 13:21:53.445000', '2022-03-15 12:48:38.400000', '2022-03-15 12:11:10.482000', '2022-03-15 11:35:51.382000', '2022-03-15 09:08:24.356000', '2022-03-15 07:41:11.408000'], 'Filename': ['PHMHX-NR5ZU', 'IRE6B-K5TOT', '8XQ5L-ABGSW', 'ACZQE-N43MY', '8GTBT-D7PSK', 'B9LOC-FIMLZ', 'H0BKV-UAZSJ', 'CDDGS-WBO84', '7MOHR-HIUPE', 'CSNH3-FVICX'], 'Runtime': ['0:35:00.025000', '0:31:36.741000', '0:31:37.072000', '0:31:10.074000', '0:37:16.222000', '0:29:35.774000', '0:31:21.946000', '0:31:33.029000', '0:33:12.573000', '0:33:55.017000'], 'Material': ['25.664243', '23.945642', '23.0820183', '23.417009', '28.234522', '23.753262', '21.773434', '16.59832', '26.191809', '27.0441433'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-14': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9'], 'Start Time': ['2022-03-15 16:18:10.129000', '2022-03-15 15:36:41.999000', '2022-03-15 14:32:37.095000', '2022-03-15 13:16:26.531000', '2022-03-15 12:30:45.529000', '2022-03-15 11:53:38.573000', '2022-03-15 10:59:46', '2022-03-15 09:00:04.547000', '2022-03-15 07:43:46.128000'], 'Filename': ['DFWPA-XLGGP', 'NT4TV-RZOQE', '2VLU7-E7DM5', '6L9HS-D43TD', 'T23QI-UWH5M', 'I52UK-UWH5M', 'BHVSA-ELFNA', 'C4GII-U2LC7', 'IM95L-SGTKV'], 'Runtime': ['0:34:43.174000', '0:29:19.305000', '0:28:51.961000', '0:29:05.765000', '0:29:46.272000', '0:29:46.225000', '0:31:20.549000', '0:33:49.507000', '0:29:59.422000'], 'Material': ['26.870327', '18.672647', '29.21315', '24.476133', '27.235849', '28.685737', '18.0509571', '31.0319451', '28.894086'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-15': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'], 'Start Time': ['2022-03-15 18:28:34.259000', '2022-03-15 17:26:15.863000', '2022-03-15 16:45:46.346000', '2022-03-15 16:08:32.304000', '2022-03-15 15:26:22.132000', '2022-03-15 14:46:40.721000', '2022-03-15 14:08:14.758000', '2022-03-15 13:12:49.450000', '2022-03-15 12:33:10.168000', '2022-03-15 12:00:28.282000', '2022-03-15 11:21:26.896000', '2022-03-15 10:42:33.206000', '2022-03-15 09:05:11.646000', '2022-03-15 07:50:29.766000'], 'Filename': ['FO38I-auto', '7UDQS-auto', 'F96DT-auto', '5HFBQ-auto', 'IVLO6-auto', 'ABPQE-auto', '8PEDY-auto', '8YS5C-auto', 'U28YU-auto', '6WUVD-auto', 'C5CYC-auto', 'BQVE6-auto', 'TFKP7-auto', '9K35J-auto'], 'Runtime': ['0:28:53.101000', '0:30:00.473000', '0:37:40.956000', '0:31:37.501000', '0:33:40.521000', '0:30:42.634000', '0:30:56.049000', '0:31:37.849000', '0:29:41.691000', '0:28:25.797000', '0:32:46.176000', '0:32:29.900000', '0:28:00.957000', '0:28:40.855000'], 'Material': ['19.581591', '19.772849', '23.646725', '24.469283', '28.152168', '22.35691', '23.564011', '25.117362', '9.196358', '18.608194', '27.74196', '21.62856', '22.886195', '21.467646'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-16': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'], 'Start Time': ['2022-03-15 18:28:49.323000', '2022-03-15 17:28:58.754000', '2022-03-15 16:43:57.811000', '2022-03-15 16:05:31.753000', '2022-03-15 15:28:12.732000', '2022-03-15 14:43:49.105000', '2022-03-15 14:05:21.789000', '2022-03-15 13:19:06.265000', '2022-03-15 12:46:13.348000', '2022-03-15 12:12:50.795000', '2022-03-15 11:19:16.949000', '2022-03-15 10:42:08.359000', '2022-03-15 09:02:53.917000', '2022-03-15 07:47:36.389000'], 'Filename': ['BQUK7-auto', 'VJSI9-auto', '7V798-auto', '37HYT-auto', 'XWG87-auto', 'IWDB7-auto', 'OJ4HL-auto', '6DEHQ-auto', 'JBA22-auto', 'TFKP7-auto', 'RA6ND-XTIEM', '6LC8P-SFNLT', '8XQ5L-D43TD', '4BLJL-QLB5G'], 'Runtime': ['0:28:40.145000', '0:34:21.915000', '0:33:14.151000', '0:30:18.454000', '0:30:45.481000', '0:33:40.081000', '0:30:13.921000', '0:36:27.674000', '0:30:29.544000', '0:28:01.397000', '0:31:37.466000', '0:29:36.292000', '0:31:36.989000', '0:30:46.520000'], 'Material': ['20.149377', '29.437634', '28.782117', '28.997833', '28.40441', '26.544195', '19.731322', '11.522789', '23.764463', '24.539377', '24.757537', '25.750176', '23.157942', '29.0485554'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-17': {'Print Number': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'], 'Start Time': ['2022-03-15 20:25:53.568000', '2022-03-15 19:44:30.089000', '2022-03-15 17:24:04.238000', '2022-03-15 16:41:54.120000', '2022-03-15 16:02:50.557000', '2022-03-15 15:27:29.676000', '2022-03-15 14:57:22.928000', '2022-03-15 13:09:55.109000', '2022-03-15 12:27:32.160000', '2022-03-15 11:54:16.074000', '2022-03-15 11:16:49.012000', '2022-03-15 10:34:15.606000', '2022-03-15 08:57:36.163000', '2022-03-15 07:44:21.992000'], 'Filename': ['WPQKY-auto', 'FJ2C9-auto', 'DU9TH-auto', 'A5DIM-auto', '54GYT-auto', 'MEATL-auto', 'CUBES +L', '54GYT-auto', '5FSCG-auto', 'BQUK7-auto', '7I4T6-auto', '7QLOW-auto', 'AOUAK-auto', '6YSV5-auto'], 'Runtime': ['0:31:36.556000', '0:31:39.212000', '0:29:18.605000', '0:30:43.778000', '0:30:01.245000', '0:31:09.421000', '0:16:52.360000', '0:30:01.183000', '0:30:24.662000', '0:28:38.978000', '0:29:23.400000', '0:29:10.266000', '0:32:59.654000', '0:30:46.602000'], 'Material': ['24.306088', '29.0160695', '17.274291', '26.575563', '22.654049', '23.755896', '8.513265', '22.654049', '15.665199', '20.150239', '27.85352', '28.0162759', '28.0653283', '29.156378'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}}
#data_dic = {'IDB-PT-07': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:05:20.155000', '2022-03-16 12:30:45.159000', '2022-03-16 11:41:57.554000', '2022-03-16 11:00:43.627000', '2022-03-16 10:28:58.203000', '2022-03-16 09:43:48.624000'], 'Filename': ['IY858-NYL5W', '9Z1QY-DGM3E', 'NQ8WC-auto', 'DU9TH-auto', 'DQRVB-auto', 'NUPA8-auto'], 'Runtime': ['0:29:49.965000', '0:30:16.979000', '0:30:30.152000', '0:29:09.271000', '0:28:56.269000', '0:42:37.748000'], 'Material': ['22.256794', '22.141927', '23.11121', '16.557993', '23.873707', '31.0559309'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-08': {'Print Number': [], 'Start Time': [], 'Filename': [], 'Runtime': [], 'Material': [], 'Completion': []}, 'IDB-PT-09': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:10:00.682000', '2022-03-16 12:35:39.077000', '2022-03-16 11:43:44.727000', '2022-03-16 11:07:04.311000', '2022-03-16 10:22:35.908000', '2022-03-16 09:48:01.232000'], 'Filename': ['K3UDR-auto', '2OYZI-auto', '96DXH', 'HZPI9-auto', 'SATIQ-auto', 'VRYJV-auto'], 'Runtime': ['0:31:36.833000', '0:31:38.282000', '0:29:25.784000', '0:29:22.979000', '0:32:44.175000', '0:29:35.533000'], 'Material': ['23.563462', '25.366265', '30.866296', '25.0518916', '23.742894', '23.137944'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-11': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:07:24.332000', '2022-03-16 12:35:59.838000', '2022-03-16 11:46:19.358000', '2022-03-16 11:07:24.877000', '2022-03-16 10:24:46.274000', '2022-03-16 09:50:21.898000'], 'Filename': ['3J59W-auto', '6673L-auto', '4YRCU-auto', 'WCDJK-ZIZ38', 'CLXYF-W537F', '02852-UEBQ9'], 'Runtime': ['0:28:01.594000', '0:29:22.841000', '0:30:41.043000', '0:31:09.269000', '0:30:02.344000', '0:29:08.473000'], 'Material': ['24.594843', '26.955557', '19.23872', '23.342313', '24.652116', '23.412955'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-12': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:02:02.500000', '2022-03-16 12:14:40.311000', '2022-03-16 11:40:04.892000', '2022-03-16 10:58:21.406000', '2022-03-16 10:20:36.536000', '2022-03-16 09:42:07.532000'], 'Filename': ['55IY3-auto', 'TUGC9-auto', 'GKZL8-auto', 'KGQOG-LZLBV', 'E2A2S-NYRFA', 'BJUE6-KGQOG'], 'Runtime': ['0:31:10.326000', '0:27:34.209000', '0:31:23.344000', '0:31:38.091000', '0:34:23.213000', '0:31:38.719000'], 'Material': ['23.75899', '22.32287', '22.0941802', '25.956911', '31.500522', '26.699679'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-13': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 12:57:50.234000', '2022-03-16 11:59:21.424000', '2022-03-16 11:21:08.356000', '2022-03-16 10:43:05.898000', '2022-03-16 10:04:33.782000'], 'Filename': ['RZOQE-XWYG9', 'IRE6B-N46DQ', 'ABGSW-K5TOT', '2SR9I-ELFNA', 'KILQV-MVB5F'], 'Runtime': ['0:29:33.184000', '0:31:39', '0:30:42.057000', '0:30:25.518000', '0:33:13.137000'], 'Material': ['18.00421236', '27.853992', '21.398314', '15.974282', '27.61321'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-14': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 13:20:44.024000', '2022-03-16 12:49:04.020000', '2022-03-16 11:52:11.032000', '2022-03-16 11:13:52.016000', '2022-03-16 10:25:56.512000'], 'Filename': ['DIHEK-MJYBG', 'SMR2L-WRX4N', '2U33G-3CTPA', 'HKR8O-MWMMH', 'CAMLR-FVPNL'], 'Runtime': ['0:29:19.274000', '0:29:19.279000', '0:31:21.272000', '0:29:46.289000', '0:33:22.538000'], 'Material': ['24.335385', '23.588719', '27.698816', '28.704109', '23.72156'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-15': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 12:55:13.446000', '2022-03-16 11:56:27.724000', '2022-03-16 11:18:47.266000', '2022-03-16 10:40:48.306000', '2022-03-16 10:01:49.186000'], 'Filename': ['LQ8OU-auto', 'K53OW-auto', 'HE2SX-auto', 'DRQUS-auto', '5LVLR-auto'], 'Runtime': ['0:28:54.384000', '0:25:50.886000', '0:29:34.565000', '0:28:54.031000', '0:31:08.438000'], 'Material': ['22.0503912', '4.128555', '21.537776', '21.91535', '20.789582'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-16': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:22:47.933000', '2022-03-16 12:50:57.945000', '2022-03-16 11:54:19.900000', '2022-03-16 11:16:42.585000', '2022-03-16 10:38:31.378000', '2022-03-16 09:59:57.853000'], 'Filename': ['SSKBC-auto', 'PDMPF-auto', '4UTV6-auto', 'ALQAS-auto', 'FS32E-X4H65', '23HZO-CMSDF'], 'Runtime': ['0:30:03.751000', '0:29:08.736000', '0:28:55.016000', '0:30:17.094000', '0:31:38.031000', '0:29:36.554000'], 'Material': ['25.795031', '23.33846', '23.262757', '25.0381324', '25.256576', '26.475941'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-17': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:24:56.080000', '2022-03-16 12:46:47.606000', '2022-03-16 11:50:08.664000', '2022-03-16 11:11:44.100000', '2022-03-16 10:36:02.524000', '2022-03-16 09:56:26.042000'], 'Filename': ['ND7O7-auto', 'QHT4P-auto', 'V5Q6N-auto', '6WJRY-auto', 'J3XUB-auto-2', '5FSCG-auto-2'], 'Runtime': ['0:27:19.035000', '0:34:18.014000', '0:44:53.924000', '0:28:41.005000', '0:30:42.090000', '0:30:25.079000'], 'Material': ['21.83621', '23.927395', '27.0662202', '23.650249', '21.906895', '15.665199'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}}
#data_dic = {'IDB-PT-07': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:05:20.155000', '2022-03-16 12:30:45.159000', '2022-03-16 11:41:57.554000', '2022-03-16 11:00:43.627000', '2022-03-16 10:28:58.203000', '2022-03-16 09:43:48.624000'], 'Filename': ['IY858-NYL5W', '9Z1QY-DGM3E', 'NQ8WC-auto', 'DU9TH-auto', 'DQRVB-auto', 'NUPA8-auto'], 'Runtime': ['0:29:49.965000', '0:30:16.979000', '0:30:30.152000', '0:29:09.271000', '0:28:56.269000', '0:42:37.748000'], 'Material': ['22.256794', '22.141927', '23.11121', '16.557993', '23.873707', '31.0559309'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-08': {'Print Number': [], 'Start Time': [], 'Filename': [], 'Runtime': [], 'Material': [], 'Completion': []}, 'IDB-PT-09': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:10:00.682000', '2022-03-16 12:35:39.077000', '2022-03-16 11:43:44.727000', '2022-03-16 11:07:04.311000', '2022-03-16 10:22:35.908000', '2022-03-16 09:48:01.232000'], 'Filename': ['K3UDR-auto', '2OYZI-auto', '96DXH', 'HZPI9-auto', 'SATIQ-auto', 'VRYJV-auto'], 'Runtime': ['0:31:36.833000', '0:31:38.282000', '0:29:25.784000', '0:29:22.979000', '0:32:44.175000', '0:29:35.533000'], 'Material': ['23.563462', '25.366265', '30.866296', '25.0518916', '23.742894', '23.137944'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-11': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:07:24.332000', '2022-03-16 12:35:59.838000', '2022-03-16 11:46:19.358000', '2022-03-16 11:07:24.877000', '2022-03-16 10:24:46.274000', '2022-03-16 09:50:21.898000'], 'Filename': ['3J59W-auto', '6673L-auto', '4YRCU-auto', 'WCDJK-ZIZ38', 'CLXYF-W537F', '02852-UEBQ9'], 'Runtime': ['0:28:01.594000', '0:29:22.841000', '0:30:41.043000', '0:31:09.269000', '0:30:02.344000', '0:29:08.473000'], 'Material': ['24.594843', '26.955557', '19.23872', '23.342313', '24.652116', '23.412955'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-12': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:02:02.500000', '2022-03-16 12:14:40.311000', '2022-03-16 11:40:04.892000', '2022-03-16 10:58:21.406000', '2022-03-16 10:20:36.536000', '2022-03-16 09:42:07.532000'], 'Filename': ['55IY3-auto', 'TUGC9-auto', 'GKZL8-auto', 'KGQOG-LZLBV', 'E2A2S-NYRFA', 'BJUE6-KGQOG'], 'Runtime': ['0:31:10.326000', '0:27:34.209000', '0:31:23.344000', '0:31:38.091000', '0:34:23.213000', '0:31:38.719000'], 'Material': ['23.75899', '22.32287', '22.0941802', '25.956911', '31.500522', '26.699679'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-13': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 12:57:50.234000', '2022-03-16 11:59:21.424000', '2022-03-16 11:21:08.356000', '2022-03-16 10:43:05.898000', '2022-03-16 10:04:33.782000'], 'Filename': ['RZOQE-XWYG9', 'IRE6B-N46DQ', 'ABGSW-K5TOT', '2SR9I-ELFNA', 'KILQV-MVB5F'], 'Runtime': ['0:29:33.184000', '0:31:39', '0:30:42.057000', '0:30:25.518000', '0:33:13.137000'], 'Material': ['18.00421236', '27.853992', '21.398314', '15.974282', '27.61321'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-14': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 13:20:44.024000', '2022-03-16 12:49:04.020000', '2022-03-16 11:52:11.032000', '2022-03-16 11:13:52.016000', '2022-03-16 10:25:56.512000'], 'Filename': ['DIHEK-MJYBG', 'SMR2L-WRX4N', '2U33G-3CTPA', 'HKR8O-MWMMH', 'CAMLR-FVPNL'], 'Runtime': ['0:29:19.274000', '0:29:19.279000', '0:31:21.272000', '0:29:46.289000', '0:33:22.538000'], 'Material': ['24.335385', '23.588719', '27.698816', '28.704109', '23.72156'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-15': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 12:55:13.446000', '2022-03-16 11:56:27.724000', '2022-03-16 11:18:47.266000', '2022-03-16 10:40:48.306000', '2022-03-16 10:01:49.186000'], 'Filename': ['LQ8OU-auto', 'K53OW-auto', 'HE2SX-auto', 'DRQUS-auto', '5LVLR-auto'], 'Runtime': ['0:28:54.384000', '0:25:50.886000', '0:29:34.565000', '0:28:54.031000', '0:31:08.438000'], 'Material': ['22.0503912', '4.128555', '21.537776', '21.91535', '20.789582'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-16': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:22:47.933000', '2022-03-16 12:50:57.945000', '2022-03-16 11:54:19.900000', '2022-03-16 11:16:42.585000', '2022-03-16 10:38:31.378000', '2022-03-16 09:59:57.853000'], 'Filename': ['SSKBC-auto', 'PDMPF-auto', '4UTV6-auto', 'ALQAS-auto', 'FS32E-X4H65', '23HZO-CMSDF'], 'Runtime': ['0:30:03.751000', '0:29:08.736000', '0:28:55.016000', '0:30:17.094000', '0:31:38.031000', '0:29:36.554000'], 'Material': ['25.795031', '23.33846', '23.262757', '25.0381324', '25.256576', '26.475941'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-17': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:24:56.080000', '2022-03-16 12:46:47.606000', '2022-03-16 11:50:08.664000', '2022-03-16 11:11:44.100000', '2022-03-16 10:36:02.524000', '2022-03-16 09:56:26.042000'], 'Filename': ['ND7O7-auto', 'QHT4P-auto', 'V5Q6N-auto', '6WJRY-auto', 'J3XUB-auto-2', '5FSCG-auto-2'], 'Runtime': ['0:27:19.035000', '0:34:18.014000', '0:44:53.924000', '0:28:41.005000', '0:30:42.090000', '0:30:25.079000'], 'Material': ['21.83621', '23.927395', '27.0662202', '23.650249', '21.906895', '15.665199'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}}
# data_dic = {'IDB-PT-07': {'Print Number': ['1', '2', '3', '4', '5', '6', '7'], 'Start Time': ['2022-03-16 14:01:58.135000', '2022-03-16 13:05:20.155000', '2022-03-16 12:30:45.159000', '2022-03-16 11:41:57.554000', '2022-03-16 11:00:43.627000', '2022-03-16 10:28:58.203000', '2022-03-16 09:43:48.624000'], 'Filename': ['ABGSW-K5TOT', 'IY858-NYL5W', '9Z1QY-DGM3E', 'NQ8WC-auto', 'DU9TH-auto', 'DQRVB-auto', 'NUPA8-auto'], 'Runtime': [datetime.timedelta(seconds=1830, microseconds=266000), datetime.timedelta(seconds=1789, microseconds=965000), datetime.timedelta(seconds=1816, microseconds=979000), datetime.timedelta(seconds=1830, microseconds=152000), datetime.timedelta(seconds=1749, microseconds=271000), datetime.timedelta(seconds=1736, microseconds=269000), datetime.timedelta(seconds=2557, microseconds=748000)], 'Material': ['20.589103', '22.256794', '22.141927', '23.11121', '16.557993', '23.873707', '31.0559309'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-08': {'Print Number': [], 'Start Time': [], 'Filename': [], 'Runtime': [], 'Material': [], 'Completion': []}, 'IDB-PT-09': {'Print Number': ['1', '2', '3', '4', '5', '6', '7'], 'Start Time': ['2022-03-16 14:03:36.599000', '2022-03-16 13:10:00.682000', '2022-03-16 12:35:39.077000', '2022-03-16 11:43:44.727000', '2022-03-16 11:07:04.311000', '2022-03-16 10:22:35.908000', '2022-03-16 09:48:01.232000'], 'Filename': ['7TC3N-auto', 'K3UDR-auto', '2OYZI-auto', '96DXH', 'HZPI9-auto', 'SATIQ-auto', 'VRYJV-auto'], 'Runtime': [datetime.timedelta(seconds=1857, microseconds=478000), datetime.timedelta(seconds=1896, microseconds=833000), datetime.timedelta(seconds=1898, microseconds=282000), datetime.timedelta(seconds=1765, microseconds=784000), datetime.timedelta(seconds=1762, microseconds=979000), datetime.timedelta(seconds=1964, microseconds=175000), datetime.timedelta(seconds=1775, microseconds=533000)], 'Material': ['24.272437', '23.563462', '25.366265', '30.866296', '25.0518916', '23.742894', '23.137944'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-11': {'Print Number': ['1', '2', '3', '4', '5', '6', '7'], 'Start Time': ['2022-03-16 14:06:04.834000', '2022-03-16 13:07:24.332000', '2022-03-16 12:35:59.838000', '2022-03-16 11:46:19.358000', '2022-03-16 11:07:24.877000', '2022-03-16 10:24:46.274000', '2022-03-16 09:50:21.898000'], 'Filename': ['NQ8WC-auto', '3J59W-auto', '6673L-auto', '4YRCU-auto', 'WCDJK-ZIZ38', 'CLXYF-W537F', '02852-UEBQ9'], 'Runtime': [datetime.timedelta(seconds=1842, microseconds=342000), datetime.timedelta(seconds=1681, microseconds=594000), datetime.timedelta(seconds=1762, microseconds=841000), datetime.timedelta(seconds=1841, microseconds=43000), datetime.timedelta(seconds=1869, microseconds=269000), datetime.timedelta(seconds=1802, microseconds=344000), datetime.timedelta(seconds=1748, microseconds=473000)], 'Material': ['23.85404', '24.594843', '26.955557', '19.23872', '23.342313', '24.652116', '23.412955'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-12': {'Print Number': ['1', '2', '3', '4', '5', '6', '7'], 'Start Time': ['2022-03-16 13:59:44.404000', '2022-03-16 13:02:02.500000', '2022-03-16 12:14:40.311000', '2022-03-16 11:40:04.892000', '2022-03-16 10:58:21.406000', '2022-03-16 10:20:36.536000', '2022-03-16 09:42:07.532000'], 'Filename': ['HZPI9-auto', '55IY3-auto', 'TUGC9-auto', 'GKZL8-auto', 'KGQOG-LZLBV', 'E2A2S-NYRFA', 'BJUE6-KGQOG'], 'Runtime': [datetime.timedelta(seconds=1763, microseconds=585000), datetime.timedelta(seconds=1870, microseconds=326000), datetime.timedelta(seconds=1654, microseconds=209000), datetime.timedelta(seconds=1883, microseconds=344000), datetime.timedelta(seconds=1898, microseconds=91000), datetime.timedelta(seconds=2063, microseconds=213000), datetime.timedelta(seconds=1898, microseconds=719000)], 'Material': ['25.514367', '23.75899', '22.32287', '22.0941802', '25.956911', '31.500522', '26.699679'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-13': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 12:57:50.234000', '2022-03-16 11:59:21.424000', '2022-03-16 11:21:08.356000', '2022-03-16 10:43:05.898000', '2022-03-16 10:04:33.782000'], 'Filename': ['RZOQE-XWYG9', 'IRE6B-N46DQ', 'ABGSW-K5TOT', '2SR9I-ELFNA', 'KILQV-MVB5F'], 'Runtime': [datetime.timedelta(seconds=1773, microseconds=184000), datetime.timedelta(seconds=1899), datetime.timedelta(seconds=1842, microseconds=57000), datetime.timedelta(seconds=1825, microseconds=518000), datetime.timedelta(seconds=1993, microseconds=137000)], 'Material': ['18.00421236', '27.853992', '21.398314', '15.974282', '27.61321'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-14': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 13:20:44.024000', '2022-03-16 12:49:04.020000', '2022-03-16 11:52:11.032000', '2022-03-16 11:13:52.016000', '2022-03-16 10:25:56.512000'], 'Filename': ['DIHEK-MJYBG', 'SMR2L-WRX4N', '2U33G-3CTPA', 'HKR8O-MWMMH', 'CAMLR-FVPNL'], 'Runtime': [datetime.timedelta(seconds=1759, microseconds=274000), datetime.timedelta(seconds=1759, microseconds=279000), datetime.timedelta(seconds=1881, microseconds=272000), datetime.timedelta(seconds=1786, microseconds=289000), datetime.timedelta(seconds=2002, microseconds=538000)], 'Material': ['24.335385', '23.588719', '27.698816', '28.704109', '23.72156'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-15': {'Print Number': ['1', '2', '3', '4', '5'], 'Start Time': ['2022-03-16 12:55:13.446000', '2022-03-16 11:56:27.724000', '2022-03-16 11:18:47.266000', '2022-03-16 10:40:48.306000', '2022-03-16 10:01:49.186000'], 'Filename': ['LQ8OU-auto', 'K53OW-auto', 'HE2SX-auto', 'DRQUS-auto', '5LVLR-auto'], 'Runtime': [datetime.timedelta(seconds=1734, microseconds=384000), datetime.timedelta(seconds=1550, microseconds=886000), datetime.timedelta(seconds=1774, microseconds=565000), datetime.timedelta(seconds=1734, microseconds=31000), datetime.timedelta(seconds=1868, microseconds=438000)], 'Material': ['22.0503912', '4.128555', '21.537776', '21.91535', '20.789582'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-16': {'Print Number': ['1', '2', '3', '4', '5', '6', '7'], 'Start Time': ['2022-03-16 14:09:52.097000', '2022-03-16 13:22:47.933000', '2022-03-16 12:50:57.945000', '2022-03-16 11:54:19.900000', '2022-03-16 11:16:42.585000', '2022-03-16 10:38:31.378000', '2022-03-16 09:59:57.853000'], 'Filename': ['EU4GV-auto', 'SSKBC-auto', 'PDMPF-auto', '4UTV6-auto', 'ALQAS-auto', 'FS32E-X4H65', '23HZO-CMSDF'], 'Runtime': [datetime.timedelta(seconds=1711, microseconds=814000), datetime.timedelta(seconds=1803, microseconds=751000), datetime.timedelta(seconds=1748, microseconds=736000), datetime.timedelta(seconds=1735, microseconds=16000), datetime.timedelta(seconds=1817, microseconds=94000), datetime.timedelta(seconds=1898, microseconds=31000), datetime.timedelta(seconds=1776, microseconds=554000)], 'Material': ['30.11591', '25.795031', '23.33846', '23.262757', '25.0381324', '25.256576', '26.475941'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}, 'IDB-PT-17': {'Print Number': ['1', '2', '3', '4', '5', '6'], 'Start Time': ['2022-03-16 13:24:56.080000', '2022-03-16 12:46:47.606000', '2022-03-16 11:50:08.664000', '2022-03-16 11:11:44.100000', '2022-03-16 10:36:02.524000', '2022-03-16 09:56:26.042000'], 'Filename': ['ND7O7-auto', 'QHT4P-auto', 'V5Q6N-auto', '6WJRY-auto', 'J3XUB-auto-2', '5FSCG-auto-2'], 'Runtime': [datetime.timedelta(seconds=1639, microseconds=35000), datetime.timedelta(seconds=2058, microseconds=14000), datetime.timedelta(seconds=2693, microseconds=924000), datetime.timedelta(seconds=1721, microseconds=5000), datetime.timedelta(seconds=1842, microseconds=90000), datetime.timedelta(seconds=1825, microseconds=79000)], 'Material': ['21.83621', '23.927395', '27.0662202', '23.650249', '21.906895', '15.665199'], 'Completion': ['Successful', 'Successful', 'Successful', 'Successful', 'Successful', 'Successful']}}
file_date = datetime.datetime.now().strftime("%m-%d-%Y")
datafile = f'IDB_Printer_Data_{file_date}'
with open(f'{datafile}.csv','w') as file:
    for printer, line in data_dic.items():
        print(printer, line)
        file.write(f'{printer}\n')
        file.write(f'Print Number, Start TimeStamp, Filename, Runtime, Material (ml), Completion\n')
        number_aborts = 0
        uptime = datetime.timedelta(seconds=0)
        material=0
        for [prt,srt,fln,run,mtl,cmp] in zip(data_dic[printer]['Print Number'],data_dic[printer]['Start Time'], data_dic[printer]['Filename'], data_dic[printer]['Runtime'], data_dic[printer]['Material'], data_dic[printer]['Completion']):
            line = [prt,srt,fln,run,mtl,cmp]
            if cmp != "Successful":
                number_aborts += 1
            uptime += run
            print(run)
            material+=float(mtl)
            for c,data in enumerate(line):
                # print(data,c)
                if not isinstance(data, str):
                    line[c] = str(data)
            file.write(f"{', '.join(line)}\n")


        try:
            # number_aborts = 0
            # for f in data_dic[printer]['Completion']:
            #     if f != "Successful":
            #         number_aborts += 1
            # uptime = datetime.timedelta(seconds=0)
            #
            # for run,mtl in data_dic[printer]['Runtime']:
            #     uptime += run
            #     print(run)
            print('total',uptime)
            avg_run = uptime.total_seconds() / len(data_dic[printer]['Runtime'])
            avg_run = datetime.timedelta(seconds=avg_run)
            avg_mat = material/len(data_dic[printer]['Material'])
            print('average',avg_run,avg_mat)
            file.write(f'Total, {len(data_dic[printer]["Print Number"])-number_aborts},  , {uptime}, {material}\n')
            file.write(f'  , , Averages, {avg_run}, {avg_mat}\n')
        except:
            print(traceback.format_exc())
        file.write('\n')

# for key,value in data_dic.items():
#     list_of_lines=[]
#     end_time=''
#     f_line=True
#     for line in value[::-1]:
#         list_of_lines.append(line)
#
#         if "JOB FINISHED" in line:
#
#             for c in range(100):
#                 try:
#                     t_finish = datetime.datetime.strptime(list_of_lines[-4][7:30],
#                                                           "%Y-%m-%d_%H:%M:%S.%f")
#
#                     break
#                 except ValueError:
#                     continue
#         if "START JOB" in line:
#
#             for c in range(100):
#                 try:
#                     t_start = datetime.datetime.strptime(list_of_lines[-4][7:30], "%Y-%m-%d_%H:%M:%S.%f")
#                     break
#                 except ValueError:
#                     continue
#
#             runtime = t_finish - t_start
#             #print(t_finish, t_start, runtime)
#             if abs(runtime)>datetime.timedelta(hours=1):
#                 #print(abs(runtime))
#                 continue
#
#             runtime_dic[key]=runtime_dic[key]+ runtime
#     last_time = t_start
#     print(key, last_time, runtime_dic[key])
#     runtime_str = '_'.join(str(runtime_dic[key]).split((', ')))
#     seconds = runtime_dic[key].total_seconds()
#     run_hours = str(seconds/(60*60))
#     csv_dic[key]=[key, str(last_time), runtime_str,run_hours]
#
# with open('printer_uptime.csv','w')as f:
#     f.write('Printer, Start of Log File, Total Uptime, Total Uptime(hours)\n')
#     for key,item in csv_dic.items():
#         f.write(f'{", ".join(csv_dic[key])}\n')