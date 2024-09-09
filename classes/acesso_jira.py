from __future__ import annotations

import traceback
from typing import cast, List

import jirapt
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue

import config
from classes.funcoes import handling_fields, data_formatada


class AcessoJira:
    def __init__(self):
        pass

    @staticmethod
    def pesquisar(jql):
        """
        Retorna a lista de dicionários com chamados do jira
        :param jql:
        :return: lista_chamados
        """
        jira = JIRA(basic_auth=(config.USER_JIRA, config.API_TOKEN),
                    server=config.SERVIDOR)

        myself = jira.myself()

        issues = cast(ResultList[Issue], jirapt.search_issues(jira, jql, 2))

        lista_chamados: List = []

        for chamado in issues:
            try:
                lista_chamados.append({
                    "CHAVE": handling_fields("issuekey", chamado.raw),
                    "TIPO_x0020_DE_x0020_ITEM": chamado.raw.get("fields").get("issuetype").get("name"),
                    "REQUEST_x0020_TYPE": chamado.raw.get("fields").get("customfield_10010").get("requestType").
                    get("name", "vazio"),
                    "RESUMO": handling_fields("summary", chamado.raw),
                    "STATUS": handling_fields("status", chamado.raw),
                    "RESOLUCAO": handling_fields("resolution", chamado.raw),
                    "ATUALIZADO": data_formatada(handling_fields("updated", chamado.raw)),
                    "CRIADO_x0020_EM": data_formatada(handling_fields("created", chamado.raw)),
                    "RELATOR": handling_fields("reporter", chamado.raw),
                    "RESOLVIDO_x0020_EM": data_formatada(handling_fields("resolutiondate", chamado.raw)),
                    "UTILIZAR_x0020_CENTRO_x0020_DE_x": handling_fields("customfield_10122", chamado.raw),
                    "QUANTIDADE_x0020_DE_x0020_FAIXAS": handling_fields("customfield_10160", chamado.raw),
                    "SERIE_x0020_DO_x0020_EQUIPAMENTO": handling_fields("customfield_10134", chamado.raw),
                    "TIPO_x0020_DE_x0020_EQUIPAMENTO": handling_fields("customfield_10334", chamado.raw).replace("-", ""),
                    "CATEGORIA_x0020_DO_x0020_EQUIPAM": handling_fields("customfield_10703", chamado.raw).replace("-", ""),
                    "DATA_x0020_DA_x0020_AFERICAO": data_formatada(handling_fields("customfield_10336", chamado.raw)),
                    "RESPONSAVEL_x0020_DA_x0020_AFERI": handling_fields("customfield_10447", chamado.raw).replace("-", ""),
                })
            except AttributeError as e:
                print(f"Erro ao processar chamado {chamado.raw.get('key')}: {type(e).__name__} : - {e}")
                traceback.print_exc()
            except TypeError as e:
                print(f"Erro ao processar chamado {chamado.raw.get('key')}: {type(e).__name__} : - {e}")
        return lista_chamados
