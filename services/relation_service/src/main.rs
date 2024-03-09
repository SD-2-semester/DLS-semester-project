use actix_web::{middleware::Logger, web, App, HttpServer};
use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;

mod dao;
mod db;
mod dtos;
mod handlers;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // create logger
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    // Create neo4j db
    let graph = db::db::create_graph()
        .await
        .expect("Failed to create graph");

    #[derive(OpenApi)]
    #[openapi(
        paths(handlers::relation::test, handlers::relation::create_relation),
        components(schemas(
            dtos::response_dto::ResponseDataString,
            dtos::relation_dto::RelationInputDTO
        ))
    )]
    struct ApiDoc;
    let openapi = ApiDoc::openapi();

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(web::Data::new(graph.clone()))
            .service(
                SwaggerUi::new("/swagger-ui/{_:.*}").url("/api-docs/openapi.json", openapi.clone()),
            )
            .configure(handlers::relation::relation_router_config)
    })
    .bind(("127.0.0.1", 8000))?
    .run()
    .await
}
