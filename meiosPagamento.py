import pandas
from dicionario import dicionario
from pandas import read_excel
import os

dic = dicionario()
#Carregando o arquivo
path = os.getcwd() + "\pedidos.xlsx"
dados = read_excel(path, sheet_name = "Sheet1")

#Identificando os tipos de pagamento
meiosPagamento = set(dados[dic.tipoPag].values)
print(meiosPagamento)

#infoPagamentos = {"TipoDePagamento": [QtdUsos, QtdAprovações]}
infoPagamentos = {}
for tipo in meiosPagamento:
    qtdUsos      = len(dados.loc[dados[dic.tipoPag] == tipo])
    qtdAprovados = len(dados.loc[(dados[dic.tipoPag] == tipo) & (dados[dic.status] == dic.entregue)])
    infoPagamentos[tipo] = [qtdUsos, qtdAprovados]

print(infoPagamentos)