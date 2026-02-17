/**
 * LinkedIn Extractor Content Script
 * Extracts data from LinkedIn pages including company employee lists
 */

(function() {
  'use strict';

  console.log('[hrunxtnshn] LinkedIn extractor loaded on:', window.location.href);

  // Listen for extraction requests from background script
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[hrunxtnshn] Received message:', request.action);

    if (request.action === 'EXTRACT_LINKEDIN_DATA') {
      handleExtraction(request, sendResponse);
      return true; // Will respond asynchronously
    }

    if (request.action === 'EXTRACT_COMPANY_EMPLOYEES') {
      extractCompanyEmployees(request.maxPages || 6)
        .then(data => sendResponse({ success: true, data }))
        .catch(error => sendResponse({ success: false, error: error.toString() }));
      return true; // Will respond asynchronously
    }

    if (request.action === 'CHECK_PAGE_TYPE') {
      const pageType = detectPageType();
      sendResponse({ success: true, pageType, url: window.location.href });
      return false;
    }
  });

  /**
   * Detect what type of LinkedIn page we're on
   */
  function detectPageType() {
    const url = window.location.href;
    
    if (url.includes('/company/') && url.includes('/people')) {
      return 'company_people';
    }
    if (url.includes('/company/')) {
      return 'company_profile';
    }
    if (url.includes('/in/')) {
      return 'user_profile';
    }
    if (url.includes('/search/results/people')) {
      return 'people_search';
    }
    if (url.includes('/search/results/companies')) {
      return 'company_search';
    }
    
    return 'unknown';
  }

  /**
   * Handle extraction based on page type
   */
  async function handleExtraction(request, sendResponse) {
    const pageType = detectPageType();
    console.log('[hrunxtnshn] Page type:', pageType);

    try {
      let data;
      
      switch (pageType) {
        case 'company_people':
          data = await extractCompanyEmployees(request.maxPages || 6);
          break;
        case 'company_profile':
          data = extractCompanyProfile();
          break;
        case 'user_profile':
          data = extractUserProfile();
          break;
        default:
          data = { error: 'Unsupported page type: ' + pageType };
      }

      sendResponse({ success: true, pageType, data });
    } catch (error) {
      console.error('[hrunxtnshn] Extraction error:', error);
      sendResponse({ success: false, error: error.toString() });
    }
  }

  /**
   * Extract company employees from people page
   */
  async function extractCompanyEmployees(maxPages = 6) {
    console.log('[hrunxtnshn] Starting employee extraction, max pages:', maxPages);
    
    const allEmployees = [];
    let currentPage = 1;
    
    // Extract company info
    const companyNameEl = document.querySelector('h1.org-top-card-summary__title, h1[data-test-id="org-name"]');
    const companyName = companyNameEl ? companyNameEl.textContent.trim() : '';
    
    const employeeCountEl = document.querySelector('.org-people__header-spacing-carousel h2, .org-people-bar-graph-module__count');
    const employeeCountText = employeeCountEl ? employeeCountEl.textContent.trim() : '';
    const totalEmployees = employeeCountText.match(/\d+/) ? parseInt(employeeCountText.match(/\d+/)[0]) : 0;
    
    console.log('[hrunxtnshn] Company:', companyName, 'Total employees:', totalEmployees);
    
    // Extract employees from current page
    while (currentPage <= maxPages) {
      console.log('[hrunxtnshn] Extracting page', currentPage);
      
      // Wait for content to load
      await wait(1000);
      
      // Extract visible employees
      const employees = extractVisibleEmployees();
      console.log('[hrunxtnshn] Found', employees.length, 'employees on page', currentPage);
      
      allEmployees.push(...employees);
      
      // Try to load more or go to next page
      const showMoreBtn = document.querySelector('button[aria-label*="Show more"], .scaffold-finite-scroll__load-button');
      if (showMoreBtn && !showMoreBtn.disabled) {
        console.log('[hrunxtnshn] Clicking "Show more" button');
        showMoreBtn.click();
        await wait(2000);
        continue;
      }
      
      // Try next page
      const nextBtn = document.querySelector('button[aria-label="Next"]:not([disabled])');
      if (nextBtn && currentPage < maxPages) {
        console.log('[hrunxtnshn] Going to next page');
        nextBtn.click();
        await wait(3000);
        currentPage++;
      } else {
        console.log('[hrunxtnshn] No more pages or reached max pages');
        break;
      }
    }
    
    // Remove duplicates
    const uniqueEmployees = removeDuplicates(allEmployees);
    
    console.log('[hrunxtnshn] Extraction complete:', uniqueEmployees.length, 'unique employees');
    
    return {
      companyName,
      companyUrl: window.location.href,
      totalEmployees,
      extractedCount: uniqueEmployees.length,
      employees: uniqueEmployees,
      pagesScraped: currentPage,
      extractedAt: new Date().toISOString()
    };
  }

  /**
   * Extract visible employees from current view
   */
  function extractVisibleEmployees() {
    const employees = [];
    const employeeCards = document.querySelectorAll('.org-people-profile-card, .entity-result');
    
    employeeCards.forEach((card, index) => {
      try {
        // Extract name
        const nameEl = card.querySelector('.org-people-profile-card__profile-title, .entity-result__title-text a');
        const name = nameEl ? nameEl.textContent.trim() : '';
        
        // Extract profile URL
        const linkEl = card.querySelector('a[href*="/in/"]');
        const profileUrl = linkEl ? linkEl.href.split('?')[0] : ''; // Remove query params
        
        // Extract headline/position
        const headlineEl = card.querySelector('.artdeco-entity-lockup__subtitle, .entity-result__primary-subtitle');
        const headline = headlineEl ? headlineEl.textContent.trim() : '';
        
        // Extract location
        const locationEl = card.querySelector('.artdeco-entity-lockup__caption, .entity-result__secondary-subtitle');
        const location = locationEl ? locationEl.textContent.trim() : '';
        
        // Extract connection degree
        const degreeEl = card.querySelector('.dist-value, .entity-result__badge-text');
        const connectionDegree = degreeEl ? degreeEl.textContent.trim() : '';
        
        // Extract time at company (if visible)
        const timeEl = card.querySelector('.org-people-profile-card__profile-info-subtitle');
        const timeAtCompany = timeEl ? timeEl.textContent.trim() : '';
        
        if (name && profileUrl) {
          employees.push({
            name,
            profileUrl,
            headline,
            location,
            connectionDegree,
            timeAtCompany,
            extractedAt: new Date().toISOString()
          });
        }
      } catch (error) {
        console.error('[hrunxtnshn] Error extracting employee card:', error);
      }
    });
    
    return employees;
  }

  /**
   * Remove duplicate employees based on profile URL
   */
  function removeDuplicates(employees) {
    const seen = new Set();
    return employees.filter(emp => {
      if (seen.has(emp.profileUrl)) {
        return false;
      }
      seen.add(emp.profileUrl);
      return true;
    });
  }

  /**
   * Extract company profile data
   */
  function extractCompanyProfile() {
    const nameEl = document.querySelector('h1.org-top-card-summary__title');
    const descEl = document.querySelector('.org-top-card-summary__tagline');
    const industryEl = document.querySelector('dd.org-page-details__definition-text');
    const sizeEl = document.querySelector('.org-top-card-summary-info-list__info-item');
    const followersEl = document.querySelector('.org-top-card-secondary-content__follower-count');
    
    return {
      name: nameEl ? nameEl.textContent.trim() : '',
      description: descEl ? descEl.textContent.trim() : '',
      industry: industryEl ? industryEl.textContent.trim() : '',
      size: sizeEl ? sizeEl.textContent.trim() : '',
      followers: followersEl ? followersEl.textContent.trim() : '',
      url: window.location.href,
      extractedAt: new Date().toISOString()
    };
  }

  /**
   * Extract user profile data
   */
  function extractUserProfile() {
    const nameEl = document.querySelector('h1.text-heading-xlarge');
    const headlineEl = document.querySelector('.text-body-medium.break-words');
    const locationEl = document.querySelector('.text-body-small.inline.t-black--light.break-words');
    
    return {
      name: nameEl ? nameEl.textContent.trim() : '',
      headline: headlineEl ? headlineEl.textContent.trim() : '',
      location: locationEl ? locationEl.textContent.trim() : '',
      url: window.location.href,
      extractedAt: new Date().toISOString()
    };
  }

  /**
   * Wait helper
   */
  function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  console.log('[hrunxtnshn] LinkedIn extractor ready');
})();
