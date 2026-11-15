from app.rag import RAGPipeline

# Initialize RAG pipeline
rag = RAGPipeline(top_k=3)

# Ask a question
question = "Tell me about Ahmednagar Fort."

# Generate answer
result = rag.answer(question)

# Display output
print("\nQUESTION:")
print(question)

print("\nRAG RESPONSE:")
print(result)