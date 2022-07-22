# Python Discord Code Jam 2022
Rare Rainbow Serpents' Submission

## Enviroment Set Up

Before doing anything, be sure you have clone the project and you are in the repo directory. You should have installed the python 3.10.5 interpreter.
Then to create the virtual enviroment you should run:

    python3.10 -m venv .venv

This should have created a folder .venv where python and all the dependencies for the project are going to live. Now, every time you are going to run 
your code or you are going to install a dependencie, be sure that the virtual enviroment is active. In linux, this is made by:

    source <repo path>/.venv/bin/activate

In order to manage dependencies easily, we are going to work with [pip-tools](https://github.com/jazzband/pip-tools). So once the enviroment is active, 
run its instalation:

    python -m pip install pip-tools

This tool divide the core dependencies of the project( the ones that we select ) and the derivate dependencies (dependencies need by packeges). It also help you to keep 
your enviroment cleaned if you make some test with a dependency. 

(OPTIONAL STEP)The desired dependencies are listed in the requirements.in file. If you make an modification, you should run pip-compile to let pip-tools search for other dependencies.
This updates the requirement.txt file that pip-tools use to manage your enviroment

    pip-compile requirement.in

To install desired dependencies and clean your env for not listed dependencies, you should run:

    pip-sync requirements.txt dev-requirements.txt



