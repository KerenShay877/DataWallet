
#try 1:
import os
import time
time = "1585226467.8931706"
directory = "C:/Users/user/Desktop/Magshimim_Project/project-604/hospital_files/patient_md_files"
request = "760,325002426,0"
files = os.listdir(directory+"/"+request.split(",")[1])
for file in files:
    file_time = os.path.getctime(directory+"/"+request.split(",")[1]+"/"+file)
    print(file_time)
    if float(file_time) > float(time):
        print(file)
