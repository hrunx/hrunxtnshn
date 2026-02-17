/**
 * LinkedIn Company People Page Extractor
 * Extracts employee data from LinkedIn company people page
 */

(function() {
  'use strict';

  /**
   * Extract employee data from company people page
   */
  function extractCompanyEmployees() {
    const employees = [];
    
    // Check if we're on a company people page
    const url = window.location.href;
    if (!url.includes('/company/') || !url.includes('/people')) {
      return { error: 'Not a company people page' };
    }
    
    // Extract company name
    const companyNameEl = document.querySelector('h1.org-top-card-summary__title');
    const companyName = companyNameEl ? companyNameEl.textContent.trim() : '';
    
    // Extract employee count
    const employeeCountEl = document.querySelector('.org-people__header-spacing-carousel h2');
    const employeeCountText = employeeCountEl ? employeeCountEl.textContent.trim() : '';
    const employeeCount = employeeCountText.match(/\d+/) ? parseInt(employeeCountText.match(/\d+/)[0]) : 0;
    
    // Extract visible employee cards
    const employeeCards = document.querySelectorAll('.org-people-profile-card');
    
    employeeCards.forEach((card, index) => {
      try {
        // Extract name
        const nameEl = card.querySelector('.org-people-profile-card__profile-title');
        const name = nameEl ? nameEl.textContent.trim() : '';
        
        // Extract profile link
        const linkEl = card.querySelector('a[href*="/in/"]');
        const profileUrl = linkEl ? linkEl.href : '';
        
        // Extract headline/position
        const headlineEl = card.querySelector('.artdeco-entity-lockup__subtitle');
        const headline = headlineEl ? headlineEl.textContent.trim() : '';
        
        // Extract location
        const locationEl = card.querySelector('.artdeco-entity-lockup__caption');
        const location = locationEl ? locationEl.textContent.trim() : '';
        
        // Extract connection degree
        const degreeEl = card.querySelector('.dist-value');
        const connectionDegree = degreeEl ? degreeEl.textContent.trim() : '';
        
        if (name) {
          employees.push({
            name,
            profileUrl,
            headline,
            location,
            connectionDegree,
            extractedAt: new Date().toISOString()
          });
        }
      } catch (error) {
        console.error('Error extracting employee card:', error);
      }
    });
    
    return {
      companyName,
      companyUrl: url,
      totalEmployees: employeeCount,
      extractedCount: employees.length,
      employees,
      extractedAt: new Date().toISOString()
    };
  }

  /**
   * Load more employees by clicking "Show more" button
   */
  async function loadMoreEmployees() {
    const showMoreButton = document.querySelector('button[aria-label*="Show more"]');
    if (showMoreButton && !showMoreButton.disabled) {
      showMoreButton.click();
      // Wait for content to load
      await new Promise(resolve => setTimeout(resolve, 2000));
      return true;
    }
    return false;
  }

  /**
   * Navigate to next page
   */
  async function goToNextPage() {
    const nextButton = document.querySelector('button[aria-label="Next"]');
    if (nextButton && !nextButton.disabled) {
      nextButton.click();
      // Wait for page to load
      await new Promise(resolve => setTimeout(resolve, 3000));
      return true;
    }
    return false;
  }

  /**
   * Extract all employees with pagination
   */
  async function extractAllEmployees(maxPages = 6) {
    const allEmployees = [];
    let currentPage = 1;
    
    while (currentPage <= maxPages) {
      console.log(`Extracting page ${currentPage}...`);
      
      // Extract current page
      const pageData = extractCompanyEmployees();
      if (pageData.employees) {
        allEmployees.push(...pageData.employees);
      }
      
      // Try to load more on current page
      const loadedMore = await loadMoreEmployees();
      if (loadedMore) {
        continue; // Extract again after loading more
      }
      
      // Try to go to next page
      const wentToNextPage = await goToNextPage();
      if (!wentToNextPage) {
        break; // No more pages
      }
      
      currentPage++;
    }
    
    // Get final company info
    const finalData = extractCompanyEmployees();
    
    return {
      companyName: finalData.companyName,
      companyUrl: finalData.companyUrl,
      totalEmployees: finalData.totalEmployees,
      extractedCount: allEmployees.length,
      employees: allEmployees,
      pagesScraped: currentPage,
      extractedAt: new Date().toISOString()
    };
  }

  // Listen for messages from background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'EXTRACT_COMPANY_EMPLOYEES') {
      // Extract employees with pagination
      extractAllEmployees(request.maxPages || 6)
        .then(data => {
          sendResponse({ success: true, data });
        })
        .catch(error => {
          sendResponse({ success: false, error: error.toString() });
        });
      
      return true; // Will respond asynchronously
    }
    
    if (request.action === 'EXTRACT_COMPANY_EMPLOYEES_CURRENT_PAGE') {
      // Extract only current page
      try {
        const data = extractCompanyEmployees();
        sendResponse({ success: true, data });
      } catch (error) {
        sendResponse({ success: false, error: error.toString() });
      }
      
      return false;
    }
  });

  console.log('LinkedIn Company People Extractor loaded');
})();
