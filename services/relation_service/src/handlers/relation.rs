use actix_web::{get, web, HttpResponse, Responder};

#[get("/test")]
async fn test() -> impl Responder {
    return HttpResponse::Ok().json("hello");
}

pub fn relation_router_config(cfg: &mut web::ServiceConfig) -> () {
    cfg.service(web::scope("relation").service(test));
}
