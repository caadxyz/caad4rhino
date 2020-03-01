### how to setup python environment

Some users will find that Caad4Rhino cannot be loaded.   
This is mainly because the python environment of rhino is not set up properly, especially in Windows

You can solve it in the following ways:

**Step One** : Checking python environment

* Open rhino software
* Click on the menu Tools-> PythonScript-> Edit
* Click the menu File-> New-> Command
* Enter `Helloworld` in the command field
* Enter `Helloworld` in the plugin field
* Click on the green button to run
* Click the `saveall` button
* Close rhino and restart

**Step Two** : loading python environment

* Open rhino software
* Click on the menu Tools-> PythonScript-> Edit
* Click menu File-> Open, open `Helloworld_cmd.py`
* Click on the green button to run
* Close Rhino python editor
* Enter `Helloworld` in the rhino software command field
* If this command works, then your python environment is loaded. 
* If it doesn't work, you can wait a bit, it takes time for rhino to load, or try the second step again.

**Step Three**  install Caad4Rhino

* Open rhino software
* Click on the menu Tools-> PythonScript-> Edit
* Click menu File-> Open, open `Helloworld_cmd.py`
* Click the save as button to see the folder location: `%AppData%\McNeel\Rhinoceros\6.0\Plug-ins\PythonPlugins\Helloworld{058e2284-c977-4a3a-a188-d2f62ac95e66}`
* Install `caad4rhino{417c9034-2152-48dc-b487-29b584c473a5}` under the same folder `%AppData%\McNeel\Rhinoceros\6.0\ Plug-ins\PythonPlugins` 
* Close rhino and restart

If you can run the `Helloworld` command this time, you should also be able to run the `caad` command
