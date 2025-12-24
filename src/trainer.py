import torch
import time
import matplotlib.pyplot as plt
from pathlib import Path

class Trainer:
    """
    A modular class to handle model training and validation.
    """
    def __init__(self, model, train_loader, val_loader, criterion, optimizer, device, output_dir, scheduler=None):
        """
        Args:
            model: PyTorch model.
            train_loader: DataLoader for training.
            val_loader: DataLoader for validation.
            criterion: Loss function.
            optimizer: Optimizer.
            device: 'cuda' or 'cpu'.
            output_dir: Directory to save plots and checkpoints.
            scheduler: Learning rate scheduler (optional).
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.history = {
            'train_loss': [], 'val_loss': [],
            'train_acc': [], 'val_acc': []
        }
        self.best_acc = 0.0
        
    def train_one_epoch(self, epoch_index, limit_batches=None):
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for i, (inputs, labels) in enumerate(self.train_loader):
            if limit_batches and i >= limit_batches:
                break
                
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            
            self.optimizer.zero_grad()
            
            outputs = self.model(inputs)
            loss = self.criterion(outputs, labels)
            loss.backward()
            self.optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
            if (i + 1) % 10 == 0:
                print(f"Epoch [{epoch_index+1}] Batch [{i+1}/{len(self.train_loader)}] Loss: {loss.item():.4f}")
            
        # Adjust normalization if we broke early
        num_samples = len(self.train_loader.dataset)
        if limit_batches:
             num_samples = total

        epoch_loss = running_loss / num_samples if num_samples > 0 else 0
        epoch_acc = correct / total if total > 0 else 0
        return epoch_loss, epoch_acc

    def validate(self, limit_batches=None):
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for i, (inputs, labels) in enumerate(self.val_loader):
                if limit_batches and i >= limit_batches:
                    break
                    
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                
                running_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        # Adjust normalization
        num_samples = len(self.val_loader.dataset)
        if limit_batches:
            num_samples = total

        epoch_loss = running_loss / num_samples if num_samples > 0 else 0
        epoch_acc = correct / total if total > 0 else 0
        return epoch_loss, epoch_acc

    def train(self, num_epochs=5, limit_batches=None):
        print(f"Starting training on {self.device} for {num_epochs} epochs...")
        if limit_batches:
             print(f"Running in fast mode: capping at {limit_batches} batches per epoch.")
             
        start_time = time.time()
        
        for epoch in range(num_epochs):
            train_loss, train_acc = self.train_one_epoch(epoch, limit_batches)
            val_loss, val_acc = self.validate(limit_batches)
            
            # Update scheduler if provided
            if self.scheduler:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_loss)
                else:
                    self.scheduler.step()
                
                current_lr = self.optimizer.param_groups[0]['lr']
                print(f"Current LR: {current_lr:.6f}")
            
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_acc'].append(val_acc)
            
            print(f"Epoch [{epoch+1}/{num_epochs}] "
                  f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
                  f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}")
            
            # Save Best Model
            if val_acc > self.best_acc:
                self.best_acc = val_acc
                self.save_checkpoint(is_best=True)
                print(f"New best model saved with Acc: {val_acc:.4f}")
            
        total_time = time.time() - start_time
        print(f"Training complete in {total_time // 60:.0f}m {total_time % 60:.0f}s. Best Acc: {self.best_acc:.4f}")
        
        self.save_checkpoint(is_best=False) # Save final model
        self.plot_history()
        
    def save_checkpoint(self, is_best=False):
        if is_best:
            path = self.output_dir / 'best_model.pth'
        else:
            path = self.output_dir / 'final_model.pth'
            
        torch.save(self.model.state_dict(), path)
        if not is_best:
            print(f"Final model saved to {path}")

    def plot_history(self):
        epochs = range(1, len(self.history['train_loss']) + 1)
        
        plt.figure(figsize=(12, 5))
        
        # Loss Plot
        plt.subplot(1, 2, 1)
        plt.plot(epochs, self.history['train_loss'], 'b-', label='Training Loss')
        plt.plot(epochs, self.history['val_loss'], 'r-', label='Validation Loss')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        
        # Accuracy Plot
        plt.subplot(1, 2, 2)
        plt.plot(epochs, self.history['train_acc'], 'b-', label='Training Acc')
        plt.plot(epochs, self.history['val_acc'], 'r-', label='Validation Acc')
        plt.title('Training and Validation Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'training_curves.png')
        print(f"Training curves saved to {self.output_dir / 'training_curves.png'}")
