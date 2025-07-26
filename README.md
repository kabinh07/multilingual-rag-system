# Multilingual RAG System

A multilingual question-answering system using RAG (Retrieval-Augmented Generation) with support for Bengali language processing.

## Setup

### Prerequisites
- Docker and Docker Compose
- At least 16GB RAM

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

## Usage

The API will be available at `http://localhost:8000`

### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
  "message": "your question here"
}
```

## Example Questions

Test the system with these curl commands:

### Bengali Questions
```bash
# Ask about Bengali literature
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "অনুপমের ভাষায় সুপুরুষ কাকে বলা হয়েছে?"}'

# Ask about a specific topic from your knowledge base
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "কাকে অনুপমের ভাগ্য দেবতা বলে উল্লেখ করা হয়েছে?"}'

# Ask for a summary
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "বিয়ের সময় কল্যাণীর প্রকৃত বয়স কত ছিল?"}'
```

## Services

The system runs three services:
- **App** (port 8000): Main API server
- **Ollama** (port 11434): Language model server  
- **Qdrant** (port 6333): Vector database

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

## Configuration

### Changing the Language Model

The default model is `gemma3:1b`. To use a different model:

**Option 1: Change in entrypoint.sh**
Edit `ollama/entrypoint.sh` and change line 9:
```bash
ollama pull gemma3:12b  # or any other model
```

**Option 2: Manually pull model after startup**
```bash
# After docker-compose up, pull a different model
docker exec -it ollama ollama pull gemma3:12b
docker exec -it ollama ollama pull llama3:8b
docker exec -it ollama ollama pull mistral:7b
```

### Environment Variables
Create a `.env` file to customize settings:
```env
LLM_MODEL=gemma3:12b
EMB_MODEL=l3cube-pune/bengali-sentence-similarity-sbert
```

**Note**: Make sure the `LLM_MODEL` in your `.env` file matches the model you pulled in ollama.

## Stopping the System

```bash
docker-compose down
