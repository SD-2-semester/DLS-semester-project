use crate::dao;
use crate::dtos;
use actix_web::{get, post, web, HttpResponse, Responder};
use neo4rs::Graph;
use utoipa;

#[utoipa::path(
    tag="relation", 
    path="/relation/test", 
    responses((status = 200, description = "Test", body = ResponseDataString))
)]
#[get("/test")]
async fn test() -> impl Responder {
    return HttpResponse::Ok().json(dtos::response_dto::ResponseData { data: "hello" });
}

#[utoipa::path(
    tag="relation", 
    path="/relation", 
    responses((status = 201, description = "Test", body = RelationInputDTO))
)]
#[post("")]
async fn create_relation(
    input_dto: web::Json<dtos::relation_dto::RelationInputDTO>,
    db: web::Data<Graph>,
) -> impl Responder {
    
    dao::relation_dao::create_node(&db).await.expect("damn");

    return HttpResponse::Created().json(dtos::response_dto::ResponseData { data: input_dto });
}

pub fn relation_router_config(cfg: &mut web::ServiceConfig) -> () {
    cfg.service(
        web::scope("relation")
            .service(test)
            .service(create_relation),
    );
}
