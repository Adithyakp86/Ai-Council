"""Property-based tests for password hashing with bcrypt.

Property 5: Password Hashing with Bcrypt
Validates: Requirements 2.6, 17.1
"""

import re
import pytest
from hypothesis import given, strategies as st, assume, settings

from app.core.security import hash_password, verify_password


class TestPasswordHashingProperties:
    """Property-based tests for password hashing."""

    @settings(max_examples=10, deadline=None)
    @given(password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=72))
    def test_hashed_password_never_equals_plaintext(self, password: str):
        """
        Property: Hashed passwords must never equal the plaintext password.
        
        **Validates: Requirements 2.6, 17.1**
        
        This ensures that passwords are actually being hashed and not stored
        in plaintext, which is a critical security requirement.
        
        Note: Bcrypt has a 72-byte limit. We use ASCII characters (1 byte each)
        to ensure we stay within the limit.
        """
        # Ensure password is within bcrypt's 72-byte limit
        assume(len(password.encode('utf-8')) <= 72)
        
        hashed = hash_password(password)
        
        # The hashed password should never equal the plaintext
        assert hashed != password, "Hashed password must not equal plaintext"
        
        # The hashed password should be a string
        assert isinstance(hashed, str), "Hashed password must be a string"
        
        # The hashed password should not be empty
        assert len(hashed) > 0, "Hashed password must not be empty"
        
        # Verify that the password can be verified correctly
        assert verify_password(password, hashed), "Password verification must work"

    def test_bcrypt_cost_factor_is_12(self):
        """
        Property: Bcrypt cost factor must be exactly 12.
        
        **Validates: Requirements 2.6, 17.1**
        
        This ensures that the bcrypt algorithm uses the specified cost factor
        of 12, which provides a good balance between security and performance.
        """
        # Hash a test password
        test_password = "TestPassword123"
        hashed = hash_password(test_password)
        
        # Bcrypt hashes have the format: $2b$<cost>$<salt+hash>
        # Extract the cost factor from the hash
        match = re.match(r'\$2[aby]\$(\d+)\$', hashed)
        assert match is not None, "Hash should be in bcrypt format"
        
        cost_factor = int(match.group(1))
        assert cost_factor == 12, f"Bcrypt cost factor must be 12, got {cost_factor}"

    @settings(max_examples=10, deadline=None)
    @given(password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=72))
    def test_same_password_produces_different_hashes(self, password: str):
        """
        Property: Hashing the same password twice should produce different hashes.
        
        This is because bcrypt uses a random salt for each hash, which is a
        security best practice to prevent rainbow table attacks.
        
        Note: Bcrypt has a 72-byte limit. We use ASCII characters (1 byte each).
        """
        # Ensure password is within bcrypt's 72-byte limit
        assume(len(password.encode('utf-8')) <= 72)
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # The hashes should be different due to different salts
        assert hash1 != hash2, "Same password should produce different hashes"
        
        # But both should verify correctly
        assert verify_password(password, hash1), "First hash should verify"
        assert verify_password(password, hash2), "Second hash should verify"

    @settings(max_examples=10, deadline=None)
    @given(
        password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=72),
        wrong_password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=72)
    )
    def test_wrong_password_fails_verification(self, password: str, wrong_password: str):
        """
        Property: Verifying with a wrong password should fail.
        
        This ensures that the password verification function correctly
        rejects incorrect passwords.
        
        Note: Bcrypt has a 72-byte limit. We use ASCII characters (1 byte each).
        """
        # Ensure passwords are within bcrypt's 72-byte limit
        assume(len(password.encode('utf-8')) <= 72)
        assume(len(wrong_password.encode('utf-8')) <= 72)
        
        # Skip if passwords happen to be the same
        if password == wrong_password:
            return
        
        hashed = hash_password(password)
        
        # Wrong password should not verify
        assert not verify_password(wrong_password, hashed), \
            "Wrong password should not verify"

    @settings(max_examples=10, deadline=None)
    @given(password=st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=72))
    def test_hash_is_deterministically_verifiable(self, password: str):
        """
        Property: A hashed password should always verify correctly with the
        original password.
        
        This ensures consistency in the hashing and verification process.
        
        Note: Bcrypt has a 72-byte limit. We use ASCII characters (1 byte each).
        """
        # Ensure password is within bcrypt's 72-byte limit
        assume(len(password.encode('utf-8')) <= 72)
        
        hashed = hash_password(password)
        
        # Verify multiple times to ensure consistency
        for _ in range(3):
            assert verify_password(password, hashed), \
                "Password should verify consistently"
