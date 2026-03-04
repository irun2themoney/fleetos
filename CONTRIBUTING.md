# Contributing to FleetOS

Thank you for your interest in contributing to FleetOS! This document provides guidelines for getting started.

## Getting Started

### Prerequisites
- Python 3.10+
- Git
- Docker & Docker Compose (recommended)
- 16GB+ RAM for local Ollama

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fleetos.git
   cd fleetos
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Copy environment template**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

6. **Verify setup**
   ```bash
   python -c "import fleetos; print('FleetOS ready!')"
   ```

## Development Workflow

### Branch Naming
- Feature: `feature/feature-name`
- Bug fix: `fix/bug-name`
- Documentation: `docs/doc-name`
- Phase work: `phase/2-orchestration`

### Commit Messages
Follow conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(planner): add role decomposition logic
fix(orchestrator): handle agent timeout gracefully
docs(readme): add quick start guide
test(verifier): add confidence scoring tests
```

### Code Quality

1. **Format code**
   ```bash
   black fleetos tests
   isort fleetos tests
   ```

2. **Lint**
   ```bash
   flake8 fleetos tests
   mypy fleetos
   ```

3. **Test**
   ```bash
   pytest tests/ -v --cov=fleetos
   ```

### Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat(scope): describe your changes"
   ```

3. **Push to your fork**
   ```bash
   git push origin feature/your-feature
   ```

4. **Open Pull Request**
   - Reference any related issues: `Closes #123`
   - Describe the changes clearly
   - Include test coverage
   - Update documentation if needed

5. **Address review feedback**
   - Respond to comments
   - Make requested changes
   - Keep conversations respectful

## Areas for Contribution

### Phase 1 (Days 1-2): Local Setup
- [ ] OpenClaw wrapper enhancements
- [ ] Ollama configuration utilities
- [ ] Telegram integration helpers
- [ ] Local testing utilities

### Phase 2 (Days 3-5): Orchestration
- [ ] LangGraph planner node implementation
- [ ] Orchestrator agent spawning logic
- [ ] Artifact aggregation utilities
- [ ] State management helpers

### Phase 3 (Days 6-8): Memory & Evolution
- [ ] Chroma vector store integration
- [ ] GraphRAG knowledge graph setup
- [ ] Feedback loop analysis
- [ ] Auto-skill generation logic

### Phase 4 (Days 9-11): Dashboard
- [ ] Streamlit UI components
- [ ] Real-time agent status visualization
- [ ] Fleet control buttons and forms
- [ ] Artifact display components

### Phase 5 (Days 12-14): Verification
- [ ] VerdictNet critic node implementation
- [ ] Confidence scoring logic
- [ ] Telegram approval flow
- [ ] Human-in-the-loop gating

### Phase 6 (Days 15-20): Templates
- [ ] Business template schema definition
- [ ] Newsletter template implementation
- [ ] Lead-Gen template implementation
- [ ] Template matcher logic

### Phase 7 (Days 21-30): Cloud Deployment
- [ ] Kubernetes YAML configurations
- [ ] kagent CRD definitions
- [ ] Cloud deployment scripts
- [ ] Observability setup

### Testing
- [ ] Unit tests for all modules
- [ ] Integration tests for data flow
- [ ] End-to-end tests for business templates
- [ ] Load testing and performance benchmarks

### Documentation
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Tutorial walkthroughs
- [ ] Troubleshooting guides

## Reporting Issues

1. **Check existing issues** to avoid duplicates
2. **Use issue templates** (feature request, bug report)
3. **Provide clear description** with steps to reproduce (for bugs)
4. **Include environment info**: Python version, OS, etc.
5. **Attach logs** if relevant (from `logs/` directory)

## Discussions

Have questions or ideas? Start a discussion:
- Feature requests
- Design decisions
- Implementation approaches
- General questions

## Code of Conduct

- Be respectful and inclusive
- Assume good intent
- Provide constructive feedback
- No harassment or discrimination
- Report violations to maintainers

## Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project documentation

## Questions?

- Check [README.md](README.md) for overview
- Read [FleetOS_Project_Specification.docx](docs/FleetOS_Project_Specification.docx) for architecture
- Ask in GitHub Discussions
- Email: contact@fleetos.dev

Thank you for contributing! 🙌
