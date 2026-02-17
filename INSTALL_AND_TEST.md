# Installation and Testing Guide

## Quick Start: Test the Extension in 5 Minutes

### Step 1: Install the Extension

1. **Open Chrome** and navigate to:
   ```
   chrome://extensions/
   ```

2. **Enable Developer Mode**
   - Look for the toggle in the top right corner
   - Turn it ON

3. **Load the Extension**
   - Click "Load unpacked"
   - Navigate to the `hrunxtnshn/extension` folder
   - Click "Select Folder"

4. **Verify Installation**
   - You should see "hrunxtnshn" in your extensions list
   - The extension icon should appear in your Chrome toolbar
   - Status should show "Enabled"

### Step 2: Test LinkedIn Employee Extraction

#### Prerequisites
- You must be logged into LinkedIn in your Chrome browser
- If not logged in, go to https://linkedin.com and log in first

#### Test Procedure

1. **Navigate to Gasable's LinkedIn People Page**
   ```
   https://www.linkedin.com/company/gasable/people/
   ```

2. **Open Browser Console** (to see extraction logs)
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Press `Cmd+Option+I` (Mac)
   - Go to the "Console" tab

3. **Verify Content Script Loaded**
   - You should see in the console:
     ```
     [hrunxtnshn] LinkedIn extractor loaded on: https://www.linkedin.com/company/gasable/people/
     [hrunxtnshn] LinkedIn extractor ready
     ```

4. **Test Extraction via Console**
   - In the console, paste and run:
     ```javascript
     chrome.runtime.sendMessage({
       action: 'EXTRACT_COMPANY_EMPLOYEES',
       maxPages: 3
     }, (response) => {
       console.log('Extraction result:', response);
       if (response.success) {
         console.log('Company:', response.data.companyName);
         console.log('Extracted:', response.data.extractedCount, 'employees');
         console.log('Employees:', response.data.employees);
       }
     });
     ```

5. **View Results**
   - The console will show extraction progress:
     ```
     [hrunxtnshn] Starting employee extraction, max pages: 3
     [hrunxtnshn] Company: Gasable | غازابل Total employees: 63
     [hrunxtnshn] Extracting page 1
     [hrunxtnshn] Found 12 employees on page 1
     [hrunxtnshn] Extraction complete: 63 unique employees
     ```
   
   - Final result object will contain:
     ```json
     {
       "success": true,
       "data": {
         "companyName": "Gasable | غازابل",
         "companyUrl": "https://www.linkedin.com/company/gasable/people/",
         "totalEmployees": 63,
         "extractedCount": 63,
         "employees": [
           {
             "name": "Dana Al-Yemni",
             "profileUrl": "https://www.linkedin.com/in/...",
             "headline": "Deputy Manager Of Information Technology at ...",
             "location": "Riyadh, Saudi Arabia",
             "connectionDegree": "2nd",
             "timeAtCompany": "3 years 2 months",
             "extractedAt": "2026-02-17T..."
           },
           // ... more employees
         ],
         "pagesScraped": 3,
         "extractedAt": "2026-02-17T..."
       }
     }
     ```

### Step 3: Test via Extension Popup (Optional)

1. **Click the Extension Icon** in your toolbar

2. **The popup should open** showing the extension interface

3. **Type a command** like:
   ```
   Extract all employees from this company
   ```

4. **Click "Execute"** or press Enter

5. **View Results** in the popup interface

---

## Expected Results

### What You Should See

✅ **Console Logs:**
- Content script loaded message
- Extraction progress logs
- Page-by-page extraction status
- Final employee count

✅ **Extracted Data:**
- Company name: "Gasable | غازابل"
- Total employees: ~63
- Employee list with:
  - Full names
  - LinkedIn profile URLs
  - Job titles/headlines
  - Locations
  - Connection degrees
  - Time at company (if visible)

✅ **Data Structure:**
```json
{
  "companyName": "string",
  "companyUrl": "string",
  "totalEmployees": number,
  "extractedCount": number,
  "employees": [
    {
      "name": "string",
      "profileUrl": "string",
      "headline": "string",
      "location": "string",
      "connectionDegree": "string",
      "timeAtCompany": "string",
      "extractedAt": "ISO date string"
    }
  ],
  "pagesScraped": number,
  "extractedAt": "ISO date string"
}
```

---

## Troubleshooting

### Extension Not Appearing

**Problem:** Extension icon doesn't show in toolbar

**Solutions:**
1. Reload the extension in `chrome://extensions/`
2. Click the puzzle icon in toolbar and pin hrunxtnshn
3. Check for errors in the extensions page
4. Make sure you selected the correct `extension` folder

### Content Script Not Loading

**Problem:** No console logs appear on LinkedIn

**Solutions:**
1. Refresh the LinkedIn page after loading extension
2. Check `chrome://extensions/` for errors
3. Verify "Content scripts" section in extension details
4. Make sure LinkedIn is in the host permissions

### Extraction Returns Empty Data

**Problem:** Extraction completes but no employees found

**Solutions:**
1. **Make sure you're logged into LinkedIn**
2. Wait for page to fully load before extracting
3. Check if LinkedIn's HTML structure changed
4. Try manually scrolling down first to load content
5. Check browser console for JavaScript errors

### "chrome.runtime is undefined"

**Problem:** Error when running test command

**Solutions:**
1. Make sure you're on the LinkedIn page (not test HTML)
2. Refresh the page after loading extension
3. Check that extension is enabled in chrome://extensions/

### LinkedIn Blocks Extraction

**Problem:** LinkedIn shows CAPTCHA or rate limiting

**Solutions:**
1. Wait a few minutes before trying again
2. Use smaller `maxPages` value (e.g., 1 or 2)
3. Add delays between pages (already implemented)
4. Make sure you're not running multiple extractions simultaneously

---

## Advanced Testing

### Test Different Page Types

#### 1. Company Profile Page
```
https://www.linkedin.com/company/gasable/
```

Console command:
```javascript
chrome.runtime.sendMessage({
  action: 'CHECK_PAGE_TYPE'
}, (response) => {
  console.log('Page type:', response.pageType);
});
```

Expected: `pageType: "company_profile"`

#### 2. User Profile Page
```
https://www.linkedin.com/in/your-profile/
```

Expected: `pageType: "user_profile"`

#### 3. Company People Page
```
https://www.linkedin.com/company/gasable/people/
```

Expected: `pageType: "company_people"`

### Test Pagination

Extract multiple pages:
```javascript
chrome.runtime.sendMessage({
  action: 'EXTRACT_COMPANY_EMPLOYEES',
  maxPages: 6  // Extract up to 6 pages
}, (response) => {
  console.log('Pages scraped:', response.data.pagesScraped);
  console.log('Total extracted:', response.data.extractedCount);
});
```

### Export Results

Save extraction to file:
```javascript
chrome.runtime.sendMessage({
  action: 'EXTRACT_COMPANY_EMPLOYEES',
  maxPages: 3
}, (response) => {
  if (response.success) {
    // Convert to JSON
    const json = JSON.stringify(response.data, null, 2);
    
    // Create download
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'gasable_employees.json';
    a.click();
  }
});
```

---

## Performance Notes

### Extraction Speed

- **Single page:** ~2-3 seconds
- **Multiple pages (3):** ~10-15 seconds
- **Full extraction (6 pages):** ~30-40 seconds

### Rate Limiting

The extension includes built-in delays:
- 1 second between employee card extractions
- 2 seconds after "Show more" clicks
- 3 seconds between page navigations

This helps avoid LinkedIn rate limiting.

---

## Next Steps

After successful testing:

1. ✅ **Verify Data Quality**
   - Check that all employee names are correct
   - Verify profile URLs are valid
   - Confirm no duplicates

2. ✅ **Test Other Companies**
   - Try different company sizes
   - Test with companies you have connections at
   - Verify pagination works correctly

3. ✅ **Integrate with Backend**
   - Set up the Python orchestrator
   - Connect extension to orchestrator
   - Test end-to-end workflow

4. ✅ **Push to GitHub**
   - Commit all changes
   - Push to repository
   - Update documentation

---

## Support

If you encounter issues:

1. **Check Console Logs:** Most errors will appear in browser console
2. **Check Extension Errors:** Go to `chrome://extensions/` and click "Errors"
3. **Review Code:** Check `extension/content/linkedinExtractor.js` for logic
4. **Test Manually:** Try navigating and clicking manually first

---

## Success Criteria

Your test is successful if:

✅ Extension loads without errors
✅ Content script injects on LinkedIn pages
✅ Console shows extraction progress
✅ Employee data is extracted correctly
✅ No duplicates in results
✅ All required fields are populated
✅ Extraction completes within reasonable time

**Congratulations!** Your extension is working correctly. You can now proceed to integrate it with the orchestrator backend or use it standalone.
