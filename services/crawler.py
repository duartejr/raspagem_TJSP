from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from glob import glob

class CrawlerTJSP():
    def __init__(self, user, pswd, download_dir=None) -> None:
        self.__user = user
        self.__pswd = pswd
        
        if not download_dir:
            download_dir = os.path.expanduser('~')
        
        options = Options()
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)
        options.set_preference("browser.download.dir", download_dir)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/pdf")
        options.set_preference("pdfjs.disabled", True)
        self.__driver = webdriver.Firefox(options=options)
    
    
    def login(self):
        self.__driver.get("https://esaj.tjsp.jus.br/sajcas/login?service=https%3A%2F%2Fesaj.tjsp.jus.br%2Fesaj%2Fj_spring_cas_security_check")
        
        # find username/email field and send the username itself to the input field
        self.__driver.find_element("id", "usernameForm").send_keys(self.__user)
        # find password input field and insert password as well
        self.__driver.find_element("id", "passwordForm").send_keys(self.__pswd)
        # click login button
        self.__driver.find_element("name", "pbEntrar").click()
    
    
    def find_process(self, process):
        part1, part2 = process.split('.8.26')
        self.__driver.get("https://esaj.tjsp.jus.br/cpopg/open.do")
        self.__driver.find_element("name", "numeroDigitoAnoUnificado").send_keys(part1)
        self.__driver.find_element("name", "foroNumeroUnificado").send_keys(part2)
        time.sleep(5)
        self.__driver.find_element("id", "botaoConsultarProcessos").click()
    
    
    def find_incidentes(self):
        self.__incidentes_links = []
        try:
            incidentes = self.__driver.find_elements(By.CLASS_NAME, "incidente")
            self.__incidentes_links = []
            for incidente in incidentes:
                self.__incidentes_links.append(incidente.get_attribute("href"))
            
        except Exception as e:
            print(e)
    
    
    def start_download(self, link=None, replace_file=False, download_dir=None):
        
        if link:
            self.__driver.get(link)
        
        if not download_dir:
            download_dir = os.path.expanduser('~')
        
        try:
            self.__driver.find_element("id", "linkPasta").click()
        except:
            return False
        
        time.sleep(3)
        element = self.__driver.find_element(By.CLASS_NAME, "unj-larger")
        
        lawsuit = element.get_attribute('innerText')
        lawsuit = ''.join(lawsuit.split('(')[1:]).replace(') ', '-').replace(')', '')
        
        if lawsuit[-1] == '-':
            lawsuit = lawsuit[:-1]

        lawsuit_file = f'{download_dir}/{lawsuit}.pdf'
        
        if os.path.isfile(lawsuit_file):
            if replace_file == False:
                self.__driver.close()
                window_after = self.__driver.window_handles[0]
                self.__driver.switch_to.window(window_after)
                return None
            else:
                os.remove(lawsuit_file)
         
        window_after = self.__driver.window_handles[1]
        self.__driver.switch_to.window(window_after)
        time.sleep(3)
        WebDriverWait(self.__driver, 1).until(EC.presence_of_element_located((By.ID, "selecionarButton"))).click()
        self.__driver.find_element("id", "selecionarButton").click()
        self.__driver.find_element("id", "salvarButton").click()
        WebDriverWait(self.__driver, 20).until(EC.presence_of_element_located((By.ID, "opcao1"))).click()
        self.__driver.find_element("id", "opcao1").click()
        self.__driver.find_element("id", "botaoContinuar").click()
        
        WebDriverWait(self.__driver, 5).until(EC.presence_of_element_located((By.ID, "imgSuccess")))

        while True:
            try:
                btnDownload = self.__driver.find_element("id", "btnAguardarProcessamento")
                btnDownloadAttrs = self.__driver.execute_script('var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;', btnDownload)
                time.sleep(1)
                if 'style' in list(btnDownloadAttrs.keys()):
                    break
            except:
                break
        
        self.__driver.find_element("id", "btnDownloadDocumento").click()

        while True:
            if not len(glob(f'{download_dir}/*.pdf.part')):
                break
        
        self.__driver.close()
        window_after = self.__driver.window_handles[0]
        self.__driver.switch_to.window(window_after)

        try:
            file_download = glob('-'.join(lawsuit_file.split('-')[:-1])+'.pdf')[0]
            os.rename(file_download, lawsuit_file)
        except:
            file_download = glob(lawsuit_file)[0]
            os.rename(file_download, lawsuit_file)
        
    
    def download_data(self, lawsuits, replace_file=False, download_dir=None):
        
        if not download_dir:
            download_dir = os.path.expanduser('~')
        
        for lawsuit in lawsuits:
            self.find_process(lawsuit)
            time.sleep(3)
            self.find_incidentes()
            
            if len(self.__incidentes_links):
                for incidente_link in self.__incidentes_links:
                    print('incidente:', incidente_link)
                    self.start_download(link=incidente_link, replace_file=False, download_dir=download_dir)
            else:
                self.start_download(replace_file=False, download_dir=download_dir)
    
            
    def quit(self):
        self.__driver.quit()