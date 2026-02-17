/**
 * Instagram Profile Data Extraction Schema
 */

function parseInstagram(doc) {
  const data = {
    username: '',
    fullName: '',
    bio: '',
    followers: 0,
    following: 0,
    posts: 0,
    isPrivate: false,
    isVerified: false,
    profilePicUrl: '',
    externalUrl: '',
    recentPosts: []
  };

  try {
    // Extract username from header
    const usernameEl = doc.querySelector('header h1') ||
                       doc.querySelector('h1.x1lliihq');
    if (usernameEl) {
      data.username = usernameEl.innerText.trim();
    }

    // Extract full name
    const fullNameEl = doc.querySelector('header section h2') ||
                       doc.querySelector('h2.x1lliihq');
    if (fullNameEl) {
      data.fullName = fullNameEl.innerText.trim();
    }

    // Extract bio
    const bioEl = doc.querySelector('header section span') ||
                  doc.querySelector('span._ap3a._aaco._aacu._aacx._aad7._aade');
    if (bioEl) {
      data.bio = bioEl.innerText.trim();
    }

    // Extract stats (followers, following, posts)
    const statsEls = doc.querySelectorAll('header section ul li');
    if (statsEls.length >= 3) {
      // Posts
      const postsText = statsEls[0].innerText;
      const postsMatch = postsText.match(/([\d,]+)/);
      if (postsMatch) {
        data.posts = parseInt(postsMatch[1].replace(/,/g, ''));
      }

      // Followers
      const followersText = statsEls[1].innerText;
      const followersMatch = followersText.match(/([\d,]+)/);
      if (followersMatch) {
        data.followers = parseInt(followersMatch[1].replace(/,/g, ''));
      }

      // Following
      const followingText = statsEls[2].innerText;
      const followingMatch = followingText.match(/([\d,]+)/);
      if (followingMatch) {
        data.following = parseInt(followingMatch[1].replace(/,/g, ''));
      }
    }

    // Check if private
    const privateEl = doc.querySelector('[aria-label*="private"]') ||
                      doc.querySelector('h2:contains("This Account is Private")');
    data.isPrivate = !!privateEl;

    // Check if verified
    const verifiedEl = doc.querySelector('[aria-label*="Verified"]') ||
                       doc.querySelector('svg[aria-label="Verified"]');
    data.isVerified = !!verifiedEl;

    // Extract profile picture
    const profilePicEl = doc.querySelector('header img') ||
                         doc.querySelector('img[alt*="profile picture"]');
    if (profilePicEl) {
      data.profilePicUrl = profilePicEl.src;
    }

    // Extract external URL
    const externalUrlEl = doc.querySelector('header a[href^="http"]') ||
                          doc.querySelector('a.x1i10hfl[href^="http"]');
    if (externalUrlEl) {
      data.externalUrl = externalUrlEl.href;
    }

    // Extract recent posts (if not private)
    if (!data.isPrivate) {
      const postEls = [...doc.querySelectorAll('article a[href*="/p/"]')].slice(0, 12);
      
      for (const postEl of postEls) {
        try {
          const postUrl = postEl.href;
          const imgEl = postEl.querySelector('img');
          const imageUrl = imgEl?.src || '';
          const altText = imgEl?.alt || '';
          
          // Try to extract likes/comments from alt text or nearby elements
          const likesEl = postEl.querySelector('[aria-label*="likes"]');
          const commentsEl = postEl.querySelector('[aria-label*="comments"]');
          
          data.recentPosts.push({
            postUrl,
            imageUrl,
            caption: altText,
            likes: likesEl?.innerText || '',
            comments: commentsEl?.innerText || ''
          });
        } catch (e) {
          console.error('Error parsing post:', e);
        }
      }
    }

  } catch (error) {
    console.error('Error parsing Instagram data:', error);
  }

  return data;
}
