use neo4rs::*;

pub async fn create_graph() -> Result<Graph, Error> {
    let config = ConfigBuilder::default()
        .uri("bolt://localhost:7687")
        .user("neo4j")
        .password("password")
        .db("neo4j")
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
