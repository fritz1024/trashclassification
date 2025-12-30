# Backend Scripts

This directory contains utility scripts for database initialization, data migration, and system maintenance.

## Scripts Overview

### 1. init_db.py
**Purpose:** Initialize the database schema and create tables

**Usage:**
```bash
python scripts/init_db.py
```

**Description:**
- Creates all database tables based on SQLAlchemy models
- Should be run once when setting up a new environment
- Safe to run multiple times (won't duplicate data)

---

### 2. init_rag.py
**Purpose:** Initialize the RAG (Retrieval-Augmented Generation) knowledge base

**Usage:**
```bash
python scripts/init_rag.py
```

**Description:**
- Sets up the vector database for RAG functionality
- Loads initial knowledge base documents
- Configures embeddings and indexing
- Required for AI chat features

**Prerequisites:**
- Database must be initialized first
- ChromaDB or vector database must be configured
- API keys for embedding models must be set in .env

---

### 3. migrate_knowledge.py
**Purpose:** Migrate knowledge base data between different formats or versions

**Usage:**
```bash
python scripts/migrate_knowledge.py
```

**Description:**
- Migrates knowledge base documents to new format
- Updates vector embeddings if needed
- Useful when upgrading RAG system or changing embedding models

---

### 4. update_categories.py
**Purpose:** Update garbage classification categories in the database

**Usage:**
```bash
python scripts/update_categories.py
```

**Description:**
- Updates classification categories from data files
- Synchronizes category data with the latest model
- Should be run after updating the ML model

---

## Execution Order

For a fresh installation, run scripts in this order:

1. `init_db.py` - Initialize database
2. `update_categories.py` - Load classification categories
3. `init_rag.py` - Initialize RAG knowledge base (optional)
4. `migrate_knowledge.py` - Only if migrating from old system

## Notes

- All scripts should be run from the backend root directory
- Ensure .env file is configured before running
- Check logs/ directory for execution logs
- Backup database before running migration scripts
