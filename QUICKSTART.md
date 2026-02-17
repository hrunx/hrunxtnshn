# Quick Start Guide

Get started with hrunxtnshn in 5 minutes!

## Prerequisites

- Chrome 109+ or Edge 109+
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## Installation (3 steps)

### Step 1: Download

```bash
# Clone the repository
git clone https://github.com/hrunx/hrunxtnshn.git
cd hrunxtnshn
```

Or download the archive and extract it.

### Step 2: Load Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top right corner)
3. Click **Load unpacked**
4. Select the `extension` folder from the downloaded repository
5. The hrunxtnshn icon should appear in your toolbar

### Step 3: Configure

1. Click the **hrunxtnshn icon** in your toolbar
2. Click **Settings**
3. Select **Standalone (OpenAI API)** mode
4. Enter your **OpenAI API key**
5. Select model: **gpt-4.1-mini** (recommended)
6. Click **Save Settings**
7. Click **Test Connection** to verify

✅ You're ready to go!

## First Task

Let's test with a simple task:

1. Click the **hrunxtnshn icon**
2. In the task field, enter:
   ```
   What is 2+2? Just respond with the number.
   ```
3. Click **Execute Task**
4. You should see the result: `4`

## Real-World Example

Now let's try something more useful:

### Extract LinkedIn Profile

**Prerequisites**: You must be logged into LinkedIn in your browser

1. Find a LinkedIn profile URL, for example:
   ```
   https://www.linkedin.com/in/example
   ```

2. In the extension popup, enter:
   ```
   Extract data from LinkedIn profile https://www.linkedin.com/in/example
   ```

3. Click **Execute Task**

4. The extension will:
   - Load the profile invisibly in the background
   - Extract structured data (name, headline, experience, education)
   - Return the results

5. View the extracted data in the result panel

### Extract Google Maps Place

1. Find a Google Maps place URL:
   ```
   https://www.google.com/maps/place/Eiffel+Tower
   ```

2. Enter task:
   ```
   Extract data from Google Maps place https://www.google.com/maps/place/Eiffel+Tower
   ```

3. Get structured data including:
   - Name, rating, reviews
   - Address, phone, website
   - Hours, category
   - Recent reviews

## Advanced: Run Your Own Backend

Want full control? Run the Python orchestrator locally:

### Setup (5 minutes)

1. **Install Python dependencies**:
   ```bash
   cd orchestrator
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key:
   # OPENAI_API_KEY=sk-your-key-here
   ```

3. **Start the server**:
   ```bash
   python main.py
   ```
   
   You should see:
   ```
   Starting hrunxtnshn orchestrator...
   OpenAI Model: gpt-4.1-mini
   Server: 0.0.0.0:8000
   Agent initialized
   Task queue processor started
   Orchestrator ready!
   ```

4. **Configure extension**:
   - Open extension settings
   - Select **Custom Orchestrator** mode
   - Enter endpoint: `http://localhost:8000`
   - Save and test connection

5. **Test it**:
   - Execute a task in the extension
   - The orchestrator will process it with full AI planning

## Common Tasks

### Research Task
```
Research the history of the Eiffel Tower and tell me:
1. When it was built
2. Who designed it
3. How tall it is
```

### Data Collection
```
Find the top-rated restaurant in San Francisco on Google Maps and extract:
- Name
- Rating
- Address
- Phone number
- Recent reviews
```

### Profile Analysis
```
Extract Instagram profile data from https://www.instagram.com/natgeo
```

## Tips

1. **Be specific**: More detailed prompts yield better results
2. **Check login**: Ensure you're logged into websites before extracting data
3. **Wait for results**: Complex tasks may take 10-30 seconds
4. **Check errors**: If something fails, read the error message carefully

## Troubleshooting

### "Not configured" status
- Make sure you entered your API key in Settings
- Click "Test Connection" to verify

### "Connection error"
- Check your internet connection
- Verify your API key is valid
- For orchestrator mode, ensure the backend is running

### Extraction fails
- Make sure you're logged into the target website
- Try loading the page manually first
- Check the browser console for errors

### "Extension not connected" (orchestrator mode)
- Verify the orchestrator is running: `curl http://localhost:8000/health`
- Check the endpoint URL in extension settings
- Make sure there's no firewall blocking port 8000

## Next Steps

- Read the [full documentation](README.md)
- Check out [usage examples](EXAMPLES.md)
- Learn about [deployment options](DEPLOYMENT.md)
- Explore the [testing guide](TESTING.md)

## Need Help?

- **Documentation**: Check the README and guides
- **Issues**: Report bugs on GitHub Issues
- **Examples**: See EXAMPLES.md for more use cases

## Limits & Best Practices

- **Rate limiting**: Wait 2-3 seconds between requests to the same website
- **API costs**: Monitor your OpenAI API usage
- **Privacy**: Always respect website terms of service
- **Login required**: Some extractions require being logged in

---

**Congratulations!** You're now ready to use hrunxtnshn for autonomous browsing and data extraction. Start with simple tasks and gradually explore more complex use cases.

Happy browsing! 🚀
