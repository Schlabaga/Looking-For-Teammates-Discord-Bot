import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import os
from config import dbValorant

# Configuration       
cloudinary.config( 
    cloud_name = "dbcqyozi5", 
    api_key = "815561692885965", 
    api_secret = "fIPa3UNn796jwP_cxgqx5tWJSZ8", # Click 'View Credentials' below to copy your API secret
    secure=True
)



def upload_image(type,dossier):
    
    dossier = f"crosshairs/{type}"
    # Iterate over all folders in the specified directory
    for root, dirs, files in os.walk(dossier):
        
        crosshair_id = root.split("\\")[-1]
        print(crosshair_id)
        

        crosshair_data = dbValorant.crosshairs.find_one({"id": crosshair_id})
        try:
            crosshair_data["yellow"]
            print("Crosshair already uploaded")
            pass
        
        except Exception as e:
            print(str(e))
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                name = file_name.replace(".png", "")
                
                upload_result = cloudinary.uploader.upload(file_path,
                                                        public_id=f"{crosshair_id}_{name}",
                                                        quality="auto",
                                                        tags = [type])
                
                dbValorant.crosshairs.update_one({"id": crosshair_id}, {"$set": {f"{name}": upload_result["url"]}})
                
                print(upload_result["url"])
                
                print(f"Image {file_name} uploaded")

    return 

upload_image("user", "crosshairs/")
