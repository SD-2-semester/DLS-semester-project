use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema)]
#[aliases(ResponseDataString = ResponseData<String>)]
pub struct ResponseData<T> {
    pub data: T,
}
