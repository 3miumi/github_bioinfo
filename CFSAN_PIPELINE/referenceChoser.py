import sys, os
from unittest import result
from urllib.request import FTPHandler
from matplotlib.pyplot import text
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import time
from collections import defaultdict
from subprocess import CalledProcessError
import requests, zipfile, io, gzip, shutil
from selenium.common.exceptions import NoSuchElementException, TimeoutException,StaleElementReferenceException


def main(args):
  
    opts = parse_cmdline_params(args[1:])
    folder =opts.folder 

    l = defaultdict()
    """In case any error happen, go to next SRR"""
    srrlist = opts.SRR.split()
    #fullpath is the path of reference from NCBI
    fullpath = ""
    for SRR in srrlist:
        fullpath = getContigs(SRR, folder, l)
        if fullpath != "":
            referencePath = download(folder, fullpath)
            break
    # fullpath = "" means the contigs of all SRR in list are out of limit.
    # choose whatever least contigs in the dict l.
    if fullpath == "":
        temp = min(l.values())
        res = [key for key in l if l[key] == temp]
        referencePath = download(folder, res[0])
    
    # referencePath is the path of reference where was already downloaded
    return referencePath




def getContigs(SRR, folder, l):
    PATH = 'https://www.ncbi.nlm.nih.gov/pathogens/'
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : folder}
    # headless mode
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument('--headless') 
    options.add_experimental_option("prefs",prefs)
    
    
    # "C:\\Users\ming\\Downloads\\chromedriver_win32\\chromedriver.exe"
    #    executable_path="/home/ming/dev/chromedriver",
    driver = webdriver.Chrome( executable_path="/home/ming/dev/chromedriver",chrome_options=options)
    driver.delete_all_cookies()



    
    driver.get(PATH)
    # find the searchbox
    searchbox = driver.find_element(By.XPATH,'//*[@id="main-isolates-search-field"]')
    # send SRR to search box
    searchbox.send_keys(SRR)

    search = waitUntil(driver, By.XPATH,'//*[@id="main-isolates-search"]/button/span')
    search.click()
    # driver.find_element(By.XPATH,'//*[@id="main-isolates-search"]/button/span').click()




    """
    There are two situations:
    1. The SRR doesn't have snp cluster. tab = 1
    2. The SRR has snp cluster. tab =2(most of time)
    """
    try:
        searchTable = waitUntil(driver, By.XPATH,'//*[@id="gridview-1022-record-65"]/tbody/tr/td[11]/div/a')
    # driver.find_element(By.XPATH,'//*[@id="gridview-1022-record-65"]/tbody/tr/td[6]/div/a')
        searchTable.click()
        driver.switch_to.window(driver.window_handles[1])
        print(driver.current_url)
        tab = 2
        # enable_download_in_headless_chrome(driver, opts.folders)


    except AttributeError:
        tab = 1
        pass
 
    headerchoose = waitUntil(driver, By.XPATH, '//*[@id="button-column-chooser-btnInnerEl"]')
    driver.implicitly_wait(5)
    headerchoose.click()

    # get "Contigs" column
    source_element = driver.find_element_by_xpath('//div[contains(text( ), "Contigs")]')
    dest_element = driver.find_element_by_xpath('//div[contains( text( ), "Organism group")]')
    
    ActionChains(driver).click_and_hold(source_element).move_to_element(dest_element).release(dest_element).perform()
    time.sleep(1)
    driver.implicitly_wait(10)
    # driver.save_screenshot("path to save screen.png") for debug
    colchoose = waitUntil(driver, By.XPATH, '//span[contains( text( ), "OK")]')
    colchoose.click()
    
    # get ascending button
    ascending = waitUntil(driver, By.XPATH , '//*[@id="gridcolumn-1058-triggerEl"]')
    driver.execute_script("arguments[0].click();", ascending)
    driver.implicitly_wait(10)


    ascending_excute = waitUntil(driver, By.XPATH,'//span[contains(text( ), "Sort Ascending")]')


        
    driver.execute_script("arguments[0].click();", ascending_excute)
    # driver.implicitly_wait(20)
    time.sleep(2)

    contigs,species = getContigsNumber(driver, tab)
    
    # driver.implicitly_wait(15)
    time.sleep(1)


    # Set contigs limit for difference spcies
    fullPath = ""
    if ("Listeria" in species and int(contigs) >= 25 ) or ("Salmonella"  in species and int(contigs) >= 40) or ("E.coli"  in species and int(contigs) >= 80):
        print("The contigs number for " + SRR + " is "+ str(contigs))
        fullPathTemp = getGCA(driver,tab)
        l[fullPathTemp] = int(contigs)
        print("Go to next SRR")
    
    else:
        print("The contigs number for " + SRR + " is "+ str(contigs))
        fullPath = getGCA(driver,tab)
    

    driver.close()
    return fullPath






"""Get contigs number"""
# There are two situations:
# 1. The SRR doesn't have snp cluster. tab = 1, and the contigs column may be 3, 4
# 2. The SRR has snp cluster. tab =2, and the contigs column may be 2, 3
def getContigsNumber(driver, tab):
    # In the drag and drop process, the contig may be drop below or above Organism group. The contigs column 
    # is either in column 3 or 4. Need to be determine
    leastContigs = waitUntil(driver, By.XPATH,'//*[starts-with(@id,"gridview-1022-record")]/tbody/tr/td[3]/div')
    if leastContigs.text.isnumeric():
        if tab == 1:
            species = waitUntil(driver, By.XPATH,'//*[starts-with(@id,"gridview-1022-record")]/tbody/tr/td[2]/div').text
        else:
            species = waitUntil(driver, By.XPATH,'//*[starts-with(@id,"gridview-1022-record")]/tbody/tr/td[4]/div').text
    

    else:
        if tab == 1:
            leastContigs = waitUntil(driver, By.XPATH,'//*[starts-with(@id,"gridview-1022-record")]/tbody/tr/td[2]/div')
            
        else:
            leastContigs = waitUntil(driver, By.XPATH,'//*[starts-with(@id,"gridview-1022-record")]/tbody/tr/td[4]/div')
        
        species = waitUntil(driver, By.XPATH,'//*[starts-with(@id,"gridview-1022-record")]/tbody/tr/td[3]/div').text
    # driver.implicitly_wait(15)
    time.sleep(1)
    contigs =  leastContigs.text

    #return contigs number and speices name
    return contigs, species

    




    


def getGCA(driver,tab):
# get GCA information
    try:
        targetGCA = waitUntil(driver, By.XPATH,'//*[starts-with(@id,"gridview-1022-record")]/tbody/tr/td[16]/div/a')
        driver.implicitly_wait(15)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", targetGCA)
        targetGCA = targetGCA.text
        time.sleep(1)
    except NoSuchElementException:
        return ""

    
    # swicth to the second/third tab
    driver.switch_to.window(driver.window_handles[tab])
    # driver.save_screenshot("path to save screen.png")

    try:
        ftp = waitUntil(driver, By.XPATH, '//*[@id="ui-portlet_content-1"]/ul/li[3]/a')
        ftp.click()
        time.sleep(1)
    except StaleElementReferenceException:
        return ""



    ftpName = driver.current_url.split("/")[-2] + "_genomic.fna.gz"
    # ftpName =waitUntil(driver, By.XPATH, '//a[contains(text(),"genomic.fna.gz")]').text
    # ftpName =waitUntil(driver, By.XPATH, '/html/body/pre/a[7]').text
    fullPath = driver.current_url + ftpName
    return fullPath










def download(folder, fullPath):
# download fna.gz file to current/reference folder
    ftpName = fullPath.split("/")[-1]
    ftp_local_path = os.path.join(folder, ftpName)
    with open(ftp_local_path, "wb") as f:
        r = requests.get(fullPath)
        f.write(r.content)

    unzip_filename = os.path.splitext(ftpName)[0]
    unzip_local_path = os.path.join(folder, unzip_filename)
    with gzip.open(ftp_local_path, 'rb') as f_in:
        with open(unzip_local_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(ftp_local_path)


    return unzip_filename




def waitUntil(driver, by, xpath):
    timeout = 5
    try:
        element_present = EC.presence_of_element_located((by,xpath))
        
        return WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        pass


# def enable_download_in_headless_chrome(driver, download_dir):
#     # add missing support for chrome "send_command"  to selenium webdriver
#     driver.command_executor._commands["send_command"] = ("POST",'/session/$sessionId/chromium/send_command')
#     params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
#     command_result = driver.execute("send_command", params)



def parse_cmdline_params(arg_list):
    """Parses commandline arguments.
    :param arg_list: Arguments to parse. Default is argv when called from the
    command-line.
    :type arg_list: list.
    """
    #Create instance of ArgumentParser
    options_parser = ArgumentParser(formatter_class=
                                    ArgumentDefaultsHelpFormatter)
    options_parser.add_argument('--SRR', dest='SRR', type=str, required=True,
                                help="SRR number need to be searched")
    options_parser.add_argument('--folder', dest='folder', type=str, required=True,
                                help="Destination folder to download")

    opts = options_parser.parse_args(args=arg_list)
    return opts

    
if __name__ == "__main__":
    main(sys.argv)