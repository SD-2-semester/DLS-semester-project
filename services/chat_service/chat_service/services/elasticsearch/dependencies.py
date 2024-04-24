from typing import Annotated, Any, Literal, Type, TypeVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Request
from pydantic import BaseModel

from chat_service import exceptions
from chat_service.utils import dtos

MessageDTO = dtos.ChatElasticDTO | dtos.ServerElasticDTO
OutDTO = TypeVar("OutDTO", bound=MessageDTO)


def get_es_client(request: Request) -> AsyncElasticsearch:
    """Get Elasticsearch client from app state."""
    return request.app.state.es


class ElasticsearchService:
    """Elasticsearch Service."""

    def __init__(
        self,
        es_client: AsyncElasticsearch = Depends(get_es_client),
    ) -> None:
        self.es_client = es_client

    async def post_message(self, index: str, dto: MessageDTO) -> None:
        """Post DTO data to an index."""
        try:
            await self.es_client.index(
                index=index,
                body=dto.model_dump_json(),
            )
        except Exception as exc:
            raise exceptions.Http500(detail=f"Error: {exc}")

    async def search_messages(
        self,
        obj_id: UUID,
        index: Literal["server_message", "chat_message"],
        message: str,
        out_dto: Type[OutDTO],
    ) -> list[OutDTO]:
        """Search messages by object id and message."""

        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                (
                                    "server_id"
                                    if index == "server_message"
                                    else "chat_id"
                                ): obj_id
                            }
                        },
                        {"match": {"message": message}},
                    ]
                }
            }
        }

        try:
            result = await self.es_client.search(
                index=index,
                body=query,
            )
        except Exception as exc:
            raise exceptions.Http500(detail=f"Error: {exc}")

        hits = result["hits"]["hits"]

        print(result)

        if not hits:
            return []

        return [out_dto.model_validate(hit["_source"]) for hit in hits]


GetES = Annotated[ElasticsearchService, Depends(ElasticsearchService)]
