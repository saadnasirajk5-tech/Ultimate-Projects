

##  rick_and_morty_collector.py
"""
RICK AND MORTY API COLLECTOR
A complete Python script that:
1. Connects to the public Rick and Morty API
2. Handles pagination (page 1, 2, 3... until no more data)
3. Validates every character with Pydantic v2
4. Saves clean, structured data to JSON (and CSV bonus)
5. Has rock-solid error handling

Perfect for learning APIs, pagination, validation & file I/O!
"""


import requests
import json
import csv
import time
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime

# =============================================================================
# 1. PYDANTIC MODEL - Data Validation Superhero
# =============================================================================
class Origin(BaseModel):
    """Nested model for character's origin location."""
    name: str
    url: str


class Character(BaseModel):
    """Pydantic model for one Rick and Morty character.
    This ensures the API data is exactly what we expect.
    If the API changes or sends bad data → we catch it immediately!
    """
    model_config = ConfigDict(
        extra='ignore',              # Ignore any extra fields the API might add
        str_strip_whitespace=True    # Clean up spaces automatically
    )

    id: int = Field(gt=0, description="Character ID must be positive")
    name: str = Field(min_length=1, max_length=100)
    status: str = Field(pattern="^(Alive|Dead|unknown)$")
    species: str
    gender: str
    origin: Origin                   # Nested model!
    image: str = Field(pattern=r"^https?://")
    episode: List[str] = Field(default_factory=list)
    created: datetime                # Auto-converts string to datetime

    @field_validator('name')
    @classmethod
    def name_must_be_fun(cls, v: str) -> str:
        """Custom validator - just for fun!"""
        if len(v) < 3:
            raise ValueError("Character names must be at least 3 characters!")
        return v


# =============================================================================
# 2. MAIN FUNCTION - The Brain of the Script
# =============================================================================
def fetch_all_characters() -> List[Character]:
    """
    Fetches EVERY character from the Rick and Morty API using pagination.
    Returns a list of validated Pydantic Character objects.
    """
    all_characters: List[Character] = []
    page = 1
    base_url = "https://rickandmortyapi.com/api/character"

    print(" Starting the multiverse crawl... Let's go get some characters!")

    while True:
        url = f"{base_url}?page={page}"
        
        try:
            response = requests.get(url, timeout=10)
            
            # Rate limiting protection
            if response.status_code == 429:
                print(" Rate limited! Waiting 2 seconds...")
                time.sleep(2)
                continue

            response.raise_for_status()  # Raises error for 4xx/5xx codes
            
            data = response.json()

            # Validate every character with Pydantic
            for char_data in data["results"]:
                try:
                    character = Character.model_validate(char_data)
                    all_characters.append(character)
                except Exception as e:
                    print(f" Validation failed for character on page {page}: {e}")

            print(f" Page {page} loaded - {len(data['results'])} characters validated!")

            # Check if there's a next page (this is how pagination works!)
            if data["info"]["next"] is None:
                break

            page += 1
            time.sleep(0.5)  # Be nice to the API

        except requests.exceptions.RequestException as e:
            print(f" Network error on page {page}: {e}")
            break
        except json.JSONDecodeError:
            print(" Invalid JSON received!")
            break

    print(f" Mission complete! Total characters collected: {len(all_characters)}")
    return all_characters


# =============================================================================
# 3. SAVE TO FILES - JSON + Bonus CSV
# =============================================================================
def save_to_json(characters: List[Character], filename: str = "rick_and_morty_characters.json"):
    """Saves validated characters to a beautiful, clean JSON file."""
    data_to_save = [char.model_dump(mode="json") for char in characters]
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)
    
    print(f" Saved {len(characters)} characters to {filename}")


def save_to_csv(characters: List[Character], filename: str = "rick_and_morty_characters.csv"):
    """Bonus: Saves the same data to CSV for Excel/Google Sheets lovers."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "name", "status", "species", "gender", "origin_name", "image"
        ])
        writer.writeheader()
        
        for char in characters:
            writer.writerow({
                "id": char.id,
                "name": char.name,
                "status": char.status,
                "species": char.species,
                "gender": char.gender,
                "origin_name": char.origin.name,
                "image": char.image
            })
    
    print(f"📊 Bonus CSV saved: {filename}")


# =============================================================================
# 4. RUN THE WHOLE SHOW
# =============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" RICK AND MORTY API COLLECTOR STARTING")
    print("   Using: requests + Pydantic v2 + Pagination")
    print("=" * 60)

    characters = fetch_all_characters()
    
    if characters:
        save_to_json(characters)
        save_to_csv(characters)   # Remove this line if you don't want CSV
        
        print("\nProject complete! Check the files in your folder.")
        print("   You now have clean, validated Rick and Morty data!")
    else:
        print("No characters collected. Something went wrong.")
        
    
    
    
    
    
    
    