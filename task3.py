import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models
from PIL import Image
import matplotlib.pyplot as plt
import copy

def load_image(img_path, max_size=400, shape=None):
    image = Image.open(img_path).convert('RGB')
    
    if max(image.size) > max_size:
        size = max_size
    else:
        size = max(image.size)
    
    if shape is not None:
        size = shape[-2:]  # Ensure we get (height, width) from shape

    if isinstance(size, int):
        size = (size, size)  # Convert to (H, W) tuple if it's a single int

    in_transform = transforms.Compose([
        transforms.Resize(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    
    image = in_transform(image)[:3, :, :].unsqueeze(0)
    return image

# Function to display image
def im_convert(tensor):
    image = tensor.to("cpu").clone().detach().squeeze()
    image = image.numpy().transpose(1, 2, 0)
    image = image * [0.229, 0.224, 0.225] + [0.485, 0.456, 0.406]
    image = image.clip(0, 1)
    return image

# Load content and style images
content = load_image('OneDrive/Pictures/9e833426824c34a0d4ec5c72e0a3bfa4.jpg').to('cuda' if torch.cuda.is_available() else 'cpu')
style = load_image('OneDrive/Pictures/Tanjiro_Kamado_Full_Body_29.jpg', shape=content.shape[-2:]).to('cuda' if torch.cuda.is_available() else 'cpu')

# Load pretrained VGG19 model
from torchvision.models import vgg19, VGG19_Weights

weights = VGG19_Weights.IMAGENET1K_V1
vgg = vgg19(weights=weights).features


# Freeze parameters
for param in vgg.parameters():
    param.requires_grad_(False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vgg.to(device)

# Layers to extract style and content
def get_features(image, model, layers=None):
    if layers is None:
        layers = {
            '0': 'conv1_1',
            '5': 'conv2_1',
            '10': 'conv3_1',
            '19': 'conv4_1',
            '21': 'conv4_2',  # Content representation
            '28': 'conv5_1'
        }
    
    features = {}
    x = image
    for name, layer in model._modules.items():
        x = layer(x)
        if name in layers:
            features[layers[name]] = x
            
    return features

# Gram Matrix for style representation

    stydef gram_matrix(tensor):
    _, d, h, w = tensor.size()
    tensor = tensor.view(d, h * w)
    gram = torch.mm(tensor, tensor.t())
    return gram

# Extract features
content_features = get_features(content, vgg)
style_features = get_features(style, vgg)

# Compute style Gram matrices
style_grams = {layer: gram_matrix(style_features[layer]) for layer in style_features}

# Create target image to optimize
target = content.clone().requires_grad_(True).to(device)

# Define weights for layers
style_weights = {
    'conv1_1': 1.0,
    'conv2_1': 0.75,
    'conv3_1': 0.2,
    'conv4_1': 0.2,
    'conv5_1': 0.1
}
content_weight = 1  # alpha
style_weight = 1e6  # beta

# Optimizer
optimizer = optim.Adam([target], lr=0.003)

# Style Transfer loop
steps = 2000

for step in range(1, steps+1):
    target_features = get_features(target, vgg)
    
    content_loss = torch.mean((target_features['conv4_2'] - content_features['conv4_2'])**2)
    le_loss = 0
    for layer in style_weights:
        target_feature = target_features[layer]
        target_gram = gram_matrix(target_feature)
        style_gram = style_grams[layer]
        layer_style_loss = style_weights[layer] * torch.mean((target_gram - style_gram)**2)
        style_loss += layer_style_loss / (target_feature.shape[1]**2)
        
    total_loss = content_weight * content_loss + style_weight * style_loss
    
    optimizer.zero_grad()
    total_loss.backward()
    optimizer.step()
    
    if step % 500 == 0:
        print(f"Step {step}, Total loss: {total_loss.item()}")

# Show final result
final_img = im_convert(target)
plt.imshow(final_img)
plt.axis("off")
plt.show()
