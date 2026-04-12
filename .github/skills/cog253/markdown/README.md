# Markdown Versions of APL and UIA Pages

This directory contains markdown conversions of the HTML files from the original APL and UIA collections.

## APL (A Pattern Language) 

The `apl/` directory contains 253 markdown files converted from Christopher Alexander's "A Pattern Language" HTML files. Each file represents a design pattern with:

- **Problem statement**: The central issue the pattern addresses
- **Solution**: Alexander's proposed solution 
- **Discussion**: Detailed explanation and reasoning
- **Related Patterns**: Cross-references to other patterns

Files are named `apl001.md` through `apl253.md` corresponding to the original pattern numbers.

## UIA (Union of International Associations)

The `uia/` directory contains 253 markdown files converted from the UIA "Patterns & Metaphors" collection. Each pattern includes:

- **Template**: General pattern template
- **Physical**: Physical domain application
- **Social**: Social domain application  
- **Conceptual**: Conceptual domain application
- **Psychic**: Psychological domain application
- **Broader/Narrower Patterns**: Hierarchical relationships

Files are named using their original IDs (e.g., `12610010.md` through `12612530.md`).

## Conversion Process

The markdown files were generated using Python scripts that:

1. Parse the original HTML files with BeautifulSoup
2. Extract structured content while removing boilerplate
3. Convert to clean, readable markdown format
4. Preserve cross-references between patterns
5. Maintain the essential content structure

## Usage

These markdown files provide a more accessible and portable format for:

- Reading and studying the patterns
- Including in documentation systems
- Processing with markdown tools
- Version control and collaboration
- Text-based search and analysis

The content preserves the essential information from the original HTML while being more readable and maintainable in plain text format.