use actix_web::{middleware::Logger, web, App, HttpServer};

use utoipa::OpenApi;
use utoipa_swagger_ui::SwaggerUi;
mod dao;
mod db;
mod dtos;
mod handlers;
pub mod rabbitmq;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // create logger
    env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));

    // Create neo4j db
    let graph = db::db::create_graph()
        .await
        .expect("Failed to create graph");

    let graph_data = web::Data::new(graph);

    let connection = rabbitmq::connection::get_connection().await;
    let channel = rabbitmq::connection::channel_rabbitmq(&connection).await;
    rabbitmq::connection::create_queue(&channel, "new_relation_queue").await;
    rabbitmq::connection::create_queue(&channel, "new_user_queue").await;
    let consumer_a =
        rabbitmq::connection::create_consumer(&channel, "new_relation_queue").await;
    let consumer_b =
        rabbitmq::connection::create_consumer(&channel, "new_user_queue").await;
    rabbitmq::connection::print_result(&consumer_a).await;
    rabbitmq::connection::create_new_user(&consumer_b, graph_data.clone()).await;

    #[derive(OpenApi)]
    #[openapi(
        paths(
            handlers::users::test,
            handlers::users::create_user,
            handlers::users::create_user_relation
        ),
        components(schemas(
            dtos::response_dtos::ResponseDataString,
            dtos::response_dtos::ResponseDataMessageOK,
            dtos::response_dtos::MessageOk,
            dtos::response_dtos::Status,
            dtos::response_dtos::MessageError,
            dtos::user_dtos::RelationInputDTO,
            dtos::user_dtos::UserInputDTO
        ))
    )]
    struct ApiDoc;
    let openapi = ApiDoc::openapi();

    HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .app_data(graph_data.clone())
            .app_data(web::Data::new(channel.clone()))
            .service(
                SwaggerUi::new("/swagger-ui/{_:.*}")
                    .url("/api-docs/openapi.json", openapi.clone()),
            )
            .configure(handlers::users::relation_router_config)
    })
    .bind(("0.0.0.0", 8000))?
    .run()
    .await
}
