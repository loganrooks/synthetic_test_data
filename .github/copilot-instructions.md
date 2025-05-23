# GitHub Copilot Repository Instructions
> Last Updated: 2025-05-20 19:24:10 UTC  
> Updated By: loganrooks

## General Coding Style & Practices

- Use well-structured, modular code with clear separation of concerns
- Keep functions/methods under 500 lines for readability
- Write comprehensive comments and documentation
- Use meaningful variable/function names following consistent naming conventions
- Follow SOLID principles and dependency injection where appropriate

## Code Organization

- Maintain clear directory structure with logical organization
- Use feature-based or domain-driven organization when appropriate
- Separate implementation from interfaces and abstractions

## Version Control Practices

- Write meaningful commit messages that explain "why" not just "what"
- Use the format: `<type>(<scope>): <description>` for commit messages
  - Example: `feat(auth): implement OAuth2 authentication flow`
  - Types: feat, fix, docs, style, refactor, test, chore
- Make atomic commits (single logical change per commit)
- Follow Git Flow or GitHub Flow branching strategy:
  - `main`/`master` - production-ready code
  - `develop` - integration branch for features
  - `feature/*` - new features
  - `hotfix/*` - urgent production fixes
  - `release/*` - preparation for release
- Create descriptive pull requests with:
  - Clear description of changes
  - Link to related issues
  - Testing information
- Resolve merge conflicts by understanding both sides of the change
- Tag releases with semantic versioning (MAJOR.MINOR.PATCH)

## Documentation Standards

- Document all public APIs, interfaces and classes
- Include usage examples in documentation
- Update documentation when code changes
- Write README.md files for each major component/module

## Testing Approach

- Follow Test-Driven Development (TDD) principles:
  - Write tests before implementation
  - Run tests frequently
  - Refactor after tests pass
- Include unit tests, integration tests, and end-to-end tests as appropriate
- Aim for high test coverage, especially for core functionality
- Mock external dependencies for deterministic testing

## Error Handling

- Use structured error handling with specific error types
- Provide meaningful error messages and context
- Log errors appropriately with context information
- Handle edge cases explicitly

## Context Management

- Consider context limits when implementing complex solutions
- Break down complex tasks into manageable components
- Use clear dependency management

## Security Practices

- Validate all inputs, especially user inputs
- Follow security best practices for authentication, authorization, and data protection
- Avoid common vulnerabilities (XSS, CSRF, SQL injection, etc.)
- Use secure default settings

## Feedback & Improvement

- When receiving user feedback, incorporate it immediately
- Document lessons learned from errors or problematic implementations
- Continuously improve implementation and approaches

## Mode-Specific Instructions

Use specialized prompts from the `.github/prompts` directory when you want me to focus on specific tasks like:
- Architecture design
- Code implementation
- Testing and QA
- DevOps tasks
- Security reviews
- Documentation writing
- Holistic code review

Example: "Using the DevOps prompt, help me set up CI/CD for this repository"