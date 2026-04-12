#!/usr/bin/env python3
"""
Scrape all 253 APL patterns from https://www.iwritewordsgood.com/apl/
and populate the pattern data for the repository model.
"""

import os
import re
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
from html.parser import HTMLParser

# Constants
BASE_URL = "https://www.iwritewordsgood.com/apl/patterns/"
PATTERN_URL_FORMAT = "apl{:03d}.htm"


class APLPatternParser(HTMLParser):
    """Parse APL pattern HTML to extract structured information."""
    
    def __init__(self):
        super().__init__()
        self.pattern_data = {
            'number': 0,
            'name': '',
            'asterisks': 0,
            'context': '',
            'problem': '',
            'solution': '',
            'diagram': '',
            'connections': '',
            'related_patterns': []
        }
        self.current_section = None
        self.in_header = False
        self.in_problem = False
        self.in_solution = False
        self.temp_text = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Pattern title/header
        if tag == 'p' and attrs_dict.get('class') == 'header1':
            self.in_header = True
            self.temp_text = []
        
        # Problem section (bold)
        elif tag == 'p' and attrs_dict.get('class') == 'header2':
            self.in_problem = True
            self.temp_text = []
    
    def handle_endtag(self, tag):
        if tag == 'p':
            if self.in_header:
                self.in_header = False
                header_text = ''.join(self.temp_text).strip()
                self._parse_header(header_text)
                self.temp_text = []
            elif self.in_problem:
                self.in_problem = False
                self.pattern_data['problem'] = ''.join(self.temp_text).strip()
                self.temp_text = []
    
    def handle_data(self, data):
        if self.in_header or self.in_problem:
            self.temp_text.append(data)
    
    def _parse_header(self, header: str):
        """Parse pattern number, name, and asterisks from header."""
        # Format: "56 Bike Paths and Racks*" or "1 Independent Regions**"
        match = re.match(r'^(\d+)\s+(.+?)(\**)$', header)
        if match:
            self.pattern_data['number'] = int(match.group(1))
            self.pattern_data['name'] = match.group(2).strip()
            self.pattern_data['asterisks'] = len(match.group(3))


def fetch_pattern_html(pattern_num: int) -> str:
    """Fetch pattern HTML from the website."""
    url = f"{BASE_URL}{PATTERN_URL_FORMAT.format(pattern_num)}"
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching pattern {pattern_num}: {e}")
        return ""


def extract_pattern_from_html(html: str, pattern_num: int) -> Dict[str, Any]:
    """Extract pattern information from HTML."""
    pattern = {
        'number': pattern_num,
        'name': '',
        'asterisks': 0,
        'context': '',
        'problem': '',
        'solution': '',
        'diagram': '',
        'connections': '',
        'related_patterns': []
    }
    
    # Extract pattern name and asterisks from title
    title_match = re.search(r'<p\s+class="header1">(\d+)\s+(.+?)(\**)</p>', html, re.IGNORECASE)
    if title_match:
        pattern['name'] = title_match.group(2).strip()
        pattern['asterisks'] = len(title_match.group(3))
    
    # Extract context (introductory paragraph before problem)
    context_match = re.search(r'<p\s*>([^<]*?)\.\s*\.\s*\.\s*(.*?)</p>', html, re.IGNORECASE | re.DOTALL)
    if context_match:
        pattern['context'] = re.sub(r'<[^>]+>', '', context_match.group(2)).strip()
    
    # Extract problem (in bold/header2)
    problem_match = re.search(r'<P\s+class="header2">(.*?)</[Pp]>', html, re.IGNORECASE | re.DOTALL)
    if problem_match:
        pattern['problem'] = re.sub(r'<[^>]+>', '', problem_match.group(1)).strip()
    
    # Extract solution (after "Therefore:")
    solution_match = re.search(r'Therefore:\s*</p>\s*<p>\s*<span\s+class="header2">(.*?)</span>', html, re.IGNORECASE | re.DOTALL)
    if solution_match:
        pattern['solution'] = re.sub(r'<[^>]+>', '', solution_match.group(1)).strip()
    
    # Extract related patterns (links in format <A HREF="aplXXX.htm">PATTERN NAME (N)</A>)
    related_matches = re.findall(r'<A\s+HREF="apl(\d+)\.htm"[^>]*>([^<]+)</A>', html, re.IGNORECASE)
    for match in related_matches:
        pattern_id = int(match[0])
        if pattern_id != pattern_num:  # Don't include self-reference
            pattern['related_patterns'].append(pattern_id)
    
    # Remove duplicates from related patterns
    pattern['related_patterns'] = sorted(list(set(pattern['related_patterns'])))
    
    return pattern


def convert_to_markdown(pattern: Dict[str, Any]) -> str:
    """Convert pattern data to markdown format."""
    md_lines = [
        f"# {pattern['number']} - {pattern['name'].upper()}",
        "",
        "## Problem",
        "",
        pattern['problem'],
        "",
    ]
    
    if pattern.get('context'):
        md_lines.insert(4, "## Context")
        md_lines.insert(5, "")
        md_lines.insert(6, pattern['context'])
        md_lines.insert(7, "")
    
    if pattern.get('solution'):
        md_lines.extend([
            "## Solution",
            "",
            pattern['solution'],
            "",
        ])
    
    if pattern.get('related_patterns'):
        md_lines.extend([
            "## Related Patterns",
            "",
        ])
        for related in pattern['related_patterns']:
            md_lines.append(f"- Pattern {related}")
    
    return '\n'.join(md_lines)


def scrape_missing_patterns():
    """Scrape missing patterns from the website."""
    markdown_dir = Path('markdown/apl')
    
    # Find missing pattern numbers
    existing_patterns = set()
    for f in markdown_dir.glob('apl*.md'):
        stem = f.stem.replace('apl', '')
        if stem.isdigit():
            existing_patterns.add(int(stem))
    
    missing = []
    for i in range(1, 254):
        if i not in existing_patterns:
            missing.append(i)
    
    print(f"Found {len(missing)} missing patterns: {missing}")
    
    # Scrape missing patterns
    for pattern_num in missing:
        print(f"Scraping pattern {pattern_num}...")
        html = fetch_pattern_html(pattern_num)
        if html:
            pattern = extract_pattern_from_html(html, pattern_num)
            
            # Save as markdown
            md_content = convert_to_markdown(pattern)
            md_file = markdown_dir / f"apl{pattern_num:03d}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"  Saved {md_file}")
            
            # Be nice to the server
            time.sleep(1)
        else:
            print(f"  Failed to fetch pattern {pattern_num}")
    
    return missing


def main():
    """Main entry point."""
    print("APL Pattern Scraper")
    print("=" * 50)
    print()
    
    # Scrape missing patterns
    missing = scrape_missing_patterns()
    
    print()
    print(f"Completed! Scraped {len(missing)} missing patterns.")


if __name__ == '__main__':
    main()
