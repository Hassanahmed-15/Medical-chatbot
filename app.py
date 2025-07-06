from flask import Flask, render_template, request, jsonify
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA

# Initialize Flask
app = Flask(__name__)

# Initialize Pinecone client
pc = Pinecone(api_key="pcsk_MxPfh_3R9kDC6vpMGQP8v8ESMehd5Z5oaMiz7Jakf95aqQEiEHLBntGq3GN5YMbEgsuJH", environment="us-east-1")
index = pc.Index("medical")

# Initialize Embeddings & Vector Store
embeddings = HuggingFaceEmbeddings(model_name="thenlper/gte-large")
vector_store = PineconeVectorStore(index=index, embedding=embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 6})

# Initialize Llama Model for QA
llm = CTransformers(
    model=r"D:\Dell\Documents\Medical-chatbot\Medical-chatbot\model\llama-2-7b-chat.ggmlv3.q2_K.bin",
    model_type="llama",
    model_kwargs={
        "gpu_layers": 40,
        "max_new_tokens": 256,
        "temperature": 0.1,
    },
)

qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

# Store the conversation in memory
conversation_history = []

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def get_bot_response():
    user_msg = request.form.get("msg")
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    # Add user message to conversation history
    conversation_history.append(f"User: {user_msg}")

    # Get chatbot's answer
    answer = qa_chain.run(user_msg)
    
    # Add bot's answer to conversation history
    conversation_history.append(f"Bot: {answer}")

    return jsonify(answer)

if __name__ == "__main__":
    app.run(debug=True)
