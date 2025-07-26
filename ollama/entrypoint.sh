#!/bin/bash
ollama serve &

until curl -s http://localhost:11434/api/tags > /dev/null; do
  echo "Waiting for Ollama..."
  sleep 2
done

ollama pull gemma3:12b # Change the model if you want to pull the other model while startup

wait