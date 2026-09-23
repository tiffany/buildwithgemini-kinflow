import sys
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
import vertexai

PROJECT_ID = "qwiklabs-gcp-04-b99c507c7b84"
LOCATION   = "us-central1"
GCS_PATH   = "gs://kinflow-media-qwiklabs-gcp-04-b99c507c7b84/rag/"

PARSING_PROMPT = (
    "Extract the individual useful clinical facts, emergency protocols, and insurance guidelines described in this text. "
    "Ignore and omit all metadata and boilerplate. "
    "Output clean, self-contained care coordination guidance."
)

print(f"Initializing Vertex AI in {LOCATION}...")
vertexai.init(project=PROJECT_ID, location=LOCATION)

print("1. Updating RAG Engine config to Serverless mode...")
cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
rag.update_rag_engine_config(rag_engine_config=rag.RagEngineConfig(
    name=cfg,
    rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
))
print("Serverless mode confirmed.")

print("2. Creating RAG corpus...")
corpus = rag.create_corpus(
    display_name="kinflow-care-guidance",
    embedding_model_config=rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-005"),
)
print("CORPUS_NAME:", corpus.name)

print("3. Importing, parsing, chunking, and embedding documents...")
resp = rag.import_files(
    corpus_name=corpus.name,
    paths=[GCS_PATH],
    transformation_config=rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)),
    llm_parser=rag.LlmParserConfig(
        model_name="gemini-3.6-flash",
        custom_parsing_prompt=PARSING_PROMPT),
)
print(f"Import complete! Imported {resp.imported_rag_files_count} files.")
