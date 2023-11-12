from typing import Union,List
from utils.file_io import read_txt,get_file_list
from config import REDIS_HOST,CHROME_DRIVER_PATH,APK_SAVE_PATH
from redis import Redis
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep,time
from random import randint
from traceback import print_exc
from multiprocessing import Pool
from utils.my_logging import FileLogger
import os
from utils.androguard_parse import AndroguardParse
from shutil import move
from tqdm import tqdm
from argparse import ArgumentParser
logger = FileLogger(log_file="./log/download.log",log_name="download",log_level="INFO")
redis_client = Redis(host=REDIS_HOST,port=6379,db=0)
script = """
var items = document.querySelector('downloads-manager')
    .shadowRoot.getElementById('downloadsList').items;
if (items.every(e => e.state === "COMPLETE"))
    return items.map(e => e.fileUrl || e.file_url);
"""

def load_app_id(app_lst_file:str,begin:int=0,offset:int=100):
    return read_txt(app_lst_file)[begin:begin+offset]

def check_missing_apk(app_list:Union[str,List],store_path:str):
    """
    check missing apk\\
    :param app_list: app id list or app id file path\\
    :param store_path: apk save path\\
    """
    file_lst = get_file_list(source_dir=store_path)
    package_lst = []
    for file in tqdm(file_lst,desc="check miss"):
        if file.endswith(".apk"):
            package_lst.append(str(AndroguardParse(file=file).get_package()).strip())
    if isinstance(app_list,str):
        app_list = read_txt(app_list)
    miss = list(set(app_list).difference(set(package_lst)))
    return miss

def modify_apk_name(store_path:str):
    file_lst = get_file_list(store_path)
    for file in tqdm(file_lst,desc="rename"):
        if file.endswith(".apk") and "_Apkpure" in file:
            package = str(AndroguardParse(file=file).get_package())
            move(file,os.path.join(store_path,f"{package}.apk"))
    return

def check_apk_count(store_path:str,clean_others:bool=True):
    """
    check store path apk count\\
    :param store_path: apk save path\\
    :param clean_others: clean other files\\
    """
    files = get_file_list(source_dir=store_path)
    count = 0
    if clean_others:
        for file in files:
            if not file.endswith(".apk"):
                os.remove(file)
            else:
                count+=1
    else:
        for file in files:
            if file.endswith(".apk"):
                count+=1
    return count

def insert_into_redis(app_list:List):
    """
    insert into redis for mutirprocess
    """
    redis_client = Redis(host=REDIS_HOST,port=6379,db=0)
    # clean redis
    redis_client.delete("apkpure")
    redis_client.sadd("apkpure",*app_list)
    print(f"insert {len(app_list)} to redis done!!!")

def get_download_url(app_id:str,version_code:str=""):
    """
    get app download url
    """
    if len(version_code) == 0:
        return f'https://d.apkpure.com/b/APK/{app_id}?version=latest'
    else:
        return f'https://d.apkpure.com/b/APK/{app_id}?versionCode={version_code}'

def check_download_finish(driver):
    """
    check download status
    """
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    return driver.execute_script(script)

def download_apks(url_list:List,store_path:str,chrome_driver_path:str,wait_check_time:int=20,download_timeout:int=360,poll_frequency:int=1):
    """
    control browser to download apps\\
    :param url_list: app download url list\\
    :param wait_check_time: wait time for check download status\\
    :param download_timeout: download timeout\\
    :param poll_frequency: check download timeout frequency\\
    """
    option = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": store_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    option.add_experimental_option("prefs", prefs)

    browser = webdriver.Chrome(executable_path=chrome_driver_path, options=option)
    for url in url_list:
        browser.get(url)
    
    sleep(wait_check_time)
    WebDriverWait(browser,download_timeout,poll_frequency).until(check_download_finish)
    sleep_time = randint(1,6)
    sleep(sleep_time)
    browser.quit()

def process(apps:List,store_path:str,chrome_driver_path:str):
    url_list = []
    try:
        for app in apps:
            url=get_download_url(app)
            url_list.append(url)
        download_apks(url_list,store_path,chrome_driver_path)
    except Exception as e:
        print_exc()
    return

def multi_process(worker:int=2,batch_size = 10,store_path:str=None,chrome_driver_path:str=None,miss_mode:bool=False):
    start_time = time()
    pool = Pool(processes=worker)
    flag = False
    redis_client = Redis(host=REDIS_HOST,port=6379,db=0)
    while True:
        app_lst = []
        for i in range(batch_size):
            app = redis_client.spop("apkpure")
            if app is None:
                flag = True
                break
            app_lst.append(app.decode())
        pool.apply_async(process,args=(app_lst,store_path,chrome_driver_path,))
        if flag:
            break
    pool.close()
    pool.join()
    end_time = time()
    # time format minute
    cost_time = (end_time-start_time)/60
    count = check_apk_count(store_path,clean_others=True) # must clean non-apk file
    if miss_mode:
        logger.info(f"miss mode: download {count} app, cost {cost_time} mins")
    else:
        logger.info(f"norm mode: download {count} app, cost {cost_time} mins")

if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('-m',"--miss",action="store_true",help="miss mode")
    parser.add_argument("-b","--begin",type=int,default=0,help="begin index")
    parser.add_argument("-f","--offset",type=int,default=100,help="offset")
    args = parser.parse_args()
    miss = args.miss
    begin = args.begin
    offset = args.offset
    app_list_path = r"E:\apkpure_download\app_list\google-play-app.txt"
    app_list = load_app_id(app_list_path,begin,offset)
    if miss:
        miss_list = check_missing_apk(app_list,APK_SAVE_PATH)
        insert_into_redis(miss_list)
    else:
        insert_into_redis(app_list)
    multi_process(worker=2,batch_size=10,store_path=APK_SAVE_PATH,chrome_driver_path=CHROME_DRIVER_PATH,miss_mode=miss)
    modify_apk_name(APK_SAVE_PATH)