import sys
sys.path.append('..')

import streamlit as st
from controller.connection import DBConnectionHandler
from controller.connection_repository import CollectionRepository

db_handle = DBConnectionHandler()
db_handle.connect_to_db()
db_connection = db_handle.get_db_connection()
my_collection_repository = CollectionRepository(db_connection)

# função para a página de consultar dados
def select():

    st.title('Consultar Dados')
    
    field = st.radio('Campo', ['Número processo', 'Processo principal',
                                'Devedor', 'Natureza', 'nome',
                                'cpf/cnpj/rne'])
    order = st.text_input('Informe o ' + field)
    

    if order:
        
        if field in ['nome','cpf/cnpj/rne']:
            order = {f"credores.{field}": order}
        else:
            order = {field: order}
        
        query = my_collection_repository.select_many(order)
        st.write(query)

