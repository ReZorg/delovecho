import sys

def generate_harmonic_op(op_name):
    template = f'''
#include "ggml.h"

// Forward declaration
void ggml_compute_forward_{op_name.lower()}(const struct ggml_compute_params * params, const struct ggml_tensor * src0, const struct ggml_tensor * src1, struct ggml_tensor * dst);

struct ggml_tensor * ggml_{op_name.lower()}(struct ggml_context * ctx, struct ggml_tensor * a, struct ggml_tensor * b) {{
    GGML_ASSERT(ggml_are_same_shape(a, b));
    struct ggml_tensor * result = ggml_new_tensor(ctx, a->type, a->n_dims, a->ne);
    result->op = GGML_OP_{op_name.upper()};
    result->grad = NULL;
    result->src[0] = a;
    result->src[1] = b;
    return result;
}}

void ggml_compute_forward_{op_name.lower()}(const struct ggml_compute_params * params, const struct ggml_tensor * src0, const struct ggml_tensor * src1, struct ggml_tensor * dst) {{
    // TODO: Implement the frequency-domain logic for the {op_name} operation.
    // This will likely involve element-wise operations on the complex-valued tensors.
}}
'''
    return template

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_harmonic_ops.py <OperatorName>")
        sys.exit(1)
    
    op_name = sys.argv[1]
    print(generate_harmonic_op(op_name))
