from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai
from openai.embeddings_utils import cosine_similarity
import json
import os
import glob
import tiktoken
import numpy as np
import pandas as pd

# Get your key: https://platform.openai.com/account/api-keys
openai.api_key = 'YOUR-OAI-KEY'

# Define completion model, embedding model and encoding
COMPLETION_MODEL = 'text-davinci-003'
EMBEDDING_MODEL = 'text-embedding-ada-002'
EMBEDDING_ENCODING = 'cl100k_base'
EMBEDDING_CHUNK_SIZE = 8000

# initialize tiktoken for encoding text
encoding = tiktoken.get_encoding(EMBEDDING_ENCODING)

# Variables
current_directory = os.path.dirname(__file__)
groups_directory = os.path.join(current_directory, "groups")
group_files = glob.glob(os.path.join(groups_directory, "*.md"))

# read content field from each file and append it to documents, and remove and newlines (better for embeddings later)
documents = []
for gFile in group_files:
    print(f'[+] Reading {gFile}..')
    with open(gFile, "r", encoding="utf8") as f:
        content = json.dumps(json.load(f))
        content = content.replace("\n", " ")
        content = content.replace("  ", " ")
        documents.append(content)

# print some stats about the documents
print(f"Loaded {len(documents)} documents")
for doc in documents:
    num_tokens = len(encoding.encode(doc))
    print(f"Content: {doc[:80]}... \n---> Tokens: {num_tokens}\n")

# Create embeddings for all docs
embeddings = [openai.Embedding.create(input=doc, engine=EMBEDDING_MODEL)["data"][0]["embedding"] for doc in documents]

# print some stats about the embeddings
for e in embeddings:
    print(len(e))

# create embedding for question
question = "What are some similarities between NOBELIUM and GOLD CABIN groups?"
qe = openai.Embedding.create(input=question, engine=EMBEDDING_MODEL)["data"][0]["embedding"]

# calculate cosine similarity between question and each document
similaries = [cosine_similarity(qe, e) for e in embeddings]

# Get the matching document, in this case we just use argmax of similarities
max_i = np.argmax(similaries)

# print some stats about the similarities
for i, s in enumerate(similaries):
    print(f"Similarity to {group_files[i]} is {s}")
print(f"Matching document is {group_files[max_i]}")

# Generate a prompt that we use for completion, in this case we put the matched document and the question in the prompt
prompt = f""""
Content:
{documents[max_i]}
Please answer the question below using only the content from above. If you don't know the answer, say "I couldn't find the answer".
Question: {question}
Answer:"""

# get response from completion model
response = openai.Completion.create(
    engine=COMPLETION_MODEL,
    prompt=prompt,
    temperature=0.7,
    max_tokens=500,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None
)
answer = response['choices'][0]['text']

# print the question and answer
print(f"Question was: {question}\nRetrieved answer was: {answer}")