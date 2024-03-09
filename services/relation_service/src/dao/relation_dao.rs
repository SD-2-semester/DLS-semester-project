use neo4rs::*;

pub async fn create_node(graph: &Graph) -> Result<(), neo4rs::Error> {
    graph
        .run(
            query("CREATE (p:Person {name: $name, made_in: $made_in})")
                .param("name", "snab")
                .param("made_in", "rust"),
        )
        .await
        .unwrap();
    Ok(())
}
