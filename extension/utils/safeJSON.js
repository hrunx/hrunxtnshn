/**
 * Safe JSON Utilities
 * Handles JSON parsing with error handling
 */

function safeJSONParse(text, defaultValue = null) {
  try {
    return JSON.parse(text);
  } catch (error) {
    console.error('JSON parse error:', error);
    return defaultValue;
  }
}

function safeJSONStringify(obj, defaultValue = '{}') {
  try {
    return JSON.stringify(obj);
  } catch (error) {
    console.error('JSON stringify error:', error);
    return defaultValue;
  }
}
