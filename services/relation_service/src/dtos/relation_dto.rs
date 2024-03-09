use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct RelationInputDTO {
    pub user_id_1: i32,
    pub user_id_2: i32,
}
