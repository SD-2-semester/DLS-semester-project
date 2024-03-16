use crate::dtos::user_dtos::{RelationInputDTO, UserInputDTO, UserRelationDTO};
use chrono;
use neo4rs::*;
use uuid;

/// Create user in the database.
pub async fn create_node(
    graph: &Graph,
    user_dto: UserInputDTO,
) -> Result<(), neo4rs::Error> {
    let created_at = chrono::Utc::now();

    let query = query(
        "CREATE (p:User {user_id: $user_id, 
        user_name: $user_name, created_at: $created_at})",
    )
    .param("user_id", user_dto.user_id.to_string())
    .param("user_name", user_dto.user_name)
    .param("created_at", created_at.to_rfc3339());

    graph.run(query).await?;

    Ok(())
}

/// Create relationship between two users in the database.
/// If the database doesn't return an id, return None (returns an Option).
pub async fn create_relationship(
    graph: &Graph,
    relation_dto: &RelationInputDTO,
) -> Result<Option<i32>, neo4rs::Error> {
    let created_at = chrono::Utc::now();
    let query = query(
        "MATCH (a:User), (b:User)
        WHERE a.user_id = $user_id_1 AND b.user_id = $user_id_2
        MERGE (a)-[r:IsFriendsWith]->(b)
        ON CREATE SET r.created_at = $created_at
        RETURN id(r) as relation_id",
    )
    .param("user_id_1", relation_dto.user_id_1.to_string())
    .param("user_id_2", relation_dto.user_id_2.to_string())
    .param("created_at", created_at.to_rfc3339());

    let mut result = graph.execute(query).await?;

    // Check if the relationship was created
    if let Some(row) = result.next().await? {
        let relation_id: i32 = row.get("relation_id").unwrap();
        Ok(Some(relation_id))
    } else {
        Ok(None)
    }
}

pub async fn get_all_relationships(
    user_id: uuid::Uuid,
    graph: &Graph,
) -> Result<Vec<UserRelationDTO>, neo4rs::Error> {
    let mut relation_list: Vec<UserRelationDTO> = Vec::new();

    let query = query(
        "
        MATCH (a:User {user_id: $user_id})-[r:IsFriendsWith]-(b:User)
        RETURN  b.user_name as user_name, r.created_at as friends_since
    ",
    )
    .param("user_id", user_id.to_string());

    let mut result = graph.execute(query).await?;

    while let Some(row) = result.next().await? {
        // Handle potential conversion error
        match row.to::<UserRelationDTO>() {
            Ok(user_relation) => relation_list.push(user_relation),
            Err(e) => {
                eprintln!("Error converting row to UserRelationDTO: {}", e);
                continue;
            }
        }
    }

    println!("{:?}", relation_list);

    Ok(relation_list)
}
