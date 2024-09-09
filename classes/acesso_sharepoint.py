import time
from typing import List

import requests.exceptions
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

from config import *

ctx_auth = UserCredential(USUARIO_365, SENHA)
ctx = ClientContext(SHAREPOINT_SITE).with_credentials(ctx_auth)


class SharepointHandler:
    def __init__(self, nome_da_lista):
        self.nome_lista = nome_da_lista
        self.lista = self.__get_list()

    def __get_list(self):
        try:
            web = ctx.web
            list_title = self.nome_lista
            target_list = web.lists.get_by_title(list_title)
            ctx.load(target_list)
            ctx.execute_query()
        except Exception as e:
            print(str(e))

        return target_list

    def get_list_dict(self) -> List:
        lista: List = []
        items = self.lista.items.get_all()
        ctx.load(items)
        ctx.execute_query()

        lista_campo_padrao = ['FileSystemObjectType',
                              'ServerRedirectedEmbedUri',
                              'ServerRedirectedEmbedUrl',
                              'ContentTypeId',
                              'Title',
                              'OData__ColorTag',
                              'ComplianceAssetId',
                              'AuthorId',
                              'EditorId',
                              'OData__UIVersionString',
                              'Attachments',
                              'GUID',
                              'ID']

        for item in items:
            dicionario = dict(item.properties.items().mapping)
            for coluna in lista_campo_padrao:
                del dicionario[coluna]

            lista.append(dicionario)

        return lista

    def add_item_list(self, chamados_adicionar):
        for jira in chamados_adicionar:
            try:
                new_item = self.lista.add_item(jira)
                ctx.execute_query()
                time.sleep(0.5)
            except Exception as e:
                print(str(e))

    def remove_item_list(self, chamados_excluir: List):
        for item in chamados_excluir:
            item_id = item.get(id)
            item = self.lista.items.get_by_id(item_id)
            item.delete_object()
            ctx.execute_query()
            time.sleep(0.5)

    def update_item_list(self, chamados_desatualizados):
        for chamado in chamados_desatualizados:
            try:
                id = chamado.get("Id")
                itens = self.lista.items.get_by_id(id)
                itens.set_property('CHAVE', chamado.get("CHAVE"))
                itens.set_property('TIPO_x0020_DE_x0020_ITEM', chamado.get("TIPO_x0020_DE_x0020_ITEM"))
                itens.set_property('REQUEST_x0020_TYPE', chamado.get("REQUEST_x0020_TYPE"))
                itens.set_property('RESUMO', chamado.get("RESUMO"))
                itens.set_property('STATUS', chamado.get("STATUS"))
                itens.set_property('RESOLUCAO', chamado.get("RESOLUCAO"))
                itens.set_property('ATUALIZADO', chamado.get("ATUALIZADO"))
                itens.set_property('CRIADO_x0020_EM', chamado.get("CRIADO_x0020_EM"))
                itens.set_property('RELATOR', chamado.get("RELATOR"))
                itens.set_property('RESOLVIDO_x0020_EM', chamado.get("RESOLVIDO_x0020_EM"))
                itens.set_property('UTILIZAR_x0020_CENTRO_x0020_DE_x', chamado.get("UTILIZAR_x0020_CENTRO_x0020_DE_x"))
                itens.set_property('SERIE_x0020_DO_x0020_EQUIPAMENTO', chamado.get("SERIE_x0020_DO_x0020_EQUIPAMENTO"))
                itens.set_property('TIPO_x0020_DE_x0020_EQUIPAMENTO', chamado.get("TIPO_x0020_DE_x0020_EQUIPAMENTO"))
                itens.set_property('CATEGORIA_x0020_DO_x0020_EQUIPAM', chamado.get("CATEGORIA_x0020_DO_x0020_EQUIPAM"))
                itens.set_property('DATA_x0020_DA_x0020_AFERICAO', chamado.get("DATA_x0020_DA_x0020_AFERICAO"))
                itens.set_property('RESPONSAVEL_x0020_DA_x0020_AFERI', chamado.get("RESPONSAVEL_x0020_DA_x0020_AFERI"))
                itens.update()
                ctx.execute_query()
                time.sleep(0.2)
            except ConnectionAbortedError as e:
                print(str(e))
                continue
            except ConnectionError as e:
                print(str(e))
                continue
            except ConnectionRefusedError as e:
                print(str(e))
                continue
            except requests.exceptions.HTTPError as e:
                print(str(e))
                continue