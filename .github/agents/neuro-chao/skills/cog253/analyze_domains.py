#!/usr/bin/env python3
"""
Analyze UIA pattern descriptions to identify generic vs domain-specific vocabulary.

This script parses all UIA markdown files and analyzes the vocabulary used in each
domain (Template, Physical, Social, Conceptual, Psychic) to identify:
- Generic terms that appear consistently across all domains
- Domain-specific terms that vary according to the domain context
"""

import os
import re
import json
from collections import defaultdict, Counter
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    print("Warning: Could not download NLTK data. Using basic tokenization.")

def extract_domain_sections(content):
    """Extract content from each domain section of a UIA pattern."""
    sections = {}
    
    # Define section patterns
    section_patterns = {
        'Template': r'## Template\s*\n\n(.*?)(?=\n## |$)',
        'Physical': r'## Physical\s*\n\n(.*?)(?=\n## |$)',
        'Social': r'## Social\s*\n\n(.*?)(?=\n## |$)',
        'Conceptual': r'## Conceptual\s*\n\n(.*?)(?=\n## |$)',
        'Psychic': r'## Psychic\s*\n\n(.*?)(?=\n## |$)'
    }
    
    for domain, pattern in section_patterns.items():
        match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
        if match:
            sections[domain] = match.group(1).strip()
        else:
            sections[domain] = ""
    
    return sections

def clean_and_tokenize(text):
    """Clean text and extract meaningful tokens."""
    if not text:
        return []
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and split into words
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Simple word tokenization
    words = text.split()
    
    # Filter out common stop words and short words
    try:
        stop_words = set(stopwords.words('english'))
    except:
        # Fallback stop words if NLTK not available
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'such', 'this', 'that', 'these', 'those', 'it', 'its', 'they', 'their', 'them', 'there', 'where', 'when', 'how', 'what', 'which', 'who', 'why'}
    
    # Filter meaningful words (length > 2, not stop words, not numbers)
    words = [w for w in words if len(w) > 2 and w not in stop_words and not w.isdigit()]
    
    return words

def extract_phrases(text, n=2):
    """Extract n-gram phrases from text."""
    if not text:
        return []
    
    words = text.lower().split()
    phrases = []
    for i in range(len(words) - n + 1):
        phrase = ' '.join(words[i:i + n])
        # Skip phrases with too much punctuation or stop words
        if len([w for w in phrase.split() if w.isalpha() and len(w) > 2]) >= n:
            phrases.append(phrase)
    
    return phrases

def analyze_patterns():
    """Main analysis function."""
    markdown_dir = Path('/home/runner/work/p235/p235/markdown/uia')
    
    # Storage for domain vocabulary
    domain_vocabulary = {
        'Template': Counter(),
        'Physical': Counter(),
        'Social': Counter(),
        'Conceptual': Counter(),
        'Psychic': Counter()
    }
    
    # Storage for domain phrases
    domain_phrases = {
        'Template': Counter(),
        'Physical': Counter(),
        'Social': Counter(),
        'Conceptual': Counter(),
        'Psychic': Counter()
    }
    
    pattern_count = 0
    processed_files = []
    
    print("Analyzing UIA patterns...")
    
    # Process each UIA pattern file
    for md_file in sorted(markdown_dir.glob('*.md')):
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract domain sections
            sections = extract_domain_sections(content)
            
            # Analyze vocabulary for each domain
            for domain, text in sections.items():
                if text:
                    # Extract words
                    words = clean_and_tokenize(text)
                    domain_vocabulary[domain].update(words)
                    
                    # Extract 2-gram phrases
                    phrases = extract_phrases(text, 2)
                    domain_phrases[domain].update(phrases)
            
            pattern_count += 1
            processed_files.append(md_file.name)
            
            if pattern_count % 50 == 0:
                print(f"Processed {pattern_count} patterns...")
                
        except Exception as e:
            print(f"Error processing {md_file}: {e}")
    
    print(f"Total patterns processed: {pattern_count}")
    
    # Analyze vocabulary patterns
    analysis = analyze_vocabulary_patterns(domain_vocabulary, domain_phrases, pattern_count)
    
    return analysis, processed_files

def analyze_vocabulary_patterns(domain_vocabulary, domain_phrases, pattern_count):
    """Analyze vocabulary to identify generic vs domain-specific terms."""
    
    analysis = {
        'summary': {
            'total_patterns': pattern_count,
            'domains': list(domain_vocabulary.keys())
        },
        'generic_terms': {},
        'domain_specific_terms': {},
        'generic_phrases': {},
        'domain_specific_phrases': {},
        'vocabulary_stats': {}
    }
    
    # Get all unique words across all domains
    all_words = set()
    for domain_words in domain_vocabulary.values():
        all_words.update(domain_words.keys())
    
    # Identify generic terms (appear in multiple domains with high frequency)
    generic_threshold = 3  # Must appear in at least 3 domains
    min_frequency = 10     # Must appear at least 10 times
    
    for word in all_words:
        domain_presence = {}
        total_frequency = 0
        
        for domain in domain_vocabulary:
            freq = domain_vocabulary[domain][word]
            if freq > 0:
                domain_presence[domain] = freq
                total_frequency += freq
        
        # Classify as generic if appears in multiple domains with reasonable frequency
        if len(domain_presence) >= generic_threshold and total_frequency >= min_frequency:
            analysis['generic_terms'][word] = {
                'total_frequency': total_frequency,
                'domain_frequencies': domain_presence,
                'domain_count': len(domain_presence)
            }
    
    # Identify domain-specific terms (appear primarily in one domain)
    for domain in domain_vocabulary:
        domain_specific = {}
        
        # Get top words for this domain
        for word, freq in domain_vocabulary[domain].most_common(100):
            if word not in analysis['generic_terms'] and freq >= 5:
                # Check if this word is significantly more common in this domain
                other_domain_freq = sum(domain_vocabulary[other_domain][word] 
                                      for other_domain in domain_vocabulary 
                                      if other_domain != domain)
                
                # If word appears much more in this domain than others
                if freq > other_domain_freq * 2:
                    domain_specific[word] = {
                        'frequency': freq,
                        'other_domains_freq': other_domain_freq
                    }
        
        analysis['domain_specific_terms'][domain] = domain_specific
    
    # Analyze phrases similarly
    all_phrases = set()
    for domain_phrases_dict in domain_phrases.values():
        all_phrases.update(domain_phrases_dict.keys())
    
    for phrase in all_phrases:
        domain_presence = {}
        total_frequency = 0
        
        for domain in domain_phrases:
            freq = domain_phrases[domain][phrase]
            if freq > 0:
                domain_presence[domain] = freq
                total_frequency += freq
        
        # Generic phrases (appear across domains)
        if len(domain_presence) >= 2 and total_frequency >= 5:
            analysis['generic_phrases'][phrase] = {
                'total_frequency': total_frequency,
                'domain_frequencies': domain_presence,
                'domain_count': len(domain_presence)
            }
    
    # Domain-specific phrases
    for domain in domain_phrases:
        domain_specific_phrases = {}
        
        for phrase, freq in domain_phrases[domain].most_common(50):
            if phrase not in analysis['generic_phrases'] and freq >= 3:
                other_domain_freq = sum(domain_phrases[other_domain][phrase] 
                                      for other_domain in domain_phrases 
                                      if other_domain != domain)
                
                if freq > other_domain_freq:
                    domain_specific_phrases[phrase] = {
                        'frequency': freq,
                        'other_domains_freq': other_domain_freq
                    }
        
        analysis['domain_specific_phrases'][domain] = domain_specific_phrases
    
    # Vocabulary statistics
    for domain in domain_vocabulary:
        total_words = sum(domain_vocabulary[domain].values())
        unique_words = len(domain_vocabulary[domain])
        analysis['vocabulary_stats'][domain] = {
            'total_words': total_words,
            'unique_words': unique_words,
            'avg_word_frequency': total_words / unique_words if unique_words > 0 else 0
        }
    
    return analysis

def save_analysis(analysis, processed_files, output_file):
    """Save analysis results to a JSON file."""
    output_data = {
        'analysis': analysis,
        'processed_files': processed_files,
        'metadata': {
            'script_version': '1.0',
            'description': 'Analysis of UIA patterns to identify generic vs domain-specific vocabulary'
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Analysis saved to: {output_file}")

def create_readable_report(analysis, output_file):
    """Create a human-readable report."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# UIA Domain Vocabulary Analysis Report\n\n")
        f.write(f"Analysis of {analysis['summary']['total_patterns']} UIA patterns\n")
        f.write(f"Domains analyzed: {', '.join(analysis['summary']['domains'])}\n\n")
        
        # Generic terms section
        f.write("## Generic Terms\n\n")
        f.write("Terms that appear consistently across multiple domains:\n\n")
        
        generic_terms = sorted(analysis['generic_terms'].items(), 
                              key=lambda x: x[1]['total_frequency'], reverse=True)
        
        for term, data in generic_terms[:30]:  # Top 30 generic terms
            f.write(f"- **{term}** (total: {data['total_frequency']}, domains: {data['domain_count']})\n")
            domain_freqs = ', '.join(f"{domain}: {freq}" for domain, freq in sorted(data['domain_frequencies'].items()))
            f.write(f"  - {domain_freqs}\n")
        
        # Domain-specific terms section
        f.write("\n## Domain-Specific Terms\n\n")
        
        for domain in analysis['summary']['domains']:
            f.write(f"### {domain} Domain\n\n")
            
            domain_terms = sorted(analysis['domain_specific_terms'][domain].items(),
                                key=lambda x: x[1]['frequency'], reverse=True)
            
            for term, data in domain_terms[:15]:  # Top 15 terms per domain
                f.write(f"- **{term}** ({data['frequency']} occurrences)\n")
        
        # Generic phrases section  
        f.write("\n## Generic Phrases\n\n")
        f.write("Phrases that appear across multiple domains:\n\n")
        
        generic_phrases = sorted(analysis['generic_phrases'].items(),
                               key=lambda x: x[1]['total_frequency'], reverse=True)
        
        for phrase, data in generic_phrases[:20]:  # Top 20 generic phrases
            f.write(f"- **\"{phrase}\"** (total: {data['total_frequency']}, domains: {data['domain_count']})\n")
        
        # Vocabulary statistics
        f.write("\n## Vocabulary Statistics\n\n")
        f.write("| Domain | Total Words | Unique Words | Avg Frequency |\n")
        f.write("|--------|-------------|--------------|---------------|\n")
        
        for domain, stats in analysis['vocabulary_stats'].items():
            f.write(f"| {domain} | {stats['total_words']} | {stats['unique_words']} | {stats['avg_word_frequency']:.2f} |\n")

if __name__ == "__main__":
    print("Starting UIA domain vocabulary analysis...")
    
    try:
        # Run the analysis
        analysis, processed_files = analyze_patterns()
        
        # Save results
        json_output = "/home/runner/work/p235/p235/domain_analysis.json"
        report_output = "/home/runner/work/p235/p235/domain_analysis_report.md"
        
        save_analysis(analysis, processed_files, json_output)
        create_readable_report(analysis, report_output)
        
        print(f"\nAnalysis complete!")
        print(f"- Detailed data: {json_output}")
        print(f"- Readable report: {report_output}")
        
        # Print summary
        print(f"\nSummary:")
        print(f"- Patterns analyzed: {analysis['summary']['total_patterns']}")
        print(f"- Generic terms found: {len(analysis['generic_terms'])}")
        print(f"- Generic phrases found: {len(analysis['generic_phrases'])}")
        
        for domain in analysis['summary']['domains']:
            domain_specific_count = len(analysis['domain_specific_terms'][domain])
            print(f"- {domain} domain-specific terms: {domain_specific_count}")
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()