import os
import traceback
from pprint import pprint
from typing import cast, List

import jirapt
import pandas as pd
from dotenv import load_dotenv
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
from .funcoes import data_formatada, handling_fields

load_dotenv()


class JiraHandling:
    def __init__(self, url: str, username: str, password: str, fields: str = None):
        self.__jql = ""
        self.__url = url
        self.__username = username
        self.__password = password
        self.__fields = fields
        self.__jira = JIRA(
            server=os.getenv("BASE_URL"), basic_auth=(self.__username, self.__password)
        )

    def __set_jql(self, escolha: str, dt_inicial: str = None, dt_final: str = None):
        """
        Método para definir uma variável de classe para ser utilizada pelo método search()

        :param escolha: - Escolher qual consulta realizar
        :param dt_inicial: - Data de ínicio da pesquisa.
        :param dt_final: Data final da pesquisa
        :return: Não retorna valor
        """
        match escolha:
            case "perkons-preventivas-pcls":
                self.__jql = f"""assignee in (currentUser()) AND project = CIES AND issuetype = "Preventiva PCL" AND 
                "Request Type" in ("PREVENTIVA PONTO DE COLETA (CIES)") AND status = Resolved AND resolved >= 
                {dt_inicial} AND resolved <= {dt_final}  ORDER BY cf[10139] ASC, cf[10116] DESC, 
                 created ASC, cf[10060] ASC, creator DESC, issuetype ASC, timespent DESC, cf[10061] DESC"""

            case "perkons-preventivas-salas":
                self.__jql = f"""assignee in (currentUser()) AND project = CIES AND issuetype = "Preventiva Salas"  
                AND "Request Type" in ("PREVENTIVAS SALA DE CONTROLE E OPERAÇÃO E PRODEST (CIES)") AND 
                status = Resolved AND resolved >= {dt_inicial} AND resolved <= {dt_final} ORDER 
                BY cf[10139] ASC, cf[10116] DESC, created ASC, cf[10060] ASC, creator DESC, issuetype ASC,
                timespent DESC, cf[10061] DESC"""

            case "perkons-corretivas-rmgv":
                self.__jql = f"""project = CIES AND issuetype IN standardIssueTypes() AND status = Resolved 
                AND assignee IN (qm:ba8a45d0-c8a8-4107-98fe-bfc59d6bde38:ba97e46a-d996-40bb-aeff-9e4d73cd3ce2,
                625768b25d1e700069aef70c, qm:ba8a45d0-c8a8-4107-98fe-bfc59d6bde38:70e33655-0037-42f7-94ef-d8503e158e39,
                currentUser()) AND type IN ("Prioridade 1", "Prioridade 2", "Prioridade 3") AND resolved >= 
                {dt_inicial} AND resolved <= {dt_final} AND "equipamentos[select list (cascading)]" IN 
                cascadeOption(10110) ORDER BY created ASC, cf[10060] ASC, creator DESC, issuetype ASC, 
                timespent DESC, cf[10061] DESC"""

            case "perkons-corretivas-fora-divisa":
                self.__jql = f"""project = CIES AND issuetype IN standardIssueTypes() AND status = Resolved AND 
                assignee IN (qm:ba8a45d0-c8a8-4107-98fe-bfc59d6bde38:ba97e46a-d996-40bb-aeff-9e4d73cd3ce2,
                625768b25d1e700069aef70c, qm:ba8a45d0-c8a8-4107-98fe-bfc59d6bde38:70e33655-0037-42f7-94ef-d8503e158e39, 
                currentUser()) AND type IN ("Prioridade 1", "Prioridade 2", "Prioridade 3") AND resolved >=
                {dt_inicial} AND resolved <= {dt_final} AND "equipamentos[select list (cascading)]" 
                IN cascadeOption(10113) ORDER BY created ASC, cf[10060] ASC, creator DESC, issuetype ASC, timespent 
                DESC, cf[10061] DESC"""

            case "velsis-preventivas-balancas":
                self.__jql = f"""created >= {dt_inicial} AND created <= {dt_final} AND project = CIES 
                AND issuetype = "Preventiva Balança" AND status = Resolved AND 
                reporter = 712020:3f4d8c9e-ec2e-4d7a-afaa-9655498b3d4b ORDER BY cf[10135] DESC, cf[10121] DESC, 
                cf[10130] ASC, cf[10124] DESC, created ASC, cf[10060] ASC, creator DESC, issuetype ASC, 
                timespent DESC, cf[10061] DESC"""

            case "perkons-preventivas-pcls-mes":
                self.__jql = """assignee in (currentUser()) AND project = CIES And created >= startOfMonth() 
                AND created <= now() AND "Request Type" IN ("PREVENTIVA PONTO DE COLETA (CIES)")"""

            case "verificacoes":
                self.__jql = f"""project = METRO AND issuetype = "Auto Verificação" AND resolution IN 
                (Concluido, Cancelado, Falhou, Reprovado, Aprovado, Unresolved) AND created >= "2022-12-31"
                AND created <= "2034-12-31" ORDER BY created DESC"""

    def __repr__(self):
        return f"{self.__jql, self.__url, self.__username, self.__jql}"

    def __search(self, fields):
        """
        :param fields: Lista de Campos para retorno do json
        :return: ResultList (Tipo personalizado da classe Jira)
        """
        issues = cast(
            ResultList[Issue],
            jirapt.search_issues(self.__jira, self.__jql, 4, fields=fields),
        )
        return issues

    def __getissues(self):
        try:
            issues = self.__search(self.__fields)
            dict_chamados = {}
            for issue in issues:
                dict_chamados[issue.key] = issue
            return dict_chamados
        except Exception as e:
            print(f"Erro ai camarada: {e.__str__()}")

    def getfields(self) -> list:
        fields = self.__jira.fields()
        return fields

    def getattachements(self, chave):
        issue = self.__jira
        attachment = issue.issue(chave, fields="attachment")
        return attachment

    def get_statistic_preventive(self):
        issues = self.getissues()
        list_preventive: list = []
        for issue in issues.values():
            list_preventive.append(
                {
                    "key": issue.key,
                    "status": issue.fields.customfield_10010.currentStatus.status,
                    "regiao": issue.fields.customfield_10060.value,
                }
            )

        if list_preventive:
            df = pd.DataFrame(list_preventive)

            dados_estatisticos: dict = {
                "ABERTOS_RMGV": len(
                    df.loc[
                        (df["regiao"] == "RMGV/Divisa")
                        & (df["status"] == "Work in progress")
                        ]
                ),
                "ABERTOS_FORA_DIVISA": len(
                    df.loc[
                        (df["regiao"] == "Fora Divisa")
                        & (df["status"] == "Work in progress")
                        ]
                ),
                "FECHADOS_RMGV": len(
                    df.loc[
                        (df["regiao"] == "RMGV/Divisa") & (df["status"] == "Resolvido")
                        ]
                ),
                "FECHADOS_FORA_DIVISA": len(
                    df.loc[
                        (df["regiao"] == "Fora Divisa") & (df["status"] == "Resolvido")
                        ]
                ),
                "CHAMADOS_ABERTOS": len(df.loc[df["status"] == "Work in progress"]),
                "TOTAL_DE_CHAMADOS": len(df["status"]),
            }

            return dados_estatisticos
        else:
            return None

    def get_statistic_corrective(self):
        issues = self.getissues()
        list_corrective: list = []
        for corrective in issues.values():
            list_corrective.append(
                {
                    "chave": corrective.key,
                    "prioridade": corrective.fields.priority,
                    "atendimento": corrective.fields.customfield_10062.completedCycles[
                        0
                    ].breached,
                    "solucao": corrective.fields.customfield_10063.completedCycles[
                        0
                    ].breached,
                }
            )

        if list_corrective:
            df = pd.DataFrame(list_corrective)
            df["prioridade"] = df["prioridade"].astype(str)

            dados_estatisticos: dict = {
                "solucao_no_prazo_p1": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 1") & (df["solucao"] == False)
                        ]
                ),
                "solucao_fora_prazo_p1": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 1") & (df["solucao"] == True)
                        ]
                ),
                "solucao_no_prazo_p2": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 2") & (df["solucao"] == False)
                        ]
                ),
                "solucao_fora_prazo_p2": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 2") & (df["solucao"] == True)
                        ]
                ),
                "solucao_no_prazo_p3": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 3") & (df["solucao"] == False)
                        ]
                ),
                "solucao_fora_prazo_p3": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 3") & (df["solucao"] == True)
                        ]
                ),
                "atendimento_no_prazo_p1": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 1")
                        & (df["atendimento"] == False)
                        ]
                ),
                "atendimento_fora_prazo_p1": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 1")
                        & (df["atendimento"] == True)
                        ]
                ),
                "atendimento_no_prazo_p2": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 2")
                        & (df["atendimento"] == False)
                        ]
                ),
                "atendimento_fora_prazo_p2": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 2")
                        & (df["atendimento"] == True)
                        ]
                ),
                "atendimento_no_prazo_p3": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 3")
                        & (df["atendimento"] == False)
                        ]
                ),
                "atendimento_fora_prazo_p3": len(
                    df.loc[
                        (df["prioridade"] == "Prioridade 3")
                        & (df["atendimento"] == True)
                        ]
                ),
            }
            return dados_estatisticos
        else:
            return None

    def prepare_list(self):
        lista_chamados: List = []
        self.__set_jql('verificacoes')
        issues = self.__getissues()
        for k,v in issues.items():
            try:
                lista_chamados.append({
                    "CHAVE": handling_fields("issuekey", v.raw),
                    "TIPO_x0020_DE_x0020_ITEM": v.fields.issuetype.name,
                    "REQUEST_x0020_TYPE": v.fields.customfield_10010.requestType.name,
                    "RESUMO": handling_fields("summary", v.raw),
                    "STATUS": handling_fields("status", v.raw),
                    "RESOLUCAO": handling_fields("resolution", v.raw),
                    "ATUALIZADO": data_formatada(handling_fields("updated", v.raw)),
                    "CRIADO_x0020_EM": data_formatada(handling_fields("created", v.raw)),
                    "RELATOR": handling_fields("reporter", v.raw),
                    "RESOLVIDO_x0020_EM": data_formatada(handling_fields("resolutiondate", v.raw)),
                    "UTILIZAR_x0020_CENTRO_x0020_DE_x": handling_fields("customfield_10122", v.raw),
                    "QUANTIDADE_x0020_DE_x0020_FAIXAS": handling_fields("customfield_10160", v.raw),
                    "SERIE_x0020_DO_x0020_EQUIPAMENTO": handling_fields("customfield_10134", v.raw),
                    "TIPO_x0020_DE_x0020_EQUIPAMENTO": handling_fields("customfield_10334", v.raw).replace("-",
                                                                                                                 ""),
                    "CATEGORIA_x0020_DO_x0020_EQUIPAM": handling_fields("customfield_10703", v.raw).replace("-",
                                                                                                                  ""),
                    "DATA_x0020_DA_x0020_AFERICAO": data_formatada(handling_fields("customfield_10336", v.raw)),
                    "RESPONSAVEL_x0020_DA_x0020_AFERI": handling_fields("customfield_10447", v.raw).replace("-",
                                                                                                                  ""),
                })
            except AttributeError as e:
                print(f"Erro ao processar chamado {v.raw.get('key')}: {type(e).__name__} : - {e}")
                traceback.print_exc()
            except TypeError as e:
                print(f"Erro ao processar chamado {v.raw.get('key')}: {type(e).__name__} : - {e}")
        return lista_chamados


if __name__ == "__main__":
    pass