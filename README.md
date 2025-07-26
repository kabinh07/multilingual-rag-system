# Multilingual RAG System

A multilingual question-answering system using RAG (Retrieval-Augmented Generation) with support for Bengali language processing. This system combines document processing, vector embeddings, and large language models to provide accurate answers from Bengali and English documents.

## Setup Guide

### Prerequisites
- Docker and Docker Compose
- At least 16GB RAM (recommended for optimal performance)
- NVIDIA GPU (optional, for faster processing)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd multilingual-rag-system
   ```

2. **Add your PDF documents**:
   Place PDF files in the `app/knowledge_bases/` directory

3. **Start the system**:
   ```bash
   docker-compose up -d
   ```

4. **Wait for initialization**:
   The system will automatically download the required model and process your documents. This may take a few minutes on first run.

### Without GPU Support
If you don't have NVIDIA GPU support, comment out the `deploy` section in `docker-compose.yaml`:
```yaml
# deploy:                       # Comment this out if there is no gpu support
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: 1
#           capabilities: [gpu]
```

## Tools, Libraries, and Packages Used

### Core Framework
- **LangChain**: Framework for building LLM applications
- **LangGraph**: State-based graph framework for complex workflows
- **FastAPI**: Modern web framework for building APIs

### Language Models & Embeddings
- **Ollama**: Local LLM server (default: `gemma3:12b`)
- **HuggingFace Transformers**: For embedding models
- **Bengali Sentence Similarity SBERT**: Specialized Bengali embedding model

### Vector Database & Search
- **Qdrant**: Vector database for similarity search
- **LangChain Qdrant**: Integration layer for vector operations

### Document Processing
- **PyMuPDF**: PDF text extraction
- **bangla-pdf-ocr**: OCR for broken/scanned Bengali PDFs
- **RecursiveCharacterTextSplitter**: Intelligent text chunking

### Additional Libraries
- **Sentence Transformers**: Embedding model support
- **Python-dotenv**: Environment configuration
- **Uvicorn**: ASGI server for FastAPI

## Sample Queries and Outputs

### Bengali Questions

#### Query 1: Literary Analysis
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?"}'
```

#### Query 2: Character Information
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "কাকে অনুপমের ভাগ্য দেবতা বলে উল্লেখ করা হয়েছে?"}'
```

#### Query 3: Specific Details
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "বিয়ের সময় কল্যাণীর প্রকৃত বয়স কত ছিল?"}'
```

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### POST /chat
Processes user questions and returns AI-generated responses based on the knowledge base.

**Request:**
```json
{
  "message": "Your question here in Bengali or English"
}
```

**Response:**
- **Content-Type:** `text/plain`
- **Format:** Streaming response
- **Body:** AI-generated answer based on retrieved context

**Example:**
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "আপনার প্রশ্ন এখানে লিখুন"}'
```

### Error Handling
- Returns JSON error object if request processing fails
- Format: `{"error": "error_description"}`

### Quality Assessment

#### Strengths
- **Multilingual Support**: Handles both Bengali and English effectively
- **Context Preservation**: Maintains document context through chunking
- **Semantic Search**: Uses specialized Bengali embeddings for better understanding
- **Real-time Processing**: Streaming responses for better user experience

#### Areas for Improvement
- **Complex Queries**: Performance decreases with multi-part questions
- **Cross-lingual Queries**: Mixed language queries need refinement
- **Long Documents**: Very large documents may lose context coherence

## Technical Implementation Details

### 1. Text Extraction Method

The original PDF used the `Noto Sans Bengali` font, and I couldn’t find any PDF reader capable of properly normalizing the text. I also attempted text normalization using Python’s `unicodedata` and `bnunicodedata` libraries after extracting text from the PDF, but these approaches failed.

As a result, I opted for **bangla-pdf-ocr**, which converts PDF pages into images and then performs OCR using either **Tesseract** or **EasyOCR**.

However, the OCR output was not identical to the original PDF content:
- Some portions of text were missing.
- Certain parts were broken or incorrectly recognized.

I applied multiple regex-based cleaning techniques to improve the output. Although the final cleaned text was still not fully satisfactory, it was good enough to proceed with downstream tasks.

---

### 2. Chunking Strategy

For chunking, I used the **RecursiveCharacterTextSplitter** from **LangChain**, a tool I was already comfortable with from previous projects.

I experimented with various chunk sizes ranging from 100 to 1000 tokens. A chunk size of **500 tokens** produced the best balance between context coverage and semantic similarity.

Additionally, I implemented a **multi-level chunking strategy**:
1. Attempt paragraph-based chunking.
2. Fall back to line-break-based splitting.
3. Then sentence-level splitting.
4. Finally, split by spaces if needed.

---

### 3. Embedding Model

I experimented with several multilingual and Bangla-specific sentence transformers:
- `intfloat/multilingual-e5-base`
- `shihab17/bangla-sentence-transformer`
- `l3cube-pune/bengali-sentence-similarity-sbert` (inspired by **PoRAG**)

Among these, **l3cube-pune/bengali-sentence-similarity-sbert** provided the best retrieval performance for my RAG setup.

Both Bangla-specific models (`shihab17/bangla-sentence-transformer` and `l3cube-pune/bengali-sentence-similarity-sbert`) are fine-tuned on Bangla data and share the same **context length and embedding dimension (768)**. Sentence Transformers encode text into semantically meaningful vectors, which is ideal for similarity search.

---

### 4. Vector Database and Similarity Metric

I chose **Qdrant** as my vector database because it is:
- Open-source
- Lightweight and easy to deploy
- Simple to integrate with LangChain

For similarity, I used **cosine similarity** instead of dot product:
- Cosine similarity normalizes vector length, removing dependency on text sequence length.
- It provides a bounded score in the range [-1, 1], making thresholding straightforward.

---

### 5. Retrieval and Query Comparison

There is no explicit documented comparison method implemented. The retrieval process is purely vector-based:
- Query embeddings are compared with stored document embeddings using the chosen similarity metric.
- Retrieved results include similarity scores.
- If no relevant context is found (low similarity or vague match), the LLM responds with “not in knowledge base.”

---

### 6. Current Performance and Possible Improvements

#### Current State
- Retrieval works well when relevant context is present in the vector database.
- Performance is limited due to **inaccuracies in OCR extraction** from the PDF.

#### Improvement Areas
- **Knowledge Base Quality**: Use normalized fonts or better OCR to improve text quality.
- **Vectorization Strategy**: Separate embeddings for different content types:
  - Story sections and question sections.
  - Tabular data (e.g., MCQ answer tables) treated separately.
- **Research Documentation**: Maintain detailed documentation of experiments and R&D for better reproducibility and visualization.

**The performance heavily depends on the parameter size of the LLM**

## Services Architecture

The system runs three containerized services:

- **App** (port 8000): FastAPI server handling user requests
- **Ollama** (port 11434): Local LLM server for text generation  
- **Qdrant** (port 6333): Vector database for similarity search

## Configuration

### Environment Variables
Create a `.env` file to customize settings:
```env
LLM_MODEL=gemma3:12b
EMB_MODEL=l3cube-pune/bengali-sentence-similarity-sbert
QDRANT_HOST=qdrant
QDRANT_PORT=6333
COLLECTION_NAME=chatbot_context
VECTOR_SIZE=768
```

### Changing the Language Model

**Option 1: Change in entrypoint.sh**
Edit `ollama/entrypoint.sh` and change line 9:
```bash
ollama pull gemma3:12b  # or any other model
```

**Option 2: Manually pull model after startup**
```bash
docker exec -it ollama ollama pull llama3:8b
docker exec -it ollama ollama pull mistral:7b
```

## Troubleshooting

### Check if services are running:
```bash
docker-compose ps
```

### View logs:
```bash
docker-compose logs app
docker-compose logs ollama
docker-compose logs qdrant
```

### Restart services:
```bash
docker-compose restart
```

## Stopping the System

```bash
docker-compose down
```

## Performance Optimization

### For Better Results:
1. **GPU Usage**: Enable GPU support for faster embedding generation
2. **Model Selection**: Use larger models (gemma3:12b vs gemma3:1b) for better understanding
3. **Document Quality**: Ensure PDFs are text-based rather than scanned images
4. **Query Specificity**: More specific questions yield better results

### Memory Requirements:
- **Minimum**: 8GB RAM (basic functionality)
- **Recommended**: 16GB RAM (optimal performance)
- **With GPU**: Additional 4-8GB VRAM depending on model size