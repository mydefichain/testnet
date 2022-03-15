from os import path
from logging import basicConfig, info, INFO
from credentials import WWW_DIR, DEFID, DEFICONF, API_LIST
from subfunctions import save_json_to_www, create_connection_rpc, get_systeminfo, get_version
from subfunctions import read_deficonf, remove_unused_dirs, api_calls, get_operators, get_servername

# psutil, shutil, python-bitcoinrpc, requests nicht Standardinstallation

# variables
filename = path.basename(__file__)
directory = path.dirname(__file__)
logfile = path.dirname(__file__)+"/"+filename.split(".")[0]+".log"

# program start
basicConfig(filename=logfile, format='%(asctime)s - %(message)s', level=INFO)
info("######################################")
info(f"Start {filename}")

errors = []

#TODO put a try, except around the special functions or direct in the subfunctions
KEEP_DIRECTORYS = ["systeminfo","version","operatoraddresses"]
save_json_to_www(WWW_DIR, "systeminfo",        get_systeminfo())
save_json_to_www(WWW_DIR, "version",           get_version(DEFID))
save_json_to_www(WWW_DIR, "operatoraddresses", get_operators(DEFICONF))

rpc_connection = create_connection_rpc(read_deficonf(DEFICONF))

try:
    functions = api_calls(API_LIST)
except Exception as e:
    functions = {}
    errors.append(f'api_calls() {str(e)}')
    print (f'api_calls() {str(e)}')

if functions:
    for i in functions:
        print (f'{i} {functions[i]}')
        info (f'{i} {functions[i]}')
        try:
            if   len(functions[i]) == 0:
                save_json_to_www(WWW_DIR, i, getattr(rpc_connection, i)())
            elif len(functions[i]) == 1:
                save_json_to_www(WWW_DIR, i, getattr(rpc_connection, i)(functions[i][0]))
            elif len(functions[i]) == 2:
                save_json_to_www(WWW_DIR, i, getattr(rpc_connection, i)(functions[i][0], functions[i][1]))
            elif len(functions[i]) == 3:
                save_json_to_www(WWW_DIR, i, getattr(rpc_connection, i)(functions[i][0], functions[i][1], functions[i][2]))
        except Exception as e:
            errors.append(f'{i} {str(e)}')
            print (f'{i} {str(e)}')

servername, ip_address = get_servername()

print(f'removed directorys: {remove_unused_dirs(WWW_DIR, list(functions.keys()) + KEEP_DIRECTORYS)}')

if errors:
    text = f"Problems with {filename} on {servername} {ip_address}\n{errors}"
    print (text)
    info (text)

info(f"End {filename}")
