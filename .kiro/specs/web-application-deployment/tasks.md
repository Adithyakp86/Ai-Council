# Implementation Plan: AI Council Web Application

## Overview

This implementation plan transforms the AI Council Python library into a production-ready multi-user web application. The approach follows an incremental build strategy: start with core infrastructure (database, authentication), add cloud AI integration to replace Ollama, build the FastAPI backend with WebSocket support, create the Next.js frontend, and finally deploy to production infrastructure.

The implementation prioritizes getting a working MVP first, then enhancing with advanced features. Each task builds on previous work, ensuring no orphaned code.

## Tasks

- [x] 1. Project setup and infrastructure foundation
  - [x] 1.1 Initialize backend project structure
    - Create FastAPI project with Poetry for dependency management
    - Set up directory structure: app/, app/api/, app/models/, app/services/, app/core/
    - Configure Python 3.11+ with FastAPI 0.104+, SQLAlchemy 2.0, Alembic, Pydantic v2
    - Create .env.example with all required environment variables
    - Set up .gitignore for Python and Node.js
    - _Requirements: 16.5_
  
  - [x] 1.2 Initialize frontend project structure
    - Create Next.js 14 project with TypeScript and App Router
    - Configure Tailwind CSS and shadcn/ui components
    - Set up directory structure: app/, components/, lib/, hooks/, types/
    - Install dependencies: React Query, Zustand, WebSocket client
    - Create .env.local.example with API URL and WebSocket URL
    - _Requirements: 14.1, 14.7_
  
  - [x] 1.3 Set up PostgreSQL database schema
    - Create Alembic migration for users table (id, email, password_hash, name, role, is_active, created_at, updated_at)
    - Create migration for requests table (id, user_id, content, execution_mode, status, created_at, completed_at)
    - Create migration for responses table (id, request_id, content, confidence, total_cost, execution_time, models_used, orchestration_metadata)
    - Create migration for subtasks table (id, request_id, content, task_type, priority, assigned_model, status, result, confidence, cost, execution_time)
    - Add indexes on user_id, created_at, status fields
    - Add foreign key constraints with CASCADE delete
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6_
  
  - [x] 1.4 Create SQLAlchemy models
    - Implement User model with relationships to requests
    - Implement Request model with relationships to user, response, and subtasks
    - Implement Response model with JSONB fields for metadata
    - Implement Subtask model for orchestration tracking
    - Configure database connection with connection pooling
    - _Requirements: 13.1, 13.2, 13.3, 13.8_
  
  - [x] 1.5 Set up Redis for caching and rate limiting
    - Configure Redis connection with retry logic
    - Implement rate limiting key structures (rate_limit:{user_id}:hour:{timestamp})
    - Implement WebSocket session tracking keys (websocket:active:{request_id})
    - Implement request status cache keys (request:status:{request_id})
    - _Requirements: 10.5, 19.1_
  
  - [x] 1.6 Write property test for database schema
    - **Property: Database Foreign Key Integrity**
    - **Validates: Requirements 13.4, 13.5**
    - Test that deleting a user cascades to delete all their requests and responses
    - Test that deleting a request cascades to delete its response and subtasks

- [-] 2. Authentication and user management
  - [x] 2.1 Implement password hashing with bcrypt
    - Create password hashing utility with bcrypt cost factor 12
    - Implement password verification function
    - Add password strength validation (min 8 chars, uppercase, digit)
    - _Requirements: 2.6, 2.9, 17.1_
  
  - [x] 2.2 Write property test for password hashing
    - **Property 5: Password Hashing with Bcrypt**
    - **Validates: Requirements 2.6, 17.1**
    - Test that hashed passwords never equal plaintext
    - Test that bcrypt cost factor is 12
  
  - [x] 2.3 Implement JWT token generation and validation
    - Create JWT token generation with 7-day expiration
    - Implement token verification with expiration checking
    - Add token refresh endpoint
    - Store secret key in environment variables
    - _Requirements: 2.3, 2.5, 16.5_
  
  - [x] 2.4 Write property test for JWT token expiration
    - **Property 7: JWT Token Validity Period**
    - **Validates: Requirements 2.3**
    - Test that tokens expire exactly 7 days after issuance
  
  - [x] 2.5 Create authentication endpoints
    - Implement POST /api/v1/auth/register endpoint with email validation
    - Implement POST /api/v1/auth/login endpoint with credential verification
    - Implement POST /api/v1/auth/logout endpoint
    - Implement GET /api/v1/auth/me endpoint for current user info
    - Add Pydantic schemas for UserRegister, UserLogin, UserResponse, TokenResponse
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.7, 2.8_
  
  - [x] 2.6 Write property test for email validation
    - **Property 8: Email Format Validation**
    - **Validates: Requirements 2.8**
    - Test that invalid email formats are rejected
  
  - [x] 2.7 Implement authentication middleware
    - Create JWT authentication dependency for FastAPI
    - Extract user_id from valid tokens
    - Return 401 for missing/invalid/expired tokens
    - _Requirements: 9.2, 9.3_
  
  - [x] 2.8 Write unit tests for authentication endpoints
    - Test successful registration creates user
    - Test duplicate email registration fails
    - Test successful login returns token
    - Test invalid credentials fail
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2.9 Git push - Authentication complete
  - Create new branch: feature/authentication
  - Commit all authentication code
  - Push to remote repository
  - Create pull request for review

- [x] 3. Cloud AI provider integration
  - [x] 3.1 Create cloud AI provider adapter base class
    - Implement CloudAIAdapter class that implements AIModel interface from AI Council
    - Add methods: generate_response(), get_model_id()
    - Add provider-specific client creation logic
    - _Requirements: 1.1, 1.2_
  
  - [x] 3.2 Implement Groq API client
    - Create GroqClient with chat completion endpoint
    - Support models: llama3-70b-8192, mixtral-8x7b-32768
    - Handle API authentication with bearer token
    - Parse response to extract generated text
    - _Requirements: 1.1, 1.2_
  
  - [x] 3.3 Implement Together.ai API client
    - Create TogetherClient with inference endpoint
    - Support models: Mixtral-8x7B-Instruct, Llama-2-70b-chat
    - Handle API authentication and response parsing
    - _Requirements: 1.1, 1.2_
  
  - [x] 3.4 Implement OpenRouter API client
    - Create OpenRouterClient with chat completion endpoint
    - Support models: claude-3-sonnet, gpt-4-turbo
    - Add required headers: HTTP-Referer, X-Title
    - _Requirements: 1.1, 1.2_
  
  - [x] 3.5 Implement HuggingFace API client
    - Create HuggingFaceClient with text generation endpoint
    - Support model: Mistral-7B-Instruct
    - Handle inference API response format
    - _Requirements: 1.1, 1.2_
  
  - [x] 3.6 Create model registry configuration
    - Define MODEL_REGISTRY with all cloud models
    - Include capabilities, cost per token, latency, max context for each model
    - Map TaskType to model capabilities
    - _Requirements: 1.2, 1.6, 4.5_
  
  - [x] 3.7 Write property test for cloud AI response parsing
    - **Property 1: Cloud AI Provider Response Parsing**
    - **Validates: Requirements 1.3**
    - Test that valid responses from each provider parse to AgentResponse
  
  - [x] 3.8 Write property test for model routing
    - **Property 2: Model Routing Based on Capabilities**
    - **Validates: Requirements 1.2, 4.5**
    - Test that subtasks are routed to models with matching capabilities
  
  - [x] 3.9 Implement circuit breaker for provider failures
    - Add circuit breaker logic that opens after 5 consecutive failures
    - Implement exponential backoff for retries
    - Add fallback model selection when circuit is open
    - _Requirements: 1.4_
  
  - [x] 3.10 Write property test for circuit breaker
    - **Property 4: Circuit Breaker Activation on Failures**
    - **Validates: Requirements 1.4**
    - Test that 5+ failures open the circuit breaker
  
  - [x] 3.11 Remove Ollama dependencies
    - Remove all Ollama imports and references from codebase
    - Update AI Council initialization to use only cloud adapters
    - Remove Ollama configuration files
    - _Requirements: 1.7_

- [x] 3.12 Git push - Cloud AI integration complete
  - Create new branch: feature/cloud-ai-integration
  - Commit all cloud AI adapter code
  - Push to remote repository
  - Create pull request for review

- [ ] 4. Checkpoint - Verify cloud AI integration
  - Ensure all cloud provider clients work with test API keys
  - Verify model registry is correctly configured
  - Test circuit breaker functionality
  - Ask the user if questions arise

- [x] 5. WebSocket manager and real-time communication
  - [x] 5.1 Implement WebSocket manager
    - Create WebSocketManager class with connection tracking
    - Implement connect(), disconnect(), send_message() methods
    - Add broadcast_progress() for orchestration updates
    - Track connection metadata (user_id, connected_at, last_heartbeat)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 19.1_
  
  - [x] 5.2 Implement WebSocket heartbeat mechanism
    - Create heartbeat_loop() that sends heartbeat every 30 seconds
    - Disconnect inactive connections after 5 minutes
    - _Requirements: 19.4, 19.8_
  
  - [x] 5.3 Implement WebSocket reconnection logic
    - Queue messages when connection drops
    - Replay queued messages on reconnection
    - Resume from last acknowledged message
    - _Requirements: 6.9, 19.2, 19.3_
  
  - [x] 5.4 Write property test for WebSocket heartbeat frequency
    - **Property 28: WebSocket Heartbeat Frequency**
    - **Validates: Requirements 19.4**
    - Test that heartbeats are sent every 30 seconds (±5 seconds)
  
  - [x] 5.5 Create WebSocket endpoint
    - Implement WebSocket endpoint at /ws/{request_id}
    - Validate authentication token from query parameter
    - Register connection with WebSocketManager
    - Handle disconnect and cleanup
    - _Requirements: 19.1, 19.6_
  
  - [x] 5.6 Write unit tests for WebSocket manager
    - Test connection establishment and tracking
    - Test message sending and broadcasting
    - Test reconnection and message replay
    - _Requirements: 19.1, 19.2, 19.3_

- [x] 5.7 Git push - WebSocket implementation complete
  - Create new branch: feature/websocket-realtime
  - Commit all WebSocket code
  - Push to remote repository
  - Create pull request for review

- [-] 6. AI Council orchestration bridge
  - [x] 6.1 Create CouncilOrchestrationBridge class
    - Initialize with WebSocketManager
    - Implement process_request() method that wraps AI Council
    - Create _create_ai_council() to initialize with cloud adapters
    - _Requirements: 4.1, 4.2, 5.2_
  
  - [x] 6.2 Hook into AI Council analysis layer
    - Intercept analysis completion events
    - Send WebSocket message with type "analysis_complete"
    - Include intent and complexity in message data
    - _Requirements: 6.1_
  
  - [x] 6.3 Write property test for analysis started message
    - **Property 23: Analysis Started Message**
    - **Validates: Requirements 6.1**
    - Test that analysis triggers WebSocket message
  
  - [x] 6.4 Hook into AI Council routing layer
    - Intercept routing completion events
    - Send WebSocket message with type "routing_complete"
    - Include model assignments for each subtask
    - _Requirements: 6.3_
  
  - [x] 6.5 Write property test for routing complete message
    - **Property 25: Routing Complete Message**
    - **Validates: Requirements 6.3**
    - Test that routing sends assignments via WebSocket
  
  - [x] 6.6 Hook into AI Council execution layer
    - Intercept subtask execution completion
    - Send WebSocket message with type "execution_progress"
    - Include confidence, cost, execution time for each subtask
    - _Requirements: 6.4, 6.5_
  
  - [x] 6.7 Write property test for execution progress messages
    - **Property 26: Execution Progress Messages**
    - **Validates: Requirements 6.4, 6.5**
    - Test that completed subtasks send progress updates
  
  - [x] 6.8 Hook into AI Council arbitration layer
    - Intercept arbitration decisions
    - Send WebSocket message with type "arbitration_decision"
    - Include conflicting results and selected result with reasoning
    - _Requirements: 6.6_
  
  - [x] 6.9 Hook into AI Council synthesis layer
    - Intercept synthesis progress
    - Send WebSocket message with type "synthesis_progress"
    - Send final response with all metadata
    - _Requirements: 6.7, 6.8_
  
  - [x] 6.10 Write property test for final response completeness
    - **Property 27: Final Response Message Completeness**
    - **Validates: Requirements 6.8**
    - Test that final message includes all required fields
  
  - [ ] 6.11 Write property test for synthesis combines all results
    - **Property 15: Synthesis Combines All Subtask Results**
    - **Validates: Requirements 4.8**
    - Test that final response references all subtask results

- [x] 6.12 Git push - AI Council bridge complete
  - Create new branch: feature/council-orchestration-bridge
  - Commit all orchestration bridge code
  - Push to remote repository
  - Create pull request for review

- [-] 7. Rate limiting implementation
  - [x] 7.1 Implement rate limiter with Redis
    - Create RateLimiter class using Redis counters
    - Implement check_limit() method with sliding window
    - Set limits: 100/hour for authenticated users, 3/hour for demo users
    - Store counters with 1-hour expiration
    - _Requirements: 10.1, 10.2, 10.5, 10.6_
  
  - [x] 7.2 Create rate limiting middleware
    - Apply rate limiter to all API endpoints
    - Return 429 with retry_after on limit exceeded
    - Include reset_at timestamp in error response
    - _Requirements: 10.3, 10.4_
  
  - [x] 7.3 Write property test for rate limit enforcement
    - **Property 34: Rate Limit Enforcement**
    - **Validates: Requirements 10.1, 10.3**
    - Test that 101st request returns 429
  
  - [ ] 7.4 Write property test for rate limit reset time
    - **Property 35: Rate Limit Reset Time Included**
    - **Validates: Requirements 10.4**
    - Test that error response includes retry_after

- [x] 7.5 Git push - Rate limiting complete
  - Create new branch: feature/rate-limiting
  - Commit all rate limiting code
  - Push to remote repository
  - Create pull request for review

- [x] 8. Council processing endpoints
  - [x] 8.1 Implement POST /api/v1/council/process endpoint
    - Validate request content (1-5000 chars) and execution mode
    - Create Request record with status "pending"
    - Establish WebSocket connection
    - Start async processing with CouncilOrchestrationBridge
    - Return request_id and websocket_url
    - _Requirements: 5.1, 5.2, 5.3, 5.7, 5.8_
  
  - [x] 8.2 Write property test for request validation
    - **Property 20: Request Validation and Task Creation**
    - **Validates: Requirements 5.1, 5.8**
    - Test that valid requests create Task and Request record
  
  - [x] 8.3 Write property test for WebSocket establishment
    - **Property 21: WebSocket Establishment for All Requests**
    - **Validates: Requirements 5.3, 19.1**
    - Test that submitted requests establish WebSocket
  
  - [x] 8.4 Implement GET /api/v1/council/status/{request_id} endpoint
    - Query Request record by ID
    - Return status, progress, current_stage
    - Return 404 if request not found
    - _Requirements: 9.6_
  
  - [x] 8.5 Implement GET /api/v1/council/result/{request_id} endpoint
    - Query Request and Response records
    - Return full Council_Response with orchestration metadata
    - Return 404 if request not found
    - _Requirements: 9.6_
  
  - [x] 8.6 Write property test for request completion updates history
    - **Property 22: Request Completion Updates History**
    - **Validates: Requirements 5.9**
    - Test that completed requests update status and create Response
  
  - [x] 8.7 Write unit tests for council endpoints
    - Test successful request submission
    - Test request validation failures
    - Test status and result retrieval
    - _Requirements: 5.1, 5.7, 9.6_

- [x] 8.8 Git push - Council endpoints complete
  - Create new branch: feature/council-endpoints
  - Commit all council processing endpoint code
  - Push to remote repository
  - Create pull request for review

- [x] 9. Execution mode implementation
  - [x] 9.1 Configure execution mode parameters
    - Define FAST mode: minimal decomposition, cheaper models
    - Define BALANCED mode: moderate decomposition, mixed models
    - Define BEST_QUALITY mode: maximum decomposition, premium models, arbitration
    - Pass execution mode to AI Council Core
    - _Requirements: 5.4, 5.5, 5.6_
  
  - [x] 9.2 Write property test for FAST mode uses fewer subtasks
    - **Property 17: FAST Mode Uses Fewer Subtasks**
    - **Validates: Requirements 5.4, 5.6**
    - Test that FAST produces fewer subtasks than BEST_QUALITY
  
  - [x] 9.3 Write property test for FAST mode uses cheaper models
    - **Property 18: FAST Mode Uses Cheaper Models**
    - **Validates: Requirements 5.4, 5.6**
    - Test that FAST uses lower cost_per_token models
  
  - [x] 9.4 Write property test for execution mode affects cost
    - **Property 19: Execution Mode Affects Total Cost**
    - **Validates: Requirements 5.4, 5.5, 5.6**
    - Test that cost_fast ≤ cost_balanced ≤ cost_best_quality

- [x] 9.5 Git push - Execution modes complete
  - Create new branch: feature/execution-modes
  - Commit all execution mode configuration code
  - Push to remote repository
  - Create pull request for review

- [x] 10. Cost calculation and estimation
  - [x] 10.1 Implement cost calculation from token usage
    - Calculate cost per subtask: input_tokens × cost_per_input + output_tokens × cost_per_output
    - Sum costs across all subtasks for total cost
    - Store cost breakdown in orchestration metadata
    - _Requirements: 1.6, 7.5_
  
  - [x] 10.2 Write property test for cost calculation accuracy
    - **Property 3: Cost Calculation Accuracy**
    - **Validates: Requirements 1.6**
    - Test that calculated cost matches sum of token costs
  
  - [x] 10.3 Implement cost estimation for execution modes
    - Estimate based on request length and historical data
    - Return estimates for all three execution modes
    - Cache estimates in Redis for 1 hour
    - _Requirements: 18.1, 18.2, 18.3, 18.4_
  
  - [x] 10.4 Write property test for cost estimates ordering
    - **Property 36: Cost Estimates for All Modes**
    - **Validates: Requirements 18.1, 18.2, 18.3**
    - Test that fast_cost ≤ balanced_cost ≤ best_quality_cost
  
  - [x] 10.5 Write property test for cost estimate based on length
    - **Property 37: Cost Estimate Based on Length**
    - **Validates: Requirements 18.4**
    - Test that longer requests have higher estimates
  
  - [x] 10.6 Implement cost discrepancy logging
    - Compare actual cost to estimated cost after completion
    - Log when |actual - estimate| / estimate > 0.5
    - _Requirements: 18.5_
  
  - [x] 10.7 Write property test for cost discrepancy logging
    - **Property 38: Significant Cost Discrepancy Logging**
    - **Validates: Requirements 18.5**
    - Test that >50% discrepancies are logged

- [x] 10.8 Git push - Cost calculation complete
  - Create new branch: feature/cost-calculation
  - Commit all cost calculation and estimation code
  - Push to remote repository
  - Create pull request for review

- [-] 11. Request history and pagination
  - [x] 11.1 Implement GET /api/v1/council/history endpoint
    - Query user's requests with pagination (page, limit)
    - Support search filter by content substring
    - Support filter by execution_mode
    - Support filter by date range (startDate, endDate)
    - Sort by created_at DESC
    - Return items, total, page, pages
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [x] 11.2 Write property test for pagination
    - **Property: Pagination Correctness**
    - **Validates: Requirements 8.5**
    - Test that pagination returns correct number of items per page
    - Test that page numbers are calculated correctly
  
  - [x] 11.3 Write property test for search filtering
    - **Property: Search Filter Accuracy**
    - **Validates: Requirements 8.6**
    - Test that search returns only matching requests
  
  - [x] 11.4 Write property test for date range filtering
    - **Property: Date Range Filter Correctness**
    - **Validates: Requirements 8.8**
    - Test that only requests within date range are returned

- [x] 11.5 Git push - Request history complete
  - Create new branch: feature/request-history
  - Commit all request history code
  - Push to remote repository
  - Create pull request for review

- [x] 12. User dashboard and statistics
  - [x] 12.1 Implement GET /api/v1/user/stats endpoint
    - Calculate total requests from Request_History
    - Calculate total cost from Response records
    - Calculate average confidence score
    - Group requests by execution_mode
    - Generate time series data for requests over time
    - Identify most frequently used models
    - Calculate average response time
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [x] 12.2 Write property test for statistics calculation
    - **Property: Statistics Accuracy**
    - **Validates: Requirements 8.8**
    - Test that calculated statistics match actual data
  
  - [x] 12.3 Implement caching for dashboard statistics
    - Cache statistics in Redis for 5 minutes
    - Invalidate cache when new request completes
    - _Requirements: 8.8_
  
  - [x] 12.4 Write property test for cache invalidation
    - **Property: Cache Invalidation on New Request**
    - **Validates: Requirements 8.8**
    - Test that cache is invalidated when new request completes

- [x] 12.5 Git push - User dashboard complete
  - Create new branch: feature/user-dashboard
  - Commit all dashboard statistics code
  - Push to remote repository
  - Create pull request for review

- [-] 13. Admin user management
  - [x] 13.1 Implement GET /api/v1/admin/users endpoint
    - Query all users with pagination
    - Return email, registration date, total requests, account status
    - Require admin role for access
    - _Requirements: 11.1, 11.2_
  
  - [x] 13.2 Implement PATCH /api/v1/admin/users/{userId} endpoint
    - Allow admin to disable/enable user accounts
    - Allow admin to promote users to admin role
    - Log all admin actions for audit
    - _Requirements: 11.3, 11.4, 11.7, 11.8_
  
  - [x] 13.3 Implement GET /api/v1/admin/users/{userId} endpoint
    - Return detailed user information
    - Include request history and statistics
    - _Requirements: 11.5_
  
  - [x] 13.4 Implement admin role middleware
    - Check if user has admin role
    - Return 403 Forbidden if not admin
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.7_
  
  - [x] 13.5 Implement first user as admin logic
    - Automatically assign admin role to first registered user
    - _Requirements: 11.6_
  
  - [x] 13.6 Write property test for admin authorization
    - **Property: Admin Authorization**
    - **Validates: Requirements 11.1**
    - Test that non-admin users cannot access admin endpoints
  
  - [x] 13.7 Write property test for audit logging
    - **Property: Admin Action Audit Logging**
    - **Validates: Requirements 11.8**
    - Test that all admin actions are logged

- [x] 13.8 Git push - Admin management complete
  - Create new branch: feature/admin-management
  - Commit all admin management code
  - Push to remote repository
  - Create pull request for review

- [-] 14. System monitoring dashboard
  - [x] 14.1 Implement GET /api/v1/admin/monitoring endpoint
    - Count total registered users
    - Count requests in last 24 hours
    - Calculate average response time
    - Calculate total cost in last 24 hours
    - Calculate success rate
    - Count active WebSocket connections
    - Check Cloud_AI_Provider health status
    - Check circuit breaker states
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_
  
  - [x] 14.2 Implement provider health check
    - Ping each Cloud_AI_Provider
    - Return "healthy", "degraded", or "down"
    - Cache health status for 1 minute
    - _Requirements: 12.7_
  
  - [x] 14.3 Implement monitoring data refresh
    - Auto-refresh monitoring data every 30 seconds
    - Use WebSocket for real-time updates
    - _Requirements: 12.9_
  
  - [x] 14.4 Write property test for monitoring accuracy
    - **Property: Monitoring Data Accuracy**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5**
    - Test that monitoring data matches actual system state

- [x] 14.5 Git push - Monitoring dashboard complete
  - Create new branch: feature/monitoring-dashboard
  - Commit all monitoring code
  - Push to remote repository
  - Create pull request for review

- [x] 15. Backend API complete - Major milestone
  - Create new branch: milestone/backend-api-complete
  - Merge all feature branches
  - Run full test suite
  - Push to remote repository
  - Tag release: v1.0.0-backend

- [x] 16. Frontend - Landing page
  - [x] 16.1 Create landing page layout
    - Hero section with AI Council explanation
    - Features section highlighting multi-agent orchestration
    - How it works section with visual diagrams
    - Pricing section (if applicable)
    - Call-to-action buttons
    - _Requirements: 3.1, 3.2, 3.3, 14.3_
  
  - [x] 16.2 Implement orchestration explanation visualization
    - Interactive diagram showing task decomposition
    - Animation showing parallel execution
    - Visual representation of synthesis
    - _Requirements: 3.2_
  
  - [x] 16.3 Implement demo query interface
    - Simple text input for demo queries
    - Limit to 200 characters
    - Show orchestration steps in real-time
    - Display cost savings comparison
    - _Requirements: 3.4, 3.7, 3.8, 3.10_
  
  - [x] 16.4 Implement demo rate limiting
    - Limit to 3 queries per IP per hour
    - Show remaining demo queries
    - Suggest registration when limit reached
    - _Requirements: 3.5, 3.6_
  
  - [x] 16.5 Implement responsive design
    - Mobile-first approach
    - Breakpoints for tablet and desktop
    - Touch-friendly interactions
    - _Requirements: 14.1_

- [x] 16.6 Git push - Landing page complete
  - Create new branch: feature/frontend-landing-page
  - Commit all landing page code
  - Push to remote repository
  - Create pull request for review

- [x] 17. Frontend - Authentication UI
  - [x] 17.1 Create login page
    - Email and password inputs
    - Form validation with real-time feedback
    - Error message display
    - Link to registration page
    - _Requirements: 2.3, 2.4, 14.4_
  
  - [x] 17.2 Create registration page
    - Email, password, name inputs
    - Password strength indicator
    - Email format validation
    - Terms of service checkbox
    - _Requirements: 2.1, 2.2, 2.8, 2.9, 14.4_
  
  - [x] 17.3 Create user profile page
    - Display user information
    - Edit profile functionality
    - Change password functionality
    - Delete account option
    - _Requirements: 2.1, 2.2_
  
  - [x] 17.4 Implement authentication state management
    - Store JWT token in localStorage
    - Auto-refresh token before expiration
    - Redirect to login on 401 errors
    - Persist user session across page reloads
    - _Requirements: 2.3, 2.5_

- [x] 17.5 Git push - Authentication UI complete
  - Create new branch: feature/frontend-authentication-ui
  - Commit all authentication UI code
  - Push to remote repository
  - Create pull request for review

- [x] 18. Frontend - Main application interface
  - [x] 18.1 Create query input component
    - Multi-line text input
    - Character counter (max 5000)
    - Execution mode selector
    - Cost estimation display
    - Submit button
    - _Requirements: 5.1, 5.7, 18.1, 18.2, 18.3_
  
  - [x] 18.2 Create execution mode selector
    - Radio buttons for FAST, BALANCED, BEST_QUALITY
    - Description for each mode
    - Estimated cost and time for each
    - Recommended mode highlighting
    - _Requirements: 5.4, 5.5, 5.6_
  
  - [x] 18.3 Create orchestration visualization component
    - Visual diagram of orchestration stages
    - Real-time progress updates via WebSocket
    - Animated transitions between stages
    - Show active agents and completed subtasks
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.10_
  
  - [x] 18.4 Create progress timeline component
    - Chronological list of orchestration events
    - Auto-scroll to latest event
    - Expandable details for each event
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  
  - [x] 18.5 Create response viewer component
    - Display final synthesized response
    - Syntax highlighting for code blocks
    - Copy to clipboard button
    - Download as JSON button
    - _Requirements: 7.1, 7.10, 7.11_
  
  - [x] 18.6 Create orchestration breakdown component
    - Expandable tree view of task decomposition
    - Table showing model contributions
    - Cost breakdown by model and subtask
    - Parallel execution efficiency metrics
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9_
  
  - [x] 18.7 Create request history page
    - Paginated list of past requests
    - Search and filter functionality
    - Click to view full details
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [x] 18.8 Create user dashboard page
    - Overview cards with key metrics
    - Charts for requests over time
    - Model usage breakdown
    - Cost trends
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [x] 18.9 Git push - Main application UI complete
  - Create new branch: feature/frontend-main-application
  - Commit all main application UI code
  - Push to remote repository
  - Create pull request for review

- [x] 19. Frontend - Admin interface
  - [x] 19.1 Create admin dashboard page
    - System overview cards
    - User management table
    - Monitoring visualizations
    - _Requirements: 11.1, 11.2, 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [x] 19.2 Create user management interface
    - List all users with pagination
    - Enable/disable user accounts
    - Promote users to admin
    - View user details
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [x] 19.3 Create system monitoring visualizations
    - Real-time charts for system metrics
    - Provider health status indicators
    - Circuit breaker state display
    - Active connections counter
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8_
  
  - [x] 19.4 Implement admin role protection
    - Check user role before rendering admin UI
    - Redirect non-admin users to main app
    - _Requirements: 11.1_

- [x] 19.5 Git push - Admin interface complete
  - Create new branch: feature/frontend-admin-interface
  - Commit all admin interface code
  - Push to remote repository
  - Create pull request for review

- [x] 20. Frontend - Styling and themes
  - [x] 20.1 Implement dark/light theme toggle
    - Theme switcher component
    - Persist theme preference in localStorage
    - Apply theme to all components
    - _Requirements: 14.2_
  
  - [x] 20.2 Implement responsive design
    - Mobile-first approach (320px+)
    - Tablet breakpoints (768px+)
    - Desktop breakpoints (1024px+)
    - 4K support (2560px+)
    - _Requirements: 14.1_
  
  - [x] 20.3 Implement loading states
    - Skeleton loaders for content
    - Progress indicators for actions
    - Smooth transitions
    - _Requirements: 14.5_
  
  - [x] 20.4 Implement error states
    - User-friendly error messages
    - Suggested actions for errors
    - Error boundary components
    - _Requirements: 14.6, 15.1, 15.2, 15.3, 15.4_
  
  - [x] 20.5 Optimize accessibility
    - ARIA labels for all interactive elements
    - Keyboard navigation support
    - Screen reader compatibility
    - Achieve Lighthouse accessibility score 90+
    - _Requirements: 14.8_
  
  - [x] 20.6 Optimize performance
    - Code splitting for routes
    - Lazy loading for components
    - Image optimization
    - Achieve initial load under 3 seconds on 3G
    - _Requirements: 14.9_

- [x] 20.7 Git push - Styling and themes complete
  - Create new branch: feature/frontend-styling-themes
  - Commit all styling code
  - Push to remote repository
  - Create pull request for review

- [x] 21. Frontend complete - Major milestone
  - Create new branch: milestone/frontend-complete
  - Merge all frontend feature branches
  - Run full test suite
  - Push to remote repository
  - Tag release: v1.0.0-frontend

- [-] 22. Multi-AI Provider Integration & Comprehensive Testing
  - [x] 22.1 Set up Ollama for local testing
    - Install Ollama from https://ollama.ai (Windows/Mac/Linux)
    - Pull required models: `ollama pull llama2`, `ollama pull mistral`, `ollama pull codellama`, `ollama pull phi`
    - Verify Ollama is running: `curl http://localhost:11434/api/generate`
    - Test basic inference with sample prompt
    - Document Ollama setup steps in backend/docs/OLLAMA_SETUP.md
    - Note: Ollama provides free, local AI models with no API costs
  
  - [x] 22.2 Implement Ollama adapter for AI Council
    - Create backend/app/services/cloud_ai/ollama_adapter.py
    - Implement OllamaClient class extending CloudAIAdapter base
    - Add methods: generate_response(), get_model_id(), health_check()
    - Support models: llama2 (7B, 13B), mistral (7B), codellama (7B), phi (2.7B), neural-chat (7B)
    - Handle streaming responses from Ollama API
    - Add error handling for connection failures
    - Test adapter with multiple prompts and models
  
  - [x] 22.3 Add Ollama models to MODEL_REGISTRY
    - Add ollama-llama2-7b with capabilities: [REASONING, RESEARCH, CREATIVE_OUTPUT]
    - Add ollama-mistral-7b with capabilities: [REASONING, CODE_GENERATION]
    - Add ollama-codellama-7b with capabilities: [CODE_GENERATION, DEBUGGING]
    - Add ollama-phi-2.7b with capabilities: [REASONING, CREATIVE_OUTPUT]
    - Set cost_per_token to 0.0 (local, free)
    - Set average_latency based on local hardware
    - Set max_context for each model
    - Set reliability_score based on testing
  
  - [x] 22.4 Add Google AI / Gemini API integration
    - Sign up at https://makersuite.google.com/app/apikey
    - Get free API key (Free tier: 60 requests/minute, no billing required)
    - Create backend/app/services/cloud_ai/gemini_adapter.py
    - Implement GeminiClient for gemini-pro and gemini-pro-vision models
    - Add to MODEL_REGISTRY with capabilities: [REASONING, RESEARCH, CREATIVE_OUTPUT, FACT_CHECKING]
    - Set cost_per_token (free tier has no cost, but track usage)
    - Test with sample prompts including multimodal (text + image)
    - Document setup in backend/docs/GEMINI_SETUP.md with screenshots
    - Include rate limit handling (60 req/min)
  
  - [x] 22.5 Add HuggingFace Inference API integration
    - Sign up at https://huggingface.co
    - Get free API token from https://huggingface.co/settings/tokens
    - Create backend/app/services/cloud_ai/huggingface_adapter.py
    - Implement HuggingFaceClient for inference API
    - Support models: mistralai/Mistral-7B-Instruct-v0.2, meta-llama/Llama-2-7b-chat-hf, google/flan-t5-xxl
    - Add to MODEL_REGISTRY with appropriate capabilities
    - Set cost_per_token to 0.0 (free tier)
    - Handle rate limits (free tier: ~1000 requests/day)
    - Test with multiple models
    - Document setup in backend/docs/HUGGINGFACE_SETUP.md
  
  - [x] 22.6 Add OpenRouter integration
    - Sign up at https://openrouter.ai
    - Get API key (includes free credits on signup: $1-5)
    - Create backend/app/services/cloud_ai/openrouter_adapter.py
    - Implement OpenRouterClient with unified API interface
    - Support models: openai/gpt-3.5-turbo, anthropic/claude-instant-1, meta-llama/llama-2-70b-chat, google/palm-2-chat-bison
    - Add to MODEL_REGISTRY with accurate pricing per model
    - Handle HTTP-Referer and X-Title headers (required by OpenRouter)
    - Test with multiple model providers through OpenRouter
    - Document setup in backend/docs/OPENROUTER_SETUP.md
    - Note: Free credits expire, but provides access to many models
  
  - [x] 22.7 Add Together AI integration
    - Sign up at https://api.together.xyz
    - Get API key (free credits on signup: $25)
    - Create backend/app/services/cloud_ai/together_adapter.py
    - Implement TogetherClient for inference API
    - Support models: togethercomputer/llama-2-70b-chat, mistralai/Mixtral-8x7B-Instruct-v0.1, NousResearch/Nous-Hermes-2-Yi-34B
    - Add to MODEL_REGISTRY with capabilities and pricing
    - Test with sample prompts
    - Document setup in backend/docs/TOGETHER_SETUP.md
    - Note: Free credits are generous for prototyping
  
  - [x] 22.8 Add OpenAI integration (optional, paid)
    - Sign up at https://platform.openai.com
    - Get API key (requires payment method, but has $5 free trial)
    - Create backend/app/services/cloud_ai/openai_adapter.py
    - Implement OpenAIClient for chat completions
    - Support models: gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview
    - Add to MODEL_REGISTRY with accurate pricing
    - Test with sample prompts
    - Document setup in backend/docs/OPENAI_SETUP.md
    - Mark as optional in documentation
  
  - [x] 22.9 Add Qwen (Alibaba Cloud) integration (optional)
    - Sign up at https://dashscope.aliyun.com
    - Get API key (free tier available in some regions)
    - Create backend/app/services/cloud_ai/qwen_adapter.py
    - Implement QwenClient for DashScope API
    - Support models: qwen-turbo, qwen-plus, qwen-max
    - Add to MODEL_REGISTRY
    - Test with sample prompts
    - Document setup in backend/docs/QWEN_SETUP.md
    - Mark as optional in documentation
  
  - [x] 22.10 Create unified provider configuration system
    - Create backend/app/core/provider_config.py
    - Implement ProviderConfig class to manage all API keys and endpoints
    - Load configuration from environment variables with fallbacks
    - Validate API keys on application startup
    - Log which providers are available and which are disabled
    - Create provider health check system
    - Update backend/.env.example with all provider keys and clear instructions
    - Add comments explaining which providers are free vs paid
  
  - [x] 22.11 Implement dynamic provider selection and orchestration
    - Update CouncilOrchestrationBridge to detect available providers at runtime
    - Only initialize adapters for providers with valid API keys
    - Prioritize providers based on: availability > cost > latency > capabilities
    - Implement intelligent fallback when primary provider fails
    - Distribute subtasks across multiple providers for parallel execution
    - Log provider selection decisions for each subtask
    - Track which provider handled which subtask in response metadata
  
  - [ ] 22.12 Create comprehensive provider testing script
    - Create backend/test_all_providers.py
    - Test each configured provider with identical sample prompts
    - Measure response time for each provider
    - Measure response quality (length, coherence)
    - Calculate cost per request for each provider
    - Test error handling and retry logic
    - Generate detailed comparison report
    - Save results to backend/docs/PROVIDER_COMPARISON.md with tables and charts
  
  - [x] 22.13 Test orchestration with multiple providers
    - Submit complex query: "Explain quantum computing, write a Python example, and suggest real-world applications"
    - Verify AI Council decomposes into multiple subtasks
    - Verify subtasks are distributed across available providers
    - Verify parallel execution with mixed providers (local + cloud)
    - Verify arbitration works when providers give different answers
    - Verify synthesis combines results from different providers coherently
    - Measure total cost and time vs single-provider approach
    - Document test results in backend/docs/ORCHESTRATION_TEST_RESULTS.md
  
  - [x] 22.14 Create provider health monitoring system
    - Implement health check endpoint for each provider
    - Check API key validity without consuming credits
    - Check response time with lightweight test request
    - Check rate limit status
    - Display provider status in admin dashboard (healthy/degraded/down)
    - Set up alerts when provider is down or slow
    - Cache health status for 1 minute to avoid excessive checks
  
  - [x] 22.15 Create provider cost tracking and analytics
    - Track cost per provider per request in database
    - Calculate total cost by provider over time
    - Display cost breakdown in user dashboard
    - Display cost breakdown in admin monitoring dashboard
    - Generate monthly cost reports by provider
    - Alert when costs exceed thresholds
    - Show cost savings from using free providers
  
  - [ ] 22.16 Write comprehensive integration tests
    - Test with only Ollama (local, free)
    - Test with only free cloud providers (Gemini, HuggingFace)
    - Test with mixed local + cloud providers
    - Test failover when provider is unavailable
    - Test rate limit handling and backoff
    - Test cost calculation accuracy across providers
    - Test orchestration quality with different provider combinations
    - Verify all tests pass before proceeding

- [x] 22.17 Git push - Multi-provider integration complete
  - Create new branch: feature/multi-provider-integration
  - Commit all provider adapters, tests, and documentation
  - Push to remote repository
  - Create pull request for review

- [x] 23. User API Key Management System
  - [x] 23.1 Create API key storage database schema
    - Add user_api_keys table with fields: id, user_id, provider_name, api_key_encrypted, is_active, created_at, updated_at, last_used_at
    - Add foreign key constraint to users table
    - Add unique constraint on (user_id, provider_name)
    - Create Alembic migration: backend/alembic/versions/YYYYMMDD_add_user_api_keys.py
    - Run migration: `alembic upgrade head`
    - Verify table created in database
  
  - [x] 23.2 Implement API key encryption system
    - Create backend/app/core/encryption.py
    - Use Fernet symmetric encryption (from cryptography library)
    - Generate encryption key from environment variable ENCRYPTION_KEY
    - Implement encrypt_api_key(plain_key: str) -> str function
    - Implement decrypt_api_key(encrypted_key: str) -> str function
    - Add key rotation support for future security updates
    - Test encryption/decryption with sample keys
  
  - [x] 23.3 Create UserAPIKey SQLAlchemy model
    - Create backend/app/models/user_api_key.py
    - Define UserAPIKey model with all fields
    - Add relationship to User model
    - Add methods: encrypt_key(), decrypt_key(), test_validity()
    - Add validation for provider_name (must be in supported providers list)
  
  - [x] 23.4 Create API key management endpoints
    - POST /api/v1/user/api-keys - Add new API key for a provider
    - GET /api/v1/user/api-keys - List user's configured providers (keys masked)
    - PUT /api/v1/user/api-keys/{provider} - Update API key for provider
    - DELETE /api/v1/user/api-keys/{provider} - Delete API key for provider
    - POST /api/v1/user/api-keys/{provider}/test - Test API key validity
    - Add Pydantic schemas: APIKeyCreate, APIKeyUpdate, APIKeyResponse
    - Implement in backend/app/api/user_api_keys.py
  
  - [x] 23.5 Update orchestration to use user API keys
    - Modify CouncilOrchestrationBridge.process_request()
    - Load user's API keys from database at request time
    - Initialize provider adapters with user's keys if available
    - Fall back to system API keys if user hasn't configured provider
    - Track which API keys (user vs system) were used for each subtask
    - Store this information in response metadata
    - Log API key usage for billing/analytics
  
  - [x] 23.6 Create settings page in frontend
    - Create frontend/app/settings/page.tsx
    - Add "API Keys" section with card layout
    - List all supported providers with logos/icons
    - Show which providers user has configured (green checkmark)
    - Show which providers are using system defaults (yellow warning)
    - Add "Add API Key" button for each provider
    - Show masked API keys (e.g., "sk-...xyz" showing first 3 and last 3 chars)
    - Add "Test" button to validate each configured key
    - Add "Delete" button to remove configured key
  
  - [x] 23.7 Create API key configuration dialog
    - Create frontend/components/settings/api-key-dialog.tsx
    - Show provider name and logo
    - Show link to get API key (e.g., "Get your Gemini API key")
    - Input field for API key (password type, with show/hide toggle)
    - "Test Key" button to validate before saving
    - Show validation result (success/error message)
    - "Save" button to store encrypted key
    - Show benefits of adding this provider (capabilities, cost)
  
  - [x] 23.8 Add settings link to sidebar navigation
    - Add "Settings" link to sidebar with gear icon
    - Position above "Admin" link (if admin) or at bottom
    - Highlight when user has no API keys configured
    - Show badge with count of configured providers
  
  - [x] 23.9 Create API key setup wizard for new users
    - Create frontend/components/onboarding/api-key-wizard.tsx
    - Show on first login if user has no API keys configured
    - Explain benefits of adding own API keys vs using system defaults
    - Guide through adding at least one free provider (Gemini or HuggingFace)
    - Show step-by-step instructions with screenshots
    - Allow skipping to use system default keys
    - Mark wizard as completed in user preferences
  
  - [ ] 23.10 Write tests for API key management
    - Test API key encryption/decryption
    - Test API key CRUD operations via API
    - Test API key validation for each provider
    - Test orchestration with user API keys
    - Test fallback to system keys when user key is invalid
    - Test security: users can only access their own keys
    - Verify encrypted keys are never exposed in API responses

- [x] 23.11 Git push - API key management complete
  - Create new branch: feature/user-api-key-management
  - Commit all API key management code and tests
  - Push to remote repository
  - Create pull request for review

- [x] 24. Enhanced Chat Dashboard UI (IDE-Style Layout)
  - [x] 24.1 Create new chat page with split-pane layout
    - Create frontend/app/chat/page.tsx (new main interface after login)
    - Implement CSS Grid layout: left pane (40%) + right pane (60%)
    - Left pane contains: chat input, execution mode, analytics preview
    - Right pane initially hidden, slides in when response arrives
    - Make responsive: stack vertically on mobile (<768px)
    - Add resize handle between panes for desktop
  
  - [x] 24.2 Create enhanced chat input component
    - Create frontend/components/chat/enhanced-chat-input.tsx
    - Center-aligned in left pane
    - Multi-line textarea with auto-resize (min 3 lines, max 10 lines)
    - Character counter: "0 / 5000" below input
    - Send button (paper plane icon) or Enter to send
    - Shift+Enter for new line
    - Execution mode selector (FAST/BALANCED/BEST_QUALITY) below input
    - Real-time cost estimate display
    - Disable input during processing
  
  - [x] 24.3 Create chat history sidebar
    - Create frontend/components/chat/chat-history-sidebar.tsx
    - Collapsible sidebar on far left (can be toggled)
    - List previous conversations with timestamps
    - Show first 50 chars of each conversation
    - Click to load conversation into main chat
    - Search conversations by content
    - Delete conversation option (with confirmation)
    - "New Chat" button at top
  
  - [x] 24.4 Create response panel component
    - Create frontend/components/chat/response-panel.tsx
    - Slides in from right with smooth animation when response arrives
    - Header: "Response" with close button
    - Main content area with syntax highlighting (using react-syntax-highlighter)
    - Copy button (copies full response to clipboard)
    - Download button (downloads as .txt or .md)
    - Share button (generates shareable link)
    - Scroll to top button when content is long
  
  - [x] 24.5 Create analytics section below chat input
    - Create frontend/components/chat/analytics-preview.tsx
    - Compact card showing: Total Queries, Total Cost, Avg Confidence
    - Mini chart showing queries over last 7 days
    - Provider usage breakdown (pie chart or bars)
    - Collapsible section (collapsed by default on mobile)
    - Click to expand for more details
    - Link to full analytics page
  
  - [x] 24.6 Implement smooth layout transitions
    - When user sends message: chat input moves to top-left
    - Analytics section moves below chat input
    - Response panel slides in from right
    - Use CSS transitions (300ms ease-in-out)
    - Add loading skeleton in response panel during processing
    - Smooth scroll to show response when ready
  
  - [x] 24.7 Create orchestration detail panel
    - Create frontend/components/chat/orchestration-detail-panel.tsx
    - Expandable section in response panel
    - Show "Orchestration Details" accordion
    - Task decomposition tree (expandable nodes)
    - Model assignments for each subtask
    - Execution timeline with timestamps
    - Cost breakdown by subtask and provider
    - Confidence scores for each subtask
    - Total execution time and parallel efficiency
  
  - [x] 24.8 Add real-time progress indicators
    - Create frontend/components/chat/progress-indicator.tsx
    - Show in response panel during processing
    - Progress bar with percentage (0-100%)
    - Current stage text: "Analyzing...", "Routing...", "Executing...", "Synthesizing..."
    - Show active models with spinning icons
    - Show completed subtasks count: "3 / 5 subtasks completed"
    - Animate updates via WebSocket messages
    - Pulse animation for active stage
  
  - [x] 24.9 Implement keyboard shortcuts
    - Ctrl/Cmd + Enter: Send message
    - Ctrl/Cmd + K: Focus chat input
    - Ctrl/Cmd + B: Toggle chat history sidebar
    - Ctrl/Cmd + /: Toggle orchestration details
    - Esc: Close response panel
    - Ctrl/Cmd + N: New chat
    - Create help modal showing all shortcuts (Ctrl/Cmd + ?)
  
  - [x] 24.10 Create mobile-responsive layout
    - Stack layout vertically on mobile
    - Chat input fixed at bottom
    - Response slides up from bottom (full screen)
    - Swipe down to close response
    - Hamburger menu for chat history sidebar
    - Touch-friendly button sizes (min 44x44px)
    - Test on iOS Safari and Android Chrome
  
  - [x] 24.11 Add theme support to new layout
    - Ensure dark/light theme works throughout
    - Syntax highlighting theme switches with app theme
    - Smooth theme transitions (200ms)
    - Persist theme preference in localStorage
    - Add theme toggle in sidebar
  
  - [x] 24.12 Update navigation flow
    - After login, redirect to /chat (not /dashboard)
    - Update sidebar: Chat (home icon), History, Analytics, Settings, Admin
    - Add breadcrumbs: Home > Chat
    - Update landing page CTA to point to /chat after login
    - Move old dashboard content to /analytics route

- [x] 24.13 Git push - Enhanced chat UI complete
  - Create new branch: feature/enhanced-chat-ui
  - Commit all chat UI components and styles
  - Push to remote repository
  - Create pull request for review

- [x] 25. Complete User Flow Implementation & Testing
  - [x] 25.1 Update landing page CTAs
    - Change "Get Started" button to redirect to /register
    - Change "Try Demo" to open demo modal (not redirect)
    - Add "Sign In" button in navigation header
    - Update hero section copy to mention multi-provider support
    - Add provider logos to features section
  
  - [x] 25.2 Update authentication flow
    - After successful login, redirect to /chat (not /dashboard)
    - After successful registration, redirect to /chat with welcome toast
    - Show API key setup wizard on first login (if no keys configured)
    - Allow skipping wizard to use system defaults
    - Store wizard completion in user preferences
  
  - [x] 25.3 Update sidebar navigation
    - Reorder links: Chat (home), History, Analytics, Settings, Admin (if admin)
    - Add icons: MessageSquare, History, BarChart3, Settings, Shield
    - Highlight active route with background color
    - Add user profile dropdown at bottom with: Profile, Logout
    - Show user's name and email in dropdown
    - Add avatar (initials or uploaded image)
  
  - [x] 25.4 Create welcome tour for new users
    - Create frontend/components/onboarding/welcome-tour.tsx
    - Use react-joyride or similar library
    - Show on first visit to /chat
    - Steps: 1) Chat input, 2) Execution modes, 3) Settings for API keys, 4) History sidebar
    - Allow skipping tour
    - Store tour completion in localStorage
    - Add "Restart Tour" option in help menu
  
  - [x] 25.5 Add contextual help throughout app
    - Add "?" icon next to execution modes with tooltip explanations
    - Add tooltips for all interactive elements
    - Create help modal accessible from sidebar (? icon)
    - Include: Keyboard shortcuts, FAQ, Getting started guide
    - Add "What's this?" links in complex sections
    - Add inline hints for first-time actions
  
  - [x] 25.6 Implement session persistence
    - Save current conversation in localStorage
    - Restore conversation on page reload
    - Auto-save draft messages every 2 seconds
    - Warn before leaving page with unsaved changes
    - Clear localStorage on logout
    - Add "Resume last session" option on login
  
  - [x] 25.7 Add conversation sharing functionality
    - Create frontend/app/share/[id]/page.tsx for public view
    - Add "Share" button in response panel
    - Generate unique shareable link
    - Create public view (no auth required) showing conversation
    - Add privacy controls: Public / Private / Unlisted
    - Add "Copy link" and "Embed code" options
    - Track view count for shared conversations
  
  - [x] 25.8 Comprehensive end-to-end user testing
    - Test flow: Landing → Register → API Key Wizard → Chat → Response
    - Test with different screen sizes: Mobile (375px), Tablet (768px), Desktop (1920px)
    - Test with different browsers: Chrome, Firefox, Safari, Edge
    - Test keyboard navigation throughout app
    - Test with screen reader (NVDA or VoiceOver)
    - Test all error scenarios (invalid API key, network error, etc.)
    - Document any issues found in TESTING_REPORT.md

- [x] 25.9 Git push - Complete user flow implementation
  - Create new branch: feature/complete-user-flow
  - Commit all user flow improvements and tests
  - Push to remote repository
  - Create pull request for review

- [x] 26. Supabase Database Setup (PRIORITY - Required for Login/Register)
  - [x] 26.1 Create Supabase account and project
    - Sign up at https://supabase.com
    - Create new project with strong password
    - Wait for project provisioning (2-3 minutes)
    - Save database password securely
  
  - [x] 26.2 Get Supabase credentials
    - Navigate to Project Settings → Database
    - Copy Connection String (Pooler) for DATABASE_URL
    - Navigate to Project Settings → API
    - Copy Project URL for NEXT_PUBLIC_SUPABASE_URL
    - Copy anon public key for NEXT_PUBLIC_SUPABASE_ANON_KEY
  
  - [x] 26.3 Configure backend environment
    - Update backend/.env with Supabase DATABASE_URL
    - Format: postgresql://postgres.xxxxx:[PASSWORD]@aws-0-region.pooler.supabase.com:6543/postgres
    - Update SECRET_KEY with strong 32+ character key
    - Configure CORS_ORIGINS=["http://localhost:3000"]
  
  - [x] 26.4 Configure frontend environment
    - Update frontend/.env.local with Supabase credentials
    - Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    - Set NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
    - Set NEXT_PUBLIC_SUPABASE_URL from Supabase
    - Set NEXT_PUBLIC_SUPABASE_ANON_KEY from Supabase
  
  - [x] 26.5 Run database migrations
    - Execute: cd backend && python -m poetry run alembic upgrade head
    - Verify tables created in Supabase Table Editor
    - Check for migration errors in console
    - Verify users, requests, responses, subtasks tables exist
  
  - [x] 26.6 Test database connection
    - Restart backend server
    - Check logs for successful database connection
    - Test user registration endpoint via API docs (http://localhost:8000/api/v1/docs)
    - Verify data appears in Supabase dashboard
  
  - [x] 26.7 Set up Redis (optional but recommended)
    - Option A: Use Docker - docker run -d -p 6379:6379 redis:alpine
    - Option B: Use Upstash - create free Redis database at https://upstash.com
    - Update REDIS_URL in backend/.env
    - Test Redis connection (backend will log connection status)
  
  - [x] 26.8 Test authentication flow
    - Open frontend at http://localhost:3000
    - Click "Get Started" to register
    - Fill in email, password, name
    - Verify registration succeeds
    - Verify redirect to chat page
    - Logout and login again
    - Verify login works

- [x] 26.9 Git push - Supabase integration complete
  - Create new branch: feature/supabase-integration
  - Commit environment configuration updates
  - Update documentation with Supabase setup
  - Push to remote repository
  - Create pull request for review

- [ ] 27. Multi-Provider API Keys Setup Guide
  - [ ] 27.1 Create comprehensive API keys setup guide
    - Create backend/API_KEYS_QUICK_START.md
    - List all supported providers with links
    - Indicate which are free vs paid
    - Provide step-by-step instructions for each
  
  - [ ] 27.2 Document free provider setup
    - **Ollama (Local, Free)**:
      - Install from https://ollama.ai
      - Run: ollama pull llama2 && ollama pull mistral
      - Add OLLAMA_ENDPOINT=http://localhost:11434 to .env
    
    - **Google Gemini (Free Tier)**:
      - Get key from https://makersuite.google.com/app/apikey
      - Free: 60 requests/minute
      - Add GEMINI_API_KEY=your_key to .env
    
    - **HuggingFace (Free)**:
      - Get token from https://huggingface.co/settings/tokens
      - Free: ~1000 requests/day
      - Add HUGGINGFACE_TOKEN=your_token to .env
    
    - **OpenRouter (Free Credits)**:
      - Sign up at https://openrouter.ai
      - Get $1-5 free credits
      - Add OPENROUTER_API_KEY=your_key to .env
    
    - **Together AI (Free Credits)**:
      - Sign up at https://api.together.xyz
      - Get $25 free credits
      - Add TOGETHER_API_KEY=your_key to .env
  
  - [ ] 27.3 Document paid provider setup (optional)
    - **OpenAI (Paid, $5 trial)**:
      - Sign up at https://platform.openai.com
      - Requires payment method
      - Add OPENAI_API_KEY=your_key to .env
    
    - **Groq (Free Beta)**:
      - Sign up at https://console.groq.com
      - Currently free during beta
      - Add GROQ_API_KEY=your_key to .env
    
    - **Qwen/Alibaba Cloud (Regional)**:
      - Sign up at https://dashscope.aliyun.com
      - Free tier in some regions
      - Add QWEN_API_KEY=your_key to .env
  
  - [ ] 27.4 Create automated setup script
    - Create backend/setup_api_keys.ps1 (PowerShell)
    - Prompt user for each API key
    - Validate key format
    - Test each key with simple API call
    - Update .env file automatically
    - Show summary of configured providers
  
  - [ ] 27.5 Create API key testing utility
    - Create backend/test_all_providers.py
    - Test each configured provider
    - Show which providers are working
    - Show response time for each
    - Show estimated cost per 1000 tokens
    - Generate comparison report
  
  - [ ] 27.6 Update backend/.env.example
    - Add all provider API key placeholders
    - Add comments explaining each provider
    - Mark which are free vs paid
    - Add links to get each key
    - Add example values format
  
  - [ ] 27.7 Create troubleshooting guide
    - Common API key errors and solutions
    - Rate limit handling
    - Provider-specific issues
    - How to verify keys are working
    - How to switch providers

- [ ] 27.8 Git push - API keys setup guide complete
  - Create new branch: feature/api-keys-setup-guide
  - Commit all documentation and scripts
  - Push to remote repository
  - Create pull request for review

- [ ] 28. Provider Integration Testing
  - [ ] 28.1 Test with Ollama only (local, free)
    - Start Ollama service: ollama serve
    - Disable all cloud providers in .env (comment out API keys)
    - Restart backend
    - Submit test query: "Explain machine learning in simple terms"
    - Verify orchestration uses only Ollama models
    - Verify response quality is acceptable
    - Verify cost is $0.00
    - Document results in backend/docs/TEST_RESULTS_OLLAMA.md
  
  - [ ] 28.2 Test with free cloud providers only
    - Stop Ollama service
    - Enable Gemini, HuggingFace, OpenRouter (free tier) in .env
    - Restart backend
    - Submit test query: "Write a Python function to calculate fibonacci numbers"
    - Verify orchestration distributes across free providers
    - Verify parallel execution works
    - Verify response quality
    - Check cost (should be $0.00 or minimal)
    - Document results in backend/docs/TEST_RESULTS_FREE_CLOUD.md
  
  - [ ] 28.3 Test with all providers enabled
    - Enable all providers (Ollama + all cloud)
    - Submit complex query: "Explain quantum computing, write a Python simulation, and suggest real-world applications"
    - Verify AI Council decomposes into multiple subtasks
    - Verify orchestration uses best provider for each subtask
    - Verify parallel execution across mixed providers
    - Verify arbitration if providers disagree
    - Verify synthesis combines results coherently
    - Check total cost and compare to single-provider approach
    - Document results in backend/docs/TEST_RESULTS_ALL_PROVIDERS.md
  
  - [ ] 28.4 Test user API key functionality
    - Register new test user account
    - Go to Settings → API Keys
    - Add Gemini API key
    - Submit query
    - Verify user's Gemini key is used (check logs)
    - Verify cost is tracked correctly
    - Remove user's Gemini key
    - Submit another query
    - Verify fallback to system Gemini key
    - Document results in backend/docs/TEST_RESULTS_USER_API_KEYS.md
  
  - [ ] 28.5 Test error scenarios
    - Test with invalid API key → verify user-friendly error message
    - Test with rate-limited provider → verify fallback to other provider
    - Test with provider timeout → verify retry logic
    - Test with network error → verify graceful degradation
    - Document all error scenarios in backend/docs/ERROR_HANDLING_TEST.md
  
  - [ ] 28.6 Performance testing
    - Test with 10 concurrent users submitting queries
    - Measure average response time
    - Measure database query times
    - Measure WebSocket connection stability
    - Identify bottlenecks
    - Document results in backend/docs/PERFORMANCE_TEST_RESULTS.md

- [ ] 28.7 Git push - Provider testing complete
  - Create new branch: feature/provider-integration-testing
  - Commit all test reports
  - Push to remote repository
  - Create pull request for review

- [ ] 29. Final Integration & Comprehensive Testing
  - [ ] 26.1 Environment setup and API key configuration
    - **USER ACTION REQUIRED**: Set up all API keys in backend/.env
    - Add OLLAMA_ENDPOINT=http://localhost:11434 (if using Ollama)
    - Add GEMINI_API_KEY=your_key_here (get from https://makersuite.google.com)
    - Add HUGGINGFACE_TOKEN=your_token_here (get from https://huggingface.co/settings/tokens)
    - Add OPENROUTER_API_KEY=your_key_here (get from https://openrouter.ai)
    - Add TOGETHER_API_KEY=your_key_here (get from https://api.together.xyz)
    - Add OPENAI_API_KEY=your_key_here (optional, get from https://platform.openai.com)
    - Add QWEN_API_KEY=your_key_here (optional, get from https://dashscope.aliyun.com)
    - Add ENCRYPTION_KEY=your_32_char_key_here (generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`)
    - Verify all keys are valid by running: `python backend/test_all_providers.py`
  
  - [ ] 26.2 Test with Ollama only (local, free)
    - Start Ollama service: `ollama serve`
    - Disable all cloud providers in .env (comment out API keys)
    - Start backend: `cd backend && poetry run uvicorn app.main:app --reload`
    - Start frontend: `cd frontend && npm run dev`
    - Submit test query: "Explain machine learning in simple terms"
    - Verify orchestration uses only Ollama models
    - Verify response quality is acceptable
    - Verify cost is $0.00
    - Document results in docs/TEST_RESULTS_OLLAMA.md
  
  - [ ] 26.3 Test with free cloud providers only
    - Stop Ollama service
    - Enable Gemini, HuggingFace, OpenRouter (free tier) in .env
    - Restart backend
    - Submit test query: "Write a Python function to calculate fibonacci numbers"
    - Verify orchestration distributes across free providers
    - Verify parallel execution works
    - Verify response quality
    - Check cost (should be $0.00 or minimal)
    - Document results in docs/TEST_RESULTS_FREE_CLOUD.md
  
  - [ ] 26.4 Test with all providers enabled
    - Enable all providers (Ollama + all cloud)
    - Submit complex query: "Explain quantum computing, write a Python simulation, and suggest real-world applications"
    - Verify AI Council decomposes into multiple subtasks
    - Verify orchestration uses best provider for each subtask
    - Verify parallel execution across mixed providers
    - Verify arbitration if providers disagree
    - Verify synthesis combines results coherently
    - Check total cost and compare to single-provider approach
    - Document results in docs/TEST_RESULTS_ALL_PROVIDERS.md
  
  - [ ] 26.5 Test user API key functionality
    - Register new test user account
    - Go to Settings → API Keys
    - Add Gemini API key
    - Submit query
    - Verify user's Gemini key is used (check logs)
    - Verify cost is tracked correctly
    - Remove user's Gemini key
    - Submit another query
    - Verify fallback to system Gemini key
    - Document results in docs/TEST_RESULTS_USER_API_KEYS.md
  
  - [ ] 26.6 Test complete user journey
    - Start from landing page (http://localhost:3000)
    - Click "Get Started" → Register new account
    - Complete API key setup wizard (add at least one free provider)
    - Submit first query in chat interface
    - Watch real-time orchestration progress
    - View response in IDE-style layout
    - Expand orchestration details
    - Check analytics section
    - Go to History page, verify query is saved
    - Go to Analytics page, verify stats are updated
    - Go to Settings, test adding/removing API keys
    - If admin: Go to Admin panel, verify monitoring works
    - Document complete journey with screenshots in docs/USER_JOURNEY_TEST.md
  
  - [ ] 26.7 Test error scenarios and edge cases
    - Test with invalid API key → verify user-friendly error message
    - Test with rate-limited provider → verify fallback to other provider
    - Test with provider timeout → verify retry logic
    - Test with network error → verify graceful degradation
    - Test with very long query (>5000 chars) → verify validation
    - Test with empty query → verify validation
    - Test with special characters in query → verify sanitization
    - Test concurrent requests from same user → verify rate limiting
    - Document all error scenarios in docs/ERROR_HANDLING_TEST.md
  
  - [ ] 26.8 Performance and load testing
    - Use Apache Bench or similar tool
    - Test with 10 concurrent users submitting queries
    - Test with 50 concurrent users
    - Measure average response time
    - Measure database query times
    - Measure WebSocket connection stability
    - Identify bottlenecks (database, AI providers, WebSocket)
    - Optimize if response time > 10 seconds
    - Document results in docs/PERFORMANCE_TEST_RESULTS.md
  
  - [ ] 26.9 Create comprehensive final test report
    - Compile all test results into docs/FINAL_TEST_REPORT.md
    - Include: All test scenarios, screenshots, videos
    - List all providers tested with success/failure status
    - Include performance metrics (response times, costs)
    - List any issues found and their severity
    - Include recommendations for improvements
    - Add conclusion: Ready for production / Needs fixes

- [ ] 26.10 Git push - Final integration testing complete
  - Create new branch: feature/final-integration-testing
  - Commit all test reports and any bug fixes
  - Push to remote repository
  - Create pull request for review

- [ ] 27. API documentation
  - [ ] 22.1 Configure OpenAPI/Swagger documentation
    - Enable automatic OpenAPI spec generation
    - Serve interactive docs at /api/docs
    - Serve ReDoc at /api/redoc
    - _Requirements: 20.1, 20.2, 20.3_
  
  - [ ] 22.2 Add endpoint descriptions and examples
    - Document all endpoints with descriptions
    - Add request/response examples
    - Mark authentication requirements
    - Document error codes
    - _Requirements: 20.4, 20.5, 20.7_
  
  - [ ] 22.3 Create code examples
    - Python examples for all endpoints
    - JavaScript examples for all endpoints
    - cURL examples for all endpoints
    - _Requirements: 20.6_
  
  - [ ] 22.4 Create getting started guide
    - API authentication guide
    - Quick start examples
    - Common use cases
    - Troubleshooting section
    - _Requirements: 20.8_

- [ ] 22.5 Git push - API documentation complete
  - Create new branch: feature/api-documentation
  - Commit all documentation code
  - Push to remote repository
  - Create pull request for review

- [ ] 23. Error handling and logging
  - [ ] 23.1 Implement centralized error handling
    - Global exception handler for FastAPI
    - Standardized error response format
    - Error code mapping
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.8_
  
  - [ ] 23.2 Implement user-friendly error messages
    - Map technical errors to user-friendly messages
    - Provide suggested actions for common errors
    - Hide sensitive information from error messages
    - _Requirements: 15.1, 15.2, 15.3, 15.4_
  
  - [ ] 23.3 Implement centralized logging
    - Configure structured logging
    - Log all errors with context
    - Log all API requests
    - Exclude sensitive information from logs
    - _Requirements: 15.7, 17.6_
  
  - [ ] 23.4 Integrate error tracking (Sentry)
    - Set up Sentry for error tracking
    - Configure error grouping
    - Set up alerts for critical errors
    - _Requirements: 15.7_
  
  - [ ] 23.5 Implement WebSocket error handling
    - Handle connection failures gracefully
    - Implement automatic reconnection (up to 3 attempts)
    - Queue messages during reconnection
    - _Requirements: 15.6, 19.2, 19.3, 19.7_
  
  - [ ] 23.6 Implement database error handling
    - Handle connection failures with retries
    - Display maintenance message when DB unavailable
    - _Requirements: 13.9, 15.5_

- [ ] 23.7 Git push - Error handling complete
  - Create new branch: feature/error-handling-logging
  - Commit all error handling code
  - Push to remote repository
  - Create pull request for review

- [ ] 24. Security implementation
  - [ ] 24.1 Implement HTTPS/TLS
    - Configure SSL certificates
    - Enforce HTTPS for all connections
    - _Requirements: 16.6, 17.2_
  
  - [ ] 24.2 Implement input validation and sanitization
    - Validate all user inputs
    - Sanitize inputs to prevent injection attacks
    - _Requirements: 17.3_
  
  - [ ] 24.3 Implement CSRF protection
    - Add CSRF tokens to state-changing operations
    - Validate CSRF tokens on backend
    - _Requirements: 17.4_
  
  - [ ] 24.4 Implement secure HTTP headers
    - Set Content-Security-Policy header
    - Set X-Frame-Options header
    - Set X-Content-Type-Options header
    - Set Strict-Transport-Security header
    - _Requirements: 17.5_
  
  - [ ] 24.5 Implement rate limiting for login
    - Limit login attempts to prevent brute force
    - Implement exponential backoff
    - _Requirements: 17.7_
  
  - [ ] 24.6 Implement CORS configuration
    - Configure CORS to allow only frontend domain
    - Set appropriate CORS headers
    - _Requirements: 16.7_
  
  - [ ] 24.7 Implement data deletion
    - Implement account deletion endpoint
    - Delete all user data within 30 days
    - _Requirements: 17.8, 17.9_

- [ ] 24.8 Git push - Security implementation complete
  - Create new branch: feature/security-implementation
  - Commit all security code
  - Push to remote repository
  - Create pull request for review

- [ ] 25. Testing and quality assurance
  - [ ] 25.1 Write unit tests for backend
    - Test all service functions
    - Test all utility functions
    - Achieve 80%+ code coverage
  
  - [ ] 25.2 Write integration tests for backend
    - Test complete API workflows
    - Test database interactions
    - Test WebSocket communication
  
  - [ ] 25.3 Write property-based tests
    - Run all property tests defined in tasks
    - Verify all correctness properties
  
  - [ ] 25.4 Write unit tests for frontend
    - Test all React components
    - Test all utility functions
    - Achieve 70%+ code coverage
  
  - [ ] 25.5 Write end-to-end tests
    - Test complete user workflows
    - Test authentication flow
    - Test query submission and response
    - Test admin workflows
  
  - [ ] 25.6 Run full test suite
    - Run all backend tests
    - Run all frontend tests
    - Fix any failing tests
  
  - [ ] 25.7 Perform manual testing
    - Test on different browsers (Chrome, Firefox, Safari, Edge)
    - Test on different devices (mobile, tablet, desktop)
    - Test all user flows
    - Test error scenarios
  
  - [ ] 25.8 Run Lighthouse audit
    - Achieve performance score 90+
    - Achieve accessibility score 90+
    - Achieve best practices score 90+
    - Achieve SEO score 90+

- [ ] 25.9 Git push - Testing complete
  - Create new branch: feature/testing-qa
  - Commit all test code
  - Push to remote repository
  - Create pull request for review

- [ ] 26. Supabase database integration
  - [ ] 26.1 Create Supabase account and project
    - Sign up at https://supabase.com
    - Create new project with strong password
    - Wait for project provisioning (2-3 minutes)
    - Save database password securely
  
  - [ ] 26.2 Get Supabase credentials
    - Navigate to Project Settings → Database
    - Copy Connection String (Pooler) for DATABASE_URL
    - Navigate to Project Settings → API
    - Copy Project URL for NEXT_PUBLIC_SUPABASE_URL
    - Copy anon public key for NEXT_PUBLIC_SUPABASE_ANON_KEY
  
  - [ ] 26.3 Configure backend environment
    - Update backend/.env with Supabase DATABASE_URL
    - Update SECRET_KEY with strong 32+ character key
    - Configure CORS_ORIGINS for frontend URL
    - Set up Redis URL (Upstash or local)
  
  - [ ] 26.4 Configure frontend environment
    - Create frontend/.env.local from template
    - Set NEXT_PUBLIC_API_URL to backend URL
    - Set NEXT_PUBLIC_WS_URL to WebSocket URL
    - Set NEXT_PUBLIC_SUPABASE_URL from Supabase
    - Set NEXT_PUBLIC_SUPABASE_ANON_KEY from Supabase
  
  - [ ] 26.5 Run database migrations
    - Execute: cd backend && python -m poetry run alembic upgrade head
    - Verify tables created in Supabase Table Editor
    - Check for migration errors in console
  
  - [ ] 26.6 Test database connection
    - Restart backend server
    - Check logs for successful database connection
    - Test user registration endpoint
    - Verify data appears in Supabase dashboard
  
  - [ ] 26.7 Set up Redis (optional but recommended)
    - Option A: Use Docker - docker run -d -p 6379:6379 redis:alpine
    - Option B: Use Upstash - create free Redis database at https://upstash.com
    - Update REDIS_URL in backend/.env
    - Test Redis connection
  
  - [ ] 26.8 Add AI API keys
    - Get Groq API key from https://console.groq.com
    - Get Together AI key from https://api.together.xyz
    - Get OpenRouter key from https://openrouter.ai
    - Get Hugging Face token from https://huggingface.co/settings/tokens
    - Add all keys to backend/.env
  
  - [ ] 26.9 Test complete setup
    - Start backend: cd backend && python -m poetry run uvicorn app.main:app --reload
    - Start frontend: cd frontend && npm run dev
    - Open http://localhost:3000
    - Register new account
    - Login successfully
    - Submit test query
    - Verify data persists in Supabase

- [ ] 26.10 Git push - Supabase integration complete
  - Create new branch: feature/supabase-integration
  - Commit environment configuration files
  - Update documentation with Supabase setup
  - Push to remote repository
  - Create pull request for review

- [ ] 27. Deployment preparation
  - [ ] 26.1 Create environment configuration
    - Create .env.example files
    - Document all environment variables
    - Create separate configs for dev/staging/prod
    - _Requirements: 16.5_
  
  - [ ] 26.2 Set up PostgreSQL database
    - Create database on Railway or Supabase
    - Run migrations
    - Set up connection pooling
    - _Requirements: 16.3, 13.8_
  
  - [ ] 26.3 Set up Redis cache
    - Create Redis instance on Upstash
    - Configure connection
    - Test caching functionality
    - _Requirements: 16.4_
  
  - [ ] 26.4 Configure API keys
    - Set up Groq API key
    - Set up Together.ai API key
    - Set up OpenRouter API key
    - Set up HuggingFace API key
    - Store keys in environment variables
    - _Requirements: 1.5, 16.5_
  
  - [ ] 26.5 Create health check endpoints
    - Implement /health endpoint
    - Check database connectivity
    - Check Redis connectivity
    - Check AI provider connectivity
    - _Requirements: 16.8_
  
  - [ ] 26.6 Configure automatic restarts
    - Set up process manager (PM2 or similar)
    - Configure restart on crash
    - _Requirements: 16.9_

- [ ] 26.7 Git push - Deployment preparation complete
  - Create new branch: feature/deployment-preparation
  - Commit all deployment configuration
  - Push to remote repository
  - Create pull request for review

- [ ] 27. Deploy backend to Railway/Render
  - [ ] 27.1 Create Railway/Render account
    - Sign up for Railway or Render
    - Connect GitHub repository
  
  - [ ] 27.2 Configure backend deployment
    - Create new project
    - Connect to GitHub repository
    - Set environment variables
    - Configure build command
    - Configure start command
    - _Requirements: 16.2_
  
  - [ ] 27.3 Deploy backend
    - Trigger initial deployment
    - Monitor deployment logs
    - Verify deployment success
    - Test health check endpoint
  
  - [ ] 27.4 Configure automatic deployments
    - Enable automatic deployments from main branch
    - Test automatic deployment with a commit
    - _Requirements: 16.2_
  
  - [ ] 27.5 Configure custom domain (optional)
    - Purchase domain (if not already owned)
    - Configure DNS settings
    - Set up SSL certificate
    - _Requirements: 16.6_

- [ ] 27.6 Git push - Backend deployment complete
  - Tag release: v1.0.0-backend-deployed
  - Push tag to remote repository

- [ ] 28. Deploy frontend to Vercel
  - [ ] 28.1 Create Vercel account
    - Sign up for Vercel
    - Connect GitHub repository
  
  - [ ] 28.2 Configure frontend deployment
    - Import project from GitHub
    - Set environment variables (API URL, WebSocket URL)
    - Configure build settings
    - _Requirements: 16.1_
  
  - [ ] 28.3 Deploy frontend
    - Trigger initial deployment
    - Monitor deployment logs
    - Verify deployment success
    - Test application in production
  
  - [ ] 28.4 Configure automatic deployments
    - Enable automatic deployments from main branch
    - Test automatic deployment with a commit
    - _Requirements: 16.1_
  
  - [ ] 28.5 Configure custom domain
    - Add custom domain to Vercel
    - Configure DNS settings
    - Verify SSL certificate
    - _Requirements: 16.6_

- [ ] 28.6 Git push - Frontend deployment complete
  - Tag release: v1.0.0-frontend-deployed
  - Push tag to remote repository

- [ ] 29. Post-deployment testing
  - [ ] 29.1 Test production backend
    - Test all API endpoints
    - Test WebSocket connections
    - Test authentication flow
    - Test rate limiting
  
  - [ ] 29.2 Test production frontend
    - Test all pages and components
    - Test user registration and login
    - Test query submission and response
    - Test request history
    - Test dashboard
  
  - [ ] 29.3 Test end-to-end workflows
    - Register new user
    - Submit query
    - View real-time orchestration
    - View response
    - Check request history
    - View dashboard
  
  - [ ] 29.4 Test on multiple devices
    - Test on mobile devices
    - Test on tablets
    - Test on desktop browsers
  
  - [ ] 29.5 Monitor production logs
    - Check for errors in logs
    - Monitor performance metrics
    - Check database queries
  
  - [ ] 29.6 Load testing
    - Test with multiple concurrent users
    - Monitor response times
    - Check for memory leaks
    - Verify rate limiting works

- [ ] 29.7 Git push - Post-deployment testing complete
  - Document test results
  - Create issue for any bugs found
  - Push documentation to repository

- [ ] 30. Documentation and launch
  - [ ] 30.1 Create user documentation
    - Getting started guide
    - How to submit queries
    - Understanding orchestration results
    - Managing account
    - FAQ section
  
  - [ ] 30.2 Create developer documentation
    - API integration guide
    - Authentication guide
    - Code examples
    - Webhook documentation (if applicable)
  
  - [ ] 30.3 Create deployment documentation
    - Deployment guide
    - Environment variables reference
    - Troubleshooting guide
    - Backup and recovery procedures
  
  - [ ] 30.4 Create README.md
    - Project overview
    - Features list
    - Technology stack
    - Installation instructions
    - Deployment instructions
    - Contributing guidelines
  
  - [ ] 30.5 Create launch checklist
    - Verify all features work
    - Verify all documentation is complete
    - Verify monitoring is set up
    - Verify backups are configured
    - Prepare announcement

- [ ] 30.6 Git push - Documentation complete
  - Tag release: v1.0.0
  - Push final release to repository
  - Create GitHub release with changelog

- [ ] 31. Launch and monitoring
  - [ ] 31.1 Announce launch
    - Post on social media
    - Send to mailing list (if applicable)
    - Post on relevant forums/communities
  
  - [ ] 31.2 Set up monitoring
    - Configure uptime monitoring
    - Set up error alerts
    - Configure performance monitoring
    - Set up cost alerts
  
  - [ ] 31.3 Monitor initial usage
    - Watch for errors
    - Monitor performance
    - Collect user feedback
    - Track key metrics
  
  - [ ] 31.4 Create feedback channels
    - Set up support email
    - Create feedback form
    - Monitor social media mentions
  
  - [ ] 31.5 Plan next iteration
    - Collect feature requests
    - Prioritize improvements
    - Plan next release

## 🎉 Congratulations!

You've successfully transformed AI Council into a production-ready multi-user web application!

**What you've built:**
- ✅ Beautiful web application accessible online
- ✅ Real cloud AI models (no Ollama!)
- ✅ Multi-user authentication and management
- ✅ Real-time orchestration visualization
- ✅ Request history and analytics
- ✅ Admin panel for monitoring
- ✅ Comprehensive API documentation
- ✅ Production deployment on Vercel + Railway
- ✅ Professional quality with testing and monitoring

**Next steps:**
- Monitor usage and performance
- Collect user feedback
- Plan feature enhancements
- Scale infrastructure as needed
- Build community around your product

**You're now live! 🚀**


## Extended Tasks: Multi-Provider Testing & Enhanced UI

- [ ] 32. Multi-AI Provider Integration & Testing
  - [ ] 32.1 Set up Ollama for local testing
    - Install Ollama from https://ollama.ai
    - Pull models: ollama pull llama2, ollama pull mistral, ollama pull codellama
    - Verify Ollama is running on http://localhost:11434
    - Test basic inference with: curl http://localhost:11434/api/generate
    - Document Ollama setup in backend/docs/OLLAMA_SETUP.md
  
  - [ ] 32.2 Implement Ollama adapter
    - Create backend/app/services/cloud_ai/ollama_adapter.py
    - Implement OllamaClient class with generate() method
    - Add Ollama models to MODEL_REGISTRY with local endpoint
    - Support models: llama2, mistral, codellama, phi, neural-chat
    - Test adapter with sample prompts
  
  - [ ] 32.3 Add Google AI / Gemini API integration
    - Sign up at https://makersuite.google.com/app/apikey
    - Get free API key (free tier: 60 requests/minute)
    - Create backend/app/services/cloud_ai/gemini_adapter.py
    - Implement GeminiClient for gemini-pro and gemini-pro-vision
    - Add to MODEL_REGISTRY with capabilities and costs
    - Test with sample prompts
    - Document setup in backend/docs/GEMINI_SETUP.md
  
  - [ ] 32.4 Add HuggingFace Inference API integration
    - Sign up at https://huggingface.co
    - Get free API token from https://huggingface.co/settings/tokens
    - Create backend/app/services/cloud_ai/huggingface_adapter.py
    - Support models: mistralai/Mistral-7B-Instruct-v0.2, meta-llama/Llama-2-7b-chat-hf
    - Add to MODEL_REGISTRY
    - Test with sample prompts
    - Document setup in backend/docs/HUGGINGFACE_SETUP.md
  
  - [ ] 32.5 Add OpenRouter integration
    - Sign up at https://openrouter.ai
    - Get API key (includes free credits on signup)
    - Create backend/app/services/cloud_ai/openrouter_adapter.py
    - Support models: openai/gpt-3.5-turbo, anthropic/claude-instant, meta-llama/llama-2-70b-chat
    - Add to MODEL_REGISTRY
    - Test with sample prompts
    - Document setup in backend/docs/OPENROUTER_SETUP.md
  
  - [ ] 32.6 Add Together AI integration
    - Sign up at https://api.together.xyz
    - Get API key (free credits on signup)
    - Create backend/app/services/cloud_ai/together_adapter.py
    - Support models: togethercomputer/llama-2-70b-chat, mistralai/Mixtral-8x7B-Instruct-v0.1
    - Add to MODEL_REGISTRY
    - Test with sample prompts
    - Document setup in backend/docs/TOGETHER_SETUP.md
  
  - [ ] 32.7 Add OpenAI integration
    - Sign up at https://platform.openai.com
    - Get API key (requires payment but has free trial credits)
    - Create backend/app/services/cloud_ai/openai_adapter.py
    - Support models: gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview
    - Add to MODEL_REGISTRY with accurate pricing
    - Test with sample prompts
    - Document setup in backend/docs/OPENAI_SETUP.md
  
  - [ ] 32.8 Add Qwen (Alibaba Cloud) integration
    - Sign up at https://dashscope.aliyun.com
    - Get API key (free tier available)
    - Create backend/app/services/cloud_ai/qwen_adapter.py
    - Support models: qwen-turbo, qwen-plus, qwen-max
    - Add to MODEL_REGISTRY
    - Test with sample prompts
    - Document setup in backend/docs/QWEN_SETUP.md
  
  - [ ] 32.9 Create unified provider configuration system
    - Create backend/app/core/provider_config.py
    - Implement ProviderConfig class to manage all API keys
    - Load API keys from environment variables
    - Validate API keys on startup
    - Log which providers are available
    - Create backend/.env.example with all provider keys
  
  - [ ] 32.10 Implement dynamic provider selection
    - Update CouncilOrchestrationBridge to detect available providers
    - Only use providers with valid API keys
    - Prioritize providers based on availability and cost
    - Implement fallback logic when primary provider fails
    - Log provider selection decisions
  
  - [ ] 32.11 Create comprehensive provider testing script
    - Create backend/test_all_providers.py
    - Test each provider with sample prompts
    - Measure response time for each provider
    - Measure cost for each provider
    - Generate comparison report
    - Save results to backend/docs/PROVIDER_COMPARISON.md
  
  - [ ] 32.12 Test orchestration with multiple providers
    - Submit complex query requiring multiple subtasks
    - Verify AI Council distributes work across available providers
    - Verify parallel execution works with mixed providers
    - Verify arbitration works when providers disagree
    - Verify synthesis combines results from different providers
    - Document test results in backend/docs/ORCHESTRATION_TEST_RESULTS.md
  
  - [ ] 32.13 Create provider health monitoring
    - Implement health check for each provider
    - Check API key validity
    - Check rate limits
    - Check response times
    - Display provider status in admin dashboard
    - Alert when provider is down or slow
  
  - [ ] 32.14 Create provider cost tracking
    - Track cost per provider per request
    - Calculate total cost by provider
    - Display cost breakdown in user dashboard
    - Display cost breakdown in admin monitoring
    - Generate cost reports
  
  - [ ] 32.15 Write comprehensive integration tests
    - Test with only Ollama (local)
    - Test with only free cloud providers
    - Test with mixed local + cloud providers
    - Test failover when provider is unavailable
    - Test rate limit handling
    - Test cost calculation accuracy
    - Verify all tests pass

- [ ] 32.16 Git push - Multi-provider integration complete
  - Create new branch: feature/multi-provider-integration
  - Commit all provider adapters and tests
  - Push to remote repository
  - Create pull request for review

- [ ] 33. User API Key Management System
  - [ ] 33.1 Create API key storage schema
    - Add user_api_keys table to database
    - Fields: id, user_id, provider_name, api_key_encrypted, is_active, created_at, updated_at
    - Create Alembic migration
    - Run migration
  
  - [ ] 33.2 Implement API key encryption
    - Create backend/app/core/encryption.py
    - Use Fernet symmetric encryption for API keys
    - Store encryption key in environment variable
    - Implement encrypt_api_key() and decrypt_api_key() functions
  
  - [ ] 33.3 Create API key management endpoints
    - POST /api/v1/user/api-keys - Add new API key
    - GET /api/v1/user/api-keys - List user's API keys (masked)
    - PUT /api/v1/user/api-keys/{provider} - Update API key
    - DELETE /api/v1/user/api-keys/{provider} - Delete API key
    - POST /api/v1/user/api-keys/{provider}/test - Test API key validity
  
  - [ ] 33.4 Update orchestration to use user API keys
    - Modify CouncilOrchestrationBridge to check for user API keys
    - Prioritize user's API keys over system API keys
    - Fall back to system API keys if user hasn't provided keys
    - Track which API keys were used for each request
  
  - [ ] 33.5 Create settings page in frontend
    - Create frontend/app/settings/page.tsx
    - Add "API Keys" section
    - List all supported providers
    - Show which providers user has configured
    - Add form to add/update API keys
    - Add test button to validate API keys
    - Show masked API keys (e.g., "sk-...xyz")
  
  - [ ] 33.6 Add API key management to sidebar
    - Add "Settings" link to sidebar navigation
    - Add icon for settings (gear/cog icon)
    - Highlight when user has no API keys configured
  
  - [ ] 33.7 Create API key setup wizard
    - Show wizard on first login if no API keys configured
    - Guide user through adding at least one API key
    - Explain benefits of adding multiple providers
    - Allow skipping to use system default keys
  
  - [ ] 33.8 Write tests for API key management
    - Test API key encryption/decryption
    - Test API key CRUD operations
    - Test API key validation
    - Test orchestration with user API keys
    - Test fallback to system keys

- [ ] 33.9 Git push - API key management complete
  - Create new branch: feature/user-api-key-management
  - Commit all API key management code
  - Push to remote repository
  - Create pull request for review

- [ ] 34. Enhanced Chat Dashboard UI (IDE-Style Layout)
  - [ ] 34.1 Redesign dashboard layout
    - Create frontend/app/chat/page.tsx (new main chat interface)
    - Implement split-pane layout: left (chat) + right (response)
    - Use CSS Grid for responsive layout
    - Left pane: 40% width on desktop, full width on mobile
    - Right pane: 60% width on desktop, slides in on mobile
  
  - [ ] 34.2 Create enhanced chat input component
    - Create frontend/components/chat/chat-input.tsx
    - Center-aligned chat input box
    - Multi-line textarea with auto-resize
    - Character counter (0/5000)
    - Send button (or Enter to send, Shift+Enter for new line)
    - Execution mode selector below input
    - Cost estimate display
  
  - [ ] 34.3 Create chat history sidebar
    - Create frontend/components/chat/chat-history-sidebar.tsx
    - Show previous conversations
    - Click to load conversation
    - Search conversations
    - Delete conversation option
  
  - [ ] 34.4 Create response panel component
    - Create frontend/components/chat/response-panel.tsx
    - Slides in from right when response arrives
    - Shows response content with syntax highlighting
    - Shows orchestration visualization
    - Shows cost and time metrics
    - Copy button, download button, share button
  
  - [ ] 34.5 Create analytics section below chat
    - Create frontend/components/chat/analytics-section.tsx
    - Shows user statistics (total queries, total cost, avg confidence)
    - Shows recent activity chart
    - Shows provider usage breakdown
    - Collapsible section
  
  - [ ] 34.6 Implement smooth transitions
    - Animate chat section moving to left when response arrives
    - Animate response panel sliding in from right
    - Smooth scroll to response
    - Loading animations during processing
  
  - [ ] 34.7 Create orchestration detail panel
    - Create frontend/components/chat/orchestration-detail.tsx
    - Expandable panel showing full orchestration flow
    - Task decomposition tree
    - Model assignments
    - Execution timeline
    - Cost breakdown by subtask
    - Confidence scores
  
  - [ ] 34.8 Add real-time progress indicators
    - Show progress bar during processing
    - Show current stage (Analysis, Routing, Execution, Synthesis)
    - Show active models
    - Show completed subtasks count
    - Animate progress updates via WebSocket
  
  - [ ] 34.9 Implement keyboard shortcuts
    - Ctrl/Cmd + Enter: Send message
    - Ctrl/Cmd + K: Focus chat input
    - Ctrl/Cmd + /: Toggle sidebar
    - Esc: Close response panel
    - Document shortcuts in help modal
  
  - [ ] 34.10 Create mobile-responsive layout
    - Stack layout vertically on mobile
    - Chat input at bottom
    - Response slides up from bottom
    - Swipe gestures to navigate
    - Hamburger menu for sidebar
  
  - [ ] 34.11 Add theme support to new layout
    - Ensure dark/light theme works
    - Add syntax highlighting theme switching
    - Smooth theme transitions
  
  - [ ] 34.12 Update navigation flow
    - Landing page → Sign in → Chat dashboard (not old dashboard)
    - Move old dashboard to /analytics route
    - Update sidebar navigation
    - Add breadcrumbs

- [ ] 34.13 Git push - Enhanced chat UI complete
  - Create new branch: feature/enhanced-chat-ui
  - Commit all chat UI code
  - Push to remote repository
  - Create pull request for review

- [ ] 35. Complete User Flow Implementation
  - [ ] 35.1 Update landing page CTA
    - Change "Get Started" button to redirect to /register
    - Change "Try Demo" to show demo in modal
    - Add "Sign In" button in navigation
  
  - [ ] 35.2 Update authentication flow
    - After successful login, redirect to /chat (not /dashboard)
    - After successful registration, redirect to /chat with welcome message
    - Show API key setup wizard on first login
  
  - [ ] 35.3 Update sidebar navigation
    - Reorder: Chat (home), History, Analytics, Settings, Admin (if admin)
    - Add icons for each section
    - Highlight active route
    - Add user profile dropdown at bottom
  
  - [ ] 35.4 Create welcome tour
    - Show interactive tour on first visit to /chat
    - Highlight chat input
    - Highlight execution mode selector
    - Highlight settings for API keys
    - Allow skipping tour
    - Store tour completion in localStorage
  
  - [ ] 35.5 Add contextual help
    - Add "?" icon next to execution modes with explanations
    - Add tooltips for all interactive elements
    - Add help modal accessible from sidebar
    - Include keyboard shortcuts reference
  
  - [ ] 35.6 Implement session persistence
    - Save current conversation in localStorage
    - Restore conversation on page reload
    - Auto-save draft messages
    - Warn before leaving with unsaved changes
  
  - [ ] 35.7 Add sharing functionality
    - Generate shareable link for conversations
    - Create public view for shared conversations
    - Add privacy controls (public/private)
    - Add embed code for conversations
  
  - [ ] 35.8 Create comprehensive user testing
    - Test complete flow: Landing → Register → Chat → Response
    - Test with different screen sizes
    - Test with different browsers
    - Test keyboard navigation
    - Test with screen readers
    - Document any issues found

- [ ] 35.9 Git push - User flow complete
  - Create new branch: feature/complete-user-flow
  - Commit all user flow improvements
  - Push to remote repository
  - Create pull request for review

- [ ] 36. Final Integration & End-to-End Testing
  - [ ] 36.1 Set up all API keys in .env
    - Add Ollama endpoint (local)
    - Add Google Gemini API key
    - Add HuggingFace token
    - Add OpenRouter API key
    - Add Together AI API key
    - Add OpenAI API key (optional)
    - Add Qwen API key (optional)
    - Verify all keys are valid
  
  - [ ] 36.2 Test with Ollama only
    - Start Ollama service
    - Submit test query
    - Verify orchestration uses only Ollama models
    - Verify response quality
    - Document results
  
  - [ ] 36.3 Test with free cloud providers only
    - Disable Ollama
    - Enable Gemini, HuggingFace, OpenRouter, Together
    - Submit test query
    - Verify orchestration distributes across providers
    - Verify response quality
    - Document results
  
  - [ ] 36.4 Test with all providers enabled
    - Enable all providers
    - Submit complex query requiring multiple subtasks
    - Verify orchestration uses best provider for each subtask
    - Verify parallel execution across providers
    - Verify cost optimization
    - Document results
  
  - [ ] 36.5 Test user API key functionality
    - Add user API keys in settings
    - Submit query
    - Verify user's API keys are used
    - Verify cost is tracked correctly
    - Remove user API keys
    - Verify fallback to system keys
  
  - [ ] 36.6 Test complete user journey
    - Start from landing page
    - Register new account
    - Complete API key setup wizard
    - Submit first query
    - View orchestration in real-time
    - View response in IDE-style layout
    - Check analytics section
    - View history
    - Test settings page
    - Test admin panel (if admin)
  
  - [ ] 36.7 Test error scenarios
    - Test with invalid API key
    - Test with rate-limited provider
    - Test with provider timeout
    - Test with network error
    - Verify graceful error handling
    - Verify user-friendly error messages
  
  - [ ] 36.8 Performance testing
    - Test with 10 concurrent users
    - Test with 50 concurrent users
    - Measure response times
    - Measure database query times
    - Identify bottlenecks
    - Optimize if needed
  
  - [ ] 36.9 Create comprehensive test report
    - Document all test scenarios
    - Include screenshots/videos
    - List all providers tested
    - Include performance metrics
    - List any issues found
    - Save as docs/FINAL_TEST_REPORT.md

- [ ] 36.10 Git push - Final testing complete
  - Create new branch: feature/final-integration-testing
  - Commit test report and any fixes
  - Push to remote repository
  - Create pull request for review

- [ ] 37. Documentation & Launch Preparation
  - [ ] 37.1 Create comprehensive setup guide
    - Create docs/COMPLETE_SETUP_GUIDE.md
    - Include all provider setup instructions
    - Include screenshots for each step
    - Include troubleshooting section
    - Include FAQ
  
  - [ ] 37.2 Create video tutorials
    - Record setup walkthrough
    - Record user flow walkthrough
    - Record API key configuration
    - Record admin features
    - Upload to YouTube/Vimeo
    - Add links to documentation
  
  - [ ] 37.3 Update README.md
    - Add project description
    - Add features list with screenshots
    - Add supported AI providers list
    - Add quick start guide
    - Add deployment instructions
    - Add contributing guidelines
    - Add license information
  
  - [ ] 37.4 Create API documentation
    - Document all endpoints
    - Include request/response examples
    - Include authentication guide
    - Include rate limiting info
    - Include error codes reference
  
  - [ ] 37.5 Create user guide
    - How to register and login
    - How to configure API keys
    - How to submit queries
    - How to understand orchestration
    - How to view history
    - How to manage account
  
  - [ ] 37.6 Create admin guide
    - How to access admin panel
    - How to manage users
    - How to monitor system
    - How to view provider health
    - How to handle issues
  
  - [ ] 37.7 Create deployment guide
    - Backend deployment to Railway/Render
    - Frontend deployment to Vercel
    - Database setup (Supabase)
    - Redis setup (Upstash)
    - Environment variables reference
    - SSL/HTTPS configuration
  
  - [ ] 37.8 Create changelog
    - List all features implemented
    - List all providers supported
    - List all improvements made
    - Save as CHANGELOG.md

- [ ] 37.9 Git push - Documentation complete
  - Merge all feature branches to main
  - Tag release: v2.0.0-multi-provider
  - Push to remote repository
  - Create GitHub release with full changelog

## 🎉 Extended Implementation Complete!

**What you've added:**
- ✅ Support for 8+ AI providers (Ollama, Gemini, HuggingFace, OpenRouter, Together, OpenAI, Qwen, etc.)
- ✅ User API key management system
- ✅ Enhanced IDE-style chat interface
- ✅ Real-time orchestration across multiple providers
- ✅ Comprehensive provider testing and monitoring
- ✅ Complete user flow from landing to response
- ✅ Settings page for API configuration
- ✅ Analytics and cost tracking per provider
- ✅ Comprehensive documentation and guides

**Your application now:**
- Works with local Ollama models (free, private)
- Works with multiple free cloud providers
- Allows users to bring their own API keys
- Intelligently orchestrates across available providers
- Provides detailed orchestration visibility
- Offers professional IDE-style interface
- Tracks costs and performance per provider

**You're ready to launch! 🚀**
