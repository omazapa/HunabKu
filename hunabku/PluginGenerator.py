from hunabku import templates
from shutil import copytree, move, rmtree
import pathlib
import os


class PluginGenerator:
    """
    Class to generate a hunabku plugin from the template.
    The generated plugin is a python package ready to install with pip and it can be deployed in pipy.
    """
    def __init__(self, name: str, prefix="HunabKu"):
        self.name = name
        self.tname = "template"
        self.prefix = prefix
        self.template_path = os.path.join(
            str(pathlib.Path(templates.__file__).parent.absolute()), "plugin")
        self.template_path = os.path.join(
            self.template_path, "HunabKu_template")

    def replace(self, filename, old, new):
        content = ""
        with open(filename, "r") as file:
            content = file.read()
            content = content.replace(old, new)
            file.close()
        with open(filename, "w") as file:
            file.write(str(content))
            file.close()

    def generate(self, path: str = os.getcwd()):
        output_path = os.path.join(os.getcwd(), f"{self.prefix}_{self.name}")
        readme = os.path.join(output_path, "README.md")
        setup = os.path.join(output_path, "setup.py")
        manifest = os.path.join(output_path, "MANIFEST.in")
        package_folder_old = os.path.join(output_path, f"hunabku_template")
        package_folder_new = os.path.join(
            output_path, f"{self.prefix}_{self.name}".lower())
        package_folder_endpoints = os.path.join(package_folder_new,"endpoints")

        copytree(self.template_path, output_path)
        move(package_folder_old, package_folder_new)
        
        rmtree(os.path.join(output_path, "__pycache__"), ignore_errors=True)
        rmtree(os.path.join(package_folder_new, "__pycache__"), ignore_errors=True)
        rmtree(os.path.join(package_folder_endpoints, "__pycache__"), ignore_errors=True)
         
        self.replace(readme, self.tname, self.name)
        self.replace(setup, self.tname, self.name)
        self.replace(manifest, self.tname, self.name)
