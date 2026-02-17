/**
 * LinkedIn Profile Data Extraction Schema
 */

function parseLinkedIn(doc) {
  const data = {
    name: '',
    headline: '',
    location: '',
    connections: '',
    about: '',
    experience: [],
    education: [],
    skills: [],
    profileUrl: ''
  };

  try {
    // Extract name
    const nameEl = doc.querySelector('h1.text-heading-xlarge') ||
                   doc.querySelector('.pv-text-details__left-panel h1') ||
                   doc.querySelector('h1');
    if (nameEl) {
      data.name = nameEl.innerText.trim();
    }

    // Extract headline
    const headlineEl = doc.querySelector('.text-body-medium.break-words') ||
                       doc.querySelector('.pv-text-details__left-panel .text-body-medium') ||
                       doc.querySelector('.pv-top-card--list-bullet .pv-text-details__left-panel h2');
    if (headlineEl) {
      data.headline = headlineEl.innerText.trim();
    }

    // Extract location
    const locationEl = doc.querySelector('.text-body-small.inline.t-black--light.break-words') ||
                       doc.querySelector('.pv-text-details__left-panel span.text-body-small');
    if (locationEl) {
      data.location = locationEl.innerText.trim();
    }

    // Extract connections
    const connectionsEl = doc.querySelector('.pv-top-card--list-bullet li') ||
                          doc.querySelector('[aria-label*="connections"]');
    if (connectionsEl) {
      data.connections = connectionsEl.innerText.trim();
    }

    // Extract about section
    const aboutEl = doc.querySelector('#about ~ .display-flex .inline-show-more-text') ||
                    doc.querySelector('.pv-about-section .pv-about__summary-text');
    if (aboutEl) {
      data.about = aboutEl.innerText.trim();
    }

    // Extract experience
    const experienceSection = doc.querySelector('#experience');
    if (experienceSection) {
      const experienceItems = experienceSection.parentElement.querySelectorAll('li.artdeco-list__item');
      
      for (const item of experienceItems) {
        try {
          const titleEl = item.querySelector('.mr1.t-bold span[aria-hidden="true"]');
          const companyEl = item.querySelector('.t-14.t-normal span[aria-hidden="true"]');
          const durationEl = item.querySelector('.t-14.t-normal.t-black--light span[aria-hidden="true"]');
          const descriptionEl = item.querySelector('.inline-show-more-text');
          
          if (titleEl || companyEl) {
            data.experience.push({
              title: titleEl?.innerText.trim() || '',
              company: companyEl?.innerText.trim() || '',
              duration: durationEl?.innerText.trim() || '',
              description: descriptionEl?.innerText.trim() || ''
            });
          }
        } catch (e) {
          console.error('Error parsing experience item:', e);
        }
      }
    }

    // Extract education
    const educationSection = doc.querySelector('#education');
    if (educationSection) {
      const educationItems = educationSection.parentElement.querySelectorAll('li.artdeco-list__item');
      
      for (const item of educationItems) {
        try {
          const schoolEl = item.querySelector('.mr1.t-bold span[aria-hidden="true"]');
          const degreeEl = item.querySelector('.t-14.t-normal span[aria-hidden="true"]');
          const yearsEl = item.querySelector('.t-14.t-normal.t-black--light span[aria-hidden="true"]');
          
          if (schoolEl) {
            data.education.push({
              school: schoolEl.innerText.trim(),
              degree: degreeEl?.innerText.trim() || '',
              years: yearsEl?.innerText.trim() || ''
            });
          }
        } catch (e) {
          console.error('Error parsing education item:', e);
        }
      }
    }

    // Extract skills
    const skillsSection = doc.querySelector('#skills');
    if (skillsSection) {
      const skillItems = skillsSection.parentElement.querySelectorAll('.mr1.hoverable-link-text.t-bold span[aria-hidden="true"]');
      
      for (const skillEl of skillItems) {
        const skill = skillEl.innerText.trim();
        if (skill) {
          data.skills.push(skill);
        }
      }
    }

    // Get profile URL from current page
    data.profileUrl = doc.location?.href || '';

  } catch (error) {
    console.error('Error parsing LinkedIn data:', error);
  }

  return data;
}
