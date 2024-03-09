use actix_web::{middleware::Logger, App, HttpServer};
use utoipa::{openapi, OpenApi};
use utoipa_swagger_ui::SwaggerUi;

mod handlers;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // create logger
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    // // create openapi
    // struct ApiDoc;
    // let openapi = ApiDoc::openapi();

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .configure(handlers::relation::relation_router_config)
    })
    .bind(("127.0.0.1", 8000))?
    .run()
    .await
}
