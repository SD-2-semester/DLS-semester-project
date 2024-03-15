use crate::dao;
use crate::dtos;
use crate::rabbitmq;

use actix_web::{get, post, web, HttpResponse, Responder};
use neo4rs::Graph;
use utoipa;
use lapin::{
    Channel
};

#[utoipa::path(
    tag="user",
    path="/user/test",
    responses(
        (status = 200, description = "Test", body = ResponseDataString))
)]
#[get("/test")]
async fn test(_channel: web::Data<Channel>) -> impl Responder {
    // rabbitmq::connection::publish_to_queue(&channel, "new_user").await;
    HttpResponse::Ok().json(dtos::response_dtos::ResponseData { data: "hello" })
}


// Get a users relations.
#[utoipa::path(
    tag="user",
    path="/user",
    responses((status = 200, description = "Get a users relations", body = ResponseDataString))
)]
#[get("")]
async fn get_user_relations() -> impl Responder {
    HttpResponse::Ok().json(dtos::response_dtos::ResponseData { data: "hello" })
}

// Create a user.
#[utoipa::path(
    tag="user",
    path="/user",
    request_body = UserInputDTO,
    responses(
        (status = 201, body = ResponseDataMessageOK),
        (status = 409, body = ResponseDataMessageError)),
)]
#[post("")]
async fn create_user(
    input_dto: web::Json<dtos::user_dtos::UserInputDTO>,
    db: web::Data<Graph>,
) -> impl Responder {

    match  dao::user_dao::create_node(&db, input_dto.into_inner()).await {
    Ok(_) =>HttpResponse::Created().json(dtos::response_dtos::ResponseData { data: dtos::response_dtos::MessageOk::default()}),
    Err(e) => {
        // Here you can log the error and return an error response
        println!("Error creating user: {:?}", e);
        HttpResponse::Conflict().json(dtos::response_dtos::ResponseData { data: dtos::response_dtos::MessageError::new(e.to_string())})
    }
}
}

// Create a relationship between two user.
#[utoipa::path(
    tag="user",
    path="/user/relation",
    request_body = RelationInputDTO,
    responses(
        (status = 201, body = ResponseDataMessageOK),
        (status = 404, body = ResponseDataMessageError),),

)]
#[post("/relation")]
async fn create_user_relation(
    input_dto: web::Json<dtos::user_dtos::RelationInputDTO>,
    db: web::Data<Graph>,
    channel: web::Data<Channel>
) -> impl Responder {

    let relation_dto = input_dto.into_inner();

    match dao::user_dao::create_relationship(&db, &relation_dto).await {
        Ok(Some(_)) =>  {
            rabbitmq::connection::publish_to_queue(&channel, "new_relation_queue", &relation_dto).await;
            HttpResponse::Created().json(dtos::response_dtos::ResponseData {
                data: dtos::response_dtos::MessageOk::default()
            })},
        Ok(None) =>  HttpResponse::NotFound().json(dtos::response_dtos::ResponseData { data: dtos::response_dtos::MessageError::default()}),
        Err(e) => HttpResponse::InternalServerError().json(dtos::response_dtos::ResponseData { data: dtos::response_dtos::MessageError::new(e.to_string())})
    }


}

pub fn relation_router_config(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("user")
            .service(test)
            .service(create_user)
            .service(create_user_relation),
    );
}
