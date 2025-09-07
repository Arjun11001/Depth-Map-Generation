from PIL import Image
import depth_pro
import matplotlib.pyplot as plt
import numpy as np
import cv2

# Load model and preprocessing transform
model, transform = depth_pro.create_model_and_transforms(device='cuda')
model.eval()

# Load and preprocess an image.
image, _, f_px = depth_pro.load_rgb('data/example.jpg')
image = transform(image)

# Run inference.
prediction = model.infer(image, f_px=f_px)
depth = prediction["depth"]  # Depth in [m].

# Focal length in pixels.
focallength_px = prediction["focallength_px"]
print("Focal length (px):", focallength_px)

# Convert depth tensor to numpy array
depth_np = depth.squeeze().cpu().numpy()

# Example: Get real distance at the center of the image
h, w = depth_np.shape
center_x, center_y = w // 2, h // 2
real_distance_m = depth_np[center_y, center_x]
print(f"Real distance at image center: {real_distance_m:.2f} meters")

# Save depth map as an image (using a colormap for visualization)
depth_normalized = cv2.normalize(depth_np, None, 0, 255, cv2.NORM_MINMAX)
depth_normalized = depth_normalized.astype(np.uint8)

# Invert depth if needed
depth_inverted = 255 - depth_normalized

# Apply colormap (e.g., COLORMAP_JET)
colored_depth = cv2.applyColorMap(depth_inverted, cv2.COLORMAP_JET)
depth_colormap = colored_depth
#depth_normalized = (depth_np - np.min(depth_np)) / (np.max(depth_np) - np.min(depth_np) + 1e-8)
#depth_colormap = cv2.applyColorMap((depth_normalized * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
text_focal = f"Focal length (px): {focallength_px:.2f}"
text_distance = f"Real distance (m): {real_distance_m:.2f}"
font = cv2.FONT_HERSHEY_SIMPLEX
cv2.putText(depth_colormap, text_focal, (10, 30), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(depth_colormap, text_distance, (10, 60), font, 0.8, (255, 255, 255), 2, cv2.LINE_AA)
cv2.imwrite("depth_map.png", depth_colormap)
# cv2.imshow("Depth Map with Info", depth_colormap)
cv2.waitKey(0)
cv2.destroyAllWindows()
print("Depth map saved as depth_map.png")