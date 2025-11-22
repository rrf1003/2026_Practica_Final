from repo.repo_manager import RepoManager  # Probablemente lo necesites para borrar


manager = RepoManager()
url = "https://github.com/octocat/Hello-World.git"

#print("--- Probando clonado ---")
path = manager.ensure_repo(url)
#print(f"Repo clonado en: {path}")
# print(f"¿Existe el directorio? {path.exists()}")

print("--- Probando borrado ---")
manager.remove_repo(url)
print(f"¿Existe tras borrar? {path.exists()}")