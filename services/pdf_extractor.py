import re
from typing import Dict, List
from pdfminer.high_level import extract_text


class PdfExtractor():
    def __init__(self) -> None:
        """
        Initialize the PDf extractor. This class is responsible to extract the
        information from the lawsuit reports. The default fields that are extracted are:
        - Lawsuit number [Número processo]
        - Main lawsuit number [Processo principal]
        - Debtor [Devedor]
        - Nature [Natureza]
        - Global value [Valor global]
        - Number of creditors [numero credores]
        - Name of creditors [nome]
        - CPF/CNPJ/RNE of creditors [cpf/cnpj/rne]
        - Creditors date of birth [data nascimento]
        - Creditors requested values [valor requisitado]
        """
        
        # These patterns are used to find the fields into the PDF documents.
        # Each key is formed by [regex, limits, type] which are:
        # regex - Regex pattern fo find the field into the PDf document.
        # limits - Defines where in the regex answer are the fields values.
        # type - Informs the datatype of the fields.
        self.__patterns = {
            'Número processo': ['Processo nº: .{0,}\n', [13, -1], str],
            'Processo principal': ['Processo Principal/Conhecimento: .{0,}\n', [33,-1], str],
            'Devedor': ['Devedor: .{0,}\n', [9, -1], str],
            'Natureza': ['Natureza: .{0,}\n', [10, -1], str],
            'Valor global': ['Valor global da requisição: .{0,} \(', [31, -3], float],
            'numero credores': ['Quantidade de credores: .{0,}\n', [24, -1], int],
            'credores': {
                'nome': ['Nome: .{0,}\n', [6,-1], str],
                'cpf/cnpj/rne': ['CPF/CNPJ/RNE: .{0,}\n', [15, -1], str],
                'cpf/cnpj': ['CPF/CNPJ: .{0,}\n', [10, -1], str],
                'data nascimento': ['Data do nascimento: .{0,}\n', [20, -1], str],
                'valor requisitado': ['Valor requisitado: .{0,} \(', [22, -2], float]
            }
        }
        
        # Into the dictionary are stored the field values founded in the PDF
        self.__fields = { }
    
    
    def get_text(self) -> List[str]:
        """
        Method to obtain the text readed in the PDF document.

        Returns:
            List[str]: Text readed from the PDF
        """
        return self.__text
    
    
    def get_fields(self) -> Dict:
        """
        Method to get the fields founded into the PDF document.

        Returns:
            Dict: Dictionary with the field values
        """
        return self.__fields
    
    
    def extract_from_pdf(self, file_path: str):
        """
        Method to extract the text from PDF document

        Args:
            file_path (str): Path of the PDF document.
        """
        try:
            # Read the text into the PDF
            self.__text = extract_text(file_path)
            
            # Removes all the extra blank spaces in the text extracte before
            while '  ' in self.__text:
                self.__text = self.__text.replace('  ', ' ')
                
        except Exception as e:
            # Raise a error when the files is not available.
            print(e)
    
    
    def find_patterns(self):
        """
        Method to find the fields into the text extracted from the PDF.
        """
        
        for field in self.__patterns:
            
            # When the field is "credores" it is necessary anothe aproach.
            if field == 'credores':
                continue
            
            # Selects the pattern to search in the text
            pattern = self.__patterns[field][0]
            
            # Exists an option to specify new field patterns to search this is one of them.
            if field == 'OAB advogado(s)':
                pattern = self.__patterns[field][0].format(self.__fields['Advogado'])
            
            try:
                # Gets the text with the pattern
                answer = re.findall(pattern, self.__text)[0]
                # Remove extra information and keeps just the field values
                answer = answer[self.__patterns[field][1][0]:self.__patterns[field][1][1]]
   
                # Convert the field values to the correct datatype
                if self.__patterns[field][2] == int:
                    answer = int(answer)
                elif self.__patterns[field][2] == float:
                    answer = float(answer.replace('.', '').replace(',', '.'))
                
                # Saves the answer into the fields dictionary
                self.__fields[field] = answer
            
            except Exception as e:
                print(e)
        
        # It is excecuted the extraction of the creditors data
        credores = []
        
        # Loop along the creditors fields
        for i in range(int(self.__fields['numero credores'])):
            # Storage the information about a specific creditor
            credor_i = {} 
            # Find the first position of the text about the creditor i
            start_credor_i = self.__text.find('Credor nº.: {}'.format(i+1))
            # Find the last position of the text about the creditor i
            end_credor_i = self.__text.find('Credor nº.: {}'.format(i+2))
            # Selects just the text about the creditor i
            text = self.__text[start_credor_i:end_credor_i]
            # Field patterns about the creditors
            credores_fields = self.__patterns['credores']
            
            # Loop along the fields of creditors
            for field in credores_fields:
                try:
                    # Selects the pattern to search
                    pattern = credores_fields[field][0]
                    # Gets the text with the pattern
                    answer = re.findall(pattern, text)[0]
                    # Remove extra information and keeps just the field values
                    answer = answer[credores_fields[field][1][0]:credores_fields[field][1][1]]
                    
                    # Convert the field values to the correct datatype
                    if credores_fields[field][2] == float:
                        answer = float(answer.replace('.', '').replace(',', '.'))
                    
                    # Standardize the cpf/cnpj/rne field. In some documents this
                    # field is named cpf/cnpj and in others is cpf/cnpj/rne
                    if field == 'cpf/cnpj':
                        field = 'cpf/cnpj/rne'
                    
                    # Saves the answer into the credor_i dictionary
                    credor_i[field] = answer
                    
                except Exception as e:
                    print(e)
            
            # Adds the credor_i into the list of creditors
            credores.append(credor_i)
        
        # Saves the answer into the fields dictionary
        self.__fields['credores'] = credores
    
    
    def find_regex(self, regex: str) -> List[str]:
        """
        Method to find a regex into the text extracted from the PDF document.

        Args:
            regex (str): Regex with the pattern to search.

        Returns:
            List[str]: List with all the text fractions where the regex pattern was founded.
        """
        return re.findall(regex, self.__text)
