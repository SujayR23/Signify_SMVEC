from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
model = BertModel.from_pretrained("bert-base-uncased")

input_text = "BThis is river bank."


encoded_output = tokenizer.encode_plus(
    input_text,
    add_special_tokens=True, 
    return_tensors="pt"
)

input_ids = encoded_output["input_ids"]
attention_mask = encoded_output["attention_mask"]

with torch.no_grad():
    outputs = model(input_ids, attention_mask=attention_mask)

last_hidden_states = outputs.last_hidden_state 

tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
dense_vectors = last_hidden_states[0]

print("Tokens and Dense Vectors:")
for token, vector in zip(tokens, dense_vectors):
    print(f"Token: {token}\nVector: {vector.numpy()[:5]}...")