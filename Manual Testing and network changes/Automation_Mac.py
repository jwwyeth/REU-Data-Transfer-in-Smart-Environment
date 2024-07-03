import os
import time
import subprocess
import socket

#SERVER="input ip address"
#ADDR=(SERVER,5060)

#greenflag=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#greenflag.connect(ADDR)

# Set the file paths and machine names
RE_path = "<insert file path>"
amdt1_path = "<insert file path>"
amdt2_path = "<insert file path>"
am1_path = "<insert file path>"
am2_path = "<insert file path>"

#start RE
print("Running RE...")
os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{RE_path}\\\"\"'")

# Set the number of iterations
num_iterations = 1

# Loop through the files in the desired order
for i in range(num_iterations):
    print(f"Iteration {i+1}...")
    
    # Run AMDT1
    print("Running AMDT1...")
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{amdt1_path}\\\"\"'")

    # Run AMDT2 on the Mac machine
    #greenflag.recv(1024).decode()
    print("Running AMDT2...")
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{amdt2_path}\\\"\"'")

    #greenflag.sendall('green'.encode())
    print("Running AM1...")
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{am1_path}\\\"\"'")
    
    # Run AM2
    print("Running AM2...")
    os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{am2_path}\\\"\"'")
    
    # Wait for 1 second before the next iteration
    time.sleep(1)
print("Killing all Terminal processes...")
#os.system("pkill Terminal")

print("Completed!")