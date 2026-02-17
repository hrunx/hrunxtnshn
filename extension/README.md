# hrunxtnshn Browser Extension

Invisible autonomous research assistant running inside your browser.

## Features

- **Invisible Browsing**: Uses Chrome offscreen API for background web navigation
- **Data Extraction**: Extract structured data from LinkedIn, Instagram, and Google Maps
- **Authenticated Requests**: Uses your browser session cookies
- **Multiple Integration Modes**:
  - **Standalone**: Direct OpenAI API integration
  - **Platform**: Connect to Leadora or Gasable Hub
  - **Orchestrator**: Custom Python backend

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/hrunx/hrunxtnshn.git
   cd hrunxtnshn/extension
   ```

2. Open Chrome and navigate to `chrome://extensions/`

3. Enable "Developer mode" (toggle in top right)

4. Click "Load unpacked" and select the `extension` directory

5. The extension icon should appear in your toolbar

## Configuration

### Standalone Mode (Recommended for Testing)

1. Click the extension icon
2. Click "Settings"
3. Select "Standalone (OpenAI API)" mode
4. Enter your OpenAI API key
5. Choose a model (default: gpt-4.1-mini)
6. Click "Save Settings"
7. Click "Test Connection" to verify

### Platform Mode

1. Select "Platform (Leadora/Gasable)" mode
2. Choose your platform (Gasable Hub or Leadora)
3. Enter the platform API endpoint
4. Enter your platform API key
5. Save and test connection

### Orchestrator Mode

1. Start the Python orchestrator backend (see `../orchestrator/README.md`)
2. Select "Custom Orchestrator" mode
3. Enter the orchestrator endpoint (default: `http://localhost:8000`)
4. Optionally enter an API key if authentication is enabled
5. Save and test connection

## Usage

### Basic Task Execution

1. Click the extension icon
2. Enter a task description, for example:
   - "Extract data from LinkedIn profile https://linkedin.com/in/example"
   - "Get reviews from Google Maps place https://maps.google.com/..."
   - "Extract Instagram profile data from https://instagram.com/username"
3. Click "Execute Task"
4. View the extracted data in the result panel

### Advanced Usage

The extension can execute complex multi-step tasks when using AI planning:

```
Find the top 5 restaurants in San Francisco on Google Maps and extract their:
- Name
- Rating
- Address
- Phone number
- Recent reviews
```

## Permissions

The extension requires the following permissions:

- **tabs**: Navigate and interact with browser tabs
- **cookies**: Access session cookies for authenticated requests
- **scripting**: Inject content scripts for data extraction
- **offscreen**: Create invisible browsing context
- **storage**: Store configuration settings
- **activeTab**: Access currently active tab
- **identity**: OAuth authentication (future feature)
- **geolocation**: Location-based features (future feature)

## Privacy & Security

- **No data collection**: The extension does not collect or transmit your personal data
- **Local processing**: All data extraction happens locally in your browser
- **Secure storage**: API keys are stored in Chrome's encrypted storage
- **Session isolation**: Offscreen browsing is isolated from your main browser
- **User consent**: Explicit permission required for invisible browsing

## Troubleshooting

### "Not configured" status

- Make sure you've entered your API key in Settings
- Test the connection to verify credentials

### "Connection error"

- Check your internet connection
- Verify the API endpoint is correct
- For orchestrator mode, ensure the backend is running

### Extraction fails

- Make sure you're logged in to the target website
- Some websites may block automated access
- Try loading the page manually first

### Permission denied

- Click "Approve" when prompted for offscreen browsing permission
- You can revoke this permission at any time in Settings

## Development

### Project Structure

```
extension/
├── manifest.json           # Extension manifest
├── background/             # Background service worker
│   ├── background.js       # Main entry point
│   ├── taskRouter.js       # Task routing
│   ├── apiClient.js        # API client
│   ├── fetchEngine.js      # Authenticated fetch
│   ├── offscreenController.js  # Offscreen management
│   └── extractorRouter.js  # Extraction routing
├── offscreen/              # Offscreen document
│   ├── offscreen.html
│   └── offscreen.js
├── content/                # Content scripts (future)
├── ui/                     # User interface
│   ├── popup.html          # Extension popup
│   ├── popup.js
│   ├── settings.html       # Settings page
│   ├── settings.js
│   ├── permissionPrompt.html
│   └── styles.css
└── utils/                  # Utilities
    ├── config.js           # Configuration manager
    ├── schemaMaps.js       # Maps extraction schema
    ├── schemaLinkedIn.js   # LinkedIn extraction schema
    ├── schemaInstagram.js  # Instagram extraction schema
    └── safeJSON.js         # JSON utilities
```

### Building

The extension is vanilla JavaScript and doesn't require a build step. Just load it unpacked in Chrome.

### Testing

1. Load the extension in Chrome
2. Open the extension popup
3. Configure standalone mode with your API key
4. Test with a simple extraction task
5. Check the browser console for logs

## License

MIT License - see LICENSE file for details

## Support

For issues and feature requests, please visit:
https://github.com/hrunx/hrunxtnshn/issues
