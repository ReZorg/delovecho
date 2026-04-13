# Tool Prompt Template

Save this file as `prompts/agent.system.tool.{tool_name}.md` to define how the agent uses your tool.

---

## {tool_name}

{Brief description of what the tool does and when to use it.}

**Arguments:**
- `param1` (string, required): {Description of first parameter}
- `param2` (number, optional): {Description of second parameter, default: 0}
- `optional_flag` (boolean, optional): {Description of flag, default: false}

**Returns:**
{Description of what the tool returns}

**Example usage:**

~~~json
{
    "thoughts": [
        "I need to {reason for using tool}",
        "The user wants {what user requested}",
        "I will use {tool_name} to {action}"
    ],
    "tool_name": "{tool_name}",
    "tool_args": {
        "param1": "example_value",
        "param2": 42,
        "optional_flag": true
    }
}
~~~

**Notes:**
- {Any important usage notes}
- {Limitations or constraints}
- {Best practices}

---

## Example: Web Scraper Tool

## web_scraper

Scrape content from a web page and extract text or specific elements.

**Arguments:**
- `url` (string, required): The URL to scrape
- `selector` (string, optional): CSS selector to extract specific elements
- `format` (string, optional): Output format - "text", "html", or "json" (default: "text")

**Returns:**
Extracted content from the web page in the specified format.

**Example usage:**

~~~json
{
    "thoughts": [
        "The user wants to get the main article content from this news page",
        "I should use web_scraper to extract the article text",
        "I'll use a CSS selector to target the article body"
    ],
    "tool_name": "web_scraper",
    "tool_args": {
        "url": "https://example.com/article",
        "selector": "article.main-content",
        "format": "text"
    }
}
~~~

**Notes:**
- Respects robots.txt by default
- Maximum page size: 5MB
- Timeout: 30 seconds
- For JavaScript-rendered pages, use browser_agent instead
