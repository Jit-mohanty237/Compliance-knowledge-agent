// Configured backend API URL
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Temporary diagnostic log for Vercel production check
console.log("API URL:", import.meta.env.VITE_API_URL);

const API_BASE_URL = `${API_URL}/api`;

/**
 * Sends a message to the FastAPI compliance agent backend.
 * 
 * @param {string} message - The compliance question.
 * @param {string|null} sessionId - The current active session ID.
 * @returns {Promise<{response: string, session_id: string}>}
 */
export async function sendChatMessage(message, sessionId = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });

    if (!response.ok) {
      // Extract detailed error from FastAPI if available
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Server responded with status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Service Error:', error);
    throw error;
  }
}
