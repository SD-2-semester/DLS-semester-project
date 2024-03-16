use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;

#[derive(Serialize, Deserialize, ToSchema, Debug)]
#[aliases(RelationInputDTO = RelationInputDTO)]
pub struct RelationInputDTO {
    pub user_id_1: Uuid,
    pub user_id_2: Uuid,
}

#[derive(Serialize, Deserialize, ToSchema, Debug)]
#[aliases(UserInputDTO = UserInputDTO)]
pub struct UserInputDTO {
    pub user_id: Uuid,
    pub user_name: String,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
#[aliases(UserRelationDTO=UserRelationDTO)]
pub struct UserRelationDTO {
    pub user_name: String,
    pub friends_since: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
#[aliases(UserRelationRequestDTO=UserRelationRequestDTO)]
pub struct UserRelationRequestDTO {
    pub user_id: Uuid,
}
