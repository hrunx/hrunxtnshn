# hrunxtnshn

**Invisible autonomous research assistant running inside your browser**

A complete, deployable autonomous-browsing extension with multiple integration modes, including standalone OpenAI API support, platform integration (Leadora/Gasable Hub), and a custom Python orchestrator backend using LangGraph.

## Features

### Browser Extension
- **Manifest V3** compatible Chrome extension
- **Invisible browsing** using Chrome offscreen API
- **Authenticated requests** using browser session cookies
- **Data extraction** from LinkedIn, Instagram, and Google Maps
- **Multiple integration modes**:
  - Standalone with OpenAI API
  - Platform integration (Leadora/Gasable Hub)
  - Custom Python orchestrator

### Python Orchestrator
- **LangGraph agent** for autonomous task planning
- **FastAPI backend** with async support
- **Task queue** for concurrent processing
- **Streaming API** for real-time updates
- **Fully local** and self-contained

## Project Structure

```
hrunxtnshn/
├── extension/              # Browser extension
│   ├── manifest.json
│   ├── background/         # Service worker
│   ├── offscreen/          # Invisible browsing
│   ├── content/            # Content scripts
│   ├── ui/                 # User interface
│   └── utils/              # Utilities
├── orchestrator/           # Python backend
│   ├── main.py
│   ├── agent/              # LangGraph agent
│   ├── api/                # FastAPI routes
│   ├── services/           # Services
│   └── utils/              # Utilities
├── backend/                # Node.js backend (optional)
├── portal-integration/     # Next.js integration examples
└── docs/                   # Documentation
```

## Quick Start

### 1. Install Browser Extension

```bash
# Clone repository
git clone https://github.com/hrunx/hrunxtnshn.git
cd hrunxtnshn

# Load extension in Chrome
# 1. Open chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select the "extension" directory
```

### 2. Configure Standalone Mode (Recommended for Testing)

1. Click the extension icon in Chrome toolbar
2. Click "Settings"
3. Select "Standalone (OpenAI API)" mode
4. Enter your OpenAI API key
5. Save settings and test connection

### 3. Test the Extension

1. Click the extension icon
2. Enter a task, for example:
   ```
   Extract data from LinkedIn profile https://linkedin.com/in/example
   ```
3. Click "Execute Task"
4. View the extracted data

### 4. (Optional) Run Python Orchestrator

```bash
# Navigate to orchestrator directory
cd orchestrator

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# Start server
python main.py
```

Then configure the extension to use orchestrator mode with endpoint `http://localhost:8000`.

## Integration Modes

### Standalone Mode

**Best for**: Testing, individual use, simple tasks

- Direct OpenAI API integration
- No backend required
- Configure API key in extension settings
- Instant setup

### Platform Mode

**Best for**: Integration with existing orchestrator platforms

- Connect to Leadora or Gasable Hub
- Shared authentication and task management
- Platform-managed agent infrastructure
- Configure platform endpoint and API key

### Orchestrator Mode

**Best for**: Full control, advanced use cases, local deployment

- Custom Python backend using LangGraph
- Run locally or deploy to server
- Full control over agent behavior
- Configurable LLM and parameters

## Documentation

- [Extension README](extension/README.md) - Extension installation and usage
- [Orchestrator README](orchestrator/README.md) - Python backend setup and API
- [Architecture Design](docs/architecture.md) - System architecture and design decisions

## Use Cases

### Data Extraction
- Extract LinkedIn profiles for lead generation
- Scrape Instagram profiles for social media analysis
- Collect Google Maps reviews for market research

### Research Automation
- Gather information from multiple sources
- Monitor competitor websites
- Track product prices and availability

### Testing & QA
- Automated website testing
- Form submission testing
- User flow validation

## Privacy & Security

- **No data collection**: Extension doesn't collect or transmit personal data
- **Local processing**: All extraction happens in your browser
- **Encrypted storage**: API keys stored in Chrome's encrypted storage
- **User consent**: Explicit permission required for invisible browsing
- **Session isolation**: Offscreen browsing isolated from main browser

## Requirements

### Browser Extension
- Chrome 109+ or Edge 109+
- Manifest V3 support

### Python Orchestrator
- Python 3.11+
- OpenAI API key

## Development

### Extension Development

```bash
cd extension
# Make changes to code
# Reload extension in chrome://extensions/
```

### Orchestrator Development

```bash
cd orchestrator
pip install -r requirements.txt
python main.py
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

For issues, questions, or feature requests:
- GitHub Issues: https://github.com/hrunx/hrunxtnshn/issues
- Documentation: https://github.com/hrunx/hrunxtnshn/wiki

## Roadmap

- [ ] WebSocket support for real-time extension-orchestrator communication
- [ ] More extractors (Twitter, Facebook, Reddit)
- [ ] Browser automation (form filling, clicking)
- [ ] Multi-tab orchestration
- [ ] Visual workflow builder
- [ ] Chrome Web Store publication

## Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent workflow
- [FastAPI](https://fastapi.tiangolo.com/) - Python web framework
- [Chrome Extensions API](https://developer.chrome.com/docs/extensions/) - Browser extension platform

## Author

Created by hrunx

---

**Note**: This extension is for educational and research purposes. Always respect website terms of service and robots.txt when using automated browsing tools.
