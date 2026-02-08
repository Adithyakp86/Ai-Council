export interface ErrorDetails {
  title: string
  message: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function getErrorMessage(error: unknown): ErrorDetails {
  // Network errors
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      title: 'Connection Error',
      message: 'Unable to connect to the server. Please check your internet connection and try again.',
      action: {
        label: 'Retry',
        onClick: () => window.location.reload(),
      },
    }
  }

  // API errors
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const apiError = error as { response?: { status?: number; data?: { message?: string } } }
    const status = apiError.response?.status
    const message = apiError.response?.data?.message

    switch (status) {
      case 400:
        return {
          title: 'Invalid Request',
          message: message || 'The request contains invalid data. Please check your input and try again.',
        }
      case 401:
        return {
          title: 'Authentication Required',
          message: 'Your session has expired. Please log in again.',
          action: {
            label: 'Log In',
            onClick: () => window.location.href = '/login',
          },
        }
      case 403:
        return {
          title: 'Access Denied',
          message: 'You do not have permission to perform this action.',
        }
      case 404:
        return {
          title: 'Not Found',
          message: 'The requested resource could not be found.',
        }
      case 429:
        return {
          title: 'Rate Limit Exceeded',
          message: 'You have made too many requests. Please wait a moment and try again.',
        }
      case 500:
      case 502:
      case 503:
        return {
          title: 'Server Error',
          message: 'The server encountered an error. Please try again later.',
          action: {
            label: 'Retry',
            onClick: () => window.location.reload(),
          },
        }
      default:
        return {
          title: 'Request Failed',
          message: message || 'An error occurred while processing your request. Please try again.',
        }
    }
  }

  // Validation errors
  if (error instanceof Error && error.message.includes('validation')) {
    return {
      title: 'Validation Error',
      message: error.message,
    }
  }

  // Generic error
  if (error instanceof Error) {
    return {
      title: 'Error',
      message: error.message || 'An unexpected error occurred. Please try again.',
    }
  }

  // Unknown error
  return {
    title: 'Unexpected Error',
    message: 'Something went wrong. Please try again or contact support if the problem persists.',
  }
}

export function getValidationError(field: string, type: string): string {
  const messages: Record<string, Record<string, string>> = {
    email: {
      required: 'Email address is required',
      invalid: 'Please enter a valid email address',
    },
    password: {
      required: 'Password is required',
      minLength: 'Password must be at least 8 characters long',
      weak: 'Password must contain uppercase, lowercase, and a number',
    },
    name: {
      required: 'Name is required',
      minLength: 'Name must be at least 2 characters long',
    },
    content: {
      required: 'Content is required',
      maxLength: 'Content exceeds maximum length',
    },
  }

  return messages[field]?.[type] || 'Invalid input'
}
