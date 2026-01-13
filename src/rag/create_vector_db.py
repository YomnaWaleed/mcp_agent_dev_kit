import json
import chromadb
from sentence_transformers import SentenceTransformer


def create_product_embeddings():
    # Load products
    with open("src/rag/products/products.json", "r") as f:
        data = json.load(f)

    # Initialize embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Create ChromaDB client
    client = chromadb.PersistentClient(path="src/rag/products/chroma_db")

    # Create or get collection
    collection = client.get_or_create_collection(
        name="bank_products", metadata={"description": "Bank product knowledge base"}
    )

    # Prepare documents
    documents = []
    metadatas = []
    ids = []

    for product in data["products"]:
        # Create searchable text
        features_str = ", ".join(product.get("features", []))
        doc_text = f"""
        Product: {product['name']}
        Type: {product['type']}
        Description: {product['description']}
        Features: {features_str}
        """

        documents.append(doc_text)

        # Convert all list values to strings for ChromaDB compatibility
        metadata = {}
        for key, value in product.items():
            if isinstance(value, list):
                metadata[key] = ", ".join(
                    str(v) for v in value
                )  # Convert list to comma-separated string
            else:
                metadata[key] = value

        metadatas.append(metadata)
        ids.append(product["id"])

    # Add to collection
    collection.add(documents=documents, metadatas=metadatas, ids=ids)

    print(f"✅ Created vector database with {len(documents)} products")
    print(f"📁 Location: src/rag/products/chroma_db")


if __name__ == "__main__":
    create_product_embeddings()
