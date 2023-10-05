import re
from pdfminer.high_level import extract_text
from glob import glob


class PdfExtractor():
    def __init__(self) -> None:
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
       
        self.__fields = { }
    
    
    def get_text(self):
        return self.__text
    
    
    def get_fields(self):
        return self.__fields
    
    
    def extract_from_pdf(self, file_path):
        try:
            self.__text = extract_text(file_path)
            while '  ' in self.__text:
                self.__text = self.__text.replace('  ', ' ')
        except Exception as e:
            print(e)
    
    
    def find_patterns(self):       
        for field in self.__patterns:
            
            if field == 'credores':
                continue
            
            pattern = self.__patterns[field][0]
            
            if field == 'OAB advogado(s)':
                pattern = self.__patterns[field][0].format(self.__fields['Advogado'])
            
            try:
                answer = re.findall(pattern, self.__text)[0]
                answer = answer[self.__patterns[field][1][0]:self.__patterns[field][1][1]]
   
                if self.__patterns[field][2] == int:
                    answer = int(answer)
                elif self.__patterns[field][2] == float:
                    answer = float(answer.replace('.', '').replace(',', '.'))
               
                self.__fields[field] = answer
            
            except Exception as e:
                print(e)
        
        credores = []
        
        for i in range(int(self.__fields['numero credores'])):
            credor_i = {}
            start_credor_i = self.__text.find('Credor nº.: {}'.format(i+1))
            end_credor_i = self.__text.find('Credor nº.: {}'.format(i+2))
            text = self.__text[start_credor_i:end_credor_i]
            credores_fields = self.__patterns['credores']
            
            for field in credores_fields:
                try:
                    pattern = credores_fields[field][0]
                    answer = re.findall(pattern, text)[0]
                    answer = answer[credores_fields[field][1][0]:credores_fields[field][1][1]]
                    
                    if credores_fields[field][2] == float:
                        answer = float(answer.replace('.', '').replace(',', '.'))
                    
                    if field == 'cpf/cnpj':
                        field = 'cpf/cnpj/rne'
                    
                    credor_i[field] = answer
                    
                except Exception as e:
                    print(e)
                
            credores.append(credor_i)
        
        self.__fields['credores'] = credores
    
    def find_regex(self, regex):
        return re.findall(regex, self.__text)