from typing import List

from classes.acesso_jira import AcessoJira
from classes.acesso_sharepoint import SharepointHandler
from classes.emailsender import Emailer
from classes.funcoes import verifica_diferenca, retorna_chamados_diferentes
from config import *

mensagem = ""

# Pegando Lista de Chamados do Jira
chamados_jira: List = AcessoJira.pesquisar(JQL)

# Pegando Lista do Sharepoint
lista_sharepoint = SharepointHandler("Aferições iniciais realizadas")
chamados_sharepoint = lista_sharepoint.get_list_dict()

diferenca_chamados_jira = retorna_chamados_diferentes(
    chamados_jira, chamados_sharepoint
)
diferenca_chamados_sp = retorna_chamados_diferentes(
    chamados_sharepoint, chamados_jira
)

if diferenca_chamados_jira:
    lista_sharepoint.add_item_list(diferenca_chamados_jira)
    mensagem = f"Adicionado {len(diferenca_chamados_jira)} chamados a lista do Sharepoint!\n"
else:
    mensagem += f"Sem chamados para adicionar na lista do Sharepoint! \n"
    print("Sem chamados para adicionar na lista!")

if diferenca_chamados_sp:
    lista_sharepoint.remove_item_list([""])
    mensagem += f"Foram removidos {len(diferenca_chamados_sp)} chamados da lista do Sharepoint! \n"
else:
    mensagem += f"Sem chamados para excluir na lista do Sharepoint! \n"
    print("Sem chamados para excluir!")

chamados_sharepoint = lista_sharepoint.get_list_dict()
if chamados_sharepoint:
    chamados_desatualizados = verifica_diferenca(chamados_sharepoint, chamados_jira)
    mensagem += f" {len(chamados_desatualizados)} foram atualizados na lista do Sharepoint! \n"
    lista_sharepoint.update_item_list(chamados_desatualizados)
else:
    mensagem += f"Não há mudanças na lista do Sharepoint!\n"
    print("Sem chamados para atualizar a lista!")


def enviar_email_robo(mensagem) -> None:
    email = Emailer("andre@andrealves.eng.br", "andre-28")
    email.definir_conteudo(
        topico="Robô Metrologia",
        email_remetente="andre@andrealves.eng.br",
        lista_contatos=[
            "carolina.s@perkons.com"
            "a.alves@perkons.com"
        ],
        conteudo_email=mensagem,
    )
    email.enviar_email(5)
