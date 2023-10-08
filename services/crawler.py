import os
import time
from glob import glob
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class CrawlerTJSP():
    
    
    def __init__(self, user: str, pswd:str, download_dir=None) -> None:
        """_summary_

        Args:
            user (str): _description_
            pswd (str): _description_
            download_dir (_type_, optional): _description_. Defaults to None.
        """
        self.__user = user # username
        self.__pswd = pswd # password
        
        # Checks if the dowload_dir already exists if not so create the diretory.
        if not download_dir:
            download_dir = os.path.expanduser('~')
        
        # Options to personalize the browser operation.
        options = Options()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", 
                               False)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                               "application/pdf")
        options.set_preference("pdfjs.disabled", True)
        self.__driver = webdriver.Firefox(options=options)
    
    def login(self):
        """
        Method to log into the TJSP site
        """
        tjsp_url = "https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fesaj%2Fj_spring_cas_security_check"
        self.__driver.get(tjsp_url) # It conect with the TJSP site.
        
        # Find username field and send the username itself to the input field
        self.__driver.find_element("id", "usernameForm").send_keys(self.__user)
        # Find password input field and insert password as well
        self.__driver.find_element("id", "passwordForm").send_keys(self.__pswd)
        # Click login button
        self.__driver.find_element("name", "pbEntrar").click()
    
    def find_lawsuit(self, lawsuit: str):
        """
        Method to find the lawsuits into the TJSP site.

        Args:
            lawsuit (str): String with the lawsuit number.
        """
        # Apart the lawsuit number in two parts one before and one after the .8.26
        # .8.26 is a comom value to all the lawsuit numbers in TJSP, and it is
        # already filed in the search bar in the site of TJSP.
        part1, part2 = lawsuit.split('.8.26') 
        # Open the search page
        self.__driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        # Fill the first part of the lawsuit
        self.__driver.find_element("name", "numeroDigitoAnoUnificado").send_keys(part1)
        # Fill the second part of the lawsuit
        self.__driver.find_element("name", "foroNumeroUnificado").send_keys(part2)
        # Wait 5 seconds util next action, it is necessary to avoid bloking in the TJSP
        time.sleep(5)
        # Find the search lawsuit button and click
        self.__driver.find_element("id", "botaoConsultarProcessos").click()
    
    def find_incidentes(self):
        """
        Method to find incidentes in the lawsuits.
        """
        self.__incidentes_links = []
        
        # In pages that do not have "incidentes" this method skips.
        try:
            # Find the list of "incidente"
            incidentes = self.__driver.find_elements(By.CLASS_NAME, "incidente")
            self.__incidentes_links = []
            
            # Extract the url of each "incidente"
            for incidente in incidentes:
                self.__incidentes_links.append(incidente.get_attribute("href"))
            
        except Exception as e:
            print(e)
    
    def start_download(self, link:str=None, replace_file:bool=False, download_dir:str=None) -> bool:
        """
        Method to download the lawsuits reports.

        Args:
            link (str, optional): Adress of the lawsuit report. Defaults to None.
            replace_file (bool, optional): If True it will overwrite previous reports other wise it will skip the download of repeated lawsuit reports. Defaults to False.
            download_dir (str, optional): Directory where the lawsuit reports will be storaged. Defaults to None.

        Returns:
            bool: If False means the occurred an error during the download.
        """
        # Connect with the lawsuit report page.
        if link:
            self.__driver.get(link)
        
        # If the download_dir was not specified it will do the download in the user main directory.
        if not download_dir:
            download_dir = os.path.expanduser('~')
        
        # Checks if there lawsuit reports available in the page.
        try:
            self.__driver.find_element("id", "linkPasta").click()
        except:
            return False
        
        time.sleep(3)
        
        # Get element that contains the lawsuit report
        element = self.__driver.find_element(By.CLASS_NAME, "unj-larger")
        
        # Extract the lawsuit number from the report page
        lawsuit = element.get_attribute('innerText')
        lawsuit = ''.join(lawsuit.split('(')[1:]).replace(') ', '-').replace(')', '')
        
        if lawsuit[-1] == '-':
            lawsuit = lawsuit[:-1]

        # Specify the lawsuit report filename in the download directory
        lawsuit_file = f'{download_dir}/{lawsuit}.pdf'
        
        # Check if lawsuit_file already exists in the download directory
        if os.path.isfile(lawsuit_file):
            # If is not to replace the file it ends the method
            if replace_file == False:
                self.__driver.close()
                window_after = self.__driver.window_handles[0]
                self.__driver.switch_to.window(window_after)
                return None
            else:
                # Otherwise it removes the existing file in continues the method
                os.remove(lawsuit_file)
        
        # The lawsuit report is always opened in another window so it changes the
        # current windows. 
        window_after = self.__driver.window_handles[1]
        self.__driver.switch_to.window(window_after)
        time.sleep(3)
        
        # This instructions interate with the download pop-up
        WebDriverWait(self.__driver, 1).until(EC.presence_of_element_located((By.ID, "selecionarButton"))).click()
        self.__driver.find_element("id", "selecionarButton").click()
        self.__driver.find_element("id", "salvarButton").click()
        WebDriverWait(self.__driver, 20).until(EC.presence_of_element_located((By.ID, "opcao1"))).click() # Download all files as an unique document.
        self.__driver.find_element("id", "opcao1").click()
        self.__driver.find_element("id", "botaoContinuar").click()
        WebDriverWait(self.__driver, 5).until(EC.presence_of_element_located((By.ID, "imgSuccess")))

        # The method needs to wait until the requisition is ready
        while True:
            try:
                # Indicates that is necessary wait
                btnDownload = self.__driver.find_element("id", "btnAguardarProcessamento")
                btnDownloadAttrs = self.__driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', btnDownload)
                time.sleep(1)
                if 'style' in list(btnDownloadAttrs.keys()):
                    break
            except:
                break
        
        # When the requisition is ready it clicks in the final download button
        self.__driver.find_element("id", "btnDownloadDocumento").click()

        # It wait until the download is finished. It is necessary to avoid to
        # close the driver before the download is finished and corrupt the files
        while True:
            if not len(glob(f'{download_dir}/*.pdf.part')):
                break
        
        # When the download is finished the currente windows is closed and the
        # method returnd to previous windows to coninue the downloads.
        self.__driver.close()
        window_after = self.__driver.window_handles[0]
        self.__driver.switch_to.window(window_after)

        # It renames the downloaded files to keeps in the pattern where the 
        # filename is the lawsuit number.
        try:
            file_download = glob('-'.join(lawsuit_file.split('-')[:-1])+'.pdf')[0]
            os.rename(file_download, lawsuit_file)
        except:
            file_download = glob(lawsuit_file)[0]
            os.rename(file_download, lawsuit_file)   
    
    def download_data(self, lawsuits:List[str], replace_file:bool=False, download_dir:str=None):
        """
        Method do automates the download of all documents related with the specified
        lawsuits list.

        Args:
            lawsuits (List[str]): List of the list of lawsuit numbers to download the reports.
            replace_file (bool, optional): When True if marks to overwirite previous lawsuit reports. Defaults to False.
            download_dir (str, optional): Specifies the download direcory, where the files will be saved. Defaults to None.
        """
        # If the download_dir was not specified it will do the download in the user main directory.
        if not download_dir:
            download_dir = os.path.expanduser('~')
        
        # Interates along the lawsuits list
        for lawsuit in lawsuits:
            self.find_lawsuit(lawsuit) # Find the lawsuits
            time.sleep(3)
            self.find_incidentes() # Find "incidentes" int the lawsuits
            
            # When there incidentes in the lawsuit it is necessary to download
            # reports related with all of them
            if len(self.__incidentes_links):
                for incidente_link in self.__incidentes_links:
                    print('incidente:', incidente_link)
                    self.start_download(link=incidente_link, 
                                        replace_file=False, 
                                        download_dir=download_dir)
            else:
                # Other wise is download just the reports related with the main
                # lawsuit
                self.start_download(replace_file=False, 
                                    download_dir=download_dir)
            
    def quit(self):
        """
        Method to finishe de crawler closing the webdriver.
        """
        self.__driver.quit()