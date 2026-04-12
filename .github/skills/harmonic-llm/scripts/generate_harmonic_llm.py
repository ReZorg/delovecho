import sys

def generate_harmonic_llm(model_name):
    template = f'''
import torch
import torch.nn as nn

class HarmonicAttention(nn.Module):
    def __init__(self, embed_dim, n_heads):
        super().__init__()
        self.embed_dim = embed_dim
        self.n_heads = n_heads
        self.head_dim = embed_dim // n_heads

        self.q_proj = nn.Linear(embed_dim, embed_dim)
        self.k_proj = nn.Linear(embed_dim, embed_dim)
        self.v_proj = nn.Linear(embed_dim, embed_dim)
        self.out_proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, x):
        # x is a complex tensor in the frequency domain
        q = self.q_proj(x)
        k = self.k_proj(x)
        v = self.v_proj(x)

        # Phase-based attention
        attn_scores = torch.einsum("bic,bjc->bij", q.angle(), k.angle())
        attn_weights = torch.softmax(attn_scores, dim=-1)

        # Weighted sum of values
        attn_output = torch.einsum("bij,bjc->bic", attn_weights, v)

        return self.out_proj(attn_output)

class {model_name}(nn.Module):
    def __init__(self, vocab_size, embed_dim, n_heads, n_layers):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.layers = nn.ModuleList([
            HarmonicAttention(embed_dim, n_heads) for _ in range(n_layers)
        ])
        self.out = nn.Linear(embed_dim, vocab_size)

    def forward(self, x):
        # x is a sequence of token indices
        x = self.embedding(x)

        # Transform to frequency domain
        x_fft = torch.fft.fft(x, dim=1)

        for layer in self.layers:
            x_fft = layer(x_fft)

        # Transform back to time domain
        x_out = torch.fft.ifft(x_fft, dim=1).real

        return self.out(x_out)
'''
    return template

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_harmonic_llm.py <ModelName>")
        sys.exit(1)
    
    model_name = sys.argv[1]
    print(generate_harmonic_llm(model_name))
