# AustinsArkServer

## Developing using WSL-Ubuntu before Kubernetes/Docker containerization: 
If we're working on this project using WSL:Ubuntu, we might run into an error/warning when trying to install python packages like kafka-python using pip because it conflicts/interferes with the host OS python environment (Win11 python vs WSL:Ubuntu-python). To get around this, we need to go about setting up a virtual environment for python inside our project directory that acts as a "python bubble" of sorts. Once we activate this python virtual environment, we step into an isolated environment where we can freely install packages using pip and develop without fear of breaking our host OS (like I did which required me to reinstall windows and go through a painful troubleshooting process). 

Follow the steps below to get the virtual environment within WSL-Ubuntu set up:

1. Install venv using the apt package manager with in WSL:Ubuntu

```bash
sudo apt install python3-venv
``` 

2. Create a virtual environment within your project directory (cd into project repo and then execute the command)
```bash
python3 -m venv venv
```

3. Activate the virtual environment
```bash
source venv/bin/activate
```
4. You should now be able to install python packages using pip without conflicts.
```bash
pip install kafka-python
```
