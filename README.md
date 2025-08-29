# 🔍 LICENSEER - Knowledge Graph and LLM-based License Compatibility Framework

> **A Knowledge Graph and LLM-based Framework for Automated License Compatibility Detection**

## 📋 Project Overview

LICENSEER is an AI-powered tool that helps developers understand license compatibility between open-source packages using a sophisticated combination of Knowledge Graphs, Large Language Models (LLMs), and Retrieval-Augmented Generation (RAG).

### 🎯 Problem Statement

Modern software depends heavily on open-source components, with **72.91%** of OSS projects encountering license incompatibilities. These incompatibilities lead to:
- **Legal Liability** - Violations of copyleft requirements
- **Restricted Distribution** - Preventing lawful distribution  
- **Complex Compliance** - Difficult to track and reconcile licensing

Traditional methods are inadequate due to:
- Over 200 recognized licenses (OSI and SPDX)
- Nuanced, version-specific differences (e.g., GPLv2 vs. GPLv3)
- Need for continuous updates

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Query   │───▶│  LLM Parser    │───▶│ Knowledge Graph │
│                │    │  (GPT-4)       │    │   (Neo4j)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   RAG System   │    │ Compatibility   │
                       │ (FAISS + LLM)  │    │   Checker      │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Structured    │    │  Detailed      │
                       │   Response     │    │ Explanation    │
                       └─────────────────┘    └─────────────────┘
```

## 🧠 Core Components

### 1. Knowledge Graph Construction
Using Neo4j to store:
- **Licenses**: Nodes for licenses (MIT, GPLv3, Apache-2.0) with version details
- **Dependencies**: Each OSS dependency linked via `HAS_LICENSE` relationship
- **Terms**: Nodes for obligations with relationships: `REQUIRES`, `PROHIBITS`, `PERMITS`
- **Compatibility Edges**: `COMPATIBLE_WITH`/`INCOMPATIBLE_WITH` relationships

**Example Graph Structure:**
```
requests --[HAS_LICENSE]--> MIT --[REQUIRES]--> Attribution
Flask --[HAS_LICENSE]--> BSD --[COMPATIBLE_WITH]--> MIT
```

### 2. LLM-driven License Parsing
- **Scraping module** collects license texts
- **LLM (GPT-4)** parses texts to extract:
  - Obligations (what users MUST do)
  - Prohibitions (what users CANNOT do)
  - Permissions (what users CAN do)
  - Version-specific clauses
- **Key Advantage**: No retraining needed for new license types

### 3. RAG for Explainability
**Retrieval-Augmented Generation** provides:
- Embedding and indexing of official license texts
- Retrieving relevant license chunks for compatibility questions
- Generating context-rich explanations with citations

## 🚀 Key Features

- **Natural Language Queries**: Ask questions like "Are requests and urllib3 compatible?"
- **Real-time Compatibility Checking**: Instant analysis of license compatibility
- **Citation-backed Explanations**: RAG system provides source references
- **Continuous Learning**: Automatically adapts to new licenses
- **CI/CD Integration**: Fits into development workflows

## 📊 Performance Results

| Metric | LiDetector | LICENSEER (KG+RAG) | Improvement |
|--------|------------|-------------------|-------------|
| **Accuracy** | 93.2% | **97.4%** | +4.2% |
| **F1-Score** | 88.7% | **94.6%** | +5.9% |
| **False Positive Rate** | 10.1% | **5.3%** | -4.8% |
| **Context Understanding** | 78.3% | **96.5%** | +18.2% |
| **Compliance Detection** | 65% | **92%** | +27% |

### Key Improvements:
- **4.2%** higher license detection accuracy
- **5.9%** better conflict detection (F1)
- **4.8%** lower false positive rate
- **Explainability score**: 4.7/5 vs 3.2/5
- **71%** reduction in memory usage
- **7x** improvement in license update latency (1 day vs 7 days)
- **225%** more citations in explanations

## 🔬 Case Study: Elasticsearch + Lucene

**LiDetector Analysis:**
- Detects usage restrictions in Elastic License
- Identifies Apache 2.0 terms
- Flags potential incompatibility
- Lacks version-specific context

**LICENSEER KG+RAG Analysis:**
- Differentiates `Elastic License 2.0` from older versions
- Retrieves specific clauses (Section 4.2) via RAG
- Provides citations from license texts
- Suggests alternatives for compliance

## 🛠️ Technical Stack

- **Backend**: Python, FastAPI
- **Database**: Neo4j Graph Database
- **AI/ML**: OpenAI GPT-4, LangChain
- **Vector Database**: FAISS, ChromaDB
- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **License Data**: SPDX, OSI standards

## 🚀 How to Run the Project

### Prerequisites
- Python 3.8+
- Neo4j Aura account (or local Neo4j instance)
- OpenAI API key

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Licenseer_Project.git
   cd Licenseer_Project/src
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the `src` directory:
   ```env
   NEO4J_URI=neo4j+ssc://your-instance.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_neo4j_password
   NEO4J_DATABASE=neo4j
   OPENAI_API_KEY=sk-your_openai_api_key_here
   ```

4. **Initialize the Neo4j database (if needed)**
   ```bash
   cd ../PFE_Licenseer
   python -m src.main --init-db
   ```

5. **Run the Streamlit application**
   ```bash
   cd ../src
   streamlit run licenseer_app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

### Usage Examples

- **Simple Query**: "Are numpy and matplotlib compatible?"
- **Complex Query**: "Can I use Apache 2.0 licensed packages in my GPL-3.0 project?"
- **Package-Specific**: "What license conflicts exist with tensorflow and scikit-learn?"

## 📁 Project Structure & Code Explanation

```
src/
├── licenseer_app.py              # Main Streamlit application
├── license_compatibility_llm.py  # LLM orchestrator
├── license_rag.py               # RAG system implementation
├── license_compatibility_checker.py # Neo4j client
├── graph_builder.py             # Knowledge graph construction
├── data/
│   ├── licenses/                # License JSON files
│   ├── dependencies/            # Package dependency data
│   └── vector_db/              # Pre-built FAISS index
└── requirements.txt             # Python dependencies
```

### 🔍 Detailed Code Components

#### 1. `licenseer_app.py` - Main Streamlit Application
```python
# Primary user interface that handles:
# - User input through Streamlit chat interface
# - Session state management for conversation history
# - Integration with LLM compatibility checker
# - Response formatting and display

class LicenseerApp:
    def __init__(self):
        self.compatibility_checker = LicenseCompatibilityLLM()
    
    def process_query(self, user_input):
        # Processes natural language queries
        # Returns structured compatibility analysis
```

#### 2. `license_compatibility_llm.py` - LLM Orchestrator
```python
# Coordinates between different AI components:
# - OpenAI GPT-4 for natural language understanding
# - Neo4j for structured data retrieval
# - RAG system for contextual explanations

class LicenseCompatibilityLLM:
    def generate_response(self, user_input):
        # 1. Parse query using OpenAI
        # 2. Extract package names and licenses
        # 3. Query Neo4j for compatibility data
        # 4. Generate RAG-enhanced explanation
        # 5. Return comprehensive analysis
```

#### 3. `license_rag.py` - RAG System Implementation
```python
# Implements Retrieval-Augmented Generation:
# - Loads license texts from JSON files
# - Creates FAISS vector embeddings
# - Retrieves relevant license clauses
# - Provides contextual information for explanations

class LicenseRAG:
    def __init__(self):
        self.vector_store = self.load_or_create_vector_db()
        self.llm = OpenAI()
    
    def get_relevant_context(self, query):
        # Retrieves license clauses relevant to query
        # Returns citations and explanations
```

#### 4. `license_compatibility_checker.py` - Neo4j Client
```python
# Handles all Neo4j database operations:
# - Connection management with SSL
# - Cypher query execution
# - License and package data retrieval
# - Compatibility relationship queries

class LicenseCompatibilityChecker:
    def check_compatibility(self, package1, package2):
        # Executes Cypher queries to find:
        # - Package licenses
        # - Compatibility relationships
        # - Conflict indicators
```

#### 5. `graph_builder.py` - Knowledge Graph Construction
```python
# Builds the Neo4j knowledge graph:
# - Loads license and package data
# - Creates nodes and relationships
# - Establishes compatibility constraints
# - Populates graph database

class GraphBuilder:
    def build_graph(self):
        # 1. Create license nodes with properties
        # 2. Create package nodes with metadata
        # 3. Establish HAS_LICENSE relationships
        # 4. Define compatibility rules
```

### 🔄 Data Flow Architecture

```
User Query → Streamlit Interface → LLM Parser → Neo4j Query
     ↓              ↓                  ↓           ↓
Response ← RAG System ← Context Retrieval ← Compatibility Check
```

### 📊 Key Algorithms

#### License Compatibility Algorithm
```python
def check_compatibility(license1, license2):
    """
    1. Retrieve license obligations and permissions
    2. Check for conflicting requirements
    3. Evaluate copyleft implications
    4. Return compatibility score and reasoning
    """
```

#### RAG Context Retrieval
```python
def retrieve_context(query, top_k=3):
    """
    1. Embed user query using OpenAI embeddings
    2. Search FAISS vector database
    3. Retrieve top-k relevant license clauses
    4. Return ranked context with citations
    """
```

## ⚙️ Configuration Options

### Environment Variables
```env
# Neo4j Configuration
NEO4J_URI=neo4j+ssc://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# OpenAI Configuration
OPENAI_API_KEY=sk-your_api_key

# Optional: RAG Configuration
VECTOR_DB_PATH=./data/vector_db/
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Database Initialization
The system requires a populated Neo4j database. If starting fresh:

```bash
# Navigate to the PFE_Licenseer directory
cd ../PFE_Licenseer

# Initialize database with license and package data
python -m src.main --init-db

# Verify database connection
python -m src.test_neo4j
```

### Troubleshooting Common Issues

1. **Neo4j Connection Error**
   - Verify your credentials in `.env`
   - Check network connectivity
   - Ensure database is running

2. **Missing Dependencies**
   - Run `pip install -r requirements.txt` again
   - Check Python version compatibility

3. **Vector Database Issues**
   - Delete `data/vector_db/` folder to force rebuild
   - Verify license JSON files exist in `data/licenses/`

## 🔬 API Usage (Alternative Access)

For programmatic access, you can use the core components directly:

```python
from license_compatibility_llm import LicenseCompatibilityLLM

# Initialize the compatibility checker
checker = LicenseCompatibilityLLM()

# Check compatibility
result = checker.generate_response("Are MIT and GPL-3.0 compatible?")
print(result)
```

## 🌟 Innovation Highlights

1. **Hybrid Approach**: Combines rule-based and AI-driven analysis
2. **Dynamic Learning**: Automatically adapts to new license types
3. **Explainable AI**: Provides citations and reasoning for decisions
4. **Scalable Architecture**: Handles growing license ecosystem
5. **Real-time Processing**: Instant compatibility analysis

## 🔧 Development & Testing

### Running Tests
```bash
# Test Neo4j connection
python test_neo4j.py

# Test RAG system
python -c "from license_rag import LicenseRAG; rag = LicenseRAG(); print('RAG system initialized successfully')"

# Test full pipeline
python -c "from license_compatibility_llm import LicenseCompatibilityLLM; llm = LicenseCompatibilityLLM(); print(llm.generate_response('Test query'))"
```

### Adding New Licenses
1. Add license JSON file to `data/licenses/`
2. Update compatibility matrix if needed
3. Rebuild vector database: Delete `data/vector_db/` and restart app

## 🔮 Future Research Directions

- Domain-specific extensions (healthcare, automotive)
- Multi-modal analysis combining license text and code
- Temporal license evolution modeling
- Fine-tuned LLMs for legal license analysis
- Integration with package managers and CI/CD tools

## 📚 Academic Context

This project addresses the critical gap in open-source license management by combining:
- **Knowledge Graph Theory**: For relationship modeling
- **Natural Language Processing**: For license text understanding
- **Information Retrieval**: For context-aware explanations
- **Software Engineering**: For practical integration

## 🏆 Impact

LICENSEER represents a significant advancement in automated license compatibility detection, providing developers with:
- **Accurate** license analysis
- **Explainable** decision-making
- **Scalable** solution for growing OSS ecosystem
- **Practical** integration into development workflows

---

*Developed as part of the PFE (Projet de Fin d'Études) at Tunis Business School*
