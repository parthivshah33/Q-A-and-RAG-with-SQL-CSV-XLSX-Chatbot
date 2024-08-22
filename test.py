import torch

# Determine the device to use and print GPU details if available
if torch.cuda.is_available():
    device = 'cuda'
    gpu_details = torch.cuda.get_device_properties(0)  # Get properties of the first GPU
    print(f"Using GPU: {gpu_details.name}")
    print(f"  Memory Allocated: {torch.cuda.memory_allocated(0) / 1e9:.2f} GB")
    print(f"  Memory Cached: {torch.cuda.memory_reserved(0) / 1e9:.2f} GB")
    print(f"  Total Memory: {gpu_details.total_memory / 1e9:.2f} GB")
else:
    device = 'cpu'
    print("Using CPU")
    
    
    
import torch
print(torch.cuda.device_count())  # Should return 1 or more if GPUs are detected
print(torch.cuda.current_device())  # Should return the index of the current device
print(torch.cuda.get_device_name(0))  # Should return the name of the GPU
