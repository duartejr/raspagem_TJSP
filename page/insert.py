import sys
sys.path.append('..')

import streamlit as st
from services.pdf_extractor import PdfExtractor
from controller.connection import DBConnectionHandler
from controller.connection_repository import CollectionRepository

db_handle = DBConnectionHandler()
db_handle.connect_to_db()
db_connection = db_handle.get_db_connection()
my_collection_repository = CollectionRepository(db_connection)

pdf_extractor = PdfExtractor()

def insert():
    st.title('Inserção e atualização de dados')
    filepaths = st.file_uploader('Escolha arquivos', 
                                 accept_multiple_files=True)
        
    if filepaths and st.button("Iniciar"):
        for filepath in filepaths:
            st.write(filepath)
            pdf_extractor.extract_from_pdf(filepath)
            pdf_extractor.find_patterns()
            text = pdf_extractor.get_fields()
            
            st.write(text)
            my_collection_repository.insert_document(text)

            print(db_handle)
            st.write('Dados inseridos com sucesso.')
            filepath = None
        
