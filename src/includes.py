'''Module to define constants and config functions for the project'''
import os
from pathlib import Path

ROOT_DIR = os.path.abspath(Path(__file__).parent.parent)


# Corpus, mappings, samples
DATA_DIR = ROOT_DIR + "/data"
CORPUS_BASE = DATA_DIR + "/corpus"
HIPAAIMPL_CORPUS = CORPUS_BASE + "/NIST.SP.800-66r2r2"
SCHEMA_BASE = DATA_DIR + "/graphdb"

OPENAI_API_KEY = os.environ.get("OPEN_API_SECRET")
