use neo4rs::*;

pub async fn create_graph() -> Result<Graph> {
    let config = ConfigBuilder::default()
        .uri("bolt://neo4j:7687")
        .user("neo4j")
        .password("password")
        .db("neo4j")
        .fetch_size(500)
        .max_connections(10)
        .build()
        .unwrap();
    let graph = Graph::connect(config).await?;
    Ok(graph)
}
