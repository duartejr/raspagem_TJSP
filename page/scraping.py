import sys
sys.path.append('..')

import streamlit as st
from services.pdf_extractor import PdfExtractor
from controller.connection import DBConnectionHandler
from controller.connection_repository import CollectionRepository
from services.crawler import CrawlerTJSP

db_handle = DBConnectionHandler()
db_handle.connect_to_db()
db_connection = db_handle.get_db_connection()
my_collection_repository = CollectionRepository(db_connection)
import os

pdf_extractor = PdfExtractor()

def scraping():
    st.title('Raspagem de dados')

    user = st.text_input('Usuário TJSP')
    pswd = st.text_input('Senha TJSP', type='password')
    year = st.text_input('Ano do processo')
    lawsuits = []

    lawsuit_files = st.file_uploader('Escolha arquivo com a lista de processos')
    download_path = st.text_input('Informe o diretório onde deseja salvar os processos',
                                   value=os.path.expanduser('~'))

    if st.button('Checar diretório de destino'):
        if not os.path.isdir(download_path):
            st.error("O diretório não é válido. Informe um diretório existente")
            st.error("Por favor user o símbolo / para separar os diretórios ao invés de \\")
        else:
            st.write('Diretório de destino é válido.')

    if lawsuit_files and st.button("Iniciar raspagem"):
        pdf_extractor.extract_from_pdf(lawsuit_files)

        if year:
            lawsuit_regex = '[0-9]{7}-[0-9]{2}.' + year + '.[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}'
        else:
            lawsuit_regex = '[0-9]{7}-[0-9]{2}.[0-9]{4}.[0-9]{1,2}.[0-9]{1,2}.[0-9]{4}'

        lawsuits = pdf_extractor.find_regex(lawsuit_regex)
        lawsuits = list(dict.fromkeys(lawsuits))

        if year:
            complement = ' para o ano de {year}.'
        else:
            complement = '.'

        st.write(f'Foram encontrados {len(lawsuits)} processos{complement}')
        
        if len(lawsuits):
            
            st.write('Iniciando raspagem')
            crawler_tjsp = CrawlerTJSP(user, pswd, download_dir=download_path)
            crawler_tjsp.login()
            crawler_tjsp.download_data(lawsuits, download_dir=download_path)
            crawler_tjsp.quit()
            st.write('Raspagem finalizada')





