# Agent Zero Development Setup

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Integration](#docker-integration)
4. [Debugging](#debugging)
5. [Building Custom Docker Images](#building-custom-docker-images)

## Prerequisites

- VS Code compatible IDE (VS Code, Cursor, Windsurf)
- Python environment (Conda, venv, uv)
- Docker (Docker Desktop, docker-ce)
- Git (optional but recommended)

## Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/agent0ai/agent-zero
cd agent-zero
```

### Step 2: Create Python Environment

```bash
# Using conda
conda create -n agent-zero python=3.12
conda activate agent-zero

# Or using venv
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Step 4: Configure IDE

The project includes `.vscode/` with:
- `launch.json` - Debugger configurations
- `extensions.json` - Recommended extensions

Install recommended extensions:
- `ms-python.python`
- `ms-python.debugpy`
- `usernamehw.errorlens`

### Step 5: Run Locally

```bash
python run_ui.py --port=5000
```

Or use VS Code debugger (F5) with "run_ui.py" configuration.

## Docker Integration

Local development connects to Docker for code execution and system operations.

### Step 1: Run Docker Container

```bash
docker pull agent0ai/agent-zero
docker run -d \
    -p 8880:80 \
    -p 8822:22 \
    -v $(pwd):/a0 \
    --name agent-zero-dev \
    agent0ai/agent-zero
```

Port mappings:
- `8880:80` - Web UI (Docker instance)
- `8822:22` - SSH for code execution

Volume mount syncs local changes to container.

### Step 2: Configure RFC Connection

**In Docker instance (Settings > Development):**
- Set `RFC Password` to a secure value

**In Local instance (Settings > Development):**
- Set `RFC Password` to same value
- Set `SSH Port` to `8822`
- Set `HTTP Port` to `8880`
- Set `RFC Destination URL` to `localhost`

### Step 3: Test Connection

Ask the agent to run a terminal command:
```
Get current OS version
```

Should return "Kali GNU/Linux Rolling" (Docker's OS).

## Debugging

### Setting Breakpoints

1. Open any Python file (e.g., `python/api/message.py`)
2. Click left of line number to set breakpoint
3. Run debugger (F5)
4. Send message in UI to trigger breakpoint

### Inspecting Variables

At breakpoint:
- View local/global variables in Debug sidebar
- Use Debug Console for expressions
- Step through code (F10/F11)

### Common Debug Points

| File | Function | Purpose |
|------|----------|---------|
| `python/api/message.py` | `communicate` | Message handling |
| `agent.py` | `monologue` | Agent loop |
| `agent.py` | `process_tools` | Tool execution |
| `python/tools/*.py` | `execute` | Individual tools |

### Debugging Extensions

Add logging in extensions:

```python
class MyExtension(Extension):
    async def execute(self, **kwargs):
        import logging
        logging.debug(f"Extension executing with: {kwargs}")
        # ... extension logic
```

## Building Custom Docker Images

### Using DockerfileLocal

```bash
docker build -f DockerfileLocal \
    -t agent-zero-custom \
    --build-arg CACHE_DATE=$(date +%Y-%m-%d:%H:%M:%S) \
    .
```

The `CACHE_DATE` argument invalidates cache for final steps only.

### Customizing the Image

Create custom Dockerfile:

```dockerfile
FROM agent0ai/agent-zero

# Add custom tools
COPY my_tools/ /a0/python/tools/

# Install additional packages
RUN pip install my-package

# Custom configuration
COPY my_config.json /a0/tmp/settings.json
```

### Multi-Stage Development

```dockerfile
# Development stage
FROM agent0ai/agent-zero as dev
RUN pip install debugpy pytest

# Production stage
FROM agent0ai/agent-zero as prod
COPY --from=dev /a0 /a0
```

## Environment Variables

Create `.env` file in project root:

```env
# Web UI
WEB_UI_PORT=5000
WEB_UI_HOST=0.0.0.0

# Development
DEBUG=true
LOG_LEVEL=DEBUG

# API Keys (for testing)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

## Testing

### Running Tests

```bash
pytest tests/ -v
```

### Testing Tools

```python
# tests/test_my_tool.py
import pytest
from python.tools.my_tool import MyTool

@pytest.mark.asyncio
async def test_my_tool():
    tool = MyTool(agent=mock_agent, name="my_tool", args={"param": "value"})
    response = await tool.execute()
    assert response.message == "Expected output"
```

### Testing Extensions

```python
# tests/test_my_extension.py
import pytest
from python.extensions.agent_init.my_extension import MyExtension

@pytest.mark.asyncio
async def test_extension():
    ext = MyExtension(agent=mock_agent)
    await ext.execute()
    assert mock_agent.agent_name == "Expected"
```

## Troubleshooting

### Common Issues

**RFC Connection Failed**
- Verify Docker container is running
- Check port mappings match settings
- Ensure RFC passwords match

**Code Execution Timeout**
- Increase timeouts in `code_execution_tool.py`
- Check Docker container resources

**Extension Not Loading**
- Verify file location and naming
- Check for syntax errors
- Ensure class inherits from `Extension`

### Logs

Check logs in:
- `logs/` directory for session logs
- Docker logs: `docker logs agent-zero-dev`
- Browser console for frontend issues
