import Api.MD.mrequests as md

api = md.MangaDexAPI(lang="en")

api.loadManga("Spice and Wolf", 20)