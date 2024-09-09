import re
from collections import defaultdict, OrderedDict
from datetime import datetime
from pprint import pprint
from typing import List


def retorna_chamados_diferentes(lista1, lista2) -> List:
    """
    Retorna a diferença entra as listas de dicionários
    :param lista1:
    :param lista2:
    :return: diferença entre as listas
    """
    diferenca: List = []
    for dicionario1 in lista1:
        existe = False
        for dicionario2 in lista2:
            if dicionario1['CHAVE'] == dicionario2['CHAVE']:
                existe = True
                break

        if not existe:
            diferenca.append(dicionario1)

    return diferenca


def verifica_diferenca(lista1, lista2) -> List:
    """
    Compara duas listas de dicionários e retorna uma lista com as diferenças.

    Args:
        lista1: Lista de dicionários (SharePoint).
        lista2: Lista de dicionários (Jira).

    Returns:
        Lista de dicionários atualizados com as diferenças.
    """

    # Cria um dicionário para agrupar os dicionários da lista2 por chave
    dicionario_jira = defaultdict(dict)
    for dicionario_in_lista2 in lista2:
        dicionario_jira[dicionario_in_lista2['CHAVE']] = OrderedDict(sorted(dicionario_in_lista2.items()))

    dicionario_sharepoint = defaultdict(dict)
    for dicionario_in_lista1 in lista1:
        dicionario_sharepoint['CHAVE'] = OrderedDict(sorted(dicionario_in_lista1.items()))

    # Atualiza os dicionários da lista1 com os valores da lista2
    diferencas = []
    for dicionario1 in lista1:
        chave = dicionario1['CHAVE']
        if chave in dicionario_jira:
            dicionario2 = dicionario_jira[chave]
            for campo, valor in dicionario2.items():
                if dicionario1.get(campo) != valor:
                    dicionario1[campo] = valor
                    diferencas.append(dicionario1)
                    break

    return diferencas


def verfica_lista(labels) -> List:
    if labels:
        lista_labels = ",".join(labels)
        return lista_labels
    else:
        return labels


def verfica_tipo_afericao(tipo_afericao) -> str:
    if tipo_afericao is None:
        return "Não Selecionado"
    else:
        return tipo_afericao[0].value


def handling_fields(value_field, issue) -> str:
    default_fields_mapping = {
        "assignee": "assignee.displayName",
        "reporter": "reporter.displayName",
        "resolution": "resolution.name",
        "resolutiondate": "resolutiondate",
        "status": "status.name",
        "summary": "summary"
    }

    if value_field == "issuekey":
        return issue['key']

    # Trata campos obrigatórios do JIRA
    if value_field in default_fields_mapping:
        field_path = default_fields_mapping[value_field]
        return get_nested_value(issue['fields'], field_path, "-")

    # Trata custom_fields desconhecidos
    if value_field in issue["fields"]:
        field_value = issue["fields"][value_field]
        if field_value is None:
            return "-"
        elif isinstance(field_value, str):
            return field_value
        elif isinstance(field_value, dict):
            child_value = field_value.get('child', {}).get('value', '-')
            return field_value.get('value', '-') + "-" + child_value
        elif isinstance(field_value, list):
            if field_value:
                if isinstance(field_value[0], dict):
                    return field_value[0].get("value", "-")
                else:
                    return ",".join(map(str, field_value))
            else:
                return "-"
        elif isinstance(field_value, float):
            return str(field_value)
        return "-"


def get_nested_value(dictionary, path, default=" "):
    keys = path.split('.')
    current = dictionary
    for key in keys:
        if current is None:
            return default
        if key in current:
            current = current[key]
        else:
            return default
    return current


def data_formatada(data) -> str:
    if data is None:
        return "00/00/00"
    if len(data) == 10:
        return re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1", data)
    return datetime.fromisoformat(data[0:10]).strftime("%d/%m/%y")
