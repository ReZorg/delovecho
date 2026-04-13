import json
import sys

def define_prime_grammar(domain_name, vocab_size):
    # TODO: Implement a more sophisticated prime factorization algorithm
    factors = {2: 10, 3: 2, 5: 1, 1117: 1} # Example for 50257
    
    grammar = {
        "domain": domain_name,
        "vocab_size": vocab_size,
        "prime_factors": factors
    }
    
    with open(f"{domain_name}_grammar.json", "w") as f:
        json.dump(grammar, f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python define_prime_grammar.py <DomainName> <VocabSize>")
        sys.exit(1)
    
    domain_name = sys.argv[1]
    vocab_size = int(sys.argv[2])
    define_prime_grammar(domain_name, vocab_size)
