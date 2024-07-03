import os
import time
import subprocess
import socket

#SERVER= '<insert ip address>'
#ADDR=(SERVER,5060)

#greenflag=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#greenflag.connect(ADDR)

# Set your own file paths and machine names
RE_path = "<insert file path>"
amdt1_path = "insert file path>" 
amdt2_path = "insert file path>"
am1_path = "insert file path>"
am2_path = "insert file path>"

print("Running RE...")
os.system("gnome-terminal -- bash -c 'python3 " + RE_path + "; bash'")

# Set the number of iterations
num_iterations = 1

# Loop through the files in the desired order
for i in range(num_iterations):
    print(f"Iteration {i+1}...")
    
   # Run AMDT1
    print("Running AMDT1...")
    os.system("gnome-terminal -- bash -c 'python3 " + amdt1_path + "; bash'")

    # Run AMDT2 on the Linux machine
    print("Running AMDT2...")
    os.system("gnome-terminal -- bash -c 'python3 " + amdt2_path + "; bash'")

    print("Running AM1...")
    os.system("gnome-terminal -- bash -c 'python3 " + am1_path + "; bash'")
    
    # Run AM2
    print("Running AM2...")
    os.system("gnome-terminal -- bash -c 'python3 " + am2_path + "; bash'")
    
    # Wait for 1 second before the next iteration
    time.sleep(5)
print("Killing all Terminal processes...")

print("Completed!")