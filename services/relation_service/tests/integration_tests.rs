#[cfg(test)]
mod tests {

    use serde_json::Value;
    extern crate relation_service;
    use relation_service::{db, handlers};

    use actix_web::{middleware::Logger, test, web, App};



    #[actix_web::test]
    async fn test_index_get() {
        // create logger
        env_logger::init_from_env(env_logger::Env::new().default_filter_or("info"));
        // Create neo4j db
        let graph = db::db::create_graph()
            .await
            .expect("Failed to create graph");

        let app = test::init_service(
            App::new()
                .wrap(Logger::default())
                .app_data(web::Data::new(graph.clone()))
                .configure(handlers::users::relation_router_config),
        )
        .await;

        // make a request
        let req = test::TestRequest::with_uri("/user/test").to_request();

        // send the request
        let resp = test::call_service(&app, req).await;

        // check if the response is success
        assert!(resp.status().is_success());

        // Read the response body
        let body = test::read_body(resp).await;
        let body: Value = serde_json::from_slice(&body).expect("Invalid JSON");
        println!("Response body: {}", body);
        // Check the response body
        let expected_json = serde_json::json!({ "data": "hello" });
        assert_eq!(body, expected_json);
    }
}
