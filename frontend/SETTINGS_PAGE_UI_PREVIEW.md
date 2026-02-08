# Settings Page UI Preview

## Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Settings                                    [Back to Dashboard]  │
│ Manage your API keys and preferences                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ 🔑 API Keys                                                      │
│ Configure your own API keys for AI providers. Keys are          │
│ encrypted and stored securely.                                   │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 🦙  Ollama                                    ✅ [Local]    │  │
│ │     Local AI models running on your machine.               │  │
│ │     100% free, no API keys needed.                         │  │
│ │     Completely free - runs locally on your hardware        │  │
│ │                                                             │  │
│ │     Key: sk-...xyz                                         │  │
│ │     Last used: Jan 15, 2024                                │  │
│ │                                                             │  │
│ │                              [Test] [Update] [Delete]      │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ ✨  Google Gemini                            ✅ [Free]     │  │
│ │     Google's Gemini AI models with generous free tier.    │  │
│ │     Free tier: 60 requests/minute, no billing required     │  │
│ │                                                             │  │
│ │     Key: AIz...abc                                         │  │
│ │     Last used: Jan 14, 2024                                │  │
│ │                                                             │  │
│ │                              [Test] [Update] [Delete]      │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 🤗  HuggingFace                              ⚠️ [Free]     │  │
│ │     Open-source AI models via HuggingFace Inference API.  │  │
│ │     Free tier: ~1000 requests/day                          │  │
│ │                                                             │  │
│ │                              [Add Key] [Get API Key]       │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ ⚡  Groq                                     ⚠️             │  │
│ │     Ultra-fast inference with Groq's LPU technology.      │  │
│ │     Free credits available on signup                       │  │
│ │                                                             │  │
│ │                              [Add Key] [Get API Key]       │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 🤝  Together AI                              ⚠️             │  │
│ │     Access to diverse open-source models.                  │  │
│ │     $25 free credits on signup                             │  │
│ │                                                             │  │
│ │                              [Add Key] [Get API Key]       │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 🔀  OpenRouter                               ⚠️             │  │
│ │     Unified access to multiple AI providers.               │  │
│ │     $1-5 free credits on signup                            │  │
│ │                                                             │  │
│ │                              [Add Key] [Get API Key]       │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 🤖  OpenAI                                   ⚠️             │  │
│ │     GPT-3.5, GPT-4, and other OpenAI models.              │  │
│ │     $5 free trial (requires payment method)                │  │
│ │                                                             │  │
│ │                              [Add Key] [Get API Key]       │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ 🐼  Qwen (Alibaba Cloud)                     ⚠️             │  │
│ │     Alibaba's Qwen AI models.                              │  │
│ │     Free tier available in some regions                    │  │
│ │                                                             │  │
│ │                              [Add Key] [Get API Key]       │  │
│ └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│ ┌───────────────────────────────────────────────────────────┐  │
│ │ ⚠️  About API Keys                                         │  │
│ │                                                             │  │
│ │ • Your API keys are encrypted and stored securely          │  │
│ │ • Keys with a green checkmark are configured by you        │  │
│ │ • Keys with a yellow warning are using system defaults     │  │
│ │ • Free tier providers are great for getting started        │  │
│ │ • You can test your keys to verify they work correctly     │  │
│ └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Add/Update API Key Dialog

```
┌─────────────────────────────────────────────────────────┐
│ Add API Key                                        [X]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ Enter your API key for Google Gemini. Your key will    │
│ be encrypted and stored securely.                      │
│                                                         │
│ API Key                                                 │
│ ┌─────────────────────────────────────────────────┐   │
│ │ ••••••••••••••••••••••••••••••••••••••••••  👁️  │   │
│ └─────────────────────────────────────────────────┘   │
│ Get your API key from Google Gemini                    │
│                                                         │
│                              [Cancel] [Save API Key]   │
└─────────────────────────────────────────────────────────┘
```

## Status Indicators

### Configured (Green Checkmark ✅)
- User has added their own API key
- Key is encrypted and stored
- Can be tested, updated, or deleted

### System Default (Yellow Warning ⚠️)
- No user key configured
- May fall back to system defaults if available
- User should add their own key for better control

## Button Actions

### Add Key
- Opens dialog to enter new API key
- Validates input before submission
- Encrypts and stores key securely

### Update
- Opens dialog with existing key masked
- Allows replacing the current key
- Updates timestamp on save

### Test
- Validates key with the provider's API
- Shows loading spinner during test
- Displays success or error message

### Delete
- Shows confirmation dialog
- Removes key from database
- Updates UI immediately

### Get API Key
- Opens provider's signup page in new tab
- Direct link to API key generation page

## Color Coding

- **Green**: Configured, active, success states
- **Yellow**: Warnings, system defaults
- **Red**: Errors, destructive actions
- **Blue**: Local providers
- **Gray**: Neutral, inactive states

## Responsive Behavior

### Desktop (>768px)
- Full card layout with side-by-side content
- Multiple action buttons visible
- Optimal spacing and padding

### Mobile (<768px)
- Stacked layout
- Buttons stack vertically
- Touch-friendly tap targets
- Scrollable content

## Accessibility Features

- Proper ARIA labels on all interactive elements
- Keyboard navigation support
- Focus indicators on all focusable elements
- Screen reader friendly descriptions
- High contrast text and icons
- Semantic HTML structure

## Loading States

### Initial Load
- Skeleton loaders for provider cards
- Smooth fade-in animation

### Submitting
- Spinner on submit button
- Button disabled during submission
- "Saving..." text feedback

### Testing
- Spinner on test button
- Button disabled during test
- "Testing..." text feedback

## Error Handling

### Network Errors
- Toast notification with error message
- Retry option available
- Graceful degradation

### Validation Errors
- Inline error messages
- Field highlighting
- Clear error descriptions

### API Errors
- Backend error messages displayed
- User-friendly error translations
- Actionable error guidance
