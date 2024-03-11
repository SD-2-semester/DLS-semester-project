use crate::dao;
use crate::dtos;
use actix_web::http::StatusCode;
use actix_web::{get, post, web, HttpResponse, Responder};
use neo4rs::Graph;
use utoipa;

#[utoipa::path(
    tag="user", 
    path="/user/test", 
    responses(
        (status = 200, description = "Test", body = ResponseDataString))
)]
#[get("/test")]
async fn test() -> impl Responder {
    return HttpResponse::Ok().json(dtos::response_dtos::ResponseData { data: "hello" });
}


#[utoipa::path(
    tag="user", 
    path="/user", 
    responses((status = 200, description = "Get a users relations", body = ResponseDataString))
)]
#[get("")]
async fn get_user_relations() -> impl Responder {
    return HttpResponse::Ok().json(dtos::response_dtos::ResponseData { data: "hello" });
}


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
) -> impl Responder {
    
    let relation_dto = input_dto.into_inner();

    match dao::user_dao::create_relationship(&db, relation_dto).await {
        Ok(Some(_)) =>  HttpResponse::Created().json(dtos::response_dtos::ResponseData { data: dtos::response_dtos::MessageOk::default() }),
        Ok(None) => HttpResponse::new(StatusCode::NOT_FOUND),
        Err(_) => HttpResponse::new(StatusCode::INTERNAL_SERVER_ERROR)
    }
}

pub fn relation_router_config(cfg: &mut web::ServiceConfig) -> () {
    cfg.service(
        web::scope("user")
            .service(test)
            .service(create_user)
            .service(create_user_relation),
    );
}
