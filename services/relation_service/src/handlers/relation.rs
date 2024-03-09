use crate::dtos;
use actix_web::{get, post, web, HttpResponse, Responder};
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
    path="/relation/", 
    responses((status = 201, description = "Test", body = ResponseDataString))
)]
#[post("/")]
async fn create_relation() -> impl Responder {
    return HttpResponse::Created().json(dtos::response_dto::ResponseData { data: "hello" });
}

pub fn relation_router_config(cfg: &mut web::ServiceConfig) -> () {
    cfg.service(
        web::scope("relation")
            .service(test)
            .service(create_relation),
    );
}
