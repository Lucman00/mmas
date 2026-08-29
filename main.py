import Api.MD.requests as md

api = md.MangaDexAPI(lang="en")

api.loadManga("Spice and Wolf", 20)