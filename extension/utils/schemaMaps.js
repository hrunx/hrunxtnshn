/**
 * Google Maps Data Extraction Schema
 */

function parseMaps(doc) {
  const data = {
    name: '',
    rating: null,
    reviewCount: 0,
    address: '',
    phone: '',
    website: '',
    hours: {},
    category: '',
    priceLevel: '',
    photos: [],
    reviews: []
  };

  try {
    // Extract place name
    const nameEl = doc.querySelector('h1.fontHeadlineLarge') || 
                   doc.querySelector('[data-item-id*="title"]') ||
                   doc.querySelector('.Nv2PK');
    if (nameEl) {
      data.name = nameEl.innerText.trim();
    }

    // Extract rating
    const ratingEl = doc.querySelector('[aria-label*="stars"]') ||
                     doc.querySelector('.MW4etd');
    if (ratingEl) {
      const ratingText = ratingEl.innerText || ratingEl.getAttribute('aria-label');
      const match = ratingText.match(/(\d+\.?\d*)/);
      if (match) {
        data.rating = parseFloat(match[1]);
      }
    }

    // Extract review count
    const reviewCountEl = doc.querySelector('[aria-label*="reviews"]');
    if (reviewCountEl) {
      const text = reviewCountEl.innerText || reviewCountEl.getAttribute('aria-label');
      const match = text.match(/([\d,]+)\s*reviews?/i);
      if (match) {
        data.reviewCount = parseInt(match[1].replace(/,/g, ''));
      }
    }

    // Extract address
    const addressEl = doc.querySelector('[data-item-id*="address"]') ||
                      doc.querySelector('.Io6YTe');
    if (addressEl) {
      data.address = addressEl.innerText.trim();
    }

    // Extract phone
    const phoneEl = doc.querySelector('[data-item-id*="phone"]') ||
                    doc.querySelector('[aria-label*="Phone"]');
    if (phoneEl) {
      data.phone = phoneEl.innerText.trim();
    }

    // Extract website
    const websiteEl = doc.querySelector('[data-item-id*="authority"]') ||
                      doc.querySelector('a[href*="http"]');
    if (websiteEl) {
      data.website = websiteEl.href;
    }

    // Extract category
    const categoryEl = doc.querySelector('.DkEaL');
    if (categoryEl) {
      data.category = categoryEl.innerText.trim();
    }

    // Extract reviews
    const reviewEls = [...doc.querySelectorAll('.jftiEf, .Nv2PK')].slice(0, 10);
    for (const reviewEl of reviewEls) {
      try {
        const author = reviewEl.querySelector('.d4r55')?.innerText || '';
        const ratingEl = reviewEl.querySelector('[aria-label*="stars"]');
        const rating = ratingEl ? parseFloat(ratingEl.getAttribute('aria-label').match(/(\d+)/)[1]) : 0;
        const text = reviewEl.querySelector('.wiI7pd')?.innerText || '';
        const date = reviewEl.querySelector('.rsqaWe')?.innerText || '';
        
        if (author || text) {
          data.reviews.push({
            author,
            rating,
            text,
            date
          });
        }
      } catch (e) {
        console.error('Error parsing review:', e);
      }
    }

  } catch (error) {
    console.error('Error parsing Maps data:', error);
  }

  return data;
}
