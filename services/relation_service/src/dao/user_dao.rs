use crate::dtos::user_dtos::{RelationInputDTO, UserInputDTO};
use neo4rs::*;

// Create user in the database.
pub async fn create_node(graph: &Graph, user_dto: UserInputDTO) -> Result<(), neo4rs::Error> {
    let query = query("CREATE (p:User {user_id: $user_id, user_name: $user_name})")
        .param("user_id", user_dto.user_id.to_string())
        .param("user_name", user_dto.user_name);

    graph.run(query).await?;

    Ok(())
}

// Create relationship between two users in the database.
// If the database doesn't return an id, return None (returns an Option).
pub async fn create_relationship(
    graph: &Graph,
    relation_dto: &RelationInputDTO,
) -> Result<Option<i32>, neo4rs::Error> {
    let query = query(
        "MATCH (a:User), (b:User)
        WHERE a.user_id = $user_id_1 AND b.user_id = $user_id_2
        CREATE (a)-[r:IsFriendsWith]->(b)
        RETURN id(r) as relation_id",
    )
    .param("user_id_1", relation_dto.user_id_1.to_string())
    .param("user_id_2", relation_dto.user_id_2.to_string());

    let mut result = graph.execute(query).await?;

    // Check if the relationship was created
    if let Some(row) = result.next().await? {
        let relation_id: i32 = row.get("relation_id").unwrap();
        Ok(Some(relation_id))
    } else {
        Ok(None)
    }
}
