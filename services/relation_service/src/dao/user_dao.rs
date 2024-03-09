use crate::dtos::user_dtos::{RelationInputDTO, UserInputDTO};
use neo4rs::*;

pub async fn create_node(graph: &Graph, user_dto: UserInputDTO) -> Result<(), neo4rs::Error> {
    let query = query("CREATE (p:User {user_id: $user_id, user_name: $user_name})")
        .param("user_id", user_dto.user_id.to_string())
        .param("user_name", user_dto.user_name);

    graph.run(query).await.unwrap();
    Ok(())
}

pub async fn create_relationship(
    graph: &Graph,
    relation_dto: RelationInputDTO,
) -> Result<(), neo4rs::Error> {
    let query = query(
        "MATCH (a:User), (b:User)
        WHERE a.user_id = $user_id_1 AND b.user_id = $user_id_2
        CREATE (a)-[r:IsFriendsWith]->(b)",
    )
    .param("user_id_1", relation_dto.user_id_1.to_string())
    .param("user_id_2", relation_dto.user_id_2.to_string());
    graph.run(query).await.unwrap();
    Ok(())
}
