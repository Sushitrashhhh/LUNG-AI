import os
import shutil
from datasets import load_dataset
from tqdm import tqdm # You may need to run: pip install tqdm
from PIL import Image # You may need to run: pip install Pillow

# THIS IS THE FIX: Map the 7+ dataset classes to the 4 project classes
def get_project_class(dataset_class_name):
    """Maps a detailed class name to one of the 4 project categories."""
    dcn = dataset_class_name.lower() # dcn = dataset class name
    if 'adenocarcinoma' in dcn:
        return 'Adenocarcinoma'
    if 'large.cell' in dcn:
        return 'Large_cell_carcinoma'
    if 'squamous' in dcn:
        return 'Squamous_cell_carcinoma'
    if 'normal' in dcn:
        return 'Normal'
    return None # We will ignore any class that doesn't fit

def setup_dataset():
    base_dir = "Processed_Data"
    
    # Clean up the directory if it already exists from a failed run
    if os.path.exists(base_dir):
        print(f"Removing old '{base_dir}' directory...")
        shutil.rmtree(base_dir)
        print("Done.")

    # 1. Load the dataset
    print("Loading dataset 'dorsar/lung-cancer' from Hugging Face...")
    ds = load_dataset("dorsar/lung-cancer", "default", trust_remote_code=True)
    
    # 2. Get the *dataset's* class names
    dataset_class_names = ds['train'].features['label'].names
    print(f"Found {len(dataset_class_names)} dataset classes: {dataset_class_names}")

    # 3. Define the *project's* 4 classes
    project_class_names = ['Adenocarcinoma', 'Large_cell_carcinoma', 'Normal', 'Squamous_cell_carcinoma']
    print(f"Mapping them into 4 project classes: {project_class_names}")

    # 4. Loop through each split (train, validation, test)
    for split in ds.keys():
        print(f"\nProcessing '{split}' split...")
        split_data = ds[split]
        
        for i, item in enumerate(tqdm(split_data, desc=f"Saving {split} images")):
            image = item['image']
            label_index = item['label']
            
            # Get the dataset's class name (e.g., 'adenocarcinoma_left.lower.lobe...')
            dataset_class_name = dataset_class_names[label_index]
            
            # --- THIS IS THE NEW LOGIC ---
            # Convert it to the project's class name (e.g., 'Adenocarcinoma')
            project_class_name = get_project_class(dataset_class_name)
            
            # If it's not one of our 4 classes, skip this image
            if project_class_name is None:
                continue
            # --- END OF NEW LOGIC ---

            # Create the full directory path
            # e.g., "Processed_Data/train/Adenocarcinoma"
            target_dir = os.path.join(base_dir, split, project_class_name)
            
            # Create the directories if they don't already exist
            os.makedirs(target_dir, exist_ok=True)
            
            # Convert to RGB to avoid errors with PNG/grayscale images
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Create a unique filename and save as JPEG
            filename = f"{split}_{project_class_name}_{i}.jpg"
            save_path = os.path.join(target_dir, filename)
            image.save(save_path, "JPEG")

    print(f"\n✅ All data downloaded and RE-MAPPED successfully!")
    print(f"Your data is ready in the '{base_dir}' folder with the correct 4 classes.")

if __name__ == "__main__":
    # This makes the script runnable from the command line
    setup_dataset()