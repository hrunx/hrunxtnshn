# Deployment Guide

This guide covers deploying the hrunxtnshn extension and orchestrator for different use cases.

## Table of Contents

1. [Extension Deployment](#extension-deployment)
2. [Orchestrator Deployment](#orchestrator-deployment)
3. [Platform Integration](#platform-integration)
4. [GitHub Repository Setup](#github-repository-setup)

## Extension Deployment

### Local Development

1. **Load unpacked extension in Chrome**:
   ```bash
   # Open Chrome
   chrome://extensions/
   
   # Enable Developer mode (toggle in top right)
   # Click "Load unpacked"
   # Select the "extension" directory
   ```

2. **Configure settings**:
   - Click extension icon
   - Click "Settings"
   - Choose integration mode
   - Enter API credentials
   - Save and test connection

### Chrome Web Store (Future)

To publish to Chrome Web Store:

1. Create a developer account at https://chrome.google.com/webstore/devconsole
2. Package the extension:
   ```bash
   cd extension
   zip -r hrunxtnshn.zip *
   ```
3. Upload to Chrome Web Store
4. Fill in store listing details
5. Submit for review

## Orchestrator Deployment

### Local Development

```bash
cd orchestrator
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your OpenAI API key
python main.py
```

### Production Server

#### Using systemd (Linux)

1. Create service file `/etc/systemd/system/hrunxtnshn.service`:
   ```ini
   [Unit]
   Description=hrunxtnshn Orchestrator
   After=network.target

   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/hrunxtnshn/orchestrator
   Environment="PATH=/path/to/venv/bin"
   EnvironmentFile=/path/to/hrunxtnshn/orchestrator/.env
   ExecStart=/path/to/venv/bin/python main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

2. Enable and start:
   ```bash
   sudo systemctl enable hrunxtnshn
   sudo systemctl start hrunxtnshn
   sudo systemctl status hrunxtnshn
   ```

#### Using Docker

1. Create `Dockerfile` in orchestrator directory:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["python", "main.py"]
   ```

2. Build and run:
   ```bash
   cd orchestrator
   docker build -t hrunxtnshn-orchestrator .
   docker run -d -p 8000:8000 --env-file .env --name hrunxtnshn hrunxtnshn-orchestrator
   ```

3. With docker-compose:
   ```yaml
   version: '3.8'
   services:
     orchestrator:
       build: ./orchestrator
       ports:
         - "8000:8000"
       env_file:
         - ./orchestrator/.env
       restart: unless-stopped
   ```

#### Cloud Deployment

##### Heroku

1. Create `Procfile` in orchestrator directory:
   ```
   web: python main.py
   ```

2. Deploy:
   ```bash
   heroku create hrunxtnshn-orchestrator
   heroku config:set OPENAI_API_KEY=your-key
   git push heroku master
   ```

##### AWS EC2

1. Launch EC2 instance (Ubuntu 22.04)
2. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install python3.11 python3-pip git
   ```
3. Clone repository and setup
4. Use systemd service (see above)
5. Configure security group to allow port 8000

##### DigitalOcean App Platform

1. Connect GitHub repository
2. Select orchestrator directory
3. Set environment variables
4. Deploy

### Nginx Reverse Proxy (Production)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable HTTPS with Let's Encrypt:
```bash
sudo certbot --nginx -d your-domain.com
```

## Platform Integration

### Gasable Hub Integration

1. **Register extension with Gasable Hub**:
   - Get API endpoint from Gasable Hub dashboard
   - Generate API key
   - Configure extension with endpoint and key

2. **Extension configuration**:
   ```json
   {
     "mode": "platform",
     "platform": {
       "type": "gasable",
       "endpoint": "https://api.gasablehub.com/agent",
       "apiKey": "your-api-key"
     }
   }
   ```

### Leadora Integration

Similar to Gasable Hub:

1. Get Leadora API credentials
2. Configure extension with Leadora endpoint
3. Test connection

## GitHub Repository Setup

### Initial Setup

The repository has been initialized locally. To upload to GitHub:

```bash
# Authenticate with GitHub
gh auth login

# Run upload script
./upload_to_github.sh
```

Or manually:

```bash
# Create repository on GitHub
gh repo create hrunxtnshn --private --description="Invisible autonomous research assistant"

# Add remote and push
git remote add origin https://github.com/hrunx/hrunxtnshn.git
git branch -M main
git push -u origin main
```

### Repository Settings

1. **Branch Protection**:
   - Require pull request reviews
   - Require status checks
   - Restrict who can push to main

2. **Secrets** (for CI/CD):
   - `OPENAI_API_KEY`: For testing
   - `CHROME_EXTENSION_ID`: For extension updates

3. **Topics/Tags**:
   - browser-extension
   - chrome-extension
   - autonomous-agent
   - web-scraping
   - langgraph
   - fastapi

### CI/CD with GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test-orchestrator:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd orchestrator
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd orchestrator
          python -m pytest tests/
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Security Considerations

### API Keys

- Never commit API keys to repository
- Use environment variables
- Rotate keys regularly
- Use different keys for dev/prod

### Extension Security

- Validate all user inputs
- Sanitize extracted data
- Use HTTPS for all API calls
- Implement rate limiting

### Orchestrator Security

- Enable API key authentication in production
- Use HTTPS (SSL/TLS)
- Implement request validation
- Set up CORS properly
- Monitor for unusual activity

## Monitoring

### Orchestrator Logs

```bash
# View systemd logs
sudo journalctl -u hrunxtnshn -f

# View Docker logs
docker logs -f hrunxtnshn
```

### Health Checks

```bash
# Check orchestrator health
curl http://localhost:8000/health

# Check extension connection
curl http://localhost:8000/
```

## Troubleshooting

### Extension not connecting to orchestrator

1. Check orchestrator is running
2. Verify endpoint URL in extension settings
3. Check CORS configuration
4. Check firewall rules

### Orchestrator errors

1. Check logs for error messages
2. Verify OpenAI API key is valid
3. Check Python dependencies are installed
4. Verify port 8000 is not in use

### Performance issues

1. Increase `MAX_CONCURRENT_TASKS` in .env
2. Use faster LLM model (gpt-4.1-nano)
3. Optimize extraction schemas
4. Add caching layer

## Backup and Recovery

### Backup

```bash
# Backup configuration
cp orchestrator/.env orchestrator/.env.backup

# Backup extension settings
# Settings are stored in Chrome sync storage
```

### Recovery

```bash
# Restore configuration
cp orchestrator/.env.backup orchestrator/.env

# Restart orchestrator
sudo systemctl restart hrunxtnshn
```

## Scaling

### Horizontal Scaling

1. Deploy multiple orchestrator instances
2. Use load balancer (Nginx, HAProxy)
3. Share task queue (Redis, RabbitMQ)
4. Implement session affinity

### Vertical Scaling

1. Increase server resources
2. Optimize Python code
3. Use faster LLM models
4. Implement caching

## Support

For deployment issues:
- GitHub Issues: https://github.com/hrunx/hrunxtnshn/issues
- Documentation: https://github.com/hrunx/hrunxtnshn/wiki
