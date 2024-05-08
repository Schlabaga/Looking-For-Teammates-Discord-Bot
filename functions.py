import requests
from config import dbValorant

class SyncApi(): # PERMET DE SYNC LE BOT AVEC L'API VALORANT ET DE METTRE A JOUR LES DONNEES DANS LA BASE DE DONNEES
    
    def __init__(self):
        self.agentDict = {}
        self.skinDict = {}
    
    def get_all_agents(self):
        
        url = "https://valorant-api.com/v1/agents"
        params ={"language": "fr-FR","isPlayableCharacter": "true"}
        response = requests.get(url = url, params=params)

        if response.status_code == 200:
            data = response.json()
            for agent in data["data"]:
                
                self.agentDict = {}
                self.agentDict["uuid"] = agent["uuid"]
                self.agentDict["displayName"] = agent["displayName"]
                self.agentDict["description"] = agent["description"]
                self.agentDict["role"] = agent["role"]
                self.agentDict["charactrerTags"] = agent["characterTags"]
                self.agentDict["abilities"] = agent["abilities"]
                self.agentDict["background"] = agent["background"]
                self.agentDict["fullPortrait"] = agent["fullPortrait"]
                self.agentDict["fullPotraitV2"] = agent["fullPortraitV2"]
                self.agentDict["bustPortrait"] = agent["bustPortrait"]
                self.agentDict["displayIcon"] = agent["displayIcon"]
                self.agentDict["voiceLine"] = agent["voiceLine"]
                
                print(self.agentDict)
                dbValorant.agents.update_one({"uuid": agent["uuid"]}, {"$set": self.agentDict}, upsert=True)
 
            return data
        
        else:
            print("Failed to retrieve agents. Status code:", response.status_code)
            return None

    def get_all_skins(self):
        url = "https://valorant-api.com/v1/weapons/skins"
        params = {"language": "fr-FR"}
        response = requests.get(url=url, params=params)

        if response.status_code == 200:
            data = response.json()
            for skin in data["data"]:
                self.skinDict = {}
                self.skinDict["uuid"] = skin["uuid"]
                self.skinDict["displayName"] = skin["displayName"]
                self.skinDict["levels"] = skin["levels"]
                self.skinDict["contentTierUuid"] = skin["contentTierUuid"]
                self.skinDict["wallpaper"] = skin["wallpaper"]  
                self.skinDict["displayIcon"] = skin["displayIcon"]
                self.skinDict["chromas"] = skin["chromas"]

                print(self.skinDict)
                # dbValorant.skins.update_one({"uuid": skin["uuid"]}, {"$set": self.skinDict}, upsert=True)

            return data

        else:
            print("Failed to retrieve skins. Status code:", response.status_code)
            return None
        
        
valorantSync =  SyncApi()

valorantSync.get_all_agents()
valorantSync.get_all_skins()