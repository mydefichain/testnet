from os import path, makedirs, listdir
import re
from json import JSONEncoder, dumps
from socket import gethostbyname, gethostname
from decimal import Decimal
from subprocess import check_output
import shutil
from bitcoinrpc.authproxy import AuthServiceProxy
from psutil import virtual_memory, cpu_percent, cpu_freq, net_io_counters
from psutil import cpu_count, disk_usage, disk_partitions


API_INDEX_PHP = "<?PHP header('Content-Type: application/json');\n"\
                "\n$data = file_get_contents('data.json');\n"\
                "\necho $data;\n\n?>"
GLOBAL_INDEX_PHP =  "<!DOCTYPE html>\n<html>\n<body>\n<?PHP\n$verzeichnis = '.';\n"\
                    "$verz_inhalt = scandir($verzeichnis);\nforeach ($verz_inhalt as $folder)"\
                    "{\n    if (is_dir($folder)){\n        echo '<a href=\"'.$folder.'/\">'.$folder.'</a><br>';\n"\
                    "}\n}\n?>\n</body>\n</html>"

class DecimalEncoder (JSONEncoder):
    def default (self, obj):
        if isinstance (obj, Decimal):
            return float (obj)
        return JSONEncoder.default (self, obj)

def read_deficonf(filename):
    returnvalue = {}
    with open(filename) as file:
        for line in file.read().split('\n'):
            if line.startswith("rpcuser"):
                returnvalue["rpcuser"]     = line.split("=")[1].strip(" ")
            elif line.startswith("rpcpassword"):
                returnvalue["rpcpassword"] = line.split("=")[1].strip(" ")
            elif line.startswith("rpcport"):
                returnvalue["rpcport"]     = line.split("=")[1].strip(" ")
            elif line.startswith("rpcbind"):
                returnvalue["rpcbind"]     = line.split("=")[1].strip(" ")
    return returnvalue

def create_connection_rpc(secrets):
    url = "http://%s:%s@%s:%s/"%(secrets["rpcuser"], secrets["rpcpassword"], secrets["rpcbind"], secrets["rpcport"])
    return AuthServiceProxy(url)

def save_json_to_www(folder, subfolder, data):
    if not path.exists(folder+"/"+subfolder):
        makedirs(folder+"/"+subfolder)
        phpfileobject = open(folder+"/"+subfolder+"/index.php", 'w')
        phpfileobject.write(API_INDEX_PHP)
        phpfileobject.close()
        #TODO 1 create empty data file
        #TODO 2 set chmod rights
        #TODO 3 set owner chown for new directory and file www-data

    if not path.isfile(folder+"/index.php"):
        phpfileobject = open(folder+"/index.php", 'w')
        phpfileobject.write(GLOBAL_INDEX_PHP)
        phpfileobject.close()

    json_data = dumps(data, cls = DecimalEncoder, sort_keys=True, indent=4)
    fileobject = open(folder+"/"+subfolder+"/data.json", 'w')
    fileobject.write(json_data)
    fileobject.close()
    return 0

def get_operators(filename):
    file = open(filename,'r')
    regex_pattern = r'masternode_operator\s*=\s*([A-HJ-NP-Za-km-z1-9]{34})'
    operatorlist = re.findall(regex_pattern, file.read())
    print (operatorlist)
    return operatorlist

def get_systeminfo():
    stats_data = {"disk_total": 0, "disk_used": 0, "disk_free": 0}
    partitions = disk_partitions()
    for i in enumerate(partitions):
        try:
            space = disk_usage(partitions[i[0]].mountpoint)
            stats_data["disk_total"] += space.total
            stats_data["disk_used"] += space.used
            stats_data["disk_free"] += space.free
        except Exception:
            continue

    stats_data["bytes_sent"]   = net_io_counters().bytes_sent
    stats_data["bytes_recv"]   = net_io_counters().bytes_recv
    stats_data["cpu_count"]    = cpu_count()
    stats_data["cpu_freq"]     = cpu_freq().current
    stats_data["cpu_load"]     = cpu_percent(interval=1, percpu=False)
    stats_data["memory_total"] = virtual_memory().total
    stats_data["memory_used"]  = virtual_memory().used
    stats_data["memory_free"]  = virtual_memory().free
    print (stats_data)
    return stats_data

def get_version(file):
    version = check_output([file, '--version'], encoding='UTF-8').split('\n', maxsplit=1)[0]
    print (version)
    return version

def get_servername():
    try:
        servername = gethostname()
        ip_address = gethostbyname(servername)
        print(f"IP address {ip_address} successfully collected for {servername}")
        return servername, ip_address
    except Exception:
        return "",""


def api_calls(filename):
    returnvalue = {}
    with open(filename) as file:
        for line in file.read().split('\n'):
            if line.startswith("=") or line.startswith("#"): #if header or commented, then skip
                continue
            if line:
                returnvalue[line.split(" ")[0]] = list(map(eval,line.split(" ")[1:]))
    return returnvalue

def remove_unused_dirs(folder, keep_dir):
    deleted = []
    for file in listdir(folder):
        if path.isdir(folder + "/" + file):
            if file.split("/")[-1] not in keep_dir:
                try:
                    shutil.rmtree(folder + "/" + file)
                    deleted.append(file)
                except OSError as err:
                    print(err)
                else:
                    print(f"The directory {file} is deleted successfully")
    return deleted