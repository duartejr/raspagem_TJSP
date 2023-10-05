import streamlit as st
import page.insert as insert
import page.select as select
import page.delete as delete
import page.scraping as scraping

# Criando a barra lateral do menu
st.sidebar.title('Menu')
page = st.sidebar.selectbox('Ações',['Raspagem', 'Inserir', 'Consultar', 'Deletar'])

# carregando as páginas de acordo com a seleção do menu
if page == "Raspagem":
    scraping.scraping()
if page == 'Consultar':
    select.select()
if page == 'Inserir':
    insert.insert()
if page == 'Deletar':
    delete.delete()