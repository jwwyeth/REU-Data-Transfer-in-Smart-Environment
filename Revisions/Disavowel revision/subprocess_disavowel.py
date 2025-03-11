import os
import time
import subprocess
import socket

# Set the file paths and machine names
Repath="C:\\Users\\Pikmi\\OneDrive\\Desktop\\revisions\\Disavowel-revision\\RE.py"
print("Running RE...")
os.system(f"start cmd /k python \"{Repath}\"")


'''
#STAGe 2 DT_AM
green_flag_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR=socket.gethostbyname(socket.gethostname()), 5060
green_flag_socket.bind(ADDR)
green_flag_socket.listen()
greenflag,address=green_flag_socket.accept()
print('connected to', address)
'''
amdt1_path = "C:\\Users\\Pikmi\\OneDrive\\Desktop\\revisions\\Disavowel-revision\\AMDT1.py"
amdt2_path = "C:\\Users\\Pikmi\\OneDrive\\Desktop\\revisions\\Disavowel-revision\\AMDT2.py"
am1_path = "C:\\Users\\Pikmi\\OneDrive\\Desktop\\revisions\\Disavowel-revision\\AM1.py"
am2_path = "C:\\Users\\Pikmi\\OneDrive\\Desktop\\revisions\\Disavowel-revision\\AM2.py"

# Set the number of iterations
num_iterations =1


# Loop through the files in the desired order
for i in range(num_iterations):
    print(f"Iteration {i}...")
    
    # Run AMDT1
    print("Running AMDT1...")
    os.system(f"start cmd /k python \"{amdt1_path}\"")
   # greenflag.sendall('green'.encode())
    # Run AMDT2 on the Mac machine
    #print("Running AMDT2...")
    
    os.system(f"start cmd /k python \"{amdt2_path}\"")
    
    # Run AM1 on the Mac machine
    #print("Running AM1...")

    #os.system(f"start cmd /k python \"{am1_path}\"")
 
    # Run AM2
   # greenflag.recv(1024).decode()
    print("Running AM2...")
    #os.system(f"start cmd /k python \"{am2_path}\"")
    
    # Wait for 1 second before the next iteration
    #time.sleep(5)


    print("run completed, ending now")
    time.sleep(1)

    #os.system("taskkill /im cmd.exe /f")



with open(r"output.txt","r")as fp:
    lines = len(fp.readlines())
    print('\nTotal Number of successful Disavowel Instances over',num_iterations, 'iterations:', lines)
