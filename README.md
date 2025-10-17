

# # 🔍 Code Review Assistant

An AI-powered **Code Review Web Application** that analyzes uploaded source code using **Large Language Models (LLMs)** via the **OpenRouter API**, generates detailed feedback, and provides downloadable PDF reports.  
The system also supports multi-user authentication, report history tracking, and an admin dashboard.

---

🌐 **Live App:** [https://unthinkable-santhosh22bce3084.streamlit.app/](https://unthinkable-santhosh22bce3084.streamlit.app/)  
📦 **Repository:** [https://github.com/isanthosh2004/unthinkable_submission](https://github.com/isanthosh2004/unthinkable_submission)  
🎥 **Demo Video:** [Watch on Google Drive](https://drive.google.com/file/d/16rE-IeC6FqorXCXd6Yesl_tUlO-rmYbj/view?usp=sharing)

---

## ✨ Features

- 🧠 **AI-Powered Code Reviews** — Uses Qwen 2.5 Coder model via OpenRouter API  
- 📂 **Multi-File Uploads** — Supports major programming languages (Python, C++, Java, etc.)  
- 📊 **Complexity Graphs** — Visual time and space complexity using `matplotlib`  
- 🧾 **PDF Report Generation** — Generates professional reports with graphs and metadata  
- 🗄️ **SQLite Database** — Stores all reviews, files, and metadata  
- 🔐 **Role-Based Access** — Admin can view all reports; users can view only their own  
- 🧭 **Dashboard Interface** — Intuitive Streamlit UI for uploads, reports, and search  
- ☁️ **Streamlit Cloud Deployment** — Fully hosted, with secure API key management  


---
## Sample Deployed version

<img width="1903" height="932" alt="image" src="https://github.com/user-attachments/assets/b7c6171b-4c7a-4493-8e3b-df8ffb2c783a" />

--- 
## DFD 

![WhatsApp Image 2025-10-15 at 23 21 09_178440f7](https://github.com/user-attachments/assets/eab6eee7-b9d1-4590-868b-b7a2f58a2e95)

---


## 🏗 Architecture

```
Code Review Assistant/
├── app.py                 # Main Streamlit application
├── services/
│   ├── llm_client.py     # OpenRouter API integration
│   └── pdf_generator.py  # PDF report generation
├── db/
│   └── database.py       # SQLite database management
├── reports/              # Generated PDF reports storage
├── requirements.txt      # Python dependencies
├── env.example          # Environment configuration template
└── README.md            # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd Code-Review-Assistant

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your OpenRouter API key
OPENROUTER_API_KEY=your_actual_api_key_here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `DATABASE_PATH` | SQLite database file path | `db/code_reviews.db` |
| `REPORTS_DIRECTORY` | PDF reports storage directory | `reports` |
| `DEFAULT_MODEL` | LLM model to use | `qwen/qwen-2.5-coder-32b-instruct:free` |
| `MAX_TOKENS` | Maximum tokens for LLM response | `4000` |
| `TEMPERATURE` | LLM temperature setting | `0.3` |

### Supported File Types

- **Python**: `.py`
- **JavaScript**: `.js`
- **TypeScript**: `.ts`
- **C++**: `.cpp`, `.c`
- **Java**: `.java`
- **Go**: `.go`
- **Rust**: `.rs`
- **PHP**: `.php`
- **Ruby**: `.rb`
- **Swift**: `.swift`
- **Kotlin**: `.kt`

## 📋 Usage

### 1. Upload Files
- Navigate to the "Upload & Review" tab
- Select one or more code files
- Click "Start Code Review"

### 2. Review Process
- Files are sent to the LLM for analysis
- Progress is shown with a progress bar
- Review covers:
  - Code Quality & Readability
  - Modularity & Architecture
  - Potential Bugs
  - Security Issues
  - Performance Analysis
  - Best Practices
  - Improvement Suggestions

### 3. Download Reports
- PDF reports are automatically generated
- Download button appears after review completion
- Reports are stored in the `reports/` directory

### 4. View History
- Navigate to "Reports History" tab
- View all past reviews
- Search and filter reports
- Re-download PDF reports

## 🛠 API Integration

### OpenRouter Configuration

The application uses OpenRouter API with the following configuration:

```python
# Model: qwen/qwen-2.5-coder-32b-instruct:free
# Endpoint: https://openrouter.ai/api/v1/chat/completions
# Max Tokens: 4000
# Temperature: 0.3
```

### Customizing the LLM Prompt

Edit `services/llm_client.py` to modify the review prompt:

```python
def _build_review_prompt(self, file_contents):
    # Customize the prompt here
    prompt_parts = [
        "Your custom prompt here...",
        # ... rest of the prompt
    ]
    return "\n".join(prompt_parts)
```

## 📊 Database Schema

### Reports Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | Unique report identifier (UUID) |
| `files` | TEXT | Comma-separated list of reviewed files |
| `pdf_path` | TEXT | Path to generated PDF report |
| `review_content` | TEXT | Full review content (markdown) |
| `metadata` | TEXT | JSON metadata (tokens, model, etc.) |
| `created_at` | TIMESTAMP | Report creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

## 🔒 Security Considerations

- API keys are stored in environment variables
- File uploads are validated by extension
- Database uses parameterized queries to prevent SQL injection
- PDF files are stored locally (consider cloud storage for production)

## 🐛 Troubleshooting

### Common Issues

1. **"OPENROUTER_API_KEY environment variable is required"**
   - Ensure you've created a `.env` file with your API key
   - Check that the key is valid and has sufficient credits

2. **"Failed to initialize database"**
   - Ensure the `db/` directory exists and is writable
   - Check file permissions

3. **"PDF generation failed"**
   - Ensure the `reports/` directory exists and is writable
   - Check available disk space

4. **"Request timeout"**
   - The LLM request took too long
   - Try with smaller files or check your internet connection

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## 🚀 Production Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Add environment variables in the dashboard
4. Deploy

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Environment Variables for Production
- Set `OPENROUTER_API_KEY` in your deployment environment
- Configure `DATABASE_PATH` for persistent storage
- Set `REPORTS_DIRECTORY` for cloud storage integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Please check the license file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue with detailed error information

---

**Happy Code Reviewing! 🔍✨**


