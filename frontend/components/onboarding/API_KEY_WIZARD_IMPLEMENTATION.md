# API Key Setup Wizard Implementation

## Overview

The API Key Setup Wizard is an onboarding component that guides new users through setting up their first AI provider API key. It appears automatically on first login if the user has no API keys configured.

## Components

### 1. APIKeyWizard Component
**Location:** `frontend/components/onboarding/api-key-wizard.tsx`

A multi-step wizard dialog that guides users through:
- **Welcome Step**: Explains benefits of adding own API keys vs using system defaults
- **Choose Provider Step**: Shows recommended free providers (Gemini, HuggingFace)
- **Setup Key Step**: Step-by-step instructions with API key input and testing
- **Complete Step**: Success message with next steps

**Features:**
- 4-step wizard flow with navigation
- Visual step-by-step instructions for each provider
- API key testing before saving
- Show/hide password toggle for API key input
- Skip option at any step
- Marks wizard as completed in localStorage
- Encrypted API key storage

### 2. useAPIKeyWizard Hook
**Location:** `frontend/hooks/use-api-key-wizard.ts`

Custom hook that manages wizard state:
- Checks if user has any API keys configured
- Checks if wizard has been completed before (localStorage)
- Determines if wizard should be shown
- Provides methods to mark wizard as completed or reset

**API:**
```typescript
const {
  shouldShowWizard,    // boolean - should wizard be shown
  isChecking,          // boolean - loading state
  markWizardCompleted, // function - mark wizard as done
  resetWizard,         // function - reset wizard state
} = useAPIKeyWizard();
```

## Integration

### Dashboard Page
The wizard is integrated into the dashboard page (`frontend/app/dashboard/page.tsx`):

```typescript
import { APIKeyWizard } from '@/components/onboarding/api-key-wizard';
import { useAPIKeyWizard } from '@/hooks/use-api-key-wizard';

function DashboardContent() {
  const { shouldShowWizard, isChecking, markWizardCompleted } = useAPIKeyWizard();
  const [wizardOpen, setWizardOpen] = useState(false);

  // Show wizard when needed
  useEffect(() => {
    if (!isChecking && shouldShowWizard) {
      const timer = setTimeout(() => {
        setWizardOpen(true);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [isChecking, shouldShowWizard]);

  return (
    <>
      {/* Dashboard content */}
      
      <APIKeyWizard
        open={wizardOpen}
        onOpenChange={setWizardOpen}
        onComplete={markWizardCompleted}
      />
    </>
  );
}
```

## Recommended Free Providers

The wizard recommends two completely free providers:

### 1. Google Gemini
- **Free Tier**: 60 requests/minute, no billing required
- **Benefits**: Fast inference, large context window, multimodal support
- **Signup**: https://makersuite.google.com/app/apikey
- **Icon**: ✨

### 2. HuggingFace
- **Free Tier**: ~1000 requests/day
- **Benefits**: Open-source models, community-driven, great for experimentation
- **Signup**: https://huggingface.co/settings/tokens
- **Icon**: 🤗

## User Flow

1. **User logs in for the first time**
   - Hook checks if user has API keys
   - Hook checks if wizard was completed before
   - If no keys and not completed, wizard shows after 500ms delay

2. **Welcome Step**
   - Explains benefits: Free tier, better performance, privacy, no shared limits
   - Shows system defaults option
   - User can skip or continue

3. **Choose Provider Step**
   - Shows Gemini and HuggingFace cards
   - Displays benefits and free tier info
   - User selects a provider or skips

4. **Setup Key Step**
   - Shows numbered step-by-step instructions
   - Link to provider signup page (opens in new tab)
   - API key input with show/hide toggle
   - Test button to validate key
   - Shows success/error message after testing
   - Save button (enabled only after successful test)

5. **Complete Step**
   - Success message
   - Next steps guidance
   - Tip about adding more providers
   - Finish button to close wizard

6. **Wizard Completion**
   - Marks wizard as completed in localStorage
   - Calls onComplete callback
   - User can now use the application

## Skip Behavior

Users can skip the wizard at any step:
- Wizard is marked as completed in localStorage
- User can use system default API keys
- User can add their own keys later in Settings page
- Wizard won't show again unless localStorage is cleared

## Storage

### localStorage Keys
- `api_key_wizard_completed`: 'true' when wizard is completed or skipped

### Database
- API keys are stored encrypted in `user_api_keys` table
- Only masked keys are returned in API responses
- Full keys are only used server-side for AI provider calls

## API Endpoints Used

### GET /api/v1/user/api-keys
- Fetches user's configured API keys
- Returns masked keys only
- Used to check if user has any keys

### POST /api/v1/user/api-keys/test-new
- Tests API key validity without saving
- Takes provider_name and api_key
- Returns is_valid and error_message

### POST /api/v1/user/api-keys
- Saves encrypted API key
- Takes provider_name and api_key
- Returns success/error

## Styling

The wizard uses:
- shadcn/ui Dialog component for modal
- shadcn/ui Card components for provider cards
- shadcn/ui Alert components for messages
- shadcn/ui Button and Input components
- Lucide icons for visual elements
- Tailwind CSS for styling
- Responsive design (mobile-friendly)

## Benefits Highlighted

### Free Tier Benefits
- Many providers offer generous free tiers
- Use own keys to maximize free usage
- Icon: 💵 (DollarSign)

### Better Performance
- Dedicated rate limits
- Faster response times
- Icon: ⚡ (Zap)

### Privacy & Control
- Your API keys, your data
- Full control over providers
- Icon: 🛡️ (Shield)

### No Shared Limits
- Avoid shared system rate limits
- Your keys = your quota
- Icon: 🔑 (Key)

## Testing

To test the wizard:

1. **Clear localStorage**: `localStorage.removeItem('api_key_wizard_completed')`
2. **Delete user API keys**: Remove all keys via Settings page
3. **Refresh page**: Wizard should appear after 500ms
4. **Test flow**: Go through all steps
5. **Test skip**: Skip at different steps
6. **Test API key validation**: Try valid and invalid keys

## Future Enhancements

Potential improvements:
- Add more free providers (Anthropic Claude free tier, etc.)
- Add screenshots/GIFs for setup instructions
- Add video tutorial links
- Add provider comparison table
- Add estimated cost calculator
- Add provider health status indicators
- Add "Remind me later" option (shows again in 7 days)
- Add progress indicator (Step 1 of 4)
- Add keyboard navigation (arrow keys, escape)

## Troubleshooting

### Wizard doesn't show
- Check if `api_key_wizard_completed` is in localStorage
- Check if user has API keys configured
- Check browser console for errors
- Verify useAPIKeyWizard hook is called

### API key test fails
- Verify API key is correct
- Check provider API status
- Check network connectivity
- Check backend logs for errors

### Wizard shows every time
- Check if localStorage is being cleared
- Check if markWizardCompleted is being called
- Verify localStorage.setItem is working

## Related Files

- `frontend/components/onboarding/api-key-wizard.tsx` - Main wizard component
- `frontend/hooks/use-api-key-wizard.ts` - Wizard state management hook
- `frontend/app/dashboard/page.tsx` - Integration point
- `frontend/components/settings/api-key-dialog.tsx` - Settings API key dialog
- `frontend/app/settings/page.tsx` - Settings page with API key management
- `backend/app/api/user_api_keys.py` - API key endpoints
- `backend/app/core/encryption.py` - API key encryption

## Security Considerations

- API keys are never stored in plain text
- Keys are encrypted before storage using Fernet encryption
- Only masked keys are returned in API responses
- Keys are transmitted over HTTPS only
- Test endpoint doesn't save keys permanently
- User can delete keys at any time
- Keys are deleted when user deletes account

## Accessibility

- Keyboard navigation supported
- ARIA labels on interactive elements
- Focus management between steps
- Screen reader friendly
- High contrast mode compatible
- Responsive design for all screen sizes
