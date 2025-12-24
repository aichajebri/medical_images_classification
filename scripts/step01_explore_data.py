import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Add the project root to sys.path to allow imports from src
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.data_loader import BrainTumorDataset

def explore_data():
    dataset_path = "c:/Users/asus/Downloads/Medical"
    output_dir = Path("c:/Users/asus/Downloads/Medical/outputs/step1_exploration")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Initializing Dataset...")
    ds = BrainTumorDataset(dataset_path)
    
    # 1. Class Distribution
    print("Calculating statistics...")
    stats = ds.get_stats()
    print("Stats:", stats)
    
    # Prepare data for plotting
    train_counts = [stats['train'][c] for c in ds.classes]
    test_counts = [stats['test'][c] for c in ds.classes]
    
    x = range(len(ds.classes))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(10, 6))
    rects1 = ax.bar([i - width/2 for i in x], train_counts, width, label='Train')
    rects2 = ax.bar([i + width/2 for i in x], test_counts, width, label='Test')
    
    ax.set_ylabel('Count')
    ax.set_title('Class Distribution in Brain Tumor Dataset')
    ax.set_xticks(x)
    ax.set_xticklabels(ds.classes)
    ax.legend()
    
    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'class_distribution.png')
    print(f"Saved distribution plot to {output_dir / 'class_distribution.png'}")
    
    # 2. Sample Images
    print("Generating sample grid...")
    samples = ds.get_sample_images(num_samples=1)
    
    fig, axes = plt.subplots(1, 4, figsize=(15, 5))
    for ax, (cls, paths) in zip(axes, samples.items()):
        if paths:
            img = plt.imread(str(paths[0]))
            ax.imshow(img, cmap='gray')
            ax.set_title(cls)
            ax.axis('off')
        else:
            ax.text(0.5, 0.5, 'No Image', ha='center')
            
    plt.suptitle("Sample Brain MRI Images (Training Set)")
    plt.savefig(output_dir / 'sample_mris.png')
    print(f"Saved sample grid to {output_dir / 'sample_mris.png'}")

if __name__ == "__main__":
    explore_data()
