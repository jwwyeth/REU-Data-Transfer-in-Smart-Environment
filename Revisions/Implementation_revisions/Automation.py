import os
import time
import subprocess
import requests

# Set the GitHub permalinks for each file
RE_path = "FILE PATH GOES HERE"
AMDT1_permalink = 'FILE PATH GOES HERE'
AMDT2_permalink = 'FILE PATH GOES HERE'
AM1_permalink = 'FILE PATH GOES HERE'
AM2_permalink = 'FILE PATH GOES HERE'
num_iterations = 1


print("Running RE...")
os.system(f"start cmd /k python \"{RE_path}\"")


# Loop through the files in the desired order
for i in range(num_iterations):
    print(f"Iteration {i}...")
    
    # Run AMDT1
    print("Running AMDT1...")
    os.system(f"start cmd /k python \"{AMDT1_permalink}\"")
    #greenflag.sendall('green'.encode())
    # Run AMDT2 on the Mac machine
    print("Running AMDT2...")
    
    os.system(f"start cmd /k python \"{AMDT2_permalink}\"")
    
    # Run AM1 on the Mac machine
    print("Running AM1...")

    os.system(f"start cmd /k python \"{AM1_permalink}\"")
 
    # Run AM2
    #greenflag.recv(1024).decode()
    print("Running AM2...")
    os.system(f"start cmd /k python \"{AM2_permalink}\"")
    
    # Wait for 1 second before the next iteration
    time.sleep(5)
    #print("Killing all cmd.exe processes...")
    
    #os.system("taskkill /im cmd.exe /f")

print("Completed!")