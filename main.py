import os
from typing import List, Any

from classes.jira_handling import JiraHandling
from classes.acesso_sharepoint import SharepointHandler
from classes.emailsender import Emailer
from classes.funcoes import verifica_diferenca, retorna_chamados_diferentes
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='app.log', format='%(asctime)s - %(levelname)s: %(message)s', encoding='utf-8',
                    level=logging.INFO)


load_dotenv()

# Pegando Lista de Chamados do Jira
instancia_jira = JiraHandling(os.getenv("URL"), os.getenv("USER_JIRA"),
                        os.getenv("API_TOKEN"),
                        os.getenv("CAMPOS_VERIFICACOES"))

chamados_jira: List[dict[str:Any]] = instancia_jira.prepare_list()

# Pegando Lista do Sharepoint
lista_sharepoint = SharepointHandler("Verificações iniciais realizadas")
chamados_sharepoint = lista_sharepoint.get_list_dict()

diferenca_chamados_jira = retorna_chamados_diferentes(
    chamados_jira, chamados_sharepoint
)
diferenca_chamados_sp = retorna_chamados_diferentes(
    chamados_sharepoint, chamados_jira
)

if diferenca_chamados_jira:
    lista_sharepoint.add_item_list(diferenca_chamados_jira)
    mensagem = f"Adicionado {len(diferenca_chamados_jira)} chamados a lista do Sharepoint! - "
else:
    logger.info(f"Sem chamados para adicionar na lista do Sharepoint!")

if diferenca_chamados_sp:
    lista_sharepoint.remove_item_list([""])
    logger.info(f"Foram removidos {len(diferenca_chamados_sp)} chamados da lista do Sharepoint!")
else:
    logger.info(f"Sem chamados para excluir na lista do Sharepoint!")

chamados_sharepoint = lista_sharepoint.get_list_dict()
if chamados_sharepoint:
    chamados_desatualizados = verifica_diferenca(chamados_sharepoint, chamados_jira)
    print(len(chamados_desatualizados))
    logger.info(f" {len(chamados_desatualizados)} foram atualizados na lista do Sharepoint!")
    lista_sharepoint.update_item_list(chamados_desatualizados)
else:
    logger.info(f"Não há mudanças na lista do Sharepoint!")