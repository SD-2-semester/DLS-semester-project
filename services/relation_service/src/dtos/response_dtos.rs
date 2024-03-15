use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use std::fmt;

#[derive(Serialize, Deserialize, ToSchema)]
pub enum Status{
    Success,
    Failure,
}
impl fmt::Display for Status {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{}", match self {
            Status::Success => "Success",
            Status::Failure => "Failure",
        })
    }
}

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
    pub status: Status,
}

impl Default for MessageOk {
    fn default() -> Self {
        MessageOk {
            message: "Object was created.".to_string(),
            status: Status::Success,
        }
    }
}

#[derive(Serialize, Deserialize, ToSchema)]
#[aliases(MessageError = MessageError)]
pub struct MessageError {
    pub message: String,
    pub status: Status,
}

impl Default for MessageError {
    fn default() -> Self {
        MessageError {
            message: "Object was not created.".to_string(),
            status: Status::Failure,
        }
    }
}

// MessageError with a custom message
impl MessageError {
    pub fn new(message: String) -> Self {
        MessageError {
            message,
            status: Status::Failure,
        }
    }
}