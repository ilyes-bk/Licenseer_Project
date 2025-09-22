# LARK Environment Setup

## 🔧 Environment Variables Configuration

All credentials and configuration are now managed through environment variables for security.

### 📋 Required Environment Variables

Create a `.env` file in the `src/` directory with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-openai-api-key-here

# Neo4j Configuration  
NEO4J_URI=neo4j+ssc://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-actual-neo4j-password
NEO4J_DATABASE=neo4j

# Optional: RAG Configuration
VECTOR_DB_PATH=./data/vector_db/
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 🚀 Quick Setup

1. **Copy the template:**
   ```bash
   cp src/env_template.txt src/.env
   ```

2. **Edit `.env` with your actual credentials:**
   ```bash
   nano src/.env
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   streamlit run licenseer_app.py
   ```

### 🔒 Security Notes

- **Never commit `.env` files** to version control
- **Use strong, unique passwords** for all services
- **Rotate API keys regularly**
- **Use environment-specific configurations** for different deployments

### 🐛 Troubleshooting

If you get errors about missing credentials:

1. **Check your `.env` file exists** in the `src/` directory
2. **Verify all required variables are set** (no empty values)
3. **Ensure no extra spaces** around the `=` signs
4. **Restart your application** after changing environment variables

### 📝 Example `.env` File

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz

# Neo4j Configuration
NEO4J_URI=neo4j+ssc://abc123def.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=MySecurePassword123!
NEO4J_DATABASE=neo4j
```

### 🌐 Deployment

For production deployments:

- **Streamlit Cloud**: Add secrets in the dashboard
- **Docker**: Use `--env-file .env` or environment variables
- **Kubernetes**: Use ConfigMaps and Secrets
- **Cloud Platforms**: Use their secret management services

### ✅ Verification

Test your setup:

```bash
# Test Neo4j connection
python test_connection.py

# Test OpenAI API
python simple_license_parser.py
```

Both should work without hardcoded credentials!
