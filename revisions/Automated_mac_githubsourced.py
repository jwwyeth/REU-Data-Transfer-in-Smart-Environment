import os
import time
import subprocess
import requests
import platform

# Set the GitHub permalinks for each file
RE_permalink = 'https://raw.github.com/jwwyeth/REU-Data-Transfer-in-Smart-Environment/dcbff18387b3cf90e5a10f5fda2d1f66440a029e/Automated%20showcase/RE.py'
AMDT1_permalink = 'https://raw.github.com/jwwyeth/REU-Data-Transfer-in-Smart-Environment/dcbff18387b3cf90e5a10f5fda2d1f66440a029e/Automated%20showcase/AMDT1.py'
AMDT2_permalink = 'https://raw.github.com/jwwyeth/REU-Data-Transfer-in-Smart-Environment/dcbff18387b3cf90e5a10f5fda2d1f66440a029e/Automated%20showcase/AMDT2.py'
AM1_permalink = 'https://raw.github.com/jwwyeth/REU-Data-Transfer-in-Smart-Environment/dcbff18387b3cf90e5a10f5fda2d1f66440a029e/Automated%20showcase/AM1.py'
AM2_permalink = 'https://raw.github.com/jwwyeth/REU-Data-Transfer-in-Smart-Environment/dcbff18387b3cf90e5a10f5fda2d1f66440a029e/Automated%20showcase/AM2.py'

# Set the number of iterations
num_iterations = 1

# Loop through the files in the desired order
for i in range(num_iterations):
    print(f"Iteration {i+1}...")
    '''
    # Download and run RE
    print("Running RE...")
    response = requests.get(RE_permalink)
    with open('RE_fromgit.py', 'wb') as f:
        f.write(response.content)
        os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{os.getcwd()}/{'RE_fromgit.py'}\\\"\"'")
    
    # Download and run AMDT1
    print("Running AMDT1...")
    response = requests.get(AMDT1_permalink)
    with open('AMDT1_fromgit.py', 'wb') as f:
        f.write(response.content)
        os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{os.getcwd()}/{'AMDT1_fromgit.py'}\\\"\"'")
    '''
    # Download and run AMDT2
    print("Running AMDT2...")
    response = requests.get(AMDT2_permalink)
    with open('AMDT2_fromgit.py', 'wb') as f:
        f.write(response.content)
        os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{os.getcwd()}/{'AMDT2_fromgit.py'}\\\"\"'")
    
    # Download and run AM1
    print("Running AM1...")
    response = requests.get(AM1_permalink)
    with open('AM1_fromgit.py', 'wb') as f:
        f.write(response.content)
        os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{os.getcwd()}/{'AM1_fromgit.py'}\\\"\"'")

    
    # Download and run AM2
    print("Running AM2...")
    response = requests.get(AM2_permalink)
    with open('AM2_fromgit.py', 'wb') as f:
        f.write(response.content)
        os.system(f"osascript -e 'tell application \"Terminal\" to do script \"python3 \\\"{os.getcwd()}/{'AM2_fromgit.py'}\\\"\"'")

    
    # Wait for 1 second before the next iteration
    time.sleep(1)

print("Completed!")