use dotenv::dotenv;
use neo4rs::*;
use std::env;

/// Create a connection to the database and return db abstraction.
pub async fn create_graph() -> Result<Graph, Error> {
    dotenv().ok(); // Load .env file

    let uri =
        env::var("NEO4J_URI").unwrap_or_else(|_| "bolt://localhost:7687".to_string());
    let user = env::var("NEO4J_USER").unwrap_or_else(|_| "neo4j".to_string());
    let password =
        env::var("NEO4J_PASSWORD").unwrap_or_else(|_| "password".to_string());
    let db = env::var("NEO4J_DB").unwrap_or_else(|_| "neo4j".to_string());

    let config = ConfigBuilder::default()
        .uri(&uri)
        .user(&user)
        .password(&password)
        .db(db)
        .fetch_size(500)
        .max_connections(10)
        .build()
        .unwrap();

    let graph = Graph::connect(config).await?;

    // create unique constraint on user_id
    let constraint_query = query(
        "CREATE CONSTRAINT FOR (user:User) REQUIRE user.user_id IS UNIQUE
    ",
    );

    match graph.run(constraint_query).await {
        Ok(_) => println!("Unique constraint created or already exists"),
        Err(e) => println!("Failed to create unique constraint: {:?}", e),
    }

    Ok(graph)
}
