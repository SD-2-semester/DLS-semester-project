from typing import Annotated, Any, Literal, Type, TypeVar
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import Depends, Request
from pydantic import BaseModel

from chat_service import exceptions
from chat_service.utils import dtos

MessageCreateDTO = dtos.ChatElasticCreateDTO | dtos.ServerElasticCreateDTO
MessageResponseDTO = dtos.ChatElasticDTO | dtos.ServerElasticDTO
OutDTO = TypeVar("OutDTO", bound=MessageResponseDTO)


def get_es_client(request: Request) -> AsyncElasticsearch:
    """Get Elasticsearch client from app state."""
    return request.app.state.es


Index = Literal["server_message", "chat_message"]


class ElasticsearchService:
    """Elasticsearch Service."""

    def __init__(
        self,
        es_client: AsyncElasticsearch = Depends(get_es_client),
    ) -> None:
        self.es_client = es_client

    async def post_message(
        self,
        index: Index,
        dto: MessageCreateDTO,
    ) -> None:
        """Post DTO data to an index."""
        try:
            await self.es_client.index(
                index=index,
                body=dto.model_dump_json(),
            )
        except Exception as exc:
            raise exceptions.Http500(detail=f"Error when posting: {exc}")

    async def search_messages(
        self,
        obj_id: Annotated[UUID, "Either chat_id or server_id."],
        index: Index,
        message: str,
        out_dto: Type[OutDTO],
    ) -> list[OutDTO]:
        """Search messages by object id and message."""

        field_name = "server_id" if index == "server_message" else "chat_id"

        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {f"{field_name}.keyword": obj_id}},
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
            raise exceptions.Http500(detail=f"Error when searching: {exc}")

        hits = result["hits"]["hits"]
        if not hits:
            return []

        return [out_dto.model_validate(hit["_source"]) for hit in hits]  # type: ignore


GetES = Annotated[ElasticsearchService, Depends(ElasticsearchService)]
