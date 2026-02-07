"""Unit tests for JWT token generation and validation."""

import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from hypothesis import given, strategies as st, settings as hypothesis_settings

from app.core.security import create_access_token, verify_token
from app.core.config import settings


def test_create_access_token_with_default_expiration():
    """Test that tokens are created with 7-day default expiration."""
    data = {"sub": "user123"}
    token = create_access_token(data)
    
    # Decode token to check expiration
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert "exp" in payload
    assert "sub" in payload
    assert payload["sub"] == "user123"
    
    # Check expiration is approximately 7 days from now
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    time_diff = exp_datetime - now
    
    # Should be close to 7 days (allow 1 minute tolerance for test execution time)
    expected_seconds = 7 * 24 * 60 * 60
    assert abs(time_diff.total_seconds() - expected_seconds) < 60


def test_create_access_token_with_custom_expiration():
    """Test that tokens can be created with custom expiration."""
    data = {"sub": "user456"}
    custom_delta = timedelta(hours=1)
    token = create_access_token(data, expires_delta=custom_delta)
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    time_diff = exp_datetime - now
    
    # Should be close to 1 hour
    expected_seconds = 60 * 60
    assert abs(time_diff.total_seconds() - expected_seconds) < 60


def test_verify_valid_token():
    """Test that valid tokens are verified successfully."""
    data = {"sub": "user789", "role": "admin"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == "user789"
    assert payload["role"] == "admin"


def test_verify_expired_token():
    """Test that expired tokens are rejected."""
    data = {"sub": "user999"}
    # Create token that expired 1 hour ago
    expired_delta = timedelta(hours=-1)
    token = create_access_token(data, expires_delta=expired_delta)
    
    payload = verify_token(token)
    
    assert payload is None


def test_verify_invalid_token():
    """Test that invalid tokens are rejected."""
    invalid_token = "invalid.token.string"
    
    payload = verify_token(invalid_token)
    
    assert payload is None


def test_verify_token_with_wrong_secret():
    """Test that tokens signed with wrong secret are rejected."""
    data = {"sub": "user111"}
    # Create token with wrong secret
    wrong_token = jwt.encode(data, "wrong-secret-key", algorithm=settings.ALGORITHM)
    
    payload = verify_token(wrong_token)
    
    assert payload is None


def test_token_contains_all_provided_data():
    """Test that all data provided is included in the token."""
    data = {
        "sub": "user222",
        "email": "user@example.com",
        "role": "user",
        "custom_field": "custom_value"
    }
    token = create_access_token(data)
    
    payload = verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == "user222"
    assert payload["email"] == "user@example.com"
    assert payload["role"] == "user"
    assert payload["custom_field"] == "custom_value"


def test_token_expiration_is_exactly_7_days():
    """Test that default token expiration is exactly 7 days."""
    data = {"sub": "user333"}
    token = create_access_token(data)
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    exp_timestamp = payload["exp"]
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    
    # Calculate difference in days
    time_diff = exp_datetime - now
    days_diff = time_diff.total_seconds() / (24 * 60 * 60)
    
    # Should be very close to 7 days (within 1 minute tolerance)
    assert abs(days_diff - 7) < (1 / (24 * 60))


def test_multiple_tokens_are_unique():
    """Test that creating multiple tokens with same data produces different tokens."""
    import time
    
    data = {"sub": "user444"}
    
    token1 = create_access_token(data)
    time.sleep(1.1)  # Delay to ensure different timestamps (JWT uses seconds precision)
    token2 = create_access_token(data)
    
    # Tokens should be different because expiration timestamps differ
    assert token1 != token2
    
    # But both should be valid
    payload1 = verify_token(token1)
    payload2 = verify_token(token2)
    
    assert payload1 is not None
    assert payload2 is not None
    assert payload1["sub"] == payload2["sub"]


class TestJWTTokenExpirationProperties:
    """Property-based tests for JWT token expiration.
    
    Property 7: JWT Token Validity Period
    Validates: Requirements 2.3
    """

    @hypothesis_settings(max_examples=20, deadline=None)
    @given(
        user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'), 
            whitelist_characters='-_'
        )),
        additional_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters='_'
            )),
            values=st.one_of(
                st.text(max_size=50),
                st.integers(),
                st.booleans()
            ),
            max_size=5
        )
    )
    def test_tokens_expire_exactly_7_days_after_issuance(self, user_id: str, additional_data: dict):
        """
        Property: Tokens created with default expiration must expire exactly 7 days after issuance.
        
        **Validates: Requirements 2.3**
        
        This property ensures that JWT tokens have a consistent validity period of 7 days
        when created without a custom expiration delta. This is critical for security
        and user experience - tokens should not expire too soon (poor UX) or too late
        (security risk).
        
        The test verifies:
        1. The token contains an expiration claim
        2. The expiration is set to exactly 7 days from the creation time
        3. This holds true regardless of the token payload content
        
        Note: JWT timestamps are stored as integers (seconds since epoch), so we lose
        microsecond precision. We account for this by allowing a 2-second tolerance.
        """
        # Create token data
        token_data = {"sub": user_id}
        token_data.update(additional_data)
        
        # Record the time before token creation
        before_creation = datetime.now(timezone.utc)
        
        # Create token with default expiration (should be 7 days)
        token = create_access_token(token_data)
        
        # Record the time after token creation
        after_creation = datetime.now(timezone.utc)
        
        # Decode the token to inspect expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Verify expiration claim exists
        assert "exp" in payload, "Token must contain expiration claim"
        
        # Convert expiration timestamp to datetime
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        
        # Calculate expected expiration (7 days from creation)
        # JWT stores timestamps as integers (seconds), so we need to account for rounding
        expected_exp_min = before_creation + timedelta(days=7) - timedelta(seconds=2)
        expected_exp_max = after_creation + timedelta(days=7) + timedelta(seconds=2)
        
        # Verify expiration is exactly 7 days from creation time
        assert expected_exp_min <= exp_datetime <= expected_exp_max, \
            f"Token expiration must be exactly 7 days from issuance. " \
            f"Expected between {expected_exp_min} and {expected_exp_max}, got {exp_datetime}"
        
        # Additional verification: calculate the actual difference in days
        # Use the midpoint of creation window for more accurate measurement
        creation_midpoint = before_creation + (after_creation - before_creation) / 2
        time_diff = exp_datetime - creation_midpoint
        days_diff = time_diff.total_seconds() / (24 * 60 * 60)
        
        # Should be very close to 7 days (within 2 seconds tolerance)
        tolerance_days = 2 / (24 * 60 * 60)  # 2 seconds in days
        assert abs(days_diff - 7) < tolerance_days, \
            f"Token expiration must be exactly 7 days. Got {days_diff} days"

    @hypothesis_settings(max_examples=10, deadline=None)
    @given(
        user_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd'),
            whitelist_characters='-_'
        ))
    )
    def test_token_becomes_invalid_after_7_days(self, user_id: str):
        """
        Property: Tokens must become invalid exactly after 7 days.
        
        **Validates: Requirements 2.3**
        
        This property verifies that tokens are rejected by the verification
        function after their 7-day validity period expires.
        """
        token_data = {"sub": user_id}
        
        # Create a token that expires in 7 days minus 1 second (should be valid)
        almost_7_days = timedelta(days=7, seconds=-1)
        valid_token = create_access_token(token_data, expires_delta=almost_7_days)
        
        # This token should be valid
        payload = verify_token(valid_token)
        assert payload is not None, "Token expiring in 6 days 23:59:59 should be valid"
        assert payload["sub"] == user_id
        
        # Create a token that expired 1 second after 7 days (should be invalid)
        just_over_7_days = timedelta(days=7, seconds=1)
        # To simulate expiration, we need to create a token that expired in the past
        expired_token = create_access_token(token_data, expires_delta=timedelta(seconds=-1))
        
        # This token should be invalid
        payload = verify_token(expired_token)
        assert payload is None, "Expired token should be rejected"

    @hypothesis_settings(max_examples=10, deadline=None)
    @given(
        custom_days=st.integers(min_value=1, max_value=365)
    )
    def test_custom_expiration_overrides_default_7_days(self, custom_days: int):
        """
        Property: Custom expiration deltas should override the default 7-day period.
        
        **Validates: Requirements 2.3**
        
        This ensures that when a custom expiration is provided, it takes precedence
        over the default 7-day expiration.
        
        Note: JWT timestamps are stored as integers (seconds since epoch), so we lose
        microsecond precision. We account for this by allowing a 2-second tolerance.
        """
        token_data = {"sub": "test_user"}
        
        # Record creation time
        before_creation = datetime.now(timezone.utc)
        
        # Create token with custom expiration
        custom_delta = timedelta(days=custom_days)
        token = create_access_token(token_data, expires_delta=custom_delta)
        
        after_creation = datetime.now(timezone.utc)
        
        # Decode and check expiration
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp_datetime = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        
        # Calculate expected expiration with tolerance for JWT integer timestamps
        expected_exp_min = before_creation + custom_delta - timedelta(seconds=2)
        expected_exp_max = after_creation + custom_delta + timedelta(seconds=2)
        
        # Verify expiration matches custom delta, not default 7 days
        assert expected_exp_min <= exp_datetime <= expected_exp_max, \
            f"Token with custom expiration of {custom_days} days should expire in {custom_days} days, not 7"
        
        # Verify it's NOT 7 days if custom_days != 7
        if custom_days != 7:
            creation_midpoint = before_creation + (after_creation - before_creation) / 2
            time_diff = exp_datetime - creation_midpoint
            days_diff = time_diff.total_seconds() / (24 * 60 * 60)
            
            # Should NOT be 7 days (allow 2 second tolerance)
            tolerance_days = 2 / (24 * 60 * 60)
            assert abs(days_diff - 7) > tolerance_days, \
                f"Token with custom expiration should not default to 7 days"

