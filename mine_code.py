import pandas as pd
import json
from dicionario import dicionario
from pandas import read_excel
from datetime import datetime as dt
import os

dic = dicionario()
#Carregando o arquivo
path = os.getcwd() + "\TCC\dados\pedidos.xlsx"
path2 = os.getcwd() + "\TCC\dados\clientes.xlsx"

# Dados: Todos os pedidos
planilhaPedidos = pd.read_excel(open(path, mode="rb"), engine="openpyxl")
planilhaClientes = pd.read_excel(open(path2, mode="rb"), engine="openpyxl")

def calculaIdade(dataNascimento):
    dataNascimento = dataNascimento.replace('/','-')
    dataNascimento = dt.strptime(dataNascimento, "%Y-%m-%d")
    agora          = dt.today()
    idade = agora - dataNascimento
    return (idade.days // 365)

def entreDatas(dataInicio, dataVerificar, dataLimite = None, tempo = 'Dias'):
    '''
    Verifica se uma data está entre outras duas datas.
    OBS: Também são consideradas as datas de inicio e fim.
    Return: Boolean.
    '''
    dataVerificar = dataVerificar.replace('/', '-')
    dataInicio    = dataInicio.replace('/', '-')

    response = False
    if (dataLimite == None):
        if(tempo == 'Dias'):
            inicio    = dt.strptime(dataInicio,    "%Y-%m-%d")
            verificar = dt.strptime(dataVerificar, "%Y-%m-%d")
            response  = (inicio <= verificar)
        elif(tempo == 'Meses'):
            inicio    = dt.strptime(dataInicio,    "%Y-%m")
            verificar = dt.strptime(dataVerificar, "%Y-%m")
            response  = (inicio <= verificar)
        elif tempo == 'Anos':
            inicio    = dt.strptime(dataInicio,    "%Y")
            verificar = dt.strptime(dataVerificar, "%Y")
            response  = (inicio <= verificar)

    else:
        if tempo == 'Dias':
            dataLimite = dataLimite.replace('/', '-')
            inicio     = dt.strptime(dataInicio,    "%Y-%m-%d")
            verificar  = dt.strptime(dataVerificar, "%Y-%m-%d")
            limite     = dt.strptime(dataLimite,    "%Y-%m-%d")
            response   = (inicio <= verificar) and (verificar <= limite)
        elif tempo == 'Meses':
            dataLimite = dataLimite.replace('/', '-')
            inicio     = dt.strptime(dataInicio,    "%Y-%m")
            verificar  = dt.strptime(dataVerificar, "%Y-%m")
            limite     = dt.strptime(dataLimite,    "%Y-%m")
            response   = (inicio <= verificar) and (verificar <= limite)
        elif tempo == 'Anos':
            inicio     = dt.strptime(dataInicio,    "%Y")
            verificar  = dt.strptime(dataVerificar, "%Y")
            limite     = dt.strptime(dataLimite,    "%Y")
            response   = (inicio <= verificar) and (verificar <= limite)
            
    return response

def seriesTo_json(dados):
    result = dados.to_json(orient="columns", force_ascii = False)
    parsed = json.loads(result)
    #parsed = json.dump(parsed)
    return parsed

'''
Converte um dicionário para json, usar quando o dic estiver ainda vazio
'''
def dictTo_json(dicionario):
    response = json.dumps(dicionario, sort_keys=False, indent=4)
    response = json.loads(response)
    print("Tipo:", type(response))
    return response

def jsonPrint(json):
    print("{")
    for dado in json.keys():
        print("    \"" + str(dado) + "\"" + ":", json[dado])
    print("}")

'''
RF__01 Quantidade de pedidos por estado   OK
ADICIONAR Somente já entregues            OK
'''
def pedidosPorEstado(dados, somenteEntregues = False):
    if somenteEntregues:
        dados = dados.loc[dados[dic.status] == dic.entregue]
    dados = dados[dic.estadoDest].value_counts()
    return seriesTo_json(dados)

'''
RF__02 Quantidade de pedidos por cidade   OK
ADICIONAR Somente já entregues            OK
'''
def pedidosPorCidade(dados, somenteEntregues = False):
    if somenteEntregues:
        dados = dados.loc[dados[dic.status] == dic.entregue]
    dados = dados[dic.cidadeDest].value_counts()
    return seriesTo_json(dados)

''' 
RF_03 Reincidencia de compra
'clientes' = False: Retorna a % de clientes que compraram mais de 1 vez.    OK
'clientes' = True : Retorna o json de clientes que compraram mais de 1 vez. OK
Exemplo json: {"nome" : QtdCompras}
'''
def taxaReincidencia(dados, clientes = False):
    
    resultado = dados[dic.clienteID].value_counts()
    novosClientes = {}
    reincidentes  = {}
    #reincidentes = dictTo_json(reincidentes)
    for id in resultado.keys():
        indexNome  = dados.loc[dados[dic.clienteID] == int(id)].index
        nome       = dados[dic.nomeDest][indexNome[0]]
        qtdPedidos = resultado[id] 
        #print("nome:", nome, "Fim")
        if qtdPedidos > 1:
            reincidentes[nome]  = int(qtdPedidos)
        elif qtdPedidos == 1:
            novosClientes[nome] = int(qtdPedidos)

    if (clientes):
        response = reincidentes
    else:
        response = {
            "reincidentes": len(reincidentes),
            "novos clientes": len(novosClientes) 
        }
    return (response)


'''
RF_04 Gênero predominante
Quantidade de clientes que fizeram um pedido
ADICIONAR: Somente pedidos já entregues
'''
def genPred(planilhaClientes, planilhaPedidos, apenasCadastrados=False, somenteEntregues = False):
    # planilha_pedidos = planilhaPedidos
    # if somenteEntregues:
    #     d = planilhaPedidos.loc[planilhaPedidos[dic.status] == dic.entregue]

    publicoMasculino = {'total':0}
    publicoFeminino  = {'total':0}

    #Contagem de clientes cadastrados Masculinos e Femininos.
    for cliente in range(len(planilhaClientes)):
        if planilhaClientes[dic.genero][cliente] == 'M':
            chave = planilhaClientes[dic.Id][cliente]
            publicoMasculino[chave]   = 'M'
            publicoMasculino['total'] += 1

        elif planilhaClientes[dic.genero][cliente] == 'F':
            chave = planilhaClientes[dic.Id][cliente]
            publicoFeminino[chave]   = 'F'
            publicoFeminino['total'] += 1


    if apenasCadastrados:
        return {'M':publicoMasculino['total'], 'F':publicoFeminino['total']}
    
    #Contagem por gênero de clientes que realizaram pedido.
    M_Total = 0
    F_Total = 0
    for pedido in range(len(planilhaPedidos)):
        status = planilhaPedidos[dic.status][pedido]
        if somenteEntregues == True and status != dic.entregue:
            pass
        else:
            id = planilhaPedidos[dic.clienteID][pedido]
            if id in publicoMasculino.keys():
                M_Total += 1
            elif id in publicoFeminino.keys():
                F_Total += 1
    
    return {'F':F_Total, 'M':M_Total}


'''
RF_05 Faixa Etária OK
'''
def faixa_etaria(planilhaClientes, passo=5):
    index    = []     #[0, 0, 0, 1, 1, 1, 2, 2, 2]
    chaves   = []     #['0-2', '3-5', '6-8']
    response = {}
    count = 0
    for i in range(0, 121, passo):
        for j in range(passo):
            index.append(count)
        count += 1
        chave = str(i)
        if passo > 1:
            chave +=  '-' + str(i + passo-1)
        chaves.append(chave)
    
    for cliente in range(len(planilhaClientes)):
        dataNascimento = planilhaClientes[dic.dataNasc][cliente]
        idade = calculaIdade(dataNascimento)
        #print(idade)
        if idade < 122:
            pos = index[idade]
            chave = chaves[pos]
            if (chave in response) == False:
                response[chave] = 0
            response[chave] += 1
    return response

'''
RF_06 Períodos com mais cadastros em MESES
Geral               OK
Período definido    OK
Meses e Anos        OK
'''
def cadastrosPeriodo(planilhaClientes, dataInicial=None, dataFinal=None, tempo = "Meses"):
    response = {}
    for cliente in range(len(planilhaClientes)):
        dataCriacao = planilhaClientes[dic.clientCriac][cliente].split()[0]

        if tempo == "Meses":
            dataCriacao = dataCriacao[:7]
        elif tempo == "Anos":
            dataCriacao = dataCriacao[:4]
        
        if (dataInicial != None):
            if entreDatas(dataInicial, dataCriacao, dataFinal, tempo):
                if (dataCriacao in response) == False:
                    response[dataCriacao] = 0
                response[dataCriacao] += 1
        else:
            if (dataCriacao in response) == False:
                response[dataCriacao] = 0
            response[dataCriacao] += 1
    return response


'''
RF_07 Faturamento por período
Por ano     OK
Por mês     OK
Por dias    OK
Truncar     FAZER
'''
def faturamentoPeriodo(planilhaPedidos, tempo='Dias', dataInicial=None, dataFinal=None):
    response = {}
    for pedido in range(len(planilhaPedidos)):
        status = planilhaPedidos[dic.status][pedido]
        if status == dic.entregue or status == "Pedido Enviado":
            data = planilhaPedidos[dic.dataCriacao][pedido].split(' ')[0] #YYYY-MM-DD
            
            chave = ''
            if (tempo == 'Dias'):
                chave = data
            elif tempo == 'Meses':
                chave = data[:7]    # YYYY-MM
            elif tempo == 'Anos':
                chave = data[:4]
            #print(chave)
            valorPedido = float(planilhaPedidos[dic.valorTotal][pedido])
            if(dataInicial != None):
                if entreDatas(dataInicial, chave, dataFinal, tempo):
                    if (chave in response.keys()) == False:
                        response[chave] = 0
                    response[chave] += valorPedido
            else: 
                if (chave in response.keys()) == False:
                    response[chave] = 0
                response[chave] += valorPedido

    return response

'''
RF_08 Cancelamento por período
'''
def cancelamentosPeriodo(planilhaPedidos, dataInicial=None, dataFinal=None, tempo = "Meses"):
    response = {}
    for pedido in range(len(planilhaPedidos)):
        dataCriacao = planilhaPedidos[dic.dataCriacao][pedido].split()[0]
    
        if tempo == "Meses":
            dataCriacao = dataCriacao[:7]
        elif tempo == "Anos":
            dataCriacao = dataCriacao[:4]

        status = planilhaPedidos[dic.status][pedido]
        if status == dic.cancelado:
            if (dataInicial != None):
                if entreDatas(dataInicial, dataCriacao, dataFinal, tempo):
                    if (dataCriacao in response) == False:
                        response[dataCriacao] = 0
                    response[dataCriacao] += 1
            else:
                if (dataCriacao in response) == False:
                    response[dataCriacao] = 0
                response[dataCriacao] += 1
    return response


'''
RF_09 
'''

'''
RF__10 Taxa de cancelamento por método de pagamento
RF__11 Preferência por método de pegamento
'''
def metPagAprovacoes(dados):
    meiosPagamento = set(dados[dic.tipoPag].values)
    print(meiosPagamento)


    infoPagamentos = {}
    for tipo in meiosPagamento:
        qtdUsos      = len(dados.loc[dados[dic.tipoPag] == tipo])
        qtdAprovados = len(dados.loc[(dados[dic.tipoPag] == tipo) & (dados[dic.status] == dic.entregue)])
        infoPagamentos[tipo] = [qtdUsos, qtdAprovados]

    print(infoPagamentos)

'''
RF_12 Preferencia pelos meios de envio
Total   
Melhoria: Por período FAZER
'''
def metEnvioPref(planilhaPedidos):
    response = {}
    for pedido in range(len(planilhaPedidos)):
        if planilhaPedidos[dic.status][pedido] == dic.entregue:
            metodoEnvio = planilhaPedidos[dic.metEnvio][pedido]
            if (metodoEnvio in response.keys()) == False:
                response[metodoEnvio] = 0
            response[metodoEnvio] += 1
    return response

# print(pedidosPorEstado(dados))
#jsonPrint(pedidosPorCidade(dados))
print((taxaReincidencia(planilhaPedidos, True)))
#print(len(aprovados))
#print(taxaReincidencia(dados, clientes=True))
#print(json.dumps(taxaReincidencia(dados), ident=4))
# for i in pedidosPorCidade(dados).keys():
#     print(i.encode())
# jsonPrint(faturamentoPeriodo(planilhaPedidos, "Dias", "2021-01-01"))
# metPagAprovacoes(dados)

#jsonPrint(pedidosPorCidade(planilhaPedidos, False))
# jsonPrint(genPredCad(planilhaClientes))
# jsonPrint(genPredPed(planilhaClientes, planilhaPedidos, False, True))
# print(entreDatas("2017", "2018", "2019", 'Anos'))

# jsonPrint(faixa_etaria(planilhaClientes, 3))
# calculaIdade("1994/03/23")

# jsonPrint( metEnvioPref(planilhaPedidos))

# jsonPrint(cadastrosPeriodo(planilhaClientes, "2020-05", "2021-03", tempo="Meses"))
# jsonPrint(cancelamentosPeriodo(planilhaPedidos))
# jsonPrint(taxaReincidencia(planilhaPedidos))