import os
from torchvision import datasets, transforms
import torch
from pathlib import Path
import matplotlib.pyplot as plt

class BrainTumorDataset:
    """
    A class to handle dataset loading and exploration for Brain Tumor MRI.
    """
    def __init__(self, root_dir):
        """
        Args:
            root_dir (str): Path to the dataset (e.g. 'Downloads/Medical')
        """
        self.root_dir = Path(root_dir)
        self.train_dir = self.root_dir / 'Training'
        self.test_dir = self.root_dir / 'Testing'
        self.classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
        
        self._check_structure()

    def _check_structure(self):
        """Verifies that Training and Testing directories exist and contain class folders."""
        if not self.train_dir.exists():
            raise FileNotFoundError(f"Training directory not found at {self.train_dir}")
        if not self.test_dir.exists():
            raise FileNotFoundError(f"Testing directory not found at {self.test_dir}")
        
        for c in self.classes:
            if not (self.train_dir / c).exists():
                print(f"Warning: Class directory '{c}' missing in Training")
            if not (self.test_dir / c).exists():
                print(f"Warning: Class directory '{c}' missing in Testing")

    def get_stats(self):
        """Returns a dictionary with counts of images per class for Train and Test."""
        stats = {'train': {}, 'test': {}}
        
        for c in self.classes:
            stats['train'][c] = len(list((self.train_dir / c).glob('*.jpg')))
            if stats['train'][c] == 0: # Try png or jpeg if jpg fails, or just *
                 stats['train'][c] = len(list((self.train_dir / c).glob('*')))
                 
            stats['test'][c] = len(list((self.test_dir / c).glob('*.jpg')))
            if stats['test'][c] == 0:
                 stats['test'][c] = len(list((self.test_dir / c).glob('*')))
                 
        return stats

    def get_sample_images(self, num_samples=1):
        """Returns a dict with `num_samples` file paths per class from Training set."""
        samples = {}
        for c in self.classes:
            # We explicitly look for common image extensions
            files = list((self.train_dir / c).glob('*'))
            samples[c] = files[:num_samples]
        return samples

    def get_pytorch_datasets(self, transform=None):
        """Returns standard PyTorch datasets for training and testing."""
        if transform is None:
            # We will use specific transforms per phase usually, but this is a fallback
            transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor()
            ])
            
        train_dataset = datasets.ImageFolder(root=self.train_dir, transform=transform)
        test_dataset = datasets.ImageFolder(root=self.test_dir, transform=transform)
        
        return train_dataset, test_dataset

    def get_transforms(self, phase='train'):
        """
        Returns the data transformation pipeline for the specified phase.
        Args:
            phase (str): 'train' or 'test'
        """
        # ImageNet normalization statistics
        normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                         std=[0.229, 0.224, 0.225])
        
        if phase == 'train':
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomRotation(degrees=15),
                transforms.ColorJitter(brightness=0.2, contrast=0.2),
                transforms.ToTensor(),
                normalize
            ])
        else:
            return transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                normalize
            ])

    def get_loaders(self, batch_size=32, num_workers=2):
        """
        Returns DataLoader objects for training and testing.
        Args:
            batch_size (int): Batch size for loading.
            num_workers (int): Number of subprocesses for data loading.
        """
        train_transform = self.get_transforms('train')
        test_transform = self.get_transforms('test')
        
        train_dataset = datasets.ImageFolder(root=self.train_dir, transform=train_transform)
        test_dataset = datasets.ImageFolder(root=self.test_dir, transform=test_transform)
        
        train_loader = torch.utils.data.DataLoader(train_dataset, 
                                                   batch_size=batch_size, 
                                                   shuffle=True, 
                                                   num_workers=num_workers)
                                                   
        test_loader = torch.utils.data.DataLoader(test_dataset, 
                                                  batch_size=batch_size, 
                                                  shuffle=False, 
                                                  num_workers=num_workers)
                                                  
        return train_loader, test_loader
