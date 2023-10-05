import sys
sys.path.append('..')

import streamlit as st
from controller.connection import DBConnectionHandler
from controller.connection_repository import CollectionRepository

db_handle = DBConnectionHandler()
db_handle.connect_to_db()
db_connection = db_handle.get_db_connection()
my_collection_repository = CollectionRepository(db_connection)


def delete():
    st.title('Remoção de dados')
    st.write('Escolha um campo para procurar o(s) processo(s) que deseja excluir:')
    
    field = st.radio('Campo', ['Número processo', 
                               'Processo principal',
                                'Devedor', 
                                'Natureza', 
                                'nome',
                                'cpf/cnpj/rne'])
    
    order = st.text_input('Informe o ' + field)
    
    if order:
        
        if field in ['nome','cpf/cnpj/rne']:
            order = {f"credores.{field}": order}
        else:
            order = {field: order}
        
        documents = my_collection_repository.select_many(order)
        
        st.write('Lista de processos encontrados:')
        st.write(documents)
        
        if len(documents) and st.button('Confirma remoção?'):
            my_collection_repository.delete_documents(documents)
            
            st.write('Processo(s) removido')
            
        
