use crate::dao;
use crate::dtos;
use actix_web::{get, post, web, HttpResponse, Responder};
use neo4rs::Graph;
use utoipa;

#[utoipa::path(
    tag="user", 
    path="/user/test", 
    responses((status = 200, description = "Test", body = ResponseDataString))
)]
#[get("/test")]
async fn test() -> impl Responder {
    return HttpResponse::Ok().json(dtos::response_dtos::ResponseData { data: "hello" });
}

#[utoipa::path(
    tag="user", 
    path="/user", 
    request_body = UserInputDTO,
    responses((status = 201, 
        description = "Endpoint for creating a relation between two users.", 
            body = ResponseDataMessageOK)),
)]
#[post("")]
async fn create_user(
    input_dto: web::Json<dtos::user_dtos::UserInputDTO>,
    db: web::Data<Graph>,
) -> impl Responder {
    
    let user_dto = input_dto.into_inner();
    dao::user_dao::create_node(&db, user_dto).await.expect("damn");

    return HttpResponse::Created().json(dtos::response_dtos::ResponseData { data: dtos::response_dtos::MessageOk::default() });
}


#[utoipa::path(
    tag="user", 
    path="/user/relation", 
    request_body = RelationInputDTO,
    responses((status = 201, 
        description = "Endpoint for creating a relation between two users.", 
            body = ResponseDataMessageOK)),
)]
#[post("/relation")]
async fn create_user_relation(
    input_dto: web::Json<dtos::user_dtos::RelationInputDTO>,
    db: web::Data<Graph>,
) -> impl Responder {
    
    let relation_dto = input_dto.into_inner();
    dao::user_dao::create_relationship(&db, relation_dto).await.expect("damn");

    return HttpResponse::Created().json(dtos::response_dtos::ResponseData { data: dtos::response_dtos::MessageOk::default() });
}


pub fn relation_router_config(cfg: &mut web::ServiceConfig) -> () {
    cfg.service(
        web::scope("user")
            .service(test)
            .service(create_user)
            .service(create_user_relation),
    );
}
