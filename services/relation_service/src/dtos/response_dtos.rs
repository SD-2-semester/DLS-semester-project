use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Serialize, Deserialize, ToSchema)]
#[aliases(ResponseDataString = ResponseData<String>, 
    ResponseDataMessageOK = ResponseData<MessageOk>, 
    ResponseDataMessageError = ResponseData<MessageError>)]
pub struct ResponseData<T> {
    pub data: T,
}

#[derive(Serialize, Deserialize, ToSchema)]
#[aliases(MessageOk = MessageOk)]
pub struct MessageOk {
    pub message: String,
    pub status: String,
}

impl Default for MessageOk {
    fn default() -> Self {
        MessageOk {
            message: "Object was created.".to_string(),
            status: "Ok".to_string(),
        }
    }
}

#[derive(Serialize, Deserialize, ToSchema)]
#[aliases(MessageError = MessageError)]
pub struct MessageError {
    pub message: String,
    pub status: String,
}

impl Default for MessageError {
    fn default() -> Self {
        MessageError {
            message: "Object was not created.".to_string(),
            status: "failed".to_string(),
        }
    }
}

// MessageError with a custom message
impl MessageError {
    pub fn new(message: String) -> Self {
        MessageError {
            message,
            status: "failed".to_string(),
        }
    }
}