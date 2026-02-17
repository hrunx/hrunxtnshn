/**
 * LinkedIn Content Script
 * Main content script for LinkedIn pages
 */

(function() {
  'use strict';

  console.log('LinkedIn content script loaded on:', window.location.href);

  // Inject company extractor if on company people page
  if (window.location.href.includes('/company/') && window.location.href.includes('/people')) {
    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('content/linkedinCompanyExtractor.js');
    (document.head || document.documentElement).appendChild(script);
  }

  // Listen for extraction requests
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Content script received message:', request);

    if (request.action === 'CHECK_PAGE_TYPE') {
      const pageType = detectLinkedInPageType();
      sendResponse({ success: true, pageType });
      return false;
    }

    if (request.action === 'EXTRACT_CURRENT_PAGE') {
      const pageType = detectLinkedInPageType();
      const data = extractPageData(pageType);
      sendResponse({ success: true, pageType, data });
      return false;
    }
  });

  /**
   * Detect what type of LinkedIn page we're on
   */
  function detectLinkedInPageType() {
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
   * Extract data based on page type
   */
  function extractPageData(pageType) {
    switch (pageType) {
      case 'company_people':
        return extractCompanyPeoplePage();
      case 'company_profile':
        return extractCompanyProfile();
      case 'user_profile':
        return extractUserProfile();
      default:
        return { error: 'Unsupported page type' };
    }
  }

  /**
   * Extract company people page (simplified version)
   */
  function extractCompanyPeoplePage() {
    const employees = [];
    const employeeCards = document.querySelectorAll('.org-people-profile-card');
    
    employeeCards.forEach(card => {
      const nameEl = card.querySelector('.org-people-profile-card__profile-title');
      const linkEl = card.querySelector('a[href*="/in/"]');
      const headlineEl = card.querySelector('.artdeco-entity-lockup__subtitle');
      
      if (nameEl) {
        employees.push({
          name: nameEl.textContent.trim(),
          profileUrl: linkEl ? linkEl.href : '',
          headline: headlineEl ? headlineEl.textContent.trim() : ''
        });
      }
    });
    
    return { employees, count: employees.length };
  }

  /**
   * Extract company profile
   */
  function extractCompanyProfile() {
    const nameEl = document.querySelector('h1.org-top-card-summary__title');
    const descEl = document.querySelector('.org-top-card-summary__tagline');
    const industryEl = document.querySelector('[data-test-id="about-us__industry"]');
    const sizeEl = document.querySelector('[data-test-id="about-us__size"]');
    
    return {
      name: nameEl ? nameEl.textContent.trim() : '',
      description: descEl ? descEl.textContent.trim() : '',
      industry: industryEl ? industryEl.textContent.trim() : '',
      size: sizeEl ? sizeEl.textContent.trim() : ''
    };
  }

  /**
   * Extract user profile
   */
  function extractUserProfile() {
    const nameEl = document.querySelector('h1.text-heading-xlarge');
    const headlineEl = document.querySelector('.text-body-medium');
    const locationEl = document.querySelector('.text-body-small.inline');
    
    return {
      name: nameEl ? nameEl.textContent.trim() : '',
      headline: headlineEl ? headlineEl.textContent.trim() : '',
      location: locationEl ? locationEl.textContent.trim() : ''
    };
  }
})();
