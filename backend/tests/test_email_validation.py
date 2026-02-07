"""Property-based tests for email validation.

Property 8: Email Format Validation
Validates: Requirements 2.8
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from pydantic import ValidationError

from app.api.auth import UserRegister


class TestEmailValidationProperties:
    """Property-based tests for email format validation."""

    @settings(max_examples=50, deadline=None)
    @given(
        invalid_email=st.one_of(
            # Emails without @ symbol
            st.text(
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    whitelist_characters='.-_'
                ),
                min_size=1,
                max_size=50
            ).filter(lambda x: '@' not in x),
            
            # Emails with multiple @ symbols
            st.text(
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    whitelist_characters='@.-_'
                ),
                min_size=3,
                max_size=50
            ).filter(lambda x: x.count('@') > 1),
            
            # Emails starting with @
            st.text(
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    whitelist_characters='.-_'
                ),
                min_size=1,
                max_size=49
            ).map(lambda x: '@' + x),
            
            # Emails ending with @
            st.text(
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    whitelist_characters='.-_'
                ),
                min_size=1,
                max_size=49
            ).map(lambda x: x + '@'),
            
            # Empty local part (e.g., "@example.com")
            st.text(
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    whitelist_characters='.-'
                ),
                min_size=1,
                max_size=30
            ).map(lambda x: '@' + x),
            
            # Empty domain part (e.g., "user@")
            st.text(
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd'),
                    whitelist_characters='.-_'
                ),
                min_size=1,
                max_size=30
            ).map(lambda x: x + '@'),
            
            # Domain without dot (e.g., "user@domain")
            st.builds(
                lambda local, domain: f"{local}@{domain}",
                local=st.text(
                    alphabet=st.characters(
                        whitelist_categories=('Lu', 'Ll', 'Nd'),
                        whitelist_characters='.-_'
                    ),
                    min_size=1,
                    max_size=20
                ),
                domain=st.text(
                    alphabet=st.characters(
                        whitelist_categories=('Lu', 'Ll', 'Nd')
                    ),
                    min_size=1,
                    max_size=20
                ).filter(lambda x: '.' not in x)
            ),
            
            # Just @ symbol
            st.just('@'),
            
            # Empty string
            st.just(''),
            
            # Whitespace only
            st.text(alphabet=' \t\n', min_size=1, max_size=10),
        ),
        password=st.text(min_size=8, max_size=50),
        name=st.text(min_size=1, max_size=50)
    )
    def test_invalid_email_formats_are_rejected(
        self, 
        invalid_email: str, 
        password: str, 
        name: str
    ):
        """
        Property: Invalid email formats must be rejected during registration.
        
        **Validates: Requirements 2.8**
        
        This property ensures that the system properly validates email formats
        and rejects invalid emails during user registration. Email validation
        is critical for:
        1. Ensuring users can receive password reset emails
        2. Preventing typos that would lock users out of their accounts
        3. Maintaining data quality in the user database
        
        The test generates various invalid email formats including:
        - Emails without @ symbol
        - Emails with multiple @ symbols
        - Emails starting or ending with @
        - Empty local or domain parts
        - Domains without dots
        - Empty strings and whitespace
        
        All of these should be rejected by the email validation logic.
        """
        # Skip if the email happens to be valid (very unlikely with our generators)
        # This is a safety check to ensure we're actually testing invalid emails
        if '@' in invalid_email and invalid_email.count('@') == 1:
            parts = invalid_email.split('@')
            if len(parts) == 2 and parts[0] and parts[1] and '.' in parts[1]:
                # This might be a valid email, skip it
                assume(False)
        
        # Attempt to create UserRegister with invalid email
        # This should raise a ValidationError
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                email=invalid_email,
                password=password,
                name=name
            )
        
        # Verify that the error is related to email validation
        errors = exc_info.value.errors()
        assert len(errors) > 0, "ValidationError should contain at least one error"
        
        # Check that at least one error is for the email field
        email_errors = [e for e in errors if 'email' in str(e.get('loc', []))]
        assert len(email_errors) > 0, \
            f"Email validation should fail for invalid email: {invalid_email}"

    @settings(max_examples=30, deadline=None)
    @given(
        local_part=st.text(
            alphabet=st.characters(
                min_codepoint=ord('a'),
                max_codepoint=ord('z')
            ) | st.characters(
                min_codepoint=ord('A'),
                max_codepoint=ord('Z')
            ) | st.characters(
                min_codepoint=ord('0'),
                max_codepoint=ord('9')
            ) | st.sampled_from(['.', '-', '_', '+']),
            min_size=1,
            max_size=30
        ).filter(lambda x: x and x[0] not in '.-' and x[-1] not in '.-'),
        domain_name=st.text(
            alphabet=st.characters(
                min_codepoint=ord('a'),
                max_codepoint=ord('z')
            ) | st.characters(
                min_codepoint=ord('A'),
                max_codepoint=ord('Z')
            ) | st.characters(
                min_codepoint=ord('0'),
                max_codepoint=ord('9')
            ) | st.just('-'),
            min_size=1,
            max_size=20
        ).filter(lambda x: x and x[0] not in '-' and x[-1] not in '-'),
        tld=st.text(
            alphabet=st.characters(
                min_codepoint=ord('a'),
                max_codepoint=ord('z')
            ) | st.characters(
                min_codepoint=ord('A'),
                max_codepoint=ord('Z')
            ),
            min_size=2,
            max_size=10
        ),
        password=st.text(min_size=8, max_size=50),
        name=st.text(min_size=1, max_size=50)
    )
    def test_valid_email_formats_are_accepted(
        self,
        local_part: str,
        domain_name: str,
        tld: str,
        password: str,
        name: str
    ):
        """
        Property: Valid email formats must be accepted during registration.
        
        **Validates: Requirements 2.8**
        
        This property ensures that the system accepts properly formatted emails.
        A valid email has the format: local@domain.tld where:
        - local part contains alphanumeric characters and some special chars
        - domain contains alphanumeric characters and hyphens
        - TLD is at least 2 characters long (ASCII only to avoid Unicode issues)
        
        This test complements the invalid email test by ensuring we don't
        reject valid emails (avoiding false positives).
        
        Note: We use ASCII-only characters to avoid edge cases with Unicode
        normalization and international domain names, which are beyond the
        scope of basic email validation.
        """
        # Construct a valid email
        valid_email = f"{local_part}@{domain_name}.{tld}"
        
        # This should NOT raise a ValidationError
        try:
            user_register = UserRegister(
                email=valid_email,
                password=password,
                name=name
            )
            
            # Verify the email was accepted and normalized (lowercased)
            assert user_register.email == valid_email.lower(), \
                "Email should be normalized to lowercase"
            
        except ValidationError as e:
            # If validation fails, this is a test failure
            pytest.fail(
                f"Valid email '{valid_email}' was incorrectly rejected. "
                f"Validation errors: {e.errors()}"
            )

    def test_common_invalid_email_patterns(self):
        """
        Test common invalid email patterns that users might enter.
        
        **Validates: Requirements 2.8**
        
        This test covers specific known-bad email patterns that should
        always be rejected.
        """
        invalid_emails = [
            "",  # Empty string
            " ",  # Whitespace
            "notanemail",  # No @ symbol
            "@example.com",  # Missing local part
            "user@",  # Missing domain
            "user@@example.com",  # Double @
            "user@example",  # Missing TLD
            "user @example.com",  # Space in local part
            "user@exam ple.com",  # Space in domain
            "@",  # Just @
            "user@.com",  # Domain starts with dot
            "user@example.",  # Domain ends with dot
            ".user@example.com",  # Local starts with dot
            "user.@example.com",  # Local ends with dot
        ]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                UserRegister(
                    email=invalid_email,
                    password="ValidPass123",
                    name="Test User"
                )
            
            errors = exc_info.value.errors()
            email_errors = [e for e in errors if 'email' in str(e.get('loc', []))]
            assert len(email_errors) > 0, \
                f"Email '{invalid_email}' should be rejected but wasn't"

    def test_common_valid_email_patterns(self):
        """
        Test common valid email patterns that should be accepted.
        
        **Validates: Requirements 2.8**
        
        This test covers specific known-good email patterns that should
        always be accepted.
        """
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user_name@example.com",
            "user123@example.com",
            "123user@example.com",
            "user@subdomain.example.com",
            "user@example.co.uk",
            "a@b.co",
            "test.email.with.multiple.dots@example.com",
        ]
        
        for valid_email in valid_emails:
            try:
                user_register = UserRegister(
                    email=valid_email,
                    password="ValidPass123",
                    name="Test User"
                )
                assert user_register.email == valid_email.lower()
            except ValidationError as e:
                pytest.fail(
                    f"Valid email '{valid_email}' was incorrectly rejected. "
                    f"Errors: {e.errors()}"
                )
