# Reservoir Architecture for Conversational State

This document outlines the Echo State Network (ESN) architecture for tracking conversational state in the `deltecho` skill.

## 1. Core Components

- **`DeltaChatMessageNode`**: Encodes raw message metadata (e.g., `is_bot`, `has_attachment`) into a numerical feature vector. This is the primary input to the reservoir.
- **`Reservoir`**: A large, fixed recurrent neural network that receives input from `DeltaChatMessageNode`. Its internal state captures the temporal dynamics of the conversation.
- **`Ridge` (Readout)**: A trainable linear regression layer that maps the high-dimensional reservoir state to a lower-dimensional output, representing the current conversational state or a predicted response.
- **`ConversationStateNode`**: A trainable node that can learn to classify or predict aspects of the conversation based on the reservoir's output.
- **`CognitiveResponseNode`**: An online-trainable node that learns to generate response vectors based on the cognitive pipeline's output, allowing the ESN to adapt to the bot's evolving behavior.

## 2. Data Flow & Composition

The primary composition is a feed-forward ESN:

```python
from reservoirpy.nodes import Reservoir, Ridge
from .reservoir_nodes import DeltaChatMessageNode

# 1. Message Encoder
msg_encoder = DeltaChatMessageNode()

# 2. Reservoir
reservoir = Reservoir(100, lr=0.5, sr=0.9) # 100 neurons, learning rate 0.5, spectral radius 0.9

# 3. Readout Layer
readout = Ridge(ridge=1e-6)

# 4. Compose the ESN
esn = msg_encoder >> reservoir >> readout
```

### With Feedback:

For more context-aware responses, the readout's output can be fed back into the reservoir.

```python
esn_with_feedback = (msg_encoder & readout) >> reservoir >> readout
```

## 3. Training

### Online Learning

The `CognitiveResponseNode` can be trained incrementally after each message, allowing the bot to learn from its own responses.

```python
# Conceptual
cognitive_readout = CognitiveResponseNode(output_dim=...)
esn = msg_encoder >> reservoir >> cognitive_readout

# After sending a response:
response_vector = # ... encode the bot's response
input_vector = # ... vector from the message that triggered the response
esn.train(input_vector, response_vector)
```

### Offline Training

The `ConversationStateNode` can be trained offline on historical conversation data to learn patterns, such as classifying conversation topics or predicting user intent.

```python
# Conceptual
state_classifier = ConversationStateNode(output_dim=...)
esn = msg_encoder >> reservoir >> state_classifier

# On a dataset of conversation histories:
X_train = # ... sequence of message vectors
Y_train = # ... sequence of state labels
esn.fit(X_train, Y_train, warmup=10)
```

## 4. Integration in `deltecho_bot.py`

The ESN is run for each new message. Its state is not directly used for the response in the initial design but is intended to be a foundation for more advanced features like:

- Predicting user intent.
- Detecting conversation topic shifts.
- Generating more nuanced, context-aware responses.
- Anomaly detection in conversation patterns of conversational patterns.
