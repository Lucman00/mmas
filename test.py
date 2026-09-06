import Api.MD.mrequests as Md
from Api.Mal.searchnsort import manageMal as Mal

# Test 1: Direct MangaDex search
md = Md.MangaDexAPI()
response = md.searchManga("Spice and Wolf", 5)
print("Search status:", response.status_code)

# Test 2: Print filtered results
print(md.simpleMangaId("Spice and Wolf", response.json()))

# Test 3: Try full flow with error handling
try:
    Mal().searchMangaMatch("Spice and Wolf")
except Exception as e:
    print(f"Error: {e}") 