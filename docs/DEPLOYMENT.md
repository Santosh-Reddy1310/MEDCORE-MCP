# MedCore MCP - Production Deployment Guide

## 🚀 Quick Production Deployment

### 1. Prerequisites
- Python 3.8+
- Groq API Key ([Get one here](https://console.groq.com/keys))

### 2. Environment Setup

```bash
# Clone or extract the project
cd medcore-mcp

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Database Initialization

The database auto-initializes on first run, but you can also manually initialize:

```bash
python db/setup_db.py
```

### 4. Run the Application

```bash
streamlit run app.py
```

The app will be available at: `http://localhost:8501`

## 🌐 Deployment Platforms

### Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Settings → Secrets:
   ```toml
   GROQ_API_KEY = "your_key_here"
   ```
5. Deploy!

### Heroku Deployment

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create your-app-name
heroku config:set GROQ_API_KEY=your_key_here
git push heroku main
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | *required* | Your Groq API key |
| `MODEL` | `llama-3.3-70b-versatile` | Groq model to use |
| `DB_AUTO_INIT` | `true` | Auto-initialize database |
| `MCP_TIMEOUT` | `30` | MCP server timeout (seconds) |
| `MCP_MAX_RETRIES` | `3` | Max retry attempts |
| `ENVIRONMENT` | `production` | Environment mode |
| `DEBUG` | `false` | Enable debug mode |

## 🔧 Troubleshooting

### Database Issues

If database is corrupted or missing:
```bash
rm db/hospital.db
python db/setup_db.py
```

### MCP Server Not Connecting

1. Check database exists: `ls db/hospital.db`
2. Verify Python path: `which python`
3. Test MCP server: `python server/hospital_server.py`

### API Key Issues

Verify your `.env` file:
```bash
cat .env  # or type .env on Windows
```

Should contain:
```
GROQ_API_KEY=gsk_...
```

## 📊 Health Checks

### Database Status
```bash
python utils/db_init.py
```

### Configuration Check
```bash
python utils/config.py
```

### Full System Test
```bash
python health_check.py
```

## 🔒 Security Best Practices

1. **Never commit `.env` files** - Already in `.gitignore`
2. **Use environment secrets** in production platforms
3. **Rotate API keys** regularly
4. **Enable HTTPS** in production
5. **Set strong database permissions**

## 📈 Monitoring

Monitor application health:
- Check Streamlit logs for errors
- Monitor Groq API usage in console
- Track database size growth
- Set up uptime monitoring

## 🆘 Support

If you encounter issues:

1. Check logs: Streamlit shows errors in the UI
2. Run health checks: `python utils/config.py`
3. Verify database: `python utils/db_init.py`
4. Test MCP server: `python -c "from client.ai_client import ask_sync; print(ask_sync('test'))"`

## 📝 Production Checklist

- [ ] Environment variables configured
- [ ] Database initialized and populated
- [ ] API key valid and working
- [ ] Application runs locally
- [ ] Error handling tested
- [ ] Security best practices followed
- [ ] Monitoring set up
- [ ] Backup strategy in place

## 🎯 Performance Tips

1. **Database**: SQLite is fast for read operations
2. **MCP Server**: Adjust `MCP_TIMEOUT` based on your needs
3. **Caching**: Streamlit caches responses automatically
4. **Scaling**: For high traffic, consider PostgreSQL migration

---

**Ready for Production** ✅

The application is now fully configured for production deployment with:
- Auto-initialization
- Comprehensive error handling
- Retry logic and timeouts
- Environment-based configuration
- Production-ready defaults
