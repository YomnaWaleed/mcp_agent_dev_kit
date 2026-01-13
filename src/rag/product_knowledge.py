import chromadb
from sentence_transformers import SentenceTransformer


class ProductRAG:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.client = chromadb.PersistentClient(path="src/rag/products/chroma_db")
        self.collection = self.client.get_collection("bank_products")

    def search_products(self, query: str, n_results: int = 3):
        """Search for relevant products"""
        results = self.collection.query(query_texts=[query], n_results=n_results)

        products = []
        for i, metadata in enumerate(results["metadatas"][0]):
            products.append(
                {"product": metadata, "relevance_score": results["distances"][0][i]}
            )

        return products

    def get_product_by_id(self, product_id: str):
        """Get specific product by ID"""
        result = self.collection.get(ids=[product_id])
        if result["metadatas"]:
            return result["metadatas"][0]
        return None


# Test function
if __name__ == "__main__":
    rag = ProductRAG()
    results = rag.search_products("I need a savings account")
    print(results)
