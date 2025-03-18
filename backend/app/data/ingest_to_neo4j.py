from app.db.neo4j_client import Neo4jClient


def create_gene_power_mapping(tx, mapping):
    query = """
    UNWIND $mapping as pair
    MERGE (g:Gene {name: pair.gene})
    MERGE (p:Power {name: pair.power})
    MERGE (g)-[r:CONFERS]->(p)
    ON CREATE SET r.weight = rand()
    """
    mapping_list = [{"power": power, "gene": gene} for power, gene in mapping.items()]
    tx.run(query, mapping=mapping_list)


def create_character(tx, name, description, primary_powers, affiliations, genes):
    query = """
    WITH $name AS name, 
         $description AS description, 
         $primary_powers AS primary_powers, 
         $affiliations AS affiliations, 
         $genes AS genes
    // Create or merge the Character node and set its description.
    MERGE (c:Character {name: name})
      SET c.description = description

    // For each primary power, create a Power node and connect via POSSESSES_POWER.
    FOREACH (power IN primary_powers |
      MERGE (p:Power {name: power})
      MERGE (c)-[:POSSESSES_POWER]->(p)
    )

    // For each affiliation, create a Team node and connect via MEMBER_OF.
    FOREACH (team IN affiliations |
      MERGE (t:Team {name: team})
      MERGE (c)-[:MEMBER_OF]->(t)
    )

    // For each gene, create a Gene node and connect via HAS_MUTATION with a random weight.
    FOREACH (gene IN genes |
      MERGE (g:Gene {name: gene})
      MERGE (c)-[r:HAS_MUTATION]->(g)
      ON CREATE SET r.weight = rand()
    )
    """
    tx.run(query,
           name=name,
           description=description,
           primary_powers=primary_powers,
           affiliations=affiliations,
           genes=genes)


def ingest_to_neo4j(df, power_gene_map):
    client = Neo4jClient()
    client.write_transaction(create_gene_power_mapping, power_gene_map)
    with client.driver.session() as session:
        for _, row in df.iterrows():
            session.write_transaction(
                create_character,
                row["Character Name"],
                row["Description"],
                row["Primary Powers"],
                row["Affiliation"],
                row["Genes"]
            )
    client.close()
